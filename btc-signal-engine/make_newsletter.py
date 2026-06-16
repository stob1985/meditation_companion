#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Napi BTC hirlevel generator - egyszeru nyelv, grafikon + tobboldalas PDF."""
import os, datetime as dt
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import yaml
from engine import data, events as ev, vdb, signal, liquidity, dwell as dwellmod, realflow

OUT = "/home/user/btc-signal-engine/newsletter"
os.makedirs(OUT, exist_ok=True)
cfg = yaml.safe_load(open("config.yaml"))

# ---- adat + elemzes -------------------------------------------------------
df = data.load_live("BTCUSDT", "D", 1000, "okx", verbose=False)
events = ev.detect(df, cfg)
db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
dw = dwellmod.build(df, cfg)
sig = signal.composite(df, events, db, cfg, at=-1, dwell=dw)
liq = liquidity.build(df, cfg)
ml = liquidity.build_multi(cfg)
rf = realflow.build(cfg, liq["price"], liq["atr"])
px = liq["price"]

above = sorted([c for c in ml["clusters_above"] if c["n_venues"] >= 4], key=lambda c: c["price"])
below = sorted([c for c in ml["clusters_below"] if c["n_venues"] >= 4], key=lambda c: -c["price"])
res = above[0] if above else None                       # legkozelebbi ellenallas
sup = below[0] if below else None                       # legkozelebbi tamasz
big_below = max(below, key=lambda c: c["count"]) if below else None   # legnagyobb magnes lent

# szavazas
votes = {"UP": 0, "DOWN": 0}
def vote(d):
    if d in ("UP", "DOWN"): votes[d] += 1
vote(sig["bias"]); vote("DOWN" if sig["mtf"] < 0 else "UP" if sig["mtf"] > 0 else None)
vote(dw.get("dwell_bias")); vote("UP" if liq["cvd_bias"] == "LONG" else "DOWN")
vote("UP" if "BULL" in liq["imbalance"] else "DOWN" if "BEAR" in liq["imbalance"] else None)
if rf and rf.get("ls_ratio"): vote(rf["ls_ratio"]["contrarian"])
verdict = "ELADAS fele" if votes["DOWN"] > votes["UP"] else "VETEL fele" if votes["UP"] > votes["DOWN"] else "VARAKOZAS"

# ---- grafikon -------------------------------------------------------------
d = df.tail(120)
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(d.index, d["close"], color="#111", lw=1.8, label="BTC ar")
ax.axhline(px, color="#0066ff", lw=2, ls="-")
ax.text(d.index[0], px, f"  MOST: {px:,.0f}", color="#0066ff", va="bottom", fontweight="bold", fontsize=11)
for c in above[:3]:
    ax.axhline(c["price"], color="#d11", lw=1.1, ls="--", alpha=.7)
    ax.text(d.index[-1], c["price"], f" ELLENALLAS {c['price']:,.0f} (x{c['count']})", color="#d11", va="center", fontsize=8)
for c in below[:4]:
    big = c is big_below
    ax.axhline(c["price"], color="#1a8", lw=2.2 if big else 1.1, ls="--", alpha=.85 if big else .6)
    tag = "  <== FO CEL" if big else ""
    ax.text(d.index[-1], c["price"], f" TAMASZ {c['price']:,.0f} (x{c['count']}){tag}", color="#0a6" if big else "#1a8",
            va="center", fontsize=8, fontweight="bold" if big else "normal")
ax.set_title(f"BTC / USD - napi grafikon es likvidacios szintek  ({df.index[-1].date()})", fontsize=12, fontweight="bold")
ax.set_ylabel("ar (USD)"); ax.grid(alpha=.25); ax.margins(x=0)
fig.tight_layout()
chart = f"{OUT}/btc_chart.png"
fig.savefig(chart, dpi=130); plt.close(fig)
print("chart kesz")

# ---- PDF (matplotlib PdfPages - nincs cryptography fuggoseg) --------------
import textwrap
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
plt.rcParams["font.family"] = "DejaVu Sans"

today = df.index[-1].date()
ls = rf["ls_ratio"]["ratio"] if rf and rf.get("ls_ratio") else None
verdict_col = "#c83c3c" if "ELADAS" in verdict else "#28a05a" if "VETEL" in verdict else "#d2961e"

class Page:
    def __init__(self, pdf):
        self.fig = plt.figure(figsize=(8.27, 11.69))   # A4
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.axis("off")
        self.y = 0.95; self.pdf = pdf
    def head(self):
        self.ax.text(0.94, 0.975, "BTC NAPI HÍRLEVÉL — kis befektetőknek", ha="right",
                     fontsize=8, color="#999")
    def foot(self):
        self.ax.text(0.5, 0.025, "Oktatási célú összefoglaló — NEM pénzügyi tanács. A kripto kockázatos.",
                     ha="center", fontsize=7.5, color="#999")
    def text(self, t, size=11, weight="normal", color="#282828", wrap=95, gap=0.004, indent=0.07):
        for line in t.split("\n"):
            wrapped = textwrap.wrap(line, wrap) or [""]
            for w in wrapped:
                self.ax.text(indent, self.y, w, fontsize=size, fontweight=weight, color=color, va="top")
                self.y -= size / 750.0 + gap
        self.y -= 0.006
    def box(self, t, rgb, size=14):
        self.y -= 0.004
        self.ax.add_patch(plt.Rectangle((0.07, self.y - 0.045), 0.86, 0.045, color=rgb, transform=self.fig.transFigure))
        self.ax.text(0.5, self.y - 0.0225, t, ha="center", va="center", fontsize=size, color="white", fontweight="bold")
        self.y -= 0.062
    def image(self, path, h=0.40):
        img = mpimg.imread(path)
        ax2 = self.fig.add_axes([0.07, self.y - h, 0.86, h]); ax2.axis("off"); ax2.imshow(img)
        self.y -= h + 0.01
    def save(self):
        self.head(); self.foot(); self.pdf.savefig(self.fig); plt.close(self.fig)

pdfpath = f"{OUT}/BTC_napi_hirlevel_{today}.pdf"
with PdfPages(pdfpath) as pp:
    # OLDAL 1
    p = Page(pp)
    p.text(f"BITCOIN (BTC) — {today}", 22, "bold", "#111"); p.y -= 0.01
    p.text(f"Mai ár: {px:,.0f} dollár.    Hangulat ma: a piac inkább LEFELÉ húz, de már gyengül.", 12)
    p.box(f"MAI ÁLLÁS: {verdict}   (jelek: lefelé {votes['DOWN']} – felfelé {votes['UP']})", verdict_col)
    p.text("Mit jelent ez röviden, hétköznapi nyelven:", 12, "bold")
    p.text(f"• A Bitcoin ára most esik egy ideje, több jelzőnk még lefelé mutat.\n"
           f"• DE: egyre több jel azt súgja, hogy az alja közeledik (lásd 3. oldal).\n"
           f"• A legfontosabb szint lent: {big_below['price']:,.0f} $. Ide „húzhatja\" a piac az árat.\n"
           + (f"• Felfelé az első komoly akadály: {res['price']:,.0f} $." if res else ""), 11)
    p.y -= 0.01
    p.text("FONTOS: ez NEM tanács arra, hogy vegyél vagy adj el. Ez egy térkép. "
           "Te döntesz — kis pénzzel, csak amennyit el is bírsz veszteni.", 10, color="#666")
    p.save()
    # OLDAL 2 — grafikon
    p = Page(pp)
    p.text("1) A térkép — hol az ár és a fontos szintek", 15, "bold", "#111")
    p.text("A zöld vonalak lent = ahol sokan „longolnak\" (felfelé fogadnak); ha az ár odaér, "
           "őket „kirázzák\". Ezek MÁGNESEK: az ár hajlamos lefelé odamenni. A vastag zöld a legerősebb.\n"
           "A piros vonalak fent = ellenállás, ahol az emelkedés elakadhat.", 10.5)
    p.image(chart, h=0.42)
    p.text(f"Most itt vagyunk: {px:,.0f} $. Alattunk a nagy mágnes: {big_below['price']:,.0f} $ "
           f"(itt van a legtöbb ember „stopja\").", 11)
    p.save()
    # OLDAL 3 — szamok
    p = Page(pp)
    p.text("2) A fontos számok — egyszerűen", 15, "bold", "#111")
    p.text(f"• Ár: {px:,.0f} $    •  RSI: {sig['rsi']:.0f}  (50 alatt = inkább eladók vannak túlsúlyban)", 11)
    p.text(f"• Irányjelzőnk (összesített): {sig['bias']} "
           f"{(sig['up'] if sig['bias']=='UP' else sig['dn']):.0f}%  („{sig['strength']}\").", 11)
    if ls is not None:
        p.text(f"• Tömeg-arány (L/S): {ls}.  Még többen fogadnak felfelé, mint lefelé.\n"
               f"  Ez ELLENJEL: a piac szereti a többséget „kirázni\". Ha ez 1,3 alá esik → közel az alj.", 11)
    p.text(f"• Pénz-áramlás (CVD): {liq['cvd_bias']}.  "
           + ("Már lassan vesznek → jó jel az aljhoz." if liq['cvd_bias'] == "LONG" else "Még eladnak."), 11)
    p.y -= 0.01
    p.text("A legfontosabb szintek (dollár):", 13, "bold", "#111")
    p.text(f"   FŐ CÉL LENT:    {big_below['price']:,.0f}   (a legnagyobb mágnes — ide tarthat)", 12, "bold", "#0a6")
    if sup and sup is not big_below: p.text(f"   közeli támasz:  {sup['price']:,.0f}", 11)
    if res: p.text(f"   első ellenállás felfelé: {res['price']:,.0f}", 11, color="#c0392b")
    p.save()
    # OLDAL 4 — strategia
    p = Page(pp)
    p.text("3) A stratégia — mit csinálj (és mit NE)", 15, "bold", "#111")
    p.box("MOST: NE kapkodj. Várj a szintekre.", "#d2961e", 13)
    p.text(f"1) VÉTELRE várj a nagy mágnesnél: {big_below['price']:,.0f} $ körül. "
           "Ott a legnagyobb esély a visszapattanásra. De csak ha látod a fordulást "
           "(az ár megáll esni és visszakapaszkodik) — ne „eső kést\" kapj el!", 11)
    p.text(f"2) Ha az ár visszakapaszkodik kb. {int((px//1000)*1000+3000):,} $ fölé és ott marad → "
           "az is jó jel, hogy fordul.", 11)
    p.text("3) Mindig legyen „stop\" (kilépési szint), ha rosszul megy. Soha ne tedd be az összes pénzed.", 11)
    p.text("4) NE használj nagy tőkeáttételt (leverage). Kis befektetőnek az gyors bukás.", 11)
    p.y -= 0.01
    p.text("Röviden, egy mondatban:", 13, "bold", "#111")
    p.text(f"A Bitcoin lefelé húz a {big_below['price']:,.0f} $-os nagy szint felé. "
           "Ott érdemes figyelni a vételt — türelmesen, fordulás-jellel, kis pénzzel.", 12, "bold", verdict_col)
    p.y -= 0.02
    p.text("Ez a hírlevél egy automatikus elemző rendszer kimenete "
           "(események + likvidációk + pénz-áramlás). Oktatási cél, NEM pénzügyi tanács. "
           "A kripto nagyon kockázatos; csak annyit kockáztass, amit elvesztened is el tudsz viselni.", 9, color="#666")
    p.save()
print("PDF kesz:", pdfpath)
print("verdict:", verdict, votes)

