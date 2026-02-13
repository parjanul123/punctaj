#!/usr/bin/env python3
"""
⚡ REAL-TIME SYNC MONITOR - Monitorizeaza sincronizarea in timp real
"""

import os
import json
import time
import requests
import configparser
from pathlib import Path
from datetime import datetime

config = configparser.ConfigParser()
config.read("supabase_config.ini")

SUPABASE_URL = config.get('supabase', 'url', fallback='')
SUPABASE_KEY = config.get('supabase', 'key', fallback='')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_police_data_count():
    """Get current count of records in police_data"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/police_data?select=count()"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            count = response.headers.get('content-range', '0/0').split('/')[1]
            return int(count) if count != '*' else 0
    except:
        pass
    return 0

def get_employees_count():
    """Get current count of employees"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees?select=count()"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            count = response.headers.get('content-range', '0/0').split('/')[1]
            return int(count) if count != '*' else 0
    except:
        pass
    return 0

def get_latest_police_data():
    """Get most recent police_data records"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/police_data?order=updated_at.desc&limit=3"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_latest_employees():
    """Get most recent employees"""
    try:
        url = f"{SUPABASE_URL}/rest/v1/employees?order=updated_at.desc&limit=5"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def monitor_realtime():
    """Monitor real-time sync"""
    print("\n" + "="*70)
    print("  ⚡ REAL-TIME SYNC MONITOR")
    print("="*70)
    
    print("""
  INSTRUCTIONS:
  1. Leave this script running
  2. Go to app (or keep another terminal open)
  3. Make a change: Add/Edit/Delete an employee
  4. Watch this monitor for updates
  
  You should see counts INCREASE within 2-5 seconds
  
  Press Ctrl+C to stop monitoring
    """)
    
    print("="*70 + "\n")
    
    # Get initial counts
    initial_police = get_police_data_count()
    initial_employees = get_employees_count()
    
    print(f"Initial state:")
    print(f"  📄 police_data records: {initial_police}")
    print(f"  👥 employees records: {initial_employees}")
    print(f"\nMonitoring (checking every 2 seconds)...")
    print(f"Press Ctrl+C to stop\n")
    
    check_number = 0
    last_police_data = get_latest_police_data()
    last_employees = get_latest_employees()
    
    try:
        while True:
            time.sleep(2)
            check_number += 1
            
            current_police = get_police_data_count()
            current_employees = get_employees_count()
            
            # Get latest records
            new_police_data = get_latest_police_data()
            new_employees = get_latest_employees()
            
            # Check if counts changed
            police_changed = current_police != initial_police
            employees_changed = current_employees != initial_employees
            
            # Check if records changed
            data_changed = new_police_data != last_police_data
            emp_changed = new_employees != last_employees
            
            if police_changed or employees_changed or data_changed or emp_changed:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ✅ CHANGE DETECTED!")
                
                if police_changed:
                    print(f"  📄 police_data: {initial_police} → {current_police}")
                    initial_police = current_police
                
                if employees_changed:
                    print(f"  👥 employees: {initial_employees} → {current_employees}")
                    initial_employees = current_employees
                
                if data_changed and new_police_data:
                    latest = new_police_data[0]
                    print(f"  Latest police_data: {latest.get('city')}/{latest.get('institution')}")
                    last_police_data = new_police_data
                
                if emp_changed and new_employees:
                    latest = new_employees[0]
                    print(f"  Latest employee: {latest.get('employee_name')} in {latest.get('rank')}")
                    last_employees = new_employees
                
                print()
            else:
                # Show heartbeat every 30 seconds
                if check_number % 15 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring... no changes yet")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("  ⏹️  Monitoring stopped")
        print("="*70)
        
        print(f"\nFinal state:")
        print(f"  📄 police_data records: {get_police_data_count()}")
        print(f"  👥 employees records: {get_employees_count()}")
        
        print(f"\n📊 ANALYSIS:")
        
        if get_police_data_count() == 0 and get_employees_count() == 0:
            print(f"  ❌ NO DATA SYNCED AT ALL!")
            print(f"\n  PROBLEMS:")
            print(f"     1. police_data table missing?")
            print(f"     2. RLS blocking INSERT?")
            print(f"     3. sync_data() function not called?")
            print(f"\n  FIXES:")
            print(f"     python initialize_supabase_tables.py")
            print(f"     python disable_rls_for_testing.py")
            print(f"     python diagnose_realtime_sync.py")
        else:
            print(f"  ✅ Data IS synced")
            print(f"     Police data records: {get_police_data_count()}")
            print(f"     Employees records: {get_employees_count()}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    monitor_realtime()
