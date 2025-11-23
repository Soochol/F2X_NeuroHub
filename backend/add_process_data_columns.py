import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

try:
    # Add defects column (JSON type)
    cursor.execute("""
        ALTER TABLE process_data 
        ADD COLUMN defects JSON
    """)
    print("✓ Added defects column")
except sqlite3.OperationalError as e:
    print(f"defects: {e}")

try:
    # Add duration_seconds column
    cursor.execute("""
        ALTER TABLE process_data 
        ADD COLUMN duration_seconds INTEGER
    """)
    print("✓ Added duration_seconds column")
except sqlite3.OperationalError as e:
    print(f"duration_seconds: {e}")

conn.commit()

# Verify the changes
cursor.execute("PRAGMA table_info(process_data);")
columns = cursor.fetchall()

print("\nProcess_data table columns after update:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
