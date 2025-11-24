"""
Fixed script to add WIP completion logic to process_service.py
This version correctly handles the process variable reference.
"""
import re

# Read the file
file_path = r"c:\myCodeRepoWindows\F2X_NeuroHub\backend\app\services\process_service.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add imports
old_import = """from app.models import (
    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus
)"""

new_import = """from app.models import (
    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus, WIPStatus, WIPProcessHistory
)"""

content = content.replace(old_import, new_import)

# Fix 2: Add WIP completion logic with correct process variable
old_code = """                # Update serial status if FAIL
                if result == ProcessResult.FAIL and process_data.serial_id:
                    serial = db.query(Serial).filter(Serial.id == process_data.serial_id).first()
                    if serial:
                        serial.status = SerialStatus.FAILED

                # Auto-print label"""

new_code = """                # Update serial status if FAIL
                if result == ProcessResult.FAIL and process_data.serial_id:
                    serial = db.query(Serial).filter(Serial.id == process_data.serial_id).first()
                    if serial:
                        serial.status = SerialStatus.FAILED

                # --- WIP Logic: Create WIPProcessHistory and Update Status ---
                if wip_for_query:  # If processing a WIP item
                    # Get process object for logging
                    process = db.query(Process).filter(Process.id == process_data.process_id).first()
                    
                    # 1. Create WIPProcessHistory record
                    wip_history = WIPProcessHistory(
                        wip_item_id=wip_for_query.id,
                        process_id=process_data.process_id,  # Use process_data.process_id directly
                        result=result.value,
                        started_at=process_data.started_at,
                        completed_at=completed_at,
                        operator_id=process_data.operator_id
                    )
                    db.add(wip_history)
                    if process:
                        logger.info(f"Created WIPProcessHistory for WIP {wip_for_query.wip_id}, Process {process.process_number}, Result: {result.value}")

                    # 2. If PASS, check if all processes are complete
                    if result == ProcessResult.PASS:
                        # Get all active processes (processes 1-6 are manufacturing)
                        all_processes = db.query(Process).filter(
                            Process.process_number.in_([1, 2, 3, 4, 5, 6]),
                            Process.is_active == True
                        ).all()
                        
                        # Check if all have PASS results in WIPProcessHistory
                        passed_count = db.query(WIPProcessHistory).filter(
                            WIPProcessHistory.wip_item_id == wip_for_query.id,
                            WIPProcessHistory.result == ProcessResult.PASS.value
                        ).distinct(WIPProcessHistory.process_id).count()
                        
                        # If all processes passed, mark WIP as COMPLETED
                        if passed_count >= len(all_processes):
                            wip_for_query.status = WIPStatus.COMPLETED.value
                            logger.info(f"WIP {wip_for_query.wip_id} marked as COMPLETED - all processes passed ({passed_count}/{len(all_processes)})")

                # Auto-print label"""

content = content.replace(old_code, new_code)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully added WIP completion logic to process_service.py")
print("Changes made:")
print("1. Added WIPStatus and WIPProcessHistory to imports")
print("2. Added WIP history creation and status update logic in complete_process method")
print("3. Fixed process variable reference (using process_data.process_id)")
