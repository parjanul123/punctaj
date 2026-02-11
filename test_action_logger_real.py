# -*- coding: utf-8 -*-
"""
Test ACTION_LOGGER - Verifica daca logurile se salveaza corect
"""

# Simulam SUPABASE_SYNC fara a conecta la internet
class MockSupabaseSync:
    def __init__(self):
        self.url = "https://yzlkgifumrwqlfgimcai.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        self.table_logs = "audit_logs"

# Importa ActionLogger
from action_logger import ActionLogger

# Creeaza mock sync
mock_sync = MockSupabaseSync()

# Initializeaza ACTION_LOGGER
action_logger = ActionLogger(mock_sync, logs_dir="logs")

print("🧪 TEST: ACTION_LOGGER - Logging per institutie\n")

# Test 1: Log pentru Saint_Denis/Politie
print("Test 1: Adaugare angajat in Saint_Denis/Politie")
result = action_logger.log_add_employee(
    discord_id="parjanu",
    city="Saint_Denis",
    institution_name="Politie",
    employee_name="Agent Smith",
    employee_data={"name": "Agent Smith", "points": 50}
)
print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}\n")

# Test 2: Edit points in Saint_Denis/Politie
print("Test 2: Edit puncte Agent Smith")
result = action_logger.log_edit_points(
    discord_id="admin_user",
    city="Saint_Denis",
    institution_name="Politie",
    employee_name="Agent Smith",
    old_points=50,
    new_points=75,
    action="add"
)
print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}\n")

# Test 3: Delete employee in BlackWater/Politie
print("Test 3: Stergere angajat in BlackWater/Politie")
result = action_logger.log_delete_employee(
    discord_id="parjanu",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Officer Johnson",
    employee_data={"name": "Officer Johnson", "points": 100}
)
print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}\n")

# Test 4: Edit employee in BlackWater/Politie
print("Test 4: Editare date angajat in BlackWater/Politie")
result = action_logger.log_edit_employee_safe(
    discord_id="admin_user",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Officer Brown",
    changes="Email: old@email.com → new@email.com"
)
print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}\n")

# Verifica structura finala
print("="*60)
print("📁 STRUCTURA FINALA A LOGURILOR:")
print("="*60)

import os
import json

logs_dir = "logs"
if os.path.exists(logs_dir):
    for root, dirs, files in os.walk(logs_dir):
        level = root.replace(logs_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        rel_path = os.path.relpath(root, os.getcwd())
        print(f'{indent}📂 {os.path.basename(root)}/') if level > 0 else print(f'{indent}📂 logs/')
        
        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files):
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            
            if file.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        count = len(content)
                        print(f'{subindent}📄 {file} ({count} logs, {file_size} bytes)')
                    elif isinstance(content, dict):
                        count = content.get('total_actions', '?')
                        print(f'{subindent}📄 {file} ({count} total actions, {file_size} bytes)')
else:
    print("❌ logs folder not found!")

# Arata continut detailed
print("\n" + "="*60)
print("📖 DETALII LOGURI:")
print("="*60)

for root, dirs, files in os.walk(logs_dir):
    for file in sorted(files):
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            rel_path = os.path.relpath(file_path, os.getcwd())
            print(f"\n{rel_path}:")
            
            if isinstance(content, list):
                for i, log in enumerate(content, 1):
                    print(f"  [{i}] {log['action_type']}")
                    print(f"      User: {log['discord_id']}")
                    print(f"      City: {log['city']}")
                    print(f"      Institution: {log['institution']}")
                    print(f"      Details: {log['details']}")
                    print(f"      Time: {log['timestamp']}")
            elif isinstance(content, dict):
                print(f"  Updated at: {content.get('updated_at', '?')}")
                print(f"  Users: {content.get('users_connected', [])}")
                print(f"  Cities: {list(content.get('cities_modified', {}).keys())}")
                print(f"  Total actions: {content.get('total_actions', 0)}")
                
                # Arata institutii modificate
                inst_mod = content.get('institutions_modified', {})
                for inst_key, inst_data in inst_mod.items():
                    actions_count = len(inst_data.get('actions', []))
                    print(f"    • {inst_key}: {actions_count} actions")

print("\n" + "="*60)
print("✅ TEST COMPLETED!")
print("="*60)
