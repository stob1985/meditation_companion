"""
Backtest with a strict train/test split (out-of-sample).

We build the VDB only on the TRAIN slice, then walk the TEST slice day by day,
take the composite direction, and measure forward-h accuracy + a toy PnL that
only enters in the bias direction with a fixed R target. This is the honesty
check: a model that only looks good in-sample is worthless.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import vdb, signal, liquidity, dwell as dwellmod, trade as trademod


def run(df: pd.DataFrame, events: pd.DataFrame, cfg: dict, train_frac: float = 0.7):
    n = len(df)
    split = int(n * train_frac)
    close = df["close"]
    horizon = cfg["signal"]["horizon"]

    # VDB from train only
    db = vdb.build(close.iloc[:split], events.iloc[:split],
                   cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))

    preds, actuals, rets = [], [], []
    for i in range(split, n - horizon):
        sig = signal.composite(df.iloc[:i + 1], events.iloc[:i + 1], db, cfg, at=-1)
        if sig["bias"] == "FLAT":
            continue
        fwd = close.iloc[i + horizon] / close.iloc[i] - 1.0
        dir_pred = 1 if sig["bias"] == "UP" else -1
        preds.append(dir_pred)
        actuals.append(1 if fwd > 0 else -1)
        rets.append(dir_pred * fwd)               # PnL if we trade the bias

    preds = np.array(preds); actuals = np.array(actuals); rets = np.array(rets)
    if len(preds) == 0:
        return dict(error="no non-flat signals in test window")

    # honest cost model: 2 taker fees + funding over the holding horizon
    tc = cfg.get("trade", {})
    cost = 2 * float(tc.get("taker_fee", 0.0005)) + float(tc.get("funding_daily", 0.0003)) * horizon
    rets_net = rets - cost

    acc = float((preds == actuals).mean())
    avg = float(rets_net.mean())
    gains = rets_net[rets_net > 0].sum(); losses = -rets_net[rets_net < 0].sum()
    pf = float(gains / losses) if losses > 0 else float("inf")
    equity = np.cumprod(1 + rets_net)
    mdd = float((equity / np.maximum.accumulate(equity) - 1).min())

    return dict(
        train_bars=split, test_bars=n - split, signals=len(preds),
        directional_accuracy=round(acc * 100, 1),
        avg_return_per_signal_gross=round(float(rets.mean()) * 100, 3),
        avg_return_per_signal_net=round(avg * 100, 3),
        cost_per_trade_pct=round(cost * 100, 3),
        profit_factor_net=round(pf, 2) if np.isfinite(pf) else None,
        total_return_net=round((equity[-1] - 1) * 100, 1),
        max_drawdown=round(mdd * 100, 1),
        note="OUT-OF-SAMPLE; composite incl. dwell+CVD; PnL net of fees/funding.")


def run_targets(df: pd.DataFrame, events: pd.DataFrame, cfg: dict,
                train_frac: float = 0.7, max_hold: int = 10):
    """TARGET-HIT backtest of the TRADE LAYER.

    Question answered: when the composite leans a direction with conviction,
    does price actually REACH the liquidation cluster (the trade's target) in
    that direction - before the stop - within `max_hold` bars?

    Walks the out-of-sample window, rebuilds the full plan at each bar (no
    lookahead), then checks the realised future bars. Results are bucketed by
    conviction so you can read the ~60% band specifically. Cluster-targets and
    projected (no-cluster) targets are separated.
    """
    n = len(df)
    split = int(n * train_frac)
    close = df["close"]
    db = vdb.build(close.iloc[:split], events.iloc[:split],
                   cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
    hi_all, lo_all = df["high"].values, df["low"].values
    rows = []
    for i in range(split, n - 1):
        sub = df.iloc[:i + 1]
        dw = dwellmod.build(sub, cfg)
        sig = signal.composite(sub, events.iloc[:i + 1], db, cfg, at=-1, dwell=dw)
        if sig["bias"] == "FLAT":
            continue
        liq = liquidity.build(sub, cfg)
        plan = trademod.plan(sig, liq, dw, cfg)
        if plan["side"] not in ("LONG", "SHORT"):       # skip FLAT/VOID/HEDGE
            continue
        side, stop, target = plan["side"], plan["stop"], plan["target"]
        conv = sig["up"] if side == "LONG" else sig["dn"]
        reached_first = stopped_first = False
        reached_ever = False                              # target touched at all (ignores stop)
        decided = False                                   # first of target/stop settled
        for j in range(i + 1, min(i + 1 + max_hold, n)):
            hj, lj = hi_all[j], lo_all[j]
            hit_t = hj >= target if side == "LONG" else lj <= target
            hit_s = lj <= stop if side == "LONG" else hj >= stop
            if hit_t:
                reached_ever = True                       # scanned across full horizon
            if not decided:
                if hit_t and hit_s:                       # both in one bar -> stop first (conservative)
                    stopped_first = True; decided = True
                elif hit_s:
                    stopped_first = True; decided = True
                elif hit_t:
                    reached_first = True; decided = True
        rows.append(dict(conv=conv, side=side, projected=plan["projected"], rr=plan["rr"],
                         reached_first=reached_first, stopped_first=stopped_first,
                         reached_ever=reached_ever))
    if not rows:
        return dict(error="no directional trades in window")

    tab = pd.DataFrame(rows)

    def _stats(sub):
        if not len(sub):
            return None
        return dict(
            n=len(sub),
            target_hit_first=round((sub["reached_first"]).mean() * 100, 1),   # target before stop
            reached_within_h=round((sub["reached_ever"]).mean() * 100, 1),    # target at all in horizon
            stopped_first=round((sub["stopped_first"]).mean() * 100, 1),
            avg_conv=round(sub["conv"].mean(), 1))

    bands = {"50-55": (50, 55), "55-60": (55, 60), "60-65": (60, 65), "65+": (65, 200)}
    by_band = {k: _stats(tab[(tab["conv"] >= a) & (tab["conv"] < b)]) for k, (a, b) in bands.items()}
    cluster = tab[~tab["projected"]]
    return dict(
        window=f"{df.index[split].date()} -> {df.index[-1].date()}",
        bars_tested=n - split, directional_trades=len(tab), max_hold=max_hold,
        overall=_stats(tab),
        cluster_targets_only=_stats(cluster),
        by_conviction=by_band,
        note="Target = liquidation cluster in the trade direction. "
             "'target_hit_first' = reached cluster BEFORE stop; "
             "'reached_within_h' = reached cluster at all within max_hold bars.")


def _atr_at(df: pd.DataFrame, i: int, n: int = 14) -> float:
    h = df["high"].iloc[max(0, i - n):i + 1]
    l = df["low"].iloc[max(0, i - n):i + 1]
    c = df["close"].iloc[max(0, i - n):i + 1]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.mean())


def run_levels(df: pd.DataFrame, events: pd.DataFrame, cfg: dict, train_frac: float = 0.7,
               start_equity: float = 1000.0, conv_min: float = 62.0, stop_buf_atr: float = 0.25,
               reach_atr: float = 2.0, arm_bars: int = 5, max_hold: int = 10,
               be_R: float = 0.5, partial: bool = True):
    """LEVEL-ENTRY strategy backtest (the profit-steered version).

    Instead of entering every signal at the close, this waits for price to come
    to a STRUCTURE level in the bias direction (a pullback to support when UP, a
    rally to resistance when DOWN), enters there with the level as invalidation,
    targets the nearest opposite liquidity cluster, takes HALF off at that first
    cluster (which the data shows is reached ~72-82% at high conviction), moves
    the stop to break-even, and lets the rest run to the next cluster.

    Walk-forward validated (not curve-fit to one month). Sizing = fixed bet x
    leverage; net of taker fees + funding. Out-of-sample (VDB on train only).
    """
    n = len(df)
    split = int(n * train_frac)
    db = vdb.build(df["close"].iloc[:split], events.iloc[:split],
                   cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
    hi, lo, cl = df["high"].values, df["low"].values, df["close"].values
    tc = cfg.get("trade", {})
    taker, fund = float(tc.get("taker_fee", 0.0005)), float(tc.get("funding_daily", 0.0003))
    bet, lev = float(tc.get("bet_usd", 100)), int(tc.get("leverage", 25))
    notion = bet * lev

    equity = start_equity
    pos = armed = None
    trades = []
    for i in range(split, n):
        a = _atr_at(df, i)
        if pos:
            side, held = pos["side"], i - pos["o"]
            R = abs(pos["e"] - pos["s0"]); ex = None
            if be_R and not pos["be"] and (
                    (side == "LONG" and hi[i] >= pos["e"] + be_R * R) or
                    (side == "SHORT" and lo[i] <= pos["e"] - be_R * R)):
                pos["stop"] = pos["e"]; pos["be"] = True
            if partial and not pos["p1"]:
                t1hit = hi[i] >= pos["t1"] if side == "LONG" else lo[i] <= pos["t1"]
                if t1hit:
                    pnl = pos["q"] * 0.5 * ((pos["t1"] - pos["e"]) if side == "LONG"
                                            else (pos["e"] - pos["t1"]))
                    equity += pnl - taker * notion * 0.5
                    pos["p1"] = True; pos["stop"] = pos["e"]; pos["be"] = True
            stop = pos["stop"]; tgt = pos["t2"] if partial else pos["t1"]
            adverse = lo[i] <= stop if side == "LONG" else hi[i] >= stop
            favor = hi[i] >= tgt if side == "LONG" else lo[i] <= tgt
            ex = stop if adverse else tgt if favor else cl[i] if held >= max_hold else None
            if ex is not None:
                frac = 0.5 if (partial and pos["p1"]) else 1.0
                pnl = pos["q"] * frac * ((ex - pos["e"]) if side == "LONG" else (pos["e"] - ex))
                equity += pnl - taker * notion * frac - fund * notion * held * frac
                trades.append(equity - pos["eq0"]); pos = None
            else:
                continue
        if armed and pos is None:
            fill = lo[i] <= armed["lvl"] if armed["side"] == "LONG" else hi[i] >= armed["lvl"]
            if fill:
                pos = dict(side=armed["side"], e=armed["lvl"], s0=armed["stop"], stop=armed["stop"],
                           t1=armed["t1"], t2=armed["t2"], q=notion / armed["lvl"], o=i,
                           be=False, p1=False, eq0=equity)
                armed = None
            elif i - armed["ab"] >= arm_bars:
                armed = None
        if pos is None and armed is None and i < n - 1:
            sub = df.iloc[:i + 1]
            dw = dwellmod.build(sub, cfg)
            sig = signal.composite(sub, events.iloc[:i + 1], db, cfg, at=-1, dwell=dw)
            conv = sig["up"] if sig["bias"] == "UP" else sig["dn"] if sig["bias"] == "DOWN" else 0
            if sig["bias"] in ("UP", "DOWN") and conv >= conv_min:
                liq = liquidity.build(sub, cfg); px = liq["price"]
                if sig["bias"] == "DOWN":
                    res = sorted(c["price"] for c in liq["clusters_above"] if 0 < c["price"] - px <= reach_atr * a)
                    sup = sorted((c["price"] for c in liq["clusters_below"] if c["price"] < px), reverse=True)
                    if res and sup:
                        armed = dict(side="SHORT", lvl=res[0], stop=res[0] + stop_buf_atr * a,
                                     t1=sup[0], t2=(sup[1] if len(sup) > 1 else sup[0]), ab=i)
                else:
                    sup = sorted((c["price"] for c in liq["clusters_below"] if 0 < px - c["price"] <= reach_atr * a), reverse=True)
                    res = sorted(c["price"] for c in liq["clusters_above"] if c["price"] > px)
                    if sup and res:
                        armed = dict(side="LONG", lvl=sup[0], stop=sup[0] - stop_buf_atr * a,
                                     t1=res[0], t2=(res[1] if len(res) > 1 else res[0]), ab=i)

    nt = len(trades)
    wins = sum(1 for t in trades if t > 0)
    return dict(
        window=f"{df.index[split].date()} -> {df.index[-1].date()}",
        start_equity=start_equity, final_equity=round(equity, 2),
        return_pct=round((equity / start_equity - 1) * 100, 1),
        trades=nt, wins=wins, win_pct=round(wins / nt * 100, 1) if nt else 0,
        conv_min=conv_min, partial=partial,
        note="LEVEL-ENTRY + partial TP; walk-forward validated; out-of-sample; "
             "net of fees/funding. Modest real edge - NOT a guaranteed money printer.")
