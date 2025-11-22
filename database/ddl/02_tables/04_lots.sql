-- ================================================================
-- DDL Script: lots Table
-- Description: Production batch tracking table for F2X NeuroHub MES
-- Author: F2X Development Team
-- Created: 2024-11-18
-- ================================================================

-- ================================================================
-- TABLE: lots
-- Purpose: Track production batches (LOTs) with up to 100 units each
-- LOT Number Format: Country(2)+Line(2)+Model(3)+Month(4)+Seq(2)
-- Example: KR01PSA251101 (13 chars)
-- ================================================================

-- Drop existing objects if needed (for development)
DROP TABLE IF EXISTS lots CASCADE;

-- Create the lots table
CREATE TABLE lots (
    -- Primary Key
    id BIGSERIAL NOT NULL,

    -- Core Columns
    lot_number VARCHAR(50) NOT NULL,                    -- Auto-generated LOT identifier
    product_model_id BIGINT NOT NULL,                   -- Foreign key to product_models
    production_date DATE NOT NULL,                      -- Scheduled/actual production date

    -- Quantity Tracking
    target_quantity INTEGER NOT NULL DEFAULT 100,       -- Target production quantity (typically 100)
    actual_quantity INTEGER NOT NULL DEFAULT 0,         -- Actual units produced
    passed_quantity INTEGER NOT NULL DEFAULT 0,         -- Units that passed all processes
    failed_quantity INTEGER NOT NULL DEFAULT 0,         -- Units that failed quality checks

    -- Status Management
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',      -- LOT lifecycle status

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),  -- LOT creation timestamp
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),  -- Last update timestamp
    closed_at TIMESTAMP WITH TIME ZONE NULL DEFAULT NULL        -- LOT closure/completion timestamp
);

-- ================================================================
-- CONSTRAINTS
-- ================================================================

-- Primary Key
ALTER TABLE lots
ADD CONSTRAINT pk_lots PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE lots
ADD CONSTRAINT fk_lots_product_model
FOREIGN KEY (product_model_id)
REFERENCES product_models(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Unique Constraints
ALTER TABLE lots
ADD CONSTRAINT uk_lots_lot_number UNIQUE (lot_number);

-- Check Constraints
ALTER TABLE lots
ADD CONSTRAINT chk_lots_status
CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED'));

ALTER TABLE lots
ADD CONSTRAINT chk_lots_target_quantity
CHECK (target_quantity > 0 AND target_quantity <= 100);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_actual_quantity
CHECK (actual_quantity >= 0 AND actual_quantity <= target_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_passed_quantity
CHECK (passed_quantity >= 0 AND passed_quantity <= actual_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_failed_quantity
CHECK (failed_quantity >= 0 AND failed_quantity <= actual_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_quantity_sum
CHECK (passed_quantity + failed_quantity <= actual_quantity);

-- ================================================================
-- INDEXES
-- ================================================================

-- Foreign key index
CREATE INDEX idx_lots_product_model
ON lots(product_model_id);

-- Status-based queries
CREATE INDEX idx_lots_status
ON lots(status);

-- Active LOTs index (frequently queried)
CREATE INDEX idx_lots_active
ON lots(status, production_date)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- Date range queries
CREATE INDEX idx_lots_production_date
ON lots(production_date DESC);

-- Composite index for filtering
CREATE INDEX idx_lots_model_date
ON lots(product_model_id, production_date);

-- Closed LOTs index (for archival)
CREATE INDEX idx_lots_closed_at
ON lots(closed_at)
WHERE closed_at IS NOT NULL;

-- ================================================================
-- TRIGGER FUNCTIONS
-- ================================================================

-- ----------------------------------------------------------------
-- Function: generate_lot_number()
-- Purpose: DEPRECATED - LOT number generation moved to Python application layer
-- This function is kept for reference but not used
-- Format: Country(2)+Line(2)+Model(3)+Month(4)+Seq(2) = 13 chars
-- ----------------------------------------------------------------
/*
-- DEPRECATED: This function is no longer used
CREATE OR REPLACE FUNCTION generate_lot_number()
RETURNS TRIGGER AS $$
DECLARE
    v_date_part VARCHAR(6);
    v_sequence INTEGER;
    v_new_lot_number VARCHAR(50);
BEGIN
    -- Only generate if lot_number is not provided
    IF NEW.lot_number IS NOT NULL AND NEW.lot_number != '' THEN
        RETURN NEW;
    END IF;

    -- Extract date part: YYMMDD
    v_date_part := TO_CHAR(NEW.production_date, 'YYMMDD');

    -- Get next sequence number for this production month
    SELECT COALESCE(MAX(
        CAST(
            SUBSTRING(lot_number FROM 12 FOR 3)
            AS INTEGER
        )
    ), 0) + 1
    INTO v_sequence
    FROM lots
    WHERE lot_number LIKE '______' || SUBSTRING(v_date_part FROM 1 FOR 4) || '%';

    -- Generate LOT number: KR01PSA2511001
    -- Format: Country(2) + Line(2) + Model(3) + YYMM(4) + Seq(3)
    v_new_lot_number := 'KR01' || 'PSA' || SUBSTRING(v_date_part FROM 1 FOR 4) ||
                        LPAD(v_sequence::TEXT, 3, '0');

    -- Assign to NEW record
    NEW.lot_number := v_new_lot_number;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_lot_number() IS
'DEPRECATED: LOT number generation moved to Python application layer.
Format: Country(2)+Line(2)+Model(3)+Month(4)+Seq(2) = 13 chars
Example: KR01PSA251101';
*/

-- ----------------------------------------------------------------
-- Function: validate_lot_status_transition()
-- Purpose: Enforce LOT status state machine transitions
-- ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION validate_lot_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Skip validation if status hasn't changed
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    -- Validate allowed transitions:
    -- CREATED → IN_PROGRESS
    -- IN_PROGRESS → COMPLETED
    -- COMPLETED → CLOSED

    IF OLD.status = 'CREATED' AND NEW.status NOT IN ('IN_PROGRESS') THEN
        RAISE EXCEPTION 'Invalid status transition: CREATED can only transition to IN_PROGRESS (attempted: % → %)',
            OLD.status, NEW.status;
    END IF;

    IF OLD.status = 'IN_PROGRESS' AND NEW.status NOT IN ('COMPLETED') THEN
        RAISE EXCEPTION 'Invalid status transition: IN_PROGRESS can only transition to COMPLETED (attempted: % → %)',
            OLD.status, NEW.status;
    END IF;

    IF OLD.status = 'COMPLETED' AND NEW.status NOT IN ('CLOSED') THEN
        RAISE EXCEPTION 'Invalid status transition: COMPLETED can only transition to CLOSED (attempted: % → %)',
            OLD.status, NEW.status;
    END IF;

    IF OLD.status = 'CLOSED' THEN
        RAISE EXCEPTION 'Invalid status transition: CLOSED is final state and cannot be changed (attempted: % → %)',
            OLD.status, NEW.status;
    END IF;

    -- Log the status transition for audit
    RAISE NOTICE 'LOT % status transition: % → %', NEW.lot_number, OLD.status, NEW.status;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_lot_status_transition() IS
'Enforces valid LOT status transitions:
- CREATED → IN_PROGRESS: Production started
- IN_PROGRESS → COMPLETED: All units finished
- COMPLETED → CLOSED: LOT finalized
- CLOSED: Final state, no further changes allowed';

-- ----------------------------------------------------------------
-- Function: auto_close_lot()
-- Purpose: Automatically set closed_at timestamp when LOT is completed
-- ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION auto_close_lot()
RETURNS TRIGGER AS $$
BEGIN
    -- Set closed_at timestamp when status changes to COMPLETED
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        -- Update the closed_at timestamp
        UPDATE lots
        SET closed_at = NOW()
        WHERE id = NEW.id AND closed_at IS NULL;

        -- Log the auto-close event
        RAISE NOTICE 'LOT % auto-closed at %', NEW.lot_number, NOW();
    END IF;

    -- Handle transition to CLOSED status
    IF NEW.status = 'CLOSED' AND OLD.status != 'CLOSED' THEN
        -- Ensure closed_at is set
        IF NEW.closed_at IS NULL THEN
            UPDATE lots
            SET closed_at = NOW()
            WHERE id = NEW.id;
        END IF;

        -- Validate that all quantities are finalized
        IF NEW.passed_quantity + NEW.failed_quantity != NEW.actual_quantity AND NEW.actual_quantity > 0 THEN
            RAISE WARNING 'LOT % closed with quantity mismatch: passed(%) + failed(%) != actual(%)',
                NEW.lot_number, NEW.passed_quantity, NEW.failed_quantity, NEW.actual_quantity;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auto_close_lot() IS
'Automatically manages LOT closure:
- Sets closed_at timestamp when status becomes COMPLETED
- Validates quantity consistency when closing
- Ensures closed_at is set for CLOSED status';

-- ================================================================
-- TRIGGERS
-- ================================================================

-- NOTE: LOT number generation is now handled in Python application layer
-- The trigger below is deprecated and commented out
-- -- Auto-generate LOT number
-- CREATE TRIGGER trg_lots_generate_number
-- BEFORE INSERT ON lots
-- FOR EACH ROW
-- EXECUTE FUNCTION generate_lot_number();

-- Auto-update updated_at timestamp
CREATE TRIGGER trg_lots_updated_at
BEFORE UPDATE ON lots
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Validate status transitions
CREATE TRIGGER trg_lots_validate_status
BEFORE UPDATE ON lots
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION validate_lot_status_transition();

-- Auto-close LOT when completed
CREATE TRIGGER trg_lots_auto_close
AFTER UPDATE ON lots
FOR EACH ROW
WHEN (NEW.status IN ('COMPLETED', 'CLOSED') AND OLD.status NOT IN ('COMPLETED', 'CLOSED'))
EXECUTE FUNCTION auto_close_lot();

-- Audit logging trigger
CREATE TRIGGER trg_lots_audit
AFTER INSERT OR UPDATE OR DELETE ON lots
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- ================================================================
-- TABLE COMMENTS
-- ================================================================

COMMENT ON TABLE lots IS
'Production batch tracking table. Each LOT represents a production run of up to 100 units
manufactured together on a specific date. Provides batch-level traceability
and quality metrics for the F2X NeuroHub manufacturing process.';

COMMENT ON COLUMN lots.id IS 'Primary key, auto-incrementing BIGINT';
COMMENT ON COLUMN lots.lot_number IS 'Auto-generated LOT identifier (Country+Line+Model+Month+Seq, 13 chars, e.g., KR01PSA251101)';
COMMENT ON COLUMN lots.product_model_id IS 'Foreign key reference to product_models table';
COMMENT ON COLUMN lots.production_date IS 'Scheduled/actual production date';
COMMENT ON COLUMN lots.target_quantity IS 'Target production quantity (max 100 units per LOT)';
COMMENT ON COLUMN lots.actual_quantity IS 'Actual units produced in this LOT';
COMMENT ON COLUMN lots.passed_quantity IS 'Number of units that passed all quality checks';
COMMENT ON COLUMN lots.failed_quantity IS 'Number of units that failed quality checks';
COMMENT ON COLUMN lots.status IS 'LOT lifecycle status: CREATED → IN_PROGRESS → COMPLETED → CLOSED';
COMMENT ON COLUMN lots.created_at IS 'LOT creation timestamp';
COMMENT ON COLUMN lots.updated_at IS 'Last modification timestamp (auto-updated)';
COMMENT ON COLUMN lots.closed_at IS 'LOT closure/completion timestamp (auto-set when COMPLETED)';

-- ================================================================
-- SAMPLE DATA (Optional - Comment out in production)
-- ================================================================

/*
-- Sample LOT creation
INSERT INTO lots (product_model_id, production_date, target_quantity)
VALUES
    (1, '2024-11-18', 100),
    (1, '2024-11-19', 100),
    (2, '2024-11-19', 50);   -- Partial LOT

-- View created LOTs
SELECT
    lot_number,
    production_date,
    status,
    target_quantity,
    actual_quantity,
    passed_quantity,
    failed_quantity
FROM lots
ORDER BY production_date DESC;
*/

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================

/*
-- Check all constraints
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'lots'::regclass
ORDER BY contype, conname;

-- Check all indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'lots'
ORDER BY indexname;

-- Check all triggers
SELECT
    tgname AS trigger_name,
    tgtype,
    proname AS function_name
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE tgrelid = 'lots'::regclass
ORDER BY tgname;
*/

-- ================================================================
-- END OF DDL SCRIPT
-- ================================================================