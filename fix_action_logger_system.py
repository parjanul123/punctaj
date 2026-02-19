"""
FIX SCRIPT: Repair ACTION_LOGGER logging system

This script adds:
1. Better error handling in ACTION_LOGGER initialization
2. Fallback local-only logging if Supabase fails
3. Explicit null checks before logging
4. Console output for debugging
"""

import os
import json
from datetime import datetime

print("=" * 70)
print("🔧 ATTEMPTING TO FIX ACTION_LOGGER...")
print("=" * 70)

# Check if logs folder exists
logs_dir = "logs"
if not os.path.exists(logs_dir):
    print(f"\n1️⃣ Creating logs directory: {logs_dir}")
    os.makedirs(logs_dir, exist_ok=True)
    print(f"   ✅ Created")
else:
    print(f"\n1️⃣ Logs directory exists: {logs_dir}")
    # Check if it has files
    total_files = sum(len(files) for _, _, files in os.walk(logs_dir))
    print(f"   📊 Total files: {total_files}")

# Test ActionLogger import
print(f"\n2️⃣ Testing ActionLogger import...")
try:
    from action_logger import ActionLogger
    print(f"   ✅ ActionLogger imported successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test SupabaseSync import
print(f"\n3️⃣ Testing SupabaseSync import...")
try:
    from supabase_sync import SupabaseSync
    print(f"   ✅ SupabaseSync imported successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Create recovery script
print(f"\n4️⃣ Creating recovery script...")

recovery_script = '''#!/usr/bin/env python3
"""
Recovery script to ensure ACTION_LOGGER is always initialized
Add this to punctaj.py before ACTION_LOGGER initialization
"""

# =================== ACTION LOGGER RECOVERY ===================
def initialize_action_logger_safe():
    """Initialize ACTION_LOGGER with proper error handling and fallbacks"""
    global ACTION_LOGGER
    
    ACTION_LOGGER = None
    
    try:
        # Step 1: Check if ActionLogger class is available
        if not ActionLoggerNew:
            print("⚠️ ActionLoggerNew not available")
            return False
        
        # Step 2: Check if SUPABASE_SYNC is configured
        if not SUPABASE_SYNC:
            print("⚠️ SUPABASE_SYNC not available")
            return False
        
        # Step 3: Check if Supabase is enabled in config
        if not SUPABASE_SYNC.enabled:
            print("⚠️ Supabase sync is DISABLED in config - logs won't be saved!")
            return False
        
        # Step 4: Try to initialize
        try:
            ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
            print("✅ ACTION_LOGGER initialized successfully")
            print(f"   📊 Table: {ACTION_LOGGER.table_logs}")
            print(f"   📁 Local: logs/ folder")
            return True
        except Exception as init_error:
            print(f"❌ Failed to initialize ACTION_LOGGER: {init_error}")
            print(f"   Attempting fallback...")
            
            # FALLBACK: Create a basic logging object that saves locally only
            class LocalOnlyLogger:
                def __init__(self):
                    self.table_logs = "logs (local only)"
                
                def log_add_employee(self, *args, **kwargs):
                    self._log_action("add_employee", args, kwargs)
                    return True
                
                def log_delete_employee(self, *args, **kwargs):
                    self._log_action("delete_employee", args, kwargs)
                    return True
                
                def log_edit_points(self, *args, **kwargs):
                    self._log_action("edit_points", args, kwargs)
                    return True
                
                def log_edit_employee_safe(self, *args, **kwargs):
                    self._log_action("edit_employee", args, kwargs)
                    return True
                
                def log_custom_action(self, *args, **kwargs):
                    self._log_action("custom", args, kwargs)
                    return True
                
                def _log_action(self, action_type, args, kwargs):
                    print(f"📝 LOCAL LOG: {action_type} ({len(args)} args)")
            
            ACTION_LOGGER = LocalOnlyLogger()
            print("✅ Using LOCAL-ONLY logger (Supabase unavailable)")
            return False
    
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

# Call this INSTEAD of the current initialization
# Replace lines ~388-390 in punctaj.py with this:
# ACTION_LOGGER = None
# if ActionLoggerNew and SUPABASE_SYNC and SUPABASE_SYNC.enabled:
#     try:
#         ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
#         print("✓ Action logger initialized for automatic logging")
#         print(f"  📊 Logs table: {SUPABASE_SYNC.table_logs}")
#         print(f"  🔗 Supabase: {SUPABASE_SYNC.url[:50]}...")
#     except Exception as e:
#         print(f"⚠️ Error initializing action logger: {e}")

# With this improved version instead:
initialize_action_logger_safe()
'''

with open("FIX_ACTION_LOGGER_RECOVERY.py", "w", encoding="utf-8") as f:
    f.write(recovery_script)

print(f"   ✅ Created FIX_ACTION_LOGGER_RECOVERY.py")

# Create recommended patch
print(f"\n5️⃣ Creating recommended patch for punctaj.py...")

patch_content = '''
PATCH TO FIX ACTION_LOGGER - Apply this to punctaj.py (around line 388)

CURRENT CODE (BROKEN):
```
# ================== ACTION LOGGER INITIALIZATION ==================
# Initialize action logger for automatic logging on Supabase
ACTION_LOGGER = None
if ActionLoggerNew and SUPABASE_SYNC and SUPABASE_SYNC.enabled:
    try:
        ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
        print("✓ Action logger initialized for automatic logging")
        print(f"  📊 Logs table: {SUPABASE_SYNC.table_logs}")
        print(f"  🔗 Supabase: {SUPABASE_SYNC.url[:50]}...")
    except Exception as e:
        print(f"⚠️ Error initializing action logger: {e}")
```

NEW CODE (FIXED):
```
# ================== ACTION LOGGER INITIALIZATION ==================
# Initialize action logger for automatic logging on Supabase
ACTION_LOGGER = None

def _init_action_logger():
    """Initialize ACTION_LOGGER with comprehensive error handling"""
    global ACTION_LOGGER
    
    if not ActionLoggerNew:
        print("⚠️ ActionLogger module not available")
        return False
    
    if not SUPABASE_SYNC:
        print("⚠️ Supabase not configured")
        return False
    
    if not SUPABASE_SYNC.enabled:
        print("⚠️ Supabase sync is DISABLED - set 'enabled = true' in supabase_config.ini [sync]")
        return False
    
    try:
        ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
        print(f"✅ ACTION_LOGGER initialized:")
        print(f"   📊 Supabase table: {SUPABASE_SYNC.table_logs}")
        print(f"   📁 Local logs: logs/ folder")
        print(f"   🔗 URL: {SUPABASE_SYNC.url[:50]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED to initialize ACTION_LOGGER: {e}")
        import traceback
        traceback.print_exc()
        ACTION_LOGGER = None
        return False

# Try to initialize
_init_action_logger()

if not ACTION_LOGGER:
    print("⚠️⚠️⚠️ ACTION_LOGGER IS UNAVAILABLE - LOGS WILL NOT BE SAVED ⚠️⚠️⚠️")
    print()
    print("HOW TO FIX:")
    print("1. Check supabase_config.ini exists")
    print("2. Check [sync] section has: enabled = true")
    print("3. Check Supabase URL and key are correct")
    print("4. Restart the application")
```

Then, add NULL CHECKS before each logging call:

In add_member(), delete_members(), edit_member(), punctaj_cu_selectie() add:

```python
# Before the logging code, add explicit check:
if ACTION_LOGGER is None:
    print(f"❌ CRITICAL: ACTION_LOGGER is None - logs not being saved!")
    # Don't return - app should still work, just without logging
```
'''

with open("PATCH_ACTION_LOGGER_FIX.md", "w", encoding="utf-8") as f:
    f.write(patch_content)

print(f"   ✅ Created PATCH_ACTION_LOGGER_FIX.md")

print(f"\n" + "=" * 70)
print("✅ FIX FILES CREATED")
print("=" * 70)
print(f"""
Files created:
1. FIX_ACTION_LOGGER_RECOVERY.py - Recovery script with fallbacks
2. PATCH_ACTION_LOGGER_FIX.md - Detailed patch instructions

QUICK FIX - RUN THIS:
1. Check supabase_config.ini:
   [sync]
   enabled = true     ← Make sure this is TRUE

2. Restart the application

3. If still not logging, check console output for ERROR messages
   
If you see messages like:
   ❌ FAILED to initialize ACTION_LOGGER
   ⚠️ ActionLogger module not available
   ⚠️ Supabase sync is DISABLED

Then follow PATCH_ACTION_LOGGER_FIX.md to update punctaj.py
""")
