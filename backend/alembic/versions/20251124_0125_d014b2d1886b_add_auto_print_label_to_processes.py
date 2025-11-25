"""add_auto_print_label_to_processes

Revision ID: d014b2d1886b
Revises: 0003_add_wip_unique_index
Create Date: 2025-11-24 01:25:29.377894

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd014b2d1886b'
down_revision = '0003_add_wip_unique_index'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration - Add auto_print_label and supporting tables."""
    # Create saved_filters table
    op.create_table('saved_filters',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filters', sa.JSON(), nullable=False),
        sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create print_logs table
    op.create_table('print_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label_type', sa.String(length=50), nullable=False, comment='Label template type (WIP_LABEL, SERIAL_LABEL, LOT_LABEL)'),
        sa.Column('label_id', sa.String(length=255), nullable=False, comment='ID of the printed label'),
        sa.Column('process_id', sa.Integer(), nullable=True, comment='Associated process ID'),
        sa.Column('process_data_id', sa.Integer(), nullable=True, comment='Associated process data ID'),
        sa.Column('printer_ip', sa.String(length=50), nullable=True, comment='Printer IP address'),
        sa.Column('printer_port', sa.Integer(), nullable=True, comment='Printer port number'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Print status (SUCCESS/FAILED)'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if print failed'),
        sa.Column('operator_id', sa.Integer(), nullable=True, comment='User who triggered the print'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Print timestamp'),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['process_data_id'], ['process_data.id'], ),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_print_logs_created_at', 'print_logs', ['created_at'], unique=False)
    op.create_index('idx_print_logs_label_type', 'print_logs', ['label_type'], unique=False)
    op.create_index('idx_print_logs_status', 'print_logs', ['status'], unique=False)

    # Add defects and duration_seconds columns to process_data
    op.add_column('process_data', sa.Column('defects', sa.JSON(), nullable=True))
    op.add_column('process_data', sa.Column('duration_seconds', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Revert migration."""
    # Remove columns from process_data
    op.drop_column('process_data', 'duration_seconds')
    op.drop_column('process_data', 'defects')

    # Drop print_logs table
    op.drop_index('idx_print_logs_status', table_name='print_logs')
    op.drop_index('idx_print_logs_label_type', table_name='print_logs')
    op.drop_index('idx_print_logs_created_at', table_name='print_logs')
    op.drop_table('print_logs')

    # Drop saved_filters table
    op.drop_table('saved_filters')
