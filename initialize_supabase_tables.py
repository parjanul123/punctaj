#!/usr/bin/env python3
"""
Initialize Supabase tables automatically
Run this ONCE to create all required tables
"""

import requests
import json
import configparser
import os
from pathlib import Path

# Load Supabase config
config = configparser.ConfigParser()
config_paths = [
    "supabase_config.ini",
    os.path.join(os.path.dirname(__file__), "supabase_config.ini")
]

config_file = None
for path in config_paths:
    if os.path.exists(path):
        config_file = path
        break

if not config_file:
    print("❌ supabase_config.ini not found!")
    exit(1)

config.read(config_file)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# SQL queries to create tables
CREATE_TABLES_SQL = """
-- ============================================================================
-- 1. CITIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS cities (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2. INSTITUTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS institutions (
  id BIGSERIAL PRIMARY KEY,
  city_id BIGINT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(city_id, name)
);

-- ============================================================================
-- 3. EMPLOYEES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS employees (
  id BIGSERIAL PRIMARY KEY,
  institution_id BIGINT NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
  discord_username TEXT,
  employee_name TEXT NOT NULL,
  rank TEXT,
  role TEXT,
  punctaj INT DEFAULT 0,
  id_card_series TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 4. DISCORD USERS TABLE 
-- ============================================================================
CREATE TABLE IF NOT EXISTS discord_users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  discord_id BIGINT UNIQUE,
  email TEXT,
  role TEXT DEFAULT 'viewer',
  is_superuser BOOLEAN DEFAULT FALSE,
  is_admin BOOLEAN DEFAULT FALSE,
  permissions JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 5. AUDIT_LOGS TABLE (for activity tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY,
  discord_id TEXT,
  discord_username TEXT,
  action_type TEXT NOT NULL,
  city TEXT,
  institution TEXT,
  entity_name TEXT,
  details TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 6. POLICE_DATA TABLE (main sync table for institution data)
-- ============================================================================
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

-- ============================================================================
-- 7. WEEKLY_REPORTS TABLE (for weekly summaries)
-- ============================================================================
CREATE TABLE IF NOT EXISTS weekly_reports (
  id BIGSERIAL PRIMARY KEY,
  week_start DATE NOT NULL,
  week_end DATE NOT NULL,
  city TEXT NOT NULL,
  institution TEXT NOT NULL,
  employee_count INT,
  reset_by TEXT,
  discord_id TEXT,
  report_data JSONB,
  archived_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 8. SYNC_METADATA TABLE (for tracking sync state)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_metadata (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT,
  version INT DEFAULT 1,
  last_synced TIMESTAMP WITH TIME ZONE,
  conflict_resolution TEXT DEFAULT 'latest_timestamp',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 9. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_institutions_city_id ON institutions(city_id);
CREATE INDEX IF NOT EXISTS idx_employees_institution_id ON employees(institution_id);
CREATE INDEX IF NOT EXISTS idx_employees_discord ON employees(discord_username);
CREATE INDEX IF NOT EXISTS idx_discord_users_discord_id ON discord_users(discord_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_discord ON audit_logs(discord_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_police_data_city_inst ON police_data(city, institution);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_city_inst ON weekly_reports(city, institution);
CREATE INDEX IF NOT EXISTS idx_weekly_reports_week ON weekly_reports(week_start, week_end);

-- ============================================================================
-- 10. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE cities ENABLE ROW LEVEL SECURITY;
ALTER TABLE institutions ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE discord_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE police_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_metadata ENABLE ROW LEVEL SECURITY;
"""

def execute_sql(sql_statement):
    """Execute a single SQL statement"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/rpc/sql"
        payload = {
            "query": sql_statement
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ Success")
            return True
        else:
            print(f"❌ Failed ({response.status_code})")
            if response.text:
                print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return False

def main():
    print("=" * 70)
    print("SUPABASE TABLE INITIALIZATION")
    print("=" * 70)
    print(f"\n🔗 Connecting to: {SUPABASE_URL}")
    
    # Split SQL into individual statements
    statements = [s.strip() for s in CREATE_TABLES_SQL.split(';') if s.strip()]
    
    print(f"\n📋 Found {len(statements)} SQL statements to execute")
    print("\n⏳ Creating tables... (this might take a moment)\n")
    
    success_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments and empty lines
        if statement.startswith('--') or not statement:
            continue
        
        # Extract table name if it's a CREATE TABLE statement
        table_name = "statement"
        if "CREATE TABLE IF NOT EXISTS" in statement:
            try:
                table_name = statement.split("CREATE TABLE IF NOT EXISTS")[1].split("(")[0].strip()
            except:
                pass
        elif "CREATE INDEX IF NOT EXISTS" in statement:
            try:
                table_name = statement.split("CREATE INDEX IF NOT EXISTS")[1].split("ON")[0].strip()
            except:
                pass
        elif "ALTER TABLE" in statement:
            try:
                table_name = statement.split("ALTER TABLE")[1].split()[0].strip()
            except:
                pass
        
        print(f"[{i}/{len(statements)}] {table_name:30s} ... ", end="", flush=True)
        
        if execute_sql(statement):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ INITIALIZATION COMPLETE: {success_count}/{len(statements)} statements executed")
    print("=" * 70)
    
    if success_count == len(statements):
        print("\n✅ All tables created successfully!")
        print("\n📊 Created tables:")
        print("   • cities")
        print("   • institutions")
        print("   • employees")
        print("   • discord_users")
        print("   • audit_logs")
        print("   • police_data (main sync table)")
        print("   • weekly_reports")
        print("   • sync_metadata")
        print("\n🎉 Your Supabase database is now ready!")
    else:
        print(f"\n⚠️  Some statements failed. Please check errors above.")
        print("\n📝 Manual setup:")
        print("1. Go to: https://supabase.com/dashboard/project/yzlkgifumrwqlfgimcai/sql/new")
        print("2. Click 'New Query'")
        print("3. Copy the SQL from create_tables_auto.py and paste it")
        print("4. Click 'Run'")

if __name__ == "__main__":
    main()
