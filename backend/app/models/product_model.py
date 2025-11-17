"""SQLAlchemy ORM model for product_models table.

This module defines the ProductModel entity for master data containing product
model definitions and specifications. It implements F2X NeuroHub MES database
schema using SQLAlchemy 2.0 syntax.
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Index, String, Text, CheckConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductModel(Base):
    """Product model definitions and specifications.

    This table serves as the master data for all product models in the F2X
    NeuroHub MES system. It contains product metadata, technical specifications,
    and lifecycle information.

    Attributes:
        id: Primary key, auto-incrementing identifier (BIGSERIAL).
        model_code: Unique model identifier (e.g., NH-F2X-001). Unique constraint.
        model_name: Product name in Korean/English format.
        category: Product category or family classification.
        production_cycle_days: Expected production cycle duration in days.
        specifications: Technical specifications stored in JSON format.
        status: Product lifecycle status (ACTIVE, INACTIVE, DISCONTINUED).
        created_at: Record creation timestamp with timezone awareness.
        updated_at: Last update timestamp with timezone awareness.

    Examples:
        Create a new product model:
        >>> model = ProductModel(
        ...     model_code="NH-F2X-001",
        ...     model_name="NeuroHub F2X Standard",
        ...     category="Standard",
        ...     production_cycle_days=5,
        ...     specifications={
        ...         "dimensions": {"width_mm": 100, "height_mm": 50},
        ...         "weight_grams": 250
        ...     },
        ...     status="ACTIVE"
        ... )

    Notes:
        - Uses PostgreSQL JSONB for flexible specifications storage
        - Auto-updated timestamp via database trigger
        - Audit logging implemented via database trigger
        - Status values are enforced by CHECK constraint at database level
        - Production cycle days must be positive if specified
    """

    __tablename__ = "product_models"

    # =========================================================================
    # Primary Key
    # =========================================================================
    id: Mapped[int] = mapped_column(primary_key=True)

    # =========================================================================
    # Core Columns
    # =========================================================================
    model_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        doc="Unique model identifier (e.g., NH-F2X-001)"
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Product name (Korean/English)"
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Product category or family"
    )

    production_cycle_days: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        doc="Expected production cycle duration in days"
    )

    specifications: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {},
        server_default=text("'{}'::jsonb"),
        doc="Technical specifications in JSON format"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE",
        doc="Product lifecycle status (ACTIVE, INACTIVE, DISCONTINUED)"
    )

    # =========================================================================
    # Timestamp Columns
    # =========================================================================
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        doc="Record creation timestamp with timezone awareness"
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        doc="Last update timestamp with timezone awareness"
    )

    # =========================================================================
    # Constraints
    # =========================================================================
    __table_args__ = (
        # Status check constraint
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'DISCONTINUED')",
            name="chk_product_models_status"
        ),
        # Production cycle days positive check constraint
        CheckConstraint(
            "production_cycle_days IS NULL OR production_cycle_days > 0",
            name="chk_product_models_cycle_days"
        ),
        # Indexes
        Index(
            "idx_product_models_status",
            "status",
            postgresql_where=text("status = 'ACTIVE'"),
            doc="Partial index for active products query"
        ),
        Index(
            "idx_product_models_name_search",
            text("to_tsvector('simple', model_name)"),
            postgresql_using="gin",
            doc="Full-text search index on model name"
        ),
        Index(
            "idx_product_models_specifications",
            "specifications",
            postgresql_using="gin",
            doc="GIN index for JSONB specifications"
        ),
        Index(
            "idx_product_models_category",
            "category",
            postgresql_where=text("category IS NOT NULL"),
            doc="Category classification partial index"
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of ProductModel.

        Returns:
            String representation showing model code and name.

        Examples:
            >>> model = ProductModel(model_code="NH-F2X-001", model_name="Standard")
            >>> repr(model)
            "<ProductModel(model_code='NH-F2X-001', model_name='Standard')>"
        """
        return (
            f"<ProductModel("
            f"model_code={self.model_code!r}, "
            f"model_name={self.model_name!r})>"
        )
