from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import crud
from app.models.equipment import Equipment
from app.schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentInDB
)
from app.core.exceptions import (
    EquipmentNotFoundException,
    DuplicateResourceException,
    ConstraintViolationException,
    ValidationException,
    DatabaseException,
)
from app.services.base_service import BaseService


class EquipmentService(BaseService[Equipment]):
    """
    Service for managing Equipment entities.
    Encapsulates business logic and data access for Equipment.

    Inherits from BaseService for common functionality:
    - Transaction management
    - Error handling
    - Logging operations
    """

    def __init__(self):
        """Initialize EquipmentService with Equipment as the model."""
        super().__init__(model_name="Equipment")

    def list_equipment(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """List all equipment with pagination."""
        try:
            return crud.equipment.get_multi(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="list")

    def get_active_equipment(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """Get active equipment with pagination."""
        try:
            return crud.equipment.get_active(db, skip=skip, limit=limit)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_active")

    def get_equipment_needs_maintenance(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """Get equipment that needs maintenance."""
        try:
            return crud.equipment.get_needs_maintenance(
                db, skip=skip, limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_needs_maintenance")

    def get_equipment_by_type(
        self,
        db: Session,
        equipment_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """Get equipment filtered by type."""
        try:
            return crud.equipment.get_by_type(
                db, equipment_type=equipment_type, skip=skip, limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_type")

    def get_equipment_by_production_line(
        self,
        db: Session,
        production_line_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """Get equipment filtered by production line."""
        try:
            return crud.equipment.get_by_production_line(
                db, production_line_id=production_line_id,
                skip=skip, limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_production_line")

    def get_equipment_by_process(
        self,
        db: Session,
        process_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[EquipmentInDB]:
        """Get equipment filtered by process."""
        try:
            return crud.equipment.get_by_process(
                db, process_id=process_id, skip=skip, limit=limit
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_process")

    def get_equipment_by_code(
        self, db: Session, equipment_code: str
    ) -> EquipmentInDB:
        """Get equipment by unique equipment code."""
        try:
            obj = crud.equipment.get_by_code(
                db, equipment_code=equipment_code
            )
            return self.validate_not_none(
                obj,
                f"code='{equipment_code}'",
                EquipmentNotFoundException
            )
        except EquipmentNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get_by_code")

    def get_equipment(self, db: Session, equipment_id: int) -> EquipmentInDB:
        """Get equipment by primary key ID."""
        try:
            obj = crud.equipment.get(db, equipment_id=equipment_id)
            return self.validate_not_none(
                obj,
                f"id={equipment_id}",
                EquipmentNotFoundException
            )
        except EquipmentNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get")

    def create_equipment(
        self, db: Session, obj_in: EquipmentCreate
    ) -> EquipmentInDB:
        """Create new equipment."""
        # Check if equipment_code already exists
        existing = crud.equipment.get_by_code(
            db, equipment_code=obj_in.equipment_code
        )
        if existing:
            raise DuplicateResourceException(
                resource_type="Equipment",
                identifier=f"code='{obj_in.equipment_code}'"
            )

        try:
            with self.transaction(db):
                equipment = crud.equipment.create(db, equipment_in=obj_in)
                self.log_operation("create", equipment.id, {
                    "equipment_code": obj_in.equipment_code,
                    "equipment_name": obj_in.equipment_name
                })
                return equipment
        except IntegrityError as e:
            self.handle_integrity_error(
                e,
                identifier=f"code='{obj_in.equipment_code}'",
                operation="create"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="create")

    def update_equipment(
        self,
        db: Session,
        equipment_id: int,
        obj_in: EquipmentUpdate
    ) -> EquipmentInDB:
        """Update existing equipment."""
        # First verify equipment exists
        try:
            obj = crud.equipment.get(db, equipment_id=equipment_id)
            if not obj:
                raise EquipmentNotFoundException(equipment_id=equipment_id)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="verify_exists")

        # Check if updating equipment_code to an existing code
        if (obj_in.equipment_code and
                obj_in.equipment_code.upper() != obj.equipment_code):
            existing = crud.equipment.get_by_code(
                db, equipment_code=obj_in.equipment_code
            )
            if existing:
                raise DuplicateResourceException(
                    resource_type="Equipment",
                    identifier=f"code='{obj_in.equipment_code}'"
                )

        try:
            with self.transaction(db):
                equipment = crud.equipment.update(
                    db, equipment_id=equipment_id, equipment_in=obj_in
                )
                self.log_operation("update", equipment_id, {
                    "updates": obj_in.dict(exclude_unset=True)
                })
                return equipment
        except IntegrityError as e:
            identifier = None
            if obj_in.equipment_code:
                identifier = f"code='{obj_in.equipment_code}'"
            self.handle_integrity_error(
                e,
                identifier=identifier,
                operation="update"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update")

    def delete_equipment(self, db: Session, equipment_id: int) -> None:
        """Delete equipment by ID."""
        # First verify equipment exists
        try:
            obj = crud.equipment.get(db, equipment_id=equipment_id)
            if not obj:
                raise EquipmentNotFoundException(equipment_id=equipment_id)
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="verify_exists")

        try:
            with self.transaction(db):
                deleted = crud.equipment.delete(db, equipment_id=equipment_id)
                if not deleted:
                    raise EquipmentNotFoundException(equipment_id=equipment_id)
                self.log_operation("delete", equipment_id)
        except (EquipmentNotFoundException, DuplicateResourceException,
                ConstraintViolationException, ValidationException) as e:
            # Re-raise business exceptions as-is
            raise
        except IntegrityError as e:
            # Handle foreign key constraints
            raise ConstraintViolationException(
                message="Cannot delete equipment with associated records"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="delete")


equipment_service = EquipmentService()