"""
Liquidity map (PROXY - free, estimated).

Real liquidation heatmaps need order-book / Coinglass data. This recreates the
second screenshot's logic WITHOUT paid data, the same way the reference tool's
"PROXY" mode does:

  - find recent swing highs/lows (where crowds entered)
  - project where 10x/25x/50x/100x positions opened there would get liquidated
        long  liq  = entry * (1 - 1/lev + mmr)      (below price)
        short liq  = entry * (1 + 1/lev - mmr)      (above price)
  - cluster nearby levels (within ATR * zone_mult)
  - measure long/short imbalance, nearest cluster distance, CVD bias
"""
from __future__ import annotations
import numpy as np
import pandas as pd

TIERS = [10, 25, 50, 100]
MMR = 0.005          # ~0.5% maintenance margin approximation


def _swings(df: pd.DataFrame, lb: int):
    hi, lo = df["high"], df["low"]
    win = 2 * lb + 1
    sh = hi[(hi == hi.rolling(win, center=True).max())].dropna()
    sl = lo[(lo == lo.rolling(win, center=True).min())].dropna()
    return sh, sl


def _cluster(levels, width):
    """Greedy 1-D clustering; returns list of (price, count, members)."""
    if not levels:
        return []
    levels = sorted(levels, key=lambda x: x[0])
    clusters = []
    cur = [levels[0]]
    for lv in levels[1:]:
        if abs(lv[0] - cur[-1][0]) <= width:
            cur.append(lv)
        else:
            clusters.append(cur); cur = [lv]
    clusters.append(cur)
    out = []
    for c in clusters:
        price = np.mean([x[0] for x in c])
        out.append(dict(price=round(price, 1), count=len(c),
                        tiers=sorted({x[1] for x in c}),
                        side=c[0][2]))
    return out


def build(df: pd.DataFrame, cfg: dict) -> dict:
    lb = cfg["liquidity"]["swing_lookback"]
    look = cfg["liquidity"]["history_bars"]
    d = df.tail(look)
    price = float(d["close"].iloc[-1])
    a = (d["high"] - d["low"]).rolling(14).mean().iloc[-1]
    width = a * cfg["liquidity"]["zone_mult"]

    mmr_tiers = cfg["liquidity"].get("mmr_tiers", {})

    def _mmr(lev):
        return float(mmr_tiers.get(lev, mmr_tiers.get(str(lev), MMR)))

    sh, sl = _swings(d, lb)
    levels = []
    # shorts entered at swing HIGHS -> liquidate ABOVE (tiered maintenance margin)
    for entry in sh.values:
        for lev in TIERS:
            lv = entry * (1 + 1 / lev - _mmr(lev))
            if lv > price:
                levels.append((lv, lev, "short"))
    # longs entered at swing LOWS -> liquidate BELOW
    for entry in sl.values:
        for lev in TIERS:
            lv = entry * (1 - 1 / lev + _mmr(lev))
            if lv < price:
                levels.append((lv, lev, "long"))

    clusters = _cluster(levels, width)

    # tap count: how many bars probed within `width` of each cluster price.
    # heavily-tapped levels are "worn" (power-of-three: they tend to break),
    # fresh levels are cleaner magnets/targets.
    hi_arr, lo_arr = d["high"].values, d["low"].values
    for c in clusters:
        p = c["price"]
        c["taps"] = int(np.sum((lo_arr <= p + width) & (hi_arr >= p - width)))
        c["fresh"] = c["taps"] <= 3

    above = [c for c in clusters if c["price"] > price]
    below = [c for c in clusters if c["price"] < price]
    n_long = sum(1 for c in clusters if c["side"] == "long")
    n_short = sum(1 for c in clusters if c["side"] == "short")

    # nearest cluster distance in ATR
    if clusters:
        nearest = min(clusters, key=lambda c: abs(c["price"] - price))
        nearest_atr = round(abs(nearest["price"] - price) / a, 1)
    else:
        nearest_atr = None

    # CVD bias (signed-volume cumulative, recent window)
    sign = np.sign(d["close"] - d["open"])
    cvd = (sign * d["volume"]).tail(cfg["liquidity"]["cvd_bars"]).sum()
    cvd_bias = "LONG" if cvd > 0 else "SHORT"

    # imbalance: more buy-side (short liq above) vs sell-side (long liq below)
    buyside = sum(c["count"] for c in above)
    sellside = sum(c["count"] for c in below)
    if buyside == sellside:
        imb = "FLAT"
    elif buyside > sellside * 1.3:
        imb = "BULLISH"
    elif sellside > buyside * 1.3:
        imb = "BEARISH"
    else:
        imb = "MILD " + ("BULLISH" if buyside > sellside else "BEARISH")

    return dict(price=price, atr=round(a, 1),
                tiers_count={t: sum(1 for c in clusters if t in c["tiers"]) for t in TIERS},
                active=len(clusters), long_short=(n_long, n_short),
                nearest_atr=nearest_atr,
                imbalance=imb, cvd_bias=cvd_bias,
                clusters_above=sorted(above, key=lambda c: c["price"]),
                clusters_below=sorted(below, key=lambda c: -c["price"]),
                zone_mult=cfg["liquidity"]["zone_mult"])
