#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix: Disable RLS on audit_logs table so all rows are visible
"""

import requests
import configparser

config = configparser.ConfigParser()
config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

print("=" * 70)
print("🔧 FIXING RLS POLICY ON audit_logs TABLE")
print("=" * 70)

print("""
The audit_logs table has RLS enabled which blocks viewing logs in the UI.

SOLUTION: Disable RLS for audit_logs (it's internal audit data)

You need to run this SQL in Supabase:
""")

sql_commands = """
-- Disable RLS on audit_logs (allows all views)
ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

-- If you want to re-enable it later with a permissive policy:
--ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
--CREATE POLICY "Allow all audit_logs" ON audit_logs
--FOR ALL USING (true);
"""

print(sql_commands)

print("\n" + "=" * 70)
print("📋 HOW TO APPLY THE FIX:")
print("=" * 70)
print("""
1. Go to: https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new

2. Click "New Query" or paste in SQL editor

3. Copy and paste EXACTLY this:

   ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

4. Click "Run" button (or press Ctrl+Enter)

5. Should see: "Query executed successfully"

6. Then go back to Table Editor and look at audit_logs table
   - Refresh the page (Ctrl+R)
   - You should now see ALL logs!

7. Verify by checking the table has data
""")

print("\n" + "=" * 70)
print("ALTERNATIVE: Check RLS status via API")
print("=" * 70)

# Try to query with explicit SELECT to see the error
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

url = f"{SUPABASE_URL}/rest/v1/audit_logs?limit=1"
response = requests.get(url, headers=headers)

print(f"\nSELECT test on audit_logs:")
print(f"  Status: {response.status_code}")
if response.status_code == 200:
    print(f"  ✅ SELECT works - RLS not blocking")
    data = response.json()
    print(f"  Found {len(data)} rows")
else:
    print(f"  ❌ SELECT blocked - likely RLS policy issue")
    print(f"  Response: {response.text}")

print("\n" + "=" * 70)
print("IF YOU DON'T HAVE DATABASE ACCESS:")
print("=" * 70)
print("""
Ask the Supabase project owner to run:

  ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;

Then you'll be able to see the logs in the Table Editor.
""")
