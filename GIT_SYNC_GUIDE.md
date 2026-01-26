# 🔄 Setup Multi-Device cu Git

## Pe primul device (SETUP INIȚIAL)

Dacă nu ai făcut deja setup Git, urmează pașii:

### 1. Configurează Git
```bash
git config --global user.name "Numele Tău"
git config --global user.email "email@tau.com"
```

### 2. Verifică că repo-ul e conectat
```bash
cd d:\punctaj
git remote -v
```

Ar trebui să vezi:
```
origin  https://github.com/parjanul123/punctaj.git (fetch)
origin  https://github.com/parjanul123/punctaj.git (push)
```

### 3. Test Push
Modifică ceva în aplicație și verifică în terminal:
```
✓ Git push: data/Oras/Institutie.json
```

## Pe un device NOU

### Varianta 1: Clonare completă (RECOMANDAT)

```bash
# Clonează repo-ul
git clone https://github.com/parjanul123/punctaj.git
cd punctaj

# Instalează dependențele (doar pentru development)
pip install -r requirements.txt

# Rulează aplicația
dist\PunctajManager.exe
```

**Datele tale vor fi deja acolo!** 🎉

### Varianta 2: Doar exe-ul (fără Git sync)

1. Copiază doar `PunctajManager.exe`
2. Rulează-l
3. Aplicația va funcționa, dar **FĂRĂ sincronizare Git**
4. Datele vor fi doar locale

## 🔄 Sincronizare Automată

### Când aplicația face Push:
- ✅ Salvezi date noi
- ✅ Modifici punctaje
- ✅ Adaugi angajați
- ✅ Ștergi instituții
- ✅ Modifici coloane/rankuri

### Când aplicația face Pull:
- ✅ La pornirea aplicației
- ✅ Când dai refresh manual (dacă există opțiunea)

## ⚠️ Conflicte Git

Dacă lucrezi pe **2 device-uri simultan**, pot apărea conflicte:

```
✗ Git error: merge conflict
```

### Soluție:
1. Închide aplicația
2. Deschide terminal în folderul punctaj:
```bash
cd d:\punctaj

# Vezi ce fișiere au conflicte
git status

# Alege varianta ta sau a lor
git checkout --ours data/Oras/Institutie.json    # Păstrează versiunea ta
git checkout --theirs data/Oras/Institutie.json  # Ia versiunea de pe GitHub

# Sau rezolvă manual conflictele în VS Code

# După rezolvare:
git add .
git commit -m "Rezolvat conflicte"
git push
```

## 🔐 Autentificare GitHub

### Prima dată când faci push, Git va cere autentificare:

**Username**: `parjanul123`  
**Password**: ⚠️ **NU mai merge parola!** Trebuie **Personal Access Token**

### Generare Token:
1. https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Selectează: `repo` (full control)
4. Copiază token-ul
5. Folosește-l în loc de parolă

### Salvare credențiale:
```bash
git config --global credential.helper store
```

Apoi, la următorul push, introdu token-ul - va fi salvat automat!

## 📊 Verificare Sincronizare

### Vezi ultimele commit-uri:
```bash
git log --oneline -10
```

### Vezi ce s-a modificat:
```bash
git diff
```

### Vezi starea curentă:
```bash
git status
```

## 🚀 Best Practices

1. **Închide aplicația** pe un device înainte să o deschizi pe altul
2. **Pull manual** dacă ai modificat pe alt device:
   ```bash
   git pull
   ```
3. **Verifică GitHub** periodic: https://github.com/parjanul123/punctaj/tree/main/data

## ❓ Troubleshooting

### "fatal: not a git repository"
```bash
cd d:\punctaj
git init
git remote add origin https://github.com/parjanul123/punctaj.git
git pull origin main
```

### "fatal: refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
```

### Vrei să resetezi totul?
```bash
# ⚠️ ATENȚIE: Șterge toate modificările locale!
git fetch origin
git reset --hard origin/main
```
