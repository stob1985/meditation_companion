# FOLYTATÁS — hogyan viszem tovább egy új ablakban

A **kód és a tudásbázis a GitHub-on van** (nem vész el). Az új Claude-ablak üresen
indul, de **1 üzenettel képbe hozható**. Csináld ezt:

## 1. Új ablak / új session indítása

- **Claude Code (terminál):** klónozd és lépj be, majd indíts `claude`-ot:
  ```bash
  git clone https://github.com/stob1985/meditation_companion.git
  cd meditation_companion && git checkout claude/blissful-meitner-1u3fp
  cd btc-signal-engine && pip install -r requirements.txt
  claude
  ```
- **Claude.ai / web:** nyiss új chatet, és másold be a lenti indító-üzenetet.

## 2. Az INDÍTÓ ÜZENET (másold be elsőként az új ablakba)

```
Egy BTC/kripto jelző-rendszert fejlesztünk. A teljes kód és tudásbázis itt:
repo stob1985/meditation_companion, branch claude/blissful-meitner-1u3fp,
almappa btc-signal-engine/. ELŐSZÖR olvasd el a btc-signal-engine/HANDOVER.md-t
és a README.md-t — abban van az architektúra, minden modul és a stratégia.

Amit eddig csináltunk és a stílusom:
- Minden nap lefuttatjuk: `python run.py --source live` (BTC), és kérésre ETH is.
- MINDIG a TELJES kimenetet kérem (összes modul), nem rövidített összefoglalót.
- Fókusz: likvidációs szintek + egyértelmű BUY/SHORT/WAIT döntés, magyarul.
- Fontos elv: őszinteség — a korlátokat is mondd ki (napi idősík, proxy likvidáció,
  vékony minta), soha ne hamisíts zöld számot.
- A saját tézisem: a nagy lenti likvidációs medence miatt BIKACSAPDA-kockázat —
  ezt a gép a LIQUIDITY GRAVITY + TRAP WATCH modullal figyeli.
- ÚJ (2026-07-19): kapott egy SWING RÉTEGET (havi 1-3 nagy trade mód) — 6 kapu
  (heti regime, kompozit 65+, vol-kompresszió timing, ETF-flow, tömeg/funding,
  gravitáció) + 1/3 TP + Donchian(10) runner. A dashboardon "SWING RÉTEG" szekció;
  backtest: `run.py --backtest` a SWING BACKTEST blokkot is kiírja. A scalp/napi
  réteg VÁLTOZATLAN — a swing additív. Részletek: HANDOVER.md 3/7/9. pont.

Első feladat: futtasd le a mai BTC-t a teljes stack-kel és add meg az
egyértelmű jelzést (döntés + szintek + gravity + csapda-státusz).
```

## 3. Jelenlegi állás (a legutóbbi olvasat — kontextusnak)

- **Rendszer kész, 22+3 modul aktív** (lásd HANDOVER.md modul-térkép; a +3 a
  SWING réteg: volregime.py, etfflow.py, swing.py + backtest.run_swing).
- **Legutóbbi kép (kb. 2026-07 közepe):** BTC ~62–65k sávban, kompozit ingadozik
  FLAT/UP körül, **a LIQUIDITY GRAVITY tartósan LEFELÉ húz** (nagy lenti mágnes
  ~57–58k, x70–x79) → a **bikacsapda a fő szcenárió** egy 67–73k-s rally esetén.
  ETH relatíve erősebb/kiegyensúlyozottabb gravitációval; a cél fent ~2,186.
- **Nyitott roadmap:** valós likvidációs heatmap (Coinglass) · intraday HTF-motor ·
  trap_watch backteszt · 4H-reversal bekötése a napi futásba · walk-forward súly-opt.

## 4. Fontos, hogy ne vessz el

- A friss munkát **commitold + pushold** minden session végén (a konténer efemer).
- A branch **feature-ág** a meditation_companion repóban; ha külön repót akarsz,
  neked kell nyitnod (a connector csak a meditation_companion-ra jogosít).
- Ez oktatási/kutatási eszköz, **nem pénzügyi tanács**.
