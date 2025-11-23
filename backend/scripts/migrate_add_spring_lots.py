import sqlite3
import os

# Path to database file
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dev.db')

def migrate():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Error: Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Adding parent_spring_lot column...")
    try:
        cursor.execute("ALTER TABLE lots ADD COLUMN parent_spring_lot VARCHAR(50)")
        print("Successfully added parent_spring_lot")
    except sqlite3.OperationalError as e:
        print(f"Error adding parent_spring_lot (might already exist): {e}")

    print("Adding sma_spring_lot column...")
    try:
        cursor.execute("ALTER TABLE lots ADD COLUMN sma_spring_lot VARCHAR(50)")
        print("Successfully added sma_spring_lot")
    except sqlite3.OperationalError as e:
        print(f"Error adding sma_spring_lot (might already exist): {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
