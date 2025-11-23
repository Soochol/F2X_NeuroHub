-- =============================================================================
-- Migration Script: Add WIP Tracking Integration
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Integrate WIP tracking system with existing process_data table
--          by adding wip_id foreign key column and associated indexes.
--
-- Changes:
--   1. Add wip_id column to process_data table (nullable)
--   2. Add foreign key constraint to wip_items table
--   3. Add indexes for WIP-based queries
--   4. Add check constraint for WIP/Serial data consistency
--   5. Update existing indexes for optimal WIP query performance
--
-- Rollback: See rollback section at bottom
--
-- Author: F2X Database Team
-- Date: 2025-11-21
-- =============================================================================

-- =============================================================================
-- PHASE 1: Add wip_id column to process_data
-- =============================================================================

DO $$
BEGIN
    -- Check if column already exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'process_data'
          AND column_name = 'wip_id'
    ) THEN
        -- Add wip_id column (nullable for backward compatibility)
        ALTER TABLE process_data
        ADD COLUMN wip_id BIGINT;

        RAISE NOTICE 'Added wip_id column to process_data table';
    ELSE
        RAISE NOTICE 'Column wip_id already exists in process_data table';
    END IF;
END $$;

-- Add column comment
COMMENT ON COLUMN process_data.wip_id IS
'Foreign key to wip_items table. Used for WIP-level process tracking (processes 1-6).
NULL for serial-level tracking (processes 7-8) or pre-WIP data.';

-- =============================================================================
-- PHASE 2: Add foreign key constraint
-- =============================================================================

DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_process_data_wip'
          AND table_name = 'process_data'
    ) THEN
        -- Add foreign key constraint
        ALTER TABLE process_data
        ADD CONSTRAINT fk_process_data_wip
        FOREIGN KEY (wip_id)
        REFERENCES wip_items(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE;

        RAISE NOTICE 'Added foreign key constraint fk_process_data_wip';
    ELSE
        RAISE NOTICE 'Foreign key constraint fk_process_data_wip already exists';
    END IF;
END $$;

-- =============================================================================
-- PHASE 3: Add check constraint for WIP/Serial data consistency
-- =============================================================================

DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'chk_process_data_wip_serial_consistency'
          AND table_name = 'process_data'
    ) THEN
        -- Add check constraint
        -- Business rule: Either wip_id OR serial_id must be set (or both during transition)
        ALTER TABLE process_data
        ADD CONSTRAINT chk_process_data_wip_serial_consistency
        CHECK (wip_id IS NOT NULL OR serial_id IS NOT NULL);

        RAISE NOTICE 'Added check constraint chk_process_data_wip_serial_consistency';
    ELSE
        RAISE NOTICE 'Check constraint chk_process_data_wip_serial_consistency already exists';
    END IF;
END $$;

-- =============================================================================
-- PHASE 4: Add indexes for WIP-based queries
-- =============================================================================

-- Index for WIP-based lookups
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_process_data_wip'
    ) THEN
        CREATE INDEX idx_process_data_wip
        ON process_data(wip_id)
        WHERE wip_id IS NOT NULL;

        RAISE NOTICE 'Created index idx_process_data_wip';
    ELSE
        RAISE NOTICE 'Index idx_process_data_wip already exists';
    END IF;
END $$;

-- Composite index for WIP process traceability
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_process_data_wip_process'
    ) THEN
        CREATE INDEX idx_process_data_wip_process
        ON process_data(wip_id, process_id, started_at DESC)
        WHERE wip_id IS NOT NULL;

        RAISE NOTICE 'Created index idx_process_data_wip_process';
    ELSE
        RAISE NOTICE 'Index idx_process_data_wip_process already exists';
    END IF;
END $$;

-- Index for WIP result filtering
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_process_data_wip_result'
    ) THEN
        CREATE INDEX idx_process_data_wip_result
        ON process_data(wip_id, result, started_at DESC)
        WHERE wip_id IS NOT NULL;

        RAISE NOTICE 'Created index idx_process_data_wip_result';
    ELSE
        RAISE NOTICE 'Index idx_process_data_wip_result already exists';
    END IF;
END $$;

-- =============================================================================
-- PHASE 5: Update existing lots table indexes for WIP queries
-- =============================================================================

-- Add composite index for active LOT filtering with WIP support
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_lots_status_production_date_id'
    ) THEN
        CREATE INDEX idx_lots_status_production_date_id
        ON lots(status, production_date, id)
        WHERE status IN ('CREATED', 'IN_PROGRESS');

        RAISE NOTICE 'Created index idx_lots_status_production_date_id on lots table';
    ELSE
        RAISE NOTICE 'Index idx_lots_status_production_date_id already exists';
    END IF;
END $$;

-- =============================================================================
-- PHASE 6: Add indexes to serials table for WIP transition tracking
-- =============================================================================

-- Add index for serial creation timestamp (WIP transition tracking)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = 'idx_serials_created_at'
    ) THEN
        CREATE INDEX idx_serials_created_at
        ON serials(created_at DESC, lot_id);

        RAISE NOTICE 'Created index idx_serials_created_at on serials table';
    ELSE
        RAISE NOTICE 'Index idx_serials_created_at already exists';
    END IF;
END $$;

-- =============================================================================
-- PHASE 7: Create helper function for WIP → Serial data migration
-- =============================================================================

CREATE OR REPLACE FUNCTION migrate_wip_to_serial_process_data(
    p_wip_id BIGINT,
    p_serial_id BIGINT
)
RETURNS INTEGER AS $$
DECLARE
    v_updated_count INTEGER;
BEGIN
    -- Update process_data records from WIP to Serial tracking
    -- Used when WIP transitions to Serial at process 7
    UPDATE process_data
    SET
        serial_id = p_serial_id,
        data_level = 'SERIAL',
        updated_at = NOW()
    WHERE wip_id = p_wip_id
      AND serial_id IS NULL;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;

    RAISE NOTICE 'Migrated % process_data records from WIP % to Serial %',
        v_updated_count, p_wip_id, p_serial_id;

    RETURN v_updated_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION migrate_wip_to_serial_process_data(BIGINT, BIGINT) IS
'Migrates process_data records from WIP-level to Serial-level tracking.
Called when WIP item transitions to Serial at process 7 (Label Printing).
Returns the number of records updated.';

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify column addition
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'process_data'
  AND column_name = 'wip_id';

-- Verify constraints
SELECT
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'process_data'
  AND constraint_name LIKE '%wip%'
ORDER BY constraint_name;

-- Verify indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'process_data'
  AND indexname LIKE '%wip%'
ORDER BY indexname;

-- =============================================================================
-- ROLLBACK SCRIPT (Use only if migration needs to be reverted)
-- =============================================================================

/*
-- WARNING: This will remove WIP tracking from process_data
-- Only run this if you need to completely rollback the WIP integration

BEGIN;

-- Drop indexes
DROP INDEX IF EXISTS idx_process_data_wip CASCADE;
DROP INDEX IF EXISTS idx_process_data_wip_process CASCADE;
DROP INDEX IF EXISTS idx_process_data_wip_result CASCADE;
DROP INDEX IF EXISTS idx_lots_status_production_date_id CASCADE;
DROP INDEX IF EXISTS idx_serials_created_at CASCADE;

-- Drop function
DROP FUNCTION IF EXISTS migrate_wip_to_serial_process_data(BIGINT, BIGINT) CASCADE;

-- Drop constraints
ALTER TABLE process_data DROP CONSTRAINT IF EXISTS chk_process_data_wip_serial_consistency CASCADE;
ALTER TABLE process_data DROP CONSTRAINT IF EXISTS fk_process_data_wip CASCADE;

-- Drop column
ALTER TABLE process_data DROP COLUMN IF EXISTS wip_id CASCADE;

COMMIT;

-- Verify rollback
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'process_data'
  AND column_name = 'wip_id';
-- Should return 0 rows if rollback successful
*/

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Summary report
DO $$
BEGIN
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'WIP Tracking Integration Migration Complete';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Changes Applied:';
    RAISE NOTICE '  1. Added wip_id column to process_data';
    RAISE NOTICE '  2. Added foreign key constraint to wip_items';
    RAISE NOTICE '  3. Added check constraint for WIP/Serial consistency';
    RAISE NOTICE '  4. Created 3 new indexes on process_data for WIP queries';
    RAISE NOTICE '  5. Created 2 new indexes on lots and serials for WIP support';
    RAISE NOTICE '  6. Created migrate_wip_to_serial_process_data() helper function';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Deploy wip_items table (11_wip_items.sql)';
    RAISE NOTICE '  2. Deploy wip_process_history table (12_wip_process_history.sql)';
    RAISE NOTICE '  3. Deploy WIP views (see views/wip_views/ directory)';
    RAISE NOTICE '  4. Update application code to use WIP tracking';
    RAISE NOTICE '=============================================================================';
END $$;

-- =============================================================================
-- END OF MIGRATION SCRIPT
-- =============================================================================
