"""
Money flow / CVD module.
====================================================================
The transcript calls CVD + money flow "the meta and the cheat code". Two parts:

1) df-based CVD (always available, backtestable):
     signed volume = sign(close-open) * volume ; CVD = cumulative sum.
     We read the recent SLOPE of CVD -> a flow bias, and compare it to price:
       price up   + CVD up   = healthy advance
       price up   + CVD down = weak / distribution
       price down + CVD up   = absorption / accumulation
   This is folded into the composite (small weight) and is computable on any
   historical bar, so the backtest reflects it without lookahead.

2) spot-vs-perp divergence (best-effort, live OKX, last bar only):
     If perp taker flow pushes hard one way while spot stays flat/opposite, the
     move is "perp-driven" (manipulation-prone) and lower quality. Shown as a
     confluence overlay only; degrades gracefully when offline.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def cvd_bias(df: pd.DataFrame, win: int = 30) -> dict:
    """df-derived CVD slope + price/CVD agreement over the last `win` bars."""
    sign = np.sign(df["close"] - df["open"]).fillna(0.0)
    cvd = (sign * df["volume"]).cumsum()
    w = min(win, len(df) - 1)
    if w < 3:
        return dict(bias="FLAT", up=0.5, slope=0.0, agree="n/a")
    cvd_chg = float(cvd.iloc[-1] - cvd.iloc[-w])
    px_chg = float(df["close"].iloc[-1] / df["close"].iloc[-w] - 1.0)
    norm = float(df["volume"].tail(w).sum()) or 1.0
    slope = cvd_chg / norm                              # -1..1-ish
    bias = "LONG" if slope > 0.03 else "SHORT" if slope < -0.03 else "FLAT"
    # agreement between price move and flow
    if px_chg > 0 and slope > 0:
        agree = "confirm-up"
    elif px_chg < 0 and slope < 0:
        agree = "confirm-down"
    elif px_chg > 0 and slope < 0:
        agree = "weak-up (distribution)"
    elif px_chg < 0 and slope > 0:
        agree = "absorption (accum)"
    else:
        agree = "flat"
    up = 0.5 + max(-0.5, min(0.5, slope * 4))           # map slope -> up prob
    return dict(bias=bias, up=round(up, 3), slope=round(slope, 4), agree=agree)


def okx_spot_perp_divergence(period: str = "1D", limit: int = 14) -> dict | None:
    """Best-effort: OKX taker buy/sell volume for SPOT vs PERP (SWAP).
    Returns a divergence read, or None if offline / unavailable."""
    try:
        import requests
        url = "https://www.okx.com/api/v5/rubik/stat/taker-volume"
        sp = requests.get(url, params=dict(ccy="BTC", instType="SPOT",
                                           period=period, limit=limit), timeout=12).json()["data"]
        pp = requests.get(url, params=dict(ccy="BTC", instType="CONTRACTS",
                                           period=period, limit=limit), timeout=12).json()["data"]

        def _cvd(rows):                                 # [ts, buyVol, sellVol]
            b = sum(float(r[1]) for r in rows)
            s = sum(float(r[2]) for r in rows)
            tot = b + s or 1.0
            return (b - s) / tot                        # -1..1
        spot = _cvd(sp)
        perp = _cvd(pp)
        diverge = abs(perp - spot) > 0.15 and (np.sign(perp) != np.sign(spot) or abs(spot) < 0.03)
        return dict(spot=round(spot, 3), perp=round(perp, 3),
                    diverging=bool(diverge),
                    note=("perp-driven (spot not confirming)" if diverge
                          else "spot & perp aligned"))
    except Exception:                                   # noqa: BLE001
        return None
