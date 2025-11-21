"""
WIP number generation and validation utilities.

This module provides functions for generating, parsing, and validating WIP IDs
in the F2X NeuroHub Manufacturing Execution System. WIP IDs are temporary
identifiers assigned to units during production processes 1-6, before they
receive permanent serial numbers in process 7.

WIP ID Format: WIP-{LOT}-{SEQ} = 19 characters
    - Prefix: "WIP-" (4 chars)
    - LOT: LOT number (11 chars, format: {Country 2}{Line 2}{Model 3}{Month 4})
    - Separator: "-" (1 char)
    - Sequence: Sequence within LOT (3 chars, 001-999)

Example: WIP-KR01PSA2511-001
    - Prefix: WIP-
    - LOT: KR01PSA2511
    - Separator: -
    - Sequence: 001

Functions:
    - generate_wip_id: Generate WIP ID from LOT number and sequence
    - parse_wip_id: Parse WIP ID into components (LOT number, sequence)
    - validate_wip_id: Validate WIP ID format and components
    - generate_batch_wip_ids: Generate multiple WIP IDs for a LOT
"""

import re
from typing import Tuple, List, Optional


# WIP ID format constants
WIP_PREFIX = "WIP-"
WIP_ID_PATTERN = re.compile(r"^WIP-([A-Z0-9]{11})-(\d{3})$")
LOT_NUMBER_LENGTH = 11
SEQUENCE_LENGTH = 3
WIP_ID_LENGTH = 19  # WIP- (4) + LOT (11) + - (1) + SEQ (3) = 19

# Valid sequence range
MIN_SEQUENCE = 1
MAX_SEQUENCE = 100  # Business rule: max 100 units per LOT
MAX_LOT_QUANTITY = 100  # Business rule: max 100 units per LOT


def generate_wip_id(lot_number: str, sequence: int) -> str:
    """
    Generate WIP ID from LOT number and sequence.

    WIP ID Format: WIP-{LOT}-{SEQ}
    Example: WIP-KR01PSA2511-001

    Args:
        lot_number: LOT number (11 characters, format: {Country 2}{Line 2}{Model 3}{Month 4})
        sequence: Sequence number within LOT (1-999)

    Returns:
        Generated WIP ID (19 characters)

    Raises:
        ValueError: If LOT number or sequence is invalid

    Examples:
        >>> generate_wip_id("KR01PSA2511", 1)
        'WIP-KR01PSA2511-001'

        >>> generate_wip_id("KR01PSA2511", 42)
        'WIP-KR01PSA2511-042'

        >>> generate_wip_id("KR02WFA2511", 100)
        'WIP-KR02WFA2511-100'
    """
    # Validate LOT number
    if not lot_number:
        raise ValueError("lot_number is required")

    if not isinstance(lot_number, str):
        raise ValueError("lot_number must be a string")

    lot_number = lot_number.strip().upper()

    if len(lot_number) != LOT_NUMBER_LENGTH:
        raise ValueError(
            f"lot_number must be exactly {LOT_NUMBER_LENGTH} characters, "
            f"got {len(lot_number)}"
        )

    # Validate LOT number format: {Country 2}{Line 2}{Model 3}{Month 4}
    # Example: KR01PSA2511
    if not re.match(r"^[A-Z]{2}\d{2}[A-Z]{3}\d{4}$", lot_number):
        raise ValueError(
            f"Invalid LOT number format: {lot_number}. "
            f"Expected format: {{Country 2}}{{Line 2}}{{Model 3}}{{Month 4}} "
            f"(e.g., KR01PSA2511)"
        )

    # Validate sequence
    if not isinstance(sequence, int):
        raise ValueError("sequence must be an integer")

    if sequence < MIN_SEQUENCE or sequence > MAX_SEQUENCE:
        raise ValueError(
            f"sequence must be between {MIN_SEQUENCE} and {MAX_SEQUENCE}, "
            f"got {sequence}"
        )

    # Generate WIP ID
    sequence_str = f"{sequence:03d}"  # Zero-pad to 3 digits
    wip_id = f"{WIP_PREFIX}{lot_number}-{sequence_str}"

    return wip_id


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

        >>> parse_wip_id("WIP-KR01PSA2511-042")
        ('KR01PSA2511', 42)

        >>> parse_wip_id("WIP-KR02WFA2511-100")
        ('KR02WFA2511', 100)
    """
    if not wip_id:
        raise ValueError("wip_id is required")

    if not isinstance(wip_id, str):
        raise ValueError("wip_id must be a string")

    wip_id = wip_id.strip().upper()

    # Validate format
    match = WIP_ID_PATTERN.match(wip_id)
    if not match:
        raise ValueError(
            f"Invalid WIP ID format: {wip_id}. "
            f"Expected format: WIP-{{LOT 11}}-{{SEQ 3}} (e.g., WIP-KR01PSA2511-001)"
        )

    lot_number = match.group(1)
    sequence_str = match.group(2)
    sequence = int(sequence_str)

    return lot_number, sequence


def validate_wip_id(wip_id: str) -> bool:
    """
    Validate WIP ID format and components.

    Args:
        wip_id: WIP ID to validate

    Returns:
        True if WIP ID is valid, False otherwise

    Examples:
        >>> validate_wip_id("WIP-KR01PSA2511-001")
        True

        >>> validate_wip_id("WIP-KR01PSA2511-042")
        True

        >>> validate_wip_id("WIP-INVALID-001")
        False

        >>> validate_wip_id("INVALID")
        False
    """
    try:
        parse_wip_id(wip_id)
        return True
    except ValueError:
        return False


def generate_batch_wip_ids(lot_number: str, quantity: int, start_sequence: int = 1) -> List[str]:
    """
    Generate multiple WIP IDs for a LOT.

    This is used when starting WIP generation for a LOT. Generates a batch of
    sequential WIP IDs.

    Args:
        lot_number: LOT number (11 characters)
        quantity: Number of WIP IDs to generate (1-100)
        start_sequence: Starting sequence number (default: 1)

    Returns:
        List of generated WIP IDs

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> generate_batch_wip_ids("KR01PSA2511", 3)
        ['WIP-KR01PSA2511-001', 'WIP-KR01PSA2511-002', 'WIP-KR01PSA2511-003']

        >>> generate_batch_wip_ids("KR01PSA2511", 2, start_sequence=5)
        ['WIP-KR01PSA2511-005', 'WIP-KR01PSA2511-006']
    """
    # Validate quantity
    if not isinstance(quantity, int):
        raise ValueError("quantity must be an integer")

    if quantity < 1 or quantity > MAX_LOT_QUANTITY:
        raise ValueError(
            f"quantity must be between 1 and {MAX_LOT_QUANTITY}, got {quantity}"
        )

    # Validate start_sequence
    if not isinstance(start_sequence, int):
        raise ValueError("start_sequence must be an integer")

    if start_sequence < MIN_SEQUENCE:
        raise ValueError(
            f"start_sequence must be at least {MIN_SEQUENCE}, got {start_sequence}"
        )

    # Check that end sequence doesn't exceed max
    end_sequence = start_sequence + quantity - 1
    if end_sequence > MAX_SEQUENCE:
        raise ValueError(
            f"end_sequence ({end_sequence}) would exceed maximum ({MAX_SEQUENCE}). "
            f"Reduce quantity or start_sequence."
        )

    # Generate batch of WIP IDs
    wip_ids = []
    for seq in range(start_sequence, start_sequence + quantity):
        wip_id = generate_wip_id(lot_number, seq)
        wip_ids.append(wip_id)

    return wip_ids


def get_next_sequence(lot_number: str, existing_wip_ids: List[str]) -> int:
    """
    Get next available sequence number for a LOT.

    This is useful when adding more WIP IDs to an existing LOT.

    Args:
        lot_number: LOT number (11 characters)
        existing_wip_ids: List of existing WIP IDs for this LOT

    Returns:
        Next available sequence number

    Raises:
        ValueError: If all sequences are used (max 999)

    Examples:
        >>> existing = ['WIP-KR01PSA2511-001', 'WIP-KR01PSA2511-002']
        >>> get_next_sequence("KR01PSA2511", existing)
        3

        >>> existing = []
        >>> get_next_sequence("KR01PSA2511", existing)
        1
    """
    if not existing_wip_ids:
        return MIN_SEQUENCE

    # Parse all sequences from existing WIP IDs
    sequences = []
    for wip_id in existing_wip_ids:
        try:
            parsed_lot, seq = parse_wip_id(wip_id)
            if parsed_lot == lot_number:
                sequences.append(seq)
        except ValueError:
            # Skip invalid WIP IDs
            continue

    if not sequences:
        return MIN_SEQUENCE

    # Find max sequence and return next
    max_seq = max(sequences)

    if max_seq >= MAX_SEQUENCE:
        raise ValueError(
            f"All sequences exhausted for LOT {lot_number} (max: {MAX_SEQUENCE})"
        )

    return max_seq + 1


def extract_lot_number(wip_id: str) -> Optional[str]:
    """
    Extract LOT number from WIP ID.

    Convenience function to get just the LOT number without parsing the full ID.

    Args:
        wip_id: WIP ID to extract from

    Returns:
        LOT number if valid, None if invalid

    Examples:
        >>> extract_lot_number("WIP-KR01PSA2511-001")
        'KR01PSA2511'

        >>> extract_lot_number("INVALID")
        None
    """
    try:
        lot_number, _ = parse_wip_id(wip_id)
        return lot_number
    except ValueError:
        return None
