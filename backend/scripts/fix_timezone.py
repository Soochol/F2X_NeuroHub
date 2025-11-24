"""Fix timezone handling in process_service.py"""
import re

# Read the file
with open('app/services/process_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Replace korea_tz timezone definition and completed_at assignment
old_text1 = """            # Update process data
            korea_tz = timezone(timedelta(hours=9))
            completed_at = datetime.now(korea_tz)"""

new_text1 = """            # Update process data
            completed_at = datetime.now(timezone.utc)"""

content = content.replace(old_text1, new_text1)

# Fix 2: Replace timezone handling in duration calculation
old_text2 = """                if start_ts.tzinfo is None:
                    start_ts = start_ts.replace(tzinfo=korea_tz)
                if end_ts.tzinfo is None:
                    end_ts = end_ts.replace(tzinfo=korea_tz)"""

new_text2 = """                # Convert to UTC for consistent calculation
                if start_ts.tzinfo is None:
                    start_ts = start_ts.replace(tzinfo=timezone.utc)
                else:
                    start_ts = start_ts.astimezone(timezone.utc)
                
                if end_ts.tzinfo is None:
                    end_ts = end_ts.replace(tzinfo=timezone.utc)
                else:
                    end_ts = end_ts.astimezone(timezone.utc)"""

content = content.replace(old_text2, new_text2)

# Write the fixed content back
with open('app/services/process_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully fixed timezone handling in process_service.py")
print("Changes made:")
print("1. Replaced korea_tz with timezone.utc for completed_at timestamp")
print("2. Updated duration calculation to consistently use UTC")
