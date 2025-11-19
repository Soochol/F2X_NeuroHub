-- =============================================================================
-- Migration Script: Add Production Line and Equipment References
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Add production_line_id to lots table and equipment_id to process_data table
-- Dependencies:
--   - lots table (existing)
--   - process_data table (existing)
--   - production_lines table (must be created first)
--   - equipment table (must be created first)
-- =============================================================================

-- =============================================================================
-- PRE-MIGRATION CHECKS
-- =============================================================================
DO $$
BEGIN
    -- Check if production_lines table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'production_lines') THEN
        RAISE EXCEPTION 'Migration failed: production_lines table does not exist. Please create it first using 08_production_lines.sql';
    END IF;

    -- Check if equipment table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'equipment') THEN
        RAISE EXCEPTION 'Migration failed: equipment table does not exist. Please create it first using 09_equipment.sql';
    END IF;
END $$;

-- =============================================================================
-- ALTER TABLE: lots - Add production_line_id
-- =============================================================================

-- Add column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'lots' AND column_name = 'production_line_id'
    ) THEN
        ALTER TABLE lots
        ADD COLUMN production_line_id BIGINT;

        RAISE NOTICE 'Added production_line_id column to lots table';
    ELSE
        RAISE NOTICE 'Column production_line_id already exists in lots table';
    END IF;
END $$;

-- Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_lots_production_line' AND table_name = 'lots'
    ) THEN
        ALTER TABLE lots
        ADD CONSTRAINT fk_lots_production_line
        FOREIGN KEY (production_line_id)
        REFERENCES production_lines(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

        RAISE NOTICE 'Added foreign key constraint fk_lots_production_line';
    ELSE
        RAISE NOTICE 'Constraint fk_lots_production_line already exists';
    END IF;
END $$;

-- Add index for foreign key
CREATE INDEX IF NOT EXISTS idx_lots_production_line
ON lots(production_line_id)
WHERE production_line_id IS NOT NULL;

-- Add comment for the new column
COMMENT ON COLUMN lots.production_line_id IS 'Foreign key reference to production_lines table';

-- =============================================================================
-- ALTER TABLE: process_data - Add equipment_id
-- =============================================================================

-- Add column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'process_data' AND column_name = 'equipment_id'
    ) THEN
        ALTER TABLE process_data
        ADD COLUMN equipment_id BIGINT;

        RAISE NOTICE 'Added equipment_id column to process_data table';
    ELSE
        RAISE NOTICE 'Column equipment_id already exists in process_data table';
    END IF;
END $$;

-- Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_process_data_equipment' AND table_name = 'process_data'
    ) THEN
        ALTER TABLE process_data
        ADD CONSTRAINT fk_process_data_equipment
        FOREIGN KEY (equipment_id)
        REFERENCES equipment(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

        RAISE NOTICE 'Added foreign key constraint fk_process_data_equipment';
    ELSE
        RAISE NOTICE 'Constraint fk_process_data_equipment already exists';
    END IF;
END $$;

-- Add index for foreign key
CREATE INDEX IF NOT EXISTS idx_process_data_equipment
ON process_data(equipment_id)
WHERE equipment_id IS NOT NULL;

-- Add composite index for equipment utilization analysis
CREATE INDEX IF NOT EXISTS idx_process_data_equipment_utilization
ON process_data(equipment_id, process_id, result, started_at)
WHERE equipment_id IS NOT NULL;

-- Add comment for the new column
COMMENT ON COLUMN process_data.equipment_id IS 'Foreign key reference to equipment table (equipment used for this process execution)';

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

/*
-- Verify lots table changes
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'lots' AND column_name = 'production_line_id';

-- Verify process_data table changes
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'process_data' AND column_name = 'equipment_id';

-- Verify constraints
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid IN ('lots'::regclass, 'process_data'::regclass)
  AND conname IN ('fk_lots_production_line', 'fk_process_data_equipment')
ORDER BY conrelid, conname;

-- Verify indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('lots', 'process_data')
  AND indexname LIKE '%production_line%' OR indexname LIKE '%equipment%'
ORDER BY tablename, indexname;
*/

-- =============================================================================
-- SAMPLE UPDATE QUERIES (Optional - for testing)
-- =============================================================================

/*
-- Update existing lots with production line reference
UPDATE lots
SET production_line_id = (
    SELECT id FROM production_lines WHERE line_code = 'LINE_A' LIMIT 1
)
WHERE production_line_id IS NULL;

-- Update existing process_data with equipment reference
UPDATE process_data pd
SET equipment_id = (
    SELECT e.id FROM equipment e
    WHERE e.process_id = pd.process_id
    LIMIT 1
)
WHERE pd.equipment_id IS NULL;
*/

-- =============================================================================
-- ROLLBACK SCRIPT (Use with caution - for reverting changes)
-- =============================================================================

/*
-- To rollback this migration, run the following:

-- Remove indexes
DROP INDEX IF EXISTS idx_lots_production_line;
DROP INDEX IF EXISTS idx_process_data_equipment;
DROP INDEX IF EXISTS idx_process_data_equipment_utilization;

-- Remove foreign key constraints
ALTER TABLE lots DROP CONSTRAINT IF EXISTS fk_lots_production_line;
ALTER TABLE process_data DROP CONSTRAINT IF EXISTS fk_process_data_equipment;

-- Remove columns
ALTER TABLE lots DROP COLUMN IF EXISTS production_line_id;
ALTER TABLE process_data DROP COLUMN IF EXISTS equipment_id;
*/

-- =============================================================================
-- END OF MIGRATION SCRIPT
-- =============================================================================
