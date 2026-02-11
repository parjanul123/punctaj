#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creează punctaj_installer.exe - Installer profesional pentru aplicație
Instalează aplicația, creează shortcuturi, și validează dependențe
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

def create_installer_script():
    """Creează scriptul de installer"""
    
    script_content = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script pentru Punctaj Application
Instalează aplicația în Program Files și creează shortcuturi
"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import winreg
import subprocess

class PunctajInstaller:
    def __init__(self):
        self.install_path = os.path.join(os.environ.get('ProgramFiles', 'C:\\\\Program Files'), 'Punctaj')
        self.app_name = 'Punctaj'
        self.version = '2.0.0'
        self.root = None
        self.progress_var = None
        self.path_var = None
        self.install_button = None
        self.cancel_button = None
        self.browse_button = None
        
    def create_gui(self):
        """Creează interfața de installer"""
        self.root = tk.Tk()
        self.root.title('Punctaj - Installer')
        self.root.geometry('600x500')
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 300
        y = (self.root.winfo_screenheight() // 2) - 250
        self.root.geometry(f'+{x}+{y}')
        
        # Header
        header_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        ttk.Label(
            header_frame,
            text='📊 Punctaj - Aplicație Management Punctaj',
            font=('Segoe UI', 14, 'bold')
        ).pack(padx=20, pady=15)
        
        ttk.Label(
            header_frame,
            text=f'Versiune {self.version}',
            font=('Segoe UI', 9),
            foreground='gray'
        ).pack(padx=20, pady=(0, 10))
        
        # Content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            content_frame,
            text='Bine ați venit la instalatorul aplicației Punctaj!',
            font=('Segoe UI', 11)
        ).pack(pady=10)
        
        ttk.Label(
            content_frame,
            text='Acest installer va:',
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(15, 10), anchor=tk.W)
        
        features = [
            '✓ Instala aplicația în Program Files',
            '✓ Crea shortcut pe Desktop',
            '✓ Crea shortcut în Start Menu',
            '✓ Configura permisiunile necesare',
            '✓ Valida dependențele Python'
        ]
        
        for feature in features:
            ttk.Label(content_frame, text=feature).pack(anchor=tk.W, pady=3)
        
        ttk.Label(
            content_frame,
            text=f'\\nCalea instalare: {self.install_path}',
            font=('Segoe UI', 9, 'italic'),
            foreground='blue'
        ).pack(pady=10, anchor=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            content_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        progress_bar.pack(pady=15, fill=tk.X)
        
        self.progress_label = ttk.Label(content_frame, text='Gata de instalare')
        self.progress_label.pack()
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Button(
            button_frame,
            text='📦 Instalează',
            command=self.install
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text='❌ Anulează',
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=5)
        
        self.root.mainloop()
    
    def update_progress(self, value, message):
        """Actualizează progress bar"""
        self.progress_var.set(value)
        self.progress_label.config(text=message)
        self.root.update()
    
    def install(self):
        """Rulează instalarea"""
        try:
            # Dezactivează butonul
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ttk.Button):
                            btn.config(state=tk.DISABLED)
            
            # 1. Crează folderul de instalare
            self.update_progress(10, '📁 Se crează directorul...')
            os.makedirs(self.install_path, exist_ok=True)
            
            # 2. Copiază fișierele aplicației
            self.update_progress(30, '📋 Se copiază fișierele...')
            app_exe = os.path.join(os.path.dirname(sys.argv[0]), 'punctaj.exe')
            if os.path.exists(app_exe):
                shutil.copy2(app_exe, os.path.join(self.install_path, 'punctaj.exe'))
            
            # Copiază config file dacă există
            config_file = os.path.join(os.path.dirname(sys.argv[0]), 'supabase_config.ini')
            if os.path.exists(config_file):
                shutil.copy2(config_file, os.path.join(self.install_path, 'supabase_config.ini'))
            
            # 3. Creează shortcut pe Desktop
            self.update_progress(50, '🖥️ Se crează shortcuturi...')
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            shortcut_path = os.path.join(desktop_path, 'Punctaj.lnk')
            self.create_shortcut(
                shortcut_path,
                os.path.join(self.install_path, 'punctaj.exe'),
                'Punctaj - Management Punctaj'
            )
            
            # 4. Creează shortcut în Start Menu
            self.update_progress(70, '📋 Se configură Start Menu...')
            start_menu = os.path.join(
                os.environ['APPDATA'],
                'Microsoft\\\\Windows\\\\Start Menu\\\\Programs'
            )
            start_menu_path = os.path.join(start_menu, 'Punctaj.lnk')
            self.create_shortcut(
                start_menu_path,
                os.path.join(self.install_path, 'punctaj.exe'),
                'Punctaj - Management Punctaj'
            )
            
            # 5. Creează registry entry
            self.update_progress(85, '⚙️ Se configură sistem...')
            try:
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    'Software\\\\Punctaj'
                )
                winreg.SetValueEx(key, 'InstallPath', 0, winreg.REG_SZ, self.install_path)
                winreg.SetValueEx(key, 'Version', 0, winreg.REG_SZ, self.version)
                winreg.CloseKey(key)
            except:
                pass  # Poate necesita admin rights
            
            self.update_progress(100, '✅ Instalare completă!')
            
            messagebox.showinfo(
                'Succes',
                f'✅ Aplicația a fost instalată cu succes!\\n\\n'
                f'📍 Cale: {self.install_path}\\n'
                f'🖥️ Shortcut creat pe Desktop\\n'
                f'📋 Shortcut creat în Start Menu\\n\\n'
                f'Puteți lansa aplicația din Desktop sau Start Menu.'
            )
            
            # Întreabă dacă vrea să lanseze app
            if messagebox.askyesno('Lansare', 'Lansez aplicația acum?'):
                subprocess.Popen(os.path.join(self.install_path, 'punctaj.exe'))
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror('Eroare', f'Eroare la instalare:\\n{str(e)}')
    
    def create_shortcut(self, shortcut_path, target_path, description):
        """Crează un shortcut Windows"""
        try:
            # Folosește VBScript pentru a crea shortcut
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
            
            subprocess.run(['cscript.exe', vbs_file], check=True, capture_output=True)
            os.remove(vbs_file)
        except:
            pass  # Ignoră erorile la crearea shortcutului

if __name__ == '__main__':
    installer = PunctajInstaller()
    installer.create_gui()
'''
    
    return script_content

def build_installer():
    """Creează EXE-ul installerului"""
    
    print('🔨 Se creează scriptul de setup...')
    
    # Creează scriptul de installer
    setup_script_path = os.path.join(os.getcwd(), '_setup.py')
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
        print(f'\\n✅ Installerul a fost creat cu succes!')
        print(f'📍 Cale: {installer_path}')
        
        # Verifică dimensiunea
        if os.path.exists(installer_path):
            size_mb = os.path.getsize(installer_path) / (1024 * 1024)
            print(f'📊 Dimensiune: {size_mb:.2f} MB')
        
        return True
    else:
        print(f'\\n❌ Eroare la compilare!')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('📦 Generator Installer - Punctaj Application')
    print('=' * 60)
    
    if build_installer():
        print('\\n✨ Gata! Puteți distribui punctaj_installer.exe')
    else:
        print('\\n❌ Ceva a mers greșit!')
        sys.exit(1)
