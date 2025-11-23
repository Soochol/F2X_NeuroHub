
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add backend directory to path to import app modules if needed, 
# but for raw SQL we just need the connection string.
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# from app.core.config import settings

# Override DATABASE_URL if needed, but settings should pick it up from env or defaults
# Assuming the app is running with the default postgres url from docker-compose or similar
# The user's context says: postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes

DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_lot():
    db = SessionLocal()
    try:
        # Check for the exact LOT number the user mentioned
        lot_short = "KR01TES251101"
        lot_long = "KR01TES251101001"
        
        print(f"Checking for LOT: {lot_short}")
        result_short = db.execute(text("SELECT id, lot_number, status FROM lots WHERE lot_number = :lot_number"), {"lot_number": lot_short}).fetchone()
        
        if result_short:
            print(f"Found LOT {lot_short}: ID={result_short[0]}, Status={result_short[2]}")
        else:
            print(f"LOT {lot_short} NOT FOUND")
            
        print(f"Checking for LOT: {lot_long}")
        result_long = db.execute(text("SELECT id, lot_number, status FROM lots WHERE lot_number = :lot_number"), {"lot_number": lot_long}).fetchone()
        
        if result_long:
            print(f"Found LOT {lot_long}: ID={result_long[0]}, Status={result_long[2]}")
        else:
            print(f"LOT {lot_long} NOT FOUND")

        # List all lots to be sure
        print("\nAll Lots:")
        all_lots = db.execute(text("SELECT lot_number FROM lots")).fetchall()
        for row in all_lots:
            print(f" - {row[0]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_lot()
