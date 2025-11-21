"""FastAPI router for WIP Item entity endpoints.

This module provides RESTful API endpoints for managing WIP (Work-In-Progress)
items in the F2X NeuroHub MES system. Implements WIP ID generation, process
tracking, barcode operations, and serial conversion.

Endpoints:
    GET /wip-items: List WIP items with filters
    GET /wip-items/{wip_id}: Get WIP by ID
    GET /wip-items/barcode/{wip_id}: Generate barcode image
    POST /wip-items/{wip_id}/scan: Scan WIP barcode
    POST /wip-items/{wip_id}/start-process: Start process (BR-003)
    POST /wip-items/{wip_id}/complete-process: Complete process (BR-004)
    POST /wip-items/{wip_id}/convert-to-serial: Convert to serial (BR-005)
    GET /wip-items/statistics: Get WIP statistics

Note: WIP generation endpoint moved to /lots/{lot_id}/start-wip-generation in lots.py
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.crud import wip_item as crud
from app.schemas.wip_item import (
    WIPItemCreate,
    WIPItemInDB,
    WIPItemScan,
    WIPItemProcessStart,
    WIPItemProcessComplete,
    WIPItemConvert,
    WIPStatistics,
    WIPStatus,
)
from app.utils.barcode_generator import generate_barcode_image
from app.services.wip_service import WIPValidationError


router = APIRouter(
    prefix="/wip-items",
    tags=["WIP Items"],
    responses={
        404: {"description": "WIP item not found"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict (e.g., constraint violation)"},
    },
)


@router.get(
    "/",
    response_model=List[WIPItemInDB],
    summary="List WIP items",
    description="Retrieve paginated list of WIP items with optional filters",
)
def list_wip_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    lot_id: Optional[int] = Query(None, description="Filter by LOT ID"),
    status: Optional[WIPStatus] = Query(None, description="Filter by status"),
    process_id: Optional[int] = Query(None, description="Filter by current process"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> List[WIPItemInDB]:
    """
    List WIP items with pagination and filters.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum records to return
        lot_id: Optional LOT ID filter
        status: Optional status filter
        process_id: Optional process ID filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of WIP items
    """
    if lot_id:
        return crud.get_by_lot(db, lot_id, skip=skip, limit=limit)
    elif status:
        return crud.get_by_status(db, status.value, skip=skip, limit=limit)
    else:
        return crud.get_multi(db, skip=skip, limit=limit)


@router.get(
    "/{wip_id}",
    response_model=WIPItemInDB,
    summary="Get WIP by ID",
    description="Retrieve a specific WIP item by its ID",
)
def get_wip_item(
    wip_id: int = Path(..., gt=0, description="WIP item identifier"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> WIPItemInDB:
    """Get WIP item by ID."""
    wip_item = crud.get(db, wip_id)
    if not wip_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WIP item with id {wip_id} not found"
        )
    return wip_item


@router.get(
    "/barcode/{wip_id}",
    summary="Generate barcode image",
    description="Generate Code128 barcode image for WIP ID",
)
def get_wip_barcode(
    wip_id: str = Path(..., description="WIP ID (e.g., WIP-KR01PSA2511-001)"),
    barcode_type: str = Query("code128", description="Barcode type (code128 or qr)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Generate barcode image for WIP ID.

    Args:
        wip_id: WIP ID string
        barcode_type: Type of barcode (code128 or qr)
        db: Database session
        current_user: Current authenticated user

    Returns:
        PNG image as StreamingResponse

    Raises:
        HTTPException: 404 if WIP not found, 400 if barcode generation fails
    """
    # Verify WIP exists
    wip_item = crud.get_by_wip_id(db, wip_id)
    if not wip_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WIP {wip_id} not found"
        )

    try:
        # Generate barcode image
        barcode_image = generate_barcode_image(wip_id, barcode_type=barcode_type)

        # Return as streaming response
        return StreamingResponse(
            barcode_image,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=wip_{wip_id}_barcode.png"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate barcode: {str(e)}"
        )


@router.post(
    "/{wip_id}/scan",
    response_model=WIPItemInDB,
    summary="Scan WIP barcode",
    description="Process WIP barcode scan",
)
def scan_wip_barcode(
    wip_id: str = Path(..., description="WIP ID from barcode scan"),
    process_id: Optional[int] = Query(None, description="Process ID for validation"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> WIPItemInDB:
    """
    Process WIP barcode scan.

    Args:
        wip_id: WIP ID from barcode scan
        process_id: Optional process ID for validation
        db: Database session
        current_user: Current authenticated user

    Returns:
        WIP item

    Raises:
        HTTPException: 404 if WIP not found, 400 if validation fails
    """
    try:
        wip_item = crud.scan(db, wip_id, process_id)
        if not wip_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"WIP {wip_id} not found"
            )
        return wip_item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{wip_id}/start-process",
    response_model=WIPItemInDB,
    summary="Start process on WIP",
    description="Start a manufacturing process on WIP item (BR-003)",
)
def start_wip_process(
    wip_id: int = Path(..., gt=0, description="WIP item identifier"),
    process_start: WIPItemProcessStart = ...,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> WIPItemInDB:
    """
    Start a process on WIP item.

    Business Rule BR-003: Process can only start if previous process is PASS
    (except process 1).

    Args:
        wip_id: WIP item identifier
        process_start: Process start data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated WIP item

    Raises:
        HTTPException: 404 if not found, 400 if validation fails
    """
    try:
        wip_item = crud.start_process(
            db,
            wip_id,
            process_start.process_id,
            process_start.operator_id,
            process_start.equipment_id,
            process_start.started_at,
        )
        return wip_item
    except WIPValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{wip_id}/complete-process",
    response_model=dict,
    summary="Complete process on WIP",
    description="Complete a manufacturing process on WIP item (BR-004)",
)
def complete_wip_process(
    wip_id: int = Path(..., gt=0, description="WIP item identifier"),
    process_id: int = Query(..., ge=1, le=6, description="Process identifier (1-6)"),
    operator_id: int = Query(..., gt=0, description="Operator identifier"),
    process_complete: WIPItemProcessComplete = ...,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Complete a process on WIP item.

    Business Rule BR-004: Same process cannot have duplicate PASS results.

    Args:
        wip_id: WIP item identifier
        process_id: Process identifier (1-6)
        operator_id: Operator identifier
        process_complete: Process completion data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Process history record and updated WIP item

    Raises:
        HTTPException: 404 if not found, 400 if validation fails
    """
    try:
        history = crud.complete_process(
            db,
            wip_id,
            process_id,
            operator_id,
            process_complete.result,
            process_complete.measurements,
            process_complete.defects,
            process_complete.notes,
            completed_at=process_complete.completed_at,
        )

        # Get updated WIP item
        wip_item = crud.get(db, wip_id)

        return {
            "process_history": history.to_dict(),
            "wip_item": wip_item.to_dict(),
        }
    except WIPValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{wip_id}/convert-to-serial",
    response_model=dict,
    summary="Convert WIP to serial",
    description="Convert WIP to permanent serial number (BR-005, process 7)",
)
def convert_wip_to_serial(
    wip_id: int = Path(..., gt=0, description="WIP item identifier"),
    convert_data: WIPItemConvert = ...,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Convert WIP to serial number (process 7).

    Business Rule BR-005: All processes 1-6 must have PASS results.

    Args:
        wip_id: WIP item identifier
        convert_data: Conversion data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created serial and updated WIP item

    Raises:
        HTTPException: 404 if not found, 400 if validation fails
    """
    try:
        serial = crud.convert_to_serial(
            db,
            wip_id,
            convert_data.operator_id,
            convert_data.notes,
        )

        # Get updated WIP item
        wip_item = crud.get(db, wip_id)

        return {
            "serial": serial.to_dict(),
            "wip_item": wip_item.to_dict(),
        }
    except WIPValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/statistics",
    response_model=WIPStatistics,
    summary="Get WIP statistics",
    description="Get WIP statistics by LOT or process",
)
def get_wip_statistics(
    lot_id: Optional[int] = Query(None, description="Filter by LOT ID"),
    process_id: Optional[int] = Query(None, description="Filter by process ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> WIPStatistics:
    """
    Get WIP statistics.

    Args:
        lot_id: Optional LOT ID filter
        process_id: Optional process ID filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        WIP statistics
    """
    stats = crud.get_statistics(db, lot_id, process_id)
    return WIPStatistics(**stats)
