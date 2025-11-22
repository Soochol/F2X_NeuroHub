"""
Quick database connection test script.
"""
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def test_connection():
    print(f"Testing database connection...")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✓ Connection successful!")
            print(f"✓ Users table has {count} records")
            
            result = conn.execute(text("SELECT COUNT(*) FROM wip_items"))
            count = result.scalar()
            print(f"✓ WIP items table has {count} records")
            
            result = conn.execute(text("SELECT COUNT(*) FROM process_data"))
            count = result.scalar()
            print(f"✓ Process data table has {count} records")
            
            return True
    except Exception as e:
        print(f"✗ Connection failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
