# ÁLLAPOT, TANULSÁGOK, NYITOTT TEENDŐK (élő dokumentum)

> Utolsó frissítés: **2026-11-24 11:40 (magyar idő)**. Minden új session ELŐSZÖR ezt olvassa,
> utána a HANDOVER.md-t. Minden munkamenet végén frissíteni + commitolni.
> A felhasználó kérése: **csak adat alapján** dolgozzunk, ne az ő véleménye alapján.

## 1. Mit validáltunk (ami működik és ami NEM)

| Eszköz / jel | Eredmény | Következmény |
|---|---|---|
| **Tömeg L/S (OKX számlaarány), kontrár** | Okt–nov során a **legmegbízhatóbb** jel. L/S 2,8–3,2 + emelkedő OI → −12% (nov. 5–14); L/S 2,6–2,8 esésbe vásárolva → nov. 23–24 lecsorgás | **Kemény kapu:** long csak ha L/S ≤ 2,3 (vagy likvidációs hullám + visszavétel) |
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
| Elnyelés (negatív CVD + stagnáló ár) | nov. 23 délelőtt → +5% kilövés | **bikás**, nem medvés (rosszul olvastam) |

## 2. Szabályok (a hibákból)

1. **Stop mindig a likvidációs csomó ALÁ / FÖLÉ, sosem bele, sosem kerek szám mellé.** (Nov. 24: a 59 800-as stop két long-csomó közé esett, 59 455-ig söpört és visszajött.)
2. **Belépés csak akkor, ha MINDEN feltétel teljesül.** „Majdnem” = stop-vadászat.
3. **Tőkeáttétel:** terv szerinti (5–10x); 20x esetén fél pozíció. Veszteség után kisebb méret.
4. **Részzárás a dokumentált ellenállásoknál**, stop break-evenre az első célnál.
5. **Egyszerre egy pozíció** — ellentétes jel nyitott pozíció mellett = figyelmeztetés, nem fordulás.
6. **Napi záró:** a motor OKX 16:00 UTC (17:00 HU), a TradingView 00:00 UTC (01:00 HU) — mindig mondd meg, melyikről van szó.
7. **Proxy-térkép kisöpört szintjei fantomok** — a Pine LiqMap és a liquidity.py még nem szűri (lásd TODO).

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

## 6. Nyitott teendők (prioritás szerint)

1. **L/S-kapu beépítése** a trade-logikába (long tiltva, ha L/S > 2,3 és OI nő) + visszateszt.
2. **Kisöpört szintek szűrése** a `liquidity.py`-ba és a Pine `liq_map.pine`-ba (szintenként, a pivot óta).
3. **OI-alapú likvidációs modul** (`engine/oimap.py`) — eddig csak ad-hoc szkriptben fut.
4. **Reversal-mód R:R-szűrő** (nov. 2 és 23: R:R 0,64–0,78-as tervet adott ki).
5. **Elnyelés-detektor** az OF-Suite értelmezésébe (negatív CVD + stagnáló ár = bikás).
6. **Opciós modul** (Deribit: max pain, nagy strike-ok lejáratonként) — ma derült ki, hogy kimaradt.
7. **Bányászati modul** (hashrate, hashprice, kikapcsolási sávok, hash ribbon).
8. **Makró-bemenet** (Nasdaq/ES): a nov. 23-i +7%-os NDX hajtotta a mozgást; a Stooq blokkolt.
9. **ETF-áramlás** forrás (farside blokkolt) — a 1,79 Mrd $ kiáramlás fontos volt.
10. **Binance/Bybit adat** csak a felhasználó gépéről érhető el (felhőből 451/403) — Remote Control.
11. Kompozit megjelölése „nem validált irány”-ként a dashboardon.
12. Teljes újravalidálás (walk-forward) — a stratégiák romlottak.
13. Coinbase-prémium és Anchored VWAP visszatesztje; Cipher B divergencia-teszt.
