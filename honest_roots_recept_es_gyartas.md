# Honest Roots — Gyártói specifikáció (recept) + Hol gyártsd le
### Női hajegészség-kiegészítő · Nutrafol-alternatíva · Készen ajánlatkéréshez (RFQ)

> ⚠️ **Fontos:** Ez egy fejlesztési/koncepció-specifikáció. A végleges receptet, segédanyagokat, túladagolásokat és a stabilitást egy **képzett formulátor + bérgyártó** validálja. Forgalomba hozatal előtt **regulációs bejelentés** kell (HU: OGYÉI). Az állítások csak „structure/function" jellegűek lehetnek — gyógyhatás tilos.

---

# A RÉSZ — A RECEPT (Master Manufacturing Specification)

**Termék:** Honest Roots Women's Core
**Adagforma:** napi 1 adag = **2 db softgel (olajos hatóanyagok) + 1 db kemény kapszula (porok)**
**Kiszerelés:** 90 egység/doboz (60 softgel + 30 kapszula) = **30 napra**

## A.1 — SOFTGEL összetétel (olajok) — 2 db/nap

| # | Hatóanyag | Nyersanyag-spec / grade | mg / softgel | mg / nap (2 db) |
|---|---|---|---|---|
| 1 | Saw palmetto kivonat | CO₂-extrakt, **85–95% szabad zsírsav (FFA)**, olaj | 160 | **320** |
| 2 | Tökmagolaj | hidegen sajtolt, std. fitoszterol | 200 | **400** |
| 3 | Tokotrienol-komplex | pálma (pl. Tocomin/EVNol **50%**) → 25 mg tokotrienol/db | 50 | **100** (= 50 mg tokotrienol) |
| 4 | Vivőolaj | MCT vagy magas-oleinsavú napraforgóolaj | ~90 | q.s. |
| 5 | Antioxidáns | kevert tokoferolok (oxidáció ellen) | ~5 | — |
| | **Töltet összesen** | | **~505 mg** | méret ~7–8 oblong |
| | **Héj** | marha-zselatin + glicerin + tisztított víz (vagy vegán: módosított keményítő/karragén) | | |

## A.2 — KEMÉNY KAPSZULA összetétel (porok) — 1 db/nap

| # | Hatóanyag | Nyersanyag-spec / grade | Címke-dózis | Beadott mennyiség* |
|---|---|---|---|---|
| 1 | L-Cisztein | L-cisztein (HCl monohidrát) — **NEM NAC** | 200 mg | ~200 mg |
| 2 | C-vitamin | aszkorbinsav | 90 mg | ~100 mg (+10% túladag) |
| 3 | Cink | **biszglicinát kelát** (~20% elemi Zn) | 15 mg | ~75 mg só |
| 4 | Réz | biszglicinát (~13% elemi Cu) | 1 mg | ~7,7 mg só |
| 5 | Szelén | L-szelenometionin premix (0,5% Se) | 55 mcg | ~11 mg premix |
| 6 | D3-vitamin | kolekalciferol trituráció (100 NE/mg) | 1000 NE (25 mcg) | ~10 mg premix (+30% túladag) |
| 7 | Biotin | D-biotin 1% trituráció | 300 mcg | ~30 mg premix |
| 8 | Csúsztató/töltő | szerves rizshéj-koncentrátum | — | q.s. ~550 mg-ra |
| 9 | Csomósodásgátló | szilícium-dioxid | — | ~5 mg |
| | **Töltet összesen** | | | **~550 mg**, 00-ás **vegán kapszula (hipromellóz)** |

\* A mikrodózisú vitaminok/ásványok standardizált premixből mennek; a D3/biotin/C eltarthatósági **túladagolást** kap.

## A.3 — OPT-IN ADD-ON kapszulák (külön SKU, nem alap)

| Add-on | Nyersanyag | Címke-dózis | Megjegyzés |
|---|---|---|---|
| Ashwagandha | Sensoril, ≥10% withanolid | **125 mg** | stresszhullás; máj-/pajzsmirigy-figyelmeztetéssel, opcionális |
| Vas | ferro-biszglicinát (~20% Fe) | **9 mg** elemi (≈45 mg só) | csak igazolt alacsony ferritinnél; pajzsmirigy-gyógyszertől 4 órára elkülönítve |

## A.4 — "Collagen+" tasak (külön termék)

| Hatóanyag | Dózis / adag |
|---|---|
| Hidrolizált kollagén-peptid (Verisol-grade bioaktív) | **2,5 g** (generikusnál ~5 g) |
| C-vitamin | 40 mg |
| Szilícium (bambusz-kivonat 70% SiO₂ vagy ch-OSA) | 5–10 mg Si |

---

## A.5 — Pilot batch nyersanyaglista (BOM) — 1.000 dobozra (= 30.000 adag)

> Egységdarab: **60.000 softgel + 30.000 kapszula** / 1.000 doboz.

| Hatóanyag | kg / 1.000 doboz | kg / 5.000 doboz |
|---|---|---|
| Saw palmetto (85–95% FFA) | 9,6 | 48,0 |
| Tökmagolaj | 12,0 | 60,0 |
| Tokotrienol-komplex 50% | 3,0 | 15,0 |
| L-cisztein HCl | 6,0 | 30,0 |
| C-vitamin (aszkorbinsav) | ~3,0 | ~15,0 |
| Cink-biszglicinát | 2,25 | 11,25 |
| Réz-biszglicinát | 0,23 | 1,15 |
| Szelén-premix (0,5%) | 0,33 | 1,65 |
| D3-premix | ~0,30 | ~1,50 |
| Biotin 1% trituráció | 0,90 | 4,50 |
| Vivőolaj / tokoferol / rizshéj / SiO₂ | q.s. | q.s. |

**⚠️ MOQ-valóság:** a softgel-gyártás minimum sorozata jellemzően **100.000–250.000 db** (≈ 1.700–4.200 doboz). Egy reális első sorozat ezért inkább **2.000–4.000 doboz**, vagy keress alacsony-MOQ-s gyártót.

## A.6 — Minőségi követelmények (ezt írd a gyártói szerződésbe)
- Sarzsonkénti **COA** (azonosság + hatóanyag-tartalom).
- **Nehézfém-panel:** As / Pb / Cd / Hg (különösen a botanikumokra és a halból eredő hatóanyagokra).
- **Mikrobiológia** (összcsíraszám, E. coli, Salmonella, élesztő/penész).
- **Stabilitási teszt** (min. 6 hó gyorsított) — az olajok **oxidációs indexe** (peroxidszám) kulcskérdés.
- **Túladagolási terv** a vitaminokra (eltarthatóság végéig tartsa a címkeértéket).
- Nitrogén-öblítés / antioxidáns a softgelekhez (avasodás ellen).

---

# B RÉSZ — HOL TUDOD LEGYÁRTATNI

Mivel a Vitalo magyar/EU bolt, az **EU-s utat** javaslom (logisztika, notifikáció, fogyasztói bizalom).

## B.1 — A gyártó típusa
| Forma | Mit kapsz | Neked |
|---|---|---|
| **White/Private label** | Kész alapreceptre a márkád. Olcsó, gyors, de nem a mi egyedi receptünk. | csak gyors teszthez |
| **Custom / Contract Manufacturing (CMO)** | A **mi receptünket** gyártják. | ✅ EZ KELL |

## B.2 — Kötelező követelmények a gyártónál (szűrőkérdések)
- **EU GMP** + **ISO 22000 / FSSC 22000** + **HACCP**
- Tud **softgelt ÉS kapszulát** is (vagy két specialista + közös „kit"-csomagolás)
- Sarzsonkénti **COA**, **nehézfém-vizsgálat**, **stabilitási teszt**
- Vállalja a **regulációs dokumentációt** (vagy ajánl tanácsadót)

## B.3 — Hol találsz gyártót
1. **Szakvásár (a leggyorsabb):** **Vitafoods Europe** (Barcelona) és **SupplySide / Hi&Fi Europe** — egy nap alatt 50 EU-s CMO.
2. **EU softgel-specialisták** (saw palmetto/tökmagolaj softgelhez): pl. **EuroCaps (UK)**, **Procaps**, **Catalent**, **Captek**, plus német/holland/lengyel/spanyol bérgyártók.
3. **EU kapszula-/porkeverék private label:** német, holland, lengyel és **magyar** bérgyártók — kérj ajánlatot 3–4 helyről (MOQ + ár + tanúsítványok összevetése).
4. **Alacsonyabb MOQ / olcsóbb:** Alibaba-n ázsiai GMP-gyártók — **csak alapos auditálással** (GMP-tanúsítvány, EU-import megfelelőség, harmadik fél tesztje). Olcsóbb, de nagyobb a megfelelőségi kockázat.

## B.4 — EU / magyar szabályozás (más, mint az USA!)
- A táplálékkiegészítő itt **élelmiszer** (2002/46/EK irányelv) — nem „supplement" az FDA szerint.
- **Bejelentés Magyarországon:** forgalomba hozatal előtt **OGYÉI**-notifikáció (terméklap + címke). Intézi a gyártó/forgalmazó vagy egy regulációs tanácsadó.
- **Botanikumok (saw palmetto stb.):** EU-ban engedélyezettek étrend-kiegészítőként; a **címkeállítások szigorúak**. Engedélyezett EFSA-állítások pl.: cink/szelén/biotin „a normál haj fenntartásához hozzájárul". **Gyógyhatás tilos.**
- **Terhességi figyelmeztetés** a saw palmetto miatt kötelező a címkén.

## B.5 — Nagyságrendi költségek (irány)
- **Pilot sorozat (egyszeri):** formuláció + sorozat + tesztek ≈ **€15.000–40.000** előzetes ráfordítás.
- **Gyártott önköltség:** reálisan **~$25–40/doboz** induló volumenen (két dózisforma!), skálázva csökken → ezért a javasolt ár **$45/hó**.

## B.6 — Cselekvési terv (lépésről lépésre)
1. Véglegesítsd ezt a specifikációt egy formulátorral (dózis-illesztés, segédanyagok, túladagolás).
2. Küldd ki az **RFQ-t** (lent) 3–4 EU CMO-nak.
3. Hasonlítsd: MOQ, ár/doboz, átfutás, tanúsítványok, stabilitás.
4. Rendelj **mintát + COA-t** a nyertestől, mielőtt a teljes sorozatot megrendeled.
5. Intézd az **OGYÉI-bejelentést** és a végleges címkét (regulációs tanácsadóval).
6. Indítsd a stabilitási tesztet; a kész sarzs COA-ját töltsd fel a termékoldalra (QR).

---

# C RÉSZ — RFQ (ajánlatkérő) e-mail sablon

**Tárgy:** RFQ – Custom hair-wellness supplement (softgel + capsule), EU GMP

> Hello [Manufacturer],
>
> We are launching a women's hair-wellness supplement (EU/Hungary market) and are looking for an **EU GMP / ISO 22000** contract manufacturer for a **custom formulation** in two dose forms: **softgels (oils)** and **vegetable capsules (powders)**, packaged together (90 units/bottle, 30-day supply).
>
> Please quote for **2,000 and 5,000 bottles**, including:
> 1. Price per bottle (formulation + encapsulation + bottling + label application)
> 2. **MOQ** for softgels and for capsules
> 3. Lead time
> 4. Certifications (GMP, ISO 22000/FSSC, HACCP), per-batch **COA**, **heavy-metal** testing (As/Pb/Cd/Hg), and **6-month accelerated stability**
> 5. Whether you can support **EU food-supplement labelling / notification** documentation
>
> Formula (per daily serving = 2 softgels + 1 capsule):
> *Softgel:* Saw palmetto CO₂ extract (85–95% FFA) 320 mg · Pumpkin seed oil 400 mg · Tocotrienol complex 100 mg.
> *Capsule:* L-Cysteine 200 mg · Vitamin C 90 mg · Zinc bisglycinate (15 mg Zn) · Copper bisglycinate (1 mg Cu) · Selenium 55 mcg · Vitamin D3 1000 IU · Biotin 300 mcg.
>
> NDA available on request. Thank you!
> [Your name / Vitalo]

---

*Készült dinamikus multi-agent workflow eredményéből (review-kutatás → összetevő-tudomány → formuláció → reguláció → adverszariális red-team). A dózisok, biztonsági határok és regulációs pontok az al-ágens-jelentésekben forrásolva; kereskedelmi használat előtt elsődleges forrásból ellenőrizendő.*
