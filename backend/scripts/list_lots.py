"""List all lots in the database."""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.models.lot import Lot

db = SessionLocal()

try:
    lots = db.query(Lot).order_by(Lot.created_at.desc()).limit(10).all()
    
    print(f"📦 Recent LOTs ({len(lots)} shown):")
    print("-" * 100)
    print(f"{'ID':<6} {'LOT Number':<25} {'Status':<12} {'Target Qty':<10} {'Created At':<20}")
    print("-" * 100)
    
    for lot in lots:
        print(f"{lot.id:<6} {lot.lot_number:<25} {lot.status:<12} {lot.target_quantity:<10} {str(lot.created_at)[:19]}")
    
    # Count WIP items per lot
    print()
    print("🔍 Checking for WIP items...")
    
    from app.models.wip_item import WIPItem
    
    for lot in lots[:3]:
        wip_count = db.query(WIPItem).filter(WIPItem.lot_id == lot.id).count()
        if wip_count > 0:
            print(f"  LOT {lot.lot_number}: {wip_count} WIP items")
            sample_wip = db.query(WIPItem).filter(WIPItem.lot_id == lot.id).first()
            if sample_wip:
                print(f"    Example WIP ID: {sample_wip.wip_id}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
