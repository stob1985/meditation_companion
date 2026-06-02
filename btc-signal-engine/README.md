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
    liquidity.py        proxy likvidációs klaszterek
    signal.py           kompozit irány + adaptív súlyok + forecast
    dwell.py            dwell time / dwell block (idő-volumen-az-áron profil)
    trade.py            kereskedési réteg: entry/stop/target, R:R, méret, likvidáció
    backtest.py         OUT-OF-SAMPLE backteszt (train/test split)
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
Idő- és volumen-az-áron profil: **POC**, **value area**, és a magas-elidőzésű
**dwell blokkok** (acceptance zónák → erős támasz/ellenállás, fékezik a mozgást).
A `state` (COILING / TRENDING) jelzi, hogy az ár szűk sávban tekeredik-e
(kitörés előtt) vagy trendel. A trade réteg ezt használja a stop elhelyezéséhez.

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
| `trade.bet_usd` | fix tét / margin tradenként (USD) |
| `trade.leverage` | tőkeáttétel (10/25/50/100) |
| `trade.stop_buffer_atr` | stop puffer a struktúra mögött (ATR) |
| `dwell.lookback` / `bins` | profil hossza / ár-vödrök száma |
| `dwell.value_area_pct` | value area aránya (alap 0.70) |
| `dwell.block_pctile` | dwell percentilis a blokk-küszöbhöz |

---

## Roadmap (következő lépések)
- [ ] Valós likviditási adat opció (Coinglass / order-book) a proxy mellé
- [ ] Intraday session-detektor (Ázsia/London/NY) valós időbélyegekkel
- [x] Kereskedési réteg: belépő/cél/SL a klaszterekből, R:R ≥ 1:3, pozícióméret
- [x] „dwell time / dwell block" modul (a videók fő koncepciója)
- [x] Több-tőzsdés élő adat (OKX/Hyperliquid/Binance.US/Coinbase/Kraken) fallbackkel
- [ ] A trade réteg backtesztelése (entry/stop/target szimuláció a klasztereken)
- [ ] Walk-forward optimalizálás (az AUTO-OPT helyett, túlillesztés ellen)
- [ ] Pine: dwell blokkok + trade szintek megjelenítése
- [ ] HTML/web-dashboard a terminál helyett, riasztások (webhook)

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
