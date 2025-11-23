"""Test equipment creation to identify validation error"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.schemas.equipment import EquipmentCreate
from pydantic import ValidationError

# Test data that matches the frontend form
test_data = {
    "equipment_code": "EQ_TEST_001",
    "equipment_name": "Test Equipment",
    "equipment_type": "TEST_TYPE",
    "description": "",
    "process_id": None,
    "production_line_id": None,
    "manufacturer": "",
    "model_number": "",
    "serial_number": "",
    "status": "AVAILABLE",
    "is_active": True,
}

print("\n=== Testing Equipment Creation Validation ===\n")
print(f"Test data: {test_data}\n")

try:
    equipment = EquipmentCreate(**test_data)
    print("✅ Validation PASSED!")
    print(f"Created equipment schema: {equipment.model_dump()}")
except ValidationError as e:
    print("❌ Validation FAILED!")
    print(f"\nValidation errors:")
    for error in e.errors():
        print(f"  - Field: {error['loc']}")
        print(f"    Type: {error['type']}")
        print(f"    Message: {error['msg']}")
        print(f"    Input: {error.get('input', 'N/A')}")
        print()
