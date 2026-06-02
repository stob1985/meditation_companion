"""
Session sequence module (Asia / London / New York).
====================================================================
The transcript trades sessions constantly and quotes conditional stats like
"Asia pumped, London pumped -> 74% chance New York pumps". This needs INTRADAY
data (timestamps within the day). We split each day's bars into three UTC
windows, take each session's return sign, then estimate:

  P(NY up | Asia dir, London dir)   over the available history.

On daily data there are no intraday sessions, so this returns a note and is
skipped. Switch config data.interval to "60" or "120" to activate it.

UTC session windows (approx):
  Asia   00:00-07:00
  London 07:00-13:00
  NewYork 13:00-21:00
"""
from __future__ import annotations
import numpy as np
import pandas as pd

_SESS = {"Asia": (0, 7), "London": (7, 13), "NewYork": (13, 21)}


def _session_of(hour: int) -> str | None:
    for name, (a, b) in _SESS.items():
        if a <= hour < b:
            return name
    return None


def build(df: pd.DataFrame, cfg: dict) -> dict | None:
    if not cfg.get("sessions", {}).get("enabled", True):
        return None
    # need intraday: more than ~3 bars per calendar day on average
    days = df.index.normalize()
    if df.index.size / max(1, days.nunique()) < 3:
        return dict(intraday=False,
                    note="daily data - set data.interval to '60'/'120' for sessions")

    sess = pd.Series([_session_of(h) for h in df.index.hour], index=df.index)
    ret = df["close"].pct_change().fillna(0.0)
    rows = []
    for day, grp in ret.groupby(days):
        rec = {"day": day}
        for name in _SESS:
            mask = (sess.loc[grp.index] == name)
            rec[name] = int(np.sign(grp[mask].sum())) if mask.any() else 0
        rows.append(rec)
    tab = pd.DataFrame(rows)
    if len(tab) < 10:
        return dict(intraday=True, note="not enough session-days yet")

    # conditional probability table for NY given (Asia, London)
    cond = {}
    for a in (1, -1):
        for l in (1, -1):
            sub = tab[(tab["Asia"] == a) & (tab["London"] == l)]
            if len(sub):
                p_up = float((sub["NewYork"] > 0).mean())
                cond[(a, l)] = dict(n=len(sub), p_ny_up=round(p_up * 100, 1))

    # today's read so far
    today = tab.iloc[-1]
    key = (today["Asia"], today["London"])
    today_pred = cond.get(key)
    return dict(intraday=True, n_days=len(tab), conditional=cond,
                today=dict(asia=int(today["Asia"]), london=int(today["London"])),
                today_pred=today_pred)
