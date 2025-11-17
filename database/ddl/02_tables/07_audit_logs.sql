-- =============================================================================
-- File: 07_audit_logs.sql
-- Description: Comprehensive audit trail table for F2X NeuroHub MES
-- Author: Database Architecture Team
-- Created: 2025-11-10
-- Modified: 2025-11-18
-- Version: 1.0
-- =============================================================================
-- Purpose:
--   Immutable audit log table capturing all system changes for compliance,
--   security, and traceability. Records CREATE/UPDATE/DELETE operations on
--   all critical entities with before/after snapshots.
--
-- Business Requirements:
--   - Regulatory compliance (3-year retention)
--   - Security monitoring and forensics
--   - Change history for troubleshooting
--   - User accountability
--   - Immutable records (append-only)
-- =============================================================================

-- Drop existing objects if needed (for clean deployment)
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP FUNCTION IF EXISTS prevent_audit_modification() CASCADE;

-- =============================================================================
-- TRIGGER FUNCTION
-- =============================================================================
-- Create function to prevent modification of audit logs
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION prevent_audit_modification() IS
'Trigger function to enforce immutability of audit logs - prevents UPDATE and DELETE operations';

-- =============================================================================
-- MAIN TABLE DEFINITION (Partitioned)
-- =============================================================================
-- Create partitioned table for audit logs
CREATE TABLE audit_logs (
    -- Primary key
    id                  BIGSERIAL NOT NULL,

    -- User tracking
    user_id             BIGINT NOT NULL,

    -- Entity identification
    entity_type         VARCHAR(50) NOT NULL,
    entity_id           BIGINT NOT NULL,

    -- Action tracking
    action              VARCHAR(10) NOT NULL,

    -- Data snapshots (JSONB for flexible schema)
    old_values          JSONB NULL,
    new_values          JSONB NULL,

    -- Client information
    ip_address          VARCHAR(45) NULL,      -- Supports both IPv4 and IPv6
    user_agent          TEXT NULL,

    -- Timestamp
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Primary key constraint (defined here for partitioned table)
    CONSTRAINT pk_audit_logs PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Table documentation
COMMENT ON TABLE audit_logs IS
'Immutable audit trail capturing all system changes for compliance and security. Partitioned monthly by created_at.';

-- Column documentation
COMMENT ON COLUMN audit_logs.id IS 'Unique identifier for audit log entry';
COMMENT ON COLUMN audit_logs.user_id IS 'ID of user who performed the action (FK to users table)';
COMMENT ON COLUMN audit_logs.entity_type IS 'Name of the table/entity being audited';
COMMENT ON COLUMN audit_logs.entity_id IS 'Primary key of the affected record in entity_type table';
COMMENT ON COLUMN audit_logs.action IS 'Type of operation: CREATE, UPDATE, or DELETE';
COMMENT ON COLUMN audit_logs.old_values IS 'Complete record snapshot before change (NULL for CREATE)';
COMMENT ON COLUMN audit_logs.new_values IS 'Complete record snapshot after change (NULL for DELETE)';
COMMENT ON COLUMN audit_logs.ip_address IS 'Client IP address (IPv4 or IPv6 format)';
COMMENT ON COLUMN audit_logs.user_agent IS 'Client user agent string for security analysis';
COMMENT ON COLUMN audit_logs.created_at IS 'Timestamp when audit entry was created';

-- =============================================================================
-- CONSTRAINTS
-- =============================================================================

-- Foreign key to users table
ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_user
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE RESTRICT      -- Prevent deletion of users with audit history
ON UPDATE CASCADE;       -- Allow user ID updates to cascade

-- Check constraint for action types
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_action
CHECK (action IN ('CREATE', 'UPDATE', 'DELETE'));

-- Check constraint for entity types (allowed tables)
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_entity_type
CHECK (entity_type IN (
    'product_models',
    'lots',
    'serials',
    'processes',
    'process_data',
    'users',
    'audit_logs'
));

-- Check constraint for old_values based on action
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_old_values
CHECK (
    (action = 'CREATE' AND old_values IS NULL) OR
    (action IN ('UPDATE', 'DELETE') AND old_values IS NOT NULL)
);

-- Check constraint for new_values based on action
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_new_values
CHECK (
    (action = 'DELETE' AND new_values IS NULL) OR
    (action IN ('CREATE', 'UPDATE') AND new_values IS NOT NULL)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Index 1: Foreign key index for user lookups
CREATE INDEX idx_audit_logs_user
ON audit_logs(user_id);

-- Index 2: Entity tracking for specific record history
CREATE INDEX idx_audit_logs_entity
ON audit_logs(entity_type, entity_id);

-- Index 3: Action type filtering with time ordering
CREATE INDEX idx_audit_logs_action
ON audit_logs(action, created_at DESC);

-- Index 4: Time-based queries (most common access pattern)
CREATE INDEX idx_audit_logs_created_at
ON audit_logs(created_at DESC);

-- Index 5: User activity analysis
CREATE INDEX idx_audit_logs_user_activity
ON audit_logs(user_id, created_at DESC);

-- Index 6: Composite index for complete entity history
CREATE INDEX idx_audit_logs_entity_history
ON audit_logs(entity_type, entity_id, created_at DESC);

-- Index 7: GIN index for JSONB search on old_values
CREATE INDEX idx_audit_logs_old_values
ON audit_logs USING gin(old_values);

-- Index 8: GIN index for JSONB search on new_values
CREATE INDEX idx_audit_logs_new_values
ON audit_logs USING gin(new_values);

-- Index 9: IP-based security analysis (partial index)
CREATE INDEX idx_audit_logs_ip_address
ON audit_logs(ip_address, created_at DESC)
WHERE ip_address IS NOT NULL;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger to prevent UPDATE and DELETE operations (enforce immutability)
CREATE TRIGGER trg_audit_logs_immutable
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_modification();

COMMENT ON TRIGGER trg_audit_logs_immutable ON audit_logs IS
'Enforces immutability by preventing UPDATE and DELETE operations on audit logs';

-- =============================================================================
-- PARTITIONS
-- =============================================================================
-- Create initial partitions for operational months

-- Partition for November 2025
CREATE TABLE audit_logs_y2025m11 PARTITION OF audit_logs
FOR VALUES FROM ('2025-11-01 00:00:00+00') TO ('2025-12-01 00:00:00+00');

-- Partition for December 2025
CREATE TABLE audit_logs_y2025m12 PARTITION OF audit_logs
FOR VALUES FROM ('2025-12-01 00:00:00+00') TO ('2026-01-01 00:00:00+00');

-- Partition for January 2026
CREATE TABLE audit_logs_y2026m01 PARTITION OF audit_logs
FOR VALUES FROM ('2026-01-01 00:00:00+00') TO ('2026-02-01 00:00:00+00');

-- Add comments to partitions
COMMENT ON TABLE audit_logs_y2025m11 IS 'Audit logs partition for November 2025';
COMMENT ON TABLE audit_logs_y2025m12 IS 'Audit logs partition for December 2025';
COMMENT ON TABLE audit_logs_y2026m01 IS 'Audit logs partition for January 2026';

-- =============================================================================
-- PARTITION MANAGEMENT FUNCTIONS
-- =============================================================================

-- Function to create monthly partitions automatically
CREATE OR REPLACE FUNCTION create_monthly_audit_partition(
    start_date DATE
)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    start_ts TIMESTAMP WITH TIME ZONE;
    end_ts TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Generate partition name
    partition_name := 'audit_logs_y' || TO_CHAR(start_date, 'YYYY') ||
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
            'CREATE TABLE %I PARTITION OF audit_logs ' ||
            'FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_ts, end_ts
        );

        -- Add comment
        EXECUTE format(
            'COMMENT ON TABLE %I IS %L',
            partition_name,
            'Audit logs partition for ' || TO_CHAR(start_date, 'Month YYYY')
        );

        RAISE NOTICE 'Created partition: %', partition_name;
    ELSE
        RAISE NOTICE 'Partition % already exists', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_monthly_audit_partition(DATE) IS
'Creates a monthly partition for audit_logs table for the given start date';

-- Function to create partitions for the next N months
CREATE OR REPLACE FUNCTION create_future_audit_partitions(
    months_ahead INTEGER DEFAULT 3
)
RETURNS void AS $$
DECLARE
    i INTEGER;
    partition_date DATE;
BEGIN
    FOR i IN 0..months_ahead-1 LOOP
        partition_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
        PERFORM create_monthly_audit_partition(partition_date);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_future_audit_partitions(INTEGER) IS
'Creates audit_logs partitions for the specified number of months ahead';

-- Function to drop old partitions (for archival)
CREATE OR REPLACE FUNCTION drop_old_audit_partitions(
    months_to_keep INTEGER DEFAULT 36  -- 3 years default retention
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
        WHERE tablename LIKE 'audit_logs_y%'
        AND schemaname = 'public'
    LOOP
        -- Extract date from partition name (audit_logs_yYYYYmMM)
        IF partition_record.tablename ~ '^audit_logs_y\d{4}m\d{2}$' THEN
            DECLARE
                partition_year INTEGER;
                partition_month INTEGER;
                partition_date DATE;
            BEGIN
                partition_year := SUBSTRING(partition_record.tablename FROM 12 FOR 4)::INTEGER;
                partition_month := SUBSTRING(partition_record.tablename FROM 17 FOR 2)::INTEGER;
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

COMMENT ON FUNCTION drop_old_audit_partitions(INTEGER) IS
'Drops audit_logs partitions older than the specified number of months (default 36 months for 3-year retention)';

-- =============================================================================
-- MAINTENANCE PROCEDURES
-- =============================================================================

-- Procedure to perform monthly maintenance
CREATE OR REPLACE PROCEDURE maintain_audit_partitions()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Create partitions for next 3 months
    PERFORM create_future_audit_partitions(3);

    -- Note: Uncomment the following line to enable automatic cleanup
    -- WARNING: This will permanently delete old audit data!
    -- PERFORM drop_old_audit_partitions(36);  -- Keep 3 years

    -- Analyze statistics on current month's partition
    EXECUTE format(
        'ANALYZE audit_logs_y%sm%s',
        TO_CHAR(CURRENT_DATE, 'YYYY'),
        TO_CHAR(CURRENT_DATE, 'MM')
    );
END;
$$;

COMMENT ON PROCEDURE maintain_audit_partitions() IS
'Monthly maintenance procedure for audit_logs partitions - creates future partitions and optionally drops old ones';

-- =============================================================================
-- SAMPLE QUERIES AND USAGE EXAMPLES
-- =============================================================================

/*
-- Example 1: Get complete change history for a specific LOT
SELECT
    al.id,
    u.username,
    al.action,
    al.old_values,
    al.new_values,
    al.created_at
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'lots'
  AND al.entity_id = 123
ORDER BY al.created_at DESC;

-- Example 2: Find who changed a serial's status to FAILED
SELECT
    u.username,
    al.created_at,
    al.old_values->>'status' AS old_status,
    al.new_values->>'status' AS new_status,
    al.ip_address
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'serials'
  AND al.entity_id = 456
  AND al.action = 'UPDATE'
  AND al.new_values->>'status' = 'FAILED';

-- Example 3: Audit user activity summary for specific date
SELECT
    u.username,
    al.action,
    al.entity_type,
    COUNT(*) as change_count,
    MIN(al.created_at) as first_change,
    MAX(al.created_at) as last_change
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE DATE(al.created_at) = '2025-11-10'
GROUP BY u.username, al.action, al.entity_type
ORDER BY change_count DESC;

-- Example 4: Detect suspicious activity (many changes from single IP)
SELECT
    ip_address,
    COUNT(*) as change_count,
    COUNT(DISTINCT user_id) as user_count,
    array_agg(DISTINCT entity_type) as affected_entities,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen
FROM audit_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
  AND ip_address IS NOT NULL
GROUP BY ip_address
HAVING COUNT(*) > 100
ORDER BY change_count DESC;

-- Example 5: Track specific field changes using JSONB operators
SELECT
    entity_id,
    old_values->>'lot_status' as old_status,
    new_values->>'lot_status' as new_status,
    created_at
FROM audit_logs
WHERE entity_type = 'lots'
  AND action = 'UPDATE'
  AND old_values->>'lot_status' != new_values->>'lot_status'
ORDER BY created_at DESC
LIMIT 100;

-- Example 6: Find all deletes in last 24 hours
SELECT
    u.username,
    al.entity_type,
    al.entity_id,
    al.old_values,
    al.created_at,
    al.ip_address
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.action = 'DELETE'
  AND al.created_at > NOW() - INTERVAL '24 hours'
ORDER BY al.created_at DESC;
*/

-- =============================================================================
-- PARTITION MANAGEMENT AUTOMATION (CRON JOB EXAMPLE)
-- =============================================================================

/*
-- Add this to system crontab or pg_cron for automatic partition management:
-- Runs on the 1st of every month at 2:00 AM

-- Using pg_cron extension:
SELECT cron.schedule(
    'audit_partition_maintenance',
    '0 2 1 * *',  -- At 02:00 on day-of-month 1
    'CALL maintain_audit_partitions();'
);

-- Or using system cron with psql:
-- 0 2 1 * * psql -U dbuser -d neurohub -c "CALL maintain_audit_partitions();"
*/

-- =============================================================================
-- ARCHIVAL STRATEGY DOCUMENTATION
-- =============================================================================

/*
ARCHIVAL AND RETENTION STRATEGY:

1. RETENTION POLICY:
   - Active partitions: Keep for 12 months in primary database
   - Archive partitions: 12-36 months old, move to archive storage
   - Delete: After 36 months (3 years) per compliance requirements

2. ARCHIVAL PROCESS:

   Step 1: Export partition to archive format
   pg_dump -U dbuser -d neurohub -t audit_logs_y2022m01 -f /archive/audit_logs_y2022m01.sql

   Step 2: Compress archive file
   gzip /archive/audit_logs_y2022m01.sql

   Step 3: Upload to cold storage (S3, Azure Blob, etc.)
   aws s3 cp /archive/audit_logs_y2022m01.sql.gz s3://neurohub-archives/audit-logs/

   Step 4: Drop partition from primary database
   DROP TABLE audit_logs_y2022m01;

3. RESTORATION PROCESS:

   Step 1: Download from cold storage
   aws s3 cp s3://neurohub-archives/audit-logs/audit_logs_y2022m01.sql.gz /tmp/

   Step 2: Decompress
   gunzip /tmp/audit_logs_y2022m01.sql.gz

   Step 3: Restore partition
   psql -U dbuser -d neurohub -f /tmp/audit_logs_y2022m01.sql

   Step 4: Re-attach partition to parent table
   ALTER TABLE audit_logs ATTACH PARTITION audit_logs_y2022m01
   FOR VALUES FROM ('2022-01-01') TO ('2022-02-01');

4. MONITORING:
   - Monitor partition sizes monthly
   - Alert if partition creation fails
   - Track archival job success/failure
   - Validate 3-year retention compliance
*/

-- =============================================================================
-- PERFORMANCE TUNING NOTES
-- =============================================================================

/*
PERFORMANCE CONSIDERATIONS:

1. PARTITION PRUNING:
   - Always include created_at in WHERE clauses when possible
   - PostgreSQL will automatically exclude irrelevant partitions

2. JSONB INDEXING:
   - GIN indexes support containment operators (@>, <@)
   - For specific field queries, consider expression indexes:
     CREATE INDEX idx_audit_logs_lot_status
     ON audit_logs((new_values->>'lot_status'))
     WHERE entity_type = 'lots';

3. VACUUM STRATEGY:
   - Autovacuum handles partitions independently
   - Consider more aggressive settings for current month:
     ALTER TABLE audit_logs_y2025m11
     SET (autovacuum_vacuum_scale_factor = 0.01);

4. STATISTICS:
   - Update statistics after bulk inserts:
     ANALYZE audit_logs_y2025m11;

5. CONNECTION POOLING:
   - Use connection pooling for high-frequency audit writes
   - Consider async/batch inserts for non-critical audits
*/

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant appropriate permissions (adjust as needed)
GRANT SELECT ON audit_logs TO readonly_role;
GRANT INSERT ON audit_logs TO application_role;
GRANT SELECT ON audit_logs TO admin_role;
GRANT EXECUTE ON FUNCTION create_monthly_audit_partition TO admin_role;
GRANT EXECUTE ON FUNCTION create_future_audit_partitions TO admin_role;
GRANT EXECUTE ON FUNCTION drop_old_audit_partitions TO admin_role;
GRANT EXECUTE ON PROCEDURE maintain_audit_partitions TO admin_role;

-- Note: UPDATE and DELETE are blocked by trigger for all roles

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
WHERE table_name = 'audit_logs'
ORDER BY ordinal_position;

-- Verify partitions
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'audit_logs%'
ORDER BY tablename;

-- Verify constraints
SELECT
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'audit_logs'::regclass;

-- Verify indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'audit_logs'
ORDER BY indexname;

-- Verify triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table = 'audit_logs';
*/

-- =============================================================================
-- END OF SCRIPT
-- =============================================================================