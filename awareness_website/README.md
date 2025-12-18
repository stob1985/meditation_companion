# Figyelemfelhívó Weboldal - Ittas Vezetés

Ez egy figyelemfelhívó weboldal az ittas vezetés veszélyeire és következményeire. A weboldal az ittasvezetes.hu mintájára készült.

## 📋 Jellemzők

- **Professzionális dizájn**: Piros és sötét színvilág a figyelem felkeltésére
- **Responzív elrendezés**: Mobil és asztali eszközökön is jól néz ki
- **Interaktív űrlap**: Részletes adatgyűjtés validációval
- **CAPTCHA védelem**: Biztonságos űrlap beküldés
- **Smooth animációk**: Kellemesebb felhasználói élmény
- **SEO optimalizált**: Meta tagek és szemantikus HTML

## 🚀 Használat

### Helyi futtatás

1. Nyisd meg a `index.html` fájlt egy böngészőben:
   ```bash
   # Linux/Mac
   open index.html

   # Vagy egyszerűen dupla kattintás a fájlon
   ```

2. Vagy használj egy helyi webszervert:
   ```bash
   # Python 3
   python3 -m http.server 8000

   # Node.js (http-server)
   npx http-server
   ```

3. Majd navigálj a `http://localhost:8000` címre a böngészőben.

## 📁 Fájlstruktúra

```
awareness_website/
├── index.html          # Fő HTML fájl
├── styles.css          # Stíluslapok
├── script.js           # JavaScript funkcionalitás
├── assets/             # Képek és egyéb fájlok
│   └── logo.png       # Logo (hozzáadandó)
└── README.md          # Ez a fájl
```

## 🎨 Testreszabás

### Színek módosítása

A `styles.css` fájlban találhatók a fő színek:
- Piros (#c00 vagy #8b0000): Figyelem felkeltő szín
- Sötét háttér (#2a2a2a): Kontrasztos háttér
- Kék (#1e3a8a): Űrlap háttér

### Tartalom szerkesztése

Az `index.html` fájlban módosíthatod:
- Szövegeket
- Telefonszámot (S.O.S. Vonal)
- Navigációs menüpontokat
- Űrlap mezőket

### Logo hozzáadása

1. Helyezz el egy `logo.png` fájlt az `assets/` mappában
2. Ajánlott méret: 200x200 pixel
3. Átlátszó háttérrel (PNG formátum)

## ⚙️ Funkciók

### Űrlap validáció
- Minden kötelező mező ellenőrzése
- Email formátum validáció
- Telefonszám formátum validáció (06- előtag)
- CAPTCHA ellenőrzés
- Adatvédelmi feltételek elfogadása

### CAPTCHA
- Automatikusan generált 5 karakteres kód
- Frissítés gomb a kód újragenerálásához
- Védi az űrlapot spam beküldésektől

### Smooth scrolling
- Navigációs linkek simán görgetnek a megfelelő szekcióhoz
- Jobb felhasználói élmény

## 🔒 Biztonság

- CAPTCHA védelem az űrlapon
- Client-side validáció
- XSS védelem (ne használd éles környezetben backend nélkül!)
- HTTPS ajánlott éles használathoz

## 📱 Reszponzív dizájn

A weboldal optimalizált:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobil (< 768px)

## 🌐 Böngésző támogatás

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 Licensz

Ez egy demo projekt oktatási célokra.

## ⚠️ Fontos megjegyzések

1. **Éles használathoz szükséges**:
   - Backend (PHP, Node.js, Python, stb.)
   - Adatbázis kapcsolat
   - Email küldés funkció
   - HTTPS tanúsítvány
   - GDPR megfelelőség
   - Cookie beleegyező rendszer

2. **Jelenleg**:
   - Az űrlap adatokat csak kliens oldalon validálja
   - Nem küldi el valós szervernek az adatokat
   - Csak demo/development célokra használható

## 🔧 Továbbfejlesztési lehetőségek

- [ ] Backend implementáció
- [ ] Valódi email küldés
- [ ] Adatbázis integráció
- [ ] Admin felület
- [ ] Többnyelvűség
- [ ] Cookie consent banner
- [ ] Google Analytics
- [ ] reCAPTCHA integráció

## 📞 Kapcsolat

Ha kérdésed van a weboldallal kapcsolatban, keress fel!

---

**Készítve**: 2025
**Technológiák**: HTML5, CSS3, Vanilla JavaScript
