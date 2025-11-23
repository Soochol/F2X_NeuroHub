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
from app.services.printer_service import printer_service
from app.models.process import Process
from app.models.process_data import ProcessData, ProcessResult


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
    "/{wip_id}/print-label",
    summary="Print WIP label",
    description="Print WIP label to Zebra printer (60mm x 30mm)",
)
def print_wip_label(
    wip_id: str = Path(..., description="WIP ID (e.g., WIP-KR01PSA2511-001)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Print WIP label to Zebra printer.

    Args:
        wip_id: WIP ID string
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: 404 if WIP not found, 500 if print fails
    """
    # Verify WIP exists
    wip_item = crud.get_by_wip_id(db, wip_id)
    if not wip_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WIP {wip_id} not found"
        )

    try:
        # Print label
        success = printer_service.print_wip_label(wip_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send print job to printer"
            )
        
        return {
            "success": True,
            "message": f"Label for {wip_id} sent to printer",
            "wip_id": wip_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Print failed: {str(e)}"
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
    "/{wip_id}/trace",
    response_model=dict,
    summary="Get WIP traceability",
    description="Get complete traceability information for a WIP item including process history.",
)
def get_wip_trace(
    wip_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get complete traceability information for a WIP item.

    Path Parameters:
        wip_id: WIP identifier

    Returns:
        Complete traceability record
    """
    # Get WIP item
    wip_item = crud.get_by_wip_id(db, wip_id)
    if not wip_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WIP {wip_id} not found"
        )

    # Get LOT information
    lot_info = None
    if wip_item.lot:
        lot_info = {
            "lot_number": wip_item.lot.lot_number,
            "product_model": wip_item.lot.product_model.model_code if wip_item.lot.product_model else None,
            "production_date": wip_item.lot.production_date.isoformat() if wip_item.lot.production_date else None,
            "target_quantity": wip_item.lot.target_quantity,
        }

    # Get all process data for this WIP (ordered by process sequence and timestamp)
    process_data_records = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip_item.id)
        .join(Process, ProcessData.process_id == Process.id)
        .order_by(Process.process_number, ProcessData.created_at)
        .all()
    )

    # Build process history
    process_history = []
    rework_history = []
    total_cycle_time = 0

    for pd in process_data_records:
        process_record = {
            "process_number": pd.process.process_number if pd.process else None,
            "process_code": pd.process.process_code if pd.process else None,
            "process_name": pd.process.process_name_en if pd.process else None,
            "worker_id": pd.operator.username if pd.operator else None,
            "worker_name": pd.operator.full_name if pd.operator else None,
            "started_at": pd.started_at.isoformat() if pd.started_at else None,
            "completed_at": pd.completed_at.isoformat() if pd.completed_at else None,
            "cycle_time_seconds": pd.duration_seconds,
            "duration_seconds": pd.duration_seconds,
            "result": pd.result if pd.result else None,
            "measurements": pd.measurements if pd.measurements else {},
            "defect_codes": pd.defects if pd.defects and pd.result == ProcessResult.FAIL.value else [],
            "defects": pd.defects if pd.defects and pd.result == ProcessResult.FAIL.value else [],
            "notes": pd.notes,
            "is_rework": False # WIP rework logic might differ, assuming false for now or check logic
        }

        process_history.append(process_record)

        # Accumulate cycle time
        if pd.duration_seconds:
            total_cycle_time += pd.duration_seconds

    # Extract component LOTs from process data if available
    component_lots = {}
    for pd in process_data_records:
        if pd.measurements and isinstance(pd.measurements, dict):
            # Look for component tracking fields
            if "busbar_lot" in pd.measurements:
                component_lots["busbar_lot"] = pd.measurements["busbar_lot"]
            if "sma_spring_lot" in pd.measurements:
                component_lots["sma_spring_lot"] = pd.measurements["sma_spring_lot"]
            if "component_lots" in pd.measurements:
                component_lots.update(pd.measurements["component_lots"])

    return {
        "wip_id": wip_item.wip_id,
        "lot_number": wip_item.lot.lot_number if wip_item.lot else None,
        "sequence_in_lot": wip_item.sequence_in_lot,
        "status": wip_item.status,
        "created_at": wip_item.created_at.isoformat(),
        "completed_at": wip_item.completed_at.isoformat() if wip_item.completed_at else None,
        "converted_at": wip_item.converted_at.isoformat() if wip_item.converted_at else None,
        "serial_id": wip_item.serial_id,
        "lot_info": lot_info,
        "process_history": process_history,
        "rework_history": rework_history,
        "component_lots": component_lots,
        "total_cycle_time_seconds": total_cycle_time
    }

