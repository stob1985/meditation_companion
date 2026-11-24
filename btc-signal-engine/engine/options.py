"""
Options context (Deribit public API, live, best-effort).
====================================================================
Per upcoming expiry: open interest (coins), put/call ratio, MAX PAIN (the
settlement price that minimises option holders' payoff) and the biggest put /
call strikes. Large strikes near spot are where dealer hedging can pin or
accelerate price around the expiry; the monthly/quarterly expiries (last
Friday, 08:00 UTC) are volatility events. Context only - not validated.
"""
from __future__ import annotations
import re
import numpy as np
import pandas as pd


def build(cfg: dict, price: float | None = None) -> dict | None:
    oc = cfg.get("options", {})
    if not oc.get("enabled", True):
        return None
    ccy = cfg.get("realflow", {}).get("inst_family", "BTC-USDT").split("-")[0]
    if ccy not in ("BTC", "ETH"):
        return None
    try:
        import requests
        j = requests.get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency",
                         params=dict(currency=ccy, kind="option"), timeout=20).json()["result"]
    except Exception:                                   # noqa: BLE001
        return None
    rows = []
    for x in j:
        m = re.match(rf"{ccy}-(\d+[A-Z]{{3}}\d{{2}})-(\d+)-([CP])", x.get("instrument_name", ""))
        if m:
            rows.append((m.group(1), int(m.group(2)), m.group(3), float(x.get("open_interest") or 0),
                         x.get("underlying_price")))
    if not rows:
        return None
    D = pd.DataFrame(rows, columns=["exp", "K", "t", "oi", "und"])
    D["expd"] = pd.to_datetime(D.exp, format="%d%b%y") + pd.Timedelta(hours=8)   # 08:00 UTC settlement
    spot = float(price or D.und.dropna().median())
    now = pd.Timestamp.utcnow().tz_localize(None)
    out = []
    for e, g in D[D.expd >= now].groupby("expd"):
        if g.oi.sum() <= 0:
            continue
        calls, puts = g[g.t == "C"], g[g.t == "P"]
        pain = [(k, float((np.maximum(k - calls.K, 0) * calls.oi).sum() + (np.maximum(puts.K - k, 0) * puts.oi).sum()))
                for k in sorted(g.K.unique())]
        mp = min(pain, key=lambda z: z[1])[0]
        out.append(dict(expiry=e, oi=round(g.oi.sum()), oi_usd_bn=round(g.oi.sum() * spot / 1e9, 2),
                        pc=round(puts.oi.sum() / max(calls.oi.sum(), 1e-9), 2), max_pain=int(mp),
                        top_puts=[(int(k), round(v)) for k, v in puts.nlargest(3, "oi")[["K", "oi"]].values],
                        top_calls=[(int(k), round(v)) for k, v in calls.nlargest(3, "oi")[["K", "oi"]].values]))
    if not out:
        return None
    big = max(out[:6], key=lambda x: x["oi"])
    near = [o for o in out if o["oi"] >= 0.15 * big["oi"]][: int(oc.get("n_expiries", 4))]
    # strikes within +-10% of spot across the listed expiries = options battleground levels
    near_strikes = D[(D.expd >= now) & (D.expd <= near[-1]["expiry"]) & (D.K.between(spot * 0.9, spot * 1.1))]
    bg = near_strikes.groupby(["K", "t"]).oi.sum().nlargest(5)
    return dict(ccy=ccy, spot=round(spot, 1), total_oi=round(D.oi.sum()), expiries=near, biggest=big,
                battleground=[(int(k), t, round(v)) for (k, t), v in bg.items()])
