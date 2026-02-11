#!/usr/bin/env python3
"""Delete all current logs to start fresh"""

import requests

headers = {
    'apikey': 'sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM',
    'Authorization': 'Bearer sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM'
}

print("Deleting all audit logs to start fresh...")

# Get all logs
url = 'https://yzlkgifumrwqlfgimcai.supabase.co/rest/v1/audit_logs'
r = requests.get(url, headers=headers, timeout=5)

if r.status_code == 200:
    logs = r.json()
    
    # Delete all
    for log in logs:
        log_id = log.get('id')
        delete_url = f'https://yzlkgifumrwqlfgimcai.supabase.co/rest/v1/audit_logs?id=eq.{log_id}'
        r = requests.delete(delete_url, headers=headers, timeout=5)
        
        if r.status_code in [200, 204]:
            print(f'✅ Deleted ID {log_id}')
        else:
            print(f'❌ Failed ID {log_id}')
    
    print(f'\n✅ All {len(logs)} logs deleted! Table is now clean.')
