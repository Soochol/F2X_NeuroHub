"""Add WIP support to process_data table

Revision ID: 0002_add_wip_support
Revises: 0001_initial
Create Date: 2025-11-23 23:30:00

This migration adds comprehensive WIP support to the process_data table including:
- lot_id column for LOT-level tracking
- Proper constraints for data_level (LOT, WIP, SERIAL)
- Updated foreign key relationships
- Performance indexes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_add_wip_support'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add WIP support to process_data table."""

    # For SQLite, we need to handle migrations differently
    # Check if we're using SQLite or PostgreSQL
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'sqlite':
        # SQLite doesn't support ALTER TABLE for adding constraints
        # We need to recreate the table
        upgrade_sqlite()
    else:
        # PostgreSQL supports direct ALTER TABLE
        upgrade_postgresql()


def upgrade_postgresql():
    """PostgreSQL-specific upgrade."""

    # Add lot_id column if it doesn't exist
    op.add_column('process_data',
        sa.Column('lot_id', sa.BigInteger(), nullable=False)
    )

    # Add foreign key constraint for lot_id
    op.create_foreign_key(
        'fk_process_data_lot',
        'process_data', 'lots',
        ['lot_id'], ['id'],
        ondelete='RESTRICT',
        onupdate='CASCADE'
    )

    # Drop old constraints
    op.drop_constraint('ck_process_data_wip_or_serial', 'process_data', type_='check')
    op.drop_constraint('ck_process_data_level', 'process_data', type_='check')

    # Add new constraints for data_level
    op.create_check_constraint(
        'ck_process_data_data_level',
        'process_data',
        "data_level IN ('LOT', 'WIP', 'SERIAL')"
    )

    # Add constraint for WIP/Serial consistency
    op.create_check_constraint(
        'ck_process_data_consistency',
        'process_data',
        """
        (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR
        (data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR
        (data_level = 'SERIAL' AND serial_id IS NOT NULL)
        """
    )

    # Add indexes for performance
    op.create_index('idx_process_data_lot', 'process_data', ['lot_id'])
    op.create_index('idx_process_data_lot_process', 'process_data', ['lot_id', 'process_id', 'result'])
    op.create_index('idx_process_data_data_level_lot', 'process_data', ['data_level', 'lot_id'])


def upgrade_sqlite():
    """SQLite-specific upgrade using table recreation."""

    # Step 1: Rename existing table
    op.execute("DROP TABLE IF EXISTS process_data_old")
    op.rename_table('process_data', 'process_data_old')

    # Step 2: Create new table with updated schema
    op.create_table('process_data',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_id', sa.BigInteger(), nullable=False),
        sa.Column('wip_id', sa.BigInteger(), nullable=True),
        sa.Column('serial_id', sa.BigInteger(), nullable=True),
        sa.Column('process_id', sa.BigInteger(), nullable=False),
        sa.Column('operator_id', sa.BigInteger(), nullable=False),
        sa.Column('equipment_id', sa.BigInteger(), nullable=True),
        sa.Column('data_level', sa.String(length=10), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('process_time_seconds', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(length=10), nullable=False, server_default='pending'),
        sa.Column('measurements', sa.JSON(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('defect_code', sa.String(length=50), nullable=True),
        sa.Column('defect_reason', sa.Text(), nullable=True),
        sa.Column('rework_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("data_level IN ('LOT', 'WIP', 'SERIAL')",
                          name='ck_process_data_data_level'),
        sa.CheckConstraint("result IN ('pending', 'pass', 'fail', 'rework')",
                          name='ck_process_data_result'),
        sa.CheckConstraint(
            """
            (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR
            (data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR
            (data_level = 'SERIAL' AND serial_id IS NOT NULL)
            """,
            name='ck_process_data_consistency'
        ),
        sa.CheckConstraint('process_time_seconds >= 0', name='ck_process_data_time'),
        sa.CheckConstraint('rework_count >= 0', name='ck_process_data_rework_count'),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='RESTRICT', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id']),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id']),
        sa.ForeignKeyConstraint(['serial_id'], ['serials.id']),
        sa.ForeignKeyConstraint(['wip_id'], ['wip_items.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Step 3: Migrate data from old table
    # We need to handle the fact that lot_id might not exist in old data
    # We'll derive it from wip_id or serial_id relationships
    op.execute("""
        INSERT INTO process_data
        SELECT
            pd.id,
            COALESCE(wi.lot_id, s.lot_id, 0) as lot_id,  -- Get lot_id from relationships
            pd.wip_id,
            pd.serial_id,
            pd.process_id,
            pd.operator_id,
            pd.equipment_id,
            CASE
                WHEN pd.serial_id IS NOT NULL THEN 'SERIAL'
                WHEN pd.wip_id IS NOT NULL THEN 'WIP'
                ELSE 'LOT'
            END as data_level,
            pd.started_at,
            pd.completed_at,
            pd.process_time_seconds,
            pd.result,
            pd.measurements,
            pd.parameters,
            pd.defect_code,
            pd.defect_reason,
            pd.rework_count,
            pd.notes,
            pd.created_at,
            pd.updated_at
        FROM process_data_old pd
        LEFT JOIN wip_items wi ON pd.wip_id = wi.id
        LEFT JOIN serials s ON pd.serial_id = s.id
    """)

    # Step 4: Drop old table
    op.drop_table('process_data_old')

    # Step 5: Recreate indexes
    op.create_index('idx_process_data_completed', 'process_data', ['completed_at'])
    op.create_index('idx_process_data_level', 'process_data', ['data_level'])
    op.create_index('idx_process_data_lot', 'process_data', ['lot_id'])
    op.create_index('idx_process_data_operator', 'process_data', ['operator_id'])
    op.create_index('idx_process_data_process', 'process_data', ['process_id'])
    op.create_index('idx_process_data_result', 'process_data', ['result'])
    op.create_index('idx_process_data_serial', 'process_data', ['serial_id'])
    op.create_index('idx_process_data_started', 'process_data', ['started_at'])
    op.create_index('idx_process_data_wip', 'process_data', ['wip_id'])
    op.create_index('idx_process_data_lot_process', 'process_data', ['lot_id', 'process_id', 'result'])
    op.create_index('idx_process_data_data_level_lot', 'process_data', ['data_level', 'lot_id'])


def downgrade() -> None:
    """Remove WIP support from process_data table."""

    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'sqlite':
        downgrade_sqlite()
    else:
        downgrade_postgresql()


def downgrade_postgresql():
    """PostgreSQL-specific downgrade."""

    # Drop new indexes
    op.drop_index('idx_process_data_data_level_lot', table_name='process_data')
    op.drop_index('idx_process_data_lot_process', table_name='process_data')
    op.drop_index('idx_process_data_lot', table_name='process_data')

    # Drop new constraints
    op.drop_constraint('ck_process_data_consistency', 'process_data', type_='check')
    op.drop_constraint('ck_process_data_data_level', 'process_data', type_='check')

    # Recreate old constraints
    op.create_check_constraint(
        'ck_process_data_level',
        'process_data',
        "data_level IN ('wip', 'serial')"
    )

    op.create_check_constraint(
        'ck_process_data_wip_or_serial',
        'process_data',
        "(wip_id IS NOT NULL AND serial_id IS NULL) OR (wip_id IS NULL AND serial_id IS NOT NULL)"
    )

    # Drop foreign key constraint
    op.drop_constraint('fk_process_data_lot', 'process_data', type_='foreignkey')

    # Drop lot_id column
    op.drop_column('process_data', 'lot_id')


def downgrade_sqlite():
    """SQLite-specific downgrade using table recreation."""

    # Rename current table
    op.rename_table('process_data', 'process_data_temp')

    # Create table with old schema
    op.create_table('process_data',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wip_id', sa.BigInteger(), nullable=True),
        sa.Column('serial_id', sa.BigInteger(), nullable=True),
        sa.Column('process_id', sa.BigInteger(), nullable=False),
        sa.Column('operator_id', sa.BigInteger(), nullable=False),
        sa.Column('equipment_id', sa.BigInteger(), nullable=True),
        sa.Column('data_level', sa.String(length=10), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('process_time_seconds', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(length=10), nullable=False, server_default='pending'),
        sa.Column('measurements', sa.JSON(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('defect_code', sa.String(length=50), nullable=True),
        sa.Column('defect_reason', sa.Text(), nullable=True),
        sa.Column('rework_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("data_level IN ('wip', 'serial')", name='ck_process_data_level'),
        sa.CheckConstraint("result IN ('pending', 'pass', 'fail', 'rework')",
                          name='ck_process_data_result'),
        sa.CheckConstraint(
            "(wip_id IS NOT NULL AND serial_id IS NULL) OR (wip_id IS NULL AND serial_id IS NOT NULL)",
            name='ck_process_data_wip_or_serial'
        ),
        sa.CheckConstraint('process_time_seconds >= 0', name='ck_process_data_time'),
        sa.CheckConstraint('rework_count >= 0', name='ck_process_data_rework_count'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id']),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id']),
        sa.ForeignKeyConstraint(['serial_id'], ['serials.id']),
        sa.ForeignKeyConstraint(['wip_id'], ['wip_items.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Migrate data back (excluding LOT-level records)
    op.execute("""
        INSERT INTO process_data
        SELECT
            id, wip_id, serial_id, process_id, operator_id, equipment_id,
            CASE
                WHEN serial_id IS NOT NULL THEN 'serial'
                ELSE 'wip'
            END as data_level,
            started_at, completed_at, process_time_seconds, result,
            measurements, parameters, defect_code, defect_reason,
            rework_count, notes, created_at, updated_at
        FROM process_data_temp
        WHERE data_level != 'LOT'
    """)

    # Drop temporary table
    op.drop_table('process_data_temp')

    # Recreate original indexes
    op.create_index('idx_process_data_completed', 'process_data', ['completed_at'])
    op.create_index('idx_process_data_level', 'process_data', ['data_level'])
    op.create_index('idx_process_data_operator', 'process_data', ['operator_id'])
    op.create_index('idx_process_data_process', 'process_data', ['process_id'])
    op.create_index('idx_process_data_result', 'process_data', ['result'])
    op.create_index('idx_process_data_serial', 'process_data', ['serial_id'])
    op.create_index('idx_process_data_started', 'process_data', ['started_at'])
    op.create_index('idx_process_data_wip', 'process_data', ['wip_id'])