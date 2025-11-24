import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Check LOTs
cursor.execute("SELECT COUNT(*) FROM lots;")
lot_count = cursor.fetchone()[0]
print(f"Total LOTs: {lot_count}")

# Check WIP items
cursor.execute("SELECT COUNT(*) FROM wip_items;")
wip_count = cursor.fetchone()[0]
print(f"Total WIP items: {wip_count}")

# Check Serials
cursor.execute("SELECT COUNT(*) FROM serials;")
serial_count = cursor.fetchone()[0]
print(f"Total Serials: {serial_count}")

# Check Process Data
cursor.execute("SELECT COUNT(*) FROM process_data;")
process_data_count = cursor.fetchone()[0]
print(f"Total Process Data: {process_data_count}")

# Check active LOTs
cursor.execute("SELECT COUNT(*) FROM lots WHERE status IN ('CREATED', 'IN_PROGRESS');")
active_lots = cursor.fetchone()[0]
print(f"Active LOTs: {active_lots}")

# Check LOT details
cursor.execute("""
    SELECT lot_number, status, target_quantity, actual_quantity, passed_quantity, failed_quantity 
    FROM lots 
    LIMIT 5;
""")
lots = cursor.fetchall()
print("\nLOT Details (first 5):")
for lot in lots:
    print(f"  {lot[0]}: status={lot[1]}, target={lot[2]}, actual={lot[3]}, passed={lot[4]}, failed={lot[5]}")

conn.close()
