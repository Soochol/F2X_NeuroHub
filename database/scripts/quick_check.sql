-- =============================================================================
-- Quick Database Status Check
-- =============================================================================
-- Purpose: Fast verification of key deployment components
-- Usage: psql -U postgres -d f2x_neurohub_mes -f quick_check.sql
-- =============================================================================

\set QUIET on
\pset border 2
\pset format wrapped

\echo ''
\echo '========================================================================='
\echo 'F2X NeuroHub MES Database - Quick Status Check'
\echo '========================================================================='
\echo ''

-- Database Info
SELECT
    current_database() AS "Database",
    current_user AS "User",
    NOW() AS "Check Time";

\echo ''
\echo '--- Component Status ---'

-- Create summary table
WITH status_summary AS (
    -- Functions
    SELECT 'Functions' AS component,
           (SELECT COUNT(*) FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            AND p.proname IN ('update_timestamp', 'log_audit_event', 'prevent_audit_modification',
                              'prevent_process_deletion', 'prevent_user_deletion', 'generate_lot_number',
                              'validate_lot_status_transition', 'auto_close_lot', 'generate_serial_number',
                              'validate_lot_capacity', 'validate_serial_status_transition',
                              'update_lot_quantities', 'calculate_process_duration', 'validate_process_sequence')
           ) AS actual,
           14 AS expected

    UNION ALL

    -- Tables
    SELECT 'Tables' AS component,
           (SELECT COUNT(*) FROM pg_class c
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = 'public'
            AND c.relkind IN ('r', 'p')
            AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
           ) AS actual,
           7 AS expected

    UNION ALL

    -- Primary Keys
    SELECT 'Primary Keys' AS component,
           (SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE constraint_type = 'PRIMARY KEY'
            AND table_schema = 'public'
            AND table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
           ) AS actual,
           7 AS expected

    UNION ALL

    -- Foreign Keys
    SELECT 'Foreign Keys' AS component,
           (SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_schema = 'public'
            AND table_name IN ('lots', 'serials', 'process_data', 'audit_logs')
           ) AS actual,
           7 AS expected

    UNION ALL

    -- Indexes
    SELECT 'Indexes' AS component,
           (SELECT COUNT(*) FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
           ) AS actual,
           50 AS expected

    UNION ALL

    -- Triggers
    SELECT 'Triggers' AS component,
           (SELECT COUNT(*) FROM pg_trigger t
            JOIN pg_class c ON t.tgrelid = c.oid
            WHERE NOT t.tgisinternal
            AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
           ) AS actual,
           20 AS expected

    UNION ALL

    -- Processes Master Data
    SELECT 'Processes (Master Data)' AS component,
           (SELECT COUNT(*) FROM processes
            WHERE process_code IN ('LASER_MARKING', 'LMA_ASSEMBLY', 'SENSOR_INSPECTION',
                                  'FIRMWARE_UPLOAD', 'ROBOT_ASSEMBLY', 'PERFORMANCE_TEST',
                                  'LABEL_PRINTING', 'PACKAGING_INSPECTION')
           ) AS actual,
           8 AS expected

    UNION ALL

    -- Audit Partitions
    SELECT 'Audit Log Partitions' AS component,
           (SELECT COUNT(*) FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename LIKE 'audit_logs_%'
           ) AS actual,
           3 AS expected
)
SELECT
    component AS "Component",
    actual AS "Found",
    expected AS "Expected",
    CASE
        WHEN actual >= expected THEN 'PASS'
        WHEN actual = 0 THEN 'FAIL'
        ELSE 'WARN'
    END AS "Status",
    CASE
        WHEN actual >= expected THEN ''
        WHEN actual = 0 THEN 'MISSING'
        ELSE 'INCOMPLETE'
    END AS "Note"
FROM status_summary
ORDER BY
    CASE
        WHEN actual >= expected THEN 1
        WHEN actual = 0 THEN 3
        ELSE 2
    END,
    component;

\echo ''
\echo '--- Overall Status ---'

DO $$
DECLARE
    v_function_count INTEGER;
    v_table_count INTEGER;
    v_process_count INTEGER;
    v_overall_status TEXT;
BEGIN
    -- Check critical components
    SELECT COUNT(*) INTO v_function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN ('update_timestamp', 'log_audit_event', 'generate_lot_number',
                      'generate_serial_number', 'validate_process_sequence');

    SELECT COUNT(*) INTO v_table_count
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND c.relkind IN ('r', 'p')
    AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

    SELECT COUNT(*) INTO v_process_count FROM processes;

    -- Determine overall status
    IF v_function_count >= 5 AND v_table_count = 7 AND v_process_count = 8 THEN
        v_overall_status := 'READY';
        RAISE NOTICE 'Status: % - Database is ready for use', v_overall_status;
        RAISE NOTICE 'All critical components verified.';
    ELSIF v_table_count < 7 OR v_process_count = 0 THEN
        v_overall_status := 'NOT READY';
        RAISE WARNING 'Status: % - Critical components missing', v_overall_status;
        RAISE WARNING 'Run full verification: psql -f verify.sql';
    ELSE
        v_overall_status := 'PARTIAL';
        RAISE WARNING 'Status: % - Some components incomplete', v_overall_status;
        RAISE WARNING 'Run full verification: psql -f verify.sql';
    END IF;
END $$;

\echo ''
\echo '--- Database Size ---'

SELECT
    pg_size_pretty(pg_database_size(current_database())) AS "Total Database Size";

\echo ''
\echo '--- Table Sizes ---'

SELECT
    tablename AS "Table",
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS "Size",
    pg_size_pretty(pg_relation_size('public.'||tablename)) AS "Data",
    pg_size_pretty(pg_total_relation_size('public.'||tablename) - pg_relation_size('public.'||tablename)) AS "Indexes"
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
ORDER BY pg_total_relation_size('public.'||tablename) DESC;

\echo ''
\echo '--- Production Data Summary ---'

DO $$
DECLARE
    v_lot_count INTEGER;
    v_serial_count INTEGER;
    v_process_data_count INTEGER;
    v_audit_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_lot_count FROM lots;
    SELECT COUNT(*) INTO v_serial_count FROM serials;
    SELECT COUNT(*) INTO v_process_data_count FROM process_data;
    SELECT COUNT(*) INTO v_audit_count FROM audit_logs;

    RAISE NOTICE 'LOTs:          %', v_lot_count;
    RAISE NOTICE 'Serials:       %', v_serial_count;
    RAISE NOTICE 'Process Data:  %', v_process_data_count;
    RAISE NOTICE 'Audit Logs:    %', v_audit_count;

    IF v_lot_count = 0 AND v_serial_count = 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE 'No production data yet - Ready for first LOT creation';
    END IF;
END $$;

\echo ''
\echo '========================================================================='
\echo 'Quick check complete. For detailed verification, run: verify.sql'
\echo '========================================================================='
\echo ''

\set QUIET off
