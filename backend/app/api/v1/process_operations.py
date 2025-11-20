"""
Process Operations API endpoints for manufacturing workflow.

Provides operational endpoints for:
    - Process start (착공 등록)
    - Process complete (완공 등록)
    - Process history (공정 이력 조회)

These endpoints are separate from the CRUD operations in processes.py
and handle the actual manufacturing workflow operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import deps
from app import crud
from app.core.exceptions import (
    LotNotFoundException,
    SerialNotFoundException,
    ProcessNotFoundException,
    UserNotFoundException,
    DuplicateResourceException,
    ConstraintViolationException,
    ValidationException,
    BusinessRuleException,
    DatabaseException,
)
from app.models import (
    User,
    Lot,
    Serial,
    Process,
    ProcessData,
    SerialStatus,
    LotStatus,
    Equipment,
    ProductionLine,
)
from app.schemas.process_data import ProcessDataCreate, ProcessDataInDB, DataLevel, ProcessResult


router = APIRouter()


# Request/Response schemas for process operations

class ProcessStartRequest(BaseModel):
    """Request schema for starting a process (착공 등록)."""
    lot_number: str = Field(..., description="LOT number (e.g., WF-KR-251110D-001)")
    serial_number: Optional[str] = Field(None, description="Serial number (optional for LOT-level)")
    process_id: str = Field(..., description="Process ID (e.g., PROC-001 or 1)")
    worker_id: str = Field(..., description="Worker ID (e.g., W001)")
    equipment_id: Optional[str] = Field(None, description="Equipment ID (e.g., EQ-001)")
    # Additional fields from PySide app
    line_id: Optional[str] = Field(None, description="Production line ID")
    process_name: Optional[str] = Field(None, description="Process name")
    start_time: Optional[str] = Field(None, description="Start time ISO format")


class ProcessStartResponse(BaseModel):
    """Response schema for process start."""
    success: bool
    message: str
    process_data_id: int
    started_at: datetime


class ProcessCompleteRequest(BaseModel):
    """Request schema for completing a process (완공 등록)."""
    lot_number: str = Field(..., description="LOT number")
    serial_number: Optional[str] = Field(None, description="Serial number")
    process_id: int = Field(..., gt=0, description="Process ID")
    result: str = Field(..., description="Result: PASS, FAIL, or REWORK")
    measurement_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Measurement data"
    )
    defect_data: Optional[Dict[str, Any]] = Field(
        None, description="Defect information if result=FAIL"
    )


class ProcessCompleteResponse(BaseModel):
    """Response schema for process complete."""
    success: bool
    message: str
    process_data_id: int
    completed_at: datetime
    duration_seconds: int


class ProcessHistoryItem(BaseModel):
    """Schema for a single process history item."""
    process_number: int
    process_name: str
    result: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    operator_name: Optional[str]
    measurements: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ProcessHistoryResponse(BaseModel):
    """Response schema for process history."""
    serial_number: str
    lot_number: str
    total_processes: int
    completed_processes: int
    history: List[ProcessHistoryItem]


@router.post(
    "/start",
    response_model=ProcessStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="착공 등록",
    description="Start a new process for a LOT/Serial. Validates process sequence and previous process completion.",
)
def start_process(
    request: ProcessStartRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessStartResponse:
    """
    Register process start (착공 등록).

    **Validation Rules:**
    - LOT must exist and be active (CREATED or IN_PROGRESS)
    - Serial must exist (if serial_number provided)
    - Process sequence: Previous process must be PASS (except process 1)
    - Process 7 (Label Printing): Requires ALL processes 1-6 to be PASS

    **Request Body:**
    ```json
    {
        "lot_number": "WF-KR-251110D-001",
        "serial_number": "WF-KR-251110D-001-0001",
        "process_id": 1,
        "worker_id": "W001",
        "equipment_id": "EQ-001"
    }
    ```

    **Error Responses:**
    - 400: Invalid process sequence or validation failure
    - 404: LOT, Serial, or Process not found
    - 409: Process already started (duplicate)
    """
    # Find LOT by number
    lot = db.query(Lot).filter(Lot.lot_number == request.lot_number).first()
    if not lot:
        raise LotNotFoundException(lot_number=request.lot_number)

    # Check LOT status
    if lot.status not in [LotStatus.CREATED, LotStatus.IN_PROGRESS]:
        raise ValidationException(
            message=f"LOT is not active. Current status: {lot.status}"
        )

    # Find Process - handle both "PROC-001" format and numeric ID
    process = None
    process_id_str = request.process_id

    if process_id_str.startswith("PROC-"):
        # Format: PROC-001 -> process_number 1
        try:
            proc_num = int(process_id_str.replace("PROC-", ""))
            process = db.query(Process).filter(
                Process.process_number == proc_num
            ).first()
        except ValueError:
            pass
    else:
        # Try as numeric ID
        try:
            proc_id = int(process_id_str)
            process = db.query(Process).filter(Process.id == proc_id).first()
            if not process:
                # Try as process_number
                process = db.query(Process).filter(
                    Process.process_number == proc_id
                ).first()
        except ValueError:
            pass

    if not process:
        raise ProcessNotFoundException(process_id=request.process_id)

    # Determine data level and serial
    serial = None
    data_level = DataLevel.LOT
    serial_id = None

    if request.serial_number:
        serial = db.query(Serial).filter(
            Serial.serial_number == request.serial_number,
            Serial.lot_id == lot.id
        ).first()
        if not serial:
            raise SerialNotFoundException(request.serial_number)
        data_level = DataLevel.SERIAL
        serial_id = serial.id

    # Find operator by worker_id (username)
    operator = db.query(User).filter(User.username == request.worker_id).first()
    if not operator:
        # Try to find by ID if it's numeric
        try:
            operator_id = int(request.worker_id.replace("W", ""))
            operator = db.query(User).filter(User.id == operator_id).first()
        except (ValueError, AttributeError):
            pass

    if not operator:
        raise UserNotFoundException(user_id=request.worker_id)

    # Find equipment by equipment_id (equipment_code)
    equipment = None
    equipment_id = None
    if request.equipment_id:
        equipment = db.query(Equipment).filter(
            Equipment.equipment_code == request.equipment_id
        ).first()
        if equipment:
            equipment_id = equipment.id

    # Find production line by line_id (line_code) and update LOT
    if request.line_id:
        production_line = db.query(ProductionLine).filter(
            ProductionLine.line_code == request.line_id
        ).first()
        if production_line and not lot.production_line_id:
            # Assign production line to LOT on first 착공
            lot.production_line_id = production_line.id

    # Validate process sequence
    process_number = process.process_number

    if process_number > 1:
        # Check if previous process is completed with PASS
        prev_process = db.query(Process).filter(
            Process.process_number == process_number - 1
        ).first()

        if prev_process:
            prev_data_query = db.query(ProcessData).filter(
                ProcessData.lot_id == lot.id,
                ProcessData.process_id == prev_process.id,
                ProcessData.result == ProcessResult.PASS
            )

            if serial_id:
                prev_data_query = prev_data_query.filter(
                    ProcessData.serial_id == serial_id
                )

            prev_data = prev_data_query.first()

            if not prev_data:
                raise BusinessRuleException(
                    message=f"Previous process (Process {process_number - 1}) must be completed with PASS before starting Process {process_number}"
                )

    # Special validation for Process 7 (Label Printing)
    if process_number == 7:
        # Check all processes 1-6 are PASS
        for prev_num in range(1, 7):
            prev_proc = db.query(Process).filter(
                Process.process_number == prev_num
            ).first()

            if prev_proc:
                prev_data_query = db.query(ProcessData).filter(
                    ProcessData.lot_id == lot.id,
                    ProcessData.process_id == prev_proc.id,
                    ProcessData.result == ProcessResult.PASS
                )

                if serial_id:
                    prev_data_query = prev_data_query.filter(
                        ProcessData.serial_id == serial_id
                    )

                if not prev_data_query.first():
                    # Count how many processes are PASS
                    pass_count = 0
                    for check_num in range(1, 7):
                        check_proc = db.query(Process).filter(
                            Process.process_number == check_num
                        ).first()
                        if check_proc:
                            check_query = db.query(ProcessData).filter(
                                ProcessData.lot_id == lot.id,
                                ProcessData.process_id == check_proc.id,
                                ProcessData.result == ProcessResult.PASS
                            )
                            if serial_id:
                                check_query = check_query.filter(
                                    ProcessData.serial_id == serial_id
                                )
                            if check_query.first():
                                pass_count += 1

                    raise BusinessRuleException(
                        message=f"Process 7 requires all previous processes (1-6) to be PASS. Current PASS count: {pass_count}"
                    )

    # Check for duplicate start (already in progress)
    existing = db.query(ProcessData).filter(
        ProcessData.lot_id == lot.id,
        ProcessData.process_id == process.id,
        ProcessData.completed_at.is_(None)
    )
    if serial_id:
        existing = existing.filter(ProcessData.serial_id == serial_id)

    if existing.first():
        raise DuplicateResourceException(
            resource_type="ProcessData",
            identifier=f"Process {process_number} for LOT/Serial"
        )

    # Create process data record
    # Use provided start_time or current time
    if request.start_time:
        try:
            started_at = datetime.fromisoformat(
                request.start_time.replace('Z', '+00:00')
            )
        except ValueError:
            started_at = datetime.utcnow()
    else:
        started_at = datetime.utcnow()

    process_data_create = ProcessDataCreate(
        lot_id=lot.id,
        serial_id=serial_id,
        process_id=process.id,
        operator_id=operator.id,
        equipment_id=equipment_id,
        data_level=data_level,
        result=ProcessResult.PASS,  # Default, will be updated on complete
        measurements={},
        started_at=started_at,
        completed_at=None,
    )

    try:
        process_data = crud.process_data.create(db, obj_in=process_data_create)
        db.commit()
        db.refresh(process_data)

        # Update LOT status to IN_PROGRESS if it was CREATED
        if lot.status == LotStatus.CREATED:
            lot.status = LotStatus.IN_PROGRESS
            db.commit()

        return ProcessStartResponse(
            success=True,
            message=f"Process {process_number} ({process.process_name_ko}) started successfully",
            process_data_id=process_data.id,
            started_at=started_at,
        )

    except IntegrityError as e:
        db.rollback()
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(
                resource_type="ProcessData",
                identifier=f"lot_id={lot.id}, process_id={process.id}"
            )
        if "foreign key" in error_str:
            raise ConstraintViolationException(
                message="Invalid foreign key reference in process data"
            )
        raise DatabaseException(message=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.post(
    "/complete",
    response_model=ProcessCompleteResponse,
    summary="완공 등록",
    description="Complete a process with result and measurement data.",
)
def complete_process(
    request: ProcessCompleteRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessCompleteResponse:
    """
    Register process completion (완공 등록).

    **Request Body:**
    ```json
    {
        "lot_number": "WF-KR-251110D-001",
        "serial_number": "WF-KR-251110D-001-0001",
        "process_id": 1,
        "result": "PASS",
        "measurement_data": {
            "temperature": 25.5,
            "humidity": 60
        }
    }
    ```

    **Error Responses:**
    - 400: Invalid result or validation failure
    - 404: Process data not found (not started)
    """
    # Find LOT
    lot = db.query(Lot).filter(Lot.lot_number == request.lot_number).first()
    if not lot:
        raise LotNotFoundException(lot_number=request.lot_number)

    # Find in-progress process data
    query = db.query(ProcessData).filter(
        ProcessData.lot_id == lot.id,
        ProcessData.process_id == request.process_id,
        ProcessData.completed_at.is_(None)
    )

    if request.serial_number:
        serial = db.query(Serial).filter(
            Serial.serial_number == request.serial_number,
            Serial.lot_id == lot.id
        ).first()
        if serial:
            query = query.filter(ProcessData.serial_id == serial.id)

    process_data = query.first()

    if not process_data:
        raise ValidationException(
            message=f"No in-progress process found for process_id {request.process_id}. Did you start the process first?"
        )

    # Validate result
    try:
        result = ProcessResult(request.result.upper())
    except ValueError:
        raise ValidationException(
            message=f"Invalid result. Must be one of: PASS, FAIL, REWORK"
        )

    # Update process data
    completed_at = datetime.utcnow()
    process_data.result = result
    process_data.completed_at = completed_at
    process_data.measurements = request.measurement_data or {}

    if request.defect_data and result == ProcessResult.FAIL:
        process_data.defects = request.defect_data

    # Calculate duration
    duration_seconds = int((completed_at - process_data.started_at).total_seconds())
    process_data.duration_seconds = duration_seconds

    try:
        db.commit()
        db.refresh(process_data)

        # Update serial status if FAIL
        if result == ProcessResult.FAIL and process_data.serial_id:
            serial = db.query(Serial).filter(Serial.id == process_data.serial_id).first()
            if serial:
                serial.status = SerialStatus.FAILED
                db.commit()

        return ProcessCompleteResponse(
            success=True,
            message=f"Process completed with result: {result.value}",
            process_data_id=process_data.id,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )

    except IntegrityError as e:
        db.rollback()
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate" in error_str:
            raise DuplicateResourceException(
                resource_type="ProcessData",
                identifier=f"process_data_id={process_data.id}"
            )
        if "foreign key" in error_str:
            raise ConstraintViolationException(
                message="Invalid foreign key reference in process completion"
            )
        raise DatabaseException(message=f"Database integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(message=f"Database operation failed: {str(e)}")


@router.get(
    "/history/{serial_number}",
    response_model=ProcessHistoryResponse,
    summary="공정 이력 조회",
    description="Get complete process history for a serial number.",
)
def get_process_history(
    serial_number: str = Path(..., description="Serial number to look up"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> ProcessHistoryResponse:
    """
    Get process history for a serial number (공정 이력 조회).

    Returns the complete manufacturing history showing all 8 processes
    and their execution status.

    **Response:**
    ```json
    {
        "serial_number": "WF-KR-251110D-001-0001",
        "lot_number": "WF-KR-251110D-001",
        "total_processes": 8,
        "completed_processes": 5,
        "history": [
            {
                "process_number": 1,
                "process_name": "레이저 마킹",
                "result": "PASS",
                "started_at": "2025-01-10T09:00:00",
                "completed_at": "2025-01-10T09:05:00",
                "duration_seconds": 300,
                "operator_name": "김철수"
            },
            ...
        ]
    }
    ```
    """
    # Find serial
    serial = db.query(Serial).filter(
        Serial.serial_number == serial_number
    ).first()

    if not serial:
        raise SerialNotFoundException(serial_number=serial_number)

    lot = serial.lot
    if not lot:
        raise LotNotFoundException(lot_number=f"serial={serial_number}")

    # Get all 8 processes
    processes = db.query(Process).order_by(Process.process_number).all()

    # Get process data for this serial
    process_data_list = db.query(ProcessData).filter(
        ProcessData.serial_id == serial.id
    ).all()

    # Create a map of process_id to process_data
    data_map = {pd.process_id: pd for pd in process_data_list}

    # Build history
    history = []
    completed_count = 0

    for process in processes:
        pd = data_map.get(process.id)

        history_item = ProcessHistoryItem(
            process_number=process.process_number,
            process_name=process.process_name_ko or process.process_name_en,
            result=pd.result.value if pd and pd.result else None,
            started_at=pd.started_at if pd else None,
            completed_at=pd.completed_at if pd else None,
            duration_seconds=pd.duration_seconds if pd else None,
            operator_name=pd.operator.full_name if pd and pd.operator else None,
            measurements=pd.measurements if pd else None,
        )
        history.append(history_item)

        if pd and pd.completed_at:
            completed_count += 1

    return ProcessHistoryResponse(
        serial_number=serial_number,
        lot_number=lot.lot_number,
        total_processes=len(processes),
        completed_processes=completed_count,
        history=history,
    )
