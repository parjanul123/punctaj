#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visual test of the new Logs Window
"""
import sys
sys.path.insert(0, 'd:\\punctaj')

import tkinter as tk
from tkinter import ttk
from admin_ui import get_available_institutions

# Create main window
root = tk.Tk()
root.title("Admin Panel - Test")
root.geometry("400x200")

# Create notebook like admin panel
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Tab 1: Users
users_frame = ttk.Frame(notebook)
notebook.add(users_frame, text="Utilizatori")
ttk.Label(users_frame, text="Users management here...").pack(padx=20, pady=20)

# Tab 2: Statistics
stats_frame = ttk.Frame(notebook)
notebook.add(stats_frame, text="Statistici")
ttk.Label(stats_frame, text="Statistics here...").pack(padx=20, pady=20)

# Button bar at bottom
button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X, padx=5, pady=5)

def open_logs_window():
    """Open a separate window for action logs with filters"""
    logs_window = tk.Toplevel(root)
    logs_window.title("Loguri Acțiuni - Filtrare per Instituție")
    logs_window.geometry("1100x700")
    logs_window.resizable(True, True)
    
    # Get available institutions
    cities_dict = get_available_institutions()
    cities_list = sorted(cities_dict.keys())
    
    print("Cities detected:", cities_list)
    print("Institutions:", cities_dict)
    
    # Top frame with filters
    top_frame = ttk.LabelFrame(logs_window, text="Filtre", padding=5)
    top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(top_frame, text="Utilizator:").pack(side=tk.LEFT, padx=5)
    user_entry = ttk.Entry(top_frame, width=12)
    user_entry.pack(side=tk.LEFT, padx=3)
    
    ttk.Label(top_frame, text="Acțiune:").pack(side=tk.LEFT, padx=5)
    action_entry = ttk.Entry(top_frame, width=12)
    action_entry.pack(side=tk.LEFT, padx=3)
    
    ttk.Label(top_frame, text="Oraș:").pack(side=tk.LEFT, padx=5)
    city_combo = ttk.Combobox(top_frame, width=12, values=[''] + cities_list, state='readonly')
    city_combo.pack(side=tk.LEFT, padx=3)
    city_combo.set('')
    
    ttk.Label(top_frame, text="Instituție:").pack(side=tk.LEFT, padx=5)
    institution_combo = ttk.Combobox(top_frame, width=12, state='readonly')
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
    
    # Example logs display
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
    
    # Add example log
    logs_tree.insert('', tk.END, values=(
        '10:30',
        'parjanu',
        'delete_employee',
        'BlackWater',
        'Politie',
        'Ion Popescu',
        'Deleted employee'
    ))
    
    ttk.Button(top_frame, text="🔄 Reîncarcă", command=lambda: print("Refresh clicked")).pack(side=tk.LEFT, padx=5)

ttk.Button(button_frame, text="📋 Loguri Acțiuni", command=open_logs_window).pack(side=tk.LEFT, padx=5)

print("✓ UI Test Window Created")
print("Click '📋 Loguri Acțiuni' button to open logs window")
print("\nNow you can:")
print("  1. Select a City from dropdown")
print("  2. Select an Institution from dropdown (auto-updated)")
print("  3. See logs filtered per institution")

root.mainloop()
