"""
Miner economics (mempool.space public API, live, best-effort; BTC only).
====================================================================
  - network hashrate (7d / 30d / peak) and the hash ribbon (30d vs 60d MA:
    30d < 60d = miner capitulation)
  - hashprice ($ per PH per day) = daily issuance x price / hashrate
  - difficulty adjustment: last change, next estimate, progress
  - ELECTRICITY BREAKEVEN ("shutdown price") per fleet efficiency (J/TH) and
    power price: below it a miner loses money on power alone and tends to
    sell reserves / switch off. All-in cost is roughly x1.4-1.7 of this.
Context only. In this data the hash-ribbon "recovery" was NOT a reliable buy
signal (Nov 2026 check: 9 up / 7 down after 90 days).
"""
from __future__ import annotations
import pandas as pd


def build(cfg: dict, price: float) -> dict | None:
    mc = cfg.get("mining", {})
    if not mc.get("enabled", True):
        return None
    if cfg.get("realflow", {}).get("inst_family", "BTC-USDT").split("-")[0] != "BTC":
        return None
    try:
        import requests
        g = lambda u: requests.get(u, timeout=20).json()
        hr = g("https://mempool.space/api/v1/mining/hashrate/1y")
        adj = g("https://mempool.space/api/v1/difficulty-adjustment")
        fees = g("https://mempool.space/api/v1/mining/blocks/fees/1w")
    except Exception:                                   # noqa: BLE001
        return None
    h = pd.Series({pd.to_datetime(x["timestamp"], unit="s"): x["avgHashrate"] for x in hr["hashrates"]}).sort_index() / 1e18
    if len(h) < 60:
        return None
    fee_btc = sum(x["avgFees"] for x in fees) / max(len(fees), 1) / 1e8 if fees else 0.02
    btc_day = 144 * (3.125 + fee_btc)
    h7, h30 = float(h.tail(7).mean()), float(h.tail(30).mean())
    s30, s60 = h.rolling(30).mean(), h.rolling(60).mean()
    cap = bool(s30.iloc[-1] < s60.iloc[-1])
    grid = {}
    for e in mc.get("eff_jth", [15, 17.5, 20, 25]):
        kwh_day = h7 * 1e6 * float(e) * 86400 / 3.6e6
        grid[e] = {p: round(kwh_day * float(p) / btc_day) for p in mc.get("power_usd_kwh", [0.05, 0.06])}
    eta = pd.to_datetime(adj.get("estimatedRetargetDate", 0), unit="ms") if adj.get("estimatedRetargetDate") else None
    return dict(hash7=round(h7), hash30=round(h30), peak=round(float(h.max())), peak_date=h.idxmax().date(),
                hashprice=round(btc_day * price / (h7 * 1e3), 1), btc_day=round(btc_day, 1),
                diff_prev=round(float(adj.get("previousRetarget", 0)), 2),
                diff_next=round(float(adj.get("difficultyChange", 0)), 2),
                diff_progress=round(float(adj.get("progressPercent", 0))), diff_eta=eta,
                ribbon_capitulation=cap, grid=grid)
