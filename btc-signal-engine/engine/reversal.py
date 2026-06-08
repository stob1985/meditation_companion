"""
Reversal / sweep-reclaim detector.
====================================================================
This is the missing piece that made the reference indicator flip UP while our
lagging trend model stayed DOWN. Straight from the video concept:

  "liquidity sweep of the lows -> reversal"

A BULLISH reversal = price wicks BELOW a recent swing low / liquidity magnet
(sweeps the stops & long-liquidations) but CLOSES BACK ABOVE it (reclaim), while
oversold - and is still holding above that level. The mirror (sweep a high +
reject) is BEARISH.

Pure price action over the last few bars -> backtestable, and it can OVERRIDE
the slow regime so the system is no longer structurally late to a turn.
"""
from __future__ import annotations
from .events import rsi as _rsi


def detect(df, cfg) -> dict:
    rc = cfg.get("reversal", {})
    lb = int(rc.get("swing_lookback", 10))
    confirm = int(rc.get("confirm_bars", 3))
    os_lvl = float(rc.get("rsi_os", 38))
    ob_lvl = float(rc.get("rsi_ob", 62))
    n = len(df)
    out = dict(signal=None, level=None, bars_ago=None, note="no sweep-reclaim")
    if n < lb + confirm + 2:
        return out
    rsi = _rsi(df["close"], 14)
    last_close = float(df["close"].iloc[-1])
    low, high, close = df["low"].values, df["high"].values, df["close"].values
    for k in range(1, confirm + 1):                      # most-recent bars first
        i = n - k
        prior_low = float(df["low"].iloc[i - lb:i].min())
        prior_high = float(df["high"].iloc[i - lb:i].max())
        # BULLISH: swept the low, closed back above, oversold, still holding
        if low[i] < prior_low and close[i] > prior_low and rsi.iloc[i] < os_lvl and last_close > prior_low:
            return dict(signal="BULL", level=round(prior_low, 1), bars_ago=k,
                        note=f"sweep+reclaim of {prior_low:,.0f} (low) {k} bar(s) ago, holding")
        # BEARISH: swept the high, closed back below, overbought
        if high[i] > prior_high and close[i] < prior_high and rsi.iloc[i] > ob_lvl and last_close < prior_high:
            return dict(signal="BEAR", level=round(prior_high, 1), bars_ago=k,
                        note=f"sweep+reject of {prior_high:,.0f} (high) {k} bar(s) ago")
    return out
