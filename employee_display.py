#!/usr/bin/env python3
"""
Enhanced employee display with visual grouping and organization
"""

import tkinter as tk
from tkinter import ttk

class EmployeeGroupFrame(tk.Frame):
    """Display employees grouped by city and institution with clear visual hierarchy"""
    
    def __init__(self, parent, city_name, institution_name, employees, ranks_map=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.city_name = city_name
        self.institution_name = institution_name
        self.employees = employees
        self.ranks_map = ranks_map or {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the visual hierarchy"""
        
        # ===== HEADER: CITY + INSTITUTION =====
        header = tk.Frame(self, bg="#1565c0", height=50)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # City name (large, bold)
        city_label = tk.Label(
            header,
            text=f"📍 {self.city_name}",
            font=("Segoe UI", 14, "bold"),
            bg="#1565c0",
            fg="white"
        )
        city_label.pack(side="left", padx=15, pady=10)
        
        # Institution name (large, bold)
        inst_label = tk.Label(
            header,
            text=f"🏢 {self.institution_name}",
            font=("Segoe UI", 12, "bold"),
            bg="#1565c0",
            fg="#e3f2fd"
        )
        inst_label.pack(side="left", padx=10, pady=10)
        
        # Employee count
        count_label = tk.Label(
            header,
            text=f"({len(self.employees)} employees)",
            font=("Segoe UI", 10),
            bg="#1565c0",
            fg="#b3e5fc"
        )
        count_label.pack(side="left", padx=5, pady=10)
        
        # ===== EMPLOYEE LIST =====
        content = tk.Frame(self, bg="#f5f5f5")
        content.pack(fill="both", expand=True, padx=0, pady=0)
        
        if not self.employees:
            empty_label = tk.Label(
                content,
                text="No employees",
                font=("Segoe UI", 10, "italic"),
                bg="#f5f5f5",
                fg="#999"
            )
            empty_label.pack(pady=20)
        else:
            # Create scrollable frame
            canvas = tk.Canvas(content, bg="#f5f5f5", highlightthickness=0)
            scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add employees
            for i, emp in enumerate(self.employees):
                self._create_employee_card(scrollable_frame, emp, i % 2 == 0)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
    
    def _create_employee_card(self, parent, emp, alternate_color=False):
        """Create a visual card for each employee"""
        
        bg_color = "#ffffff" if alternate_color else "#fafafa"
        
        card = tk.Frame(parent, bg=bg_color, relief="flat", height=60)
        card.pack(fill="x", padx=10, pady=5)
        card.pack_propagate(False)
        
        # Left: Name and Discord
        left_frame = tk.Frame(card, bg=bg_color)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        
        name = emp.get("NUME IC") or emp.get("employee_name", "Unknown")
        discord = emp.get("DISCORD") or emp.get("discord_username", "")
        
        name_label = tk.Label(
            left_frame,
            text=f"👤 {name}",
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg="#1565c0"
        )
        name_label.pack(anchor="w")
        
        if discord:
            discord_label = tk.Label(
                left_frame,
                text=f"Discord: {discord}",
                font=("Segoe UI", 8),
                bg=bg_color,
                fg="#666"
            )
            discord_label.pack(anchor="w")
        
        # Right: Rank, Role, Points
        right_frame = tk.Frame(card, bg=bg_color)
        right_frame.pack(side="right", padx=10, pady=8)
        
        rank = emp.get("RANK") or emp.get("rank", "?")
        role = emp.get("ROLE") or emp.get("role", "")
        points = emp.get("PUNCTAJ") or emp.get("points", 0)
        
        # Rank with role
        role_display = self.ranks_map.get(str(rank), role) if self.ranks_map else role
        
        rank_label = tk.Label(
            right_frame,
            text=f"Rank {rank}: {role_display}",
            font=("Segoe UI", 9),
            bg=bg_color,
            fg="#f57c00"
        )
        rank_label.pack(anchor="e")
        
        # Points indicator
        points_int = int(points) if isinstance(points, (int, str, float)) else 0
        points_color = "#c62828" if points_int == 0 else "#2e7d32" if points_int > 0 else "#000"
        
        points_label = tk.Label(
            right_frame,
            text=f"⭐ {points_int} points",
            font=("Segoe UI", 9, "bold"),
            bg=bg_color,
            fg=points_color
        )
        points_label.pack(anchor="e")


def create_organized_view(parent, data_structure, ranks_map=None):
    """
    Create organized view with all cities and institutions
    
    Args:
        parent: Parent widget
        data_structure: Dict with format {city: {institution: [employees]}}
        ranks_map: Dict mapping rank numbers to role names
    """
    
    main_frame = tk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # Create canvas with scrollbar
    canvas = tk.Canvas(main_frame, bg="#f0f0f0", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Add groups for each city/institution
    for city in sorted(data_structure.keys()):
        institutions = data_structure[city]
        
        for institution in sorted(institutions.keys()):
            employees = institutions[institution]
            
            group = EmployeeGroupFrame(
                scrollable_frame,
                city,
                institution,
                employees,
                ranks_map=ranks_map,
                bg="#ffffff",
                relief="solid",
                borderwidth=1
            )
            group.pack(fill="x", padx=10, pady=10)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return main_frame


# ===== TEST =====

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Employee Organization Test")
    root.geometry("800x600")
    
    # Test data
    data = {
        "BlackWater": {
            "Politie": [
                {
                    "NUME IC": "Dandeny Munoz",
                    "DISCORD": "Parjanu",
                    "RANK": "4",
                    "ROLE": "Plutonier",
                    "PUNCTAJ": 10
                },
                {
                    "NUME IC": "Vulpe Fuchs",
                    "DISCORD": "vLp",
                    "RANK": "5",
                    "ROLE": "Locotenent Instructor",
                    "PUNCTAJ": 5
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
                    "PUNCTAJ": 0
                }
            ]
        }
    }
    
    ranks_map = {
        "1": "Officer",
        "2": "Caporal",
        "3": "Sergent",
        "4": "Plutonier",
        "5": "Locotenent Instructor",
        "6": "Sherif Adjunct",
        "7": "Sherif"
    }
    
    create_organized_view(root, data, ranks_map)
    
    root.mainloop()
