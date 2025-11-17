-- =============================================================================
-- Process-Specific Views - Part 2 (4 views)
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Flatten JSONB measurement data for efficient querying of process-specific metrics
-- Views included:
--   5. v_robot_assembly_data - ROBOT_ASSEMBLY process measurements
--   6. v_performance_test_data - PERFORMANCE_TEST process measurements
--   7. v_label_printing_data - LABEL_PRINTING process measurements
--   8. v_packaging_inspection_data - PACKAGING_INSPECTION process measurements
-- =============================================================================
-- PostgreSQL Dialect
-- Created: 2025-11-18
-- =============================================================================

-- =============================================================================
-- VIEW 5: v_robot_assembly_data
-- =============================================================================
-- Purpose: Extract and flatten ROBOT_ASSEMBLY process measurements
-- Filter: process_code = 'ROBOT_ASSEMBLY'
-- Extracted fields:
--   - robot_components_installed (text[])
--   - motor_rotation_speed_rpm (int)
--   - motor_current_draw_ma (int)
--   - encoder_resolution_verified (int)
--   - torque_output_nm (float)
--   - functional_test_result (text)
--   - assembly_time_seconds (int)
-- =============================================================================

DROP VIEW IF EXISTS v_robot_assembly_data CASCADE;

CREATE VIEW v_robot_assembly_data AS
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
        SELECT jsonb_array_elements_text(pd.measurements->'robot_components_installed')
    ) AS robot_components_installed,
    (pd.measurements->>'motor_rotation_speed_rpm')::INTEGER AS motor_rotation_speed_rpm,
    (pd.measurements->>'motor_current_draw_ma')::INTEGER AS motor_current_draw_ma,
    (pd.measurements->>'encoder_resolution_verified')::INTEGER AS encoder_resolution_verified,
    (pd.measurements->>'torque_output_nm')::FLOAT AS torque_output_nm,
    pd.measurements->>'functional_test_result' AS functional_test_result,
    (pd.measurements->>'assembly_time_seconds')::INTEGER AS assembly_time_seconds,

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
    p.process_code = 'ROBOT_ASSEMBLY';

COMMENT ON VIEW v_robot_assembly_data IS 'Flattened view of ROBOT_ASSEMBLY process data with extracted JSONB measurements including robot components array and motor performance metrics';

-- =============================================================================
-- VIEW 6: v_performance_test_data
-- =============================================================================
-- Purpose: Extract and flatten PERFORMANCE_TEST process measurements
-- Filter: process_code = 'PERFORMANCE_TEST'
-- Extracted fields:
--   - response_time_ms (int)
--   - accuracy_percent (float)
--   - throughput_samples_per_sec (int)
--   - test_scenarios (jsonb) - Nested JSON with scenario test results
-- =============================================================================

DROP VIEW IF EXISTS v_performance_test_data CASCADE;

CREATE VIEW v_performance_test_data AS
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
    (pd.measurements->>'response_time_ms')::INTEGER AS response_time_ms,
    (pd.measurements->>'accuracy_percent')::FLOAT AS accuracy_percent,
    (pd.measurements->>'throughput_samples_per_sec')::INTEGER AS throughput_samples_per_sec,

    -- Keep test_scenarios as JSONB for flexible querying
    pd.measurements->'test_scenarios' AS test_scenarios,

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
    p.process_code = 'PERFORMANCE_TEST';

COMMENT ON VIEW v_performance_test_data IS 'Flattened view of PERFORMANCE_TEST process data with extracted JSONB measurements including response time, accuracy, throughput, and test scenario results';

-- =============================================================================
-- VIEW 7: v_label_printing_data
-- =============================================================================
-- Purpose: Extract and flatten LABEL_PRINTING process measurements
-- Filter: process_code = 'LABEL_PRINTING'
-- Extracted fields:
--   - label_type (text)
--   - resolution (text)
--   - verification_required (boolean)
--   - printing_time_seconds (int)
--   - label_quality (text)
-- =============================================================================

DROP VIEW IF EXISTS v_label_printing_data CASCADE;

CREATE VIEW v_label_printing_data AS
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
    pd.measurements->>'label_type' AS label_type,
    pd.measurements->>'resolution' AS resolution,
    (pd.measurements->>'verification_required')::BOOLEAN AS verification_required,
    (pd.measurements->>'printing_time_seconds')::INTEGER AS printing_time_seconds,
    pd.measurements->>'label_quality' AS label_quality,

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
    p.process_code = 'LABEL_PRINTING';

COMMENT ON VIEW v_label_printing_data IS 'Flattened view of LABEL_PRINTING process data with extracted JSONB measurements including label type, resolution, and quality verification';

-- =============================================================================
-- VIEW 8: v_packaging_inspection_data
-- =============================================================================
-- Purpose: Extract and flatten PACKAGING_INSPECTION process measurements
-- Filter: process_code = 'PACKAGING_INSPECTION'
-- Extracted fields:
--   - anti_static_bag (boolean)
--   - visual_defect_check (boolean)
--   - label_verification (boolean)
--   - packaging_time_seconds (int)
--   - inspection_result (text)
-- =============================================================================

DROP VIEW IF EXISTS v_packaging_inspection_data CASCADE;

CREATE VIEW v_packaging_inspection_data AS
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
    (pd.measurements->>'anti_static_bag')::BOOLEAN AS anti_static_bag,
    (pd.measurements->>'visual_defect_check')::BOOLEAN AS visual_defect_check,
    (pd.measurements->>'label_verification')::BOOLEAN AS label_verification,
    (pd.measurements->>'packaging_time_seconds')::INTEGER AS packaging_time_seconds,
    pd.measurements->>'inspection_result' AS inspection_result,

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
    p.process_code = 'PACKAGING_INSPECTION';

COMMENT ON VIEW v_packaging_inspection_data IS 'Flattened view of PACKAGING_INSPECTION process data with extracted JSONB measurements including anti-static bag, visual defect check, and label verification';

-- =============================================================================
-- USAGE EXAMPLES
-- =============================================================================

/*
-- Example 1: Robot assembly quality analysis - motor performance
SELECT
    serial_number,
    lot_number,
    robot_components_installed,
    motor_rotation_speed_rpm,
    motor_current_draw_ma,
    torque_output_nm,
    functional_test_result,
    operator_name,
    result
FROM v_robot_assembly_data
WHERE
    motor_rotation_speed_rpm NOT BETWEEN 950 AND 1050  -- Out of spec RPM
    OR motor_current_draw_ma > 550  -- Excessive current draw
    OR functional_test_result != 'PASS'
ORDER BY completed_at DESC;

-- Example 2: Performance test metrics summary by lot
SELECT
    lot_number,
    COUNT(*) AS total_tests,
    AVG(response_time_ms) AS avg_response_time_ms,
    AVG(accuracy_percent) AS avg_accuracy_percent,
    AVG(throughput_samples_per_sec) AS avg_throughput,
    MIN(response_time_ms) AS min_response_time_ms,
    MAX(response_time_ms) AS max_response_time_ms,
    SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) AS passed_tests,
    ROUND(
        100.0 * SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS pass_rate_percent
FROM v_performance_test_data
WHERE
    completed_at >= NOW() - INTERVAL '30 days'
GROUP BY lot_number
ORDER BY avg_accuracy_percent DESC;

-- Example 3: Performance test scenarios analysis
-- Unnest test_scenarios JSONB array to analyze individual scenario results
SELECT
    serial_number,
    lot_number,
    response_time_ms,
    accuracy_percent,
    scenario->>'scenario' AS scenario_name,
    scenario->>'result' AS scenario_result,
    completed_at
FROM v_performance_test_data,
LATERAL jsonb_array_elements(test_scenarios) AS scenario
WHERE
    scenario->>'result' != 'PASS'
ORDER BY completed_at DESC;

-- Example 4: Label printing quality by operator
SELECT
    operator_name,
    COUNT(*) AS total_labels,
    SUM(CASE WHEN label_quality = 'GOOD' THEN 1 ELSE 0 END) AS good_quality,
    SUM(CASE WHEN label_quality = 'FAIR' THEN 1 ELSE 0 END) AS fair_quality,
    SUM(CASE WHEN label_quality = 'POOR' THEN 1 ELSE 0 END) AS poor_quality,
    AVG(printing_time_seconds) AS avg_printing_time_sec,
    ROUND(
        100.0 * SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS pass_rate_percent
FROM v_label_printing_data
WHERE
    completed_at >= NOW() - INTERVAL '7 days'
GROUP BY operator_name
ORDER BY pass_rate_percent DESC;

-- Example 5: Packaging inspection failure analysis
SELECT
    serial_number,
    lot_number,
    anti_static_bag,
    visual_defect_check,
    label_verification,
    inspection_result,
    packaging_time_seconds,
    operator_name,
    completed_at,
    notes
FROM v_packaging_inspection_data
WHERE
    result = 'FAIL'
    OR anti_static_bag = FALSE
    OR visual_defect_check = FALSE
    OR label_verification = FALSE
ORDER BY completed_at DESC;

-- Example 6: Complete process flow analysis for a single serial
-- Join all process views to see complete production history
SELECT
    'ROBOT_ASSEMBLY' AS process,
    ra.serial_number,
    ra.completed_at,
    ra.result,
    ra.operator_name,
    ra.duration_seconds,
    ra.functional_test_result AS detail
FROM v_robot_assembly_data ra
WHERE ra.serial_number = 'NH-F2X-001-00001'

UNION ALL

SELECT
    'PERFORMANCE_TEST' AS process,
    pt.serial_number,
    pt.completed_at,
    pt.result,
    pt.operator_name,
    pt.duration_seconds,
    CONCAT('Accuracy: ', pt.accuracy_percent::TEXT, '%') AS detail
FROM v_performance_test_data pt
WHERE pt.serial_number = 'NH-F2X-001-00001'

UNION ALL

SELECT
    'LABEL_PRINTING' AS process,
    lp.serial_number,
    lp.completed_at,
    lp.result,
    lp.operator_name,
    lp.duration_seconds,
    lp.label_quality AS detail
FROM v_label_printing_data lp
WHERE lp.serial_number = 'NH-F2X-001-00001'

UNION ALL

SELECT
    'PACKAGING_INSPECTION' AS process,
    pi.serial_number,
    pi.completed_at,
    pi.result,
    pi.operator_name,
    pi.duration_seconds,
    pi.inspection_result AS detail
FROM v_packaging_inspection_data pi
WHERE pi.serial_number = 'NH-F2X-001-00001'

ORDER BY completed_at;

-- Example 7: Robot assembly component frequency analysis
-- Analyze which components are most commonly installed
SELECT
    component,
    COUNT(*) AS installation_count,
    COUNT(DISTINCT serial_number) AS unique_serials,
    SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) AS successful_installations
FROM v_robot_assembly_data,
LATERAL unnest(robot_components_installed) AS component
WHERE
    completed_at >= NOW() - INTERVAL '30 days'
GROUP BY component
ORDER BY installation_count DESC;

-- Example 8: Performance degradation over time
-- Detect if performance metrics are trending down
SELECT
    DATE_TRUNC('day', completed_at) AS test_date,
    COUNT(*) AS tests_performed,
    AVG(response_time_ms) AS avg_response_time,
    AVG(accuracy_percent) AS avg_accuracy,
    AVG(throughput_samples_per_sec) AS avg_throughput,
    STDDEV(response_time_ms) AS stddev_response_time,
    STDDEV(accuracy_percent) AS stddev_accuracy
FROM v_performance_test_data
WHERE
    completed_at >= NOW() - INTERVAL '90 days'
    AND result = 'PASS'
GROUP BY DATE_TRUNC('day', completed_at)
ORDER BY test_date DESC;

-- Example 9: Packaging inspection completion rate by shift
-- Analyze efficiency by time of day (assuming 3 shifts: 06:00-14:00, 14:00-22:00, 22:00-06:00)
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM completed_at) BETWEEN 6 AND 13 THEN 'Morning Shift (06:00-14:00)'
        WHEN EXTRACT(HOUR FROM completed_at) BETWEEN 14 AND 21 THEN 'Evening Shift (14:00-22:00)'
        ELSE 'Night Shift (22:00-06:00)'
    END AS shift,
    COUNT(*) AS total_inspections,
    AVG(packaging_time_seconds) AS avg_time_seconds,
    SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) AS passed,
    ROUND(
        100.0 * SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS pass_rate_percent
FROM v_packaging_inspection_data
WHERE
    completed_at >= NOW() - INTERVAL '7 days'
GROUP BY shift
ORDER BY pass_rate_percent DESC;

-- Example 10: Correlation analysis - Robot assembly vs Performance test
-- Identify if robot assembly metrics correlate with performance test results
SELECT
    ra.serial_number,
    ra.lot_number,
    ra.motor_rotation_speed_rpm,
    ra.motor_current_draw_ma,
    ra.torque_output_nm,
    ra.functional_test_result,
    pt.response_time_ms,
    pt.accuracy_percent,
    pt.throughput_samples_per_sec,
    ra.result AS assembly_result,
    pt.result AS performance_result,
    ra.operator_name AS assembly_operator,
    pt.operator_name AS test_operator
FROM v_robot_assembly_data ra
INNER JOIN v_performance_test_data pt ON ra.serial_number = pt.serial_number
WHERE
    ra.completed_at >= NOW() - INTERVAL '30 days'
ORDER BY ra.completed_at DESC;
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
- Array operations (robot_components_installed) may benefit from additional indexes

Execution plan analysis example:
EXPLAIN ANALYZE
SELECT * FROM v_robot_assembly_data
WHERE motor_rotation_speed_rpm > 1050
LIMIT 100;

Expected query patterns:
- Robot Assembly: Motor performance analysis, component tracking
- Performance Test: Response time trends, accuracy monitoring, scenario analysis
- Label Printing: Quality tracking by operator, time analysis
- Packaging Inspection: Defect identification, final quality gate
*/

-- =============================================================================
-- MATERIALIZED VIEW ALTERNATIVES (For high-performance scenarios)
-- =============================================================================
/*
If query performance becomes critical for analytics/reporting, consider
converting to materialized views:

-- Create materialized view for robot assembly
CREATE MATERIALIZED VIEW mv_robot_assembly_data AS
SELECT * FROM v_robot_assembly_data;

-- Create indexes on materialized view
CREATE INDEX idx_mv_robot_assembly_serial ON mv_robot_assembly_data(serial_number);
CREATE INDEX idx_mv_robot_assembly_lot ON mv_robot_assembly_data(lot_number);
CREATE INDEX idx_mv_robot_assembly_rpm ON mv_robot_assembly_data(motor_rotation_speed_rpm);
CREATE INDEX idx_mv_robot_assembly_result ON mv_robot_assembly_data(result);

-- Create materialized view for performance test
CREATE MATERIALIZED VIEW mv_performance_test_data AS
SELECT * FROM v_performance_test_data;

CREATE INDEX idx_mv_performance_test_serial ON mv_performance_test_data(serial_number);
CREATE INDEX idx_mv_performance_test_accuracy ON mv_performance_test_data(accuracy_percent);
CREATE INDEX idx_mv_performance_test_response ON mv_performance_test_data(response_time_ms);

-- Refresh strategies:
-- 1. Scheduled refresh (hourly/daily based on reporting needs):
--    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_robot_assembly_data;
--    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_performance_test_data;
--
-- 2. Trigger-based refresh on process_data INSERT/UPDATE:
--    CREATE TRIGGER refresh_mv_on_robot_assembly ...
--
-- 3. Manual refresh for ad-hoc analysis:
--    REFRESH MATERIALIZED VIEW mv_robot_assembly_data;

Trade-offs:
- Materialized views: Faster queries, stale data, storage overhead
- Regular views: Real-time data, slower complex queries, no storage overhead
*/

-- =============================================================================
-- INDEX RECOMMENDATIONS FOR HEAVY ANALYTICAL WORKLOADS
-- =============================================================================
/*
If these views are used heavily in analytics, consider adding these indexes:

-- Index on process_data for robot assembly queries
CREATE INDEX idx_process_data_robot_assembly
ON process_data(process_id, serial_id)
WHERE process_id = (SELECT id FROM processes WHERE process_code = 'ROBOT_ASSEMBLY');

-- Index on process_data for performance test queries
CREATE INDEX idx_process_data_performance_test
ON process_data(process_id, completed_at)
WHERE process_id = (SELECT id FROM processes WHERE process_code = 'PERFORMANCE_TEST');

-- JSONB specific indexes for frequently queried fields
CREATE INDEX idx_measurements_motor_rpm
ON process_data ((measurements->>'motor_rotation_speed_rpm'))
WHERE process_id = (SELECT id FROM processes WHERE process_code = 'ROBOT_ASSEMBLY');

CREATE INDEX idx_measurements_accuracy
ON process_data ((measurements->>'accuracy_percent'))
WHERE process_id = (SELECT id FROM processes WHERE process_code = 'PERFORMANCE_TEST');

-- Composite index for time-series queries
CREATE INDEX idx_process_data_completed_result
ON process_data(completed_at, result, process_id);

Note: Add these indexes only if query performance analysis (EXPLAIN ANALYZE)
shows they would be beneficial. Monitor index usage with pg_stat_user_indexes.
*/

-- =============================================================================
-- DATA QUALITY CHECKS
-- =============================================================================
/*
These queries can be used to validate data quality in the process views:

-- Check for missing required measurements in robot assembly
SELECT
    serial_number,
    lot_number,
    CASE WHEN robot_components_installed IS NULL THEN 'components' END,
    CASE WHEN motor_rotation_speed_rpm IS NULL THEN 'rpm' END,
    CASE WHEN torque_output_nm IS NULL THEN 'torque' END
FROM v_robot_assembly_data
WHERE
    robot_components_installed IS NULL
    OR motor_rotation_speed_rpm IS NULL
    OR torque_output_nm IS NULL;

-- Check for out-of-range performance test values
SELECT
    serial_number,
    response_time_ms,
    accuracy_percent,
    throughput_samples_per_sec
FROM v_performance_test_data
WHERE
    response_time_ms < 0 OR response_time_ms > 1000
    OR accuracy_percent < 0 OR accuracy_percent > 100
    OR throughput_samples_per_sec < 0;

-- Check for inconsistent packaging inspection data
SELECT
    serial_number,
    anti_static_bag,
    visual_defect_check,
    label_verification,
    result
FROM v_packaging_inspection_data
WHERE
    result = 'PASS'
    AND (
        anti_static_bag = FALSE
        OR visual_defect_check = FALSE
        OR label_verification = FALSE
    );
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================
