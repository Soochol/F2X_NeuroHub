-- =============================================================================
-- File: 10_error_logs.sql
-- Description: Error logging table for F2X NeuroHub MES
-- Author: Database Architecture Team
-- Created: 2025-11-20
-- Modified: 2025-11-20
-- Version: 1.0
-- =============================================================================
-- Purpose:
--   Centralized error log table capturing all API errors for monitoring,
--   debugging, and analytics. Records 4xx/5xx HTTP errors with trace IDs
--   for frontend-backend correlation.
--
-- Business Requirements:
--   - Real-time error monitoring and alerting
--   - Debug support via trace_id correlation
--   - Error trend analysis for quality improvement
--   - User-specific error tracking
--   - Performance optimization via partitioning
-- =============================================================================

-- Drop existing objects if needed (for clean deployment)
DROP TABLE IF EXISTS error_logs CASCADE;

-- =============================================================================
-- MAIN TABLE DEFINITION (Partitioned)
-- =============================================================================
-- Create partitioned table for error logs
CREATE TABLE error_logs (
    -- Primary key
    id                  BIGSERIAL NOT NULL,

    -- Trace correlation
    trace_id            UUID NOT NULL UNIQUE,

    -- Error classification
    error_code          VARCHAR(20) NOT NULL,
    message             TEXT NOT NULL,

    -- Request context
    path                VARCHAR(500) NULL,
    method              VARCHAR(10) NULL,
    status_code         INTEGER NOT NULL,

    -- User tracking
    user_id             BIGINT NULL,

    -- Additional details (JSONB for flexible schema)
    details             JSONB NULL,

    -- Timestamp
    timestamp           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Primary key constraint (defined here for partitioned table)
    CONSTRAINT pk_error_logs PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Table documentation
COMMENT ON TABLE error_logs IS
'Centralized error logging table capturing all API errors for monitoring and debugging. Partitioned monthly by timestamp.';

-- Column documentation
COMMENT ON COLUMN error_logs.id IS 'Unique identifier for error log entry';
COMMENT ON COLUMN error_logs.trace_id IS 'Unique trace ID for correlating frontend-backend errors (matches StandardErrorResponse)';
COMMENT ON COLUMN error_logs.error_code IS 'Standardized error code from ErrorCode enum (e.g., RES_001, VAL_002)';
COMMENT ON COLUMN error_logs.message IS 'Human-readable error message';
COMMENT ON COLUMN error_logs.path IS 'API endpoint path where error occurred';
COMMENT ON COLUMN error_logs.method IS 'HTTP method (GET, POST, PUT, DELETE, PATCH)';
COMMENT ON COLUMN error_logs.status_code IS 'HTTP status code (4xx for client errors, 5xx for server errors)';
COMMENT ON COLUMN error_logs.user_id IS 'ID of user who triggered the error (NULL for unauthenticated requests)';
COMMENT ON COLUMN error_logs.details IS 'Additional error details in JSONB format (stack trace, field errors, etc.)';
COMMENT ON COLUMN error_logs.timestamp IS 'Timestamp when error occurred';

-- =============================================================================
-- CONSTRAINTS
-- =============================================================================

-- Foreign key to users table (nullable for unauthenticated requests)
ALTER TABLE error_logs
ADD CONSTRAINT fk_error_logs_user
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE SET NULL      -- Allow user deletion, set to NULL
ON UPDATE CASCADE;       -- Allow user ID updates to cascade

-- Check constraint for HTTP status codes (4xx and 5xx only)
ALTER TABLE error_logs
ADD CONSTRAINT chk_error_logs_status_code
CHECK (status_code >= 400 AND status_code < 600);

-- Check constraint for HTTP methods
ALTER TABLE error_logs
ADD CONSTRAINT chk_error_logs_method
CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'));

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Index 1: Time-based queries (most common access pattern)
CREATE INDEX idx_error_logs_timestamp
ON error_logs(timestamp DESC);

-- Index 2: Error code filtering with time ordering
CREATE INDEX idx_error_logs_error_code
ON error_logs(error_code, timestamp DESC);

-- Index 3: Trace ID lookup for debugging (unique index for fast search)
CREATE INDEX idx_error_logs_trace_id
ON error_logs(trace_id);

-- Index 4: User-specific error tracking
CREATE INDEX idx_error_logs_user_id
ON error_logs(user_id, timestamp DESC)
WHERE user_id IS NOT NULL;

-- Index 5: API endpoint error analysis
CREATE INDEX idx_error_logs_path
ON error_logs(path, timestamp DESC)
WHERE path IS NOT NULL;

-- Index 6: HTTP status code distribution analysis
CREATE INDEX idx_error_logs_status_code
ON error_logs(status_code, timestamp DESC);

-- Index 7: GIN index for JSONB search on details
CREATE INDEX idx_error_logs_details
ON error_logs USING gin(details);

-- =============================================================================
-- PARTITIONS
-- =============================================================================
-- Create initial partitions for operational months

-- Partition for November 2025
CREATE TABLE error_logs_y2025m11 PARTITION OF error_logs
FOR VALUES FROM ('2025-11-01 00:00:00+00') TO ('2025-12-01 00:00:00+00');

-- Partition for December 2025
CREATE TABLE error_logs_y2025m12 PARTITION OF error_logs
FOR VALUES FROM ('2025-12-01 00:00:00+00') TO ('2026-01-01 00:00:00+00');

-- Partition for January 2026
CREATE TABLE error_logs_y2026m01 PARTITION OF error_logs
FOR VALUES FROM ('2026-01-01 00:00:00+00') TO ('2026-02-01 00:00:00+00');

-- Add comments to partitions
COMMENT ON TABLE error_logs_y2025m11 IS 'Error logs partition for November 2025';
COMMENT ON TABLE error_logs_y2025m12 IS 'Error logs partition for December 2025';
COMMENT ON TABLE error_logs_y2026m01 IS 'Error logs partition for January 2026';

-- =============================================================================
-- PARTITION MANAGEMENT FUNCTIONS
-- =============================================================================

-- Function to create monthly partitions automatically
CREATE OR REPLACE FUNCTION create_monthly_error_log_partition(
    start_date DATE
)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    start_ts TIMESTAMP WITH TIME ZONE;
    end_ts TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Generate partition name
    partition_name := 'error_logs_y' || TO_CHAR(start_date, 'YYYY') ||
                     'm' || TO_CHAR(start_date, 'MM');

    -- Calculate partition boundaries
    start_ts := start_date::TIMESTAMP WITH TIME ZONE;
    end_ts := (start_date + INTERVAL '1 month')::TIMESTAMP WITH TIME ZONE;

    -- Check if partition already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_class
        WHERE relname = partition_name
    ) THEN
        -- Create the partition
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF error_logs ' ||
            'FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_ts, end_ts
        );

        -- Add comment
        EXECUTE format(
            'COMMENT ON TABLE %I IS %L',
            partition_name,
            'Error logs partition for ' || TO_CHAR(start_date, 'Month YYYY')
        );

        RAISE NOTICE 'Created partition: %', partition_name;
    ELSE
        RAISE NOTICE 'Partition % already exists', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_monthly_error_log_partition(DATE) IS
'Creates a monthly partition for error_logs table for the given start date';

-- Function to create partitions for the next N months
CREATE OR REPLACE FUNCTION create_future_error_log_partitions(
    months_ahead INTEGER DEFAULT 3
)
RETURNS void AS $$
DECLARE
    i INTEGER;
    partition_date DATE;
BEGIN
    FOR i IN 0..months_ahead-1 LOOP
        partition_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
        PERFORM create_monthly_error_log_partition(partition_date);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_future_error_log_partitions(INTEGER) IS
'Creates error_logs partitions for the specified number of months ahead';

-- Function to drop old partitions (for cleanup after retention period)
CREATE OR REPLACE FUNCTION drop_old_error_log_partitions(
    months_to_keep INTEGER DEFAULT 6  -- 6 months default retention for error logs
)
RETURNS void AS $$
DECLARE
    partition_record RECORD;
    cutoff_date DATE;
BEGIN
    cutoff_date := DATE_TRUNC('month', CURRENT_DATE - (months_to_keep || ' months')::INTERVAL);

    FOR partition_record IN
        SELECT
            schemaname,
            tablename
        FROM pg_tables
        WHERE tablename LIKE 'error_logs_y%'
        AND schemaname = 'public'
    LOOP
        -- Extract date from partition name (error_logs_yYYYYmMM)
        IF partition_record.tablename ~ '^error_logs_y\d{4}m\d{2}$' THEN
            DECLARE
                partition_year INTEGER;
                partition_month INTEGER;
                partition_date DATE;
            BEGIN
                partition_year := SUBSTRING(partition_record.tablename FROM 13 FOR 4)::INTEGER;
                partition_month := SUBSTRING(partition_record.tablename FROM 18 FOR 2)::INTEGER;
                partition_date := MAKE_DATE(partition_year, partition_month, 1);

                IF partition_date < cutoff_date THEN
                    RAISE NOTICE 'Dropping old partition: %', partition_record.tablename;
                    EXECUTE format('DROP TABLE IF EXISTS %I.%I',
                                 partition_record.schemaname,
                                 partition_record.tablename);
                END IF;
            END;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION drop_old_error_log_partitions(INTEGER) IS
'Drops error_logs partitions older than the specified number of months (default 6 months retention)';

-- =============================================================================
-- MAINTENANCE PROCEDURES
-- =============================================================================

-- Procedure to perform monthly maintenance
CREATE OR REPLACE PROCEDURE maintain_error_log_partitions()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Create partitions for next 3 months
    PERFORM create_future_error_log_partitions(3);

    -- Note: Uncomment the following line to enable automatic cleanup
    -- WARNING: This will permanently delete old error logs!
    -- PERFORM drop_old_error_log_partitions(6);  -- Keep 6 months

    -- Analyze statistics on current month's partition
    EXECUTE format(
        'ANALYZE error_logs_y%sm%s',
        TO_CHAR(CURRENT_DATE, 'YYYY'),
        TO_CHAR(CURRENT_DATE, 'MM')
    );
END;
$$;

COMMENT ON PROCEDURE maintain_error_log_partitions() IS
'Monthly maintenance procedure for error_logs partitions - creates future partitions and optionally drops old ones';

-- =============================================================================
-- SAMPLE QUERIES AND USAGE EXAMPLES
-- =============================================================================

/*
-- Example 1: Get recent errors (last 24 hours)
SELECT
    el.trace_id,
    el.error_code,
    el.message,
    el.path,
    el.method,
    el.status_code,
    u.username,
    el.timestamp
FROM error_logs el
LEFT JOIN users u ON el.user_id = u.id
WHERE el.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY el.timestamp DESC
LIMIT 100;

-- Example 2: Find error by trace_id (debugging)
SELECT
    el.*,
    u.username,
    u.email
FROM error_logs el
LEFT JOIN users u ON el.user_id = u.id
WHERE el.trace_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';

-- Example 3: Error statistics by error code (last 7 days)
SELECT
    error_code,
    COUNT(*) as error_count,
    COUNT(DISTINCT user_id) as affected_users,
    MIN(timestamp) as first_occurrence,
    MAX(timestamp) as last_occurrence
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY error_code
ORDER BY error_count DESC;

-- Example 4: Error trend by hour (last 24 hours)
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as error_count,
    COUNT(DISTINCT error_code) as unique_error_codes
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- Example 5: Top error-prone API endpoints
SELECT
    path,
    method,
    COUNT(*) as error_count,
    ARRAY_AGG(DISTINCT error_code) as error_codes,
    AVG(status_code)::INTEGER as avg_status_code
FROM error_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
  AND path IS NOT NULL
GROUP BY path, method
ORDER BY error_count DESC
LIMIT 20;

-- Example 6: User error activity analysis
SELECT
    u.username,
    u.email,
    COUNT(*) as error_count,
    ARRAY_AGG(DISTINCT el.error_code) as error_types,
    MAX(el.timestamp) as last_error
FROM error_logs el
JOIN users u ON el.user_id = u.id
WHERE el.timestamp > NOW() - INTERVAL '30 days'
GROUP BY u.username, u.email
ORDER BY error_count DESC
LIMIT 50;

-- Example 7: 5xx server errors (critical monitoring)
SELECT
    error_code,
    message,
    path,
    COUNT(*) as occurrence_count,
    MAX(timestamp) as last_occurrence
FROM error_logs
WHERE status_code >= 500
  AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY error_code, message, path
ORDER BY occurrence_count DESC;

-- Example 8: Error details analysis (using JSONB)
SELECT
    trace_id,
    error_code,
    message,
    details->>'field' as error_field,
    details->>'code' as detail_code,
    timestamp
FROM error_logs
WHERE error_code = 'VAL_001'  -- Validation errors
  AND timestamp > NOW() - INTERVAL '7 days'
  AND details IS NOT NULL
ORDER BY timestamp DESC
LIMIT 100;
*/

-- =============================================================================
-- PERFORMANCE TUNING NOTES
-- =============================================================================

/*
PERFORMANCE CONSIDERATIONS:

1. PARTITION PRUNING:
   - Always include timestamp in WHERE clauses when possible
   - PostgreSQL will automatically exclude irrelevant partitions

2. JSONB INDEXING:
   - GIN indexes support containment operators (@>, <@)
   - For specific field queries, consider expression indexes:
     CREATE INDEX idx_error_logs_field_errors
     ON error_logs((details->'field_errors'))
     WHERE error_code = 'VAL_001';

3. VACUUM STRATEGY:
   - Autovacuum handles partitions independently
   - Consider more aggressive settings for current month:
     ALTER TABLE error_logs_y2025m11
     SET (autovacuum_vacuum_scale_factor = 0.01);

4. STATISTICS:
   - Update statistics after bulk inserts:
     ANALYZE error_logs_y2025m11;

5. RETENTION:
   - Error logs typically need shorter retention than audit logs
   - 6-month retention recommended (can be adjusted based on needs)
   - Archive to cold storage before deletion if long-term analysis needed
*/

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant appropriate permissions (adjust as needed)
GRANT SELECT ON error_logs TO readonly_role;
GRANT INSERT ON error_logs TO application_role;
GRANT SELECT, INSERT ON error_logs TO admin_role;
GRANT EXECUTE ON FUNCTION create_monthly_error_log_partition TO admin_role;
GRANT EXECUTE ON FUNCTION create_future_error_log_partitions TO admin_role;
GRANT EXECUTE ON FUNCTION drop_old_error_log_partitions TO admin_role;
GRANT EXECUTE ON PROCEDURE maintain_error_log_partitions TO admin_role;

-- Note: UPDATE and DELETE should be restricted (error logs should be append-only)

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify table structure
/*
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'error_logs'
ORDER BY ordinal_position;

-- Verify partitions
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'error_logs%'
ORDER BY tablename;

-- Verify constraints
SELECT
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'error_logs'::regclass;

-- Verify indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'error_logs'
ORDER BY indexname;
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================
