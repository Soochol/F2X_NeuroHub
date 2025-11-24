"""
Check WIP completion status and process history.

This script investigates why WIP-DT01A10251104-001 doesn't show as completed
in the web dashboard after completing Process 1.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import WIPItem, WIPProcessHistory, Process, ProcessData

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    wip_id_str = "WIP-DT01A10251104-001"
    
    print(f"\n{'='*80}")
    print(f"WIP COMPLETION STATUS INVESTIGATION: {wip_id_str}")
    print(f"{'='*80}\n")
    
    # 1. Check WIP Item status
    wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
    if not wip:
        print(f"❌ WIP item not found: {wip_id_str}")
        sys.exit(1)
    
    print(f"📦 WIP ITEM STATUS")
    print(f"   ID: {wip.id}")
    print(f"   WIP ID: {wip.wip_id}")
    print(f"   Status: {wip.status}")
    print(f"   LOT ID: {wip.lot_id}")
    print()
    
    # 2. Check WIPProcessHistory records
    histories = db.query(WIPProcessHistory).filter(
        WIPProcessHistory.wip_item_id == wip.id
    ).order_by(WIPProcessHistory.completed_at.desc()).all()
    
    print(f"📝 WIP PROCESS HISTORY RECORDS: {len(histories)} total")
    if histories:
        for i, h in enumerate(histories, 1):
            process = db.query(Process).filter(Process.id == h.process_id).first()
            print(f"   {i}. Process {process.process_number if process else '?'}: {h.result}")
            print(f"      Started: {h.started_at}")
            print(f"      Completed: {h.completed_at}")
            print(f"      Operator ID: {h.operator_id}")
    else:
        print(f"   ⚠️  NO HISTORY RECORDS FOUND!")
    print()
    
    # 3. Check ProcessData records
    process_data_records = db.query(ProcessData).filter(
        ProcessData.wip_id == wip.id
    ).order_by(ProcessData.started_at.desc()).all()
    
    print(f"🔧 PROCESS DATA RECORDS: {len(process_data_records)} total")
    for i, pd in enumerate(process_data_records, 1):
        process = db.query(Process).filter(Process.id == pd.process_id).first()
        print(f"   {i}. Process {process.process_number if process else '?'}: {pd.result}")
        print(f"      ProcessData ID: {pd.id}")
        print(f"      Started: {pd.started_at}")
        print(f"      Completed: {pd.completed_at}")
        print(f"      Duration: {pd.duration_seconds}s")
    print()
    
    # 4. Check all active processes
    all_processes = db.query(Process).filter(
        Process.process_number.in_([1, 2, 3, 4, 5, 6]),
        Process.is_active == True
    ).order_by(Process.process_number).all()
    
    print(f"🎯 ACTIVE MANUFACTURING PROCESSES: {len(all_processes)} total")
    for proc in all_processes:
        # Get latest history for this process
        latest = db.query(WIPProcessHistory).filter(
            WIPProcessHistory.wip_item_id == wip.id,
            WIPProcessHistory.process_id == proc.id,
            WIPProcessHistory.completed_at.isnot(None)
        ).order_by(WIPProcessHistory.completed_at.desc()).first()
        
        if latest:
            status = "✅ PASS" if latest.result == "PASS" else "❌ FAIL/REWORK"
        else:
            status = "⏸️  NOT COMPLETED"
        
        print(f"   Process {proc.process_number}: {status}")
    print()
    
    # 5. Determine expected status
    passed_count = 0
    for proc in all_processes:
        latest = db.query(WIPProcessHistory).filter(
            WIPProcessHistory.wip_item_id == wip.id,
            WIPProcessHistory.process_id == proc.id,
            WIPProcessHistory.completed_at.isnot(None)
        ).order_by(WIPProcessHistory.completed_at.desc()).first()
        
        if latest and latest.result == "PASS":
            passed_count += 1
    
    print(f"📊 COMPLETION ANALYSIS")
    print(f"   Passed Processes: {passed_count}/{len(all_processes)}")
    print(f"   Expected Status: {'COMPLETED' if passed_count >= len(all_processes) else 'IN_PROGRESS'}")
    print(f"   Actual Status: {wip.status}")
    print()
    
    if passed_count >= len(all_processes) and wip.status != "COMPLETED":
        print(f"❌ STATUS MISMATCH DETECTED!")
        print(f"   All processes passed but WIP status is '{wip.status}' instead of 'COMPLETED'")
    elif passed_count < len(all_processes) and wip.status == "COMPLETED":
        print(f"⚠️  PREMATURE COMPLETION!")
        print(f"   Only {passed_count} processes passed but WIP is marked as 'COMPLETED'")
    elif len(histories) == 0:
        print(f"🔴 CRITICAL ISSUE: No WIPProcessHistory records found!")
        print(f"   This means the WIP completion logic is not creating history records.")
    else:
        print(f"✅ Status is consistent with completion rules")
    
finally:
    db.close()
