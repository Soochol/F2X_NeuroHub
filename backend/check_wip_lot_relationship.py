import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Check WIP items with their LOT associations
cursor.execute("""
    SELECT w.wip_id, w.lot_id, w.status, w.current_process_id, l.lot_number
    FROM wip_items w
    LEFT JOIN lots l ON w.lot_id = l.id
    ORDER BY w.id;
""")
wips = cursor.fetchall()

print("WIP Items and their LOT associations:")
print(f"{'WIP ID':<25} {'LOT ID':<10} {'Status':<15} {'Process':<10} {'LOT Number':<20}")
print("-" * 90)
for wip in wips:
    print(f"{wip[0]:<25} {wip[1] or 'NULL':<10} {wip[2]:<15} {wip[3] or 'NULL':<10} {wip[4] or 'NULL':<20}")

# Check LOT summary with WIP counts
print("\n\nLOT Summary with WIP counts:")
cursor.execute("""
    SELECT 
        l.lot_number,
        l.status,
        l.target_quantity,
        COUNT(w.id) as wip_count
    FROM lots l
    LEFT JOIN wip_items w ON l.id = w.lot_id
    GROUP BY l.id
    ORDER BY l.created_at DESC;
""")
lots = cursor.fetchall()

print(f"{'LOT Number':<20} {'Status':<15} {'Target':<10} {'WIP Count':<10}")
print("-" * 60)
for lot in lots:
    print(f"{lot[0]:<20} {lot[1]:<15} {lot[2]:<10} {lot[3]:<10}")

conn.close()
