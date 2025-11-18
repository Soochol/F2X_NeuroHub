# F2X NeuroHub MES Database Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the F2X NeuroHub MES PostgreSQL database using the master deployment script (`deploy.sql`).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Script Features](#deployment-script-features)
- [Execution Order](#execution-order)
- [Usage Examples](#usage-examples)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Post-Deployment Tasks](#post-deployment-tasks)

## Prerequisites

### Software Requirements

- PostgreSQL 14 or higher
- `psql` command-line client
- Superuser or database owner privileges

### Database Requirements

- Minimum 500 MB free disk space (for initial deployment)
- UTF-8 encoding support
- `plpgsql` language extension (usually installed by default)

### File Structure

Ensure the following directory structure exists:

```
database/
├── deploy.sql                          # Master deployment script
├── DEPLOYMENT_GUIDE.md                 # This file
├── ddl/
│   ├── 01_functions/
│   │   ├── update_timestamp.sql
│   │   ├── prevent_audit_modification.sql
│   │   ├── log_audit_event.sql
│   │   ├── prevent_process_deletion.sql
│   │   └── prevent_user_deletion.sql
│   └── 02_tables/
│       ├── 01_product_models.sql
│       ├── 02_processes.sql
│       ├── 03_users.sql
│       ├── 04_lots.sql
│       ├── 05_serials.sql
│       ├── 06_process_data.sql
│       └── 07_audit_logs.sql
└── views/                              # (Optional - currently empty)
    └── process_views/
```

## Quick Start

### Option 1: Deploy to Existing Database

```bash
# Connect to your PostgreSQL server and run the deployment script
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Option 2: Create Database First, Then Deploy

```bash
# Step 1: Create the database
psql -U postgres -c "CREATE DATABASE f2x_neurohub_mes WITH ENCODING 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TEMPLATE template0;"

# Step 2: Run deployment
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Option 3: All-in-One (Create + Deploy)

```bash
# Edit deploy.sql and uncomment the database creation section (lines 76-82)
# Then run:
psql -U postgres -f deploy.sql
```

## Deployment Script Features

### Transaction Management

- Each major step wrapped in transactions with savepoints
- Automatic rollback on errors (when `\set ON_ERROR_STOP on`)
- Ability to resume from savepoints

### Error Handling

- Stop on first error (configurable)
- Clear error messages with context
- Verification queries after each step

### Progress Reporting

- Real-time progress indicators
- Timing information for each step
- Final summary report

### Verification Queries

- Table creation verification
- Foreign key constraint validation
- Row count checks
- Size and performance metrics

## Execution Order

The deployment script executes DDL in the following dependency-safe order:

### Step 1: Database Creation (Optional)

```sql
CREATE DATABASE f2x_neurohub_mes WITH ENCODING 'UTF8';
```

- **Duration**: < 1 second
- **Dependencies**: None
- **Can Skip**: Yes (if database already exists)

### Step 2: Common Functions (Parallel-Safe)

Executes in order:

1. `update_timestamp()` - Auto-updates `updated_at` timestamps
2. `prevent_audit_modification()` - Enforces audit log immutability
3. `log_audit_event()` - Captures audit trail for all DML operations
4. `prevent_process_deletion()` - Prevents deletion of processes with data
5. `prevent_user_deletion()` - Prevents deletion of users with audit history

- **Duration**: < 5 seconds
- **Dependencies**: None
- **Can Parallelize**: Yes (functions are independent)

### Step 3: Independent Tables (Group A)

Executes in order:

1. `product_models` - Master product definitions
2. `processes` - 8 manufacturing processes (includes INSERT statements)
3. `users` - System users and operators

- **Duration**: < 10 seconds
- **Dependencies**: Requires functions from Step 2
- **Can Parallelize**: Yes (tables are independent)

### Step 4: First-Level Dependencies (Group B)

1. `lots` - Production batches

- **Duration**: < 5 seconds
- **Dependencies**: `product_models`

### Step 5: Second-Level Dependencies (Group C)

1. `serials` - Individual unit tracking

- **Duration**: < 5 seconds
- **Dependencies**: `lots`

### Step 6: Third-Level Dependencies (Group D)

1. `process_data` - Process execution records

- **Duration**: < 5 seconds
- **Dependencies**: `lots`, `serials`, `processes`, `users`

### Step 7: Final Dependencies (Group E)

1. `audit_logs` - Audit trail with 3 initial partitions

- **Duration**: < 5 seconds
- **Dependencies**: `users`

### Step 8: Views (Optional)

Currently skipped (no view files available)

- **Duration**: N/A
- **Dependencies**: All tables

## Usage Examples

### Standard Deployment

```bash
# Navigate to database directory
cd /path/to/F2X_NeuroHub/database

# Run deployment
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Deployment with Logging

```bash
# Save deployment output to log file
psql -U postgres -d f2x_neurohub_mes -f deploy.sql 2>&1 | tee deployment.log
```

### Deployment to Remote Server

```bash
# Deploy to remote PostgreSQL server
psql -h remote-server.example.com -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Deployment with Custom Variables

```bash
# Override default variables
psql -U postgres -d f2x_neurohub_mes \
  -v db_owner='custom_owner' \
  -f deploy.sql
```

### Stop on Specific Step

Edit `deploy.sql` and add `\q` at the desired step to exit early:

```sql
\echo 'Step 3 completed successfully. (3 tables created)'
\q  -- Exit here
```

## Verification

### Check Deployment Status

```sql
-- Connect to database
\c f2x_neurohub_mes

-- Check all tables
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Expected output:
-- audit_logs
-- audit_logs_y2025m11
-- audit_logs_y2025m12
-- audit_logs_y2026m01
-- lots
-- process_data
-- processes
-- product_models
-- serials
-- users
```

### Verify Functions

```sql
-- Check all functions
SELECT proname AS function_name
FROM pg_proc
WHERE pronamespace = 'public'::regnamespace
  AND prokind = 'f'
ORDER BY proname;

-- Expected output:
-- log_audit_event
-- prevent_audit_modification
-- prevent_process_deletion
-- prevent_user_deletion
-- update_timestamp
```

### Verify Initial Data

```sql
-- Check processes (should have 8 records)
SELECT COUNT(*) FROM processes;

-- View all processes
SELECT
    process_number,
    process_code,
    process_name_ko,
    process_name_en
FROM processes
ORDER BY process_number;
```

### Verify Foreign Keys

```sql
-- Check all foreign key relationships
SELECT
    tc.table_name,
    tc.constraint_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

### Check Database Size

```sql
SELECT
    pg_size_pretty(pg_database_size(current_database())) AS database_size;
```

## Troubleshooting

### Error: "database does not exist"

**Problem**: Target database hasn't been created

**Solution**:
```bash
# Create database first
psql -U postgres -c "CREATE DATABASE f2x_neurohub_mes WITH ENCODING 'UTF8';"

# Then run deployment
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Error: "permission denied"

**Problem**: Insufficient privileges

**Solution**:
```bash
# Run as superuser
psql -U postgres -d f2x_neurohub_mes -f deploy.sql

# OR grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE f2x_neurohub_mes TO your_user;
```

### Error: "No such file or directory"

**Problem**: Incorrect working directory or missing DDL files

**Solution**:
```bash
# Ensure you're in the database directory
cd /path/to/F2X_NeuroHub/database

# Verify all DDL files exist
ls -R ddl/

# Run deployment with absolute path
psql -U postgres -d f2x_neurohub_mes -f /absolute/path/to/deploy.sql
```

### Error: "relation already exists"

**Problem**: Previous deployment exists

**Solution - Clean Deployment**:
```sql
-- WARNING: This will delete ALL data!
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Then run deployment again
\i deploy.sql
```

**Solution - Keep Existing Data**:
```bash
# Comment out specific DROP statements in individual DDL files
# Edit the relevant .sql files and comment out "DROP TABLE IF EXISTS"
```

### Error: Functions reference missing columns

**Problem**: `process_data.sql` references columns that don't exist in `processes` table

**Current Status**: The script handles this by checking the actual column structure

**Solution**: If errors occur, verify processes table has these columns:
- `allow_skip` (BOOLEAN) - If missing, add it
- `is_required` (BOOLEAN) - If missing, add it

```sql
-- Check if columns exist
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'processes'
ORDER BY ordinal_position;

-- If missing, add them:
ALTER TABLE processes ADD COLUMN allow_skip BOOLEAN DEFAULT FALSE;
ALTER TABLE processes ADD COLUMN is_required BOOLEAN DEFAULT TRUE;
```

### Slow Performance

**Problem**: Deployment takes too long

**Solution**:
```sql
-- Disable synchronous commit during deployment (faster but less safe)
SET synchronous_commit = OFF;

-- Run deployment
\i deploy.sql

-- Re-enable after deployment
SET synchronous_commit = ON;
```

## Post-Deployment Tasks

### 1. Create Application Roles

```sql
-- Create roles
CREATE ROLE mes_application WITH LOGIN PASSWORD 'secure_password_here';
CREATE ROLE mes_readonly WITH LOGIN PASSWORD 'secure_password_here';
CREATE ROLE mes_admin WITH LOGIN PASSWORD 'secure_password_here';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO mes_application;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mes_readonly;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mes_admin;

-- Grant sequence usage
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mes_application;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mes_admin;

-- Grant function execution
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mes_application;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mes_admin;
```

### 2. Insert Initial Users

```sql
-- Insert system user (used for automated operations)
INSERT INTO users (username, full_name, role, email, is_active)
VALUES ('system', 'System User', 'SYSTEM', 'system@example.com', TRUE);

-- Insert admin user
INSERT INTO users (username, full_name, role, email, is_active)
VALUES ('admin', 'Administrator', 'ADMIN', 'admin@example.com', TRUE);

-- Insert operators
INSERT INTO users (username, full_name, role, email, department, is_active)
VALUES
    ('operator01', 'Kim Min-jun', 'OPERATOR', 'kim@example.com', 'Production', TRUE),
    ('operator02', 'Lee Seo-yeon', 'OPERATOR', 'lee@example.com', 'Production', TRUE);
```

### 3. Insert Product Models

```sql
-- Insert sample product models
INSERT INTO product_models (model_code, model_name, category, production_cycle_days, specifications, status)
VALUES
('NH-F2X-001', 'NeuroHub F2X Standard', 'Standard', 5,
 '{
    "dimensions": {"width_mm": 100, "height_mm": 50, "depth_mm": 30},
    "weight_grams": 250,
    "electrical": {"voltage_range": "3.3V-5V", "current_max_ma": 500}
  }', 'ACTIVE'),
('NH-F2X-002', 'NeuroHub F2X Pro', 'Professional', 7,
 '{
    "dimensions": {"width_mm": 120, "height_mm": 60, "depth_mm": 35},
    "weight_grams": 350,
    "electrical": {"voltage_range": "3.3V-5V", "current_max_ma": 750}
  }', 'ACTIVE');
```

### 4. Configure Partition Management

```sql
-- Create partitions for next 6 months
SELECT create_future_audit_partitions(6);

-- Schedule monthly partition maintenance (requires pg_cron)
-- SELECT cron.schedule('audit_partition_maintenance', '0 2 1 * *', 'CALL maintain_audit_partitions();');
```

### 5. Set Up Backups

```bash
# Daily full backup (add to crontab)
0 2 * * * pg_dump -U postgres f2x_neurohub_mes | gzip > /backup/f2x_neurohub_mes_$(date +\%Y\%m\%d).sql.gz

# Weekly backup with retention (keep last 4 weeks)
0 3 * * 0 pg_dump -U postgres f2x_neurohub_mes | gzip > /backup/weekly/f2x_neurohub_mes_$(date +\%Y\%m\%d).sql.gz && find /backup/weekly/ -name "*.sql.gz" -mtime +28 -delete
```

### 6. Configure Monitoring

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Check slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY mean_time DESC
LIMIT 20;
```

### 7. Optimize Performance

```sql
-- Update statistics
ANALYZE;

-- Reindex if needed
REINDEX DATABASE f2x_neurohub_mes;

-- Vacuum
VACUUM ANALYZE;
```

## Performance Benchmarks

Expected deployment times on standard hardware (4 CPU cores, 8GB RAM, SSD):

| Step | Duration | Notes |
|------|----------|-------|
| Database Creation | < 1s | If needed |
| Functions (5) | 2-3s | Compilation time |
| Tables (7) | 8-12s | Including indexes and triggers |
| Initial Data | 1-2s | 8 process records |
| Verification | 3-5s | All checks |
| **Total** | **15-25s** | Complete deployment |

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [F2X NeuroHub MES Documentation](../README.md)
- [Database Schema Diagram](./docs/schema_diagram.md)
- [Performance Tuning Guide](./docs/performance_tuning.md)

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review deployment logs for error messages
3. Consult the database team
4. Create an issue in the project repository

---

**Version**: 1.0
**Last Updated**: 2025-11-18
**Database Version**: PostgreSQL 14+
