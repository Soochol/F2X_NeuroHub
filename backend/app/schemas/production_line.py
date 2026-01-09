"""
Pydantic schemas for the ProductionLine entity.

This module provides request/response schemas for production line management in the F2X NeuroHub
Manufacturing Execution System. It includes validation for line codes, capacity constraints,
and location information.

Schemas:
    - ProductionLineBase: Base schema with core fields and validators
    - ProductionLineCreate: Schema for creating new production line records
    - ProductionLineUpdate: Schema for updating existing production line records
    - ProductionLineInDB: Schema for database response with all fields
    - ProductionLineResponse: Schema for API response with relationships

Key Features:
    - Line code format validation (alphanumeric, hyphens, and underscores)
    - Cycle time validation (positive integer)
    - Location and description fields
    - is_active status flag
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductionLineBase(BaseModel):
    """
    Base schema for ProductionLine with core fields and validation.

    Attributes:
        line_code: Unique line identifier (e.g., 'LINE-A')
        line_name: Display name for the line (e.g., '조립라인 A')
        description: Detailed description of the production line (optional)
        cycle_time_sec: Cycle time in seconds per unit (optional)
        location: Physical location (e.g., 'Building 1, Zone A') (optional)
        is_active: Whether this line is currently operational (default: True)

    Validators:
        - validate_line_code: Ensures line_code contains only alphanumeric, hyphens, and underscores
        - validate_cycle_time_sec: Ensures positive cycle time if provided
    """

    line_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique line identifier (e.g., 'LINE-A')"
    )
    line_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Display name for the line (e.g., '조립라인 A')"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of the production line"
    )
    cycle_time_sec: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cycle time in seconds per unit (optional)"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Physical location (e.g., 'Building 1, Zone A')"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this line is currently operational"
    )

    @field_validator("line_code")
    @classmethod
    def validate_line_code(cls, value: str) -> str:
        """
        Validate line_code format.

        Ensures line code follows naming convention with alphanumeric
        characters and hyphens only.

        Args:
            value: Line code to validate

        Returns:
            Uppercase version of the line code

        Raises:
            ValueError: If line_code contains invalid characters
        """
        if not value:
            raise ValueError("line_code cannot be empty")

        # Check for valid characters (alphanumeric, hyphens, and underscores)
        if not all(c.isalnum() or c in '-_' for c in value):
            raise ValueError(
                "line_code can only contain alphanumeric characters, hyphens, and underscores"
            )

        return value.upper()


class ProductionLineCreate(ProductionLineBase):
    """
    Schema for creating new ProductionLine records.

    Inherits all validation from ProductionLineBase.
    All required fields must be provided on creation.

    Example:
        production_line_create = ProductionLineCreate(
            line_code="LINE-A",
            line_name="조립라인 A",
            cycle_time_sec=60,
            location="Building 1, Zone A"
        )
    """
    pass


class ProductionLineUpdate(BaseModel):
    """
    Schema for updating ProductionLine records.

    All fields are optional to allow partial updates.
    Validators ensure consistency when fields are provided.

    Attributes:
        line_code: Updated line code (optional)
        line_name: Updated line name (optional)
        description: Updated description (optional)
        cycle_time_sec: Updated cycle time (optional)
        location: Updated location (optional)
        is_active: Updated active status (optional)
    """

    line_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Unique line identifier"
    )
    line_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Display name for the line"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of the production line"
    )
    cycle_time_sec: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cycle time in seconds per unit"
    )
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Physical location"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether this line is currently operational"
    )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("line_code")
    @classmethod
    def validate_line_code(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate and uppercase line_code if provided.

        Args:
            value: Line code to validate

        Returns:
            Uppercase version of the line code or None

        Raises:
            ValueError: If line_code is provided but invalid
        """
        if value is None:
            return None

        if not value:
            raise ValueError("line_code cannot be empty")

        # Check for valid characters (alphanumeric, hyphens, and underscores)
        if not all(c.isalnum() or c in '-_' for c in value):
            raise ValueError(
                "line_code can only contain alphanumeric characters, hyphens, and underscores"
            )

        return value.upper()


class ProductionLineInDB(ProductionLineBase):
    """
    Schema for ProductionLine database response with all fields.

    Includes read-only fields populated by the database such as IDs and
    timestamps. Used for returning full production line details from API endpoints.

    Attributes:
        id: Primary key (auto-generated BIGSERIAL)
        created_at: Record creation timestamp (UTC timezone-aware)
        updated_at: Last update timestamp (UTC timezone-aware)
        All attributes from ProductionLineBase

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


class EquipmentSummarySchema(BaseModel):
    """
    Summary schema for Equipment relationship in ProductionLine response.

    Provides basic equipment information for nested display.

    Attributes:
        id: Equipment identifier
        equipment_code: Unique equipment identifier
        equipment_name: Display name
        equipment_type: Type classification
        is_active: Whether equipment is currently operational
    """
    id: int
    equipment_code: str
    equipment_name: str
    equipment_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProductionLineResponse(ProductionLineInDB):
    """
    Schema for ProductionLine API response with relationships.

    Extends ProductionLineInDB with nested equipment relationship data.

    Attributes:
        equipment: List of equipment assigned to this production line
        All attributes from ProductionLineInDB

    Configuration:
        - Uses from_attributes=True for SQLAlchemy ORM compatibility
    """

    equipment: List[EquipmentSummarySchema] = Field(
        default_factory=list,
        description="List of equipment assigned to this production line"
    )

    model_config = ConfigDict(from_attributes=True)
