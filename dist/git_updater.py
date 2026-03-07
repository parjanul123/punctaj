# -*- coding: utf-8 -*-
"""
🔄 Git Updater - Aplicație separată pentru actualizări
Permite actualizarea aplicației principale prin git pull
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
from datetime import datetime
import configparser

# Versiune
VERSION = "1.0.0"

class GitUpdater:
    """Aplicație pentru actualizarea aplicației din git"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"🔄 Git Updater v{VERSION}")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Iconă dacă există
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Variabile
        self.is_updating = False
        self.repo_path = os.path.dirname(os.path.abspath(__file__))
        
        # UI
        self.setup_ui()
        
        # Verifică git la startup
        self.root.after(1000, self.check_git_status)
    
    def setup_ui(self):
        """Configurează interfața utilizator"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🔄 Git Updater",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=25)
        
        # Versiune
        tk.Label(
            header_frame,
            text=f"v{VERSION}",
            font=("Segoe UI", 10),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack(side=tk.RIGHT, padx=20, pady=25)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Repository info
        repo_frame = tk.LabelFrame(main_frame, text="📁 Repository Info", font=("Segoe UI", 10, "bold"), bg="#ecf0f1")
        repo_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            repo_frame,
            text=f"Path: {self.repo_path}",
            font=("Segoe UI", 9),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        self.status_label = tk.Label(
            repo_frame,
            text="📊 Verificând statusul git...",
            font=("Segoe UI", 9),
            bg="#ecf0f1",
            fg="#e67e22"
        )
        self.status_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Control buttons
        controls_frame = tk.Frame(main_frame, bg="#ecf0f1")
        controls_frame.pack(fill=tk.X, pady=10)
        
        self.check_button = tk.Button(
            controls_frame,
            text="🔍 Verifică Modificări",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            command=self.check_updates,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = tk.Button(
            controls_frame,
            text="⬇️ Actualizează (Git Pull)",
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.start_update,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.restart_button = tk.Button(
            controls_frame,
            text="🔄 Restart Aplicație",
            font=("Segoe UI", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            command=self.restart_main_app,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Output log
        log_frame = tk.LabelFrame(main_frame, text="📋 Output Log", font=("Segoe UI", 10, "bold"), bg="#ecf0f1")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ecf0f1",
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_text = tk.Label(
            status_frame,
            text="Pregătit pentru actualizare",
            font=("Segoe UI", 9),
            bg="#34495e",
            fg="white"
        )
        self.status_text.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Binding pentru închidere
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def log(self, message, level="INFO"):
        """Adaugă mesaj în log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
        print(f"{log_entry.strip()}")  # Also print to console
    
    def update_status(self, text):
        """Actualizează status bar"""
        self.status_text.config(text=text)
        self.root.update()
    
    def run_git_command(self, command, cwd=None):
        """Execută comandă git și returnează output"""
        try:
            if cwd is None:
                cwd = self.repo_path
            
            self.log(f"Executând: {command}", "CMD")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log(f"Succes: {result.stdout.strip()}", "SUCCESS")
                return True, result.stdout.strip()
            else:
                self.log(f"Eroare: {result.stderr.strip()}", "ERROR")
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            self.log("Timeout la execuția comenzii git", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self.log(f"Excepție la execuția git: {e}", "ERROR")
            return False, str(e)
    
    def check_git_status(self):
        """Verifică statusul git repository-ului"""
        self.log("Verificând statusul git repository...")
        
        # Verifică dacă este git repo
        success, output = self.run_git_command("git status --porcelain")
        if not success:
            self.status_label.config(
                text="❌ Nu este un repository git valid",
                fg="#e74c3c"
            )
            self.update_button.config(state=tk.DISABLED)
            return
        
        # Verifică branch
        success, branch = self.run_git_command("git branch --show-current")
        if success:
            self.log(f"Branch curent: {branch}")
        
        # Verifică status local
        if output.strip():
            self.status_label.config(
                text="⚠️ Modificări locale necommit-ate",
                fg="#e67e22"
            )
            self.log("Atenție: Există modificări locale necommit-ate")
        else:
            self.status_label.config(
                text="✓ Repository curat",
                fg="#27ae60"
            )
    
    def check_updates(self):
        """Verifică dacă există actualizări disponibile"""
        if self.is_updating:
            return
        
        def check_thread():
            self.is_updating = True
            self.check_button.config(state=tk.DISABLED)
            self.progress_bar.start()
            self.update_status("Verificând actualizări...")
            
            try:
                # Fetch remote changes
                self.log("Verificând actualizări disponibile...")
                success, output = self.run_git_command("git fetch origin")
                
                if not success:
                    messagebox.showerror("Eroare", f"Nu pot verifica actualizările:\n{output}")
                    return
                
                # Verifică dacă sunt modificări
                success, output = self.run_git_command("git log HEAD..origin/main --oneline")
                
                if not success:
                    # Încearcă cu master dacă main nu există
                    success, output = self.run_git_command("git log HEAD..origin/master --oneline")
                
                if success and output.strip():
                    lines = output.strip().split('\n')
                    count = len(lines)
                    self.log(f"Găsite {count} actualizări disponibile:")
                    for line in lines:
                        self.log(f"  • {line}")
                    
                    messagebox.showinfo(
                        "Actualizări Disponibile",
                        f"🔄 Găsite {count} actualizări!\n\n"
                        f"Apasă 'Actualizează (Git Pull)' pentru a le descărca."
                    )
                else:
                    self.log("Nu sunt actualizări disponibile")
                    messagebox.showinfo(
                        "La Zi",
                        "✅ Aplicația este deja la ultima versiune!"
                    )
            
            finally:
                self.is_updating = False
                self.check_button.config(state=tk.NORMAL)
                self.progress_bar.stop()
                self.update_status("Verificare completă")
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def start_update(self):
        """Începe procesul de actualizare"""
        if self.is_updating:
            return
        
        # Confirmă actualizarea
        if not messagebox.askyesno(
            "Confirmă Actualizarea",
            "🔄 Vei actualiza aplicația cu ultimele modificări din git.\n\n"
            "⚠️ Orice modificări locale necommit-ate pot fi pierdute.\n"
            "✓ Se recomandă să închizi aplicația principală mai întâi.\n\n"
            "Continuă actualizarea?"
        ):
            return
        
        def update_thread():
            self.is_updating = True
            self.update_button.config(state=tk.DISABLED)
            self.check_button.config(state=tk.DISABLED)
            self.progress_bar.start()
            self.update_status("Actualizare în progres...")
            
            try:
                # Backup config files înainte de pull
                self.log("Făcând backup la fișierele de configurare...")
                config_files = ["supabase_config.ini", "users_permissions.json"]
                backup_made = False
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        backup_name = f"{config_file}.backup.{int(time.time())}"
                        try:
                            import shutil
                            shutil.copy2(config_file, backup_name)
                            self.log(f"Backup creat: {backup_name}")
                            backup_made = True
                        except Exception as e:
                            self.log(f"Eroare la backup {config_file}: {e}", "WARNING")
                
                # Git stash pentru modificări locale
                self.log("Salvând modificările locale cu git stash...")
                success, output = self.run_git_command("git stash")
                if success and "No local changes to save" not in output:
                    self.log("Modificări locale stash-uite")
                
                # Git pull
                self.log("Descărcând actualizările cu git pull...")
                success, output = self.run_git_command("git pull origin")
                
                if success:
                    if "Already up to date" in output or "Already up-to-date" in output:
                        self.log("Aplicația era deja la zi")
                        messagebox.showinfo(
                            "La Zi",
                            "✅ Aplicația era deja la ultima versiune!"
                        )
                    else:
                        self.log("Actualizare completă cu succes!")
                        
                        # Re-aplică stash dacă este necesar
                        success_stash, _ = self.run_git_command("git stash list")
                        if success_stash:
                            self.log("Re-aplicând modificările locale...")
                            self.run_git_command("git stash pop")
                        
                        self.restart_button.config(state=tk.NORMAL)
                        
                        messagebox.showinfo(
                            "Actualizare Completă",
                            "✅ Aplicația a fost actualizată cu succes!\n\n"
                            "🔄 Poți restarța aplicația principală acum.\n\n"
                            f"Backup config files: {'Da' if backup_made else 'Nu'}"
                        )
                else:
                    messagebox.showerror(
                        "Eroare Actualizare",
                        f"❌ Eroare la git pull:\n\n{output}\n\n"
                        f"Verifică conexiunea la internet și repository-ul git."
                    )
            
            except Exception as e:
                self.log(f"Excepție în timpul actualizării: {e}", "ERROR")
                messagebox.showerror("Eroare", f"Eroare neașteptată:\n{e}")
            
            finally:
                self.is_updating = False
                self.update_button.config(state=tk.NORMAL)
                self.check_button.config(state=tk.NORMAL)
                self.progress_bar.stop()
                self.update_status("Actualizare completă")
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def restart_main_app(self):
        """Restartează aplicația principală"""
        main_app = os.path.join(self.repo_path, "punctaj.py")
        exe_app = os.path.join(self.repo_path, "dist", "Punctaj.exe")
        
        # Încearcă să găsească aplicația
        app_to_run = None
        if os.path.exists(exe_app):
            app_to_run = exe_app
        elif os.path.exists(main_app):
            app_to_run = f"python {main_app}"
        
        if app_to_run:
            if messagebox.askyesno(
                "Restart Aplicație",
                f"🔄 Vei restarța aplicația principală:\n{app_to_run}\n\n"
                f"Updater-ul se va închide automat.\n\nContinuă?"
            ):
                try:
                    self.log(f"Restartând aplicația: {app_to_run}")
                    
                    if app_to_run.endswith(".exe"):
                        subprocess.Popen([app_to_run], cwd=self.repo_path)
                    else:
                        subprocess.Popen(app_to_run, shell=True, cwd=self.repo_path)
                    
                    self.log("Aplicația principală a fost restartată")
                    self.root.after(2000, self.root.quit)
                    
                except Exception as e:
                    messagebox.showerror("Eroare", f"Nu pot restarța aplicația:\n{e}")
        else:
            messagebox.showerror(
                "Aplicație Negăsită",
                "Nu pot găsi aplicația principală pentru restart.\n\n"
                "Caută manual 'punctaj.py' sau 'Punctaj.exe'"
            )
    
    def on_closing(self):
        """Handler pentru închiderea aplicației"""
        if self.is_updating:
            if messagebox.askyesno(
                "Actualizare în Progres",
                "O actualizare este în progres.\n\n"
                "Ești sigur că vrei să închizi updater-ul?"
            ):
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Pornește aplicația"""
        self.root.mainloop()

# Entry point
if __name__ == "__main__":
    print(f"🔄 Git Updater v{VERSION}")
    print(f"Repository: {os.path.dirname(os.path.abspath(__file__))}")
    
    app = GitUpdater()
    app.run()