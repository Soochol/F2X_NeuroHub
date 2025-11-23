-- =============================================================================
-- DDL Script: wip_items (Work In Progress Items)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Track individual products during manufacturing processes 1-6 using
--          temporary WIP IDs before serial number generation at process 7.
--          Each LOT spawns 1-100 WIP items at production start.
--
-- WIP ID Format: WIP-{LOT_NUMBER}-{SEQUENCE}
--   Example: WIP-KR01PSA2511-001
--   - LOT_NUMBER: 14 chars (e.g., KR01PSA2511001)
--   - SEQUENCE: 3-digit zero-padded (001-100)
--
-- Lifecycle:
--   1. LOT created → WIP items generated (CREATED)
--   2. Process 1-6 execution → status updates (IN_PROGRESS)
--   3. Process 7 (Label Printing) → Serial created → WIP COMPLETED
--   4. Process failure → WIP marked FAILED
--
-- Dependencies:
--   - lots (foreign key)
--   - serials (foreign key, nullable until process 7)
--   - processes (foreign key for current_process_id)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS wip_items CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE wip_items (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- WIP identification
    wip_id VARCHAR(50) NOT NULL,                      -- Auto-generated WIP identifier (WIP-{LOT}-{seq})

    -- Foreign keys
    lot_id BIGINT NOT NULL,                           -- Parent LOT reference
    serial_id BIGINT,                                 -- Linked serial (NULL until process 7)

    -- Sequence tracking
    sequence_in_lot INTEGER NOT NULL,                 -- Position in LOT (1-100)

    -- Status management
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',    -- WIP lifecycle status

    -- Process tracking
    current_process_id BIGINT,                        -- Current/last process location

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),      -- WIP creation time
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),      -- Last update time
    completed_at TIMESTAMP WITH TIME ZONE,                           -- All processes (1-6) completed time
    converted_at TIMESTAMP WITH TIME ZONE,                           -- Serial conversion time (process 7)

    -- Additional tracking
    notes TEXT                                        -- Additional notes or observations
);

-- =============================================================================
-- COMMENT DOCUMENTATION
-- =============================================================================
COMMENT ON TABLE wip_items IS
'Work In Progress (WIP) tracking table for individual units during processes 1-6.
Each WIP item represents one physical product unit before serial number generation at process 7.';

COMMENT ON COLUMN wip_items.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN wip_items.wip_id IS 'Auto-generated WIP identifier, format: WIP-{LOT_NUMBER}-{SEQUENCE} (e.g., WIP-KR01PSA2511-001)';
COMMENT ON COLUMN wip_items.lot_id IS 'Foreign key to parent LOT';
COMMENT ON COLUMN wip_items.serial_id IS 'Foreign key to serial, populated at process 7 (Label Printing) when serial number is generated';
COMMENT ON COLUMN wip_items.sequence_in_lot IS 'Sequential position within LOT (1-100)';
COMMENT ON COLUMN wip_items.status IS 'WIP lifecycle status: CREATED → IN_PROGRESS → COMPLETED (or FAILED)';
COMMENT ON COLUMN wip_items.current_process_id IS 'Current or most recent process that this WIP item is/was at';
COMMENT ON COLUMN wip_items.created_at IS 'WIP item creation timestamp (at LOT start)';
COMMENT ON COLUMN wip_items.updated_at IS 'Last update timestamp (auto-updated)';
COMMENT ON COLUMN wip_items.completed_at IS 'Completion timestamp when all processes 1-6 are completed (status becomes COMPLETED)';
COMMENT ON COLUMN wip_items.converted_at IS 'Conversion timestamp when serial is generated (process 7) and WIP transitions to CONVERTED status';
COMMENT ON COLUMN wip_items.notes IS 'Additional notes or observations';

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE wip_items
ADD CONSTRAINT pk_wip_items PRIMARY KEY (id);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================
-- Foreign key to lots table
ALTER TABLE wip_items
ADD CONSTRAINT fk_wip_items_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to serials table (nullable until process 7)
ALTER TABLE wip_items
ADD CONSTRAINT fk_wip_items_serial
FOREIGN KEY (serial_id)
REFERENCES serials(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to processes table (for current process location)
ALTER TABLE wip_items
ADD CONSTRAINT fk_wip_items_current_process
FOREIGN KEY (current_process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- =============================================================================
-- UNIQUE CONSTRAINTS
-- =============================================================================
-- WIP ID must be globally unique
ALTER TABLE wip_items
ADD CONSTRAINT uk_wip_items_wip_id UNIQUE (wip_id);

-- Sequence in LOT must be unique per LOT
ALTER TABLE wip_items
ADD CONSTRAINT uk_wip_items_lot_sequence UNIQUE (lot_id, sequence_in_lot);

-- Serial ID must be unique (one-to-one mapping after process 7)
ALTER TABLE wip_items
ADD CONSTRAINT uk_wip_items_serial UNIQUE (serial_id);

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Status validation
ALTER TABLE wip_items
ADD CONSTRAINT chk_wip_items_status
CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CONVERTED'));

-- Sequence in LOT must be between 1 and 100
ALTER TABLE wip_items
ADD CONSTRAINT chk_wip_items_sequence
CHECK (sequence_in_lot BETWEEN 1 AND 100);

-- Serial ID consistency: CONVERTED status requires serial_id
ALTER TABLE wip_items
ADD CONSTRAINT chk_wip_items_serial_consistency
CHECK (
    (status = 'CONVERTED' AND serial_id IS NOT NULL) OR
    (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED'))
);

-- Completed timestamp consistency
ALTER TABLE wip_items
ADD CONSTRAINT chk_wip_items_completed_at
CHECK (
    (status IN ('COMPLETED', 'CONVERTED') AND completed_at IS NOT NULL) OR
    (status IN ('CREATED', 'IN_PROGRESS', 'FAILED'))
);

-- Converted timestamp consistency
ALTER TABLE wip_items
ADD CONSTRAINT chk_wip_items_converted_at
CHECK (
    (status = 'CONVERTED' AND converted_at IS NOT NULL) OR
    (status != 'CONVERTED')
);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Foreign key indexes
CREATE INDEX idx_wip_items_lot
ON wip_items(lot_id);

CREATE INDEX idx_wip_items_serial
ON wip_items(serial_id)
WHERE serial_id IS NOT NULL;

CREATE INDEX idx_wip_items_current_process
ON wip_items(current_process_id)
WHERE current_process_id IS NOT NULL;

-- Status-based queries (frequently used for dashboards)
CREATE INDEX idx_wip_items_status
ON wip_items(status);

-- Active WIP items (most common query)
CREATE INDEX idx_wip_items_active
ON wip_items(status, lot_id)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- Composite index for LOT-level queries (lot + status + current process)
CREATE INDEX idx_wip_items_lot_status_process
ON wip_items(lot_id, status, current_process_id);

-- Process-level WIP queuing (for production monitoring)
CREATE INDEX idx_wip_items_process_queue
ON wip_items(current_process_id, status)
WHERE status = 'IN_PROGRESS';

-- Completion tracking
CREATE INDEX idx_wip_items_completed_at
ON wip_items(completed_at DESC)
WHERE completed_at IS NOT NULL;

-- Time-based analytics
CREATE INDEX idx_wip_items_created_at
ON wip_items(created_at DESC);

-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: generate_wip_id()
-- Purpose: Auto-generate WIP ID in format: WIP-{LOT_NUMBER}-{SEQUENCE}
-- Example: WIP-KR01PSA2511-001
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION generate_wip_id()
RETURNS TRIGGER AS $$
DECLARE
    v_lot_number VARCHAR(50);
    v_wip_id VARCHAR(50);
BEGIN
    -- Only generate if wip_id is not provided
    IF NEW.wip_id IS NOT NULL AND NEW.wip_id != '' THEN
        RETURN NEW;
    END IF;

    -- Get LOT number from lots table
    SELECT lot_number INTO v_lot_number
    FROM lots
    WHERE id = NEW.lot_id;

    IF v_lot_number IS NULL THEN
        RAISE EXCEPTION 'Cannot generate WIP ID: LOT with id % not found', NEW.lot_id;
    END IF;

    -- Generate WIP ID: WIP-{LOT_NUMBER}-{SEQUENCE}
    -- Sequence is zero-padded to 3 digits (001-100)
    v_wip_id := 'WIP-' || v_lot_number || '-' || LPAD(NEW.sequence_in_lot::TEXT, 3, '0');

    -- Assign to NEW record
    NEW.wip_id := v_wip_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_wip_id() IS
'Auto-generates WIP ID in format: WIP-{LOT_NUMBER}-{SEQUENCE}
Example: WIP-KR01PSA2511-001
Triggered before INSERT on wip_items when wip_id is not provided.';

-- -----------------------------------------------------------------------------
-- Function: validate_wip_status_transition()
-- Purpose: Enforce WIP status state machine transitions
-- Valid transitions:
--   CREATED → IN_PROGRESS (start processing)
--   IN_PROGRESS → COMPLETED (serial generated at process 7)
--   IN_PROGRESS → FAILED (quality failure)
--   FAILED → IN_PROGRESS (rework attempt)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION validate_wip_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Skip validation if status hasn't changed
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    -- Validate allowed transitions
    CASE OLD.status
        WHEN 'CREATED' THEN
            IF NEW.status NOT IN ('IN_PROGRESS') THEN
                RAISE EXCEPTION 'Invalid WIP status transition: CREATED can only transition to IN_PROGRESS (attempted: % → %)',
                    OLD.status, NEW.status;
            END IF;

        WHEN 'IN_PROGRESS' THEN
            IF NEW.status NOT IN ('COMPLETED', 'FAILED') THEN
                RAISE EXCEPTION 'Invalid WIP status transition: IN_PROGRESS can only transition to COMPLETED or FAILED (attempted: % → %)',
                    OLD.status, NEW.status;
            END IF;

        WHEN 'FAILED' THEN
            IF NEW.status NOT IN ('IN_PROGRESS') THEN
                RAISE EXCEPTION 'Invalid WIP status transition: FAILED can only transition back to IN_PROGRESS for rework (attempted: % → %)',
                    OLD.status, NEW.status;
            END IF;

        WHEN 'COMPLETED' THEN
            RAISE EXCEPTION 'Invalid WIP status transition: COMPLETED is a final state and cannot be changed (attempted: % → %)',
                OLD.status, NEW.status;
    END CASE;

    -- Log the status transition
    RAISE NOTICE 'WIP % status transition: % → %', NEW.wip_id, OLD.status, NEW.status;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_wip_status_transition() IS
'Enforces valid WIP status transitions:
- CREATED → IN_PROGRESS: Production started
- IN_PROGRESS → COMPLETED: Serial generated (process 7)
- IN_PROGRESS → FAILED: Quality failure
- FAILED → IN_PROGRESS: Rework attempt
- COMPLETED: Final state, no further changes';

-- -----------------------------------------------------------------------------
-- Function: auto_complete_wip_on_serial_creation()
-- Purpose: Automatically mark WIP as COMPLETED when serial is assigned
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION auto_complete_wip_on_serial_creation()
RETURNS TRIGGER AS $$
BEGIN
    -- If serial_id is being set (process 7), mark WIP as completed
    IF NEW.serial_id IS NOT NULL AND (OLD.serial_id IS NULL OR OLD.serial_id != NEW.serial_id) THEN
        NEW.status := 'COMPLETED';
        NEW.completed_at := NOW();

        RAISE NOTICE 'WIP % automatically marked as COMPLETED due to serial assignment (serial_id: %)',
            NEW.wip_id, NEW.serial_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auto_complete_wip_on_serial_creation() IS
'Automatically marks WIP item as COMPLETED when serial_id is assigned at process 7.
Sets completed_at timestamp and logs the transition.';

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-generate WIP ID
CREATE TRIGGER trg_wip_items_generate_id
BEFORE INSERT ON wip_items
FOR EACH ROW
WHEN (NEW.wip_id IS NULL OR NEW.wip_id = '')
EXECUTE FUNCTION generate_wip_id();

-- Auto-update updated_at timestamp
CREATE TRIGGER trg_wip_items_updated_at
BEFORE UPDATE ON wip_items
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Validate status transitions
CREATE TRIGGER trg_wip_items_validate_status
BEFORE UPDATE ON wip_items
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION validate_wip_status_transition();

-- Auto-complete on serial assignment
CREATE TRIGGER trg_wip_items_auto_complete
BEFORE UPDATE ON wip_items
FOR EACH ROW
WHEN (NEW.serial_id IS NOT NULL AND (OLD.serial_id IS NULL OR OLD.serial_id IS DISTINCT FROM NEW.serial_id))
EXECUTE FUNCTION auto_complete_wip_on_serial_creation();

-- Audit logging trigger
CREATE TRIGGER trg_wip_items_audit
AFTER INSERT OR UPDATE OR DELETE ON wip_items
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- VERIFICATION QUERIES (For testing)
-- =============================================================================

/*
-- Verify WIP items for a LOT
SELECT
    wip_id,
    sequence_in_lot,
    status,
    current_process_id,
    serial_id,
    created_at,
    completed_at
FROM wip_items
WHERE lot_id = 1
ORDER BY sequence_in_lot;

-- Check WIP item counts by status
SELECT
    l.lot_number,
    wi.status,
    COUNT(*) as count
FROM wip_items wi
JOIN lots l ON wi.lot_id = l.id
GROUP BY l.lot_number, wi.status
ORDER BY l.lot_number, wi.status;

-- Find active WIP items at specific process
SELECT
    wi.wip_id,
    l.lot_number,
    p.process_code,
    wi.status,
    wi.created_at
FROM wip_items wi
JOIN lots l ON wi.lot_id = l.id
LEFT JOIN processes p ON wi.current_process_id = p.id
WHERE wi.status = 'IN_PROGRESS'
  AND wi.current_process_id = 3
ORDER BY wi.created_at;
*/

-- =============================================================================
-- END OF DDL SCRIPT
-- =============================================================================
