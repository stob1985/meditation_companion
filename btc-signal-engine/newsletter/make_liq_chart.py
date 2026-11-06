import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["text.parse_math"] = False
BG, INK, MUT, RED, GRN, GOLD = "#0d1117", "#e6edf3", "#8b949e", "#f0514a", "#2fbf71", "#f0b429"
rows = [("±2%", 0.8, 0.1), ("±5%", 1.05, 0.65), ("±8%", 1.15, 1.6), ("±11%", 1.23, 3.3), ("to $87k", 1.23, 4.5)]
fig = plt.figure(figsize=(16, 9), dpi=100); fig.patch.set_facecolor(BG)
fig.text(0.05, 0.92, "BTC liquidations: much more fuel above — but the nearest pool is below",
         fontsize=26, color=INK, weight="bold")
fig.text(0.05, 0.875, "Price $75,633  ·  Binance BTC/USDT perp, 30-day liquidation map  ·  cumulative $ that gets force-closed",
         fontsize=15, color=MUT)
ax = fig.add_axes([0.11, 0.25, 0.53, 0.56]); ax.set_facecolor(BG)
y = list(range(len(rows)))[::-1]
for yi, (lab, lo, hi) in zip(y, rows):
    ax.barh(yi, -lo, color=RED, height=0.62); ax.barh(yi, hi, color=GRN, height=0.62)
    ax.text(-lo - 0.08, yi, f"${lo:.1f}B", va="center", ha="right", color=INK, fontsize=15, weight="bold")
    ax.text(hi + 0.08, yi, f"${hi:.1f}B", va="center", ha="left", color=INK, fontsize=15, weight="bold")
    r = hi / lo
    tag = f"{1/r:.1f}× below" if r < 1 else f"{r:.1f}× above"
    ax.text(5.6, yi, tag, va="center", ha="left", color=(RED if r < 1 else GRN), fontsize=14, weight="bold")
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], color=INK, fontsize=16, weight="bold")
ax.axvline(0, color=MUT, lw=1); ax.set_xlim(-2.2, 6.6)
ax.set_xticks([]); [s.set_visible(False) for s in ax.spines.values()]; ax.tick_params(length=0)
ax.text(-1.1, len(rows) - 0.35, "LONGS liquidated below", color=RED, fontsize=15, ha="center", weight="bold")
ax.text(2.25, len(rows) - 0.35, "SHORTS liquidated above", color=GRN, fontsize=15, ha="center", weight="bold")
# right panel: price ladder
lx = fig.add_axes([0.68, 0.18, 0.29, 0.66]); lx.set_facecolor(BG); lx.set_xlim(0, 1); lx.set_ylim(66500, 88500); lx.axis("off")
def band(y0, y1, col, txt, sub, ty=None):
    lx.add_patch(FancyBboxPatch((0.02, y0), 0.30, y1 - y0, boxstyle="round,pad=0,rounding_size=0.02", fc=col, ec="none", alpha=0.85))
    ty = (y0 + y1) / 2 if ty is None else ty
    lx.text(0.37, ty + 300, txt, color=INK, fontsize=13.5, weight="bold", va="center")
    lx.text(0.37, ty - 450, sub, color=MUT, fontsize=11.5, va="center")
band(85000, 86200, GRN, "$85–86k", "2nd short wall · cum. ~$4B")
band(81200, 83300, GRN, "$81–83k", "main short wall · $1.3B → $2.9B")
band(78600, 78900, GRN, "$78.7k", "first short block")
lx.plot([0.0, 1.0], [75633, 75633], color=GOLD, lw=2.5, ls="--")
lx.text(0.37, 76500, "PRICE $75,633", color=GOLD, fontsize=14, weight="bold", va="center")
band(74100, 75600, RED, "$74.1–75.6k", "~2/3 of ALL longs to $67k · 50–100x", ty=74000)
lx.add_patch(FancyBboxPatch((0.02, 67200), 0.30, 73900 - 67200, boxstyle="round,pad=0,rounding_size=0.02", fc=RED, ec="none", alpha=0.18))
lx.text(0.37, 70600, "below $74k: nearly empty", color=INK, fontsize=13.5, weight="bold", va="center")
lx.text(0.37, 69850, "~$0.4B spread over $7,000", color=MUT, fontsize=11.5, va="center")
fig.text(0.05, 0.13, "Read: the closest, most fragile pool (50–100x longs) sits 0.5–2% under price → likely flushed first.",
         fontsize=15, color=INK)
fig.text(0.05, 0.09, "After that, little is left below to hunt — and ~$4.5B of shorts sits above.",
         fontsize=15, color=INK)
fig.text(0.05, 0.035, "Values read from the Coinglass chart (±15%). Binance only, model estimate. Not financial advice.",
         fontsize=11.5, color=MUT, style="italic")
out = "/home/user/meditation_companion/btc-signal-engine/newsletter/img/social/btc_liq_asymmetry.png"
fig.savefig(out, facecolor=BG); print(out)
