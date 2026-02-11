# -*- coding: utf-8 -*-
"""
Exemplu de Integrare - Permisiuni Instituții în Interfața Principală

Arată cum să integrez verificări de permisiuni în orice pagină de instituție
"""

from admin_permissions import InstitutionPermissionManager
import tkinter as tk
from tkinter import ttk, messagebox


class InstitutionViewExample:
    """
    Exemplu de pagină care afișează instituții cu control permisiuni
    
    Folosește:
    - can_view: Afișează/ascunde lista angajați
    - can_edit: Activează/dezactivează butoanele de Adaugă și Editează
    - can_delete: Activează/dezactivează butoanele de Șterge și Reset Punctaj
    """
    
    def __init__(self, root, supabase_sync, current_user_discord_id, data_dir):
        self.root = root
        self.supabase_sync = supabase_sync
        self.current_user_id = current_user_discord_id
        self.data_dir = data_dir
        
        # Inițializare permission manager
        self.perm_manager = InstitutionPermissionManager(supabase_sync, data_dir)
        
        # State
        self.current_city = None
        self.current_institution = None
        self.employees = []
        
        self.create_ui()
    
    def create_ui(self):
        """Creează interfața cu selecție instituții și control permisiuni"""
        
        # ===== FRAME PRINCIPAL =====
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== TOP: SELECȚIE INSTITUȚIE =====
        selection_frame = ttk.LabelFrame(main_frame, text="📍 Selectare Instituție", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dropdown Orașe
        ttk.Label(selection_frame, text="Oraș:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.city_var,
            state="readonly",
            width=30
        )
        self.city_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.city_combo.bind("<<ComboboxSelected>>", self.on_city_changed)
        
        # Dropdown Instituții
        ttk.Label(selection_frame, text="Instituție:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=(5, 0))
        self.institution_var = tk.StringVar()
        self.institution_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.institution_var,
            state="readonly",
            width=30
        )
        self.institution_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=(5, 0))
        self.institution_combo.bind("<<ComboboxSelected>>", self.on_institution_changed)
        
        # Load cities
        self.load_available_cities()
        
        # ===== MIDDLE: AFIȘARE ANGAJAȚI (cu control vizibilitate) =====
        employees_frame = ttk.LabelFrame(main_frame, text="👥 Angajați", padding=10)
        employees_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.employees_frame = employees_frame
        
        # Create treeview for employees
        columns = ("Nume", "Poziție", "Salariu")
        self.tree = ttk.Treeview(employees_frame, columns=columns, height=15)
        self.tree.column("#0", width=30)
        self.tree.column("Nume", width=150)
        self.tree.column("Poziție", width=150)
        self.tree.column("Salariu", width=100)
        
        self.tree.heading("#0", text="ID")
        self.tree.heading("Nume", text="Nume")
        self.tree.heading("Poziție", text="Poziție")
        self.tree.heading("Salariu", text="Salariu")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder pentru "Nu ai acces"
        self.access_denied_label = ttk.Label(
            employees_frame,
            text="❌ Nu ai permisiuni pentru a vizualiza această instituție",
            font=("Segoe UI", 11)
        )
        
        # ===== BOTTOM: BUTOANE =====
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.add_button = ttk.Button(
            buttons_frame,
            text="➕ Adaugă Angajat",
            command=self.on_add_employee
        )
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_button = ttk.Button(
            buttons_frame,
            text="✏️ Editează",
            command=self.on_edit_employee
        )
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(
            buttons_frame,
            text="❌ Șterge",
            command=self.on_delete_employee
        )
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(buttons_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.reset_button = ttk.Button(
            buttons_frame,
            text="🔄 Reset Punctaj",
            command=self.on_reset_scores
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.deduct_button = ttk.Button(
            buttons_frame,
            text="📉 Scade Puncte",
            command=self.on_deduct_scores
        )
        self.deduct_button.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = ttk.Label(buttons_frame, text="", foreground="gray")
        self.info_label.pack(side=tk.LEFT, padx=20)
    
    def load_available_cities(self):
        """Încarcă lista de orașe"""
        try:
            institutions_by_city = self.perm_manager.get_all_institutions_by_city()
            cities = sorted(institutions_by_city.keys())
            self.city_combo['values'] = cities
            self.all_institutions_by_city = institutions_by_city
            
            if cities:
                self.city_combo.current(0)
                self.on_city_changed()
        except Exception as e:
            print(f"Error loading cities: {e}")
            messagebox.showerror("Eroare", f"Eroare la încărcarea orașelor: {e}")
    
    def on_city_changed(self, *args):
        """Se apelează când se schimbă orașul selectat"""
        city = self.city_var.get()
        if not city:
            return
        
        try:
            # Încarcă instituțiile pentru acest oraș
            institutions = self.all_institutions_by_city.get(city, [])
            self.institution_combo['values'] = institutions
            
            if institutions:
                self.institution_combo.current(0)
                self.on_institution_changed()
        except Exception as e:
            print(f"Error loading institutions: {e}")
    
    def on_institution_changed(self, *args):
        """Se apelează când se schimbă instituția selectată"""
        city = self.city_var.get()
        institution = self.institution_var.get()
        
        if not city or not institution:
            return
        
        self.current_city = city
        self.current_institution = institution
        
        # ===== VERIFICARE PERMISIUNI =====
        can_view = self.perm_manager.check_user_institution_permission(
            self.current_user_id, city, institution, 'can_view'
        )
        can_edit = self.perm_manager.check_user_institution_permission(
            self.current_user_id, city, institution, 'can_edit'
        )
        can_delete = self.perm_manager.check_user_institution_permission(
            self.current_user_id, city, institution, 'can_delete'
        )
        can_reset_scores = self.perm_manager.check_user_institution_permission(
            self.current_user_id, city, institution, 'can_reset_scores'
        )
        can_deduct_scores = self.perm_manager.check_user_institution_permission(
            self.current_user_id, city, institution, 'can_deduct_scores'
        )
        
        print(f"📋 Permisiuni pentru {city}/{institution}:")
        print(f"   can_view: {can_view}")
        print(f"   can_edit: {can_edit}")
        print(f"   can_delete: {can_delete}")
        print(f"   can_reset_scores: {can_reset_scores}")
        print(f"   can_deduct_scores: {can_deduct_scores}")
        
        # ===== CONTROL INTERFAȚĂ =====
        
        # 1. Afișează/ascunde lista angajați
        if can_view:
            self.tree.pack(fill=tk.BOTH, expand=True)
            self.access_denied_label.pack_forget()
            self.load_employees(city, institution)
        else:
            self.tree.pack_forget()
            self.access_denied_label.pack(fill=tk.BOTH, expand=True, pady=20)
            self.info_label.config(text="🚫 Acces refuzat")
        
        # 2. Activează/dezactivează butonul Adaugă
        if can_edit and can_view:
            self.add_button.config(state=tk.NORMAL)
        else:
            self.add_button.config(state=tk.DISABLED)
        
        # 3. Activează/dezactivează butonul Editează
        if can_edit and can_view:
            self.edit_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
        
        # 4. Activează/dezactivează butonul Șterge
        if can_delete and can_view:
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)
        
        # 5. Activează/dezactivează butonul Reset Punctaj
        if can_reset_scores and can_view:
            self.reset_button.config(state=tk.NORMAL)
        else:
            self.reset_button.config(state=tk.DISABLED)
        
        # 6. Activează/dezactivează butonul Scade Puncte
        if can_deduct_scores and can_view:
            self.deduct_button.config(state=tk.NORMAL)
        else:
            self.deduct_button.config(state=tk.DISABLED)
        
        # 7. Info label
        perm_text = f"👁️" if can_view else "❌"
        perm_text += f" | ✏️" if can_edit else " | ❌"
        perm_text += f" | 🔄" if can_reset_scores else " | ❌"
        perm_text += f" | 📉" if can_deduct_scores else " | ❌"
        self.info_label.config(text=f"Permisiuni: {perm_text}")
    
    def load_employees(self, city: str, institution: str):
        """Încarcă angajații pentru instituția selectată"""
        try:
            # TODO: Implementare cu încărcarea din Supabase/fișier
            self.tree.delete(*self.tree.get_children())
            
            # Exemplu de date
            employees = [
                ("1", "Ion Popescu", "Polițist", "2500 RON"),
                ("2", "Maria Ionescu", "Sergent", "3000 RON"),
                ("3", "George Șerban", "Ofițer", "3500 RON"),
            ]
            
            for emp in employees:
                self.tree.insert("", tk.END, text=emp[0], values=(emp[1], emp[2], emp[3]))
            
            self.employees = employees
            
        except Exception as e:
            print(f"Error loading employees: {e}")
    
    # ===== HANDLER-E PENTRU BUTOANE =====
    
    def on_add_employee(self):
        """Handler pentru butonul Adaugă Angajat"""
        print(f"✅ Adaugă angajat la {self.current_city}/{self.current_institution}")
        
        # Verificare permisiuni (redundant, dar sigur)
        if not self.perm_manager.check_user_institution_permission(
            self.current_user_id, self.current_city, self.current_institution, 'can_edit'
        ):
            messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
            return
        
        # Deschide dialog de adaugă
        messagebox.showinfo("Dialog Adaugă", "🔄 Dialog de adaugă angajat (de implementat)")
    
    def on_edit_employee(self):
        """Handler pentru butonul Editează"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selectare", "Selectează un angajat!")
            return
        
        # Verificare permisiuni
        if not self.perm_manager.check_user_institution_permission(
            self.current_user_id, self.current_city, self.current_institution, 'can_edit'
        ):
            messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
            return
        
        print(f"✏️ Editează angajat")
    
    def on_delete_employee(self):
        """Handler pentru butonul Șterge"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selectare", "Selectează un angajat!")
            return
        
        # Verificare permisiuni
        if not self.perm_manager.check_user_institution_permission(
            self.current_user_id, self.current_city, self.current_institution, 'can_delete'
        ):
            messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
            return
        
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi?"):
            print(f"❌ Șterge angajat")
    
    def on_reset_scores(self):
        """Handler pentru butonul Reset Punctaj"""
        # Verificare permisiuni
        if not self.perm_manager.check_user_institution_permission(
            self.current_user_id, self.current_city, self.current_institution, 'can_reset_scores'
        ):
            messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
            return
        
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să resetezi punctajul?"):
            print(f"🔄 Reset punctaj pentru {self.current_city}/{self.current_institution}")
    
    def on_deduct_scores(self):
        """Handler pentru butonul Scade Puncte"""
        # Verificare permisiuni
        if not self.perm_manager.check_user_institution_permission(
            self.current_user_id, self.current_city, self.current_institution, 'can_deduct_scores'
        ):
            messagebox.showerror("Eroare", "❌ Nu ai permisiuni pentru această acțiune!")
            return
        
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să scazi punctele?"):
            print(f"📉 Scade puncte pentru {self.current_city}/{self.current_institution}")


# ===== EXEMPLU DE FOLOSIRE =====
if __name__ == "__main__":
    
    # Simulare
    root = tk.Tk()
    root.title("Exemplu - Permisiuni Instituții")
    root.geometry("700x500")
    
    # Înlocuiți cu valorile reale
    from supabase_sync import SupabaseSync
    
    supabase_sync = SupabaseSync()  # Inițializez cu configurări reale
    current_user_discord_id = "123456"  # ID-ul utilizatorului curent
    data_dir = "d:/punctaj/data"  # Calea către directorul cu orașe
    
    app = InstitutionViewExample(root, supabase_sync, current_user_discord_id, data_dir)
    
    root.mainloop()
