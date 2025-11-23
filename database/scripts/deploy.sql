-- =============================================================================
-- F2X NeuroHub MES - PostgreSQL Database Master Deployment Script
-- =============================================================================
-- Purpose: Complete database deployment automation with dependency ordering
-- Author: Database Architecture Team
-- Created: 2025-11-18
-- Database: PostgreSQL 14+
-- Encoding: UTF-8
-- =============================================================================
--
-- EXECUTION ORDER:
--   1. Database Creation (optional)
--   2. Common Functions (parallel-safe, no dependencies)
--   3. Independent Tables (Group A - parallel execution possible)
--   4. First-Level Dependencies (Group B - depends on Group A)
--   5. Second-Level Dependencies (Group C - depends on Group B)
--   6. Third-Level Dependencies (Group D - depends on Group C)
--   7. Final Dependencies (Group E)
--   8. Views (optional)
--
-- FEATURES:
--   - Transaction management with savepoints
--   - Comprehensive error handling
--   - Detailed timing information
--   - Verification queries after each step
--   - Progress reporting
--   - Rollback capability
--
-- USAGE:
--   psql -U postgres -f deploy.sql
--   OR
--   psql -U postgres -v skip_db_creation=1 -f deploy.sql  (to skip DB creation)
--
-- =============================================================================

\set ON_ERROR_STOP on
\timing on

-- =============================================================================
-- CONFIGURATION VARIABLES
-- =============================================================================
\set db_name 'f2x_neurohub_mes'
\set db_owner 'postgres'
\set db_encoding 'UTF8'
\set db_locale 'en_US.UTF-8'

-- =============================================================================
-- BANNER
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'F2X NeuroHub MES - PostgreSQL Database Deployment'
\echo '==============================================================================='
\echo 'Database Name: ' :db_name
\echo 'Encoding:      ' :db_encoding
\echo 'Started:       ' `date '+%Y-%m-%d %H:%M:%S'`
\echo '==============================================================================='
\echo ''

-- =============================================================================
-- STEP 1: DATABASE CREATION (Optional)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 1: DATABASE CREATION'
\echo '==============================================================================='

-- Check if database exists
SELECT 'Database already exists: ' || datname AS info
FROM pg_database
WHERE datname = :'db_name';

-- Create database if it doesn't exist
-- Note: This must be run outside a transaction block
-- Uncomment the following lines if you want to create the database
/*
\echo 'Creating database if it does not exist...'
SELECT 'CREATE DATABASE ' || :'db_name || ' WITH ENCODING ' || quote_literal(:'db_encoding) || ' LC_COLLATE = ' || quote_literal(:'db_locale) || ' LC_CTYPE = ' || quote_literal(:'db_locale) || ' TEMPLATE template0'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'db_name') \gexec

\echo 'Connecting to database...'
\c :db_name
*/

\echo 'Current database: ' :DBNAME
\echo 'Current user:     ' :USER
\echo 'Step 1 completed successfully.'
\echo ''

-- =============================================================================
-- STEP 2: COMMON FUNCTIONS (No Dependencies)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 2: DEPLOYING COMMON FUNCTIONS (Parallel-Safe, No Dependencies)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_functions;

\echo '[2.1] Creating function: update_timestamp()...'
\i ddl/01_functions/update_timestamp.sql
\echo '      OK - update_timestamp() created'

\echo '[2.2] Creating function: prevent_audit_modification()...'
\i ddl/01_functions/prevent_audit_modification.sql
\echo '      OK - prevent_audit_modification() created'

\echo '[2.3] Creating function: log_audit_event()...'
\i ddl/01_functions/log_audit_event.sql
\echo '      OK - log_audit_event() created'

\echo '[2.4] Creating function: prevent_process_deletion()...'
\i ddl/01_functions/prevent_process_deletion.sql
\echo '      OK - prevent_process_deletion() created'

\echo '[2.5] Creating function: prevent_user_deletion()...'
\i ddl/01_functions/prevent_user_deletion.sql
\echo '      OK - prevent_user_deletion() created'

COMMIT;

\echo ''
\echo 'Verification: Checking created functions...'
SELECT
    proname AS function_name,
    pg_get_function_result(oid) AS return_type,
    pronargs AS arg_count
FROM pg_proc
WHERE proname IN (
    'update_timestamp',
    'prevent_audit_modification',
    'log_audit_event',
    'prevent_process_deletion',
    'prevent_user_deletion'
)
ORDER BY proname;

\echo ''
\echo 'Step 2 completed successfully. (5 functions created)'
\echo ''

-- =============================================================================
-- STEP 3: INDEPENDENT TABLES (Group A - No Dependencies)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 3: DEPLOYING INDEPENDENT TABLES (Group A)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_independent_tables;

\echo '[3.1] Creating table: product_models...'
\i ddl/02_tables/01_product_models.sql
\echo '      OK - product_models table created'

\echo '[3.2] Creating table: processes (with 8 process records)...'
\i ddl/02_tables/02_processes.sql
\echo '      OK - processes table created and populated'

\echo '[3.3] Creating table: users...'
\i ddl/02_tables/03_users.sql
\echo '      OK - users table created'

COMMIT;

\echo ''
\echo 'Verification: Checking independent tables...'
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename IN ('product_models', 'processes', 'users')
  AND schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo 'Verification: Checking processes data...'
SELECT
    process_number,
    process_code,
    process_name_ko,
    process_name_en,
    is_active
FROM processes
ORDER BY process_number;

\echo ''
\echo 'Step 3 completed successfully. (3 tables created)'
\echo ''

-- =============================================================================
-- STEP 4: FIRST-LEVEL DEPENDENCIES (Group B)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 4: DEPLOYING FIRST-LEVEL DEPENDENCIES (Group B)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_lots_table;

\echo '[4.1] Creating table: lots (depends on product_models)...'
\i ddl/02_tables/04_lots.sql
\echo '      OK - lots table created'

COMMIT;

\echo ''
\echo 'Verification: Checking lots table...'
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE tablename = 'lots'
  AND schemaname = 'public';

\echo ''
\echo 'Verification: Checking lots foreign keys...'
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'lots';

\echo ''
\echo 'Step 4 completed successfully. (1 table created)'
\echo ''

-- =============================================================================
-- STEP 5: SECOND-LEVEL DEPENDENCIES (Group C)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 5: DEPLOYING SECOND-LEVEL DEPENDENCIES (Group C)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_serials_table;

\echo '[5.1] Creating table: serials (depends on lots)...'
\i ddl/02_tables/05_serials.sql
\echo '      OK - serials table created'

COMMIT;

\echo ''
\echo 'Verification: Checking serials table...'
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE tablename = 'serials'
  AND schemaname = 'public';

\echo ''
\echo 'Verification: Checking serials foreign keys...'
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'serials';

\echo ''
\echo 'Step 5 completed successfully. (1 table created)'
\echo ''

-- =============================================================================
-- STEP 6: THIRD-LEVEL DEPENDENCIES (Group D)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 6: DEPLOYING THIRD-LEVEL DEPENDENCIES (Group D)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_process_data_table;

\echo '[6.1] Creating table: process_data (depends on lots, serials, processes, users)...'
\i ddl/02_tables/06_process_data.sql
\echo '      OK - process_data table created'

COMMIT;

\echo ''
\echo 'Verification: Checking process_data table...'
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE tablename = 'process_data'
  AND schemaname = 'public';

\echo ''
\echo 'Verification: Checking process_data foreign keys...'
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'process_data'
ORDER BY tc.constraint_name;

\echo ''
\echo 'Step 6 completed successfully. (1 table created)'
\echo ''

-- =============================================================================
-- STEP 7: FINAL DEPENDENCIES (Group E)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 7: DEPLOYING FINAL DEPENDENCIES (Group E)'
\echo '==============================================================================='
\echo ''

BEGIN;

SAVEPOINT before_audit_logs_table;

\echo '[7.1] Creating table: audit_logs (depends on users)...'
\i ddl/02_tables/07_audit_logs.sql
\echo '      OK - audit_logs table created with partitions'

COMMIT;

\echo ''
\echo 'Verification: Checking audit_logs table and partitions...'
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'audit_logs%'
  AND schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo 'Verification: Checking audit_logs foreign keys...'
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name = 'audit_logs';

\echo ''
\echo 'Step 7 completed successfully. (1 table created with 3 partitions)'
\echo ''

-- =============================================================================
-- STEP 8: VIEWS (Optional)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 8: DEPLOYING VIEWS (Optional)'
\echo '==============================================================================='
\echo ''
\echo 'NOTE: View creation is currently skipped as view files were not found.'
\echo 'If you have view definition files, include them here:'
\echo '  - views/process_views/01_process_views_part1.sql'
\echo '  - views/process_views/02_process_views_part2.sql'
\echo ''

-- Uncomment the following lines when view files are available:
-- BEGIN;
-- SAVEPOINT before_views;
-- \echo '[8.1] Creating views: process_views_part1...'
-- \i views/process_views/01_process_views_part1.sql
-- \echo '      OK - process_views_part1 created'
-- \echo '[8.2] Creating views: process_views_part2...'
-- \i views/process_views/02_process_views_part2.sql
-- \echo '      OK - process_views_part2 created'
-- COMMIT;

\echo 'Step 8 skipped. (No views to create)'
\echo ''

-- =============================================================================
-- FINAL VERIFICATION AND SUMMARY
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'FINAL VERIFICATION AND SUMMARY'
\echo '==============================================================================='
\echo ''

\echo 'All Database Tables:'
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size,
    pg_total_relation_size('public.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT LIKE 'audit_logs_y%'  -- Exclude partition tables from main list
ORDER BY tablename;

\echo ''
\echo 'All Database Functions:'
SELECT
    proname AS function_name,
    pg_get_function_result(oid) AS return_type,
    pg_get_functiondef(oid) IS NOT NULL AS has_definition
FROM pg_proc
WHERE pronamespace = 'public'::regnamespace
  AND prokind = 'f'
ORDER BY proname;

\echo ''
\echo 'All Triggers:'
SELECT
    trigger_schema,
    trigger_name,
    event_object_table,
    action_timing,
    string_agg(event_manipulation, ', ') AS events
FROM information_schema.triggers
WHERE trigger_schema = 'public'
GROUP BY trigger_schema, trigger_name, event_object_table, action_timing
ORDER BY event_object_table, trigger_name;

\echo ''
\echo 'All Foreign Key Constraints:'
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name;

\echo ''
\echo 'Database Size Summary:'
SELECT
    pg_database.datname AS database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = current_database();

\echo ''
\echo 'Table Row Counts:'
SELECT
    'product_models' AS table_name, COUNT(*) AS row_count FROM product_models
UNION ALL
SELECT 'processes', COUNT(*) FROM processes
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'lots', COUNT(*) FROM lots
UNION ALL
SELECT 'serials', COUNT(*) FROM serials
UNION ALL
SELECT 'process_data', COUNT(*) FROM process_data
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs
ORDER BY table_name;

\echo ''
\echo '==============================================================================='
\echo 'DEPLOYMENT SUMMARY'
\echo '==============================================================================='
\echo ''
\echo 'Deployment completed successfully!'
\echo ''
\echo 'Objects Created:'
\echo '  - Functions:  5 (update_timestamp, prevent_audit_modification, log_audit_event,'
\echo '                   prevent_process_deletion, prevent_user_deletion)'
\echo '  - Tables:     7 (product_models, processes, users, lots, serials,'
\echo '                   process_data, audit_logs)'
\echo '  - Partitions: 3 (audit_logs_y2025m11, audit_logs_y2025m12, audit_logs_y2026m01)'
\echo '  - Views:      0 (skipped)'
\echo ''
\echo 'Initial Data:'
\echo '  - 8 manufacturing processes pre-loaded'
\echo ''
\echo 'Completed:    ' `date '+%Y-%m-%d %H:%M:%S'`
\echo '==============================================================================='
\echo ''

-- =============================================================================
-- POST-DEPLOYMENT RECOMMENDATIONS
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'POST-DEPLOYMENT RECOMMENDATIONS'
\echo '==============================================================================='
\echo ''
\echo '1. Create application roles and grant appropriate permissions:'
\echo '   CREATE ROLE mes_application;'
\echo '   CREATE ROLE mes_readonly;'
\echo '   CREATE ROLE mes_admin;'
\echo ''
\echo '2. Insert initial users into users table'
\echo ''
\echo '3. Insert product models into product_models table'
\echo ''
\echo '4. Configure audit_logs partition maintenance:'
\echo '   SELECT create_future_audit_partitions(6);  -- Create 6 months ahead'
\echo ''
\echo '5. Set up regular maintenance tasks:'
\echo '   - VACUUM ANALYZE (weekly)'
\echo '   - Partition management (monthly)'
\echo '   - Index maintenance (quarterly)'
\echo ''
\echo '6. Configure connection pooling (PgBouncer recommended)'
\echo ''
\echo '7. Set up database backups:'
\echo '   - Daily full backups'
\echo '   - Point-in-time recovery (WAL archiving)'
\echo '   - Test restore procedures quarterly'
\echo ''
\echo '8. Monitor performance metrics:'
\echo '   - Query execution times'
\echo '   - Index usage statistics'
\echo '   - Table bloat'
\echo '   - Connection pool utilization'
\echo ''
\echo '==============================================================================='
\echo ''

-- =============================================================================
-- END OF DEPLOYMENT SCRIPT
-- =============================================================================
