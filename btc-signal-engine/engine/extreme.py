"""
EXTREME DETECTOR + ARMED logic.

The system's core philosophy change: instead of a daily signal machine,
this layer detects the 4-8 moments per year when the market is at a true
extreme and a large asymmetric move is statistically favored.

5 signals (+1 best-effort external):
  1. CROWD     — L/S ratio extreme (crowd heavily one-sided)
  2. FUNDING   — funding rate extreme (overheated longs / capitulating shorts)
  3. BOX       — price at the macro box border (outer band)
  4. RSI       — daily RSI at a true extreme
  5. CASCADE   — liquidation cascade (mass forced exits)
  6. FEAR&GREED (external, best-effort) — alternative.me index at extreme

ARMED = at least `arm_min` (default 3) signals active simultaneously.
When not ARMED the correct output is: "NO SETUP — do nothing."
"""
from __future__ import annotations
import json
import urllib.request
import pandas as pd


def _fng(timeout: int = 6) -> dict | None:
    """Fear & Greed index from alternative.me (free, no key). Best-effort."""
    try:
        req = urllib.request.Request(
            "https://api.alternative.me/fng/?limit=1",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
        v = int(data["data"][0]["value"])
        label = data["data"][0]["value_classification"]
        return {"value": v, "label": label}
    except Exception:
        return None


def detect(df: pd.DataFrame, cfg: dict, sig: dict,
           realflow: dict | None, drp: dict | None) -> dict:
    """
    Evaluate all extreme signals. Returns ARMED status + direction.
    Direction is CONTRARIAN at extremes (crowd long -> short setup).
    """
    ex_cfg = cfg.get("extreme", {})
    arm_min = int(ex_cfg.get("arm_min", 3))
    signals = []          # (name, active, direction, detail)

    # ── 1. CROWD extreme (contrarian) ──────────────────────────────────────
    ls = None
    if realflow:
        ls_raw = realflow.get("ls_ratio")
        if isinstance(ls_raw, dict):
            ls = float(ls_raw.get("ratio", 1.0))
        elif ls_raw is not None:
            ls = float(ls_raw)
    ls_long_x = float(ex_cfg.get("ls_long_extreme", 1.8))
    ls_short_x = float(ex_cfg.get("ls_short_extreme", 0.80))
    if ls is not None and ls >= ls_long_x:
        signals.append(("CROWD", True, "DOWN", f"L/S {ls:.2f} ≥ {ls_long_x} (tömeg long)"))
    elif ls is not None and ls <= ls_short_x:
        signals.append(("CROWD", True, "UP", f"L/S {ls:.2f} ≤ {ls_short_x} (tömeg short/kapituláció)"))
    else:
        signals.append(("CROWD", False, None, f"L/S {ls:.2f} — nem extrém" if ls else "n/a"))

    # ── 2. FUNDING extreme (contrarian) ────────────────────────────────────
    fnd = None
    if realflow:
        f_raw = realflow.get("funding")
        if isinstance(f_raw, dict):
            fnd = float(f_raw.get("funding", 0.0))
        elif f_raw is not None:
            fnd = float(f_raw)
    f_hot = float(ex_cfg.get("funding_hot", 5.0e-5))
    f_neg = float(ex_cfg.get("funding_capitulation", -2.0e-5))
    if fnd is not None and fnd >= f_hot:
        signals.append(("FUNDING", True, "DOWN", f"funding {fnd:.1e} ≥ {f_hot:.0e} (túlfűtött long)"))
    elif fnd is not None and fnd <= f_neg:
        signals.append(("FUNDING", True, "UP", f"funding {fnd:.1e} ≤ {f_neg:.0e} (short-kapituláció)"))
    else:
        signals.append(("FUNDING", False, None,
                        f"funding {fnd:.1e} — semleges" if fnd is not None else "n/a"))

    # ── 3. BOX border (DrProfit: csak a széleken van üzlet) ────────────────
    box = (drp or {}).get("box", {})
    if box.get("border"):
        d = "UP" if box.get("zone") == "BOTTOM BORDER" else "DOWN"
        signals.append(("BOX", True, d, f"{box['zone']} ({box.get('box_pct')}%)"))
    else:
        signals.append(("BOX", False, None,
                        f"{box.get('zone','?')} ({box.get('box_pct','?')}%) — nem szél"))

    # ── 4. RSI daily extreme ───────────────────────────────────────────────
    rsi = float(sig.get("rsi", 50))
    rsi_lo = float(ex_cfg.get("rsi_extreme_low", 25))
    rsi_hi = float(ex_cfg.get("rsi_extreme_high", 78))
    if rsi <= rsi_lo:
        signals.append(("RSI", True, "UP", f"RSI {rsi:.0f} ≤ {rsi_lo} (túladott)"))
    elif rsi >= rsi_hi:
        signals.append(("RSI", True, "DOWN", f"RSI {rsi:.0f} ≥ {rsi_hi} (túlvett)"))
    else:
        signals.append(("RSI", False, None, f"RSI {rsi:.0f} — semleges"))

    # ── 5. LIQUIDATION CASCADE ─────────────────────────────────────────────
    n_liqs = int((realflow or {}).get("n_liqs", 0))
    casc_min = int(ex_cfg.get("cascade_min_liqs", 3000))
    if n_liqs >= casc_min:
        # cascade direction: flush of the crowded side → contrarian bounce
        d = "UP" if (ls or 1.0) > 1.0 else "DOWN"
        signals.append(("CASCADE", True, d, f"{n_liqs} likvidáció (≥{casc_min}) — kényszer-zárások"))
    else:
        signals.append(("CASCADE", False, None, f"{n_liqs} likvidáció — normál"))

    # ── 6. FEAR & GREED (external, best-effort) ────────────────────────────
    fng = _fng() if ex_cfg.get("use_fng", True) else None
    if fng:
        v = fng["value"]
        if v <= int(ex_cfg.get("fng_fear", 15)):
            signals.append(("F&G", True, "UP", f"Fear&Greed {v} ({fng['label']}) — extrém félelem"))
        elif v >= int(ex_cfg.get("fng_greed", 85)):
            signals.append(("F&G", True, "DOWN", f"Fear&Greed {v} ({fng['label']}) — extrém kapzsiság"))
        else:
            signals.append(("F&G", False, None, f"Fear&Greed {v} ({fng['label']})"))

    # ── ARMED verdict ──────────────────────────────────────────────────────
    active = [s for s in signals if s[1]]
    n_active = len(active)
    armed = n_active >= arm_min

    direction = None
    if armed:
        ups = sum(1 for s in active if s[2] == "UP")
        dns = sum(1 for s in active if s[2] == "DOWN")
        if ups > dns:
            direction = "UP"
        elif dns > ups:
            direction = "DOWN"
        else:
            armed = False          # conflicting extremes → no clean setup

    return dict(
        armed=armed,
        direction=direction,
        n_active=n_active,
        n_total=len(signals),
        arm_min=arm_min,
        signals=[dict(name=n, active=a, direction=d, detail=t)
                 for (n, a, d, t) in signals],
        fng=fng,
    )
