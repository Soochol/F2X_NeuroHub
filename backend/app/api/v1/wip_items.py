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

from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.core.deps import StationAuth, get_auth_context
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
    WIPScanResponse,
)
from app.utils.barcode_generator import generate_barcode_image
from app.services.wip_service import WIPValidationError
from app.services.printer_service import printer_service
from app.models.process import Process
from app.models.process_data import ProcessData, ProcessResult
from app.models.wip_process_history import WIPProcessHistory
from app.core.exceptions import (
    WIPItemNotFoundException,
    ValidationException,
    BusinessRuleException,
    InternalServerException,
)


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
        raise WIPItemNotFoundException(wip_id=wip_id)
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
        raise WIPItemNotFoundException(wip_id=wip_id)

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
        raise ValidationException(message=f"Failed to generate barcode: {str(e)}")


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
        raise WIPItemNotFoundException(wip_id=wip_id)

    try:
        # Print label
        result = printer_service.print_wip_label(wip_id, db=db, operator_id=current_user.id)

        if not result.get("success", False):
            raise InternalServerException(message=result.get("message", "Failed to send print job to printer"))

        return {
            "success": True,
            "message": f"Label for {wip_id} sent to printer",
            "wip_id": wip_id
        }
    except InternalServerException:
        raise
    except Exception as e:
        raise InternalServerException(message=f"Print failed: {str(e)}")



@router.post(
    "/{wip_id}/scan",
    response_model=WIPScanResponse,
    summary="Scan WIP barcode",
    description="Process WIP barcode scan. Supports both JWT and API Key authentication.",
)
def scan_wip_barcode(
    wip_id: str = Path(..., description="WIP ID from barcode scan"),
    process_id: Optional[int] = Query(None, description="Process ID for validation"),
    db: Session = Depends(deps.get_db),
    auth: Union[User, StationAuth] = Depends(get_auth_context),
) -> WIPScanResponse:
    """
    Process WIP barcode scan.

    Supports hybrid authentication:
    - JWT Bearer token (user authentication)
    - X-API-Key header (station authentication)

    Args:
        wip_id: WIP ID from barcode scan
        process_id: Optional process ID for validation
        db: Database session
        auth: Authentication context (User or StationAuth)

    Returns:
        WIP item with process validation info (has_pass_for_process)

    Raises:
        HTTPException: 404 if WIP not found, 400 if validation fails
    """
    try:
        wip_item = crud.scan(db, wip_id, process_id)
        if not wip_item:
            raise WIPItemNotFoundException(wip_id=wip_id)

        # Check if WIP already has COMPLETED PASS for the requested process (BR-004 pre-check)
        # Only check for PASS records that have completed_at set (truly completed)
        has_pass = False
        warning_msg = None
        if process_id:
            existing_pass = db.query(WIPProcessHistory).filter(
                WIPProcessHistory.wip_item_id == wip_item.id,
                WIPProcessHistory.process_id == process_id,
                WIPProcessHistory.result == ProcessResult.PASS.value,
                WIPProcessHistory.completed_at.isnot(None),  # Must be completed
            ).first()
            if existing_pass:
                has_pass = True
                process = db.query(Process).filter(Process.id == process_id).first()
                process_name = process.process_name_ko if process else f"공정 {process_id}"
                warning_msg = f"이 WIP는 이미 '{process_name}'을 PASS했습니다. 다시 실행하면 완공 시 에러가 발생합니다."

        # Convert to response with additional fields
        response = WIPScanResponse.model_validate(wip_item)
        response.has_pass_for_process = has_pass
        response.pass_warning_message = warning_msg
        return response
    except ValueError as e:
        raise ValidationException(message=str(e))


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
            process_start.process_session_id,
        )
        return wip_item
    except WIPValidationError as e:
        raise BusinessRuleException(message=str(e))
    except ValueError as e:
        raise WIPItemNotFoundException(wip_id=wip_id)


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
            started_at=process_complete.started_at,
            completed_at=process_complete.completed_at,
        )

        # Get updated WIP item
        wip_item = crud.get(db, wip_id)

        return {
            "process_history": history.to_dict(),
            "wip_item": wip_item.to_dict(),
        }
    except WIPValidationError as e:
        raise BusinessRuleException(message=str(e))
    except ValueError as e:
        raise WIPItemNotFoundException(wip_id=wip_id)


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
        raise BusinessRuleException(message=str(e))
    except ValueError as e:
        raise WIPItemNotFoundException(wip_id=wip_id)





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
        raise WIPItemNotFoundException(wip_id=wip_id)

    # Get LOT information
    lot_info = None
    if wip_item.lot:
        lot_info = {
            "lot_number": wip_item.lot.lot_number,
            "product_model": wip_item.lot.product_model.model_code if wip_item.lot.product_model else None,
            "production_date": wip_item.lot.production_date.isoformat() if wip_item.lot.production_date else None,
            "target_quantity": wip_item.lot.target_quantity,
        }

    # Get all WIP process history records (ordered by process sequence and timestamp)
    # Note: WIPProcessHistory stores 완공 records, ProcessData stores 착공 records
    wip_history_records = (
        db.query(WIPProcessHistory)
        .filter(WIPProcessHistory.wip_item_id == wip_item.id)
        .join(Process, WIPProcessHistory.process_id == Process.id)
        .order_by(Process.process_number, WIPProcessHistory.created_at)
        .all()
    )

    # Also get ProcessData records for in-progress (착공 only, not yet 완공)
    # These are processes that have been started but not yet completed
    process_data_records = (
        db.query(ProcessData)
        .filter(
            ProcessData.wip_id == wip_item.id,
            ProcessData.completed_at.is_(None)  # Only in-progress records
        )
        .join(Process, ProcessData.process_id == Process.id)
        .order_by(Process.process_number, ProcessData.started_at)
        .all()
    )

    # Build process history
    process_history = []
    rework_history = []
    total_cycle_time = 0

    # Track which processes we've already added from WIPProcessHistory
    added_process_ids = set()

    for ph in wip_history_records:
        process_record = {
            "process_number": ph.process.process_number if ph.process else None,
            "process_code": ph.process.process_code if ph.process else None,
            "process_name": ph.process.process_name_en if ph.process else None,
            "worker_id": ph.operator.username if ph.operator else None,
            "worker_name": ph.operator.full_name if ph.operator else None,
            "start_time": ph.started_at.isoformat() if ph.started_at else None,
            "complete_time": ph.completed_at.isoformat() if ph.completed_at else None,
            "cycle_time_seconds": ph.duration_seconds,
            "duration_seconds": ph.duration_seconds,
            "result": ph.result if ph.result else None,
            "measurements": ph.measurements if ph.measurements else {},
            "defect_codes": ph.defects if ph.defects and ph.result == "FAIL" else [],
            "defects": ph.defects if ph.defects and ph.result == "FAIL" else [],
            "notes": ph.notes,
            "is_rework": ph.result == "REWORK" if ph.result else False
        }

        process_history.append(process_record)
        added_process_ids.add(ph.process_id)

        # Accumulate cycle time
        if ph.duration_seconds:
            total_cycle_time += ph.duration_seconds

    # Add in-progress records from ProcessData (착공 only, not yet completed)
    # Note: Always add these records even if there's a completed record for the same process_id
    # This supports rework scenarios where a FAIL was recorded and a new 착공 started
    for pd in process_data_records:
        # Check if this is a rework (same process has a completed record)
        is_rework = pd.process_id in added_process_ids

        process_record = {
            "process_number": pd.process.process_number if pd.process else None,
            "process_code": pd.process.process_code if pd.process else None,
            "process_name": pd.process.process_name_en if pd.process else None,
            "worker_id": pd.operator.username if pd.operator else None,
            "worker_name": pd.operator.full_name if pd.operator else None,
            "start_time": pd.started_at.isoformat() if pd.started_at else None,
            "complete_time": None,  # Not completed yet
            "cycle_time_seconds": None,
            "duration_seconds": None,
            "result": None,  # In progress, no result yet
            "measurements": {},
            "defect_codes": [],
            "defects": [],
            "notes": None,
            "is_rework": is_rework
        }
        process_history.append(process_record)

    # Sort process_history by process_number
    process_history.sort(key=lambda x: (x["process_number"] or 0, x["start_time"] or ""))

    # Extract component LOTs from process history if available
    component_lots = {}
    for ph in wip_history_records:
        if ph.measurements and isinstance(ph.measurements, dict):
            # Look for component tracking fields
            if "busbar_lot" in ph.measurements:
                component_lots["busbar_lot"] = ph.measurements["busbar_lot"]
            if "sma_spring_lot" in ph.measurements:
                component_lots["sma_spring_lot"] = ph.measurements["sma_spring_lot"]
            if "component_lots" in ph.measurements:
                component_lots.update(ph.measurements["component_lots"])

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

