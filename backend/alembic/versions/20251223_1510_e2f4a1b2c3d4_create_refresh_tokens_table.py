"""create refresh_tokens table

Revision ID: e2f4a1b2c3d4
Revises: d7a413c6064f
Create Date: 2025-12-23 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'e2f4a1b2c3d4'
down_revision = 'd7a413c6064f'
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def index_exists(table_name: str, index_name: str) -> bool:
    """Check if an index exists on a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)


def upgrade() -> None:
    """Apply migration."""
    # Check if table already exists (idempotent migration)
    if table_exists('refresh_tokens'):
        return

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('idx_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('idx_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    """Revert migration."""
    # Only drop if table exists (idempotent downgrade)
    if not table_exists('refresh_tokens'):
        return

    if index_exists('refresh_tokens', 'idx_refresh_tokens_user_id'):
        op.drop_index(op.f('idx_refresh_tokens_user_id'), table_name='refresh_tokens')
    if index_exists('refresh_tokens', 'idx_refresh_tokens_token'):
        op.drop_index(op.f('idx_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
