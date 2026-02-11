#!/usr/bin/env python3
"""
Test the detailed logging system
"""

print("""
🧪 TESTING DETAILED LOGGING

Steps:
1. App will start
2. Go to: File → BlackWater → Politie
3. Double-click PUNCTAJ column for "vLp" (first employee)
4. Change it from 0 to 50
5. Save with Ctrl+S (or File → Save Employees)
6. Close app
7. Check logs/SUMMARY_global.json
8. You should see:
   ✅ discord_username: parjanu
   ✅ action: edit_punctaj (specific!)
   ✅ details: vLp: PUNCTAJ: 0 → 50
   ✅ changes: PUNCTAJ: 0 → 50

Ready? Starting app in 3 seconds...
""")

import time
time.sleep(3)

import subprocess
subprocess.run(["py", "punctaj.py"])
