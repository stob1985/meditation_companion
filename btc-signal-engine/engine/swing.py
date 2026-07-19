"""
SWING layer - the "1-3 big trades per month" mode.
====================================================================
ADDITIVE layer on top of the existing daily engine. The daily composite +
liquidity map stay the PRECISION layer (where exactly to enter); this module
is the SELECTION layer (whether this is one of the few monthly moves worth
taking at all) and the MANAGEMENT layer (how to ride it instead of cutting it).

Six gates - each ✓/✗ on the dashboard, most must agree or the answer is WAIT:

  1. WEEKLY REGIME  (mandatory)  close vs SMA200 + EMA50/EMA200 structure
  2. COMPOSITE      (mandatory)  the existing composite, at a RAISED bar
                                 (swing.conv_min, default 70 > the 62 scalp bar)
  3. TIMING                      vol compression (volregime) or an aligned
                                 sweep-reclaim - big moves start coiled or at a flush
  4. ETF FLOW                    5-day net spot-ETF flow direction (etfflow)
  5. CROWD                       funding/L-S not hot AGAINST the idea (realflow)
  6. GRAVITY                     liquidity gravity pulls in the trade direction

Exit design is the big difference vs the scalp plan: TP1 takes only 1/3 (not
half), the rest is a RUNNER trailed on a 20-day Donchian stop - no fixed T2,
because the whole point is not to amputate the monthly move at +2R.

Educational, not financial advice. Same honesty rules as the rest of the repo.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def weekly_regime(df: pd.DataFrame) -> dict:
    """HTF gate from daily data: SMA200 position + EMA50/EMA200 structure."""
    close = df["close"]
    px = float(close.iloc[-1])
    n = len(close)
    sma200 = float(close.rolling(min(200, max(50, n // 2))).mean().iloc[-1])
    ema50 = float(close.ewm(span=50).mean().iloc[-1])
    ema200 = float(close.ewm(span=min(200, max(50, n // 2))).mean().iloc[-1])
    above = px > sma200
    golden = ema50 > ema200
    regime = "BULL" if (above and golden) else "BEAR" if (not above and not golden) else "MIXED"
    return dict(regime=regime, px=px, sma200=round(sma200, 1),
                ema50=round(ema50, 1), ema200=round(ema200, 1),
                low_confidence=n < 200)


def _donchian_stop(df: pd.DataFrame, side: str, bars: int, buf: float) -> float:
    if side == "LONG":
        return float(df["low"].tail(bars).min()) - buf
    return float(df["high"].tail(bars).max()) + buf


def build(df: pd.DataFrame, sig: dict, liq: dict, cfg: dict,
          vol: dict = None, etf: dict = None, rf: dict = None,
          grav: dict = None) -> dict | None:
    """Evaluate the swing gates and, if enough agree, emit a swing plan."""
    sc = cfg.get("swing", {})
    if not sc.get("enabled", True):
        return None
    conv_min = float(sc.get("conv_min", 70))
    min_ratio = float(sc.get("min_gate_ratio", 0.66))
    reach = float(sc.get("reach_atr", 3.0))
    buf = float(sc.get("stop_buffer_atr", 0.5))
    stop_max = float(sc.get("stop_max_atr", 4.0))
    don = int(sc.get("donchian_bars", 20))
    tp1_frac = float(sc.get("tp1_frac", 0.33))
    bet = float(sc.get("bet_usd", cfg.get("trade", {}).get("bet_usd", 100)))
    lev = int(sc.get("leverage", 5))
    horizon = int(sc.get("horizon", 21))

    px = float(sig["price"]); atr = float(liq["atr"])
    wk = weekly_regime(df)

    # candidate direction: weekly regime picks the ONLY tradeable side
    side = "LONG" if wk["regime"] == "BULL" else "SHORT" if wk["regime"] == "BEAR" else None
    want = "UP" if side == "LONG" else "DOWN" if side == "SHORT" else None
    conv = sig["up"] if want == "UP" else sig["dn"] if want == "DOWN" else 0.0

    gates = {}   # name -> (ok: bool|None, detail)  None = data unavailable
    gates["weekly"] = (side is not None,
                       f"{wk['regime']} (px {'>' if wk['px'] > wk['sma200'] else '<'} SMA200, "
                       f"EMA50 {'>' if wk['ema50'] > wk['ema200'] else '<'} EMA200)")
    gates["composite"] = ((sig["bias"] == want and conv >= conv_min) if want else False,
                          f"bias {sig['bias']} conv {conv:.0f}% (kell: {want or '-'} ≥{conv_min:.0f}%)")

    rev = sig.get("reversal") or {}
    rev_align = (rev.get("signal") == "BULL" and side == "LONG") or \
                (rev.get("signal") == "BEAR" and side == "SHORT")
    if vol and vol.get("state") != "UNKNOWN":
        timing_ok = bool(vol.get("recent_squeeze")) or rev_align
        gates["timing"] = (timing_ok,
                          f"vol {vol['state']} (ATR p{vol['atr_pctile']:.0f}/BBW p{vol['bbw_pctile']:.0f}"
                          + (f", squeeze {vol['squeeze_days']}d" if vol.get("squeeze") else "")
                          + (", sweep-reclaim ✓" if rev_align else "") + ")")
    else:
        gates["timing"] = (None, "volregime n/a")

    if etf:
        eb = etf["bias"]
        ok = (eb.startswith("UP") if side == "LONG" else eb.startswith("DOWN")) if side else False
        gates["etf"] = (ok, f"5d nettó {etf['sum5']:+,.0f}M$ ({etf['trend']})")
    else:
        gates["etf"] = (None, "ETF flow n/a (offline/blocked)")

    if rf:
        ls = rf.get("ls_ratio") or {}; fund = rf.get("funding") or {}
        against = ("DOWN" if side == "LONG" else "UP")
        hot_against = (ls.get("contrarian") == against) or (fund.get("bias") == against)
        gates["crowd"] = (not hot_against,
                          f"L/S {ls.get('ratio', '?')} funding {fund.get('funding', '?')}"
                          + (" — tömeg a MI oldalunkon (squeeze-kockázat)" if hot_against else " — nem ellenszél"))
    else:
        gates["crowd"] = (None, "realflow n/a")

    if grav and grav.get("direction"):
        ok = (grav["direction"] == "UP" and side == "LONG") or \
             (grav["direction"] == "DOWN" and side == "SHORT")
        gates["gravity"] = (ok, f"gravitáció {grav['direction']} (arány {grav.get('ratio', '?')})")
    else:
        gates["gravity"] = (None, "gravity n/a")

    avail = {k: v for k, v in gates.items() if v[0] is not None}
    n_ok = sum(1 for ok, _ in avail.values() if ok)
    n_av = len(avail)
    mandatory_ok = bool(gates["weekly"][0]) and bool(gates["composite"][0])
    ratio_ok = n_av > 0 and (n_ok / n_av) >= min_ratio
    fire = mandatory_ok and ratio_ok

    # long-horizon forecast band (the swing analogue of the 3-day band)
    ret_h = df["close"].pct_change(horizon).tail(int(cfg["signal"]["band_lookback"]))
    sigma = float(ret_h.std()) if len(ret_h.dropna()) > 20 else None
    band = (round(px * (1 + sigma), 0), round(px * (1 - sigma), 0)) if sigma else None

    out = dict(gates={k: dict(ok=v[0], detail=v[1]) for k, v in gates.items()},
               n_ok=n_ok, n_avail=n_av, mandatory_ok=mandatory_ok,
               side=side, conv=round(conv, 1), horizon=horizon, band=band,
               weekly=wk, status="ARMED" if fire else "WAIT")
    if not fire:
        why = []
        if not gates["weekly"][0]:
            why.append("heti regime MIXED/ellentétes")
        if not gates["composite"][0]:
            why.append(f"kompozit {conv:.0f}% < {conv_min:.0f}%")
        if mandatory_ok and not ratio_ok:
            why.append(f"kapuk {n_ok}/{n_av} < {min_ratio:.0%}")
        out["reason"] = " · ".join(why) or "nincs elég konfluencia"
        return out

    # ---- plan: entry / capped structural stop / TP1>=1R third / runner ------
    tp1_min_r = float(sc.get("tp1_min_r", 1.0))
    if side == "LONG":
        sup = sorted((c["price"] for c in liq["clusters_below"]
                      if 0 < px - c["price"] <= reach * atr), reverse=True)
        entry = sup[0] if sup else px
        entry_type = "LIMIT (pullback a szintre)" if sup else "MARKET"
        stop = _donchian_stop(df, "LONG", don, buf * atr)
        stop = max(stop, entry - stop_max * atr)            # cap the risk
        risk0 = entry - stop
        # TP1 must be at least tp1_min_r * risk away - the nearest cluster is
        # often too close for a SWING partial; skip forward to the first one
        # that pays, else a fixed R-multiple
        res = sorted(c["price"] for c in liq["clusters_above"]
                     if c["price"] >= entry + tp1_min_r * risk0)
        tp1 = res[0] if res else round(entry + max(tp1_min_r * risk0, 2 * atr), 1)
        big = max(liq["clusters_above"], key=lambda c: c["count"], default=None) \
            if liq["clusters_above"] else None
        liq_price = entry * (1 - 1 / lev + 0.005)
        liq_safe = stop > liq_price
    else:
        res = sorted(c["price"] for c in liq["clusters_above"]
                     if 0 < c["price"] - px <= reach * atr)
        entry = res[0] if res else px
        entry_type = "LIMIT (rally a szintre)" if res else "MARKET"
        stop = _donchian_stop(df, "SHORT", don, buf * atr)
        stop = min(stop, entry + stop_max * atr)
        risk0 = stop - entry
        sup = sorted((c["price"] for c in liq["clusters_below"]
                      if c["price"] <= entry - tp1_min_r * risk0), reverse=True)
        tp1 = sup[0] if sup else round(entry - max(tp1_min_r * risk0, 2 * atr), 1)
        big = max(liq["clusters_below"], key=lambda c: c["count"], default=None) \
            if liq["clusters_below"] else None
        liq_price = entry * (1 + 1 / lev - 0.005)
        liq_safe = stop < liq_price

    risk = abs(entry - stop)
    if risk <= 0:
        out.update(status="WAIT", reason="degenerált stop (risk<=0)")
        return out
    rr1 = round(abs(tp1 - entry) / risk, 2)
    target_big = big["price"] if big else None
    rr_big = round(abs(target_big - entry) / risk, 2) if target_big else None
    # a "nagy mozgás" kapu: a nagy mágnesnek legalább rr_big_min R-re kell lennie,
    # különben a kockázathoz képest nincs mit megfogni -> WAIT (ez öli meg a
    # tág-stop + közeli-cél aszimmetriát, amit a backtest kimutatott)
    rr_big_min = float(sc.get("rr_big_min", 1.5))
    if rr_big is not None and rr_big < rr_big_min:
        out.update(status="WAIT",
                   reason=f"nagy cél csak {rr_big}R (kell ≥{rr_big_min}R) — a mozgás "
                          f"nem nagy a kockázathoz képest")
        return out
    out.update(status="ARMED", entry=round(entry, 1), entry_type=entry_type,
               stop=round(stop, 1), risk=round(risk, 1),
               tp1=round(tp1, 1), tp1_frac=tp1_frac, rr1=rr1,
               target_big=(round(target_big, 1) if target_big else None), rr_big=rr_big,
               trail=f"Donchian({don}) {'low' if side == 'LONG' else 'high'} + BE TP1 után",
               bet_usd=bet, leverage=lev, notional=round(bet * lev, 1),
               qty=round(bet * lev / entry, 6),
               liq_price=round(liq_price, 1), liq_safe=liq_safe,
               plan_note=(f"{int(tp1_frac * 100)}% zárás TP1-nél + stop BE; a runner a "
                          f"Donchian({don})-t követi — a havi mozgást NEM vágjuk le fix T2-nél"))
    return out
