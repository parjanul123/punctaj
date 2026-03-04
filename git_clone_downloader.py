#!/usr/bin/env python3
"""
Git Clone Downloader - Punctaj Project
Permite selectarea unei locații și descărcarea proiectului de pe GitHub
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
from pathlib import Path
import threading

class GitCloneDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Punctaj Project - Git Clone Downloader")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Repository URL
        self.repo_url = "https://github.com/parjanul123/punctaj.git"
        
        # Variables
        self.selected_path = tk.StringVar()
        self.progress_var = tk.StringVar()
        self.progress_var.set("Selectează o locație pentru descărcare...")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurează interfața utilizator"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Punctaj Project - Downloader", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Repository info
        repo_frame = ttk.LabelFrame(main_frame, text="Informații Repository", padding="10")
        repo_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        repo_frame.columnconfigure(1, weight=1)
        
        ttk.Label(repo_frame, text="URL Repository:").grid(row=0, column=0, sticky=tk.W, pady=2)
        url_entry = ttk.Entry(repo_frame, textvariable=tk.StringVar(value=self.repo_url), 
                             state='readonly', font=('Consolas', 9))
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Path selection frame
        path_frame = ttk.LabelFrame(main_frame, text="Selectare Locație", padding="10")
        path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)
        
        # Path selection
        path_selection_frame = ttk.Frame(path_frame)
        path_selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_selection_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_selection_frame, textvariable=self.selected_path, 
                                   font=('Consolas', 9))
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(path_selection_frame, text="Selectează Folder", 
                               command=self.browse_folder)
        browse_btn.grid(row=0, column=1)
        
        # Info text
        info_text = tk.Text(path_frame, height=6, wrap=tk.WORD, font=('Arial', 9))
        info_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        path_frame.rowconfigure(1, weight=1)
        
        info_content = """Instrucțiuni:
1. Selectează un folder de pe disc unde vrei să descarci proiectul
2. Apasă butonul "Descarcă Proiect" pentru a începe descărcarea
3. Proiectul va fi descărcat într-un subfolder numit "punctaj"

Cerințe:
- Git trebuie să fie instalat pe sistem
- Conexiune la internet activă"""
        
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        # Progress and controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        controls_frame.columnconfigure(0, weight=1)
        
        # Progress label
        self.progress_label = ttk.Label(controls_frame, textvariable=self.progress_var, 
                                       font=('Arial', 9))
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.download_btn = ttk.Button(buttons_frame, text="Descarcă Proiect", 
                                      command=self.start_download, style='Accent.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(buttons_frame, text="Deschide Folder", 
                                         command=self.open_download_folder, state='disabled')
        self.open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = ttk.Button(buttons_frame, text="Ieșire", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT)
        
    def browse_folder(self):
        """Deschide dialog pentru selectarea folderului"""
        folder_path = filedialog.askdirectory(
            title="Selectează folderul pentru descărcarea proiectului",
            initialdir=str(Path.home() / "Desktop")
        )
        
        if folder_path:
            self.selected_path.set(folder_path)
            self.progress_var.set(f"Locație selectată: {folder_path}")
            
    def check_git_installed(self):
        """Verifică dacă Git este instalat"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
            
    def start_download(self):
        """Începe procesul de descărcare într-un thread separat"""
        if not self.selected_path.get():
            messagebox.showerror("Eroare", "Te rog să selectezi mai întâi un folder de destinație!")
            return
            
        if not self.check_git_installed():
            messagebox.showerror(
                "Git nu este instalat", 
                "Git nu a fost găsit pe sistem.\n\n"
                "Te rog să instalezi Git de la: https://git-scm.com/download/win\n"
                "și să restartezi această aplicație."
            )
            return
            
        # Disable button and start progress
        self.download_btn.config(state='disabled')
        self.open_folder_btn.config(state='disabled')
        self.progress_bar.start()
        
        # Start download in separate thread
        download_thread = threading.Thread(target=self.download_project, daemon=True)
        download_thread.start()
        
    def download_project(self):
        """Execută git clone în thread separat"""
        try:
            target_path = Path(self.selected_path.get())
            project_path = target_path / "punctaj"
            
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Verificare locație..."))
            
            # Check if target directory already exists
            if project_path.exists():
                response = messagebox.askyesno(
                    "Folderul există", 
                    f"Folderul 'punctaj' există deja în locația selectată.\n\n"
                    f"Vrei să îl ștergi și să descarci din nou proiectul?",
                    icon='warning'
                )
                if not response:
                    self.download_complete(False, "Descărcare anulată de utilizator.")
                    return
                    
                # Remove existing directory
                self.root.after(0, lambda: self.progress_var.set("Ștergere folder existent..."))
                import shutil
                shutil.rmtree(project_path)
            
            # Update progress
            self.root.after(0, lambda: self.progress_var.set("Descărcare proiect de pe GitHub..."))
            
            # Change to target directory
            original_cwd = os.getcwd()
            os.chdir(target_path)
            
            # Execute git clone
            process = subprocess.Popen(
                ['git', 'clone', self.repo_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Read output
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    # Update progress with last line
                    self.root.after(0, lambda line=output.strip(): 
                                   self.progress_var.set(f"Git: {line}"))
            
            # Get return code
            return_code = process.poll()
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if return_code == 0:
                self.download_complete(True, f"Proiect descărcat cu succes în:\n{project_path}")
            else:
                error_output = '\n'.join(output_lines[-5:])  # Last 5 lines
                self.download_complete(False, f"Eroare la descărcare:\n{error_output}")
                
        except Exception as e:
            self.download_complete(False, f"Eroare neașteptată: {str(e)}")
            
    def download_complete(self, success, message):
        """Callback când descărcarea s-a terminat"""
        self.root.after(0, lambda: self.progress_bar.stop())
        self.root.after(0, lambda: self.download_btn.config(state='normal'))
        
        if success:
            self.root.after(0, lambda: self.progress_var.set("Descărcare completă cu succes!"))
            self.root.after(0, lambda: self.open_folder_btn.config(state='normal'))
            self.root.after(0, lambda: messagebox.showinfo("Succes", message))
        else:
            self.root.after(0, lambda: self.progress_var.set("Eroare la descărcare."))
            self.root.after(0, lambda: messagebox.showerror("Eroare", message))
            
    def open_download_folder(self):
        """Deschide folderul unde a fost descărcat proiectul"""
        if self.selected_path.get():
            project_path = Path(self.selected_path.get()) / "punctaj"
            if project_path.exists():
                os.startfile(str(project_path))
            else:
                messagebox.showerror("Eroare", "Folderul proiectului nu a fost găsit!")
                
    def run(self):
        """Pornește aplicația"""
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start main loop
        self.root.mainloop()

def main():
    """Funcție principală"""
    try:
        app = GitCloneDownloader()
        app.run()
    except Exception as e:
        messagebox.showerror("Eroare critică", f"Eroare la pornirea aplicației:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()