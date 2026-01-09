"""Rename header_id to process_session_id

Revision ID: 20260109_1030
Revises: 3e25d5f87008
Create Date: 2026-01-09 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260109_1030'
down_revision = '3e25d5f87008'
branch_labels = None
depends_on = None


def upgrade():
    """Rename header_id to process_session_id in process_data and wip_process_history tables."""

    # ============================================================
    # 1. process_data table
    # ============================================================

    # Drop foreign key constraint
    op.drop_constraint('process_data_header_id_fkey', 'process_data', type_='foreignkey')

    # Drop index
    op.drop_index('idx_process_data_header', 'process_data')

    # Rename column
    op.alter_column('process_data', 'header_id', new_column_name='process_session_id')

    # Recreate foreign key constraint with new column name
    op.create_foreign_key(
        'process_data_process_session_id_fkey',
        'process_data', 'process_headers',
        ['process_session_id'], ['id'],
        ondelete='SET NULL', onupdate='CASCADE'
    )

    # Recreate index with new column name
    op.create_index('idx_process_data_session', 'process_data', ['process_session_id'])

    # ============================================================
    # 2. wip_process_history table
    # ============================================================

    # Drop foreign key constraint
    op.drop_constraint('wip_process_history_header_id_fkey', 'wip_process_history', type_='foreignkey')

    # Drop index
    op.drop_index('idx_wip_history_header', 'wip_process_history')

    # Rename column
    op.alter_column('wip_process_history', 'header_id', new_column_name='process_session_id')

    # Recreate foreign key constraint with new column name
    op.create_foreign_key(
        'wip_process_history_process_session_id_fkey',
        'wip_process_history', 'process_headers',
        ['process_session_id'], ['id'],
        ondelete='SET NULL', onupdate='CASCADE'
    )

    # Recreate index with new column name
    op.create_index('idx_wip_history_session', 'wip_process_history', ['process_session_id'])


def downgrade():
    """Rollback: Rename process_session_id back to header_id."""

    # ============================================================
    # 1. wip_process_history table (reverse order)
    # ============================================================

    # Drop index
    op.drop_index('idx_wip_history_session', 'wip_process_history')

    # Drop foreign key constraint
    op.drop_constraint('wip_process_history_process_session_id_fkey', 'wip_process_history', type_='foreignkey')

    # Rename column back
    op.alter_column('wip_process_history', 'process_session_id', new_column_name='header_id')

    # Recreate foreign key constraint with old column name
    op.create_foreign_key(
        'wip_process_history_header_id_fkey',
        'wip_process_history', 'process_headers',
        ['header_id'], ['id'],
        ondelete='SET NULL', onupdate='CASCADE'
    )

    # Recreate index with old column name
    op.create_index('idx_wip_history_header', 'wip_process_history', ['header_id'])

    # ============================================================
    # 2. process_data table (reverse order)
    # ============================================================

    # Drop index
    op.drop_index('idx_process_data_session', 'process_data')

    # Drop foreign key constraint
    op.drop_constraint('process_data_process_session_id_fkey', 'process_data', type_='foreignkey')

    # Rename column back
    op.alter_column('process_data', 'process_session_id', new_column_name='header_id')

    # Recreate foreign key constraint with old column name
    op.create_foreign_key(
        'process_data_header_id_fkey',
        'process_data', 'process_headers',
        ['header_id'], ['id'],
        ondelete='SET NULL', onupdate='CASCADE'
    )

    # Recreate index with old column name
    op.create_index('idx_process_data_header', 'process_data', ['header_id'])
