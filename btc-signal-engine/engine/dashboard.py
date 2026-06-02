"""
Dashboard - prints a terminal panel that mimics the two screenshots.
Pure stdlib formatting (no deps) so it runs anywhere.
"""
from __future__ import annotations


def _c(s, w, align="<"):
    s = str(s)
    return f"{s:{align}{w}}"[:w]


def render(sig: dict, liq: dict, db: dict, cfg: dict,
           dwell: dict = None, trade: dict = None) -> str:
    H = cfg["signal"]["horizon"]
    L = []
    L.append("=" * 92)
    L.append(f" BTCUSDT  ·  {sig['date']}  ·  px {sig['price']:.1f}   "
             f"RSI {sig['rsi']:.0f}  ADX {sig['adx']:.1f}  "
             f"MTF {sig['mtf']:+d} ({sig['regime']})")
    L.append("=" * 92)

    # ---- Phase 1 event table -------------------------------------------
    hdr = (_c("EVENT", 24) + _c("DN%", 6) + _c("UP%", 6) + _c("WIN", 6) +
           _c("n", 6) + _c("EXPECT", 9) + _c("PF", 6) + _c("QUAL", 6) + _c("BIAS", 10) + "MARK")
    L.append(hdr)
    L.append("-" * 92)
    for r in sorted(sig["rows"], key=lambda x: -x["qual"]):
        L.append(_c(r["event"], 24) + _c(r["dn"], 6) + _c(r["up"], 6) +
                 _c(r["win"], 6) + _c(r["n"], 6) + _c(f"{r['expect']:+.2f}%", 9) +
                 _c(r["pf"], 6) + _c(r["qual"], 6) + _c(r["bias"], 10) + r["mark"])
    L.append("-" * 92)

    # ---- composite ------------------------------------------------------
    L.append(f" COMPOSITE ({sig['active']} active)   "
             f"UP {sig['up']}%  |  DN {sig['dn']}%   "
             f"Bias: {sig['bias']}   {sig['strength']}   Q:{sig['q']}")
    f = sig["forecast"]
    L.append(f" FORECAST  {H}-day @ {f['conf']}%      "
             f"\u25b2 {f['hi']}     \u25bc {f['lo']}")
    if sig["planet"]:
        p = sig["planet"]
        asp = "  ".join(a["pair"] + f"({a['arc']}\u00b0)" for a in p["active"]) or "none"
        L.append(f" PLANET COMPOSITE  UP {p['up']}% | DN {p['dn']}%  Bias:{p['bias']}"
                 f"   aspects: {asp}")
    L.append("=" * 92)

    # ---- liquidity map --------------------------------------------------
    nl, ns = liq["long_short"]
    L.append(f" LIQUIDITY MAP (PROXY)   active {liq['active']}   "
             f"Long/Short {nl}/{ns}   nearest {liq['nearest_atr']} ATR")
    L.append(f"   Liq Imbalance: {liq['imbalance']}    CVD Bias: {liq['cvd_bias']}    "
             f"ATR {liq['atr']}   zones ATR\u00d7{liq['zone_mult']}")
    tiers = "  ".join(f"{t}x:{liq['tiers_count'][t]}" for t in (10, 25, 50, 100))
    L.append(f"   tiers  {tiers}")
    L.append("   ── magnets ABOVE (short liq / resistance) ──")
    for c in liq["clusters_above"][:6]:
        L.append(f"      {c['price']:>11.1f}   x{c['count']:<2}  {c['tiers']}")
    L.append(f"   ▶ price {liq['price']:.1f}")
    L.append("   ── magnets BELOW (long liq / targets) ──")
    for c in liq["clusters_below"][:6]:
        L.append(f"      {c['price']:>11.1f}   x{c['count']:<2}  {c['tiers']}")
    L.append("=" * 92)

    # ---- dwell blocks ---------------------------------------------------
    if dwell and not dwell.get("empty"):
        va = dwell["value_area"]
        L.append(f" DWELL PROFILE   state {dwell['state']}   "
                 f"run {dwell['current_run']} bars  dwell-ratio {dwell['dwell_ratio']}%  "
                 f"(band ±{dwell['band']})")
        L.append(f"   POC {dwell['poc']}   value area {va[0]} – {va[1]}   "
                 f"blocks {dwell['n_blocks']}")
        for b in dwell["blocks"][:5]:
            tag = {"above": "▲", "below": "▼", "around": "◆"}.get(b["side"], " ")
            L.append(f"   {tag} {b['lo']:>10.1f} – {b['hi']:<10.1f}  "
                     f"time {b['dwell']:>4.1f}%  vol {b['vol_share']:>4.1f}%")
        L.append("=" * 92)

    # ---- trade plan -----------------------------------------------------
    if trade:
        if trade["side"] == "FLAT":
            L.append(f" TRADE PLAN   ⏸  NO TRADE  ·  {trade['reason']}")
        else:
            t = trade
            L.append(f" TRADE PLAN   {t['side']}  ({t['bias']} {t['strength']}, "
                     f"liq {t['confluence']})   R:R {t['rr']}  [floor {t['rr_min']:.0f}]")
            L.append(f"   entry  {t['entry']:>11.1f}")
            L.append(f"   stop   {t['stop']:>11.1f}   (-{t['risk']:.0f}  ·  {t['stop_src']})")
            L.append(f"   target {t['target']:>11.1f}   (+{t['reward']:.0f}  ·  {t['target_src']})")
            L.append(f"   size   bet ${t['bet_usd']:.0f} × {t['leverage']}x = "
                     f"${t['notional']:.0f} notional  ·  {t['qty']} BTC")
            L.append(f"   P/L    win +${t['profit_usd']:.2f}   loss -${t['loss_usd']:.2f}   "
                     f"(risk {t['risk_pct']:.1f}% of bet)")
            safe = "OK" if t["liq_safe"] else "⚠ UNSAFE"
            L.append(f"   liq    {t['liq_price']:>11.1f}   [{safe}]  "
                     f"max safe lev ~{t['max_safe_leverage']}x")
            for w in t["warnings"]:
                L.append(f"   ⚠ {w}")
        L.append("=" * 92)

    return "\n".join(L)
