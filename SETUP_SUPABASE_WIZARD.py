#!/usr/bin/env python3
"""
Punctaj - Supabase Configuration Setup Wizard
Ajuta utilizatorii sa configure baza de date pe orice dispozitiv
"""

import os
import sys
import configparser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import json

class SupabaseSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("Punctaj - Database Setup Wizard")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Determina locatia de salvare a configului
        self.app_dir = self.get_app_directory()
        
        self.setup_ui()
        self.center_window()
    
    def get_app_directory(self):
        """Gaseste sau creeaza folderul aplicatiei"""
        # Incearca mai intai folderul curent
        if os.path.exists("supabase_config.ini"):
            return os.getcwd()
        
        # Apoi %ProgramFiles%\Punctaj
        program_files_path = os.path.expandvars(r"%ProgramFiles%\Punctaj")
        if os.path.exists(program_files_path):
            return program_files_path
        
        # Apoi folderul scriptului
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.access(script_dir, os.W_OK):
            return script_dir
        
        # Altfel, folderul user
        return os.path.expanduser("~")
    
    def center_window(self):
        """Centeaza fereastra pe ecran"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Creeaza interfata"""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#007bff", height=80)
        header_frame.pack(fill=tk.X)
        
        title = tk.Label(header_frame, text="Database Configuration", 
                        font=("Arial", 16, "bold"), bg="#007bff", fg="white")
        title.pack(pady=10)
        
        subtitle = tk.Label(header_frame, text="Configure Supabase connection for Punctaj",
                           font=("Arial", 10), bg="#007bff", fg="white")
        subtitle.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        instr_text = (
            "Enter your Supabase connection details below.\n"
            "You can find these in your Supabase project settings."
        )
        instr = tk.Label(content_frame, text=instr_text, font=("Arial", 10),
                        bg="#f8f9fa", justify=tk.LEFT)
        instr.pack(anchor=tk.W, pady=(0, 20))
        
        # URL input
        tk.Label(content_frame, text="Supabase URL:", font=("Arial", 10, "bold"),
                bg="#f8f9fa").pack(anchor=tk.W, pady=(5, 0))
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(content_frame, textvariable=self.url_var,
                                 font=("Arial", 10), width=50)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))
        
        # API Key input
        tk.Label(content_frame, text="API Key (Public):", font=("Arial", 10, "bold"),
                bg="#f8f9fa").pack(anchor=tk.W, pady=(5, 0))
        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(content_frame, textvariable=self.key_var,
                                 font=("Arial", 10), width=50, show="*")
        self.key_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Show password checkbox
        self.show_key_var = tk.BooleanVar()
        show_key_check = tk.Checkbutton(content_frame, text="Show API Key",
                                       variable=self.show_key_var,
                                       command=self.toggle_key_visibility,
                                       bg="#f8f9fa", font=("Arial", 9))
        show_key_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg="#f8f9fa")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        load_btn = tk.Button(button_frame, text="Load from File", command=self.load_from_file,
                            font=("Arial", 10), width=15, bg="#6c757d", fg="white",
                            activebackground="#5a6268")
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_btn = tk.Button(button_frame, text="Test Connection", command=self.test_connection,
                            font=("Arial", 10), width=15, bg="#ffc107", fg="black",
                            activebackground="#e0a800")
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = tk.Button(button_frame, text="Save & Continue", command=self.save_config,
                            font=("Arial", 10), width=15, bg="#28a745", fg="white",
                            activebackground="#218838")
        save_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Arial", 9),
                                    bg="#f8f9fa", fg="#666")
        self.status_label.pack(side=tk.BOTTOM, padx=20, pady=10)
    
    def toggle_key_visibility(self):
        """Arata/ascunde API key"""
        show = self.show_key_var.get()
        self.key_entry.config(show="" if show else "*")
    
    def load_from_file(self):
        """Incarca configurare din fisier existent"""
        file_path = filedialog.askopenfilename(
            title="Select supabase_config.ini",
            filetypes=[("INI files", "*.ini"), ("All files", "*.*")],
            initialdir=self.app_dir
        )
        
        if file_path:
            config = configparser.ConfigParser()
            try:
                config.read(file_path)
                if 'supabase' in config:
                    url = config.get('supabase', 'url', fallback='')
                    key = config.get('supabase', 'key', fallback='')
                    
                    self.url_var.set(url)
                    self.key_var.set(key)
                    
                    self.status_label.config(text=f"✓ Loaded from: {Path(file_path).name}",
                                           fg="#28a745")
                    return
            except:
                pass
            
            messagebox.showerror("Error", "Could not load configuration from file")
    
    def test_connection(self):
        """Testeaza conexiunea la Supabase"""
        url = self.url_var.get().strip()
        key = self.key_var.get().strip()
        
        if not url or not key:
            messagebox.showwarning("Missing Data", "Please enter URL and API Key")
            return
        
        try:
            import requests
            
            headers = {
                'apikey': key,
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {key}'
            }
            
            test_url = f"{url}/rest/v1/users?limit=1&select=id"
            
            self.status_label.config(text="Testing connection...", fg="#666")
            self.root.update()
            
            response = requests.get(test_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                self.status_label.config(text="✓ Connection successful!",
                                        fg="#28a745")
                messagebox.showinfo("Success", "Connection to Supabase is working!")
                return True
            elif response.status_code == 401:
                self.status_label.config(text="✗ Unauthorized - Invalid API key",
                                        fg="#dc3545")
                messagebox.showerror("Error", "API key is invalid or expired")
                return False
            else:
                self.status_label.config(text=f"✗ Error: HTTP {response.status_code}",
                                        fg="#dc3545")
                messagebox.showerror("Error", f"Connection failed: HTTP {response.status_code}")
                return False
                
        except ImportError:
            messagebox.showerror("Error", "requests module not installed")
            return False
        except Exception as e:
            self.status_label.config(text=f"✗ Connection failed: {str(e)[:40]}",
                                    fg="#dc3545")
            messagebox.showerror("Error", f"Connection test failed:\n{e}")
            return False
    
    def save_config(self):
        """Salveaza configurarea"""
        url = self.url_var.get().strip()
        key = self.key_var.get().strip()
        
        if not url or not key:
            messagebox.showwarning("Missing Data", "Please enter URL and API Key")
            return
        
        # Creeaza configuratia
        config = configparser.ConfigParser()
        config['supabase'] = {
            'url': url,
            'key': key,
            'table_sync': 'police_data',
            'table_logs': 'audit_logs',
            'table_users': 'users'
        }
        config['sync'] = {
            'enabled': 'true',
            'auto_sync': 'true',
            'sync_interval': '30',
            'conflict_resolution': 'latest_timestamp',
            'sync_on_startup': 'true'
        }
        
        # Salveaza fisierul
        config_path = os.path.join(self.app_dir, 'supabase_config.ini')
        
        try:
            os.makedirs(self.app_dir, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.status_label.config(text=f"✓ Config saved to {Path(config_path).name}",
                                    fg="#28a745")
            
            messagebox.showinfo("Success", 
                f"Configuration saved successfully!\n\n"
                f"File: {config_path}\n\n"
                f"You can now run Punctaj.exe")
            
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save configuration:\n{e}")

def main():
    root = tk.Tk()
    app = SupabaseSetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
