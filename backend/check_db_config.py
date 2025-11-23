import sys
sys.path.append('.')

from app.config import settings

print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")
print(f"Is SQLite: {'sqlite' in settings.DATABASE_URL}")

# Check actual database file
from app.database import engine
print(f"\nEngine URL: {engine.url}")

# List database files in current directory
import os
print(f"\n.db files in backend directory:")
for file in os.listdir('.'):
    if file.endswith('.db'):
        size = os.path.getsize(file)
        print(f"  {file}: {size} bytes")
