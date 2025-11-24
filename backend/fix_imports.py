"""
Script to fix missing imports in process_service.py
"""

# Read the file
with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the target string to replace
target = """    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus
)"""

# Define the replacement string
replacement = """    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus, WIPProcessHistory, WIPStatus
)"""

# Perform the replacement
if target in content:
    new_content = content.replace(target, replacement)
    with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Successfully added WIPProcessHistory and WIPStatus to imports.")
else:
    print("❌ Target string not found. Checking for partial match...")
    # Fallback: try to find just the last line of imports
    partial_target = "    LotStatus, SerialStatus\n)"
    partial_replacement = "    LotStatus, SerialStatus, WIPProcessHistory, WIPStatus\n)"
    
    if partial_target in content:
        new_content = content.replace(partial_target, partial_replacement)
        with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully added imports using partial match.")
    else:
        print("❌ Could not find import block to replace.")
        # Print the actual content around the area for debugging
        start_idx = content.find("from app.models import")
        if start_idx != -1:
            print("Actual content found:")
            print(content[start_idx:start_idx+200])
