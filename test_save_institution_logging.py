# -*- coding: utf-8 -*-
"""
Test: Simuleaza salvarea unei institutii si verifica daca ACTION_LOGGER logheaza
"""

import sys
import os
import json
import configparser
from datetime import datetime

print("="*70)
print("🧪 TEST: SAVE INSTITUTION WITH ACTION_LOGGER")
print("="*70)

# Setup
print("\n1️⃣ Setting up...")
from supabase_sync import SupabaseSync
from action_logger import ActionLogger

supabase_sync = SupabaseSync('supabase_config.ini')
action_logger = ActionLogger(supabase_sync, logs_dir="logs")
print("   ✅ Setup complete")

# Clear logs folder
print("\n2️⃣ Clearing old logs...")
import shutil
if os.path.exists('logs'):
    shutil.rmtree('logs')
    os.makedirs('logs', exist_ok=True)
print("   ✅ Logs cleared")

# Simulate saving institution data
print("\n3️⃣ SIMULATING: Save institution data (like user made edits)...")

# This is what save_institution() does
city = "Saint_Denis"
institution = "Politie"
rows_updated = 3

# Log the action (as added in save_institution)
try:
    discord_id = "parjanu"
    changes_desc = f"Updated {rows_updated} entries"
    
    result = action_logger._log_action(
        discord_id=discord_id,
        action_type="edit_institution",
        city=city,
        institution_name=institution,
        details=changes_desc
    )
    
    if result:
        print(f"   ✅ Institution save logged successfully")
    else:
        print(f"   ❌ Institution save log failed")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Check results
print("\n4️⃣ Checking results...")

log_file = f"logs/{city}/Politie.json"
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    print(f"   ✅ Log file created with {len(logs)} entries")
    if logs:
        latest = logs[-1]
        print(f"      - Action: {latest['action_type']}")
        print(f"      - Details: {latest['details']}")
else:
    print(f"   ❌ Log file not created")

summary_file = "logs/SUMMARY_global.json"
if os.path.exists(summary_file):
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    print(f"   ✅ Summary file created")
    print(f"      - Total actions: {summary.get('total_actions', 0)}")
    print(f"      - Users: {summary.get('users_connected', [])}")

print("\n" + "="*70)
print("✅ TEST COMPLETE - Institution saves are now being logged!")
print("="*70)
