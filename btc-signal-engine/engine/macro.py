"""
Macro correlation overlay (best-effort).
====================================================================
The transcript hammers one point: BTC currently tracks NASDAQ / S&P 500 / Dow,
and reacts to DXY, gold, oil. We pull free daily series (Stooq) and compute:
  - rolling correlation of BTC daily returns vs each macro series
  - a macro lean: BTC tends to follow SPX/NDX (positive) and invert DXY.

This is a CONFLUENCE OVERLAY, not a backtested composite input: it needs an
aligned external history that may be unavailable offline, so it degrades to
None when the data cannot be fetched (e.g. Stooq blocked from a cloud).
On a normal machine it returns live values.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

# Stooq symbols
_SERIES = {"SPX": "^spx", "NDX": "^ndx", "DXY": "^dxy", "GOLD": "xauusd", "OIL": "cl.f"}
# sign of expected BTC lean per macro direction (+1 follows, -1 inverts)
_LEAN_SIGN = {"SPX": +1, "NDX": +1, "DXY": -1, "GOLD": +1, "OIL": 0}


def _stooq(sym: str) -> pd.Series | None:
    try:
        import requests
        url = f"https://stooq.com/q/d/l/?s={sym}&i=d"
        txt = requests.get(url, timeout=12).text
        if "Date" not in txt:
            return None
        from io import StringIO
        df = pd.read_csv(StringIO(txt))
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
        return df.set_index("Date")["Close"].astype(float)
    except Exception:                                   # noqa: BLE001
        return None


def build(df: pd.DataFrame, cfg: dict, win: int = 30) -> dict | None:
    if not cfg.get("macro", {}).get("enabled", True):
        return None
    btc_ret = df["close"].pct_change()
    out, leans = {}, []
    got_any = False
    for name, sym in _SERIES.items():
        s = _stooq(sym)
        if s is None or len(s) < win + 2:
            continue
        got_any = True
        s = s.reindex(df.index, method="ffill")
        mret = s.pct_change()
        corr = btc_ret.tail(win).corr(mret.tail(win))
        recent = float(mret.tail(3).mean())
        out[name] = dict(corr=round(float(corr), 2) if pd.notna(corr) else None,
                         recent=round(recent * 100, 2))
        if _LEAN_SIGN[name] and pd.notna(corr):
            leans.append(_LEAN_SIGN[name] * np.sign(recent) * abs(corr))
    if not got_any:
        return None
    score = float(np.mean(leans)) if leans else 0.0
    bias = "UP" if score > 0.1 else "DOWN" if score < -0.1 else "NEUTRAL"
    return dict(series=out, score=round(score, 2), bias=bias,
                up=round(0.5 + max(-0.5, min(0.5, score)) * 0.5, 3))
