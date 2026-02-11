#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test action logging with detailed institution info
"""
import sys
sys.path.insert(0, 'd:\\punctaj')

class MockSupabaseSync:
    def __init__(self):
        self.url = "https://yzlkgifumrwqlfgimcai.supabase.co"
        self.key = "test_key"

from action_logger import ActionLogger

# Test logging
sync = MockSupabaseSync()
logger = ActionLogger(sync)

print("=" * 70)
print("TEST 1: Log add_employee")
print("=" * 70)
result = logger.log_add_employee(
    discord_id="user123",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Ion Popescu",
    employee_data={"PUNCT": "0", "PREZENTA": "0"}
)
print(f"Result: {result}\n")

print("=" * 70)
print("TEST 2: Log delete_employee")
print("=" * 70)
result = logger.log_delete_employee(
    discord_id="user456",
    city="Saint_Denis",
    institution_name="Pompieri",
    employee_name="Gheorghe Marin",
    employee_data={"PUNCT": "15", "PREZENTA": "10"}
)
print(f"Result: {result}\n")

print("=" * 70)
print("TEST 3: Log edit_points (add)")
print("=" * 70)
result = logger.log_edit_points(
    discord_id="user789",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Ana Ionescu",
    old_points=10,
    new_points=15,
    action="add"
)
print(f"Result: {result}\n")

print("=" * 70)
print("TEST 4: Log edit_points (remove)")
print("=" * 70)
result = logger.log_edit_points(
    discord_id="user321",
    city="Saint_Denis",
    institution_name="Pompieri",
    employee_name="Vasile Stanescu",
    old_points=20,
    new_points=18,
    action="remove"
)
print(f"Result: {result}\n")

print("=" * 70)
print("TEST 5: Log edit_employee")
print("=" * 70)
changed = {
    "PREZENTA": (5, 8),
    "PUNCT": (10, 12)
}
result = logger.log_edit_employee(
    discord_id="user654",
    city="BlackWater",
    institution_name="Politie",
    employee_name="Maria Popescu",
    changed_fields=changed
)
print(f"Result: {result}\n")

print("=" * 70)
print("EXPECTED IN SUPABASE TABLE 19922 (action_log):")
print("=" * 70)
print("""
Row 1: user=User_...., action=add_employee, city=BlackWater, institution=Politie
Row 2: user=User_...., action=delete_employee, city=Saint_Denis, institution=Pompieri
Row 3: user=User_...., action=edit_points, city=BlackWater, institution=Politie, details=Changed points from 10 to 15 (add)
Row 4: user=User_...., action=edit_points, city=Saint_Denis, institution=Pompieri, details=Changed points from 20 to 18 (remove)
Row 5: user=User_...., action=edit_employee, city=BlackWater, institution=Politie
""")
