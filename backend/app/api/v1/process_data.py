"""
FastAPI router for ProcessData entity API endpoints.

Provides RESTful API endpoints for managing process execution records in the
F2X NeuroHub Manufacturing Execution System. Implements full CRUD operations
plus specialized filtering endpoints for serial, LOT, process type, result
status, operator, date range, and failure analysis.

Endpoints:
    GET /process-data - List all process data records with pagination
    GET /process-data/{id} - Get process data record by ID
    GET /process-data/serial/{serial_id} - Get all process data for a serial
    GET /process-data/lot/{lot_id} - Get all process data for a LOT
    GET /process-data/process/{process_id} - Filter by process type
    GET /process-data/result/{result} - Filter by PASS/FAIL/REWORK
    GET /process-data/failures - Get failed processes for defect analysis
    GET /process-data/operator/{operator_id} - Filter by operator
    GET /process-data/date-range - Filter by date range (query params)
    GET /process-data/serial/{serial_id}/process/{process_id} - Get specific serial-process record
    GET /process-data/incomplete - Get in-progress processes (completed_at IS NULL)
    POST /process-data - Create new process data record
    PUT /process-data/{id} - Update process data record
    DELETE /process-data/{id} - Delete process data record

Key Features:
    - JSONB fields: measurements, defects
    - Data level: LOT or SERIAL
    - Process sequence enforcement (1→2→3→...→8)
    - Duration auto-calculated
    - Result enum: PASS, FAIL, REWORK
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import User
from app.models.process_data import DataLevel, ProcessResult
from app.schemas.process_data import (
    ProcessDataCreate,
    ProcessDataInDB,
    ProcessDataUpdate,
    MeasurementHistoryItem,
    MeasurementHistoryResponse,
    MeasurementHistoryListResponse,
    MeasurementSummaryResponse,
    ProcessMeasurementSummary,
    MeasurementSpec,
    MeasurementCodeInfo,
    MeasurementCodesResponse,
)
# New exception imports
from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    InvalidDataFormatException,
)

router = APIRouter(
    prefix="/process-data",
    tags=["Process Data"],
)


@router.get(
    "/",
    response_model=List[ProcessDataInDB],
    summary="List all process data records with pagination",
    description="Retrieve a paginated list of all process execution records ordered by creation time (newest first).",
)
def list_process_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    List all process data records with pagination.

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 50, max: 100)

    Returns:
        List of ProcessData objects ordered by creation time (descending)

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_multi(db, skip=skip, limit=limit)
    return process_data_records


@router.get(
    "/{process_data_id}",
    response_model=ProcessDataInDB,
    summary="Get process data record by ID",
    description="Retrieve a specific process execution record by its primary key.",
)
def get_process_data(
    process_data_id: int = Path(..., gt=0, description="Process data record ID"),
    db: Session = Depends(deps.get_db),
):
    """
    Get a single process data record by ID.

    Path Parameters:
        process_data_id: Process data record primary key

    Returns:
        ProcessData object with full details

    Raises:
        HTTPException 404: If process data record not found
    """
    process_data_record = crud.process_data.get(db, process_data_id=process_data_id)
    if not process_data_record:
        raise ResourceNotFoundException("Process data record", process_data_id)
    return process_data_record


@router.get(
    "/serial/{serial_id}",
    response_model=List[ProcessDataInDB],
    summary="Get all process data for a serial",
    description="Retrieve all process execution records for a specific serial with pagination.",
)
def get_process_data_by_serial(
    serial_id: int = Path(..., gt=0, description="Serial ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Get all process data records for a specific serial.

    Path Parameters:
        serial_id: Serial primary key

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects for the serial, ordered by creation time

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_by_serial(
        db, serial_id=serial_id, skip=skip, limit=limit
    )
    return process_data_records


@router.get(
    "/lot/{lot_id}",
    response_model=List[ProcessDataInDB],
    summary="Get all process data for a LOT",
    description="Retrieve all process execution records for a specific LOT with pagination.",
)
def get_process_data_by_lot(
    lot_id: int = Path(..., gt=0, description="LOT ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Get all process data records for a specific LOT.

    Path Parameters:
        lot_id: LOT primary key

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects for the LOT, ordered by creation time

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_by_lot(
        db, lot_id=lot_id, skip=skip, limit=limit
    )
    return process_data_records


@router.get(
    "/process/{process_id}",
    response_model=List[ProcessDataInDB],
    summary="Filter process data by process type",
    description="Retrieve all process execution records for a specific manufacturing process with pagination.",
)
def get_process_data_by_process(
    process_id: int = Path(..., gt=0, description="Process ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Filter process data records by process type.

    Path Parameters:
        process_id: Process primary key (e.g., 1 for LASER_MARKING, 2 for LMA_ASSEMBLY, etc.)

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects for the specified process, ordered by creation time

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_by_process(
        db, process_id=process_id, skip=skip, limit=limit
    )
    return process_data_records


@router.get(
    "/result/{result}",
    response_model=List[ProcessDataInDB],
    summary="Filter process data by result status",
    description="Retrieve process execution records filtered by result (PASS, FAIL, REWORK) with pagination.",
)
def get_process_data_by_result(
    result: str = Path(..., description="Result filter: PASS, FAIL, or REWORK"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Filter process data records by result status.

    Path Parameters:
        result: Result status filter (PASS, FAIL, or REWORK)

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects with specified result, ordered by creation time

    Raises:
        HTTPException 400: If result is not a valid ProcessResult value
        HTTPException 422: If query parameters are invalid
    """
    try:
        process_data_records = crud.process_data.get_by_result(
            db, result=result, skip=skip, limit=limit
        )
        return process_data_records
    except ValueError as e:
        raise ValidationException(message=str(e))


@router.get(
    "/failures",
    response_model=List[ProcessDataInDB],
    summary="Get failed process data for defect analysis",
    description="Retrieve all process execution records with result=FAIL for quality analysis and defect tracking.",
)
def get_failed_process_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Get failed process execution records.

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects with result=FAIL, ordered by creation time (descending)

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_failures(db, skip=skip, limit=limit)
    return process_data_records


@router.get(
    "/operator/{operator_id}",
    response_model=List[ProcessDataInDB],
    summary="Filter process data by operator",
    description="Retrieve all process execution records performed by a specific operator for performance analysis.",
)
def get_process_data_by_operator(
    operator_id: int = Path(..., gt=0, description="Operator (User) ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Filter process data records by operator.

    Path Parameters:
        operator_id: Operator (User) primary key

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects performed by the operator, ordered by creation time

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_by_operator(
        db, operator_id=operator_id, skip=skip, limit=limit
    )
    return process_data_records


@router.get(
    "/date-range",
    response_model=List[ProcessDataInDB],
    summary="Filter process data by date range",
    description="Retrieve process execution records within a specified time window based on started_at timestamp.",
)
def get_process_data_by_date_range(
    start_date: datetime = Query(..., description="Start of date range (inclusive) - ISO 8601 format"),
    end_date: datetime = Query(..., description="End of date range (inclusive) - ISO 8601 format"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Filter process data records by date range.

    Query Parameters:
        start_date: Start of date range (inclusive) - ISO 8601 format (e.g., 2025-01-01T00:00:00Z)
        end_date: End of date range (inclusive) - ISO 8601 format (e.g., 2025-01-31T23:59:59Z)
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects within the date range, ordered by creation time

    Raises:
        HTTPException 422: If query parameters are invalid or date format is incorrect
    """
    if start_date > end_date:
        raise InvalidDataFormatException(
            "start_date",
            "start_date must be before or equal to end_date"
        )

    process_data_records = crud.process_data.get_by_date_range(
        db, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )
    return process_data_records


@router.get(
    "/serial/{serial_id}/process/{process_id}",
    response_model=ProcessDataInDB,
    summary="Get process data for a specific serial-process combination",
    description="Retrieve the process execution record for a specific serial executing a specific process.",
)
def get_process_data_by_serial_and_process(
    serial_id: int = Path(..., gt=0, description="Serial ID"),
    process_id: int = Path(..., gt=0, description="Process ID"),
    db: Session = Depends(deps.get_db),
):
    """
    Get process data for a specific serial-process combination.

    Path Parameters:
        serial_id: Serial primary key
        process_id: Process primary key

    Returns:
        ProcessData object for the serial-process pair

    Raises:
        HTTPException 404: If record not found
    """
    process_data_record = crud.process_data.get_by_serial_and_process(
        db, serial_id=serial_id, process_id=process_id
    )
    if not process_data_record:
        raise ResourceNotFoundException(
            resource_type="ProcessData",
            resource_id=f"serial_id={serial_id}, process_id={process_id}"
        )
    return process_data_record


@router.get(
    "/incomplete",
    response_model=List[ProcessDataInDB],
    summary="Get in-progress processes",
    description="Retrieve process execution records that are not yet completed (completed_at IS NULL) for real-time monitoring.",
)
def get_incomplete_process_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return (max 100)"),
    db: Session = Depends(deps.get_db),
):
    """
    Get in-progress process execution records.

    Query Parameters:
        skip: Offset for pagination (default: 0)
        limit: Number of records to return (default: 100, max: 100)

    Returns:
        List of ProcessData objects with completed_at=NULL, ordered by started_at (ascending)

    Raises:
        HTTPException 422: If query parameters are invalid
    """
    process_data_records = crud.process_data.get_incomplete_processes(
        db, skip=skip, limit=limit
    )
    return process_data_records


@router.post(
    "/",
    response_model=ProcessDataInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new process data record",
    description="Create a new process execution record with validation of data level and serial_id consistency.",
)
def create_process_data(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: ProcessDataCreate,
):
    """
    Create a new process data record.

    Request Body:
        ProcessDataCreate: Process data for creation
            - lot_id: LOT primary key (required, positive integer)
            - serial_id: Serial primary key (required for SERIAL level, NULL for LOT level)
            - process_id: Process primary key (required, positive integer)
            - operator_id: Operator primary key (required, positive integer)
            - data_level: Data granularity level (required: LOT or SERIAL)
            - result: Process result (default: PASS, options: PASS, FAIL, REWORK)
            - measurements: JSONB field with process-specific measurements (default: {})
            - defects: JSONB field with defect information if result=FAIL (optional)
            - started_at: Process execution start timestamp (required, ISO 8601 format)
            - completed_at: Process completion timestamp (optional, ISO 8601 format)
            - notes: Additional comments (optional, max 1000 characters)

    Returns:
        Created ProcessData with auto-generated ID and timestamps

    Raises:
        HTTPException 400: If validation fails (data_level/serial_id mismatch, timestamp order)
        HTTPException 409: If constraint violated (foreign key, sequence, etc.)
        HTTPException 422: If request body is invalid

    Validation:
        - If data_level=SERIAL: serial_id MUST be provided (not NULL)
        - If data_level=LOT: serial_id MUST be NULL
        - completed_at must be >= started_at (if provided)
        - result must be one of: PASS, FAIL, REWORK
        - Process sequence 1→2→3→...→8 is enforced by database trigger
        - Process 7 (Label Printing): Requires ALL processes 1-6 to be PASS
        - Duration is auto-calculated by database trigger

    Example Request:
        POST /api/v1/process-data
        {
            "lot_id": 1,
            "serial_id": 42,
            "process_id": 1,
            "operator_id": 5,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {
                "marking_quality": "GOOD",
                "readability_score": 0.98,
                "laser_power_actual": "19.8W"
            },
            "started_at": "2025-01-18T09:30:00Z",
            "completed_at": "2025-01-18T09:35:00Z",
            "notes": "Good quality marking"
        }
    """
    # Validate data_level and serial_id consistency
    if obj_in.data_level == DataLevel.SERIAL and not obj_in.serial_id:
        raise ValidationException(
            message="serial_id is required when data_level='SERIAL'"
        )
    if obj_in.data_level == DataLevel.LOT and obj_in.serial_id:
        raise ValidationException(
            message="serial_id must be NULL when data_level='LOT'"
        )

    try:
        process_data_record = crud.process_data.create(db, obj_in=obj_in)
        db.commit()
        db.refresh(process_data_record)
        return process_data_record
    except ValueError as e:
        db.rollback()
        raise ValidationException(message=str(e))
    except IntegrityError as e:
        db.rollback()
        error_message = str(e)

        # Parse specific database trigger exceptions for better error messages
        if "Process 7" in error_message and "requires all previous processes" in error_message:
            # BR-007: Process 7 validation failure
            raise BusinessRuleException(
                message="Process 7 (Label Printing) requires all previous processes (1-6) to be PASS. Please ensure all manufacturing processes are completed successfully before label printing."
            )
        elif "Process sequence violation" in error_message:
            # Process sequence violation
            raise BusinessRuleException(
                message=f"Process sequence violation: {error_message}"
            )
        else:
            if "foreign key" in error_message.lower():
                raise ConstraintViolationException(
                    message="Invalid foreign key reference in process data"
                )
            raise DatabaseException(message=f"Failed to create process data record: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.put(
    "/{process_data_id}",
    response_model=ProcessDataInDB,
    summary="Update process data record",
    description="Perform partial update of a process data record. Only provided fields are updated.",
)
def update_process_data(
    process_data_id: int = Path(..., gt=0, description="Process data record ID"),
    obj_in: ProcessDataUpdate = None,
    db: Session = Depends(deps.get_db),
):
    """
    Update an existing process data record.

    Path Parameters:
        process_data_id: Process data record primary key

    Request Body:
        ProcessDataUpdate: Updated fields (all optional for partial updates)
            - result: Updated result (PASS, FAIL, REWORK)
            - measurements: Updated measurements JSONB
            - defects: Updated defects JSONB
            - completed_at: Updated completion timestamp
            - notes: Updated notes

    Returns:
        Updated ProcessData object

    Raises:
        HTTPException 404: If process data record not found
        HTTPException 400: If validation fails
        HTTPException 422: If request body is invalid

    Note:
        - Only incomplete records (completed_at IS NULL) should be updated
        - Completed records (completed_at IS NOT NULL) are typically immutable
        - Duration is auto-calculated by database trigger when completed_at is set
    """
    process_data_record = crud.process_data.get(db, process_data_id=process_data_id)
    if not process_data_record:
        raise ResourceNotFoundException("Process data record", process_data_id)

    try:
        updated_record = crud.process_data.update(
            db, db_obj=process_data_record, obj_in=obj_in
        )
        db.commit()
        db.refresh(updated_record)
        return updated_record
    except ValueError as e:
        db.rollback()
        raise ValidationException(message=str(e))
    except IntegrityError as e:
        db.rollback()
        raise ConstraintViolationException(
            message="Failed to update process data record. Check constraint violations."
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.delete(
    "/{process_data_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete process data record",
    description="Delete a process execution record. Note: Database triggers may prevent deletion of completed records.",
)
def delete_process_data(
    process_data_id: int = Path(..., gt=0, description="Process data record ID"),
    db: Session = Depends(deps.get_db),
):
    """
    Delete a process data record.

    Path Parameters:
        process_data_id: Process data record primary key

    Raises:
        HTTPException 404: If process data record not found
        HTTPException 409: If deletion is prevented by database constraints or triggers

    Note:
        Database constraints enforce:
        - Foreign key references prevent deletion if this record is referenced elsewhere
        - Database triggers may prevent deletion of completed processes for audit integrity
    """
    process_data_record = crud.process_data.get(db, process_data_id=process_data_id)
    if not process_data_record:
        raise ResourceNotFoundException("Process data record", process_data_id)

    try:
        success = crud.process_data.delete(db, process_data_id=process_data_id)
        if success:
            db.commit()
        else:
            raise ResourceNotFoundException("Process data record", process_data_id)
    except IntegrityError as e:
        db.rollback()
        raise ConstraintViolationException(
            message="Failed to delete process data record. Database constraints may prevent deletion."
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(message=f"Failed to delete process data record: {str(e)}")


# =============================================================================
# Measurement History Endpoints
# =============================================================================

def _parse_measurements(measurements_dict: dict) -> list:
    """
    Parse measurements JSONB dict into list of MeasurementHistoryItem.

    Handles two formats:
    1. {"items": [...]} - Standard format from equipment
    2. Direct dict with measurement codes as keys
    """
    if not measurements_dict:
        return []

    items = measurements_dict.get("items", [])
    if items:
        result = []
        for item in items:
            spec_data = item.get("spec")
            spec = None
            if spec_data:
                spec = MeasurementSpec(
                    min=spec_data.get("min"),
                    max=spec_data.get("max"),
                    target=spec_data.get("target")
                )
            result.append(MeasurementHistoryItem(
                code=item.get("code", ""),
                name=item.get("name", ""),
                value=float(item.get("value", 0)),
                unit=item.get("unit"),
                spec=spec,
                result=item.get("result", "PASS")
            ))
        return result

    # Fallback: try to parse as direct key-value pairs
    result = []
    for key, value in measurements_dict.items():
        if key == "items":
            continue
        if isinstance(value, dict):
            spec_data = value.get("spec")
            spec = None
            if spec_data:
                spec = MeasurementSpec(
                    min=spec_data.get("min"),
                    max=spec_data.get("max"),
                    target=spec_data.get("target")
                )
            result.append(MeasurementHistoryItem(
                code=key,
                name=value.get("name", key),
                value=float(value.get("value", 0)),
                unit=value.get("unit"),
                spec=spec,
                result=value.get("result", "PASS")
            ))
        elif isinstance(value, (int, float)):
            result.append(MeasurementHistoryItem(
                code=key,
                name=key,
                value=float(value),
                unit=None,
                spec=None,
                result="PASS"
            ))
    return result


@router.get(
    "/measurements/history",
    response_model=MeasurementHistoryListResponse,
    summary="Get measurement data history",
    description="Retrieve measurement data history with filtering and pagination for quality analysis. Includes both WIP (processes 1-6) and Serial (processes 7-8) data.",
)
def get_measurement_history(
    start_date: Optional[datetime] = Query(None, description="Start date filter (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (inclusive)"),
    process_id: Optional[int] = Query(None, gt=0, description="Filter by process ID"),
    lot_id: Optional[int] = Query(None, gt=0, description="Filter by LOT ID"),
    process_session_id: Optional[int] = Query(None, gt=0, description="Filter by process session (execution session) ID"),
    result: Optional[str] = Query(None, description="Filter by result: PASS, FAIL, or REWORK"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return (max 500)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get measurement data history for quality analysis.

    This endpoint returns measurement data from two sources:
    1. wip_process_history: WIP processes 1-6 (for Serial-converted WIPs only)
    2. process_data: Serial processes 7-8

    Query Parameters:
        start_date: Filter records from this date (inclusive)
        end_date: Filter records up to this date (inclusive)
        process_id: Filter by specific process
        lot_id: Filter by specific LOT
        process_session_id: Filter by specific process session (execution session)
        result: Filter by result status (PASS, FAIL, REWORK)
        skip: Offset for pagination
        limit: Maximum records per page (max 500)

    Returns:
        MeasurementHistoryListResponse with paginated measurement records

    Raises:
        HTTPException 400: If date range is invalid
        HTTPException 422: If query parameters are invalid
    """
    if start_date and end_date and start_date > end_date:
        raise InvalidDataFormatException(
            "start_date",
            "start_date must be before or equal to end_date"
        )

    items = []

    # 1. Get WIP measurements (processes 1-6, Serial-converted WIPs only)
    wip_records, wip_total = crud.process_data.get_wip_measurements(
        db,
        start_date=start_date,
        end_date=end_date,
        process_id=process_id,
        lot_id=lot_id,
        result_filter=result,
        skip=0,  # Get all for now, will sort and paginate combined results
        limit=limit + skip,  # Get enough for pagination
    )

    # Transform WIP records to response format
    for record in wip_records:
        measurements = _parse_measurements(record.measurements)
        wip_item = record.wip_item

        items.append(MeasurementHistoryResponse(
            id=record.id,
            lot_number=wip_item.lot.lot_number if wip_item and wip_item.lot else "",
            wip_id=wip_item.wip_id if wip_item else None,
            serial_number=None,  # WIP doesn't have serial yet (will be linked via wip_item.serial_id)
            process_name=record.process.process_name_ko if record.process else "",
            process_number=record.process.process_number if record.process else 0,
            result=record.result,
            operator_name=record.operator.full_name if record.operator else "",
            measurements=measurements,
            started_at=record.started_at,
            completed_at=record.completed_at,
            duration_seconds=record.duration_seconds,
        ))

    # 2. Get ProcessData measurements (processes 7-8)
    pd_records, pd_total = crud.process_data.get_with_measurements(
        db,
        start_date=start_date,
        end_date=end_date,
        process_id=process_id,
        lot_id=lot_id,
        process_session_id=process_session_id,
        result=result,
        skip=0,
        limit=limit + skip,
    )

    # Transform ProcessData records to response format
    for record in pd_records:
        measurements = _parse_measurements(record.measurements)

        items.append(MeasurementHistoryResponse(
            id=record.id + 1000000,  # Offset ID to avoid collision with WIP IDs
            lot_number=record.lot.lot_number if record.lot else "",
            wip_id=record.wip_item.wip_id if record.wip_item else None,
            serial_number=record.serial.serial_number if record.serial else None,
            process_name=record.process.process_name_ko if record.process else "",
            process_number=record.process.process_number if record.process else 0,
            result=record.result,
            operator_name=record.operator.full_name if record.operator else "",
            measurements=measurements,
            started_at=record.started_at,
            completed_at=record.completed_at,
            duration_seconds=record.duration_seconds,
        ))

    # Sort combined results by completed_at descending
    items.sort(key=lambda x: x.completed_at or datetime.min, reverse=True)

    # Calculate total and apply pagination
    total = wip_total + pd_total
    paginated_items = items[skip:skip + limit]

    return MeasurementHistoryListResponse(
        items=paginated_items,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/measurements/summary",
    response_model=MeasurementSummaryResponse,
    summary="Get measurement data summary statistics",
    description="Get aggregate statistics for measurement data including pass/fail rates and process breakdown. Includes both WIP and Serial data.",
)
def get_measurement_summary(
    start_date: Optional[datetime] = Query(None, description="Start date filter (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (inclusive)"),
    process_id: Optional[int] = Query(None, gt=0, description="Filter by process ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get measurement data summary statistics.

    This endpoint combines data from two sources:
    1. wip_process_history: WIP processes 1-6 (for Serial-converted WIPs only)
    2. process_data: Serial processes 7-8

    Query Parameters:
        start_date: Filter records from this date (inclusive)
        end_date: Filter records up to this date (inclusive)
        process_id: Filter by specific process

    Returns:
        MeasurementSummaryResponse with aggregate statistics

    Raises:
        HTTPException 400: If date range is invalid
        HTTPException 422: If query parameters are invalid
    """
    if start_date and end_date and start_date > end_date:
        raise InvalidDataFormatException(
            "start_date",
            "start_date must be before or equal to end_date"
        )

    # 1. Get WIP measurement summary
    wip_summary = crud.process_data.get_wip_measurement_summary(
        db,
        start_date=start_date,
        end_date=end_date,
        process_id=process_id,
    )

    # 2. Get ProcessData measurement summary
    pd_summary = crud.process_data.get_measurement_summary(
        db,
        start_date=start_date,
        end_date=end_date,
        process_id=process_id,
    )

    # Combine totals
    total_count = wip_summary["total_count"] + pd_summary["total_count"]
    pass_count = wip_summary["pass_count"] + pd_summary["pass_count"]
    fail_count = wip_summary["fail_count"] + pd_summary["fail_count"]
    rework_count = wip_summary["rework_count"] + pd_summary["rework_count"]
    pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0.0

    # Combine by_process (merge entries with same process_id)
    process_map = {}
    for p in wip_summary["by_process"]:
        pid = p["process_id"]
        process_map[pid] = {
            "process_id": pid,
            "process_name": p["process_name"],
            "total": p["total"],
            "fail": p["fail"],
        }
    for p in pd_summary["by_process"]:
        pid = p["process_id"]
        if pid in process_map:
            process_map[pid]["total"] += p["total"]
            process_map[pid]["fail"] += p["fail"]
        else:
            process_map[pid] = {
                "process_id": pid,
                "process_name": p["process_name"],
                "total": p["total"],
                "fail": p["fail"],
            }

    # Calculate rates and transform to schema format
    by_process = []
    for pid in sorted(process_map.keys()):
        p = process_map[pid]
        rate = (p["fail"] / p["total"] * 100) if p["total"] > 0 else 0.0
        by_process.append(ProcessMeasurementSummary(
            process_id=p["process_id"],
            process_name=p["process_name"],
            total=p["total"],
            fail=p["fail"],
            rate=round(rate, 2),
        ))

    return MeasurementSummaryResponse(
        total_count=total_count,
        pass_count=pass_count,
        fail_count=fail_count,
        rework_count=rework_count,
        pass_rate=round(pass_rate, 2),
        by_process=by_process,
    )


@router.get(
    "/measurements/codes",
    response_model=MeasurementCodesResponse,
    summary="Get all unique measurement codes",
    description="Extract all unique measurement codes from the database for dynamic filtering.",
)
def get_measurement_codes(
    process_id: Optional[int] = Query(None, gt=0, description="Filter by process ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get all unique measurement codes from the database.

    This endpoint scans the measurements JSONB field across all process_data records
    and extracts unique measurement codes for dynamic filtering in the frontend.

    Query Parameters:
        process_id: Optional filter to get codes only from a specific process

    Returns:
        MeasurementCodesResponse with list of unique measurement codes and their metadata
    """
    codes = crud.process_data.get_measurement_codes(db, process_id=process_id)

    code_infos = [
        MeasurementCodeInfo(
            code=c["code"],
            name=c["name"],
            unit=c.get("unit"),
            count=c["count"],
            process_ids=c.get("process_ids", []),
        )
        for c in codes
    ]

    return MeasurementCodesResponse(
        codes=code_infos,
        total_codes=len(code_infos),
    )
