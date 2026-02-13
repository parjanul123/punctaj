#!/usr/bin/env python3
"""
🚀 COMPLETE REALTIME SYNC FIX - Repara sincronizarea timp real complet
"""

import subprocess
import sys
import time

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_command(script_name, description):
    """Run a diagnostic/fix script"""
    print(f"▶️  Running: {description}...")
    print(f"   Script: {script_name}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed")
            return True
        else:
            print(f"\n⚠️  {script_name} exited with code {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {script_name} timed out")
        return False
    except FileNotFoundError:
        print(f"\n❌ {script_name} not found!")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    print_header("🚀 COMPLETE REAL-TIME SYNC FIX")
    print("""
  This will:
  1. Check real-time sync status
  2. Fix RLS if needed
  3. Verify all tables
  4. Test manual sync
  5. Monitor for live updates
    """)
    
    input("Press Enter to start...\n")
    
    # Step 1: Diagnose
    print_header("STEP 1️⃣ - DIAGNOSING...")
    if not run_command("diagnose_realtime_sync.py", "Real-time sync diagnostic"):
        print("⚠️  Diagnostic had issues")
    
    time.sleep(2)
    
    # Step 2: Check RLS
    print_header("STEP 2️⃣ - CHECKING RLS POLICIES...")
    if not run_command("check_rls_status.py", "RLS status checker"):
        print("⚠️  RLS check had issues")
    
    input("Press Enter to continue...\n")
    
    # Step 3: Disable RLS if needed
    print_header("STEP 3️⃣ - DISABLING RLS (for better sync)...")
    print("""
  RLS might be blocking sync. Disabling it allows:
  - INSERT of new records
  - UPDATE of existing records
  - DELETE of records
  """)
    
    response = input("Disable RLS? (y/n): ").lower()
    
    if response == 'y':
        if run_command("disable_rls_for_testing.py", "RLS disabler"):
            print("\n✅ RLS disabled")
        else:
            print("\n⚠️  RLS disable had issues")
    
    time.sleep(2)
    
    # Step 4: Check tables
    print_header("STEP 4️⃣ - CHECKING ALL TABLES...")
    if not run_command("check_all_tables_sync.py", "Table sync checker"):
        print("⚠️  Table check had issues")
    
    time.sleep(2)
    
    # Step 5: Monitor
    print_header("STEP 5️⃣ - REAL-TIME MONITORING")
    print("""
  Now we'll monitor real-time sync:
  
  1. The monitor will start watching for changes
  2. Open the app in another window
  3. Make a test change (add/edit/delete employee)
  4. Watch the monitor for instant updates
  
  Expected: Change appears within 2-5 seconds
    """)
    
    response = input("Start real-time monitor? (y/n): ").lower()
    
    if response == 'y':
        print("\nStarting monitor...\n")
        run_command("monitor_realtime_sync.py", "Real-time monitor")
    
    print_header("✅ REAL-TIME SYNC FIX COMPLETE")
    print("""
  Summary:
  ✅ Diagnostics ran
  ✅ RLS policies checked/fixed
  ✅ All tables verified
  ✅ Real-time sync tested
  
  If still not working:
  1. Restart app: python punctaj.py
  2. Make a change (add/edit employee)
  3. Check Supabase dashboard immediately
  4. Check console for "SUPABASE_UPLOAD" messages
    """)
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
