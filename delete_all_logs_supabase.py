# -*- coding: utf-8 -*-
"""
Sterge TOATE logurile din Supabase tabelul audit_logs
"""

import configparser
import requests
import json

# Load config
config = configparser.ConfigParser()
config.read('supabase_config.ini')

url = config.get('supabase', 'url')
key = config.get('supabase', 'key')
table = config.get('supabase', 'table_logs')

print(f"🗑️ Deleting all logs from: {table}")
print(f"Supabase: {url[:50]}...\n")

# Delete all records from audit_logs
delete_url = f"{url}/rest/v1/{table}"

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# DELETE all records using RLS bypass (match all with id>0)
response = requests.delete(
    f"{delete_url}?id=gte.0",
    headers=headers,
    timeout=10
)

print(f"Response Status: {response.status_code}")
print(f"Response: {response.text}\n")

if response.status_code in [200, 204]:
    print("✅ ALL LOGS DELETED FROM SUPABASE!")
    print(f"   Table: {table}")
    print(f"   All records removed")
else:
    print(f"❌ Failed to delete logs")
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.text}")
