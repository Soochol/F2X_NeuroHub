-- =============================================================================
-- Migration: Consolidate equipment_name_ko and equipment_name_en to equipment_name
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Simplify equipment table by merging name columns into single field
-- Date: 2024-11-20
-- =============================================================================

-- Step 1: Add new equipment_name column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'equipment' AND column_name = 'equipment_name'
    ) THEN
        ALTER TABLE equipment ADD COLUMN equipment_name VARCHAR(255);
    END IF;
END $$;

-- Step 2: Migrate data from equipment_name_ko to equipment_name (if old columns exist)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'equipment' AND column_name = 'equipment_name_ko'
    ) THEN
        UPDATE equipment SET equipment_name = equipment_name_ko WHERE equipment_name IS NULL;
    END IF;
END $$;

-- Step 3: Set NOT NULL constraint on equipment_name
ALTER TABLE equipment ALTER COLUMN equipment_name SET NOT NULL;

-- Step 4: Drop old columns if they exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'equipment' AND column_name = 'equipment_name_ko'
    ) THEN
        ALTER TABLE equipment DROP COLUMN equipment_name_ko;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'equipment' AND column_name = 'equipment_name_en'
    ) THEN
        ALTER TABLE equipment DROP COLUMN equipment_name_en;
    END IF;
END $$;

-- Step 5: Add comment
COMMENT ON COLUMN equipment.equipment_name IS 'Equipment name';

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
