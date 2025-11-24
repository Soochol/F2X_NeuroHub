"""
Detailed analysis of ProcessData ID 53
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import ProcessData, WIPItem

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    pd = db.query(ProcessData).filter(ProcessData.id == 53).first()
    
    print("\n" + "="*80)
    print("PROCESS DATA ID 53 DETAILED ANALYSIS")
    print("="*80 + "\n")
    
    print(f"ProcessData ID: {pd.id}")
    print(f"LOT ID: {pd.lot_id}")
    print(f"WIP ID: {pd.wip_id}")
    print(f"Serial ID: {pd.serial_id}")
    print(f"Process ID: {pd.process_id}")
    print(f"Result: {pd.result}")
    print(f"Started At: {pd.started_at}")
    print(f"Completed At: {pd.completed_at}")
    print(f"Duration (seconds): {pd.duration_seconds}")
    print(f"Operator ID: {pd.operator_id}")
    print(f"Measurements: {pd.measurements}")
    print(f"Defects: {pd.defects}")
    print()
    
    print("🔍 KEY FINDINGS:")
    if pd.completed_at is None:
        print("   ❌ CRITICAL: completed_at is NULL!")
        print("      This means the ProcessData was NOT properly updated during completion")
    
    if pd.duration_seconds is None:
        print("   ❌ CRITICAL: duration_seconds is NULL!")
        print("      This confirms the complete_process logic did not update ProcessData")
    
    # Check WIP item
    if pd.wip_id:
        wip = db.query(WIPItem).filter(WIPItem.id == pd.wip_id).first()
        print(f"\n   WIP Item ID {pd.wip_id}: {wip.wip_id if wip else 'NOT FOUND'}")
        print(f"   WIP Status: {wip.status if wip else 'N/A'}")
        
        if wip and wip.status == "CREATED":
            print(f"   ⚠️  WIP status should be 'IN_PROGRESS' after first process completion")
    
finally:
    db.close()
