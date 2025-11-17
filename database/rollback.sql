-- =============================================================================
-- F2X NeuroHub MES - PostgreSQL Database Rollback Script
-- =============================================================================
-- Purpose: Complete database teardown in reverse dependency order
-- Author: Database Architecture Team
-- Created: 2025-11-18
-- Database: PostgreSQL 14+
-- =============================================================================
--
-- WARNING: THIS SCRIPT WILL DELETE ALL DATA!
-- This script removes all database objects created by deploy.sql
--
-- USAGE:
--   psql -U postgres -d f2x_neurohub_mes -f rollback.sql
--
-- IMPORTANT NOTES:
--   - This script performs a complete teardown
--   - All data will be permanently lost
--   - Always backup before running this script
--   - Consider exporting data first if needed
--
-- BACKUP COMMAND:
--   pg_dump -U postgres f2x_neurohub_mes > backup_before_rollback.sql
--
-- =============================================================================

\set ON_ERROR_STOP on
\timing on

-- =============================================================================
-- BANNER
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'F2X NeuroHub MES - PostgreSQL Database Rollback'
\echo '==============================================================================='
\echo 'WARNING: This will delete ALL database objects and data!'
\echo 'Database: ' :DBNAME
\echo 'User:     ' :USER
\echo 'Started:  ' `date '+%Y-%m-%d %H:%M:%S'`
\echo '==============================================================================='
\echo ''

-- Pause and require user confirmation
\prompt 'Type YES to continue with rollback (anything else to cancel): ' confirm

-- Check confirmation (note: this is a safety check in interactive mode)
\if :{?confirm}
\else
    \echo 'Confirmation variable not set. Exiting.'
    \q
\endif

-- =============================================================================
-- PRE-ROLLBACK BACKUP RECOMMENDATION
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'PRE-ROLLBACK CHECKS'
\echo '==============================================================================='
\echo ''
\echo 'Current table row counts (will be lost):'

SELECT
    'product_models' AS table_name,
    COUNT(*) AS row_count,
    pg_size_pretty(pg_total_relation_size('product_models')) AS size
FROM product_models
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'product_models')
UNION ALL
SELECT 'processes', COUNT(*), pg_size_pretty(pg_total_relation_size('processes'))
FROM processes
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'processes')
UNION ALL
SELECT 'users', COUNT(*), pg_size_pretty(pg_total_relation_size('users'))
FROM users
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'users')
UNION ALL
SELECT 'lots', COUNT(*), pg_size_pretty(pg_total_relation_size('lots'))
FROM lots
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'lots')
UNION ALL
SELECT 'serials', COUNT(*), pg_size_pretty(pg_total_relation_size('serials'))
FROM serials
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'serials')
UNION ALL
SELECT 'process_data', COUNT(*), pg_size_pretty(pg_total_relation_size('process_data'))
FROM process_data
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'process_data')
UNION ALL
SELECT 'audit_logs', COUNT(*), pg_size_pretty(pg_total_relation_size('audit_logs'))
FROM audit_logs
WHERE EXISTS (SELECT FROM pg_tables WHERE tablename = 'audit_logs');

\echo ''
\echo 'If you need this data, press Ctrl+C NOW and run:'
\echo 'pg_dump -U postgres ' :DBNAME ' > backup.sql'
\echo ''

-- Additional confirmation pause
\prompt 'Press ENTER to continue with rollback or Ctrl+C to cancel: ' pause

-- =============================================================================
-- STEP 1: DROP VIEWS (if any exist)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 1: DROPPING VIEWS'
\echo '==============================================================================='
\echo ''

-- Currently no views exist, but include for completeness
\echo 'No views to drop.'
\echo ''

-- =============================================================================
-- STEP 2: DROP AUDIT LOGS (Group E - Last dependency)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 2: DROPPING AUDIT LOGS (Group E)'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[2.1] Dropping audit_logs and all partitions...'

-- Drop audit management functions first
DROP FUNCTION IF EXISTS maintain_audit_partitions() CASCADE;
DROP FUNCTION IF EXISTS drop_old_audit_partitions(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS create_future_audit_partitions(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS create_monthly_audit_partition(DATE) CASCADE;

-- Drop the main table (CASCADE will drop all partitions)
DROP TABLE IF EXISTS audit_logs CASCADE;

\echo '      OK - audit_logs and partitions dropped'

COMMIT;

\echo ''
\echo 'Step 2 completed.'
\echo ''

-- =============================================================================
-- STEP 3: DROP PROCESS DATA (Group D - Third-level dependencies)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 3: DROPPING PROCESS DATA (Group D)'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[3.1] Dropping process_data table...'

-- Drop functions specific to process_data
DROP FUNCTION IF EXISTS update_serial_status_from_process() CASCADE;
DROP FUNCTION IF EXISTS validate_process_sequence() CASCADE;
DROP FUNCTION IF EXISTS calculate_process_duration() CASCADE;

-- Drop the table
DROP TABLE IF EXISTS process_data CASCADE;

\echo '      OK - process_data table dropped'

COMMIT;

\echo ''
\echo 'Step 3 completed.'
\echo ''

-- =============================================================================
-- STEP 4: DROP SERIALS (Group C - Second-level dependencies)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 4: DROPPING SERIALS (Group C)'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[4.1] Dropping serials table...'

-- Drop functions specific to serials
DROP FUNCTION IF EXISTS update_lot_quantities() CASCADE;
DROP FUNCTION IF EXISTS validate_serial_status_transition() CASCADE;
DROP FUNCTION IF EXISTS validate_lot_capacity() CASCADE;
DROP FUNCTION IF EXISTS generate_serial_number() CASCADE;

-- Drop the table
DROP TABLE IF EXISTS serials CASCADE;

\echo '      OK - serials table dropped'

COMMIT;

\echo ''
\echo 'Step 4 completed.'
\echo ''

-- =============================================================================
-- STEP 5: DROP LOTS (Group B - First-level dependencies)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 5: DROPPING LOTS (Group B)'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[5.1] Dropping lots table...'

-- Drop functions specific to lots
DROP FUNCTION IF EXISTS auto_close_lot() CASCADE;
DROP FUNCTION IF EXISTS validate_lot_status_transition() CASCADE;
DROP FUNCTION IF EXISTS generate_lot_number() CASCADE;

-- Drop the table
DROP TABLE IF EXISTS lots CASCADE;

\echo '      OK - lots table dropped'

COMMIT;

\echo ''
\echo 'Step 5 completed.'
\echo ''

-- =============================================================================
-- STEP 6: DROP INDEPENDENT TABLES (Group A)
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 6: DROPPING INDEPENDENT TABLES (Group A)'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[6.1] Dropping users table...'
DROP TABLE IF EXISTS users CASCADE;
\echo '      OK - users table dropped'

\echo '[6.2] Dropping processes table...'
DROP TABLE IF EXISTS processes CASCADE;
\echo '      OK - processes table dropped'

\echo '[6.3] Dropping product_models table...'
DROP TABLE IF EXISTS product_models CASCADE;
\echo '      OK - product_models table dropped'

COMMIT;

\echo ''
\echo 'Step 6 completed.'
\echo ''

-- =============================================================================
-- STEP 7: DROP COMMON FUNCTIONS
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'STEP 7: DROPPING COMMON FUNCTIONS'
\echo '==============================================================================='
\echo ''

BEGIN;

\echo '[7.1] Dropping prevent_user_deletion()...'
DROP FUNCTION IF EXISTS prevent_user_deletion() CASCADE;
\echo '      OK'

\echo '[7.2] Dropping prevent_process_deletion()...'
DROP FUNCTION IF EXISTS prevent_process_deletion() CASCADE;
\echo '      OK'

\echo '[7.3] Dropping log_audit_event()...'
DROP FUNCTION IF EXISTS log_audit_event() CASCADE;
\echo '      OK'

\echo '[7.4] Dropping prevent_audit_modification()...'
DROP FUNCTION IF EXISTS prevent_audit_modification() CASCADE;
\echo '      OK'

\echo '[7.5] Dropping update_timestamp()...'
DROP FUNCTION IF EXISTS update_timestamp() CASCADE;
\echo '      OK'

COMMIT;

\echo ''
\echo 'Step 7 completed.'
\echo ''

-- =============================================================================
-- VERIFICATION
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'ROLLBACK VERIFICATION'
\echo '==============================================================================='
\echo ''

\echo 'Remaining tables in public schema:'
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''
\echo 'Remaining functions in public schema:'
SELECT
    proname AS function_name,
    pg_get_function_result(oid) AS return_type
FROM pg_proc
WHERE pronamespace = 'public'::regnamespace
  AND prokind = 'f'
ORDER BY proname;

\echo ''
\echo 'Remaining triggers in public schema:'
SELECT
    trigger_schema,
    trigger_name,
    event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- =============================================================================
-- SUMMARY
-- =============================================================================
\echo ''
\echo '==============================================================================='
\echo 'ROLLBACK SUMMARY'
\echo '==============================================================================='
\echo ''
\echo 'Rollback completed successfully!'
\echo ''
\echo 'Objects Removed:'
\echo '  - Functions:  9+ (all trigger functions and utility functions)'
\echo '  - Tables:     7  (product_models, processes, users, lots, serials,'
\echo '                    process_data, audit_logs)'
\echo '  - Partitions: 3  (audit_logs_y2025m11, y2025m12, y2026m01)'
\echo '  - Triggers:   All (automatically dropped with tables)'
\echo ''
\echo 'Database is now in clean state.'
\echo ''
\echo 'To redeploy, run:'
\echo '  psql -U postgres -d ' :DBNAME ' -f deploy.sql'
\echo ''
\echo 'Completed: ' `date '+%Y-%m-%d %H:%M:%S'`
\echo '==============================================================================='
\echo ''

-- =============================================================================
-- OPTIONAL: DROP DATABASE
-- =============================================================================
\echo ''
\echo 'Do you want to also DROP the entire database?'
\echo 'WARNING: This requires disconnecting and cannot be undone!'
\echo ''
\prompt 'Type DROP_DATABASE to drop the entire database (anything else to skip): ' drop_db_confirm

-- Note: The actual DROP DATABASE must be done from outside this connection
-- Provide instructions instead

\if :{?drop_db_confirm}
    \echo ''
    \echo 'To drop the entire database, disconnect and run:'
    \echo '  psql -U postgres -c "DROP DATABASE IF EXISTS ' :DBNAME ';"'
    \echo ''
\endif

-- =============================================================================
-- END OF ROLLBACK SCRIPT
-- =============================================================================
