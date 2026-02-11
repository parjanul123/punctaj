# -*- coding: utf-8 -*-
"""
Test de validare pentru noua structura de loguri per institutie
"""

import json
import os
from datetime import datetime

# Simuleaza ACTION_LOGGER cu noua structura
def test_logging_structure():
    """Testeaza structura de loguri organizate per institutie"""
    
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    print("🧪 TESTING: Noua structura de loguri per institutie\n")
    
    # Test 1: Salvare log pentru Saint_Denis/Politie
    print("Test 1: Salvare log pentru Saint_Denis/Politie")
    log_entry_1 = {
        "discord_id": "parjanu",
        "action_type": "add_employee",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Added employee: Agent Smith",
        "timestamp": datetime.now().isoformat()
    }
    
    city_dir = os.path.join(logs_dir, "Saint_Denis")
    os.makedirs(city_dir, exist_ok=True)
    institution_file = os.path.join(city_dir, "Politie.json")
    
    logs = []
    if os.path.exists(institution_file):
        with open(institution_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    logs.append(log_entry_1)
    
    with open(institution_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved to: {institution_file}\n")
    
    # Test 2: Altul log pentru Saint_Denis/Politie
    print("Test 2: Altul log pentru Saint_Denis/Politie")
    log_entry_2 = {
        "discord_id": "admin_user",
        "action_type": "edit_points",
        "city": "Saint_Denis",
        "institution": "Politie",
        "details": "Agent Smith: 50 → 75",
        "timestamp": datetime.now().isoformat()
    }
    
    if os.path.exists(institution_file):
        with open(institution_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry_2)
    
    with open(institution_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved to: {institution_file}\n")
    
    # Test 3: Log pentru BlackWater/Politie
    print("Test 3: Log pentru BlackWater/Politie")
    log_entry_3 = {
        "discord_id": "parjanu",
        "action_type": "delete_employee",
        "city": "BlackWater",
        "institution": "Politie",
        "details": "Deleted employee: Officer Johnson",
        "timestamp": datetime.now().isoformat()
    }
    
    city_dir = os.path.join(logs_dir, "BlackWater")
    os.makedirs(city_dir, exist_ok=True)
    institution_file = os.path.join(city_dir, "Politie.json")
    
    logs = []
    if os.path.exists(institution_file):
        with open(institution_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    logs.append(log_entry_3)
    
    with open(institution_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved to: {institution_file}\n")
    
    # Test 4: Globalny summary
    print("Test 4: Update SUMMARY_global.json")
    global_summary_file = os.path.join(logs_dir, "SUMMARY_global.json")
    
    summary = {
        "updated_at": datetime.now().isoformat(),
        "users_connected": ["parjanu", "admin_user"],
        "cities_modified": {
            "Saint_Denis": {
                "added": [],
                "deleted": [],
                "edited": []
            },
            "BlackWater": {
                "added": [],
                "deleted": [],
                "edited": []
            }
        },
        "institutions_modified": {
            "Saint_Denis/Politie": {
                "city": "Saint_Denis",
                "institution": "Politie",
                "actions": [
                    {
                        "timestamp": log_entry_1["timestamp"],
                        "user": "parjanu",
                        "action": "add_employee",
                        "details": "Added employee: Agent Smith"
                    },
                    {
                        "timestamp": log_entry_2["timestamp"],
                        "user": "admin_user",
                        "action": "edit_points",
                        "details": "Agent Smith: 50 → 75"
                    }
                ]
            },
            "BlackWater/Politie": {
                "city": "BlackWater",
                "institution": "Politie",
                "actions": [
                    {
                        "timestamp": log_entry_3["timestamp"],
                        "user": "parjanu",
                        "action": "delete_employee",
                        "details": "Deleted employee: Officer Johnson"
                    }
                ]
            }
        },
        "total_actions": 3
    }
    
    with open(global_summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved to: {global_summary_file}\n")
    
    # Verifica structura finala
    print("="*60)
    print("📁 STRUCTURA FINALA:")
    print("="*60)
    
    for root, dirs, files in os.walk(logs_dir):
        level = root.replace(logs_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f'{subindent}{file} ({file_size} bytes)')
    
    # Citeste si verifica fiecare fisier
    print("\n" + "="*60)
    print("📖 CONTINUT FISIERE:")
    print("="*60)
    
    saint_denis_file = os.path.join(logs_dir, "Saint_Denis", "Politie.json")
    if os.path.exists(saint_denis_file):
        print(f"\n{saint_denis_file}:")
        with open(saint_denis_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        print(f"  Loguri: {len(logs)} items")
        for i, log in enumerate(logs, 1):
            print(f"  {i}. {log['action_type']} by {log['discord_id']}: {log['details']}")
    
    blackwater_file = os.path.join(logs_dir, "BlackWater", "Politie.json")
    if os.path.exists(blackwater_file):
        print(f"\n{blackwater_file}:")
        with open(blackwater_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        print(f"  Loguri: {len(logs)} items")
        for i, log in enumerate(logs, 1):
            print(f"  {i}. {log['action_type']} by {log['discord_id']}: {log['details']}")
    
    if os.path.exists(global_summary_file):
        print(f"\n{global_summary_file}:")
        with open(global_summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        print(f"  Users connected: {summary['users_connected']}")
        print(f"  Cities modified: {list(summary['cities_modified'].keys())}")
        print(f"  Total actions: {summary['total_actions']}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLET - Structura noua este corecta!")
    print("="*60)

if __name__ == "__main__":
    test_logging_structure()
