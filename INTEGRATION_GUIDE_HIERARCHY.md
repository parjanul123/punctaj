"""
INTEGRATION GUIDE: Global Hierarchy Permissions
================================================
Cum să integrezi permisiunile de Orașe și Instituții în aplicație
"""

# ============ SETUP ============

from global_hierarchy_permissions import GlobalHierarchyPermissionManager, integrate_add_city_button, integrate_add_institution_button
from global_hierarchy_admin_panel import open_global_hierarchy_admin_panel


# În main application:
def setup_permissions(supabase_sync):
    """Inițializează manager-ul de permisiuni"""
    return GlobalHierarchyPermissionManager(supabase_sync.supabase, "d:/punctaj/data")


# ============ 1. INTEGRARE: BUTON ADAUGĂ ORAȘE ============

def integrate_add_city_button_in_ui(manager, user_id):
    """
    Controlează starea butonului "Adaugă Oraș"
    
    Usage în punctaj.py:
        # La inițializarea UI
        can_add_city = integrate_add_city_button(manager, current_user_id)
        add_city_button.config(state=tk.NORMAL if can_add_city else tk.DISABLED)
        
        # La click
        def on_add_city():
            if not manager.can_add_cities(current_user_id):
                messagebox.showerror("Eroare", "❌ Nu ai permisiune să adaugi orașe!")
                return
            # ... add city logic ...
    """
    return manager.can_add_cities(user_id)


# ============ 2. INTEGRARE: BUTON ADAUGĂ INSTITUȚII PE FIECARE ORAȘ ============

def integrate_add_institution_button_in_city_view(manager, user_id, city):
    """
    Controlează starea butonului "Adaugă Instituție" pentru un anumit oraș
    
    Usage în punctaj.py, în funcția care arată instituții dintr-un oraș:
        # La click pe un oraș
        def on_city_selected(city):
            # ... show institutions ...
            can_add_inst = integrate_add_institution_button(manager, current_user_id, city)
            add_institution_button.config(state=tk.NORMAL if can_add_inst else tk.DISABLED)
            
            # La click pe buton
            def on_add_institution():
                if not manager.can_add_institutions(current_user_id, city):
                    messagebox.showerror("Eroare", f"❌ Nu ai permisiune în {city}!")
                    return
                # ... add institution logic ...
    """
    return manager.can_add_institutions(user_id, city)


# ============ 3. INTEGRARE: DESCHIDERE PANOU ADMIN ============

def open_admin_panel_from_app(manager, supabase_sync):
    """
    Deschide panelul admin din aplicație
    
    Usage în punctaj.py:
        def on_admin_button_click():
            if not is_user_admin(current_user_id):
                messagebox.showerror("Eroare", "❌ Acces refuzat!")
                return
            open_global_hierarchy_admin_panel(manager, supabase_sync)
    """
    open_global_hierarchy_admin_panel(manager, supabase_sync)


# ============ 4. EXEMPLU COMPLET: PAGINĂ CU ORAȘE ============

import tkinter as tk
from tkinter import ttk, messagebox


class CitiesPageWithPermissions:
    """
    Exemplu pagină care arată orașe și permitere adăugare
    """
    
    def __init__(self, manager, user_id, supabase_sync):
        self.manager = manager
        self.user_id = user_id
        self.supabase_sync = supabase_sync
        
        self.window = tk.Tk()
        self.window.title("🏙️ Orașe")
        self.window.geometry("700x500")
        
        self._setup_ui()
        self._load_cities()
    
    def _setup_ui(self):
        """Construiește UI"""
        # Title
        ttk.Label(self.window, text="🏙️ ORAȘE", font=("Arial", 14, "bold")).pack(padx=10, pady=10)
        
        # Button bar
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buton Adaugă Oraș - CONTROLAT DE PERMISIUNI
        can_add_city = self.manager.can_add_cities(self.user_id)
        self.add_city_button = ttk.Button(
            btn_frame,
            text="➕ Adaugă Oraș",
            command=self._on_add_city,
            state=tk.NORMAL if can_add_city else tk.DISABLED
        )
        self.add_city_button.pack(side=tk.LEFT, padx=5)
        
        # Admin button
        ttk.Button(btn_frame, text="🔐 Admin", command=self._on_admin).pack(side=tk.RIGHT, padx=5)
        
        # Cities list
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ("City", "Institutions")
        self.cities_tree = ttk.Treeview(list_frame, columns=columns, height=20)
        self.cities_tree.column("#0", width=0, stretch=tk.NO)
        self.cities_tree.column("City", anchor=tk.W, width=200)
        self.cities_tree.column("Institutions", anchor=tk.W, width=300)
        
        self.cities_tree.heading("#0", text="", anchor=tk.W)
        self.cities_tree.heading("City", text="Oraș", anchor=tk.W)
        self.cities_tree.heading("Institutions", text="Instituții", anchor=tk.W)
        
        self.cities_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click
        self.cities_tree.bind("<Double-1>", self._on_city_double_click)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def _load_cities(self):
        """Încarcă orașe"""
        try:
            response = self.supabase_sync.supabase.table("cities").select("name").execute()
            cities = [row["name"] for row in response.data] if response.data else []
            
            for city in cities:
                # Count institutions
                inst_response = self.supabase_sync.supabase.table("institutions").select(
                    "name"
                ).eq("city", city).execute()
                inst_count = len(inst_response.data) if inst_response.data else 0
                
                self.cities_tree.insert("", "end", values=(city, f"{inst_count} instituții"))
            
            self.status_var.set(f"Loaded {len(cities)} cities")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cities: {e}")
    
    def _on_add_city(self):
        """Handler Adaugă Oraș"""
        # Check permission
        if not self.manager.can_add_cities(self.user_id):
            messagebox.showerror("Eroare", "❌ Nu ai permisiune să adaugi orașe!")
            return
        
        # Create input window
        dialog = tk.Toplevel(self.window)
        dialog.title("Adaugă Oraș")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text="Numele orașului:", font=("Arial", 10)).pack(padx=10, pady=10)
        
        entry = ttk.Entry(dialog, width=30)
        entry.pack(padx=10, pady=5)
        
        def save():
            city_name = entry.get().strip()
            if not city_name:
                messagebox.showwarning("Warning", "Please enter city name")
                return
            
            try:
                # Add to database
                self.supabase_sync.supabase.table("cities").insert({
                    "name": city_name
                }).execute()
                
                messagebox.showinfo("Success", f"✅ Orașul {city_name} a fost adăugat!")
                dialog.destroy()
                self.window.destroy()
                self.__init__(self.manager, self.user_id, self.supabase_sync)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add city: {e}")
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def _on_city_double_click(self, event):
        """Handler click pe oraș - arată instituții"""
        item = self.cities_tree.selection()[0]
        values = self.cities_tree.item(item, "values")
        
        if values:
            city = values[0]
            self._show_institutions_for_city(city)
    
    def _show_institutions_for_city(self, city):
        """Arată instituții dintr-un oraș"""
        # Create new window
        inst_window = tk.Toplevel(self.window)
        inst_window.title(f"🏢 Instituții în {city}")
        inst_window.geometry("600x400")
        
        ttk.Label(inst_window, text=f"Instituții în {city}", font=("Arial", 12, "bold")).pack(padx=10, pady=10)
        
        # Button bar
        btn_frame = ttk.Frame(inst_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Buton Adaugă Instituție - CONTROLAT DE PERMISIUNI
        can_add_inst = self.manager.can_add_institutions(self.user_id, city)
        add_inst_button = ttk.Button(
            btn_frame,
            text="➕ Adaugă Instituție",
            state=tk.NORMAL if can_add_inst else tk.DISABLED
        )
        add_inst_button.pack(side=tk.LEFT, padx=5)
        
        if not can_add_inst:
            ttk.Label(btn_frame, text="❌ Nu ai permisiuni în acest oraș", foreground="red").pack(side=tk.LEFT, padx=10)
        
        # Institutions list
        list_frame = ttk.Frame(inst_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        inst_tree = ttk.Treeview(list_frame)
        inst_tree.column("#0", anchor=tk.W, width=300)
        inst_tree.heading("#0", text="Instituție")
        inst_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load institutions
        try:
            response = self.supabase_sync.supabase.table("institutions").select("name").eq("city", city).execute()
            for row in response.data:
                inst_tree.insert("", "end", text=row["name"])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load institutions: {e}")
    
    def _on_admin(self):
        """Deschide panelul admin"""
        open_global_hierarchy_admin_panel(self.manager, self.supabase_sync)
    
    def run(self):
        """Rulează aplicația"""
        self.window.mainloop()


# ============ EXEMPLU UTILIZARE ============

if __name__ == "__main__":
    """
    Exemplu cum să folosești în punctaj.py:
    
    1. Inițializează manager:
        perm_manager = GlobalHierarchyPermissionManager(supabase_client)
    
    2. Cand afișezi orașe - controlează buton:
        can_add = perm_manager.can_add_cities(user_id)
        add_button.config(state=tk.NORMAL if can_add else tk.DISABLED)
    
    3. Cand utilizatorul apasă buton:
        if not perm_manager.can_add_cities(user_id):
            messagebox.showerror("Eroare", "❌ Nu ai permisiune!")
            return
        # ... create city ...
    
    4. Similar pentru instituții (per-city):
        can_add_inst = perm_manager.can_add_institutions(user_id, city_name)
        add_inst_button.config(state=tk.NORMAL if can_add_inst else tk.DISABLED)
    
    5. Admin setează permisiuni:
        open_global_hierarchy_admin_panel(perm_manager, supabase_sync)
    """
    pass
