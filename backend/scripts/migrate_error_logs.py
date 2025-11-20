"""
Migration script to create error_logs table with partitioning.

This script creates the error_logs table with monthly partitioning
and necessary indexes for performance optimization.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine
from app.config import settings


def run_migration():
    """Execute the error_logs table migration."""

    migration_sql = """
    -- Create error_logs table with monthly partitioning
    CREATE TABLE IF NOT EXISTS error_logs (
        id SERIAL,
        trace_id UUID NOT NULL,
        error_code VARCHAR(20) NOT NULL,
        message TEXT NOT NULL,
        path VARCHAR(500),
        method VARCHAR(10),
        status_code INTEGER NOT NULL,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        details JSONB,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id, timestamp)
    ) PARTITION BY RANGE (timestamp);

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs (timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_error_logs_error_code ON error_logs (error_code);
    CREATE INDEX IF NOT EXISTS idx_error_logs_trace_id ON error_logs (trace_id);
    CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs (user_id);
    CREATE INDEX IF NOT EXISTS idx_error_logs_path ON error_logs (path);
    CREATE INDEX IF NOT EXISTS idx_error_logs_status_code ON error_logs (status_code);
    CREATE INDEX IF NOT EXISTS idx_error_logs_details ON error_logs USING GIN (details);

    -- Create initial monthly partitions (last 3 months + current + next 3 months)
    CREATE TABLE IF NOT EXISTS error_logs_y2025m10 PARTITION OF error_logs
        FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

    CREATE TABLE IF NOT EXISTS error_logs_y2025m11 PARTITION OF error_logs
        FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

    CREATE TABLE IF NOT EXISTS error_logs_y2025m12 PARTITION OF error_logs
        FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

    CREATE TABLE IF NOT EXISTS error_logs_y2026m01 PARTITION OF error_logs
        FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

    CREATE TABLE IF NOT EXISTS error_logs_y2026m02 PARTITION OF error_logs
        FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

    -- Function to create a new monthly partition
    CREATE OR REPLACE FUNCTION create_monthly_error_log_partition(year INT, month INT)
    RETURNS void AS $$
    DECLARE
        partition_name TEXT;
        start_date DATE;
        end_date DATE;
    BEGIN
        partition_name := 'error_logs_y' || year || 'm' || LPAD(month::TEXT, 2, '0');
        start_date := make_date(year, month, 1);
        end_date := start_date + INTERVAL '1 month';

        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF error_logs FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
    END;
    $$ LANGUAGE plpgsql;

    -- Function to drop old partitions (older than 6 months)
    CREATE OR REPLACE FUNCTION drop_old_error_log_partitions(retention_months INT DEFAULT 6)
    RETURNS void AS $$
    DECLARE
        partition_record RECORD;
        cutoff_date DATE;
    BEGIN
        cutoff_date := CURRENT_DATE - (retention_months || ' months')::INTERVAL;

        FOR partition_record IN
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename LIKE 'error_logs_y%'
        LOOP
            -- Extract year and month from partition name (e.g., error_logs_y2025m01)
            DECLARE
                year INT;
                month INT;
                partition_date DATE;
            BEGIN
                year := substring(partition_record.tablename FROM 'y(\d{4})m')::INT;
                month := substring(partition_record.tablename FROM 'm(\d{2})')::INT;
                partition_date := make_date(year, month, 1);

                IF partition_date < cutoff_date THEN
                    EXECUTE format('DROP TABLE IF EXISTS %I', partition_record.tablename);
                    RAISE NOTICE 'Dropped partition: %', partition_record.tablename;
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING 'Could not process partition: % - %', partition_record.tablename, SQLERRM;
            END;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """

    print("Running error_logs table migration...")

    try:
        with engine.begin() as conn:
            # Split and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"Executing statement {i}/{len(statements)}...")
                    conn.execute(text(statement))

        print("✅ Migration completed successfully!")
        print("\nCreated:")
        print("  - error_logs table (partitioned by timestamp)")
        print("  - Indexes for performance optimization")
        print("  - Monthly partitions (2025-10 to 2026-02)")
        print("  - Partition management functions")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_migration()
