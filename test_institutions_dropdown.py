#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test institutions dropdown detection
"""
import sys
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from admin_ui import get_available_institutions

print("=" * 70)
print("DETECTING AVAILABLE CITIES AND INSTITUTIONS")
print("=" * 70)

cities_dict = get_available_institutions()

print(f"\nTotal cities found: {len(cities_dict)}\n")

for city, institutions in sorted(cities_dict.items()):
    print(f"📍 {city}")
    for inst in institutions:
        print(f"   ✓ {inst}")
    print()

print("=" * 70)
print("EXPECTED IN ADMIN PANEL:")
print("=" * 70)
print("""
City Dropdown: [BlackWater] [Saint_Denis]
Institution Dropdown (when city selected):
  - BlackWater → [Politie] [Pompieri] ...
  - Saint_Denis → [Politie] [Pompieri] ...
""")
