#!/usr/bin/env python3
"""
Supabase RLS Disable Tool
Dezactiveaza RLS blocages care ar putea impiedica syncronizarea
"""

import requests
import configparser
import os
import sys

print("="*70)
print("SUPABASE RLS FIX TOOL")
print("="*70)

# Load config
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), "supabase_config.ini")

if not os.path.exists(config_file):
    print(f"❌ {config_file} not found!")
    sys.exit(1)

config.read(config_file)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"\n⚠️  This script will DISABLE RLS on tables to allow sync")
print(f"   This is for TESTING ONLY - RLS should be re-enabled in production")

confirm = input("\nContinue? (yes/no): ").lower().strip()
if confirm != "yes":
    print("Cancelled")
    sys.exit(0)

# SQL to disable RLS
SQL_DISABLE_RLS = """
-- ============================================================================
-- DISABLE RLS ON ALL TABLES
-- This allows INSERT/UPDATE/DELETE from API without policies
-- ============================================================================

ALTER TABLE IF EXISTS police_data DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS cities DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS institutions DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS audit_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS discord_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS weekly_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS sync_metadata DISABLE ROW LEVEL SECURITY;

-- Grant permissions to authenticated users
GRANT ALL ON public.police_data TO anon, authenticated;
GRANT ALL ON public.employees TO anon, authenticated;
GRANT ALL ON public.cities TO anon, authenticated;
GRANT ALL ON public.institutions TO anon, authenticated;
GRANT ALL ON public.audit_logs TO anon, authenticated;
GRANT ALL ON public.discord_users TO anon, authenticated;
GRANT ALL ON public.weekly_reports TO anon, authenticated;
GRANT ALL ON public.sync_metadata TO anon, authenticated;
"""

# Split into statement and try via RPC
statements = [s.strip() for s in SQL_DISABLE_RLS.split(';') if s.strip()]

print(f"\n🔄 Disabling RLS on {len(statements)} tables/views...\n")

success = 0
for i, statement in enumerate(statements, 1):
    try:
        print(f"[{i}/{len(statements)}] {statement[:60]}...", end=" ", flush=True)
        
        url = f"{SUPABASE_URL}/rest/v1/rpc/sql"
        payload = {"query": statement}
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅")
            success += 1
        else:
            print(f"⚠️  HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ {str(e)[:30]}")

print(f"\n" + "="*70)
print(f"✅ {success}/{len(statements)} commands executed")
print("="*70)

if success == len(statements):
    print("\n✅ RLS has been disabled successfully!")
    print("\n📝 TO RE-ENABLE RLS in Production:")
    print("   1. Go to Supabase Dashboard")
    print("   2. Select each table")
    print("   3. Click 'RLS' button to re-enable")
    print("   4. Add appropriate policies for your users")
else:
    print("\n⚠️  Some commands failed - check Supabase permissions")
    print("   You may need to manually disable RLS in the dashboard")

print("\n" + "="*70)
print("ℹ️  Next steps:")
print("   1. Restart the application")
print("   2. Make changes (add/edit/delete)")
print("   3. Check Supabase dashboard for updates")
print("   4. Run: python test_sync_flow.py")
print("="*70)
