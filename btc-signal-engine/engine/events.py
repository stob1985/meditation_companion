"""
Phase 1 - Event detectors.

Each detector flags days where an "event" is true. These mirror the rows in the
first screenshot's EVENT table:
  Saturday + TOM, Pivot, RSI OS, Vol Spike, No Streak, Full Moon, ASIA/Late Asia, Planets P2
"""
from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
from . import astro


# ---- indicators ----------------------------------------------------------
def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = atr(df, n)
    pdi = 100 * pd.Series(plus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / tr
    mdi = 100 * pd.Series(minus, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / tr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean().fillna(0)


# ---- detectors ------------------------------------------------------------
def detect(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]

    # calendar: Saturday OR turn-of-month (last 2 / first 2 days)
    dow = df.index.dayofweek                                  # Mon=0 .. Sun=6
    dom = df.index.day
    days_in_month = df.index.days_in_month
    tom = (dom <= 2) | (dom >= days_in_month - 1)
    out["Saturday + TOM"] = (dow == 5) | tom

    # pivot (a confirmed swing high/low with lookback L)
    L = cfg["events"]["pivot_lookback"]
    hi = df["high"]; lo = df["low"]
    piv_hi = (hi == hi.rolling(2 * L + 1, center=True).max())
    piv_lo = (lo == lo.rolling(2 * L + 1, center=True).min())
    out["Pivot"] = (piv_hi | piv_lo).fillna(False)

    # RSI oversold
    r = rsi(close, cfg["events"]["rsi_len"])
    out["RSI OS (36)"] = r < cfg["events"]["rsi_os"]

    # volume spike
    vmean = df["volume"].rolling(cfg["events"]["vol_lookback"]).mean()
    out["Vol Spike"] = df["volume"] > cfg["events"]["vol_mult"] * vmean

    # no streak (neither in a strong up nor down run)
    sign = np.sign(close.diff()).fillna(0)
    streak = sign.groupby((sign != sign.shift()).cumsum()).cumcount() + 1
    out["No Streak"] = (streak * sign).abs() <= cfg["events"]["streak_max"]

    # full moon
    illum = pd.Series([astro.moon_illumination(d.date()) for d in df.index], index=df.index)
    out["Full Moon"] = illum >= cfg["events"]["full_moon_pct"]

    # session: on daily data this is a proxy (close>open => "asia up").
    # On intraday data replace with real session timestamps.
    out["ASIA / Late Asia"] = (close < df["open"])            # placeholder polarity

    # planets P2: any active aspect today
    if cfg["astro"]["enabled"]:
        nasp = pd.Series([astro.aspects(d.date(), cfg["astro"]["orb"])["n_aspects"]
                          for d in df.index], index=df.index)
        out["Planets P2"] = nasp > 0
    else:
        out["Planets P2"] = False

    # keep diagnostics for the dashboard
    out.attrs["rsi"] = r
    out.attrs["atr"] = atr(df)
    out.attrs["adx"] = adx(df)
    out.attrs["illum"] = illum
    return out.astype(bool)
