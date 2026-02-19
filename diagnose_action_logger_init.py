#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic: Check ACTION_LOGGER initialization at startup
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🔍 DIAGNOSING ACTION_LOGGER INITIALIZATION")
print("=" * 70)

# Test 1: Check if ActionLoggerNew class exists
print("\n1️⃣ Checking ActionLoggerNew class...")
try:
    from action_logger import ActionLogger as ActionLoggerNew
    print(f"   ✅ ActionLoggerNew class imported: {ActionLoggerNew}")
except ImportError as e:
    print(f"   ❌ Failed to import ActionLogger: {e}")
    sys.exit(1)

# Test 2: Check SupabaseSync
print("\n2️⃣ Checking SupabaseSync...")
try:
    from supabase_sync import SupabaseSync
    print(f"   ✅ SupabaseSync class imported")
except ImportError as e:
    print(f"   ❌ Failed to import SupabaseSync: {e}")
    sys.exit(1)

# Test 3: Initialize SupabaseSync like the app does
print("\n3️⃣ Initializing SupabaseSync (like the app)...")
try:
    SUPABASE_SYNC = SupabaseSync()
    print(f"   ✅ SUPABASE_SYNC created")
    print(f"   ✓ URL: {SUPABASE_SYNC.url[:50]}...")
    print(f"   ✓ enabled: {SUPABASE_SYNC.enabled}")
    print(f"   ✓ table_logs: {SUPABASE_SYNC.table_logs}")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    SUPABASE_SYNC = None

# Test 4: Check conditions for ACTION_LOGGER initialization
print("\n4️⃣ Checking ACTION_LOGGER initialization conditions...")
print(f"   ✓ ActionLoggerNew exists: {ActionLoggerNew is not None}")
print(f"   ✓ SUPABASE_SYNC exists: {SUPABASE_SYNC is not None}")
if SUPABASE_SYNC:
    print(f"   ✓ SUPABASE_SYNC.enabled: {SUPABASE_SYNC.enabled}")

# Test 5: Try to initialize ACTION_LOGGER
print("\n5️⃣ Attempting to initialize ACTION_LOGGER...")
ACTION_LOGGER = None
try:
    if ActionLoggerNew and SUPABASE_SYNC and SUPABASE_SYNC.enabled:
        print(f"   → All conditions met, creating ACTION_LOGGER...")
        ACTION_LOGGER = ActionLoggerNew(SUPABASE_SYNC)
        print(f"   ✅ ACTION_LOGGER created successfully!")
        print(f"   ✓ table_logs: {ACTION_LOGGER.table_logs}")
        print(f"   ✓ supabase_url: {ACTION_LOGGER.supabase_url[:50]}...")
    else:
        print(f"   ❌ Conditions NOT met:")
        if not ActionLoggerNew:
            print(f"      - ActionLoggerNew is None/missing")
        if not SUPABASE_SYNC:
            print(f"      - SUPABASE_SYNC is None")
        if SUPABASE_SYNC and not SUPABASE_SYNC.enabled:
            print(f"      - SUPABASE_SYNC.enabled is False")
except Exception as e:
    print(f"   ❌ Exception during initialization:")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Final status
print("\n6️⃣ FINAL STATUS:")
if ACTION_LOGGER:
    print(f"   ✅✅✅ ACTION_LOGGER IS AVAILABLE")
    print(f"   → Logs will be saved to Supabase: {ACTION_LOGGER.table_logs}")
    print(f"   → This should work in the app!")
else:
    print(f"   ❌❌❌ ACTION_LOGGER IS NONE")
    print(f"   → Logs will NOT be saved!")
    print(f"\n   💡 POSSIBLE FIXES:")
    if not ActionLoggerNew:
        print(f"      1. Check if action_logger.py exists and is importable")
    if not SUPABASE_SYNC:
        print(f"      2. Check supabase_config.ini file exists")
        print(f"      3. Check Supabase credentials in config")
    if SUPABASE_SYNC and not SUPABASE_SYNC.enabled:
        print(f"      3. Check 'enabled = true' in supabase_config.ini [sync] section")

print("\n" + "=" * 70)
print("END OF DIAGNOSTIC")
print("=" * 70)
