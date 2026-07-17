"""
DrProfit Framework Layer — TA / LCA / Psychological Breakdown

Integrates Doctor Profit's (@DrProfitCrypto) macro swing-trading methodology
into the composite signal. Three pillars:

  1. BOX POSITION   — where is price relative to the macro consolidation range?
                      (auto-detected from dwell value area)
  2. STAGE          — which of the 6 bear/bull stages is the market in?
                      (auto-inferred from MTF, ATH distance, OI, volatility)
  3. CROWD PSYCH    — contrarian read from L/S ratio, funding, OI direction
                      (from realflow + liquidity modules)

Output bias:
  UP   → price at box bottom border + crowd bearish + early stage
  DOWN → price at box top border + crowd long-heavy + late stage (4-5)
  NEUTRAL → price mid-box or signals conflicting → DO NOTHING (DrProfit rule)

NOTE: the 10% DCA zone detection tells whether price is currently
inside one of DrProfit's documented entry zones (short or long).
"""
from __future__ import annotations
import numpy as np
import pandas as pd


# ── Stage inference ────────────────────────────────────────────────────────────
_STAGE_LABELS = {
    1: "DISTRIBUTION (ATH area — sell spot / begin shorts)",
    2: "FIRST DROP (retail dip-buys — hold shorts)",
    3: "BULL TRAP RALLY (add shorts at top — 10%/day)",
    4: "SECOND LEG DOWN (partial profit-taking)",
    5: "MAX PAIN (violent swings — exchange risk — hold shorts)",
    6: "CBB — Confirmed BlackRock Bottom (close shorts / accumulate spot)",
}

def _infer_stage(df: pd.DataFrame, realflow: dict | None, cfg: dict) -> int:
    """
    Auto-infer DrProfit's 6-stage bear market position from available signals.
    Falls back to cfg['drprofit']['stage'] if set to a non-zero value (manual override).
    """
    manual = int(cfg.get("drprofit", {}).get("stage", 0))
    if manual > 0:
        return manual  # manual override wins

    close = df["close"]
    px = float(close.iloc[-1])

    # ATH distance
    ath = float(close.max())
    ath_dist = (ath - px) / ath  # 0 = at ATH, 0.5 = 50% below ATH

    # multi-EMA trend score
    emas = [close.ewm(span=s).mean().iloc[-1] for s in (10, 20, 50, 100, 200)]
    mtf = sum(1 if px > e else -1 for e in emas)  # -5 .. +5

    # volatility (ATR/price as %)
    highs = df["high"]; lows = df["low"]; closes = df["close"]
    tr = pd.concat([highs - lows,
                    (highs - closes.shift()).abs(),
                    (lows  - closes.shift()).abs()], axis=1).max(axis=1)
    atr_val = tr.ewm(alpha=1/14, adjust=False).mean().iloc[-1]
    vol_pct = atr_val / px  # relative volatility

    # crowd long/short ratio
    ls_raw = (realflow or {}).get("ls_ratio", 1.0)
    ls = float(ls_raw["ratio"] if isinstance(ls_raw, dict) else ls_raw)
    oi_raw = (realflow or {}).get("oi", {})
    oi_trend = str(oi_raw.get("trend", "flat") if isinstance(oi_raw, dict) else oi_raw).lower()

    # --- heuristic stage mapping ---
    # Stage 6: CBB — price near multi-year support, extreme fear, low vol
    if ath_dist > 0.60 and mtf <= -4 and ls < 0.9:
        return 6
    # Stage 5: max pain — strong bear, high vol, crowd still long
    if mtf <= -3 and ath_dist > 0.35 and vol_pct > 0.025 and ls > 1.3:
        return 5
    # Stage 4: second leg down — bear trend, moderate crowd long
    if mtf <= -2 and ath_dist > 0.25:
        return 4
    # Stage 3: bull trap rally — price recovered but still below key EMAs
    if -2 < mtf <= 0 and ath_dist > 0.15:
        return 3
    # Stage 2: first drop — just turned bear
    if mtf < 0 and ath_dist < 0.20:
        return 2
    # Stage 1: distribution — near ATH
    if ath_dist < 0.10 and mtf >= 2:
        return 1
    # Default: mid-cycle
    return 3


# ── Box detection ──────────────────────────────────────────────────────────────
def _box_position(px: float, dwell: dict | None, cfg: dict) -> dict:
    """
    Determine where price sits relative to the macro box.
    DrProfit rule: trade only at the BORDERS (top/bottom 15%).
    Mid-box = DO NOTHING.
    """
    drp_cfg = cfg.get("drprofit", {})

    # prefer dwell value area (auto) over manual config
    if dwell and not dwell.get("empty"):
        box_lo = float(dwell.get("value_area_lo", drp_cfg.get("box_low", 0)))
        box_hi = float(dwell.get("value_area_hi", drp_cfg.get("box_high", 0)))
    else:
        box_lo = float(drp_cfg.get("box_low", 0))
        box_hi = float(drp_cfg.get("box_high", 0))

    if box_hi <= box_lo or box_lo == 0:
        return {"zone": "UNKNOWN", "box_lo": box_lo, "box_hi": box_hi,
                "box_pct": None, "border": False}

    box_range = box_hi - box_lo
    border_pct = float(drp_cfg.get("box_border_pct", 0.15))
    border_band = box_range * border_pct

    # position within box: 0.0 = bottom, 1.0 = top
    box_pct = (px - box_lo) / box_range

    if px <= box_lo + border_band:
        zone = "BOTTOM BORDER"   # buy zone
        border = True
    elif px >= box_hi - border_band:
        zone = "TOP BORDER"      # short zone
        border = True
    elif box_pct < 0.5:
        zone = "LOWER HALF"
        border = False
    else:
        zone = "UPPER HALF"
        border = False

    return {"zone": zone, "box_lo": box_lo, "box_hi": box_hi,
            "box_pct": round(box_pct * 100, 1), "border": border}


# ── Crowd psychology read ──────────────────────────────────────────────────────
def _crowd_read(realflow: dict | None, cfg: dict) -> dict:
    """
    Contrarian crowd sentiment — DrProfit's psychological layer.
    Heavy crowd LONG → bearish signal (contra).
    Heavy crowd SHORT / capitulation → bullish signal (contra).
    """
    if not realflow:
        return {"sentiment": "UNKNOWN", "contra_bias": "NEUTRAL", "ls": None}

    ls_raw = realflow.get("ls_ratio", 1.0)
    ls = float(ls_raw["ratio"] if isinstance(ls_raw, dict) else ls_raw)
    funding_raw = realflow.get("funding", {})
    funding = float(funding_raw.get("funding", 0.0) if isinstance(funding_raw, dict) else funding_raw)
    oi_raw = realflow.get("oi", {})
    oi_trend = str(oi_raw.get("trend", "flat") if isinstance(oi_raw, dict) else oi_raw).lower()
    ls_hot = float(cfg.get("drprofit", {}).get("crowd_ls_hot", 1.5))

    # crowd heavily long → contrarian bearish
    if ls > ls_hot:
        sentiment = f"CROWD LONG-HEAVY (L/S {ls:.2f}) → CONTRA BEARISH"
        contra_bias = "DOWN"
    # capitulation — crowd exiting longs
    elif ls < 0.85:
        sentiment = f"CAPITULATION (L/S {ls:.2f}) → CONTRA BULLISH"
        contra_bias = "UP"
    else:
        sentiment = f"BALANCED (L/S {ls:.2f})"
        contra_bias = "NEUTRAL"

    # funding confirms
    funding_hot = float(cfg.get("drprofit", {}).get("funding_hot", 2e-5))
    if funding > funding_hot and contra_bias == "DOWN":
        sentiment += " + FUNDING HOT"
    elif funding < -1e-5 and contra_bias == "UP":
        sentiment += " + FUNDING NEG (bearish exit)"

    return {"sentiment": sentiment, "contra_bias": contra_bias,
            "ls": ls, "funding": funding, "oi_trend": oi_trend}


# ── DCA zone detection ─────────────────────────────────────────────────────────
def _dca_zone(px: float, cfg: dict) -> dict:
    """
    Is the current price inside one of DrProfit's documented DCA entry zones?
    If yes: which side (short/long) and which zone.
    DrProfit's method: add 10% of position each day price stays in the zone.
    """
    drp_cfg = cfg.get("drprofit", {})
    zones = drp_cfg.get("dca_zones", {})

    for side in ("short", "long"):
        for zone in zones.get(side, []):
            lo, hi = float(zone[0]), float(zone[1])
            if lo <= px <= hi:
                return {
                    "active": True,
                    "side": side.upper(),
                    "zone": f"{lo:,.0f}–{hi:,.0f}",
                    "instruction": f"Add 10% of {side} position today (DrProfit DCA method)"
                }
    return {"active": False, "side": None, "zone": None, "instruction": "Price outside all DCA zones — WAIT"}


# ── Main entry point ───────────────────────────────────────────────────────────
def analyze(df: pd.DataFrame, cfg: dict,
            dwell: dict | None = None,
            realflow: dict | None = None) -> dict:
    """
    Run the full DrProfit framework layer.

    Returns:
        stage       int 1-6
        stage_label str
        box         dict (zone, box_lo, box_hi, box_pct, border)
        crowd       dict (sentiment, contra_bias, ls, funding)
        dca         dict (active, side, zone, instruction)
        drp_bias    str UP / DOWN / NEUTRAL
        drp_up      float 0.0-1.0  (probability for composite blending)
        summary     str  one-liner for dashboard
    """
    px = float(df["close"].iloc[-1])

    stage = _infer_stage(df, realflow, cfg)
    box   = _box_position(px, dwell, cfg)
    crowd = _crowd_read(realflow, cfg)
    dca   = _dca_zone(px, cfg)

    # ── Composite DrProfit bias ────────────────────────────────────────────────
    # Rules (in priority order):
    # 1. Stage 5-6 + crowd long-heavy + top border → STRONG DOWN
    # 2. Stage 5-6 + bottom border + capitulation → UP (CBB approach)
    # 3. Mid-box (not border) → NEUTRAL (DrProfit rule: do nothing)
    # 4. Otherwise blend crowd + box position

    votes_up = 0.0
    votes_total = 0.0

    # box position vote
    if box["zone"] == "BOTTOM BORDER":
        votes_up += 0.75; votes_total += 1.0
    elif box["zone"] == "TOP BORDER":
        votes_up += 0.25; votes_total += 1.0
    elif box["zone"] in ("LOWER HALF", "UPPER HALF"):
        # mid-box: no vote, low weight (DrProfit: don't trade the middle)
        votes_total += 0.3

    # crowd psychology vote
    if crowd["contra_bias"] == "UP":
        votes_up += 0.75; votes_total += 1.0
    elif crowd["contra_bias"] == "DOWN":
        votes_up += 0.25; votes_total += 1.0

    # stage vote
    if stage in (1, 2, 3):
        # early bear or distribution — bearish
        votes_up += 0.30; votes_total += 1.0
    elif stage == 4:
        votes_up += 0.35; votes_total += 1.0
    elif stage == 5:
        # max pain — stay bearish but violent swings possible
        votes_up += 0.25; votes_total += 1.0
    elif stage == 6:
        # CBB — accumulate spot
        votes_up += 0.80; votes_total += 1.0

    drp_up = (votes_up / votes_total) if votes_total > 0 else 0.5

    # force NEUTRAL if mid-box and no strong crowd signal
    if not box["border"] and crowd["contra_bias"] == "NEUTRAL":
        drp_bias = "NEUTRAL"
        drp_up = 0.5
    elif drp_up >= 0.60:
        drp_bias = "UP"
    elif drp_up <= 0.40:
        drp_bias = "DOWN"
    else:
        drp_bias = "NEUTRAL"

    # one-liner for dashboard
    summary = (
        f"Stage {stage}/6 · Box {box['zone']} ({box['box_pct']}%) · "
        f"{crowd['sentiment'].split('→')[0].strip()} · "
        f"DCA: {dca['zone'] or 'WAIT'} · Bias: {drp_bias}"
    )

    return dict(
        stage=stage,
        stage_label=_STAGE_LABELS.get(stage, "UNKNOWN"),
        box=box,
        crowd=crowd,
        dca=dca,
        drp_bias=drp_bias,
        drp_up=round(drp_up, 3),
        summary=summary,
    )
