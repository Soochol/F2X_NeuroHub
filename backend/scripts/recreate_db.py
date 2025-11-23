
import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.database import engine, Base
from app.models import *  # Import all models to register them with Base
from scripts.seed_dashboard_data import main as seed_main

from app.config import settings

DB_FILE = backend_path / "dev.db"

def recreate_database():
    print(f"Current DATABASE_URL: {settings.DATABASE_URL}")
    print(f"Recreating database at {DB_FILE}...")
    
    # 1. Remove existing DB file
    if DB_FILE.exists():
        try:
            os.remove(DB_FILE)
            print("  - Removed existing dev.db")
        except Exception as e:
            print(f"  - Error removing dev.db: {e}")
            return

    # 2. Create tables
    print("  - Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("  - Tables created successfully")
    except Exception as e:
        print(f"  - Error creating tables: {e}")
        return

    # 3. Seed data
    print("  - Seeding data...")
    try:
        # Mock args for seed script
        class Args:
            reset = False
            scale = "medium"
        
        # We can't easily mock argparse, so let's just call the functions directly if possible
        # or just run the script via subprocess if importing is hard due to argparse
        # But seed_dashboard_data.py has a main() that parses args.
        # Let's try to run it via subprocess to be safe and clean
        import subprocess
        subprocess.run([sys.executable, "backend/scripts/seed_dashboard_data.py", "--scale", "medium"], check=True)
        print("  - Data seeded successfully")
        
    except Exception as e:
        print(f"  - Error seeding data: {e}")

if __name__ == "__main__":
    recreate_database()
