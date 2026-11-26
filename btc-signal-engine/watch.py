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

    for name, s in cfg["setups"].items():
        side, typ = s["side"], s["type"]
        crowd_ok = ls > cr["ls_short_min"] if side == "short" else ls <= cr["ls_long_max"]
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
        if fired:
            if crowd_ok:
                size = ""
                if side == "long":
                    size = "TELJES méret" if ls <= cr["ls_long_full"] else "FÉL méret (L/S 2,3–2,6)"
                elif name == "L2":
                    size = "FÉL méret (nem validált)"
                alerts.append(f"▶ {name} {side.upper()} BELÉPŐ — {s['desc']}\n   {why}\n   L/S {ls:.2f} ✓ · "
                              f"stop {fmt(s['stop'])} · célok {' / '.join(fmt(t) for t in s['targets'])} {size}")
            else:
                notes.append(f"{name}: ár-feltétel teljesült ({why}), DE a tömegkapu tilt (L/S {ls:.2f})")

    pos = cfg.get("position") or {}
    if pos.get("side") == "short":
        if last.c > pos["exit_close_above"]:
            alerts.append(f"■ KISZÁLLÁS a {fmt(pos['entry'])}-es SHORTBÓL — 1H záró {fmt(last.c)} > {fmt(pos['exit_close_above'])}")
        if closed.iloc[-1].h >= pos["hard_stop"]:
            alerts.append(f"■ A SHORT hard stopja ({fmt(pos['hard_stop'])}) elérve — csúcs {fmt(closed.iloc[-1].h)}")
        if closed.iloc[-1].l <= pos["targets"][0]:
            alerts.append(f"✔ SHORT T1 {fmt(pos['targets'][0])} elérve — 50% zárás, stop break-evenre ({fmt(pos['entry'])})")

    # ---------------- report ----------------
    hu = now + dt.timedelta(hours=1)
    head = "RIASZTÁS" if alerts else "NINCS RIASZTÁS"
    print(f"=== {head} · {hu:%Y-%m-%d %H:%M} HU · lezárt 1H gyertya: {last.t + dt.timedelta(hours=1):%H}:00–{last.t + dt.timedelta(hours=2):%H}:00 HU ===")
    for a in alerts:
        print(a)
    for n in notes:
        print("• " + n)
    print(f"\nÁr {fmt(price)} · 1H O/H/L/C {fmt(last.o)}/{fmt(last.h)}/{fmt(last.l)}/{fmt(last.c)}")
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
    return 10 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
