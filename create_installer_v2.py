#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creează punctaj_installer.exe - Installer profesional pentru aplicație
Instalează aplicația, creează shortcuturi, și validează dependențe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_installer_script():
    """Creează scriptul de installer"""
    
    script_content = r"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Setup Script pentru Punctaj Application
Instalează aplicația în locația dorită și creează shortcuturi
'''

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import winreg
import subprocess

class PunctajInstaller:
    def __init__(self):
        self.default_path = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Punctaj')
        self.install_path = self.default_path
        self.app_name = 'Punctaj'
        self.version = '2.0.0'
        self.root = None
        self.progress_var = None
        self.path_var = None
        self.install_button = None
        self.cancel_button = None
        self.installing = False
        
    def create_gui(self):
        """Creează interfața de installer"""
        self.root = tk.Tk()
        self.root.title('Punctaj - Installer')
        self.root.geometry('750x700')
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 375
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f'+{x}+{y}')
        
        # Header
        header_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        ttk.Label(
            header_frame,
            text='📊 Punctaj - Instalator Aplicație',
            font=('Segoe UI', 16, 'bold')
        ).pack(padx=20, pady=15)
        
        ttk.Label(
            header_frame,
            text=f'Versiune {self.version}',
            font=('Segoe UI', 10),
            foreground='gray'
        ).pack(padx=20, pady=(0, 10))
        
        # Content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        ttk.Label(
            content_frame,
            text='Bine ați venit la instalatorul aplicației Punctaj!',
            font=('Segoe UI', 12, 'bold')
        ).pack(pady=10, anchor=tk.W)
        
        ttk.Label(
            content_frame,
            text='Acest installer va realiza următoarele acțiuni:',
            font=('Segoe UI', 10)
        ).pack(pady=(15, 10), anchor=tk.W)
        
        features = [
            '✓ Instala aplicația în locația aleasă',
            '✓ Crea shortcut pe Desktop',
            '✓ Crea shortcut în Start Menu',
            '✓ Configura permisiunile necesare',
            '✓ Inregistra aplicația în sistem'
        ]
        
        for feature in features:
            ttk.Label(content_frame, text=feature, font=('Segoe UI', 10)).pack(anchor=tk.W, pady=4)
        
        # Installation path selection
        ttk.Label(
            content_frame,
            text='📁 Selectează locația de instalare:',
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(20, 10), anchor=tk.W)
        
        path_frame = ttk.Frame(content_frame)
        path_frame.pack(fill=tk.X, pady=8)
        
        self.path_var = tk.StringVar(value=self.default_path)
        
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.path_var,
            font=('Segoe UI', 10),
            width=55
        )
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        browse_button = ttk.Button(
            path_frame,
            text='Răsfoire...',
            command=self.browse_folder,
            width=15
        )
        browse_button.pack(side=tk.LEFT)
        
        # Progress bar
        ttk.Label(
            content_frame,
            text='Progres instalare:',
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(20, 8), anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            content_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        progress_bar.pack(pady=(0, 5), fill=tk.X)
        
        self.progress_label = ttk.Label(
            content_frame,
            text='Gata de instalare',
            font=('Segoe UI', 10),
            foreground='blue'
        )
        self.progress_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=25, pady=20)
        
        self.install_button = ttk.Button(
            button_frame,
            text='📦 Instalează Acum',
            command=self.install,
            width=25
        )
        self.install_button.pack(side=tk.LEFT, padx=8)
        
        self.cancel_button = ttk.Button(
            button_frame,
            text='❌ Anulează',
            width=25,
            command=self.on_cancel
        )
        self.cancel_button.pack(side=tk.LEFT, padx=8)
        
        self.root.mainloop()
    
    def browse_folder(self):
        """Permite selectarea unei cale custom"""
        try:
            folder = filedialog.askdirectory(
                title='Selectează locația de instalare',
                initialdir=self.path_var.get()
            )
            if folder:
                self.install_path = folder
                self.path_var.set(folder)
        except Exception as e:
            messagebox.showerror('Eroare', f'Eroare la selectare folder: {e}')
    
    def on_cancel(self):
        """Gestionează anularea"""
        if self.installing:
            if messagebox.askyesno('Confirmare', 'Instalarea este în curs. Sigur vreți să anulați?'):
                sys.exit(0)
        else:
            self.root.quit()
    
    def update_progress(self, value, message):
        """Actualizează progress bar"""
        self.progress_var.set(min(value, 100))
        self.progress_label.config(text=message)
        self.root.update()
        self.root.after(10)
    
    def install(self):
        """Rulează instalarea"""
        if self.installing:
            return
        
        self.installing = True
        self.install_path = self.path_var.get()
        
        # Dezactivează butoane
        self.install_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        path_entries = [w for w in self.root.winfo_children() if isinstance(w, ttk.Frame)]
        
        try:
            # 1. Crează folderul de instalare
            self.update_progress(10, '📁 Se crează directorul de instalare...')
            os.makedirs(self.install_path, exist_ok=True)
            
            # 2. Copiază fișierele aplicației
            self.update_progress(30, '📋 Se copiază fișierele aplicației...')
            app_exe = os.path.join(os.path.dirname(sys.argv[0]), 'punctaj.exe')
            if os.path.exists(app_exe):
                shutil.copy2(app_exe, os.path.join(self.install_path, 'punctaj.exe'))
                self.update_progress(50, '✓ Fișier principal copiat')
            
            # Copiază config file dacă există
            config_file = os.path.join(os.path.dirname(sys.argv[0]), 'supabase_config.ini')
            if os.path.exists(config_file):
                shutil.copy2(config_file, os.path.join(self.install_path, 'supabase_config.ini'))
                self.update_progress(60, '✓ Configurație copiată')
            
            # 3. Creează shortcut pe Desktop
            self.update_progress(70, '🖥️ Se creează shortcut pe Desktop...')
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            self.create_shortcut(
                os.path.join(desktop_path, 'Punctaj.lnk'),
                os.path.join(self.install_path, 'punctaj.exe'),
                'Punctaj - Management Punctaj'
            )
            
            # 4. Creează shortcut în Start Menu
            self.update_progress(80, '📋 Se configurează Start Menu...')
            start_menu = os.path.join(
                os.environ['APPDATA'],
                'Microsoft\\Windows\\Start Menu\\Programs'
            )
            self.create_shortcut(
                os.path.join(start_menu, 'Punctaj.lnk'),
                os.path.join(self.install_path, 'punctaj.exe'),
                'Punctaj - Management Punctaj'
            )
            
            # 5. Creează registry entry
            self.update_progress(90, '⚙️ Se configurează sistem...')
            try:
                key = winreg.CreateKey(
                    winreg.HKEY_CURRENT_USER,
                    'Software\\Punctaj'
                )
                winreg.SetValueEx(key, 'InstallPath', 0, winreg.REG_SZ, self.install_path)
                winreg.SetValueEx(key, 'Version', 0, winreg.REG_SZ, self.version)
                winreg.CloseKey(key)
            except Exception as e:
                print(f'Registry error: {e}')
            
            self.update_progress(100, '✅ Instalare completă!')
            
            messagebox.showinfo(
                'Instalare Reușită',
                f'✅ Aplicația a fost instalată cu succes!\\n\\n'
                f'📍 Cale instalare: {self.install_path}\\n'
                f'🖥️ Shortcut pe Desktop\\n'
                f'📋 Shortcut în Start Menu\\n\\n'
                f'Puteți lansa aplicația din Desktop sau Start Menu.'
            )
            
            # Întreabă dacă vrea să lanseze app
            if messagebox.askyesno('Lansare', 'Lansez aplicația acum?'):
                subprocess.Popen(os.path.join(self.install_path, 'punctaj.exe'))
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror('Eroare la Instalare', f'❌ Eroare:\\n{str(e)}')
            self.installing = False
            self.install_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)
    
    def create_shortcut(self, shortcut_path, target_path, description):
        """Crează un shortcut Windows"""
        try:
            vbs_script = f"""Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_path}"
oLink.Description = "{description}"
oLink.WorkingDirectory = "{os.path.dirname(target_path)}"
oLink.Save
"""
            vbs_file = os.path.join(os.environ['TEMP'], 'create_shortcut.vbs')
            with open(vbs_file, 'w', encoding='utf-8') as f:
                f.write(vbs_script)
            
            subprocess.run(['cscript.exe', vbs_file], check=False, capture_output=True)
            try:
                os.remove(vbs_file)
            except:
                pass
        except Exception as e:
            print(f'Shortcut error: {e}')

if __name__ == '__main__':
    installer = PunctajInstaller()
    installer.create_gui()
"""
    
    return script_content

def build_installer():
    """Creează EXE-ul installerului"""
    
    print('🔨 Se creează scriptul de setup...')
    
    # Creează scriptul de installer
    setup_script_path = os.path.join(os.getcwd(), '_setup_v2.py')
    with open(setup_script_path, 'w', encoding='utf-8') as f:
        f.write(create_installer_script())
    
    print(f'✅ Script de setup creat: {setup_script_path}')
    
    # Copie EXE-ul aplicației
    dist_exe = os.path.join(os.getcwd(), 'dist', 'punctaj.exe')
    dist_config = os.path.join(os.getcwd(), 'dist', 'supabase_config.ini')
    
    if not os.path.exists(dist_exe):
        print(f'❌ Eroare: {dist_exe} nu există!')
        return False
    
    print(f'📦 Copiez aplicația din {dist_exe}...')
    
    # Creează PyInstaller executable din scriptul de installer
    print('🔨 Se compilează installerul cu PyInstaller...')
    
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'punctaj_installer',
        '--distpath', 'dist',
        '--icon=NONE',
        '--add-data', f'{dist_exe}:.',
    ]
    
    # Adaugă config file dacă există
    if os.path.exists(dist_config):
        cmd.extend(['--add-data', f'{dist_config}:.'])
    
    cmd.append(setup_script_path)
    
    print(f'Comandă: {" ".join(cmd)}')
    
    result = subprocess.run(cmd, cwd=os.getcwd())
    
    if result.returncode == 0:
        installer_path = os.path.join(os.getcwd(), 'dist', 'punctaj_installer.exe')
        print(f'\n✅ Installerul a fost creat cu succes!')
        print(f'📍 Cale: {installer_path}')
        
        # Verifică dimensiunea
        if os.path.exists(installer_path):
            size_mb = os.path.getsize(installer_path) / (1024 * 1024)
            print(f'📊 Dimensiune: {size_mb:.2f} MB')
        
        return True
    else:
        print(f'\n❌ Eroare la compilare!')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('📦 Generator Installer v2 - Punctaj Application')
    print('=' * 60)
    
    if build_installer():
        print('\n✨ Gata! Puteți distribui punctaj_installer.exe')
    else:
        print('\n❌ Ceva a mers greșit!')
        sys.exit(1)
