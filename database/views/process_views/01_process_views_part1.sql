-- =============================================================================
-- Process-Specific Views - Part 1 (4 views)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Flatten JSONB measurement data for efficient querying of process-specific metrics
-- Views included:
--   1. v_laser_marking_data - LASER_MARKING process measurements
--   2. v_lma_assembly_data - LMA_ASSEMBLY process measurements
--   3. v_sensor_inspection_data - SENSOR_INSPECTION process measurements
--   4. v_firmware_upload_data - FIRMWARE_UPLOAD process measurements
-- =============================================================================
-- PostgreSQL Dialect
-- Created: 2025-11-18
-- =============================================================================

-- =============================================================================
-- VIEW 1: v_laser_marking_data
-- =============================================================================
-- Purpose: Extract and flatten LASER_MARKING process measurements
-- Filter: process_code = 'LASER_MARKING'
-- Extracted fields:
--   - marking_quality (text)
--   - readability_score (float)
--   - position_offset_mm (float)
--   - laser_power_actual (text)
--   - marking_time_seconds (int)
-- =============================================================================

DROP VIEW IF EXISTS v_laser_marking_data CASCADE;

CREATE VIEW v_laser_marking_data AS
SELECT
    -- Process data core fields
    pd.id,
    s.serial_number,
    l.lot_number,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name AS operator_name,

    -- Extracted JSONB measurements
    pd.measurements->>'marking_quality' AS marking_quality,
    (pd.measurements->>'readability_score')::FLOAT AS readability_score,
    (pd.measurements->>'position_offset_mm')::FLOAT AS position_offset_mm,
    pd.measurements->>'laser_power_actual' AS laser_power_actual,
    (pd.measurements->>'marking_time_seconds')::INTEGER AS marking_time_seconds,

    -- Additional context
    pd.notes,
    p.process_name_ko,
    p.process_name_en,
    pd.created_at
FROM
    process_data pd
    INNER JOIN processes p ON pd.process_id = p.id
    INNER JOIN lots l ON pd.lot_id = l.id
    LEFT JOIN serials s ON pd.serial_id = s.id
    INNER JOIN users u ON pd.operator_id = u.id
WHERE
    p.process_code = 'LASER_MARKING';

COMMENT ON VIEW v_laser_marking_data IS 'Flattened view of LASER_MARKING process data with extracted JSONB measurements';

-- =============================================================================
-- VIEW 2: v_lma_assembly_data
-- =============================================================================
-- Purpose: Extract and flatten LMA_ASSEMBLY process measurements
-- Filter: process_code = 'LMA_ASSEMBLY'
-- Extracted fields:
--   - components_installed (text[])
--   - torque_applied_nm (float)
--   - alignment_offset_mm (float)
--   - visual_inspection (text)
--   - assembly_time_seconds (int)
--   - quality_check (text)
-- =============================================================================

DROP VIEW IF EXISTS v_lma_assembly_data CASCADE;

CREATE VIEW v_lma_assembly_data AS
SELECT
    -- Process data core fields
    pd.id,
    s.serial_number,
    l.lot_number,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name AS operator_name,

    -- Extracted JSONB measurements
    -- Convert JSON array to PostgreSQL text array
    ARRAY(
        SELECT jsonb_array_elements_text(pd.measurements->'components_installed')
    ) AS components_installed,
    (pd.measurements->>'torque_applied_nm')::FLOAT AS torque_applied_nm,
    (pd.measurements->>'alignment_offset_mm')::FLOAT AS alignment_offset_mm,
    pd.measurements->>'visual_inspection' AS visual_inspection,
    (pd.measurements->>'assembly_time_seconds')::INTEGER AS assembly_time_seconds,
    pd.measurements->>'quality_check' AS quality_check,

    -- Additional context
    pd.notes,
    p.process_name_ko,
    p.process_name_en,
    pd.created_at
FROM
    process_data pd
    INNER JOIN processes p ON pd.process_id = p.id
    INNER JOIN lots l ON pd.lot_id = l.id
    LEFT JOIN serials s ON pd.serial_id = s.id
    INNER JOIN users u ON pd.operator_id = u.id
WHERE
    p.process_code = 'LMA_ASSEMBLY';

COMMENT ON VIEW v_lma_assembly_data IS 'Flattened view of LMA_ASSEMBLY process data with extracted JSONB measurements including components array';

-- =============================================================================
-- VIEW 3: v_sensor_inspection_data
-- =============================================================================
-- Purpose: Extract and flatten SENSOR_INSPECTION process measurements
-- Filter: process_code = 'SENSOR_INSPECTION'
-- Extracted fields:
--   - sensor_channels_tested (int)
--   - signal_quality_avg (float)
--   - noise_level_db (float)
--   - calibration_offset (float[])
--   - baseline_values (int[])
-- =============================================================================

DROP VIEW IF EXISTS v_sensor_inspection_data CASCADE;

CREATE VIEW v_sensor_inspection_data AS
SELECT
    -- Process data core fields
    pd.id,
    s.serial_number,
    l.lot_number,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name AS operator_name,

    -- Extracted JSONB measurements
    (pd.measurements->>'sensor_channels_tested')::INTEGER AS sensor_channels_tested,
    (pd.measurements->>'signal_quality_avg')::FLOAT AS signal_quality_avg,
    (pd.measurements->>'noise_level_db')::FLOAT AS noise_level_db,

    -- Convert JSON arrays to PostgreSQL arrays
    ARRAY(
        SELECT (jsonb_array_elements(pd.measurements->'calibration_offset'))::TEXT::FLOAT
    ) AS calibration_offset,
    ARRAY(
        SELECT (jsonb_array_elements(pd.measurements->'baseline_values'))::TEXT::INTEGER
    ) AS baseline_values,

    -- Additional context
    pd.notes,
    p.process_name_ko,
    p.process_name_en,
    pd.created_at
FROM
    process_data pd
    INNER JOIN processes p ON pd.process_id = p.id
    INNER JOIN lots l ON pd.lot_id = l.id
    LEFT JOIN serials s ON pd.serial_id = s.id
    INNER JOIN users u ON pd.operator_id = u.id
WHERE
    p.process_code = 'SENSOR_INSPECTION';

COMMENT ON VIEW v_sensor_inspection_data IS 'Flattened view of SENSOR_INSPECTION process data with extracted JSONB measurements including calibration and baseline arrays';

-- =============================================================================
-- VIEW 4: v_firmware_upload_data
-- =============================================================================
-- Purpose: Extract and flatten FIRMWARE_UPLOAD process measurements
-- Filter: process_code = 'FIRMWARE_UPLOAD'
-- Extracted fields:
--   - firmware_version (text)
--   - checksum (text)
--   - upload_duration_seconds (int)
--   - verification_passed (boolean)
--   - device_id (text)
-- =============================================================================

DROP VIEW IF EXISTS v_firmware_upload_data CASCADE;

CREATE VIEW v_firmware_upload_data AS
SELECT
    -- Process data core fields
    pd.id,
    s.serial_number,
    l.lot_number,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name AS operator_name,

    -- Extracted JSONB measurements
    pd.measurements->>'firmware_version' AS firmware_version,
    pd.measurements->>'checksum' AS checksum,
    (pd.measurements->>'upload_duration_seconds')::INTEGER AS upload_duration_seconds,
    (pd.measurements->>'verification_passed')::BOOLEAN AS verification_passed,
    pd.measurements->>'device_id' AS device_id,

    -- Additional context
    pd.notes,
    p.process_name_ko,
    p.process_name_en,
    pd.created_at
FROM
    process_data pd
    INNER JOIN processes p ON pd.process_id = p.id
    INNER JOIN lots l ON pd.lot_id = l.id
    LEFT JOIN serials s ON pd.serial_id = s.id
    INNER JOIN users u ON pd.operator_id = u.id
WHERE
    p.process_code = 'FIRMWARE_UPLOAD';

COMMENT ON VIEW v_firmware_upload_data IS 'Flattened view of FIRMWARE_UPLOAD process data with extracted JSONB measurements';

-- =============================================================================
-- USAGE EXAMPLES
-- =============================================================================

/*
-- Example 1: Query laser marking data with quality filters
SELECT
    serial_number,
    lot_number,
    marking_quality,
    readability_score,
    position_offset_mm,
    operator_name,
    completed_at
FROM v_laser_marking_data
WHERE
    readability_score < 0.95  -- Quality threshold
    AND result = 'PASS'
ORDER BY completed_at DESC;

-- Example 2: LMA assembly component analysis
SELECT
    lot_number,
    components_installed,
    torque_applied_nm,
    visual_inspection,
    quality_check,
    operator_name
FROM v_lma_assembly_data
WHERE
    torque_applied_nm NOT BETWEEN 0.8 AND 1.2  -- Out of spec torque
    OR visual_inspection != 'PASS'
ORDER BY started_at DESC;

-- Example 3: Sensor inspection - channel quality analysis
SELECT
    serial_number,
    sensor_channels_tested,
    signal_quality_avg,
    noise_level_db,
    calibration_offset,
    baseline_values,
    result
FROM v_sensor_inspection_data
WHERE
    signal_quality_avg < 0.85  -- Below threshold
    OR noise_level_db > -40    -- Too much noise
ORDER BY signal_quality_avg ASC;

-- Example 4: Firmware upload success rate by version
SELECT
    firmware_version,
    COUNT(*) AS total_uploads,
    SUM(CASE WHEN verification_passed THEN 1 ELSE 0 END) AS successful_uploads,
    ROUND(
        100.0 * SUM(CASE WHEN verification_passed THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS success_rate_percent,
    AVG(upload_duration_seconds) AS avg_upload_time_seconds
FROM v_firmware_upload_data
GROUP BY firmware_version
ORDER BY firmware_version DESC;

-- Example 5: Join laser marking with assembly for defect correlation
SELECT
    lm.serial_number,
    lm.lot_number,
    lm.marking_quality,
    lm.readability_score,
    la.torque_applied_nm,
    la.visual_inspection,
    lm.operator_name AS laser_operator,
    la.operator_name AS assembly_operator
FROM v_laser_marking_data lm
INNER JOIN v_lma_assembly_data la ON lm.serial_number = la.serial_number
WHERE
    lm.result = 'FAIL'
    OR la.result = 'FAIL'
ORDER BY lm.started_at DESC;

-- Example 6: Time-series analysis of sensor quality by lot
SELECT
    lot_number,
    DATE_TRUNC('hour', completed_at) AS hour_bucket,
    COUNT(*) AS inspections_count,
    AVG(signal_quality_avg) AS avg_signal_quality,
    AVG(noise_level_db) AS avg_noise_level,
    MIN(signal_quality_avg) AS min_signal_quality,
    MAX(signal_quality_avg) AS max_signal_quality
FROM v_sensor_inspection_data
WHERE
    completed_at >= NOW() - INTERVAL '7 days'
    AND result = 'PASS'
GROUP BY lot_number, DATE_TRUNC('hour', completed_at)
ORDER BY hour_bucket DESC, lot_number;
*/

-- =============================================================================
-- PERFORMANCE OPTIMIZATION NOTES
-- =============================================================================
/*
These views leverage existing GIN indexes on process_data.measurements for
efficient JSONB queries. The following indexes are already in place:

1. idx_process_data_measurements (GIN on measurements JSONB column)
2. idx_process_data_process (on process_id)
3. idx_process_data_serial_process (composite on serial_id, process_id, result)

For optimal query performance:
- Filter by process_code is resolved via process_id index
- JSONB field extraction benefits from GIN index
- JOIN operations use existing foreign key indexes
- Consider adding materialized views if query latency becomes an issue

Example execution plan analysis:
EXPLAIN ANALYZE
SELECT * FROM v_laser_marking_data
WHERE readability_score < 0.95
LIMIT 100;
*/

-- =============================================================================
-- MATERIALIZED VIEW ALTERNATIVES (For high-performance scenarios)
-- =============================================================================
/*
If query performance becomes critical, consider converting to materialized views:

-- Create materialized view
CREATE MATERIALIZED VIEW mv_laser_marking_data AS
SELECT * FROM v_laser_marking_data;

-- Create indexes on materialized view
CREATE INDEX idx_mv_laser_marking_serial ON mv_laser_marking_data(serial_number);
CREATE INDEX idx_mv_laser_marking_lot ON mv_laser_marking_data(lot_number);
CREATE INDEX idx_mv_laser_marking_quality ON mv_laser_marking_data(readability_score);

-- Refresh strategy (choose one):
-- 1. Manual refresh: REFRESH MATERIALIZED VIEW mv_laser_marking_data;
-- 2. Scheduled refresh: Use pg_cron or application scheduler
-- 3. Trigger-based: Create triggers on process_data to refresh selectively

-- Concurrent refresh (allows queries during refresh):
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_laser_marking_data;
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================
