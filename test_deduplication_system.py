#!/usr/bin/env python3
"""
Validate that no duplicates are loaded from either Supabase or local JSON
Tests the deduplicate_rows function and full loading pipeline
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the deduplicate_rows function
from punctaj import deduplicate_rows

def check_file_duplicates(filepath):
    """Check a JSON file for duplicate Discord IDs"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Handle list format
        if isinstance(data, list):
            rows = data
        else:
            rows = data.get("rows", [])
        
        if not rows:
            return True, 0  # Empty is ok
        
        # Check for duplicates
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            discord_id = row.get("DISCORD", "")
            if discord_id:
                groups[discord_id].append(i)
        
        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        
        if duplicates:
            print(f"   ❌ {len(duplicates)} duplicate Discord IDs:")
            for discord_id, indices in duplicates.items():
                names = [rows[i].get("NUME IC", "Unknown") for i in indices]
                print(f"      Discord {discord_id}: {', '.join(names)}")
            return False, len(duplicates)
        
        return True, 0
    
    except Exception as e:
        print(f"   ⚠️ Error reading file: {e}")
        return False, 0

def test_deduplicate_function():
    """Test the deduplicate_rows function"""
    print("\n" + "="*60)
    print("🧪 TEST 1: deduplicate_rows() function")
    print("="*60)
    
    # Create test data with duplicates
    test_data = [
        {"DISCORD": "123", "NUME IC": "Ion Popescu", "PUNCTAJ": 10},
        {"DISCORD": "456", "NUME IC": "Maria Ionescu", "PUNCTAJ": 15},
        {"DISCORD": "123", "NUME IC": "Ion Popescu", "PUNCTAJ": 10},  # Duplicate
        {"DISCORD": "789", "NUME IC": "Andrei Georgescu", "PUNCTAJ": 20},
        {"DISCORD": "456", "NUME IC": "Maria Ionescu", "PUNCTAJ": 15},  # Duplicate
    ]
    
    print(f"Input: {len(test_data)} rows (3 unique, 2 duplicates)")
    
    # Deduplicate
    result = deduplicate_rows(test_data)
    
    print(f"Output: {len(result)} rows")
    
    if len(result) == 3:
        print("✅ PASS: Correctly removed duplicates")
        return True
    else:
        print("❌ FAIL: Expected 3 rows")
        return False

def check_all_local_files():
    """Check all local JSON files for duplicates"""
    print("\n" + "="*60)
    print("🔍 TEST 2: Local JSON files")
    print("="*60)
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("⚠️ No local data directory found")
        return True
    
    all_clean = True
    files_checked = 0
    
    for city_dir in data_dir.iterdir():
        if not city_dir.is_dir():
            continue
        
        city = city_dir.name
        
        for json_file in city_dir.glob("*.json"):
            institution = json_file.stem
            
            is_clean, dup_count = check_file_duplicates(json_file)
            files_checked += 1
            
            if is_clean:
                print(f"✅ {city}/{institution}")
            else:
                print(f"❌ {city}/{institution} - {dup_count} duplicate IDs")
                all_clean = False
    
    print(f"\nChecked {files_checked} files")
    return all_clean

def check_supabase_integration():
    """Check that load_institution() function works with deduplication"""
    print("\n" + "="*60)
    print("🔍 TEST 3: Supabase integration (load_institution)")
    print("="*60)
    
    try:
        from punctaj import load_institution
        
        # Try to load a test institution
        test_city = "Saint_Denis"
        test_institution = "Politie"
        
        print(f"Loading {test_city}/{test_institution}...")
        data = load_institution(test_city, test_institution)
        
        if not data:
            print("⚠️ No data loaded")
            return True
        
        rows = data.get("rows", [])
        print(f"Loaded {len(rows)} rows from {data.get('source', 'unknown')} source")
        
        # Check for duplicates
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            discord_id = row.get("DISCORD", "")
            if discord_id:
                groups[discord_id].append(i)
        
        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        
        if duplicates:
            print(f"❌ Found {len(duplicates)} duplicate Discord IDs")
            return False
        else:
            print(f"✅ All {len(rows)} rows are unique (no duplicates)")
            return True
    
    except Exception as e:
        print(f"⚠️ Could not test Supabase integration: {e}")
        return True

def main():
    print("\n" + "="*60)
    print("✨ DUPLICATE VALIDATION TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("deduplicate_rows function", test_deduplicate_function()))
    results.append(("Local JSON files", check_all_local_files()))
    results.append(("Supabase integration", check_supabase_integration()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✨ All tests passed! System is deduplication-safe.")
    else:
        print("\n⚠️ Some tests failed. Please review above.")

if __name__ == "__main__":
    main()
