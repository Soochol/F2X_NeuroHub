"""
Pydantic schemas for the Lot entity.

This module provides request/response schemas for lot management in the F2X NeuroHub
Manufacturing Execution System. It includes validation for LOT number format,
quantities, status lifecycle, shift enumeration, and computed quality metrics.

Schemas:
    - LotStatus: Enumeration of LOT lifecycle statuses
    - Shift: Enumeration of production shifts
    - LotBase: Base schema with core fields and validators
    - LotCreate: Schema for creating new LOT records
    - LotUpdate: Schema for updating existing LOT records
    - LotInDB: Schema for database response with relationships

Key Features:
    - LotStatus enum: CREATED, IN_PROGRESS, COMPLETED, CLOSED
    - Shift enum: D (Day), N (Night)
    - LOT number format validation: WF-KR-YYMMDD{D|N}-nnn
    - Target quantity validation: max 100 units
    - Nested ProductModel schema in InDB
    - Computed fields: defect_rate, pass_rate
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class LotStatus(str, Enum):
    """
    LOT lifecycle status enumeration.

    Attributes:
        CREATED: Initial state after LOT creation
        IN_PROGRESS: Production is actively underway
        COMPLETED: All production units finished
        CLOSED: Final state, LOT is archived
    """
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class Shift(str, Enum):
    """
    Production shift enumeration.

    Attributes:
        DAY: Day shift (06:00-18:00)
        NIGHT: Night shift (18:00-06:00)
    """
    DAY = "D"
    NIGHT = "N"


class ProductModelSchema(BaseModel):
    """
    Nested ProductModel schema for relationship data.

    Attributes:
        id: Product model identifier
        model_code: Unique model identifier (e.g., NH-F2X-001)
        model_name: Product name (Korean/English)
        category: Product category or family
        production_cycle_days: Expected production cycle duration in days
        status: Product lifecycle status (ACTIVE, INACTIVE, DISCONTINUED)
    """
    id: int
    model_code: str
    model_name: str
    category: Optional[str] = None
    production_cycle_days: Optional[int] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ProductionLineSchema(BaseModel):
    """
    Nested ProductionLine schema for relationship data.

    Attributes:
        id: Production line identifier
        line_code: Unique line identifier (e.g., 'LINE-A')
        line_name: Display name for the line (e.g., '조립라인 A')
        cycle_time_sec: Cycle time in seconds for one unit (optional)
        is_active: Whether this line is currently operational
    """
    id: int
    line_code: str
    line_name: str
    cycle_time_sec: Optional[int] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LotBase(BaseModel):
    """
    Base schema for Lot with core fields and validation.

    Attributes:
        product_model_id: Foreign key to product_models table (required)
        production_line_id: Foreign key to production_lines table (required for LOT number generation)
        production_date: Scheduled/actual production date (required)
        shift: Production shift (D for Day, N for Night)
        target_quantity: Target production quantity (max 100 units per LOT)
        status: LOT lifecycle status (default: CREATED)

    Validators:
        - validate_shift: Ensures shift is 'D' or 'N'
        - validate_target_quantity: Ensures 1 <= target_quantity <= 100
        - validate_status: Ensures valid LOT status
    """

    product_model_id: int = Field(..., gt=0, description="Product model identifier")
    production_line_id: Optional[int] = Field(
        default=None, description="Production line identifier (required for LOT number generation, optional for legacy data)"
    )
    production_date: date = Field(..., description="Scheduled/actual production date")
    shift: str = Field(
        ...,
        pattern="^[DN]$",
        description="Production shift: D (Day) or N (Night)"
    )
    target_quantity: int = Field(
        ...,
        ge=1,
        le=100,
        description="Target production quantity (1-100 units per LOT)"
    )
    status: str = Field(
        default=LotStatus.CREATED,
        description="LOT lifecycle status: CREATED, IN_PROGRESS, COMPLETED, CLOSED"
    )

    @field_validator("shift", mode="before")
    @classmethod
    def validate_shift(cls, v: str) -> str:
        """
        Validate and convert shift to valid enumeration value.

        Args:
            v: Input value for shift

        Returns:
            Shift value ('D' or 'N')

        Raises:
            ValueError: If value is not a valid shift
        """
        if isinstance(v, Shift):
            return v.value
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper in ("D", "N"):
                return v_upper
            try:
                # Try to match by enum name (DAY, NIGHT)
                shift_enum = Shift[v_upper]
                return shift_enum.value
            except KeyError:
                raise ValueError(
                    f"shift must be 'D' (Day) or 'N' (Night), got '{v}'"
                )
        raise ValueError(f"shift must be a string, got {type(v)}")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        Validate and convert status to valid enumeration value.

        Args:
            v: Input value for status

        Returns:
            LotStatus value

        Raises:
            ValueError: If value is not a valid status
        """
        if isinstance(v, LotStatus):
            return v.value
        if isinstance(v, str):
            try:
                status_enum = LotStatus(v.upper())
                return status_enum.value
            except ValueError:
                valid_statuses = [e.value for e in LotStatus]
                raise ValueError(
                    f"status must be one of {valid_statuses}, got '{v}'"
                )
        raise ValueError(f"status must be a string, got {type(v)}")

    @field_validator("target_quantity")
    @classmethod
    def validate_target_quantity(cls, v: int) -> int:
        """
        Validate target quantity constraints.

        Args:
            v: Target quantity value

        Returns:
            Validated target quantity

        Raises:
            ValueError: If quantity is outside valid range
        """
        if not isinstance(v, int):
            raise ValueError("target_quantity must be an integer")
        if v < 1:
            raise ValueError("target_quantity must be at least 1")
        if v > 100:
            raise ValueError("target_quantity cannot exceed 100 units per LOT")
        return v


class LotCreate(LotBase):
    """
    Schema for creating new Lot records.

    Inherits all validation from LotBase.
    All required fields must be provided on creation.
    Validates that production_line_id is provided for LOT number generation.
    """

    @field_validator('production_line_id')
    @classmethod
    def validate_production_line_required(cls, v):
        """Ensure production_line_id is provided for new LOT creation."""
        if v is None:
            raise ValueError('production_line_id is required for creating new LOTs')
        if v <= 0:
            raise ValueError('production_line_id must be greater than 0')
        return v


class LotUpdate(BaseModel):
    """
    Schema for updating Lot records.

    All fields are optional to allow partial updates.
    Validators ensure consistency when fields are provided.

    Attributes:
        production_line_id: Updated production line (optional)
        production_date: Updated production date (optional)
        shift: Updated shift (optional)
        target_quantity: Updated target quantity (optional)
        actual_quantity: Updated actual quantity (optional)
        passed_quantity: Updated passed quantity (optional)
        failed_quantity: Updated failed quantity (optional)
        status: Updated LOT status (optional)
        closed_at: Closure timestamp (optional)
    """

    production_line_id: Optional[int] = Field(
        None,
        gt=0,
        description="Production line identifier"
    )
    production_date: Optional[date] = Field(
        None,
        description="Scheduled/actual production date"
    )
    shift: Optional[str] = Field(
        None,
        pattern="^[DN]$",
        description="Production shift: D (Day) or N (Night)"
    )
    target_quantity: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Target production quantity (1-100 units per LOT)"
    )
    actual_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Actual units produced in this LOT"
    )
    passed_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Number of units that passed all quality checks"
    )
    failed_quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Number of units that failed quality checks"
    )
    status: Optional[str] = Field(
        None,
        description="LOT lifecycle status: CREATED, IN_PROGRESS, COMPLETED, CLOSED"
    )
    closed_at: Optional[datetime] = Field(
        None,
        description="LOT closure/completion timestamp"
    )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("shift", mode="before")
    @classmethod
    def validate_shift(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and convert shift to valid enumeration value.

        Args:
            v: Input value for shift

        Returns:
            Shift value ('D' or 'N') or None
        """
        if v is None:
            return None
        if isinstance(v, Shift):
            return v.value
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper in ("D", "N"):
                return v_upper
            try:
                shift_enum = Shift[v_upper]
                return shift_enum.value
            except KeyError:
                raise ValueError(
                    f"shift must be 'D' (Day) or 'N' (Night), got '{v}'"
                )
        raise ValueError(f"shift must be a string, got {type(v)}")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and convert status to valid enumeration value.

        Args:
            v: Input value for status

        Returns:
            LotStatus value or None
        """
        if v is None:
            return None
        if isinstance(v, LotStatus):
            return v.value
        if isinstance(v, str):
            try:
                status_enum = LotStatus(v.upper())
                return status_enum.value
            except ValueError:
                valid_statuses = [e.value for e in LotStatus]
                raise ValueError(
                    f"status must be one of {valid_statuses}, got '{v}'"
                )
        raise ValueError(f"status must be a string, got {type(v)}")

    @field_validator("target_quantity")
    @classmethod
    def validate_target_quantity(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate target quantity constraints.

        Args:
            v: Target quantity value

        Returns:
            Validated target quantity or None
        """
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError("target_quantity must be an integer")
        if v < 1:
            raise ValueError("target_quantity must be at least 1")
        if v > 100:
            raise ValueError("target_quantity cannot exceed 100 units per LOT")
        return v

    @field_validator("actual_quantity")
    @classmethod
    def validate_actual_quantity(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate actual quantity constraints.

        Args:
            v: Actual quantity value

        Returns:
            Validated actual quantity or None
        """
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError("actual_quantity must be an integer")
        if v < 0:
            raise ValueError("actual_quantity cannot be negative")
        return v

    @field_validator("passed_quantity")
    @classmethod
    def validate_passed_quantity(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate passed quantity constraints.

        Args:
            v: Passed quantity value

        Returns:
            Validated passed quantity or None
        """
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError("passed_quantity must be an integer")
        if v < 0:
            raise ValueError("passed_quantity cannot be negative")
        return v

    @field_validator("failed_quantity")
    @classmethod
    def validate_failed_quantity(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate failed quantity constraints.

        Args:
            v: Failed quantity value

        Returns:
            Validated failed quantity or None
        """
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError("failed_quantity must be an integer")
        if v < 0:
            raise ValueError("failed_quantity cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_quantity_consistency(self) -> "LotUpdate":
        """
        Validate quantity consistency constraints.

        When provided, ensures:
        - actual_quantity >= passed_quantity
        - actual_quantity >= failed_quantity
        - actual_quantity <= target_quantity
        - passed_quantity + failed_quantity <= actual_quantity

        Returns:
            Self instance if valid

        Raises:
            ValueError: If quantities are inconsistent
        """
        if self.actual_quantity is not None:
            if self.target_quantity is not None:
                if self.actual_quantity > self.target_quantity:
                    raise ValueError(
                        "actual_quantity cannot exceed target_quantity"
                    )

            if self.passed_quantity is not None:
                if self.passed_quantity > self.actual_quantity:
                    raise ValueError(
                        "passed_quantity cannot exceed actual_quantity"
                    )

            if self.failed_quantity is not None:
                if self.failed_quantity > self.actual_quantity:
                    raise ValueError(
                        "failed_quantity cannot exceed actual_quantity"
                    )

            if (self.passed_quantity is not None and
                    self.failed_quantity is not None):
                if (self.passed_quantity + self.failed_quantity >
                        self.actual_quantity):
                    raise ValueError(
                        "passed_quantity + failed_quantity cannot exceed actual_quantity"
                    )

        return self


class LotInDB(LotBase):
    """
    Schema for Lot database response with relationships and computed fields.

    Extends LotBase with database-generated fields, nested relationships, and
    computed quality metrics (defect_rate and pass_rate).

    Attributes:
        id: Primary key identifier
        lot_number: Auto-generated LOT identifier (WF-KR-YYMMDD{D|N}-nnn)
        production_line_id: Production line identifier (optional for backward compatibility)
        actual_quantity: Actual units produced in this LOT
        passed_quantity: Number of units that passed all quality checks
        failed_quantity: Number of units that failed quality checks
        created_at: LOT creation timestamp
        updated_at: Last modification timestamp
        closed_at: LOT closure/completion timestamp (optional)
        product_model: Nested ProductModel relationship data
        defect_rate: Calculated defect rate percentage (optional)
        pass_rate: Calculated pass rate percentage (optional)

    Configuration:
        - Uses from_attributes=True for SQLAlchemy ORM compatibility
        - All fields are read-only at API level
    """

    id: int = Field(..., description="LOT identifier")
    lot_number: str = Field(
        ...,
        pattern="^[A-Z]+-[A-Z0-9-]+-[0-9]{6}[DN]-[0-9]{3}$",
        description="Auto-generated LOT identifier ({model_prefix}-{line_code}-YYMMDD{D|N}-nnn)"
    )
    actual_quantity: int = Field(
        ...,
        ge=0,
        description="Actual units produced in this LOT"
    )
    passed_quantity: int = Field(
        ...,
        ge=0,
        description="Number of units that passed all quality checks"
    )
    failed_quantity: int = Field(
        ...,
        ge=0,
        description="Number of units that failed quality checks"
    )
    created_at: datetime = Field(..., description="LOT creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    closed_at: Optional[datetime] = Field(
        None,
        description="LOT closure/completion timestamp"
    )
    product_model: Optional[ProductModelSchema] = Field(
        None,
        description="Nested ProductModel relationship data"
    )
    production_line: Optional[ProductionLineSchema] = Field(
        None,
        description="Nested ProductionLine relationship data"
    )
    defect_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Defect rate percentage (0-100) or None if no actual quantity"
    )
    pass_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Pass rate percentage (0-100) or None if no actual quantity"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("defect_rate", mode="before")
    @classmethod
    def calculate_defect_rate(cls, v: Optional[float], info) -> Optional[float]:
        """
        Calculate defect_rate from failed_quantity and actual_quantity if not provided.

        Defect rate = (failed_quantity / actual_quantity) * 100

        Args:
            v: defect_rate value
            info: Validation info with other field values

        Returns:
            Defect rate percentage (rounded to 2 decimals) or None if no actual quantity
        """
        if v is not None:
            return v

        # Try to calculate from quantities
        data = info.data
        failed_quantity = data.get("failed_quantity", 0)
        actual_quantity = data.get("actual_quantity", 0)

        if actual_quantity == 0:
            return None

        return round((failed_quantity / actual_quantity) * 100, 2)

    @field_validator("pass_rate", mode="before")
    @classmethod
    def calculate_pass_rate(cls, v: Optional[float], info) -> Optional[float]:
        """
        Calculate pass_rate from passed_quantity and actual_quantity if not provided.

        Pass rate = (passed_quantity / actual_quantity) * 100

        Args:
            v: pass_rate value
            info: Validation info with other field values

        Returns:
            Pass rate percentage (rounded to 2 decimals) or None if no actual quantity
        """
        if v is not None:
            return v

        # Try to calculate from quantities
        data = info.data
        passed_quantity = data.get("passed_quantity", 0)
        actual_quantity = data.get("actual_quantity", 0)

        if actual_quantity == 0:
            return None

        return round((passed_quantity / actual_quantity) * 100, 2)
