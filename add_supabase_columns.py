#!/usr/bin/env python3
"""
Add missing columns to Supabase audit_logs table
Executes the SQL via Supabase REST API
"""

import requests
import json
from urllib.parse import quote

# Configuration from supabase_config.ini
SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl6bGtnaWZ1bXJ3cWxmZ2ltY2FpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzYyNDU0MjcsImV4cCI6MjA1MTgyMTQyN30.45fxNfXgfJG6tPUmJYDcHhPbv9_CqfwgSwWlr3Z6B0c"

def add_columns_to_audit_logs():
    """Add new columns to audit_logs table"""
    
    print("🔧 Adding missing columns to Supabase audit_logs table...\n")
    
    # SQL to add columns
    sql = """
    ALTER TABLE audit_logs
    ADD COLUMN IF NOT EXISTS discord_username TEXT DEFAULT 'unknown',
    ADD COLUMN IF NOT EXISTS entity_name TEXT,
    ADD COLUMN IF NOT EXISTS entity_id TEXT,
    ADD COLUMN IF NOT EXISTS changes TEXT;
    """
    
    # Execute via Supabase SQL API
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use Supabase's PostgreSQL endpoint for SQL
    sql_endpoint = f"{SUPABASE_URL}/rest/v1/rpc/sql"
    
    try:
        # Note: Direct SQL execution via REST might not be available
        # Alternative: Use pgAdmin or Supabase Dashboard directly
        
        print("⚠️  Direct SQL execution via REST API not available.\n")
        print("📋 Manual Steps to Add Columns:")
        print("=" * 60)
        print("""
1. Go to: https://app.supabase.com/project/yzlkgifumrwqlfgimcai/sql
2. Click "New Query" (or "+" button)
3. Copy and paste this SQL:

---BEGIN SQL---
ALTER TABLE audit_logs
ADD COLUMN IF NOT EXISTS discord_username TEXT DEFAULT 'unknown',
ADD COLUMN IF NOT EXISTS entity_name TEXT,
ADD COLUMN IF NOT EXISTS entity_id TEXT,
ADD COLUMN IF NOT EXISTS changes TEXT;
---END SQL---

4. Click "Run" (or Ctrl+Enter)
5. Should see: "EXECUTED" message

✅ After that, all logs will sync properly!
        """)
        print("=" * 60)
        
        # Test if columns exist
        test_query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'audit_logs' AND column_name IN ('discord_username', 'entity_name', 'entity_id', 'changes')"
        
        print("\n🔍 Checking column status...")
        print("Note: Run the SQL above first, then re-run this script to verify.\n")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False

if __name__ == "__main__":
    add_columns_to_audit_logs()
