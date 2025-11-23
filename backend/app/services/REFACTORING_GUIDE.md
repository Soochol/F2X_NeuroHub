# Service Refactoring Guide

This guide documents how to refactor service classes to use the BaseService pattern for improved maintainability and consistency.

## Overview

The `BaseService` class provides common functionality for all service classes:
- Transaction management with automatic rollback
- Centralized error handling for SQLAlchemy exceptions
- Logging helpers for operations and errors
- Business rule validation utilities
- Type-safe generic implementation

## Benefits

1. **DRY Principle**: Eliminates duplicate error handling code across services
2. **Consistency**: Ensures all services handle errors and logging uniformly
3. **Maintainability**: Changes to error handling logic only need to be made once
4. **Type Safety**: Generic typing ensures compile-time type checking
5. **Debugging**: Centralized logging makes debugging easier

## Migration Steps

### 1. Import BaseService and Update Class Definition

**Before:**
```python
from app.core.exceptions import (
    DuplicateResourceException,
    ValidationException,
    DatabaseException,
    # ... other exceptions
)

class MyService:
    """Service for managing entities."""
    pass
```

**After:**
```python
from app.services.base_service import BaseService
from app.models.my_model import MyModel
from app.core.exceptions import (
    MyModelNotFoundException,
    ValidationException,
    BusinessRuleException,
)

class MyService(BaseService[MyModel]):
    """Service for managing entities."""

    def __init__(self):
        super().__init__(model_name="MyModel")
```

### 2. Replace Manual Error Handling

**Before:**
```python
def create_entity(self, db: Session, obj_in: EntityCreate) -> EntityInDB:
    try:
        return crud.create(db, obj_in=obj_in)
    except IntegrityError as e:
        error_str = str(e).lower()
        if "unique constraint" in error_str:
            raise DuplicateResourceException(
                resource_type="Entity",
                identifier=f"name={obj_in.name}"
            )
        if "foreign key" in error_str:
            raise ConstraintViolationException(
                message="Invalid foreign key reference"
            )
        raise DatabaseException(message=f"Database error: {str(e)}")
    except SQLAlchemyError as e:
        raise DatabaseException(message=f"Database operation failed: {str(e)}")
```

**After:**
```python
def create_entity(self, db: Session, obj_in: EntityCreate) -> EntityInDB:
    try:
        entity = crud.create(db, obj_in=obj_in)
        self.log_operation("create", entity.id, {"name": obj_in.name})
        return entity
    except IntegrityError as e:
        identifier = f"name={obj_in.name}" if hasattr(obj_in, 'name') else None
        self.handle_integrity_error(e, identifier=identifier, operation="create")
    except SQLAlchemyError as e:
        self.handle_sqlalchemy_error(e, operation="create")
```

### 3. Use Transaction Context Manager

**Before:**
```python
def complex_operation(self, db: Session, data: dict):
    try:
        # Multiple operations
        obj1 = crud.create(db, obj1_in)
        obj2 = crud.create(db, obj2_in)
        db.commit()
        return obj1, obj2
    except Exception as e:
        db.rollback()
        raise
```

**After:**
```python
def complex_operation(self, db: Session, data: dict):
    with self.transaction(db):
        # Multiple operations - automatically committed or rolled back
        obj1 = crud.create(db, obj1_in)
        obj2 = crud.create(db, obj2_in)
        self.log_operation("complex_operation", details={"created": 2})
        return obj1, obj2
```

### 4. Use Business Rule Validation

**Before:**
```python
def process_entity(self, db: Session, entity_id: int):
    entity = crud.get(db, entity_id)
    if not entity:
        raise EntityNotFoundException(entity_id)

    if entity.status != "READY":
        raise BusinessRuleException(
            message=f"Entity must be in READY status, got {entity.status}"
        )

    # Process entity...
```

**After:**
```python
def process_entity(self, db: Session, entity_id: int):
    entity = crud.get(db, entity_id)
    entity = self.validate_not_none(entity, entity_id, EntityNotFoundException)

    self.check_business_rule(
        entity.status == "READY",
        f"Entity must be in READY status, got {entity.status}"
    )

    # Process entity...
```

### 5. Add Structured Logging

**Before:**
```python
def update_entity(self, db: Session, entity_id: int, obj_in: EntityUpdate):
    try:
        entity = crud.update(db, entity_id, obj_in)
        return entity
    except Exception as e:
        print(f"Error updating entity {entity_id}: {e}")
        raise
```

**After:**
```python
def update_entity(self, db: Session, entity_id: int, obj_in: EntityUpdate):
    try:
        entity = crud.update(db, entity_id, obj_in)
        self.log_operation("update", entity_id, {"changes": obj_in.dict(exclude_unset=True)})
        return entity
    except Exception as e:
        self.log_error(e, "update", {"entity_id": entity_id})
        raise
```

## Complete Example: Equipment Service

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.base_service import BaseService
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentInDB
from app.core.exceptions import EquipmentNotFoundException, ValidationException
from app import crud


class EquipmentService(BaseService[Equipment]):
    """Service for managing Equipment entities."""

    def __init__(self):
        super().__init__(model_name="Equipment")

    def get_equipment(self, db: Session, equipment_id: int) -> EquipmentInDB:
        """Get equipment by ID."""
        try:
            equipment = crud.equipment.get(db, equipment_id)
            return self.validate_not_none(
                equipment, equipment_id, EquipmentNotFoundException
            )
        except EquipmentNotFoundException:
            raise
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="get")

    def create_equipment(
        self,
        db: Session,
        equipment_in: EquipmentCreate
    ) -> EquipmentInDB:
        """Create new equipment."""
        try:
            with self.transaction(db):
                equipment = crud.equipment.create(db, obj_in=equipment_in)
                self.log_operation(
                    "create",
                    equipment.id,
                    {"code": equipment_in.equipment_code}
                )
                return equipment
        except IntegrityError as e:
            self.handle_integrity_error(
                e,
                identifier=f"code={equipment_in.equipment_code}",
                operation="create"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="create")

    def update_equipment(
        self,
        db: Session,
        equipment_id: int,
        equipment_in: EquipmentUpdate
    ) -> EquipmentInDB:
        """Update equipment."""
        # Check existence first
        equipment = self.get_equipment(db, equipment_id)

        try:
            updated = crud.equipment.update(db, equipment_id, equipment_in)
            self.log_operation(
                "update",
                equipment_id,
                {"changes": equipment_in.dict(exclude_unset=True)}
            )
            return updated
        except IntegrityError as e:
            self.handle_integrity_error(
                e,
                identifier=f"id={equipment_id}",
                operation="update"
            )
        except SQLAlchemyError as e:
            self.handle_sqlalchemy_error(e, operation="update")

    def validate_equipment_status(
        self,
        db: Session,
        equipment_id: int
    ) -> bool:
        """Validate equipment is ready for use."""
        equipment = self.get_equipment(db, equipment_id)

        # Use business rule checking
        self.check_business_rule(
            equipment.status == "ACTIVE",
            f"Equipment {equipment.equipment_code} is not active"
        )

        self.check_business_rule(
            equipment.last_maintenance_date is not None,
            f"Equipment {equipment.equipment_code} has no maintenance record"
        )

        return True


equipment_service = EquipmentService()
```

## Services to Refactor

### Priority 1 (Completed)
- [x] `lot_service.py` - Refactored to use BaseService
- [x] `serial_service.py` - Refactored to use BaseService
- [ ] `wip_service.py` - Needs refactoring (validation logic, no class structure)

### Priority 2 (High complexity)
- [ ] `process_service.py` - Complex operations, would benefit from transaction management
- [ ] `equipment_service.py` - Standard CRUD with validation
- [ ] `analytics_service.py` - Read-heavy, less error handling needed

### Priority 3 (Lower complexity)
- [ ] `notification_service.py` - External service calls
- [ ] `printer_service.py` - Hardware integration

## Testing After Refactoring

1. **Unit Tests**: Ensure all existing tests pass
2. **Error Scenarios**: Test duplicate keys, foreign key violations
3. **Transaction Rollback**: Verify failed operations don't leave partial data
4. **Logging**: Check logs are properly formatted and informative
5. **Performance**: Ensure no performance degradation

## Best Practices

1. **Keep business logic in service**: BaseService handles infrastructure concerns
2. **Use descriptive operation names**: For logging and debugging
3. **Include context in errors**: Pass relevant IDs and values to error handlers
4. **Test error paths**: Ensure error handling works as expected
5. **Document complex operations**: Add comments for non-obvious business rules

## FAQ

**Q: When should I use `transaction()` context manager?**
A: Use it when performing multiple database operations that should be atomic.

**Q: Should I catch all exceptions in service methods?**
A: Only catch exceptions you can handle. Let unexpected errors bubble up.

**Q: How do I handle custom business exceptions?**
A: Use `check_business_rule()` for validation, raise custom exceptions for complex cases.

**Q: Should every service inherit from BaseService?**
A: Yes, for consistency. Even read-only services benefit from logging and error handling.