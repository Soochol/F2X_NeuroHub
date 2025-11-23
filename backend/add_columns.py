import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

try:
    # Add auto_print_label column
    cursor.execute("""
        ALTER TABLE processes 
        ADD COLUMN auto_print_label BOOLEAN NOT NULL DEFAULT 0
    """)
    print("✓ Added auto_print_label column")
except sqlite3.OperationalError as e:
    print(f"auto_print_label: {e}")

try:
    # Add label_template_type column
    cursor.execute("""
        ALTER TABLE processes 
        ADD COLUMN label_template_type VARCHAR(50)
    """)
    print("✓ Added label_template_type column")
except sqlite3.OperationalError as e:
    print(f"label_template_type: {e}")

conn.commit()

# Verify the changes
cursor.execute("PRAGMA table_info(processes);")
columns = cursor.fetchall()

print("\nProcesses table columns after update:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
