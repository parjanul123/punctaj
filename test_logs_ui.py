#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visual test of the logs dropdown UI
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk
from admin_ui import get_available_institutions

# Create test window
root = tk.Tk()
root.title("Admin Panel - Loguri Acțiuni (Test)")
root.geometry("900x600")

# Get available institutions
cities_dict = get_available_institutions()
cities_list = sorted(cities_dict.keys())

# Create frame like in admin_ui
top_frame = ttk.Frame(root)
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

# Initialize institution dropdown with first city
if cities_list:
    institution_combo['values'] = [''] + cities_dict.get(cities_list[0], [])

ttk.Button(top_frame, text="Reîncarcă loguri").pack(side=tk.LEFT, padx=5)

# Info text
info_frame = ttk.Frame(root)
info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

info_text = tk.Text(info_frame, height=20, width=80, wrap=tk.WORD)
info_text.pack(fill=tk.BOTH, expand=True)

info_text.insert(tk.END, "INSTRUCTIONS:\n\n")
info_text.insert(tk.END, "1. Select a City from the 'Oraș' dropdown\n")
info_text.insert(tk.END, "2. The 'Instituție' dropdown will automatically populate\n")
info_text.insert(tk.END, "3. Select an Institution to filter logs\n\n")
info_text.insert(tk.END, "AVAILABLE CITIES:\n")
for city in cities_list:
    info_text.insert(tk.END, f"  • {city}\n")
    for inst in cities_dict[city]:
        info_text.insert(tk.END, f"    - {inst}\n")

info_text.config(state=tk.DISABLED)

print("✓ UI Test Window Created")
print("Open the window to see the dropdown selectors")
print("\nAvailable Cities:", cities_list)
print("Institutions:", cities_dict)

root.mainloop()
