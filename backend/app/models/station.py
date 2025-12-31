"""
SQLAlchemy ORM model for the Station entity.

Represents a Station Service instance that connects to the backend.
Stations are automatically registered when they connect and report their status.

Database table: stations
Primary key: id (BIGINT)
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, JSONBDict


class StationStatus(str, PyEnum):
    """Station connection status."""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"


class Station(Base):
    """
    SQLAlchemy ORM model for Station Service instances.

    Represents a station service that connects to the backend for
    test sequence execution and batch management.

    Attributes:
        id: Primary key, auto-incrementing BIGINT
        station_id: Unique station identifier (from station config)
        station_name: Display name of the station
        description: Station description
        host: IP address or hostname of the station
        port: Port number of the station service
        status: Current connection status (ONLINE, OFFLINE, DEGRADED)
        version: Station service version
        is_active: Whether station is enabled
        last_seen_at: Last heartbeat timestamp
        health_data: Health metrics in JSONB format
        created_at: First registration timestamp
        updated_at: Last update timestamp

    Indexes:
        - idx_station_status: On (status) for filtering
        - idx_station_active: On (is_active, status) for active stations
    """

    __tablename__ = "stations"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Core Columns
    station_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Unique station identifier from config",
    )

    station_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name of the station",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Station description",
    )

    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="IP address or hostname",
    )

    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8080,
        comment="Port number of station service",
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=StationStatus.OFFLINE.value,
        server_default=text("'OFFLINE'"),
        comment="Connection status: ONLINE, OFFLINE, DEGRADED",
    )

    version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Station service version",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("TRUE"),
        comment="Whether station is enabled",
    )

    # Health Data (JSONB)
    health_data: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        server_default=text("'{}'"),
        comment="Health metrics: disk_usage, batches_running, backend_status, uptime",
    )

    # Timestamps
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last heartbeat timestamp",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="First registration timestamp",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Last update timestamp",
    )

    # Table Arguments: Indexes
    __table_args__ = (
        Index("idx_station_status", status),
        Index("idx_station_active", is_active, status),
        Index("idx_station_id", station_id),
    )

    def __repr__(self) -> str:
        """Return string representation of Station instance."""
        return (
            f"<Station(id={self.id}, station_id='{self.station_id}', "
            f"name='{self.station_name}', status='{self.status}')>"
        )

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.station_id}: {self.station_name} ({self.host}:{self.port})"

    def to_dict(self) -> dict:
        """Convert Station instance to dictionary."""
        return {
            "id": self.id,
            "station_id": self.station_id,
            "station_name": self.station_name,
            "description": self.description,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "version": self.version,
            "is_active": self.is_active,
            "health_data": self.health_data,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def is_online(self) -> bool:
        """Check if station is currently online."""
        return self.status == StationStatus.ONLINE.value

    @property
    def url(self) -> str:
        """Get the station service URL."""
        return f"http://{self.host}:{self.port}"
