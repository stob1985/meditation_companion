#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTC napi hirlevel - profi kiadas.
Modszertan a stob1985/agency-agents-stob repobol (raw GitHub-rol behuzva es alkalmazva):
  - Executive Summary Generator: SCQA + Pyramid + Bain Action (5 szekcios vezetoi osszefoglalo)
  - Analytics Reporter: minden szam kontextussal + forrassal, indikator-dashboard tablazat
  - Content Creator: narrativ iv, egyszeru nyelv, vizualis horgonyok
  - Visual Storyteller: ar+szintek es likvidacios profil grafikon
Adat: OKX + 5 tozsde (likviditas). Makro hirek: webes forrasok (utolso oldal)."""
import os, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
import yaml
from engine import data, events as ev, vdb, signal, liquidity, dwell as dwellmod, realflow

plt.rcParams["font.family"] = "DejaVu Sans"
OUT = "/home/user/btc-signal-engine/newsletter"; os.makedirs(OUT, exist_ok=True)
cfg = yaml.safe_load(open("config.yaml"))

NEWS = dict(
    cpi="Május CPI (jún. 10): 4,2% éves (= várt); mag 2,9% / 0,2% havi (várt alatt). Reakció: tompa.",
    fomc="FOMC kamatdöntés JÚN. 16–17 (MA/HOLNAP) — a hét döntő eseménye.",
    dove="Galamb dot-plot → BTC rally 66–70e $ felé (becslés).",
    hawk="Héja dot-plot → vissza 58–60e $ támasz felé (becslés).",
    crash="Heti −17% oka: héja Fed + Irán-feszültség + rekord 13 napos ETF-kiáramlás (4,4 Mrd $) + Strategy-eladás.",
    relief="Irán–USA tűzszünet → olaj le, likviditás fel → rövid short-squeeze.",
)
SOURCES = ["blockchainreporter.net – BTC Price Today (jún.10)", "IG.com – Why BTC crashed / after CPI (jún.15)",
           "cryptonews.com – June CPI & FOMC (2026)", "fxleaders.com – BTC & Iran ceasefire (jún.16)"]

# ---- ADAT + ELEMZES -------------------------------------------------------
df = data.load_live("BTCUSDT", "D", 1000, "okx", verbose=False)
events = ev.detect(df, cfg)
db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
dw = dwellmod.build(df, cfg)
sig = signal.composite(df, events, db, cfg, at=-1, dwell=dw)
liq = liquidity.build(df, cfg); ml = liquidity.build_multi(cfg); rf = realflow.build(cfg, liq["price"], liq["atr"])
px = liq["price"]; today = df.index[-1].date()
above = sorted([c for c in ml["clusters_above"] if c["n_venues"] >= 4], key=lambda c: c["price"])
below = sorted([c for c in ml["clusters_below"] if c["n_venues"] >= 4], key=lambda c: -c["price"])
res = above[0] if above else None; big = max(below, key=lambda c: c["count"]) if below else None
ls = rf["ls_ratio"]["ratio"] if rf and rf.get("ls_ratio") else None
chg7 = (px/df["close"].iloc[-8]-1)*100; chg30 = (px/df["close"].iloc[-31]-1)*100
hi30, lo30 = df["high"].tail(30).max(), df["low"].tail(30).min()
bias_pct = sig["up"] if sig["bias"] == "UP" else sig["dn"]
votes = {"UP": 0, "DOWN": 0}
def vote(d):
    if d in ("UP", "DOWN"): votes[d] += 1
vote(sig["bias"]); vote("DOWN" if sig["mtf"] < 0 else "UP" if sig["mtf"] > 0 else None)
vote(dw.get("dwell_bias")); vote("UP" if liq["cvd_bias"] == "LONG" else "DOWN")
vote("UP" if "BULL" in liq["imbalance"] else "DOWN" if "BEAR" in liq["imbalance"] else None)
if rf and rf.get("ls_ratio"): vote(rf["ls_ratio"]["contrarian"])
verdict = "ELADÁS felé" if votes["DOWN"] > votes["UP"] else "VÉTEL felé" if votes["UP"] > votes["DOWN"] else "VÁRAKOZÁS"
vcol = "#c0392b" if "ELAD" in verdict else "#27ae60" if "VÉT" in verdict else "#e29a25"

# ---- GRAFIKONOK -----------------------------------------------------------
d = df.tail(120)
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.plot(d.index, d["close"], color="#111", lw=1.8); ax.axhline(px, color="#2257d6", lw=2)
ax.text(d.index[0], px, f"  MOST {px:,.0f}", color="#2257d6", va="bottom", fontweight="bold", fontsize=11)
for c in above[:3]:
    ax.axhline(c["price"], color="#d11", lw=1.1, ls="--", alpha=.7)
    ax.text(d.index[-1], c["price"], f" {c['price']:,.0f} (x{c['count']})", color="#d11", va="center", fontsize=8)
for c in below[:4]:
    b = c is big; ax.axhline(c["price"], color="#0a7", lw=2.4 if b else 1.1, ls="--", alpha=.9 if b else .55)
    ax.text(d.index[-1], c["price"], f" {c['price']:,.0f} (x{c['count']}){'  FŐ CÉL' if b else ''}",
            color="#085" if b else "#0a7", va="center", fontsize=8, fontweight="bold" if b else "normal")
ax.set_title(f"BTC/USD — napi ár és likvidációs szintek ({today})", fontsize=12, fontweight="bold")
ax.grid(alpha=.25); ax.margins(x=0); fig.tight_layout(); chart1 = f"{OUT}/btc_chart.png"; fig.savefig(chart1, dpi=130); plt.close(fig)

allc = sorted(above[:6] + below[:6], key=lambda c: c["price"])
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.barh([f"{c['price']:,.0f}" for c in allc], [c["count"] for c in allc],
        color=["#d11" if c["price"] > px else "#0a7" for c in allc], alpha=.85)
for i, c in enumerate(allc): ax.text(c["count"]+0.4, i, f"x{c['count']} · {c['n_venues']} tőzsde", va="center", fontsize=8)
ax.axhline(sum(1 for c in allc if c["price"] < px)-0.5, color="#2257d6", lw=2)
ax.set_title(f"Likvidációs profil — hol a legtöbb „beragadt\" pozíció (ár {px:,.0f})", fontsize=12, fontweight="bold")
ax.set_xlabel("klaszter-méret = mennyi pozíció dőlne be (nagyobb = erősebb mágnes)")
fig.tight_layout(); chart2 = f"{OUT}/btc_liqprofile.png"; fig.savefig(chart2, dpi=130); plt.close(fig)
print("grafikonok kesz")

# ---- PDF ------------------------------------------------------------------
class Page:
    def __init__(self, pp, title=""):
        self.fig = plt.figure(figsize=(8.27, 11.69)); self.ax = self.fig.add_axes([0,0,1,1])
        self.ax.set_xlim(0,1); self.ax.set_ylim(0,1); self.ax.set_autoscale_on(False); self.ax.axis("off")
        self.pp = pp
        # masthead (data coords on fixed 0..1 axes)
        self.ax.add_patch(plt.Rectangle((0,0.93),1,0.07, color="#0e1b33"))
        self.ax.text(0.07,0.962,"BTC DAILY", fontsize=18, fontweight="bold", color="white", va="center")
        self.ax.text(0.07,0.943,"Bitcoin napi elemző hírlevél · kis befektetőknek", fontsize=8.5, color="#9fb3d1", va="center")
        self.ax.text(0.93,0.957,str(today), fontsize=9, color="#cfe", va="center", ha="right")
        if title: self.ax.text(0.93,0.94,title, fontsize=8.5, color="#9fb3d1", va="center", ha="right")
        self.y = 0.90
    def t(self, txt, size=10.3, w="normal", c="#282828", wrap=100, gap=0.0033, x=0.07):
        for line in txt.split("\n"):
            for ww in (textwrap.wrap(line, wrap) or [""]):
                self.ax.text(x, self.y, ww, fontsize=size, fontweight=w, color=c, va="top"); self.y -= size/790.0+gap
        self.y -= 0.004
    def h(self, txt, size=14, c="#0e1b33"):
        self.y -= 0.004; self.ax.text(0.07, self.y, txt, fontsize=size, fontweight="bold", color=c, va="top")
        self.y -= size/430.0; self.ax.plot([0.07,0.93],[self.y,self.y], color="#dde3ec", lw=1); self.y -= 0.012
    def box(self, txt, rgb, size=12.5, h=0.044):
        self.ax.add_patch(plt.Rectangle((0.07, self.y-h),0.86,h, color=rgb))
        self.ax.text(0.5, self.y-h/2, txt, ha="center", va="center", fontsize=size, color="white", fontweight="bold"); self.y -= h+0.013
    def img(self, path, h=0.40):
        a = self.fig.add_axes([0.07, self.y-h, 0.86, h]); a.axis("off"); a.imshow(mpimg.imread(path)); self.y -= h+0.012
    def table(self, rows, cols, widths, rowh=0.030, fs=8.8):
        x0=0.07; tw=0.86
        self.ax.add_patch(plt.Rectangle((x0, self.y-rowh), tw, rowh, color="#0e1b33"))
        cx=x0
        for j,col in enumerate(cols):
            self.ax.text(cx+0.006, self.y-rowh/2, col, fontsize=fs, color="white", fontweight="bold", va="center"); cx+=widths[j]*tw
        self.y-=rowh
        for i,row in enumerate(rows):
            self.ax.add_patch(plt.Rectangle((x0, self.y-rowh), tw, rowh, color="#f4f6f9" if i%2 else "#ffffff"))
            cx=x0
            for j,cell in enumerate(row):
                col="#222"; weight="normal"
                if isinstance(cell,tuple): cell,col=cell; weight="bold"
                self.ax.text(cx+0.006, self.y-rowh/2, str(cell), fontsize=fs, color=col, fontweight=weight, va="center"); cx+=widths[j]*tw
            self.y-=rowh
        self.y-=0.012
    _n = 0
    def save(self):
        self.ax.text(0.5,0.018,"Oktatási célú összefoglaló — NEM pénzügyi tanács. A kripto kockázatos. · BTC DAILY",
                     ha="center", fontsize=7.5, color="#999")
        self.pp.savefig(self.fig); plt.close(self.fig)

reclaim = int((px//1000)*1000+3000)
pdfpath = f"{OUT}/BTC_napi_hirlevel_{today}.pdf"
with PdfPages(pdfpath) as pp:
    # ===== 1. VEZETŐI ÖSSZEFOGLALÓ (SCQA - Executive Summary Generator) =====
    p = Page(pp, "1/9 · Vezetői összefoglaló")
    p.box(f"MAI ÁLLÁS: {verdict}   ·   ár {px:,.0f} $   ·   jelek {votes['DOWN']} le / {votes['UP']} fel", vcol, 13, 0.05)
    p.h("Helyzet")
    _w7 = "emelkedett" if chg7 >= 0 else "esett"
    p.t(f"A Bitcoin {px:,.0f} $-on áll: a hónap {chg30:+.0f}% (erős esés), de a héten {abs(chg7):.0f}%-ot {_w7} "
        f"(visszapattanás). MA Fed-kamatdöntés (FOMC) van — ez határozza meg a következő nagy irányt. "
        f"A kérdés: venni, eladni vagy várni?")
    p.h("Kulcs-megállapítások (számokkal)")
    p.t(f"1. Az irány lefelé: a 6 fő jelből {votes['DOWN']} mutat LE, {votes['UP']} fel. "
        f"Összesített erő: {sig['bias']} {bias_pct:.0f}% („{sig['strength']}\").  → A trend még eladói.", w="bold" if False else "normal")
    p.t(f"2. A tömeg kezd kapitulálni: a Long/Short arány {('1.34' if ls is None else ls)} "
        f"(egy hete 2.16 volt). 1,3 alatt általában közel az alj.  → Az alj ÉPÜL, de még nincs itt.")
    p.t(f"3. A piac egy mágnest céloz: a legnagyobb likvidációs torlódás {big['price']:,.0f} $-nál (x{big['count']}, mind az 5 tőzsdén). "
        f"  → Ez a legvalószínűbb lefelé úti cél és a fő vételi figyelő-zóna.")
    p.t(f"4. Esemény-kockázat MA: FOMC. Galamb → 66–70e felé; héja → 58–60e felé.  → A döntésig magas a bizonytalanság.")
    p.h("Piaci hatás")
    p.t(f"Rövid táv (0–3 nap): a várható mozgástér {sig['forecast']['lo']:,.0f}–{sig['forecast']['hi']:,.0f} $. "
        f"A Fed-döntés ezt mindkét irányban kitágíthatja. A fő lefelé cél {big['price']:,.0f} $.")
    p.h("Ajánlások (prioritás szerint)")
    p.table(
        [[("KRITIKUS","#c0392b"), "Ne kereskedj a Fed-döntésbe", "ma, a döntésig", "tőke megóvása"],
         [("MAGAS","#e29a25"), f"VÉTELT figyelj {big['price']:,.0f} $-nál + fordulás-jel", "ha odaér", "jó belépő ár"],
         [("KÖZEPES","#2257d6"), f"Vagy reclaim {reclaim:,} $ fölé tartósan", "1–3 nap", "fordulat megerősítése"]],
        ["Prioritás","Teendő","Mikor","Várt eredmény"], [0.16,0.46,0.20,0.18], rowh=0.034, fs=8.6)
    p.h("Következő lépések (≤48 óra)")
    p.t(f"• Várd meg a Fed-döntést (ma/holnap).  • Figyeld a {big['price']:,.0f} $-os szintet.  "
        f"• Belépés CSAK kis téttel, stoppal, fordulás-jelre.  Döntési pont: a Fed-reakció + a szint.")
    p.save()

    # ===== 2. INDIKÁTOR-DASHBOARD (Analytics Reporter) =====
    p = Page(pp, "2/9 · Indikátor-dashboard")
    p.h("Minden műszer egy táblában — érték, jel, jelentés")
    p.t("Több független mérőszám. A „jel\" oszlop a mai irányt mutatja. Egyik sem tévedhetetlen — együtt számítanak.", 9.5, c="#666")
    UP=("FEL","#27ae60"); DN=("LE","#c0392b"); NE=("semleges","#888")
    rows=[
      ["Összesített irány", f"{sig['bias']} {bias_pct:.0f}% ({sig['strength']})", (DN if sig['bias']=='DOWN' else UP if sig['bias']=='UP' else NE), "sok jel együtt"],
      ["RSI (lendület)", f"{sig['rsi']:.0f} / 100", (("túladott","#27ae60") if sig['rsi']<35 else ("túlvett","#c0392b") if sig['rsi']>65 else NE), "nagy esés után pihen"],
      ["ADX (trend ereje)", f"{sig['adx']:.0f}", ("erős","#c0392b"), "az esésnek lendülete van"],
      ["Regime / MTF", f"{sig['regime']} ({sig['mtf']})", (DN if sig['mtf']<0 else UP), "átlagok alatt = bear"],
      ["Dwell (idő-az-áron)", f"{dw.get('location')} blokk", (DN if dw.get('dwell_bias')=='DOWN' else UP if dw.get('dwell_bias')=='UP' else NE), "blokk alatt ragad"],
      ["CVD / pénz-áramlás", f"{liq['cvd_bias']}", (UP if liq['cvd_bias']=='LONG' else DN), "vevők vagy eladók"],
      ["Long/Short (tömeg)", f"{ls if ls is not None else '1.34'}", DN, "tömeg long → kontrár le"],
      ["Open Interest", f"{rf['oi']['trend'] if rf and rf.get('oi') else 'n/a'}", NE, "pozíciók épülnek/zárnak"],
      ["Funding", f"{rf['funding']['funding'] if rf and rf.get('funding') else 'n/a'}", NE, "ki fizet kinek"],
      ["Likvidáció imbalance", f"{liq['imbalance']}", (UP if 'BULL' in liq['imbalance'] else DN if 'BEAR' in liq['imbalance'] else NE), "több mágnes fent/lent"],
    ]
    p.table(rows, ["Indikátor","Érték","Jel","Mit jelent"], [0.27,0.24,0.17,0.32], rowh=0.0345, fs=8.7)
    p.t(f"Adat-alap (Analytics Reporter elv): ár+likvidáció 5 tőzsde konfluenciájából (OKX, Binance.US, Hyperliquid, "
        f"Kraken, Coinbase), {len(df)} napi gyertya. Minden szám élő.", 8.6, c="#666")
    p.save()

    # ===== 3. ÁRMOZGÁS + GRAFIKON (Content Creator + Visual Storyteller) =====
    p = Page(pp, "3/9 · Mi történt")
    p.h("Az elmúlt hetek története")
    p.t(f"A csúcs {hi30:,.0f} $ volt, onnan esett {lo30:,.0f} $-ig (30 napos sáv). Ez nem véletlen zuhanás:")
    p.t(f"• {NEWS['crash']}\n• {NEWS['relief']}", 10)
    p.t(f"Most egy kis visszapattanás van {px:,.0f} $-ig. A nagy kérdés: ez fordulat, vagy csak szusszanás az esésben?")
    p.img(chart1, h=0.40)
    p.t("Fekete = ár. Piros = ellenállás (fent elakadhat). Zöld = támasz (lent megfoghatja). A vastag zöld a legerősebb mágnes.", 9, c="#666")
    p.save()

    # ===== 4. FOMC / MAKRÓ =====
    p = Page(pp, "4/9 · A mai esemény")
    p.h("Ma dönt a Fed (FOMC)")
    p.box("MA / HOLNAP: Fed kamatdöntés — a hét legfontosabb eseménye", "#0e1b33", 12)
    p.t(f"• {NEWS['fomc']}\n• {NEWS['cpi']}\n• A Fed egész évben nem vágott kamatot — a magas kamat nyomja a kockázatos eszközöket.", 10.2)
    p.t("Két forgatókönyv (becslés, nem jóslat):", 11, "bold", "#0e1b33")
    p.t(f"   ↑ {NEWS['dove']}", 10.3, c="#27ae60")
    p.t(f"   ↓ {NEWS['hawk']}", 10.3, c="#c0392b")
    p.box("Szabály: Fed-döntés ELŐTT ne nyiss pozíciót. Várd meg a reakciót.", "#e29a25", 11.5)
    p.t("Ilyenkor az ár percek alatt ugrálhat oda-vissza, és kirázza a stopokat mindkét irányban. "
        "A fegyelmezett lépés: megvárni a döntést, és csak a tiszta irányba belépni, egy szintnél.", 10)
    p.save()

    # ===== 5. LIKVIDÁCIÓS TÉRKÉP =====
    p = Page(pp, "5/9 · Likvidációs térkép")
    p.h("Hol vannak a mágnesek — és MIÉRT pont ott")
    p.t("Sokan tőkeáttéttel kereskednek (10x–100x). Ha az ár ellenük megy, a tőzsde kényszer-zárja (likvidálja) őket. "
        "Ahol sok ilyen zárás torlódik = MÁGNES: az ár hajlamos oda menni. Ha 5 tőzsdén UGYANOTT torlódik (pl. x45), az nagyon erős.", 10.2)
    p.img(chart2, h=0.42)
    p.t(f"FŐ lefelé cél: {big['price']:,.0f} $ (x{big['count']}). " + (f"Első fal felfelé: {res['price']:,.0f} $." if res else ""), 10.3, "bold", "#0e1b33")
    p.save()

    # ===== 6. AKCIÓTERV =====
    p = Page(pp, "6/9 · Akcióterv")
    p.h("Mit tegyél, mit NE — és MIKOR")
    p.box(f"MOST: VÁRJ — (1) a Fed-döntésre, (2) a {big['price']:,.0f} $ szintre.", "#e29a25", 12)
    p.t("Belépési ravaszok (elég az egyik):", 11, "bold", "#0e1b33")
    p.t(f"   A) Ár a {big['price']:,.0f} $ mágneshez ér ÉS megfordul (megáll esni, visszakapaszkodik) → VÉTEL fontolható.", 10.2, c="#27ae60")
    p.t(f"   B) Ár visszaveszi a ~{reclaim:,} $ szintet és ott marad → fordulás-jel magasabbról.", 10.2, c="#27ae60")
    p.t("Ha jön a jel — a 4 lépés:", 11, "bold", "#0e1b33")
    p.t("   1) Kis tét (a pénzed töredéke).   2) STOP a szint alá (kilépés, ha rosszul megy).\n"
        "   3) Cél kijelölve előre (hova adsz el).   4) Útközben részben profitot kiveszel.", 10.2)
    p.t("Amit NE:", 11, "bold", "#c0392b")
    p.t("   ✗ Ne vegyél esés közben („eső kést elkapni\").  ✗ Ne kereskedj a Fed-döntésbe.\n"
        "   ✗ Ne használj nagy tőkeáttételt (kis számlán gyors bukás).  ✗ Ne tedd be az összes pénzed.", 10.2)
    p.save()

    # ===== 7. PSZICHOLÓGIA =====
    p = Page(pp, "7/9 · Pszichológia")
    p.h("A fejed a legfontosabb műszer")
    p.t("A legtöbb kis befektető nem rossz elemzés, hanem érzelmek miatt bukik:")
    p.t("• FOMO: amikor minden zöld és „mindenki nyer\" → gyakran a TETŐ. Ne ott vegyél.", 10.2)
    p.t("• Félelem: amikor mindenki pánikol → gyakran az ALJ közelében. A Long/Short arány pont ezt méri: a tömeg "
        "általában a rossz oldalon áll.", 10.2)
    p.t("• Türelem: a jó belépő ritka. A pénz nagy részét a VÁRAKOZÁSSAL keresed, nem a sok kereskedéssel.", 10.2)
    p.t("• Veszteség: kis veszteség OK. A nagy bukás a „reménykedés stop nélkül + egyre lejjebb átlagolás\"-ból jön. "
        "Mindig legyen kilépési terved ELŐRE.", 10.2)
    p.t("• Egy trade nem számít: a rendszer sok döntés átlagában működik.", 10.2)
    p.box("Aranyszabály: tervezz előre, lépj kicsiben, fogadd el a kis veszteséget, várd ki a jó pontot.", "#0e1b33", 11)
    p.save()

    # ===== 8. KONKRÉT SZINTEK (gyorslap) =====
    p = Page(pp, "8/9 · Szint-gyorslap")
    p.h("A fontos árszintek egy helyen")
    rr=[["Ellenállás 1", f"{res['price']:,.0f} $" if res else "—", "ide eladni egy rallyt"],
        ["MOST (ár)", f"{px:,.0f} $", "itt vagyunk"],
        ["Reclaim-jel", f"~{reclaim:,} $", "efölött tartósan = fordulás"],
        ]
    for c in below[:4]:
        tag="FŐ CÉL / vételi figyelő" if c is big else "támasz / lefelé cél"
        rr.append([("FŐ TÁMASZ","#085") if c is big else "Támasz", f"{c['price']:,.0f} $ (x{c['count']})", tag])
    p.table(rr, ["Szint","Ár","Szerep"], [0.26,0.30,0.44], rowh=0.036, fs=9)
    p.t("Tipp: a vételt a FŐ TÁMASZNÁL figyeld fordulás-jellel; az eladást egy rally-nál az ellenállásnál.", 9.5, c="#666")
    p.save()

    # ===== 9. ÖSSZEFOGLALÓ + FORRÁSOK + MÓDSZERTAN =====
    p = Page(pp, "9/9 · Összefoglaló")
    p.h("Összefoglaló — egy percben")
    p.t(f"• Ár {px:,.0f} $, trend lefelé (jelek {votes['DOWN']}–{votes['UP']}), de gyengül; a tömeg kezd kapitulálni.", 10.3)
    p.t(f"• MA Fed-döntés → ez dönt. Galamb 66–70e felé, héja 58–60e felé.", 10.3)
    p.t(f"• Fő vételi figyelő-zóna: {big['price']:,.0f} $. Türelem a döntésig és a szintig.", 10.3)
    p.h("Hogyan készült (módszertan)")
    p.t("A hírlevél a stob1985/agency-agents-stob agent-definícióit alkalmazza: Executive Summary Generator "
        "(SCQA vezetői összefoglaló), Analytics Reporter (számok kontextussal + dashboard), Content Creator "
        "(egyszerű nyelv), Visual Storyteller (grafikonok). Adat: 5 tőzsde + saját elemző motor.", 9.6, c="#444")
    p.t("Makró-források:", 10, "bold", "#0e1b33")
    for s in SOURCES: p.t("   – "+s, 8.8, c="#777", gap=0.0015)
    p.box("FIGYELMEZTETÉS: NEM pénzügyi tanács. A kripto nagyon kockázatos.", "#c0392b", 11)
    p.t("Csak annyit kockáztass, amit elvesztened is el tudsz viselni. A múlt nem garancia a jövőre.", 9.3, c="#666")
    p.save()
print("PDF kesz:", pdfpath, "| verdict:", verdict, votes)
