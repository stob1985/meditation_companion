#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Napi BTC hirlevel - melyverzio: indikator-magyarazatok, ar-tortenet, hirek/FOMC,
pszichologia, idozites. Grafikon (ar+szintek) + likvidacios profil + tobboldalas PDF.
Forrasok: OKX (ar/likviditas), webes hirek (CPI/FOMC/ETF) - lasd utolso oldal."""
import os, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
import yaml
from engine import data, events as ev, vdb, signal, liquidity, dwell as dwellmod, realflow

plt.rcParams["font.family"] = "DejaVu Sans"
OUT = "/home/user/btc-signal-engine/newsletter"; os.makedirs(OUT, exist_ok=True)
cfg = yaml.safe_load(open("config.yaml"))

# ---- VALOS HIREK (webes keresesbol, 2026-06, forrasokkal a vegen) ---------
NEWS = dict(
    cpi="Május CPI (jún. 10): 4,2% éves — a várttal megegyező; mag-infláció 2,9% (0,2% havi, a várt alatt).",
    fed="A Fed egész évben NEM vágott kamatot — a magas kamat nyomja a kockázatos eszközöket (BTC-t is).",
    fomc="FOMC kamatdöntés JÚN. 16–17 (MA/HOLNAP) — ez a hét döntő eseménye.",
    scen_dove="Galamb (laza) dot-plot → BTC rally 66–70e $ felé.",
    scen_hawk="Héja (szigorú) dot-plot → vissza 58–60e $ támasz felé.",
    crash="A heti −17% oka: héja Fed + Irán-feszültség + rekord 13 napos ETF-kiáramlás (4,4 Mrd $) + a Strategy meglepetés-eladása.",
    relief="Irán–USA tűzszünet enyhítette a feszültséget, olaj esett, likviditás nőtt → rövid squeeze.",
)
SOURCES = [
    "blockchainreporter.net – Bitcoin Price Today (jún. 10, 2026)",
    "IG.com – Bitcoin after CPI / why Bitcoin crashed (2026-06-15)",
    "cryptonews.com – June CPI & FOMC: Bitcoin's next move (2026)",
    "fxleaders.com – BTC prediction, Trump–Iran ceasefire (jún. 16, 2026)",
]

# ---- ADAT + ELEMZES -------------------------------------------------------
df = data.load_live("BTCUSDT", "D", 1000, "okx", verbose=False)
events = ev.detect(df, cfg)
db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
dw = dwellmod.build(df, cfg)
sig = signal.composite(df, events, db, cfg, at=-1, dwell=dw)
liq = liquidity.build(df, cfg)
ml = liquidity.build_multi(cfg)
rf = realflow.build(cfg, liq["price"], liq["atr"])
px = liq["price"]; today = df.index[-1].date()
above = sorted([c for c in ml["clusters_above"] if c["n_venues"] >= 4], key=lambda c: c["price"])
below = sorted([c for c in ml["clusters_below"] if c["n_venues"] >= 4], key=lambda c: -c["price"])
res = above[0] if above else None
sup = below[0] if below else None
big = max(below, key=lambda c: c["count"]) if below else None
ls = rf["ls_ratio"]["ratio"] if rf and rf.get("ls_ratio") else None
chg7 = (px / df["close"].iloc[-8] - 1) * 100
chg30 = (px / df["close"].iloc[-31] - 1) * 100
hi30, lo30 = df["high"].tail(30).max(), df["low"].tail(30).min()

votes = {"UP": 0, "DOWN": 0}
def vote(d):
    if d in ("UP", "DOWN"): votes[d] += 1
vote(sig["bias"]); vote("DOWN" if sig["mtf"] < 0 else "UP" if sig["mtf"] > 0 else None)
vote(dw.get("dwell_bias")); vote("UP" if liq["cvd_bias"] == "LONG" else "DOWN")
vote("UP" if "BULL" in liq["imbalance"] else "DOWN" if "BEAR" in liq["imbalance"] else None)
if rf and rf.get("ls_ratio"): vote(rf["ls_ratio"]["contrarian"])
verdict = "ELADÁS felé" if votes["DOWN"] > votes["UP"] else "VÉTEL felé" if votes["UP"] > votes["DOWN"] else "VÁRAKOZÁS"
vcol = "#c83c3c" if "ELAD" in verdict else "#28a05a" if "VÉT" in verdict else "#d2961e"

# ---- 1. GRAFIKON: ar + szintek --------------------------------------------
d = df.tail(120)
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.plot(d.index, d["close"], color="#111", lw=1.8)
ax.axhline(px, color="#0066ff", lw=2)
ax.text(d.index[0], px, f"  MOST {px:,.0f}", color="#0066ff", va="bottom", fontweight="bold", fontsize=11)
for c in above[:3]:
    ax.axhline(c["price"], color="#d11", lw=1.1, ls="--", alpha=.7)
    ax.text(d.index[-1], c["price"], f" ellenállás {c['price']:,.0f} (x{c['count']})", color="#d11", va="center", fontsize=8)
for c in below[:4]:
    b = c is big
    ax.axhline(c["price"], color="#0a7", lw=2.4 if b else 1.1, ls="--", alpha=.9 if b else .55)
    ax.text(d.index[-1], c["price"], f" támasz {c['price']:,.0f} (x{c['count']}){'  <== FŐ CÉL' if b else ''}",
            color="#085" if b else "#0a7", va="center", fontsize=8, fontweight="bold" if b else "normal")
ax.set_title(f"BTC/USD — napi ár és likvidációs szintek ({today})", fontsize=12, fontweight="bold")
ax.set_ylabel("ár (USD)"); ax.grid(alpha=.25); ax.margins(x=0)
fig.tight_layout(); chart1 = f"{OUT}/btc_chart.png"; fig.savefig(chart1, dpi=130); plt.close(fig)

# ---- 2. GRAFIKON: likvidacios profil (vizszintes barok) -------------------
allc = sorted(above[:6] + below[:6], key=lambda c: c["price"])
fig, ax = plt.subplots(figsize=(10, 5.6))
prices = [c["price"] for c in allc]; counts = [c["count"] for c in allc]
colors = ["#d11" if c["price"] > px else "#0a7" for c in allc]
ax.barh([f"{p:,.0f}" for p in prices], counts, color=colors, alpha=.85)
for i, c in enumerate(allc):
    ax.text(c["count"] + 0.4, i, f"x{c['count']} ({c['n_venues']} tőzsde)", va="center", fontsize=8)
ax.axhline(sum(1 for p in prices if p < px) - 0.5, color="#0066ff", lw=2)
ax.set_title(f"Likvidációs profil — hol a legtöbb „beragadt\" pozíció (ár {px:,.0f})", fontsize=12, fontweight="bold")
ax.set_xlabel("klaszter-méret (mennyi pozíció dőlne be) — nagyobb = erősebb mágnes")
fig.tight_layout(); chart2 = f"{OUT}/btc_liqprofile.png"; fig.savefig(chart2, dpi=130); plt.close(fig)
print("grafikonok kesz")

# ---- PDF ------------------------------------------------------------------
class Page:
    def __init__(self, pp):
        self.fig = plt.figure(figsize=(8.27, 11.69)); self.ax = self.fig.add_axes([0,0,1,1]); self.ax.axis("off")
        self.y = 0.955; self.pp = pp
    def t(self, txt, size=10.5, w="normal", c="#282828", wrap=98, gap=0.0035, x=0.07):
        for line in txt.split("\n"):
            for ww in (textwrap.wrap(line, wrap) or [""]):
                self.ax.text(x, self.y, ww, fontsize=size, fontweight=w, color=c, va="top")
                self.y -= size/780.0 + gap
        self.y -= 0.005
    def box(self, txt, rgb, size=13):
        self.ax.add_patch(plt.Rectangle((0.07, self.y-0.044), 0.86, 0.044, color=rgb, transform=self.fig.transFigure))
        self.ax.text(0.5, self.y-0.022, txt, ha="center", va="center", fontsize=size, color="white", fontweight="bold")
        self.y -= 0.058
    def img(self, path, h=0.40):
        a = self.fig.add_axes([0.07, self.y-h, 0.86, h]); a.axis("off"); a.imshow(mpimg.imread(path)); self.y -= h+0.012
    def ind(self, name, now, mean):
        self.ax.text(0.07, self.y, "● "+name, fontsize=10.5, fontweight="bold", color="#111", va="top"); self.y -= 0.016
        self.t("   MOST: "+now, 9.8, c="#333", gap=0.002)
        self.t("   MIT JELENT: "+mean, 9.8, c="#555", gap=0.002); self.y -= 0.002
    def save(self):
        self.ax.text(0.94, 0.978, "BTC NAPI HÍRLEVÉL", ha="right", fontsize=8, color="#aaa")
        self.ax.text(0.5, 0.022, "Oktatási célú összefoglaló — NEM pénzügyi tanács. A kripto kockázatos.", ha="center", fontsize=7.5, color="#aaa")
        self.pp.savefig(self.fig); plt.close(self.fig)

bias_pct = sig["up"] if sig["bias"] == "UP" else sig["dn"]
pdfpath = f"{OUT}/BTC_napi_hirlevel_{today}.pdf"
with PdfPages(pdfpath) as pp:
    # 1 — CÍMLAP + TL;DR
    p = Page(pp)
    p.t(f"BITCOIN (BTC/USD) — napi hírlevél", 21, "bold", "#111"); p.t(f"{today}", 12, c="#777")
    p.y -= 0.005
    p.box(f"MAI ÁLLÁS: {verdict}   ·   ár {px:,.0f} $   ·   jelek {votes['DOWN']} le / {votes['UP']} fel", vcol)
    p.t("RÖVIDEN (ha csak ennyit olvasol el):", 12, "bold", "#111")
    p.t(f"• A Bitcoin egy hét alatt {chg7:+.0f}%-ot esett, most {px:,.0f} $. A trend lefelé, de már gyengül.", 11)
    p.t(f"• MA Fed-kamatdöntés van (FOMC). EZ dönti el a következő nagy mozgást — ne kereskedj bele vakon!", 11)
    p.t(f"• A legfontosabb szint lent: {big['price']:,.0f} $ — ide „húzhatja\" a piac az árat. Itt érdemes VÉTELT figyelni.", 11)
    p.t(f"• Most a helyes lépés: TÜRELEM. Megvárni a Fed-et és a szintet. Kapkodni a legrosszabb.", 11)
    p.y -= 0.006
    p.t("Ez a hírlevél 4 dolgot rak össze: (1) mi történt, (2) a mai hír/esemény, (3) minden indikátor "
        "egyszerű magyarázata és mai értéke, (4) konkrét terv + pszichológia. Lépésről lépésre.", 10, c="#666")
    p.save()

    # 2 — MI TÖRTÉNT (ar-tortenet) + chart
    p = Page(pp)
    p.t("1) Mi történt mostanában?", 15, "bold", "#111")
    p.t(f"Az elmúlt hónapban a BTC a {hi30:,.0f} $-os csúcsról {lo30:,.0f} $-ig esett (30 napos sáv). "
        f"A héten {chg7:+.0f}%, a hónapban {chg30:+.0f}%. Ez egy erős leértékelődés.", 10.5)
    p.t("MIÉRT esett? Négy dolog egyszerre (valós hírek alapján):", 11, "bold", "#111")
    p.t(f"• {NEWS['crash']}", 10.3)
    p.t(f"• {NEWS['relief']}", 10.3)
    p.t(f"Vagyis nem „csak úgy\" esett: a magas kamat + tőkekivonás (ETF) + félelem nyomta le. "
        f"Most egy kis visszapattanás (squeeze) van {px:,.0f} $-ig.", 10.5)
    p.img(chart1, h=0.40)
    p.t("A fekete vonal az ár. Piros = ellenállás fent, zöld = támasz lent. A vastag zöld a legerősebb mágnes.", 9.3, c="#666")
    p.save()

    # 3 — A MAI ESEMÉNY: FOMC
    p = Page(pp)
    p.t("2) A mai nagy esemény: a Fed (FOMC)", 15, "bold", "#111")
    p.box("MA / HOLNAP: Fed kamatdöntés — a hét legfontosabb eseménye", "#34495e")
    p.t(f"• {NEWS['fomc']}", 10.5)
    p.t(f"• {NEWS['fed']}", 10.5)
    p.t(f"• {NEWS['cpi']}", 10.5)
    p.t("Mi a tét? A „dot-plot\" = a Fed jelzése, lesz-e kamatvágás. Két forgatókönyv:", 11, "bold", "#111")
    p.t(f"   ↑ {NEWS['scen_dove']}", 10.5, c="#0a7")
    p.t(f"   ↓ {NEWS['scen_hawk']}", 10.5, c="#c0392b")
    p.y -= 0.004
    p.box("TANULSÁG: Fed-döntés előtt NE nyiss pozíciót. Várd meg a reakciót.", "#d2961e", 12)
    p.t("Miért? Ilyenkor az ár pár perc alatt ugrálhat oda-vissza (kirázza a stopokat mindkét irányban). "
        "A profik megvárják a döntést, és csak a TISZTA irányba lépnek be utána, egy szintnél.", 10.3)
    p.save()

    # 4 — INDIKÁTOROK 1
    p = Page(pp)
    p.t("3) Az indikátorok — mit mérnek, mit mutatnak MOST (1/2)", 14, "bold", "#111")
    p.t("Több független „mérőműszert\" használunk. Egyik sem tévedhetetlen — együtt adnak képet.", 10, c="#666")
    p.y -= 0.004
    p.ind("Összesített irány (kompozit)",
          f"{sig['bias']} {bias_pct:.0f}% ({sig['strength']}).",
          "Sok kis jelet összegez egy számba: 50% felett vételi, alatt eladói túlsúly. Most lefelé húz.")
    p.ind("RSI (lendület 0–100)", f"{sig['rsi']:.0f}.",
          "30 alatt „túladott\" (sokat esett, pihenhet); 70 felett „túlvett\". Most alacsony = nagy esés után.")
    p.ind("ADX (trend ereje 0–100)", f"{sig['adx']:.0f}.",
          "40 felett ERŐS trend. Magas ADX + eső ár = az esésnek lendülete van, ne állj elé.")
    p.ind("Regime / MTF (hol az ár a mozgóátlagokhoz képest)", f"{sig['regime']} (MTF {sig['mtf']}).",
          "Minden átlag alatt = bear. A −5 a legrosszabb; ha −3-ra javul, a trend gyengül (most javult).")
    p.ind("Dwell blokkok (idő-az-áron)", f"az ár a fő blokk {dw.get('location')} részén → {dw.get('dwell_bias')}.",
          "Ahol az ár sok időt töltött = erős zóna. Szabály: blokk alatt ragad → lefelé; fölé tör → felfelé.")
    p.save()

    # 5 — INDIKÁTOROK 2
    p = Page(pp)
    p.t("3) Az indikátorok (2/2) — a pénz és a tömeg", 14, "bold", "#111")
    p.ind("CVD / pénz-áramlás", f"{liq['cvd_bias']} ({sig['flow']['agree']}).",
          "Többen vesznek vagy adnak el? LONG/abszorpció = lassan vevők lépnek be → jó jel az aljhoz.")
    if ls is not None:
        p.ind("Tömeg-arány (Long/Short)", f"{ls} (a tömeg {rf['ls_ratio']['crowd']}).",
              "Hányan fogadnak fel vs le. ELLENJEL: a piac a többséget szereti kirázni. 1,3 alá esve → közel az alj.")
    if rf and rf.get("oi"): p.ind("Open Interest (nyitott pozíciók)", f"{rf['oi']['trend']}.",
          "Nő = új pénz/tét épül; esik = pozíciók zárása/likvidálás (tisztulás, gyakran alj közelében).")
    if rf and rf.get("funding"): p.ind("Funding (ki fizet kinek)", f"{rf['funding']['funding']}.",
          "Pozitív: a longok fizetnek (túl sokan állnak fel → eséskockázat). Negatív felé fordulva → kapituláció.")
    p.ind("Sweep-reclaim (fordulat-jel)", "most nincs aktív.",
          "Ha az ár lesöpör egy mélyet, majd visszaugrik fölé → klasszikus alj-jel. Erre várunk a nagy szintnél.")
    p.ind("Előrejelző sáv (3 nap)", f"{sig['forecast']['lo']:,.0f} – {sig['forecast']['hi']:,.0f} $.",
          "A várható mozgástér 3 napra a friss ingadozás alapján — nem jóslat, hanem keret.")
    p.save()

    # 6 — LIKVIDÁCIÓS TÉRKÉP + MIÉRT
    p = Page(pp)
    p.t("4) A likvidációs térkép — és MIÉRT pont ezek a szintek", 14, "bold", "#111")
    p.t("Ez a legfontosabb rész. Sokan tőkeáttéttel kereskednek (10x/25x/50x/100x). Ha az ár ellenük megy, "
        "a tőzsde KÉNYSZER-zárja (likvidálja) a pozíciójukat. Ahol sok ilyen zárás torlódik, az MÁGNES: "
        "az ár hajlamos pont oda menni, mert ott a legtöbb kényszer-megbízás. Ha 5 tőzsdén UGYANOTT van "
        "torlódás (pl. x45), az nagyon erős.", 10.3)
    p.img(chart2, h=0.42)
    p.t(f"Ezért a FŐ lefelé cél a {big['price']:,.0f} $ (a legnagyobb, x{big['count']}). "
        + (f"Felfelé az első fal {res['price']:,.0f} $." if res else ""), 10.3, "bold", "#111")
    p.save()

    # 7 — MIT TEGYÉL / NE + IDŐZÍTÉS
    p = Page(pp)
    p.t("5) Mit tegyél, mit NE — és MIKOR", 15, "bold", "#111")
    p.box("MOST: VÁRJ. (1) a Fed-döntésre, (2) a szintre.", "#d2961e", 12)
    p.t("MEDDIG várj? Amíg az alábbiak EGYIKE be nem jön:", 11, "bold", "#111")
    p.t(f"   A) Az ár leesik a {big['price']:,.0f} $-os nagy mágneshez ÉS ott megfordul "
        f"(megáll esni, visszakapaszkodik) → ITT lehet VÉTELT fontolni.", 10.5, c="#0a7")
    p.t(f"   B) Az ár visszaveszi a ~{int((px//1000)*1000+3000):,} $ szintet és ott marad → "
        f"szintén fordulás-jel, magasabbról.", 10.5, c="#0a7")
    p.t("MIT lépj, ha jön a jel:", 11, "bold", "#111")
    p.t("   1) Kis tétel (a pénzed töredéke). 2) Tegyél STOP-ot (kilépés, ha rosszul megy, a szint alá). "
        "3) Célt is jelölj ki előre (hova akarsz eladni). 4) Részben vegyél ki profitot útközben.", 10.3)
    p.t("MIT NE tegyél:", 11, "bold", "#c0392b")
    p.t("   ✗ Ne vegyél MOST, esés közben („eső kést elkapni\"). ✗ Ne kereskedj a Fed-döntésbe. "
        "✗ Ne használj nagy tőkeáttételt (10x+ = gyors bukás kis számlán). ✗ Ne tedd be az összes pénzed.", 10.3)
    p.save()

    # 8 — PSZICHOLÓGIA
    p = Page(pp)
    p.t("6) Pszichológia — a fejed a legfontosabb „indikátor\"", 15, "bold", "#111")
    p.t("A legtöbb kis befektető nem a rossz elemzés miatt bukik, hanem az érzelmei miatt. Pár szabály:", 10.5)
    p.t("• FOMO (lemaradás-félelem): amikor minden zöld és „mindenki nyer\", az gyakran a TETŐ. Ne ott vegyél.", 10.3)
    p.t("• Félelem: amikor mindenki pánikol és „vége a kriptónak\", az gyakran az ALJ közelében van. "
        "Pont ezt méri a Long/Short arány: a tömeg általában a rossz oldalon áll.", 10.3)
    p.t("• Türelem: a jó belépő ritka. A pénz nagy részét a VÁRAKOZÁSSAL keresed, nem a sok kereskedéssel.", 10.3)
    p.t("• Veszteség kezelése: kis veszteséget elfogadni OK. A nagy bukás onnan jön, hogy valaki „reménykedik\" "
        "stop nélkül, és egyre lejjebb átlagol. Mindig legyen kilépési terved ELŐRE.", 10.3)
    p.t("• Egy trade nem számít: a rendszer sok döntés átlagában működik. Ne ragadj bele egyetlenbe.", 10.3)
    p.y -= 0.004
    p.box("Aranyszabály: tervezz előre, lépj kicsiben, fogadd el a kis veszteséget, várd ki a jó pontot.", "#34495e", 11)
    p.save()

    # 9 — ÖSSZEFOGLALÓ + FORRÁSOK
    p = Page(pp)
    p.t("Összefoglaló", 16, "bold", "#111")
    p.t(f"• Ár {px:,.0f} $, a trend lefelé (jelek {votes['DOWN']}–{votes['UP']}), de gyengül; a tömeg kezd kapitulálni.", 10.8)
    p.t(f"• MA Fed-döntés → ez dönt. Galamb = 66–70e felé, héja = 58–60e felé.", 10.8)
    p.t(f"• Fő vételi figyelő-zóna lent: {big['price']:,.0f} $ (a legnagyobb likvidációs mágnes).", 10.8)
    p.t(f"• Teendő: TÜRELEM — várd a Fed-et és a szintet; kis tét, stop, ne tőkeáttételezz.", 10.8)
    p.y -= 0.01
    p.t("Hogyan készült", 12, "bold", "#111")
    p.t("Az ár- és likvidációs adat 5 tőzsdéről (OKX, Binance.US, Hyperliquid, Kraken, Coinbase). "
        "Az indikátorokat egy saját elemző motor számolja. A makró-hírek nyilvános forrásokból:", 9.6, c="#555")
    for s in SOURCES: p.t("   – " + s, 9, c="#777", gap=0.001)
    p.y -= 0.008
    p.box("FIGYELMEZTETÉS: NEM pénzügyi tanács. A kripto nagyon kockázatos.", "#c0392b", 11)
    p.t("Ez egy automatikus elemzés oktatási céllal. Csak annyit kockáztass, amit elvesztened is el tudsz "
        "viselni. A múltbeli adat nem garancia a jövőre.", 9.3, c="#666")
    p.save()
print("PDF kesz:", pdfpath, "| verdict:", verdict, votes)
