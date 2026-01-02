"""Add sequences tables for CLI-based sequence management.

Revision ID: c3d4e5f6a7b8
Revises: 20250102_0001_b2c3d4e5f6a7_add_process_headers_table
Create Date: 2025-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "20250102_0001_b2c3d4e5f6a7_add_process_headers_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sequences table
    op.create_table(
        "sequences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, comment="Unique sequence identifier"),
        sa.Column("version", sa.String(length=20), nullable=False, server_default="1.0.0", comment="Current version"),
        sa.Column("display_name", sa.String(length=200), nullable=True, comment="Human-readable display name"),
        sa.Column("description", sa.Text(), nullable=True, comment="Sequence description"),
        sa.Column("package_data", sa.Text(), nullable=False, comment="Base64-encoded ZIP package"),
        sa.Column("checksum", sa.String(length=64), nullable=False, comment="SHA-256 checksum"),
        sa.Column("package_size", sa.Integer(), nullable=False, server_default="0", comment="Package size in bytes"),
        sa.Column("hardware", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Required hardware configuration"),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Default parameters"),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Sequence steps metadata"),
        sa.Column("process_id", sa.Integer(), nullable=True, comment="Target process ID"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true", comment="Whether sequence is active"),
        sa.Column("is_deprecated", sa.Boolean(), nullable=False, server_default="false", comment="Whether sequence is deprecated"),
        sa.Column("uploaded_by", sa.Integer(), nullable=True, comment="User who uploaded"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_sequences_name"), "sequences", ["name"], unique=True)

    # Create sequence_versions table
    op.create_table(
        "sequence_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sequence_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False, comment="Version string"),
        sa.Column("package_data", sa.Text(), nullable=False, comment="Base64-encoded ZIP package"),
        sa.Column("checksum", sa.String(length=64), nullable=False, comment="SHA-256 checksum"),
        sa.Column("package_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hardware", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("change_notes", sa.Text(), nullable=True, comment="Release notes"),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sequence_id"], ["sequences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sequence_id", "version", name="uq_sequence_version"),
    )
    op.create_index(op.f("ix_sequence_versions_sequence_id"), "sequence_versions", ["sequence_id"], unique=False)
    op.create_index("ix_sequence_versions_sequence_version", "sequence_versions", ["sequence_id", "version"], unique=False)

    # Create sequence_deployments table
    op.create_table(
        "sequence_deployments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sequence_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.String(length=50), nullable=True, comment="Target station ID"),
        sa.Column("batch_id", sa.String(length=50), nullable=True, comment="Target batch ID"),
        sa.Column("version", sa.String(length=20), nullable=False, comment="Deployed version"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending", comment="Deployment status"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="Error message if failed"),
        sa.Column("deployed_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True, comment="When deployment confirmed"),
        sa.ForeignKeyConstraint(["sequence_id"], ["sequences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["deployed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sequence_deployments_sequence_id"), "sequence_deployments", ["sequence_id"], unique=False)
    op.create_index("ix_sequence_deployments_station", "sequence_deployments", ["station_id", "batch_id"], unique=False)
    op.create_index("ix_sequence_deployments_status", "sequence_deployments", ["status"], unique=False)


def downgrade() -> None:
    op.drop_table("sequence_deployments")
    op.drop_table("sequence_versions")
    op.drop_table("sequences")
