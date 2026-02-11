#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add institution_permissions column to discord_users table"""

import sys
import json
import requests
from pathlib import Path
from configparser import ConfigParser

# Load Supabase config
config = ConfigParser()
config.read('supabase_config.ini')

url = config.get('supabase', 'url')
key = config.get('supabase', 'key')

# First, check what columns exist
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

print("🔍 Checking existing columns in discord_users...")
response = requests.get(
    f"{url}/rest/v1/discord_users?limit=1",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    if data:
        print("📋 Existing columns:", list(data[0].keys()))
    else:
        print("❌ No data returned")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
    sys.exit(1)

# Check if institution_permissions already exists
if 'institution_permissions' in data[0]:
    print("✅ institution_permissions column already exists!")
else:
    print("⚠️  institution_permissions column does NOT exist")
    print("\n📝 To add the column, you need to:")
    print("1. Go to Supabase dashboard")
    print("2. Open the discord_users table")
    print("3. Add new column: institution_permissions (jsonb, nullable)")
    print("\nOr run SQL in Supabase SQL Editor:")
    print("ALTER TABLE discord_users ADD COLUMN institution_permissions jsonb;")
