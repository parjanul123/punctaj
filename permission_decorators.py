# -*- coding: utf-8 -*-
"""
Decorator & Middleware pentru Verificare Permisiuni

Util pentru a proteja funcții cu verificări de permisiuni automate
"""

from functools import wraps
from tkinter import messagebox
import json


def require_institution_permission(perm_manager, permission_type: str):
    """
    Decorator pentru a verifica permisiuni înainte de execuție
    
    Utilizare:
    @require_institution_permission(perm_manager, 'can_edit')
    def add_employee(city, institution, data):
        # Codul care necesită permisiune
        ...
    
    Args:
        perm_manager: Instanță de InstitutionPermissionManager
        permission_type: 'can_view', 'can_edit', sau 'can_delete'
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user_id=None, city=None, institution=None, **kwargs):
            if not user_id or not city or not institution:
                messagebox.showerror(
                    "Eroare",
                    "❌ Parametrii lipsă: user_id, city, institution"
                )
                return None
            
            # Verifică permisiune
            if not perm_manager.check_user_institution_permission(
                user_id, city, institution, permission_type
            ):
                messagebox.showerror(
                    "Acces Refuzat",
                    f"❌ Nu ai permisiunea '{permission_type}' pentru {city}/{institution}"
                )
                return None
            
            # Execută funcția
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class PermissionChecker:
    """Utility class pentru verificări de permisiuni frecvente"""
    
    def __init__(self, perm_manager, user_id: str):
        self.perm_manager = perm_manager
        self.user_id = user_id
    
    def can_view(self, city: str, institution: str) -> bool:
        """Poate vedea instituția?"""
        return self.perm_manager.check_user_institution_permission(
            self.user_id, city, institution, 'can_view'
        )
    
    def can_edit(self, city: str, institution: str) -> bool:
        """Poate edita instituția?"""
        return self.perm_manager.check_user_institution_permission(
            self.user_id, city, institution, 'can_edit'
        )
    
    def can_delete(self, city: str, institution: str) -> bool:
        """Poate șterge din instituție?"""
        return self.perm_manager.check_user_institution_permission(
            self.user_id, city, institution, 'can_delete'
        )
    
    def get_accessible_institutions(self, cities_institutions: dict) -> dict:
        """
        Returnează doar instituțiile pe care utilizatorul are acces
        
        Args:
            cities_institutions: {"Blackwater": ["Politie", "Medical"], ...}
        
        Returns:
            {"Blackwater": ["Politie"], ...}  (doar cu can_view=True)
        """
        accessible = {}
        
        for city, institutions in cities_institutions.items():
            accessible[city] = []
            for institution in institutions:
                if self.can_view(city, institution):
                    accessible[city].append(institution)
        
        return {k: v for k, v in accessible.items() if v}  # Remove empty cities
    
    def filter_visible_institutions(self, all_institutions: list) -> list:
        """
        Filtrează lista de instituții care sunt vizibile
        
        Format input: ["Blackwater/Politie", "Blackwater/Medical", ...]
        Return: ["Blackwater/Politie"]  (doar cu can_view=True)
        """
        visible = []
        for inst_path in all_institutions:
            try:
                city, institution = inst_path.split('/')
                if self.can_view(city, institution):
                    visible.append(inst_path)
            except ValueError:
                continue
        return visible
    
    def get_button_states(self, city: str, institution: str) -> dict:
        """Returnează stările butoanelor pentru o instituție"""
        return {
            'can_add': self.can_edit(city, institution),
            'can_edit': self.can_edit(city, institution),
            'can_delete': self.can_delete(city, institution),
            'can_reset': self.can_delete(city, institution),
            'can_view': self.can_view(city, institution),
        }
    
    def has_any_permission(self, city: str, institution: str) -> bool:
        """Are vreun fel de acces?"""
        return self.can_view(city, institution)
    
    def has_edit_access(self, city: str, institution: str) -> bool:
        """Are acces pentru a modifica?"""
        return self.can_edit(city, institution)
    
    def has_delete_access(self, city: str, institution: str) -> bool:
        """Are acces pentru a șterge?"""
        return self.can_delete(city, institution)


class PermissionGuard:
    """Context manager pentru verificări de permisiuni"""
    
    def __init__(self, perm_manager, user_id: str, city: str, institution: str, permission: str):
        self.perm_manager = perm_manager
        self.user_id = user_id
        self.city = city
        self.institution = institution
        self.permission = permission
        self.has_access = False
    
    def __enter__(self):
        self.has_access = self.perm_manager.check_user_institution_permission(
            self.user_id, self.city, self.institution, self.permission
        )
        
        if not self.has_access:
            messagebox.showerror(
                "Acces Refuzat",
                f"❌ Nu ai acces pentru {self.city}/{self.institution}"
            )
        
        return self.has_access
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# ===== EXEMPLE DE UTILIZARE =====

"""
# Exemplu 1: Cu decorator
@require_institution_permission(perm_manager, 'can_edit')
def add_employee(city, institution, name, position):
    # Codul se execută doar dacă are permisiune
    return supabase_sync.add_employee(city, institution, name, position)

# Apel cu parametrii:
add_employee("Ion", "Polițist", user_id="123456", city="Blackwater", institution="Politie")


# Exemplu 2: Cu PermissionChecker
checker = PermissionChecker(perm_manager, current_user_id)

if checker.can_edit("Blackwater", "Politie"):
    add_button.config(state=tk.NORMAL)
else:
    add_button.config(state=tk.DISABLED)


# Exemplu 3: Filtrare instituții vizibile
accessible = checker.get_accessible_institutions(institutions_by_city)
# Acum afișează doar instituțiile vizibile


# Exemplu 4: Cu context manager (PermissionGuard)
with PermissionGuard(perm_manager, user_id, "Blackwater", "Politie", "can_delete") as has_access:
    if has_access:
        delete_employee(...)
    # else - messagebox deja afișat


# Exemplu 5: Stări butoane
states = checker.get_button_states("Blackwater", "Politie")
add_button.config(state=tk.NORMAL if states['can_add'] else tk.DISABLED)
edit_button.config(state=tk.NORMAL if states['can_edit'] else tk.DISABLED)
delete_button.config(state=tk.NORMAL if states['can_delete'] else tk.DISABLED)
reset_button.config(state=tk.NORMAL if states['can_reset'] else tk.DISABLED)
"""
