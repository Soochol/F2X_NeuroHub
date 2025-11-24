import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Get processes table schema
cursor.execute("PRAGMA table_info(processes);")
columns = cursor.fetchall()

print("Processes table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
