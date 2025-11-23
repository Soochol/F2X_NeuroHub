"""
SQLAlchemy ORM model for the ProductionLine entity.

Represents production lines in the F2X NeuroHub manufacturing facility.
Each production line is a physical manufacturing area with specific capacity
and location information.

Database table: production_lines
Primary key: id (BIGINT)
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.equipment import Equipment
    from app.models.lot import Lot


class ProductionLine(Base):
    """
    SQLAlchemy ORM model for production lines.

    Represents a physical production line in the manufacturing facility.
    Each line has a unique code, name, capacity, and location information.

    Attributes:
        id: Primary key, auto-incrementing BIGINT
        line_code: Unique line identifier (e.g., 'LINE-A')
        line_name: Display name for the line (e.g., '조립라인 A')
        description: Detailed description of the production line
        cycle_time_sec: Cycle time in seconds per unit (optional)
        location: Physical location (e.g., 'Building 1, Zone A')
        is_active: Whether this line is currently operational (default: True)
        created_at: Record creation timestamp
        updated_at: Last update timestamp

    Constraints:
        - line_code must be unique

    Indexes:
        - idx_production_lines_active: On (is_active) for active lines
        - idx_production_lines_code: On (line_code) for lookups
    """

    __tablename__ = "production_lines"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Core Columns
    line_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique line identifier (e.g., 'LINE-A')",
    )

    line_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name for the line (e.g., '조립라인 A')",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed description of the production line",
    )

    cycle_time_sec: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Cycle time in seconds per unit (optional)",
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Physical location (e.g., 'Building 1, Zone A')",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
        comment="Whether this line is currently operational",
    )

    # Timestamp Columns
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Record creation timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Last update timestamp",
    )

    # Relationships
    equipment: Mapped[List["Equipment"]] = relationship(
        "Equipment",
        back_populates="production_line",
        cascade="all, delete-orphan",
    )

    lots: Mapped[List["Lot"]] = relationship(
        "Lot",
        back_populates="production_line",
    )

    # Table Arguments: Indexes
    __table_args__ = (
        Index(
            "idx_production_lines_active",
            is_active,
        ),
        Index(
            "idx_production_lines_code",
            line_code,
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of ProductionLine instance."""
        return (
            f"<ProductionLine(id={self.id}, code='{self.line_code}', "
            f"name='{self.line_name}', cycle_time={self.cycle_time_sec}s)>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.line_code}: {self.line_name}"

    def to_dict(self) -> dict:
        """
        Convert ProductionLine instance to dictionary.

        Returns:
            dict: Dictionary representation of the production line
        """
        return {
            "id": self.id,
            "line_code": self.line_code,
            "line_name": self.line_name,
            "description": self.description,
            "cycle_time_sec": self.cycle_time_sec,
            "location": self.location,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
