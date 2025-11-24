"""
Script to apply both remaining changes
"""
import re

# 1. Update wip_service.py
file_path = r"c:\myCode\F2X_NeuroHub\backend\app\services\wip_service.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the early return for process 1
old_code = '''    # BR-003: First process can always start if WIP is CREATED or IN_PROGRESS
    if process_number == 1:
        if wip_item.status not in (WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value):
            raise WIPValidationError(
                f"WIP {wip_item.wip_id} must be in CREATED or IN_PROGRESS status. "
                f"Current status: {wip_item.status}"
            )
        return

    # BR-003: For subsequent processes, check if previous process is PASS'''

new_code = '''    # BR-003: First process can always start if WIP is CREATED or IN_PROGRESS
    if process_number == 1:
        if wip_item.status not in (WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value):
            raise WIPValidationError(
                f"WIP {wip_item.wip_id} must be in CREATED or IN_PROGRESS status. "
                f"Current status: {wip_item.status}"
            )
        # Don't return yet - check for PASS completion below

    # BR-NEW: Check if process already has PASS completion
    # Prevents re-starting processes that have already been successfully completed
    # FAIL completions are allowed to restart (rework scenario)
    existing_pass = db.query(WIPProcessHistory).filter(
        WIPProcessHistory.wip_item_id == wip_item.id,
        WIPProcessHistory.process_id == process_id,
        WIPProcessHistory.result == ProcessResult.PASS.value,
        WIPProcessHistory.completed_at.isnot(None)
    ).first()

    if existing_pass:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} already completed Process {process_number} with PASS. "
            f"Cannot restart a passed process."
        )

    # Early return for process 1 after PASS check
    if process_number == 1:
        return

    # BR-003: For subsequent processes, check if previous process is PASS'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Updated wip_service.py with PASS completion check")
else:
    print("⚠ wip_service.py pattern not found or already updated")

# 2. Update process_service.py start_process method
file_path2 = r"c:\myCode\F2X_NeuroHub\backend\app\services\process_service.py"
with open(file_path2, 'r', encoding='utf-8') as f:
    content2 = f.read()

old_validation = '''            # Validate process sequence
            self._validate_process_sequence(db, lot, process, serial_id, wip_item_id)

            # Check for concurrent work
            self._check_concurrent_work(db, lot, process, serial_id, wip_item_id)'''

new_validation = '''            # Validate process sequence
            self._validate_process_sequence(db, lot, process, serial_id, wip_item_id)

            # Check if process already has PASS completion (new validation)
            self._check_pass_completion(db, process, serial_id, wip_item_id)

            # Check for concurrent work
            self._check_concurrent_work(db, lot, process, serial_id, wip_item_id)'''

if old_validation in content2:
    content2 = content2.replace(old_validation, new_validation)
    with open(file_path2, 'w', encoding='utf-8') as f:
        f.write(content2)
    print("✓ Updated process_service.py start_process with _check_pass_completion call")
else:
    print("⚠ process_service.py pattern not found or already updated")

print("\n✅ All changes applied successfully!")
