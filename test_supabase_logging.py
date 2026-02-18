# -*- coding: utf-8 -*-
"""
Test script to verify Supabase logging is working
"""

import requests
import json
from datetime import datetime
import configparser
import os

# Load config
config = configparser.ConfigParser()
config.read('supabase_config.ini')

url = config.get('supabase', 'url')
key = config.get('supabase', 'key')
table_logs = config.get('supabase', 'table_logs', fallback='audit_logs')

print(f"\n{'='*60}")
print(f"  SUPABASE LOGGING TEST")
print(f"{'='*60}\n")

print(f"📋 Configuration:")
print(f"   URL: {url[:50]}...")
print(f"   Key: {key[:20]}...")
print(f"   Table: {table_logs}")
print()

# Try different table names
tables_to_test = [
    config.get('supabase', 'table_logs', fallback='audit_logs'),
    'action_log',
    'audit_logs',
    'logs'
]

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

print(f"Testing tables: {tables_to_test}\n")

for table in tables_to_test:
    try:
        # Create test log entry
        log_entry = {
            "discord_id": "TEST_USER",
            "discord_username": "TEST_USER",
            "action_type": "test_connection",
            "city": "TEST",
            "institution": "TEST",
            "entity_name": "test_entity",
            "entity_id": "",
            "details": "Testing Supabase connection",
            "changes": "Connection test",
            "timestamp": datetime.now().isoformat()
        }
        
        test_url = f"{url}/rest/v1/{table}"
        print(f"🔍 Testing: {table}")
        print(f"   URL: {test_url}")
        
        response = requests.post(
            test_url,
            json=log_entry,
            headers=headers,
            timeout=5
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [201, 200]:
            print(f"   ✅ SUCCESS - Log inserted into {table}")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ FAILED")
            print(f"   Response: {response.text}")
        
        print()
    except Exception as e:
        print(f"   ❌ ERROR: {e}\n")

print(f"{'='*60}\n")
