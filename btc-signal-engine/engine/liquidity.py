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

    # bounce rate: of bars that pierced a cluster zone, how many REJECTED it
    # (open & close on the same side of the level = poked and returned) vs broke
    # through (open & close straddle the level). Mirrors the "Bounce Rate" panel.
    o_arr, cl_arr = d["open"].values, d["close"].values
    touches = bounces = 0
    for c in clusters:
        p = c["price"]
        pierce = (lo_arr <= p) & (hi_arr >= p)
        if not pierce.any():
            continue
        so = np.sign(o_arr[pierce] - p)
        sc = np.sign(cl_arr[pierce] - p)
        rej = (so == sc) & (so != 0)
        touches += int(pierce.sum())
        bounces += int(rej.sum())
    bounce_rate = round(bounces / touches * 100, 1) if touches else None

    return dict(price=price, atr=round(a, 1),
                tiers_count={t: sum(1 for c in clusters if t in c["tiers"]) for t in TIERS},
                active=len(clusters), long_short=(n_long, n_short),
                nearest_atr=nearest_atr, bounce_rate=bounce_rate, bounce_events=touches,
                imbalance=imb, cvd_bias=cvd_bias,
                clusters_above=sorted(above, key=lambda c: c["price"]),
                clusters_below=sorted(below, key=lambda c: -c["price"]),
                zone_mult=cfg["liquidity"]["zone_mult"])


# ---------------------------------------------------------------- multi-venue
def _merge_venues(items, width):
    """items: list of (cluster_dict, venue). Group by price proximity; a level
    confirmed by MORE venues is a stronger, higher-confluence magnet."""
    if not items:
        return []
    items = sorted(items, key=lambda t: t[0]["price"])
    groups, cur = [], [items[0]]
    for it in items[1:]:
        if abs(it[0]["price"] - cur[-1][0]["price"]) <= width:
            cur.append(it)
        else:
            groups.append(cur); cur = [it]
    groups.append(cur)
    out = []
    for g in groups:
        prices = [c["price"] for c, _ in g]
        venues = sorted({v for _, v in g})
        tiers = sorted({t for c, _ in g for t in c["tiers"]})
        out.append(dict(price=round(float(np.mean(prices)), 1),
                        count=sum(c["count"] for c, _ in g),
                        venues=venues, n_venues=len(venues), tiers=tiers))
    return out


def build_multi(cfg: dict) -> dict | None:
    """Aggregate the PROXY liquidation map across several exchanges.
    Levels where multiple venues agree = cross-exchange confluence. Best-effort:
    skips venues that fail, returns None if none reachable."""
    from . import data
    venues = cfg["liquidity"].get("venues",
                                  ["okx", "binanceus", "hyperliquid", "kraken", "coinbase"])
    sym, interval = cfg["data"]["symbol"], cfg["data"]["interval"]
    limit = min(int(cfg["data"].get("limit", 1000)), 500)
    per, all_above, all_below = {}, [], []
    ref_price = ref_atr = None
    for ex in venues:
        try:
            dfx = data.load_live(sym, interval, limit, exchange=ex, verbose=False)
            m = build(dfx, cfg)
        except Exception:                              # noqa: BLE001
            continue
        per[ex] = dict(price=m["price"], imbalance=m["imbalance"],
                       cvd_bias=m["cvd_bias"], active=m["active"],
                       bounce=m["bounce_rate"])
        if ref_price is None:
            ref_price, ref_atr = m["price"], m["atr"]
        all_above += [(c, ex) for c in m["clusters_above"]]
        all_below += [(c, ex) for c in m["clusters_below"]]
    if not per:
        return None
    width = ref_atr * cfg["liquidity"]["zone_mult"]
    above = sorted(_merge_venues(all_above, width), key=lambda c: c["price"])
    below = sorted(_merge_venues(all_below, width), key=lambda c: -c["price"])
    # consensus imbalance across venues
    bull = sum(1 for v in per.values() if "BULL" in v["imbalance"])
    bear = sum(1 for v in per.values() if "BEAR" in v["imbalance"])
    consensus = "BULLISH" if bull > bear else "BEARISH" if bear > bull else "MIXED"
    return dict(venues=list(per.keys()), per_venue=per, ref_price=ref_price,
                clusters_above=above, clusters_below=below, consensus=consensus,
                n_venues=len(per))
