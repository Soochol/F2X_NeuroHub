"""
Pydantic schemas for the Process entity validation and serialization.

This module defines Pydantic schemas for handling Process ORM model instances
across API operations (create, read, update). Includes comprehensive validation
for process-specific constraints such as process number range (1-8), unique codes,
positive sort order, and quality criteria as JSONB.

Schemas:
    ProcessBase: Base schema with common fields for Process entity
    ProcessCreate: Schema for creating new Process instances
    ProcessUpdate: Schema for updating existing Process instances
    ProcessInDB: Complete schema with all fields including database-generated timestamps
"""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProcessBase(BaseModel):
    """
    Base schema for Process entity with common fields.

    Includes core process attributes with validation for process number range,
    code uniqueness requirements, sort order, and quality criteria as JSONB.
    Used as a base for Create and InDB schemas.

    Attributes:
        process_number: Process sequence number in manufacturing line (1-8, required, unique)
        process_code: Unique code identifier for the process (e.g., 'LASER_MARKING')
        process_name_ko: Process name in Korean
        process_name_en: Process name in English
        description: Detailed description of the process (optional)
        estimated_duration_seconds: Expected duration in seconds (optional, must be positive if provided)
        quality_criteria: JSONB field storing quality standards and acceptance criteria (dict)
        is_active: Whether this process is currently in use (default: True)
        sort_order: Display sort order for UI presentation (must be > 0)
    """

    process_number: int = Field(
        ...,
        ge=1,
        le=8,
        description="Process sequence number in manufacturing line (1-8, required, unique)"
    )
    process_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique code identifier for the process (e.g., 'LASER_MARKING')"
    )
    process_name_ko: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Process name in Korean language"
    )
    process_name_en: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Process name in English language"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of the process and operational details"
    )
    estimated_duration_seconds: Optional[int] = Field(
        default=None,
        gt=0,
        description="Expected duration in seconds (must be positive if specified)"
    )
    quality_criteria: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSONB field storing quality standards and acceptance criteria"
    )
    is_active: bool = Field(
        default=True,
        description="Whether this process is currently in use and active"
    )
    sort_order: int = Field(
        ...,
        gt=0,
        description="Display sort order for UI presentation (must be > 0)"
    )

    @field_validator("process_code")
    @classmethod
    def validate_process_code_uppercase(cls, value: str) -> str:
        """
        Validate that process_code is in uppercase.

        Ensures process codes follow naming convention for consistency
        and uniqueness requirements.

        Args:
            value: Process code to validate

        Returns:
            Uppercase version of the process code

        Raises:
            ValueError: If process_code contains invalid characters
        """
        if not value:
            raise ValueError("process_code cannot be empty")

        # Check for valid characters (alphanumeric and underscores)
        if not all(c.isalnum() or c == '_' for c in value):
            raise ValueError(
                "process_code can only contain alphanumeric characters and underscores"
            )

        return value.upper()

    @field_validator("quality_criteria")
    @classmethod
    def validate_quality_criteria(cls, value: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate quality_criteria field as JSONB dict.

        Ensures the field is a valid dictionary that can be stored as JSONB.

        Args:
            value: Quality criteria dictionary

        Returns:
            Validated quality criteria dict (empty dict if None)

        Raises:
            ValueError: If value is not a dict
        """
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("quality_criteria must be a dictionary")
        return value


class ProcessCreate(ProcessBase):
    """
    Schema for creating new Process instances.

    Inherits all validation from ProcessBase. All required fields from base
    must be provided. Optional fields use their defaults.

    Example:
        process_create = ProcessCreate(
            process_number=1,
            process_code="LASER_MARKING",
            process_name_ko="레이저 마킹",
            process_name_en="Laser Marking",
            sort_order=1,
            quality_criteria={
                "min_power": 50,
                "max_power": 100
            }
        )
    """

    pass


class ProcessUpdate(BaseModel):
    """
    Schema for updating existing Process instances.

    All fields are optional to allow partial updates. Only provided fields
    will be updated in the database. Immutable fields like process_number
    and process_code should not be updated.

    Attributes:
        process_number: Updated process sequence number (optional, 1-8 range)
        process_code: Updated process code (optional, will be uppercased)
        process_name_ko: Updated Korean name (optional)
        process_name_en: Updated English name (optional)
        description: Updated description (optional)
        estimated_duration_seconds: Updated duration estimate (optional, positive if provided)
        quality_criteria: Updated quality criteria (optional)
        is_active: Updated active status (optional)
        sort_order: Updated sort order (optional, must be > 0)

    Note:
        process_number and process_code are unique identifiers and updates
        should be handled carefully to avoid uniqueness constraint violations.
    """

    process_number: Optional[int] = Field(
        default=None,
        ge=1,
        le=8,
        description="Process sequence number (1-8 range)"
    )
    process_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Unique code identifier for the process"
    )
    process_name_ko: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Process name in Korean"
    )
    process_name_en: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Process name in English"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Detailed description of the process"
    )
    estimated_duration_seconds: Optional[int] = Field(
        default=None,
        gt=0,
        description="Expected duration in seconds (must be positive if provided)"
    )
    quality_criteria: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSONB field with quality standards and acceptance criteria"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Whether this process is currently active"
    )
    sort_order: Optional[int] = Field(
        default=None,
        gt=0,
        description="Display sort order for UI presentation (must be > 0)"
    )

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("process_code")
    @classmethod
    def validate_process_code_uppercase(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate and uppercase process_code if provided.

        Args:
            value: Process code to validate

        Returns:
            Uppercase version of the process code or None

        Raises:
            ValueError: If process_code is provided but invalid
        """
        if value is None:
            return None

        if not value:
            raise ValueError("process_code cannot be empty")

        # Check for valid characters (alphanumeric and underscores)
        if not all(c.isalnum() or c == '_' for c in value):
            raise ValueError(
                "process_code can only contain alphanumeric characters and underscores"
            )

        return value.upper()

    @field_validator("quality_criteria")
    @classmethod
    def validate_quality_criteria(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate quality_criteria field as JSONB dict if provided.

        Args:
            value: Quality criteria dictionary

        Returns:
            Validated quality criteria dict or None

        Raises:
            ValueError: If value is provided but not a dict
        """
        if value is not None and not isinstance(value, dict):
            raise ValueError("quality_criteria must be a dictionary")
        return value


class ProcessInDB(ProcessBase):
    """
    Complete schema for Process instances with all database fields.

    Includes read-only fields populated by the database such as IDs and
    timestamps. Used for returning full process details from API endpoints.

    Attributes:
        id: Primary key (auto-generated BIGSERIAL)
        created_at: Record creation timestamp (UTC timezone-aware)
        updated_at: Last update timestamp (UTC timezone-aware)
        All attributes from ProcessBase

    Configuration:
        from_attributes: Enables Pydantic to populate from ORM model instances
        This allows direct conversion from SQLAlchemy ORM models to Pydantic schemas

    Example:
        process_in_db = ProcessInDB(
            id=1,
            process_number=1,
            process_code="LASER_MARKING",
            process_name_ko="레이저 마킹",
            process_name_en="Laser Marking",
            sort_order=1,
            quality_criteria={...},
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
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
