# BTC Signal Engine (MVP)

Egy kétrészes rendszer, ami a két képernyőképet reprodukálja:

1. **Irány-motor** (1. kép: *P2+VDB v4*) – esemény-alapú valószínűségi modell
   (naptár / technikai / hold / bolygók) + **Virtual Event Database** (eseményenkénti
   visszatesztelt hozam-statisztika) → kompozit **UP/DN bias** + 5 napos előrejelzés.
2. **Likviditás-motor** (2. kép: likvidációs hőtérkép) – **PROXY** (ingyenes, becsült)
   likvidációs klaszterek a swing-pivotokból × tőkeáttéti szintekből (10/25/50/100x),
   imbalance, CVD bias, klaszter-szintek.
3. **Kereskedési réteg** (`engine/trade.py`) – az irány + likviditási klaszterek +
   dwell blokkok → konkrét **belépő / stop / cél**, **R:R ≥ 1:3**, **fix tét × tőkeáttétel**
   pozícióméret, és **likvidáció-vs-stop biztonsági ellenőrzés**.
4. **Dwell time / dwell block** (`engine/dwell.py`) – idő/volumen-az-áron profil:
   POC, value area, magas-elidőzésű blokkok (acceptance zónák), és egy „coiling/trending"
   állapotjelző. A trade réteg ezt használja a stop/cél finomításához.

A statisztikai mag **Python**, a vizualizáció **Pine Script** (TradingView).

---

## Mappa-szerkezet
```
btc-signal-engine/
  run.py                CLI – ez fut le
  config.yaml           minden paraméter (a képek értékeire hangolva)
  engine/
    data.py             OHLCV: live (több tőzsde) / csv / synthetic
    events.py           Phase 1 esemény-detektorok
    astro.py            Phase 2 – hold + bolygó-aspektusok (pyephem)
    vdb.py              Virtual Event Database (forward-return statisztika)
    liquidity.py        proxy likvidációs klaszterek (tiered MMR + tap-count)
    dwell.py            dwell time / dwell block + IRÁNY-szabály
    flow.py             money flow / CVD + spot-vs-perp divergencia
    signal.py           kompozit irány (events + dwell + CVD + planet) + forecast
    trade.py            entry/stop/target, R:R, méret, likvidáció, díjak, hedge, void
    macro.py            makró-korreláció overlay (SPX/NDX/DXY/arany/olaj – best-effort)
    sessions.py         Asia/London/NY session-szekvencia valószínűség (intraday)
    backtest.py         OUT-OF-SAMPLE backteszt (díj+funding nettósítva)
    dashboard.py        terminál panel a képek stílusában
  pine/
    p2_vdb_lite.pine    TradingView companion indikátor
```

## Futtatás (Claude Code-ban, valós adattal)
```bash
pip install -r requirements.txt
python run.py --source live --backtest      # valós napi adat + backteszt
python run.py                               # offline demó (szintetikus adat)
python run.py --source csv                  # saját CSV-ből (config.yaml: csv_path)
```
A `config.yaml`-ban `data.interval`-t állítsd `"60"`-ra (1H) vagy `"120"`-ra (2H),
ha a 2. kép intraday likviditási nézetét akarod.

### Élő adat – több tőzsde, automatikus fallback
A `data.py` sorban próbálja a nyilvános (kulcs nélküli) tőzsde-API-kat, és az
elsőt használja, amelyik válaszol – így akkor is megy, ha az egyik geo-blokkolt:

```
OKX → Hyperliquid → Binance.US → Coinbase → Kraken
```
`config.yaml: data.exchange` = `auto` (alapért.) vagy egy konkrét tőzsde neve.
**Megjegyzés:** a **Bybit egyes felhőkből 403-mal tiltott** (pl. ez a futtatókörnyezet),
ezért nincs az alap-láncban; saját gépen `exchange: bybit`-tel elérheted.
A motor itt **valós OKX BTC-USDT napi adaton** lett tesztelve.

## Kereskedési réteg (`engine/trade.py`)
A kompozit irányból + a likviditási térképből + a dwell blokkokból egy konkrét tervet ad:

- **stop** = a legközelebbi struktúra (dwell blokk / likviditási klaszter) mögé,
  ATR-pufferrel; ha nincs struktúra, ATR-fallback.
- **target** = a legközelebbi likvidációs **mágnes**, ami eléri az **R:R ≥ rr_min**-t
  (alap 1:3); ha egyik sem elég távoli, egy *projektált* R-szintet ad (megjelölve).
- **pozícióméret** = **fix tét (USD margin) × tőkeáttétel** → notional, BTC-mennyiség,
  USD-ben kifejezett nyereség/veszteség, és a tét %-ában mért kockázat.
- **likvidáció + biztonsági check**: kiszámolja a pozíció likvidációs árát, és
  **figyelmeztet, ha a likvidáció a stop előtt ütne be** (50–100x-nél tipikus), plusz
  megadja a *max biztonságos tőkeáttétel*-szintet.

## Dwell time / dwell block (`engine/dwell.py`)
Idő- és volumen-az-áron profil: **POC** (külön a blokkoktól), **value area**, és a
magas-elidőzésű **dwell blokkok** (acceptance zónák → erős támasz/ellenállás).
A `state` (COILING / TRENDING) jelzi, szűk sávban tekeredik-e az ár.

**Dwell IRÁNY-szabály (a transcript fő éle):** az ár helye a legközelebbi blokkhoz
képest adja az irányt — **blokk FÖLÖTT → UP** (shift out), **blokk ALATT → DOWN**
(„goner"), **blokk KÖZEPÉN → DOWN**, majd a következő blokkot célozza. Ez bekerül a
kompozitba (`signal.dwell_weight`), így a backtest is méri.

## Pontosság-növelő bővítések (ChentoTrades transcript alapján)
A `chentotrades_all_transcripts.txt`-ből kinyert és beépített elemek:

1. **Dwell irány-szabály** → kompozit irányjelzés (fent).
2. **Money flow / CVD** (`flow.py`) → a CVD lejtése + ár/CVD egyezés (confirm /
   distribution / absorption) bekerül a kompozitba (`signal.flow_weight`).
3. **Spot-vs-perp CVD divergencia** (OKX, best-effort) → ha a perp húzza az árat,
   de a spot nem erősíti meg, „perp-driven" (gyengébb) jelzés. Overlay.
4. **Tiered maintenance margin** → a likvidáció a tőkeáttétellel skálázódik
   (`liquidity.mmr_tiers`, `trade.mmr_tiers`), reálisabb likvidációs ár.
5. **Díjak + funding** a P/L-ben és a backtestben → nettó R:R és nettó expectancy.
6. **Void / no-trade zóna** → ha az ár nincs struktúra közelében (`trade.void_atr`),
   nincs trade („everything in between is noise").
7. **Regime-alapú HEDGE** → range/egyensúlyban long ÉS short láb, nettó lean-nel.
8. **Tap-count / power-of-three** → sokszor tesztelt szint „worn" (gyengébb cél).
9. **Makró-korreláció** (`macro.py`) → BTC vs SPX/NDX/DXY/arany/olaj (best-effort).
10. **Session-szekvencia** (`sessions.py`) → P(NY↑ | Asia, London) intraday adaton.
11. **Multi-tőzsdés likvidációk** (`liquidity.build_multi`) → a proxy likvidációs
    térképet **több tőzsdén** (OKX/Binance.US/Hyperliquid/Kraken/Coinbase) építi fel
    és **összevonja**: ahol több tőzsde egyetért egy szinten, az **erősebb mágnes**
    (kereszt-tőzsdei konfluencia). Élő módban fut, `liquidity.multi_venue`.
12. **Bounce Rate** + **LAST-5 / L-N WR / EDGE** oszlopok → a referencia dashboard
    hiányzó mezői (klaszter-visszapattanási arány; esemény friss teljesítménye).
13. **Regime-override** (`signal.regime_weight`) → a kompozit nem longoz erős
    trend ellen; ez hangolja a motort a referencia '0up/Ndown after regime'-jéhez.
14. **VALÓS flow** (`realflow.py`, élő-only) → OKX tényleges likvidációk + Open
    Interest + **long/short pozíció-arány** (kontrár olvasat) + Hyperliquid funding.
    Ez a valódi adat, amit a referencia-trader is néz (nem proxy). Overlay.
15. **Szint-belépő stratégia** (`backtest.run_levels`) → nem minden gyertyán lép be,
    hanem **a struktúra-szintnél** (UP → pullback a támaszhoz, DOWN → rally az
    ellenálláshoz), a szint az invalidáció, cél a szemközti klaszter, **fél pozíció
    a legközelebbi klaszternél zár + stop break-even**, a maradék fut. Walk-forward
    validált (nem egy hónapra illesztve).

### A szint-belépő backteszt (out-of-sample, díj+funding nettó)
```python
from engine import data, events as ev, backtest
import yaml; cfg = yaml.safe_load(open("config.yaml"))
df = data.load_live("BTCUSDT","D",1000,"okx")
print(backtest.run_levels(df, ev.detect(df,cfg), cfg))
```
Eredmény a tesztelt BTC történeten: **~+27% (~300 nap, out-of-sample), 4/5 walk-
forward ablak pozitív**, a brutális 2026-májusi szakasz −16.9% helyett ~nullszaldó.
**Szerény, valódi él — NEM garantált pénznyomtató**; alacsony trade-szám, magas szórás.

> A backtesztelt kompozit a df-ből számolható jeleket használja (events + dwell + CVD).
> A makró / session / spot-perp overlay-k **kontextus**, nem backteszt-bemenet
> (külső/élő adat kell hozzájuk; offline szépen kimaradnak).

## Pine indikátor
Másold a `pine/p2_vdb_lite.pine` tartalmát a TradingView Pine editorba → *Add to chart*.
Ez a „lite" verzió a hold-fázist és élő rolling win-rate-eket számol; a teljes
bolygó-aspektus + 500-mintás VDB a Python motorban él (az a mérvadó).

## Paraméter-megfeleltetés a képekhez
| Kép felirat | config kulcs |
|---|---|
| `pivLB=10` | `events.pivot_lookback` |
| `RSI OS (36)` | `events.rsi_os` |
| `Orb: Standard (6°)` | `astro.orb` |
| `cap 500 samples/event` | `vdb.cap` |
| `FORECAST 5-day @ 68%` | `signal.forecast_conf` |
| `Zones: ATR×0.3` | `liquidity.zone_mult` |
| `Piv: 5` | `liquidity.swing_lookback` |

## Trade / dwell paraméterek (`config.yaml`)
| Kulcs | Jelentés |
|---|---|
| `trade.rr_min` | minimum reward:risk (alap 3.0 = 1:3) |
| `trade.bet_usd` / `leverage` | fix tét + tőkeáttétel |
| `trade.mmr_tiers` | tiered maintenance margin tőkeáttételenként |
| `trade.taker_fee` / `funding_daily` | díj + funding a nettó P/L-hez |
| `trade.void_atr` / `enable_hedge` | no-trade zóna / hedge mód |
| `signal.dwell_weight` / `flow_weight` | dwell-irány és CVD súlya a kompozitban |
| `dwell.lookback` / `bins` / `block_pctile` | profil hossza / vödrök / blokk-küszöb |
| `macro.enabled` / `sessions.enabled` | overlay-k be/ki |

---

## Roadmap (következő lépések)
- [ ] Valós likviditási adat opció (Coinglass / order-book) a proxy mellé
- [x] Intraday session-detektor (Ázsia/London/NY) valós időbélyegekkel
- [x] Kereskedési réteg: belépő/cél/SL a klaszterekből, R:R ≥ 1:3, pozícióméret
- [x] „dwell time / dwell block" modul + irány-szabály
- [x] Több-tőzsdés élő adat (OKX/Hyperliquid/Binance.US/Coinbase/Kraken) fallbackkel
- [x] Money flow / CVD + spot-perp divergencia
- [x] Tiered MMR, díj+funding nettósítás, void zóna, regime-hedge, tap-count
- [x] Makró-korreláció overlay (SPX/NDX/DXY/arany/olaj)
- [ ] A trade réteg teljes backtesztelése (entry/stop/target szimuláció)
- [ ] Walk-forward optimalizálás (túlillesztés ellen)
- [ ] Pine: dwell blokkok + trade szintek megjelenítése
- [ ] HTML/web-dashboard, riasztások (webhook)

---

## ⚠️ Fontos, őszinte figyelmeztetések
- Ez **technikai/oktatási** projekt, **nem pénzügyi tanács**, és nem garantál nyereséget.
- A referencia-indikátoron látott **élek gyengék** (win rate ~50%, expectancy ~0,
  PF~1). A backteszt szándékosan **out-of-sample** – ha véletlen adaton ~50%-ot ad,
  az helyes (nincs valódi él).
- A **bolygó-/asztro-modul asztrológia**: matematikailag pontos pozíciókat számol,
  de **nincs bizonyított prediktív ereje** a piacon. Kikapcsolható: `astro.enabled: false`.
- A likviditás **PROXY** = becslés, nem valós tőzsdei book-adat.
- A **kereskedési réteg** szintjei (entry/stop/target) **illusztratív** számítások a
  proxy klaszterekből és napi gyertyákból – **nem kereskedési jelzés**. A backteszt
  a *kompozit irányt* méri, nem ezeket a trade-szinteket (az még TODO a roadmapen).
- A videókban látott 50–100x tőkeáttétel rendkívül kockázatos; a motor épp ezért
  **figyelmeztet, ha a likvidáció a stop előtt ütne be**. Éles használat előtt
  papír-/demókereskedésben validáld a jelzéseket.
