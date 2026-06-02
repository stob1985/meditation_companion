"""
Trading layer.
====================================================================
Turns the DIRECTION (composite bias) + the LIQUIDITY MAP + the DWELL BLOCKS
into a concrete, checkable trade plan:

  entry / stop / target   with   R:R >= rr_min (default 1:3)
  position size           with   FIXED collateral (USD) x LEVERAGE  (10/25/50/100x)
  liquidation price       + a hard check that the STOP triggers BEFORE liquidation
  net P/L                 after taker fees + estimated funding

Accuracy / realism upgrades distilled from the ChentoTrades transcript:
  - TIERED maintenance margin (higher leverage liquidates earlier).
  - FEES + FUNDING folded into the P/L so expectancy is honest.
  - VOID / no-trade zones: if price sits in a thin area far from any dwell block
    or liquidity cluster, there is nothing to trade against -> stand aside.
  - REGIME HEDGE: in a range / equilibrium (flat MTF, weak bias, mid-block dwell)
    it returns BOTH a long and a short leg with a net lean, the way the trader
    hedges when there is no clean swing.
  - FRESH magnets preferred as targets (heavily-tapped levels are "worn").

NOTE: educational, not financial advice. Proxy liquidity, daily-bar structure.
"""
from __future__ import annotations


def _mmr(lev, cfg):
    tiers = cfg.get("trade", {}).get("mmr_tiers", {})
    return float(tiers.get(lev, tiers.get(str(lev), cfg.get("trade", {}).get("mmr", 0.005))))


def _nearest_support(price, liq, dwell, side="below"):
    """Candidate support(below)/resistance(above) levels with a label."""
    cands = []
    clusters = liq["clusters_below"] if side == "below" else liq["clusters_above"]
    for c in clusters:
        cands.append((c["price"], f"liq x{c['count']} {c['tiers']}"))
    if dwell and not dwell.get("empty", True):
        blk = dwell.get("nearest_below") if side == "below" else dwell.get("nearest_above")
        if blk:
            edge = blk["hi"] if side == "below" else blk["lo"]
            cands.append((edge, f"dwell block {blk['lo']}-{blk['hi']} ({blk['dwell']}%)"))
    if side == "below":
        cands = [c for c in cands if c[0] < price]
        cands.sort(key=lambda x: price - x[0])
    else:
        cands = [c for c in cands if c[0] > price]
        cands.sort(key=lambda x: x[0] - price)
    return cands


def _pick_target(entry, risk, side, liq, dwell, rr_min, mode="rr", atr=None):
    """Pick the target liquidation cluster.
    mode 'rr'      : nearest magnet that meets R:R >= rr_min (then dwell/projected).
    mode 'nearest' : the nearest cluster in the trade direction regardless of R:R
                     (data shows the nearest directional cluster is reached most
                     often at high conviction). Keeps a small ATR floor."""
    mags = liq["clusters_above"] if side == "LONG" else liq["clusters_below"]
    if mode == "nearest":
        floor = 0.3 * atr if atr else 0.0
        cand = []
        for c in mags:
            dist = (c["price"] - entry) if side == "LONG" else (entry - c["price"])
            if dist >= floor:
                cand.append((c["price"], dist, f"nearest x{c['count']} {c['tiers']}"))
        if cand:
            cand.sort(key=lambda x: x[1])
            return cand[0][0], cand[0][2], False
        # fall through to projected if nothing usable
    need = rr_min * risk
    mags = liq["clusters_above"] if side == "LONG" else liq["clusters_below"]
    qualifying = []
    for c in mags:
        dist = (c["price"] - entry) if side == "LONG" else (entry - c["price"])
        if dist >= need:
            fresh = c.get("fresh", True)
            taps = c.get("taps", 0)
            label = f"magnet x{c['count']} {c['tiers']}" + ("" if fresh else f" (worn {taps}x)")
            qualifying.append((c["price"], dist, fresh, taps, label))
    if qualifying:
        # nearest achievable magnet wins; worn levels get a mild distance penalty
        # (they tend to break rather than cleanly reject - "power of three").
        qualifying.sort(key=lambda x: x[1] * (1.0 if x[2] else 1.25))
        price_, dist_, fresh_, taps_, src = qualifying[0]
        return price_, src, False
    # dwell shift-out target if it satisfies rr_min
    if dwell and not dwell.get("empty") and dwell.get("dwell_target"):
        dt = dwell["dwell_target"]
        dist = (dt - entry) if side == "LONG" else (entry - dt)
        if dist >= need:
            return round(dt, 1), f"dwell {dwell.get('dwell_target_src', 'shift-out')}", False
    proj = entry + need if side == "LONG" else entry - need
    return round(proj, 1), f"projected {rr_min:.0f}R (no magnet >= {rr_min:.0f}R)", True


def _build_side(side, price, atr, liq, dwell, cfg, bet_override=None):
    """Core entry/stop/target + sizing + liquidation for one direction.
    bet_override lets the hedge size each leg independently (net-directional)."""
    tc = cfg.get("trade", {})
    rr_min = float(tc.get("rr_min", 3.0))
    bet_usd = float(bet_override) if bet_override is not None else float(tc.get("bet_usd", 100))
    lev = int(tc.get("leverage", 25))
    tiers = list(tc.get("leverage_tiers", [10, 25, 50, 100]))
    buf = float(tc.get("stop_buffer_atr", 0.25))
    fb = float(tc.get("stop_fallback_atr", 1.5))
    taker = float(tc.get("taker_fee", 0.0005))
    fund_d = float(tc.get("funding_daily", 0.0003))
    hold_d = float(cfg.get("signal", {}).get("horizon", 3))
    mmr = _mmr(lev, cfg)
    warnings = []

    # stop from nearest structure
    sup = _nearest_support(price, liq, dwell, "below" if side == "LONG" else "above")
    if sup:
        anchor, stop_src = sup[0]
        stop = anchor - buf * atr if side == "LONG" else anchor + buf * atr
        stop_src = f"{stop_src} {'-' if side == 'LONG' else '+'}{buf}ATR"
    else:
        stop = price - fb * atr if side == "LONG" else price + fb * atr
        stop_src = f"ATR fallback ({fb}xATR)"
    stop = round(stop, 1)
    risk = abs(price - stop)
    if risk <= 0:
        return None

    target, target_src, projected = _pick_target(
        price, risk, side, liq, dwell, rr_min,
        mode=tc.get("target_mode", "rr"), atr=atr)
    reward = abs(target - price)
    rr = round(reward / risk, 2)

    # sizing: fixed bet x leverage
    notional = bet_usd * lev
    qty = notional / price
    gross_loss = qty * risk
    gross_profit = qty * reward
    fees = 2 * taker * notional
    funding = fund_d * notional * hold_d
    net_profit = gross_profit - fees - funding
    net_loss = gross_loss + fees + funding
    net_rr = round(net_profit / net_loss, 2) if net_loss > 0 else None
    risk_pct = net_loss / bet_usd * 100

    # liquidation + safety (tiered MMR)
    if side == "LONG":
        liq_price = price * (1 - 1 / lev + mmr)
        liq_dist = price - liq_price
        liq_safe = stop > liq_price
    else:
        liq_price = price * (1 + 1 / lev - mmr)
        liq_dist = liq_price - price
        liq_safe = stop < liq_price
    liq_price = round(liq_price, 1)

    stop_move = risk / price
    max_lev_raw = 1.0 / (stop_move + mmr) if (stop_move + mmr) > 0 else 0
    safe_tiers = [t for t in tiers if t <= max_lev_raw]
    max_safe_leverage = max(safe_tiers) if safe_tiers else 0

    if not liq_safe:
        warnings.append(f"LIQUIDATION INSIDE STOP at {lev}x: liquidates {liq_price} "
                        f"before stop {stop}. Max safe ~{max_safe_leverage}x.")
    if projected:
        warnings.append("Target is a projected R-multiple, not a magnet - weaker confluence.")
    if net_rr is not None and net_rr < rr_min:
        warnings.append(f"NET R:R {net_rr} (after fees/funding) below the {rr_min} floor.")

    return dict(side=side, entry=round(price, 1), stop=stop, target=target,
                stop_src=stop_src, target_src=target_src, projected=projected,
                risk=round(risk, 1), reward=round(reward, 1), rr=rr, net_rr=net_rr,
                rr_min=rr_min, leverage=lev, bet_usd=bet_usd, mmr=mmr,
                notional=round(notional, 1), qty=round(qty, 6),
                gross_profit=round(gross_profit, 2), gross_loss=round(gross_loss, 2),
                fees=round(fees, 2), funding=round(funding, 2),
                net_profit=round(net_profit, 2), net_loss=round(net_loss, 2),
                risk_pct=round(risk_pct, 1),
                liq_price=liq_price, liq_safe=liq_safe, liq_dist=round(liq_dist, 1),
                max_safe_leverage=max_safe_leverage, warnings=warnings)


def plan(sig: dict, liq: dict, dwell: dict, cfg: dict) -> dict:
    tc = cfg.get("trade", {})
    void_atr = float(tc.get("void_atr", 2.0))
    price = float(sig["price"])
    atr = float(liq["atr"])
    bias = sig["bias"]
    dwell = dwell or {}

    # ---- confluence read (dwell rule + CVD flow + liquidity imbalance) ----
    conf_parts = []
    db = dwell.get("dwell_bias") if not dwell.get("empty") else None
    if db and db != "NEUTRAL":
        conf_parts.append(("dwell", db))
    fl = sig.get("flow", {})
    if fl.get("bias") in ("LONG", "SHORT"):
        conf_parts.append(("flow", "UP" if fl["bias"] == "LONG" else "DOWN"))
    imb = liq.get("imbalance", "")
    if "BULL" in imb:
        conf_parts.append(("liq", "UP"))
    elif "BEAR" in imb:
        conf_parts.append(("liq", "DOWN"))

    def _confluence(side_dir):
        agree = sum(1 for _, d in conf_parts if d == side_dir)
        total = len(conf_parts)
        return f"{agree}/{total} aligned" if total else "n/a"

    if bias == "FLAT":
        return dict(side="FLAT", reason="composite bias is FLAT - stand aside",
                    bias=bias, strength=sig["strength"])

    # ---- void / no-trade zone --------------------------------------------
    d_clu = None
    nb = (liq["clusters_above"] + liq["clusters_below"])
    if nb:
        d_clu = min(abs(c["price"] - price) for c in nb)
    inside_block = bool(dwell.get("ref_block") and dwell.get("location") == "MID")
    if dwell.get("ref_block") and not inside_block:
        rb = dwell["ref_block"]
        d_blk = min(abs(price - rb["lo"]), abs(price - rb["hi"]))
    else:
        d_blk = 0.0 if inside_block else None
    dists = [x for x in (d_clu, d_blk) if x is not None]
    nearest_struct = min(dists) / atr if dists else 99.0
    if nearest_struct > void_atr:
        return dict(side="VOID", reason=f"no structure within {void_atr} ATR "
                    f"(nearest {nearest_struct:.1f} ATR) - travel zone, stand aside",
                    bias=bias, strength=sig["strength"])

    side = "LONG" if bias == "UP" else "SHORT"

    # ---- regime filter: don't fight a STRONG trend ----------------------
    if tc.get("regime_filter", False):
        reg = sig.get("regime", "")
        if (side == "LONG" and reg == "STRONG BEAR") or (side == "SHORT" and reg == "STRONG BULL"):
            return dict(side="REGIME-VETO", bias=bias, strength=sig["strength"],
                        reason=f"bias {bias} fights regime {reg} - stand aside")

    # ---- regime hedge: range / equilibrium -> trade both sides -----------
    range_regime = (abs(sig.get("mtf", 0)) <= 1) and sig["strength"] in ("WEAK", "MODERATE")
    coiling_mid = (dwell.get("state") == "COILING" and dwell.get("location") == "MID")
    if tc.get("enable_hedge", True) and (range_regime or coiling_mid):
        base_bet = float(tc.get("bet_usd", 100))
        max_ratio = float(tc.get("hedge_max_ratio", 6.0))
        lean = sig["up"] - 50.0                        # composite tilt, in % points
        # net-directional sizing: the favoured leg keeps the full bet, the other
        # is scaled down by the ratio (so e.g. a strong lean -> ~6:1 like the desk).
        ratio = round(1.0 + (max_ratio - 1.0) * min(1.0, abs(lean) / 15.0), 1)
        if lean >= 0:
            long_bet, short_bet, heavy = base_bet, base_bet / ratio, "long"
        else:
            long_bet, short_bet, heavy = base_bet / ratio, base_bet, "short"
        long_leg = _build_side("LONG", price, atr, liq, dwell, cfg, bet_override=long_bet)
        short_leg = _build_side("SHORT", price, atr, liq, dwell, cfg, bet_override=short_bet)
        if long_leg and short_leg:
            net_notional = long_leg["notional"] - short_leg["notional"]
            net_side = "LONG" if net_notional > 0 else "SHORT" if net_notional < 0 else "FLAT"
            lean_label = "balanced" if abs(lean) < 3 else f"net {heavy} {ratio:.1f}:1"
            return dict(side="HEDGE", bias=bias, strength=sig["strength"],
                        reason="range/equilibrium - no clean swing; hedge both sides",
                        net_lean=lean_label, net_side=net_side,
                        net_notional=round(abs(net_notional), 1),
                        long_leg=long_leg, short_leg=short_leg,
                        confluence=_confluence(side), dwell_state=dwell.get("state"))

    out = _build_side(side, price, atr, liq, dwell, cfg)
    if out is None:
        return dict(side=side, reason="degenerate stop (risk<=0)", bias=bias)
    out.update(bias=bias, strength=sig["strength"],
               confluence=_confluence("UP" if side == "LONG" else "DOWN"),
               dwell_state=dwell.get("state"),
               flow=fl.get("agree", "n/a"))
    return out
