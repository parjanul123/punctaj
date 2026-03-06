# 🛡️ Punctaj Update

Aplicație specializată pentru actualizarea sistemului de management polițist Punctaj.

## 🚀 Funcții Principale

### 🔍 Verifică Actualizări
- Conectează la repository git
- Verifică commit-uri noi disponibile
- Afișează lista modificărilor

### ⬇️ Actualizează Punctaj  
- Backup automat configurații
- Git stash pentru modificări locale
- Git pull cu ultimele modificări
- Re-aplică modificări locale
- Verifică integritatea după update

### 💾 Backup Config
- Salvează fișiere importante: supabase_config.ini, users_permissions.json, discord_config.json
- Timestamp pentru organizare
- Locație: backup_configs/

### 🔄 Restart Punctaj
- Detectează automat aplicația principală  
- Pornește Punctaj.exe sau punctaj.py
- Închide updater-ul după restart

## 📊 Interfață

- **Design specializat** cu tema roșu-polițească
- **Status în timp real** pentru git, aplicație și config
- **Progres vizual** cu bara de progres  
- **Jurnal detaliat** cu color-coding pentru nivele
- **Butoane intuitive** cu icons și colors

## 🛡️ Siguranță

- Backup automat înainte de actualizare
- Git stash pentru modificări necommit-ate  
- Verificări de integritate
- Confirmări utilizator pentru operații critice
- Timeout pentru comenzi git (2 minute)

## ⚙️ Utilizare

1. **Dublu-click** pe Punctaj_Update.exe
2. **Verifică** statusul sistemului
3. **Apasă** "Verifică Actualizări" pentru a vedea ce e nou
4. **Apasă** "Actualizează Punctaj" pentru update complet
5. **Restart** aplicația după actualizare

## 🔧 Integrare

- Lansare din aplicația principală cu butonul "🛡️ Punctaj Update"
- Exe standalone în folderul dist/
- Compatibil cu toate versiunile Punctaj

---

**Versiune:** 2.0.0  
**Aplicație pentru:** Sistem Punctaj - Management Polițist  
**Build cu:** PyInstaller + Python 3.x
