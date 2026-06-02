"""
Backtest with a strict train/test split (out-of-sample).

We build the VDB only on the TRAIN slice, then walk the TEST slice day by day,
take the composite direction, and measure forward-h accuracy + a toy PnL that
only enters in the bias direction with a fixed R target. This is the honesty
check: a model that only looks good in-sample is worthless.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import vdb, signal


def run(df: pd.DataFrame, events: pd.DataFrame, cfg: dict, train_frac: float = 0.7):
    n = len(df)
    split = int(n * train_frac)
    close = df["close"]
    horizon = cfg["signal"]["horizon"]

    # VDB from train only
    db = vdb.build(close.iloc[:split], events.iloc[:split],
                   cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))

    preds, actuals, rets = [], [], []
    for i in range(split, n - horizon):
        sig = signal.composite(df.iloc[:i + 1], events.iloc[:i + 1], db, cfg, at=-1)
        if sig["bias"] == "FLAT":
            continue
        fwd = close.iloc[i + horizon] / close.iloc[i] - 1.0
        dir_pred = 1 if sig["bias"] == "UP" else -1
        preds.append(dir_pred)
        actuals.append(1 if fwd > 0 else -1)
        rets.append(dir_pred * fwd)               # PnL if we trade the bias

    preds = np.array(preds); actuals = np.array(actuals); rets = np.array(rets)
    if len(preds) == 0:
        return dict(error="no non-flat signals in test window")

    acc = float((preds == actuals).mean())
    avg = float(rets.mean())
    gains = rets[rets > 0].sum(); losses = -rets[rets < 0].sum()
    pf = float(gains / losses) if losses > 0 else float("inf")
    equity = np.cumprod(1 + rets)
    mdd = float((equity / np.maximum.accumulate(equity) - 1).min())

    return dict(
        train_bars=split, test_bars=n - split, signals=len(preds),
        directional_accuracy=round(acc * 100, 1),
        avg_return_per_signal=round(avg * 100, 3),
        profit_factor=round(pf, 2) if np.isfinite(pf) else None,
        total_return=round((equity[-1] - 1) * 100, 1),
        max_drawdown=round(mdd * 100, 1),
        note="OUT-OF-SAMPLE: VDB built on train, evaluated on unseen test bars.")
