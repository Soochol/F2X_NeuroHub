
import sqlite3
import os

DB_PATH = os.path.join("backend", "dev.db")

def check_users():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"Checking users in {DB_PATH}...")
        cursor.execute("SELECT id, username, role, is_active, password_hash FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database!")
        else:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}, Active: {user[3]}")
                print(f"Password Hash: {user[4][:20]}...")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
