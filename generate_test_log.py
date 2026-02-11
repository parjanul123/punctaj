#!/usr/bin/env python3
"""
Quick test to generate a log with the new detailed logging
"""

import json
import os
from datetime import datetime

# Simulate what should be logged
test_log = {
    "timestamp": datetime.now().isoformat(),
    "discord_id": "703316932232872016",
    "discord_username": "parjanu",
    "action_type": "edit_punctaj",
    "city": "BlackWater",
    "institution": "Politie",
    "entity_name": "vLp",
    "entity_id": "12345678",
    "details": "vLp: PUNCTAJ: 50 → 75",
    "changes": "PUNCTAJ: 50 → 75"
}

# Create directory structure
os.makedirs("logs/BlackWater", exist_ok=True)

# Write log file
log_file = "logs/BlackWater/Politie.json"
with open(log_file, 'w', encoding='utf-8') as f:
    json.dump([test_log], f, indent=2, ensure_ascii=False)

print("✅ Test log created:")
print(json.dumps(test_log, indent=2))

# Create summary
summary = {
    "updated_at": datetime.now().isoformat(),
    "users_connected": ["parjanu"],
    "institutions_modified": {
        "BlackWater/Politie": {
            "city": "BlackWater",
            "institution": "Politie",
            "actions": [
                {
                    "timestamp": test_log["timestamp"],
                    "discord_id": test_log["discord_id"],
                    "discord_username": test_log["discord_username"],
                    "action": test_log["action_type"],
                    "details": test_log["details"],
                    "changes": test_log["changes"]
                }
            ]
        }
    }
}

with open("logs/SUMMARY_global.json", 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("\n✅ Summary updated!")
print("\nNow check logs/SUMMARY_global.json to see if it shows:")
print("✅ discord_id AND discord_username")
print("✅ action: edit_punctaj (specific, not generic)")
print("✅ details with employee name and old → new values")
