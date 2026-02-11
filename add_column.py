#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add institution_permissions column using Supabase Admin API"""

import sys
import requests
from configparser import ConfigParser

# Load config
config = ConfigParser()
config.read('supabase_config.ini')

url = config.get('supabase', 'url')
service_role_key = config.get('supabase', 'service_role_key')  # Need this for admin operations

if not service_role_key or service_role_key == 'YOUR_SERVICE_ROLE_KEY':
    print("❌ Service role key not configured!")
    print("📝 Add to supabase_config.ini:")
    print("service_role_key = YOUR_SERVICE_ROLE_KEY")
    print("\nTo get it:")
    print("1. Supabase dashboard → Project → Settings → API")
    print("2. Copy 'service_role' secret")
    sys.exit(1)

# Create headers with service role
headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

# Execute SQL to add column
sql_query = """
ALTER TABLE public.discord_users 
ADD COLUMN IF NOT EXISTS institution_permissions jsonb DEFAULT '{}'::jsonb;
"""

print("🔧 Attempting to add institution_permissions column...")
print(f"SQL: {sql_query}")

response = requests.post(
    f"{url}/rest/v1/rpc/exec",
    headers=headers,
    json={"sql": sql_query}
)

print(f"Response status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code in [200, 204]:
    print("✅ Column added successfully!")
else:
    print("⚠️  Alternative: Use Supabase Dashboard to add the column manually")
    print("SQL to run in Supabase SQL Editor:")
    print("ALTER TABLE discord_users ADD COLUMN institution_permissions jsonb DEFAULT '{}'::jsonb;")
