"""
Admin Panel - Setare Permisiuni Global Hierarchy
================================================
UI pentru setarea permisiunilor pe 3 niveluri
"""

import tkinter as tk
from tkinter import ttk, messagebox
from global_hierarchy_permissions import GlobalHierarchyPermissionManager, QuickPermissionChecks


class GlobalHierarchyAdminPanel:
    """Panel admin pentru permisiuni pe 3 niveluri"""
    
    def __init__(self, manager: GlobalHierarchyPermissionManager, supabase_sync):
        """
        Inițializează panelul admin
        
        Args:
            manager: GlobalHierarchyPermissionManager instance
            supabase_sync: Supabase sync object
        """
        self.manager = manager
        self.supabase_sync = supabase_sync
        
        self.window = None
        self.selected_user = None
        self.cities_list = []
        self.institutions_dict = {}
    
    def open_panel(self):
        """Deschide panelul admin"""
        self.window = tk.Toplevel()
        self.window.title("🔐 Admin - Permisiuni Global Hierarchy")
        self.window.geometry("1000x700")
        
        self._setup_ui()
        self._load_cities_and_institutions()
    
    def _setup_ui(self):
        """Construiește UI-ul"""
        # ============ TOP: SELECT USER ============
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="👤 Select User:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.user_entry = ttk.Entry(top_frame, width=30)
        self.user_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="Load", command=self._load_user_permissions).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Show Summary", command=self._show_summary).pack(side=tk.LEFT, padx=5)
        
        # ============ MAIN: NOTEBOOK WITH 3 TABS ============
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # TAB 1: GLOBAL PERMISSIONS
        self._create_global_tab()
        
        # TAB 2: CITY LEVEL PERMISSIONS
        self._create_city_tab()
        
        # TAB 3: INSTITUTION LEVEL PERMISSIONS
        self._create_institution_tab()
        
        # ============ BOTTOM: ACTIONS ============
        bottom_frame = ttk.Frame(self.window)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="💾 Save All", command=self._save_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="🔄 Reload", command=self._load_user_permissions).pack(side=tk.RIGHT, padx=5)
    
    def _create_global_tab(self):
        """Tab 1: Permisiuni globale"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🌍 Global")
        
        # Title
        ttk.Label(frame, text="Global Permissions", font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Checkboxes
        self.global_add_cities_var = tk.BooleanVar()
        self.global_add_states_var = tk.BooleanVar()
        
        ttk.Checkbutton(
            frame, 
            text="✅ Can Add Cities (Orașe)", 
            variable=self.global_add_cities_var,
            command=self._on_global_change
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Checkbutton(
            frame, 
            text="✅ Can Add States (Județe)", 
            variable=self.global_add_states_var,
            command=self._on_global_change
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # Info
        info_frame = ttk.LabelFrame(frame, text="ℹ️ Info")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        info_text = """
🌍 GLOBAL PERMISSIONS:
• Can Add Cities: Permite adăugarea de ORAȘE noi
• Can Add States: Permite adăugarea de JUDEȚE noi

Aceștia sunt controlori globali ai structurii.
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=300).pack(padx=10, pady=10)
    
    def _create_city_tab(self):
        """Tab 2: Permisiuni la nivel city"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏙️ City Level")
        
        # Title
        ttk.Label(frame, text="City Level Permissions (Cine poate adaugă INSTITUȚII în fiecare oras)", 
                  font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Scrollable list of cities
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tree header
        ttk.Label(tree_frame, text="Orașul", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Frame pentru lista de orașe
        self.cities_frame = ttk.Frame(tree_frame)
        self.cities_frame.pack(fill=tk.BOTH, expand=True)
        
        self.cities_vars = {}  # {city: BooleanVar}
    
    def _create_institution_tab(self):
        """Tab 3: Permisiuni la nivel institution"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏢 Institution Level")
        
        # Title
        ttk.Label(frame, text="Institution Level Permissions", font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Treeview pentru instituții
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("City", "Institution", "View", "Edit", "Delete", "Reset", "Deduct")
        self.institution_tree = ttk.Treeview(tree_frame, columns=columns, height=15)
        self.institution_tree.column("#0", width=0, stretch=tk.NO)
        self.institution_tree.column("City", anchor=tk.W, width=120)
        self.institution_tree.column("Institution", anchor=tk.W, width=150)
        self.institution_tree.column("View", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Edit", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Delete", anchor=tk.CENTER, width=60)
        self.institution_tree.column("Reset", anchor=tk.CENTER, width=50)
        self.institution_tree.column("Deduct", anchor=tk.CENTER, width=50)
        
        # Headings
        self.institution_tree.heading("#0", text="", anchor=tk.W)
        self.institution_tree.heading("City", text="🏙️ City", anchor=tk.W)
        self.institution_tree.heading("Institution", text="🏢 Institution", anchor=tk.W)
        self.institution_tree.heading("View", text="👁️", anchor=tk.CENTER)
        self.institution_tree.heading("Edit", text="✏️", anchor=tk.CENTER)
        self.institution_tree.heading("Delete", text="❌", anchor=tk.CENTER)
        self.institution_tree.heading("Reset", text="🔄", anchor=tk.CENTER)
        self.institution_tree.heading("Deduct", text="📉", anchor=tk.CENTER)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.institution_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.institution_tree.xview)
        self.institution_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        # Grid
        self.institution_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click
        self.institution_tree.bind("<Double-1>", self._on_institution_double_click)
    
    def _load_cities_and_institutions(self):
        """Încarcă orașe și instituții din Supabase"""
        try:
            # Get all cities
            response = self.supabase_sync.supabase.table("cities").select("name").execute()
            self.cities_list = [row["name"] for row in response.data] if response.data else []
            
            # Get all institutions per city
            response = self.supabase_sync.supabase.table("institutions").select("name, city").execute()
            self.institutions_dict = {}
            for row in response.data:
                city = row.get("city", "Unknown")
                if city not in self.institutions_dict:
                    self.institutions_dict[city] = []
                self.institutions_dict[city].append(row["name"])
            
            print("✅ Cities and institutions loaded")
            
        except Exception as e:
            print(f"❌ Error loading cities/institutions: {e}")
            messagebox.showerror("Error", f"Failed to load cities: {e}")
    
    def _load_user_permissions(self):
        """Încarcă permisiunile unui user"""
        discord_id = self.user_entry.get().strip()
        
        if not discord_id:
            messagebox.showwarning("Warning", "Please enter Discord ID")
            return
        
        self.selected_user = discord_id
        
        try:
            perms = self.manager.get_all_permissions(discord_id)
            
            # Load global
            global_perms = perms.get("global", {})
            self.global_add_cities_var.set(global_perms.get("can_add_cities", False))
            self.global_add_states_var.set(global_perms.get("can_add_states", False))
            
            # Load city level
            self._load_city_permissions(perms)
            
            # Load institution level
            self._load_institution_permissions(perms)
            
            messagebox.showinfo("Success", f"Permissions loaded for {discord_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load permissions: {e}")
    
    def _load_city_permissions(self, perms: dict):
        """Încarcă permisiunile la nivel city"""
        # Clear old widgets
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
                text=f"✅ {city}",
                variable=var
            ).pack(anchor=tk.W, padx=20, pady=3)
    
    def _load_institution_permissions(self, perms: dict):
        """Încarcă permisiunile la nivel institution"""
        # Clear tree
        for item in self.institution_tree.get_children():
            self.institution_tree.delete(item)
        
        inst_perms = perms.get("institutions", {})
        
        for city in self.cities_list:
            city_inst = inst_perms.get(city, {})
            
            for institution in self.institutions_dict.get(city, []):
                inst_perm = city_inst.get(institution, {})
                
                # Format permissions as ✅/❌
                view_str = "✅" if inst_perm.get("can_view", False) else "❌"
                edit_str = "✅" if inst_perm.get("can_edit", False) else "❌"
                delete_str = "✅" if inst_perm.get("can_delete", False) else "❌"
                reset_str = "✅" if inst_perm.get("can_reset_scores", False) else "❌"
                deduct_str = "✅" if inst_perm.get("can_deduct_scores", False) else "❌"
                
                self.institution_tree.insert("", "end", values=(
                    city, institution, view_str, edit_str, delete_str, reset_str, deduct_str
                ))
    
    def _on_global_change(self):
        """Handler pentru schimbare permisiuni globale"""
        pass  # Will be saved on button click
    
    def _on_institution_double_click(self, event):
        """Handler pentru double-click pe institution"""
        item = self.institution_tree.selection()[0]
        values = self.institution_tree.item(item, "values")
        
        if values:
            city, institution = values[0], values[1]
            self._edit_institution_permission(city, institution)
    
    def _edit_institution_permission(self, city: str, institution: str):
        """Editează permisiunile pentru o instituție"""
        perms = self.manager.get_all_permissions(self.selected_user)
        inst_perm = perms.get("institutions", {}).get(city, {}).get(institution, {})
        
        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Edit: {city} / {institution}")
        edit_window.geometry("400x300")
        
        ttk.Label(edit_window, text=f"{city} / {institution}", 
                  font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Checkboxes
        vars = {}
        permissions = ["can_view", "can_edit", "can_delete", "can_reset_scores", "can_deduct_scores"]
        labels = ["👁️ View", "✏️ Edit", "❌ Delete", "🔄 Reset", "📉 Deduct"]
        
        for perm, label in zip(permissions, labels):
            var = tk.BooleanVar()
            var.set(inst_perm.get(perm, False))
            vars[perm] = var
            
            ttk.Checkbutton(edit_window, text=label, variable=var).pack(anchor=tk.W, padx=20, pady=5)
        
        # Save button
        def save():
            for perm in permissions:
                self.manager.set_institution_permission(
                    self.selected_user, city, institution, perm, vars[perm].get()
                )
            edit_window.destroy()
            self._load_user_permissions()
            messagebox.showinfo("Success", "Permissions saved!")
        
        ttk.Button(edit_window, text="💾 Save", command=save).pack(pady=10)
    
    def _show_summary(self):
        """Afișează sumar permisiuni"""
        if not self.selected_user:
            messagebox.showwarning("Warning", "Please load a user first")
            return
        
        summary = self.manager.get_summary(self.selected_user)
        
        # Create info window
        info_window = tk.Toplevel(self.window)
        info_window.title("Permission Summary")
        info_window.geometry("500x400")
        
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
            # Save global
            self.manager.set_global_permission(
                self.selected_user, "can_add_cities", self.global_add_cities_var.get()
            )
            self.manager.set_global_permission(
                self.selected_user, "can_add_states", self.global_add_states_var.get()
            )
            
            # Save city level
            for city, var in self.cities_vars.items():
                self.manager.set_city_permission(
                    self.selected_user, city, "can_add_institutions", var.get()
                )
            
            messagebox.showinfo("Success", "All permissions saved! ✅")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


def open_global_hierarchy_admin_panel(manager: GlobalHierarchyPermissionManager, supabase_sync):
    """
    Deschide panelul admin pentru permisiuni global hierarchy
    
    Usage:
        from global_hierarchy_permissions import GlobalHierarchyPermissionManager
        from global_hierarchy_admin_panel import open_global_hierarchy_admin_panel
        
        manager = GlobalHierarchyPermissionManager(supabase_client)
        open_global_hierarchy_admin_panel(manager, supabase_sync)
    """
    panel = GlobalHierarchyAdminPanel(manager, supabase_sync)
    panel.open_panel()
