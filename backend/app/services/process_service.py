from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import crud
from app.models import (
    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus, WIPProcessHistory, WIPStatus
)
from app.models.process import LabelTemplateType
from app.schemas.process import ProcessCreate, ProcessUpdate, ProcessInDB
from app.schemas.process_data import ProcessDataCreate, ProcessResult, DataLevel
from app.schemas.process_operations import (
    ProcessStartRequest, ProcessStartResponse,
    ProcessCompleteRequest, ProcessCompleteResponse,
    ProcessHistoryResponse, ProcessHistoryItem
)
from app.core.exceptions import (
    ProcessNotFoundException,
    LotNotFoundException,
    SerialNotFoundException,
    UserNotFoundException,
    DuplicateResourceException,
    ConstraintViolationException,
    ValidationException,
    BusinessRuleException,
    DatabaseException,
)
from app.services.base_service import BaseService
from app.services.printer_service import printer_service
import logging

logger = logging.getLogger(__name__)

class ProcessService(BaseService[Process]):
    """
    Service for managing Manufacturing Processes and Operations.
    Encapsulates business logic for Process definition and execution (Start/Complete).

    Inherits from BaseService for common functionality:
    - Transaction management
    - Error handling
    - Logging operations
    """

    def __init__(self):
        """Initialize ProcessService with Process as the model."""
        super().__init__(model_name="Process")

    # --- CRUD Operations ---

    def list_processes(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProcessInDB]:
        """List all processes with pagination."""
        try:
            return crud.process.get_multi(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="list")

    def get_process_by_number(self, db: Session, process_number: int) -> ProcessInDB:
        """Get process by unique process number."""
        try:
            obj = crud.process.get_by_number(db, process_number=process_number)
            return self.validate_not_none(
                obj,
                f"number={process_number}",
                ProcessNotFoundException
            )
        except ProcessNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_number")

    def get_process_by_code(self, db: Session, process_code: str) -> ProcessInDB:
        """Get process by unique process code."""
        try:
            obj = crud.process.get_by_code(db, process_code=process_code)
            return self.validate_not_none(
                obj,
                f"code='{process_code}'",
                ProcessNotFoundException
            )
        except ProcessNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_code")

    def get_active_processes(self, db: Session) -> List[ProcessInDB]:
        """Get all active processes."""
        try:
            return crud.process.get_active(db)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_active")

    def get_process_sequence(self, db: Session) -> List[ProcessInDB]:
        """Get processes in sequence order."""
        try:
            return crud.process.get_sequence(db)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_sequence")

    def get_process(self, db: Session, process_id: int) -> ProcessInDB:
        """Get process by primary key ID."""
        try:
            obj = crud.process.get(db, process_id=process_id)
            return self.validate_not_none(
                obj,
                f"id={process_id}",
                ProcessNotFoundException
            )
        except ProcessNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get")

    def create_process(self, db: Session, obj_in: ProcessCreate) -> ProcessInDB:
        """Create new process."""
        try:
            with self.transaction(db):
                process = crud.process.create(db, process_in=obj_in)
                self.log_operation("create", process.id, {
                    "process_number": obj_in.process_number,
                    "process_code": obj_in.process_code
                })
                return process
        except IntegrityError as e:
            identifier = f"number={obj_in.process_number}" if obj_in.process_number else f"code='{obj_in.process_code}'"
            self.handle_integrity_error(e, identifier=identifier, operation="create")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="create")

    def update_process(self, db: Session, process_id: int, obj_in: ProcessUpdate) -> ProcessInDB:
        """Update existing process."""
        # First verify process exists
        try:
            obj = crud.process.get(db, process_id=process_id)
            if not obj:
                raise ProcessNotFoundException(process_id=process_id)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="verify_exists")

        try:
            with self.transaction(db):
                process = crud.process.update(db, process_id=process_id, process_in=obj_in)
                self.log_operation("update", process_id, {
                    "updates": obj_in.dict(exclude_unset=True)
                })
                return process
        except IntegrityError as e:
            identifier = None
            if obj_in.process_number:
                identifier = f"number={obj_in.process_number}"
            elif obj_in.process_code:
                identifier = f"code='{obj_in.process_code}'"
            self.handle_integrity_error(e, identifier=identifier, operation="update")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update")

    def delete_process(self, db: Session, process_id: int) -> None:
        """Delete process by ID."""
        # First verify process exists
        try:
            obj = crud.process.get(db, process_id=process_id)
            if not obj:
                raise ProcessNotFoundException(process_id=process_id)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="verify_exists")

        try:
            with self.transaction(db):
                crud.process.delete(db, process_id=process_id)
                self.log_operation("delete", process_id)
        except IntegrityError as e:
            # Process deletion is protected by database trigger
            raise ConstraintViolationException(
                message="Cannot delete process: has dependent data (lot_processes). Process deletion is protected by database trigger."
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="delete")

    # --- Operational Logic (Start/Complete) ---

    def start_process(self, db: Session, request: ProcessStartRequest) -> ProcessStartResponse:
        """Register process start (착공 등록)."""
        try:
            # Find LOT by number
            lot_number = request.lot_number
            lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

            # Track if we found WIP item in Smart Lookup
            wip_from_smart_lookup = None
            wip_id_from_smart_lookup = None

            # If LOT not found, try to interpret as Serial, WIP ID, or Unit Barcode
            if not lot:
                # 1. Try as Serial Number
                serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
                if serial:
                    lot = serial.lot
                    if not request.serial_number:
                        request.serial_number = serial.serial_number

                # 2. Try as WIP ID
                elif lot_number.startswith("WIP-"):
                    wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
                    if wip:
                        lot = wip.lot
                        if not request.wip_id:
                            request.wip_id = wip.wip_id
                        wip_from_smart_lookup = wip
                        wip_id_from_smart_lookup = wip.id

                # 3. Try as Unit Barcode
                elif len(lot_number) > 13 and lot_number[-3:].isdigit():
                    potential_lot_num = lot_number[:-3]
                    potential_seq = lot_number[-3:]

                    lot = db.query(Lot).filter(Lot.lot_number == potential_lot_num).first()
                    if lot:
                        wip_id_str = f"WIP-{potential_lot_num}-{potential_seq}"
                        wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
                        if wip:
                            if not request.wip_id:
                                request.wip_id = wip.wip_id

            if not lot:
                raise LotNotFoundException(lot_number=request.lot_number)

            # Check LOT status
            self.check_business_rule(
                lot.status in [LotStatus.CREATED, LotStatus.IN_PROGRESS],
                f"LOT is not active. Current status: {lot.status}"
            )

            # Find Process
            process = self._resolve_process(db, request.process_id)
            if not process:
                raise ProcessNotFoundException(process_id=request.process_id)

            # Determine data level, serial, and WIP
            serial = None
            wip_item = wip_from_smart_lookup
            data_level = DataLevel.LOT
            serial_id = None
            wip_item_id = wip_id_from_smart_lookup

            if request.serial_number:
                serial = db.query(Serial).filter(
                    Serial.serial_number == request.serial_number,
                    Serial.lot_id == lot.id
                ).first()
                if not serial:
                    raise SerialNotFoundException(serial_id=request.serial_number)
                data_level = DataLevel.SERIAL
                serial_id = serial.id
            elif request.wip_id:
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
                data_level = DataLevel.WIP

            # Find operator
            operator = self._resolve_operator(db, request.worker_id)
            if not operator:
                raise UserNotFoundException(user_id=request.worker_id)

            # Find equipment
            equipment_id = None
            if request.equipment_id:
                equipment = db.query(Equipment).filter(
                    Equipment.equipment_code == request.equipment_id
                ).first()
                if equipment:
                    equipment_id = equipment.id

            # Update LOT production line if needed
            if request.line_id:
                production_line = db.query(ProductionLine).filter(
                    ProductionLine.line_code == request.line_id
                ).first()
                if production_line and not lot.production_line_id:
                    lot.production_line_id = production_line.id

            # Validate process sequence
            self._validate_process_sequence(db, lot, process, serial_id, wip_item_id)

            # Check for concurrent work
            self._check_concurrent_work(db, lot, process, serial_id, wip_item_id)

            # Create process data record
            if request.start_time:
                try:
                    started_at = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
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
                result=ProcessResult.PASS,
                measurements={},
                started_at=started_at,
                completed_at=None,
            )

            with self.transaction(db):
                process_data = crud.process_data.create(db, obj_in=process_data_create)

                if lot.status == LotStatus.CREATED:
                    lot.status = LotStatus.IN_PROGRESS

                db.refresh(process_data)

                self.log_operation("start_process", process_data.id, {
                    "lot_id": lot.id,
                    "process_id": process.id,
                    "wip_id": wip_item_id,
                    "serial_id": serial_id
                }, user_id=operator.id)

                return ProcessStartResponse(
                    success=True,
                    message=f"Process {process.process_number} ({process.process_name_ko}) started successfully",
                    process_data_id=process_data.id,
                    started_at=started_at,
                    wip_id=wip_item_id,
                    wip_id_str=wip_item.wip_id if wip_item else None,
                )

        except (LotNotFoundException, ProcessNotFoundException, SerialNotFoundException,
                UserNotFoundException, ValidationException, BusinessRuleException) as e:
            # Re-raise business exceptions as-is
            raise
        except IntegrityError as e:
            self.handle_integrity_error(
                e,
                resource_type="ProcessData",
                identifier=f"lot_id={lot.id if lot else 'unknown'}, process_id={process.id if process else 'unknown'}",
                operation="start"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="start_process")

    def complete_process(self, db: Session, request: ProcessCompleteRequest) -> ProcessCompleteResponse:
        """Register process completion (완공 등록)."""
        try:
            # Smart Lookup
            lot_number = request.lot_number
            lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

            serial_for_query = None
            wip_for_query = None

            if not lot:
                # 1. Try as Serial Number
                serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
                if serial:
                    lot = serial.lot
                    serial_for_query = serial

                # 2. Try as WIP ID
                elif lot_number.startswith("WIP-"):
                    wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
                    if wip:
                        lot = wip.lot
                        wip_for_query = wip

                # 3. Try as Unit Barcode
                elif len(lot_number) > 13 and lot_number[-3:].isdigit():
                    potential_lot_num = lot_number[:-3]
                    potential_seq = lot_number[-3:]

                    lot = db.query(Lot).filter(Lot.lot_number == potential_lot_num).first()
                    if lot:
                        wip_id_str = f"WIP-{potential_lot_num}-{potential_seq}"
                        wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
                        if wip:
                            wip_for_query = wip

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
            elif serial_for_query:
                query = query.filter(ProcessData.serial_id == serial_for_query.id)
            elif wip_for_query:
                query = query.filter(ProcessData.wip_id == wip_for_query.id)

            process_data = query.order_by(ProcessData.started_at.desc()).first()

            if not process_data:
                raise ValidationException(
                    message=f"No in-progress process found for process_id {request.process_id}. Did you start the process first?"
                )

            try:
                result = ProcessResult(request.result.upper())
            except ValueError:
                raise ValidationException(
                    message=f"Invalid result. Must be one of: PASS, FAIL, REWORK"
                )

            # Update process data
            korea_tz = timezone(timedelta(hours=9))
            completed_at = datetime.now(korea_tz)

            process_data.result = result
            process_data.completed_at = completed_at
            process_data.measurements = request.measurement_data or {}

            if request.defect_data and result == ProcessResult.FAIL:
                process_data.defects = request.defect_data

            # Calculate duration
            duration_seconds = 0
            if process_data.started_at:
                start_ts = process_data.started_at
                end_ts = completed_at

                if start_ts.tzinfo is None:
                    start_ts = start_ts.replace(tzinfo=korea_tz)
                if end_ts.tzinfo is None:
                    end_ts = end_ts.replace(tzinfo=korea_tz)

                duration_seconds = int((end_ts - start_ts).total_seconds())
                if duration_seconds < 0:
                    logger.warning(f"Negative duration: {duration_seconds}s. Setting to 0.")
                    duration_seconds = 0

                process_data.duration_seconds = duration_seconds
            else:
                process_data.duration_seconds = 0

            with self.transaction(db):
                # db.refresh(process_data)  # Bug: Discards all updates!


                # Update serial status if FAIL
                if result == ProcessResult.FAIL and process_data.serial_id:
                    serial = db.query(Serial).filter(Serial.id == process_data.serial_id).first()
                    if serial:
                        serial.status = SerialStatus.FAILED



                # --- WIP Logic: Create WIPProcessHistory and Update Status ---

                if wip_for_query:  # If processing a WIP item

                    # Get process object for logging

                    process = db.query(Process).filter(Process.id == process_data.process_id).first()

                    

                    # 1. Create WIPProcessHistory record

                    wip_history = WIPProcessHistory(

                        wip_item_id=wip_for_query.id,

                        process_id=process_data.process_id,

                        result=result.value,

                        started_at=process_data.started_at,

                        completed_at=completed_at,

                        operator_id=process_data.operator_id

                    )

                    db.add(wip_history)

                    if process:

                        logger.info(f"Created WIPProcessHistory for WIP {wip_for_query.wip_id}, Process {process.process_number}, Result: {result.value}")



                    # 2. If PASS, check if all processes are complete

                    if result == ProcessResult.PASS:

                        # Get all active processes (processes 1-6 are manufacturing)

                        all_processes = db.query(Process).filter(

                            Process.process_number.in_([1, 2, 3, 4, 5, 6]),

                            Process.is_active == True

                        ).all()

                        

                        # Check if all have PASS results in their LATEST WIPProcessHistory

                        passed_process_ids = []

                        for proc in all_processes:

                            # Get the latest completion record for this process

                            latest_history = db.query(WIPProcessHistory).filter(

                                WIPProcessHistory.wip_item_id == wip_for_query.id,

                                WIPProcessHistory.process_id == proc.id,

                                WIPProcessHistory.completed_at.isnot(None)

                            ).order_by(

                                WIPProcessHistory.completed_at.desc()

                            ).first()

                            

                            # If latest attempt is PASS, count it

                            if latest_history and latest_history.result == ProcessResult.PASS.value:

                                passed_process_ids.append(proc.id)

                        

                        # If all processes passed, mark WIP as COMPLETED

                        if len(passed_process_ids) >= len(all_processes):

                            wip_for_query.status = WIPStatus.COMPLETED.value

                            logger.info(f"WIP {wip_for_query.wip_id} marked as COMPLETED - all processes passed ({len(passed_process_ids)}/{len(all_processes)})")



                # Auto-print label
                self._check_and_print_label(
                    db=db,
                    process_data=process_data,
                    wip_item=wip_for_query,
                    serial=serial_for_query,
                    lot=lot
                )

                self.log_operation("complete_process", process_data.id, {
                    "result": result.value,
                    "duration_seconds": duration_seconds
                }, user_id=process_data.operator_id)

                return ProcessCompleteResponse(
                    success=True,
                    message=f"Process completed with result: {result.value}",
                    process_data_id=process_data.id,
                    completed_at=completed_at,
                    duration_seconds=duration_seconds,
                )

        except (LotNotFoundException, ValidationException) as e:
            # Re-raise business exceptions as-is
            raise
        except IntegrityError as e:
            self.handle_integrity_error(
                e,
                resource_type="ProcessData",
                identifier=f"process_data_id={process_data.id if process_data else 'unknown'}",
                operation="complete"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="complete_process")

    def get_process_history(self, db: Session, serial_number: str) -> ProcessHistoryResponse:
        """Get process history for a serial number."""
        try:
            serial = db.query(Serial).filter(Serial.serial_number == serial_number).first()
            if not serial:
                raise SerialNotFoundException(serial_id=serial_number)

            lot = serial.lot
            if not lot:
                raise LotNotFoundException(lot_number=f"serial={serial_number}")

            processes = db.query(Process).order_by(Process.process_number).all()
            process_data_list = db.query(ProcessData).filter(
                ProcessData.serial_id == serial.id
            ).all()

            data_map = {pd.process_id: pd for pd in process_data_list}
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
        except (SerialNotFoundException, LotNotFoundException) as e:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_process_history")

    # --- Helper Methods ---

    def _resolve_process(self, db: Session, process_id_str: str) -> Optional[Process]:
        """Resolve process from various ID formats."""
        if process_id_str.startswith("PROC-"):
            try:
                proc_num = int(process_id_str.replace("PROC-", ""))
                return db.query(Process).filter(Process.process_number == proc_num).first()
            except ValueError:
                return None
        else:
            try:
                proc_id = int(process_id_str)
                process = db.query(Process).filter(Process.id == proc_id).first()
                if not process:
                    process = db.query(Process).filter(Process.process_number == proc_id).first()
                return process
            except ValueError:
                return None

    def _resolve_operator(self, db: Session, worker_id: str) -> Optional[User]:
        """Resolve operator from various ID formats."""
        operator = db.query(User).filter(User.username == worker_id).first()
        if not operator:
            try:
                operator_id = int(worker_id.replace("W", ""))
                operator = db.query(User).filter(User.id == operator_id).first()
            except (ValueError, AttributeError):
                pass
        return operator

    def _validate_process_sequence(self, db: Session, lot: Lot, process: Process,
                                   serial_id: Optional[int], wip_item_id: Optional[int]):
        """Validate that process sequence requirements are met."""
        process_number = process.process_number

        # Check if previous process is completed
        if process_number > 1:
            prev_process = db.query(Process).filter(Process.process_number == process_number - 1).first()
            if prev_process:
                prev_data_query = db.query(ProcessData).filter(
                    ProcessData.lot_id == lot.id,
                    ProcessData.process_id == prev_process.id,
                    ProcessData.result == ProcessResult.PASS
                )
                if serial_id:
                    prev_data_query = prev_data_query.filter(ProcessData.serial_id == serial_id)
                elif wip_item_id:
                    prev_data_query = prev_data_query.filter(ProcessData.wip_id == wip_item_id)

                if not prev_data_query.first():
                    raise BusinessRuleException(
                        message=f"Previous process (Process {process_number - 1}) must be completed with PASS before starting Process {process_number}"
                    )

        # Special check for Process 7 - requires all previous processes
        if process_number == 7:
            for prev_num in range(1, 7):
                prev_proc = db.query(Process).filter(Process.process_number == prev_num).first()
                if prev_proc:
                    prev_data_query = db.query(ProcessData).filter(
                        ProcessData.lot_id == lot.id,
                        ProcessData.process_id == prev_proc.id,
                        ProcessData.result == ProcessResult.PASS
                    )
                    if serial_id:
                        prev_data_query = prev_data_query.filter(ProcessData.serial_id == serial_id)
                    elif wip_item_id:
                        prev_data_query = prev_data_query.filter(ProcessData.wip_id == wip_item_id)

                    if not prev_data_query.first():
                        raise BusinessRuleException(
                            message=f"Process 7 requires all previous processes (1-6) to be PASS."
                        )

    def _check_concurrent_work(self, db: Session, lot: Lot, process: Process,
                               serial_id: Optional[int], wip_item_id: Optional[int]):
        """Check for concurrent work on different items in the same process."""
        active_records = db.query(ProcessData).filter(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == process.id,
            ProcessData.completed_at.is_(None)
        ).all()

        for record in active_records:
            is_different_work = False
            if serial_id:
                if record.serial_id != serial_id:
                    is_different_work = True
            elif wip_item_id:
                if record.wip_id != wip_item_id:
                    is_different_work = True

            if is_different_work:
                raise BusinessRuleException(
                    message=f"Another WIP item in this LOT is already being processed in Process {process.process_number}. Finish that work first."
                )

    def _check_and_print_label(self, db: Session, process_data: ProcessData,
                               wip_item=None, serial=None, lot=None) -> dict:
        """Check if auto-print is enabled and print label if conditions are met."""
        process = db.query(Process).filter(Process.id == process_data.process_id).first()
        if not process or not process.auto_print_label or not process.label_template_type:
            return {"printed": False}

        if process_data.result != ProcessResult.PASS:
            return {"printed": False}

        if not self._validate_previous_processes_for_print(db, process, wip_item):
            logger.info(f"Previous processes not all PASS, skipping auto-print")
            return {"printed": False}

        try:
            label_type = process.label_template_type
            operator_id = process_data.operator_id

            if label_type == LabelTemplateType.WIP_LABEL.value and wip_item:
                result = printer_service.print_wip_label(
                    wip_id=wip_item.wip_id,
                    db=db,
                    operator_id=operator_id,
                    process_id=process.id,
                    process_data_id=process_data.id
                )
                if result.get("success"):
                    logger.info(f"Auto-printed WIP label: {wip_item.wip_id}")
                    return {"printed": True, "label_type": "WIP_LABEL"}

            elif label_type == LabelTemplateType.SERIAL_LABEL.value and serial:
                result = printer_service.print_serial_label(
                    serial_number=serial.serial_number,
                    db=db,
                    operator_id=operator_id,
                    process_id=process.id,
                    process_data_id=process_data.id
                )
                if result.get("success"):
                    logger.info(f"Auto-printed Serial label: {serial.serial_number}")
                    return {"printed": True, "label_type": "SERIAL_LABEL"}

            elif label_type == LabelTemplateType.LOT_LABEL.value and lot:
                result = printer_service.print_lot_label(
                    lot_number=lot.lot_number,
                    db=db,
                    operator_id=operator_id,
                    process_id=process.id,
                    process_data_id=process_data.id
                )
                if result.get("success"):
                    logger.info(f"Auto-printed LOT label: {lot.lot_number}")
                    return {"printed": True, "label_type": "LOT_LABEL"}

            return {"printed": False}

        except Exception as e:
            logger.error(f"Auto-print failed: {e}")
            return {"printed": False, "error": str(e)}

    def _validate_previous_processes_for_print(self, db: Session, process: Process, wip_item) -> bool:
        """Validate that all previous processes are PASS before printing."""
        if not wip_item:
            return False
        if process.process_number == 1:
            return True

        for prev_num in range(1, process.process_number):
            prev_process = db.query(Process).filter(
                Process.process_number == prev_num,
                Process.is_active == True
            ).first()

            if prev_process:
                prev_data = db.query(ProcessData).filter(
                    ProcessData.wip_id == wip_item.id,
                    ProcessData.process_id == prev_process.id,
                    ProcessData.result == ProcessResult.PASS,
                    ProcessData.completed_at.isnot(None)
                ).first()
                if not prev_data:
                    return False
        return True

process_service = ProcessService()