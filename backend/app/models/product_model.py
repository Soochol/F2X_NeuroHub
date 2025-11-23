"""SQLAlchemy ORM model for product_models table.

This module defines the ProductModel entity for master data containing product
model definitions and specifications. It implements F2X NeuroHub MES database
schema using SQLAlchemy 2.0 syntax.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import Index, String, Text, CheckConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict, is_postgresql


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
        unique=True
    )

    model_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    production_cycle_days: Mapped[Optional[int]] = mapped_column(
        nullable=True
    )

    specifications: Mapped[dict[str, Any]] = mapped_column(
        JSONBDict,
        nullable=False,
        default=lambda: {}
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE"
    )

    # =========================================================================
    # Timestamp Columns
    # =========================================================================
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # =========================================================================
    # Relationships
    # =========================================================================
    lots: Mapped[List["Lot"]] = relationship(  # noqa: F821
        "Lot",
        back_populates="product_model",
        cascade="all, delete-orphan"
    )

    # =========================================================================
    # Constraints
    # =========================================================================
    @staticmethod
    def _get_table_args():
        """Generate table arguments conditionally based on database dialect."""
        args = [
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
            # Basic indexes (SQLite compatible)
            Index("idx_product_models_status", "status"),
            Index("idx_product_models_category", "category"),
        ]

        # Add PostgreSQL-specific indexes
        if is_postgresql():
            args.extend([
                Index(
                    "idx_product_models_name_search",
                    text("to_tsvector('simple', model_name)"),
                    postgresql_using="gin"
                ),
                Index(
                    "idx_product_models_specifications",
                    "specifications",
                    postgresql_using="gin"
                ),
            ])

        return tuple(args)

    __table_args__ = _get_table_args()

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
