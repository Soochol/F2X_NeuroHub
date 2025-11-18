"""Test script to verify history dialog imports and initialization"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from services.history_service import HistoryService
    print("✓ HistoryService imported successfully")
except ImportError as e:
    print(f"✗ Failed to import HistoryService: {e}")
    sys.exit(1)

try:
    from views.history_dialog import HistoryDialog
    print("✓ HistoryDialog imported successfully")
except ImportError as e:
    print(f"✗ Failed to import HistoryDialog: {e}")
    sys.exit(1)

try:
    from services import APIClient
    print("✓ APIClient imported successfully")
except ImportError as e:
    print(f"✗ Failed to import APIClient: {e}")
    sys.exit(1)

# Test initialization
print("\nTesting initialization...")

try:
    api_client = APIClient("http://localhost:8000")
    print("✓ APIClient initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize APIClient: {e}")
    sys.exit(1)

try:
    history_service = HistoryService(api_client)
    print("✓ HistoryService initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize HistoryService: {e}")
    sys.exit(1)

print("\n✓ All imports and initializations successful!")
print("\nNext steps:")
print("1. Run the main application: python main.py")
print("2. Login to the system")
print("3. Use Ctrl+H or menu View > 작업 이력 to open history dialog")
