"""
VDB - Virtual Event Database.

For every event, look at every historical day where it fired and measure the
forward return over 1/3/5 trading days. Aggregate into the stats shown in the
screenshots:
  WR-1d/3d/5d, AVG-1d/3d/5d, EXPECT, PF, AVG-MDD, BEST-3d, WRST-3d, DB-QUAL, n
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _fwd_return(close: pd.Series, h: int) -> pd.Series:
    return close.shift(-h) / close - 1.0


def _max_drawdown_fwd(close: pd.Series, h: int) -> pd.Series:
    """Worst close-to-close drop within the next h days (negative number)."""
    out = pd.Series(index=close.index, dtype=float)
    arr = close.values
    n = len(arr)
    for i in range(n):
        end = min(i + h + 1, n)
        window = arr[i:end]
        if len(window) < 2:
            out.iloc[i] = np.nan
            continue
        running_min = np.minimum.accumulate(window)
        dd = (running_min - window[0]) / window[0]
        out.iloc[i] = dd.min()
    return out


def build(close: pd.Series, events: pd.DataFrame, cap: int = 500,
          horizons=(1, 3, 5)) -> dict:
    """Returns {event_name: stats_dict}."""
    fr = {h: _fwd_return(close, h) for h in horizons}
    mdd5 = _max_drawdown_fwd(close, max(horizons))
    db = {}
    for ev in events.columns:
        mask = events[ev].fillna(False).values
        idx = np.where(mask)[0]
        if len(idx) > cap:                       # keep most recent `cap`
            idx = idx[-cap:]
        if len(idx) == 0:
            continue
        rec = {"n": len(idx)}
        for h in horizons:
            r = fr[h].iloc[idx].dropna()
            if len(r) == 0:
                continue
            wins = (r > 0).mean()
            avg = r.mean()
            gains = r[r > 0].sum()
            losses = -r[r < 0].sum()
            pf = (gains / losses) if losses > 0 else np.inf
            rec[f"wr_{h}"] = round(wins * 100, 1)
            rec[f"avg_{h}"] = round(avg * 100, 3)
            rec[f"pf_{h}"] = round(pf, 2) if np.isfinite(pf) else 9.99
            rec[f"expect_{h}"] = round(avg * 100, 3)         # expectancy ~ mean ret
        m = mdd5.iloc[idx].dropna()
        rec["avg_mdd"] = round(m.mean() * 100, 2) if len(m) else np.nan
        r3 = fr[3].iloc[idx].dropna()
        rec["best_3"] = round(r3.max() * 100, 1) if len(r3) else np.nan
        rec["wrst_3"] = round(r3.min() * 100, 1) if len(r3) else np.nan

        # recent performance: LAST-5 avg return + last-N win rate + EDGE label
        hr = max(horizons)
        r_all = fr[hr].iloc[idx].dropna()
        last5 = r_all.tail(5)
        lastN = r_all.tail(10)
        rec["last5"] = round(last5.mean() * 100, 2) if len(last5) else np.nan
        rec["ln_wr"] = round((lastN > 0).mean() * 100, 0) if len(lastN) else np.nan
        hist_wr = rec.get(f"wr_{hr}", 50)
        hist_dir = 1 if hist_wr > 53 else -1 if hist_wr < 47 else 0
        rec_dir = (1 if rec["ln_wr"] > 55 else -1 if rec["ln_wr"] < 45 else 0) \
            if not np.isnan(rec["ln_wr"]) else 0
        if hist_dir != 0 and rec_dir == hist_dir:
            rec["edge"] = "EDGE↑" if hist_dir > 0 else "EDGE↓"
        elif hist_dir != 0 and rec_dir == -hist_dir:
            rec["edge"] = "FADE"           # recent contradicts the historical edge
        else:
            rec["edge"] = "NEUTRAL"

        # DB quality: how full the sample is + how stable WR across horizons
        fill = min(len(idx) / cap, 1.0)
        wr_vals = [rec.get(f"wr_{h}", 50) for h in horizons]
        stab = 1 - (np.std(wr_vals) / 50)
        rec["db_qual"] = int(round(max(0, min(1, 0.5 * fill + 0.5 * stab)) * 100))
        db[ev] = rec
    return db
