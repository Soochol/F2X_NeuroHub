"""remove_wip_process_history_unique_constraint

Revision ID: a1b2c3d4e5f6
Revises: 84d565a78b6d
Create Date: 2025-11-24 16:23:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '84d565a78b6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove unique constraint from wip_process_history to allow multiple attempts."""
    # Drop the unique index that prevents multiple PASS results
    op.drop_index(
        'uk_wip_history_wip_process_pass',
        table_name='wip_process_history'
    )
    
    # Add a new index to support queries for latest results
    # This index helps find the most recent completion for each WIP + Process
    op.create_index(
        'idx_wip_history_wip_process_completed',
        'wip_process_history',
        ['wip_item_id', 'process_id', sa.text('completed_at DESC')],
        unique=False
    )


def downgrade() -> None:
    """Restore unique constraint (only if no duplicate PASS records exist)."""
    # Drop the new index
    op.drop_index(
        'idx_wip_history_wip_process_completed',
        table_name='wip_process_history'
    )
    
    # Restore the unique index
    # WARNING: This will fail if duplicate PASS records exist
    op.create_index(
        'uk_wip_history_wip_process_pass',
        'wip_process_history',
        ['wip_item_id', 'process_id'],
        unique=True,
        postgresql_where=sa.text("result = 'PASS'")
    )
