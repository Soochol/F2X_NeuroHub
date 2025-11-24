#!/usr/bin/env python3
"""Fix timezone issues in process_service.py"""

with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: start_process - Replace datetime.utcnow() with datetime.now(tz=timezone.utc)
content = content.replace(
    'started_at = datetime.utcnow()',
    'started_at = datetime.now(tz=timezone.utc)'
)

# Fix 2: complete_process - Replace datetime.now(timezone.utc) with datetime.now(tz=timezone.utc) 
content = content.replace(
    'completed_at = datetime.now(timezone.utc)',
    'completed_at = datetime.now(tz=timezone.utc)'
)

with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed timezone issues!")
print("  - start_process: datetime.utcnow() → datetime.now(tz=timezone.utc)")
print("  - complete_process: datetime.now(timezone.utc) → datetime.now(tz=timezone.utc)")
