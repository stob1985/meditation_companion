# ÁLLAPOT, TANULSÁGOK, NYITOTT TEENDŐK (élő dokumentum)

> Utolsó frissítés: **2026-11-24 délután (magyar idő)** — a „hiányzó láncszemek” beépítése után. Minden új session ELŐSZÖR ezt olvassa,
> utána a HANDOVER.md-t. Minden munkamenet végén frissíteni + commitolni.
> A felhasználó kérése: **csak adat alapján** dolgozzunk, ne az ő véleménye alapján.

## 1. Mit validáltunk (ami működik és ami NEM)

| Eszköz / jel | Eredmény | Következmény |
|---|---|---|
| **Tömeg L/S (OKX számlaarány), kontrár** | OKX 1H, okt. 25–nov. 24 (720 óra, átfedő): **L/S > 2,6 → +72h −3,7%, 10% emelkedés**; 2,3–2,6 → semleges (+24h +0,6%, 55%); 2,0–2,3 → semleges. A 1,5–2,0 sáv is rossz volt (1 epizód). Félidők ellentmondanak, 1 hónap minta. | **CROWD GATE beépítve:** LONG tiltva L/S > 2,6; 2,3–2,6 között FÉL méret |
| Kompozit irány (engine/signal.py) | OOS irány-pontosság **45,7%**, PF 1,02 | NEM irányjelző; csak kontextus |
| Szint-belépő + részleges TP | +27% → **+12,1%** (36 trade, 36% nyerő) | Szerény, fogyó él; az R:R hozza |
| SWING réteg | −5,2%, 1/6 nyerő (2026) | jelenleg nem működik |
| Liquidity GRAVITY (A, élő) | **anti-jel** (DOWN/UP pontosság 23–24%) | nem dönt; csak kijelzés |
| Gravity C (decay90 + elhagyott pool) | stabil, de ~+4 pp él | kijelzésnek jobb, mint A |
| Gravity D (regime-kapu) | 62/82%, de a félidő-teszten bukik | figyelő mód |
| Likviditás-aszimmetria („fent több”) | 87k-sávban fent >1,5× → 10 napon 38% fel (alapráta 51%) | NEM irányjelző; HOL reagál az ár, nem MERRE |
| Nagy lenti pool elérése | 60 nap: 23% · 120 nap: 51% · **180 nap: 73%** (medián 81 nap); szinte soha nem ELSŐ (14–17%) | 3–6 hónapos célpont, nem rövid távú irány. **A 57–58k tézis (felhasználó) bejött ~5 hónap után.** |
| Cipher B / WaveTrend pontok | napi és 4H: nincs él (zöld pont 4H-n −2,1% / 38%) | csak kontextus |
| Cipher B pénzáramlás („follow the money”) | egyik állapot sem tér el az alaprátától | csak kontextus |
| RSI ≤ 18 (napi) | 3/3 rövid távú visszapattanó (+2…+11% 5–10 napon) | kevés minta |
| Medve-regime, ár 5–12%-kal a 60n mély fölött | új 60n mély 10n: 16%, 20n: 23%; +5% előbb, mint −5%: 77% (~9 epizód) | mean-reversion hajlam |
| Elnyelés (negatív CVD + stagnáló ár) | nov. 23 délelőtt → +5% kilövés (1 eset) | **bikás**; detektor beépítve (realflow.absorption, OF-Suite) — nem validált |
| **Kisöpört-szűrő a kereskedési szintekre** | szint-belépő: szűrés nélkül **+17,9% (34 trade, 41%)**, szűrve **−1,4% (6 trade, 0%)** | A fantom szintek S/R-ként MŰKÖDNEK → kereskedés: MINDEN szint; ÉLŐ lista csak a likviditás-térképre |
| Coinbase-prémium | 2 hónap, szinte mindig negatív; < −10 bp → +72h −2,15% (25%) vs −10…−3 bp → −0,41% (56%) | gyenge támogatás; pozitív fordulást nem lehetett tesztelni |
| AVWAP a 60 napos mélytől | fölötte +0,54% / 50%, alatta −0,47% / 49% (10 nap); „épp alá esett” → +0,77% / 58% | **NINCS él** — nov. 24-én tévesen kezeltem medvés jelként |
| Cipher B divergencia | napi n=2, 4H n=3–4 | eldönthetetlen (kevés minta) |
| Kompozit (újrafuttatva) | OOS 47,3%, PF 1,15, +41% nettó, max DD −55% | továbbra sem irányjelző |
| SWING (újrafuttatva) | −7,8%, 1/7 nyerő | nem működik |

## 2. Szabályok (a hibákból)

1. **Stop mindig a likvidációs csomó ALÁ / FÖLÉ, sosem bele, sosem kerek szám mellé.** (Nov. 24: a 59 800-as stop két long-csomó közé esett, 59 455-ig söpört és visszajött.)
2. **Belépés csak akkor, ha MINDEN feltétel teljesül.** „Majdnem” = stop-vadászat.
3. **Tőkeáttétel:** terv szerinti (5–10x); 20x esetén fél pozíció. Veszteség után kisebb méret.
4. **Részzárás a dokumentált ellenállásoknál**, stop break-evenre az első célnál.
5. **Egyszerre egy pozíció** — ellentétes jel nyitott pozíció mellett = figyelmeztetés, nem fordulás.
6. **Napi záró:** a motor OKX 16:00 UTC (17:00 HU), a TradingView 00:00 UTC (01:00 HU) — mindig mondd meg, melyikről van szó.
7. **Kétféle szint-térkép:** kereskedéshez MINDEN szint (validált S/R); a „hol van vadászható likviditás” kérdéshez az ÉLŐ lista (kisöpört nélkül).
8. **Market-reversal csak R:R ≥ 2-vel** (`trade.reversal_rr_min`).

## 3. Trade-napló (felhasználó)

| Dátum | Irány | Belépő | Kiszállás | Tőkeáttétel | Eredmény | Megjegyzés |
|---|---|---|---|---|---|---|
| 2026-11-22 | LONG | 59 700 | ~63 500–64 000 (nov. 23 délután) | 20x | ≈ +127…+144% a fedezeten | terv: stop BE fölé, részzárás ellenállásnál; Huang-hír kilövés |
| 2026-11-24 | LONG | 60 400 | 59 800 (stop) | ? | ≈ −1% ár (10x: −10%) | **feltételek nem teljesültek** (L/S 2,8); stop a csomók közé esett |

## 4. Piaci állapot és tervek (2026-11-24 11:40)

- Ár ~59 800. Éves mély **55 134** (nov. 21). ATH 126 200 (2025-10-06), −52%. Heti regime BEAR.
- L/S 2,52 · OI 24h −3,3% · Coinbase-prémium −78 $ · USDT.D risk-off · Nasdaq futures esnek.
- Elveszett: AVWAP az aljtól (~60,4–60,7k), napi VWAP.
- OI-modell long-likviditás lent: **58,0–59,0k (38M $)**, 57,0–58,0k (22M), rés 56–57k, **55,0–55,5k (24M)**.
- Fib (55 134→64 600): 61,8% = 58 750 · 78,6% = 57 160.

**Long-terv:** 60% @ 58 100 · 40% @ 57 200 · stop **56 400** (a résben) · T1 60 650 · T2 62 900 · 5x.
Feltétel: L/S ≤ 2,3 VAGY likvidációs hullám + 1H záró vissza a zóna fölé, ÉS 1H WaveTrend zöld kereszt −53 alatt.
Ha 4H záró 56 400 alatt: lesöprés-long az éves mélynél (visszavétel 55 134 fölé, ~55 300, stop 53 900).

**Short-tervek:** visszateszt 60 400–60 700 (stop 61 300, célok 58 600 / 57 600) · felső zóna 66 800–67 600 (stop 68 600).

## 5. Naptár / események (ami eddig kimaradt)

| Mikor | Esemény | Miért számít |
|---|---|---|
| ~nov. 25–26 | **Nehézség-igazítás kb. +8,5%** | a bányászok önköltsége ~8%-kal nő (flotta-átlag kikapcsolási ára ~55k → ~60k) |
| **nov. 26 (csüt.)** | **Hálaadás** — USA tőzsdék zárva | vékony likviditás, nincs ETF-áramlás |
| **nov. 27 (pén.)** | **Havi opciós lejárat (Deribit 09:00 HU): ~112k BTC (~6,7 Mrd $)**, max pain 72k, put/call 0,91 · CME-lejárat · USA félnap | volatilitás a lejárat körül |
| dec. 4 (pén.) | lejárat: **58k put 6 642 BTC** (a legnagyobb strike) | **58k opciós csatatér** = egybeesik a long-zónával |
| nov. 30 (hétfő) | havi gyertya zárása (november a legrosszabb hónap az adatsorban, −26%) | |
| dec. 25 (pén.) | negyedéves lejárat: ~163k BTC, max pain 72k, nagy put 60k (6 880) | |

## 6. Teendők állapota (2026-11-24)

**KÉSZ:**
- ✅ CROWD GATE (`trade.crowd_gate`, config `trade.crowd_gate`) — adat alapján hangolva (2,6 / 2,3)
- ✅ ÉLŐ likviditás-nézet (`liquidity.build` → `live_above/live_below`) + Pine LiqMap kapcsoló (alap: KI, mert a szűretlen a validált S/R)
- ✅ OI-alapú likvidációs modul: `engine/oimap.py` (dashboard: OI-ALAPÚ LIKVIDÁCIÓS TÉRKÉP)
- ✅ Reversal R:R-alsó határ (`trade.reversal_rr_min: 2.0`)
- ✅ Elnyelés-detektor: `realflow.absorption` + OF-Suite „Elnyelés (z)” sor és riasztás
- ✅ Opciós modul: `engine/options.py` (Deribit: lejáratok, max pain, P/C, csatatér-strike-ok)
- ✅ Bányászati modul: `engine/mining.py` (hashrate, hashprice, nehézség, kikapcsolási árak, hash ribbon)
- ✅ Makró: `macro.py` Yahoo-forrással (Stooq tartalék) + élő NQ/ES határidők
- ✅ Coinbase-prémium: `realflow.coinbase_premium`
- ✅ Binance (top trader/számla L/S, OI) és Bybit L/S: `realflow.binance_crowd/bybit_crowd` — **csak helyi gépen** (felhőből 451/403)
- ✅ Kompozit „NEM validált irány” jelölés a dashboardon
- ✅ Újravalidálás: L/S, Coinbase-prémium, AVWAP, Cipher-divergencia, szint-belépő, swing, kompozit (lásd 1. pont)

**MÉG NYITOTT:**
1. **ETF-áramlás:** farside Cloudflare mögött (403) — felhőből nem érhető el; helyi gépen az `etfflow.py` működhet.
2. **Binance/Bybit adat** a te gépedről (Remote Control) — a kód kész, csak a futtatási hely kell.
3. A CROWD GATE hosszabb távú validálása (OKX csak ~30 nap 1H L/S-t ad; a napi adat 180 napos).
4. trap_watch backteszt · walk-forward súly-optimalizálás · SWING réteg újragondolása.
