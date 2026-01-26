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

## � Sincronizare Multi-Device cu Git

Folderele `data/` și `arhiva/` sunt **sincronizate automat pe Git** pentru:
- ✅ **Sincronizare între device-uri** - aceleași date pe toate calculatoarele
- ✅ **Backup automat** - datele sunt salvate pe GitHub
- ✅ **Istoric modificări** - poți vedea ce s-a schimbat și când

### Cum funcționează:

1. **Când modifici date** în aplicație → Git face **commit și push automat**
2. **Când pornești aplicația** → Git face **pull automat** pentru date noi
3. **Pe alt device** → Clonează repo-ul și datele sunt acolo!

### Setup pe un nou device:

```bash
git clone https://github.com/parjanul123/punctaj.git
cd punctaj
# Apoi rulează aplicația
```

Datele tale vor fi sincronizate automat! 🚀

## 🔧 Rebuild

Pentru rebuild după modificări:
```
.\build.bat
```

Exe-ul va fi generat în `dist/PunctajManager.exe`
