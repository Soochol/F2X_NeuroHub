"""Check current database constraints on process_data table."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT conname, pg_get_constraintdef(oid) "
        "FROM pg_constraint "
        "WHERE conrelid = 'process_data'::regclass"
    ))
    
    print("Current constraints on process_data table:")
    print("=" * 80)
    for row in result:
        print(f"\n{row[0]}:")
        print(f"  {row[1]}")
