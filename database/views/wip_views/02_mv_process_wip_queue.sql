-- =============================================================================
-- Materialized View: Process WIP Queue
-- F2X NeuroHub MES Database
-- =============================================================================
-- Purpose: Aggregates WIP items waiting at each process station for production
--          planning, resource allocation, and bottleneck identification.
--
-- Refresh Strategy: CONCURRENTLY (allows queries during refresh)
-- Recommended Refresh Interval: Every 1-2 minutes during production hours
--
-- Key Metrics:
--   - WIP count waiting at each process (1-6)
--   - Average wait time at each process
--   - Oldest WIP waiting time (alerts for stuck items)
--   - Process throughput rates
--
-- Usage:
--   SELECT * FROM mv_process_wip_queue;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_process_wip_queue;
-- =============================================================================

-- Drop existing view if present
DROP MATERIALIZED VIEW IF EXISTS mv_process_wip_queue CASCADE;

-- Create materialized view
CREATE MATERIALIZED VIEW mv_process_wip_queue AS
SELECT
    -- Process information
    p.id AS process_id,
    p.process_number,
    p.process_code,
    p.process_name_en,
    p.process_name_ko,
    p.estimated_duration_seconds,

    -- WIP queue metrics
    COUNT(wi.id) AS wip_count_at_process,
    COUNT(wi.id) FILTER (WHERE wi.status = 'IN_PROGRESS') AS in_progress_count,
    COUNT(wi.id) FILTER (WHERE wi.status = 'FAILED') AS failed_count,

    -- Timing metrics
    AVG(
        EXTRACT(EPOCH FROM (NOW() - wi.updated_at))
    )::INTEGER AS avg_wait_time_seconds,

    MAX(
        EXTRACT(EPOCH FROM (NOW() - wi.updated_at))
    )::INTEGER AS max_wait_time_seconds,

    MIN(wi.updated_at) AS oldest_wip_timestamp,

    -- Throughput metrics (last hour)
    COUNT(wph.id) FILTER (
        WHERE wph.completed_at >= NOW() - INTERVAL '1 hour'
    ) AS completed_last_hour,

    COUNT(wph.id) FILTER (
        WHERE wph.started_at >= NOW() - INTERVAL '1 hour'
          AND wph.result = 'PASS'
    ) AS passed_last_hour,

    COUNT(wph.id) FILTER (
        WHERE wph.started_at >= NOW() - INTERVAL '1 hour'
          AND wph.result = 'FAIL'
    ) AS failed_last_hour,

    -- Performance metrics
    ROUND(
        100.0 * COUNT(wph.id) FILTER (
            WHERE wph.started_at >= NOW() - INTERVAL '1 hour'
              AND wph.result = 'PASS'
        ) / NULLIF(COUNT(wph.id) FILTER (
            WHERE wph.completed_at >= NOW() - INTERVAL '1 hour'
        ), 0),
        2
    ) AS pass_rate_last_hour_pct,

    AVG(
        CASE
            WHEN wph.completed_at >= NOW() - INTERVAL '1 hour'
            THEN wph.duration_seconds
            ELSE NULL
        END
    )::INTEGER AS avg_process_duration_last_hour_seconds,

    -- Capacity metrics
    ROUND(
        p.estimated_duration_seconds * COUNT(wi.id) / 3600.0,
        2
    ) AS estimated_queue_time_hours,

    -- LOT distribution
    COUNT(DISTINCT wi.lot_id) AS lot_count_in_queue,

    -- Alert flags
    CASE
        WHEN MAX(EXTRACT(EPOCH FROM (NOW() - wi.updated_at))) > 3600 THEN true
        ELSE false
    END AS has_stuck_wip,  -- WIP waiting > 1 hour

    CASE
        WHEN COUNT(wi.id) > 50 THEN true
        ELSE false
    END AS is_bottleneck,  -- More than 50 WIP items queued

    -- Timestamp
    NOW() AS last_refreshed_at

FROM processes p
LEFT JOIN wip_items wi ON p.id = wi.current_process_id
    AND wi.status IN ('IN_PROGRESS', 'FAILED')
LEFT JOIN wip_process_history wph ON p.id = wph.process_id
WHERE p.is_active = true
  AND p.process_number BETWEEN 1 AND 6  -- Only WIP processes
GROUP BY
    p.id,
    p.process_number,
    p.process_code,
    p.process_name_en,
    p.process_name_ko,
    p.estimated_duration_seconds
ORDER BY p.process_number;

-- =============================================================================
-- UNIQUE INDEX (Required for CONCURRENT refresh)
-- =============================================================================
CREATE UNIQUE INDEX idx_mv_process_wip_queue_process_id
ON mv_process_wip_queue(process_id);

-- =============================================================================
-- ADDITIONAL INDEXES (for common query patterns)
-- =============================================================================

-- Index for process number queries
CREATE INDEX idx_mv_process_wip_queue_process_number
ON mv_process_wip_queue(process_number);

-- Index for bottleneck detection
CREATE INDEX idx_mv_process_wip_queue_bottleneck
ON mv_process_wip_queue(wip_count_at_process DESC)
WHERE is_bottleneck = true;

-- Index for stuck WIP alerts
CREATE INDEX idx_mv_process_wip_queue_stuck
ON mv_process_wip_queue(max_wait_time_seconds DESC)
WHERE has_stuck_wip = true;

-- Index for throughput analysis
CREATE INDEX idx_mv_process_wip_queue_throughput
ON mv_process_wip_queue(process_number, completed_last_hour DESC);

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON MATERIALIZED VIEW mv_process_wip_queue IS
'Process-level WIP queue aggregation for production monitoring and bottleneck detection.
Shows WIP counts, wait times, and throughput metrics for each process station.
Refresh every 1-2 minutes using:
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_process_wip_queue;';

COMMENT ON COLUMN mv_process_wip_queue.process_id IS 'Process primary key';
COMMENT ON COLUMN mv_process_wip_queue.process_number IS 'Process sequence number (1-6)';
COMMENT ON COLUMN mv_process_wip_queue.wip_count_at_process IS 'Total WIP items currently at this process';
COMMENT ON COLUMN mv_process_wip_queue.in_progress_count IS 'WIP items actively being processed';
COMMENT ON COLUMN mv_process_wip_queue.failed_count IS 'WIP items that failed at this process';
COMMENT ON COLUMN mv_process_wip_queue.avg_wait_time_seconds IS 'Average wait time for WIP items at this process';
COMMENT ON COLUMN mv_process_wip_queue.max_wait_time_seconds IS 'Maximum wait time (oldest WIP item)';
COMMENT ON COLUMN mv_process_wip_queue.completed_last_hour IS 'Process executions completed in last hour';
COMMENT ON COLUMN mv_process_wip_queue.passed_last_hour IS 'Process executions passed in last hour';
COMMENT ON COLUMN mv_process_wip_queue.failed_last_hour IS 'Process executions failed in last hour';
COMMENT ON COLUMN mv_process_wip_queue.pass_rate_last_hour_pct IS 'Pass rate percentage for last hour';
COMMENT ON COLUMN mv_process_wip_queue.avg_process_duration_last_hour_seconds IS 'Average actual process duration in last hour';
COMMENT ON COLUMN mv_process_wip_queue.estimated_queue_time_hours IS 'Estimated time to clear current queue (hours)';
COMMENT ON COLUMN mv_process_wip_queue.has_stuck_wip IS 'Alert flag: WIP item waiting > 1 hour';
COMMENT ON COLUMN mv_process_wip_queue.is_bottleneck IS 'Alert flag: Queue has > 50 WIP items';

-- =============================================================================
-- SAMPLE QUERIES
-- =============================================================================

/*
-- Current process queue overview
SELECT
    process_number,
    process_code,
    process_name_en,
    wip_count_at_process,
    avg_wait_time_seconds,
    max_wait_time_seconds,
    estimated_queue_time_hours
FROM mv_process_wip_queue
ORDER BY process_number;

-- Identify bottlenecks
SELECT
    process_number,
    process_code,
    process_name_en,
    wip_count_at_process,
    estimated_queue_time_hours,
    lot_count_in_queue
FROM mv_process_wip_queue
WHERE is_bottleneck = true
ORDER BY wip_count_at_process DESC;

-- Alert for stuck WIP items
SELECT
    process_number,
    process_code,
    process_name_en,
    wip_count_at_process,
    max_wait_time_seconds / 60.0 AS max_wait_minutes,
    oldest_wip_timestamp
FROM mv_process_wip_queue
WHERE has_stuck_wip = true
ORDER BY max_wait_time_seconds DESC;

-- Process throughput analysis
SELECT
    process_number,
    process_code,
    completed_last_hour,
    passed_last_hour,
    failed_last_hour,
    pass_rate_last_hour_pct,
    avg_process_duration_last_hour_seconds,
    estimated_duration_seconds
FROM mv_process_wip_queue
ORDER BY process_number;

-- Capacity planning report
SELECT
    process_code,
    process_name_en,
    wip_count_at_process AS current_queue,
    estimated_queue_time_hours AS hours_to_clear,
    completed_last_hour AS hourly_throughput,
    CASE
        WHEN completed_last_hour > 0
        THEN ROUND(wip_count_at_process::NUMERIC / completed_last_hour, 1)
        ELSE NULL
    END AS hours_at_current_rate
FROM mv_process_wip_queue
WHERE wip_count_at_process > 0
ORDER BY estimated_queue_time_hours DESC;
*/

-- =============================================================================
-- REFRESH FUNCTION (Optional - for scheduled refreshes)
-- =============================================================================

CREATE OR REPLACE FUNCTION refresh_process_wip_queue()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_process_wip_queue;
    RAISE NOTICE 'Process WIP Queue refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_process_wip_queue() IS
'Refreshes the Process WIP Queue materialized view.
Can be scheduled via pg_cron for automatic updates:
SELECT cron.schedule(''refresh-process-queue'', ''*/2 * * * *'', ''SELECT refresh_process_wip_queue()'');';

-- =============================================================================
-- REFRESH ALL WIP VIEWS FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION refresh_all_wip_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wip_status_dashboard;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_process_wip_queue;
    RAISE NOTICE 'All WIP materialized views refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_all_wip_views() IS
'Refreshes all WIP-related materialized views concurrently.
Recommended for scheduled batch refreshes:
SELECT cron.schedule(''refresh-all-wip-views'', ''*/5 * * * *'', ''SELECT refresh_all_wip_views()'');';

-- =============================================================================
-- END OF MATERIALIZED VIEW SCRIPT
-- =============================================================================
