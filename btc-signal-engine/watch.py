#!/usr/bin/env python3
"""Hourly setup watcher: checks the trade triggers in watch_levels.yaml on CLOSED 1H candles
and prints RIASZTÁS (alert) with the full data snapshot when every condition of a setup is met.

Exit code 0 = no alert, 10 = alert. Usage: python3 watch.py
Only rule-based; 'all conditions met' is NOT a guarantee (see STATE.md validation table).
"""
import datetime as dt
import os
import sys

import pandas as pd
import requests
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OKX = "https://www.okx.com"


def _get(path, **params):
    for _ in range(3):
        try:
            return requests.get(OKX + path, params=params, timeout=20).json()["data"]
        except Exception:
            pass
    return []


def candles(inst, bar, limit=300):
    d = _get("/api/v5/market/candles", instId=inst, bar=bar, limit=limit)
    df = pd.DataFrame([r[:9] for r in d], columns=["t", "o", "h", "l", "c", "v", "vc", "vq", "confirm"])
    df[["o", "h", "l", "c", "vq"]] = df[["o", "h", "l", "c", "vq"]].astype(float)
    df["t"] = pd.to_datetime(df.t.astype("int64"), unit="ms")
    df["confirm"] = df.confirm.astype(int)
    return df.sort_values("t").reset_index(drop=True)


def wavetrend(df):
    ap = (df.h + df.l + df.c) / 3
    esa = ap.ewm(span=10, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=21, adjust=False).mean()
    return wt1, wt1.rolling(4).mean()


def fmt(x):
    return f"{x:,.0f}".replace(",", " ")


def main():
    cfg = yaml.safe_load(open(os.environ.get("WATCH_LEVELS") or os.path.join(HERE, "watch_levels.yaml")))
    until = os.environ.get("WATCH_UNTIL")  # replay/test: e.g. "2026-11-26 00:00" (UTC open time of last closed 1H)
    ecfg = yaml.safe_load(open(os.path.join(HERE, "config.yaml")))
    now = dt.datetime.now(dt.timezone.utc)

    perp = candles("BTC-USDT-SWAP", "1H", 100)
    closed = perp[perp.confirm == 1].reset_index(drop=True)
    if until:
        closed = closed[closed.t <= pd.Timestamp(until)].reset_index(drop=True)
    last = closed.iloc[-1]
    price = float(perp.iloc[-1].c)
    spot = candles("BTC-USDT", "1H", 300)
    spot_c = spot[spot.confirm == 1].reset_index(drop=True)
    if until:
        spot_c = spot_c[spot_c.t <= pd.Timestamp(until)].reset_index(drop=True)
    wt1, wt2 = wavetrend(spot_c)
    wt_green = wt1.iloc[-1] > wt2.iloc[-1] and wt1.iloc[-2] <= wt2.iloc[-2]
    wt_green_low = wt_green and wt1.iloc[-1] < -53
    w4 = candles("BTC-USDT", "4H", 300)
    w4 = w4[w4.confirm == 1].reset_index(drop=True)
    w41, w42 = wavetrend(w4)

    day = candles("BTC-USDT", "1Dutc", 300)
    day = day[day.confirm == 1].reset_index(drop=True)
    sma200 = day.c.rolling(200).mean().iloc[-1]
    e50, e200 = day.c.ewm(span=50).mean().iloc[-1], day.c.ewm(span=200).mean().iloc[-1]
    bear = day.c.iloc[-1] < sma200 and e50 < e200
    low60 = day.l.iloc[-60:].min()
    above_low = (price / low60 - 1) * 100
    atr_d = (day.h - day.l).rolling(14).mean().iloc[-1]

    ls_rows = _get("/api/v5/rubik/stat/contracts/long-short-account-ratio", ccy="BTC", period="5m")
    ls = float(ls_rows[0][1]) if ls_rows else float("nan")
    ls_1h = [round(float(r[1]), 2) for r in _get("/api/v5/rubik/stat/contracts/long-short-account-ratio",
                                                 ccy="BTC", period="1H")[:6]]
    oi = _get("/api/v5/rubik/stat/contracts/open-interest-history", instId="BTC-USDT-SWAP", period="1H", limit=7)
    oi_v = [float(r[3]) / 1e6 for r in oi]
    oi_chg = (oi_v[0] / oi_v[-1] - 1) * 100 if len(oi_v) > 1 else float("nan")
    fr = _get("/api/v5/public/funding-rate", instId="BTC-USDT-SWAP")
    funding = float(fr[0]["fundingRate"]) * 100 if fr else float("nan")

    extra = {}
    try:
        from engine import realflow as rf, oimap as om
        extra["cb"] = rf.coinbase_premium("BTC")
        extra["abs"] = rf.absorption("BTC")
        extra["oimap"] = om.build(ecfg)
    except Exception as e:  # best effort: alerts still work without these
        extra["err"] = str(e)

    cr = cfg["crowd"]
    lb = int(cfg.get("lookback_bars", 6))
    win = closed.iloc[-lb:]
    alerts, notes = [], []

    def first_close_after_touch(touch_hi=None, touch_lo=None, close_below=None, close_above=None):
        """True if the LAST closed candle is the first close back through the level after a touch in the window."""
        idx = None
        for i in range(len(win) - 1, -1, -1):
            r = win.iloc[i]
            if (touch_hi is not None and r.h >= touch_hi) or (touch_lo is not None and r.l <= touch_lo):
                idx = i
                break
        if idx is None:
            return False, None
        seg = win.iloc[idx:]
        for j in range(len(seg)):
            r = seg.iloc[j]
            ok = (close_below is not None and r.c < close_below) or (close_above is not None and r.c > close_above)
            if ok:
                return j == len(seg) - 1, seg
        return False, seg

    sample = os.environ.get("WATCH_SAMPLE")  # e.g. S1 → render that setup's message as a sample
    pos = cfg.get("position") or {}
    events = [(pd.Timestamp(e["t"]), float(e.get("window_h", 2)), e["name"]) for e in (cfg.get("events") or [])]
    cbp = (extra.get("cb") or {}).get("bp")
    absd = extra.get("abs") or {}

    def checklist(name, st, why):
        side = st["side"]
        if sample == name:
            entry = {"reject_down": st.get("close_below", 0) - 100, "break_down": st.get("level", 0),
                     "reclaim_up": sum(st.get("entries", [0])) / max(len(st.get("entries", [1])), 1),
                     "breakout_retest": st.get("level", 0)}[st["type"]]
        else:
            entry = float(last.c)
        stop, tg = st["stop"], st["targets"]
        risk = abs(entry - stop)
        rrs = [abs(t - entry) / risk if risk else 0 for t in tg]
        K, M = [], []  # (ok, label)
        if side == "short":
            K.append((ls > cr["ls_short_min"], f"tömeg L/S {ls:.2f} > {cr['ls_short_min']} (validált kontrár jel)"))
        else:
            K.append((ls <= cr["ls_long_max"], f"tömeg L/S {ls:.2f} ≤ {cr['ls_long_max']} (validált kapu)"))
        K.append((max(rrs) >= 2.0, f"R:R ≥ 2 (most {' / '.join(f'{r:.1f}' for r in rrs)})"))
        opp = pos.get("side") and pos.get("side") != side
        K.append((not opp, "nincs ellentétes nyitott pozíció (5. szabály)" if not opp
                  else f"NYITOTT {pos['side'].upper()} – előbb azt kell zárni (5. szabály)"))
        ev = [n for t, w, n in events if abs((now - t.tz_localize("UTC")).total_seconds()) <= w * 3600]
        K.append((not ev, "nincs esemény-ablak" if not ev else f"esemény-ablak: {', '.join(ev)}"))
        K.append((st.get("validated", True), "validált setup-típus" if st.get("validated", True)
                  else "NEM validált setup-típus"))
        if cbp is None:
            M.append((False, "Coinbase-prémium nem elérhető"))
        elif side == "short":
            M.append((cbp < -10, f"Coinbase-prémium {cbp:+.1f} bp < −10 (gyenge validált jel)"))
        else:
            M.append((cbp >= -10, f"Coinbase-prémium {cbp:+.1f} bp ≥ −10"))
        state = absd.get("state", "?")
        against = "ELNYELÉS" if side == "short" else "ELOSZTÁS"
        M.append((state != against, f"elnyelés-detektor: {state} (nem ellene)" if state != against
                  else f"elnyelés-detektor: {state} – ELLENE"))
        mr = bear and 5 <= above_low <= 12
        if side == "short":
            M.append((not mr, f"regime: az ár {above_low:.1f}%-kal a 60n mély fölött"
                      + (" – medvében itt 77% előbb +5% (ELLENE)" if mr else "")))
        else:
            M.append((True, f"regime: {'medve' if bear else 'nem medve'}, {above_low:.1f}% a 60n mély fölött"))
        perfect = all(o for o, _ in K) and all(o for o, _ in M)
        failed = [l for o, l in K + M if not o]
        size = "fél méret" if (side == "long" and ls > cr["ls_long_full"]) else "terv szerinti méret"
        tag = "MINTA – NEM VALÓS JEL · " if sample == name else ""
        lines = [f"{'✅ TÖKÉLETES' if perfect else '⚠ NEM tökéletes'} · {tag}{name} {side.upper()} — {st['desc']}",
                 f"   trigger: {why}",
                 f"   belépő ~{fmt(entry)} · stop {fmt(stop)} ({risk / entry * 100:.1f}%) · célok "
                 + " / ".join(fmt(t) for t in tg) + f" · {size}, 5x (20x esetén fél pozíció)",
                 "   KÖTELEZŐ:"] + [f"     {'✓' if o else '✗'} {l}" for o, l in K] + \
                ["   MEGERŐSÍTŐ:"] + [f"     {'✓' if o else '✗'} {l}" for o, l in M] + \
                ["   SZABÁLYOK: stop a csomó MÖGÖTT, nem mozdítjuk · T1-nél 50% zárás + stop break-evenre · "
                 "csak lezárt 1H gyertya számít"]
        return dict(perfect=perfect, failed=failed, text="\n".join(lines))

    for name, s in cfg["setups"].items():
        side, typ = s["side"], s["type"]
        fired, why = False, ""
        if typ == "reject_down":
            ev, seg = first_close_after_touch(touch_hi=s["touch"], close_below=s["close_below"])
            if ev and seg is not None and seg.h.max() < s["stop"]:
                fired, why = True, f"érintés {fmt(seg.h.max())}, 1H záró {fmt(last.c)} < {fmt(s['close_below'])}"
        elif typ == "break_down":
            prev = closed.iloc[-2]
            if last.c < s["level"] <= prev.c:
                fired, why = True, f"1H záró {fmt(last.c)} < {fmt(s['level'])} (előző {fmt(prev.c)})"
        elif typ == "reclaim_up":
            ev, seg = first_close_after_touch(touch_lo=s["touch"], close_above=s["close_above"])
            touched = (win.l <= s["touch"]).any()
            if ev and seg is not None and seg.l.min() > s["stop"]:
                fired, why = True, f"kisöprés {fmt(seg.l.min())}, 1H záró vissza {fmt(last.c)} > {fmt(s['close_above'])}"
            elif touched and wt_green_low and win.l.min() > s["stop"]:
                fired, why = True, f"zóna érintve ({fmt(win.l.min())}), 1H WT zöld kereszt {wt1.iloc[-1]:.1f}"
        elif typ == "breakout_retest":
            look = closed.iloc[-12:]
            above = look[look.c > s["level"]]
            if len(above):
                first_bo = above.index[0]
                if closed.loc[first_bo - 1].c <= s["level"] and last.name > first_bo \
                        and last.l <= s["level"] + 50 and last.c >= s["retest_low"] and last.c > last.o:
                    fired, why = True, f"kitörés {closed.loc[first_bo].t:%H}h, visszateszt {fmt(last.l)} tartott, záró {fmt(last.c)}"
            prev = closed.iloc[-2]
            if last.c > s["level"] >= prev.c:
                notes.append(f"{name}: 1H záró {fmt(last.c)} > {fmt(s['level'])} — kitörés, VÁRJ visszatesztre")
        if sample == name and not fired:
            fired, why = True, "MINTA – az árfeltételt itt feltételezzük"
        if fired:
            res = checklist(name, s, why)
            if res["perfect"]:
                alerts.append(res["text"])
            else:
                notes.append(f"{name}: árfeltétel teljesült ({why}), de NEM tökéletes: "
                             + ", ".join(res["failed"]))
                if sample == name:
                    alerts.append(res["text"])

    if pos.get("side") == "short":
        if last.c > pos["exit_close_above"]:
            alerts.append(f"■ KISZÁLLÁS a {fmt(pos['entry'])}-es SHORTBÓL — 1H záró {fmt(last.c)} > {fmt(pos['exit_close_above'])}")
        if closed.iloc[-1].h >= pos["hard_stop"]:
            alerts.append(f"■ A SHORT hard stopja ({fmt(pos['hard_stop'])}) elérve — csúcs {fmt(closed.iloc[-1].h)}")
        if closed.iloc[-1].l <= pos["targets"][0]:
            alerts.append(f"✔ SHORT T1 {fmt(pos['targets'][0])} elérve — 50% zárás, stop break-evenre ({fmt(pos['entry'])})")

    # ---------------- report ----------------
    hu = now + dt.timedelta(hours=1)
    head = ("MINTA" if sample else "RIASZTÁS") if alerts else "NINCS RIASZTÁS"
    print(f"=== {head} · {hu:%Y-%m-%d %H:%M} HU · lezárt 1H gyertya: {last.t + dt.timedelta(hours=1):%H}:00–{last.t + dt.timedelta(hours=2):%H}:00 HU ===")
    for a in alerts:
        print(a)
    for n in notes:
        print("• " + n)
    print(f"\nÁr {fmt(price)} · 1H O/H/L/C {fmt(last.o)}/{fmt(last.h)}/{fmt(last.l)}/{fmt(last.c)}")
    print(f"Regime: {'MEDVE' if bear else 'nem medve'} · 60n mély {fmt(low60)} (+{above_low:.1f}%) · napi ATR {fmt(atr_d)}")
    print(f"L/S {ls:.2f} (1H: {ls_1h}) · OI 6h {oi_chg:+.1f}% ({oi_v[0]:.0f}M$) · funding {funding:+.4f}%")
    print(f"WT 1H {wt1.iloc[-1]:.1f}/{wt2.iloc[-1]:.1f}{' ZÖLD KERESZT' if wt_green else ''} · "
          f"WT 4H {w41.iloc[-1]:.1f}/{w42.iloc[-1]:.1f}")
    if "cb" in extra and extra["cb"]:
        print(f"Coinbase-prémium {extra['cb']['usd']:+.0f}$ ({extra['cb']['bp']:+.1f} bp)")
    if "abs" in extra and extra["abs"]:
        a = extra["abs"]
        print(f"Taker 4h {a['net_musd']:+.0f}M$ (z {a['z']:+.2f}), ár {a['px_chg']:+.2f}% → {a['state']}")
    if "oimap" in extra and extra["oimap"]:
        b = extra["oimap"]["bands"]
        print("OI-likvidáció fent/lent (M$): " + " · ".join(f"±{k}% {v[0]:.0f}/{v[1]:.0f}" for k, v in b.items()))
        print("  fent: " + ", ".join(f"{p/1000:.1f}k {m:.0f}M" for p, m in extra["oimap"]["top_above"][:4])
              + " | lent: " + ", ".join(f"{p/1000:.1f}k {m:.0f}M" for p, m in extra["oimap"]["top_below"][:4]))
    if "err" in extra:
        print("(extra adatok hiba: " + extra["err"] + ")")
    print("\nFigyelem: a riasztás azt jelenti, hogy a terv MINDEN feltétele teljesült — nem garancia.")
    return 0 if sample else (10 if alerts else 0)


def telegram(text):
    """Send via Telegram bot. Needs env TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID (set by the user in the
    environment settings, never committed)."""
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        return "telegram: nincs beállítva"
    try:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", timeout=20,
                          json={"chat_id": chat, "text": text[:4000], "disable_web_page_preview": True})
        return f"telegram {r.status_code}" + ("" if r.ok else f" {r.json().get('description', '')}")
    except Exception as e:
        return f"telegram hiba: {type(e).__name__}"


def telegram_chat_ids():
    """Helper: list chat ids that messaged the bot (send /start to your bot first)."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not tok:
        return "nincs TELEGRAM_BOT_TOKEN"
    d = requests.get(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=20).json()
    ids = {(u.get("message") or {}).get("chat", {}).get("id") for u in d.get("result", [])}
    ids.discard(None)
    return f"chat id(k): {sorted(ids)}" if ids else "nincs üzenet — írj /start-ot a botodnak, majd futtasd újra"


def notify(text, title="BTC RIASZTAS", priority="high"):
    """Push the report to Telegram (if configured) and to the ntfy topic from watch_levels.yaml."""
    out = [telegram(f"🚨 {title}\n\n{text}")]
    try:
        cfg = yaml.safe_load(open(os.environ.get("WATCH_LEVELS") or os.path.join(HERE, "watch_levels.yaml")))
        topic = (cfg.get("notify") or {}).get("ntfy_topic")
        if not topic:
            return " · ".join(out + ["nincs ntfy_topic"])
        r = requests.post(f"https://ntfy.sh/{topic}", data=text.encode("utf-8"), timeout=20,
                          headers={"Title": title, "Priority": priority, "Tags": "rotating_light"})
        out.append(f"ntfy {r.status_code}")
    except Exception as e:
        out.append(f"ntfy hiba: {e}")
    return " · ".join(out)


if __name__ == "__main__":
    if "--tg-chatid" in sys.argv:
        print(telegram_chat_ids())
        sys.exit(0)
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main()
    text = buf.getvalue()
    print(text, end="")
    if os.environ.get("WATCH_SAMPLE") and "--send" in sys.argv:
        print(notify("MINTA uzenet (nem valos jel)\n\n" + text, title="BTC MINTA", priority="default"))
    elif "--test-notify" in sys.argv:
        print(notify("TESZT ertesites (nem valos jel)\n\n" + text, title="BTC TESZT", priority="default"))
    elif code == 10:
        print(notify(text))
    sys.exit(code)
