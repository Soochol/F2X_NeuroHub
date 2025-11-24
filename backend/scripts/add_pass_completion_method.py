"""
Script to add _check_pass_completion method to ProcessService
"""
import re

# Read the file
file_path = r"c:\myCode\F2X_NeuroHub\backend\app\services\process_service.py"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new method to add
new_method = '''
    def _check_pass_completion(self, db: Session, process: Process,
                                serial_id: Optional[int], wip_item_id: Optional[int]):
        """
        Check if current process already has PASS completion.
        
        Prevents re-starting processes that have already been successfully completed.
        FAIL completions are allowed to restart (rework scenario).
        """
        if wip_item_id:
            # Check WIP process history for PASS completion
            existing_pass = db.query(WIPProcessHistory).filter(
                WIPProcessHistory.wip_item_id == wip_item_id,
                WIPProcessHistory.process_id == process.id,
                WIPProcessHistory.result == ProcessResult.PASS.value,
                WIPProcessHistory.completed_at.isnot(None)
            ).first()
            
            if existing_pass:
                raise BusinessRuleException(
                    message=f"Process {process.process_number} already completed with PASS. Cannot restart a passed process."
                )
        elif serial_id:
            # Check serial process data for PASS completion
            existing_pass = db.query(ProcessData).filter(
                ProcessData.serial_id == serial_id,
                ProcessData.process_id == process.id,
                ProcessData.result == ProcessResult.PASS.value,
                ProcessData.completed_at.isnot(None)
            ).first()
            
            if existing_pass:
                raise BusinessRuleException(
                    message=f"Process {process.process_number} already completed with PASS for this serial. Cannot restart a passed process."
                )

'''

# Find the insertion point (before "process_service = ProcessService()")
pattern = r'\nprocess_service = ProcessService\(\)'
match = re.search(pattern, content)

if match:
    # Insert the new method before the instantiation
    insertion_point = match.start()
    new_content = content[:insertion_point] + new_method + content[insertion_point:]
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Added _check_pass_completion method to ProcessService")
else:
    print("✗ Could not find insertion point")
