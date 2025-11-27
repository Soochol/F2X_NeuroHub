"""
WIP ID Validation Utilities.

Validates WIP ID format for the F2X NeuroHub Manufacturing Execution System.
WIP IDs are temporary identifiers assigned to units during production.

WIP ID Format: WIP-{LOT}-{SEQ}
    - Prefix: "WIP-" (4 chars)
    - LOT: LOT number (10-20 chars, alphanumeric with hyphens)
    - Separator: "-" (1 char)
    - Sequence: Sequence within LOT (3 chars, 001-999)

Example: WIP-KR01PSA2511-001, WIP-DT01A10251101-002

This module mirrors the backend implementation in:
backend/app/utils/wip_number.py
"""

import re
from typing import Optional, Tuple


# WIP ID format pattern
# Allows LOT numbers between 10 and 20 characters (alphanumeric and hyphens)
WIP_ID_PATTERN = re.compile(r"^WIP-([A-Z0-9-]{10,20})-(\d{3})$")


def validate_wip_id(wip_id: str) -> bool:
    """
    Validate WIP ID format.

    Args:
        wip_id: WIP ID to validate

    Returns:
        True if WIP ID is valid, False otherwise

    Examples:
        >>> validate_wip_id("WIP-KR01PSA2511-001")
        True
        >>> validate_wip_id("WIP-DT01A10251101-002")
        True
        >>> validate_wip_id("INVALID")
        False
        >>> validate_wip_id("KR01PSA2511001")
        False
    """
    if not wip_id or not isinstance(wip_id, str):
        return False

    wip_id = wip_id.strip().upper()
    return WIP_ID_PATTERN.match(wip_id) is not None


def parse_wip_id(wip_id: str) -> Tuple[str, int]:
    """
    Parse WIP ID into components (LOT number, sequence).

    Args:
        wip_id: WIP ID to parse (format: WIP-{LOT}-{SEQ})

    Returns:
        Tuple of (lot_number, sequence)

    Raises:
        ValueError: If WIP ID format is invalid

    Examples:
        >>> parse_wip_id("WIP-KR01PSA2511-001")
        ('KR01PSA2511', 1)
        >>> parse_wip_id("WIP-DT01A10251101-002")
        ('DT01A10251101', 2)
    """
    if not wip_id or not isinstance(wip_id, str):
        raise ValueError("wip_id is required")

    wip_id = wip_id.strip().upper()

    match = WIP_ID_PATTERN.match(wip_id)
    if not match:
        raise ValueError(
            f"Invalid WIP ID format: {wip_id}. "
            f"Expected format: WIP-{{LOT}}-{{SEQ}} (e.g., WIP-KR01PSA2511-001)"
        )

    lot_number = match.group(1)
    sequence = int(match.group(2))

    return lot_number, sequence


def extract_lot_from_wip_id(wip_id: str) -> Optional[str]:
    """
    Extract LOT number from WIP ID.

    Args:
        wip_id: WIP ID to extract from

    Returns:
        LOT number if valid, None if invalid

    Examples:
        >>> extract_lot_from_wip_id("WIP-KR01PSA2511-001")
        'KR01PSA2511'
        >>> extract_lot_from_wip_id("INVALID")
        None
    """
    try:
        lot_number, _ = parse_wip_id(wip_id)
        return lot_number
    except ValueError:
        return None
