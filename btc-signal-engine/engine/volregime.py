"""
Volatility regime / compression detector (the SWING timing filter).
====================================================================
Big monthly moves are BORN from volatility compression: when daily ATR%% and
Bollinger-band width both sit in the bottom quartile of their own 1-year
history, energy is coiled and the next expansion tends to be large. The mirror
read: an EXPANDED regime late in a move is where swings die, not start.

This module answers one question for the swing layer: "is NOW a time when a
big move can start?" It never gives direction - direction stays with the
existing composite. Pure OHLCV, no new data source, fully backtestable.

  build(df, cfg) -> dict(state=COMPRESSED|NORMAL|EXPANDED, atr_pctile,
                         bbw_pctile, squeeze, squeeze_days, weekly_bbw_pctile)
  series(df, cfg) -> pd.DataFrame of the same gauges for every bar (backtest)
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _atr(df: pd.DataFrame, n: int) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def _pctile_rank(s: pd.Series, look: int) -> pd.Series:
    """Rolling percentile rank (0..100) of each value within its own trailing window."""
    return s.rolling(look, min_periods=max(30, look // 4)).rank(pct=True) * 100


def series(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    vc = cfg.get("volregime", {})
    atr_len = int(vc.get("atr_len", 14))
    bb_len = int(vc.get("bb_len", 20))
    look = int(vc.get("pctile_lookback", 365))
    sq = float(vc.get("squeeze_pctile", 25))
    ex = float(vc.get("expand_pctile", 75))

    close = df["close"]
    atr_pct = _atr(df, atr_len) / close                     # ATR as % of price
    mid = close.rolling(bb_len).mean()
    sd = close.rolling(bb_len).std()
    bbw = (4 * sd) / mid                                    # (upper-lower)/mid

    out = pd.DataFrame(index=df.index)
    out["atr_pctile"] = _pctile_rank(atr_pct, look)
    out["bbw_pctile"] = _pctile_rank(bbw, look)
    out["squeeze"] = (out["atr_pctile"] <= sq) & (out["bbw_pctile"] <= sq)
    out["expanded"] = (out["atr_pctile"] >= ex) & (out["bbw_pctile"] >= ex)
    return out


def build(df: pd.DataFrame, cfg: dict) -> dict | None:
    vc = cfg.get("volregime", {})
    if not vc.get("enabled", True):
        return None
    ser = series(df, cfg)
    last = ser.iloc[-1]
    if not np.isfinite(last["atr_pctile"]) or not np.isfinite(last["bbw_pctile"]):
        return dict(state="UNKNOWN", note="not enough history for percentiles")

    state = ("COMPRESSED" if bool(last["squeeze"]) else
             "EXPANDED" if bool(last["expanded"]) else "NORMAL")

    # how long has the squeeze been building (consecutive squeeze bars)
    sq_days = 0
    for v in ser["squeeze"].values[::-1]:
        if not v:
            break
        sq_days += 1
    # was there a squeeze recently? (a breakout bar itself is no longer squeezed)
    recent = int(vc.get("recent_bars", 10))
    recent_squeeze = bool(ser["squeeze"].tail(recent).any())

    # weekly gauge (best-effort; needs ~ bb_len weeks of daily data)
    weekly_bbw_pctile = None
    try:
        wk = df[["open", "high", "low", "close"]].resample("W").agg(
            dict(open="first", high="max", low="min", close="last")).dropna()
        if len(wk) >= 60:
            mid = wk["close"].rolling(20).mean()
            sd = wk["close"].rolling(20).std()
            bbw_w = (4 * sd) / mid
            pr = _pctile_rank(bbw_w, min(104, len(wk)))
            v = pr.iloc[-1]
            weekly_bbw_pctile = round(float(v), 0) if np.isfinite(v) else None
    except Exception:                                       # noqa: BLE001
        pass

    return dict(state=state,
                atr_pctile=round(float(last["atr_pctile"]), 0),
                bbw_pctile=round(float(last["bbw_pctile"]), 0),
                squeeze=bool(last["squeeze"]), squeeze_days=sq_days,
                recent_squeeze=recent_squeeze,
                weekly_bbw_pctile=weekly_bbw_pctile,
                note=("energia felhúzva - nagy mozgás születhet" if state == "COMPRESSED"
                      else "kitágult vol - a mozgás inkább érett, mint induló" if state == "EXPANDED"
                      else "átlagos vol-környezet"))
