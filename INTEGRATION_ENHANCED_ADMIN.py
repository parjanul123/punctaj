"""
INTEGRATION: Enhanced Admin Panel cu 4 Niveluri
===============================================
Cum să integrezi noile opțiuni de permisiuni în aplicație
"""

# ============ SETUP ============

from enhanced_admin_permissions import EnhancedPermissionManager, open_enhanced_admin_panel


def setup_permission_manager(supabase_sync):
    """Inițializează manager-ul de permisiuni"""
    return EnhancedPermissionManager(supabase_sync.supabase, "d:/punctaj/data")


# ============ INTEGRARE ÎN UI ============

def integrate_admin_button_in_menu(manager, supabase_sync, current_user_id):
    """
    Adaugă butonul Admin în meniu
    
    Usage în punctaj.py:
        # În funcția care construiește meniu
        admin_button = ttk.Button(
            menu_frame,
            text="🔐 Admin Permisiuni",
            command=lambda: open_admin_permissions_panel(manager, supabase_sync, current_user_id)
        )
        admin_button.pack()
    """
    return manager.can_manage_user_permissions(current_user_id)


def open_admin_permissions_panel(manager, supabase_sync, current_user_id):
    """
    Deschide panelul admin (cu verificare permisiuni)
    
    Usage:
        if not manager.can_manage_user_permissions(current_user_id):
            messagebox.showerror("Eroare", "❌ Nu ai permisiune!")
            return
        
        open_enhanced_admin_panel(manager, supabase_sync, current_user_id)
    """
    open_enhanced_admin_panel(manager, supabase_sync, current_user_id)


# ============ EXEMPLU PAGINĂ ADMIN ============

import tkinter as tk
from tkinter import ttk, messagebox


class AdminMainPage:
    """
    Pagina admin cu butoane pentru diferite funcțiuni
    """
    
    def __init__(self, manager, supabase_sync, current_user_id):
        self.manager = manager
        self.supabase_sync = supabase_sync
        self.current_user_id = current_user_id
        
        self.window = tk.Tk()
        self.window.title("🔐 Admin Panel")
        self.window.geometry("600x400")
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Construiește UI"""
        ttk.Label(self.window, text="🔐 ADMIN PANEL", font=("Arial", 14, "bold")).pack(padx=10, pady=10)
        
        # Button frame
        btn_frame = ttk.LabelFrame(self.window, text="Funcții Admin", padding=20)
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button 1: Manage User Permissions
        can_manage_perms = self.manager.can_manage_user_permissions(self.current_user_id)
        
        ttk.Button(
            btn_frame,
            text="👥 Gestionează Permisiuni Utilizatori",
            command=self._open_user_permissions,
            state=tk.NORMAL if can_manage_perms else tk.DISABLED,
            width=40
        ).pack(pady=10)
        
        if not can_manage_perms:
            ttk.Label(btn_frame, text="❌ Nu ai permisiune", foreground="red").pack()
        else:
            ttk.Label(btn_frame, text="✅ Poți accesa", foreground="green").pack()
        
        ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Button 2: Add Cities (global)
        can_add_cities = self.manager.can_add_cities(self.current_user_id)
        
        ttk.Button(
            btn_frame,
            text="🏙️ Adaugă Orașe",
            state=tk.NORMAL if can_add_cities else tk.DISABLED,
            width=40
        ).pack(pady=10)
        
        if not can_add_cities:
            ttk.Label(btn_frame, text="❌ Nu ai permisiune", foreground="red").pack()
        else:
            ttk.Label(btn_frame, text="✅ Poți accesa", foreground="green").pack()
        
        ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Button 3: Add States
        can_add_states = self.manager.can_add_states(self.current_user_id)
        
        ttk.Button(
            btn_frame,
            text="📍 Adaugă Județe",
            state=tk.NORMAL if can_add_states else tk.DISABLED,
            width=40
        ).pack(pady=10)
        
        if not can_add_states:
            ttk.Label(btn_frame, text="❌ Nu ai permisiune", foreground="red").pack()
        else:
            ttk.Label(btn_frame, text="✅ Poți accesa", foreground="green").pack()
        
        # Status bar
        status_text = f"Logged in as: {self.current_user_id}"
        ttk.Label(self.window, text=status_text, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def _open_user_permissions(self):
        """Deschide panelul de permisiuni"""
        open_enhanced_admin_panel(self.manager, self.supabase_sync, self.current_user_id)
    
    def run(self):
        """Rulează aplicația"""
        self.window.mainloop()


# ============ INTEGRARE ÎN PUNCTAJ.PY ============

"""
În punctaj.py, adaugă:

# 1. IMPORT
from enhanced_admin_permissions import EnhancedPermissionManager, open_enhanced_admin_panel

# 2. SETUP (în __init__)
self.perm_manager = EnhancedPermissionManager(supabase_sync.supabase)

# 3. CREATE MENU ITEM
def create_menu(self):
    # ... alte menu items ...
    
    # Admin button - APARE NUMAI DACĂ USER POATE DA PERMISIUNI
    if self.perm_manager.can_manage_user_permissions(self.current_user_id):
        admin_button = ttk.Button(
            menu_frame,
            text="🔐 Admin Permisiuni",
            command=self.open_admin_panel
        )
        admin_button.pack(side=tk.LEFT, padx=5)

# 4. HANDLER
def open_admin_panel(self):
    open_enhanced_admin_panel(
        self.perm_manager, 
        self.supabase_sync, 
        self.current_user_id
    )

# 5. VERIFICARE LA ALTE ACȚIUNI
def on_add_city(self):
    if not self.perm_manager.can_add_cities(self.current_user_id):
        messagebox.showerror("Eroare", "❌ Nu ai permisiune!")
        return
    # ... add city logic ...

def on_add_institution(self, city):
    if not self.perm_manager.can_add_institutions(self.current_user_id, city):
        messagebox.showerror("Eroare", f"❌ Nu ai permisiune în {city}!")
        return
    # ... add institution logic ...
"""


# ============ PERMISIUNI - STRUCTURA ============

PERMISSION_STRUCTURE = {
    "global": {
        "can_manage_user_permissions": "Poate DA permisiuni altor utilizatori (ADMIN)",
        "can_add_cities": "Poate adaugă ORAȘE noi",
        "can_add_states": "Poate adaugă JUDEȚE noi"
    },
    "cities": {
        "Blackwater": {
            "can_add_institutions": "Poate adaugă INSTITUȚII în Blackwater"
        },
        "Saint-Denis": {
            "can_add_institutions": "Poate adaugă INSTITUȚII în Saint-Denis"
        }
    },
    "institutions": {
        "Blackwater": {
            "Politie": {
                "can_view": "Vizualizare angajați",
                "can_edit": "Adaugă/Editează angajați",
                "can_delete": "Șterge angajați",
                "can_reset_scores": "Reset Punctaj",
                "can_deduct_scores": "Scade Puncte"
            }
        }
    }
}


# ============ EXEMPLU COMPLET: SETUP UTILIZATOR NOU ============

def setup_new_admin_user(manager, discord_id):
    """
    Exemplu: Setare permisiuni pentru admin nou
    
    Usage:
        setup_new_admin_user(perm_manager, "discord_123456")
    """
    # ADMIN: Poate da permisiuni
    manager.set_global_permission(discord_id, "can_manage_user_permissions", True)
    
    # GLOBAL: Poate adaugă orașe și județe
    manager.set_global_permission(discord_id, "can_add_cities", True)
    manager.set_global_permission(discord_id, "can_add_states", True)
    
    print(f"✅ Admin user {discord_id} setup complete!")


def setup_city_manager_user(manager, discord_id, city):
    """
    Exemplu: Setare permisiuni pentru manager de oraș
    
    Usage:
        setup_city_manager_user(perm_manager, "discord_789012", "Blackwater")
    """
    # CITY LEVEL: Poate adaugă instituții în acel oraș
    manager.set_city_permission(discord_id, city, "can_add_institutions", True)
    
    print(f"✅ City manager {discord_id} for {city} setup complete!")


def setup_institution_user(manager, discord_id, city, institution):
    """
    Exemplu: Setare permisiuni pentru manager de instituție
    
    Usage:
        setup_institution_user(perm_manager, "discord_345678", "Blackwater", "Politie")
    """
    # INSTITUTION LEVEL: Toate acțiunile în instituția aia
    manager.set_institution_permission(discord_id, city, institution, "can_view", True)
    manager.set_institution_permission(discord_id, city, institution, "can_edit", True)
    manager.set_institution_permission(discord_id, city, institution, "can_delete", True)
    manager.set_institution_permission(discord_id, city, institution, "can_reset_scores", True)
    manager.set_institution_permission(discord_id, city, institution, "can_deduct_scores", True)
    
    print(f"✅ Institution manager {discord_id} for {city}/{institution} setup complete!")


# ============ QUICK REFERENCE ============

"""
4 NIVELURI DE PERMISIUNI:

1️⃣ ADMIN LEVEL (Global)
   can_manage_user_permissions → Poate deschide panelul admin

2️⃣ GLOBAL LEVEL (Structură)
   can_add_cities → Adaugă orașe
   can_add_states → Adaugă județe

3️⃣ CITY LEVEL (Per-Oraș)
   can_add_institutions → Adaugă instituții în acel oraș

4️⃣ INSTITUTION LEVEL (Per-Instituție)
   can_view → Vizualizare
   can_edit → Adaugă/Editează
   can_delete → Șterge
   can_reset_scores → Reset Punctaj
   can_deduct_scores → Scade Puncte

FLOW:
1. Super Admin: Setează can_manage_user_permissions = True pentru Alt Admin
2. Alt Admin: Deschide panelul admin și setează permisiuni pentru alții
3. User cu can_add_cities: Poate adaugă orașe noi
4. User cu can_add_institutions în Blackwater: Poate adaugă instituții numai în Blackwater
5. User cu can_view în Blackwater/Politie: Poate vedea angajații acolo
"""
