"""
Position state — makes the engine STATEFUL across runs.
====================================================================
The gap the user spotted: a signal issued on Monday silently vanished by
Wednesday. Now an actionable plan is recorded to a small JSON file; on every
later run the open position is MANAGED against the bars that printed since it
opened (break-even, T1 take-50%, T2, stop, just like the backtest) and its
status (open P/L, what got hit, or final outcome) is reported. One tracked
position at a time. Reset with `python run.py --reset`.
"""
from __future__ import annotations
import json
import os
import pandas as pd


def load(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:                                   # noqa: BLE001
        return None


def save(path: str, pos: dict):
    with open(path, "w") as f:
        json.dump(pos, f, indent=2)


def clear(path: str):
    if os.path.exists(path):
        os.remove(path)


def open_from_plan(plan: dict, ts) -> dict:
    return dict(side=plan["side"], mode=plan.get("mode", "levels"),
                entry=plan["entry"], stop_init=plan["stop"], stop=plan["stop"],
                t1=plan["t1"], t2=plan["t2"], opened_ts=str(ts),
                partial_done=False, be_done=False)


def manage(pos: dict, df: pd.DataFrame, cfg: dict):
    """Walk the bars since the position opened; apply BE/T1/T2/stop.
    Returns (pos_or_None, status_dict)."""
    be_R = float(cfg.get("trade", {}).get("be_R", 0.5))
    side, e = pos["side"], pos["entry"]
    R = abs(e - pos["stop_init"]) or 1.0
    cur_stop, partial, be = pos["stop"], pos["partial_done"], pos["be_done"]
    realized, events = 0.0, []
    ts = pd.Timestamp(pos["opened_ts"])
    if ts.tz is None and df.index.tz is not None:
        ts = ts.tz_localize(df.index.tz)
    fut = df[df.index > ts]
    for ts2, row in fut.iterrows():
        hi, lo = float(row["high"]), float(row["low"])
        d = str(ts2.date())
        if not be and ((side == "LONG" and hi >= e + be_R * R) or
                       (side == "SHORT" and lo <= e - be_R * R)):
            cur_stop, be = e, True
            events.append((d, "stop → break-even"))
        if not partial and ((side == "LONG" and hi >= pos["t1"]) or
                            (side == "SHORT" and lo <= pos["t1"])):
            r1 = (pos["t1"] / e - 1) * 100 if side == "LONG" else (e / pos["t1"] - 1) * 100
            realized += 0.5 * r1
            partial, cur_stop, be = True, e, True
            events.append((d, f"T1 fél zár {r1:+.1f}%"))
        hit_stop = (lo <= cur_stop) if side == "LONG" else (hi >= cur_stop)
        if hit_stop:
            rs = (cur_stop / e - 1) * 100 if side == "LONG" else (e / cur_stop - 1) * 100
            realized += (0.5 if partial else 1.0) * rs
            events.append((d, f"STOP {cur_stop:,.0f} ({rs:+.1f}%)"))
            return None, dict(state="closed", realized_pct=round(realized, 2),
                              side=side, entry=e, events=events)
        hit_t2 = (hi >= pos["t2"]) if side == "LONG" else (lo <= pos["t2"])
        if partial and hit_t2:
            r2 = (pos["t2"] / e - 1) * 100 if side == "LONG" else (e / pos["t2"] - 1) * 100
            realized += 0.5 * r2
            events.append((d, f"T2 zár {r2:+.1f}%"))
            return None, dict(state="closed", realized_pct=round(realized, 2),
                              side=side, entry=e, events=events)
    pos.update(stop=cur_stop, partial_done=partial, be_done=be)
    cur = float(df["close"].iloc[-1])
    unreal = (cur / e - 1) * 100 if side == "LONG" else (e / cur - 1) * 100
    return pos, dict(state="open", realized_pct=round(realized, 2),
                     unrealized_pct=round(unreal * (0.5 if partial else 1.0), 2),
                     current=cur, entry=e, side=side, stop=cur_stop,
                     t1=pos["t1"], t2=pos["t2"], partial=partial, be=be,
                     opened=pos["opened_ts"][:10], events=events)
