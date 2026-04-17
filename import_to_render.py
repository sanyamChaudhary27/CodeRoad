#!/usr/bin/env python3
"""
Import JSON export data to Render PostgreSQL
"""
import json
import requests

RENDER_URL = "https://coderoad-gmq6.onrender.com"

def import_to_render(json_file):
    """Import JSON data to Render via API"""
    
    print(f"Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} tables\n")
    
    total_migrated = 0
    
    for table, table_data in data.items():
        columns = table_data['columns']
        rows = table_data['rows']
        
        if not rows:
            print(f"Skipping {table} (no data)")
            continue
        
        print(f"Migrating {table}: {len(rows)} rows...")
        
        # Convert rows to list of dicts
        rows_as_dicts = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            rows_as_dicts.append(row_dict)
        
        # Send to Render migration endpoint
        try:
            response = requests.post(
                f"{RENDER_URL}/api/v1/migrate/table",
                params={"table_name": table},
                json=rows_as_dicts,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                migrated = result.get('migrated', 0)
                total_migrated += migrated
                print(f"  ✅ Migrated {migrated}/{len(rows)} rows")
                if result.get('errors', 0) > 0:
                    print(f"  ⚠️  {result['errors']} errors")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print(f"✅ Migration complete! Total rows migrated: {total_migrated}")

if __name__ == "__main__":
    import_to_render("coderoad_production_export.json")
