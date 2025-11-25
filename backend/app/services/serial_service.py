from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import crud
from app.models.serial import SerialStatus, Serial
from app.models.lot import Lot, LotStatus
from app.models.process import Process
from app.models.process_data import ProcessData, ProcessResult
from app.models.wip_item import WIPItem, WIPStatus
from app.schemas.serial import (
    SerialCreate, SerialInDB, SerialUpdate, SerialListItem
)
from app.core.exceptions import (
    SerialNotFoundException,
    ValidationException,
    BusinessRuleException,
)
from app.services.base_service import BaseService
from app.services.printer_service import printer_service
import logging

logger = logging.getLogger(__name__)


class SerialService(BaseService[Serial]):
    """
    Service for managing Serial entities.
    Encapsulates business logic and data access for Serials.

    Inherits from BaseService for common functionality:
    - Transaction management
    - Error handling
    - Logging operations
    """

    def __init__(self):
        """Initialize SerialService with Serial as the model."""
        super().__init__(model_name="Serial")

    def list_serials(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[SerialInDB]:
        """List all serials with optional filtering and pagination."""
        try:
            return crud.serial.get_multi(
                db, skip=skip, limit=limit, status=status
            )
        except ValueError as e:
            self.log_error(e, "list_serials", {"status": status})
            raise ValidationException(message=str(e))
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="list")

    def get_failed_serials(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> List[SerialInDB]:
        """Get FAILED serials available for rework."""
        try:
            return crud.serial.get_failed(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_failed")

    def get_serial_by_number(self, db: Session, serial_number: str) -> SerialInDB:
        """Get serial by unique serial number."""
        try:
            serial = crud.serial.get_by_number(db, serial_number=serial_number)
            return self.validate_not_none(
                serial,
                f"number='{serial_number}'",
                SerialNotFoundException
            )
        except SerialNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_number")

    def get_serials_by_lot(
        self,
        db: Session,
        lot_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SerialListItem]:
        """Get all serials in a specific lot."""
        try:
            return crud.serial.get_by_lot(db, lot_id=lot_id, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_lot")

    def get_serials_by_status(
        self,
        db: Session,
        status_filter: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[SerialInDB]:
        """Get serials filtered by status."""
        try:
            return crud.serial.get_by_status(db, status=status_filter, skip=skip, limit=limit)
        except ValueError as e:
            self.log_error(e, "get_by_status", {"status": status_filter})
            raise ValidationException(message=str(e))
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_status")

    def get_serial(self, db: Session, serial_id: int) -> SerialInDB:
        """Get a single serial by ID."""
        try:
            serial = crud.serial.get(db, serial_id=serial_id)
            return self.validate_not_none(serial, serial_id, SerialNotFoundException)
        except SerialNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get")

    def create_serial(
        self,
        db: Session,
        serial_in: SerialCreate,
        print_label: bool = False
    ) -> SerialListItem:
        """Create a new serial."""
        try:
            serial = crud.serial.create(db, serial_in=serial_in)
            self.log_operation("create", serial.id, {"lot_id": serial_in.lot_id})

            if print_label:
                self._print_serial_label(serial)

            return serial
        except ValueError as e:
            self.log_error(e, "create", {"serial_in": serial_in.dict()})
            raise ValidationException(message=str(e))
        except IntegrityError as e:
            self.handle_integrity_error(e, operation="create")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="create")

    def generate_from_wip(
        self,
        db: Session,
        wip_id: str,
        print_label: bool = True
    ) -> SerialInDB:
        """Generate a new serial number from a WIP ID."""
        try:
            # 1. Find WIP Item
            wip_item = db.query(WIPItem).filter(WIPItem.wip_id == wip_id).first()
            if not wip_item:
                raise ValidationException(message=f"WIP ID '{wip_id}' not found")

            # 2. Validate WIP status
            self.check_business_rule(
                wip_item.serial_id is None,
                f"WIP '{wip_id}' is already converted to serial"
            )

            # 3. Get LOT
            lot = wip_item.lot
            if not lot:
                raise ValidationException(message=f"Associated LOT not found for WIP '{wip_id}'")

            # Use transaction context manager for atomic operation
            with self.transaction(db):
                # 4. Determine next sequence
                current_count = crud.serial.count_by_lot(db, lot_id=lot.id)
                next_sequence = current_count + 1

                self.check_business_rule(
                    next_sequence <= lot.target_quantity,
                    f"Target quantity ({lot.target_quantity}) reached for LOT {lot.lot_number}"
                )

                # 5. Create Serial with PASSED status (WIP conversion means all processes passed)
                serial_in = SerialCreate(
                    lot_id=lot.id,
                    sequence_in_lot=next_sequence,
                    status=SerialStatus.PASSED  # Serial is PASSED when converted from WIP
                )

                serial = crud.serial.create(db, serial_in=serial_in)

                # 5-1. Set completed_at timestamp for PASSED serial
                serial.completed_at = datetime.now(timezone.utc)
                db.add(serial)

                # 6. Update WIP Item
                wip_item.serial_id = serial.id
                wip_item.status = WIPStatus.CONVERTED.value
                wip_item.converted_at = serial.created_at
                db.add(wip_item)

                # 7. Update LOT passed_quantity and check completion
                lot.passed_quantity = (lot.passed_quantity or 0) + 1
                lot.actual_quantity = (lot.actual_quantity or 0) + 1

                # Check if LOT is complete
                total_completed = (lot.passed_quantity or 0) + (lot.failed_quantity or 0)
                if total_completed >= lot.target_quantity:
                    lot.status = LotStatus.COMPLETED.value
                    lot.closed_at = datetime.now(timezone.utc)
                    logger.info(f"LOT {lot.lot_number} marked as COMPLETED (passed={lot.passed_quantity}, failed={lot.failed_quantity})")
                db.add(lot)

                # Log the operation
                self.log_operation(
                    "generate_from_wip",
                    serial.id,
                    {"wip_id": wip_id, "serial_number": serial.serial_number, "lot_passed_qty": lot.passed_quantity}
                )

            # 7. Print Label (outside transaction)
            if print_label:
                self._print_serial_label(serial)

            return serial

        except (ValidationException, BusinessRuleException):
            raise
        except Exception as e:
            self.log_error(e, "generate_from_wip", {"wip_id": wip_id})
            raise ValidationException(message=f"Failed to generate serial: {str(e)}")

    def update_serial(
        self,
        db: Session,
        serial_id: int,
        serial_in: SerialUpdate
    ) -> SerialInDB:
        """Update an existing serial."""
        serial = crud.serial.get(db, serial_id=serial_id)
        if not serial:
            raise SerialNotFoundException(serial_id=serial_id)

        try:
            updated_serial = crud.serial.update(db, serial_id=serial_id, serial_in=serial_in)
            self.log_operation("update", serial_id, {"changes": serial_in.dict(exclude_unset=True)})
            return updated_serial
        except ValueError as e:
            self.log_error(e, "update", {"serial_id": serial_id})
            raise ValidationException(message=str(e))
        except IntegrityError as e:
            self.handle_integrity_error(e, identifier=f"serial_id={serial_id}", operation="update")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update")

    def update_serial_status(
        self,
        db: Session,
        serial_id: int,
        status_value: str,
        failure_reason: Optional[str] = None
    ) -> SerialInDB:
        """Update serial status with validation."""
        serial = crud.serial.get(db, serial_id=serial_id)
        if not serial:
            raise SerialNotFoundException(serial_id=serial_id)

        try:
            updated_serial = crud.serial.update_status(
                db,
                serial_id=serial_id,
                status=status_value,
                failure_reason=failure_reason
            )
            self.log_operation(
                "update_status",
                serial_id,
                {"status": status_value, "failure_reason": failure_reason}
            )
            return updated_serial
        except ValueError as e:
            self.log_error(e, "update_status", {"serial_id": serial_id, "status": status_value})
            raise ValidationException(message=str(e))
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update_status")

    def rework_serial(self, db: Session, serial_id: int) -> SerialInDB:
        """Start rework process for a FAILED serial."""
        serial = crud.serial.get(db, serial_id=serial_id)
        if not serial:
            raise SerialNotFoundException(serial_id=serial_id)

        # Check rework eligibility
        if not crud.serial.can_rework(db, serial_id=serial_id):
            if serial.status != SerialStatus.FAILED:
                raise BusinessRuleException(
                    message=f"Serial is not in FAILED status (current: {serial.status.value}). Cannot start rework."
                )
            else:
                raise BusinessRuleException(
                    message=f"Maximum rework count (3) exceeded for serial {serial.serial_number}"
                )

        try:
            reworked_serial = crud.serial.increment_rework(db, serial_id=serial_id)
            self.log_operation("rework", serial_id, {"rework_count": reworked_serial.rework_count})
            return reworked_serial
        except ValueError as e:
            self.log_error(e, "rework", {"serial_id": serial_id})
            raise ValidationException(message=str(e))
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="rework")

    def check_can_rework(self, db: Session, serial_id: int) -> Dict[str, Any]:
        """Check if a serial is eligible for rework."""
        serial = crud.serial.get(db, serial_id=serial_id)
        if not serial:
            raise SerialNotFoundException(serial_id=serial_id)

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

    def delete_serial(self, db: Session, serial_id: int) -> None:
        """Delete a serial."""
        try:
            deleted = crud.serial.delete(db, serial_id=serial_id)
            if not deleted:
                raise SerialNotFoundException(serial_id=serial_id)
            self.log_operation("delete", serial_id)
        except SerialNotFoundException:
            raise
        except IntegrityError as e:
            self.handle_integrity_error(e, identifier=f"serial_id={serial_id}", operation="delete")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="delete")

    def get_serial_trace(self, db: Session, serial_number: str) -> Dict[str, Any]:
        """Get complete traceability information for a serial."""
        serial = crud.serial.get_by_serial_number(db, serial_number=serial_number)
        if not serial:
            raise SerialNotFoundException(serial_id=f"serial_number='{serial_number}'")

        try:
            # Get LOT information
            lot_info = None
            if serial.lot:
                lot_info = {
                    "lot_number": serial.lot.lot_number,
                    "product_model": serial.lot.product_model.model_code if serial.lot.product_model else None,
                    "production_date": serial.lot.production_date.isoformat() if serial.lot.production_date else None,
                    "target_quantity": serial.lot.target_quantity,
                }

            # Get all process data for this serial
            process_data_records = (
                db.query(ProcessData)
                .filter(ProcessData.serial_id == serial.id)
                .join(Process)
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
                    "process_name": pd.process.process_name if pd.process else None,
                    "worker_id": pd.operator.username if pd.operator else None,
                    "worker_name": pd.operator.full_name if pd.operator else None,
                    "start_time": pd.started_at.isoformat() if pd.started_at else None,
                    "complete_time": pd.completed_at.isoformat() if pd.completed_at else None,
                    "duration_seconds": pd.duration_seconds,
                    "result": pd.result.value if pd.result else None,
                    "process_data": pd.measurements if pd.measurements else {},
                    "defects": pd.defects if pd.defects and pd.result == ProcessResult.FAIL else [],
                    "notes": pd.notes,
                    "is_rework": getattr(pd, 'is_rework', False)
                }

                process_history.append(process_record)

                if pd.duration_seconds:
                    total_cycle_time += pd.duration_seconds

                if process_record["is_rework"]:
                    rework_history.append({
                        "process_code": process_record["process_code"],
                        "process_name": process_record["process_name"],
                        "attempt_time": process_record["complete_time"],
                        "result": process_record["result"],
                        "defects": process_record["defects"]
                    })

            # Extract component LOTs
            component_lots = self._extract_component_lots(process_data_records)

            return {
                "serial_number": serial.serial_number,
                "lot_number": serial.lot.lot_number if serial.lot else None,
                "sequence_in_lot": serial.sequence_in_lot,
                "status": serial.status.value if serial.status else None,
                "rework_count": serial.rework_count,
                "created_at": serial.created_at.isoformat() if serial.created_at else None,
                "completed_at": serial.completed_at.isoformat() if serial.completed_at else None,
                "lot_info": lot_info,
                "process_history": process_history,
                "rework_history": rework_history,
                "component_lots": component_lots,
                "total_cycle_time_seconds": total_cycle_time
            }
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_serial_trace")

    def _print_serial_label(self, serial) -> None:
        """Helper method to print serial label with error handling."""
        try:
            printer_service.print_serial_label(serial_number=serial.serial_number)
        except Exception as e:
            # Log but don't fail the operation
            logger.error(f"Failed to print label for serial {serial.serial_number}: {e}")

    def _extract_component_lots(self, process_data_records) -> Dict[str, Any]:
        """Extract component LOTs from process data records."""
        component_lots = {}
        for pd in process_data_records:
            if pd.measurements and isinstance(pd.measurements, dict):
                if "busbar_lot" in pd.measurements:
                    component_lots["busbar_lot"] = pd.measurements["busbar_lot"]
                if "sma_spring_lot" in pd.measurements:
                    component_lots["sma_spring_lot"] = pd.measurements["sma_spring_lot"]
                if "component_lots" in pd.measurements:
                    component_lots.update(pd.measurements["component_lots"])
        return component_lots


serial_service = SerialService()