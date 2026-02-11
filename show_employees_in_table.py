#!/usr/bin/env python3
"""
Show all institutions and employees currently in discord_users table
"""

import requests
import json

SUPABASE_URL = "https://yzlkgifumrwqlfgimcai.supabase.co"
SUPABASE_KEY = "sb_publishable_O6UGBk4_thsIjkXyBH_3yw_Q6UDkdeM"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("INSTITUTIONS AND EMPLOYEES IN DISCORD_USERS TABLE")
print("=" * 70)

# Get all records
url = f"{SUPABASE_URL}/rest/v1/discord_users?select=*"

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        employees = response.json()
        
        if not employees:
            print("\n⚠️  Table is EMPTY - no employees loaded yet!")
        else:
            print(f"\n✓ Found {len(employees)} employees\n")
            
            # Group by city and institution
            by_city = {}
            
            for emp in employees:
                city = emp.get('city', 'Unknown')
                institution = emp.get('institution', 'Unknown')
                
                if city not in by_city:
                    by_city[city] = {}
                if institution not in by_city[city]:
                    by_city[city][institution] = []
                
                by_city[city][institution].append(emp)
            
            # Display grouped
            for city in sorted(by_city.keys()):
                print(f"\n📍 CITY: {city}")
                print("─" * 70)
                
                for institution in sorted(by_city[city].keys()):
                    emps = by_city[city][institution]
                    print(f"\n  🏢 {institution} ({len(emps)} employees)")
                    
                    for emp in emps:
                        name = emp.get('employee_name', 'Unknown')
                        discord = emp.get('discord_username', '?')
                        rank = emp.get('rank', '?')
                        points = emp.get('points', 0)
                        
                        print(f"     • {name} (Rank: {rank}, Points: {points}, Discord: {discord})")
        
        print("\n" + "=" * 70)
        print(f"TOTAL: {len(employees)} employees")
        print("=" * 70)
    
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
