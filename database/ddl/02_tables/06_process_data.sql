-- =============================================================================
-- DDL Script: process_data (공정 실행 데이터)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Process execution records table. Captures actual measurements, test results,
--          operator information, and timing for each process execution. This is the core
--          transactional table linking serials/LOTs to processes with detailed JSONB data.
-- Dependencies:
--   - lots (foreign key)
--   - serials (foreign key)
--   - processes (foreign key)
--   - users (foreign key)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS process_data CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE process_data (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Foreign keys
    lot_id BIGINT NOT NULL,                       -- Reference to lots table (required)
    serial_id BIGINT,                             -- Reference to serials table (NULL for LOT-level data)
    process_id BIGINT NOT NULL,                   -- Reference to processes table
    operator_id BIGINT NOT NULL,                  -- Reference to users table (who performed the process)

    -- Core data columns
    data_level VARCHAR(10) NOT NULL,              -- Data granularity: LOT or SERIAL
    result VARCHAR(10) NOT NULL,                  -- Process result: PASS, FAIL, REWORK

    -- Process specific data (JSONB)
    measurements JSONB DEFAULT '{}',              -- Process-specific measurement data
    defects JSONB DEFAULT '[]',                   -- Defect information (if result = FAIL)

    -- Additional information
    notes TEXT,                                   -- Additional comments or observations

    -- Timing columns
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,     -- Process start timestamp
    completed_at TIMESTAMP WITH TIME ZONE,            -- Process completion timestamp
    duration_seconds INTEGER,                         -- Actual process duration (auto-calculated)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()  -- Record creation timestamp
);

-- =============================================================================
-- COMMENT DOCUMENTATION
-- =============================================================================
COMMENT ON TABLE process_data IS 'Process execution records capturing measurements, results, and operator information for each process execution';
COMMENT ON COLUMN process_data.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN process_data.lot_id IS 'Foreign key to lots table (required)';
COMMENT ON COLUMN process_data.serial_id IS 'Foreign key to serials table (NULL for LOT-level data)';
COMMENT ON COLUMN process_data.process_id IS 'Foreign key to processes table';
COMMENT ON COLUMN process_data.operator_id IS 'Foreign key to users table (who performed the process)';
COMMENT ON COLUMN process_data.data_level IS 'Data granularity: LOT (LOT-level process) or SERIAL (per-unit process)';
COMMENT ON COLUMN process_data.result IS 'Process result: PASS (successful), FAIL (quality check failed), REWORK (retry after failure)';
COMMENT ON COLUMN process_data.measurements IS 'Process-specific measurement data in JSON format';
COMMENT ON COLUMN process_data.defects IS 'Array of defect information if result = FAIL';
COMMENT ON COLUMN process_data.notes IS 'Additional comments or observations from operator';
COMMENT ON COLUMN process_data.started_at IS 'Process start timestamp';
COMMENT ON COLUMN process_data.completed_at IS 'Process completion timestamp';
COMMENT ON COLUMN process_data.duration_seconds IS 'Actual process duration in seconds (auto-calculated)';
COMMENT ON COLUMN process_data.created_at IS 'Record creation timestamp';

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE process_data
ADD CONSTRAINT pk_process_data PRIMARY KEY (id);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================
-- Foreign key to lots table
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to serials table
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_serial
FOREIGN KEY (serial_id)
REFERENCES serials(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to processes table
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to users table (operator)
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_operator
FOREIGN KEY (operator_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Data level must be LOT or SERIAL
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_data_level
CHECK (data_level IN ('LOT', 'SERIAL'));

-- Result must be PASS, FAIL, or REWORK
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_result
CHECK (result IN ('PASS', 'FAIL', 'REWORK'));

-- Serial ID consistency with data level
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_serial_id
CHECK (
    (data_level = 'LOT' AND serial_id IS NULL) OR
    (data_level = 'SERIAL' AND serial_id IS NOT NULL)
);

-- Duration must be non-negative if set
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_duration
CHECK (duration_seconds IS NULL OR duration_seconds >= 0);

-- Completed timestamp must be after started timestamp
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_timestamps
CHECK (completed_at IS NULL OR completed_at >= started_at);

-- =============================================================================
-- UNIQUE CONSTRAINTS (Partial Indexes)
-- =============================================================================
-- Prevent duplicate PASS records for serial-process combination
CREATE UNIQUE INDEX uk_process_data_serial_process
ON process_data(serial_id, process_id)
WHERE serial_id IS NOT NULL AND result = 'PASS';

-- Prevent duplicate PASS records for LOT-level processes
CREATE UNIQUE INDEX uk_process_data_lot_process
ON process_data(lot_id, process_id)
WHERE serial_id IS NULL AND data_level = 'LOT' AND result = 'PASS';

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Foreign key indexes
CREATE INDEX idx_process_data_lot
ON process_data(lot_id);

CREATE INDEX idx_process_data_serial
ON process_data(serial_id)
WHERE serial_id IS NOT NULL;

CREATE INDEX idx_process_data_process
ON process_data(process_id);

CREATE INDEX idx_process_data_operator
ON process_data(operator_id);

-- Composite indexes for common queries
CREATE INDEX idx_process_data_serial_process
ON process_data(serial_id, process_id, result)
WHERE serial_id IS NOT NULL;

CREATE INDEX idx_process_data_lot_process
ON process_data(lot_id, process_id, result);

CREATE INDEX idx_process_data_process_result
ON process_data(process_id, result, started_at);

-- Time-based queries (for analytics and reporting)
CREATE INDEX idx_process_data_started_at
ON process_data(started_at DESC);

CREATE INDEX idx_process_data_completed_at
ON process_data(completed_at DESC)
WHERE completed_at IS NOT NULL;

-- Failed processes analysis (specialized index)
CREATE INDEX idx_process_data_failed
ON process_data(process_id, started_at)
WHERE result = 'FAIL';

-- GIN indexes for JSONB columns (enables efficient queries on JSON data)
CREATE INDEX idx_process_data_measurements
ON process_data USING gin(measurements);

CREATE INDEX idx_process_data_defects
ON process_data USING gin(defects);

-- Data level filtering
CREATE INDEX idx_process_data_data_level
ON process_data(data_level, lot_id);

-- Operator performance analysis
CREATE INDEX idx_process_data_operator_performance
ON process_data(operator_id, process_id, result, started_at);

-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: calculate_process_duration()
-- Purpose: Automatically calculate duration_seconds from timestamps
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_process_duration()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate duration if completed_at is set
    IF NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_process_duration() IS 'Automatically calculates duration_seconds from started_at and completed_at timestamps';

-- -----------------------------------------------------------------------------
-- Function: validate_process_sequence()
-- Purpose: Enforce process sequence 1→2→3→4→5→6→7→8
-- Special rule: Process 7 (Label Printing) requires ALL processes 1-6 to be PASS
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION validate_process_sequence()
RETURNS TRIGGER AS $$
DECLARE
    v_current_process_number INTEGER;
    v_max_completed_process_number INTEGER;
    v_allow_skip BOOLEAN;
    v_passed_count INTEGER;
BEGIN
    -- Only validate for SERIAL-level data
    IF NEW.data_level != 'SERIAL' OR NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Get current process number
    SELECT process_number, allow_skip
    INTO v_current_process_number, v_allow_skip
    FROM processes
    WHERE id = NEW.process_id;

    -- If allow_skip is true, no sequence validation needed
    IF v_allow_skip THEN
        RETURN NEW;
    END IF;

    -- Get max completed process number for this serial
    SELECT COALESCE(MAX(p.process_number), 0)
    INTO v_max_completed_process_number
    FROM process_data pd
    JOIN processes p ON pd.process_id = p.id
    WHERE pd.serial_id = NEW.serial_id
      AND pd.result = 'PASS'
      AND p.allow_skip = false;  -- Only consider non-skippable processes

    -- Validate sequence (can only do next process or redo failed process)
    IF v_current_process_number > v_max_completed_process_number + 1 THEN
        RAISE EXCEPTION 'Process sequence violation: cannot execute process % before completing process %',
            v_current_process_number, v_max_completed_process_number + 1
            USING HINT = 'Complete all required previous processes first';
    END IF;

    -- BR-007: Special validation for Process 7 (Label Printing)
    -- All processes 1-6 must be PASS before starting Process 7
    IF v_current_process_number = 7 THEN
        SELECT COUNT(DISTINCT p.process_number)
        INTO v_passed_count
        FROM process_data pd
        JOIN processes p ON pd.process_id = p.id
        WHERE pd.serial_id = NEW.serial_id
          AND p.process_number BETWEEN 1 AND 6
          AND pd.result = 'PASS';

        IF v_passed_count < 6 THEN
            RAISE EXCEPTION 'Process 7 (Label Printing) requires all previous processes (1-6) to be PASS. Current PASS count: %',
                v_passed_count
                USING HINT = 'Ensure all manufacturing processes 1-6 are completed with PASS result';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validate_process_sequence() IS 'Enforces process execution sequence, preventing out-of-order process execution';

-- -----------------------------------------------------------------------------
-- Function: update_serial_status_from_process()
-- Purpose: Update serial status based on process execution results
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_serial_status_from_process()
RETURNS TRIGGER AS $$
DECLARE
    v_all_processes_complete BOOLEAN;
    v_final_process_number INTEGER;
    v_has_failures BOOLEAN;
BEGIN
    -- Only process SERIAL-level data
    IF NEW.data_level != 'SERIAL' OR NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Get the maximum process number (final process)
    SELECT MAX(process_number) INTO v_final_process_number
    FROM processes
    WHERE is_active = true;

    -- Check if all processes are complete for this serial
    SELECT COUNT(DISTINCT p.id) = COUNT(DISTINCT pd.process_id)
    INTO v_all_processes_complete
    FROM processes p
    LEFT JOIN process_data pd ON pd.process_id = p.id
        AND pd.serial_id = NEW.serial_id
        AND pd.result = 'PASS'
    WHERE p.is_active = true
      AND p.is_required = true;

    -- Check for any failures
    SELECT EXISTS(
        SELECT 1 FROM process_data
        WHERE serial_id = NEW.serial_id
        AND result = 'FAIL'
        AND id = (
            SELECT MAX(id) FROM process_data pd2
            WHERE pd2.serial_id = process_data.serial_id
            AND pd2.process_id = process_data.process_id
        )
    ) INTO v_has_failures;

    -- Update serial status based on process results
    IF NEW.result = 'FAIL' THEN
        -- Mark serial as requiring rework if process failed
        UPDATE serials
        SET status = 'REWORK',
            updated_at = NOW()
        WHERE id = NEW.serial_id;

    ELSIF NEW.result = 'PASS' THEN
        -- Check if this is the final process
        IF EXISTS (
            SELECT 1 FROM processes
            WHERE id = NEW.process_id
            AND process_number = v_final_process_number
        ) THEN
            -- Final process passed - mark as completed
            UPDATE serials
            SET status = 'COMPLETED',
                updated_at = NOW()
            WHERE id = NEW.serial_id;
        ELSIF v_has_failures THEN
            -- Has failures but current process passed - still in rework
            UPDATE serials
            SET status = 'REWORK',
                updated_at = NOW()
            WHERE id = NEW.serial_id;
        ELSE
            -- Process passed and no failures - mark as in progress
            UPDATE serials
            SET status = 'IN_PROGRESS',
                updated_at = NOW()
            WHERE id = NEW.serial_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_serial_status_from_process() IS 'Updates serial status based on process execution results (IN_PROGRESS, REWORK, COMPLETED)';

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Auto-calculate duration
CREATE TRIGGER trg_process_data_calculate_duration
BEFORE INSERT OR UPDATE ON process_data
FOR EACH ROW
WHEN (NEW.completed_at IS NOT NULL)
EXECUTE FUNCTION calculate_process_duration();

-- Trigger: Validate process sequence
CREATE TRIGGER trg_process_data_validate_sequence
BEFORE INSERT ON process_data
FOR EACH ROW
EXECUTE FUNCTION validate_process_sequence();

-- Trigger: Update serial status based on process results
CREATE TRIGGER trg_process_data_update_serial_status
AFTER INSERT OR UPDATE ON process_data
FOR EACH ROW
EXECUTE FUNCTION update_serial_status_from_process();

-- Trigger: Audit logging
CREATE TRIGGER trg_process_data_audit
AFTER INSERT OR UPDATE OR DELETE ON process_data
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- PARTITIONING STRATEGY (Optional - for high-volume production environments)
-- =============================================================================
-- Note: Uncomment and modify based on actual data volume and retention requirements

/*
-- Convert table to partitioned table (by month)
-- This requires recreating the table, so should be done during initial setup

-- Create partitioned table
CREATE TABLE process_data_partitioned (
    LIKE process_data INCLUDING ALL
) PARTITION BY RANGE (started_at);

-- Create partitions for upcoming months
CREATE TABLE process_data_y2025m01 PARTITION OF process_data_partitioned
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE process_data_y2025m02 PARTITION OF process_data_partitioned
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE process_data_y2025m03 PARTITION OF process_data_partitioned
FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Continue creating partitions as needed...

-- Automated partition creation function
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    -- Calculate next month
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'process_data_y' || TO_CHAR(partition_date, 'YYYY') || 'm' || TO_CHAR(partition_date, 'MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';

    -- Check if partition already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relname = partition_name
    ) THEN
        -- Create new partition
        EXECUTE format('CREATE TABLE %I PARTITION OF process_data_partitioned FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date);

        RAISE NOTICE 'Created partition % for period % to %', partition_name, start_date, end_date;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly execution of partition creation (using pg_cron or external scheduler)
-- SELECT cron.schedule('create-monthly-partition', '0 0 1 * *', 'SELECT create_monthly_partition();');
*/

-- =============================================================================
-- SAMPLE DATA STRUCTURES (Documentation)
-- =============================================================================

/*
-- Example: LASER_MARKING process measurements
{
    "marking_quality": "GOOD",
    "readability_score": 0.98,
    "position_offset_mm": 0.05,
    "laser_power_actual": "19.8W",
    "marking_time_seconds": 58
}

-- Example: LMA_ASSEMBLY process measurements
{
    "components_installed": ["LMA_module", "connector", "screws"],
    "torque_applied_nm": 1.0,
    "alignment_offset_mm": 0.05,
    "visual_inspection": "PASS",
    "assembly_time_seconds": 175,
    "quality_check": "PASS"
}

-- Example: SENSOR_INSPECTION process measurements
{
    "sensor_channels_tested": 8,
    "signal_quality_avg": 0.92,
    "noise_level_db": -45,
    "calibration_offset": [0.01, -0.02, 0.00, 0.01, -0.01, 0.02, 0.00, -0.01],
    "baseline_values": [512, 510, 515, 508, 512, 514, 511, 509]
}

-- Example: Defects array structure
[
    {
        "defect_code": "E001",
        "defect_name": "Voltage out of range",
        "severity": "CRITICAL",
        "measured_value": 3.55,
        "expected_range": "3.2-3.4",
        "action_required": "REWORK"
    },
    {
        "defect_code": "E002",
        "defect_name": "High noise level",
        "severity": "MINOR",
        "measured_value": -38,
        "expected_value": "<-40",
        "action_required": "MONITOR"
    }
]
*/

-- =============================================================================
-- PERMISSIONS (Adjust based on your security requirements)
-- =============================================================================
-- GRANT SELECT, INSERT, UPDATE ON process_data TO mes_application;
-- GRANT SELECT ON process_data TO mes_readonly;
-- GRANT ALL ON SEQUENCE process_data_id_seq TO mes_application;

-- =============================================================================
-- END OF DDL SCRIPT
-- =============================================================================