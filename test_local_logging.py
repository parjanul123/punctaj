#!/usr/bin/env python3
"""Test local logging system"""

from action_logger import ActionLogger
from datetime import datetime

# Mock supabase_sync
class MockSupabaseSync:
    def __init__(self):
        self.url = "https://yzlkgifumrwqlfgimcai.supabase.co"
        self.key = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"
        self.table_logs = "audit_logs"
        self.enabled = False  # Disable cloud upload for this test

sync = MockSupabaseSync()
logger = ActionLogger(sync)

print("=" * 70)
print("Testing Local Logging System")
print("=" * 70)

# Simulate some actions
actions = [
    ("parjanu", "add_employee", "Saint_Denis", "Politie", "Added employee: Ion Popescu"),
    ("parjanu", "edit_points", "Saint_Denis", "Politie", "Ion Popescu: 10 → 15 (add)"),
    ("admin_user", "delete_employee", "BlackWater", "Politie", "Deleted employee: Ana Popescu"),
    ("parjanu", "edit_employee", "Saint_Denis", "Politie", "Mihai Dumitrescu: Updated multiple fields"),
]

for discord_id, action_type, city, institution, details in actions:
    print(f"\n📝 Logging: {action_type}")
    logger._log_action(discord_id, action_type, city, institution, details)

print("\n" + "=" * 70)
print("Check the logs/ folder for:")
print("  - Individual log files: log_*.json")
print("  - Global summary: SUMMARY_global.json")
print("=" * 70)
