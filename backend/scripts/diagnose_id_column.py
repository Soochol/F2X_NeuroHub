"""
Fix process_data table id column - check backend/dev.db
"""
import sqlite3

conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

try:
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='process_data'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("❌ process_data table does not exist!")
        print("\n💡 Run: uv run alembic upgrade head")
        exit(1)
    
    # Check table structure
    cursor.execute("PRAGMA table_info(process_data)")
    columns = cursor.fetchall()
    
    print("✅ process_data table exists")
    print("\nColumn structure:")
    for col in columns:
        col_id, name, col_type, notnull, default, pk = col
        marker = "🔑" if pk else "  "
        print(f"{marker} {name:20s} {col_type:15s} {'NOT NULL' if notnull else 'NULL':10s} PK={pk}")
    
    # Check the id column specifically
    id_col = [col for col in columns if col[1] == 'id'][0]
    _, name, col_type, notnull, default, pk = id_col
    
    print(f"\n📊 ID Column Analysis:")
    print(f"   Type: {col_type}")
    print(f"   Primary Key: {pk}")
    print(f"   NOT NULL: {notnull}")
    
    # Get CREATE TABLE statement
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='process_data'")
    create_sql = cursor.fetchone()[0]
    
    has_autoincrement = 'AUTOINCREMENT' in create_sql.upper()
    is_integer = col_type.upper() == 'INTEGER'
    
    print(f"   AUTOINCREMENT keyword: {'✅' if has_autoincrement else '❌'}")
    print(f"   Uses INTEGER type: {'✅' if is_integer else '❌ (uses ' + col_type + ')'}")
    
    if not is_integer and not has_autoincrement:
        print("\n🔴 PROBLEM FOUND:")
        print(f"   ID column is {col_type}, not INTEGER")
        print("   SQLite requires INTEGER PRIMARY KEY for auto-increment")
        print("\n💊 SOLUTION:")
        print("   Need to recreate table with INTEGER PRIMARY KEY")
        print("   Or explicitly add AUTOINCREMENT")
    elif is_integer and pk:
        print("\n✅ ID column should auto-increment (INTEGER PRIMARY KEY)")
    else:
        print("\n⚠️  Configuration might cause issues")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
