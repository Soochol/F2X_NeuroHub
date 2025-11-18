"""JSON Parser and Validator for process completion data"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class JSONParser:
    """Parse and validate process completion JSON files"""

    REQUIRED_FIELDS = [
        'lot_number',
        'process_id',
        'equipment_id',
        'worker_id',
        'start_time',
        'complete_time',
        'process_data'
    ]

    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """Parse JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def validate(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate JSON data
        Returns: (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        for field in JSONParser.REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        # Validate LOT number format
        if 'lot_number' in data:
            lot_number = data['lot_number']
            if not JSONParser._validate_lot_number(lot_number):
                errors.append(f"Invalid LOT number format: {lot_number}")

        # Validate process_id
        if 'process_id' in data:
            process_id = data['process_id']
            if not process_id.startswith('PROC-'):
                errors.append(f"Invalid process_id format: {process_id}")

        return (len(errors) == 0, errors)

    @staticmethod
    def _validate_lot_number(lot_number: str) -> bool:
        """Validate LOT number format: WF-KR-YYMMDDX-nnn"""
        import re
        pattern = r'^WF-KR-\d{6}[DN]-\d{3}$'
        return bool(re.match(pattern, lot_number))

    @staticmethod
    def extract_process_number(process_id: str) -> Optional[int]:
        """Extract process number from PROC-00X format"""
        try:
            return int(process_id.split('-')[1])
        except (IndexError, ValueError):
            return None
