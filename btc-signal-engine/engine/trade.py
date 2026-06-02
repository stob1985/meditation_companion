"""
Trading layer.
====================================================================
Turns the DIRECTION (composite bias) + the LIQUIDITY MAP + the DWELL BLOCKS
into a concrete, checkable trade plan:

  entry / stop / target   with   R:R >= rr_min (default 1:3)
  position size           with   FIXED collateral (USD) x LEVERAGE  (10/25/50/100x)
  liquidation price       + a hard check that the STOP triggers BEFORE liquidation.

Level logic
-----------
LONG (bias UP):
  - stop   = just BELOW the nearest support below price
             (nearest of: dwell block, liquidity cluster, else ATR fallback).
  - target = nearest short-liquidation magnet ABOVE that yields >= rr_min;
             if none reaches it, a projected entry + rr_min*risk level (flagged).
SHORT (bias DOWN): mirror image.
FLAT: no trade.

Sizing (fixed bet + leverage, per the user's choice / the video style)
----------------------------------------------------------------------
  notional = bet_usd * leverage ;  qty = notional / entry
  loss_at_stop   = qty * |entry-stop| ;  profit_at_target = qty * |target-entry|
  liq_price(LONG)  = entry * (1 - 1/lev + mmr)
  liq_price(SHORT) = entry * (1 + 1/lev + mmr)   # +mmr -> liq sits a touch further out
Safety: at high leverage the liquidation can sit INSIDE the stop, so the
position dies before the stop fires. We flag that and compute the max leverage
tier that keeps liquidation beyond the stop.

NOTE: educational, not financial advice. Proxy liquidity, daily-bar structure.
"""
from __future__ import annotations


def _nearest_support(price, liq, dwell, side="below"):
    """Collect candidate support(below)/resistance(above) levels with a label."""
    cands = []
    clusters = liq["clusters_below"] if side == "below" else liq["clusters_above"]
    for c in clusters:
        cands.append((c["price"], f"liq x{c['count']} {c['tiers']}"))
    if not dwell.get("empty", True):
        blk = dwell.get("nearest_below") if side == "below" else dwell.get("nearest_above")
        if blk:
            edge = blk["hi"] if side == "below" else blk["lo"]
            cands.append((edge, f"dwell block {blk['lo']}-{blk['hi']} ({blk['dwell']}%)"))
    if side == "below":
        cands = [c for c in cands if c[0] < price]
        cands.sort(key=lambda x: price - x[0])          # closest below first
    else:
        cands = [c for c in cands if c[0] > price]
        cands.sort(key=lambda x: x[0] - price)          # closest above first
    return cands


def _pick_target(entry, risk, side, liq, dwell, rr_min):
    """Nearest liquidation magnet that gives >= rr_min; else projected level."""
    need = rr_min * risk
    floor_hi = entry + need if side == "LONG" else None
    floor_lo = entry - need if side == "SHORT" else None
    mags = liq["clusters_above"] if side == "LONG" else liq["clusters_below"]
    qualifying = []
    for c in mags:
        dist = (c["price"] - entry) if side == "LONG" else (entry - c["price"])
        if dist >= need:
            qualifying.append((c["price"], dist, f"magnet x{c['count']} {c['tiers']}"))
    if qualifying:
        # nearest qualifying magnet = most achievable structural target
        qualifying.sort(key=lambda x: x[1])
        price_, dist_, src = qualifying[0]
        return price_, src, False
    # no structural magnet far enough -> project the minimum rr target
    proj = floor_hi if side == "LONG" else floor_lo
    return round(proj, 1), f"projected {rr_min:.0f}R (no magnet >= {rr_min:.0f}R)", True


def plan(sig: dict, liq: dict, dwell: dict, cfg: dict) -> dict:
    tc = cfg.get("trade", {})
    rr_min = float(tc.get("rr_min", 3.0))
    bet_usd = float(tc.get("bet_usd", 100))
    lev = int(tc.get("leverage", 25))
    tiers = list(tc.get("leverage_tiers", [10, 25, 50, 100]))
    mmr = float(tc.get("mmr", 0.005))
    buf = float(tc.get("stop_buffer_atr", 0.25))
    fb = float(tc.get("stop_fallback_atr", 1.5))

    price = float(sig["price"])
    atr = float(liq["atr"])
    bias = sig["bias"]
    warnings = []

    if bias == "FLAT":
        return dict(side="FLAT", reason="composite bias is FLAT - stand aside",
                    bias=bias, strength=sig["strength"])

    side = "LONG" if bias == "UP" else "SHORT"

    # ---- stop from nearest structure -----------------------------------
    sup = _nearest_support(price, liq, dwell, "below" if side == "LONG" else "above")
    if sup:
        anchor, stop_src = sup[0]
        stop = anchor - buf * atr if side == "LONG" else anchor + buf * atr
        stop_src = f"{stop_src} {'-' if side == 'LONG' else '+'}{buf}ATR"
    else:
        stop = price - fb * atr if side == "LONG" else price + fb * atr
        stop_src = f"ATR fallback ({fb}xATR, no structure)"
    stop = round(stop, 1)
    risk = abs(price - stop)
    if risk <= 0:
        return dict(side=side, reason="degenerate stop (risk<=0)", bias=bias)

    # ---- target from liquidity magnets ---------------------------------
    target, target_src, projected = _pick_target(price, risk, side, liq, dwell, rr_min)
    reward = abs(target - price)
    rr = round(reward / risk, 2)

    # ---- position sizing: fixed bet x leverage -------------------------
    notional = bet_usd * lev
    qty = notional / price
    loss_usd = qty * risk
    profit_usd = qty * reward
    risk_pct = loss_usd / bet_usd * 100

    # ---- liquidation + safety -----------------------------------------
    if side == "LONG":
        liq_price = price * (1 - 1 / lev + mmr)
        liq_dist = price - liq_price
        liq_safe = stop > liq_price
    else:
        liq_price = price * (1 + 1 / lev - mmr)
        liq_dist = liq_price - price
        liq_safe = stop < liq_price
    liq_price = round(liq_price, 1)

    # max leverage tier that keeps liquidation beyond the stop (with the buffer)
    stop_move = risk / price                          # fractional distance to stop
    max_lev_raw = 1.0 / (stop_move + mmr) if (stop_move + mmr) > 0 else 0
    safe_tiers = [t for t in tiers if t <= max_lev_raw]
    max_safe_leverage = max(safe_tiers) if safe_tiers else 0

    if not liq_safe:
        warnings.append(
            f"LIQUIDATION INSIDE STOP at {lev}x: position liquidates at "
            f"{liq_price} before the stop {stop}. Max safe tier ~{max_safe_leverage}x "
            f"(raw {max_lev_raw:.0f}x).")
    if projected:
        warnings.append("Target is a projected R-multiple, not a liquidity magnet "
                        "- weaker confluence, may not be reached.")
    if rr < rr_min:
        warnings.append(f"R:R {rr} is below the {rr_min} floor.")

    # confluence: does the composite agree with the liquidity imbalance?
    imb = liq["imbalance"]
    agree = (("BULL" in imb and side == "LONG") or ("BEAR" in imb and side == "SHORT"))
    confluence = "ALIGNED" if agree else "MIXED"

    return dict(
        side=side, bias=bias, strength=sig["strength"], confluence=confluence,
        entry=round(price, 1), stop=stop, target=target,
        stop_src=stop_src, target_src=target_src, projected=projected,
        risk=round(risk, 1), reward=round(reward, 1), rr=rr, rr_min=rr_min,
        leverage=lev, bet_usd=bet_usd, notional=round(notional, 1), qty=round(qty, 6),
        loss_usd=round(loss_usd, 2), profit_usd=round(profit_usd, 2),
        risk_pct=round(risk_pct, 1),
        liq_price=liq_price, liq_safe=liq_safe, liq_dist=round(liq_dist, 1),
        max_safe_leverage=max_safe_leverage,
        dwell_state=dwell.get("state"), warnings=warnings)
