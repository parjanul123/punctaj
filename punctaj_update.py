# -*- coding: utf-8 -*-
"""
🔄 Punctaj Update - Aplicație pentru actualizarea sistemului Punctaj
Specializată pentru aplicația de management polițist
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import json
from datetime import datetime
import configparser
import requests
from pathlib import Path

# Versiune
VERSION = "2.0.0"
APP_NAME = "Punctaj Git Pull"

class PunctajUpdater:
    """Aplicație specializată pentru actualizarea sistemului Punctaj"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"🔄 {APP_NAME} v{VERSION}")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Tema culorilor Punctaj
        self.colors = {
            "primary": "#c41e3a",      # Roșu policesc
            "secondary": "#2c3e50",    # Albastru închis
            "background": "#ecf0f1",   # Gri deschis
            "success": "#27ae60",      # Verde
            "warning": "#e67e22",      # Portocaliu
            "error": "#e74c3c",        # Roșu
            "info": "#3498db"          # Albastru
        }
        
        # Iconă dacă există
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Variabile
        self.is_updating = False
        
        # Repository path - ÎNTOTDEAUNA folderul părinte (punctaj)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir.endswith('dist'):
            # Dacă exe-ul este în dist/, mergi la folderul părinte punctaj/
            self.repo_path = os.path.dirname(current_dir)
        else:
            # Dacă rulezi direct .py din punctaj/
            self.repo_path = current_dir
        
        # Status aplicație punctaj
        self.punctaj_running = False
        
        # UI
        self.setup_ui()
        
        # Verificări la startup
        self.root.after(1000, self.startup_checks)
    
    def setup_ui(self):
        """Configurează interfața utilizator cu tema Punctaj"""
        
        # Header cu logo Punctaj
        header_frame = tk.Frame(self.root, bg=self.colors["primary"], height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo și titlu
        title_frame = tk.Frame(header_frame, bg=self.colors["primary"])
        title_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(
            title_frame,
            text="🛡️ PUNCTAJ",
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["primary"],
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text=f"Update Manager v{VERSION}",
            font=("Segoe UI", 14),
            bg=self.colors["primary"],
            fg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(0, 20), pady=20)
        
        # Versiune și info
        tk.Label(
            title_frame,
            text=f"📅 {datetime.now().strftime('%d.%m.%Y')}",
            font=("Segoe UI", 10),
            bg=self.colors["primary"],
            fg="#f8f9fa"
        ).pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.colors["background"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Status section
        status_section = tk.LabelFrame(
            main_frame, 
            text="📊 Status Sistem", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.colors["background"],
            fg=self.colors["secondary"]
        )
        status_section.pack(fill=tk.X, pady=(0, 10))
        
        # Repository info
        repo_info_frame = tk.Frame(status_section, bg=self.colors["background"])
        repo_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            repo_info_frame,
            text=f"📁 Git Repository: {self.repo_path}",
            font=("Segoe UI", 9),
            bg=self.colors["background"],
            fg=self.colors["secondary"],
            anchor="w"
        ).pack(fill=tk.X)
        
        self.status_labels = {}
        status_items = [
            ("git_status", "🔗 Git Status: Verificând..."),
            ("punctaj_status", "🛡️ Aplicația Punctaj: Detectând..."),
            ("config_status", "⚙️ Fișiere Config: Verificând...")
        ]
        
        for key, initial_text in status_items:
            label = tk.Label(
                repo_info_frame,
                text=initial_text,
                font=("Segoe UI", 9),
                bg=self.colors["background"],
                fg=self.colors["warning"],
                anchor="w"
            )
            label.pack(fill=tk.X, pady=2)
            self.status_labels[key] = label
        
        # Control buttons
        controls_frame = tk.Frame(main_frame, bg=self.colors["background"])
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Primul rând de butoane
        row1_frame = tk.Frame(controls_frame, bg=self.colors["background"])
        row1_frame.pack(fill=tk.X, pady=5)
        
        self.check_button = tk.Button(
            row1_frame,
            text="🔍 Verifică Actualizări",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["info"],
            fg="white",
            command=self.check_updates,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.update_button = tk.Button(
            row1_frame,
            text="⬇️ Git Pull Actualizări",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["success"],
            fg="white",
            command=self.start_update,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Al doilea rând de butoane - DOAR pentru info și diagnostice
        row2_frame = tk.Frame(controls_frame, bg=self.colors["background"])
        row2_frame.pack(fill=tk.X, pady=5)
        
        self.status_button = tk.Button(
            row2_frame,
            text="🔍 Status Git",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["info"],
            fg="white",
            command=self.show_git_status,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.status_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress section
        progress_frame = tk.Frame(main_frame, bg=self.colors["background"])
        progress_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            progress_frame,
            text="📈 Progres:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["background"],
            fg=self.colors["secondary"]
        ).pack(anchor="w")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Gata pentru actualizare",
            font=("Segoe UI", 9),
            bg=self.colors["background"],
            fg=self.colors["secondary"]
        )
        self.progress_label.pack(anchor="w")
        
        # Activity log
        log_frame = tk.LabelFrame(
            main_frame, 
            text="📋 Jurnal Activitate", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.colors["background"],
            fg=self.colors["secondary"]
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg=self.colors["secondary"],
            fg="#ecf0f1",
            insertbackground="#ecf0f1",
            wrap=tk.WORD,
            height=12
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors["primary"], height=35)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_text = tk.Label(
            status_frame,
            text="🛡️ Punctaj Update Manager - Pregătit",
            font=("Segoe UI", 10),
            bg=self.colors["primary"],
            fg="white"
        )
        self.status_text.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Închidere
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def log(self, message, level="INFO"):
        """Adaugă mesaj în jurnal cu timestamp și formatare"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding pentru nivele
        color_map = {
            "INFO": "#3498db",
            "SUCCESS": "#27ae60", 
            "WARNING": "#e67e22",
            "ERROR": "#e74c3c",
            "CMD": "#9b59b6"
        }
        
        # Icon mapping
        icon_map = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️", 
            "ERROR": "❌",
            "CMD": "⚡"
        }
        
        icon = icon_map.get(level, "📝")
        log_entry = f"[{timestamp}] {icon} {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
        print(f"{log_entry.strip()}")  # Console output
    
    def update_progress(self, value, text=""):
        """Actualizează bara de progres"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update()
    
    def update_status(self, text):
        """Actualizează status bar"""
        self.status_text.config(text=f"🛡️ {text}")
        self.root.update()
    
    def run_git_command(self, command, cwd=None):
        """Execută comandă git cu handling îmbunătățit"""
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
                encoding='utf-8',
                errors='replace',  # Înlocuiește caractere problematice
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    self.log(f"Rezultat: {output}", "SUCCESS")
                return True, output
            else:
                error = result.stderr.strip()
                self.log(f"Eroare git: {error}", "ERROR")
                return False, error
                
        except subprocess.TimeoutExpired:
            self.log("Timeout la execuția git - operația a durat prea mult", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self.log(f"Excepție git: {e}", "ERROR")
            return False, str(e)
    
    def startup_checks(self):
        """Verificări la startup"""
        self.log(f"📁 Working directory: {self.repo_path}")
        self.log("Începând verificările de sistem...")
        self.update_status("Verificând sistemul...")
        
        # Verifică git status
        success, _ = self.run_git_command("git status --porcelain")
        if success:
            self.status_labels["git_status"].config(
                text="🔗 Git Status: ✅ Repository valid",
                fg=self.colors["success"]
            )
        else:
            self.status_labels["git_status"].config(
                text="🔗 Git Status: ❌ Eroare repository",
                fg=self.colors["error"]
            )
        
        # Verifică aplicația Punctaj
        self.check_punctaj_app()
        
        # Verifică config files
        self.check_config_files()
        
        self.update_status("Sistem verificat - Gata pentru actualizări")
        self.log("Verificări de sistem completate")
    
    def check_punctaj_app(self):
        """Verifică statusul aplicației Punctaj"""
        punctaj_files = [
            "punctaj.py",
            "dist/Punctaj.exe",
            "Punctaj.exe"
        ]
        
        found_app = False
        for file_path in punctaj_files:
            full_path = os.path.join(self.repo_path, file_path)
            if os.path.exists(full_path):
                self.status_labels["punctaj_status"].config(
                    text=f"🛡️ Aplicația Punctaj: ✅ Găsită ({file_path})",
                    fg=self.colors["success"]
                )
                found_app = True
                break
        
        if not found_app:
            self.status_labels["punctaj_status"].config(
                text="🛡️ Aplicația Punctaj: ⚠️ Nu a fost găsită",
                fg=self.colors["warning"]
            )
    
    def check_config_files(self):
        """Verifică fișierele importante pentru git & aplicație"""
        important_files = ["punctaj.py", ".git", "README.md", "requirements.txt"]
        found_files = []
        
        for file_name in important_files:
            file_path = os.path.join(self.repo_path, file_name)
            if os.path.exists(file_path):
                found_files.append(file_name)
        
        if len(found_files) >= 2:  # Cel puțin 2 fișiere importante găsite
            self.status_labels["config_status"].config(
                text=f"⚙️ Fișiere importante: ✅ {len(found_files)} găsite",
                fg=self.colors["success"]
            )
        else:
            self.status_labels["config_status"].config(
                text=f"⚙️ Fișiere importante: ⚠️ Doar {len(found_files)} găsite",
                fg=self.colors["warning"]
            )
    
    def check_updates(self):
        """Verifică actualizări disponibile"""
        if self.is_updating:
            return
        
        def check_thread():
            self.is_updating = True
            self.check_button.config(state=tk.DISABLED)
            self.update_status("Verificând actualizări...")
            
            try:
                self.update_progress(10, "Conectând la repository...")
                success, _ = self.run_git_command("git fetch origin")
                
                if not success:
                    messagebox.showerror(
                        "Eroare Conexiune", 
                        "Nu pot verifica actualizările!\n\n"
                        "Verifică:\n"
                        "• Conexiunea la internet\n"
                        "• Configurația git\n"
                        "• Repository remote"
                    )
                    return
                
                self.update_progress(50, "Comparând versiunile...")
                
                # Verifică pentru main sau master
                branches_to_check = ["origin/main", "origin/master"]
                updates_found = False
                
                for branch in branches_to_check:
                    success, output = self.run_git_command(f"git log HEAD..{branch} --oneline")
                    if success and output.strip():
                        lines = output.strip().split('\n')
                        count = len([line for line in lines if line.strip()])
                        
                        if count > 0:
                            updates_found = True
                            self.log(f"Găsite {count} actualizări în {branch}:")
                            for line in lines[:5]:  # Primele 5
                                if line.strip():
                                    self.log(f"  • {line.strip()}")
                            
                            if count > 5:
                                self.log(f"  ... și încă {count - 5} actualizări")
                            
                            self.update_progress(100, f"{count} actualizări disponibile")
                            
                            messagebox.showinfo(
                                "🔄 Actualizări Disponibile",
                                f"Găsite {count} actualizări pentru Punctaj!\n\n"
                                f"📋 Vezi jurnalul pentru detalii\n"
                                f"⬇️ Apasă 'Git Pull Actualizări' pentru a le instala"
                            )
                            break
                
                if not updates_found:
                    self.update_progress(100, "Aplicația este la zi")
                    self.log("Nu sunt actualizări disponibile")
                    messagebox.showinfo(
                        "✅ La Zi",
                        "🛡️ Aplicația Punctaj este deja la ultima versiune!\n\n"
                        "Nu sunt necesare actualizări."
                    )
            
            finally:
                self.is_updating = False
                self.check_button.config(state=tk.NORMAL)
                self.update_status("Verificare completă")
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def start_update(self):
        """Începe procesul de actualizare SIMPLU - doar git pull"""
        if self.is_updating:
            return
        
        # Confirmă actualizarea simplă
        if not messagebox.askyesno(
            "🔄 Actualizare Punctaj",
            "Vei actualiza aplicația Punctaj cu ultimele modificări de pe git.\n\n"
            "⚡ Procesul va face DOAR:\n"
            "• Git pull pentru descărcare modificări\n"
            "• Stash pentru modificări locale (dacă e necesar)\n"
            "• Nu include backup sau restart\n\n"
            "Continuă actualizarea?"
        ):
            return
        
        def update_thread():
            self.is_updating = True  
            self.update_button.config(state=tk.DISABLED)
            self.check_button.config(state=tk.DISABLED)
            
            try:
                self.log("🚀 Începând actualizarea git pull...", "INFO")
                self.update_progress(10, "Verificând repository...")
                
                # Verifică dacă există uncommited changes
                self.update_progress(20, "Verificând modificări locale...")
                success, output = self.run_git_command("git status --porcelain")
                
                stash_created = False
                if success and output.strip():
                    self.log("Găsite modificări locale - fac stash...", "WARNING")
                    self.update_progress(30, "Salvând modificări locale...")
                    
                    success, stash_output = self.run_git_command("git stash push -m \"auto-stash-before-update\"")
                    if success:
                        stash_created = True
                        self.log("Modificări locale salvate în stash", "SUCCESS")
                    else:
                        self.log(f"Eroare la stash: {stash_output}", "ERROR")
                        messagebox.showerror("Eroare", f"Nu pot salva modificările locale:\n{stash_output}")
                        return
                
                # Git pull - operația principală
                self.update_progress(60, "Descărcând actualizări din git...")
                self.log("📥 Executând git pull...", "CMD")
                success, output = self.run_git_command("git pull origin")
                
                if success:
                    if "Already up to date" in output or "Already up-to-date" in output:
                        self.update_progress(100, "Deja la zi - nicio actualizare")
                        self.log("✅ Aplicația era deja la ultima versiune", "SUCCESS")
                        
                        # Recuperez stash-ul dacă l-am făcut
                        if stash_created:
                            self.update_progress(90, "Recuperând modificări locale...")
                            self.run_git_command("git stash pop")
                            self.log("Modificări locale recuperate", "SUCCESS")
                        
                        messagebox.showinfo(
                            "✅ La Zi",
                            "🛡️ Punctaj era deja la ultima versiune!\n\nNu au fost găsite actualizări noi."
                        )
                    else:
                        # Actualizare cu succes
                        self.update_progress(80, "Actualizări descărcate cu succes")
                        self.log("✅ GIT PULL COMPLETAT CU SUCCES!", "SUCCESS")
                        self.log(f"📋 Modificări aplicate:\n{output}", "SUCCESS")
                        
                        # Întreabă despre recuperarea modificărilor locale
                        if stash_created:
                            self.update_progress(90, "Verificând recuperare modificări...")
                            if messagebox.askyesno("Recuperare modificari", 
                                                 "Actualizarea s-a completat cu succes!\n\n"
                                                 "Vrei sa recuperez modificarile locale salvate?"):
                                self.run_git_command("git stash pop")
                                self.log("Modificări locale recuperate", "SUCCESS")
                            else:
                                self.log("Modificări locale păstrate în stash", "INFO")
                        
                        self.update_progress(100, "Actualizare git completă!")
                        
                        messagebox.showinfo(
                            "🎉 Actualizare Completă",  
                            "✅ Git pull executat cu succes!\n\n"
                            "📋 Modificările au fost descărcate\n"
                            "🔧 Aplicația poate fi folosită normal\n\n"
                            "📝 Vezi jurnalul pentru detalii complete"
                        )
                else:
                    self.update_progress(0, "Git pull eșuat")
                    self.log(f"❌ EROARE GIT PULL: {output}", "ERROR")
                    messagebox.showerror(
                        "❌ Eroare Git Pull",
                        f"Actualizarea git a eșuat!\n\n"
                        f"Eroare: {output}\n\n"
                        f"Verifică conexiunea și jurnalul pentru detalii"
                    )
            
            except Exception as e:
                self.log(f"Excepție în timpul git pull: {e}", "ERROR")
                messagebox.showerror("Eroare", f"Eroare neașteptată la git pull:\n{e}")
            
            finally:
                self.is_updating = False
                self.update_button.config(state=tk.NORMAL)
                self.check_button.config(state=tk.NORMAL)
                self.update_status("gata pentru actualizări")
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def show_git_status(self):
        """Afișează status git detaliat pentru diagnosticare"""
        self.log("🔍 Verificând status git detaliat...", "INFO")
        
        status_commands = [
            ("git status", "Status curent"),
            ("git log --oneline -5", "Ultimele 5 commit-uri"),
            ("git remote -v", "Remote repositories"),
            ("git branch -a", "Branch-uri disponibile")
        ]
        
        for command, description in status_commands:
            self.log(f"\n📋 {description}:", "INFO")
            success, output = self.run_git_command(command)
            if success:
                if output.strip():
                    self.log(output, "SUCCESS")
                else:
                    self.log("(fără output)", "INFO")
            else:
                self.log(f"Eroare: {output}", "ERROR")
    
    def on_closing(self):
        """Handler pentru închiderea aplicației"""
        if self.is_updating:
            if messagebox.askyesno(
                "Actualizare în Progres",
                "🔄 O actualizare git pull este în progres.\n\n"
                "Închiderea acum poate lăsa sistemul într-o stare inconsistentă.\n\n"
                "Ești sigur că vrei să închizi Punctaj Update?"
            ):
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Pornește aplicația"""
        self.root.mainloop()

# Entry point
if __name__ == "__main__":
    print(f"🛡️ {APP_NAME} v{VERSION}")
    
    # Determină path-ul corect
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir.endswith('dist'):
        repo_path = os.path.dirname(current_dir)
    else:
        repo_path = current_dir
        
    print(f"📁 Git Repository: {repo_path}")
    print("=" * 60)
    
    app = PunctajUpdater()
    app.run()