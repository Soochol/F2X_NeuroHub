"""Prevent duplicate incomplete WIP process records

Revision ID: 20260109_1100
Revises: 20260109_1030
Create Date: 2026-01-09 11:00:00.000000

This migration adds a unique constraint to prevent multiple incomplete
ProcessData records for the same WIP+process combination. This ensures
that only one in-progress record can exist at a time, while still
allowing multiple completed records for rework scenarios.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260109_1100'
down_revision = '20260109_1030'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint for incomplete WIP process records."""

    # Create partial unique index: only one incomplete ProcessData per WIP+process
    # This prevents race conditions and duplicate in-progress records
    # while still allowing multiple completed records for rework scenarios
    op.execute("""
        CREATE UNIQUE INDEX uk_process_data_wip_process_incomplete
        ON process_data(wip_id, process_id)
        WHERE wip_id IS NOT NULL AND completed_at IS NULL;
    """)


def downgrade():
    """Remove unique constraint for incomplete WIP process records."""

    # Drop the unique index
    op.execute("DROP INDEX IF EXISTS uk_process_data_wip_process_incomplete;")
