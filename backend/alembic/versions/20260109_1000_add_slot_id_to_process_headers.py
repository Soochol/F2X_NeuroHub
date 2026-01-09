"""add slot_id to process_headers table

Revision ID: 3e25d5f87008
Revises: d0e1f2a3b4c5
Create Date: 2026-01-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e25d5f87008'
down_revision: Union[str, None] = 'd0e1f2a3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add slot_id column (1-12 range for UI display order)
    op.add_column(
        'process_headers',
        sa.Column(
            'slot_id',
            sa.Integer(),
            nullable=True,
            comment='Slot ID for UI display order (1-12 per station)',
        ),
    )

    # Add check constraint for slot_id range (1-12)
    op.create_check_constraint(
        'chk_process_headers_slot_id_range',
        'process_headers',
        'slot_id IS NULL OR (slot_id >= 1 AND slot_id <= 12)',
    )

    # Add unique partial index: one slot per station when OPEN
    op.execute(
        """
        CREATE UNIQUE INDEX uk_process_headers_station_slot
        ON process_headers (station_id, slot_id)
        WHERE status = 'OPEN' AND slot_id IS NOT NULL
        """
    )

    # Add regular index for slot_id queries
    op.create_index(
        'idx_process_headers_slot_id',
        'process_headers',
        ['slot_id'],
    )


def downgrade() -> None:
    op.drop_index('idx_process_headers_slot_id', table_name='process_headers')
    op.execute('DROP INDEX IF EXISTS uk_process_headers_station_slot')
    op.drop_constraint('chk_process_headers_slot_id_range', 'process_headers', type_='check')
    op.drop_column('process_headers', 'slot_id')
