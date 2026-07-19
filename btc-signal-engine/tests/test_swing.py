"""Smoke tests for the SWING layer (volregime + etfflow parsing + swing gates).

Run directly (no pytest needed):  python tests/test_swing.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import yaml                                                    # noqa: E402
from engine import (data, events as ev, vdb, signal, liquidity,  # noqa: E402
                    dwell as dwellmod, volregime, etfflow, swing, backtest)


def _cfg():
    path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def test_volregime():
    cfg = _cfg()
    df = data.make_synthetic()
    v = volregime.build(df, cfg)
    assert v is not None and v["state"] in ("COMPRESSED", "NORMAL", "EXPANDED", "UNKNOWN")
    if v["state"] != "UNKNOWN":
        assert 0 <= v["atr_pctile"] <= 100 and 0 <= v["bbw_pctile"] <= 100
    ser = volregime.series(df, cfg)
    assert {"atr_pctile", "bbw_pctile", "squeeze", "expanded"} <= set(ser.columns)
    print("  volregime OK:", v["state"], f"ATR p{v.get('atr_pctile')}")


def test_etfflow_parser():
    # offline parser check only (no network dependency in tests)
    assert etfflow._num("1,234.5") == 1234.5
    assert etfflow._num("(123.4)") == -123.4
    assert etfflow._num("-") == 0.0
    assert etfflow._num("<b>77.0</b>") == 77.0
    print("  etfflow parser OK")


def test_swing_gates_and_backtest():
    cfg = _cfg()
    df = data.make_synthetic()
    events = ev.detect(df, cfg)
    db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"],
                   horizons=tuple(cfg["vdb"]["horizons"]))
    dw = dwellmod.build(df, cfg)
    sig = signal.composite(df, events, db, cfg, at=-1, dwell=dw)
    liq = liquidity.build(df, cfg)
    vol = volregime.build(df, cfg)
    sw = swing.build(df, sig, liq, cfg, vol=vol)
    assert sw is not None and sw["status"] in ("ARMED", "WAIT")
    assert set(sw["gates"]) == {"weekly", "composite", "timing", "etf", "crowd", "gravity"}
    if sw["status"] == "ARMED":
        assert sw["risk"] > 0 and sw["rr1"] >= 0
    print("  swing gates OK:", sw["status"], f"{sw['n_ok']}/{sw['n_avail']}")

    bt = backtest.run_swing(df, events, cfg)
    assert "trades" in bt and "return_pct" in bt
    print("  swing backtest OK:", bt["trades"], "trades,", bt["return_pct"], "%")


if __name__ == "__main__":
    test_volregime()
    test_etfflow_parser()
    test_swing_gates_and_backtest()
    print("ALL SWING TESTS PASSED")
