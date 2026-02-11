#!/usr/bin/env python3
"""Check audit_logs content"""
import requests

headers = {
    'apikey': 'sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM',
    'Authorization': 'Bearer sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM'
}

url = 'https://yzlkgifumrwqlfgimcai.supabase.co/rest/v1/audit_logs?order=timestamp.desc&limit=10'
r = requests.get(url, headers=headers, timeout=5)

if r.status_code == 200:
    data = r.json()
    print(f'Total records: {len(data)}\n')
    if data:
        for i, log in enumerate(data, 1):
            print(f'{i}. [{log.get("timestamp", "N/A")[:19]}] {log.get("action_type", "N/A").upper()}')
            print(f'   User: {log.get("discord_id", "N/A")}')
            print(f'   Location: {log.get("city", "N/A")} / {log.get("institution", "N/A")}')
            print(f'   Details: {log.get("details", "N/A")}')
            print()
    else:
        print('⚠️ Table is empty')
else:
    print(f'Error: HTTP {r.status_code}')
