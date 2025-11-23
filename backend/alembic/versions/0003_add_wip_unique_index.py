"""Add unique index for WIP-based process tracking

Revision ID: 0003_add_wip_unique_index
Revises: 0002_add_wip_support
Create Date: 2025-11-23 23:35:00

This migration adds a unique partial index on (lot_id, process_id, wip_id) to ensure
data integrity for WIP-level process tracking. The index only applies when wip_id
is NOT NULL, allowing multiple LOT-level entries for the same process.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '0003_add_wip_unique_index'
down_revision = '0002_add_wip_support'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique index for WIP process tracking."""

    # Get database dialect
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        # PostgreSQL supports partial indexes with WHERE clause
        op.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_process_data_lot_process_wip
            ON process_data(lot_id, process_id, wip_id)
            WHERE wip_id IS NOT NULL
        """))
    elif dialect_name == 'sqlite':
        # SQLite also supports partial indexes with WHERE clause
        # Note: IF NOT EXISTS is supported in SQLite 3.9.0+
        try:
            op.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_process_data_lot_process_wip
                ON process_data(lot_id, process_id, wip_id)
                WHERE wip_id IS NOT NULL
            """))
        except Exception:
            # Fallback for older SQLite versions
            # First check if index exists
            result = bind.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='uq_process_data_lot_process_wip'
            """))
            if not result.fetchone():
                op.execute(text("""
                    CREATE UNIQUE INDEX uq_process_data_lot_process_wip
                    ON process_data(lot_id, process_id, wip_id)
                    WHERE wip_id IS NOT NULL
                """))
    else:
        # For other databases that don't support partial indexes,
        # create a regular unique index (may need adjustment based on requirements)
        op.create_unique_constraint(
            'uq_process_data_lot_process_wip',
            'process_data',
            ['lot_id', 'process_id', 'wip_id']
        )


def downgrade() -> None:
    """Remove unique index for WIP process tracking."""

    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name in ['postgresql', 'sqlite']:
        # Drop the index using raw SQL
        op.execute(text("DROP INDEX IF EXISTS uq_process_data_lot_process_wip"))
    else:
        # For other databases, drop as constraint
        op.drop_constraint('uq_process_data_lot_process_wip', 'process_data', type_='unique')