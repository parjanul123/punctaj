"""
Enhanced Admin Permissions Panel
================================
Setează permisiuni pe TOȚI 4 niveluri:
1. GLOBAL - Orașe/Județe + Cine poate da permisiuni
2. CITY LEVEL - Cine poate adaugă instituții
3. INSTITUTION LEVEL - Acțiuni în instituții
4. Admin Controls
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Dict, Optional
from datetime import datetime


class EnhancedPermissionManager:
    """Manager permisiuni cu suport pentru 4 niveluri"""
    
    def __init__(self, supabase_client, cache_dir: str = "d:/punctaj/data"):
        self.supabase = supabase_client
        self.cache_dir = cache_dir
        self.table_name = "discord_users"
        self.column_name = "granular_permissions"
    
    def _get_user_permissions(self, discord_id: str) -> Optional[Dict]:
        """Obține permisiunile user-ului din Supabase"""
        try:
            response = self.supabase.table(self.table_name).select(
                self.column_name
            ).eq("discord_id", discord_id).execute()
            
            if response.data and len(response.data) > 0:
                perm_data = response.data[0].get(self.column_name)
                if perm_data:
                    if isinstance(perm_data, str):
                        return json.loads(perm_data)
                    return perm_data
            return None
        except Exception as e:
            print(f"❌ Eroare citire permissions: {e}")
            return None
    
    def _save_permissions(self, discord_id: str, permissions: Dict) -> bool:
        """Salvează permisiunile în Supabase"""
        try:
            perm_json = json.dumps(permissions, ensure_ascii=False, indent=2)
            self.supabase.table(self.table_name).update({
                self.column_name: perm_json,
                "updated_at": datetime.now().isoformat()
            }).eq("discord_id", discord_id).execute()
            print(f"✅ Permisiuni salvate pentru {discord_id}")
            return True
        except Exception as e:
            print(f"❌ Eroare salvare permissions: {e}")
            return False
    
    # ===== GLOBAL LEVEL =====
    def can_manage_user_permissions(self, discord_id: str) -> bool:
        """Verifică dacă user poate DA PERMISIUNI altor utilizatori"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            return False
        return perms.get("global", {}).get("can_manage_user_permissions", False)
    
    def can_add_cities(self, discord_id: str) -> bool:
        """Verifică dacă poate adaugă orașe"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            return False
        return perms.get("global", {}).get("can_add_cities", False)
    
    def can_add_states(self, discord_id: str) -> bool:
        """Verifică dacă poate adaugă județe"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            return False
        return perms.get("global", {}).get("can_add_states", False)
    
    def set_global_permission(self, discord_id: str, permission: str, value: bool) -> bool:
        """Setează permisiune globală"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            perms = {}
        if "global" not in perms:
            perms["global"] = {}
        perms["global"][permission] = value
        return self._save_permissions(discord_id, perms)
    
    # ===== CITY LEVEL =====
    def can_add_institutions(self, discord_id: str, city: str) -> bool:
        """Verifică dacă poate adaugă instituții în città"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            return False
        return perms.get("cities", {}).get(city, {}).get("can_add_institutions", False)
    
    def set_city_permission(self, discord_id: str, city: str, permission: str, value: bool) -> bool:
        """Setează permisiune la nivel city"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            perms = {}
        if "cities" not in perms:
            perms["cities"] = {}
        if city not in perms["cities"]:
            perms["cities"][city] = {}
        perms["cities"][city][permission] = value
        return self._save_permissions(discord_id, perms)
    
    # ===== INSTITUTION LEVEL =====
    def check_institution_permission(self, discord_id: str, city: str, institution: str, permission: str) -> bool:
        """Verifică permisiune la nivel instituție"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            return False
        return perms.get("institutions", {}).get(city, {}).get(institution, {}).get(permission, False)
    
    def set_institution_permission(self, discord_id: str, city: str, institution: str, permission: str, value: bool) -> bool:
        """Setează permisiune la nivel instituție"""
        perms = self._get_user_permissions(discord_id)
        if not perms:
            perms = {}
        if "institutions" not in perms:
            perms["institutions"] = {}
        if city not in perms["institutions"]:
            perms["institutions"][city] = {}
        if institution not in perms["institutions"][city]:
            perms["institutions"][city][institution] = {}
        perms["institutions"][city][institution][permission] = value
        return self._save_permissions(discord_id, perms)
    
    def get_all_permissions(self, discord_id: str) -> Dict:
        """Obține TOATE permisiunile"""
        return self._get_user_permissions(discord_id) or {}


class EnhancedAdminPanel:
    """Panel admin cu 4 niveluri de permisiuni"""
    
    def __init__(self, manager: EnhancedPermissionManager, supabase_sync, current_user_id: str):
        self.manager = manager
        self.supabase_sync = supabase_sync
        self.current_user_id = current_user_id
        
        self.window = None
        self.selected_user = None
        self.cities_list = []
        self.institutions_dict = {}
    
    def can_open(self) -> bool:
        """Verifică dacă user-ul poate accesa panoul admin"""
        return self.manager.can_manage_user_permissions(self.current_user_id)
    
    def open_panel(self):
        """Deschide panelul admin"""
        if not self.can_open():
            messagebox.showerror("Eroare", "❌ Nu ai permisiune să dai permisiuni utilizatorilor!")
            return False
        
        self.window = tk.Toplevel()
        self.window.title("🔐 Admin - Permisiuni Utilizatori (4 NIVELURI)")
        self.window.geometry("1200x750")
        
        self._setup_ui()
        self._load_cities_and_institutions()
        return True
    
    def _setup_ui(self):
        """Construiește UI"""
        # ===== TOP: SELECT USER =====
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="👤 Select User:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.user_entry = ttk.Entry(top_frame, width=30)
        self.user_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="Load", command=self._load_user_permissions).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Show Summary", command=self._show_summary).pack(side=tk.LEFT, padx=5)
        
        # ===== MAIN: NOTEBOOK WITH 4 TABS =====
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_admin_tab()
        self._create_global_tab()
        self._create_city_tab()
        self._create_institution_tab()
        
        # ===== BOTTOM: SAVE =====
        bottom_frame = ttk.Frame(self.window)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="💾 Save All", command=self._save_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="🔄 Reload", command=self._load_user_permissions).pack(side=tk.RIGHT, padx=5)
    
    def _create_admin_tab(self):
        """Tab 0: Admin Controls - Cine poate DA PERMISIUNI"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔐 Admin")
        
        ttk.Label(frame, text="Admin Controls", font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        self.admin_manage_perms_var = tk.BooleanVar()
        
        ttk.Checkbutton(
            frame,
            text="✅ Poate DA PERMISIUNI altor utilizatori",
            variable=self.admin_manage_perms_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Info", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        info_text = """
🔐 ADMIN PERMISSIONS:
• Poate DA PERMISIUNI: Permite user-ului să acceseze 
  panoul admin și să seteze permisiuni pentru alți utilizatori

ATENTIE: Acordă cu grijă doar adminilor de încredere!

Doar utilizatorii cu această permisiune pot:
  ✓ Deschide panoul admin
  ✓ Selecta și edita permisiuni pt alți utilizatori
  ✓ Seteza permisiuni globale, per-city, per-instituție
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=500).pack(padx=10, pady=10)
    
    def _create_global_tab(self):
        """Tab 1: Global Permissions"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🌍 Global")
        
        ttk.Label(frame, text="Global Permissions (Orașe & Județe)", font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        perms_frame = ttk.LabelFrame(frame, text="Permisiuni", padding=10)
        perms_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.global_add_cities_var = tk.BooleanVar()
        self.global_add_states_var = tk.BooleanVar()
        
        ttk.Checkbutton(
            perms_frame,
            text="✅ Poate ADAUGĂ ORAȘE noi",
            variable=self.global_add_cities_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Checkbutton(
            perms_frame,
            text="✅ Poate ADAUGĂ JUDEȚE noi",
            variable=self.global_add_states_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Info", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = """
🌍 GLOBAL LEVEL:
• Adaugă ORAȘE: User-ul poate adaugă orașe noi în sistem
• Adaugă JUDEȚE: User-ul poate adaugă județe noi

Aceștia sunt controlori globali ai structurii.
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=500).pack(padx=10, pady=10)
    
    def _create_city_tab(self):
        """Tab 2: City Level Permissions"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏙️ City Level")
        
        ttk.Label(frame, text="Per-City Permissions (Cine adaugă INSTITUȚII)", 
                  font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Scrollable list
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(tree_frame, text="Selectează un oraș:", font=("Arial", 10)).pack(anchor=tk.W)
        
        self.cities_frame = ttk.Frame(tree_frame)
        self.cities_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.cities_vars = {}
    
    def _create_institution_tab(self):
        """Tab 3: Institution Level Permissions"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏢 Institution Level")
        
        ttk.Label(frame, text="Per-Institution Permissions (5 acțiuni)", 
                  font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("City", "Institution", "View", "Edit", "Delete", "Reset", "Deduct")
        self.institution_tree = ttk.Treeview(tree_frame, columns=columns, height=20)
        self.institution_tree.column("#0", width=0, stretch=tk.NO)
        self.institution_tree.column("City", anchor=tk.W, width=120)
        self.institution_tree.column("Institution", anchor=tk.W, width=150)
        self.institution_tree.column("View", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Edit", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Delete", anchor=tk.CENTER, width=60)
        self.institution_tree.column("Reset", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Deduct", anchor=tk.CENTER, width=50)
        
        self.institution_tree.heading("#0", text="", anchor=tk.W)
        self.institution_tree.heading("City", text="🏙️ City", anchor=tk.W)
        self.institution_tree.heading("Institution", text="🏢 Institution", anchor=tk.W)
        self.institution_tree.heading("View", text="👁️", anchor=tk.CENTER)
        self.institution_tree.heading("Edit", text="✏️", anchor=tk.CENTER)
        self.institution_tree.heading("Delete", text="❌", anchor=tk.CENTER)
        self.institution_tree.heading("Reset", text="🔄", anchor=tk.CENTER)
        self.institution_tree.heading("Deduct", text="📉", anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.institution_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.institution_tree.xview)
        self.institution_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.institution_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.institution_tree.bind("<Double-1>", self._on_institution_double_click)
    
    def _load_cities_and_institutions(self):
        """Încarcă orașe și instituții"""
        try:
            response = self.supabase_sync.supabase.table("cities").select("name").execute()
            self.cities_list = [row["name"] for row in response.data] if response.data else []
            
            response = self.supabase_sync.supabase.table("institutions").select("name, city").execute()
            self.institutions_dict = {}
            for row in response.data:
                city = row.get("city", "Unknown")
                if city not in self.institutions_dict:
                    self.institutions_dict[city] = []
                self.institutions_dict[city].append(row["name"])
            
            print("✅ Cities and institutions loaded")
        except Exception as e:
            print(f"❌ Error loading: {e}")
    
    def _load_user_permissions(self):
        """Încarcă permisiunile unui user"""
        discord_id = self.user_entry.get().strip()
        
        if not discord_id:
            messagebox.showwarning("Warning", "Please enter Discord ID")
            return
        
        self.selected_user = discord_id
        
        try:
            perms = self.manager.get_all_permissions(discord_id)
            
            # Admin tab
            admin_perms = perms.get("global", {})
            self.admin_manage_perms_var.set(admin_perms.get("can_manage_user_permissions", False))
            
            # Global tab
            self.global_add_cities_var.set(admin_perms.get("can_add_cities", False))
            self.global_add_states_var.set(admin_perms.get("can_add_states", False))
            
            # City tab
            self._load_city_permissions(perms)
            
            # Institution tab
            self._load_institution_permissions(perms)
            
            messagebox.showinfo("Success", f"Loaded permissions for {discord_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
    
    def _load_city_permissions(self, perms: dict):
        """Încarcă permisiuni city"""
        for widget in self.cities_frame.winfo_children():
            widget.destroy()
        
        self.cities_vars = {}
        cities_perms = perms.get("cities", {})
        
        for city in self.cities_list:
            var = tk.BooleanVar()
            var.set(cities_perms.get(city, {}).get("can_add_institutions", False))
            self.cities_vars[city] = var
            
            ttk.Checkbutton(
                self.cities_frame,
                text=f"✅ {city} - Poate ADAUGĂ INSTITUȚII",
                variable=var
            ).pack(anchor=tk.W, padx=20, pady=3)
    
    def _load_institution_permissions(self, perms: dict):
        """Încarcă permisiuni instituții"""
        for item in self.institution_tree.get_children():
            self.institution_tree.delete(item)
        
        inst_perms = perms.get("institutions", {})
        
        for city in self.cities_list:
            city_inst = inst_perms.get(city, {})
            for institution in self.institutions_dict.get(city, []):
                inst_perm = city_inst.get(institution, {})
                
                view_str = "✅" if inst_perm.get("can_view", False) else "❌"
                edit_str = "✅" if inst_perm.get("can_edit", False) else "❌"
                delete_str = "✅" if inst_perm.get("can_delete", False) else "❌"
                reset_str = "✅" if inst_perm.get("can_reset_scores", False) else "❌"
                deduct_str = "✅" if inst_perm.get("can_deduct_scores", False) else "❌"
                
                self.institution_tree.insert("", "end", values=(
                    city, institution, view_str, edit_str, delete_str, reset_str, deduct_str
                ))
    
    def _on_institution_double_click(self, event):
        """Double-click pe instituție"""
        item = self.institution_tree.selection()[0]
        values = self.institution_tree.item(item, "values")
        
        if values:
            city, institution = values[0], values[1]
            self._edit_institution_permission(city, institution)
    
    def _edit_institution_permission(self, city: str, institution: str):
        """Editează permisiuni instituție"""
        perms = self.manager.get_all_permissions(self.selected_user)
        inst_perm = perms.get("institutions", {}).get(city, {}).get(institution, {})
        
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Edit: {city} / {institution}")
        edit_window.geometry("400x350")
        
        ttk.Label(edit_window, text=f"{city} / {institution}", 
                  font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        vars = {}
        permissions = ["can_view", "can_edit", "can_delete", "can_reset_scores", "can_deduct_scores"]
        labels = ["👁️ Vizualizare", "✏️ Editare", "❌ Ștergere", "🔄 Reset Punctaj", "📉 Scade Puncte"]
        
        for perm, label in zip(permissions, labels):
            var = tk.BooleanVar()
            var.set(inst_perm.get(perm, False))
            vars[perm] = var
            
            ttk.Checkbutton(edit_window, text=label, variable=var, font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=5)
        
        def save():
            for perm in permissions:
                self.manager.set_institution_permission(
                    self.selected_user, city, institution, perm, vars[perm].get()
                )
            edit_window.destroy()
            self._load_user_permissions()
            messagebox.showinfo("Success", "Permissions saved! ✅")
        
        ttk.Button(edit_window, text="💾 Save", command=save, width=20).pack(pady=10)
    
    def _show_summary(self):
        """Afișează sumar"""
        if not self.selected_user:
            messagebox.showwarning("Warning", "Please load a user first")
            return
        
        perms = self.manager.get_all_permissions(self.selected_user)
        
        summary = f"\n📋 PERMISIUNI: {self.selected_user}\n"
        summary += "=" * 60 + "\n"
        
        # Admin
        admin_perms = perms.get("global", {})
        summary += f"\n🔐 ADMIN:\n"
        summary += f"  • Poate da permisiuni: {'✅' if admin_perms.get('can_manage_user_permissions') else '❌'}\n"
        
        # Global
        summary += f"\n🌍 GLOBAL:\n"
        summary += f"  • Adaugă orașe: {'✅' if admin_perms.get('can_add_cities') else '❌'}\n"
        summary += f"  • Adaugă județe: {'✅' if admin_perms.get('can_add_states') else '❌'}\n"
        
        # Cities
        cities_perms = perms.get("cities", {})
        if cities_perms:
            summary += f"\n🏙️ ORAȘE:\n"
            for city, city_perm in cities_perms.items():
                summary += f"  • {city}: {'✅' if city_perm.get('can_add_institutions') else '❌'}\n"
        
        # Institutions
        inst_perms = perms.get("institutions", {})
        if inst_perms:
            summary += f"\n🏢 INSTITUȚII:\n"
            for city, city_inst in inst_perms.items():
                summary += f"  [{city}]\n"
                for institution, perm in city_inst.items():
                    status = f"V{'✅' if perm.get('can_view') else '❌'} E{'✅' if perm.get('can_edit') else '❌'} D{'✅' if perm.get('can_delete') else '❌'} R{'✅' if perm.get('can_reset_scores') else '❌'} Sc{'✅' if perm.get('can_deduct_scores') else '❌'}"
                    summary += f"    • {institution}: {status}\n"
        
        info_window = tk.Toplevel(self.window)
        info_window.title("Permission Summary")
        info_window.geometry("600x500")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, summary)
        text_widget.config(state=tk.DISABLED)
    
    def _save_all(self):
        """Salvează toate permisiunile"""
        if not self.selected_user:
            messagebox.showwarning("Warning", "Please load a user first")
            return
        
        try:
            # Admin
            self.manager.set_global_permission(
                self.selected_user, "can_manage_user_permissions", self.admin_manage_perms_var.get()
            )
            
            # Global
            self.manager.set_global_permission(
                self.selected_user, "can_add_cities", self.global_add_cities_var.get()
            )
            self.manager.set_global_permission(
                self.selected_user, "can_add_states", self.global_add_states_var.get()
            )
            
            # Cities
            for city, var in self.cities_vars.items():
                self.manager.set_city_permission(
                    self.selected_user, city, "can_add_institutions", var.get()
                )
            
            messagebox.showinfo("Success", "All permissions saved! ✅")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


def open_enhanced_admin_panel(manager: EnhancedPermissionManager, supabase_sync, current_user_id: str):
    """
    Deschide panelul admin enhanced cu 4 niveluri
    
    Usage:
        manager = EnhancedPermissionManager(supabase_client)
        open_enhanced_admin_panel(manager, supabase_sync, current_user_id)
    """
    panel = EnhancedAdminPanel(manager, supabase_sync, current_user_id)
    if not panel.open_panel():
        print("❌ Access denied")
