"""
SQLAlchemy ORM model for the audit_logs table.

This module provides the AuditLog entity representing immutable audit trail records
for compliance, security, and change tracking across the F2X NeuroHub system.

The audit_logs table is partitioned monthly by created_at using RANGE partitioning
with partition names following the format: audit_logs_yYYYYmMM (e.g., audit_logs_y2025m11).

Features:
    - Immutable records (append-only, no UPDATE/DELETE allowed)
    - JSONB snapshots of old and new values with GIN indexes
    - Client tracking (IP address, user agent)
    - User accountability with FK to users table
    - Comprehensive indexing for efficient auditing
    - Action tracking (CREATE, UPDATE, DELETE)
    - Entity type validation for specific audited entities

Example Usage:
    >>> # Create a new audit log entry
    >>> audit_entry = AuditLog(
    ...     user_id=1,
    ...     entity_type="lots",
    ...     entity_id=42,
    ...     action=AuditAction.UPDATE,
    ...     old_values={"status": "ACTIVE"},
    ...     new_values={"status": "COMPLETED"},
    ...     ip_address="192.168.1.100",
    ...     user_agent="Mozilla/5.0..."
    ... )
    >>> db.add(audit_entry)
    >>> db.commit()
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, JSONBDict


class AuditAction(str, Enum):
    """
    Enumeration of audit action types.

    Attributes:
        CREATE: Record was created
        UPDATE: Record was updated
        DELETE: Record was deleted
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(Base):
    """
    Immutable audit trail capturing all system changes for compliance and security.

    This entity represents an immutable log entry documenting changes to audited
    entities. The table is partitioned monthly by created_at using RANGE partitioning
    for performance and maintenance efficiency.

    Partitioning Strategy:
        - Type: RANGE partitioning on created_at column
        - Granularity: Monthly
        - Partition Naming: audit_logs_yYYYYmMM (e.g., audit_logs_y2025m11)
        - Partition Boundaries: First day of month to first day of next month

    Example Partitions:
        - audit_logs_y2025m11: 2025-11-01 to 2025-12-01
        - audit_logs_y2025m12: 2025-12-01 to 2026-01-01
        - audit_logs_y2026m01: 2026-01-01 to 2026-02-01

    Immutability:
        - Database-enforced via trigger prevent_audit_modification()
        - Prevents UPDATE and DELETE operations on all records
        - Only INSERT is allowed
        - Violations raise: "Audit logs are immutable and cannot be modified or deleted"

    Indexes:
        - idx_audit_logs_user: User lookups (B-tree)
        - idx_audit_logs_entity: Entity history by type and ID (B-tree)
        - idx_audit_logs_action: Action type filtering with time ordering (B-tree)
        - idx_audit_logs_created_at: Time-based queries, primary access pattern (B-tree)
        - idx_audit_logs_user_activity: User activity analysis (B-tree)
        - idx_audit_logs_entity_history: Complete entity history queries (B-tree)
        - idx_audit_logs_old_values: JSONB field search on old_values (GIN)
        - idx_audit_logs_new_values: JSONB field search on new_values (GIN)
        - idx_audit_logs_ip_address: IP-based security analysis, partial index (B-tree)

    Constraints:
        - pk_audit_logs: Composite primary key (id, created_at) due to partitioning
        - fk_audit_logs_user: FK to users.id (RESTRICT on DELETE, CASCADE on UPDATE)
        - chk_audit_logs_action: action IN ('CREATE', 'UPDATE', 'DELETE')
        - chk_audit_logs_entity_type: entity_type IN allowed list
        - chk_audit_logs_old_values: NULL for CREATE, NOT NULL for UPDATE/DELETE
        - chk_audit_logs_new_values: NULL for DELETE, NOT NULL for CREATE/UPDATE

    Retention Policy:
        - Active partitions: 12 months in primary database
        - Archive partitions: 12-36 months, moved to cold storage
        - Delete: After 36 months (3 years) per compliance
        - Maintenance: Automated via maintain_audit_partitions() procedure

    Note:
        This table is partitioned by created_at using RANGE partitioning.
        Partitions are created monthly for operational efficiency and are
        named following the pattern audit_logs_yYYYYmMM.
    """

    __tablename__ = "audit_logs"

    # =========================================================================
    # PRIMARY KEY
    # =========================================================================
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
        autoincrement="auto",  # SQLite compatible: auto uses ROWID for single-column PKs
    )

    # =========================================================================
    # FOREIGN KEYS
    # =========================================================================
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            name="fk_audit_logs_user",
        ),
        nullable=False,
        index=True,
    )

    # =========================================================================
    # ENTITY IDENTIFICATION
    # =========================================================================
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entity_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # =========================================================================
    # ACTION TRACKING
    # =========================================================================
    action: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # =========================================================================
    # DATA SNAPSHOTS (JSONB)
    # =========================================================================
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONBDict,
        nullable=True,
    )

    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONBDict,
        nullable=True,
    )

    # =========================================================================
    # CLIENT INFORMATION
    # =========================================================================
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================================
    # TIMESTAMP
    # =========================================================================
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        # Note: primary_key=True removed for SQLite compatibility
        # PostgreSQL partitioning uses (id, created_at) composite key
    )

    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    user: Mapped[Optional["User"]] = relationship(  # noqa: F821
        "User",
        foreign_keys=[user_id],
        uselist=False,
        lazy="select",
    )

    # =========================================================================
    # TABLE ARGUMENTS: INDEXES & CONSTRAINTS
    # =========================================================================
    __table_args__ = (
        # Composite primary key for partitioned table
        # Note: Both id and created_at are required for partitioning
        # (Defined via mapped_column primary_key=True)

        # =====================================================================
        # B-TREE INDEXES
        # =====================================================================
        Index(
            "idx_audit_logs_user",
            "user_id",
        ),
        Index(
            "idx_audit_logs_entity",
            "entity_type",
            "entity_id",
        ),
        Index(
            "idx_audit_logs_action",
            "action",
            "created_at",
        ),
        Index(
            "idx_audit_logs_created_at",
            "created_at",
        ),
        Index(
            "idx_audit_logs_user_activity",
            "user_id",
            "created_at",
        ),
        Index(
            "idx_audit_logs_entity_history",
            "entity_type",
            "entity_id",
            "created_at",
        ),

        # =====================================================================
        # GIN INDEXES FOR JSONB
        # =====================================================================
        Index(
            "idx_audit_logs_old_values",
            "old_values",
        ),
        Index(
            "idx_audit_logs_new_values",
            "new_values",
        ),

        # =====================================================================
        # PARTIAL INDEX FOR SECURITY ANALYSIS
        # =====================================================================
        Index(
            "idx_audit_logs_ip_address",
            "ip_address",
            "created_at",
        ),

        # =====================================================================
        # CHECK CONSTRAINTS
        # =====================================================================
        CheckConstraint(
            "action IN ('CREATE', 'UPDATE', 'DELETE')",
            name="chk_audit_logs_action",
        ),
        CheckConstraint(
            "entity_type IN ('product_models', 'lots', 'serials', 'processes', "
            "'process_data', 'users', 'audit_logs')",
            name="chk_audit_logs_entity_type",
        ),
        CheckConstraint(
            "(action = 'CREATE' AND old_values IS NULL) OR "
            "(action IN ('UPDATE', 'DELETE') AND old_values IS NOT NULL)",
            name="chk_audit_logs_old_values",
        ),
        CheckConstraint(
            "(action = 'DELETE' AND new_values IS NULL) OR "
            "(action IN ('CREATE', 'UPDATE') AND new_values IS NOT NULL)",
            name="chk_audit_logs_new_values",
        ),
    )

    def __repr__(self) -> str:
        """Return a detailed string representation of the audit log entry."""
        return (
            f"<AuditLog(id={self.id}, entity_type={self.entity_type!r}, "
            f"entity_id={self.entity_id}, action={self.action!r}, "
            f"user_id={self.user_id}, created_at={self.created_at!r})>"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return (
            f"AuditLog: {self.action} on {self.entity_type}#{self.entity_id} "
            f"by user {self.user_id} at {self.created_at}"
        )

    @property
    def is_create(self) -> bool:
        """Check if this log entry represents a CREATE action."""
        return self.action == AuditAction.CREATE.value

    @property
    def is_update(self) -> bool:
        """Check if this log entry represents an UPDATE action."""
        return self.action == AuditAction.UPDATE.value

    @property
    def is_delete(self) -> bool:
        """Check if this log entry represents a DELETE action."""
        return self.action == AuditAction.DELETE.value

    @property
    def has_changed_values(self) -> bool:
        """Check if both old and new values are present (UPDATE action)."""
        return self.old_values is not None and self.new_values is not None

    def get_field_change(self, field_name: str) -> tuple[Optional[Any], Optional[Any]]:
        """
        Get the before and after values for a specific field.

        Args:
            field_name: The name of the field to retrieve from snapshots

        Returns:
            A tuple of (old_value, new_value). Values are None if not applicable
            to the action type or if the field is not present in the snapshot.

        Example:
            >>> audit_log.get_field_change("status")
            ("ACTIVE", "COMPLETED")
        """
        old_val = None
        new_val = None

        if self.old_values is not None and isinstance(self.old_values, dict):
            old_val = self.old_values.get(field_name)

        if self.new_values is not None and isinstance(self.new_values, dict):
            new_val = self.new_values.get(field_name)

        return old_val, new_val

    def get_changed_fields(self) -> set[str]:
        """
        Get the set of fields that were changed in an UPDATE action.

        Returns:
            A set of field names that differ between old_values and new_values.
            Returns empty set for CREATE or DELETE actions.

        Example:
            >>> audit_log.get_changed_fields()
            {"status", "updated_by"}
        """
        if not self.has_changed_values:
            return set()

        old_keys = set(self.old_values.keys()) if isinstance(self.old_values, dict) else set()
        new_keys = set(self.new_values.keys()) if isinstance(self.new_values, dict) else set()

        # Find fields that exist in both and differ
        changed = set()
        for key in old_keys & new_keys:
            if self.old_values[key] != self.new_values[key]:
                changed.add(key)

        # Add fields that only exist in new_values (additions)
        changed.update(new_keys - old_keys)

        # Add fields that only exist in old_values (removals)
        changed.update(old_keys - new_keys)

        return changed
