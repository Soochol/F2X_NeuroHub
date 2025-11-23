-- Migration: Add WIP data level support to ProcessData
-- Date: 2025-11-23
-- Description: Update process_data table to support WIP-level data tracking

BEGIN;

-- 1. Drop old constraints
ALTER TABLE process_data DROP CONSTRAINT IF EXISTS chk_process_data_data_level;
ALTER TABLE process_data DROP CONSTRAINT IF EXISTS chk_process_data_serial_id;

-- 2. Add new constraints with WIP support
ALTER TABLE process_data ADD CONSTRAINT chk_process_data_data_level
    CHECK (data_level IN ('LOT', 'WIP', 'SERIAL'));

ALTER TABLE process_data ADD CONSTRAINT chk_process_data_wip_serial_consistency
    CHECK (
        (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR
        (data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR
        (data_level = 'SERIAL' AND serial_id IS NOT NULL)
    );

COMMIT;
