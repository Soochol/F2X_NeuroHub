"""Test if Alembic can be imported."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("Testing Alembic import...")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    # Try to find alembic in the system
    import importlib.util
    spec = importlib.util.find_spec("alembic")
    if spec:
        print(f"Alembic found at: {spec.origin}")
    else:
        print("Alembic module not found in Python path")
except Exception as e:
    print(f"Error finding alembic: {e}")

# Check for alembic folder
alembic_dir = backend_dir / "alembic"
if alembic_dir.exists():
    print(f"\nAlembic directory exists: {alembic_dir}")
    contents = list(alembic_dir.iterdir())
    for item in contents:
        print(f"  - {item.name}")
else:
    print(f"\nAlembic directory not found: {alembic_dir}")

# Check for alembic.ini
ini_file = backend_dir / "alembic.ini"
if ini_file.exists():
    print(f"\nalembic.ini exists: {ini_file}")
else:
    print(f"\nalembic.ini not found: {ini_file}")

print("\nNote: Alembic needs to be installed with: pip install alembic")
print("Currently Alembic 1.13.0 is specified in requirements.txt")