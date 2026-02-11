#!/usr/bin/env python3
"""
Test reset_punctaj logging
Verify that reset actions are properly logged
"""

import json
from pathlib import Path

def test_reset_logging():
    """Check if reset actions appear in logs"""
    
    print("\n" + "="*60)
    print("🧪 TEST: Reset Punctaj Logging")
    print("="*60)
    
    # Check institution logs
    logs_dir = Path("logs/Saint_Denis")
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return
    
    # Find log files
    log_files = list(logs_dir.glob("*.json"))
    
    if not log_files:
        print("⚠️ No log files found yet")
        return
    
    print(f"\n📁 Found {len(log_files)} log file(s):")
    
    for log_file in log_files:
        print(f"\n📄 {log_file.name}")
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            actions = data if isinstance(data, list) else data.get("actions", [])
            
            if not actions:
                print("   (empty)")
                continue
            
            # Look for reset_punctaj actions
            reset_actions = [a for a in actions if a.get("action_type") == "reset_punctaj_all"]
            
            if reset_actions:
                print(f"   ✅ Found {len(reset_actions)} reset action(s):")
                
                for action in reset_actions[-3:]:  # Show last 3
                    print(f"\n      ⏰ {action.get('timestamp', 'N/A')}")
                    print(f"      👤 {action.get('discord_username', 'Unknown')} (ID: {action.get('discord_id', 'N/A')})")
                    print(f"      📊 Affected: {action.get('changes', {}).get('affected_employees', '?')} employees")
                    print(f"      📝 {action.get('changes', {}).get('action', 'N/A')}")
            else:
                print("   (no reset actions logged yet)")
            
            # Show last 2 actions
            print(f"\n   Latest actions:")
            for action in actions[-2:]:
                action_type = action.get('action_type', 'unknown')
                print(f"      • {action_type}: {action.get('entity_name', 'N/A')} @ {action.get('timestamp', 'N/A')}")
        
        except Exception as e:
            print(f"   ❌ Error reading: {e}")
    
    # Check SUMMARY
    summary_file = Path("logs/SUMMARY_global.json")
    if summary_file.exists():
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                summary = json.load(f)
            
            reset_count = summary.get("action_counts", {}).get("reset_punctaj_all", 0)
            print(f"\n📊 Global Summary:")
            print(f"   Total reset actions: {reset_count}")
        
        except Exception as e:
            print(f"   ⚠️ Error reading summary: {e}")

if __name__ == "__main__":
    test_reset_logging()
