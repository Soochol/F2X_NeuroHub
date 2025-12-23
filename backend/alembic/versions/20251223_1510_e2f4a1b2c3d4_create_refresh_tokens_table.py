"""create refresh_tokens table

Revision ID: e2f4a1b2c3d4
Revises: d7a413c6064f
Create Date: 2025-12-23 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2f4a1b2c3d4'
down_revision = 'd7a413c6064f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
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
    op.drop_index(op.f('idx_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('idx_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
