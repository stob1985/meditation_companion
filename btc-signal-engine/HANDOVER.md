# HANDOVER — BTC Signal Engine (tudásbázis átadás)

> Ez a dokumentum egy MÁSIK AI-agentnek (pl. Hermes) készült, hogy önállóan
> megértse és integrálja ezt a rendszert. Minden, ami a rendszer működéséhez és
> továbbfejlesztéséhez kell, itt van összefoglalva.

## 0. Hol van a projekt

- **Git repo:** `stob1985/meditation_companion`
- **Branch:** `claude/blissful-meitner-1u3fp`
- **Almappa:** `btc-signal-engine/`  ← EZ a rendszer
- Lehúzás:
  ```bash
  git clone https://github.com/stob1985/meditation_companion.git
  cd meditation_companion && git checkout claude/blissful-meitner-1u3fp
  cd btc-signal-engine && pip install -r requirements.txt
  python run.py --source live        # teljes élő dashboard (BTC)
  ```
- Nyelv: Python 3.11+. Külső kulcs NEM kell (nyilvános tőzsde-API-k).

## 1. Mi ez

Kripto (elsősorban BTC) **napi jelző + kereskedési-döntés motor**, ami egy diszkrecionális
scalp-trader (ChentoTrades) videós módszertanát mechanizálja + kiegészíti. Két fő ötlet:
1. **Likvidáció-vezérelt piac**: az ár a nagy likvidációs klaszterekhez („mágnesekhez") húz.
2. **Dwell / idő-az-áron**: ahol az ár sok időt tölt = erős zóna; a hozzá viszonyított
   konszolidáció adja az irányt.

A kimenet egy terminál-dashboard (`run.py`) + PDF hírlevél (`make_newsletter.py`).

## 2. Adatforrás

`engine/data.py` — 5 nyilvános tőzsde fallback-lánccal: **OKX → Binance.US →
Hyperliquid → Kraken → Coinbase** (Bybit 403-tiltott a legtöbb felhőből, ezért kihagyva).
Interval: `1,5,15,60,120,240,D`. Bármelyik coin: `data._fetch_okx("ETH-USDT","1D",1000)`.

## 3. Modul-térkép (engine/)

| Modul | Feladat | Fő függvény |
|---|---|---|
| `data.py` | OHLCV több tőzsdéről | `load_live(sym,interval,limit,exchange)` |
| `events.py` | Phase-1 esemény-detektorok (naptár/RSI/vol/pivot/streak/hold/ASIA/planets) | `detect(df,cfg)` |
| `vdb.py` | Virtual Event Database: eseményenkénti forward-hozam statisztika (WR, EXPECT, PF, LAST-5, EDGE) | `build(close,events,cap,horizons)` |
| `astro.py` | bolygó-aspektusok (súly 0 — nincs bizonyított él, csak kijelzés) | `aspects(date,orb)` |
| `signal.py` | **KOMPOZIT**: events+dwell+CVD+regime+reversal → UP/DN%, forecast, MTF/regime | `composite(df,events,db,cfg,at,dwell)` |
| `dwell.py` | dwell blokkok (idő/volumen-az-áron) + IRÁNY-szabály (fölött→UP, alatt→DOWN, közép→DOWN) | `build(df,cfg)` |
| `liquidity.py` | proxy likvidációs klaszterek (10/25/50/100x, tiered MMR, tap-count, bounce), **multi-venue konfluencia**, **GRAVITY** | `build`, `build_multi`, `gravity` |
| `flow.py` | CVD/money-flow + spot-vs-perp divergencia | `cvd_bias`, `okx_spot_perp_divergence` |
| `realflow.py` | ÉLŐ valós adat: OKX likvidációk + OI + **long/short arány** + funding (per-coin) | `build(cfg,price,atr)` |
| `macro.py` | BTC vs SPX/NDX/DXY/arany/olaj korreláció (best-effort, Stooq) | `build(df,cfg)` |
| `sessions.py` | Asia/London/NY szekvencia-valószínűség (intraday) | `build(df,cfg)` |
| `reversal.py` | sweep-reclaim fordulat („lesöpri a mélyt, visszahódít") | `detect(df,cfg)` |
| `trade.py` | belépő/stop/T1/T2, zónák, hedge, void, **TRAP WATCH** (bikacsapda-figyelő) | `plan`, `zones`, `trap_watch` |
| `backtest.py` | 3 backteszt: irány, cél-találat, szint-belépő (walk-forward) | `run`, `run_targets`, `run_levels` |
| `position.py` | állapot-követés futások közt (BE/T1/T2/stop, --track) | `manage`, `open_from_plan` |
| `dashboard.py` | terminál-render | `render(sig,liq,db,cfg,dwell,trade,overlays)` |

`run.py` = a belépési pont (mindent összeköt). `make_newsletter.py` = PDF hírlevél
(matplotlib grafikon + PdfPages, az agency-agents-stob agent-módszertanaival).

## 4. A stratégia / koncepciók (a tudás lényege)

- **Kompozit irány**: sok gyenge jel súlyozott összege → UP/DN%. Küszöb: `conv >= 62%` a belépőhöz.
- **Regime-override** (`signal.regime_weight=2.5`): a trend ellen ne fogadjon (ne longozzon STRONG BEAR-be).
- **Dwell-szabály**: az ár helye a legközelebbi blokkhoz képest adja az irányt.
- **Likvidációs mágnesek**: swing-pivot × tőkeáttét → klaszterek; 5 tőzsdén egyező = erős (`x45` = 45 klaszter).
- **LIQUIDITY GRAVITY**: `méret/(1+ATR-táv)` húzóerő fent vs lent → melyik medence nyer.
- **TRAP WATCH**: ha a gravitáció LE, de az ár a fenti kis klaszterek felé megy → bikacsapda; 5 jel
  (CVD-divergencia, tömeg-long, funding forró, nincs dwell-acceptance, sweep-reject) → WATCH/ARMED + short-terv a nagy lenti mágnesre.
- **Szint-belépő + részleges TP**: nem minden gyertyán, hanem a struktúra-szintnél; T1-nél fél zár + stop BE, T2 runner.
- **Sweep-reclaim reversal**: alj-jel; a 4H-n élesebb, mint napin.
- **Valós flow kontrár**: L/S > 1.3 (tömeg long) → bearish; funding negatív = kapituláció.

## 5. Fő config-kulcsok (`config.yaml`)

`signal.regime_weight/dwell_weight/flow_weight/reversal_weight` · `trade.conv_min(62)/leverage(10)/
entry_mode(levels)/rr_min` · `liquidity.multi_venue/venues/mmr_tiers` · `trap.enabled/ls_hot(1.6)/funding_hot` ·
`reversal.swing_lookback/rsi_os` · `realflow.inst_family(coinonként!)`.

## 6. Programozott hívás (integrációhoz)

```python
import yaml; from engine import data, events as ev, vdb, signal, liquidity, dwell, trade
cfg = yaml.safe_load(open("config.yaml"))
df = data.load_live("BTCUSDT","D",1000,"okx")
e = ev.detect(df,cfg); db = vdb.build(df["close"],e,cap=cfg["vdb"]["cap"],horizons=(1,3,5))
dw = dwell.build(df,cfg); sig = signal.composite(df,e,db,cfg,at=-1,dwell=dw)
liq = liquidity.build(df,cfg); ml = liquidity.build_multi(cfg)
g = liquidity.gravity(ml["clusters_above"], ml["clusters_below"], liq["price"], liq["atr"])
plan = trade.plan(sig, liq, dw, cfg)          # entry/stop/T1/T2 vagy WAIT
# sig["bias"], sig["up"], liq["clusters_below"], g["direction"], plan["side"] ...
```

## 7. Backteszt (validált él)

`backtest.run_levels(df, events, cfg)` → a szint-belépő+részleges-TP stratégia. A tesztelt BTC
történeten ~+27% out-of-sample (~300 nap, 4/5 walk-forward ablak pozitív). **Szerény, valódi él —
NEM garantált.** Alacsony trade-szám, magas szórás.

## 8. ŐSZINTE korlátok (fontos a másik agentnek)

- **Napi idősík**: az él a napi/HTF adaton van; **5m/15m intraday-en a kompozit zaj** (külön HTF-bias
  + order-flow motor kellene). A sweep-reclaimet a 4H fogja, a napi késhet.
- **Proxy likvidáció** = becslés swing-pivotokból, NEM valós order-book. A multi-venue konfluencia erősíti.
- **Makró (Stooq) és néha egyes API-k** blokkoltak lehetnek felhőből — best-effort, gracefully kimarad.
- **Astro**: nincs bizonyított él (súly 0).
- **Reaktív fejlesztés kockázata**: több elem utólag került be (regime, reversal, trap) — a walk-forward
  validálás ezt csökkenti, de a minta vékony (~30 trade).
- **NEM pénzügyi tanács**; oktatási/kutatási eszköz.

## 9. Mit érdemes tovább (roadmap)

Valós likvidációs heatmap (Coinglass/force-order stream) a proxy mellé · intraday HTF-bias motor ·
a trap_watch backtesztelése · a reversal 4H-figyelő bekötése a napi futásba · walk-forward
súly-optimalizáló (túlillesztés ellen) · per-coin session/flow finomítás.
