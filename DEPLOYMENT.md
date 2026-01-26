# 📦 PunctajManager - Instalare și Utilizare

## 🎯 Cerințe de Sistem

### Necesare:
- **Windows 10/11** (64-bit)
- **Visual C++ Redistributables** - [Descarcă aici](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Opționale:
- **Git** - pentru sincronizare automată (nu e necesar pentru funcționarea aplicației)

## 🚀 Instalare

### Pas 1: Verificare Sistem
Rulează `CHECK_SYSTEM.bat` pentru a verifica dacă sistemul îndeplinește cerințele.

### Pas 2: Instalare Visual C++
Dacă verificarea arată că lipsesc Visual C++ Redistributables:
1. Descarcă: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Instalează fișierul descărcat
3. Repornește calculatorul (opțional, dar recomandat)

### Pas 3: Rulare Aplicație
Dublu-click pe `PunctajManager.exe`

## ⚠️ Depanare Erori Comune

### "The application failed to start because VCRUNTIME140.dll was not found"
**Cauză**: Lipsesc Visual C++ Redistributables  
**Soluție**: Instalează de la https://aka.ms/vs/17/release/vc_redist.x64.exe

### "Application error" sau "Failed to execute script"
**Cauză**: Antivirus-ul blochează aplicația  
**Soluție**: Adaugă `PunctajManager.exe` în excepțiile antivirus-ului

### Aplicația nu salvează date
**Verifică**:
- Folderul `data/` există lângă `PunctajManager.exe`
- Ai permisiuni de scriere în folder

## 📁 Structura Folderelor

După prima rulare, vei avea:
```
PunctajManager.exe          <- Executabilul
data/                       <- Date instituții (JSON)
  └─ Oras/
      └─ Institutie.json
arhiva/                     <- Arhive exportate (CSV)
  └─ Oras/
      └─ Institutie.csv
```

## ℹ️ Funcții Git (Opționale)

Dacă **Git NU este instalat**:
- ✅ Aplicația funcționează normal
- ❌ Nu sincronizează automat datele
- ✅ Poți exporta manual în CSV

Dacă **Git ESTE instalat**:
- ✅ Sincronizare automată a datelor
- ✅ Istoric versiuni
- ✅ Push/Pull automat (dacă e configurat remote)

## 🔧 Suport

Pentru probleme sau întrebări, verifică mai întâi:
1. Visual C++ Redistributables sunt instalate
2. Antivirus-ul nu blochează aplicația
3. Ai permisiuni de scriere în folder

## 📝 Note

- Aplicația **NU necesită Python** instalat
- Folderele `data/` și `arhiva/` sunt create automat
- Datele sunt salvate local, nu în cloud (dacă nu folosești Git)
