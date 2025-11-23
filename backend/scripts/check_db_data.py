"""Check if database has data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

print("Checking database tables...")
print("=" * 60)

with engine.connect() as conn:
    # Check users
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    user_count = result.scalar()
    print(f"Users: {user_count}")
    
    # Check lots
    result = conn.execute(text("SELECT COUNT(*) FROM lots"))
    lot_count = result.scalar()
    print(f"Lots: {lot_count}")
    
    # Check processes
    result = conn.execute(text("SELECT COUNT(*) FROM processes"))
    process_count = result.scalar()
    print(f"Processes: {process_count}")
    
    # Check wip_items
    result = conn.execute(text("SELECT COUNT(*) FROM wip_items"))
    wip_count = result.scalar()
    print(f"WIP Items: {wip_count}")
    
    # Check process_data
    result = conn.execute(text("SELECT COUNT(*) FROM process_data"))
    pd_count = result.scalar()
    print(f"Process Data: {pd_count}")
    
    print("\n" + "=" * 60)
    if user_count == 0:
        print("⚠️  Database is empty! You need to seed the database.")
        print("\nRun: uv run python scripts/seed_dashboard_data.py")
    else:
        print("✅ Database has data")
