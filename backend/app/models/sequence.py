"""
Sequence models for test sequence management.

Provides models for storing and managing test sequences that can be
deployed to Station Services for execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sequence(Base):
    """
    Test sequence package.

    Stores sequence metadata and the packaged code (ZIP) for deployment
    to Station Services.
    """

    __tablename__ = "sequences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identification
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique sequence identifier (e.g., 'psa_sensor_test')",
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
        comment="Current version (semver format)",
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Human-readable display name",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Sequence description",
    )

    # Package data
    package_data: Mapped[bytes] = mapped_column(
        Text,
        nullable=False,
        comment="Base64-encoded ZIP package",
    )
    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 checksum of package",
    )
    package_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Package size in bytes",
    )

    # Manifest data (extracted from manifest.yaml)
    hardware: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Required hardware configuration",
    )
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Default parameters",
    )
    steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Sequence steps metadata",
    )

    # Target process (optional - can be used for specific process assignment)
    process_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
        comment="Target process ID if sequence is process-specific",
    )

    # Status flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether sequence is active for deployment",
    )
    is_deprecated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether sequence is deprecated",
    )

    # Upload info
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who uploaded the sequence",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    versions: Mapped[List["SequenceVersion"]] = relationship(
        "SequenceVersion",
        back_populates="sequence",
        cascade="all, delete-orphan",
        order_by="desc(SequenceVersion.created_at)",
    )
    deployments: Mapped[List["SequenceDeployment"]] = relationship(
        "SequenceDeployment",
        back_populates="sequence",
        cascade="all, delete-orphan",
    )
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )
    process: Mapped[Optional["Process"]] = relationship(
        "Process",
        foreign_keys=[process_id],
    )

    def __repr__(self) -> str:
        return f"<Sequence {self.name} v{self.version}>"


class SequenceVersion(Base):
    """
    Sequence version history.

    Stores historical versions of sequences for rollback capability.
    """

    __tablename__ = "sequence_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Reference to sequence
    sequence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Version info
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Version string (semver format)",
    )

    # Package data
    package_data: Mapped[bytes] = mapped_column(
        Text,
        nullable=False,
        comment="Base64-encoded ZIP package",
    )
    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 checksum of package",
    )
    package_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Manifest data snapshot
    hardware: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )
    steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # Change info
    change_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Release notes for this version",
    )
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    sequence: Mapped["Sequence"] = relationship(
        "Sequence",
        back_populates="versions",
    )
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("sequence_id", "version", name="uq_sequence_version"),
        Index("ix_sequence_versions_sequence_version", "sequence_id", "version"),
    )

    def __repr__(self) -> str:
        return f"<SequenceVersion {self.sequence_id}:{self.version}>"


class SequenceDeployment(Base):
    """
    Sequence deployment tracking.

    Tracks which sequences are deployed to which stations/batches.
    """

    __tablename__ = "sequence_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Reference to sequence
    sequence_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Deployment target
    station_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Target station ID",
    )
    batch_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Target batch ID within station",
    )

    # Version deployed
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Deployed version",
    )

    # Deployment status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="Status: pending, deployed, failed, rolled_back",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if deployment failed",
    )

    # Deployment info
    deployed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    deployed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When deployment was confirmed",
    )

    # Relationships
    sequence: Mapped["Sequence"] = relationship(
        "Sequence",
        back_populates="deployments",
    )
    deployer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[deployed_by],
    )

    # Indexes
    __table_args__ = (
        Index("ix_sequence_deployments_station", "station_id", "batch_id"),
        Index("ix_sequence_deployments_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<SequenceDeployment {self.sequence_id} -> {self.station_id}:{self.batch_id}>"


# Type hints for relationships (avoid circular imports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.process import Process
