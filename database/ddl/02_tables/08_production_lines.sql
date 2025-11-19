-- =============================================================================
-- DDL Script: production_lines (생산 라인)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Master data table defining production lines in the manufacturing facility
-- Dependencies: None (independent table)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS production_lines CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE production_lines (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Core columns
    line_code VARCHAR(50) NOT NULL,               -- Unique production line code (e.g., LINE_A, LINE_B)
    line_name_ko VARCHAR(255) NOT NULL,           -- Production line name in Korean
    line_name_en VARCHAR(255) NOT NULL,           -- Production line name in English
    description TEXT,                             -- Production line description and details
    location VARCHAR(255),                        -- Physical location in the facility
    capacity_per_shift INTEGER,                   -- Maximum production capacity per shift
    is_active BOOLEAN NOT NULL DEFAULT TRUE,      -- Whether production line is currently operational
    sort_order INTEGER NOT NULL DEFAULT 1,        -- Display order for UI

    -- Configuration
    config JSONB DEFAULT '{}',                    -- Line-specific configuration settings

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE production_lines
ADD CONSTRAINT pk_production_lines PRIMARY KEY (id);

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
ALTER TABLE production_lines
ADD CONSTRAINT uk_production_lines_line_code UNIQUE (line_code);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Capacity must be positive if specified
ALTER TABLE production_lines
ADD CONSTRAINT chk_production_lines_capacity
CHECK (capacity_per_shift IS NULL OR capacity_per_shift > 0);

-- Sort order must be positive
ALTER TABLE production_lines
ADD CONSTRAINT chk_production_lines_sort_order
CHECK (sort_order > 0);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Active production lines index
CREATE INDEX idx_production_lines_active
ON production_lines(is_active, sort_order)
WHERE is_active = TRUE;

-- Sort order for UI display
CREATE INDEX idx_production_lines_sort_order
ON production_lines(sort_order);

-- Location-based queries
CREATE INDEX idx_production_lines_location
ON production_lines(location)
WHERE location IS NOT NULL;

-- GIN index for JSONB config
CREATE INDEX idx_production_lines_config
ON production_lines USING gin(config);

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_production_lines_updated_at
BEFORE UPDATE ON production_lines
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_production_lines_audit
AFTER INSERT OR UPDATE OR DELETE ON production_lines
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE production_lines IS 'Master data table defining production lines in the F2X manufacturing facility';
COMMENT ON COLUMN production_lines.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN production_lines.line_code IS 'Unique production line code (e.g., LINE_A, LINE_B)';
COMMENT ON COLUMN production_lines.line_name_ko IS 'Production line name in Korean';
COMMENT ON COLUMN production_lines.line_name_en IS 'Production line name in English';
COMMENT ON COLUMN production_lines.description IS 'Production line description and details';
COMMENT ON COLUMN production_lines.location IS 'Physical location in the facility';
COMMENT ON COLUMN production_lines.capacity_per_shift IS 'Maximum production capacity per shift';
COMMENT ON COLUMN production_lines.is_active IS 'Whether production line is currently operational';
COMMENT ON COLUMN production_lines.sort_order IS 'Display order for UI';
COMMENT ON COLUMN production_lines.config IS 'Line-specific configuration settings in JSONB format';
COMMENT ON COLUMN production_lines.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN production_lines.updated_at IS 'Last update timestamp';

-- =============================================================================
-- INITIAL DATA (OPTIONAL)
-- =============================================================================
/*
INSERT INTO production_lines (line_code, line_name_ko, line_name_en, description, location, capacity_per_shift, sort_order) VALUES
('LINE_A', 'A 라인', 'Line A', 'Primary production line for standard products', 'Building A, Floor 1', 100, 1),
('LINE_B', 'B 라인', 'Line B', 'Secondary production line for high-volume products', 'Building A, Floor 2', 150, 2),
('LINE_C', 'C 라인', 'Line C', 'Specialized production line for custom products', 'Building B, Floor 1', 50, 3);
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================
