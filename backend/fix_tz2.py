#!/usr/bin/env python3
"""Fix timezone line 456-457"""

with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace lines 456-457
for i in range(len(lines)):
    if i == 455 and 'korea_tz = timezone(timedelta(hours=9))' in lines[i]:
        # Replace line 456 with new completed_at line
        lines[i] = '            completed_at = datetime.now(tz=timezone.utc)\r\n'
        # Delete line 457
        if i + 1 < len(lines) and 'completed_at = datetime.now(korea_tz)' in lines[i + 1]:
            del lines[i + 1]
        break

with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed line 456-457!")
