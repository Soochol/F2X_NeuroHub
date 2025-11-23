-- =============================================================================
-- WIP Tracking System - Master Deployment Script
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Complete deployment of WIP (Work In Progress) tracking system
--          for processes 1-6 before serial number generation at process 7.
--
-- Components Deployed:
--   1. wip_items table - Individual WIP tracking
--   2. wip_process_history table - WIP process execution history
--   3. process_data migration - Add wip_id column
--   4. Materialized views - Dashboard and queue monitoring
--   5. Helper functions and triggers
--
-- Deployment Order:
--   Phase 1: Core tables (wip_items, wip_process_history)
--   Phase 2: process_data integration
--   Phase 3: Views and analytics
--   Phase 4: Verification
--
-- Author: F2X Database Team
-- Date: 2025-11-21
-- Version: 1.0.0
-- =============================================================================

\timing on
\set ON_ERROR_STOP on

-- =============================================================================
-- PRE-DEPLOYMENT CHECKS
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'WIP Tracking System Deployment';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Starting deployment at %', NOW();
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user;
    RAISE NOTICE '';
END $$;

-- Check PostgreSQL version
DO $$
DECLARE
    v_version INTEGER;
BEGIN
    v_version := current_setting('server_version_num')::INTEGER;
    IF v_version < 140000 THEN
        RAISE EXCEPTION 'PostgreSQL 14+ required. Current version: %', version();
    END IF;
    RAISE NOTICE 'PostgreSQL version check: PASS (version %)', version();
END $$;

-- Check required tables exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lots') THEN
        RAISE EXCEPTION 'Required table "lots" does not exist. Deploy base schema first.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'serials') THEN
        RAISE EXCEPTION 'Required table "serials" does not exist. Deploy base schema first.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processes') THEN
        RAISE EXCEPTION 'Required table "processes" does not exist. Deploy base schema first.';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'process_data') THEN
        RAISE EXCEPTION 'Required table "process_data" does not exist. Deploy base schema first.';
    END IF;
    RAISE NOTICE 'Prerequisite tables check: PASS';
END $$;

RAISE NOTICE '';
RAISE NOTICE '=============================================================================';
RAISE NOTICE 'PHASE 1: Deploy Core WIP Tables';
RAISE NOTICE '=============================================================================';
RAISE NOTICE '';

-- =============================================================================
-- PHASE 1A: Deploy wip_items table
-- =============================================================================

RAISE NOTICE '[1/5] Deploying wip_items table...';

\i ddl/02_tables/11_wip_items.sql

RAISE NOTICE '  ✓ wip_items table deployed';
RAISE NOTICE '';

-- =============================================================================
-- PHASE 1B: Deploy wip_process_history table
-- =============================================================================

RAISE NOTICE '[2/5] Deploying wip_process_history table...';

\i ddl/02_tables/12_wip_process_history.sql

RAISE NOTICE '  ✓ wip_process_history table deployed';
RAISE NOTICE '';

-- =============================================================================
-- PHASE 2: Integrate with Existing Tables
-- =============================================================================

RAISE NOTICE '=============================================================================';
RAISE NOTICE 'PHASE 2: Integrate with Existing Tables';
RAISE NOTICE '=============================================================================';
RAISE NOTICE '';

RAISE NOTICE '[3/5] Adding WIP tracking to process_data table...';

\i ddl/03_migrations/add_wip_tracking.sql

RAISE NOTICE '  ✓ process_data integration complete';
RAISE NOTICE '';

-- =============================================================================
-- PHASE 3: Deploy Analytics Views
-- =============================================================================

RAISE NOTICE '=============================================================================';
RAISE NOTICE 'PHASE 3: Deploy Analytics Views';
RAISE NOTICE '=============================================================================';
RAISE NOTICE '';

RAISE NOTICE '[4/5] Creating WIP Status Dashboard materialized view...';

\i views/wip_views/01_mv_wip_status_dashboard.sql

RAISE NOTICE '  ✓ WIP Status Dashboard view created';
RAISE NOTICE '';

RAISE NOTICE '[5/5] Creating Process WIP Queue materialized view...';

\i views/wip_views/02_mv_process_wip_queue.sql

RAISE NOTICE '  ✓ Process WIP Queue view created';
RAISE NOTICE '';

-- =============================================================================
-- PHASE 4: Verification
-- =============================================================================

RAISE NOTICE '=============================================================================';
RAISE NOTICE 'PHASE 4: Deployment Verification';
RAISE NOTICE '=============================================================================';
RAISE NOTICE '';

-- Verify tables
DO $$
DECLARE
    v_table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_table_count
    FROM information_schema.tables
    WHERE table_name IN ('wip_items', 'wip_process_history');

    IF v_table_count != 2 THEN
        RAISE EXCEPTION 'Table verification failed. Expected 2 tables, found %', v_table_count;
    END IF;

    RAISE NOTICE '✓ Tables verified: wip_items, wip_process_history';
END $$;

-- Verify functions
DO $$
DECLARE
    v_function_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname IN (
          'generate_wip_id',
          'validate_wip_status_transition',
          'auto_complete_wip_on_serial_creation',
          'calculate_wip_process_duration',
          'update_wip_current_process',
          'migrate_wip_to_serial_process_data'
      );

    RAISE NOTICE '✓ Functions verified: % WIP-related functions', v_function_count;
END $$;

-- Verify triggers
DO $$
DECLARE
    v_trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_trigger_count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    WHERE c.relname IN ('wip_items', 'wip_process_history');

    RAISE NOTICE '✓ Triggers verified: % triggers on WIP tables', v_trigger_count;
END $$;

-- Verify indexes
DO $$
DECLARE
    v_index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_index_count
    FROM pg_indexes
    WHERE tablename IN ('wip_items', 'wip_process_history', 'process_data')
      AND indexname LIKE '%wip%';

    RAISE NOTICE '✓ Indexes verified: % WIP-related indexes', v_index_count;
END $$;

-- Verify materialized views
DO $$
DECLARE
    v_view_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_view_count
    FROM pg_matviews
    WHERE matviewname IN ('mv_wip_status_dashboard', 'mv_process_wip_queue');

    IF v_view_count != 2 THEN
        RAISE EXCEPTION 'Materialized view verification failed. Expected 2 views, found %', v_view_count;
    END IF;

    RAISE NOTICE '✓ Materialized views verified: mv_wip_status_dashboard, mv_process_wip_queue';
END $$;

-- Verify process_data wip_id column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'process_data'
          AND column_name = 'wip_id'
    ) THEN
        RAISE EXCEPTION 'process_data.wip_id column not found';
    END IF;

    RAISE NOTICE '✓ process_data integration verified: wip_id column exists';
END $$;

-- =============================================================================
-- DEPLOYMENT SUMMARY
-- =============================================================================

RAISE NOTICE '';
RAISE NOTICE '=============================================================================';
RAISE NOTICE 'Deployment Summary';
RAISE NOTICE '=============================================================================';

DO $$
DECLARE
    v_wip_table_count INTEGER;
    v_wip_index_count INTEGER;
    v_wip_function_count INTEGER;
    v_wip_trigger_count INTEGER;
    v_wip_view_count INTEGER;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO v_wip_table_count
    FROM information_schema.tables
    WHERE table_name LIKE 'wip%';

    -- Count indexes
    SELECT COUNT(*) INTO v_wip_index_count
    FROM pg_indexes
    WHERE indexname LIKE '%wip%';

    -- Count functions
    SELECT COUNT(*) INTO v_wip_function_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname LIKE '%wip%';

    -- Count triggers
    SELECT COUNT(*) INTO v_wip_trigger_count
    FROM pg_trigger t
    JOIN pg_class c ON t.tgrelid = c.oid
    WHERE c.relname LIKE 'wip%';

    -- Count views
    SELECT COUNT(*) INTO v_wip_view_count
    FROM pg_matviews
    WHERE matviewname LIKE '%wip%';

    RAISE NOTICE 'Tables created:          %', v_wip_table_count;
    RAISE NOTICE 'Indexes created:         %', v_wip_index_count;
    RAISE NOTICE 'Functions created:       %', v_wip_function_count;
    RAISE NOTICE 'Triggers created:        %', v_wip_trigger_count;
    RAISE NOTICE 'Materialized views:      %', v_wip_view_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Deployment completed at: %', NOW();
END $$;

-- =============================================================================
-- POST-DEPLOYMENT TASKS
-- =============================================================================

RAISE NOTICE '';
RAISE NOTICE '=============================================================================';
RAISE NOTICE 'Post-Deployment Tasks';
RAISE NOTICE '=============================================================================';
RAISE NOTICE '';
RAISE NOTICE 'Recommended Actions:';
RAISE NOTICE '';
RAISE NOTICE '1. Schedule Materialized View Refresh (pg_cron):';
RAISE NOTICE '   SELECT cron.schedule(''refresh-wip-views'', ''*/5 * * * *'', ''SELECT refresh_all_wip_views()'');';
RAISE NOTICE '';
RAISE NOTICE '2. Grant Permissions to Application User:';
RAISE NOTICE '   GRANT SELECT, INSERT, UPDATE ON wip_items TO mes_application;';
RAISE NOTICE '   GRANT SELECT, INSERT ON wip_process_history TO mes_application;';
RAISE NOTICE '   GRANT SELECT ON mv_wip_status_dashboard TO mes_readonly;';
RAISE NOTICE '   GRANT SELECT ON mv_process_wip_queue TO mes_readonly;';
RAISE NOTICE '';
RAISE NOTICE '3. Update Application Code:';
RAISE NOTICE '   - Import WipItem and WipProcessHistory models';
RAISE NOTICE '   - Update lot creation logic to generate WIP items';
RAISE NOTICE '   - Update process execution endpoints to use WIP tracking (processes 1-6)';
RAISE NOTICE '   - Update process 7 (Label Printing) to transition WIP → Serial';
RAISE NOTICE '';
RAISE NOTICE '4. Test WIP Tracking:';
RAISE NOTICE '   - Create test LOT';
RAISE NOTICE '   - Verify WIP items auto-generated';
RAISE NOTICE '   - Execute processes 1-6 with WIP IDs';
RAISE NOTICE '   - Verify Serial generation at process 7';
RAISE NOTICE '';
RAISE NOTICE '5. Monitor Performance:';
RAISE NOTICE '   - Check materialized view refresh times';
RAISE NOTICE '   - Monitor index usage with pg_stat_user_indexes';
RAISE NOTICE '   - Analyze query performance with EXPLAIN ANALYZE';
RAISE NOTICE '';
RAISE NOTICE '=============================================================================';
RAISE NOTICE 'WIP Tracking System Deployment Complete';
RAISE NOTICE '=============================================================================';

\timing off
