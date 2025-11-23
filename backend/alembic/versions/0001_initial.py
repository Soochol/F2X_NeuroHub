"""Initial migration - Create all tables

Revision ID: 0001_initial
Revises:
Create Date: 2025-11-23 23:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for F2X NeuroHub MES."""

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('full_name_ko', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='operator'),
        sa.Column('department', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('admin', 'supervisor', 'operator', 'viewer')", name='ck_users_role'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_active', 'users', ['is_active'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('uq_users_email', 'users', ['email'], unique=True)
    op.create_index('uq_users_username', 'users', ['username'], unique=True)

    # Create product_models table
    op.create_table('product_models',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_code', sa.String(length=50), nullable=False),
        sa.Column('product_name', sa.String(length=100), nullable=False),
        sa.Column('product_name_ko', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('product_type', sa.String(length=50), nullable=True),
        sa.Column('lot_size', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.CheckConstraint('lot_size > 0 AND lot_size <= 100', name='ck_product_models_lot_size'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_product_models_active', 'product_models', ['is_active'])
    op.create_index('idx_product_models_type', 'product_models', ['product_type'])
    op.create_index('uq_product_models_product_code', 'product_models', ['product_code'], unique=True)

    # Create production_lines table
    op.create_table('production_lines',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('line_code', sa.String(length=50), nullable=False),
        sa.Column('line_name', sa.String(length=100), nullable=False),
        sa.Column('line_name_ko', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('capacity_per_hour', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("status IN ('active', 'maintenance', 'inactive')", name='ck_production_lines_status'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_production_lines_status', 'production_lines', ['status'])
    op.create_index('uq_production_lines_line_code', 'production_lines', ['line_code'], unique=True)

    # Create processes table
    op.create_table('processes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('process_number', sa.Integer(), nullable=False),
        sa.Column('process_code', sa.String(length=50), nullable=False),
        sa.Column('process_name_ko', sa.String(length=100), nullable=False),
        sa.Column('process_name_en', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quality_criteria', sa.JSON(), nullable=True),
        sa.Column('default_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('requires_equipment', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_print_label', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('label_template_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('process_number >= 1 AND process_number <= 8', name='ck_processes_number_range'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_processes_active', 'processes', ['is_active'])
    op.create_index('uq_processes_process_code', 'processes', ['process_code'], unique=True)
    op.create_index('uq_processes_process_number', 'processes', ['process_number'], unique=True)

    # Create equipment table
    op.create_table('equipment',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('equipment_code', sa.String(length=50), nullable=False),
        sa.Column('equipment_name', sa.String(length=100), nullable=False),
        sa.Column('equipment_name_ko', sa.String(length=100), nullable=True),
        sa.Column('equipment_type', sa.String(length=50), nullable=True),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='available'),
        sa.Column('last_maintenance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_maintenance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calibration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_calibration', sa.DateTime(timezone=True), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('process_id', sa.BigInteger(), nullable=True),
        sa.Column('line_id', sa.BigInteger(), nullable=True),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("status IN ('available', 'in_use', 'maintenance', 'calibration', 'broken')", name='ck_equipment_status'),
        sa.ForeignKeyConstraint(['line_id'], ['production_lines.id'], ),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_equipment_process', 'equipment', ['process_id'])
    op.create_index('idx_equipment_status', 'equipment', ['status'])
    op.create_index('idx_equipment_type', 'equipment', ['equipment_type'])
    op.create_index('uq_equipment_equipment_code', 'equipment', ['equipment_code'], unique=True)

    # Create lots table
    op.create_table('lots',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('lot_number', sa.String(length=50), nullable=False),
        sa.Column('product_model_id', sa.BigInteger(), nullable=False),
        sa.Column('target_quantity', sa.Integer(), nullable=False),
        sa.Column('completed_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defect_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='waiting'),
        sa.Column('production_line_id', sa.BigInteger(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.CheckConstraint("status IN ('waiting', 'in_progress', 'completed', 'cancelled')", name='ck_lots_status'),
        sa.CheckConstraint('completed_quantity >= 0', name='ck_lots_completed_quantity'),
        sa.CheckConstraint('defect_quantity >= 0', name='ck_lots_defect_quantity'),
        sa.CheckConstraint('target_quantity > 0 AND target_quantity <= 100', name='ck_lots_target_quantity'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['product_model_id'], ['product_models.id'], ),
        sa.ForeignKeyConstraint(['production_line_id'], ['production_lines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lots_completed_at', 'lots', ['completed_at'])
    op.create_index('idx_lots_created_at', 'lots', ['created_at'])
    op.create_index('idx_lots_product', 'lots', ['product_model_id'])
    op.create_index('idx_lots_started_at', 'lots', ['started_at'])
    op.create_index('idx_lots_status', 'lots', ['status'])
    op.create_index('uq_lots_lot_number', 'lots', ['lot_number'], unique=True)

    # Create wip_items table
    op.create_table('wip_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wip_id', sa.String(length=50), nullable=False),
        sa.Column('lot_id', sa.BigInteger(), nullable=False),
        sa.Column('current_process', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='waiting'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('process_data', sa.JSON(), nullable=True),
        sa.Column('quality_status', sa.String(length=20), nullable=True),
        sa.Column('defect_code', sa.String(length=50), nullable=True),
        sa.Column('defect_reason', sa.Text(), nullable=True),
        sa.Column('rework_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locked_by', sa.BigInteger(), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("quality_status IN ('pass', 'fail', 'rework', NULL)", name='ck_wip_items_quality_status'),
        sa.CheckConstraint("status IN ('waiting', 'in_process', 'completed', 'failed', 'rework')", name='ck_wip_items_status'),
        sa.CheckConstraint('current_process >= 1 AND current_process <= 6', name='ck_wip_items_process_range'),
        sa.CheckConstraint('rework_count >= 0', name='ck_wip_items_rework_count'),
        sa.ForeignKeyConstraint(['locked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_wip_items_completed', 'wip_items', ['completed_at'])
    op.create_index('idx_wip_items_current_process', 'wip_items', ['current_process'])
    op.create_index('idx_wip_items_lot', 'wip_items', ['lot_id'])
    op.create_index('idx_wip_items_quality', 'wip_items', ['quality_status'])
    op.create_index('idx_wip_items_started', 'wip_items', ['started_at'])
    op.create_index('idx_wip_items_status', 'wip_items', ['status'])
    op.create_index('uq_wip_items_wip_id', 'wip_items', ['wip_id'], unique=True)

    # Create serials table
    op.create_table('serials',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('serial_number', sa.String(length=50), nullable=False),
        sa.Column('wip_id', sa.BigInteger(), nullable=True),
        sa.Column('lot_id', sa.BigInteger(), nullable=False),
        sa.Column('current_process', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='waiting'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('process_data', sa.JSON(), nullable=True),
        sa.Column('quality_status', sa.String(length=20), nullable=True),
        sa.Column('defect_code', sa.String(length=50), nullable=True),
        sa.Column('defect_reason', sa.Text(), nullable=True),
        sa.Column('rework_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('locked_by', sa.BigInteger(), nullable=True),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("quality_status IN ('pass', 'fail', 'rework', NULL)", name='ck_serials_quality_status'),
        sa.CheckConstraint("status IN ('waiting', 'in_process', 'completed', 'failed', 'rework')", name='ck_serials_status'),
        sa.CheckConstraint('current_process >= 7 AND current_process <= 8', name='ck_serials_process_range'),
        sa.CheckConstraint('rework_count >= 0', name='ck_serials_rework_count'),
        sa.ForeignKeyConstraint(['locked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ),
        sa.ForeignKeyConstraint(['wip_id'], ['wip_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_serials_completed', 'serials', ['completed_at'])
    op.create_index('idx_serials_current_process', 'serials', ['current_process'])
    op.create_index('idx_serials_lot', 'serials', ['lot_id'])
    op.create_index('idx_serials_quality', 'serials', ['quality_status'])
    op.create_index('idx_serials_started', 'serials', ['started_at'])
    op.create_index('idx_serials_status', 'serials', ['status'])
    op.create_index('idx_serials_wip', 'serials', ['wip_id'])
    op.create_index('uq_serials_serial_number', 'serials', ['serial_number'], unique=True)

    # Create process_data table
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
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("(wip_id IS NOT NULL AND serial_id IS NULL) OR (wip_id IS NULL AND serial_id IS NOT NULL)", name='ck_process_data_wip_or_serial'),
        sa.CheckConstraint("data_level IN ('wip', 'serial')", name='ck_process_data_level'),
        sa.CheckConstraint("result IN ('pending', 'pass', 'fail', 'rework')", name='ck_process_data_result'),
        sa.CheckConstraint('process_time_seconds >= 0', name='ck_process_data_time'),
        sa.CheckConstraint('rework_count >= 0', name='ck_process_data_rework_count'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ),
        sa.ForeignKeyConstraint(['serial_id'], ['serials.id'], ),
        sa.ForeignKeyConstraint(['wip_id'], ['wip_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_process_data_completed', 'process_data', ['completed_at'])
    op.create_index('idx_process_data_level', 'process_data', ['data_level'])
    op.create_index('idx_process_data_operator', 'process_data', ['operator_id'])
    op.create_index('idx_process_data_process', 'process_data', ['process_id'])
    op.create_index('idx_process_data_result', 'process_data', ['result'])
    op.create_index('idx_process_data_serial', 'process_data', ['serial_id'])
    op.create_index('idx_process_data_started', 'process_data', ['started_at'])
    op.create_index('idx_process_data_wip', 'process_data', ['wip_id'])

    # Create wip_process_history table
    op.create_table('wip_process_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('wip_id', sa.BigInteger(), nullable=False),
        sa.Column('process_number', sa.Integer(), nullable=False),
        sa.Column('process_id', sa.BigInteger(), nullable=False),
        sa.Column('operator_id', sa.BigInteger(), nullable=False),
        sa.Column('equipment_id', sa.BigInteger(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('process_time_seconds', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(length=10), nullable=False, server_default='pending'),
        sa.Column('measurements', sa.JSON(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('quality_status', sa.String(length=10), nullable=True),
        sa.Column('defect_code', sa.String(length=50), nullable=True),
        sa.Column('defect_reason', sa.Text(), nullable=True),
        sa.Column('rework_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("quality_status IN ('pass', 'fail', 'rework', NULL)", name='ck_wip_process_history_quality'),
        sa.CheckConstraint("result IN ('pending', 'pass', 'fail', 'rework')", name='ck_wip_process_history_result'),
        sa.CheckConstraint('process_number >= 1 AND process_number <= 6', name='ck_wip_process_history_number'),
        sa.CheckConstraint('process_time_seconds >= 0', name='ck_wip_process_history_time'),
        sa.CheckConstraint('rework_count >= 0', name='ck_wip_process_history_rework'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ),
        sa.ForeignKeyConstraint(['wip_id'], ['wip_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_wip_process_history_completed', 'wip_process_history', ['completed_at'])
    op.create_index('idx_wip_process_history_operator', 'wip_process_history', ['operator_id'])
    op.create_index('idx_wip_process_history_process', 'wip_process_history', ['process_id', 'process_number'])
    op.create_index('idx_wip_process_history_result', 'wip_process_history', ['result'])
    op.create_index('idx_wip_process_history_started', 'wip_process_history', ['started_at'])
    op.create_index('idx_wip_process_history_wip', 'wip_process_history', ['wip_id', 'process_number', 'rework_count'])

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('table_name', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changed_fields', sa.Text(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('client_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("action IN ('INSERT', 'UPDATE', 'DELETE')", name='ck_audit_log_action'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_log_created', 'audit_log', ['created_at'])
    op.create_index('idx_audit_log_record', 'audit_log', ['table_name', 'record_id'])
    op.create_index('idx_audit_log_user', 'audit_log', ['user_id'])

    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('alert_type', sa.String(length=30), nullable=False),
        sa.Column('severity', sa.String(length=10), nullable=False, server_default='info'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('source_table', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='new'),
        sa.Column('acknowledged_by', sa.BigInteger(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.BigInteger(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("alert_type IN ('quality', 'equipment', 'process', 'system', 'maintenance')", name='ck_alerts_type'),
        sa.CheckConstraint("severity IN ('info', 'warning', 'error', 'critical')", name='ck_alerts_severity'),
        sa.CheckConstraint("status IN ('new', 'acknowledged', 'in_progress', 'resolved', 'closed')", name='ck_alerts_status'),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alerts_created', 'alerts', ['created_at'])
    op.create_index('idx_alerts_severity', 'alerts', ['severity'])
    op.create_index('idx_alerts_source', 'alerts', ['source_table', 'source_id'])
    op.create_index('idx_alerts_status', 'alerts', ['status'])
    op.create_index('idx_alerts_type', 'alerts', ['alert_type'])

    # Create error_log table
    op.create_table('error_log',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('error_level', sa.String(length=20), nullable=False, server_default='ERROR'),
        sa.Column('error_type', sa.String(length=100), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('source_module', sa.String(length=100), nullable=True),
        sa.Column('source_function', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('client_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_url', sa.Text(), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_payload', sa.JSON(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_by', sa.BigInteger(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("error_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')", name='ck_error_log_level'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_error_log_created', 'error_log', ['created_at'])
    op.create_index('idx_error_log_level', 'error_log', ['error_level'])
    op.create_index('idx_error_log_resolved', 'error_log', ['is_resolved'])
    op.create_index('idx_error_log_type', 'error_log', ['error_type'])
    op.create_index('idx_error_log_user', 'error_log', ['user_id'])

    # Create print_log table
    op.create_table('print_log',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('printer_name', sa.String(length=100), nullable=False),
        sa.Column('document_name', sa.String(length=200), nullable=False),
        sa.Column('label_type', sa.String(length=50), nullable=False),
        sa.Column('label_data', sa.JSON(), nullable=False),
        sa.Column('zpl_content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('printed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('wip_id', sa.String(length=50), nullable=True),
        sa.Column('serial_number', sa.String(length=50), nullable=True),
        sa.Column('lot_number', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("status IN ('pending', 'printing', 'completed', 'failed', 'cancelled')", name='ck_print_log_status'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_print_log_created', 'print_log', ['created_at'])
    op.create_index('idx_print_log_lot', 'print_log', ['lot_number'])
    op.create_index('idx_print_log_printed', 'print_log', ['printed_at'])
    op.create_index('idx_print_log_serial', 'print_log', ['serial_number'])
    op.create_index('idx_print_log_status', 'print_log', ['status'])
    op.create_index('idx_print_log_type', 'print_log', ['label_type'])
    op.create_index('idx_print_log_user', 'print_log', ['user_id'])
    op.create_index('idx_print_log_wip', 'print_log', ['wip_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('idx_print_log_wip', table_name='print_log')
    op.drop_index('idx_print_log_user', table_name='print_log')
    op.drop_index('idx_print_log_type', table_name='print_log')
    op.drop_index('idx_print_log_status', table_name='print_log')
    op.drop_index('idx_print_log_serial', table_name='print_log')
    op.drop_index('idx_print_log_printed', table_name='print_log')
    op.drop_index('idx_print_log_lot', table_name='print_log')
    op.drop_index('idx_print_log_created', table_name='print_log')
    op.drop_table('print_log')

    op.drop_index('idx_error_log_user', table_name='error_log')
    op.drop_index('idx_error_log_type', table_name='error_log')
    op.drop_index('idx_error_log_resolved', table_name='error_log')
    op.drop_index('idx_error_log_level', table_name='error_log')
    op.drop_index('idx_error_log_created', table_name='error_log')
    op.drop_table('error_log')

    op.drop_index('idx_alerts_type', table_name='alerts')
    op.drop_index('idx_alerts_status', table_name='alerts')
    op.drop_index('idx_alerts_source', table_name='alerts')
    op.drop_index('idx_alerts_severity', table_name='alerts')
    op.drop_index('idx_alerts_created', table_name='alerts')
    op.drop_table('alerts')

    op.drop_index('idx_audit_log_user', table_name='audit_log')
    op.drop_index('idx_audit_log_record', table_name='audit_log')
    op.drop_index('idx_audit_log_created', table_name='audit_log')
    op.drop_table('audit_log')

    op.drop_index('idx_wip_process_history_wip', table_name='wip_process_history')
    op.drop_index('idx_wip_process_history_started', table_name='wip_process_history')
    op.drop_index('idx_wip_process_history_result', table_name='wip_process_history')
    op.drop_index('idx_wip_process_history_process', table_name='wip_process_history')
    op.drop_index('idx_wip_process_history_operator', table_name='wip_process_history')
    op.drop_index('idx_wip_process_history_completed', table_name='wip_process_history')
    op.drop_table('wip_process_history')

    op.drop_index('idx_process_data_wip', table_name='process_data')
    op.drop_index('idx_process_data_started', table_name='process_data')
    op.drop_index('idx_process_data_serial', table_name='process_data')
    op.drop_index('idx_process_data_result', table_name='process_data')
    op.drop_index('idx_process_data_process', table_name='process_data')
    op.drop_index('idx_process_data_operator', table_name='process_data')
    op.drop_index('idx_process_data_level', table_name='process_data')
    op.drop_index('idx_process_data_completed', table_name='process_data')
    op.drop_table('process_data')

    op.drop_index('uq_serials_serial_number', table_name='serials')
    op.drop_index('idx_serials_wip', table_name='serials')
    op.drop_index('idx_serials_status', table_name='serials')
    op.drop_index('idx_serials_started', table_name='serials')
    op.drop_index('idx_serials_quality', table_name='serials')
    op.drop_index('idx_serials_lot', table_name='serials')
    op.drop_index('idx_serials_current_process', table_name='serials')
    op.drop_index('idx_serials_completed', table_name='serials')
    op.drop_table('serials')

    op.drop_index('uq_wip_items_wip_id', table_name='wip_items')
    op.drop_index('idx_wip_items_status', table_name='wip_items')
    op.drop_index('idx_wip_items_started', table_name='wip_items')
    op.drop_index('idx_wip_items_quality', table_name='wip_items')
    op.drop_index('idx_wip_items_lot', table_name='wip_items')
    op.drop_index('idx_wip_items_current_process', table_name='wip_items')
    op.drop_index('idx_wip_items_completed', table_name='wip_items')
    op.drop_table('wip_items')

    op.drop_index('uq_lots_lot_number', table_name='lots')
    op.drop_index('idx_lots_status', table_name='lots')
    op.drop_index('idx_lots_started_at', table_name='lots')
    op.drop_index('idx_lots_product', table_name='lots')
    op.drop_index('idx_lots_created_at', table_name='lots')
    op.drop_index('idx_lots_completed_at', table_name='lots')
    op.drop_table('lots')

    op.drop_index('uq_equipment_equipment_code', table_name='equipment')
    op.drop_index('idx_equipment_type', table_name='equipment')
    op.drop_index('idx_equipment_status', table_name='equipment')
    op.drop_index('idx_equipment_process', table_name='equipment')
    op.drop_table('equipment')

    op.drop_index('uq_processes_process_number', table_name='processes')
    op.drop_index('uq_processes_process_code', table_name='processes')
    op.drop_index('idx_processes_active', table_name='processes')
    op.drop_table('processes')

    op.drop_index('uq_production_lines_line_code', table_name='production_lines')
    op.drop_index('idx_production_lines_status', table_name='production_lines')
    op.drop_table('production_lines')

    op.drop_index('uq_product_models_product_code', table_name='product_models')
    op.drop_index('idx_product_models_type', table_name='product_models')
    op.drop_index('idx_product_models_active', table_name='product_models')
    op.drop_table('product_models')

    op.drop_index('uq_users_username', table_name='users')
    op.drop_index('uq_users_email', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_active', table_name='users')
    op.drop_table('users')