# 🔄 Git Updater - Documentație Completă

## 📋 Prezentare Generală

**Git Updater** este o aplicație separată care permite actualizarea automată a aplicației principale prin `git pull`. Este construită să fie independentă și sigură pentru actualizări.

## 🏗️ Build & Deploy

### Construire EXE
```bash
# Activează environment virtual
venv\Scripts\activate

# Rulează build
python build_updater.py
# SAU
BUILD_UPDATER.bat
```

### Output
- **Directorul**: `dist_updater/Git_Updater/`
- **Exe Principal**: `Git_Updater.exe`
- **Mărimea**: ~15-20 MB (standalone)

## 🚀 Utilizare

### 1. Verificare Modificări
- Apasă **🔍 Verifică Modificări**
- Verifică `git fetch` și compară cu remote
- Afișează numărul de commit-uri disponibile

### 2. Actualizare
- Apasă **⬇️ Actualizează (Git Pull)** 
- Face backup automat la config files
- Execută `git stash` pentru modificări locale
- Execută `git pull origin`
- Re-aplică `git stash pop` dacă necesar

### 3. Restart Aplicație
- Apasă **🔄 Restart Aplicație** (disponibil după actualizare)
- Caută automat `punctaj.py` sau `Punctaj.exe`
- Închide updater-ul și pornește aplicația principală

## 🛡️ Siguranță & Backup

### Backup Automat
- `supabase_config.ini` → `supabase_config.ini.backup.{timestamp}`
- `users_permissions.json` → `users_permissions.json.backup.{timestamp}`

### Protecție Modificări Locale
- Git stash salvează modificările locale
- Re-aplică automat după pull
- Nu se pierd modificările necommit-ate

### Verificări de Siguranță
- Verifică dacă este git repository valid
- Avertizează pentru modificări locale
- Confirmă înainte de actualizare

## 🔧 Integrare în Aplicația Principală

### Adăugare Buton în Sidebar

```python
# În punctaj.py - în secțiunea sidebar buttons
git_updater_button = tk.Button(
    sidebar,
    text="🔄 Git Updater",
    font=("Segoe UI", 10, "bold"),
    bg="#9b59b6",
    fg="white",
    command=launch_git_updater,
    relief=tk.FLAT,
    cursor="hand2"
)
git_updater_button.pack(fill=tk.X, padx=10, pady=5)
```

### Funcție de Lansare

```python
def launch_git_updater():
    """Lansează Git Updater extern"""
    updater_paths = [
        os.path.join(os.path.dirname(__file__), "dist_updater", "Git_Updater", "Git_Updater.exe"),
        os.path.join(os.path.dirname(__file__), "git_updater.py")
    ]
    
    for path in updater_paths:
        if os.path.exists(path):
            try:
                if path.endswith('.exe'):
                    subprocess.Popen([path], cwd=os.path.dirname(__file__))
                else:
                    subprocess.Popen(["python", path], cwd=os.path.dirname(__file__))
                
                messagebox.showinfo(
                    "Git Updater",
                    "🔄 Git Updater a fost lansat!\n\n"
                    "Folosește-l pentru actualizări din git."
                )
                return
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu pot lansa Git Updater: {e}")
                return
    
    messagebox.showerror(
        "Git Updater Lipsește", 
        "Nu pot găsi Git Updater.\n\n"
        "Rulează BUILD_UPDATER.bat pentru a-l construi."
    )
```

### Meniu Context (Opțional)

```python
# Adică în meniul File sau Help
def create_updater_menu_item(menubar):
    """Adaugă item pentru Git Updater în meniu"""
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    help_menu.add_command(
        label="🔄 Check for Updates...",
        command=launch_git_updater
    )
```

## 📝 Log & Debugging

### Log Format
```
[HH:MM:SS] LEVEL: Message
[14:32:15] INFO: Verificând statusul git repository...
[14:32:16] CMD: Executând: git status --porcelain
[14:32:16] SUCCESS: Succes: 
[14:32:17] INFO: Repository curat
```

### Nivele de Log
- **INFO**: Informații generale
- **CMD**: Comenzi git executate
- **SUCCESS**: Operații reușite
- **WARNING**: Avertismente (ex: backup eșuat)
- **ERROR**: Erori grave

## 🎯 Cazuri de Utilizare

### 1. Actualizare Remotă
- Developer-ul face push modificări
- Utilizatorul rulează Git Updater
- Aplicația se actualizează automat

### 2. Distribuire Patch-uri
- Fix-uri rapide prin git
- Nu necesită redistribuire exe
- Actualizare în timp real

### 3. Sincronizare Multi-Device
- Același repository pe mai multe device-uri
- Updater sincronizează toate modificările
- Consistent cu aplicația principală

## ⚙️ Configurare & Customizare

### Icon Personalizat
- Pune `icon.ico` în directorul principal
- Se include automat în exe

### Modificare Repository URL
- Git Updater folosește automat repository-ul curent
- Pentru alt repository: modifică `self.repo_path` în `git_updater.py`

### Customize UI Colors
```python
# În GitUpdater.__init__()
self.colors = {
    "primary": "#2c3e50",      # Header background
    "secondary": "#ecf0f1",    # Main background
    "accent": "#3498db",       # Button colors
    "success": "#27ae60",
    "warning": "#e67e22",
    "error": "#e74c3c"
}
```

## 🔍 Troubleshooting

### Eroare: "Nu este un repository git valid"
- **Cauză**: Directorul nu conține `.git/`
- **Soluție**: Rulează `git init` sau clonează repository-ul

### Eroare: "Timeout la execuția comenzii git"  
- **Cauză**: Conexiune lentă sau repository mare
- **Soluție**: Modifică timeout-ul în `run_git_command()` (linia 60s)

### Updater nu pornește aplicația principală
- **Cauză**: Nu găsește `punctaj.py` sau `Punctaj.exe` 
- **Soluție**: Verifică paths în `restart_main_app()`

### Git pull eșuat - merge conflicts
- **Cauză**: Modificări locale conflictuale
- **Soluție**: Git Updater face stash, dar manual trebuie rezolvat conflictul

## 📊 Statistici Build

```
├─ git_updater.py          # ~400 linii, aplicația principală
├─ build_updater.py        # ~200 linii, build script
├─ BUILD_UPDATER.bat       # ~10 linii, batch helper
└─ dist_updater/
   └─ Git_Updater/
      ├─ Git_Updater.exe   # ~15-20 MB exe final
      └─ README.md         # Documentație inclusă
```

## 🔜 Viitoare Îmbunătățiri

### V1.1 Planificat
- [ ] Auto-check pentru updates la startup
- [ ] Progres bar pentru git operations
- [ ] Support pentru multiple branches  
- [ ] Integration cu GitHub API pentru releases

### V1.2 Ideas  
- [ ] Rollback la versiunea anterioară
- [ ] Scheduler pentru updates automate
- [ ] Backup complet înainte de update
- [ ] Integration cu aplicația principală (IPC)

---

✅ **Git Updater este gata pentru producție!**

Pentru întrebări sau probleme, verifică log-urile sau contactează development team.