# Important - Structura Aplicației

## 📁 Folderul `dist/`

După build, în `dist/` vei găsi:
- **PunctajManager.exe** - executabilul principal

## 🗂️ Foldere Partajate

Aplicația folosește **aceleași foldere de date** indiferent de unde rulează exe-ul:

- **data/** - Fișierele JSON cu datele instituțiilor
- **arhiva/** - Arhivele CSV exportate

### ⚠️ IMPORTANT pentru Deployment

Când distribui aplicația:

1. **Copiază** `dist/PunctajManager.exe` în locația dorită
2. **NU** copia folderele `data/` și `arhiva/` împreună cu exe-ul
3. La prima rulare, exe-ul va crea automat aceste foldere **în locația lui**

### ✅ Avantaje

- **Un singur exe** care funcționează identic oriunde
- **Date centralizate** - dacă faci shortcut la exe, folosește **aceleași date**
- **Nu se duplică datele** când muți sau copiezi exe-ul

## 🚫 Git

Folderele `data/` și `arhiva/` sunt excluse din Git pentru că:
- Conțin date generate de aplicație
- Nu trebuie versionate
- Fiecare utilizator are propriile date locale

## 🔧 Rebuild

Pentru rebuild după modificări:
```
.\build.bat
```

Exe-ul va fi generat în `dist/PunctajManager.exe`
