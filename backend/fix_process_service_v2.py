"""
더 간단하고 확실한 수정 스크립트
"""

# Read all lines
with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix line 463: comment out db.refresh
for i, line in enumerate(lines):
    if i == 462 and 'db.refresh(process_data)' in line:  # Line 463 (0-indexed = 462)
        lines[i] = '                # db.refresh(process_data)  # Bug: Discards all updates!\r\n'
        print(f"✅ Fixed line {i+1}: Commented out db.refresh()")
        break

# Find and insert WIP logic
# Look for the line with "# Auto-print label" in complete_process method
for i, line in enumerate(lines):
    if '# Auto-print label' in line and i > 400:  # Make sure we're in complete_process
        # Check if WIP logic already exists
        if i > 10 and 'WIP Logic' in lines[i-5]:
            print("⚠️  WIP logic already exists, skipping")
            break
            
        # Insert WIP logic before this line
        wip_lines = [
            '\r\n',
            '                # --- WIP Logic: Create WIPProcessHistory and Update Status ---\r\n',
            '                if wip_for_query:  # If processing a WIP item\r\n',
            '                    # Get process object for logging\r\n',
            '                    process = db.query(Process).filter(Process.id == process_data.process_id).first()\r\n',
            '                    \r\n',
            '                    # 1. Create WIPProcessHistory record\r\n',
            '                    wip_history = WIPProcessHistory(\r\n',
            '                        wip_item_id=wip_for_query.id,\r\n',
            '                        process_id=process_data.process_id,\r\n',
            '                        result=result.value,\r\n',
            '                        started_at=process_data.started_at,\r\n',
            '                        completed_at=completed_at,\r\n',
            '                        operator_id=process_data.operator_id\r\n',
            '                    )\r\n',
            '                    db.add(wip_history)\r\n',
            '                    if process:\r\n',
            '                        logger.info(f"Created WIPProcessHistory for WIP {wip_for_query.wip_id}, Process {process.process_number}, Result: {result.value}")\r\n',
            '\r\n',
            '                    # 2. If PASS, check if all processes are complete\r\n',
            '                    if result == ProcessResult.PASS:\r\n',
            '                        # Get all active processes (processes 1-6 are manufacturing)\r\n',
            '                        all_processes = db.query(Process).filter(\r\n',
            '                            Process.process_number.in_([1, 2, 3, 4, 5, 6]),\r\n',
            '                            Process.is_active == True\r\n',
            '                        ).all()\r\n',
            '                        \r\n',
            '                        # Check if all have PASS results in their LATEST WIPProcessHistory\r\n',
            '                        passed_process_ids = []\r\n',
            '                        for proc in all_processes:\r\n',
            '                            # Get the latest completion record for this process\r\n',
            '                            latest_history = db.query(WIPProcessHistory).filter(\r\n',
            '                                WIPProcessHistory.wip_item_id == wip_for_query.id,\r\n',
            '                                WIPProcessHistory.process_id == proc.id,\r\n',
            '                                WIPProcessHistory.completed_at.isnot(None)\r\n',
            '                            ).order_by(\r\n',
            '                                WIPProcessHistory.completed_at.desc()\r\n',
            '                            ).first()\r\n',
            '                            \r\n',
            '                            # If latest attempt is PASS, count it\r\n',
            '                            if latest_history and latest_history.result == ProcessResult.PASS.value:\r\n',
            '                                passed_process_ids.append(proc.id)\r\n',
            '                        \r\n',
            '                        # If all processes passed, mark WIP as COMPLETED\r\n',
            '                        if len(passed_process_ids) >= len(all_processes):\r\n',
            '                            wip_for_query.status = WIPStatus.COMPLETED.value\r\n',
            '                            logger.info(f"WIP {wip_for_query.wip_id} marked as COMPLETED - all processes passed ({len(passed_process_ids)}/{len(all_processes)})")\r\n',
            '\r\n',
        ]
        
        lines[i:i] = wip_lines
        print(f"✅ Inserted WIP logic before line {i+1}")
        break

# Write back
with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n🎉 All fixes applied successfully!")
