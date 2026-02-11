#!/usr/bin/env python3
"""
Sync local JSON changes to Supabase
"""

import json
from pathlib import Path
from supabase_employee_manager import SupabaseEmployeeManager

manager = SupabaseEmployeeManager()

print("=" * 70)
print("SYNC SAINT_DENIS CHANGES TO SUPABASE")
print("=" * 70)

# Read local JSON
json_path = Path(__file__).parent / "data" / "Saint_Denis" / "Politie.json"

print(f"\n[Read] Reading from {json_path}...")

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, dict) or 'rows' not in data:
        print("✗ Invalid JSON structure")
        exit(1)
    
    employees = data.get('rows', [])
    print(f"✓ Found {len(employees)} employees in JSON\n")
    
    # Get Supabase IDs
    print("[Supabase] Getting city and institution IDs...")
    city_obj = manager.get_city_by_name("Saint_Denis")
    if not city_obj:
        print("✗ City 'Saint_Denis' not found in Supabase")
        exit(1)
    
    city_id = city_obj['id']
    print(f"✓ City ID: {city_id}")
    
    inst_obj = manager.get_institution_by_name(city_id, "Politie")
    if not inst_obj:
        print("✗ Institution 'Politie' not found in Supabase")
        exit(1)
    
    inst_id = inst_obj['id']
    print(f"✓ Institution ID: {inst_id}\n")
    
    # Get existing employees in Supabase
    existing = manager.get_employees_by_institution(inst_id)
    existing_names = {emp['employee_name']: emp['id'] for emp in existing}
    
    print(f"[Existing] {len(existing)} employees in Supabase")
    for name in existing_names.keys():
        print(f"  • {name}")
    
    # Sync employees
    print(f"\n[Sync] Processing {len(employees)} employees from JSON...\n")
    
    added = 0
    updated = 0
    
    for emp in employees:
        emp_name = emp.get("NUME IC", "")
        
        if not emp_name:
            print("  ⚠️ Skipping employee with no name")
            continue
        
        emp_data = {
            "discord_username": emp.get("DISCORD", ""),
            "employee_name": emp_name,
            "rank": emp.get("RANK", ""),
            "role": emp.get("ROLE", ""),
            "points": int(emp.get("PUNCTAJ", 0)),
            "id_card_series": emp.get("SERIE DE BULETIN", "")
        }
        
        if emp_name in existing_names:
            # Update existing
            emp_id = existing_names[emp_name]
            result = manager.update_employee(emp_id, emp_data)
            print(f"  ✏️  Updated: {emp_name}")
            updated += 1
        else:
            # Add new
            result = manager.add_employee(inst_id, emp_data)
            if result:
                print(f"  ✅ Added: {emp_name}")
                added += 1
            else:
                print(f"  ✗ Failed to add: {emp_name}")
    
    print("\n" + "=" * 70)
    print(f"RESULT: +{added} added, +{updated} updated")
    print("=" * 70)
    
    # Verify
    print("\n[Verify] Current state in Supabase:\n")
    structure = manager.get_full_structure()
    
    if "Saint_Denis" in structure and "Politie" in structure["Saint_Denis"]:
        employees = structure["Saint_Denis"]["Politie"]
        print(f"Saint_Denis / Politie: {len(employees)} employees")
        for emp in employees:
            print(f"  • {emp['employee_name']} (Rank: {emp['rank']}, Points: {emp['points']})")
    
    print("\n✅ SYNC COMPLETE!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
