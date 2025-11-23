-- =============================================================================
-- F2X NeuroHub MES Database Verification Script
-- =============================================================================
-- Description: Comprehensive verification of database deployment
-- Database: f2x_neurohub_mes (PostgreSQL 14+)
-- Author: F2X Database Architecture Team
-- Created: 2025-11-18
-- Version: 1.0
-- =============================================================================
--
-- This script performs 9 categories of verification checks:
--   1. Database Existence and Encoding
--   2. Function Verification (14 functions total)
--   3. Table Verification (7 tables)
--   4. Constraint Verification (Foreign Keys, Unique, Check)
--   5. Index Verification (50+ indexes)
--   6. Trigger Verification (per table)
--   7. Master Data Verification (8 processes)
--   8. Partition Verification (audit_logs partitioning)
--   9. View Verification (8 process views) - OPTIONAL
--
-- Usage:
--   psql -U postgres -d f2x_neurohub_mes -f verify.sql
--
-- Output: Pass/Fail status for each check with detailed counts
-- =============================================================================

\timing on
\set VERBOSITY verbose

-- Set output format for better readability
\pset border 2
\pset format wrapped

-- Display execution context
SELECT
    current_database() AS database_name,
    current_user AS connected_user,
    version() AS postgres_version,
    NOW() AS verification_timestamp;

\echo ''
\echo '============================================================================='
\echo 'F2X NeuroHub MES Database Verification Report'
\echo '============================================================================='
\echo ''

-- =============================================================================
-- SECTION 1: DATABASE EXISTENCE AND ENCODING
-- =============================================================================
\echo '>>> SECTION 1: Database Existence and Encoding'
\echo '-----------------------------------------------------------------------------'

DO $$
DECLARE
    v_db_name TEXT;
    v_encoding TEXT;
    v_collate TEXT;
    v_ctype TEXT;
BEGIN
    SELECT
        datname,
        pg_encoding_to_char(encoding),
        datcollate,
        datctype
    INTO v_db_name, v_encoding, v_collate, v_ctype
    FROM pg_database
    WHERE datname = 'f2x_neurohub_mes';

    IF v_db_name IS NULL THEN
        RAISE EXCEPTION 'FAIL: Database f2x_neurohub_mes does not exist';
    ELSE
        RAISE NOTICE 'PASS: Database exists: %', v_db_name;
        RAISE NOTICE '  - Encoding: %', v_encoding;
        RAISE NOTICE '  - Collate: %', v_collate;
        RAISE NOTICE '  - CType: %', v_ctype;

        IF v_encoding != 'UTF8' THEN
            RAISE WARNING 'WARNING: Expected UTF8 encoding, found: %', v_encoding;
        END IF;
    END IF;
END $$;

\echo ''

-- =============================================================================
-- SECTION 2: FUNCTION VERIFICATION (14 Functions Total)
-- =============================================================================
\echo '>>> SECTION 2: Function Verification'
\echo '-----------------------------------------------------------------------------'
\echo 'Expected Functions:'
\echo '  Common Functions (5):'
\echo '    1. update_timestamp()'
\echo '    2. log_audit_event()'
\echo '    3. prevent_audit_modification()'
\echo '    4. prevent_process_deletion()'
\echo '    5. prevent_user_deletion()'
\echo '  Table-Specific Functions (9):'
\echo '    6. generate_lot_number()'
\echo '    7. validate_lot_status_transition()'
\echo '    8. auto_close_lot()'
\echo '    9. generate_serial_number()'
\echo '    10. validate_lot_capacity()'
\echo '    11. validate_serial_status_transition()'
\echo '    12. update_lot_quantities()'
\echo '    13. calculate_process_duration()'
\echo '    14. validate_process_sequence()'
\echo '-----------------------------------------------------------------------------'

WITH expected_functions AS (
    SELECT unnest(ARRAY[
        'update_timestamp',
        'log_audit_event',
        'prevent_audit_modification',
        'prevent_process_deletion',
        'prevent_user_deletion',
        'generate_lot_number',
        'validate_lot_status_transition',
        'auto_close_lot',
        'generate_serial_number',
        'validate_lot_capacity',
        'validate_serial_status_transition',
        'update_lot_quantities',
        'calculate_process_duration',
        'validate_process_sequence'
    ]) AS function_name
),
actual_functions AS (
    SELECT
        p.proname AS function_name,
        pg_get_function_arguments(p.oid) AS arguments,
        pg_get_function_result(p.oid) AS return_type
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (SELECT function_name FROM expected_functions)
),
verification AS (
    SELECT
        e.function_name,
        CASE
            WHEN a.function_name IS NOT NULL THEN 'PASS'
            ELSE 'FAIL'
        END AS status,
        a.return_type,
        a.arguments
    FROM expected_functions e
    LEFT JOIN actual_functions a ON e.function_name = a.function_name
    ORDER BY e.function_name
)
SELECT
    function_name AS "Function Name",
    status AS "Status",
    COALESCE(return_type, 'NOT FOUND') AS "Return Type",
    COALESCE(arguments, 'N/A') AS "Arguments"
FROM verification;

-- Function count summary
WITH expected_functions AS (
    SELECT unnest(ARRAY[
        'update_timestamp', 'log_audit_event', 'prevent_audit_modification',
        'prevent_process_deletion', 'prevent_user_deletion', 'generate_lot_number',
        'validate_lot_status_transition', 'auto_close_lot', 'generate_serial_number',
        'validate_lot_capacity', 'validate_serial_status_transition',
        'update_lot_quantities', 'calculate_process_duration', 'validate_process_sequence'
    ]) AS function_name
),
actual_functions AS (
    SELECT p.proname AS function_name
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (SELECT function_name FROM expected_functions)
)
SELECT
    COUNT(*) AS found_count,
    14 AS expected_count,
    CASE
        WHEN COUNT(*) = 14 THEN 'PASS: All functions present'
        ELSE 'FAIL: Missing ' || (14 - COUNT(*)) || ' functions'
    END AS summary
FROM actual_functions;

\echo ''

-- =============================================================================
-- SECTION 3: TABLE VERIFICATION (7 Tables)
-- =============================================================================
\echo '>>> SECTION 3: Table Verification'
\echo '-----------------------------------------------------------------------------'
\echo 'Expected Tables: product_models, processes, users, lots, serials,'
\echo '                 process_data, audit_logs'
\echo '-----------------------------------------------------------------------------'

WITH expected_tables AS (
    SELECT unnest(ARRAY[
        'product_models', 'processes', 'users', 'lots',
        'serials', 'process_data', 'audit_logs'
    ]) AS table_name
),
actual_tables AS (
    SELECT
        c.relname AS table_name,
        (SELECT COUNT(*) FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = c.relname) AS column_count,
        obj_description(c.oid, 'pg_class') AS table_comment,
        CASE
            WHEN c.relkind = 'p' THEN 'Partitioned'
            ELSE 'Regular'
        END AS table_type
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND c.relkind IN ('r', 'p')
    AND c.relname IN (SELECT table_name FROM expected_tables)
),
verification AS (
    SELECT
        e.table_name,
        CASE
            WHEN a.table_name IS NOT NULL THEN 'PASS'
            ELSE 'FAIL'
        END AS status,
        a.column_count,
        a.table_type,
        CASE
            WHEN a.table_comment IS NOT NULL THEN 'Yes'
            ELSE 'No'
        END AS has_comment
    FROM expected_tables e
    LEFT JOIN actual_tables a ON e.table_name = a.table_name
    ORDER BY e.table_name
)
SELECT
    table_name AS "Table Name",
    status AS "Status",
    COALESCE(column_count::TEXT, 'N/A') AS "Columns",
    COALESCE(table_type, 'NOT FOUND') AS "Type",
    COALESCE(has_comment, 'N/A') AS "Comment"
FROM verification;

-- Table count summary
WITH expected_tables AS (
    SELECT unnest(ARRAY[
        'product_models', 'processes', 'users', 'lots',
        'serials', 'process_data', 'audit_logs'
    ]) AS table_name
),
actual_tables AS (
    SELECT c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND c.relkind IN ('r', 'p')
    AND c.relname IN (SELECT table_name FROM expected_tables)
)
SELECT
    COUNT(*) AS found_count,
    7 AS expected_count,
    CASE
        WHEN COUNT(*) = 7 THEN 'PASS: All tables present'
        ELSE 'FAIL: Missing ' || (7 - COUNT(*)) || ' tables'
    END AS summary
FROM actual_tables;

\echo ''

-- =============================================================================
-- SECTION 4: CONSTRAINT VERIFICATION
-- =============================================================================
\echo '>>> SECTION 4: Constraint Verification'
\echo '-----------------------------------------------------------------------------'

-- 4.1: Primary Key Constraints (7 expected)
\echo '--- 4.1: Primary Key Constraints ---'
SELECT
    tc.table_name AS "Table",
    tc.constraint_name AS "Constraint Name",
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS "Columns"
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
AND tc.table_schema = 'public'
AND tc.table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
GROUP BY tc.table_name, tc.constraint_name
ORDER BY tc.table_name;

SELECT
    COUNT(*) AS pk_count,
    CASE
        WHEN COUNT(*) >= 7 THEN 'PASS: All primary keys present'
        ELSE 'FAIL: Missing primary keys'
    END AS summary
FROM information_schema.table_constraints
WHERE constraint_type = 'PRIMARY KEY'
AND table_schema = 'public'
AND table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- 4.2: Foreign Key Constraints (7 expected)
\echo '--- 4.2: Foreign Key Constraints ---'
SELECT
    tc.table_name AS "From Table",
    kcu.column_name AS "Column",
    ccu.table_name AS "To Table",
    ccu.column_name AS "Referenced Column",
    tc.constraint_name AS "Constraint Name"
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public'
AND tc.table_name IN ('lots', 'serials', 'process_data', 'audit_logs')
ORDER BY tc.table_name, kcu.column_name;

SELECT
    COUNT(*) AS fk_count,
    CASE
        WHEN COUNT(*) >= 7 THEN 'PASS: ' || COUNT(*) || ' foreign keys found'
        ELSE 'WARNING: Only ' || COUNT(*) || ' foreign keys found (expected >= 7)'
    END AS summary
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
AND table_schema = 'public'
AND table_name IN ('lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- 4.3: Unique Constraints
\echo '--- 4.3: Unique Constraints ---'
SELECT
    tc.table_name AS "Table",
    tc.constraint_name AS "Constraint Name",
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS "Columns"
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
AND tc.table_schema = 'public'
AND tc.table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
GROUP BY tc.table_name, tc.constraint_name
ORDER BY tc.table_name;

SELECT
    COUNT(*) AS unique_count,
    CASE
        WHEN COUNT(*) >= 10 THEN 'PASS: ' || COUNT(*) || ' unique constraints found'
        ELSE 'WARNING: Only ' || COUNT(*) || ' unique constraints found'
    END AS summary
FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE'
AND table_schema = 'public'
AND table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- 4.4: Check Constraints
\echo '--- 4.4: Check Constraints ---'
SELECT
    tc.table_name AS "Table",
    tc.constraint_name AS "Constraint Name",
    cc.check_clause AS "Check Condition"
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.constraint_type = 'CHECK'
AND tc.table_schema = 'public'
AND tc.table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
ORDER BY tc.table_name, tc.constraint_name;

SELECT
    COUNT(*) AS check_count,
    CASE
        WHEN COUNT(*) >= 20 THEN 'PASS: ' || COUNT(*) || ' check constraints found'
        ELSE 'WARNING: Only ' || COUNT(*) || ' check constraints found'
    END AS summary
FROM information_schema.table_constraints
WHERE constraint_type = 'CHECK'
AND table_schema = 'public'
AND table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- =============================================================================
-- SECTION 5: INDEX VERIFICATION (50+ Indexes Expected)
-- =============================================================================
\echo '>>> SECTION 5: Index Verification'
\echo '-----------------------------------------------------------------------------'

-- 5.1: All indexes by table
\echo '--- 5.1: Index Summary by Table ---'
SELECT
    t.tablename AS "Table",
    COUNT(*) AS "Index Count",
    COUNT(*) FILTER (WHERE idx.indexdef LIKE '%UNIQUE%') AS "Unique Indexes",
    COUNT(*) FILTER (WHERE idx.indexdef LIKE '%gin%') AS "GIN Indexes",
    COUNT(*) FILTER (WHERE idx.indexdef LIKE '%WHERE%') AS "Partial Indexes"
FROM pg_indexes idx
JOIN pg_tables t ON idx.tablename = t.tablename
WHERE idx.schemaname = 'public'
AND t.tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
GROUP BY t.tablename
ORDER BY t.tablename;

-- 5.2: GIN indexes on JSONB columns
\echo ''
\echo '--- 5.2: GIN Indexes on JSONB Columns ---'
SELECT
    tablename AS "Table",
    indexname AS "Index Name",
    indexdef AS "Index Definition"
FROM pg_indexes
WHERE schemaname = 'public'
AND indexdef LIKE '%gin%'
AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
ORDER BY tablename, indexname;

-- 5.3: Partial indexes
\echo ''
\echo '--- 5.3: Partial Indexes ---'
SELECT
    tablename AS "Table",
    indexname AS "Index Name",
    substring(indexdef from 'WHERE (.*)$') AS "WHERE Clause"
FROM pg_indexes
WHERE schemaname = 'public'
AND indexdef LIKE '%WHERE%'
AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
ORDER BY tablename, indexname;

-- Index count summary
SELECT
    COUNT(*) AS total_indexes,
    CASE
        WHEN COUNT(*) >= 50 THEN 'PASS: ' || COUNT(*) || ' indexes found (expected >= 50)'
        ELSE 'WARNING: Only ' || COUNT(*) || ' indexes found (expected >= 50)'
    END AS summary
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- =============================================================================
-- SECTION 6: TRIGGER VERIFICATION
-- =============================================================================
\echo '>>> SECTION 6: Trigger Verification'
\echo '-----------------------------------------------------------------------------'

-- 6.1: Triggers by table
SELECT
    t.tgrelid::regclass AS "Table",
    t.tgname AS "Trigger Name",
    CASE t.tgtype::integer & 1
        WHEN 1 THEN 'ROW'
        ELSE 'STATEMENT'
    END AS "Level",
    CASE t.tgtype::integer & 66
        WHEN 2 THEN 'BEFORE'
        WHEN 64 THEN 'INSTEAD OF'
        ELSE 'AFTER'
    END AS "Timing",
    CASE
        WHEN t.tgtype::integer & 4 != 0 THEN 'INSERT'
        WHEN t.tgtype::integer & 8 != 0 THEN 'DELETE'
        WHEN t.tgtype::integer & 16 != 0 THEN 'UPDATE'
        ELSE 'TRUNCATE'
    END AS "Event",
    p.proname AS "Function"
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
JOIN pg_class c ON t.tgrelid = c.oid
WHERE NOT t.tgisinternal
AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs')
ORDER BY c.relname, t.tgname;

-- Trigger count summary
SELECT
    COUNT(*) AS trigger_count,
    CASE
        WHEN COUNT(*) >= 20 THEN 'PASS: ' || COUNT(*) || ' triggers found'
        ELSE 'WARNING: Only ' || COUNT(*) || ' triggers found (expected >= 20)'
    END AS summary
FROM pg_trigger t
JOIN pg_class c ON t.tgrelid = c.oid
WHERE NOT t.tgisinternal
AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

\echo ''

-- =============================================================================
-- SECTION 7: MASTER DATA VERIFICATION (8 Processes)
-- =============================================================================
\echo '>>> SECTION 7: Master Data Verification - Processes'
\echo '-----------------------------------------------------------------------------'
\echo 'Expected: 8 processes with codes: LASER_MARKING, LMA_ASSEMBLY,'
\echo '          SENSOR_INSPECTION, FIRMWARE_UPLOAD, ROBOT_ASSEMBLY,'
\echo '          PERFORMANCE_TEST, LABEL_PRINTING, PACKAGING_INSPECTION'
\echo '-----------------------------------------------------------------------------'

DO $$
DECLARE
    v_process_count INTEGER;
    v_expected_count INTEGER := 8;
BEGIN
    SELECT COUNT(*) INTO v_process_count FROM processes;

    IF v_process_count = 0 THEN
        RAISE WARNING 'FAIL: No processes found in processes table';
    ELSIF v_process_count < v_expected_count THEN
        RAISE WARNING 'WARNING: Only % processes found (expected %)', v_process_count, v_expected_count;
    ELSE
        RAISE NOTICE 'PASS: % processes found', v_process_count;
    END IF;
END $$;

-- Verify process details
WITH expected_processes AS (
    SELECT
        process_number,
        process_code
    FROM (VALUES
        (1, 'LASER_MARKING'),
        (2, 'LMA_ASSEMBLY'),
        (3, 'SENSOR_INSPECTION'),
        (4, 'FIRMWARE_UPLOAD'),
        (5, 'ROBOT_ASSEMBLY'),
        (6, 'PERFORMANCE_TEST'),
        (7, 'LABEL_PRINTING'),
        (8, 'PACKAGING_INSPECTION')
    ) AS t(process_number, process_code)
),
actual_processes AS (
    SELECT
        process_number,
        process_code,
        process_name_ko,
        process_name_en,
        is_active
    FROM processes
),
verification AS (
    SELECT
        e.process_number,
        e.process_code AS expected_code,
        a.process_code AS actual_code,
        a.process_name_ko,
        a.process_name_en,
        a.is_active,
        CASE
            WHEN a.process_code IS NOT NULL THEN 'PASS'
            ELSE 'FAIL'
        END AS status
    FROM expected_processes e
    LEFT JOIN actual_processes a ON e.process_number = a.process_number
    ORDER BY e.process_number
)
SELECT
    process_number AS "Number",
    expected_code AS "Expected Code",
    COALESCE(actual_code, 'MISSING') AS "Actual Code",
    process_name_ko AS "Korean Name",
    process_name_en AS "English Name",
    COALESCE(is_active::TEXT, 'N/A') AS "Active",
    status AS "Status"
FROM verification;

-- Process verification summary
WITH expected_processes AS (
    SELECT unnest(ARRAY['LASER_MARKING', 'LMA_ASSEMBLY', 'SENSOR_INSPECTION',
                        'FIRMWARE_UPLOAD', 'ROBOT_ASSEMBLY', 'PERFORMANCE_TEST',
                        'LABEL_PRINTING', 'PACKAGING_INSPECTION']) AS process_code
)
SELECT
    (SELECT COUNT(*) FROM processes WHERE process_code IN (SELECT process_code FROM expected_processes)) AS found_count,
    8 AS expected_count,
    CASE
        WHEN (SELECT COUNT(*) FROM processes WHERE process_code IN (SELECT process_code FROM expected_processes)) = 8
        THEN 'PASS: All 8 processes present'
        ELSE 'FAIL: Missing ' || (8 - (SELECT COUNT(*) FROM processes WHERE process_code IN (SELECT process_code FROM expected_processes))) || ' processes'
    END AS summary;

\echo ''

-- =============================================================================
-- SECTION 8: PARTITION VERIFICATION (audit_logs)
-- =============================================================================
\echo '>>> SECTION 8: Partition Verification - audit_logs'
\echo '-----------------------------------------------------------------------------'

-- 8.1: Check if audit_logs is partitioned
DO $$
DECLARE
    v_is_partitioned BOOLEAN;
BEGIN
    SELECT c.relkind = 'p'
    INTO v_is_partitioned
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND c.relname = 'audit_logs';

    IF v_is_partitioned THEN
        RAISE NOTICE 'PASS: audit_logs is partitioned table';
    ELSE
        RAISE WARNING 'WARNING: audit_logs is not partitioned';
    END IF;
END $$;

-- 8.2: List all partitions
\echo ''
\echo '--- 8.2: audit_logs Partitions ---'
SELECT
    schemaname AS "Schema",
    tablename AS "Partition Name",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS "Size"
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE 'audit_logs_%'
ORDER BY tablename;

-- 8.3: Partition count
SELECT
    COUNT(*) AS partition_count,
    CASE
        WHEN COUNT(*) >= 3 THEN 'PASS: ' || COUNT(*) || ' partitions found'
        ELSE 'WARNING: Only ' || COUNT(*) || ' partitions found'
    END AS summary
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE 'audit_logs_%';

-- 8.4: Verify partition functions exist
\echo ''
\echo '--- 8.4: Partition Management Functions ---'
SELECT
    p.proname AS "Function Name",
    pg_get_function_arguments(p.oid) AS "Arguments",
    'PASS' AS "Status"
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
AND p.proname IN ('create_monthly_audit_partition', 'create_future_audit_partitions', 'drop_old_audit_partitions');

\echo ''

-- =============================================================================
-- SECTION 9: VIEW VERIFICATION (Optional)
-- =============================================================================
\echo '>>> SECTION 9: View Verification (Optional)'
\echo '-----------------------------------------------------------------------------'
\echo 'Expected Views: 8 process-specific views (if implemented)'
\echo '-----------------------------------------------------------------------------'

SELECT
    schemaname AS "Schema",
    viewname AS "View Name",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||viewname)) AS "Size"
FROM pg_views
WHERE schemaname = 'public'
AND viewname LIKE '%process%'
ORDER BY viewname;

SELECT
    COUNT(*) AS view_count,
    CASE
        WHEN COUNT(*) >= 1 THEN 'INFO: ' || COUNT(*) || ' process views found'
        ELSE 'INFO: No process views found (optional)'
    END AS summary
FROM pg_views
WHERE schemaname = 'public'
AND viewname LIKE '%process%';

\echo ''

-- =============================================================================
-- FINAL SUMMARY
-- =============================================================================
\echo '============================================================================='
\echo 'FINAL VERIFICATION SUMMARY'
\echo '============================================================================='

DO $$
DECLARE
    v_db_exists BOOLEAN;
    v_function_count INTEGER;
    v_table_count INTEGER;
    v_fk_count INTEGER;
    v_pk_count INTEGER;
    v_index_count INTEGER;
    v_trigger_count INTEGER;
    v_process_count INTEGER;
    v_partition_count INTEGER;
    v_overall_status TEXT := 'PASS';
BEGIN
    -- Database check
    SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = 'f2x_neurohub_mes')
    INTO v_db_exists;

    -- Function check
    SELECT COUNT(*) INTO v_function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN ('update_timestamp', 'log_audit_event', 'prevent_audit_modification',
                      'prevent_process_deletion', 'prevent_user_deletion', 'generate_lot_number',
                      'validate_lot_status_transition', 'auto_close_lot', 'generate_serial_number',
                      'validate_lot_capacity', 'validate_serial_status_transition',
                      'update_lot_quantities', 'calculate_process_duration', 'validate_process_sequence');

    -- Table check
    SELECT COUNT(*) INTO v_table_count
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'public'
    AND c.relkind IN ('r', 'p')
    AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

    -- Foreign key check
    SELECT COUNT(*) INTO v_fk_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public'
    AND table_name IN ('lots', 'serials', 'process_data', 'audit_logs');

    -- Primary key check
    SELECT COUNT(*) INTO v_pk_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'PRIMARY KEY'
    AND table_schema = 'public'
    AND table_name IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

    -- Index check
    SELECT COUNT(*) INTO v_index_count
    FROM pg_indexes
    WHERE schemaname = 'public'
    AND tablename IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

    -- Trigger check
    SELECT COUNT(*) INTO v_trigger_count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    WHERE NOT t.tgisinternal
    AND c.relname IN ('product_models', 'processes', 'users', 'lots', 'serials', 'process_data', 'audit_logs');

    -- Process master data check
    SELECT COUNT(*) INTO v_process_count
    FROM processes
    WHERE process_code IN ('LASER_MARKING', 'LMA_ASSEMBLY', 'SENSOR_INSPECTION',
                          'FIRMWARE_UPLOAD', 'ROBOT_ASSEMBLY', 'PERFORMANCE_TEST',
                          'LABEL_PRINTING', 'PACKAGING_INSPECTION');

    -- Partition check
    SELECT COUNT(*) INTO v_partition_count
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename LIKE 'audit_logs_%';

    -- Print summary
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Verification Results:';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '1. Database Existence:        %', CASE WHEN v_db_exists THEN 'PASS' ELSE 'FAIL' END;
    RAISE NOTICE '2. Functions:                  % / 14 %', v_function_count, CASE WHEN v_function_count = 14 THEN 'PASS' ELSE 'FAIL' END;
    RAISE NOTICE '3. Tables:                     % / 7 %', v_table_count, CASE WHEN v_table_count = 7 THEN 'PASS' ELSE 'FAIL' END;
    RAISE NOTICE '4. Primary Keys:               % / 7 %', v_pk_count, CASE WHEN v_pk_count >= 7 THEN 'PASS' ELSE 'FAIL' END;
    RAISE NOTICE '5. Foreign Keys:               % / 7 %', v_fk_count, CASE WHEN v_fk_count >= 7 THEN 'PASS' ELSE 'WARNING' END;
    RAISE NOTICE '6. Indexes:                    % / 50+ %', v_index_count, CASE WHEN v_index_count >= 50 THEN 'PASS' ELSE 'WARNING' END;
    RAISE NOTICE '7. Triggers:                   % / 20+ %', v_trigger_count, CASE WHEN v_trigger_count >= 20 THEN 'PASS' ELSE 'WARNING' END;
    RAISE NOTICE '8. Process Master Data:        % / 8 %', v_process_count, CASE WHEN v_process_count = 8 THEN 'PASS' ELSE 'FAIL' END;
    RAISE NOTICE '9. audit_logs Partitions:      % / 3+ %', v_partition_count, CASE WHEN v_partition_count >= 3 THEN 'PASS' ELSE 'WARNING' END;
    RAISE NOTICE '============================================================================';

    -- Determine overall status
    IF NOT v_db_exists THEN v_overall_status := 'FAIL'; END IF;
    IF v_function_count < 14 THEN v_overall_status := 'FAIL'; END IF;
    IF v_table_count < 7 THEN v_overall_status := 'FAIL'; END IF;
    IF v_pk_count < 7 THEN v_overall_status := 'FAIL'; END IF;
    IF v_process_count < 8 THEN v_overall_status := 'FAIL'; END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'OVERALL STATUS: %', v_overall_status;
    RAISE NOTICE '============================================================================';

    IF v_overall_status = 'FAIL' THEN
        RAISE WARNING 'Database verification FAILED. Please review error messages above.';
    ELSE
        RAISE NOTICE 'Database verification completed successfully!';
    END IF;
END $$;

\echo ''
\echo 'Verification script completed.'
\echo ''

-- =============================================================================
-- END OF VERIFICATION SCRIPT
-- =============================================================================
