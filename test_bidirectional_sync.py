#!/usr/bin/env python3
"""
Test bidirectional sync between app and Supabase
"""

from supabase_employee_manager import SupabaseEmployeeManager

print("=" * 70)
print("TEST BIDIRECTIONAL SYNC")
print("=" * 70)

manager = SupabaseEmployeeManager()

# Test 1: Read from Supabase
print("\n[Test 1] Reading from Supabase...")
structure = manager.get_full_structure()

for city, institutions in structure.items():
    print(f"  📍 {city}")
    for institution, employees in institutions.items():
        print(f"    🏢 {institution}: {len(employees)} employees")
        for emp in employees:
            print(f"       • {emp['employee_name']} (ID: {emp['id']}, Rank: {emp['rank']}, Points: {emp['points']})")

# Test 2: Simulate adding employee
print("\n[Test 2] Simulating add_employee via app...")
emp_data = {
    "discord_username": "test_user",
    "employee_name": "Test Employee",
    "rank": "2",
    "role": "Caporal",
    "points": 5,
    "id_card_series": "TEST123"
}

try:
    # Get city_id for BlackWater
    city_obj = manager.get_city_by_name("BlackWater")
    if city_obj:
        # Get institution_id
        inst_obj = manager.get_institution_by_name(city_obj['id'], "Politie")
        if inst_obj:
            result = manager.add_employee(inst_obj['id'], emp_data)
            if result:
                print(f"✓ Employee added: {emp_data['employee_name']}")
                print(f"  ID: {result.get('id')}")
            else:
                print(f"✗ Failed to add employee")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Update points
print("\n[Test 3] Simulating update_points via app...")
try:
    city_obj = manager.get_city_by_name("BlackWater")
    if city_obj:
        inst_obj = manager.get_institution_by_name(city_obj['id'], "Politie")
        if inst_obj:
            emp = manager.get_employee_by_name(inst_obj['id'], "Dandeny Munoz")
            if emp:
                # Update points to 10
                result = manager.update_employee(emp['id'], {"points": 10})
                print(f"✓ Employee updated: {emp['employee_name']}")
                print(f"  New points: 10")
            else:
                print(f"✗ Employee not found")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Delete employee
print("\n[Test 4] Simulating delete_employee via app...")
try:
    city_obj = manager.get_city_by_name("BlackWater")
    if city_obj:
        inst_obj = manager.get_institution_by_name(city_obj['id'], "Politie")
        if inst_obj:
            employees = manager.get_employees_by_institution(inst_obj['id'])
            
            # Find and delete "Test Employee"
            for emp in employees:
                if emp['employee_name'] == "Test Employee":
                    if manager.delete_employee(emp['id']):
                        print(f"✓ Employee deleted: Test Employee (ID: {emp['id']})")
                    else:
                        print(f"✗ Failed to delete")
                    break
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Verify final state
print("\n[Test 5] Verifying final state...")
structure = manager.get_full_structure()

for city, institutions in structure.items():
    print(f"  📍 {city}")
    for institution, employees in institutions.items():
        print(f"    🏢 {institution}: {len(employees)} employees")
        for emp in employees:
            print(f"       • {emp['employee_name']} (Rank: {emp['rank']}, Points: {emp['points']})")

print("\n" + "=" * 70)
print("✅ BIDIRECTIONAL SYNC TEST COMPLETE")
print("=" * 70)
