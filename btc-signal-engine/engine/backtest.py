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
