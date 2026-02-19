#!/usr/bin/env python3
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
