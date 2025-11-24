"""add_process_type_column

Revision ID: 84d565a78b6d
Revises: d014b2d1886b
Create Date: 2025-11-24 15:24:19.716977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84d565a78b6d'
down_revision = 'd014b2d1886b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration - Add process_type column to processes table."""
    # Add the process_type column with default value
    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'process_type',
                sa.String(length=50),
                nullable=False,
                server_default='MANUFACTURING',
                comment='공정 유형 (MANUFACTURING, SERIAL_CONVERSION)'
            )
        )
    
    # Update existing processes based on process_number
    # Process 7 (and any future process 8) should be SERIAL_CONVERSION
    # All others (1-6) should be MANUFACTURING
    op.execute("""
        UPDATE processes 
        SET process_type = 'SERIAL_CONVERSION' 
        WHERE process_number >= 7
    """)
    
    # Note: Processes 1-6 already have 'MANUFACTURING' from the server_default


def downgrade() -> None:
    """Revert migration - Remove process_type column from processes table."""
    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.drop_column('process_type')