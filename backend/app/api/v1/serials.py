"""
FastAPI router for Serial entity API endpoints.

Provides RESTful API endpoints for managing serials (individual product units)
within production lots. Implements full CRUD operations plus specialized endpoints
for status management, rework handling, and filtering by lot/status.

Endpoints:
    GET /serials - List all serials with pagination
    GET /serials/{id} - Get serial by ID
    GET /serials/number/{serial_number} - Get serial by serial number
    GET /serials/lot/{lot_id} - Get all serials in a lot
    GET /serials/status/{status} - Filter serials by status
    GET /serials/failed - Get failed serials available for rework
    GET /serials/{id}/can-rework - Check if serial can be reworked
    POST /serials - Create new serial
    PUT /serials/{id} - Update serial
    PUT /serials/{id}/status - Update serial status
    POST /serials/{id}/rework - Start rework process
    DELETE /serials/{id} - Delete serial

State Machine:
    CREATED → IN_PROGRESS → PASSED (terminal)
                         → FAILED → IN_PROGRESS (rework, max 3x) → PASSED/FAILED
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models.serial import SerialStatus
from app.schemas.serial import SerialCreate, SerialInDB, SerialUpdate

router = APIRouter(
    prefix="/serials",
    tags=["Serials"],
)


@router.get(
    "/",
    response_model=List[SerialInDB],
    summary="List all serials with pagination",
    description="Retrieve a paginated list of all serials with optional status filtering.",
)
def list_serials(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return (max 100)"),
    status: Optional[str] = Query(None, description="Filter by status: CREATED, IN_PROGRESS, PASSED, FAILED"),
    db: Session = Depends(get_db),
):
    """
    List all serials with optional filtering and pagination.

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of serials to return (default: 50, max: 100)
        status: Optional filter for serial status

    Returns:
        List of Serial objects

    Raises:
        HTTPException 400: If status filter is invalid
        HTTPException 422: If query parameters are invalid
    """
    try:
        serials = crud.serial.get_multi(db, skip=skip, limit=limit, status=status)
        return serials
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{serial_id}",
    response_model=SerialInDB,
    summary="Get serial by ID",
    description="Retrieve a specific serial by its primary key.",
)
def get_serial(
    serial_id: int = Query(..., gt=0, description="Serial ID"),
    db: Session = Depends(get_db),
):
    """
    Get a single serial by ID.

    Path Parameters:
        serial_id: Serial primary key

    Returns:
        Serial object with full details

    Raises:
        HTTPException 404: If serial not found
    """
    serial = crud.serial.get(db, serial_id=serial_id)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")
    return serial


@router.get(
    "/number/{serial_number}",
    response_model=SerialInDB,
    summary="Get serial by serial number",
    description="Retrieve a serial by its unique serial number (e.g., WF-KR-251110D-001-0001).",
)
def get_serial_by_number(
    serial_number: str = Query(..., min_length=1, description="Serial number (format: {LOT_NUMBER}-XXXX)"),
    db: Session = Depends(get_db),
):
    """
    Get serial by unique serial number.

    Path Parameters:
        serial_number: Unique serial identifier in format {LOT_NUMBER}-XXXX

    Returns:
        Serial object with full details

    Raises:
        HTTPException 404: If serial not found
    """
    serial = crud.serial.get_by_number(db, serial_number=serial_number)
    if not serial:
        raise HTTPException(
            status_code=404,
            detail=f"Serial with number '{serial_number}' not found"
        )
    return serial


@router.get(
    "/lot/{lot_id}",
    response_model=List[SerialInDB],
    summary="Get serials by lot",
    description="Retrieve all serials in a specific lot with pagination.",
)
def get_serials_by_lot(
    lot_id: int = Query(..., gt=0, description="Lot ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(get_db),
):
    """
    Get all serials in a specific lot.

    Path Parameters:
        lot_id: ID of the lot

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of serials to return (default: 100, max: 100)

    Returns:
        List of Serial objects in the lot, ordered by sequence

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    serials = crud.serial.get_by_lot(db, lot_id=lot_id, skip=skip, limit=limit)
    return serials


@router.get(
    "/status/{status_filter}",
    response_model=List[SerialInDB],
    summary="Filter serials by status",
    description="Retrieve serials filtered by lifecycle status with pagination.",
)
def get_serials_by_status(
    status_filter: str = Query(..., description="Status filter: CREATED, IN_PROGRESS, PASSED, FAILED"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(get_db),
):
    """
    Get serials filtered by status with pagination.

    Path Parameters:
        status_filter: Serial status (CREATED, IN_PROGRESS, PASSED, FAILED)

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of serials to return (default: 50, max: 100)

    Returns:
        List of Serial objects with specified status

    Raises:
        HTTPException 400: If status is invalid
        HTTPException 422: If query parameters are invalid
    """
    try:
        serials = crud.serial.get_by_status(db, status=status_filter, skip=skip, limit=limit)
        return serials
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/failed",
    response_model=List[SerialInDB],
    summary="Get failed serials available for rework",
    description="Retrieve FAILED serials that have not exceeded maximum rework attempts (count < 3).",
)
def get_failed_serials(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(get_db),
):
    """
    Get FAILED serials available for rework.

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of serials to return (default: 50, max: 100)

    Returns:
        List of FAILED Serial objects with rework_count < 3

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    serials = crud.serial.get_failed(db, skip=skip, limit=limit)
    return serials


@router.post(
    "/",
    response_model=SerialInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new serial",
    description="Create a new serial within a lot. Serial number is auto-generated.",
)
def create_serial(
    serial_in: SerialCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new serial.

    Request Body:
        SerialCreate: Serial data for creation
            - lot_id: Parent lot ID (required, positive integer)
            - sequence_in_lot: Sequence position (required, 1-100)
            - status: Initial status (optional, default: CREATED)
            - rework_count: Initial rework count (optional, default: 0)
            - failure_reason: Failure reason (optional, only for FAILED status)

    Returns:
        Created Serial with auto-generated ID, serial_number, and timestamps

    Raises:
        HTTPException 400: If validation fails or lot_id invalid
        HTTPException 409: If unique constraint violated
        HTTPException 422: If request body is invalid
    """
    try:
        serial = crud.serial.create(db, serial_in=serial_in)
        return serial
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=409, detail="Failed to create serial. Lot may not exist or unique constraint violated.")


@router.put(
    "/{serial_id}",
    response_model=SerialInDB,
    summary="Update serial",
    description="Perform partial update of a serial. Only provided fields are updated.",
)
def update_serial(
    serial_id: int = Query(..., gt=0, description="Serial ID"),
    serial_in: SerialUpdate = None,
    db: Session = Depends(get_db),
):
    """
    Update an existing serial.

    Path Parameters:
        serial_id: Serial primary key

    Request Body:
        SerialUpdate: Updated serial fields (all optional)
            - status: Updated status
            - rework_count: Updated rework count
            - failure_reason: Updated failure reason

    Returns:
        Updated Serial object

    Raises:
        HTTPException 404: If serial not found
        HTTPException 400: If validation fails
        HTTPException 422: If request body is invalid
    """
    serial = crud.serial.get(db, serial_id=serial_id)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")

    try:
        updated_serial = crud.serial.update(db, serial_id=serial_id, serial_in=serial_in)
        return updated_serial
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{serial_id}/status",
    response_model=SerialInDB,
    summary="Update serial status",
    description="Update serial status with state machine validation and failure reason handling.",
)
def update_serial_status(
    serial_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
):
    """
    Update serial status with validation and failure reason support.

    Path Parameters:
        serial_id: Serial primary key

    Request Body:
        {
            "status": "PASSED" or "FAILED" or "IN_PROGRESS" or "CREATED",
            "failure_reason": "Optional failure reason (required if status=FAILED)"
        }

    Returns:
        Updated Serial with new status and completed_at timestamp (if reaching terminal state)

    Raises:
        HTTPException 404: If serial not found
        HTTPException 400: If status transition invalid or constraints violated
        HTTPException 422: If request body is invalid

    State Machine Rules:
        - CREATED → IN_PROGRESS (allowed)
        - IN_PROGRESS → PASSED or FAILED (allowed)
        - FAILED → IN_PROGRESS (allowed, max 3 times)
        - PASSED is final (no transitions allowed)
    """
    serial = crud.serial.get(db, serial_id=serial_id)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")

    status_value = status_update.get("status")
    failure_reason = status_update.get("failure_reason")

    if not status_value:
        raise HTTPException(status_code=400, detail="status field is required")

    try:
        updated_serial = crud.serial.update_status(
            db,
            serial_id=serial_id,
            status=status_value,
            failure_reason=failure_reason
        )
        return updated_serial
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{serial_id}/rework",
    response_model=SerialInDB,
    summary="Start rework process",
    description="Increment rework count and reset status to IN_PROGRESS for a FAILED serial.",
)
def rework_serial(
    serial_id: int,
    db: Session = Depends(get_db),
):
    """
    Start rework process for a FAILED serial.

    Path Parameters:
        serial_id: Serial primary key

    Returns:
        Updated Serial with incremented rework_count and IN_PROGRESS status

    Raises:
        HTTPException 404: If serial not found
        HTTPException 400: If serial cannot be reworked (not FAILED or max attempts exceeded)
        HTTPException 422: If path parameters are invalid

    Rework Rules:
        - Serial must be in FAILED status
        - Maximum 3 rework attempts allowed
        - Each rework resets status to IN_PROGRESS
        - After 3 failed reworks, serial is permanently failed
    """
    serial = crud.serial.get(db, serial_id=serial_id)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")

    if not crud.serial.can_rework(db, serial_id=serial_id):
        if serial.status != SerialStatus.FAILED:
            raise HTTPException(
                status_code=400,
                detail=f"Serial is not in FAILED status (current: {serial.status.value}). Cannot start rework."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum rework count (3) exceeded for serial {serial.serial_number}"
            )

    try:
        updated_serial = crud.serial.increment_rework(db, serial_id=serial_id)
        return updated_serial
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{serial_id}/can-rework",
    response_model=dict,
    summary="Check if serial can be reworked",
    description="Determine if a serial is eligible for rework based on status and rework count.",
)
def check_can_rework(
    serial_id: int,
    db: Session = Depends(get_db),
):
    """
    Check if a serial is eligible for rework.

    Path Parameters:
        serial_id: Serial primary key

    Returns:
        {
            "can_rework": boolean,
            "reason": string explaining why or why not,
            "rework_count": current rework count,
            "status": current status
        }

    Raises:
        HTTPException 404: If serial not found
        HTTPException 422: If path parameters are invalid

    Eligibility Rules:
        - Serial must be in FAILED status
        - Rework count must be less than 3
    """
    serial = crud.serial.get(db, serial_id=serial_id)
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")

    can_rework = crud.serial.can_rework(db, serial_id=serial_id)

    if can_rework:
        reason = f"Serial eligible for rework. Current rework count: {serial.rework_count}/3"
    else:
        if serial.status != SerialStatus.FAILED:
            reason = f"Serial is in {serial.status.value} status, not FAILED. Cannot rework."
        else:
            reason = f"Serial has exhausted maximum rework count (3/3)"

    return {
        "can_rework": can_rework,
        "reason": reason,
        "rework_count": serial.rework_count,
        "status": serial.status.value,
    }


@router.delete(
    "/{serial_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete serial",
    description="Delete a serial and its associated process data records.",
)
def delete_serial(
    serial_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a serial.

    Path Parameters:
        serial_id: Serial primary key

    Returns:
        204 No Content on successful deletion

    Raises:
        HTTPException 404: If serial not found
        HTTPException 409: If deletion violates constraints
        HTTPException 422: If path parameters are invalid

    Notes:
        - Deletion cascades to associated ProcessData records
        - Cannot delete serials with active dependencies (if enforced by DB constraints)
    """
    deleted = crud.serial.delete(db, serial_id=serial_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Serial not found")
    return None
