#!/usr/bin/env python3
"""
🔍 RUN ALL DIAGNOSTICS - Rulează toate testele o dată pentru diagnosticare completă
"""

import subprocess
import sys
import time
import os

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  ✓ {title}")
    print("="*70 + "\n")

def run_diagnostic(script_name, description):
    """Run a diagnostic script and report results"""
    print(f"\n📋 Running: {description}...")
    print(f"   Script: {script_name}")
    print("-" * 70)
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully")
            return True
        else:
            print(f"\n⚠️  {script_name} exited with code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ {script_name} timed out (>30s)")
        return False
    except FileNotFoundError:
        print(f"\n❌ {script_name} not found!")
        return False
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False

def main():
    """Main diagnostic runner"""
    
    print_header("COMPLETE SYNC DIAGNOSTICS")
    print("This will run 4 comprehensive diagnostics to identify why sync is failing.")
    print("Please wait, this takes ~2-3 minutes...\n")
    
    # Map of diagnostics to run
    diagnostics = [
        ("debug_sync_connection.py", "1/4: Testing Supabase Connection"),
        ("check_all_tables_sync.py", "2/4: Verifying All 5 Tables"),
        ("test_sync_flow.py", "3/4: Checking Local vs Cloud Data"),
        ("disable_rls_for_testing.py", "4/4: Disabling RLS (if needed)"),
    ]
    
    results = {}
    start_time = time.time()
    
    # Run each diagnostic
    for script, description in diagnostics:
        print(f"\n⏱️  Step {list(diagnostics).index((script, description)) + 1}/{len(diagnostics)}")
        success = run_diagnostic(script, description)
        results[script] = success
        time.sleep(1)  # Small delay between diagnostics
    
    # Print summary
    print_header("DIAGNOSTIC SUMMARY")
    
    elapsed = time.time() - start_time
    print(f"⏱️  Total time: {elapsed:.1f} seconds\n")
    
    for script, (description) in [(s, d.split(": ")[1]) for s, d in diagnostics]:
        status = "✅ PASS" if results[script] else "❌ FAIL"
        print(f"  {status} - {description}")
    
    # Overall status
    all_passed = all(results.values())
    print("\n" + "="*70)
    
    if all_passed:
        print("\n✅ All diagnostics passed!")
        print("\nNext steps:")
        print("  1. Restart the application: py punctaj.py")
        print("  2. Make a test change (add new city/employee)")
        print("  3. Check Supabase dashboard after 5 seconds")
        print("  4. If still not syncing, check application console for errors")
    else:
        print("\n⚠️  Some diagnostics failed!")
        print("\nFailed tests:")
        for script, desc in diagnostics:
            if not results[script]:
                print(f"  - {script}")
        print("\nFix the failed diagnostics above, then:")
        print("  1. Check that RLS is disabled (disable_rls_for_testing.py)")
        print("  2. Verify connection works (debug_sync_connection.py)")
        print("  3. Restart app and test sync again")
    
    print("\n📝 For detailed debugging:")
    print("  - Check console output above for specific errors")
    print("  - Run individual diagnostics: python <script_name>.py")
    print("  - Read SYNC_DIAGNOSIS_COMPLETE.md for more info")
    print("\n" + "="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
