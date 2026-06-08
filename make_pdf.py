#!/usr/bin/env python3
from fpdf import FPDF
from fpdf.fonts import FontFace

GREEN = (16, 48, 46)
GREEN2 = (28, 75, 70)
WARN_BG = (255, 244, 242)
WARN_BORDER = (192, 88, 74)
WARN_TXT = (90, 31, 23)
ROW_ALT = (242, 247, 246)
HEAD = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=GREEN)

F = "/usr/share/fonts/truetype/dejavu/"

pdf = FPDF(format="A4", unit="mm")
pdf.set_margins(16, 15, 16)
pdf.set_auto_page_break(True, margin=15)
pdf.add_font("dvs", "", F + "DejaVuSans.ttf")
pdf.add_font("dvs", "B", F + "DejaVuSans-Bold.ttf")
pdf.add_font("dvs", "I", F + "DejaVuSans-Oblique.ttf") if False else None
pdf.add_font("dvm", "", F + "DejaVuSansMono.ttf")
pdf.set_font("dvs", "", 10)
pdf.add_page()
EPW = pdf.epw

def h1(t):
    pdf.set_font("dvs", "B", 16); pdf.set_text_color(*GREEN)
    pdf.multi_cell(0, 7, t, new_x="LMARGIN", new_y="NEXT"); pdf.ln(1)

def sub(t):
    pdf.set_font("dvs", "", 9.5); pdf.set_text_color(58, 90, 87)
    pdf.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT"); pdf.ln(2)

def h2(t):
    pdf.ln(3); pdf.set_font("dvs", "B", 13); pdf.set_text_color(*GREEN)
    pdf.multi_cell(0, 6.5, t, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y(); pdf.set_draw_color(*GREEN); pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, y, pdf.l_margin + EPW, y); pdf.ln(2.5)

def h3(t):
    pdf.ln(1.5); pdf.set_font("dvs", "B", 11); pdf.set_text_color(*GREEN2)
    pdf.multi_cell(0, 5.5, t, new_x="LMARGIN", new_y="NEXT"); pdf.ln(0.5)

def para(t, size=10):
    pdf.set_font("dvs", "", size); pdf.set_text_color(26, 42, 40)
    pdf.multi_cell(0, 5, t, new_x="LMARGIN", new_y="NEXT", markdown=True); pdf.ln(1)

def small(t):
    pdf.set_font("dvs", "", 8.5); pdf.set_text_color(107, 127, 124)
    pdf.multi_cell(0, 4.2, t, new_x="LMARGIN", new_y="NEXT", markdown=True); pdf.ln(1)

def bullets(items, size=9.5):
    pdf.set_font("dvs", "", size); pdf.set_text_color(26, 42, 40)
    for it in items:
        pdf.set_x(pdf.l_margin + 2)
        pdf.multi_cell(0, 5, "•  " + it, new_x="LMARGIN", new_y="NEXT", markdown=True)
    pdf.ln(1)

def warn(t):
    pdf.ln(1); pdf.set_font("dvs", "", 9.2)
    x0, y0 = pdf.get_x(), pdf.get_y()
    pdf.set_fill_color(*WARN_BG); pdf.set_draw_color(*WARN_BORDER); pdf.set_line_width(0.3)
    pdf.set_text_color(*WARN_TXT)
    pdf.multi_cell(EPW, 5, t, border=1, fill=True, new_x="LMARGIN", new_y="NEXT", markdown=True, padding=2.5)
    pdf.ln(2)

def table(rows, widths, aligns=None, fontsize=8.6, header=True):
    pdf.set_font("dvs", "", fontsize)
    aligns = aligns or ["LEFT"] * len(widths)
    wmm = [EPW * w for w in widths]
    with pdf.table(col_widths=[w*100 for w in widths], text_align=aligns,
                   headings_style=HEAD, markdown=True, line_height=4.6,
                   borders_layout="SINGLE_TOP_LINE", first_row_as_headings=header,
                   cell_fill_color=ROW_ALT, cell_fill_mode="ROWS") as t:
        for r in rows:
            row = t.row()
            for c in r:
                row.cell(str(c))
    pdf.ln(2)

# ---------------- CONTENT ----------------
h1("Honest Roots — Gyártói specifikáció (recept) + Hol gyártsd le")
sub("Női hajegészség-kiegészítő · Nutrafol-alternatíva · Készen ajánlatkéréshez (RFQ)")
warn("**FIGYELEM:** Ez fejlesztési/koncepció-specifikáció. A végleges receptet, segédanyagokat, túladagolásokat és a stabilitást egy képzett formulátor + bérgyártó validálja. Forgalomba hozatal előtt regulációs bejelentés kell (HU: OGYÉI). Az állítások csak „structure/function\" jellegűek lehetnek — gyógyhatás tilos.")

h2("A RÉSZ — A RECEPT (Master Manufacturing Specification)")
para("**Termék:** Honest Roots Women's Core    |    **Adagforma:** napi 1 adag = 2 db softgel (olajok) + 1 db kemény kapszula (porok)    |    **Kiszerelés:** 90 egység/doboz (60 softgel + 30 kapszula) = 30 napra")

h3("A.1 — SOFTGEL összetétel (olajok) — 2 db/nap")
table([
 ["#","Hatóanyag","Nyersanyag-spec / grade","mg/softgel","mg/nap (2db)"],
 ["1","Saw palmetto kivonat","CO2-extrakt, **85–95% szabad zsírsav (FFA)**, olaj","160","**320**"],
 ["2","Tökmagolaj","hidegen sajtolt, std. fitoszterol","200","**400**"],
 ["3","Tokotrienol-komplex","pálma (Tocomin/EVNol **50%**) → 25mg/db","50","**100** (=50mg tokotr.)"],
 ["4","Vivőolaj","MCT vagy magas-oleinsavú napraforgóolaj","~90","q.s."],
 ["5","Antioxidáns","kevert tokoferolok (oxidáció ellen)","~5","—"],
 ["","**Töltet össz.** (~7–8 oblong softgel)","","**~505 mg**",""],
], [0.05,0.28,0.39,0.14,0.14], ["CENTER","LEFT","LEFT","RIGHT","RIGHT"])
para("**Héj:** marha-zselatin + glicerin + tisztított víz (vagy vegán: módosított keményítő/karragén).", 9)

h3("A.2 — KEMÉNY KAPSZULA összetétel (porok) — 1 db/nap")
table([
 ["#","Hatóanyag","Nyersanyag-spec / grade","Címke-dózis","Beadott*"],
 ["1","L-Cisztein","L-cisztein (HCl monohidrát) — **NEM NAC**","200 mg","~200 mg"],
 ["2","C-vitamin","aszkorbinsav","90 mg","~100 mg (+10%)"],
 ["3","Cink","**biszglicinát kelát** (~20% Zn)","15 mg","~75 mg só"],
 ["4","Réz","biszglicinát (~13% Cu)","1 mg","~7,7 mg só"],
 ["5","Szelén","L-szelenometionin premix (0,5% Se)","55 mcg","~11 mg"],
 ["6","D3-vitamin","kolekalciferol trituráció (100 NE/mg)","1000 NE (25 mcg)","~10 mg (+30%)"],
 ["7","Biotin","D-biotin 1% trituráció","300 mcg","~30 mg"],
 ["8","Csúsztató/töltő","szerves rizshéj-koncentrátum","—","q.s. ~550mg-ra"],
 ["9","Csomósodásgátló","szilícium-dioxid","—","~5 mg"],
 ["","**Töltet össz.** — 00-ás **vegán kapszula (hipromellóz)**","","**~550 mg**",""],
], [0.05,0.18,0.40,0.21,0.16], ["CENTER","LEFT","LEFT","LEFT","LEFT"])
small("* A mikrodózisú vitaminok/ásványok standardizált premixből mennek; a D3/biotin/C eltarthatósági túladagolást kap.")

h3("A.3 — OPT-IN ADD-ON kapszulák (külön SKU, nem alap)")
table([
 ["Add-on","Nyersanyag","Címke-dózis","Megjegyzés"],
 ["Ashwagandha","Sensoril, ≥10% withanolid","**125 mg**","stresszhullás; máj-/pajzsmirigy-figyelmeztetéssel, opcionális"],
 ["Vas","ferro-biszglicinát (~20% Fe)","**9 mg** elemi (≈45mg só)","csak igazolt alacsony ferritinnél; pajzsmirigy-gyógyszertől 4 órára"],
], [0.13,0.24,0.18,0.45])

h3("A.4 — „Collagen+\" tasak (külön termék)")
table([
 ["Hatóanyag","Dózis / adag"],
 ["Hidrolizált kollagén-peptid (Verisol-grade bioaktív)","**2,5 g** (generikusnál ~5 g)"],
 ["C-vitamin","40 mg"],
 ["Szilícium (bambusz-kivonat 70% SiO2 vagy ch-OSA)","5–10 mg Si"],
], [0.6,0.4])

h3("A.5 — Pilot batch nyersanyaglista (BOM)")
para("Egységdarab: **60.000 softgel + 30.000 kapszula** / 1.000 doboz (= 30.000 adag).", 9)
table([
 ["Hatóanyag","kg / 1.000 doboz","kg / 5.000 doboz"],
 ["Saw palmetto (85–95% FFA)","9,6","48,0"],
 ["Tökmagolaj","12,0","60,0"],
 ["Tokotrienol-komplex 50%","3,0","15,0"],
 ["L-cisztein HCl","6,0","30,0"],
 ["C-vitamin (aszkorbinsav)","~3,0","~15,0"],
 ["Cink-biszglicinát","2,25","11,25"],
 ["Réz-biszglicinát","0,23","1,15"],
 ["Szelén-premix (0,5%)","0,33","1,65"],
 ["D3-premix","~0,30","~1,50"],
 ["Biotin 1% trituráció","0,90","4,50"],
 ["Vivőolaj / tokoferol / rizshéj / SiO2","q.s.","q.s."],
], [0.5,0.25,0.25], ["LEFT","RIGHT","RIGHT"])
warn("**MOQ-valóság:** a softgel-gyártás minimum sorozata jellemzően 100.000–250.000 db (≈ 1.700–4.200 doboz). Reális első sorozat: 2.000–4.000 doboz, vagy alacsony-MOQ-s gyártó.")

h3("A.6 — Minőségi követelmények (a szerződésbe)")
bullets([
 "Sarzsonkénti **COA** (azonosság + hatóanyag-tartalom)",
 "**Nehézfém-panel:** As / Pb / Cd / Hg",
 "**Mikrobiológia** (összcsíraszám, E. coli, Salmonella, élesztő/penész)",
 "**Stabilitási teszt** (min. 6 hó gyorsított) — az olajok **oxidációs indexe** (peroxidszám) kulcs",
 "**Túladagolási terv** a vitaminokra; softgelhez nitrogén-öblítés/antioxidáns",
])

h2("B RÉSZ — HOL TUDOD LEGYÁRTATNI")
para("A Vitalo magyar/EU bolt → az **EU-s utat** javaslom (logisztika, notifikáció, bizalom).")

h3("B.1 — A gyártó típusa")
table([
 ["Forma","Mit kapsz","Neked"],
 ["White/Private label","Kész alapreceptre a márkád. Olcsó, gyors, de nem a mi egyedi receptünk.","csak gyors teszthez"],
 ["**Custom / Contract Mfg (CMO)**","A **mi receptünket** gyártják.","**EZ KELL**"],
], [0.27,0.5,0.23])

h3("B.2 — Kötelező követelmények a gyártónál")
bullets([
 "**EU GMP** + **ISO 22000 / FSSC 22000** + **HACCP**",
 "Tud **softgelt ÉS kapszulát** is (vagy két specialista + közös „kit\"-csomagolás)",
 "Sarzsonkénti **COA**, **nehézfém-vizsgálat**, **stabilitási teszt**",
 "Vállalja a **regulációs dokumentációt** (vagy ajánl tanácsadót)",
])

h3("B.3 — Hol találsz gyártót")
bullets([
 "**Szakvásár (leggyorsabb):** Vitafoods Europe (Barcelona), SupplySide / Hi&Fi Europe — egy nap alatt 50 EU CMO.",
 "**EU softgel-specialisták:** EuroCaps (UK), Procaps, Catalent, Captek + német/holland/lengyel/spanyol bérgyártók.",
 "**EU kapszula/porkeverék private label:** német, holland, lengyel és **magyar** bérgyártók — 3–4 ajánlat.",
 "**Alacsonyabb MOQ / olcsóbb:** Alibaba ázsiai GMP-gyártók — **csak alapos auditálással** (GMP, EU-import, 3. fél teszt).",
])

h3("B.4 — EU / magyar szabályozás (más, mint az USA!)")
bullets([
 "A táplálékkiegészítő itt **élelmiszer** (2002/46/EK irányelv) — nem „supplement\" az FDA szerint.",
 "**Bejelentés HU-ban:** forgalomba hozatal előtt **OGYÉI**-notifikáció (terméklap + címke).",
 "**Botanikumok (saw palmetto):** EU-ban engedélyezettek; a címkeállítások szigorúak. Engedélyezett EFSA-állítás: cink/szelén/biotin „a normál haj fenntartásához hozzájárul\". Gyógyhatás tilos.",
 "**Terhességi figyelmeztetés** a saw palmetto miatt kötelező a címkén.",
])

h3("B.5 — Nagyságrendi költségek (irány)")
bullets([
 "**Pilot sorozat (egyszeri):** formuláció + sorozat + tesztek ≈ **€15.000–40.000**.",
 "**Gyártott önköltség:** ~**$25–40/doboz** induló volumenen (két dózisforma!), skálázva csökken → javasolt ár **$45/hó**.",
])

h3("B.6 — Cselekvési terv")
bullets([
 "Véglegesítsd a specifikációt egy formulátorral (dózis-illesztés, segédanyagok, túladagolás).",
 "Küldd ki az **RFQ-t** (lent) 3–4 EU CMO-nak.",
 "Hasonlítsd: MOQ, ár/doboz, átfutás, tanúsítványok, stabilitás.",
 "Rendelj **mintát + COA-t**, mielőtt a teljes sorozatot megrendeled.",
 "Intézd az **OGYÉI-bejelentést** és a végleges címkét (regulációs tanácsadóval).",
 "Indítsd a stabilitási tesztet; a kész sarzs COA-ját töltsd a termékoldalra (QR).",
])

h2("C RÉSZ — RFQ (ajánlatkérő) e-mail sablon")
pdf.set_font("dvm", "", 8.3); pdf.set_text_color(26, 42, 40)
pdf.set_fill_color(246, 248, 248)
rfq = ("""Subject: RFQ - Custom hair-wellness supplement (softgel + capsule), EU GMP

Hello [Manufacturer],

We are launching a women's hair-wellness supplement (EU/Hungary market) and are
looking for an EU GMP / ISO 22000 contract manufacturer for a CUSTOM formulation in
two dose forms: softgels (oils) and vegetable capsules (powders), packaged together
(90 units/bottle, 30-day supply).

Please quote for 2,000 and 5,000 bottles, including:
 1. Price per bottle (formulation + encapsulation + bottling + label application)
 2. MOQ for softgels and for capsules
 3. Lead time
 4. Certifications (GMP, ISO 22000/FSSC, HACCP), per-batch COA, heavy-metal testing
    (As/Pb/Cd/Hg), and 6-month accelerated stability
 5. Whether you can support EU food-supplement labelling / notification documentation

Formula (per daily serving = 2 softgels + 1 capsule):
 Softgel: Saw palmetto CO2 extract (85-95% FFA) 320 mg; Pumpkin seed oil 400 mg;
          Tocotrienol complex 100 mg.
 Capsule: L-Cysteine 200 mg; Vitamin C 90 mg; Zinc bisglycinate (15 mg Zn);
          Copper bisglycinate (1 mg Cu); Selenium 55 mcg; Vitamin D3 1000 IU;
          Biotin 300 mcg.

NDA available on request. Thank you!
[Your name / Vitalo]""")
pdf.multi_cell(EPW, 4.2, rfq, border=1, fill=True, new_x="LMARGIN", new_y="NEXT", padding=3)
pdf.ln(3)
small("Készült dinamikus multi-agent workflow eredményéből (review-kutatás → összetevő-tudomány → formuláció → reguláció → adverszariális red-team). Kereskedelmi használat előtt elsődleges forrásból ellenőrizendő. Educational concept — not medical or regulatory advice. Nincs gyógyhatás.")

pdf.output("/home/user/meditation_companion/honest_roots_recept.pdf")
print("OK")
