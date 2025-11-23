import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Get process_data table schema
cursor.execute("PRAGMA table_info(process_data);")
columns = cursor.fetchall()

print("Process_data table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
