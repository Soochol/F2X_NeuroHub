"""
WIP (Work-In-Progress) business service module.

This module implements business rules and validation logic for WIP ID management
in the F2X NeuroHub Manufacturing Execution System. It enforces the following
business rules:

Business Rules:
    BR-001: LOT must be in CREATED status to generate WIP IDs
    BR-002: WIP generation automatically transitions LOT to IN_PROGRESS
    BR-003: Process can only start if previous process is PASS (except process 1)
    BR-004: Same process cannot have duplicate PASS results
    BR-005: Serial conversion requires all processes 1-6 to be PASS
    BR-006: WIP ID format validation (WIP-{LOT}-{SEQ})

Functions:
    - validate_lot_for_wip_generation: BR-001
    - validate_process_start: BR-003
    - validate_process_completion: BR-004
    - validate_serial_conversion: BR-005
    - can_start_process: Check if WIP can start a specific process
    - get_completed_processes: Get list of completed processes for WIP
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.lot import Lot, LotStatus
from app.models.wip_item import WIPItem, WIPStatus
from app.models.wip_process_history import WIPProcessHistory, ProcessResult
from app.models.process import Process


class WIPValidationError(Exception):
    """Exception raised for WIP validation errors."""
    pass


def validate_lot_for_wip_generation(db: Session, lot: Lot, quantity: int) -> None:
    """
    Validate LOT can generate WIP IDs (BR-001).

    Business Rule BR-001:
    - LOT must be in CREATED status to generate WIP IDs
    - Quantity must be within 1-100 range
    - Quantity must not exceed LOT target_quantity

    Args:
        db: Database session
        lot: LOT instance to validate
        quantity: Number of WIP IDs to generate

    Raises:
        WIPValidationError: If validation fails
    """
    # BR-001: LOT must be CREATED or IN_PROGRESS status
    if lot.status not in (LotStatus.CREATED.value, LotStatus.IN_PROGRESS.value):
        raise WIPValidationError(
            f"LOT {lot.lot_number} must be in CREATED or IN_PROGRESS status to generate WIP IDs. "
            f"Current status: {lot.status}"
        )

    # Validate quantity range
    if quantity < 1 or quantity > 100:
        raise WIPValidationError(
            f"Quantity must be between 1 and 100, got {quantity}"
        )

    # Validate quantity doesn't exceed target
    # REMOVED: WIP generation should not be limited by target quantity (User Request)
    # if quantity > lot.target_quantity:
    #     raise WIPValidationError(
    #         f"Quantity {quantity} exceeds LOT target_quantity {lot.target_quantity}"
    #     )

    # Check if WIP IDs already exist for this LOT
    # REMOVED: Allow adding more WIP IDs to existing LOT (User Request)
    # existing_count = db.query(WIPItem).filter(
    #     WIPItem.lot_id == lot.id
    # ).count()
    #
    # if existing_count > 0:
    #     raise WIPValidationError(
    #         f"LOT {lot.lot_number} already has {existing_count} WIP IDs. "
    #         f"Cannot generate more WIP IDs."
    #     )


def validate_process_start(
    db: Session,
    wip_item: WIPItem,
    process_id: int,
    process_number: int,
) -> None:
    """
    Validate WIP can start a process (BR-003).

    Business Rule BR-003:
    - Process 1: Can start if WIP is CREATED or IN_PROGRESS
    - Process 2-6: Can only start if previous process is PASS
    - WIP must not be in FAILED or CONVERTED status
    - Process must be 1-6 (process 7 is serial conversion)

    Args:
        db: Database session
        wip_item: WIP item instance
        process_id: Process identifier
        process_number: Process number (1-6)

    Raises:
        WIPValidationError: If validation fails
    """
    # Validate process number
    if process_number < 1 or process_number > 6:
        raise WIPValidationError(
            f"Process number must be 1-6, got {process_number}"
        )

    # Check WIP status
    if wip_item.status == WIPStatus.FAILED.value:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} is in FAILED status and cannot start processes"
        )

    if wip_item.status == WIPStatus.CONVERTED.value:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} is already converted to serial number"
        )

    # BR-003: Process 1 can always start if WIP is CREATED or IN_PROGRESS
    if process_number == 1:
        if wip_item.status not in (WIPStatus.CREATED.value, WIPStatus.IN_PROGRESS.value):
            raise WIPValidationError(
                f"WIP {wip_item.wip_id} must be in CREATED or IN_PROGRESS status. "
                f"Current status: {wip_item.status}"
            )
        return

    # BR-003: For processes 2-6, check if previous process is PASS
    previous_process_number = process_number - 1

    # Get previous process
    previous_process = db.query(Process).filter(
        Process.process_number == previous_process_number
    ).first()

    if not previous_process:
        raise WIPValidationError(
            f"Previous process {previous_process_number} not found"
        )

    # Check if previous process has PASS result
    previous_pass = db.query(WIPProcessHistory).filter(
        WIPProcessHistory.wip_item_id == wip_item.id,
        WIPProcessHistory.process_id == previous_process.id,
        WIPProcessHistory.result == ProcessResult.PASS.value,
    ).first()

    if not previous_pass:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} cannot start process {process_number}. "
            f"Previous process {previous_process_number} must be completed with PASS result."
        )


def validate_process_completion(
    db: Session,
    wip_item: WIPItem,
    process_id: int,
    result: str,
) -> None:
    """
    Validate process completion (BR-004).

    Business Rule BR-004:
    - Same process cannot have duplicate PASS results
    - FAIL results are allowed (for tracking multiple failures)

    Args:
        db: Database session
        wip_item: WIP item instance
        process_id: Process identifier
        result: Process result (PASS or FAIL)

    Raises:
        WIPValidationError: If validation fails
    """
    # BR-004: Check for duplicate PASS result
    if result == ProcessResult.PASS.value:
        existing_pass = db.query(WIPProcessHistory).filter(
            WIPProcessHistory.wip_item_id == wip_item.id,
            WIPProcessHistory.process_id == process_id,
            WIPProcessHistory.result == ProcessResult.PASS.value,
        ).first()

        if existing_pass:
            raise WIPValidationError(
                f"WIP {wip_item.wip_id} already has PASS result for process {process_id}. "
                f"Duplicate PASS results are not allowed (BR-004)."
            )


def validate_serial_conversion(
    db: Session,
    wip_item: WIPItem,
) -> None:
    """
    Validate WIP can be converted to serial number (BR-005).

    Business Rule BR-005:
    - All processes 1-6 must have PASS results
    - WIP must be in COMPLETED status
    - WIP must not already be converted

    Args:
        db: Database session
        wip_item: WIP item instance

    Raises:
        WIPValidationError: If validation fails
    """
    # Check WIP status
    if wip_item.status != WIPStatus.COMPLETED.value:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} must be in COMPLETED status for serial conversion. "
            f"Current status: {wip_item.status}"
        )

    # Check if already converted
    if wip_item.serial_id is not None:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} is already converted to serial {wip_item.serial_id}"
        )

    # BR-005: Check all processes 1-6 have PASS results
    required_processes = list(range(1, 7))  # [1, 2, 3, 4, 5, 6]

    # Get all processes
    processes = db.query(Process).filter(
        Process.process_number.in_(required_processes)
    ).all()

    if len(processes) != 6:
        raise WIPValidationError(
            f"Expected 6 processes (1-6), found {len(processes)}"
        )

    # Check PASS results for each process
    missing_processes = []
    for process in processes:
        pass_result = db.query(WIPProcessHistory).filter(
            WIPProcessHistory.wip_item_id == wip_item.id,
            WIPProcessHistory.process_id == process.id,
            WIPProcessHistory.result == ProcessResult.PASS.value,
        ).first()

        if not pass_result:
            missing_processes.append(process.process_number)

    if missing_processes:
        raise WIPValidationError(
            f"WIP {wip_item.wip_id} cannot be converted to serial. "
            f"Missing PASS results for processes: {missing_processes} (BR-005)"
        )


def can_start_process(
    db: Session,
    wip_item: WIPItem,
    process_number: int,
) -> Tuple[bool, Optional[str]]:
    """
    Check if WIP can start a specific process.

    This is a non-throwing version of validate_process_start that returns
    a boolean and error message instead of raising exceptions.

    Args:
        db: Database session
        wip_item: WIP item instance
        process_number: Process number (1-6)

    Returns:
        Tuple of (can_start: bool, error_message: Optional[str])
    """
    try:
        # Get process
        process = db.query(Process).filter(
            Process.process_number == process_number
        ).first()

        if not process:
            return False, f"Process {process_number} not found"

        validate_process_start(db, wip_item, process.id, process_number)
        return True, None

    except WIPValidationError as e:
        return False, str(e)


def get_completed_processes(
    db: Session,
    wip_item: WIPItem,
) -> List[int]:
    """
    Get list of process numbers that have PASS results for a WIP item.

    Args:
        db: Database session
        wip_item: WIP item instance

    Returns:
        List of process numbers (1-6) with PASS results
    """
    # Get all PASS results for this WIP
    pass_results = db.query(WIPProcessHistory).join(
        Process,
        WIPProcessHistory.process_id == Process.id
    ).filter(
        WIPProcessHistory.wip_item_id == wip_item.id,
        WIPProcessHistory.result == ProcessResult.PASS.value,
    ).all()

    # Extract process numbers
    completed = [history.process.process_number for history in pass_results]
    return sorted(completed)


def get_next_process(
    db: Session,
    wip_item: WIPItem,
) -> Optional[int]:
    """
    Get next process number that WIP should complete.

    Args:
        db: Database session
        wip_item: WIP item instance

    Returns:
        Next process number (1-6) or None if all completed
    """
    completed = get_completed_processes(db, wip_item)

    # Find first missing process
    for process_number in range(1, 7):
        if process_number not in completed:
            return process_number

    # All processes completed
    return None


def calculate_wip_completion_rate(
    db: Session,
    lot_id: int,
) -> dict:
    """
    Calculate WIP completion statistics for a LOT.

    Args:
        db: Database session
        lot_id: LOT identifier

    Returns:
        Dictionary with completion statistics
    """
    # Get all WIP items for LOT
    wip_items = db.query(WIPItem).filter(
        WIPItem.lot_id == lot_id
    ).all()

    total = len(wip_items)
    if total == 0:
        return {
            "total": 0,
            "completed": 0,
            "in_progress": 0,
            "failed": 0,
            "converted": 0,
            "completion_rate": 0.0,
        }

    # Count by status
    completed = sum(1 for w in wip_items if w.status == WIPStatus.COMPLETED.value)
    in_progress = sum(1 for w in wip_items if w.status == WIPStatus.IN_PROGRESS.value)
    failed = sum(1 for w in wip_items if w.status == WIPStatus.FAILED.value)
    converted = sum(1 for w in wip_items if w.status == WIPStatus.CONVERTED.value)

    completion_rate = (completed + converted) / total * 100

    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "failed": failed,
        "converted": converted,
        "completion_rate": round(completion_rate, 2),
    }
