"""add auto print label to processes

Revision ID: add_auto_print_label
Revises: 
Create Date: 2025-11-23 17:42:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_auto_print_label'
down_revision = None  # Update this with your latest revision
branch_labels = None
depends_on = None


def upgrade():
    # Add auto_print_label column
    op.add_column(
        'processes',
        sa.Column('auto_print_label', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Add label_template_type column
    op.add_column(
        'processes',
        sa.Column('label_template_type', sa.VARCHAR(50), nullable=True)
    )
    
    # Example: Enable auto-print for process 6 with WIP label
    op.execute(
        """
        UPDATE processes 
        SET auto_print_label = true, 
            label_template_type = 'WIP_LABEL'
        WHERE process_number = 6
        """
    )


def downgrade():
    op.drop_column('processes', 'label_template_type')
    op.drop_column('processes', 'auto_print_label')
