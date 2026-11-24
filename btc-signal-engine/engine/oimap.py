"""
OI-based liquidation map (live, best-effort) - sees FRESH positions.
====================================================================
The proxy map (liquidity.py) only projects liquidations from swing pivots, so
it misses leverage opened mid-move. This module rebuilds where positions were
opened from the exchange's own hourly open-interest history (OKX, ~30 days):

  - every hour OI rises, the new notional is booked at that hour's typical
    price, split long/short by taker buy share (OKX taker volume, 72h) or by
    the candle direction when taker data is not available
  - each booking is spread over a leverage mix (config oimap.lev_mix) and
    turned into liquidation prices (tiered maintenance margin)
  - positions whose liquidation price was traded through are removed
    (liquidated); OI decreases are booked as proportional closes across
    tracked AND older (unknown-price) positions

Absolute USD figures are rough (one venue, assumed leverage mix); the SHAPE
(where the bands sit, above vs below) is the useful part. Not validated as a
direction signal - it tells WHERE price can accelerate, not WHICH way.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

MMR = {10: .004, 20: .005, 25: .005, 50: .0075, 100: .01}


def _get(url, **params):
    import requests
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("data", [])


def build(cfg: dict) -> dict | None:
    oc = cfg.get("oimap", {})
    if not oc.get("enabled", True):
        return None
    try:
        from . import data
        fam = cfg.get("realflow", {}).get("inst_family", "BTC-USDT")
        ccy = fam.split("-")[0]
        lev_mix = {int(k): float(v) for k, v in oc.get("lev_mix", {10: .30, 20: .25, 25: .15, 50: .20, 100: .10}).items()}
        oi = pd.Series({pd.to_datetime(int(a), unit="ms", utc=True): float(b) for a, b, *_ in
                        _get("https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-volume",
                             ccy=ccy, period="1H")}).sort_index()
        tk = {pd.to_datetime(int(a), unit="ms", utc=True): (float(s), float(b)) for a, s, b in
              _get("https://www.okx.com/api/v5/rubik/stat/taker-volume", ccy=ccy,
                   instType="CONTRACTS", period="1H")}
        c = data.load_live(cfg["data"]["symbol"], "60", 800, "okx", verbose=False)
        c.index = c.index.tz_convert("UTC") if c.index.tz is not None else c.index.tz_localize("UTC")
    except Exception:                                   # noqa: BLE001
        return None
    idx = oi.index.intersection(c.index)
    if len(idx) < 48:
        return None
    oi, c = oi[idx], c.loc[idx]
    pos, older = [], float(oi.iloc[0])
    swept = {"L": 0.0, "S": 0.0}
    t24 = idx[-1] - pd.Timedelta(hours=24)
    for k in range(1, len(idx)):
        t = idx[k]; bar = c.loc[t]; rem = 0.0; keep = []
        for p in pos:
            if (p[1] == "L" and bar["low"] <= p[0]) or (p[1] == "S" and bar["high"] >= p[0]):
                rem += p[2]
                if t > t24:
                    swept[p[1]] += p[2]
            else:
                keep.append(p)
        pos = keep
        d_oi = oi.iloc[k] - oi.iloc[k - 1]
        if d_oi > 0:
            e = (bar["high"] + bar["low"] + bar["close"]) / 3
            if t in tk and sum(tk[t]) > 0:
                ls = tk[t][1] / sum(tk[t])
            else:
                ls = 0.5 + 0.3 * np.tanh((bar["close"] / bar["open"] - 1) / 0.005)
            for side, share in (("L", ls), ("S", 1 - ls)):
                for lev, wl in lev_mix.items():
                    m = MMR.get(lev, 0.005)
                    liq = e * (1 - 1 / lev + m) if side == "L" else e * (1 + 1 / lev - m)
                    pos.append([liq, side, d_oi * share * wl])
        elif d_oi < 0:
            tot = sum(p[2] for p in pos) + older
            amt = max(0.0, -d_oi - rem)
            f = max(0.0, 1 - amt / tot) if tot > 0 else 1.0
            for p in pos:
                p[2] *= f
            older *= f
    px = float(c["close"].iloc[-1])
    D = pd.DataFrame(pos, columns=["p", "s", "n"])
    if D.empty:
        return None
    bw = float(oc.get("bin_usd", 500))
    D["bin"] = (D.p // bw) * bw
    bands = {}
    for pct in (2, 5, 10, 20):
        a = D[(D.s == "S") & (D.p > px) & (D.p <= px * (1 + pct / 100))].n.sum()
        b = D[(D.s == "L") & (D.p < px) & (D.p >= px * (1 - pct / 100))].n.sum()
        bands[pct] = (round(a / 1e6, 1), round(b / 1e6, 1))
    up = D[(D.s == "S") & (D.p > px) & (D.p <= px * 1.15)].groupby("bin").n.sum()
    dn = D[(D.s == "L") & (D.p < px) & (D.p >= px * 0.85)].groupby("bin").n.sum()
    top = lambda s, k: [(float(b), round(v / 1e6, 1)) for b, v in s.nlargest(k).sort_index().items()]
    return dict(venue="okx", price=round(px, 1), oi_usd=round(float(oi.iloc[-1]) / 1e9, 2),
                tracked_usd=round(float(D.n.sum()) / 1e9, 2), bands=bands, bin=bw,
                top_above=top(up, 5), top_below=top(dn, 5)[::-1],
                swept_24h=(round(swept["S"] / 1e6, 1), round(swept["L"] / 1e6, 1)))
