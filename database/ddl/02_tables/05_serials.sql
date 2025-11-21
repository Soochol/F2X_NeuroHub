-- ============================================================================
-- File: 05_serials.sql
-- Description: DDL for serials table - Individual unit tracking
-- Author: Database Architecture Team
-- Created: 2025-11-18
-- Modified: 2025-11-18
-- Version: 1.0
-- ============================================================================

-- ===================
-- TRIGGER FUNCTIONS
-- ===================
--
-- NOTE: Serial number generation is handled by the Python application layer.
-- The application generates serial numbers in the format: KR01PSA2511001 (14 chars)
-- Structure: [Country 2][Line 2][Model 3][Month 4][Sequence 3]
-- This ensures business logic remains in the application layer while the database
-- enforces data integrity through constraints.

-- Function: validate_lot_capacity()
-- Purpose: Enforce maximum 100 serials per LOT
CREATE OR REPLACE FUNCTION validate_lot_capacity()
RETURNS TRIGGER AS $$
DECLARE
    v_current_count INTEGER;
    v_target_quantity INTEGER;
BEGIN
    -- Get current serial count for LOT
    SELECT COUNT(*)
    INTO v_current_count
    FROM serials
    WHERE lot_id = NEW.lot_id;

    -- Get target quantity for LOT
    SELECT target_quantity
    INTO v_target_quantity
    FROM lots
    WHERE id = NEW.lot_id;

    IF v_target_quantity IS NULL THEN
        RAISE EXCEPTION 'Invalid lot_id: % - LOT not found', NEW.lot_id;
    END IF;

    -- Check if adding this serial would exceed capacity
    IF v_current_count >= v_target_quantity THEN
        RAISE EXCEPTION 'LOT capacity exceeded: maximum % serials allowed for this LOT', v_target_quantity;
    END IF;

    -- Additional check for hard limit of 100
    IF v_current_count >= 100 THEN
        RAISE EXCEPTION 'LOT capacity exceeded: maximum 100 serials allowed per LOT';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: validate_serial_status_transition()
-- Purpose: Enforce state machine rules for serial status transitions
CREATE OR REPLACE FUNCTION validate_serial_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Skip validation on INSERT
    IF TG_OP = 'INSERT' THEN
        RETURN NEW;
    END IF;

    -- Prevent changing status if it's the same
    IF OLD.status = NEW.status THEN
        -- Allow other field updates without status change
        RETURN NEW;
    END IF;

    -- Valid transitions:
    -- CREATED → IN_PROGRESS
    -- IN_PROGRESS → PASSED/FAILED
    -- FAILED → IN_PROGRESS (rework, max 3 times)

    IF OLD.status = 'CREATED' AND NEW.status NOT IN ('IN_PROGRESS') THEN
        RAISE EXCEPTION 'Invalid status transition: CREATED can only transition to IN_PROGRESS (current: %, attempted: %)',
            OLD.status, NEW.status;
    END IF;

    IF OLD.status = 'IN_PROGRESS' AND NEW.status NOT IN ('PASSED', 'FAILED') THEN
        RAISE EXCEPTION 'Invalid status transition: IN_PROGRESS can only transition to PASSED or FAILED (current: %, attempted: %)',
            OLD.status, NEW.status;
    END IF;

    -- Rework logic for FAILED → IN_PROGRESS
    IF OLD.status = 'FAILED' AND NEW.status = 'IN_PROGRESS' THEN
        -- Increment rework count
        NEW.rework_count := OLD.rework_count + 1;

        -- Check max rework attempts
        IF NEW.rework_count > 3 THEN
            RAISE EXCEPTION 'Maximum rework attempts (3) exceeded for serial %', OLD.serial_number;
        END IF;

        -- Clear failure reason for rework
        NEW.failure_reason := NULL;

        -- Clear completed_at for rework
        NEW.completed_at := NULL;
    END IF;

    -- Prevent changes after PASSED
    IF OLD.status = 'PASSED' THEN
        RAISE EXCEPTION 'Invalid status transition: PASSED is final, cannot change status (current: %, attempted: %)',
            OLD.status, NEW.status;
    END IF;

    -- Auto-set completed_at timestamp when reaching terminal state
    IF NEW.status IN ('PASSED', 'FAILED') AND OLD.status NOT IN ('PASSED', 'FAILED') THEN
        NEW.completed_at := NOW();
    END IF;

    -- Validate failure_reason requirement
    IF NEW.status = 'FAILED' AND (NEW.failure_reason IS NULL OR TRIM(NEW.failure_reason) = '') THEN
        RAISE EXCEPTION 'failure_reason is required when status is FAILED';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: update_lot_quantities()
-- Purpose: Auto-update LOT actual_quantity, passed_quantity, and failed_quantity
CREATE OR REPLACE FUNCTION update_lot_quantities()
RETURNS TRIGGER AS $$
DECLARE
    v_lot_id BIGINT;
    v_actual_count INTEGER;
    v_passed_count INTEGER;
    v_failed_count INTEGER;
BEGIN
    -- Determine which lot_id to update
    IF TG_OP = 'DELETE' THEN
        v_lot_id := OLD.lot_id;
    ELSE
        v_lot_id := NEW.lot_id;
    END IF;

    -- Calculate current counts
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE status = 'PASSED'),
        COUNT(*) FILTER (WHERE status = 'FAILED' AND rework_count >= 3)
    INTO v_actual_count, v_passed_count, v_failed_count
    FROM serials
    WHERE lot_id = v_lot_id;

    -- Update LOT quantities
    UPDATE lots
    SET
        actual_quantity = v_actual_count,
        passed_quantity = v_passed_count,
        failed_quantity = v_failed_count,
        updated_at = NOW()
    WHERE id = v_lot_id;

    -- For UPDATE operations where lot_id changed (shouldn't happen but handle it)
    IF TG_OP = 'UPDATE' AND OLD.lot_id != NEW.lot_id THEN
        -- Recalculate for old LOT
        SELECT
            COUNT(*),
            COUNT(*) FILTER (WHERE status = 'PASSED'),
            COUNT(*) FILTER (WHERE status = 'FAILED' AND rework_count >= 3)
        INTO v_actual_count, v_passed_count, v_failed_count
        FROM serials
        WHERE lot_id = OLD.lot_id;

        UPDATE lots
        SET
            actual_quantity = v_actual_count,
            passed_quantity = v_passed_count,
            failed_quantity = v_failed_count,
            updated_at = NOW()
        WHERE id = OLD.lot_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ===================
-- TABLE DEFINITION
-- ===================

CREATE TABLE IF NOT EXISTS serials (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Serial identification
    serial_number VARCHAR(50) NOT NULL,

    -- LOT relationship
    lot_id BIGINT NOT NULL,
    sequence_in_lot INTEGER NOT NULL,

    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    rework_count INTEGER NOT NULL DEFAULT 0,
    failure_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ===================
-- CONSTRAINTS
-- ===================

-- Primary Key
ALTER TABLE serials
ADD CONSTRAINT pk_serials PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE serials
ADD CONSTRAINT fk_serials_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Unique Constraints
ALTER TABLE serials
ADD CONSTRAINT uk_serials_serial_number UNIQUE (serial_number);

ALTER TABLE serials
ADD CONSTRAINT uk_serials_lot_sequence UNIQUE (lot_id, sequence_in_lot);

-- Check Constraints
ALTER TABLE serials
ADD CONSTRAINT chk_serials_status
CHECK (status IN ('CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED'));

ALTER TABLE serials
ADD CONSTRAINT chk_serials_sequence
CHECK (sequence_in_lot >= 1 AND sequence_in_lot <= 100);

ALTER TABLE serials
ADD CONSTRAINT chk_serials_rework_count
CHECK (rework_count >= 0 AND rework_count <= 3);

ALTER TABLE serials
ADD CONSTRAINT chk_serials_failure_reason
CHECK (
    (status = 'FAILED' AND failure_reason IS NOT NULL) OR
    (status != 'FAILED' AND failure_reason IS NULL)
);

-- ===================
-- INDEXES
-- ===================

-- Foreign key index
CREATE INDEX idx_serials_lot
ON serials(lot_id);

-- Status-based queries
CREATE INDEX idx_serials_status
ON serials(status);

-- Active serials index (partial index for performance)
CREATE INDEX idx_serials_active
ON serials(lot_id, status)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- Failed serials analysis (partial index)
CREATE INDEX idx_serials_failed
ON serials(lot_id, failure_reason)
WHERE status = 'FAILED';

-- Rework tracking (partial index)
CREATE INDEX idx_serials_rework
ON serials(rework_count)
WHERE rework_count > 0;

-- Completion time analysis (partial index)
CREATE INDEX idx_serials_completed_at
ON serials(completed_at)
WHERE completed_at IS NOT NULL;

-- ===================
-- TRIGGERS
-- ===================
--
-- NOTE: Serial number auto-generation trigger removed.
-- Serial numbers are now generated by the Python application layer.
-- See: backend/app/crud/serial.py and backend/app/utils/serial_number.py

-- Auto-update updated_at timestamp
CREATE TRIGGER trg_serials_updated_at
BEFORE UPDATE ON serials
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Validate status transitions
CREATE TRIGGER trg_serials_validate_status
BEFORE UPDATE ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_serial_status_transition();

-- Update LOT quantities
CREATE TRIGGER trg_serials_update_lot_quantities
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW
EXECUTE FUNCTION update_lot_quantities();

-- Validate LOT capacity (max 100 serials)
CREATE TRIGGER trg_serials_validate_lot_capacity
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_lot_capacity();

-- Audit logging trigger
CREATE TRIGGER trg_serials_audit
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- ===================
-- COMMENTS
-- ===================

-- Table comment
COMMENT ON TABLE serials IS 'Individual unit tracking table. Each serial represents one physical product unit within a LOT.';

-- Column comments
COMMENT ON COLUMN serials.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN serials.serial_number IS 'Serial identifier generated by Python application (14 chars, format: KR01PSA2511001, structure: [Country 2][Line 2][Model 3][Month 4][Sequence 3])';
COMMENT ON COLUMN serials.lot_id IS 'Foreign key reference to parent LOT';
COMMENT ON COLUMN serials.sequence_in_lot IS 'Sequence number within LOT (1-100)';
COMMENT ON COLUMN serials.status IS 'Serial lifecycle status: CREATED, IN_PROGRESS, PASSED, FAILED';
COMMENT ON COLUMN serials.rework_count IS 'Number of rework attempts (max 3)';
COMMENT ON COLUMN serials.failure_reason IS 'Reason for failure (required when status = FAILED)';
COMMENT ON COLUMN serials.created_at IS 'Serial creation timestamp';
COMMENT ON COLUMN serials.updated_at IS 'Last update timestamp';
COMMENT ON COLUMN serials.completed_at IS 'Timestamp when serial reached PASSED or FAILED status';

-- ============================================================================
-- USAGE NOTES:
-- ============================================================================
-- 1. This table depends on the 'lots' table existing first
-- 2. The update_timestamp() function must exist (from 01_functions/update_timestamp.sql)
-- 3. The log_audit_event() function must exist (from 01_functions/log_audit_event.sql)
-- 4. Serial numbers are generated by Python application layer (backend/app/crud/serial.py)
--    Format: KR01PSA2511001 (14 chars)
--    Structure: [Country 2][Line 2][Model 3][Month 4][Sequence 3]
--    Generation uses production_line and product_model data
-- 5. Maximum 100 serials per LOT (enforced by triggers)
-- 6. Status transitions follow strict state machine rules
-- 7. Rework is limited to 3 attempts per serial
-- 8. Failure reason is mandatory when marking serial as FAILED
-- ============================================================================