-- =====================================================
-- Serial Number Format V2 Migration
-- =====================================================
-- Changes:
--   - Serial format: KR01PSA2511001 (14 chars)
--   - LOT format: KR01PSA2511 (11 chars)
--   - Production date → Production month (YYMM)
--   - Remove shift indicator from serial number
--   - Line number: 2 digits (KR001 → 01)
-- =====================================================

-- =====================================================
-- 1. Create Model Code Mapping Table
-- =====================================================

CREATE TABLE IF NOT EXISTS model_code_mapping (
    id SERIAL PRIMARY KEY,
    model_code VARCHAR(20) NOT NULL,      -- Full code: PSA10, WF
    short_code CHAR(3) NOT NULL,          -- Abbreviated: PSA, WFO
    description VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_code),
    UNIQUE(short_code)
);

COMMENT ON TABLE model_code_mapping IS 'Model code to 3-character abbreviation mapping';
COMMENT ON COLUMN model_code_mapping.model_code IS 'Full model code (e.g., PSA10, Withforce)';
COMMENT ON COLUMN model_code_mapping.short_code IS '3-character model abbreviation (e.g., PSA, WFO)';

-- Insert initial mappings
INSERT INTO model_code_mapping (model_code, short_code, description)
VALUES
    ('PSA10', 'PSA', 'PSA10 모델'),
    ('Withforce', 'WFO', 'Withforce 모델')
ON CONFLICT (model_code) DO NOTHING;

-- =====================================================
-- 2. Update Serials Table Schema
-- =====================================================

-- Add format_version column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'serials' AND column_name = 'format_version'
    ) THEN
        ALTER TABLE serials ADD COLUMN format_version SMALLINT DEFAULT 1;
        COMMENT ON COLUMN serials.format_version IS 'Serial format version (1=old 24-char, 2=new 14-char)';
    END IF;
END $$;

-- Update existing serials to version 1
UPDATE serials SET format_version = 1 WHERE format_version IS NULL;

-- Ensure serial_number column can handle both formats
ALTER TABLE serials ALTER COLUMN serial_number TYPE VARCHAR(30);

-- =====================================================
-- 3. Update Lots Table Schema
-- =====================================================

-- Ensure lot_number column can handle both formats
ALTER TABLE lots ALTER COLUMN lot_number TYPE VARCHAR(30);

-- =====================================================
-- 4. Create V2 Serial Number Generation Function
-- =====================================================

CREATE OR REPLACE FUNCTION generate_serial_number_v2()
RETURNS TRIGGER AS $$
DECLARE
    v_line_code VARCHAR(4);
    v_model_short VARCHAR(3);
    v_month_part VARCHAR(4);
    v_sequence VARCHAR(3);
    v_lot_number VARCHAR(30);
BEGIN
    -- Get LOT number
    SELECT lot_number INTO v_lot_number
    FROM lots
    WHERE id = NEW.lot_id;

    IF v_lot_number IS NULL THEN
        RAISE EXCEPTION 'LOT not found for lot_id: %', NEW.lot_id;
    END IF;

    -- Extract line code from production line
    -- KR001 → KR01, KR002 → KR02, KR010 → KR10
    SELECT CONCAT(
        SUBSTRING(pl.line_code, 1, 2),
        LPAD(SUBSTRING(pl.line_code, 3)::INTEGER::TEXT, 2, '0')
    )
    INTO v_line_code
    FROM lots l
    JOIN production_lines pl ON l.production_line_id = pl.id
    WHERE l.id = NEW.lot_id;

    IF v_line_code IS NULL THEN
        RAISE EXCEPTION 'Production line not found for lot_id: %', NEW.lot_id;
    END IF;

    -- Get model short code from mapping
    SELECT mcm.short_code
    INTO v_model_short
    FROM lots l
    JOIN product_models pm ON l.product_model_id = pm.id
    JOIN model_code_mapping mcm ON pm.model_code = mcm.model_code
    WHERE l.id = NEW.lot_id;

    IF v_model_short IS NULL THEN
        RAISE EXCEPTION 'Model code mapping not found for lot_id: %', NEW.lot_id;
    END IF;

    -- Get production month (YYMM)
    SELECT TO_CHAR(l.production_date, 'YYMM')
    INTO v_month_part
    FROM lots l
    WHERE l.id = NEW.lot_id;

    -- Get sequence number (001-999)
    v_sequence := LPAD(NEW.sequence_in_lot::TEXT, 3, '0');

    -- Build serial number: KR01PSA2511001
    NEW.serial_number := v_line_code || v_model_short || v_month_part || v_sequence;
    NEW.format_version := 2;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_serial_number_v2() IS 'Generate V2 format serial number (14 chars): KR01PSA2511001';

-- =====================================================
-- 5. Create V2 LOT Number Generation Function
-- =====================================================

CREATE OR REPLACE FUNCTION generate_lot_number_v2()
RETURNS TRIGGER AS $$
DECLARE
    v_line_code VARCHAR(4);
    v_model_short VARCHAR(3);
    v_month_part VARCHAR(4);
BEGIN
    -- Extract line code (KR001 → KR01)
    SELECT CONCAT(
        SUBSTRING(line_code, 1, 2),
        LPAD(SUBSTRING(line_code, 3)::INTEGER::TEXT, 2, '0')
    )
    INTO v_line_code
    FROM production_lines
    WHERE id = NEW.production_line_id;

    IF v_line_code IS NULL THEN
        RAISE EXCEPTION 'Production line not found: %', NEW.production_line_id;
    END IF;

    -- Get model short code
    SELECT mcm.short_code
    INTO v_model_short
    FROM product_models pm
    JOIN model_code_mapping mcm ON pm.model_code = mcm.model_code
    WHERE pm.id = NEW.product_model_id;

    IF v_model_short IS NULL THEN
        RAISE EXCEPTION 'Model code mapping not found for product_model_id: %', NEW.product_model_id;
    END IF;

    -- Production month (YYMM)
    v_month_part := TO_CHAR(NEW.production_date, 'YYMM');

    -- LOT format: KR01PSA2511
    NEW.lot_number := v_line_code || v_model_short || v_month_part;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_lot_number_v2() IS 'Generate V2 format LOT number (11 chars): KR01PSA2511';

-- =====================================================
-- 6. Replace Triggers (Optional - Use with Caution)
-- =====================================================
-- WARNING: This will affect all new serial/LOT creations
-- Only uncomment when ready to fully switch to V2 format

-- DROP TRIGGER IF EXISTS trg_generate_serial_number ON serials;
-- CREATE TRIGGER trg_generate_serial_number
--     BEFORE INSERT ON serials
--     FOR EACH ROW
--     WHEN (NEW.serial_number IS NULL)
--     EXECUTE FUNCTION generate_serial_number_v2();

-- DROP TRIGGER IF EXISTS trg_generate_lot_number ON lots;
-- CREATE TRIGGER trg_generate_lot_number
--     BEFORE INSERT ON lots
--     FOR EACH ROW
--     WHEN (NEW.lot_number IS NULL)
--     EXECUTE FUNCTION generate_lot_number_v2();

-- =====================================================
-- 7. Migration Verification Queries
-- =====================================================

-- Check model code mappings
SELECT * FROM model_code_mapping ORDER BY id;

-- Check format version distribution
SELECT
    format_version,
    COUNT(*) as count,
    MIN(LENGTH(serial_number)) as min_length,
    MAX(LENGTH(serial_number)) as max_length
FROM serials
GROUP BY format_version
ORDER BY format_version;

-- Sample V1 format serials
SELECT serial_number, format_version, created_at
FROM serials
WHERE format_version = 1
ORDER BY created_at DESC
LIMIT 5;

-- =====================================================
-- END OF MIGRATION
-- =====================================================
