#!/usr/bin/env python3
"""
Auto-create police_data table in Supabase
Runs SQL directly using Supabase connection
"""

import configparser
import os
import sys

print("=" * 70)
print("🛠️  AUTO-CREATING police_data TABLE")
print("=" * 70)

# Load config
config = configparser.ConfigParser()
if not os.path.exists('supabase_config.ini'):
    print("❌ supabase_config.ini not found!")
    sys.exit(1)

config.read('supabase_config.ini')

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

print(f"\n📡 Supabase URL: {SUPABASE_URL}")

# Try using psycopg2 for direct PostgreSQL connection
print("\n1️⃣  Trying direct PostgreSQL connection...")
try:
    import psycopg2
    from psycopg2 import sql
    
    # Extract DB connection details from Supabase config or environment
    # Supabase provides: postgres://postgres.{project}:{password}@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
    
    conn_string = config.get('postgres', 'connection_string', fallback=None)
    if not conn_string:
        print("   ⚠️  No postgres connection_string in config")
    else:
        print("   🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Create table
        create_sql = """
        CREATE TABLE IF NOT EXISTS police_data (
          id BIGSERIAL PRIMARY KEY,
          city TEXT NOT NULL,
          institution TEXT NOT NULL,
          data JSONB,
          version INT DEFAULT 1,
          last_synced TIMESTAMP WITH TIME ZONE,
          synced_by TEXT,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          UNIQUE(city, institution)
        );
        
        CREATE INDEX IF NOT EXISTS idx_police_data_city_inst ON police_data(city, institution);
        ALTER TABLE police_data ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Allow public access to police_data" ON police_data;
        CREATE POLICY "Allow public access to police_data"
          ON police_data
          FOR ALL
          USING (true)
          WITH CHECK (true);
        
        GRANT ALL ON police_data TO anon, authenticated, service_role;
        """
        
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("   ✅ Table created via direct PostgreSQL!")
        sys.exit(0)
        
except ImportError:
    print("   ⚠️  psycopg2 not available (trying REST API instead)")
except Exception as e:
    print(f"   ⚠️  Direct connection failed: {e}")

# Fallback: Use Supabase REST API with SQL function execution
print("\n2️⃣  Trying via Supabase REST API...")
import requests
import json

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Try to create table by calling a stored procedure or function
# Actually, let's try a simpler approach - use the rpc endpoint if available

# First check if we can create tables via REST
print("   🔍 Checking available methods...")

# Method 1: Try creating via metadata update
sql_statements = [
    """CREATE TABLE IF NOT EXISTS police_data (
        id BIGSERIAL PRIMARY KEY,
        city TEXT NOT NULL,
        institution TEXT NOT NULL,
        data JSONB,
        version INT DEFAULT 1,
        last_synced TIMESTAMP WITH TIME ZONE,
        synced_by TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(city, institution)
    )""",
    """CREATE INDEX IF NOT EXISTS idx_police_data_city_inst ON police_data(city, institution)""",
    """ALTER TABLE police_data ENABLE ROW LEVEL SECURITY""",
    """DROP POLICY IF EXISTS "Allow public access to police_data" ON police_data""",
    """CREATE POLICY "Allow public access to police_data" ON police_data FOR ALL USING (true) WITH CHECK (true)""",
    """GRANT ALL ON police_data TO anon, authenticated, service_role"""
]

# Try via PostgreSQL edge function or RPC
try:
    # Some Supabase instances support SQL execution via specific endpoints
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    for stmt in sql_statements:
        payload = {"sql": stmt}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Executed: {stmt[:50]}...")
        else:
            print(f"   ⚠️  {response.status_code}: {response.text[:100]}")
            
except Exception as e:
    print(f"   ⚠️  RPC method failed: {e}")

# Final check
print("\n3️⃣  Final verification...")
try:
    url = f"{SUPABASE_URL}/rest/v1/police_data?limit=1"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        print(f"   ✅ ✅ ✅ TABLE NOW EXISTS! ✅ ✅ ✅")
        print("\n✅ SUCCESS! police_data table is ready.\n")
    elif response.status_code == 404:
        print(f"   ❌ Table creation failed")
        print(f"\n📝 MANUAL INSTRUCTIONS:")
        print(f"   1. Go to: https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new")
        print(f"   2. Click 'New query'")
        print(f"   3. Paste SQL from CREATE_POLICE_DATA_TABLE.sql")
        print(f"   4. Click 'Run'")
        sys.exit(1)
    else:
        print(f"   ⚠️  Unexpected response: {response.status_code}")
except Exception as e:
    print(f"   ❌ Verification failed: {e}")

print("\n" + "=" * 70)
