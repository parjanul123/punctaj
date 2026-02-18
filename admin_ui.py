# -*- coding: utf-8 -*-
"""
Admin Panel UI - User Management & Action Logs
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json

try:
    from admin_permissions import open_granular_permissions_panel
except ImportError:
    open_granular_permissions_panel = None


def open_admin_panel(root, supabase_sync, discord_auth, data_dir=None, action_logger=None):
    """Open admin panel window"""
    if not supabase_sync or not supabase_sync.enabled:
        messagebox.showwarning("Admin Panel", "Supabase not configured")
        return
    
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel - User Management & Logs")
    
    # Responsive window sizing
    screenwidth = admin_window.winfo_screenwidth()
    screenheight = admin_window.winfo_screenheight()
    admin_width = max(900, min(1300, int(screenwidth * 0.80)))
    admin_height = max(600, min(850, int(screenheight * 0.75)))
    admin_window.geometry(f"{admin_width}x{admin_height}")
    
    admin_window.grab_set()
    admin_window.resizable(True, True)
    admin_window.minsize(900, 600)
    
    # Create notebook tabs
    notebook = ttk.Notebook(admin_window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Tab 1: User Management
    users_frame = ttk.Frame(notebook)
    notebook.add(users_frame, text="Utilizatori")
    create_users_tab(users_frame, supabase_sync, discord_auth)
    
    # Tab 2: Statistics
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text="Statistici")
    create_stats_tab(stats_frame, supabase_sync)
    
    # Tab 3: Granular Permissions
    permissions_frame = ttk.Frame(notebook)
    notebook.add(permissions_frame, text="🔐 Permisiuni Granulare")
    create_permissions_tab(permissions_frame, root, supabase_sync, discord_auth, data_dir, action_logger)
    
    # Bottom button bar
    button_frame = ttk.Frame(admin_window)
    button_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(button_frame, text="📋 Loguri Acțiuni", 
               command=lambda: open_logs_window(admin_window, supabase_sync)).pack(side=tk.LEFT, padx=5)

def open_logs_window(root, supabase_sync):
    """Open a separate window for action logs with filters"""
    try:
        logs_window = tk.Toplevel(root)
        logs_window.title("Loguri Acțiuni - Filtrare per Instituție")
        
        # Responsive window sizing
        screenwidth = logs_window.winfo_screenwidth()
        screenheight = logs_window.winfo_screenheight()
        logs_width = max(900, min(1400, int(screenwidth * 0.85)))
        logs_height = max(600, min(900, int(screenheight * 0.80)))
        logs_window.geometry(f"{logs_width}x{logs_height}")
        
        logs_window.resizable(True, True)
        logs_window.minsize(900, 600)
        
        # Get available institutions
        cities_dict = get_available_institutions()
        cities_list = sorted(cities_dict.keys())
        
        # Top frame with filters
        top_frame = ttk.Frame(logs_window)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter labels and inputs
        filter_frame = ttk.LabelFrame(top_frame, text="Filtre", padding=5)
        filter_frame.pack(fill=tk.X, padx=0, pady=5)
        
        ttk.Label(filter_frame, text="Utilizator:").pack(side=tk.LEFT, padx=5)
        user_entry = ttk.Entry(filter_frame, width=12)
        user_entry.pack(side=tk.LEFT, padx=3)
        
        ttk.Label(filter_frame, text="Acțiune:").pack(side=tk.LEFT, padx=5)
        action_entry = ttk.Entry(filter_frame, width=12)
        action_entry.pack(side=tk.LEFT, padx=3)
        
        ttk.Label(filter_frame, text="Oraș:").pack(side=tk.LEFT, padx=5)
        city_combo = ttk.Combobox(filter_frame, width=12, values=[''] + cities_list, state='readonly')
        city_combo.pack(side=tk.LEFT, padx=3)
        city_combo.set('')
        
        ttk.Label(filter_frame, text="Instituție:").pack(side=tk.LEFT, padx=5)
        institution_combo = ttk.Combobox(filter_frame, width=12, state='readonly')
        institution_combo.pack(side=tk.LEFT, padx=3)
        institution_combo.set('')
        
        # Update institutions when city changes
        def on_city_changed(event):
            selected_city = city_combo.get()
            if selected_city and selected_city in cities_dict:
                institutions = [''] + cities_dict[selected_city]
                institution_combo['values'] = institutions
                institution_combo.set('')
            else:
                institution_combo['values'] = ['']
                institution_combo.set('')
        
        city_combo.bind('<<ComboboxSelected>>', on_city_changed)
        
        # Initialize institution dropdown
        if cities_list:
            institution_combo['values'] = [''] + cities_dict.get(cities_list[0], [])
        
        # Button frame
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill=tk.X, padx=0, pady=5)
        
        # Treeview for logs
        columns = ('Timestamp', 'User', 'Action', 'City', 'Institution', 'Employee', 'Details')
        logs_tree = ttk.Treeview(logs_window, columns=columns, height=20)
        logs_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        logs_tree.column('#0', width=0, stretch=tk.NO)
        logs_tree.column('Timestamp', anchor=tk.W, width=100)
        logs_tree.column('User', anchor=tk.W, width=80)
        logs_tree.column('Action', anchor=tk.W, width=100)
        logs_tree.column('City', anchor=tk.W, width=100)
        logs_tree.column('Institution', anchor=tk.W, width=100)
        logs_tree.column('Employee', anchor=tk.W, width=100)
        logs_tree.column('Details', anchor=tk.W, width=250)
        
        for col in columns:
            logs_tree.heading(col, text=col, anchor=tk.W)
        
        # Button to refresh logs
        def refresh_logs_action():
            try:
                refresh_logs(logs_tree, supabase_sync, user_entry.get(), action_entry.get(), city_combo.get(), institution_combo.get())
            except Exception as e:
                messagebox.showerror("Error", f"Error loading logs: {e}")
        
        ttk.Button(button_frame, text="🔄 Reîncarcă loguri", command=refresh_logs_action).pack(side=tk.LEFT, padx=5)
        
        # Load logs on startup
        refresh_logs_action()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error opening logs window: {e}")
        print(f"DEBUG: Error opening logs window: {e}")
        import traceback
        traceback.print_exc()


def create_users_tab(frame, supabase_sync, discord_auth):
    """Create users management tab"""
    
    # Top frame with buttons
    top_frame = ttk.Frame(frame)
    top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(top_frame, text="Reîncarcă utilizatori", 
               command=lambda: refresh_users_list(users_tree, supabase_sync)).pack(side=tk.LEFT, padx=5)
    
    # Treeview for users
    columns = ('Discord ID', 'Username', 'Email', 'Role', 'Status', 'Last Login')
    users_tree = ttk.Treeview(frame, columns=columns, height=15)
    users_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    users_tree.column('#0', width=0, stretch=tk.NO)
    users_tree.column('Discord ID', anchor=tk.W, width=100)
    users_tree.column('Username', anchor=tk.W, width=120)
    users_tree.column('Email', anchor=tk.W, width=150)
    users_tree.column('Role', anchor=tk.CENTER, width=80)
    users_tree.column('Status', anchor=tk.CENTER, width=80)
    users_tree.column('Last Login', anchor=tk.CENTER, width=120)
    
    users_tree.heading('#0', text='', anchor=tk.W)
    users_tree.heading('Discord ID', text='Discord ID', anchor=tk.W)
    users_tree.heading('Username', text='Username', anchor=tk.W)
    users_tree.heading('Email', text='Email', anchor=tk.W)
    users_tree.heading('Role', text='Role', anchor=tk.CENTER)
    users_tree.heading('Status', text='Status', anchor=tk.CENTER)
    users_tree.heading('Last Login', text='Last Login', anchor=tk.CENTER)
    
    # Bottom frame with controls
    bottom_frame = ttk.Frame(frame)
    bottom_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(bottom_frame, text="Rol:").pack(side=tk.LEFT, padx=5)
    role_var = tk.StringVar(value="user")
    role_combo = ttk.Combobox(bottom_frame, textvariable=role_var, 
                               values=["viewer", "user", "admin"], state='readonly', width=10)
    role_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(bottom_frame, text="Actualizează rol", 
               command=lambda: update_user_role(users_tree, supabase_sync, role_var)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(bottom_frame, text="Șterge utilizator", 
               command=lambda: delete_user(users_tree, supabase_sync)).pack(side=tk.LEFT, padx=5)
    
    # Load users on startup
    refresh_users_list(users_tree, supabase_sync)


def get_available_institutions():
    """Scan /data folder to get all cities and institutions"""
    import os
    import sys
    
    # Fix for EXE: Look in EXE directory first, then fallback to Documents
    if getattr(sys, 'frozen', False):
        # Running as EXE
        data_path = os.path.join(os.path.dirname(sys.executable), 'data')
    else:
        # Running as Python script
        data_path = os.path.join(os.path.expanduser('~'), 'Documents', 'PunctajManager', 'data')
    
    cities = {}
    try:
        if os.path.exists(data_path):
            for city_folder in os.listdir(data_path):
                city_path = os.path.join(data_path, city_folder)
                if os.path.isdir(city_path):
                    institutions = []
                    for json_file in os.listdir(city_path):
                        if json_file.endswith('.json'):
                            institutions.append(json_file[:-5])
                    if institutions:
                        cities[city_folder] = sorted(institutions)
    except Exception as e:
        print(f"Error scanning institutions: {e}")
    
    return cities



def create_stats_tab(frame, supabase_sync):
    """Create statistics tab with general stats and permissions history"""
    
    # Create sub-notebook for two sections
    stats_notebook = ttk.Notebook(frame)
    stats_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # ====== TAB 1: GENERAL STATISTICS ======
    general_frame = ttk.Frame(stats_notebook)
    stats_notebook.add(general_frame, text="📊 General")
    
    stats_text = tk.Text(general_frame, height=20, width=80)
    stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    try:
        if supabase_sync and supabase_sync.enabled:
            # Get statistics
            users_url = f"{supabase_sync.url}/rest/v1/discord_users?select=count()"
            logs_url = f"{supabase_sync.url}/rest/v1/{supabase_sync.table_logs}?select=count()"
            
            import requests
            
            users_resp = requests.get(users_url, headers=supabase_sync.headers, timeout=10)
            logs_resp = requests.get(logs_url, headers=supabase_sync.headers, timeout=10)
            
            stats_text.insert(tk.END, "=== STATISTICI GENERALE ===\n\n")
            
            if users_resp.status_code == 200:
                users_count = len(users_resp.json())
                stats_text.insert(tk.END, f"👥 Total utilizatori: {users_count}\n")
            
            if logs_resp.status_code == 200:
                logs_count = len(logs_resp.json())
                stats_text.insert(tk.END, f"📝 Total acțiuni logged: {logs_count}\n")
            
            stats_text.insert(tk.END, f"\n🕐 Ultima actualizare: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    except Exception as e:
        stats_text.insert(tk.END, f"Error loading statistics: {e}")
    
    stats_text.config(state=tk.DISABLED)
    
    # ====== TAB 2: PERMISSIONS HISTORY ======
    perms_frame = ttk.Frame(stats_notebook)
    stats_notebook.add(perms_frame, text="🔐 Istoric Permisiuni")
    
    # Create treeview for permissions history
    permissions_tree = ttk.Treeview(
        perms_frame,
        columns=("Data", "Discord ID", "Username", "Persoana Modificata", "Permisiuni", "Actiune"),
        height=20
    )
    
    permissions_tree.column("#0", width=0)
    permissions_tree.column("Data", anchor=tk.W, width=120)
    permissions_tree.column("Discord ID", anchor=tk.W, width=130)
    permissions_tree.column("Username", anchor=tk.W, width=120)
    permissions_tree.column("Persoana Modificata", anchor=tk.W, width=120)
    permissions_tree.column("Permisiuni", anchor=tk.W, width=250)
    permissions_tree.column("Actiune", anchor=tk.W, width=100)
    
    permissions_tree.heading("#0", text="")
    permissions_tree.heading("Data", text="📅 Data/Ora")
    permissions_tree.heading("Discord ID", text="👤 Discord ID")
    permissions_tree.heading("Username", text="📝 Username")
    permissions_tree.heading("Persoana Modificata", text="👤 Persoana Modificata")
    permissions_tree.heading("Permisiuni", text="🔓 Permisiuni/Schimbari")
    permissions_tree.heading("Actiune", text="⚡ Actiune")
    
    # Add scrollbars
    vsb = ttk.Scrollbar(perms_frame, orient=tk.VERTICAL, command=permissions_tree.yview)
    hsb = ttk.Scrollbar(perms_frame, orient=tk.HORIZONTAL, command=permissions_tree.xview)
    
    permissions_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    
    permissions_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    
    perms_frame.grid_rowconfigure(0, weight=1)
    perms_frame.grid_columnconfigure(0, weight=1)
    
    # Button to refresh permissions history
    refresh_frame = ttk.Frame(perms_frame)
    refresh_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    
    def load_permissions_history():
        """Load permission change history from action logs"""
        # Clear existing items
        for item in permissions_tree.get_children():
            permissions_tree.delete(item)
        
        try:
            if not supabase_sync or not supabase_sync.enabled:
                return
            
            import requests
            # Load logs and filter for permission_change action type
            url = f"{supabase_sync.url}/rest/v1/{supabase_sync.table_logs}?select=*&action_type=eq.permission_change&order=timestamp.desc&limit=100"
            
            response = requests.get(url, headers=supabase_sync.headers, timeout=10)
            
            if response.status_code == 200:
                logs = response.json()
                
                for log in logs:
                    timestamp = log.get('timestamp', '')
                    if 'T' in timestamp:
                        date_part, time_part = timestamp.split('T')
                        timestamp = f"{date_part} {time_part[:5]}"
                    
                    discord_id = log.get('discord_id', '')
                    discord_username = log.get('discord_username', '')
                    entity_name = log.get('entity_name', '')  # Person who had permissions changed
                    changes = log.get('changes', '')
                    details = log.get('details', '')
                    
                    permissions_tree.insert('', tk.END, values=(
                        timestamp,
                        discord_id[:15] + "..." if len(discord_id) > 15 else discord_id,
                        discord_username,
                        entity_name,
                        changes[:50] + "..." if len(changes) > 50 else changes,
                        "Modificat"
                    ))
        
        except Exception as e:
            print(f"Error loading permissions history: {e}")
    
    ttk.Button(refresh_frame, text="🔄 Reîncarcă Istoric Permisiuni", command=load_permissions_history).pack(side=tk.LEFT, padx=5)
    
    # Load permissions history on init
    load_permissions_history()


def refresh_users_list(tree, supabase_sync):
    """Refresh users list from Supabase"""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    try:
        if not supabase_sync or not supabase_sync.enabled:
            return
        
        import requests
        url = f"{supabase_sync.url}/rest/v1/discord_users?select=*&order=last_login.desc"
        response = requests.get(url, headers=supabase_sync.headers, timeout=10)
        
        if response.status_code == 200:
            users = response.json()
            for user in users:
                last_login = user.get('last_login', 'N/A')
                if last_login and 'T' in last_login:
                    last_login = last_login.split('T')[0]
                
                # Încearcă mai întâi 'username', apoi 'discord_username' pentru compatibilitate
                username = user.get('username', user.get('discord_username', 'N/A'))
                
                # Determină rolul din coloanele is_superuser și is_admin
                is_superuser = user.get('is_superuser', False)
                is_admin = user.get('is_admin', False)
                
                if is_superuser:
                    role = 'superuser'
                elif is_admin:
                    role = 'admin'
                else:
                    role = 'user'
                
                tree.insert('', tk.END, values=(
                    user.get('discord_id', ''),
                    username,
                    user.get('email', user.get('discord_email', 'N/A')),
                    role,
                    'Active' if user.get('active') else 'Inactive',
                    last_login
                ))
    
    except Exception as e:
        print(f"Error loading users: {e}")


def refresh_logs(tree, supabase_sync, user_filter="", action_filter="", city_filter="", institution_filter=""):
    """Refresh action logs from Supabase"""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    
    try:
        if not supabase_sync or not supabase_sync.enabled:
            return
        
        import requests
        # Use configured table name from supabase_sync
        url = f"{supabase_sync.url}/rest/v1/{supabase_sync.table_logs}?select=*&order=timestamp.desc&limit=100"
        print(f"📊 Fetching logs from table: {supabase_sync.table_logs}")
        print(f"🔗 URL: {url}")
        
        response = requests.get(url, headers=supabase_sync.headers, timeout=10)
        
        if response.status_code == 200:
            logs = response.json()
            print(f"📝 Found {len(logs)} logs")
            
            for log in logs:
                # Apply filters - check multiple field names for compatibility
                user = log.get('user') or log.get('discord_id') or ''
                action = log.get('action') or log.get('action_type') or ''
                city = log.get('city') or ''
                institution = log.get('institution') or ''
                details = log.get('details') or log.get('status') or ''
                
                if user_filter and user_filter.lower() not in user.lower():
                    continue
                if action_filter and action_filter.lower() not in action.lower():
                    continue
                if city_filter and city_filter.lower() not in city.lower():
                    continue
                if institution_filter and institution_filter.lower() not in institution.lower():
                    continue
                
                timestamp = log.get('timestamp', '')
                if 'T' in timestamp:
                    timestamp = timestamp.split('T')[1][:5]
                
                tree.insert('', tk.END, values=(
                    timestamp,
                    user,
                    action,
                    city,
                    institution,
                    details[:50] if details else ''
                ))
        else:
            print(f"⚠️ Error fetching logs (status {response.status_code}): {response.text}")
    
    except Exception as e:
        print(f"❌ Error loading logs: {e}")
        import traceback
        traceback.print_exc()


def update_user_role(tree, supabase_sync, role_var):
    """Update selected user's role"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Admin Panel", "Selectează un utilizator")
        return
    
    item = selection[0]
    values = tree.item(item, 'values')
    discord_id = values[0]
    new_role = role_var.get()
    
    try:
        if supabase_sync and supabase_sync.enabled:
            import requests
            url = f"{supabase_sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}"
            
            # Map role to is_superuser și is_admin columns
            if new_role == 'superuser':
                data = {'is_superuser': True, 'is_admin': False}
            elif new_role == 'admin':
                data = {'is_superuser': False, 'is_admin': True}
            else:  # user or viewer
                data = {'is_superuser': False, 'is_admin': False}
            
            response = requests.patch(url, json=data, headers=supabase_sync.headers, timeout=10)
            
            if response.status_code in [200, 204]:
                messagebox.showinfo("Success", f"Rol actualizat la: {new_role}")
                refresh_users_list(tree, supabase_sync)
            else:
                messagebox.showerror("Error", f"Failed to update: {response.status_code}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")


def delete_user(tree, supabase_sync):
    """Delete selected user"""
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Admin Panel", "Selectează un utilizator")
        return
    
    if not messagebox.askyesno("Confirm", "Ștergi utilizatorul?"):
        return
    
    item = selection[0]
    values = tree.item(item, 'values')
    discord_id = values[0]
    
    try:
        if supabase_sync and supabase_sync.enabled:
            import requests
            url = f"{supabase_sync.url}/rest/v1/discord_users?discord_id=eq.{discord_id}"
            response = requests.delete(url, headers=supabase_sync.headers, timeout=10)
            
            if response.status_code in [204, 200]:
                messagebox.showinfo("Success", "Utilizator șters")
                tree.delete(item)
            else:
                messagebox.showerror("Error", f"Failed to delete: {response.status_code}")
    
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")


def create_permissions_tab(frame, root, supabase_sync, discord_auth, data_dir=None, action_logger=None):
    """Create granular permissions management tab"""
    
    # Header
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Label(
        header_frame,
        text="🔐 Gestiune Permisiuni Granulare",
        font=("Segoe UI", 12, "bold")
    ).pack(side=tk.LEFT)
    
    ttk.Label(
        header_frame,
        text="Seteaza permisiuni detaliate pentru fiecare utilizator",
        font=("Segoe UI", 9),
        foreground="gray"
    ).pack(side=tk.LEFT, padx=(20, 0))
    
    # Info frame
    info_frame = ttk.LabelFrame(frame, text="ℹ️ Informații", padding=10)
    info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    info_text = """
Setati permisiunile detaliate pentru fiecare utilizator prin bifarea casetelor corespunzatoare.

Categorii de permisiuni:
• Orase: Adaugă, Editează, Șterge
• Institutii: Adaugă, Editează, Șterge (per instituție)
• Angajati: Adaugă, Editează, Șterge (per instituție)
• Punctaj: Adaugă/Editează (per instituție)
• Cloud: Upload, Download
• Admin: Vizualizare Logs, Gestiune Utilizatori, Gestiune Permisiuni
    """
    
    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(fill=tk.X)
    
    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Button(
        button_frame,
        text="🔓 Deschide Gestiune Permisiuni",
        command=lambda: open_granular_permissions_panel(root, supabase_sync, discord_auth, data_dir, action_logger) if open_granular_permissions_panel else messagebox.showerror("Eroare", "Modul de permisiuni indisponibil")
    ).pack(side=tk.LEFT, padx=5)
