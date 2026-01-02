"""add process_headers table and header_id to related tables

Revision ID: b2c3d4e5f6a7
Revises: 5b352de4c7b4
Create Date: 2025-01-02 00:01:00.000000

This migration adds the process_headers table for tracking execution sessions
at the station/batch level, enabling:
- Station/batch-level process tracking
- Parameter snapshot storage for audit
- Aggregated statistics per execution session
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = '5b352de4c7b4'
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(table_name: str, index_name: str) -> bool:
    """Check if an index exists on a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        indexes = inspector.get_indexes(table_name)
        return any(idx['name'] == index_name for idx in indexes)
    except Exception:
        return False


def upgrade() -> None:
    """Apply migration: Create process_headers table and add header_id columns."""

    # =========================================================================
    # 1. Create process_headers table
    # =========================================================================
    if not table_exists('process_headers'):
        op.create_table(
            'process_headers',
            # Primary Key
            sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),

            # Station and Batch identification
            sa.Column('station_id', sa.String(length=100), nullable=False,
                      comment='Station identifier (from station config)'),
            sa.Column('batch_id', sa.String(length=200), nullable=False,
                      comment='Batch identifier from station_service'),

            # Process reference
            sa.Column('process_id', sa.BigInteger(), nullable=False,
                      comment='Foreign key to processes table'),

            # Sequence information (snapshot at header creation)
            sa.Column('sequence_package', sa.String(length=255), nullable=True,
                      comment='Sequence package name (e.g., sensor_inspection)'),
            sa.Column('sequence_version', sa.String(length=50), nullable=True,
                      comment='Sequence version at execution time'),

            # Configuration snapshots (JSONB for flexibility)
            sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()),
                      nullable=True, server_default=sa.text("'{}'::jsonb"),
                      comment='Batch parameters snapshot'),
            sa.Column('hardware_config', postgresql.JSONB(astext_type=sa.Text()),
                      nullable=True, server_default=sa.text("'{}'::jsonb"),
                      comment='Hardware configuration snapshot'),

            # Status tracking
            sa.Column('status', sa.String(length=20), nullable=False,
                      server_default=sa.text("'OPEN'"),
                      comment='Header status: OPEN, CLOSED, CANCELLED'),

            # Timing
            sa.Column('opened_at', sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text('CURRENT_TIMESTAMP'),
                      comment='When the header was opened (batch started)'),
            sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True,
                      comment='When the header was closed (batch ended)'),

            # Aggregated statistics (denormalized for performance)
            sa.Column('total_count', sa.Integer(), nullable=False, server_default=sa.text('0'),
                      comment='Total WIP items processed in this header'),
            sa.Column('pass_count', sa.Integer(), nullable=False, server_default=sa.text('0'),
                      comment='Number of PASS results'),
            sa.Column('fail_count', sa.Integer(), nullable=False, server_default=sa.text('0'),
                      comment='Number of FAIL results'),

            # Audit timestamps
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text('CURRENT_TIMESTAMP'),
                      comment='Record creation timestamp'),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text('CURRENT_TIMESTAMP'),
                      comment='Last update timestamp'),

            # Constraints
            sa.PrimaryKeyConstraint('id', name='pk_process_headers'),
            sa.ForeignKeyConstraint(
                ['process_id'], ['processes.id'],
                name='fk_process_headers_process',
                ondelete='RESTRICT', onupdate='CASCADE'
            ),
            sa.CheckConstraint(
                "status IN ('OPEN', 'CLOSED', 'CANCELLED')",
                name='chk_process_headers_status'
            ),
            sa.CheckConstraint(
                "closed_at IS NULL OR closed_at >= opened_at",
                name='chk_process_headers_timestamps'
            ),
            sa.CheckConstraint(
                "total_count >= 0 AND pass_count >= 0 AND fail_count >= 0",
                name='chk_process_headers_counts'
            ),
        )

        # Indexes for process_headers
        op.create_index(
            'idx_process_headers_station',
            'process_headers', ['station_id'],
            unique=False
        )
        op.create_index(
            'idx_process_headers_batch',
            'process_headers', ['batch_id'],
            unique=False
        )
        op.create_index(
            'idx_process_headers_process',
            'process_headers', ['process_id'],
            unique=False
        )
        op.create_index(
            'idx_process_headers_status',
            'process_headers', ['status'],
            unique=False
        )
        op.create_index(
            'idx_process_headers_opened_at',
            'process_headers', ['opened_at'],
            unique=False
        )
        # Composite index for common queries
        op.create_index(
            'idx_process_headers_station_batch_process',
            'process_headers', ['station_id', 'batch_id', 'process_id'],
            unique=False
        )
        # Unique partial index: only one OPEN header per station+batch+process
        op.create_index(
            'uk_process_headers_open',
            'process_headers', ['station_id', 'batch_id', 'process_id'],
            unique=True,
            postgresql_where=sa.text("status = 'OPEN'")
        )
        # GIN indexes for JSONB columns
        op.create_index(
            'idx_process_headers_parameters',
            'process_headers', ['parameters'],
            unique=False,
            postgresql_using='gin'
        )
        op.create_index(
            'idx_process_headers_hardware_config',
            'process_headers', ['hardware_config'],
            unique=False,
            postgresql_using='gin'
        )

    # =========================================================================
    # 2. Add header_id column to process_data table
    # =========================================================================
    if table_exists('process_data') and not column_exists('process_data', 'header_id'):
        op.add_column(
            'process_data',
            sa.Column('header_id', sa.BigInteger(), nullable=True,
                      comment='Foreign key to process_headers (execution session)')
        )
        op.create_foreign_key(
            'fk_process_data_header',
            'process_data', 'process_headers',
            ['header_id'], ['id'],
            ondelete='SET NULL', onupdate='CASCADE'
        )
        if not index_exists('process_data', 'idx_process_data_header'):
            op.create_index(
                'idx_process_data_header',
                'process_data', ['header_id'],
                unique=False
            )

    # =========================================================================
    # 3. Add header_id column to wip_process_history table
    # =========================================================================
    if table_exists('wip_process_history') and not column_exists('wip_process_history', 'header_id'):
        op.add_column(
            'wip_process_history',
            sa.Column('header_id', sa.BigInteger(), nullable=True,
                      comment='Foreign key to process_headers (execution session)')
        )
        op.create_foreign_key(
            'fk_wip_history_header',
            'wip_process_history', 'process_headers',
            ['header_id'], ['id'],
            ondelete='SET NULL', onupdate='CASCADE'
        )
        if not index_exists('wip_process_history', 'idx_wip_history_header'):
            op.create_index(
                'idx_wip_history_header',
                'wip_process_history', ['header_id'],
                unique=False
            )

    # =========================================================================
    # 4. Create trigger function for updating header statistics
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_header_statistics()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update on INSERT
            IF TG_OP = 'INSERT' AND NEW.header_id IS NOT NULL THEN
                UPDATE process_headers
                SET
                    total_count = total_count + 1,
                    pass_count = pass_count + CASE WHEN NEW.result = 'PASS' THEN 1 ELSE 0 END,
                    fail_count = fail_count + CASE WHEN NEW.result = 'FAIL' THEN 1 ELSE 0 END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.header_id;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # =========================================================================
    # 5. Create triggers on process_data and wip_process_history
    # =========================================================================
    op.execute("""
        DROP TRIGGER IF EXISTS trg_process_data_update_header_stats ON process_data;
        CREATE TRIGGER trg_process_data_update_header_stats
        AFTER INSERT ON process_data
        FOR EACH ROW
        EXECUTE FUNCTION update_header_statistics();
    """)

    op.execute("""
        DROP TRIGGER IF EXISTS trg_wip_history_update_header_stats ON wip_process_history;
        CREATE TRIGGER trg_wip_history_update_header_stats
        AFTER INSERT ON wip_process_history
        FOR EACH ROW
        EXECUTE FUNCTION update_header_statistics();
    """)

    # =========================================================================
    # 6. Create trigger for auto-updating updated_at
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_process_headers_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_process_headers_updated_at ON process_headers;
        CREATE TRIGGER trg_process_headers_updated_at
        BEFORE UPDATE ON process_headers
        FOR EACH ROW
        EXECUTE FUNCTION update_process_headers_updated_at();
    """)


def downgrade() -> None:
    """Revert migration: Drop process_headers table and related columns."""

    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS trg_wip_history_update_header_stats ON wip_process_history;")
    op.execute("DROP TRIGGER IF EXISTS trg_process_data_update_header_stats ON process_data;")
    op.execute("DROP TRIGGER IF EXISTS trg_process_headers_updated_at ON process_headers;")
    op.execute("DROP FUNCTION IF EXISTS update_header_statistics();")
    op.execute("DROP FUNCTION IF EXISTS update_process_headers_updated_at();")

    # Remove header_id from wip_process_history
    if table_exists('wip_process_history') and column_exists('wip_process_history', 'header_id'):
        if index_exists('wip_process_history', 'idx_wip_history_header'):
            op.drop_index('idx_wip_history_header', table_name='wip_process_history')
        op.drop_constraint('fk_wip_history_header', 'wip_process_history', type_='foreignkey')
        op.drop_column('wip_process_history', 'header_id')

    # Remove header_id from process_data
    if table_exists('process_data') and column_exists('process_data', 'header_id'):
        if index_exists('process_data', 'idx_process_data_header'):
            op.drop_index('idx_process_data_header', table_name='process_data')
        op.drop_constraint('fk_process_data_header', 'process_data', type_='foreignkey')
        op.drop_column('process_data', 'header_id')

    # Drop process_headers table
    if table_exists('process_headers'):
        # Drop indexes
        for idx_name in [
            'idx_process_headers_parameters',
            'idx_process_headers_hardware_config',
            'uk_process_headers_open',
            'idx_process_headers_station_batch_process',
            'idx_process_headers_opened_at',
            'idx_process_headers_status',
            'idx_process_headers_process',
            'idx_process_headers_batch',
            'idx_process_headers_station',
        ]:
            if index_exists('process_headers', idx_name):
                op.drop_index(idx_name, table_name='process_headers')

        op.drop_table('process_headers')
