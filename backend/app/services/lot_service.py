from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InternalError

from app.crud import lot as crud
from app.crud import wip_item as wip_crud
from app.schemas.lot import LotCreate, LotUpdate, LotInDB, LotStatus
from app.schemas.wip_item import WIPItemInDB
from app.models import User
from app.models.lot import Lot
from app.core.exceptions import LotNotFoundException
from app.services.base_service import BaseService
from app.services.wip_service import WIPValidationError


class LotService(BaseService[Lot]):
    """
    Service for managing Lot entities.
    Encapsulates business logic and data access for Lots.

    Inherits from BaseService for common functionality:
    - Transaction management
    - Error handling
    - Logging operations
    """

    def __init__(self):
        """Initialize LotService with Lot as the model."""
        super().__init__(model_name="Lot")

    def get_lots(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[LotStatus] = None
    ) -> List[LotInDB]:
        """
        List all LOTs with pagination and optional status filter.
        """
        try:
            if status:
                return crud.get_by_status(db, status=status.value, skip=skip, limit=limit)
            return crud.get_multi(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="list")

    def get_lot_by_number(self, db: Session, lot_number: str) -> LotInDB:
        """
        Get LOT by unique LOT number.
        """
        try:
            obj = crud.get_by_number(db, lot_number=lot_number)
            return self.validate_not_none(
                obj,
                lot_number,
                LotNotFoundException
            )
        except LotNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_number")

    def get_active_lots(self, db: Session, skip: int = 0, limit: int = 100) -> List[LotInDB]:
        """
        Get active LOTs (CREATED or IN_PROGRESS).
        """
        try:
            return crud.get_active(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_active")

    def get_lots_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[LotInDB]:
        """
        Get LOTs within production date range.
        """
        try:
            return crud.get_by_date_range(
                db,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_date_range")

    def get_lots_by_product_model(
        self,
        db: Session,
        product_model_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[LotInDB]:
        """
        Get LOTs filtered by product model.
        """
        try:
            return crud.get_by_product_model(
                db,
                product_model_id=product_model_id,
                skip=skip,
                limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_product_model")

    def get_lots_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[LotInDB]:
        """
        Get LOTs filtered by status.
        """
        try:
            return crud.get_by_status(db, status=status, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_status")

    def get_lot(self, db: Session, lot_id: int) -> LotInDB:
        """
        Get LOT by primary key ID.
        """
        try:
            obj = crud.get(db, lot_id=lot_id)
            return self.validate_not_none(obj, lot_id, LotNotFoundException)
        except LotNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get")

    def create_lot(self, db: Session, lot_in: LotCreate) -> LotInDB:
        """
        Create new LOT.
        """
        try:
            lot = crud.create(db, lot_in=lot_in)
            self.log_operation("create", lot.id, {"lot_number": lot.lot_number})
            return lot
        except ValueError as e:
            # Handle validation errors from CRUD layer
            self.log_error(e, "create", {"lot_in": lot_in.dict()})
            from app.core.exceptions import ValidationException
            raise ValidationException(message=str(e))
        except IntegrityError as e:
            identifier = f"lot_number={lot_in.lot_number}" if hasattr(lot_in, 'lot_number') else None
            self.handle_integrity_error(e, identifier=identifier, operation="create")
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="create")

    def update_lot(self, db: Session, lot_id: int, lot_in: LotUpdate) -> LotInDB:
        """
        Update existing LOT.
        """
        # First check if lot exists
        obj = crud.get(db, lot_id=lot_id)
        if not obj:
            raise LotNotFoundException(lot_id=lot_id)

        try:
            updated_lot = crud.update(db, lot_id=lot_id, lot_in=lot_in)
            self.log_operation("update", lot_id, {"changes": lot_in.dict(exclude_unset=True)})
            return updated_lot
        except IntegrityError as e:
            self.handle_integrity_error(e, identifier=f"lot_id={lot_id}", operation="update")
        except InternalError as e:
            self.handle_internal_error(e)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update")

    def start_wip_generation(
        self,
        db: Session,
        lot_id: int,
        quantity: int,
        current_user: User
    ) -> List[WIPItemInDB]:
        """
        Generate batch of WIP IDs for a LOT.
        """
        try:
            # Log the operation
            self.log_operation(
                "start_wip_generation",
                lot_id,
                {"quantity": quantity, "user_id": current_user.id}
            )

            wip_items = wip_crud.create_batch(db, lot_id, quantity)
            return wip_items

        except WIPValidationError as e:
            # Business validation error - let it bubble up
            self.log_error(e, "start_wip_generation", {"lot_id": lot_id, "quantity": quantity})
            raise
        except ValueError as e:
            # Lot not found or similar issue
            self.log_error(e, "start_wip_generation", {"lot_id": lot_id})
            raise LotNotFoundException(lot_id)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="start_wip_generation")


lot_service = LotService()