"""
Dashboard - prints a terminal panel that mimics the two screenshots.
Pure stdlib formatting (no deps) so it runs anywhere.
"""
from __future__ import annotations


def _c(s, w, align="<"):
    s = str(s)
    return f"{s:{align}{w}}"[:w]


def _leg(L, lbl, t):
    """Render one directional trade leg."""
    nrr = t["net_rr"] if t["net_rr"] is not None else t["rr"]
    L.append(f"   {lbl} {t['side']}   R:R {t['rr']} (net {nrr})  [floor {t['rr_min']:.0f}]")
    L.append(f"     entry  {t['entry']:>11.1f}")
    L.append(f"     stop   {t['stop']:>11.1f}   (-{t['risk']:.0f}  ·  {t['stop_src']})")
    L.append(f"     target {t['target']:>11.1f}   (+{t['reward']:.0f}  ·  {t['target_src']})")
    L.append(f"     size   bet ${t['bet_usd']:.0f} × {t['leverage']}x = "
             f"${t['notional']:.0f}  ·  {t['qty']} BTC   (MMR {t['mmr']*100:.2f}%)")
    L.append(f"     P/L    net win +${t['net_profit']:.2f}   net loss -${t['net_loss']:.2f}   "
             f"(fees ${t['fees']:.2f} + funding ${t['funding']:.2f})")
    safe = "OK" if t["liq_safe"] else "⚠ UNSAFE"
    L.append(f"     liq    {t['liq_price']:>11.1f}   [{safe}]  max safe ~{t['max_safe_leverage']}x")
    for w in t["warnings"]:
        L.append(f"     ⚠ {w}")


def render(sig: dict, liq: dict, db: dict, cfg: dict,
           dwell: dict = None, trade: dict = None, overlays: dict = None) -> str:
    H = cfg["signal"]["horizon"]
    L = []
    L.append("=" * 92)
    L.append(f" BTCUSDT  ·  {sig['date']}  ·  px {sig['price']:.1f}   "
             f"RSI {sig['rsi']:.0f}  ADX {sig['adx']:.1f}  "
             f"MTF {sig['mtf']:+d} ({sig['regime']})")
    L.append("=" * 92)

    # ---- Phase 1 event table -------------------------------------------
    hdr = (_c("EVENT", 22) + _c("DN%", 6) + _c("UP%", 6) + _c("WIN", 6) +
           _c("n", 6) + _c("EXPECT", 8) + _c("PF", 6) + _c("LAST5", 8) +
           _c("LNWR", 6) + _c("QUAL", 6) + _c("BIAS", 10) + _c("EDGE", 8) + "M")
    L.append(hdr)
    L.append("-" * 100)
    for r in sorted(sig["rows"], key=lambda x: -x["qual"]):
        l5 = f"{r['last5']:+.1f}%" if r.get("last5") is not None and r["last5"] == r["last5"] else "-"
        lw = f"{r['ln_wr']:.0f}" if r.get("ln_wr") is not None and r["ln_wr"] == r["ln_wr"] else "-"
        L.append(_c(r["event"], 22) + _c(r["dn"], 6) + _c(r["up"], 6) +
                 _c(r["win"], 6) + _c(r["n"], 6) + _c(f"{r['expect']:+.2f}%", 8) +
                 _c(r["pf"], 6) + _c(l5, 8) + _c(lw, 6) + _c(r["qual"], 6) +
                 _c(r["bias"], 10) + _c(r.get("edge", "-"), 8) + r["mark"])
    L.append("-" * 100)

    # ---- composite ------------------------------------------------------
    L.append(f" COMPOSITE ({sig['active']} active)   "
             f"UP {sig['up']}%  |  DN {sig['dn']}%   "
             f"Bias: {sig['bias']}   {sig['strength']}   Q:{sig['q']}")
    f = sig["forecast"]
    L.append(f" FORECAST  {H}-day @ {f['conf']}%      "
             f"\u25b2 {f['hi']}     \u25bc {f['lo']}")
    rev = sig.get("reversal")
    if rev and rev.get("signal"):
        ic = "🟢↑" if rev["signal"] == "BULL" else "🔴↓"
        L.append(f" REVERSAL  {ic} {rev['signal']} sweep-reclaim  ·  {rev['note']}")
    if sig["planet"]:
        p = sig["planet"]
        asp = "  ".join(a["pair"] + f"({a['arc']}\u00b0)" for a in p["active"]) or "none"
        L.append(f" PLANET COMPOSITE  UP {p['up']}% | DN {p['dn']}%  Bias:{p['bias']}"
                 f"   aspects: {asp}")
    L.append("=" * 92)

    # ---- liquidity map --------------------------------------------------
    nl, ns = liq["long_short"]
    br = f"{liq['bounce_rate']}% ({liq['bounce_events']} ev)" if liq.get("bounce_rate") is not None else "n/a"
    L.append(f" LIQUIDITY MAP (PROXY)   active {liq['active']}   "
             f"Long/Short {nl}/{ns}   nearest {liq['nearest_atr']} ATR   bounce {br}")
    L.append(f"   Liq Imbalance: {liq['imbalance']}    CVD Bias: {liq['cvd_bias']}    "
             f"ATR {liq['atr']}   zones ATR\u00d7{liq['zone_mult']}")
    fl = sig.get("flow")
    if fl:
        L.append(f"   Money Flow (CVD): {fl['bias']}  slope {fl['slope']}  \u00b7  {fl['agree']}")
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
        if dwell.get("dwell_bias") and dwell["dwell_bias"] != "NEUTRAL":
            L.append(f"   ↳ RULE: price {dwell['location']} block → {dwell['dwell_bias']} "
                     f"(conf {dwell['dwell_conf']})  target {dwell['dwell_target']} "
                     f"· {dwell['dwell_target_src']}")
        L.append("=" * 92)

    # ---- trade plan -----------------------------------------------------
    if trade and trade.get("mode") in ("levels", "reversal"):
        if trade["side"] == "WAIT":
            L.append(f" TRADE PLAN (LEVEL ENTRY)   ⏳ WAIT  ·  {trade['reason']}")
        else:
            t = trade
            safe = "OK" if t["liq_safe"] else "⚠ UNSAFE"
            hdr = "REVERSAL ⚡" if t["mode"] == "reversal" else "LEVEL ENTRY"
            L.append(f" TRADE PLAN ({hdr})   {t['side']}  "
                     f"({t['bias']} conv {t['conv']}%, {t['strength']})")
            L.append(f"   entry  {t['entry']:>11.1f}  {t['entry_type']}  ("
                     f"{t['pullback_atr']} ATR a szintig)")
            L.append(f"   stop   {t['stop']:>11.1f}   (-{t['risk']:.0f}  ·  level + {0.25}ATR)")
            L.append(f"   T1     {t['t1']:>11.1f}   (R:R {t['rr1']})  → take 50% + stop to break-even")
            L.append(f"   T2     {t['t2']:>11.1f}   (R:R {t['rr2']})  → runner")
            L.append(f"   size   bet ${t['bet_usd']:.0f} × {t['leverage']}x = ${t['notional']:.0f}"
                     f"  ·  {t['qty']} BTC")
            L.append(f"   liq    {t['liq_price']:>11.1f}   [{safe}]")
            L.append(f"   ▸ {t['plan_note']}")
        L.append("=" * 92)
    elif trade:
        s = trade["side"]
        if s in ("FLAT", "VOID"):
            icon = "⏸" if s == "FLAT" else "🚫"
            L.append(f" TRADE PLAN   {icon}  NO TRADE ({s})  ·  {trade['reason']}")
        elif s == "HEDGE":
            L.append(f" TRADE PLAN   ⇅  HEDGE  ({trade['bias']} {trade['strength']}, "
                     f"{trade['confluence']})   lean: {trade['net_lean']}")
            L.append(f"   {trade['reason']}")
            L.append(f"   net exposure: {trade['net_side']}  ${trade['net_notional']:.0f} notional")
            _leg(L, "▲", trade["long_leg"])
            _leg(L, "▼", trade["short_leg"])
        else:
            L.append(f" TRADE PLAN   ({trade['bias']} {trade['strength']}, "
                     f"confluence {trade['confluence']}, flow {trade.get('flow','n/a')})")
            _leg(L, "→", trade)
        L.append("=" * 92)

    # ---- multi-exchange liquidation map --------------------------------
    if overlays and overlays.get("multi_liq"):
        ml = overlays["multi_liq"]
        L.append(f" MULTI-EXCHANGE LIQUIDATIONS   venues {ml['n_venues']}: "
                 f"{', '.join(ml['venues'])}   consensus {ml['consensus']}")
        pv = "  ".join(f"{k}:{v['imbalance'].split()[-1][:4]}/{v['cvd_bias'][:1]}"
                       for k, v in ml["per_venue"].items())
        L.append(f"   per-venue (imb/cvd): {pv}")
        L.append("   ── confluence ABOVE (venues agree → stronger magnet) ──")
        for c in sorted(ml["clusters_above"], key=lambda c: -c["n_venues"])[:5]:
            L.append(f"      {c['price']:>11.1f}   {c['n_venues']}venue  "
                     f"x{c['count']:<3} {c['tiers']}  [{','.join(v[:3] for v in c['venues'])}]")
        L.append(f"   ▶ price {ml['ref_price']:.1f}")
        L.append("   ── confluence BELOW ──")
        for c in sorted(ml["clusters_below"], key=lambda c: -c["n_venues"])[:5]:
            L.append(f"      {c['price']:>11.1f}   {c['n_venues']}venue  "
                     f"x{c['count']:<3} {c['tiers']}  [{','.join(v[:3] for v in c['venues'])}]")
        L.append("=" * 92)

    # ---- liquidity gravity + trap watch --------------------------------
    if overlays and overlays.get("trap") and overlays["trap"].get("status") != "OFF":
        tw = overlays["trap"]; g = tw.get("gravity") or {}
        arrow = {"DOWN": "⬇ LEFELÉ húz", "UP": "⬆ FELFELÉ húz", "BALANCED": "⚖ kiegyenlített"}.get(g.get("direction"), "?")
        ba, bb = g.get("biggest_above"), g.get("biggest_below")
        L.append(f" LIQUIDITY GRAVITY   {arrow}   (lenti húzóerő {g.get('below_pull')} vs fenti {g.get('above_pull')}"
                 + (f", arány {g.get('ratio')}" if g.get('ratio') else "") + ")")
        if ba or bb:
            L.append("   legnagyobb mágnes:  "
                     + (f"LENT {bb['price']:,.0f} (x{bb['count']})" if bb else "lent —") + "   vs   "
                     + (f"FENT {ba['price']:,.0f} (x{ba['count']})" if ba else "fent —"))
        if tw.get("zone"):
            z1, z2 = tw["zone"]
            icon = "🪤" if tw["status"] == "ARMED" else "👁"
            name = "BIKACSAPDA" if tw.get("kind") == "bull-trap" else "MEDVECSAPDA"
            L.append(f"   {icon} {name}-FIGYELŐ  csali-zóna {min(z1,z2):,.0f}–{max(z1,z2):,.0f}   "
                     f"státusz: {tw['status']} ({tw.get('n_ok',0)}/5 jel)")
            ck = tw.get("checks") or {}
            lbl = {"cvd_div": "CVD-divergencia", "crowd_long": "tömeg-long", "crowd_short": "tömeg-short",
                   "funding_hot": "funding forró", "no_acceptance": "nincs acceptance",
                   "sweep_reject": "sweep-reject", "sweep_reclaim": "sweep-reclaim"}
            L.append("      jelek: " + "  ".join(f"{lbl.get(k,k)} {'✓' if v else '✗'}" for k, v in ck.items()))
            if tw.get("plan"):
                pl = tw["plan"]; e1, e2 = pl["entry_zone"]
                L.append(f"      ⚡ ÉLES CSAPDA-TERV: {pl['side']} a {min(e1,e2):,.0f}–{max(e1,e2):,.0f} zónában  "
                         f"stop {pl['stop']:,.0f}  cél {pl['target']:,.0f}  (R:R {pl['rr']})")
        elif tw.get("note"):
            L.append(f"   👁 {tw['note']}")
        L.append("=" * 92)

    # ---- BUY / SHORT zones (always shown) ------------------------------
    if overlays and overlays.get("zones"):
        z = overlays["zones"]

        def _zline(tag, zz, kind):
            if not zz:
                return f"   {tag}: n/a (nincs klaszter ezen az oldalon)"
            q = []
            if not zz["fresh"]:
                q.append(f"⚠ kopott {zz['taps']}x")
            if zz["just_tested"]:
                q.append("⚠ frissen tesztelve")
            qa = ("  [" + ", ".join(q) + "]") if q else "  [friss ✓]"
            tgt = f"{zz['target']:,.0f}" if zz["target"] else "n/a"
            return (f"   {tag}: {zz['lo']:,.0f}–{zz['hi']:,.0f}  ({zz['dist_atr']} ATR, x{zz['count']})"
                    f"  → cél {tgt}  stop {zz['stop']:,.0f}{qa}")

        def _show_clean(prim, clean):
            return (prim and (not prim["fresh"] or prim["just_tested"]) and clean
                    and clean["level"] != prim["level"] and (clean["dist_atr"] or 99) <= 6)

        L.append(" ZONES (mindig)")
        L.append(_zline("🔴 SHORT (rally eladása)", z.get("short"), "short"))
        if _show_clean(z.get("short"), z.get("short_clean")):
            L.append(_zline("      ↳ tisztább SHORT", z.get("short_clean"), "short"))
        L.append(_zline("🟢 BUY   (dip vétele)", z.get("buy"), "buy"))
        if _show_clean(z.get("buy"), z.get("buy_clean")):
            L.append(_zline("      ↳ tisztább BUY", z.get("buy_clean"), "buy"))
        L.append("=" * 92)

    # ---- confluence overlays -------------------------------------------
    if overlays:
        printed = False
        mac = overlays.get("macro")
        if mac:
            ser = "  ".join(f"{k}:{v['corr']}" for k, v in mac["series"].items()
                            if v["corr"] is not None)
            L.append(f" MACRO  bias {mac['bias']} (score {mac['score']})   corr[{ser}]")
            printed = True
        fd = overlays.get("flow_div")
        if fd:
            tag = "⚠ DIVERGING" if fd["diverging"] else "aligned"
            L.append(f" SPOT/PERP FLOW  spot {fd['spot']}  perp {fd['perp']}  [{tag}] · {fd['note']}")
            printed = True
        rf = overlays.get("realflow")
        if rf:
            parts = [f"flow {rf['flow_bias']}"]
            if rf.get("ls_ratio"):
                ls = rf["ls_ratio"]
                parts.append(f"L/S {ls['ratio']} (crowd {ls['crowd']} → contra {ls['contrarian']})")
            if rf.get("oi"):
                parts.append(f"OI ${rf['oi']['oi_usd']}B {rf['oi']['trend']}")
            if rf.get("funding"):
                parts.append(f"funding {rf['funding']['funding']}")
            L.append(" REAL FLOW (live)  " + "   ".join(parts))
            L.append(f"   real liquidations seen: {rf['n_liqs']} (recent, OKX)")
            printed = True
        se = overlays.get("sessions")
        if se:
            if not se.get("intraday"):
                L.append(f" SESSIONS  {se.get('note','')}")
            else:
                td = se.get("today", {})
                if se.get("today_pred"):
                    tp = se["today_pred"]
                    L.append(f" SESSIONS  Asia {td.get('asia',0):+d} London {td.get('london',0):+d} → "
                             f"P(NY↑)={tp['p_ny_up']}%  (n={tp['n']}, {se['n_days']} nap)")
                else:
                    L.append(f" SESSIONS (Asia/London/NY, {se['n_days']} nap) — ma Asia {td.get('asia',0):+d} "
                             f"London {td.get('london',0):+d} (még nem teljes)")
                cond = se.get("conditional") or {}
                key = {1: "↑", -1: "↓"}
                cells = "  ".join(f"A{key[a]}L{key[l]}→NY↑ {v['p_ny_up']}%" for (a, l), v in sorted(cond.items()))
                if cells:
                    L.append(f"   feltételes: {cells}")
            printed = True
        if printed:
            L.append("=" * 92)

    # ── DrProfit Framework Layer ───────────────────────────────────────────────
    drp = sig.get("drprofit")
    if drp:
        stage_lbl = drp.get("stage_label", "")
        box = drp.get("box", {})
        crowd = drp.get("crowd", {})
        dca = drp.get("dca", {})
        bias = drp.get("drp_bias", "NEUTRAL")
        bias_icon = "⬆" if bias == "UP" else "⬇" if bias == "DOWN" else "⟺"

        L.append(" DRPROFIT FRAMEWORK   TA / LCA / Psychological")
        L.append(f"   Stage {drp['stage']}/6: {stage_lbl}")
        L.append(
            f"   Box: {box.get('zone','?')} ({box.get('box_pct','?')}%  "
            f"lo {box.get('box_lo',0):,.0f} – hi {box.get('box_hi',0):,.0f})  "
            f"{'⚡ BORDER = ACTIONABLE' if box.get('border') else '◻ mid-box → WAIT'}"
        )
        L.append(f"   Crowd: {crowd.get('sentiment','?')}")
        if dca.get("active"):
            L.append(f"   ✅ DCA ZONE ACTIVE  {dca['side']} {dca['zone']}  → {dca['instruction']}")
        else:
            L.append(f"   ◻ {dca.get('instruction','Price outside all DCA zones')}")
        L.append(f"   DrProfit Bias: {bias_icon} {bias}  (drp_up={drp.get('drp_up',0.5):.0%})")
        L.append("=" * 92)

    return "\n".join(L)
