#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to update user role in Supabase
"""

import requests
import configparser
import os

# Load Supabase config
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "supabase_config.ini")
config.read(config_path)

if 'supabase' not in config:
    print("❌ supabase_config.ini not found!")
    exit(1)

SUPABASE_URL = config.get('supabase', 'url')
SUPABASE_KEY = config.get('supabase', 'key')

# Update parjanu to admin
discord_id = "703316952232872016"  # parjanu

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

url = f"{SUPABASE_URL}/rest/v1/discord_users?discord_id=eq.{discord_id}"
# Set is_admin to true (nu is_superuser pentru a-l face admin, nu superuser)
data = {'is_admin': True}

print(f"🔄 Updating {discord_id} to admin role")
print(f"URL: {url}")

response = requests.patch(url, json=data, headers=headers, timeout=10)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code in [200, 204]:
    print(f"✅ Role updated successfully to: ADMIN")
else:
    print(f"❌ Failed to update: {response.status_code}")
