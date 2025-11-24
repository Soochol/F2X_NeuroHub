"""
Script to fix process_service.py bugs:
1. Remove db.refresh(process_data) on line 463
2. Add WIP completion logic after line 469
"""
import re

# Read the file
with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Bug Fix #1: Comment out db.refresh(process_data)
content = content.replace(
    '                db.refresh(process_data)\r\n',
    '                # db.refresh(process_data)  # Bug: This discards all updates!\r\n'
)

# Bug Fix #2: Add WIP completion logic
# Find the location after "serial.status = SerialStatus.FAILED"
wip_logic = '''
                # --- WIP Logic: Create WIPProcessHistory and Update Status ---
                if wip_for_query:  # If processing a WIP item
                    # Get process object for logging
                    process = db.query(Process).filter(Process.id == process_data.process_id).first()
                    
                    # 1. Create WIPProcessHistory record
                    wip_history = WIPProcessHistory(
                        wip_item_id=wip_for_query.id,
                        process_id=process_data.process_id,
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
                        
                        # Check if all have PASS results in their LATEST WIPProcessHistory
                        passed_process_ids = []
                        for proc in all_processes:
                            # Get the latest completion record for this process
                            latest_history = db.query(WIPProcessHistory).filter(
                                WIPProcessHistory.wip_item_id == wip_for_query.id,
                                WIPProcessHistory.process_id == proc.id,
                                WIPProcessHistory.completed_at.isnot(None)
                            ).order_by(
                                WIPProcessHistory.completed_at.desc()
                            ).first()
                            
                            # If latest attempt is PASS, count it
                            if latest_history and latest_history.result == ProcessResult.PASS.value:
                                passed_process_ids.append(proc.id)
                        
                        # If all processes passed, mark WIP as COMPLETED
                        if len(passed_process_ids) >= len(all_processes):
                            wip_for_query.status = WIPStatus.COMPLETED.value
                            logger.info(f"WIP {wip_for_query.wip_id} marked as COMPLETED - all processes passed ({len(passed_process_ids)}/{len(all_processes)})")

'''

# Insert WIP logic before "# Auto-print label"
content = content.replace(
    '\r\n                # Auto-print label\r\n                self._check_and_print_label(',
    wip_logic + '\r\n                # Auto-print label\r\n                self._check_and_print_label('
)

# Write the fixed content
with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed 2 bugs in process_service.py:")
print("   1. Commented out db.refresh(process_data)")
print("   2. Added WIP completion logic")
