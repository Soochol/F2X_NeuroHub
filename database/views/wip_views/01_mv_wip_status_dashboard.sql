-- =============================================================================
-- Materialized View: WIP Status Dashboard
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Provides real-time WIP item status overview for production dashboards
--          with aggregated metrics by LOT, status, and process location.
--
-- Refresh Strategy: CONCURRENTLY (allows queries during refresh)
-- Recommended Refresh Interval: Every 1-5 minutes during production hours
--
-- Key Metrics:
--   - WIP count by status (CREATED, IN_PROGRESS, COMPLETED, FAILED)
--   - Current process location distribution
--   - Average cycle time per WIP item
--   - Process completion rates
--
-- Usage:
--   SELECT * FROM mv_wip_status_dashboard;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wip_status_dashboard;
-- =============================================================================

-- Drop existing view if present
DROP MATERIALIZED VIEW IF EXISTS mv_wip_status_dashboard CASCADE;

-- Create materialized view
CREATE MATERIALIZED VIEW mv_wip_status_dashboard AS
SELECT
    -- LOT information
    l.id AS lot_id,
    l.lot_number,
    l.product_model_id,
    l.production_date,
    l.shift,
    l.status AS lot_status,

    -- WIP status breakdown
    COUNT(wi.id) AS total_wip_count,
    COUNT(wi.id) FILTER (WHERE wi.status = 'CREATED') AS created_count,
    COUNT(wi.id) FILTER (WHERE wi.status = 'IN_PROGRESS') AS in_progress_count,
    COUNT(wi.id) FILTER (WHERE wi.status = 'COMPLETED') AS completed_count,
    COUNT(wi.id) FILTER (WHERE wi.status = 'FAILED') AS failed_count,

    -- Process location distribution (processes 1-6)
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 1) AS at_process_1_count,
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 2) AS at_process_2_count,
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 3) AS at_process_3_count,
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 4) AS at_process_4_count,
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 5) AS at_process_5_count,
    COUNT(wi.id) FILTER (WHERE wi.current_process_id IS NOT NULL AND p.process_number = 6) AS at_process_6_count,

    -- Completion metrics
    ROUND(
        100.0 * COUNT(wi.id) FILTER (WHERE wi.status = 'COMPLETED') / NULLIF(COUNT(wi.id), 0),
        2
    ) AS completion_rate_pct,

    ROUND(
        100.0 * COUNT(wi.id) FILTER (WHERE wi.status = 'FAILED') / NULLIF(COUNT(wi.id), 0),
        2
    ) AS failure_rate_pct,

    -- Timing metrics
    AVG(
        EXTRACT(EPOCH FROM (COALESCE(wi.completed_at, NOW()) - wi.created_at))
    )::INTEGER AS avg_cycle_time_seconds,

    MIN(wi.created_at) AS first_wip_created_at,
    MAX(wi.completed_at) AS last_wip_completed_at,

    -- Timestamp
    NOW() AS last_refreshed_at

FROM lots l
LEFT JOIN wip_items wi ON l.id = wi.lot_id
LEFT JOIN processes p ON wi.current_process_id = p.id
WHERE l.status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED')  -- Active and recent LOTs
GROUP BY
    l.id,
    l.lot_number,
    l.product_model_id,
    l.production_date,
    l.shift,
    l.status;

-- =============================================================================
-- UNIQUE INDEX (Required for CONCURRENT refresh)
-- =============================================================================
CREATE UNIQUE INDEX idx_mv_wip_status_dashboard_lot_id
ON mv_wip_status_dashboard(lot_id);

-- =============================================================================
-- ADDITIONAL INDEXES (for common query patterns)
-- =============================================================================

-- Index for date-based queries
CREATE INDEX idx_mv_wip_status_dashboard_production_date
ON mv_wip_status_dashboard(production_date DESC, lot_number);

-- Index for status filtering
CREATE INDEX idx_mv_wip_status_dashboard_lot_status
ON mv_wip_status_dashboard(lot_status, production_date DESC);

-- Index for product model filtering
CREATE INDEX idx_mv_wip_status_dashboard_product_model
ON mv_wip_status_dashboard(product_model_id, production_date DESC);

-- Index for completion rate analysis
CREATE INDEX idx_mv_wip_status_dashboard_completion_rate
ON mv_wip_status_dashboard(completion_rate_pct DESC)
WHERE completion_rate_pct IS NOT NULL;

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON MATERIALIZED VIEW mv_wip_status_dashboard IS
'Real-time WIP status dashboard providing aggregated metrics by LOT.
Includes WIP counts by status, process location distribution, and cycle times.
Refresh every 1-5 minutes during production using:
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wip_status_dashboard;';

COMMENT ON COLUMN mv_wip_status_dashboard.lot_id IS 'LOT primary key';
COMMENT ON COLUMN mv_wip_status_dashboard.lot_number IS 'LOT number identifier';
COMMENT ON COLUMN mv_wip_status_dashboard.total_wip_count IS 'Total WIP items in this LOT';
COMMENT ON COLUMN mv_wip_status_dashboard.created_count IS 'WIP items in CREATED status';
COMMENT ON COLUMN mv_wip_status_dashboard.in_progress_count IS 'WIP items in IN_PROGRESS status';
COMMENT ON COLUMN mv_wip_status_dashboard.completed_count IS 'WIP items in COMPLETED status (transitioned to Serial)';
COMMENT ON COLUMN mv_wip_status_dashboard.failed_count IS 'WIP items in FAILED status';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_1_count IS 'WIP items currently at Process 1 (Laser Marking)';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_2_count IS 'WIP items currently at Process 2 (LMA Assembly)';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_3_count IS 'WIP items currently at Process 3 (Sensor Inspection)';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_4_count IS 'WIP items currently at Process 4 (Firmware Upload)';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_5_count IS 'WIP items currently at Process 5 (Robot Assembly)';
COMMENT ON COLUMN mv_wip_status_dashboard.at_process_6_count IS 'WIP items currently at Process 6 (Performance Test)';
COMMENT ON COLUMN mv_wip_status_dashboard.completion_rate_pct IS 'Percentage of WIP items completed';
COMMENT ON COLUMN mv_wip_status_dashboard.failure_rate_pct IS 'Percentage of WIP items failed';
COMMENT ON COLUMN mv_wip_status_dashboard.avg_cycle_time_seconds IS 'Average cycle time per WIP item in seconds';
COMMENT ON COLUMN mv_wip_status_dashboard.last_refreshed_at IS 'Timestamp of last materialized view refresh';

-- =============================================================================
-- SAMPLE QUERIES
-- =============================================================================

/*
-- Get today's WIP status overview
SELECT
    lot_number,
    total_wip_count,
    in_progress_count,
    completed_count,
    failed_count,
    completion_rate_pct,
    avg_cycle_time_seconds
FROM mv_wip_status_dashboard
WHERE production_date = CURRENT_DATE
ORDER BY lot_number;

-- Find LOTs with high failure rates
SELECT
    lot_number,
    production_date,
    total_wip_count,
    failed_count,
    failure_rate_pct
FROM mv_wip_status_dashboard
WHERE failure_rate_pct > 5.0
ORDER BY failure_rate_pct DESC;

-- Process bottleneck analysis
SELECT
    lot_number,
    production_date,
    at_process_1_count AS laser_marking,
    at_process_2_count AS lma_assembly,
    at_process_3_count AS sensor_inspection,
    at_process_4_count AS firmware_upload,
    at_process_5_count AS robot_assembly,
    at_process_6_count AS performance_test
FROM mv_wip_status_dashboard
WHERE lot_status = 'IN_PROGRESS'
ORDER BY production_date DESC;

-- Production efficiency report
SELECT
    production_date,
    COUNT(*) AS lot_count,
    SUM(total_wip_count) AS total_wips,
    SUM(completed_count) AS completed_wips,
    ROUND(AVG(completion_rate_pct), 2) AS avg_completion_rate,
    ROUND(AVG(avg_cycle_time_seconds), 0) AS avg_cycle_time_sec
FROM mv_wip_status_dashboard
WHERE production_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY production_date
ORDER BY production_date DESC;
*/

-- =============================================================================
-- REFRESH FUNCTION (Optional - for scheduled refreshes)
-- =============================================================================

CREATE OR REPLACE FUNCTION refresh_wip_status_dashboard()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wip_status_dashboard;
    RAISE NOTICE 'WIP Status Dashboard refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_wip_status_dashboard() IS
'Refreshes the WIP status dashboard materialized view.
Can be called manually or scheduled via pg_cron:
SELECT cron.schedule(''refresh-wip-dashboard'', ''*/5 * * * *'', ''SELECT refresh_wip_status_dashboard()'');';

-- =============================================================================
-- END OF MATERIALIZED VIEW SCRIPT
-- =============================================================================
