"""
SQLAlchemy 2.0 ORM model for the Lot entity.

This module provides the Lot model representing production batches in the F2X NeuroHub MES.
Each LOT represents a production run of up to 100 units manufactured together on a specific
date, providing batch-level traceability and quality metrics.

LOT Number Format: {Country 2}{Line 2}{Model 3}{Month 4}{Seq 2} = 13 characters
    - Country: 2-char country code (e.g., "KR" for Korea)
    - Line: 2-digit production line number (e.g., "01")
    - Model: 3-char model code (e.g., "PSA")
    - Month: 4-digit year/month YYMM format (e.g., "2511" for Nov 2025)
    - Seq: 2-digit sequence number within the month (01-99)

Example: KR01PSA251101 (13 characters total)

Status Lifecycle: CREATED → IN_PROGRESS → COMPLETED → CLOSED
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    VARCHAR,
    DATE,
    INTEGER,
    TIMESTAMP,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LotStatus(str, Enum):
    """LOT lifecycle status enumeration.

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


class Lot(Base):
    """
    ORM model for production batch (LOT) tracking.

    Represents a single production run of units manufactured together on a specific
    date and shift. Provides batch-level traceability with quantity tracking for
    target, actual, passed, and failed units.

    Table: lots
    Primary Key: id (INTEGER AUTOINCREMENT)
    Foreign Keys: product_model_id → product_models.id

    Attributes:
        id: Primary key, auto-incrementing INTEGER
        lot_number: Auto-generated LOT identifier
        product_model_id: Foreign key reference to product_models table
        production_date: Scheduled/actual production date
        target_quantity: Target production quantity (max 100 units per LOT)
        actual_quantity: Actual units produced in this LOT
        passed_quantity: Number of units that passed all quality checks
        failed_quantity: Number of units that failed quality checks
        status: LOT lifecycle status (CREATED, IN_PROGRESS, COMPLETED, CLOSED)
        created_at: LOT creation timestamp
        updated_at: Last modification timestamp (auto-updated)
        closed_at: LOT closure/completion timestamp (auto-set when COMPLETED)
        product_model: Relationship to ProductModel (many-to-one)
        serials: Relationship to Serial (one-to-many)

    Constraints:
        - Primary Key: pk_lots (id)
        - Foreign Key: fk_lots_product_model (product_model_id → product_models.id)
        - Unique: uk_lots_lot_number (lot_number)
        - Check: status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED')
        - Check: target_quantity > 0 AND target_quantity <= 100
        - Check: actual_quantity >= 0 AND actual_quantity <= target_quantity
        - Check: passed_quantity >= 0 AND passed_quantity <= actual_quantity
        - Check: failed_quantity >= 0 AND failed_quantity <= actual_quantity
        - Check: passed_quantity + failed_quantity <= actual_quantity

    Indexes:
        - idx_lots_product_model: (product_model_id)
        - idx_lots_status: (status)
        - idx_lots_active: (status, production_date) WHERE status IN ('CREATED', 'IN_PROGRESS')
        - idx_lots_production_date: (production_date DESC)
        - idx_lots_model_date: (product_model_id, production_date)
        - idx_lots_closed_at: (closed_at) WHERE closed_at IS NOT NULL
    """

    __tablename__ = "lots"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Core Columns
    lot_number: Mapped[str] = mapped_column(
        VARCHAR(50),
        nullable=False,
        unique=True,
        comment="Auto-generated LOT identifier"
    )

    product_model_id: Mapped[int] = mapped_column(
        ForeignKey("product_models.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="Foreign key reference to product_models table"
    )

    production_line_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("production_lines.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="Foreign key reference to production_lines table"
    )

    production_date: Mapped[date] = mapped_column(
        DATE,
        nullable=False,
        comment="Scheduled/actual production date"
    )

    # Component Lots
    parent_spring_lot: Mapped[Optional[str]] = mapped_column(
        VARCHAR(50),
        nullable=True,
        comment="Parent Spring Lot number"
    )

    sma_spring_lot: Mapped[Optional[str]] = mapped_column(
        VARCHAR(50),
        nullable=True,
        comment="SMA Spring Lot number"
    )

    # Quantity Tracking
    target_quantity: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=100,
        comment="Target production quantity (max 100 units per LOT)"
    )

    actual_quantity: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=0,
        comment="Actual units produced in this LOT"
    )

    passed_quantity: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=0,
        comment="Number of units that passed all quality checks"
    )

    failed_quantity: Mapped[int] = mapped_column(
        INTEGER,
        nullable=False,
        default=0,
        comment="Number of units that failed quality checks"
    )

    # Status Management
    status: Mapped[str] = mapped_column(
        VARCHAR(20),
        nullable=False,
        default=LotStatus.CREATED,
        comment="LOT lifecycle status: CREATED → IN_PROGRESS → COMPLETED → CLOSED"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="LOT creation timestamp"
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Last modification timestamp (auto-updated)"
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        comment="LOT closure/completion timestamp (auto-set when COMPLETED)"
    )

    # Relationships
    product_model: Mapped["ProductModel"] = relationship(
        "ProductModel",
        back_populates="lots",
        foreign_keys=[product_model_id]
    )

    production_line: Mapped[Optional["ProductionLine"]] = relationship(
        "ProductionLine",
        back_populates="lots",
        foreign_keys=[production_line_id]
    )

    serials: Mapped[List["Serial"]] = relationship(
        "Serial",
        back_populates="lot",
        cascade="all, delete-orphan"
    )

    wip_items: Mapped[List["WIPItem"]] = relationship(
        "WIPItem",
        back_populates="lot",
        cascade="all, delete-orphan"
    )

    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="lot",
        cascade="all, delete-orphan"
    )

    process_data_records: Mapped[List["ProcessData"]] = relationship(
        "ProcessData",
        back_populates="lot",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        # Foreign key index
        Index("idx_lots_product_model", "product_model_id"),
        Index("idx_lots_production_line", "production_line_id"),

        # Status-based queries
        Index("idx_lots_status", "status"),

        # Active LOTs index (frequently queried)
        Index(
            "idx_lots_active",
            "status",
            "production_date"
        ),

        # Date range queries
        Index("idx_lots_production_date", "production_date"),

        # Composite index for filtering
        Index("idx_lots_model_date", "product_model_id", "production_date"),

        # Closed LOTs index (for archival)
        Index("idx_lots_closed_at", "closed_at"),
    )

    def __repr__(self) -> str:
        """Return string representation of Lot instance."""
        return (
            f"<Lot(id={self.id}, lot_number='{self.lot_number}', "
            f"product_model_id={self.product_model_id}, status='{self.status}', "
            f"actual_quantity={self.actual_quantity})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if LOT is in active production state.

        Returns:
            True if status is CREATED or IN_PROGRESS, False otherwise
        """
        return self.status in (LotStatus.CREATED, LotStatus.IN_PROGRESS)

    @property
    def is_completed(self) -> bool:
        """Check if LOT has completed production.

        Returns:
            True if status is COMPLETED or CLOSED, False otherwise
        """
        return self.status in (LotStatus.COMPLETED, LotStatus.CLOSED)

    @property
    def defect_rate(self) -> Optional[float]:
        """Calculate defect rate percentage.

        Returns:
            Defect rate as percentage (0-100), or None if no actual quantity
        """
        if self.actual_quantity == 0:
            return None
        return round((self.failed_quantity / self.actual_quantity) * 100, 2)

    @property
    def pass_rate(self) -> Optional[float]:
        """Calculate pass rate percentage.

        Returns:
            Pass rate as percentage (0-100), or None if no actual quantity
        """
        if self.actual_quantity == 0:
            return None
        return round((self.passed_quantity / self.actual_quantity) * 100, 2)

    @property
    def unverified_quantity(self) -> int:
        """Calculate units that have not yet been verified.

        Returns:
            Quantity of units neither passed nor failed
        """
        return self.actual_quantity - (self.passed_quantity + self.failed_quantity)

    @property
    def serial_count(self) -> int:
        """Calculate the number of serials generated for this LOT.

        Returns:
            Number of serials in the serials relationship
        """
        return len(self.serials) if self.serials else 0

    @property
    def wip_count(self) -> int:
        """Calculate the number of WIP items generated for this LOT.

        Returns:
            Number of WIP items in the wip_items relationship
        """
        return len(self.wip_items) if self.wip_items else 0


# Type hint imports for forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product_model import ProductModel
    from app.models.production_line import ProductionLine
    from app.models.serial import Serial
    from app.models.wip_item import WIPItem
