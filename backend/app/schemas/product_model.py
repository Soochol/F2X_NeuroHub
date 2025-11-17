"""Pydantic schemas for ProductModel entity.

This module defines Pydantic v2 schemas for validating and serializing ProductModel
data. It provides four schema variants for different use cases: base data, creation,
updates, and database responses.

Provides:
    - ProductModelBase: Base schema with shared fields for all variants
    - ProductModelCreate: Schema for creating new product models with required field validation
    - ProductModelUpdate: Schema for partial updates with all fields optional
    - ProductModelInDB: Schema for database responses including computed/audit fields

Key Features:
    - Pydantic 2.0 ConfigDict for ORM compatibility (from_attributes=True)
    - Field validation with constraints (min/max length, positive values)
    - Field validators for business logic validation
    - Comprehensive docstrings with examples
    - Type hints for all fields with Optional support
    - Enum-like status validation (ACTIVE, INACTIVE, DISCONTINUED)
"""

from datetime import datetime
from typing import Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProductStatusEnum(str, Enum):
    """Product lifecycle status enumeration.

    Attributes:
        ACTIVE: Product is currently active and available for production
        INACTIVE: Product is temporarily inactive but can be reactivated
        DISCONTINUED: Product has been discontinued and is no longer produced
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"


class ProductModelBase(BaseModel):
    """Base schema with shared fields for all ProductModel variants.

    This schema defines the core fields that are common to all ProductModel schemas.
    It serves as the foundation for Create and Update schemas, ensuring consistent
    field definitions across different operations.

    Attributes:
        model_code: Unique model identifier string (e.g., "NH-F2X-001").
            Must be 1-50 characters long. Case-sensitive and unique across database.
        model_name: Product model name in Korean/English format.
            Must be 1-255 characters long. Supports both Korean and English text.
        category: Product category or family classification.
            Optional field for grouping related product models (e.g., "Standard", "Premium").
        production_cycle_days: Expected production cycle duration in days.
            Optional positive integer. Must be > 0 if provided. Used for scheduling and planning.
        specifications: Technical specifications stored as JSON/dictionary.
            Flexible JSONB structure for storing product metadata like dimensions, weight,
            materials, features, etc. Defaults to empty dict if not provided.
        status: Product lifecycle status indicating availability and production status.
            Must be one of: ACTIVE, INACTIVE, DISCONTINUED. Defaults to ACTIVE.

    Examples:
        Create base instance with minimal fields:
        >>> base = ProductModelBase(
        ...     model_code="NH-F2X-001",
        ...     model_name="NeuroHub F2X Standard"
        ... )

        Create with full specifications:
        >>> base = ProductModelBase(
        ...     model_code="NH-F2X-002",
        ...     model_name="NeuroHub F2X Premium",
        ...     category="Premium",
        ...     production_cycle_days=7,
        ...     specifications={
        ...         "dimensions": {"width_mm": 120, "height_mm": 60},
        ...         "weight_grams": 350,
        ...         "materials": ["aluminum", "composite"]
        ...     },
        ...     status="ACTIVE"
        ... )
    """

    model_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique model identifier (e.g., NH-F2X-001)",
        examples=["NH-F2X-001", "NH-F2X-002", "NH-PRO-001"]
    )

    model_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product model name in Korean/English format",
        examples=["NeuroHub F2X Standard", "뉴로허브 F2X 프리미엄"]
    )

    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Product category or family classification",
        examples=["Standard", "Premium", "Enterprise"]
    )

    production_cycle_days: Optional[int] = Field(
        default=None,
        gt=0,
        description="Expected production cycle duration in days (must be positive)",
        examples=[5, 7, 10]
    )

    specifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Technical specifications stored in JSON/JSONB format",
        examples=[
            {
                "dimensions": {"width_mm": 100, "height_mm": 50},
                "weight_grams": 250,
                "materials": ["aluminum", "composite"]
            }
        ]
    )

    status: ProductStatusEnum = Field(
        default=ProductStatusEnum.ACTIVE,
        description="Product lifecycle status (ACTIVE, INACTIVE, DISCONTINUED)",
        examples=[ProductStatusEnum.ACTIVE]
    )

    @field_validator("model_code")
    @classmethod
    def validate_model_code(cls, value: str) -> str:
        """Validate model code format and content.

        Args:
            value: The model code string to validate.

        Returns:
            The validated model code string.

        Raises:
            ValueError: If model code is empty or contains invalid characters.

        Examples:
            >>> ProductModelBase.validate_model_code("NH-F2X-001")
            'NH-F2X-001'

            >>> ProductModelBase.validate_model_code("   ").strip()
            Traceback (most recent call last):
                ...
            ValueError: model_code cannot be empty or whitespace
        """
        if not value or not value.strip():
            raise ValueError("model_code cannot be empty or whitespace")
        return value.strip()

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        """Validate model name is not empty after stripping whitespace.

        Args:
            value: The model name string to validate.

        Returns:
            The trimmed model name string.

        Raises:
            ValueError: If model name is empty or only whitespace.

        Examples:
            >>> ProductModelBase.validate_model_name("NeuroHub F2X")
            'NeuroHub F2X'
        """
        if not value or not value.strip():
            raise ValueError("model_name cannot be empty or whitespace")
        return value.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        """Validate and clean category field.

        Args:
            value: The category string to validate, or None.

        Returns:
            Trimmed category string or None if input was None.

        Raises:
            ValueError: If category is empty string (None is allowed).

        Examples:
            >>> ProductModelBase.validate_category(None)
            >>> ProductModelBase.validate_category("  Premium  ")
            'Premium'
        """
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            raise ValueError("category cannot be empty string (use None instead)")
        return value.strip() if isinstance(value, str) else value

    @field_validator("specifications")
    @classmethod
    def validate_specifications(cls, value: dict[str, Any]) -> dict[str, Any]:
        """Validate specifications dictionary is not None.

        Args:
            value: The specifications dictionary to validate.

        Returns:
            The specifications dictionary (empty dict if not provided).

        Raises:
            ValueError: If specifications is explicitly set to None.

        Examples:
            >>> ProductModelBase.validate_specifications({})
            {}

            >>> ProductModelBase.validate_specifications(None)
            Traceback (most recent call last):
                ...
            ValueError: specifications cannot be None
        """
        if value is None:
            raise ValueError("specifications cannot be None (use empty dict instead)")
        return value


class ProductModelCreate(ProductModelBase):
    """Schema for creating new product models.

    This schema is used for input validation when creating new ProductModel records.
    It inherits all fields and validators from ProductModelBase, ensuring that
    all required fields are provided and validated consistently.

    All fields from ProductModelBase are required or have appropriate defaults.
    This schema is typically used with FastAPI route handlers for POST requests.

    Examples:
        Create new product model request body:
        >>> create_data = {
        ...     "model_code": "NH-F2X-003",
        ...     "model_name": "NeuroHub F2X Advanced",
        ...     "category": "Advanced",
        ...     "production_cycle_days": 8,
        ...     "specifications": {
        ...         "dimensions": {"width_mm": 110, "height_mm": 55},
        ...         "weight_grams": 300
        ...     },
        ...     "status": "ACTIVE"
        ... }
        >>> schema = ProductModelCreate(**create_data)
        >>> schema.model_code
        'NH-F2X-003'
    """

    pass


class ProductModelUpdate(BaseModel):
    """Schema for updating existing product models.

    This schema is used for partial update operations where all fields are optional.
    It allows updating any subset of ProductModel fields without requiring all fields
    to be present in the request.

    This schema enforces the same field constraints and validation as ProductModelBase
    but makes all fields optional to support partial updates (PATCH requests).

    Attributes:
        model_code: Optional update to unique model identifier.
        model_name: Optional update to product model name.
        category: Optional update to product category.
        production_cycle_days: Optional update to production cycle duration.
        specifications: Optional update to technical specifications.
        status: Optional update to product lifecycle status.

    Examples:
        Update only model name and status:
        >>> update_data = {
        ...     "model_name": "Updated Product Name",
        ...     "status": "INACTIVE"
        ... }
        >>> schema = ProductModelUpdate(**update_data)

        Update specifications with partial data:
        >>> update_data = {
        ...     "specifications": {
        ...         "dimensions": {"width_mm": 115},
        ...         "weight_grams": 320
        ...     }
        ... }
        >>> schema = ProductModelUpdate(**update_data)

        Minimal update (only production cycle):
        >>> update_data = {"production_cycle_days": 6}
        >>> schema = ProductModelUpdate(**update_data)
    """

    model_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated unique model identifier",
        examples=["NH-F2X-001-UPD"]
    )

    model_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated product model name",
        examples=["Updated NeuroHub F2X"]
    )

    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated product category",
        examples=["Updated Category"]
    )

    production_cycle_days: Optional[int] = Field(
        default=None,
        gt=0,
        description="Updated production cycle duration in days",
        examples=[6]
    )

    specifications: Optional[dict[str, Any]] = Field(
        default=None,
        description="Updated technical specifications",
        examples=[{"updated_field": "value"}]
    )

    status: Optional[ProductStatusEnum] = Field(
        default=None,
        description="Updated product lifecycle status",
        examples=[ProductStatusEnum.INACTIVE]
    )

    @field_validator("model_code")
    @classmethod
    def validate_model_code(cls, value: Optional[str]) -> Optional[str]:
        """Validate model code format if provided.

        Args:
            value: The model code string or None.

        Returns:
            Trimmed model code or None.

        Raises:
            ValueError: If model code is empty string (None is allowed).

        Examples:
            >>> ProductModelUpdate.validate_model_code(None)
            >>> ProductModelUpdate.validate_model_code("  NH-F2X-004  ")
            'NH-F2X-004'
        """
        if value is None:
            return None
        if not value.strip():
            raise ValueError("model_code cannot be empty string (use None instead)")
        return value.strip()

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: Optional[str]) -> Optional[str]:
        """Validate model name format if provided.

        Args:
            value: The model name string or None.

        Returns:
            Trimmed model name or None.

        Raises:
            ValueError: If model name is empty string (None is allowed).

        Examples:
            >>> ProductModelUpdate.validate_model_name(None)
            >>> ProductModelUpdate.validate_model_name("  Updated Name  ")
            'Updated Name'
        """
        if value is None:
            return None
        if not value.strip():
            raise ValueError("model_name cannot be empty string (use None instead)")
        return value.strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        """Validate and clean category field if provided.

        Args:
            value: The category string or None.

        Returns:
            Trimmed category or None.

        Raises:
            ValueError: If category is empty string (None is allowed).

        Examples:
            >>> ProductModelUpdate.validate_category(None)
            >>> ProductModelUpdate.validate_category("  Premium  ")
            'Premium'
        """
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            raise ValueError("category cannot be empty string (use None instead)")
        return value.strip() if isinstance(value, str) else value


class ProductModelInDB(ProductModelBase):
    """Schema for product model database responses.

    This schema is used when returning ProductModel records from the database.
    It includes all fields from ProductModelBase plus database-generated fields
    like primary key and audit timestamps.

    This schema is configured with `from_attributes=True` to enable automatic
    conversion from SQLAlchemy ORM models using the Pydantic `model_validate()`
    method or FastAPI's automatic response serialization.

    Attributes:
        id: Primary key identifier (auto-generated by database).
        created_at: Record creation timestamp (auto-generated on insert).
        updated_at: Last update timestamp (auto-updated on modifications).

    Model Config:
        from_attributes: True - Enables ORM mode for SQLAlchemy compatibility.
            Allows direct conversion from ORM models without dict conversion.

    Examples:
        Response from GET endpoint:
        >>> db_product = ProductModelInDB(
        ...     id=1,
        ...     model_code="NH-F2X-001",
        ...     model_name="NeuroHub F2X Standard",
        ...     category="Standard",
        ...     production_cycle_days=5,
        ...     specifications={"dimensions": {"width_mm": 100}},
        ...     status="ACTIVE",
        ...     created_at=datetime(2024, 1, 15, 10, 30, 0),
        ...     updated_at=datetime(2024, 1, 15, 10, 30, 0)
        ... )
        >>> db_product.id
        1

        Convert from SQLAlchemy ORM model:
        >>> from sqlalchemy.orm import Session
        >>> product_orm = session.query(ProductModel).first()
        >>> db_product = ProductModelInDB.model_validate(product_orm)
        >>> db_product.id
        1
    """

    id: int = Field(
        ...,
        description="Primary key identifier (auto-generated)",
        examples=[1, 2, 3]
    )

    created_at: datetime = Field(
        ...,
        description="Record creation timestamp (auto-generated on insert)",
        examples=["2024-01-15T10:30:00"]
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp (auto-updated on modifications)",
        examples=["2024-01-15T10:30:00"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )

    def __repr__(self) -> str:
        """Return string representation of ProductModelInDB instance.

        Returns:
            String representation showing id, model_code, and model_name.

        Examples:
            >>> db_product = ProductModelInDB(
            ...     id=1,
            ...     model_code="NH-F2X-001",
            ...     model_name="Standard",
            ...     created_at=datetime.now(),
            ...     updated_at=datetime.now()
            ... )
            >>> repr(db_product)
            "<ProductModelInDB(id=1, model_code='NH-F2X-001', model_name='Standard')>"
        """
        return (
            f"<ProductModelInDB("
            f"id={self.id}, "
            f"model_code={self.model_code!r}, "
            f"model_name={self.model_name!r})>"
        )
