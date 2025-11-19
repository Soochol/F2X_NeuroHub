"""
Pydantic schemas for the Equipment entity.

This module provides request/response schemas for equipment management in the F2X NeuroHub
Manufacturing Execution System. It includes validation for equipment codes, types,
maintenance tracking, and relationships with processes and production lines.

Schemas:
    - EquipmentBase: Base schema with core fields and validators
    - EquipmentCreate: Schema for creating new equipment records
    - EquipmentUpdate: Schema for updating existing equipment records
    - EquipmentInDB: Schema for database response with all fields
    - EquipmentResponse: Schema for API response with relationships

Key Features:
    - Equipment code format validation (alphanumeric and hyphens)
    - Equipment type classification
    - Maintenance date tracking
    - Foreign key relationships to Process and ProductionLine
    - Manufacturer and model information
"""

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class ProcessSummarySchema(BaseModel):
    """
    Summary schema for Process relationship in Equipment response.

    Provides basic process information for nested display.

    Attributes:
        id: Process identifier
        process_number: Process sequence number (1-8)
        process_code: Unique process code
        process_name_en: English process name
        process_name_ko: Korean process name
    """
    id: int
    process_number: int
    process_code: str
    process_name_en: str
    process_name_ko: str

    model_config = ConfigDict(from_attributes=True)


class ProductionLineSummarySchema(BaseModel):
    """
    Summary schema for ProductionLine relationship in Equipment response.

    Provides basic production line information for nested display.

    Attributes:
        id: Production line identifier
        line_code: Unique line identifier
        line_name: Display name for the line
        is_active: Whether this line is currently operational
    """
    id: int
    line_code: str
    line_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class EquipmentBase(BaseModel):
    """
    Base schema for Equipment with core fields and validation.

    Attributes:
        equipment_code: Unique equipment identifier (e.g., 'LASER-001')
        equipment_name: Display name (e.g., '레이저마킹기-001')
        equipment_type: Type classification (e.g., 'LASER_MARKER', 'SENSOR', 'ROBOT')
        process_id: Foreign key to processes table (optional)
        production_line_id: Foreign key to production_lines table (optional)
        location: Physical location within facility (optional)
        manufacturer: Equipment manufacturer name (optional)
        model_number: Manufacturer's model number (optional)
        serial_number: Equipment serial number (optional)
        install_date: Date equipment was installed (optional)
        last_maintenance_date: Last maintenance timestamp (optional)
        next_maintenance_date: Scheduled next maintenance timestamp (optional)
        is_active: Whether equipment is currently operational (default: True)

    Validators:
        - validate_equipment_code: Ensures equipment_code format is valid
        - validate_equipment_type: Ensures equipment_type is uppercased
        - validate_maintenance_dates: Ensures next_maintenance_date >= last_maintenance_date
    """

    equipment_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique equipment identifier (e.g., 'LASER-001')"
    )
    equipment_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Display name (e.g., '레이저마킹기-001')"
    )
    equipment_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type classification (e.g., 'LASER_MARKER', 'SENSOR', 'ROBOT')"
    )
    process_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Primary process this equipment is used for"
    )
    production_line_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Production line where equipment is located"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Physical location within facility"
    )
    manufacturer: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Equipment manufacturer name"
    )
    model_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Manufacturer's model number"
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Equipment serial number"
    )
    install_date: Optional[date] = Field(
        default=None,
        description="Date equipment was installed"
    )
    last_maintenance_date: Optional[datetime] = Field(
        default=None,
        description="Last maintenance timestamp"
    )
    next_maintenance_date: Optional[datetime] = Field(
        default=None,
        description="Scheduled next maintenance timestamp"
    )
    is_active: bool = Field(
        default=True,
        description="Whether equipment is currently operational"
    )

    @field_validator("equipment_code")
    @classmethod
    def validate_equipment_code(cls, value: str) -> str:
        """
        Validate equipment_code format.

        Ensures equipment code follows naming convention with alphanumeric
        characters and hyphens only.

        Args:
            value: Equipment code to validate

        Returns:
            Uppercase version of the equipment code

        Raises:
            ValueError: If equipment_code contains invalid characters
        """
        if not value:
            raise ValueError("equipment_code cannot be empty")

        # Check for valid characters (alphanumeric and hyphens)
        if not all(c.isalnum() or c == '-' for c in value):
            raise ValueError(
                "equipment_code can only contain alphanumeric characters and hyphens"
            )

        return value.upper()

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, value: str) -> str:
        """
        Validate and uppercase equipment_type.

        Args:
            value: Equipment type to validate

        Returns:
            Uppercase version of the equipment type

        Raises:
            ValueError: If equipment_type is empty or contains invalid characters
        """
        if not value:
            raise ValueError("equipment_type cannot be empty")

        # Check for valid characters (alphanumeric and underscores)
        if not all(c.isalnum() or c == '_' for c in value):
            raise ValueError(
                "equipment_type can only contain alphanumeric characters and underscores"
            )

        return value.upper()

    @model_validator(mode="after")
    def validate_maintenance_dates(self) -> "EquipmentBase":
        """
        Validate maintenance date consistency.

        Ensures next_maintenance_date >= last_maintenance_date when both are provided.

        Returns:
            Self instance if valid

        Raises:
            ValueError: If next_maintenance_date is before last_maintenance_date
        """
        if (self.last_maintenance_date is not None and
            self.next_maintenance_date is not None):
            if self.next_maintenance_date < self.last_maintenance_date:
                raise ValueError(
                    "next_maintenance_date must be greater than or equal to last_maintenance_date"
                )
        return self


class EquipmentCreate(EquipmentBase):
    """
    Schema for creating new Equipment records.

    Inherits all validation from EquipmentBase.
    All required fields must be provided on creation.

    Example:
        equipment_create = EquipmentCreate(
            equipment_code="LASER-001",
            equipment_name="레이저마킹기-001",
            equipment_type="LASER_MARKER",
            production_line_id=1,
            manufacturer="KEYENCE",
            model_number="MD-X1000"
        )
    """
    pass


class EquipmentUpdate(BaseModel):
    """
    Schema for updating Equipment records.

    All fields are optional to allow partial updates.
    Validators ensure consistency when fields are provided.

    Attributes:
        equipment_code: Updated equipment code (optional)
        equipment_name: Updated equipment name (optional)
        equipment_type: Updated equipment type (optional)
        process_id: Updated process assignment (optional)
        production_line_id: Updated production line assignment (optional)
        location: Updated location (optional)
        manufacturer: Updated manufacturer (optional)
        model_number: Updated model number (optional)
        serial_number: Updated serial number (optional)
        install_date: Updated install date (optional)
        last_maintenance_date: Updated last maintenance date (optional)
        next_maintenance_date: Updated next maintenance date (optional)
        is_active: Updated active status (optional)
    """

    equipment_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Unique equipment identifier"
    )
    equipment_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Display name for the equipment"
    )
    equipment_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Type classification"
    )
    process_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Primary process this equipment is used for"
    )
    production_line_id: Optional[int] = Field(
        default=None,
        gt=0,
        description="Production line where equipment is located"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Physical location within facility"
    )
    manufacturer: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Equipment manufacturer name"
    )
    model_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Manufacturer's model number"
    )
    serial_number: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Equipment serial number"
    )
    install_date: Optional[date] = Field(
        default=None,
        description="Date equipment was installed"
    )
    last_maintenance_date: Optional[datetime] = Field(
        default=None,
        description="Last maintenance timestamp"
    )
    next_maintenance_date: Optional[datetime] = Field(
        default=None,
        description="Scheduled next maintenance timestamp"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether equipment is currently operational"
    )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("equipment_code")
    @classmethod
    def validate_equipment_code(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate and uppercase equipment_code if provided.

        Args:
            value: Equipment code to validate

        Returns:
            Uppercase version of the equipment code or None

        Raises:
            ValueError: If equipment_code is provided but invalid
        """
        if value is None:
            return None

        if not value:
            raise ValueError("equipment_code cannot be empty")

        # Check for valid characters (alphanumeric and hyphens)
        if not all(c.isalnum() or c == '-' for c in value):
            raise ValueError(
                "equipment_code can only contain alphanumeric characters and hyphens"
            )

        return value.upper()

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate and uppercase equipment_type if provided.

        Args:
            value: Equipment type to validate

        Returns:
            Uppercase version of the equipment type or None

        Raises:
            ValueError: If equipment_type is provided but invalid
        """
        if value is None:
            return None

        if not value:
            raise ValueError("equipment_type cannot be empty")

        # Check for valid characters (alphanumeric and underscores)
        if not all(c.isalnum() or c == '_' for c in value):
            raise ValueError(
                "equipment_type can only contain alphanumeric characters and underscores"
            )

        return value.upper()


class EquipmentInDB(EquipmentBase):
    """
    Schema for Equipment database response with all fields.

    Includes read-only fields populated by the database such as IDs and
    timestamps. Used for returning full equipment details from API endpoints.

    Attributes:
        id: Primary key (auto-generated BIGSERIAL)
        created_at: Record creation timestamp (UTC timezone-aware)
        updated_at: Last update timestamp (UTC timezone-aware)
        All attributes from EquipmentBase

    Configuration:
        from_attributes: Enables Pydantic to populate from ORM model instances
    """

    id: int = Field(
        ...,
        gt=0,
        description="Primary key, auto-generated BIGSERIAL by database"
    )
    created_at: datetime = Field(
        ...,
        description="Record creation timestamp (UTC timezone-aware)"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp (UTC timezone-aware)"
    )

    model_config = ConfigDict(from_attributes=True)


class EquipmentResponse(EquipmentInDB):
    """
    Schema for Equipment API response with relationships.

    Extends EquipmentInDB with nested relationship data for process and production line.

    Attributes:
        process: Nested Process relationship data (optional)
        production_line: Nested ProductionLine relationship data (optional)
        needs_maintenance: Computed field indicating if maintenance is due
        All attributes from EquipmentInDB

    Configuration:
        - Uses from_attributes=True for SQLAlchemy ORM compatibility
    """

    process: Optional[ProcessSummarySchema] = Field(
        default=None,
        description="Nested Process relationship data"
    )
    production_line: Optional[ProductionLineSummarySchema] = Field(
        default=None,
        description="Nested ProductionLine relationship data"
    )
    needs_maintenance: bool = Field(
        default=False,
        description="Whether equipment needs maintenance (computed from dates)"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("needs_maintenance", mode="before")
    @classmethod
    def calculate_needs_maintenance(cls, v, info) -> bool:
        """
        Calculate needs_maintenance from next_maintenance_date if not provided.

        Args:
            v: needs_maintenance value
            info: Validation info with other field values

        Returns:
            True if maintenance is due, False otherwise
        """
        if v is not None and isinstance(v, bool):
            return v

        # Try to calculate from next_maintenance_date
        data = info.data
        next_maintenance_date = data.get("next_maintenance_date")

        if next_maintenance_date is None:
            return False

        return datetime.now(next_maintenance_date.tzinfo) >= next_maintenance_date
