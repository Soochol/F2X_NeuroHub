"""fix_process_data_id_to_integer

Revision ID: 72b4ce422921
Revises: a1b2c3d4e5f6
Create Date: 2025-11-24 20:05:27.170493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72b4ce422921'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Change process_data.id from BIGINT to INTEGER for SQLite autoincrement."""
    # For SQLite, we need to recreate the table
    # This is because SQLite doesn't support ALTER COLUMN
    
    op.execute("""
        -- Create new table with INTEGER id
        CREATE TABLE process_data_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id BIGINT NOT NULL,
            wip_id BIGINT,
            serial_id BIGINT,
            process_id BIGINT NOT NULL,
            operator_id BIGINT NOT NULL,
            equipment_id BIGINT,
            data_level VARCHAR(10) NOT NULL,
            started_at DATETIME NOT NULL,
            completed_at DATETIME,
            process_time_seconds INTEGER,
            result VARCHAR(10) NOT NULL,
            measurements JSON,
            parameters JSON,
            defect_code VARCHAR(50),
            defect_reason TEXT,
            rework_count INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            defects JSON,
            duration_seconds INTEGER,
            FOREIGN KEY(lot_id) REFERENCES lots (id) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY(wip_id) REFERENCES wip_items (id),
            FOREIGN KEY(serial_id) REFERENCES serials (id),
            FOREIGN KEY(process_id) REFERENCES processes (id),
            FOREIGN KEY(operator_id) REFERENCES users (id),
            FOREIGN KEY(equipment_id) REFERENCES equipment (id)
        );
        
        -- Copy data from old table
        INSERT INTO process_data_new 
        SELECT * FROM process_data;
        
        -- Drop old table
        DROP TABLE process_data;
        
        -- Rename new table
        ALTER TABLE process_data_new RENAME TO process_data;
        
        -- Recreate indexes
        CREATE INDEX IF NOT EXISTS idx_process_data_lot ON process_data(lot_id);
        CREATE INDEX IF NOT EXISTS idx_process_data_serial ON process_data(serial_id) WHERE serial_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_process_data_process ON process_data(process_id);
        CREATE INDEX IF NOT EXISTS idx_process_data_wip ON process_data(wip_id) WHERE wip_id IS NOT NULL;
    """)


def downgrade() -> None:
    """Revert to BIGINT id - not recommended."""
    # Downgrade would require recreating with BIGINT
    # This is rarely needed and risky, so we'll pass
    pass