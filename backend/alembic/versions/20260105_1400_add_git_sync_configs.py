"""add git_sync_configs table

Revision ID: d0e1f2a3b4c5
Revises: c3d4e5f6a7b8
Create Date: 2026-01-05 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0e1f2a3b4c5'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'git_sync_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('repository_url', sa.String(length=500), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False, server_default='main'),
        sa.Column('folder_path', sa.String(length=500), nullable=True),
        sa.Column('auth_type', sa.String(length=20), nullable=False, server_default='none'),
        sa.Column('auth_token', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('poll_interval_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('auto_upload', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_commit_sha', sa.String(length=40), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_check_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_status', sa.String(length=20), nullable=False, server_default='idle'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_git_sync_configs_name', 'git_sync_configs', ['name'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_git_sync_configs_name', table_name='git_sync_configs')
    op.drop_table('git_sync_configs')
