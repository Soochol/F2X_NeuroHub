"""
Serial Number Validation and Formatting Utilities
==================================================

Handles both V0 (legacy) and V1 (new standard) serial number formats:
- V1 (New Standard): KR01PSA2511001 (14 chars, no hyphens)
- V0 (Legacy): WF-KR-251119D-003-0038 (22-24 chars with hyphens)

This module mirrors the TypeScript implementation in:
frontend/src/utils/serialNumber.ts
"""

import re
from typing import Optional, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SerialNumberV1Components:
    """V1 Serial number components."""
    country_code: str
    line_number: str
    model_code: str
    production_month: str
    sequence: str


@dataclass
class SerialNumberV0Components:
    """V0 Serial number components (legacy)."""
    model_code: str
    country_code: str
    production_date: str
    shift: str
    lot_sequence: str
    serial_sequence: str


# V1 format regex: KR01PSA2511001 (14 characters)
SERIAL_PATTERN_V1 = re.compile(r'^[A-Z]{2}\d{2}[A-Z]{3}\d{4}\d{3}$')

# V0 format regex: WF-KR-251119D-003-0038 (legacy with hyphens)
SERIAL_PATTERN_V0 = re.compile(r'^[A-Z]{2,}-[A-Z]{2}-\d{6}[DN]-\d{3}-\d{4}$')


def validate_serial_number_v1(serial: str) -> bool:
    """
    Validate V1 serial number format (new standard).

    Args:
        serial: Serial number string

    Returns:
        True if valid V1 format (14 chars: KR01PSA2511001)

    Example:
        >>> validate_serial_number_v1("KR01PSA2511001")
        True
        >>> validate_serial_number_v1("INVALID")
        False
    """
    if not serial or not isinstance(serial, str):
        return False
    return SERIAL_PATTERN_V1.match(serial) is not None


def validate_serial_number_v0(serial: str) -> bool:
    """
    Validate V0 serial number format (legacy).

    Args:
        serial: Serial number string

    Returns:
        True if valid V0 format (with hyphens: WF-KR-251119D-003-0038)

    Example:
        >>> validate_serial_number_v0("WF-KR-251119D-003-0038")
        True
    """
    if not serial or not isinstance(serial, str):
        return False
    return SERIAL_PATTERN_V0.match(serial) is not None


def validate_serial_number(serial: str) -> bool:
    """
    Validate serial number (any version).

    Args:
        serial: Serial number string

    Returns:
        True if valid V0 or V1 format
    """
    return validate_serial_number_v1(serial) or validate_serial_number_v0(serial)


def detect_serial_version(serial: str) -> Optional[int]:
    """
    Auto-detect serial number version.

    Args:
        serial: Serial number string

    Returns:
        1 for V1, 0 for V0, None if invalid

    Example:
        >>> detect_serial_version("KR01PSA2511001")
        1
        >>> detect_serial_version("WF-KR-251119D-003-0038")
        0
        >>> detect_serial_version("INVALID")
        None
    """
    if validate_serial_number_v1(serial):
        return 1
    if validate_serial_number_v0(serial):
        return 0
    return None


def parse_serial_number_v1(serial: str) -> SerialNumberV1Components:
    """
    Parse V1 format serial number into components (new standard).

    Args:
        serial: Serial number (14 chars): KR01PSA2511001

    Returns:
        Parsed components

    Raises:
        ValueError: If invalid format

    Example:
        >>> parse_serial_number_v1("KR01PSA2511001")
        SerialNumberV1Components(
            country_code='KR',
            line_number='01',
            model_code='PSA',
            production_month='2511',
            sequence='001'
        )
    """
    if not validate_serial_number_v1(serial):
        raise ValueError(
            f"Invalid V1 serial number format: {serial}. "
            "Expected format: KR01PSA2511001 (14 characters)"
        )

    return SerialNumberV1Components(
        country_code=serial[0:2],
        line_number=serial[2:4],
        model_code=serial[4:7],
        production_month=serial[7:11],
        sequence=serial[11:14],
    )


def parse_serial_number_v0(serial: str) -> SerialNumberV0Components:
    """
    Parse V0 format serial number into components (legacy).

    Args:
        serial: Serial number: WF-KR-251119D-003-0038

    Returns:
        Parsed components

    Raises:
        ValueError: If invalid format
    """
    if not validate_serial_number_v0(serial):
        raise ValueError(
            f"Invalid V0 serial number format: {serial}. "
            "Expected format: WF-KR-251119D-003-0038"
        )

    parts = serial.split('-')
    return SerialNumberV0Components(
        model_code=parts[0],
        country_code=parts[1],
        production_date=parts[2][:6],
        shift=parts[2][6:],
        lot_sequence=parts[3],
        serial_sequence=parts[4],
    )


def format_serial_number_v1(serial: str, separator: str = '-') -> str:
    """
    Format V1 serial number for display (add hyphens).

    Args:
        serial: Serial number (14 chars): KR01PSA2511001
        separator: Separator character (default: "-")

    Returns:
        Formatted string: KR01-PSA-2511-001

    Example:
        >>> format_serial_number_v1("KR01PSA2511001")
        'KR01-PSA-2511-001'
        >>> format_serial_number_v1("KR01PSA2511001", " ")
        'KR01 PSA 2511 001'
    """
    if not validate_serial_number_v1(serial):
        return serial  # Return as-is if invalid

    parts = [
        serial[0:4],    # KR01
        serial[4:7],    # PSA
        serial[7:11],   # 2511
        serial[11:14],  # 001
    ]

    return separator.join(parts)


def format_serial_number(serial: str, separator: str = '-') -> str:
    """
    Format serial number (auto-detects version).

    Args:
        serial: Serial number (any format)
        separator: Separator for V1 format (default: "-")

    Returns:
        Formatted serial number

    Example:
        >>> format_serial_number("KR01PSA2511001")
        'KR01-PSA-2511-001'
        >>> format_serial_number("WF-KR-251119D-003-0038")
        'WF-KR-251119D-003-0038'
    """
    version = detect_serial_version(serial)

    if version == 1:
        return format_serial_number_v1(serial, separator)

    # V0 or invalid - return as-is
    return serial


def parse_production_month(month_str: str) -> datetime:
    """
    Parse production month from V1 format (YYMM).

    Args:
        month_str: Month string: "2511" (Nov 2025)

    Returns:
        datetime object (first day of the month)

    Raises:
        ValueError: If invalid format or month value

    Example:
        >>> parse_production_month("2511")
        datetime(2025, 11, 1, 0, 0)
    """
    if len(month_str) != 4:
        raise ValueError(
            f"Invalid month format: {month_str}. Expected YYMM (4 digits)"
        )

    year = 2000 + int(month_str[0:2])
    month = int(month_str[2:4])

    if month < 1 or month > 12:
        raise ValueError(
            f"Invalid month value: {month}. Must be 01-12"
        )

    return datetime(year, month, 1)


def get_serial_info(serial: str) -> Dict:
    """
    Get detailed serial number information.

    Args:
        serial: Serial number string

    Returns:
        Dictionary with parsed data and metadata

    Example:
        >>> get_serial_info("KR01PSA2511001")
        {
            'serial': 'KR01PSA2511001',
            'valid': True,
            'version': 1,
            'formatted': 'KR01-PSA-2511-001',
            'components': SerialNumberV1Components(...),
            'production_date': '2025-11-01T00:00:00'
        }
    """
    version = detect_serial_version(serial)

    if version is None:
        return {
            'serial': serial,
            'valid': False,
            'version': None,
            'formatted': serial,
            'error': 'Invalid serial number format',
        }

    if version == 1:
        components = parse_serial_number_v1(serial)
        production_date = parse_production_month(components.production_month)

        return {
            'serial': serial,
            'valid': True,
            'version': 1,
            'formatted': format_serial_number_v1(serial),
            'components': components,
            'production_date': production_date.isoformat(),
        }
    else:  # version == 0
        components = parse_serial_number_v0(serial)

        return {
            'serial': serial,
            'valid': True,
            'version': 0,
            'formatted': serial,  # V0 already has hyphens
            'components': components,
        }


# Export patterns for external use
PATTERNS = {
    'V0': SERIAL_PATTERN_V0,
    'V1': SERIAL_PATTERN_V1,
}


if __name__ == '__main__':
    # Example usage
    test_serials = [
        "KR01PSA2511001",
        "WF-KR-251119D-003-0038",
        "INVALID",
    ]

    for serial in test_serials:
        print(f"\nSerial: {serial}")
        info = get_serial_info(serial)
        print(f"  Valid: {info['valid']}")
        print(f"  Version: {info['version']}")
        print(f"  Formatted: {info['formatted']}")
        if 'components' in info:
            print(f"  Components: {info['components']}")
