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
    WIPItem,
)
from app.schemas.process_data import ProcessDataCreate, ProcessDataInDB, DataLevel, ProcessResult


router = APIRouter()


# Request/Response schemas for process operations

class ProcessStartRequest(BaseModel):
    """Request schema for starting a process (착공 등록)."""
    lot_number: str = Field(..., description="LOT number (e.g., WF-KR-251110D-001)")
    serial_number: Optional[str] = Field(None, description="Serial number (optional for LOT-level)")
    wip_id: Optional[str] = Field(None, description="WIP ID (e.g., WIP-KR01PSA2511-001)")
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
    wip_id: Optional[int] = None
    wip_id_str: Optional[str] = None


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
    lot_number = request.lot_number
    lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

    # Track if we found WIP item in Smart Lookup
    wip_from_smart_lookup = None
    wip_id_from_smart_lookup = None

    # If LOT not found, try to interpret as Serial, WIP ID, or Unit Barcode
    if not lot:
        print(f"[DEBUG] LOT not found by lot_number: {lot_number}")
        
        # 1. Try as Serial Number
        serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
        if serial:
            print(f"[DEBUG] Found as Serial: {serial.serial_number}")
            lot = serial.lot
            if not request.serial_number:
                request.serial_number = serial.serial_number
        
        # 2. Try as WIP ID (e.g., WIP-KR01TES251101-001)
        elif lot_number.startswith("WIP-"):
            print(f"[DEBUG] Trying as WIP ID: {lot_number}")
            print(f"[DEBUG] Query: db.query(WIPItem).filter(WIPItem.wip_id == {lot_number}).first()")
            
            # Try the query
            wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
            print(f"[DEBUG] Query result: {wip}")
            
            if wip:
                print(f"[DEBUG] Found WIP item! ID: {wip.id}, LOT ID: {wip.lot_id}")
                lot = wip.lot
                print(f"[DEBUG] Associated LOT: {lot}")
                if not request.wip_id:
                    request.wip_id = wip.wip_id
                # Save wip_item for later use
                wip_from_smart_lookup = wip
                wip_id_from_smart_lookup = wip.id
            else:
                print(f"[DEBUG] WIP item NOT found in database")
                # Check how many WIP items exist
                total_wips = db.query(WIPItem).count()
                print(f"[DEBUG] Total WIP items in database: {total_wips}")

        # 3. Try as Unit Barcode (LOT + Sequence, e.g., KR01TES251101001)
        # Assuming last 3 digits are sequence if length > 13 (typical LOT length)
        elif len(lot_number) > 13 and lot_number[-3:].isdigit():
            potential_lot_num = lot_number[:-3]
            potential_seq = lot_number[-3:]
            
            lot = db.query(Lot).filter(Lot.lot_number == potential_lot_num).first()
            if lot:
                # Found the LOT! Now try to find the specific WIP item
                wip_id_str = f"WIP-{potential_lot_num}-{potential_seq}"
                wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
                if wip:
                    if not request.wip_id:
                        request.wip_id = wip.wip_id
                
                # If we found the LOT but not the WIP item, we still proceed with the LOT
                # (The user might be starting the LOT, or the WIP item hasn't been created yet? 
                #  Actually WIP items are created when LOT is created/started. 
                #  But let's be safe and just use the LOT if found.)

    if not lot:
        raise LotNotFoundException(request.lot_number)

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

    # Determine data level, serial, and WIP
    serial = None
    wip_item = wip_from_smart_lookup  # Use WIP from Smart Lookup if found
    data_level = DataLevel.LOT
    serial_id = None
    wip_item_id = wip_id_from_smart_lookup  # Use WIP ID from Smart Lookup if found

    if request.serial_number:
        serial = db.query(Serial).filter(
            Serial.serial_number == request.serial_number,
            Serial.lot_id == lot.id
        ).first()
        if not serial:
            raise SerialNotFoundException(request.serial_number)
        data_level = DataLevel.SERIAL
        serial_id = serial.id
    elif request.wip_id:
        # Look up WIP item by wip_id string (only if not already found above)
        if not wip_item:
            wip_item = db.query(WIPItem).filter(
                WIPItem.wip_id == request.wip_id,
                WIPItem.lot_id == lot.id
            ).first()
            if not wip_item:
                raise ValidationException(
                    message=f"WIP item '{request.wip_id}' not found for LOT {lot.lot_number}"
                )
            wip_item_id = wip_item.id
        data_level = DataLevel.WIP  # Set data_level to WIP

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

            # Apply same level filter as current work
            if serial_id:
                prev_data_query = prev_data_query.filter(
                    ProcessData.serial_id == serial_id
                )
            elif wip_item_id:
                # WIP-level validation: must check same WIP item
                prev_data_query = prev_data_query.filter(
                    ProcessData.wip_id == wip_item_id
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
                elif wip_item_id:
                    prev_data_query = prev_data_query.filter(
                        ProcessData.wip_id == wip_item_id
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
                            elif wip_item_id:
                                check_query = check_query.filter(
                                    ProcessData.wip_id == wip_item_id
                                )
                            if check_query.first():
                                pass_count += 1

                    raise BusinessRuleException(
                        message=f"Process 7 requires all previous processes (1-6) to be PASS. Current PASS count: {pass_count}"
                    )

    # Check for concurrent work (WIP-Exclusive Concurrency)
    # Rule: Only one WIP item per LOT can be active in a process at a time.
    # Exception: The SAME WIP item can be started multiple times (self-overlap allowed).
    
    active_records_query = db.query(ProcessData).filter(
        ProcessData.lot_id == lot.id,
        ProcessData.process_id == process.id,
        ProcessData.completed_at.is_(None)
    )
    
    active_records = active_records_query.all()
    
    for record in active_records:
        # Check if the active record belongs to a DIFFERENT WIP/Serial
        is_different_work = False
        
        if serial_id:
            if record.serial_id != serial_id:
                is_different_work = True
        elif wip_item_id:
            if record.wip_id != wip_item_id:
                is_different_work = True
        else:
            # LOT level: If there is ANY active record, it's a conflict 
            # (unless we want to allow multiple LOT-level starts? Assuming yes for consistency)
            # But LOT level usually implies the whole LOT is the unit.
            # If data_level is LOT, we check if record.id is not None (which it always is).
            # Actually, for LOT level, we probably just allow multiple starts.
            pass

        if is_different_work:
             raise BusinessRuleException(
                message=f"Another WIP item in this LOT is already being processed in Process {process.process_number}. Finish that work first."
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
        wip_id=wip_item_id,
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
            wip_id=wip_item_id,
            wip_id_str=wip_item.wip_id if wip_item else None,
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
    # Smart Lookup: Find LOT by number, or interpret as Serial/WIP/Unit Barcode
    lot_number = request.lot_number
    lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()
    
    # If LOT not found, try to interpret as Serial, WIP ID, or Unit Barcode
    serial_for_query = None
    wip_for_query = None
    
    if not lot:
        # 1. Try as Serial Number
        serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
        if serial:
            lot = serial.lot
            serial_for_query = serial
        
        # 2. Try as WIP ID (e.g., WIP-KR01TES251101-001)
        elif lot_number.startswith("WIP-"):
            wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
            if wip:
                lot = wip.lot
                wip_for_query = wip
        
        # 3. Try as Unit Barcode (LOT + Sequence, e.g., KR01TES251101001)
        elif len(lot_number) > 13 and lot_number[-3:].isdigit():
            potential_lot_num = lot_number[:-3]
            potential_seq = lot_number[-3:]
            
            lot = db.query(Lot).filter(Lot.lot_number == potential_lot_num).first()
            if lot:
                # Found the LOT! Now try to find the specific WIP item
                wip_id_str = f"WIP-{potential_lot_num}-{potential_seq}"
                wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
                if wip:
                    wip_for_query = wip
    
    if not lot:
        raise LotNotFoundException(lot_number=request.lot_number)

    # Find in-progress process data
    # Use LIFO (Last In First Out) strategy: Find the LATEST started active record
    query = db.query(ProcessData).filter(
        ProcessData.lot_id == lot.id,
        ProcessData.process_id == request.process_id,
        ProcessData.completed_at.is_(None)
    )

    # Apply filters based on what was found in Smart Lookup
    if request.serial_number:
        # Explicit serial_number in request takes precedence
        serial = db.query(Serial).filter(
            Serial.serial_number == request.serial_number,
            Serial.lot_id == lot.id
        ).first()
        if serial:
            query = query.filter(ProcessData.serial_id == serial.id)
    elif serial_for_query:
        # Serial found via Smart Lookup
        query = query.filter(ProcessData.serial_id == serial_for_query.id)
    elif wip_for_query:
        # WIP found via Smart Lookup
        query = query.filter(ProcessData.wip_id == wip_for_query.id)

    # Order by started_at DESC to get the latest one
    process_data = query.order_by(ProcessData.started_at.desc()).first()

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

    # Update process data with LOCAL time (Korea timezone)
    from datetime import timezone, timedelta
    korea_tz = timezone(timedelta(hours=9))  # UTC+9
    completed_at = datetime.now(korea_tz)  # Use local Korea time
    
    process_data.result = result
    process_data.completed_at = completed_at
    process_data.measurements = request.measurement_data or {}

    if request.defect_data and result == ProcessResult.FAIL:
        process_data.defects = request.defect_data

    # Calculate duration with proper timezone handling
    duration_seconds = 0  # Initialize with default
    if process_data.started_at:
        start_ts = process_data.started_at
        end_ts = completed_at
        
        # Ensure both timestamps have timezone info
        # If started_at is naive, assume it's in Korea timezone
        if start_ts.tzinfo is None:
            start_ts = start_ts.replace(tzinfo=korea_tz)
        if end_ts.tzinfo is None:
            end_ts = end_ts.replace(tzinfo=korea_tz)
            
        # Calculate duration - should always be positive
        duration_seconds = int((end_ts - start_ts).total_seconds())
        
        # Safety check: if duration is negative, something is wrong with timestamps
        # Set to 0 instead of failing
        if duration_seconds < 0:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Negative duration calculated: {duration_seconds}s. "
                f"start={start_ts}, end={end_ts}. Setting to 0."
            )
            duration_seconds = 0
            
        process_data.duration_seconds = duration_seconds
    else:
        process_data.duration_seconds = 0

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
