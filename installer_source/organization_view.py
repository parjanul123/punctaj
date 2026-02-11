#!/usr/bin/env python3
"""
Create main view with organized hierarchy:
City -> Institution -> Employees

This replaces the notebook tabs with a clear visual structure
"""

import tkinter as tk
from tkinter import ttk

def create_city_institution_view(parent, structure, on_employee_click=None, ranks_map=None):
    """
    Create hierarchical view: City -> Institution -> Employees
    
    Args:
        parent: Parent widget
        structure: {city: {institution: [employees]}}
        on_employee_click: Callback when clicking employee
        ranks_map: {rank_number: role_name}
    """
    
    main_frame = tk.Frame(parent, bg="#f5f5f5")
    main_frame.pack(fill="both", expand=True)
    
    # Canvas with scrollbar
    canvas = tk.Canvas(main_frame, bg="#f5f5f5", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#f5f5f5")
    
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Build hierarchy
    for city in sorted(structure.keys()):
        # ===== CITY HEADER =====
        city_frame = tk.Frame(scroll_frame, bg="#1565c0", height=50)
        city_frame.pack(fill="x", padx=5, pady=10)
        city_frame.pack_propagate(False)
        
        city_label = tk.Label(
            city_frame,
            text=f"  📍 {city.upper()}",
            font=("Segoe UI", 14, "bold"),
            bg="#1565c0",
            fg="white",
            anchor="w"
        )
        city_label.pack(fill="x", padx=10, pady=10)
        
        institutions = structure[city]
        
        # ===== INSTITUTIONS UNDER THIS CITY =====
        city_content = tk.Frame(scroll_frame, bg="#f5f5f5")
        city_content.pack(fill="x", padx=20, pady=0)
        
        for institution in sorted(institutions.keys()):
            employees = institutions[institution]
            
            # Institution header
            inst_header = tk.Frame(city_content, bg="#0d47a1", height=40)
            inst_header.pack(fill="x", padx=10, pady=(10, 0))
            inst_header.pack_propagate(False)
            
            inst_label = tk.Label(
                inst_header,
                text=f"    🏢 {institution}   ({len(employees)} employees)",
                font=("Segoe UI", 11, "bold"),
                bg="#0d47a1",
                fg="#e3f2fd",
                anchor="w"
            )
            inst_label.pack(fill="x", padx=10, pady=8)
            
            # Employees under this institution
            emp_frame = tk.Frame(city_content, bg="#ffffff", relief="solid", borderwidth=1)
            emp_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            if not employees:
                empty_label = tk.Label(
                    emp_frame,
                    text="        (No employees)",
                    font=("Segoe UI", 9, "italic"),
                    bg="#ffffff",
                    fg="#999"
                )
                empty_label.pack(pady=10)
            else:
                for i, emp in enumerate(employees):
                    create_employee_row(emp_frame, emp, i % 2 == 0, ranks_map, on_employee_click)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return main_frame


def create_employee_row(parent, emp, alternate_bg=False, ranks_map=None, on_click=None):
    """Create visual row for single employee"""
    
    bg = "#ffffff" if alternate_bg else "#f9f9f9"
    
    row = tk.Frame(parent, bg=bg, height=50, relief="flat")
    row.pack(fill="x", padx=0, pady=0)
    row.pack_propagate(False)
    
    # Make clickable
    if on_click:
        row.bind("<Button-1>", lambda e: on_click(emp))
        row.config(cursor="hand2")
    
    # Left: Name and Discord
    left = tk.Frame(row, bg=bg)
    left.pack(side="left", fill="both", expand=True, padx=15, pady=8)
    
    name = emp.get("NUME IC") or emp.get("employee_name", "Unknown")
    discord = emp.get("DISCORD") or emp.get("discord_username", "")
    
    # Name (bold)
    name_label = tk.Label(
        left,
        text=f"👤 {name}",
        font=("Segoe UI", 10, "bold"),
        bg=bg,
        fg="#1565c0",
        anchor="w"
    )
    name_label.pack(anchor="w")
    
    # Discord (small, gray)
    if discord:
        discord_label = tk.Label(
            left,
            text=f"Discord: {discord}",
            font=("Segoe UI", 8),
            bg=bg,
            fg="#666",
            anchor="w"
        )
        discord_label.pack(anchor="w")
    
    # Middle: Rank + Role
    middle = tk.Frame(row, bg=bg)
    middle.pack(side="left", fill="both", expand=True, padx=10, pady=8)
    
    rank = str(emp.get("RANK") or emp.get("rank", "?"))
    role = emp.get("ROLE") or emp.get("role", "")
    
    if ranks_map and rank in ranks_map:
        role_display = ranks_map[rank]
    else:
        role_display = role
    
    rank_label = tk.Label(
        middle,
        text=f"Rank {rank}: {role_display}",
        font=("Segoe UI", 9),
        bg=bg,
        fg="#f57c00",
        anchor="w"
    )
    rank_label.pack(anchor="w")
    
    # Right: Points
    right = tk.Frame(row, bg=bg)
    right.pack(side="right", padx=15, pady=8)
    
    points = int(emp.get("PUNCTAJ") or emp.get("points", 0))
    points_color = "#c62828" if points == 0 else "#2e7d32"
    
    points_label = tk.Label(
        right,
        text=f"⭐ {points}",
        font=("Segoe UI", 10, "bold"),
        bg=bg,
        fg=points_color
    )
    points_label.pack()
    
    # Hover effect
    def on_enter(e):
        row.config(bg="#e3f2fd")
        for child in row.winfo_children():
            child.config(bg="#e3f2fd")
        for child in left.winfo_children():
            child.config(bg="#e3f2fd")
        for child in middle.winfo_children():
            child.config(bg="#e3f2fd")
        for child in right.winfo_children():
            child.config(bg="#e3f2fd")
    
    def on_leave(e):
        row.config(bg=bg)
        for child in row.winfo_children():
            child.config(bg=bg)
        for child in left.winfo_children():
            child.config(bg=bg)
        for child in middle.winfo_children():
            child.config(bg=bg)
        for child in right.winfo_children():
            child.config(bg=bg)
    
    row.bind("<Enter>", on_enter)
    row.bind("<Leave>", on_leave)


# ===== TEST =====

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Organization View Test")
    root.geometry("900x700")
    
    test_data = {
        "BlackWater": {
            "Politie": [
                {
                    "NUME IC": "Dandeny Munoz",
                    "DISCORD": "Parjanu",
                    "RANK": "4",
                    "ROLE": "Plutonier",
                    "PUNCTAJ": 10,
                    "SERIA": "R87G65U68"
                },
                {
                    "NUME IC": "Vulpe Fuchs",
                    "DISCORD": "vLp",
                    "RANK": "5",
                    "ROLE": "Locotenent Instructor",
                    "PUNCTAJ": 5,
                    "SERIA": "V37I61A62"
                }
            ]
        },
        "Saint_Denis": {
            "Politie": [
                {
                    "NUME IC": "Ganea Ionut",
                    "DISCORD": "Ganea",
                    "RANK": "6",
                    "ROLE": "Sherif Adjunct",
                    "PUNCTAJ": 0,
                    "SERIA": "Z29E43M59"
                }
            ]
        }
    }
    
    ranks = {
        "1": "Officer",
        "2": "Caporal",
        "3": "Sergent",
        "4": "Plutonier",
        "5": "Locotenent Instructor",
        "6": "Sherif Adjunct",
        "7": "Sherif"
    }
    
    def on_click(emp):
        print(f"Clicked: {emp.get('NUME IC')}")
    
    create_city_institution_view(root, test_data, on_click, ranks)
    
    root.mainloop()
