#!/usr/bin/env python3
"""
Clean local JSON files from duplicate employees
Ensures consistency with Supabase cleanup
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def institution_path(city, institution):
    """Get path to institution JSON file"""
    return f"data/{city}/{institution}.json"

def clean_local_duplicates():
    """Remove duplicate employees from all local JSON files"""
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return
    
    total_cleaned = 0
    files_processed = 0
    
    for city_dir in data_dir.iterdir():
        if not city_dir.is_dir():
            continue
        
        city = city_dir.name
        
        for json_file in city_dir.glob("*.json"):
            institution = json_file.stem
            
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Handle old format (list) and new format (dict)
                rows = data if isinstance(data, list) else data.get("rows", [])
                
                if not rows:
                    continue
                
                # Find duplicates by DISCORD ID
                groups = defaultdict(list)
                for i, row in enumerate(rows):
                    discord_id = row.get("DISCORD", "")
                    if discord_id:
                        groups[discord_id].append(i)
                
                duplicates = {k: v for k, v in groups.items() if len(v) > 1}
                
                if duplicates:
                    print(f"\n📁 {city}/{institution}")
                    
                    # Remove duplicates (keep first, remove rest)
                    indices_to_remove = set()
                    for discord_id, indices in duplicates.items():
                        print(f"   Discord {discord_id}: {len(indices)} copies found")
                        # Keep first, mark rest for deletion
                        for idx in indices[1:]:
                            indices_to_remove.add(idx)
                            emp_name = rows[idx].get("NUME IC", "Unknown")
                            print(f"      ❌ Removing duplicate: {emp_name}")
                    
                    # Remove in reverse order to maintain indices
                    cleaned_rows = [r for i, r in enumerate(rows) if i not in indices_to_remove]
                    
                    # Update data
                    if isinstance(data, list):
                        data = cleaned_rows
                    else:
                        data["rows"] = cleaned_rows
                    
                    # Save cleaned data
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    removed = len(indices_to_remove)
                    total_cleaned += removed
                    print(f"   ✅ Removed {removed} duplicates")
                
                files_processed += 1
            
            except Exception as e:
                print(f"❌ Error processing {city}/{institution}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   Files processed: {files_processed}")
    print(f"   Total duplicates removed: {total_cleaned}")
    print("✅ Local cleanup complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 LOCAL JSON DUPLICATE CLEANUP")
    print("=" * 60)
    
    clean_local_duplicates()
