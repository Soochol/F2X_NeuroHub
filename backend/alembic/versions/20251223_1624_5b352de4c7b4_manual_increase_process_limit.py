"""manual_increase_process_limit

Revision ID: 5b352de4c7b4
Revises: e2f4a1b2c3d4
Create Date: 2025-12-23 16:24:13.745057

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5b352de4c7b4'
down_revision = 'e2f4a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Increase process number limit to 100 for all related tables."""
    # 1. Update processes table
    op.execute("""
        DO $$
        BEGIN
            -- Drop existing constraints if they exist
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_processes_process_number') THEN
                ALTER TABLE processes DROP CONSTRAINT chk_processes_process_number;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_processes_number_range') THEN
                ALTER TABLE processes DROP CONSTRAINT ck_processes_number_range;
            END IF;
            -- Create new constraint with increased limit
            ALTER TABLE processes ADD CONSTRAINT ck_processes_number_range CHECK (process_number >= 1 AND process_number <= 100);
        END $$;
    """)

    # 2. Update wip_items table (check if column exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'wip_items' AND column_name = 'current_process') THEN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_wip_items_process_range') THEN
                    ALTER TABLE wip_items DROP CONSTRAINT ck_wip_items_process_range;
                END IF;
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_wip_items_process_range') THEN
                    ALTER TABLE wip_items DROP CONSTRAINT chk_wip_items_process_range;
                END IF;
                ALTER TABLE wip_items ADD CONSTRAINT ck_wip_items_process_range CHECK (current_process >= 1 AND current_process <= 100);
            END IF;
        END $$;
    """)

    # 3. Update serials table (check if column exists)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'serials' AND column_name = 'current_process') THEN
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_serials_process_range') THEN
                    ALTER TABLE serials DROP CONSTRAINT ck_serials_process_range;
                END IF;
                IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_serials_process_range') THEN
                    ALTER TABLE serials DROP CONSTRAINT chk_serials_process_range;
                END IF;
                ALTER TABLE serials ADD CONSTRAINT ck_serials_process_range CHECK (current_process >= 1 AND current_process <= 100);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Revert process number limits."""
    # 1. processes
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_processes_number_range') THEN
                ALTER TABLE processes DROP CONSTRAINT ck_processes_number_range;
            END IF;
            ALTER TABLE processes ADD CONSTRAINT ck_processes_number_range CHECK (process_number >= 1 AND process_number <= 8);
        END $$;
    """)

    # 2. wip_items
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'wip_items' AND column_name = 'current_process') THEN
                ALTER TABLE wip_items DROP CONSTRAINT IF EXISTS ck_wip_items_process_range;
                ALTER TABLE wip_items ADD CONSTRAINT ck_wip_items_process_range CHECK (current_process >= 1 AND current_process <= 6);
            END IF;
        END $$;
    """)

    # 3. serials
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'serials' AND column_name = 'current_process') THEN
                ALTER TABLE serials DROP CONSTRAINT IF EXISTS ck_serials_process_range;
                ALTER TABLE serials ADD CONSTRAINT ck_serials_process_range CHECK (current_process >= 7 AND current_process <= 8);
            END IF;
        END $$;
    """)
