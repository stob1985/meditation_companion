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


_YAHOO = {"SPX": "^GSPC", "NDX": "^NDX", "DXY": "DX-Y.NYB", "GOLD": "GC=F", "OIL": "CL=F"}
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126 Safari/537.36"}


def _yahoo(sym: str, rng: str = "1y", interval: str = "1d") -> pd.Series | None:
    """Yahoo Finance chart API (reachable from the cloud where Stooq is not)."""
    try:
        import requests
        j = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                         params=dict(range=rng, interval=interval), headers=_UA, timeout=12).json()
        r = j["chart"]["result"][0]
        s = pd.Series(r["indicators"]["quote"][0]["close"],
                      index=pd.to_datetime(r["timestamp"], unit="s", utc=True), dtype=float).dropna()
        return s if len(s) else None
    except Exception:                                   # noqa: BLE001
        return None


def futures_now() -> dict | None:
    """24h % change of US index futures (trade almost 24/5): NQ (Nasdaq-100), ES (S&P 500)."""
    out = {}
    for name, sym in (("NQ", "NQ=F"), ("ES", "ES=F")):
        s = _yahoo(sym, "5d", "1h")
        if s is None or len(s) < 25:
            continue
        out[name] = dict(last=round(float(s.iloc[-1]), 1), chg24=round((float(s.iloc[-1]) / float(s.iloc[-25]) - 1) * 100, 2))
    return out or None


def build(df: pd.DataFrame, cfg: dict, win: int = 30) -> dict | None:
    if not cfg.get("macro", {}).get("enabled", True):
        return None
    btc_ret = df["close"].pct_change()
    out, leans = {}, []
    got_any = False
    for name, sym in _SERIES.items():
        s = _yahoo(_YAHOO[name])
        if s is None:
            s = _stooq(sym)
        if s is None or len(s) < win + 2:
            continue
        got_any = True
        s.index = s.index.normalize()
        s = s[~s.index.duplicated(keep='last')]
        idx = df.index.tz_convert('UTC').normalize() if df.index.tz is not None else df.index.tz_localize('UTC').normalize()
        s = pd.Series(s.reindex(idx, method="ffill").values, index=df.index)
        mret = s.pct_change()
        corr = btc_ret.tail(win).corr(mret.tail(win))
        recent = float(mret.tail(3).mean())
        out[name] = dict(corr=round(float(corr), 2) if pd.notna(corr) else None,
                         recent=round(recent * 100, 2))
        if _LEAN_SIGN[name] and pd.notna(corr):
            leans.append(_LEAN_SIGN[name] * np.sign(recent) * abs(corr))
    fut = futures_now()
    if not got_any and not fut:
        return None
    score = float(np.mean(leans)) if leans else 0.0
    bias = "UP" if score > 0.1 else "DOWN" if score < -0.1 else "NEUTRAL"
    return dict(series=out, score=round(score, 2), bias=bias, futures=fut,
                up=round(0.5 + max(-0.5, min(0.5, score)) * 0.5, 3))
