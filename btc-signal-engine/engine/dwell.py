"""
Dwell time / dwell block module.
====================================================================
The core idea from the video concept: price does not treat all levels equally.
It *dwells* (spends time) inside certain price zones and rips through others.

  - "dwell" = how much TIME (and volume) price spent at each price.
  - a "dwell block" = a contiguous high-dwell zone -> acceptance / value area
        -> acts as strong support/resistance and as a brake on moves.
  - low-dwell gaps = thin zones price crosses quickly -> good travel space.

Direction rule (ChentoTrades transcript)
----------------------------------------
The edge is *where price consolidates relative to the nearest dwell block*:
  - consolidating ABOVE a block  -> block is support  -> shift out UP
  - consolidating BELOW a block  -> block is resistance-> goner, DOWN
  - consolidating in the MID of a block                -> mostly DOWN, then taps
                                                          the next block and shifts
So we classify the current location and emit a `dwell_bias` + a `dwell_target`
(the next block to shift toward). The confidence scales with the block's dwell
share and how tightly we are consolidating (coiling).

POC vs dwell block
------------------
POC (point of control) = the single most-dwelt price bucket. A dwell block is a
*contiguous run* of high-dwell buckets. They are computed differently and kept
separate on purpose (the transcript stresses they are not the same thing).

Pure pandas/numpy, no extra deps.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _atr(df: pd.DataFrame, n: int = 14) -> float:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return float(tr.rolling(n).mean().iloc[-1])


def build(df: pd.DataFrame, cfg: dict) -> dict:
    dc = cfg.get("dwell", {})
    look = int(dc.get("lookback", 200))
    bins = int(dc.get("bins", 60))
    va_pct = float(dc.get("value_area_pct", 0.70))
    block_pctile = float(dc.get("block_pctile", 75))
    tol_atr = float(dc.get("current_tol_atr", 0.5))

    d = df.tail(look)
    price = float(d["close"].iloc[-1])
    atr = _atr(df)
    lo, hi = float(d["low"].min()), float(d["high"].max())
    if hi <= lo or not np.isfinite(atr) or atr <= 0:
        return dict(empty=True, price=price, atr=round(atr, 1) if np.isfinite(atr) else None)

    edges = np.linspace(lo, hi, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    bin_w = edges[1] - edges[0]

    # time-at-price (TPO): each bar adds 1 dwell unit spread over the bins its
    # range covers (sum=1 per bar). volume-at-price: same span, volume-weighted.
    tpo = np.zeros(bins)
    vap = np.zeros(bins)
    for o, h, l, c, v in zip(d["open"], d["high"], d["low"], d["close"], d["volume"]):
        b_lo = max(0, int((l - lo) // bin_w))
        b_hi = min(bins - 1, int((h - lo) // bin_w))
        span = b_hi - b_lo + 1
        tpo[b_lo:b_hi + 1] += 1.0 / span
        vap[b_lo:b_hi + 1] += v / span

    total_tpo = tpo.sum()
    poc_i = int(np.argmax(tpo))                       # point of control (most-dwelt)
    poc = float(centers[poc_i])

    # value area: grow out from POC until va_pct of dwell captured
    order = np.argsort(tpo)[::-1]
    cum, sel = 0.0, set()
    for i in order:
        sel.add(int(i))
        cum += tpo[i]
        if cum >= va_pct * total_tpo:
            break
    va_lo = float(edges[min(sel)])
    va_hi = float(edges[max(sel) + 1])

    # dwell blocks: contiguous runs of bins above the dwell percentile threshold
    thr = np.percentile(tpo, block_pctile)
    blocks = []
    i = 0
    while i < bins:
        if tpo[i] >= thr and tpo[i] > 0:
            j = i
            while j + 1 < bins and tpo[j + 1] >= thr:
                j += 1
            mass = float(tpo[i:j + 1].sum())
            vmass = float(vap[i:j + 1].sum())
            blocks.append(dict(
                lo=round(float(edges[i]), 1), hi=round(float(edges[j + 1]), 1),
                mid=round(float((edges[i] + edges[j + 1]) / 2), 1),
                dwell=round(mass / total_tpo * 100, 1),               # % of total time
                vol_share=round(vmass / vap.sum() * 100, 1),
                side=("above" if edges[i] > price else "below" if edges[j + 1] < price
                      else "around")))
            i = j + 1
        else:
            i += 1
    blocks.sort(key=lambda b: -b["dwell"])

    # current dwell: how many of the most recent bars stayed within tol_atr of now
    band = tol_atr * atr
    closes = d["close"].values
    run = 0
    for c in closes[::-1]:
        if abs(c - price) <= band:
            run += 1
        else:
            break
    in_band = int(np.sum(np.abs(closes - price) <= band))
    dwell_ratio = round(in_band / len(closes) * 100, 1)
    coil_min = max(5, look // 30)
    state = "COILING" if run >= coil_min else "TRENDING" if run <= 1 else "NEUTRAL"

    # nearest block above / below current price (for the trade layer)
    above = [b for b in blocks if b["lo"] > price]
    below = [b for b in blocks if b["hi"] < price]
    nearest_above = min(above, key=lambda b: b["lo"] - price) if above else None
    nearest_below = min(below, key=lambda b: price - b["hi"]) if below else None

    # ---- direction rule: where are we vs the nearest block? --------------
    ref = None
    for b in blocks:                                  # block containing price?
        if b["lo"] <= price <= b["hi"]:
            ref = b; loc = "MID"; break
    if ref is None:
        # nearest block by edge distance
        cand = sorted(blocks, key=lambda b: min(abs(price - b["lo"]), abs(price - b["hi"])))
        ref = cand[0] if cand else None
        if ref is not None:
            loc = "ABOVE" if price > ref["hi"] else "BELOW"
        else:
            loc = None

    dwell_bias, dwell_conf, dwell_target, dwell_target_src = "NEUTRAL", 0.0, None, None
    if ref is not None:
        # confidence: block strength * how much we are consolidating
        consol = min(1.0, run / (2.0 * coil_min)) if state != "TRENDING" else 0.2
        block_str = min(1.0, ref["dwell"] / 20.0)     # ~20% dwell == very strong
        dwell_conf = round(max(0.0, min(1.0, 0.5 * consol + 0.5 * block_str)), 2)
        if loc == "ABOVE":                            # support below -> shift out up
            dwell_bias = "UP"
            tgt = nearest_above
            dwell_target = tgt["lo"] if tgt else round(price + 2 * atr, 1)
            dwell_target_src = (f"next block {tgt['lo']}-{tgt['hi']}" if tgt
                                else "projected +2ATR (no block above)")
        elif loc == "BELOW":                          # resistance above -> down
            dwell_bias = "DOWN"
            tgt = nearest_below
            dwell_target = tgt["hi"] if tgt else round(price - 2 * atr, 1)
            dwell_target_src = (f"next block {tgt['lo']}-{tgt['hi']}" if tgt
                                else "projected -2ATR (no block below)")
        else:                                         # MID -> mostly down, tap next
            dwell_bias = "DOWN"
            tgt = nearest_below
            dwell_target = tgt["hi"] if tgt else round(ref["lo"], 1)
            dwell_target_src = (f"mid-range -> next block {tgt['lo']}-{tgt['hi']}" if tgt
                                else "mid-range -> block low")

    return dict(empty=False, price=round(price, 1), atr=round(atr, 1),
                poc=round(poc, 1), value_area=(round(va_lo, 1), round(va_hi, 1)),
                blocks=blocks, n_blocks=len(blocks),
                current_run=run, dwell_ratio=dwell_ratio, state=state,
                band=round(band, 1),
                nearest_above=nearest_above, nearest_below=nearest_below,
                ref_block=ref, location=loc if ref is not None else None,
                dwell_bias=dwell_bias, dwell_conf=dwell_conf,
                dwell_target=dwell_target, dwell_target_src=dwell_target_src)
