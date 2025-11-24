"""
Check WIP completion status in database
"""
import sqlite3

db_path = r"c:\myCodeRepoWindows\F2X_NeuroHub\backend\neurohub.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("WIP COMPLETION DIAGNOSTIC")
print("=" * 80)

# 1. Check WIP item status
print("\n1. WIP Item Status:")
cursor.execute("""
    SELECT wip_id, status, created_at, updated_at
    FROM wip_items 
    WHERE wip_id = 'WIP-DT01A10251102-004'
""")
for row in cursor.fetchall():
    print(f"   WIP ID: {row[0]}")
    print(f"   Status: {row[1]}")
    print(f"   Created: {row[2]}")
    print(f"   Updated: {row[3]}")

# 2. Check WIPProcessHistory records
print("\n2. WIPProcessHistory Records:")
cursor.execute("""
    SELECT wph.id, p.process_number, p.process_name_ko, wph.result, wph.completed_at
    FROM wip_process_history wph
    JOIN wip_items w ON wph.wip_item_id = w.id
    JOIN processes p ON wph.process_id = p.id
    WHERE w.wip_id = 'WIP-DT01A10251102-004'
    ORDER BY wph.completed_at
""")
history = cursor.fetchall()
if history:
    for row in history:
        print(f"   Process {row[1]} ({row[2]}): {row[3]} at {row[4]}")
else:
    print("   ❌ NO RECORDS FOUND - This is the problem!")

# 3. Check ProcessData records (for comparison)
print("\n3. ProcessData Records (for comparison):")
cursor.execute("""
    SELECT pd.id, p.process_number, p.process_name_ko, pd.result, pd.completed_at
    FROM process_data pd
    JOIN wip_items w ON pd.wip_id = w.id
    JOIN processes p ON pd.process_id = p.id
    WHERE w.wip_id = 'WIP-DT01A10251102-004'
    ORDER BY pd.started_at
""")
for row in cursor.fetchall():
    print(f"   Process {row[1]} ({row[2]}): {row[3]} at {row[4]}")

# 4. Check active processes
print("\n4. Active Manufacturing Processes:")
cursor.execute("""
    SELECT process_number, process_code, process_name_ko, is_active
    FROM processes
    WHERE process_number IN (1, 2, 3, 4, 5, 6)
    ORDER BY process_number
""")
for row in cursor.fetchall():
    print(f"   P{row[0]}: {row[1]} ({row[2]}) - Active: {row[3]}")

conn.close()

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
if not history:
    print("❌ WIPProcessHistory table is EMPTY for this WIP item")
    print("   This means the WIP completion logic is NOT being executed")
    print("   Possible causes:")
    print("   1. wip_for_query is None (WIP item not found in smart lookup)")
    print("   2. Transaction is rolling back due to an error")
    print("   3. Code is not being executed (check backend logs)")
else:
    print(f"✅ WIPProcessHistory has {len(history)} records")
    print("   The logic IS working, checking status update...")
