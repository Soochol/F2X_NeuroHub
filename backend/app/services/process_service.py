from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from app import crud
from app.crud.process import ProcessValidationError
from app.models import (
    User, Lot, Serial, Process, ProcessData,
    WIPItem, Equipment, ProductionLine,
    LotStatus, SerialStatus, WIPProcessHistory, WIPStatus
)
from app.models.process import LabelTemplateType, ProcessType
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
    BusinessRuleException,
    ConstraintViolationException
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

class ProcessService(BaseService):
    """
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
        except ProcessValidationError as e:
            raise BusinessRuleException(message=str(e))
        except IntegrityError as e:
            # Determine which field caused the duplicate error
            error_str = str(e).lower()
            if "process_code" in error_str:
                identifier = f"code='{obj_in.process_code}'"
            elif "process_number" in error_str:
                identifier = f"number={obj_in.process_number}"
            else:
                identifier = f"number={obj_in.process_number} or code='{obj_in.process_code}'"
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
        except ProcessValidationError as e:
            raise BusinessRuleException(message=str(e))
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
            # 1. Resolve Process
            process = self._resolve_process(db, str(request.process_id))
            if not process:
                raise ProcessNotFoundException(process_id=request.process_id)

            # 2. Resolve Operator
            operator = self._resolve_operator(db, request.worker_id)
            if not operator:
                raise UserNotFoundException(user_id=request.worker_id)

            # 3. Resolve LOT/Serial/WIP (wip_id is now required)
            lot = None
            serial = None
            wip_item = None

            # Search by wip_id (required field)
            wip = db.query(WIPItem).filter(WIPItem.wip_id == request.wip_id).first()
            if wip:
                lot = wip.lot
                wip_item = wip

            # Fallback: if lot_number provided, use legacy lookup
            if not lot and request.lot_number:
                lot_number = request.lot_number
                lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

                if not lot:
                    # Try as Serial Number
                    serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
                    if serial:
                        lot = serial.lot
                        if not request.serial_number:
                            request.serial_number = serial.serial_number

            if not lot:
                raise LotNotFoundException(lot_number=request.wip_id)

            # Check LOT status
            self.check_business_rule(
                lot.status in [LotStatus.CREATED, LotStatus.IN_PROGRESS],
                f"LOT is not active. Current status: {lot.status}"
            )

            # 4. Check Business Rules
            self._validate_process_sequence(db, lot, process, serial.id if serial else None, wip_item.id if wip_item else None)

            # Check for existing in-progress record (재착공 허용)
            existing_record = self._check_concurrent_work(db, lot, process, serial.id if serial else None, wip_item.id if wip_item else None)

            # 5. Create or Update ProcessData
            start_time = datetime.now(timezone.utc)

            if existing_record:
                # 재착공: 기존 레코드의 started_at 업데이트
                existing_record.started_at = start_time
                existing_record.operator_id = operator.id
                process_data = existing_record
                logger.info(f"Re-starting process: updated started_at for ProcessData {process_data.id}")
            else:
                # 신규 착공: 새 레코드 생성
                if wip_item:
                    data_level = DataLevel.WIP.value
                elif serial:
                    data_level = DataLevel.SERIAL.value
                else:
                    data_level = DataLevel.LOT.value

                process_data = ProcessData(
                    lot_id=lot.id,
                    serial_id=serial.id if serial else None,
                    wip_id=wip_item.id if wip_item else None,
                    process_id=process.id,
                    header_id=request.header_id,  # Link to process header for station/batch tracking
                    operator_id=operator.id,
                    started_at=start_time,
                    data_level=data_level,
                    result=ProcessResult.PASS.value,
                )
                db.add(process_data)

            # Update WIPItem status to IN_PROGRESS
            if wip_item:
                wip_item.status = WIPStatus.IN_PROGRESS.value

            db.commit()
            db.refresh(process_data)

            return ProcessStartResponse(
                success=True,
                message=f"Process {process.process_name_ko} started.",
                process_data_id=process_data.id,
                started_at=start_time,
                wip_id=wip_item.id if wip_item else None,
                wip_id_str=wip_item.wip_id if wip_item else None,
            )

        except (ProcessNotFoundException, UserNotFoundException, LotNotFoundException) as e:
            raise
        except IntegrityError as e:
            self.handle_integrity_error(e, resource_type="ProcessData", operation="start")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="start_process")

    def complete_process(self, db: Session, request: ProcessCompleteRequest) -> ProcessCompleteResponse:
        """Register process completion (실적 등록)."""
        try:
            # 1. Resolve Process
            process = self._resolve_process(db, str(request.process_id))
            if not process:
                raise ProcessNotFoundException(process_id=request.process_id)

            # 2. Resolve Operator
            operator = self._resolve_operator(db, request.worker_id)
            if not operator:
                raise UserNotFoundException(user_id=request.worker_id)

            # 3. Resolve LOT/Serial/WIP (wip_id is now required)
            lot = None
            serial = None
            wip_item = None

            # Search by wip_id (required field)
            wip = db.query(WIPItem).filter(WIPItem.wip_id == request.wip_id).first()
            if wip:
                lot = wip.lot
                wip_item = wip

            # Fallback: if lot_number provided, use legacy lookup
            if not lot and request.lot_number:
                lot_number = request.lot_number
                lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

                if not lot:
                    # Try as Serial Number
                    serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
                    if serial:
                        lot = serial.lot
                        if not request.serial_number:
                            request.serial_number = serial.serial_number

            if not lot:
                raise LotNotFoundException(lot_number=request.wip_id)

            # 4. Find Active ProcessData
            query = db.query(ProcessData).filter(
                ProcessData.lot_id == lot.id,
                ProcessData.process_id == process.id,
                ProcessData.completed_at.is_(None)
            )
            
            if serial:
                query = query.filter(ProcessData.serial_id == serial.id)
            elif wip_item:
                query = query.filter(ProcessData.wip_id == wip_item.id)

            process_data = query.order_by(ProcessData.started_at.desc()).first()
            
            if not process_data:
                raise BusinessRuleException(message="No active process found to complete.")

            # 5. Update ProcessData
            end_time = datetime.now(timezone.utc)
            process_data.completed_at = end_time
            process_data.result = request.result
            process_data.measurements = request.measurements
            
            # Calculate duration
            if process_data.started_at:
                started_at = process_data.started_at
                if started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)
                process_data.duration_seconds = int((end_time - started_at).total_seconds())

            # --- WIP Logic: Create WIPProcessHistory and Update Status ---
            if wip_item:  # If processing a WIP item
                # 1. Create WIPProcessHistory record
                wip_history = WIPProcessHistory(
                    wip_item_id=wip_item.id,
                    process_id=process_data.process_id,
                    header_id=request.header_id,  # Link to process header for station/batch tracking
                    result=request.result,
                    started_at=process_data.started_at,
                    completed_at=end_time,
                    operator_id=process_data.operator_id,
                )
                db.add(wip_history)
                db.flush()  # Flush to make wip_history visible in subsequent queries
                logger.info(f"Created WIPProcessHistory for WIP {wip_item.wip_id}, Process {process.process_number}, Result: {request.result}")

                # 2. If PASS, check if all processes are complete
                if request.result == ProcessResult.PASS.value:
                    # Get all active MANUFACTURING processes dynamically
                    all_processes = db.query(Process).filter(
                        Process.process_type == ProcessType.MANUFACTURING.value,
                        Process.is_active == True
                    ).all()

                    # Check if all have PASS results in their LATEST WIPProcessHistory
                    passed_process_ids = []
                    for proc in all_processes:
                        # Get the latest completion record for this process
                        latest_history = db.query(WIPProcessHistory).filter(
                            WIPProcessHistory.wip_item_id == wip_item.id,
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
                        wip_item.status = WIPStatus.COMPLETED.value
                        logger.info(f"WIP {wip_item.wip_id} marked as COMPLETED - all processes passed ({len(passed_process_ids)}/{len(all_processes)})")

                    # 3. If this is SERIAL_CONVERSION process with PASS, auto-convert to Serial
                    if process.process_type == ProcessType.SERIAL_CONVERSION.value:
                        # Import serial_service here to avoid circular imports
                        from app.services.serial_service import serial_service

                        try:
                            # Determine if we should print serial label based on label_template_type
                            should_print_serial = (
                                process.auto_print_label and
                                process.label_template_type == LabelTemplateType.SERIAL_LABEL.value
                            )

                            # Generate serial from WIP (this also sets status to CONVERTED)
                            serial_result = serial_service.generate_from_wip(
                                db,
                                wip_id=wip_item.wip_id,
                                print_label=should_print_serial  # Print only if SERIAL_LABEL selected
                            )
                            logger.info(f"WIP {wip_item.wip_id} auto-converted to Serial {serial_result.serial_number}")

                            # Update serial variable for _check_and_print_label
                            serial = db.query(Serial).filter(Serial.id == serial_result.id).first()

                            # If already printed serial label, skip _check_and_print_label
                            if should_print_serial:
                                db.commit()
                                return ProcessCompleteResponse(
                                    success=True,
                                    message=f"Process completed with result: {process_data.result}",
                                    process_data_id=process_data.id,
                                    completed_at=end_time,
                                    duration_seconds=process_data.duration_seconds or 0,
                                    result=process_data.result,
                                    label_printed=True,
                                    label_type="SERIAL_LABEL"
                                )
                        except Exception as e:
                            logger.error(f"Failed to auto-convert WIP {wip_item.wip_id} to Serial: {e}")
                            raise BusinessRuleException(
                                message=f"SERIAL_CONVERSION failed: {str(e)}"
                            )

            # 6. Handle Label Printing (for non-SERIAL_CONVERSION or non-SERIAL_LABEL types)
            print_result = self._check_and_print_label(db, process_data, wip_item, serial, lot)

            db.commit()
            
            return ProcessCompleteResponse(
                success=True,
                message=f"Process completed with result: {process_data.result}",
                process_data_id=process_data.id,
                completed_at=end_time,
                duration_seconds=process_data.duration_seconds or 0,
                result=process_data.result,
                label_printed=print_result.get("printed", False),
                label_type=print_result.get("label_type")
            )

        except (ProcessNotFoundException, UserNotFoundException, LotNotFoundException) as e:
            raise
        except IntegrityError as e:
            self.handle_integrity_error(e, resource_type="ProcessData", operation="complete")
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
        """Resolve operator from various ID formats (username, full_name, id, W-prefixed id)."""
        # 1. Try by username
        operator = db.query(User).filter(User.username == worker_id).first()
        if operator:
            return operator

        # 2. Try by full_name (supports Korean names like "박수철")
        operator = db.query(User).filter(User.full_name == worker_id).first()
        if operator:
            return operator

        # 3. Try by numeric ID or W-prefixed ID (e.g., "W001" -> 1)
        try:
            operator_id = int(worker_id.replace("W", "").replace("w", ""))
            operator = db.query(User).filter(User.id == operator_id).first()
        except (ValueError, AttributeError):
            pass

        return operator

    def _validate_process_sequence(self, db: Session, lot: Lot, process: Process,
                                   serial_id: Optional[int], wip_item_id: Optional[int]):
        """Validate that process sequence requirements are met."""
        process_number = process.process_number

        # Check if this process already completed with PASS - prevent re-start
        existing_pass_query = db.query(ProcessData).filter(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == process.id,
            ProcessData.result == ProcessResult.PASS.value,
            ProcessData.completed_at.isnot(None)
        )
        if wip_item_id:
            existing_pass_query = existing_pass_query.filter(ProcessData.wip_id == wip_item_id)
        elif serial_id:
            existing_pass_query = existing_pass_query.filter(ProcessData.serial_id == serial_id)

        existing_pass = existing_pass_query.first()
        logger.info(f"[PASS CHECK] lot_id={lot.id}, process_id={process.id}, wip_item_id={wip_item_id}, serial_id={serial_id}, existing_pass={existing_pass}")

        if existing_pass:
            raise BusinessRuleException(
                message=f"Process {process_number} already completed with PASS. Cannot start again."
            )

        # Check if previous process is completed
        if process_number > 1:
            prev_process = db.query(Process).filter(Process.process_number == process_number - 1).first()
            if prev_process:
                prev_data_query = db.query(ProcessData).filter(
                    ProcessData.lot_id == lot.id,
                    ProcessData.process_id == prev_process.id,
                    ProcessData.result == ProcessResult.PASS.value
                )
                if serial_id:
                    prev_data_query = prev_data_query.filter(ProcessData.serial_id == serial_id)
                elif wip_item_id:
                    prev_data_query = prev_data_query.filter(ProcessData.wip_id == wip_item_id)

                if not prev_data_query.first():
                    raise BusinessRuleException(
                        message=f"Previous process (Process {process_number - 1}) must be completed with PASS before starting Process {process_number}"
                    )

        # Special check for SERIAL_CONVERSION process - requires all MANUFACTURING processes
        current_process = db.query(Process).filter(Process.process_number == process_number).first()
        if current_process and current_process.process_type == ProcessType.SERIAL_CONVERSION.value:
            # Get all active MANUFACTURING processes
            manufacturing_processes = db.query(Process).filter(
                Process.process_type == ProcessType.MANUFACTURING.value,
                Process.is_active == True
            ).all()

            for mfg_proc in manufacturing_processes:
                prev_data_query = db.query(ProcessData).filter(
                    ProcessData.lot_id == lot.id,
                    ProcessData.process_id == mfg_proc.id,
                    ProcessData.result == ProcessResult.PASS.value
                )
                if serial_id:
                    prev_data_query = prev_data_query.filter(ProcessData.serial_id == serial_id)
                elif wip_item_id:
                    prev_data_query = prev_data_query.filter(ProcessData.wip_id == wip_item_id)

                if not prev_data_query.first():
                    raise BusinessRuleException(
                        message=f"SERIAL_CONVERSION process requires all MANUFACTURING processes to be PASS."
                    )

    def _check_concurrent_work(self, db: Session, lot: Lot, process: Process,
                               serial_id: Optional[int], wip_item_id: Optional[int]) -> Optional[ProcessData]:
        """
        Check for concurrent work on the SAME item in the same process.

        Multiple WIP items can be processed concurrently in the same LOT and process.
        Returns existing in-progress record for re-start (overwrite), None otherwise.
        """
        # Only check if the SAME WIP/Serial is already in progress
        query = db.query(ProcessData).filter(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == process.id,
            ProcessData.completed_at.is_(None)
        )

        if wip_item_id:
            query = query.filter(ProcessData.wip_id == wip_item_id)
        elif serial_id:
            query = query.filter(ProcessData.serial_id == serial_id)
        else:
            # LOT level - check for any incomplete LOT level process
            query = query.filter(
                ProcessData.wip_id.is_(None),
                ProcessData.serial_id.is_(None)
            )

        return query.first()

    def _check_and_print_label(self, db: Session, process_data: ProcessData,
                               wip_item=None, serial=None, lot=None) -> dict:
        """Check if auto-print is enabled and print label if conditions are met."""
        from app.services.printer_service import printer_service

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