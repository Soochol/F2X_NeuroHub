-- Drop and recreate the chk_process_data_wip_serial_consistency constraint
-- This allows WIP items to have serial_id (previously required serial_id IS NULL for WIP)

ALTER TABLE process_data 
DROP CONSTRAINT IF EXISTS chk_process_data_wip_serial_consistency;

ALTER TABLE process_data 
ADD CONSTRAINT chk_process_data_wip_serial_consistency 
CHECK (
    (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR 
    (data_level = 'WIP' AND wip_id IS NOT NULL) OR 
    (data_level = 'SERIAL' AND serial_id IS NOT NULL)
);
