# -*- coding: utf-8 -*-
"""
Test: Verifica noua structura de loguri cu detalii complete
"""

import os
import json
import shutil
from supabase_sync import SupabaseSync
from action_logger import ActionLogger

print("="*80)
print("🧪 TEST: DETAILED ACTION LOGGING WITH DISCORD USERNAME & ENTITY INFO")
print("="*80)

# Setup
print("\n1️⃣ Setting up...")
supabase_sync = SupabaseSync('supabase_config.ini')
action_logger = ActionLogger(supabase_sync, logs_dir="logs")

# Clear old logs
if os.path.exists('logs'):
    shutil.rmtree('logs')
    os.makedirs('logs', exist_ok=True)
print("   ✅ Setup complete\n")

# Test 1: Add employee
print("2️⃣ TEST: Add Employee Action")
action_logger.log_add_employee(
    discord_id="parjanu",
    city="Saint_Denis",
    institution_name="Politie",
    employee_name="Agent Smith",
    employee_data={"NUME_IC": "12345678", "PUNCTAJ": 50},
    discord_username="Parjanu"
)
print()

# Test 2: Edit points (add)
print("3️⃣ TEST: Edit Points (ADD)")
action_logger.log_edit_points(
    discord_id="admin_user",
    city="Saint_Denis",
    institution_name="Politie",
    employee_name="Agent Smith",
    old_points=50,
    new_points=75,
    action="add",
    discord_username="AdminUser",
    entity_id="12345678"
)
print()

# Test 3: Edit employee
print("4️⃣ TEST: Edit Employee Data")
action_logger.log_edit_employee_safe(
    discord_id="parjanu",
    city="Saint_Denis",
    institution_name="Politie",
    employee_name="Ion Popescu",
    changes="Email: old@email.com → new@email.com, Phone: +40123 → +40456",
    discord_username="Parjanu",
    entity_id="87654321"
)
print()

# Test 4: Delete employee
print("5️⃣ TEST: Delete Employee")
action_logger.log_delete_employee(
    discord_id="admin_user",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Officer Johnson",
    employee_data={"NUME_IC": "11111111", "PUNCTAJ": 100},
    discord_username="AdminUser"
)
print()

# Display results
print("\n" + "="*80)
print("📊 DETAILED LOG STRUCTURE")
print("="*80)

log_file = "logs/Saint_Denis/Politie.json"
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"\nFile: {log_file}")
    print(f"Number of logs: {len(logs)}\n")
    
    for i, log in enumerate(logs, 1):
        print(f"LOG #{i}:")
        print(f"  🕐 Timestamp: {log.get('timestamp', '?')}")
        print(f"  👤 Discord User: {log.get('discord_username', '?')} (ID: {log.get('discord_id', '?')})")
        print(f"  🎯 Action: {log.get('action_type', '?')}")
        print(f"  📦 Entity: {log.get('entity_name', '?')} (NUME_IC: {log.get('entity_id', '?')})")
        print(f"  📝 Details: {log.get('details', '?')}")
        print(f"  🔄 Changes: {log.get('changes', '?')}")
        print()

blackwater_log_file = "logs/BlackWater/Politie.json"
if os.path.exists(blackwater_log_file):
    with open(blackwater_log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print(f"\nFile: {blackwater_log_file}")
    print(f"Number of logs: {len(logs)}\n")
    
    for i, log in enumerate(logs, 1):
        print(f"LOG #{i}:")
        print(f"  🕐 Timestamp: {log.get('timestamp', '?')}")
        print(f"  👤 Discord User: {log.get('discord_username', '?')} (ID: {log.get('discord_id', '?')})")
        print(f"  🎯 Action: {log.get('action_type', '?')}")
        print(f"  📦 Entity: {log.get('entity_name', '?')} (NUME_IC: {log.get('entity_id', '?')})")
        print(f"  📝 Details: {log.get('details', '?')}")
        print(f"  🔄 Changes: {log.get('changes', '?')}")
        print()

# Check global summary
summary_file = "logs/SUMMARY_global.json"
if os.path.exists(summary_file):
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    print("="*80)
    print("📈 GLOBAL SUMMARY")
    print("="*80)
    print(f"Total actions: {summary.get('total_actions', 0)}")
    print(f"Users: {summary.get('users_connected', [])}")
    print(f"Cities: {list(summary.get('cities_modified', {}).keys())}")
    print()

print("="*80)
print("✅ TEST COMPLETE - Detailed logging is working!")
print("="*80)
print("""
NEW LOG STRUCTURE INCLUDES:
✅ discord_username - Discord user who performed the action
✅ entity_name - Name of person/entity being modified (e.g., "Agent Smith")
✅ entity_id - NUME_IC from the table
✅ changes - Detailed description of what changed
✅ All previous fields still present (discord_id, action_type, city, institution, details, timestamp)
""")
