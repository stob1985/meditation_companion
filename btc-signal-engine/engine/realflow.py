"""
Real flow / real liquidations module (live, best-effort).
====================================================================
Unlike liquidity.py (a PROXY built from swing pivots), this pulls REAL data the
way the reference trader actually watches it:

  - OKX real liquidation orders   -> where liquidations are ACTUALLY happening
                                     now (bankruptcy price, side, size). Short
                                     liquidations print ABOVE price, longs BELOW.
  - Open Interest (OKX + HL)       -> rising OI = positions building; a sharp OI
                                     drop alongside a move = a liquidation cascade.
  - Long/Short account ratio (OKX) -> real crowd positioning (contrarian read).
  - Funding rate (Hyperliquid)     -> who pays whom; crowded side -> squeeze risk.

All live-only and best-effort: every call degrades to None when offline, so the
engine never breaks. This is NOT backtestable (no deep history), exactly like
the trader's live heatmap - it is a real-time confluence layer.
"""
from __future__ import annotations
import time
import numpy as np


def _get(url, **kw):
    import requests
    r = requests.get(url, timeout=12, **kw)
    r.raise_for_status()
    return r.json()


def okx_liquidations(inst_family="BTC-USDT", limit=100) -> list | None:
    """Recent REAL liquidations on OKX SWAP. Returns [(price, side, size, ts)]
    where side 'short' = a short was liquidated (prints above), 'long' = below."""
    try:
        j = _get("https://www.okx.com/api/v5/public/liquidation-orders",
                 params=dict(instType="SWAP", instFamily=inst_family,
                             state="filled", limit=str(limit)))
        out = []
        for item in j.get("data", []):
            for d in item.get("details", []):
                out.append((float(d["bkPx"]), d["posSide"], float(d["sz"]), int(d["ts"])))
        return out or None
    except Exception:                                  # noqa: BLE001
        return None


def _cluster_liqs(liqs, price, width):
    """Cluster real liquidation prices (size-weighted) into levels."""
    if not liqs:
        return [], []
    pts = sorted(liqs, key=lambda x: x[0])
    groups, cur = [], [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - cur[-1][0]) <= width:
            cur.append(p)
        else:
            groups.append(cur); cur = [p]
    groups.append(cur)
    clusters = []
    for g in groups:
        sz = sum(x[2] for x in g)
        px = sum(x[0] * x[2] for x in g) / sz
        longs = sum(x[2] for x in g if x[1] == "long")
        shorts = sum(x[2] for x in g if x[1] == "short")
        clusters.append(dict(price=round(px, 1), size=round(sz, 2), n=len(g),
                             side=("short" if shorts >= longs else "long")))
    above = sorted([c for c in clusters if c["price"] > price], key=lambda c: c["price"])
    below = sorted([c for c in clusters if c["price"] < price], key=lambda c: -c["price"])
    return above, below


def okx_oi_trend(ccy="BTC", period="1H", look=24) -> dict | None:
    try:
        j = _get("https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-volume",
                 params=dict(ccy=ccy, period=period, limit=str(look + 1)))
        rows = j.get("data", [])
        if len(rows) < 2:
            return None
        oi_now = float(rows[0][1]); oi_then = float(rows[min(look, len(rows) - 1)][1])
        chg = (oi_now / oi_then - 1) * 100 if oi_then else 0.0
        return dict(oi_usd=round(oi_now / 1e9, 2), change_pct=round(chg, 1),
                    trend="rising" if chg > 1 else "falling" if chg < -1 else "flat")
    except Exception:                                  # noqa: BLE001
        return None


def okx_long_short_ratio(ccy="BTC", period="1H") -> dict | None:
    try:
        j = _get("https://www.okx.com/api/v5/rubik/stat/contracts/long-short-account-ratio",
                 params=dict(ccy=ccy, period=period, limit="3"))
        rows = j.get("data", [])
        if not rows:
            return None
        ratio = float(rows[0][1])
        # >1 = crowd is net long -> contrarian bias DOWN (squeeze longs)
        bias = "DOWN" if ratio > 1.15 else "UP" if ratio < 0.87 else "NEUTRAL"
        return dict(ratio=round(ratio, 2), crowd=("LONG" if ratio > 1 else "SHORT"),
                    contrarian=bias)
    except Exception:                                  # noqa: BLE001
        return None


def hyperliquid_funding(coin="BTC") -> dict | None:
    try:
        j = _get  # noqa
        import requests
        r = requests.post("https://api.hyperliquid.xyz/info",
                          json={"type": "metaAndAssetCtxs"}, timeout=12)
        r.raise_for_status()
        meta, ctx = r.json()
        i = next(k for k, u in enumerate(meta["universe"]) if u["name"] == coin)
        c = ctx[i]
        fr = float(c.get("funding", 0))
        return dict(funding=round(fr, 6), oi=round(float(c.get("openInterest", 0)), 1),
                    # positive funding -> longs pay -> crowded long -> squeeze DOWN risk
                    bias="DOWN" if fr > 0.00005 else "UP" if fr < -0.00005 else "NEUTRAL")
    except Exception:                                  # noqa: BLE001
        return None


def build(cfg: dict, price: float, atr: float) -> dict | None:
    """Assemble the live real-flow picture. price/atr from the main feed."""
    if not cfg.get("realflow", {}).get("enabled", True):
        return None
    fam = cfg.get("realflow", {}).get("inst_family", "BTC-USDT")
    liqs = okx_liquidations(fam, cfg.get("realflow", {}).get("liq_limit", 100))
    width = atr * cfg["liquidity"]["zone_mult"]
    above, below = _cluster_liqs(liqs, price, width) if liqs else ([], [])
    oi = okx_oi_trend()
    lsr = okx_long_short_ratio()
    fund = hyperliquid_funding()
    if not any([liqs, oi, lsr, fund]):
        return None
    # net real-flow bias vote (contrarian L/S + funding)
    votes = [x["contrarian"] if isinstance(x, dict) and "contrarian" in x else
             x.get("bias") for x in (lsr, fund) if x]
    up = sum(1 for v in votes if v == "UP"); dn = sum(1 for v in votes if v == "DOWN")
    flow_bias = "UP" if up > dn else "DOWN" if dn > up else "NEUTRAL"
    return dict(n_liqs=len(liqs) if liqs else 0,
                liq_above=above[:5], liq_below=below[:5],
                oi=oi, ls_ratio=lsr, funding=fund, flow_bias=flow_bias)
