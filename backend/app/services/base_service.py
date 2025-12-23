"""
Base Service Class for F2X NeuroHub Services

This module provides a generic base service class that encapsulates common
functionality for all service classes, following the DRY (Don't Repeat Yourself)
principle and improving maintainability.

Features:
    - Generic type support for type safety
    - Common transaction management with context managers
    - Centralized error handling for SQLAlchemy exceptions
    - Logging helpers for operations
    - Exception mapping for database errors

Usage Example:
    ```python
    from app.services.base_service import BaseService
    from app.models.lot import Lot
    from app.schemas.lot import LotCreate, LotInDB

    class LotService(BaseService[Lot]):
        def __init__(self):
            super().__init__(model_name="Lot")

        def create_lot(self, db: Session, lot_in: LotCreate) -> LotInDB:
            try:
                with self.transaction(db):
                    lot = crud.lot.create(db, lot_in=lot_in)
                    self.log_operation(db, "create", lot.id)
                    return lot
            except IntegrityError as e:
                self.handle_integrity_error(e, resource_type="Lot", identifier=lot_in.lot_number)
    ```

Author: F2X NeuroHub Development Team
Date: 2024
"""

from typing import TypeVar, Generic, Optional, Any, ContextManager, Dict, Type
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InternalError
import logging
import traceback
from datetime import datetime

from app.core.exceptions import (
    DuplicateResourceException,
    ConstraintViolationException,
    DatabaseException,
    BusinessRuleException,
    ValidationException,
)

# Generic type variable for model classes
T = TypeVar('T')

class BaseService(Generic[T]):
    """
    Base service class providing common functionality for all services.

    This class implements common patterns for:
    - Transaction management
    - Error handling and mapping
    - Logging operations
    - Database exception handling

    Type Parameters:
        T: The model type this service manages (e.g., Lot, Serial, WIPItem)

    Attributes:
        model_name: Name of the model for logging and error messages
        logger: Logger instance for this service
    """

    def __init__(self, model_name: str = "Resource"):
        """
        Initialize the base service.

        Args:
            model_name: Name of the model/resource this service manages
        """
        self.model_name = model_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @contextmanager
    def transaction(self, db: Session) -> ContextManager[Session]:
        """
        Context manager for database transactions with automatic rollback on errors.

        Usage:
            ```python
            with self.transaction(db) as session:
                # Perform database operations
                crud.create(session, obj_in)
            # Transaction is automatically committed on success
            # or rolled back on exception
            ```

        Args:
            db: SQLAlchemy session

        Yields:
            The database session for operations

        Raises:
            Any exception that occurs during the transaction
        """
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            self.logger.error(f"Transaction failed: {str(e)}")
            raise

    def handle_integrity_error(
        self,
        e: IntegrityError,
        resource_type: Optional[str] = None,
        identifier: Optional[str] = None,
        operation: str = "operation"
    ) -> None:
        """
        Handle SQLAlchemy IntegrityError and convert to appropriate application exception.

        This method analyzes the error message to determine the type of integrity
        violation and raises the appropriate application-specific exception.

        Args:
            e: The IntegrityError exception
            resource_type: Type of resource (defaults to self.model_name)
            identifier: Resource identifier for error message
            operation: The operation that failed (create, update, delete)

        Raises:
            DuplicateResourceException: For unique constraint violations
            ConstraintViolationException: For foreign key violations
            DatabaseException: For other integrity errors
        """
        error_str = str(e).lower()
        resource_type = resource_type or self.model_name

        # Handle duplicate key/unique constraint violations
        if "unique constraint" in error_str or "duplicate" in error_str or "unique" in error_str:
            if identifier:
                raise DuplicateResourceException(
                    resource_type=resource_type,
                    identifier=identifier
                )
            else:
                # Try to extract field name from error message
                field_name = self._extract_field_from_error(error_str)
                raise DuplicateResourceException(
                    resource_type=resource_type,
                    identifier=field_name or "unknown"
                )

        # Handle foreign key constraint violations
        elif "foreign key" in error_str:
            if "delete" in operation.lower():
                raise ConstraintViolationException(
                    message=f"Cannot delete {resource_type}: has dependent records"
                )
            else:
                raise ConstraintViolationException(
                    message=f"Invalid reference in {resource_type} {operation}"
                )

        # Handle check constraint violations
        elif "check constraint" in error_str:
            raise ValidationException(
                message=f"Data validation failed for {resource_type}: check constraint violation ({error_str})"
            )

        # Handle not null constraint violations
        elif "not null" in error_str or "null value" in error_str:
            field_name = self._extract_field_from_error(error_str)
            raise ValidationException(
                message=f"Required field {field_name or 'unknown'} is missing for {resource_type}"
            )

        # Generic database integrity error
        else:
            raise DatabaseException(
                message=f"Database integrity error during {operation} of {resource_type}: {str(e)}"
            )

    def handle_sqlalchemy_error(
        self,
        e: SQLAlchemyError,
        operation: str = "operation",
        resource_type: Optional[str] = None
    ) -> None:
        """
        Handle general SQLAlchemy errors and convert to application exceptions.

        Args:
            e: The SQLAlchemyError exception
            operation: The operation that failed
            resource_type: Type of resource (defaults to self.model_name)

        Raises:
            DatabaseException: For all SQLAlchemy errors
        """
        resource_type = resource_type or self.model_name
        self.logger.error(f"Database error during {operation} of {resource_type}: {str(e)}")

        # Log full traceback for debugging
        self.logger.debug(f"Full traceback:\n{traceback.format_exc()}")

        raise DatabaseException(
            message=f"Database operation failed during {operation} of {resource_type}: {str(e)}"
        )

    def handle_internal_error(
        self,
        e: InternalError,
        resource_type: Optional[str] = None
    ) -> None:
        """
        Handle SQLAlchemy InternalError (often from database triggers/procedures).

        Args:
            e: The InternalError exception
            resource_type: Type of resource (defaults to self.model_name)

        Raises:
            BusinessRuleException: For business rule violations from triggers
            DatabaseException: For other internal errors
        """
        error_str = str(e)
        resource_type = resource_type or self.model_name

        # Check for known business rule violations from triggers
        if "Invalid status transition" in error_str:
            # Extract the actual error message from trigger
            msg = error_str.split("RaiseException) ")[-1].split("\n")[0] if "RaiseException)" in error_str else "Invalid status transition"
            raise BusinessRuleException(message=msg)

        # Generic internal error
        raise DatabaseException(
            message=f"Database internal error for {resource_type}: {str(e)}"
        )

    def log_operation(
        self,
        operation: str,
        entity_id: Any = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> None:
        """
        Log a service operation for audit and debugging purposes.

        Args:
            operation: Name of the operation (create, update, delete, etc.)
            entity_id: ID of the entity being operated on
            details: Additional details to log
            user_id: ID of the user performing the operation
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.__class__.__name__,
            "model": self.model_name,
            "operation": operation,
            "entity_id": entity_id,
        }

        if user_id:
            log_data["user_id"] = user_id

        if details:
            log_data["details"] = details

        self.logger.info(f"Service operation: {log_data}")

    def validate_not_none(
        self,
        obj: Optional[T],
        identifier: Any,
        exception_class: Type[Exception] = None
    ) -> T:
        """
        Validate that an object is not None, raising appropriate exception if it is.

        Args:
            obj: The object to validate
            identifier: Identifier for error message
            exception_class: Custom exception class to raise

        Returns:
            The validated object (guaranteed not None)

        Raises:
            The specified exception class or ValidationException
        """
        if obj is None:
            if exception_class:
                raise exception_class(identifier)
            else:
                raise ValidationException(
                    message=f"{self.model_name} with identifier {identifier} not found"
                )
        return obj

    def _extract_field_from_error(self, error_str: str) -> Optional[str]:
        """
        Try to extract field name from database error message.

        Args:
            error_str: The error message string

        Returns:
            Extracted field name or None
        """
        # Common patterns for field extraction
        patterns = [
            r'column[s]? "([^"]+)"',  # PostgreSQL
            r'column `([^`]+)`',      # MySQL
            r'field (\w+)',           # Generic
            r'constraint "(\w+)"',    # Constraint name
        ]

        import re
        for pattern in patterns:
            match = re.search(pattern, error_str, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def begin_nested_transaction(self, db: Session) -> ContextManager[Session]:
        """
        Begin a nested transaction (savepoint) for partial rollback support.

        Usage:
            ```python
            with self.begin_nested_transaction(db) as nested:
                # Operations that might fail
                pass
            # Only this nested part is rolled back on failure
            ```

        Args:
            db: SQLAlchemy session

        Returns:
            Context manager for nested transaction
        """
        return db.begin_nested()

    def log_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with context for debugging.

        Args:
            error: The exception that occurred
            operation: The operation during which the error occurred
            context: Additional context information
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "operation": operation,
            "model": self.model_name,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if context:
            error_data["context"] = context

        self.logger.error(f"Service error: {error_data}")
        self.logger.debug(f"Error traceback:\n{traceback.format_exc()}")

    def check_business_rule(
        self,
        condition: bool,
        error_message: str
    ) -> None:
        """
        Check a business rule condition and raise exception if violated.

        Args:
            condition: The condition that should be True
            error_message: Error message if condition is False

        Raises:
            BusinessRuleException: If condition is False
        """
        if not condition:
            self.logger.warning(f"Business rule violation: {error_message}")
            raise BusinessRuleException(message=error_message)