# Service Refactoring Checklist

## Overview

This document tracks the progress of refactoring all service classes to inherit from `BaseService` for improved code reusability, consistency, and maintainability.

## Refactoring Status

### ✅ Already Refactored

1. **LotService** (`lot_service.py`)
   - Inherits from `BaseService[Lot]`
   - Uses base transaction management
   - Leverages centralized error handling
   - Completed: 2024-11

2. **SerialService** (`serial_service.py`)
   - Inherits from `BaseService[Serial]`
   - Uses base validation methods
   - Implements proper error mapping
   - Completed: 2024-11

### 🔄 Pending Refactoring

1. **ProcessService** (`process_service.py`) - HIGH PRIORITY
   - Current: Class-based, custom error handling
   - Size: Large (~700 lines)
   - Complexity: High (Start/Complete operations)
   - Target: Inherit from `BaseService[Process]`

2. **WIPService** (`wip_service.py`) - MEDIUM PRIORITY
   - Current: Function-based with some class structure
   - Size: Medium (~320 lines)
   - Complexity: Medium (validation functions)
   - Target: Convert to full class with `BaseService[WIPItem]`

3. **EquipmentService** (`equipment_service.py`) - MEDIUM PRIORITY
   - Current: Class-based, minimal error handling
   - Size: Small (~170 lines)
   - Complexity: Low (CRUD operations)
   - Target: Inherit from `BaseService[Equipment]`

4. **AnalyticsService** (`analytics_service.py`) - LOW PRIORITY
   - Current: Class-based, focused on queries
   - Size: Large (~850 lines)
   - Complexity: Medium (reporting queries)
   - Target: Inherit from `BaseService[ProcessData]`

### ✨ Already Using BaseService (No Action Needed)

1. **PrinterService** (`printer_service.py`)
   - Already optimized with proper patterns
   - Uses async operations appropriately

2. **UserService** (`user_service.py`)
   - Authentication focused, different pattern
   - Best kept separate from BaseService

## Steps to Refactor a Service

### 1. Pre-Refactoring Analysis
- [ ] Review current service implementation
- [ ] Identify all public methods
- [ ] Document current error handling patterns
- [ ] Note any special business logic
- [ ] Check for existing tests

### 2. Create Service Class Structure
```python
from app.services.base_service import BaseService
from app.models.{model} import {Model}

class {Model}Service(BaseService[{Model}]):
    def __init__(self):
        super().__init__(model_name="{Model}")
```

### 3. Refactor Error Handling
- [ ] Replace custom try/except blocks with base methods
- [ ] Use `self.handle_integrity_error()` for IntegrityError
- [ ] Use `self.handle_sqlalchemy_error()` for SQLAlchemyError
- [ ] Use `self.transaction()` context manager

### 4. Refactor Common Patterns

#### Before:
```python
try:
    obj = crud.model.create(db, obj_in=obj_in)
    db.commit()
    return obj
except IntegrityError as e:
    db.rollback()
    if "unique" in str(e):
        raise DuplicateResourceException(...)
    raise DatabaseException(...)
```

#### After:
```python
try:
    with self.transaction(db):
        obj = crud.model.create(db, obj_in=obj_in)
        self.log_operation("create", obj.id)
        return obj
except IntegrityError as e:
    self.handle_integrity_error(e, resource_type="Model", identifier=obj_in.name)
```

### 5. Leverage Base Methods
- [ ] Use `self.validate_not_none()` for existence checks
- [ ] Use `self.check_business_rule()` for validations
- [ ] Use `self.log_operation()` for audit logging
- [ ] Use `self.log_error()` for error logging

### 6. Update Method Signatures
- [ ] Ensure consistent parameter naming
- [ ] Add type hints where missing
- [ ] Update docstrings to match base patterns

### 7. Testing and Validation
- [ ] Run existing unit tests
- [ ] Verify error messages are consistent
- [ ] Test transaction rollback behavior
- [ ] Validate logging output
- [ ] Check performance impact (should be minimal)

### 8. Documentation
- [ ] Update method docstrings
- [ ] Add refactoring note in module docstring
- [ ] Document any behavior changes
- [ ] Update API documentation if needed

## Validation Checklist

### Code Quality
- [ ] No duplicate error handling code
- [ ] Consistent error messages
- [ ] Proper transaction boundaries
- [ ] Appropriate logging levels
- [ ] Type hints on all methods

### Functionality
- [ ] All existing features work
- [ ] Error handling is consistent
- [ ] Transactions rollback properly
- [ ] Logging captures operations
- [ ] Performance unchanged or improved

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Error scenarios tested
- [ ] Transaction rollback tested
- [ ] Concurrent access handled

## Benefits of Refactoring

1. **Code Reusability**
   - Eliminate duplicate error handling
   - Shared transaction management
   - Common validation patterns

2. **Consistency**
   - Uniform error messages
   - Standardized logging
   - Predictable behavior

3. **Maintainability**
   - Central place for common logic
   - Easier to add new features
   - Simpler debugging

4. **Type Safety**
   - Generic typing with BaseService[T]
   - Better IDE support
   - Compile-time checks

5. **Testing**
   - Easier to mock base methods
   - Consistent test patterns
   - Better coverage

## Migration Priority

### High Priority (Do First)
1. **ProcessService** - Core functionality, will benefit most
2. **WIPService** - Needs class structure anyway

### Medium Priority
3. **EquipmentService** - Simple, good practice case
4. **AnalyticsService** - Can benefit from error handling

### Low Priority
- Services that don't fit the pattern
- Services with special requirements
- Third-party integrations

## Notes and Considerations

1. **Breaking Changes**: Refactoring should NOT introduce breaking changes to public APIs
2. **Performance**: BaseService adds minimal overhead (context managers, logging)
3. **Exceptions**: Some services may not fit the BaseService pattern (e.g., auth services)
4. **Testing**: Ensure comprehensive test coverage before and after refactoring
5. **Rollback Plan**: Keep backups and be ready to revert if issues arise

## Progress Tracking

| Service | Status | Started | Completed | Notes |
|---------|--------|---------|-----------|-------|
| LotService | ✅ Done | 2024-11 | 2024-11 | Fully refactored |
| SerialService | ✅ Done | 2024-11 | 2024-11 | Fully refactored |
| WIPService | ✅ Done | 2024-11 | 2024-11 | Converted to class-based with BaseService |
| ProcessService | 🔄 Pending | - | - | High priority |
| EquipmentService | 🔄 Pending | - | - | Simple refactor |
| AnalyticsService | 🔄 Pending | - | - | Low priority |
| PrinterService | ⏭️ Skip | - | - | Already optimized |
| UserService | ⏭️ Skip | - | - | Different pattern |

## References

- `app/services/base_service.py` - BaseService implementation
- `app/services/lot_service.py` - Example of refactored service
- `app/services/serial_service.py` - Example of refactored service
- `app/core/exceptions.py` - Custom exception definitions