-- =============================================================================
-- DDL Script: equipment (설비)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Master data table defining equipment/machines used in production processes
-- Dependencies:
--   - processes (foreign key)
--   - production_lines (foreign key)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS equipment CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE equipment (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Core columns
    equipment_code VARCHAR(50) NOT NULL,          -- Unique equipment code (e.g., EQ_LASER_001)
    equipment_name_ko VARCHAR(255) NOT NULL,      -- Equipment name in Korean
    equipment_name_en VARCHAR(255) NOT NULL,      -- Equipment name in English
    equipment_type VARCHAR(100) NOT NULL,         -- Equipment type/category
    description TEXT,                             -- Equipment description and details
    manufacturer VARCHAR(255),                    -- Equipment manufacturer
    model_number VARCHAR(100),                    -- Manufacturer model number
    serial_number VARCHAR(100),                   -- Equipment serial number

    -- Foreign keys
    process_id BIGINT,                            -- Reference to processes table (primary process)
    production_line_id BIGINT,                    -- Reference to production_lines table

    -- Status and availability
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',  -- Equipment status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,          -- Whether equipment is in service

    -- Utilization tracking
    last_maintenance_date DATE,                   -- Last maintenance date
    next_maintenance_date DATE,                   -- Scheduled next maintenance date
    total_operation_hours NUMERIC(10, 2) DEFAULT 0,  -- Total hours of operation

    -- Configuration
    specifications JSONB DEFAULT '{}',            -- Technical specifications
    maintenance_schedule JSONB DEFAULT '{}',      -- Maintenance schedule and procedures

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE equipment
ADD CONSTRAINT pk_equipment PRIMARY KEY (id);

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
ALTER TABLE equipment
ADD CONSTRAINT uk_equipment_equipment_code UNIQUE (equipment_code);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================
-- Foreign key to processes table
ALTER TABLE equipment
ADD CONSTRAINT fk_equipment_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Foreign key to production_lines table
ALTER TABLE equipment
ADD CONSTRAINT fk_equipment_production_line
FOREIGN KEY (production_line_id)
REFERENCES production_lines(id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Status must be valid value
ALTER TABLE equipment
ADD CONSTRAINT chk_equipment_status
CHECK (status IN ('AVAILABLE', 'IN_USE', 'MAINTENANCE', 'OUT_OF_SERVICE', 'RETIRED'));

-- Total operation hours must be non-negative
ALTER TABLE equipment
ADD CONSTRAINT chk_equipment_operation_hours
CHECK (total_operation_hours >= 0);

-- Next maintenance date must be after last maintenance date
ALTER TABLE equipment
ADD CONSTRAINT chk_equipment_maintenance_dates
CHECK (next_maintenance_date IS NULL OR last_maintenance_date IS NULL OR next_maintenance_date > last_maintenance_date);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Foreign key indexes
CREATE INDEX idx_equipment_process
ON equipment(process_id)
WHERE process_id IS NOT NULL;

CREATE INDEX idx_equipment_production_line
ON equipment(production_line_id)
WHERE production_line_id IS NOT NULL;

-- Status-based queries
CREATE INDEX idx_equipment_status
ON equipment(status);

-- Active equipment index
CREATE INDEX idx_equipment_active
ON equipment(is_active, status)
WHERE is_active = TRUE;

-- Equipment type queries
CREATE INDEX idx_equipment_type
ON equipment(equipment_type);

-- Composite index for utilization analysis
CREATE INDEX idx_equipment_utilization
ON equipment(production_line_id, process_id, status, total_operation_hours)
WHERE is_active = TRUE;

-- Maintenance scheduling queries
CREATE INDEX idx_equipment_maintenance_schedule
ON equipment(next_maintenance_date)
WHERE next_maintenance_date IS NOT NULL AND is_active = TRUE;

-- GIN indexes for JSONB columns
CREATE INDEX idx_equipment_specifications
ON equipment USING gin(specifications);

CREATE INDEX idx_equipment_maintenance_schedule_json
ON equipment USING gin(maintenance_schedule);

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_equipment_updated_at
BEFORE UPDATE ON equipment
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_equipment_audit
AFTER INSERT OR UPDATE OR DELETE ON equipment
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE equipment IS 'Master data table defining equipment and machines used in production processes';
COMMENT ON COLUMN equipment.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN equipment.equipment_code IS 'Unique equipment code (e.g., EQ_LASER_001)';
COMMENT ON COLUMN equipment.equipment_name_ko IS 'Equipment name in Korean';
COMMENT ON COLUMN equipment.equipment_name_en IS 'Equipment name in English';
COMMENT ON COLUMN equipment.equipment_type IS 'Equipment type/category';
COMMENT ON COLUMN equipment.description IS 'Equipment description and details';
COMMENT ON COLUMN equipment.manufacturer IS 'Equipment manufacturer';
COMMENT ON COLUMN equipment.model_number IS 'Manufacturer model number';
COMMENT ON COLUMN equipment.serial_number IS 'Equipment serial number';
COMMENT ON COLUMN equipment.process_id IS 'Foreign key to processes table (primary process this equipment handles)';
COMMENT ON COLUMN equipment.production_line_id IS 'Foreign key to production_lines table';
COMMENT ON COLUMN equipment.status IS 'Equipment status: AVAILABLE, IN_USE, MAINTENANCE, OUT_OF_SERVICE, RETIRED';
COMMENT ON COLUMN equipment.is_active IS 'Whether equipment is in service';
COMMENT ON COLUMN equipment.last_maintenance_date IS 'Last maintenance date';
COMMENT ON COLUMN equipment.next_maintenance_date IS 'Scheduled next maintenance date';
COMMENT ON COLUMN equipment.total_operation_hours IS 'Total hours of operation';
COMMENT ON COLUMN equipment.specifications IS 'Technical specifications in JSONB format';
COMMENT ON COLUMN equipment.maintenance_schedule IS 'Maintenance schedule and procedures in JSONB format';
COMMENT ON COLUMN equipment.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN equipment.updated_at IS 'Last update timestamp';

-- =============================================================================
-- INITIAL DATA (OPTIONAL)
-- =============================================================================
/*
INSERT INTO equipment (equipment_code, equipment_name_ko, equipment_name_en, equipment_type, description, manufacturer, model_number, process_id, production_line_id, status, sort_order) VALUES
-- Laser Marking Equipment
('EQ_LASER_001', '레이저 마킹기 001', 'Laser Marker 001', 'LASER_MARKER', 'High precision fiber laser marker', 'Keyence', 'MD-X2500', 1, 1, 'AVAILABLE'),
('EQ_LASER_002', '레이저 마킹기 002', 'Laser Marker 002', 'LASER_MARKER', 'High precision fiber laser marker', 'Keyence', 'MD-X2500', 1, 2, 'AVAILABLE'),

-- Assembly Equipment
('EQ_ASSEM_001', '조립 장비 001', 'Assembly Station 001', 'ASSEMBLY_STATION', 'LMA assembly workstation', 'Custom', 'AS-100', 2, 1, 'AVAILABLE'),
('EQ_ASSEM_002', '조립 장비 002', 'Assembly Station 002', 'ASSEMBLY_STATION', 'LMA assembly workstation', 'Custom', 'AS-100', 2, 2, 'AVAILABLE'),

-- Inspection Equipment
('EQ_INSP_001', '검사 장비 001', 'Inspection Station 001', 'INSPECTION_STATION', 'Sensor inspection equipment', 'National Instruments', 'PXI-4461', 3, 1, 'AVAILABLE');
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================
