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
| **B-terv: lesöprés-long a 60n/éves mélynél** (OKX 4H 2021-11–2026-11; trigger: 4H záró < mély+0,85%) | Odajutás (medve, 5–9%-kal a mély fölött, 15 epizód): 10 nap 30%, 20 nap 40%. Trigger után medvében **10/10** a mély alá megy; **mélység medián −9,7%**, 75%: −13,4%, 90%: −15,5%. Visszavétel-long, stop −2,24%: medve 4 T1 / 3 stop, **+0,08R**; mély alatti stop / mélyebb söprés / −10%-os limit sem jobb | **NINCS él** — a 53 900-as stop a tipikus söprés-mélységen belül van. B-terv lefokozva figyelésre |
| Hálaadás (8 év) | 3/8 év ≥2× range, mind esés (−6…−9%); 2022–25: mindkét nap a szokásosnál nyugodtabb | nem konzisztens |

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
| 2026-11-26 | SHORT | 60 700 (~06:30 HU) | kiszállási szabály: 1H záró 61 744 (nov. 27. 07:00 HU) · hard stop 62 000 (csúcs 62 028, 08:00 HU előtt) | ? | ≈ −1,7…−2,1% ár | **TANULSÁG: belépés, amikor a fő feltétel (L/S > 2,6) már nem állt (2,57) → a 2. szabály megszegése.** A watcher jelzett (ntfy; Telegram még nem volt beállítva). | Az A-terv triggere 01 UTC-kor teljesült (wick 61 620, záró 60 504, L/S 2,77). A belépéskor viszont az L/S már 2,57 volt (< 2,6 → a validált él megszűnt). Hard stop 62 000, kiszállás 1H záró > 61 700 esetén |

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

**Frissítés 13:25 HU:** ár ~60 300, 10–11 UTC között söprés 59 366-ig és visszavétel. L/S (OKX ccy=BTC, ezt nézi a kapu) 2,58–2,59 → épp a 2,6-os határ alatt = FÉL méret sáv.
OKX OI 2 órán át +1,3%, lapos ár mellett (új shortok nyílnak). Funding +0,005% (előtte −0,0005%). Coinbase-prémium −82 $ (−13,7 bp).
NQ határidős +1,7%. TV: ±5%-on belül nincs cluster; lenti mágnes 57,0–58,1k, fenti 66,7k. A tervek változatlanok.

**2026-11-25 07:00 HU:** ár ~59 070, az előző napi mély (59 260) alatt, a VWAP/VAL alatt. A taktikai short feltétele nov. 24-én 14 UTC-kor teljesült (zóna 60 558, záró 59 988), a T1 58 600 még nincs meg.
L/S 2,64 → LONG TILTVA. OI lapos, funding +0,0065%. Coinbase-prémium −14,6 bp. NQ −3,7%/24h. Hash ribbon: KAPITULÁCIÓ (nem validált).
A lenti térkép lejjebb került: motor 57 322 (x14), 5 tőzsde 57 305 (x70), TV 56 448 (x74); OI-modell ±2%: lent 42M vs fent 1M.
**ÚJ long-terv:** 60% @ 57 300 · 40% @ 56 500 · stop **55 600** (a régi 56 400-as stop a TV 56 448-as csomójába esne → 1. szabály) · T1 60 000 · T2 62 900. Feltételek változatlanok.
A felhasználó shortja (limit 60 700) NEM teljesült (csúcs 60 666) → tanulság: zónában skálázva (fele 60 450, fele 60 650), ne a zóna szélén.
**USA-adatnap mérés (OKX 1H, szept. 23–nov. 25, hétköznap, n=44):** a 13–16 UTC (14–17 HU) ablak 36%-ban emelkedett, átlag −0,31%, átlagos |mozgás| 1,04%. Az órás range 14–15 UTC-kor 1,22% (Ázsiában ~0,55%). Regime-függő, nem validált szabály.
**2026-11-25 15:25 HU (forró USA-infláció után):** 13:30 UTC-kor esés 58 824 → 57 923 (OKX perp), most ~58 400. 24h long-söprés 29 → 70M$ (az 58,5/58,0k csomók elfogytak).
Utána a taker-vétel erősebb, az OI +20M$ az árral együtt (dip-vevők). L/S 2,60–2,62 → a tömeg NEM kapitulált. NQ −3,8%, ES −2,2%, USDT.D +19 bp.
1H WT −70,6 / −66,5, zöld kereszt még nincs. (Reggel 08 UTC-kor volt egy −58,6-os zöld kereszt 59 422-n, utána −1,8% → a WT önmagában nem elég.)
Lenti térkép megint lejjebb: motor 57 073 (x12), 5 tőzsde 57 034 (x59), TV 56 073 (x64).
**Long-terv újraszintezve:** 60% @ 57 100 · 40% @ 56 200 · stop 55 600 (az éves mély fölött) · T1 59 250 (előző napi mély) · T2 61 400 (POC) · 5x.
**15:45 HU:** második hullám (NQ −4,5%), ár 57 458, mély 57 258 (OKX perp); az 57 100-as belépő még nem teljesült. L/S 2,62 → **2,55** (< 2,6 → FÉL méret engedélyezett).
OI 20 perc alatt −2,1% → long-tőkeáttétel leépül. 24h long-söprés 96M$; az 57,0k-s bin elfogyott, lent 56,0k 11M, 55,0–55,5k 33M. TV legközelebbi LENT 55 413 (x48).
WT 1H −74,8 / −67,5 (esik, nincs kereszt). Coinbase −16,9 bp, USDT.D +31 bp.
Stop marad 55 600: ha az ár eléri az 55,1–55,6k zsebet, a trigger-statisztika (medvében 10/10 alámegy) szerint az 55 029-es stop is kiüt → a szorosabb stop ugyanakkora találati esély mellett kisebb veszteség.
**16:03 HU:** mély 57 258 (14:45 UTC), az 57 100-as belépő NEM teljesült (158 pont). Visszapattanás 58 711-ig, most ~58 380.
L/S 2,55 → **2,74** (a tömeg visszavásárolt), OI +2,3% az árral → új longok. LONG TILTVA, a limitet vissza kell vonni, amíg L/S > 2,6.
15m WT zöld kereszt −62-nél; 1H még nincs (−70,3 / −69,0).
Taktikai short opció: 58 800–59 260 elutasítás + L/S > 2,6 → stop 59 800, T1 57 300, T2 56 100 (nem validált szint; az irány a validált L/S-jelből jön).
**18:36 HU:** a taktikai short trigger 17 UTC-kor teljesült (zóna 58 987, 1H záró 58 589, L/S 2,74). Utána felfutás 59 783-ig (a stop 59 800, 17 ponton múlt), most 59 471 → a short −1,5%.
L/S **2,91** (a minta legmagasabb értékei), OI +2,9% az árral → új longok. 1H WT zöld kereszt 16 UTC-kor −66,7-nél, de az ár nem érte el a long-zónát, és a kapu tilt. Coinbase −11,4 bp.
**18:40 HU – TERV (a felhasználó nincs pozícióban):** ár 59 570, napi H/L 59 801 / 57 258, napi VWAP 58 684.
OI-modell: ±2% lent 0 (a longok kisöpörve, 24h 92M$), fent 6,9M; ±5% fent 39,8M vs lent 10,8M → a közeli üzemanyag most FENT van (60–62,5k).
L/S 2,92, OI emelkedik → a validált jel lefelé mutat (72 óra), de előbb felfelé szorítás valószínű.
Motor új napi gyertyával: BUY 55 481–56 476 (x24, friss), 5 tőzsde 57 354 (x92).
- **A) Short (fő terv):** belép a 60 800–61 700 sávba, 1H záró vissza 60 800 alá, L/S > 2,6 → stop 62 000 · T1 58 700 · T2 57 350.
- **B) Short:** 62 000–62 500-ig söpör, 1H záró vissza 61 700 alá → stop 62 900 · T1 58 700 · T2 57 350.
- **C) Long:** 60% @ 57 350 · 40% @ 56 450 · stop 55 600 · T1 59 800 · T2 61 700 — csak ha L/S ≤ 2,6.
**2026-11-26 06:40 HU – belépési triggerek** (ár ~60 900, L/S 2,57):
- **S1 short:** söprés 61 500–62 300 → 1H záró < 61 500, L/S > 2,6 · stop 62 900 · T1 58 700 · T2 57 350.
- **S2 short:** 1H záró < 60 100, L/S > 2,6 · stop 61 100 · T1 58 700 · T2 57 350.
- **S3 short:** 64 500–67 700-as nagy sáv, elutasítás · stop 68 700.
- **L1 long:** 57 350 / 56 450 · stop 55 600 · L/S ≤ 2,6 (≤ 2,3 teljes méret) + megerősítés.
- **L2 long (nem validált, fél méret):** 1H záró > 61 700, visszateszt tart · stop 60 800 · T1 64 500 · T2 66 700.
**Nyitott taktikai short kezelése:** stop 60 750-re (a zóna és a tegnapi csúcs 60 666 fölé), T1 58 600-nál 50% + BE.

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

- ✅ **Óránkénti figyelő:** `watch.py` + `watch_levels.yaml`. Ütemezett feladat „BTC belépő-figyelő (óránként)”, trigger `trig_01V1CZ4p1Z8BTX73CNbhpA1y`, cron `3 * * * *` UTC, minden futás friss session, push + e-mail értesítés.
  **Tökéletes-szűrő:** Telegram/ntfy belépő-üzenet CSAK akkor megy, ha minden pont teljesül.
  KÖTELEZŐ: tömegkapu (validált), R:R ≥ 2, nincs ellentétes pozíció (5. szabály), nincs esemény-ablak, validált setup-típus (az L2 nem az).
  MEGERŐSÍTŐ: Coinbase-prémium (short < −10 bp / long ≥ −10 bp), elnyelés-detektor nem ellene, regime (shortnál: medvében 5–12%-kal a 60n mély fölött = ELLENE).
  **Nov. 27-től a felhasználó kérésére CSAK ideális („tökéletes”) belépőre megy üzenet;** a pozíciókezelési üzenetek ki vannak kapcsolva (`position: null`). MINTA: `WATCH_SAMPLE=S1 python3 watch.py [--send]`.
  Telegram: @Btcriasztasbot, chat id 1710773583. A tokent a felhasználó teszi be a környezet változói közé (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID). SOHA ne commitold.
  **A szintek változásakor a `watch_levels.yaml`-t frissíteni + pusholni kell**, a figyelő mindig a branch legfrissebb állapotát olvassa. A nyitott pozíciót a `position:` blokk írja le (null, ha nincs).

**MÉG NYITOTT:**
1. **ETF-áramlás:** farside Cloudflare mögött (403) — felhőből nem érhető el; helyi gépen az `etfflow.py` működhet.
2. **Binance/Bybit adat** a te gépedről (Remote Control) — a kód kész, csak a futtatási hely kell.
3. A CROWD GATE hosszabb távú validálása (OKX csak ~30 nap 1H L/S-t ad; a napi adat 180 napos).
4. trap_watch backteszt · walk-forward súly-optimalizálás · SWING réteg újragondolása.
