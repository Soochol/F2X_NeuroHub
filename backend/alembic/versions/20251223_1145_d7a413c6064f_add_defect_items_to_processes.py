"""add defect_items to processes

Revision ID: d7a413c6064f
Revises: 4a506fa56ef2
Create Date: 2025-12-23 11:45:26.436165

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd7a413c6064f'
down_revision = '4a506fa56ef2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    # Add defect_items column with default empty list JSON
    # Using postgresql.JSONB for PostgreSQL to support GIN index
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.add_column('processes', sa.Column(
            'defect_items', 
            postgresql.JSONB(astext_type=sa.Text()), 
            nullable=False, 
            server_default='[]'
        ))
        
        # Add GIN index for efficient JSON querying
        op.create_index(
            'idx_processes_defect_items',
            'processes',
            ['defect_items'],
            unique=False,
            postgresql_using='gin'
        )
    else:
        # Fallback for other dialects (e.g. SQLite)
        op.add_column('processes', sa.Column(
            'defect_items', 
            sa.JSON(), 
            nullable=False, 
            server_default='[]'
        ))


def downgrade() -> None:
    """Revert migration."""
    # Drop index if it exists (only on PostgreSQL)
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.drop_index('idx_processes_defect_items', table_name='processes')
    
    # Drop defect_items column
    op.drop_column('processes', 'defect_items')
