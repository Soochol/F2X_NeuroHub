-- Migration: Add equipment_id to process_data table
-- Description: Enable equipment tracking for process execution records
-- Date: 2025-11-20

-- Add equipment_id column to process_data table
ALTER TABLE process_data
ADD COLUMN IF NOT EXISTS equipment_id BIGINT NULL;

-- Add foreign key constraint
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_equipment
FOREIGN KEY (equipment_id)
REFERENCES equipment(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Create index for equipment_id
CREATE INDEX IF NOT EXISTS idx_process_data_equipment
ON process_data(equipment_id);

-- Create composite index for equipment utilization analysis
CREATE INDEX IF NOT EXISTS idx_process_data_equipment_utilization
ON process_data(equipment_id, process_id, started_at);

-- Add comment to column
COMMENT ON COLUMN process_data.equipment_id IS 'FK to equipment table - tracks which equipment was used for this process execution';

-- Verification query
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'process_data' AND column_name = 'equipment_id';
