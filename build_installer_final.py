#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creează punctaj_installer.exe - Installer profesional pentru aplicație
"""

import os
import sys
import shutil
import subprocess

def create_installer_script():
    """Creează scriptul de installer"""
    # Construiești script-ul ca string normal
    lines = [
        "#!/usr/bin/env python3",
        "# -*- coding: utf-8 -*-",
        "'''",
        "Setup Script pentru Punctaj Application",
        "'''",
        "",
        "import os",
        "import sys",
        "import shutil",
        "import tkinter as tk",
        "from tkinter import ttk, messagebox, filedialog",
        "import winreg",
        "import subprocess",
        "",
        "class PunctajInstaller:",
        "    def __init__(self):",
        "        self.default_path = os.path.join(os.environ.get('ProgramFiles', 'C:\\\\Program Files'), 'Punctaj')",
        "        self.install_path = self.default_path",
        "        self.app_name = 'Punctaj'",
        "        self.version = '2.0.0'",
        "        self.root = None",
        "        self.progress_var = None",
        "        self.path_var = None",
        "        self.install_button = None",
        "        self.cancel_button = None",
        "        self.installing = False",
        "    ",
        "    def create_gui(self):",
        "        self.root = tk.Tk()",
        "        self.root.title('Punctaj - Installer')",
        "        self.root.geometry('750x700')",
        "        self.root.resizable(False, False)",
        "        ",
        "        self.root.update_idletasks()",
        "        x = (self.root.winfo_screenwidth() // 2) - 375",
        "        y = (self.root.winfo_screenheight() // 2) - 350",
        "        self.root.geometry(f'+{x}+{y}')",
        "        ",
        "        header_frame = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=2)",
        "        header_frame.pack(fill=tk.X, padx=0, pady=0)",
        "        ",
        "        ttk.Label(header_frame, text='📊 Punctaj - Instalator Aplicație', font=('Segoe UI', 16, 'bold')).pack(padx=20, pady=15)",
        "        ttk.Label(header_frame, text=f'Versiune {self.version}', font=('Segoe UI', 10), foreground='gray').pack(padx=20, pady=(0, 10))",
        "        ",
        "        content_frame = ttk.Frame(self.root)",
        "        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)",
        "        ",
        "        ttk.Label(content_frame, text='Bine ați venit la instalatorul Punctaj!', font=('Segoe UI', 12, 'bold')).pack(pady=10, anchor=tk.W)",
        "        ttk.Label(content_frame, text='Acest installer va realiza următoarele acțiuni:', font=('Segoe UI', 10)).pack(pady=(15, 10), anchor=tk.W)",
        "        ",
        "        features = ['✓ Instala aplicația în locația aleasă', '✓ Crea shortcut pe Desktop', '✓ Crea shortcut în Start Menu', '✓ Configura permisiunile necesare', '✓ Inregistra în sistem']",
        "        for feature in features:",
        "            ttk.Label(content_frame, text=feature, font=('Segoe UI', 10)).pack(anchor=tk.W, pady=4)",
        "        ",
        "        ttk.Label(content_frame, text='📁 Selectează locația de instalare:', font=('Segoe UI', 11, 'bold')).pack(pady=(20, 10), anchor=tk.W)",
        "        ",
        "        path_frame = ttk.Frame(content_frame)",
        "        path_frame.pack(fill=tk.X, pady=8)",
        "        ",
        "        self.path_var = tk.StringVar(value=self.default_path)",
        "        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=('Segoe UI', 10), width=55)",
        "        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))",
        "        ",
        "        browse_button = ttk.Button(path_frame, text='Răsfoire...', command=self.browse_folder, width=15)",
        "        browse_button.pack(side=tk.LEFT)",
        "        ",
        "        ttk.Label(content_frame, text='Progres instalare:', font=('Segoe UI', 10, 'bold')).pack(pady=(20, 8), anchor=tk.W)",
        "        ",
        "        self.progress_var = tk.DoubleVar()",
        "        progress_bar = ttk.Progressbar(content_frame, variable=self.progress_var, maximum=100, mode='determinate')",
        "        progress_bar.pack(pady=(0, 5), fill=tk.X)",
        "        ",
        "        self.progress_label = ttk.Label(content_frame, text='Gata de instalare', font=('Segoe UI', 10), foreground='blue')",
        "        self.progress_label.pack(anchor=tk.W)",
        "        ",
        "        button_frame = ttk.Frame(self.root)",
        "        button_frame.pack(fill=tk.X, padx=25, pady=20)",
        "        ",
        "        self.install_button = ttk.Button(button_frame, text='📦 Instalează Acum', command=self.install, width=25)",
        "        self.install_button.pack(side=tk.LEFT, padx=8)",
        "        ",
        "        self.cancel_button = ttk.Button(button_frame, text='❌ Anulează', width=25, command=self.on_cancel)",
        "        self.cancel_button.pack(side=tk.LEFT, padx=8)",
        "        ",
        "        self.root.mainloop()",
        "    ",
        "    def browse_folder(self):",
        "        try:",
        "            folder = filedialog.askdirectory(title='Selectează locația', initialdir=self.path_var.get())",
        "            if folder:",
        "                self.install_path = folder",
        "                self.path_var.set(folder)",
        "        except: pass",
        "    ",
        "    def on_cancel(self):",
        "        if self.installing:",
        "            if messagebox.askyesno('Confirmare', 'Sigur anulezi?'): sys.exit(0)",
        "        else:",
        "            self.root.quit()",
        "    ",
        "    def update_progress(self, value, message):",
        "        self.progress_var.set(min(value, 100))",
        "        self.progress_label.config(text=message)",
        "        self.root.update()",
        "    ",
        "    def install(self):",
        "        if self.installing: return",
        "        self.installing = True",
        "        self.install_path = self.path_var.get()",
        "        self.install_button.config(state=tk.DISABLED)",
        "        self.cancel_button.config(state=tk.DISABLED)",
        "        ",
        "        try:",
        "            self.update_progress(10, '📁 Se crează directorul...')",
        "            os.makedirs(self.install_path, exist_ok=True)",
        "            ",
        "            self.update_progress(30, '📋 Se cauta fișierele...')",
        "            # Cauta punctaj.exe si supabase_config.ini",
        "            app_exe = None",
        "            config_file = None",
        "            ",
        "            # Functie pentru a cauta recursiv fisiere",
        "            def find_files(start_path):",
        "                nonlocal app_exe, config_file",
        "                try:",
        "                    for root, dirs, files in os.walk(start_path):",
        "                        for file in files:",
        "                            if file == 'punctaj.exe' and not app_exe:",
        "                                app_exe = os.path.join(root, file)",
        "                            elif file == 'supabase_config.ini' and not config_file:",
        "                                config_file = os.path.join(root, file)",
        "                        if app_exe and config_file:",
        "                            return",
        "                except: pass",
        "            ",
        "            # Cauta in directorul scriptului",
        "            base_dir = os.path.dirname(sys.argv[0])",
        "            find_files(base_dir)",
        "            ",
        "            # Daca nu gasit, cauta si in directorul parent si _internal",
        "            if not app_exe or not config_file:",
        "                parent_dir = os.path.dirname(base_dir)",
        "                find_files(parent_dir)",
        "            ",
        "            # Daca inca nu gasit, cauta in temp folder (PyInstaller extrage aici uneori)",
        "            if not app_exe or not config_file:",
        "                find_files(os.environ.get('TEMP', 'C:\\\\Windows\\\\Temp'))",
        "            ",
        "            self.update_progress(50, '📋 Se copiază fișierele...')",
        "            ",
        "            # Copie punctaj.exe - OBLIGATORIU",
        "            if app_exe and os.path.exists(app_exe):",
        "                try:",
        "                    shutil.copy2(app_exe, os.path.join(self.install_path, 'punctaj.exe'))",
        "                    self.update_progress(65, '✓ Aplicație copiată')",
        "                except Exception as e:",
        "                    messagebox.showerror('Eroare', f'Eroare la copiere EXE: {e}')",
        "                    raise",
        "            else:",
        "                messagebox.showerror('Eroare Critica', 'EROARE: punctaj.exe nu a fost găsit în installer!')",
        "                raise FileNotFoundError('punctaj.exe not found')",
        "            ",
        "            # Copie supabase_config.ini - OBLIGATORIU",
        "            if config_file and os.path.exists(config_file):",
        "                try:",
        "                    shutil.copy2(config_file, os.path.join(self.install_path, 'supabase_config.ini'))",
        "                    self.update_progress(75, '✓ Configurație copiată')",
        "                except Exception as e:",
        "                    messagebox.showerror('Eroare', f'Eroare la copiere config: {e}')",
        "                    raise",
        "            else:",
        "                messagebox.showerror('Eroare Critica', 'EROARE: supabase_config.ini nu a fost găsit în installer!')",
        "                raise FileNotFoundError('supabase_config.ini not found')",
        "            ",
        "            self.update_progress(80, '🖥️ Se creează shortcuturi...')",
        "            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')",
        "            self.create_shortcut(os.path.join(desktop_path, 'Punctaj.lnk'), os.path.join(self.install_path, 'punctaj.exe'), 'Punctaj')",
        "            ",
        "            start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft\\\\Windows\\\\Start Menu\\\\Programs')",
        "            self.create_shortcut(os.path.join(start_menu, 'Punctaj.lnk'), os.path.join(self.install_path, 'punctaj.exe'), 'Punctaj')",
        "            ",
        "            self.update_progress(90, '⚙️ Se configureaza sistem...')",
        "            try:",
        "                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\\\Punctaj')",
        "                winreg.SetValueEx(key, 'InstallPath', 0, winreg.REG_SZ, self.install_path)",
        "                winreg.CloseKey(key)",
        "            except: pass",
        "            ",
        "            self.update_progress(100, '✅ Instalare completă!')",
        "            messagebox.showinfo('Succes', f'✅ Instalat în: {self.install_path}')",
        "            if messagebox.askyesno('Lansare', 'Lansez aplicația?'):",
        "                subprocess.Popen(os.path.join(self.install_path, 'punctaj.exe'))",
        "            self.root.quit()",
        "        except Exception as e:",
        "            messagebox.showerror('Eroare', f'❌ {str(e)}')",
        "            self.installing = False",
        "            self.install_button.config(state=tk.NORMAL)",
        "            self.cancel_button.config(state=tk.NORMAL)",
        "    ",
        "    def create_shortcut(self, shortcut_path, target_path, desc):",
        "        try:",
        "            vbs = f'Set oWS = WScript.CreateObject(\"WScript.Shell\")\\nSet oLink = oWS.CreateShortcut(\"{shortcut_path}\")\\noLink.TargetPath = \"{target_path}\"\\noLink.Description = \"{desc}\"\\noLink.WorkingDirectory = \"{os.path.dirname(target_path)}\"\\noLink.Save'",
        "            vbs_file = os.path.join(os.environ['TEMP'], 'create_shortcut.vbs')",
        "            with open(vbs_file, 'w') as f: f.write(vbs)",
        "            subprocess.run(['cscript.exe', vbs_file], capture_output=True)",
        "            try: os.remove(vbs_file)",
        "            except: pass",
        "        except: pass",
        "",
        "if __name__ == '__main__':",
        "    installer = PunctajInstaller()",
        "    installer.create_gui()",
    ]
    
    return '\n'.join(lines)

def build_installer():
    """Creează EXE-ul installerului"""
    
    print('🔨 Se creează scriptul de setup...')
    
    # Creează scriptul de installer
    setup_script_path = os.path.join(os.getcwd(), '_setup_final.py')
    with open(setup_script_path, 'w', encoding='utf-8') as f:
        f.write(create_installer_script())
    
    print(f'✅ Script de setup creat')
    
    # Verifică EXE-ul
    dist_exe = os.path.join(os.getcwd(), 'dist', 'punctaj.exe')
    dist_config = os.path.join(os.getcwd(), 'dist', 'supabase_config.ini')
    
    if not os.path.exists(dist_exe):
        print(f'❌ Eroare: {dist_exe} nu există!')
        return False
    
    print(f'📦 Compilez installerul...')
    
    # Creează PyInstaller executable
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'punctaj_installer',
        '--distpath', 'dist',
        '--icon=NONE',
        '--add-data', f'{dist_exe}{os.pathsep}.',
    ]
    
    if os.path.exists(dist_config):
        cmd.extend(['--add-data', f'{dist_config}{os.pathsep}.'])
    
    cmd.append(setup_script_path)
    
    result = subprocess.run(cmd, cwd=os.getcwd())
    
    if result.returncode == 0:
        installer_path = os.path.join(os.getcwd(), 'dist', 'punctaj_installer.exe')
        print(f'\n✅ Installerul creat cu succes!')
        print(f'📍 Cale: {installer_path}')
        
        if os.path.exists(installer_path):
            size_mb = os.path.getsize(installer_path) / (1024 * 1024)
            print(f'📊 Dimensiune: {size_mb:.2f} MB')
        
        return True
    else:
        print(f'\n❌ Eroare la compilare!')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('📦 Generator Installer - Punctaj')
    print('=' * 60)
    
    if build_installer():
        print('\n✨ Gata! Installerul este distribuit.')
    else:
        print('\n❌ Eroare!')
        sys.exit(1)
