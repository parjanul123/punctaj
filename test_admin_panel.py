#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Admin Panel with Logs button
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import ttk
from admin_ui import open_admin_panel

# Mock Supabase sync
class MockSupabaseSync:
    def __init__(self):
        self.enabled = True
        self.url = "https://yzlkgifumrwqlfgimcai.supabase.co"
        self.key = "test_key"

# Mock Discord Auth
class MockDiscordAuth:
    def __init__(self):
        self.discord_id = "test_user_123"

# Create main window
root = tk.Tk()
root.title("PunctajManager - Admin Test")
root.geometry("500x300")

ttk.Label(root, text="Admin Panel Test", font=("Arial", 14, "bold")).pack(padx=20, pady=20)
ttk.Label(root, text="Click button below to open Admin Panel").pack(padx=20, pady=10)

def open_admin():
    supabase = MockSupabaseSync()
    discord = MockDiscordAuth()
    open_admin_panel(root, supabase, discord)
    print("✓ Admin Panel opened")
    print("✓ Look for '📋 Loguri Acțiuni' button at the bottom")

ttk.Button(root, text="🔓 Deschide Admin Panel", command=open_admin).pack(padx=20, pady=10)

print("=" * 60)
print("ADMIN PANEL TEST")
print("=" * 60)
print("\n1. Click '🔓 Deschide Admin Panel' button")
print("2. Admin panel window should appear")
print("3. Look for '📋 Loguri Acțiuni' button at the bottom")
print("4. Click it to open logs window")
print("5. Select City and Institution from dropdowns")
print("\n" + "=" * 60)

root.mainloop()
