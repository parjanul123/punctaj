# -*- coding: utf-8 -*-
"""
Diagnostic: Verifica ce se salveaza in save_institution
"""

import json
import os

print("="*80)
print("🔍 DIAGNOSTIC: SAVE_INSTITUTION BEHAVIOR")
print("="*80)

# Verifica logurile create
logs_dir = "logs"

if os.path.exists(logs_dir):
    print(f"\n📁 Found logs directory with:")
    
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith('.json') and 'SUMMARY' not in file:
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                print(f"\n{filepath}: {len(logs)} entries")
                
                for log in logs:
                    print(f"  - {log['timestamp']}: {log['action_type']}")
                    print(f"    User: {log.get('discord_username', log.get('discord_id', '?'))}")
                    print(f"    Entity: {log.get('entity_name', 'N/A')}")
                    print(f"    Details: {log.get('details', 'N/A')}")
                    print()

print("\n" + "="*80)
print("🎯 ISSUES & SOLUTIONS")
print("="*80)
print("""
PROBLEM 1: Not logging in REAL TIME
- Currently logs only when save_institution() is called
- save_institution() is called when user clicks Save or closes dialog
- Solution: Need to log IMMEDIATELY when UI values change

PROBLEM 2: FALSE edits in logs
- save_institution() saves ALL rows even if not modified
- Logs show "edit_institution" even for unchanged data
- Solution: Track which rows actually changed, log only those

HOW TO FIX:
1. Modify save_institution() to track ACTUAL changes
2. Compare old data with new data
3. Log only rows that were ACTUALLY modified
4. Include field-by-field change details
""")

print("\n" + "="*80)
print("📝 RECOMMENDATION")
print("="*80)
print("""
Instead of logging in save_institution():
  
Instead create a new approach:

1. Track changes WHILE EDITING:
   - When user edits a cell in treeview
   - Immediately save the FIELD change
   - Log the specific field that changed (e.g., "PUNCTAJ: 50 → 75")

2. Detect ACTUAL modifications:
   - Compare updated_items with all rows
   - Only log rows in updated_items
   - Provide field-by-field diff

3. Log multiple field changes as one action:
   - Group all changes to same entity in one log
   - Timestamp: when first change was made
   - Changes: all fields modified and their values

Current implementation logs:
  "Updated 3 entries" (but might be unchanged!)

Should log:
  "Updated 1 entry: PUNCTAJ 50→75, PREZENTA 10→12"
""")
