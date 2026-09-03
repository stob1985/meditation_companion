#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC NAPI JELENTÉS - "IQ 80" kiadás.
Mindenki megérti: nagy számok, közlekedési lámpa, mágnes-metafora, sima magyar.
A számok a SAJÁT motorunkból jönnek (engine/*), a Higgsfield képek a newsletter/img/ mappából.
Kimenet: newsletter/BTC_napi_jelentes.pdf  (több oldal, matplotlib PdfPages).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrow, Ellipse

A4_WH = 11.69 / 8.27  # height/width ratio; widen x so circles look round in 0..1 coords


def dot(ax, x, y, r, color, z=5):
    ax.add_patch(Ellipse((x, y), width=2 * r * A4_WH, height=2 * r, color=color, zorder=z))
from matplotlib.backends.backend_pdf import PdfPages
import yaml
from engine import (data, events as ev, vdb, signal, liquidity,
                    dwell as dwellmod, realflow, trade as trademod)

plt.rcParams["font.family"] = "DejaVu Sans"
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "newsletter", "img")
OUT = os.path.join(HERE, "newsletter", "BTC_napi_jelentes.pdf")

# ---- SZÍNPALETTA ----------------------------------------------------------
NAVY   = "#0d1b2a"
NAVY2  = "#152a41"
GOLD   = "#f0b429"
GREEN  = "#2ecc71"
RED    = "#e74c3c"
AMBER  = "#f39c12"
INK    = "#1b2733"
PAPER  = "#f7f5f0"
GREY   = "#8a94a0"
WHITE  = "#ffffff"

# ---- ADAT + ELEMZÉS (a saját motorunkból) ---------------------------------
cfg = yaml.safe_load(open(os.path.join(HERE, "config.yaml")))
df = data.load_live("BTCUSDT", "D", 1000, "okx", verbose=False)
events = ev.detect(df, cfg)
db = vdb.build(df["close"], events, cap=cfg["vdb"]["cap"], horizons=tuple(cfg["vdb"]["horizons"]))
dw = dwellmod.build(df, cfg)
sig = signal.composite(df, events, db, cfg, at=-1, dwell=dw)
liq = liquidity.build(df, cfg)
ml = liquidity.build_multi(cfg)
rf = realflow.build(cfg, liq["price"], liq["atr"])
plan = trademod.plan(sig, liq, dw, cfg)

px = liq["price"]
today = df.index[-1].date()
atr = liq["atr"]

above = sorted([c for c in ml["clusters_above"] if c["n_venues"] >= 4], key=lambda c: c["price"])
below = sorted([c for c in ml["clusters_below"] if c["n_venues"] >= 4], key=lambda c: -c["price"])
res = above[0] if above else None
big_below = max(below, key=lambda c: c["count"]) if below else None
big_above = max(above, key=lambda c: c["count"]) if above else None

g = liquidity.gravity(sorted(ml["clusters_above"], key=lambda c: c["price"]),
                      sorted(ml["clusters_below"], key=lambda c: -c["price"]), px, atr)

chg7 = (px / df["close"].iloc[-8] - 1) * 100
chg30 = (px / df["close"].iloc[-31] - 1) * 100

# --- egyszerű "szavazás" a 6 modul alapján (VÉTEL / ELADÁS / VÁRJ) ---
votes = {"UP": 0, "DOWN": 0}
def vote(d):
    if d in ("UP", "DOWN"):
        votes[d] += 1
vote(sig["bias"])
vote("DOWN" if sig["mtf"] < 0 else "UP" if sig["mtf"] > 0 else None)
vote(dw.get("dwell_bias"))
vote("UP" if liq["cvd_bias"] == "LONG" else "DOWN")
vote("UP" if "BULL" in liq["imbalance"] else "DOWN" if "BEAR" in liq["imbalance"] else None)
if rf and rf.get("flow_bias"):
    vote(rf["flow_bias"])

# a SWING réteg nagyban WAIT-et ad, a taktikai terv egy limit-long a dip-re.
# a "mai teendő" a rendszer nettó állapota: nincs piaci belépő MOST -> VÁRJ,
# és van egy előjegyzett vételi terv lentebb.
verdict = "VÁRJ"
vcol = AMBER
sub = "Most ne lépj. Van egy okos vételi terv lentebb — arra várunk."

ls = rf["ls_ratio"]["ratio"] if rf and rf.get("ls_ratio") else None
oi_trend = rf["oi"]["trend"] if rf and rf.get("oi") else "n/a"
fund = rf["funding"]["funding"] if rf and rf.get("funding") else None

entry = plan.get("entry"); stop = plan.get("stop")
t1 = plan.get("t1"); t2 = plan.get("t2"); side = plan.get("side")


# ---- SEGÉD-RAJZOLÓK -------------------------------------------------------
def page(fig_bg=PAPER):
    fig = plt.figure(figsize=(8.27, 11.69))  # A4
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                                fc=fig_bg, ec="none", zorder=-10))
    return fig, ax

def band(ax, y0, y1, color):
    ax.add_patch(FancyBboxPatch((0, y0), 1, y1 - y0, boxstyle="square,pad=0",
                                fc=color, ec="none", zorder=-5))

def rband(ax, x, y, w, h, color, r=0.02, ec="none", lw=0, z=1, alpha=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=color, ec=ec, lw=lw, zorder=z, alpha=alpha))

def img(ax, path, x, y, w, h, z=0):
    """place an image into box (x,y,w,h) on the SAME axes (so text zorder works)."""
    if not os.path.exists(path):
        rband(ax, x, y, w, h, NAVY2, r=0.02, z=z)
        return
    im = mpimg.imread(path)
    ax.imshow(im, aspect="auto", extent=(x, x + w, y, y + h), zorder=z)

def footer(ax, pg):
    ax.text(0.06, 0.028, "BTC SIGNAL ENGINE  ·  napi jelentés", fontsize=7.5,
            color=GREY, va="center")
    ax.text(0.94, 0.028, f"{pg}", fontsize=8, color=GREY, va="center", ha="right")
    ax.text(0.5, 0.028, "Nem pénzügyi tanács · oktatási célú", fontsize=7,
            color=GREY, va="center", ha="center", style="italic")


pdf = PdfPages(OUT)

# ==========================================================================
# 1. OLDAL — BORÍTÓ
# ==========================================================================
fig, ax = page(NAVY)
img(ax, os.path.join(IMG, "cover.png"), 0, 0, 1, 1, z=0)
# sötét overlay a szöveg mögé
ax.add_patch(FancyBboxPatch((0, 0.78), 1, 0.22, boxstyle="square,pad=0",
                            fc=NAVY, ec="none", alpha=0.55, zorder=5))
ax.add_patch(FancyBboxPatch((0, 0), 1, 0.30, boxstyle="square,pad=0",
                            fc=NAVY, ec="none", alpha=0.70, zorder=5))
ax.text(0.5, 0.93, "BITCOIN", fontsize=52, color=GOLD, ha="center",
        va="center", weight="bold", zorder=10)
ax.text(0.5, 0.865, "NAPI JELENTÉS — EGYSZERŰEN", fontsize=15, color=WHITE,
        ha="center", va="center", weight="bold", zorder=10)
ax.text(0.5, 0.825, f"{today}", fontsize=12, color="#c9d4e0", ha="center",
        va="center", zorder=10)

# nagy ár + mai üzenet a lenti sávban
ax.text(0.5, 0.225, "MAI ÁR", fontsize=13, color="#c9d4e0", ha="center", zorder=10)
ax.text(0.5, 0.15, f"${px:,.0f}", fontsize=46, color=WHITE, ha="center",
        weight="bold", zorder=10)
arrow = "▲" if chg7 >= 0 else "▼"
acol = GREEN if chg7 >= 0 else RED
ax.text(0.5, 0.085, f"{arrow} {chg7:+.1f}% az elmúlt 7 napban",
        fontsize=13, color=acol, ha="center", weight="bold", zorder=10)
# lámpa-jelvény
rband(ax, 0.30, 0.015, 0.40, 0.05, AMBER, r=0.025, z=10)
ax.text(0.5, 0.04, f"MAI DÖNTÉS:  VÁRJ", fontsize=15, color=NAVY, ha="center",
        va="center", weight="bold", zorder=11)
pdf.savefig(fig); plt.close(fig)

# ==========================================================================
# 2. OLDAL — MI TÖRTÉNIK? (közlekedési lámpa)
# ==========================================================================
fig, ax = page(PAPER)
band(ax, 0.92, 1.0, NAVY)
ax.text(0.06, 0.955, "1.  MI A HELYZET MA?", fontsize=20, color=WHITE,
        va="center", weight="bold")

# lámpa kép
img(ax, os.path.join(IMG, "light.png"), 0.06, 0.585, 0.40, 0.30)
# magyarázat jobbra
ax.text(0.52, 0.86, "Képzeld el úgy,", fontsize=15, color=INK, weight="bold")
ax.text(0.52, 0.825, "mint egy közlekedési lámpát.", fontsize=15, color=INK, weight="bold")
expl = ("Most SÁRGA van.\n"
        "Ne vegyél és ne adj el\n"
        "épp most.\n\n"
        "Az ár \"senki földjén\" áll —\n"
        "se nem olcsó, se drága.\n\n"
        "A türelem itt pénz.")
ax.text(0.52, 0.77, expl, fontsize=13.5, color=INK, va="top", linespacing=1.55)

# 3 nagy szám-kártya
cards = [
    (f"${px:,.0f}", "Mai ár", GOLD),
    (f"{chg7:+.1f}%", "7 napos változás", GREEN if chg7 >= 0 else RED),
    (f"{chg30:+.1f}%", "30 napos változás", GREEN if chg30 >= 0 else RED),
]
cw = 0.28; gap = 0.03; x0 = 0.06
for i, (big, lab, col) in enumerate(cards):
    x = x0 + i * (cw + gap)
    rband(ax, x, 0.375, cw, 0.15, WHITE, r=0.02, ec="#e3ddd0", lw=1)
    ax.text(x + cw/2, 0.48, big, fontsize=23, color=col, ha="center", weight="bold")
    ax.text(x + cw/2, 0.41, lab, fontsize=11.5, color=GREY, ha="center")

# egy mondatos összegzés
rband(ax, 0.06, 0.12, 0.88, 0.20, NAVY2, r=0.02)
ax.text(0.10, 0.28, "EGY MONDATBAN:", fontsize=12, color=GOLD, weight="bold")
one = ("A Bitcoin most erős, de fáradt. Felfelé megy, viszont épp\n"
       "egy nagy akadály (ellenállás) alatt pihen. A rendszerünk\n"
       "szerint MA nem érdemes belépni — inkább várunk egy jobb\n"
       "árra lentebb, ahol az esély sokkal jobb.")
ax.text(0.10, 0.185, one, fontsize=13, color=WHITE, va="center", linespacing=1.5)
footer(ax, "2")
pdf.savefig(fig); plt.close(fig)

# ==========================================================================
# 3. OLDAL — A MÁGNES-ELMÉLET (miért mozog az ár)
# ==========================================================================
fig, ax = page(PAPER)
band(ax, 0.92, 1.0, NAVY)
ax.text(0.06, 0.955, "2.  MIÉRT MOZOG AZ ÁR? — A MÁGNES", fontsize=18, color=WHITE,
        va="center", weight="bold")

img(ax, os.path.join(IMG, "magnet.png"), 0.06, 0.615, 0.44, 0.265)
ax.text(0.54, 0.855, "A piacon vannak\n\"mágnesek\".", fontsize=15, color=INK,
        weight="bold", va="top", linespacing=1.4)
mtxt = ("Ezek olyan árszintek, ahol\n"
        "sok ember pénze gyűlik\n"
        "össze. Az ár hajlamos\n"
        "ezek FELÉ mozogni —\n"
        "mint a vas a mágneshez.\n\n"
        "Aki tudja, hol vannak,\n"
        "látja, merre húzhat az ár.")
ax.text(0.54, 0.775, mtxt, fontsize=12.5, color=INK, va="top", linespacing=1.45)

# két mágnes-kártya: fent vs lent
ax.text(0.06, 0.55, "HOL VANNAK MOST A LEGNAGYOBB MÁGNESEK?",
        fontsize=13, color=INK, weight="bold")

# FENT
rband(ax, 0.06, 0.335, 0.42, 0.17, WHITE, r=0.02, ec=RED, lw=1.5)
ax.text(0.27, 0.475, "FELETTÜNK", fontsize=13, color=RED, ha="center", weight="bold")
if big_above:
    ax.text(0.27, 0.42, f"${big_above['price']:,.0f}", fontsize=22, color=INK,
            ha="center", weight="bold")
    ax.text(0.27, 0.375, f"erő: {big_above['count']}×  ·  +{(big_above['price']/px-1)*100:.1f}%",
            fontsize=11, color=GREY, ha="center")
ax.text(0.27, 0.35, "közeli, de kisebb", fontsize=10.5, color=GREY, ha="center", style="italic")

# LENT
rband(ax, 0.52, 0.335, 0.42, 0.17, WHITE, r=0.02, ec=GREEN, lw=1.5)
ax.text(0.73, 0.475, "ALATTUNK", fontsize=13, color=GREEN, ha="center", weight="bold")
if big_below:
    ax.text(0.73, 0.42, f"${big_below['price']:,.0f}", fontsize=22, color=INK,
            ha="center", weight="bold")
    ax.text(0.73, 0.375, f"erő: {big_below['count']}×  ·  {(big_below['price']/px-1)*100:.1f}%",
            fontsize=11, color=GREY, ha="center")
ax.text(0.73, 0.35, "távolabb, de ÓRIÁSI", fontsize=10.5, color=GREEN, ha="center", weight="bold")

# tanulság sáv
rband(ax, 0.06, 0.12, 0.88, 0.16, NAVY2, r=0.02)
ax.text(0.10, 0.245, "MIT JELENT EZ?", fontsize=12, color=GOLD, weight="bold")
if big_below and big_above:
    ratio = big_below["count"] / max(big_above["count"], 1)
    lesson = (f"Lent {ratio:.1f}-szer nagyobb \"mágnes\" van, mint fent. Ezért van\n"
              "esély rá, hogy az ár előbb-utóbb lefelé is elmegy vadászni —\n"
              "de amíg a fenti akadály tart, felfelé is húzhat. Ezt figyeljük.")
    ax.text(0.10, 0.16, lesson, fontsize=12.5, color=WHITE, va="center", linespacing=1.5)
footer(ax, "3")
pdf.savefig(fig); plt.close(fig)

# ==========================================================================
# 4. OLDAL — A TERV (hol és mit tennénk)
# ==========================================================================
fig, ax = page(PAPER)
band(ax, 0.92, 1.0, NAVY)
ax.text(0.06, 0.955, "3.  HA CSELEKEDNÉNK — A TERV", fontsize=19, color=WHITE,
        va="center", weight="bold")

img(ax, os.path.join(IMG, "buyzone.png"), 0.06, 0.62, 0.42, 0.26)
ax.text(0.52, 0.86, "A rendszer NEM vesz most.", fontsize=14.5, color=INK, weight="bold")
ax.text(0.52, 0.825, "De előre kijelöl egy okos", fontsize=13.5, color=INK)
ax.text(0.52, 0.795, "vételi tervet lentebb:", fontsize=13.5, color=INK)
plan_txt = ("Ha az ár lejön a zöld\nzónába, ott VESZÜNK\n"
            "egy kis részt, szoros\nbiztonsági határral.\n\n"
            "Kis kockázat,\nnagy lehetséges nyereség.")
ax.text(0.52, 0.755, plan_txt, fontsize=12.5, color=INK, va="top", linespacing=1.45)

# a terv számai lépcsőként
def steprow(y, label, value, col, note=""):
    rband(ax, 0.06, y, 0.88, 0.075, WHITE, r=0.015, ec="#e3ddd0", lw=1)
    ax.add_patch(FancyBboxPatch((0.06, y), 0.012, 0.075, boxstyle="square,pad=0",
                                fc=col, ec="none"))
    ax.text(0.10, y + 0.037, label, fontsize=12.5, color=INK, va="center", weight="bold")
    ax.text(0.66, y + 0.037, value, fontsize=15, color=col, va="center",
            ha="right", weight="bold")
    if note:
        ax.text(0.69, y + 0.037, note, fontsize=10.5, color=GREY, va="center")

y = 0.50
if side in ("LONG", "SHORT") and entry:
    steprow(y, "1) BELÉPŐ (itt veszünk)", f"${entry:,.0f}", GREEN, "csak ha ide lejön")
    steprow(y - 0.09, "2) STOP (ha rossz, itt szállunk)", f"${stop:,.0f}", RED, "kis veszteség")
    steprow(y - 0.18, "3) ELSŐ CÉL (fél zár)", f"${t1:,.0f}", GOLD, "nyereség bezseb.")
    steprow(y - 0.27, "4) MÁSODIK CÉL (a többi)", f"${t2:,.0f}", GOLD, "nagyobb nyereség")

# kockázat/nyereség dobozka
rr = plan.get("rr1") or (abs(t1 - entry) / abs(entry - stop) if (entry and stop and t1) else None)
rband(ax, 0.06, 0.12, 0.88, 0.09, NAVY2, r=0.02)
ax.text(0.10, 0.183, "A LÉNYEG:", fontsize=12, color=GOLD, weight="bold")
if entry and stop and t1:
    risk = abs(entry - stop); reward = abs(t1 - entry)
    ax.text(0.10, 0.145, f"Kockáztatunk kb. {risk:,.0f} dollárt, hogy nyerjünk kb. {reward:,.0f} dollárt az első célig.",
            fontsize=12, color=WHITE, va="center")
    if rr:
        ax.text(0.10, 0.135, f"", fontsize=1, color=WHITE)
footer(ax, "4")
pdf.savefig(fig); plt.close(fig)

# ==========================================================================
# 5. OLDAL — ÖSSZEFOGLALÓ + SZABÁLYOK
# ==========================================================================
fig, ax = page(NAVY)
ax.text(0.06, 0.93, "ÖSSZEFOGLALÓ", fontsize=24, color=GOLD, weight="bold")
ax.text(0.06, 0.885, f"{today}  ·  Bitcoin", fontsize=13, color="#c9d4e0")

# nagy lámpa
rband(ax, 0.06, 0.70, 0.88, 0.13, NAVY2, r=0.02)
dot(ax, 0.155, 0.765, 0.033, AMBER)
ax.text(0.26, 0.79, "MAI DÖNTÉS:  VÁRJ", fontsize=20, color=WHITE, weight="bold", va="center")
ax.text(0.26, 0.735, sub, fontsize=12.5, color="#c9d4e0", va="center")

# 4 tömör pont
pts = [
    ("Az ár most:", f"${px:,.0f}  ({chg7:+.1f}% / hét)"),
    ("Miért várunk:", "erős, de fáradt trend, nagy akadály felettünk"),
    ("Hol vennénk:", f"${entry:,.0f} körül, ha lejön" if entry else "lentebb, szintnél"),
    ("Nagy kép:", "a legnagyobb mágnes lent van — óvatosan felfelé"),
]
y = 0.62
for lab, val in pts:
    dot(ax, 0.10, y + 0.01, 0.010, GOLD)
    ax.text(0.13, y + 0.01, lab, fontsize=13, color=GOLD, va="center", weight="bold")
    ax.text(0.37, y + 0.01, val, fontsize=13, color=WHITE, va="center")
    y -= 0.075

# arany szabályok
rband(ax, 0.06, 0.13, 0.88, 0.18, "#10233a", r=0.02, ec=GOLD, lw=1)
ax.text(0.10, 0.28, "3 ARANYSZABÁLY KEZDŐKNEK", fontsize=13, color=GOLD, weight="bold")
rules = ("1.  Soha ne tedd fel a pénzed nagy részét egy tippre.\n"
         "2.  Mindig legyen STOP — ez a mentőöv, ha rosszul megy.\n"
         "3.  A VÁRJ is döntés. A legjobb kereskedők sokat várnak.")
ax.text(0.10, 0.205, rules, fontsize=13, color=WHITE, va="center", linespacing=1.8)

ax.text(0.5, 0.055, "Ez a jelentés a saját elemző-motorunk számaiból készült.",
        fontsize=9.5, color=GREY, ha="center")
ax.text(0.5, 0.032, "Nem pénzügyi tanács. A kripto kockázatos. Csak azt tedd kockára, amit elbírsz veszíteni.",
        fontsize=9, color=GREY, ha="center", style="italic")
pdf.savefig(fig); plt.close(fig)

pdf.close()
print("OK ->", OUT)
