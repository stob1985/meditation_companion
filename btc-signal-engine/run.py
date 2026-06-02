#!/usr/bin/env python3
"""
Entry point.

  python run.py                  # uses config.yaml (synthetic by default)
  python run.py --source live    # pull real Bybit daily data
  python run.py --backtest       # add the out-of-sample backtest report
"""
from __future__ import annotations
import argparse
import yaml
from engine import (data, events as ev, vdb, signal, liquidity, dashboard,
                    backtest, dwell as dwellmod, trade as trademod,
                    flow as flowmod, macro as macromod, sessions as sessmod)


def load_cfg(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def get_data(cfg):
    src = cfg["data"]["source"]
    if src == "live":
        return data.load_live(cfg["data"]["symbol"], cfg["data"]["interval"],
                              cfg["data"]["limit"], cfg["data"].get("exchange", "auto"))
    if src == "csv":
        return data.load_csv(cfg["data"]["csv_path"])
    return data.make_synthetic()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["synthetic", "live", "csv"])
    ap.add_argument("--backtest", action="store_true")
    ap.add_argument("--config", default="config.yaml")
    args = ap.parse_args()

    cfg = load_cfg(args.config)
    if args.source:
        cfg["data"]["source"] = args.source

    df = get_data(cfg)
    events = ev.detect(df, cfg)
    db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"],
                   horizons=tuple(cfg["vdb"]["horizons"]))
    dwell = dwellmod.build(df, cfg) if cfg.get("dwell", {}).get("enabled", True) else None
    sig = signal.composite(df, events, db, cfg, at=-1, dwell=dwell)
    liq = liquidity.build(df, cfg)
    trade = (trademod.plan(sig, liq, dwell or {}, cfg)
             if cfg.get("trade", {}).get("enabled", True) else None)

    # confluence overlays (best-effort / context, not backtested composite inputs)
    overlays = {}
    if cfg["data"]["source"] == "live":
        overlays["flow_div"] = flowmod.okx_spot_perp_divergence()
    overlays["macro"] = macromod.build(df, cfg)
    overlays["sessions"] = sessmod.build(df, cfg)

    print(dashboard.render(sig, liq, db, cfg, dwell=dwell, trade=trade, overlays=overlays))

    if args.backtest:
        bt = backtest.run(df, events, cfg)
        print("\n OUT-OF-SAMPLE BACKTEST")
        print(" " + "-" * 60)
        for k, v in bt.items():
            print(f"   {k:26s}: {v}")


if __name__ == "__main__":
    main()
