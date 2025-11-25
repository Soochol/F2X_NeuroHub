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
    """Add index for wip_process_history queries."""
    # Add an index to support queries for latest results
    # This index helps find the most recent completion for each WIP + Process
    op.create_index(
        'idx_wip_history_wip_process_completed',
        'wip_process_history',
        ['wip_id', 'process_id', 'completed_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove the index."""
    op.drop_index(
        'idx_wip_history_wip_process_completed',
        table_name='wip_process_history'
    )
