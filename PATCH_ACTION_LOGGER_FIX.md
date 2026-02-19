
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
