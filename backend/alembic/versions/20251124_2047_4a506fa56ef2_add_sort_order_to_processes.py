"""add_sort_order_to_processes

Revision ID: 4a506fa56ef2
Revises: 72b4ce422921
Create Date: 2025-11-24 20:47:36.063855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a506fa56ef2'
down_revision = '72b4ce422921'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration using batch_alter_table for SQLite compatibility."""
    # Using batch_alter_table handles table recreation for SQLite automatically
    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sort_order', sa.Integer(), nullable=True))

    # Set sort_order to match process_number for existing records
    op.execute('UPDATE processes SET sort_order = process_number')

    with op.batch_alter_table('processes', schema=None) as batch_op:
        # Make sort_order NOT NULL and add check constraint
        batch_op.alter_column('sort_order', nullable=False)
        batch_op.create_check_constraint(
            'chk_processes_sort_order_positive',
            condition='sort_order > 0'
        )


def downgrade() -> None:
    """Revert migration."""
    # Drop check constraint
    op.drop_constraint('chk_processes_sort_order_positive', 'processes', type_='check')

    # Drop sort_order column
    op.drop_column('processes', 'sort_order')
