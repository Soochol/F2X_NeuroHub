-- =============================================================================
-- DDL Script: wip_process_history (WIP Process Execution History)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Track detailed process execution history for WIP items during
--          manufacturing processes 1-6. This table captures all process
--          attempts, measurements, defects, and timing information for
--          WIP-level traceability before serial number generation.
--
-- Key Features:
--   - WIP-based process tracking (processes 1-6)
--   - JSONB storage for flexible measurement and defect data
--   - Complete timing information (start, completion, duration)
--   - Barcode scan timestamp tracking
--   - Operator and equipment attribution
--   - Support for rework attempts
--
-- Relationship:
--   - Complements process_data table (which handles serial-level tracking)
--   - Migrates to process_data history after WIP → Serial transition
--
-- Dependencies:
--   - wip_items (foreign key)
--   - processes (foreign key)
--   - users (foreign key for operator)
--   - equipment (foreign key, nullable)
-- =============================================================================

-- Drop table if exists (for development only)
DROP TABLE IF EXISTS wip_process_history CASCADE;

-- =============================================================================
-- TABLE CREATION
-- =============================================================================
CREATE TABLE wip_process_history (
    -- Primary key
    id BIGSERIAL NOT NULL,

    -- Foreign keys
    wip_item_id BIGINT NOT NULL,                      -- WIP item reference
    process_id BIGINT NOT NULL,                       -- Process reference
    operator_id BIGINT NOT NULL,                      -- Operator who performed the work
    equipment_id BIGINT,                              -- Equipment used (nullable)

    -- Process execution result
    result VARCHAR(10) NOT NULL,                      -- PASS, FAIL, REWORK

    -- Process-specific data (JSONB for flexibility)
    measurements JSONB DEFAULT '{}',                  -- Process measurement data
    defects JSONB DEFAULT '[]',                       -- Defect information array

    -- Additional information
    notes TEXT,                                       -- Operator notes or observations
    rework_reason TEXT,                               -- Reason for rework (if applicable)

    -- Timing information
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,     -- Process start timestamp
    completed_at TIMESTAMP WITH TIME ZONE,            -- Process completion timestamp
    duration_seconds INTEGER,                         -- Calculated duration
    scan_timestamp TIMESTAMP WITH TIME ZONE,          -- Barcode scan timestamp

    -- Record metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()  -- Record creation timestamp
);

-- =============================================================================
-- COMMENT DOCUMENTATION
-- =============================================================================
COMMENT ON TABLE wip_process_history IS
'Process execution history for WIP items (processes 1-6). Tracks all process attempts,
measurements, defects, and timing information with WIP-level granularity before serial
number generation at process 7.';

COMMENT ON COLUMN wip_process_history.id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN wip_process_history.wip_item_id IS 'Foreign key to wip_items table';
COMMENT ON COLUMN wip_process_history.process_id IS 'Foreign key to processes table';
COMMENT ON COLUMN wip_process_history.operator_id IS 'Foreign key to users table (operator who performed the work)';
COMMENT ON COLUMN wip_process_history.equipment_id IS 'Foreign key to equipment table (equipment used for this process, nullable)';
COMMENT ON COLUMN wip_process_history.result IS 'Process execution result: PASS (successful), FAIL (quality failure), REWORK (retry after failure)';
COMMENT ON COLUMN wip_process_history.measurements IS 'Process-specific measurement data in JSONB format (flexible schema per process)';
COMMENT ON COLUMN wip_process_history.defects IS 'Array of defect information in JSONB format (populated when result = FAIL)';
COMMENT ON COLUMN wip_process_history.notes IS 'Additional operator notes or observations';
COMMENT ON COLUMN wip_process_history.rework_reason IS 'Reason for rework attempt (if this is a rework record)';
COMMENT ON COLUMN wip_process_history.started_at IS 'Process start timestamp';
COMMENT ON COLUMN wip_process_history.completed_at IS 'Process completion timestamp';
COMMENT ON COLUMN wip_process_history.duration_seconds IS 'Calculated process duration in seconds';
COMMENT ON COLUMN wip_process_history.scan_timestamp IS 'Timestamp when WIP barcode was scanned at process station';
COMMENT ON COLUMN wip_process_history.created_at IS 'Record creation timestamp (auto-set)';

-- =============================================================================
-- PRIMARY KEY CONSTRAINT
-- =============================================================================
ALTER TABLE wip_process_history
ADD CONSTRAINT pk_wip_process_history PRIMARY KEY (id);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================
-- Foreign key to wip_items table
ALTER TABLE wip_process_history
ADD CONSTRAINT fk_wip_process_history_wip
FOREIGN KEY (wip_item_id)
REFERENCES wip_items(id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Foreign key to processes table
ALTER TABLE wip_process_history
ADD CONSTRAINT fk_wip_process_history_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to users table (operator)
ALTER TABLE wip_process_history
ADD CONSTRAINT fk_wip_process_history_operator
FOREIGN KEY (operator_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key to equipment table (nullable)
ALTER TABLE wip_process_history
ADD CONSTRAINT fk_wip_process_history_equipment
FOREIGN KEY (equipment_id)
REFERENCES equipment(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- =============================================================================
-- CHECK CONSTRAINTS
-- =============================================================================
-- Result validation
ALTER TABLE wip_process_history
ADD CONSTRAINT chk_wip_process_history_result
CHECK (result IN ('PASS', 'FAIL', 'REWORK'));

-- Duration must be non-negative if set
ALTER TABLE wip_process_history
ADD CONSTRAINT chk_wip_process_history_duration
CHECK (duration_seconds IS NULL OR duration_seconds >= 0);

-- Completed timestamp must be after started timestamp
ALTER TABLE wip_process_history
ADD CONSTRAINT chk_wip_process_history_timestamps
CHECK (completed_at IS NULL OR completed_at >= started_at);

-- =============================================================================
-- INDEXES
-- =============================================================================
-- Foreign key indexes (for join performance)
CREATE INDEX idx_wip_process_history_wip
ON wip_process_history(wip_item_id);

CREATE INDEX idx_wip_process_history_process
ON wip_process_history(process_id);

CREATE INDEX idx_wip_process_history_operator
ON wip_process_history(operator_id);

CREATE INDEX idx_wip_process_history_equipment
ON wip_process_history(equipment_id)
WHERE equipment_id IS NOT NULL;

-- Composite index for WIP traceability queries
CREATE INDEX idx_wip_process_history_wip_process
ON wip_process_history(wip_item_id, process_id, started_at DESC);

-- Result-based filtering (quality analysis)
CREATE INDEX idx_wip_process_history_result
ON wip_process_history(result, process_id);

-- Failed processes analysis
CREATE INDEX idx_wip_process_history_failed
ON wip_process_history(process_id, started_at DESC)
WHERE result = 'FAIL';

-- Time-based queries (for production analytics)
CREATE INDEX idx_wip_process_history_started_at
ON wip_process_history(started_at DESC);

CREATE INDEX idx_wip_process_history_completed_at
ON wip_process_history(completed_at DESC)
WHERE completed_at IS NOT NULL;

-- Scan timestamp tracking
CREATE INDEX idx_wip_process_history_scan_timestamp
ON wip_process_history(scan_timestamp DESC)
WHERE scan_timestamp IS NOT NULL;

-- GIN indexes for JSONB columns (enables efficient JSON queries)
CREATE INDEX idx_wip_process_history_measurements
ON wip_process_history USING gin(measurements);

CREATE INDEX idx_wip_process_history_defects
ON wip_process_history USING gin(defects);

-- Operator performance analysis
CREATE INDEX idx_wip_process_history_operator_performance
ON wip_process_history(operator_id, process_id, result, started_at DESC);

-- Equipment utilization tracking
CREATE INDEX idx_wip_process_history_equipment_utilization
ON wip_process_history(equipment_id, process_id, started_at DESC)
WHERE equipment_id IS NOT NULL;

-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: calculate_wip_process_duration()
-- Purpose: Automatically calculate duration_seconds from timestamps
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION calculate_wip_process_duration()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate duration if completed_at is set
    IF NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_wip_process_duration() IS
'Automatically calculates duration_seconds from started_at and completed_at timestamps
for WIP process history records.';

-- -----------------------------------------------------------------------------
-- Function: update_wip_current_process()
-- Purpose: Update wip_items.current_process_id when process is executed
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_wip_current_process()
RETURNS TRIGGER AS $$
BEGIN
    -- Update WIP item's current process location
    UPDATE wip_items
    SET
        current_process_id = NEW.process_id,
        status = CASE
            WHEN NEW.result = 'FAIL' THEN 'FAILED'
            WHEN NEW.result IN ('PASS', 'REWORK') THEN 'IN_PROGRESS'
            ELSE status
        END,
        updated_at = NOW()
    WHERE id = NEW.wip_item_id;

    RAISE NOTICE 'Updated WIP item % with process % result: %',
        NEW.wip_item_id, NEW.process_id, NEW.result;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_wip_current_process() IS
'Updates wip_items.current_process_id and status when a process is executed.
Automatically adjusts WIP status based on process result (PASS/FAIL/REWORK).';

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-calculate duration
CREATE TRIGGER trg_wip_process_history_calculate_duration
BEFORE INSERT OR UPDATE ON wip_process_history
FOR EACH ROW
WHEN (NEW.completed_at IS NOT NULL)
EXECUTE FUNCTION calculate_wip_process_duration();

-- Update WIP current process location
CREATE TRIGGER trg_wip_process_history_update_wip
AFTER INSERT ON wip_process_history
FOR EACH ROW
EXECUTE FUNCTION update_wip_current_process();

-- Audit logging trigger
CREATE TRIGGER trg_wip_process_history_audit
AFTER INSERT OR UPDATE OR DELETE ON wip_process_history
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- PARTITIONING STRATEGY (Optional - for high-volume production environments)
-- =============================================================================
-- Note: Uncomment and configure based on data volume and retention requirements
-- Consider partitioning by started_at (monthly) if expecting >1M records/month

/*
-- Example: Monthly partitioning by started_at
CREATE TABLE wip_process_history_partitioned (
    LIKE wip_process_history INCLUDING ALL
) PARTITION BY RANGE (started_at);

-- Create partitions for upcoming months
CREATE TABLE wip_process_history_y2025m01 PARTITION OF wip_process_history_partitioned
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE wip_process_history_y2025m02 PARTITION OF wip_process_history_partitioned
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Automated partition creation function
CREATE OR REPLACE FUNCTION create_wip_history_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'wip_process_history_y' || TO_CHAR(partition_date, 'YYYY') || 'm' || TO_CHAR(partition_date, 'MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';

    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = partition_name) THEN
        EXECUTE format('CREATE TABLE %I PARTITION OF wip_process_history_partitioned FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date);
        RAISE NOTICE 'Created partition % for period % to %', partition_name, start_date, end_date;
    END IF;
END;
$$ LANGUAGE plpgsql;
*/

-- =============================================================================
-- SAMPLE DATA STRUCTURES (Documentation)
-- =============================================================================

/*
-- Example: LASER_MARKING measurements (Process 1)
{
    "marking_quality": "GOOD",
    "readability_score": 0.98,
    "position_offset_mm": 0.05,
    "laser_power_actual": "19.8W",
    "marking_time_seconds": 58
}

-- Example: LMA_ASSEMBLY measurements (Process 2)
{
    "components_installed": ["LMA_module", "connector", "screws"],
    "torque_applied_nm": 1.0,
    "alignment_offset_mm": 0.05,
    "visual_inspection": "PASS",
    "assembly_time_seconds": 175
}

-- Example: SENSOR_INSPECTION measurements (Process 3)
{
    "sensor_channels_tested": 8,
    "signal_quality_avg": 0.92,
    "noise_level_db": -45,
    "calibration_offset": [0.01, -0.02, 0.00, 0.01],
    "baseline_values": [512, 510, 515, 508]
}

-- Example: Defects array (when result = FAIL)
[
    {
        "defect_code": "WIP-E001",
        "defect_name": "Poor laser marking quality",
        "severity": "CRITICAL",
        "measured_value": 0.65,
        "expected_value": ">0.85",
        "action_required": "REWORK",
        "detected_by": "optical_scanner"
    },
    {
        "defect_code": "WIP-E002",
        "defect_name": "Component misalignment",
        "severity": "MAJOR",
        "measured_offset_mm": 0.45,
        "tolerance_mm": 0.20,
        "action_required": "REWORK"
    }
]
*/

-- =============================================================================
-- VERIFICATION QUERIES (For testing)
-- =============================================================================

/*
-- Get complete process history for a WIP item
SELECT
    wph.id,
    p.process_code,
    p.process_name_en,
    wph.result,
    wph.started_at,
    wph.completed_at,
    wph.duration_seconds,
    u.username as operator,
    e.equipment_name
FROM wip_process_history wph
JOIN processes p ON wph.process_id = p.id
JOIN users u ON wph.operator_id = u.id
LEFT JOIN equipment e ON wph.equipment_id = e.id
WHERE wph.wip_item_id = 1
ORDER BY wph.started_at;

-- Analyze process failure rates
SELECT
    p.process_code,
    p.process_name_en,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE wph.result = 'PASS') as pass_count,
    COUNT(*) FILTER (WHERE wph.result = 'FAIL') as fail_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE wph.result = 'FAIL') / COUNT(*), 2) as failure_rate_pct
FROM wip_process_history wph
JOIN processes p ON wph.process_id = p.id
WHERE wph.started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.id, p.process_code, p.process_name_en
ORDER BY failure_rate_pct DESC;

-- Operator performance analysis
SELECT
    u.username,
    p.process_code,
    COUNT(*) as processes_executed,
    AVG(wph.duration_seconds) as avg_duration_sec,
    COUNT(*) FILTER (WHERE wph.result = 'FAIL') as failures,
    ROUND(100.0 * COUNT(*) FILTER (WHERE wph.result = 'PASS') / COUNT(*), 2) as pass_rate_pct
FROM wip_process_history wph
JOIN users u ON wph.operator_id = u.id
JOIN processes p ON wph.process_id = p.id
WHERE wph.started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.username, p.process_code
ORDER BY u.username, p.process_code;

-- Equipment utilization tracking
SELECT
    e.equipment_name,
    p.process_code,
    COUNT(*) as operations_count,
    AVG(wph.duration_seconds) as avg_duration_sec,
    MIN(wph.started_at) as first_use,
    MAX(wph.started_at) as last_use
FROM wip_process_history wph
JOIN equipment e ON wph.equipment_id = e.id
JOIN processes p ON wph.process_id = p.id
WHERE wph.started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY e.equipment_name, p.process_code
ORDER BY e.equipment_name, p.process_code;
*/

-- =============================================================================
-- END OF DDL SCRIPT
-- =============================================================================
