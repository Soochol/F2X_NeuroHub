-- =============================================================================
-- DDL Script: product_models (제품 모델)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Master data table containing product model definitions and specifications
-- Dependencies: None (independent table)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS product_models CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE product_models (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Core columns
    model_code VARCHAR(50) NOT NULL,  -- Unique model identifier (e.g., NH-F2X-001)
    model_name VARCHAR(255) NOT NULL,  -- Product name (Korean/English)
    category VARCHAR(100),            -- Product category or family
    production_cycle_days INTEGER,    -- Expected production cycle duration in days
    specifications JSONB DEFAULT '{}', -- Technical specifications in JSON format
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- Product lifecycle status

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE product_models
ADD CONSTRAINT pk_product_models PRIMARY KEY (id);

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
ALTER TABLE product_models
ADD CONSTRAINT uk_product_models_model_code UNIQUE (model_code);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Status must be one of the allowed values
ALTER TABLE product_models
ADD CONSTRAINT chk_product_models_status
CHECK (status IN ('ACTIVE', 'INACTIVE', 'DISCONTINUED'));

-- Production cycle days must be positive if specified
ALTER TABLE product_models
ADD CONSTRAINT chk_product_models_cycle_days
CHECK (production_cycle_days IS NULL OR production_cycle_days > 0);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Status filter index (for active products query)
CREATE INDEX idx_product_models_status
ON product_models(status)
WHERE status = 'ACTIVE';

-- Full-text search index on model name
CREATE INDEX idx_product_models_name_search
ON product_models USING gin(to_tsvector('simple', model_name));

-- GIN index for JSONB specifications
CREATE INDEX idx_product_models_specifications
ON product_models USING gin(specifications);

-- Category classification index
CREATE INDEX idx_product_models_category
ON product_models(category)
WHERE category IS NOT NULL;

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_product_models_updated_at
BEFORE UPDATE ON product_models
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_product_models_audit
AFTER INSERT OR UPDATE OR DELETE ON product_models
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE product_models IS 'Master data table containing product model definitions and specifications';
COMMENT ON COLUMN product_models.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN product_models.model_code IS 'Unique model identifier (e.g., NH-F2X-001)';
COMMENT ON COLUMN product_models.model_name IS 'Product name (Korean/English)';
COMMENT ON COLUMN product_models.category IS 'Product category or family';
COMMENT ON COLUMN product_models.production_cycle_days IS 'Expected production cycle duration in days';
COMMENT ON COLUMN product_models.specifications IS 'Technical specifications in JSON format';
COMMENT ON COLUMN product_models.status IS 'Product lifecycle status: ACTIVE, INACTIVE, DISCONTINUED';
COMMENT ON COLUMN product_models.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN product_models.updated_at IS 'Last update timestamp';

-- =============================================================================
-- INITIAL DATA (Optional)
-- =============================================================================
-- Example product models for F2X series
/*
INSERT INTO product_models (model_code, model_name, category, production_cycle_days, specifications, status) VALUES
('NH-F2X-001', 'NeuroHub F2X Standard', 'Standard', 5,
 '{
    "dimensions": {"width_mm": 100, "height_mm": 50, "depth_mm": 30},
    "weight_grams": 250,
    "electrical": {"voltage_range": "3.3V-5V", "current_max_ma": 500},
    "operating_temp": {"min_celsius": -10, "max_celsius": 60},
    "quality_standards": ["ISO 9001", "CE"]
  }', 'ACTIVE'),
('NH-F2X-002', 'NeuroHub F2X Pro', 'Professional', 7,
 '{
    "dimensions": {"width_mm": 120, "height_mm": 60, "depth_mm": 35},
    "weight_grams": 350,
    "electrical": {"voltage_range": "3.3V-5V", "current_max_ma": 750},
    "operating_temp": {"min_celsius": -20, "max_celsius": 70},
    "quality_standards": ["ISO 9001", "CE", "FDA"]
  }', 'ACTIVE');
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================