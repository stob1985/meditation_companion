"""
Signal engine - the COMPOSITE.

For "today" (last bar): take active events, blend each event's directional lean
(from its VDB win rate) using adaptive weights, and output a single UP/DN %,
a bias label, a strength, and a 5-day forecast band - exactly like the
"COMPOSITE" and "FORECAST" rows of the first screenshot.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import astro, flow as flowmod, dwell as dwellmod, reversal as revmod


def _adaptive_weights(db: dict, base: dict, horizon: int = 3) -> dict:
    """Scale each event's base weight by how strong/clean its edge is.
    Markers:  fire = boosted (>1.15), snow = cooled (<0.9)."""
    w = {}
    for ev, bw in base.items():
        s = db.get(ev, {})
        wr = s.get(f"wr_{horizon}", 50) / 100.0
        edge = abs(wr - 0.5) * 2          # 0..1
        qual = s.get("db_qual", 50) / 100.0
        factor = 0.6 + 1.2 * edge * qual  # ~0.6 .. 1.8
        w[ev] = round(bw * factor, 2)
    return w


def composite(df: pd.DataFrame, events: pd.DataFrame, db: dict, cfg: dict,
              at: int = -1, dwell: dict = None) -> dict:
    horizon = cfg["signal"]["horizon"]
    base = cfg["signal"]["base_weights"]
    aw = _adaptive_weights(db, base, horizon)

    row = events.iloc[at]
    active = [ev for ev in events.columns if bool(row[ev]) and ev in db]

    up_score, w_total, rows = 0.0, 0.0, []
    for ev in active:
        s = db[ev]
        wr = s.get(f"wr_{horizon}", 50) / 100.0       # >0.5 => up lean
        w = aw.get(ev, 1.0)
        up_score += wr * w
        w_total += w
        # per-event display fields (UP%/DN% blended model + db)
        up_blend = round(wr * 100, 1)
        rows.append(dict(
            event=ev, dn=round(100 - up_blend, 1), up=up_blend,
            win=s.get(f"wr_{horizon}", 50), n=s["n"],
            expect=s.get(f"expect_{horizon}", 0), pf=s.get(f"pf_{horizon}", 1.0),
            qual=s.get("db_qual", 50), weight=w,
            last5=s.get("last5"), ln_wr=s.get("ln_wr"), edge=s.get("edge", "NEUTRAL"),
            bias=("UP bias" if wr > 0.53 else "DOWN bias" if wr < 0.47 else "-"),
            mark=("\U0001f525" if w > base.get(ev, 1) * 1.15 else
                  "\u2744" if w < base.get(ev, 1) * 0.9 else "")))

    up = (up_score / w_total) if w_total else 0.5

    # planet composite (Phase 2) folded in with its own weight
    if cfg["astro"]["enabled"]:
        pc = astro.aspects(df.index[at].date(), cfg["astro"]["orb"])
        pw = cfg["signal"]["planet_weight"]
        up = (up * w_total + (pc["up"] / 100) * pw) / (w_total + pw) if w_total else pc["up"] / 100
        w_total += pw
    else:
        pc = None

    # dwell direction rule (the transcript's main edge) folded in
    sub = df.iloc[:at + 1] if at != -1 else df
    if dwell is None and cfg.get("dwell", {}).get("enabled", True):
        dwell = dwellmod.build(sub, cfg)
    dw_w = float(cfg["signal"].get("dwell_weight", 0.0))
    if dwell and not dwell.get("empty") and dwell.get("dwell_bias") not in (None, "NEUTRAL") and dw_w > 0:
        dconf = float(dwell.get("dwell_conf", 0.0))
        dwell_up = 0.5 + (0.5 * dconf if dwell["dwell_bias"] == "UP" else -0.5 * dconf)
        eff = dw_w * max(0.1, dconf)                   # weak conviction -> small weight
        up = (up * w_total + dwell_up * eff) / (w_total + eff)
        w_total += eff

    # money flow / CVD folded in
    fl_w = float(cfg["signal"].get("flow_weight", 0.0))
    fl = flowmod.cvd_bias(sub, win=cfg.get("liquidity", {}).get("cvd_bars", 30))
    if fl_w > 0 and fl["bias"] != "FLAT":
        up = (up * w_total + fl["up"] * fl_w) / (w_total + fl_w)
        w_total += fl_w

    # regime / trend (multi-EMA agreement) folded in - keeps the composite from
    # leaning against a strong trend (e.g. going long into a STRONG BEAR)
    rw = float(cfg["signal"].get("regime_weight", 0.0))
    if rw > 0:
        px0 = float(df["close"].iloc[at])
        emas0 = [df["close"].ewm(span=s).mean().iloc[at] for s in (10, 20, 50, 100, 200)]
        mtf0 = sum(1 if px0 > e else -1 for e in emas0)
        reg_up = 0.5 + (mtf0 / 5.0) * 0.5              # -5..5 -> 0..1
        up = (up * w_total + reg_up * rw) / (w_total + rw)
        w_total += rw

    # sweep-reclaim REVERSAL (the video's "sweep the lows -> reversal") - a strong
    # override so the model is not structurally late to a turn the way pure trend
    # following is. A confirmed sweep+reclaim pulls the bias toward the reclaim.
    rev = revmod.detect(sub, cfg)
    rev_w = float(cfg["signal"].get("reversal_weight", 0.0))
    if rev_w > 0 and rev["signal"] == "BULL":
        up = (up * w_total + 0.80 * rev_w) / (w_total + rev_w); w_total += rev_w
    elif rev_w > 0 and rev["signal"] == "BEAR":
        up = (up * w_total + 0.20 * rev_w) / (w_total + rev_w); w_total += rev_w

    up_pct = round(up * 100, 1)
    dn_pct = round(100 - up_pct, 1)
    bias = "UP" if up_pct > 52 else "DOWN" if up_pct < 48 else "FLAT"

    # strength from agreement + sample
    spread = abs(up_pct - 50)
    strength = ("VERY STRONG" if spread > 18 else "STRONG" if spread > 10
                else "MODERATE" if spread > 4 else "WEAK")
    q = int(round(min(100, spread * 3 + np.mean([r["qual"] for r in rows]) / 2))) if rows else 0

    # forecast band: project the dominant move size over horizon
    close = df["close"]
    ret_h = close.pct_change(horizon)
    sigma = ret_h.tail(cfg["signal"]["band_lookback"]).std()
    px = float(close.iloc[at])
    hi = round(px * (1 + sigma), 2)
    lo = round(px * (1 - sigma), 2)

    # regime / MTF (simple multi-EMA agreement on close)
    emas = [close.ewm(span=s).mean().iloc[at] for s in (10, 20, 50, 100, 200)]
    mtf = sum(1 if px > e else -1 for e in emas)
    regime = "STRONG BEAR" if mtf <= -4 else "BEAR" if mtf < 0 else \
             "STRONG BULL" if mtf >= 4 else "BULL" if mtf > 0 else "NEUTRAL"

    return dict(rows=rows, active=len(active),
                up=up_pct, dn=dn_pct, bias=bias, strength=strength, q=q,
                forecast=dict(conf=int(cfg["signal"]["forecast_conf"] * 100), hi=hi, lo=lo),
                planet=pc, dwell=dwell, flow=fl, reversal=rev, weights=aw, mtf=mtf, regime=regime,
                rsi=round(float(events.attrs["rsi"].iloc[at]), 0),
                adx=round(float(events.attrs["adx"].iloc[at]), 1),
                price=px, date=df.index[at].date())
