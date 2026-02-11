#!/usr/bin/env python3
"""List and delete test logs"""

import requests

headers = {
    'apikey': 'sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM',
    'Authorization': 'Bearer sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM'
}

print("=" * 90)
print("LISTING ALL LOGS")
print("=" * 90)

# Get all logs
url = 'https://yzlkgifumrwqlfgimcai.supabase.co/rest/v1/audit_logs?order=id'
r = requests.get(url, headers=headers, timeout=5)

if r.status_code == 200:
    logs = r.json()
    print(f'\nTotal logs: {len(logs)}\n')
    
    test_ids = []
    for log in logs:
        log_id = log.get('id')
        user = log.get('discord_id', 'N/A')
        action = log.get('action_type', 'N/A')
        details = log.get('details', '')[:40]
        
        # Mark test logs
        is_test = user == 'test_user' or action == 'TEST_ACTION'
        marker = '🗑️ TEST' if is_test else '✅'
        
        print(f'{marker} ID: {log_id:3} | User: {user:15} | Action: {action:20} | Details: {details}')
        
        if is_test:
            test_ids.append(log_id)
    
    if test_ids:
        print(f'\n{"=" * 90}')
        print(f'Found {len(test_ids)} test logs to delete: IDs {test_ids}')
        print(f'{"=" * 90}')
        
        # Delete test logs
        for log_id in test_ids:
            delete_url = f'https://yzlkgifumrwqlfgimcai.supabase.co/rest/v1/audit_logs?id=eq.{log_id}'
            r = requests.delete(delete_url, headers=headers, timeout=5)
            
            if r.status_code in [200, 204]:
                print(f'✅ Deleted log ID {log_id}')
            else:
                print(f'❌ Failed to delete log ID {log_id}: HTTP {r.status_code}')
        
        print(f'\n✅ Deleted {len(test_ids)} test logs!')
    else:
        print('\nℹ️ No test logs found')
