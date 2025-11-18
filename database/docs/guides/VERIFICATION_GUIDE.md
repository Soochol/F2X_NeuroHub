# F2X NeuroHub MES Database Verification Guide

## Overview

This guide explains how to use the comprehensive verification script (`verify.sql`) to validate the F2X NeuroHub MES database deployment.

## Quick Start

```bash
# Connect to PostgreSQL and run verification
psql -U postgres -d f2x_neurohub_mes -f verify.sql

# Or with output to file
psql -U postgres -d f2x_neurohub_mes -f verify.sql > verification_report.txt 2>&1
```

## Verification Categories

The script performs **9 comprehensive verification checks**:

### 1. Database Existence and Encoding

**Checks:**
- Database `f2x_neurohub_mes` exists
- Character encoding is UTF8
- Collation and CType settings

**Expected Result:**
```
PASS: Database exists: f2x_neurohub_mes
  - Encoding: UTF8
  - Collate: en_US.UTF-8
  - CType: en_US.UTF-8
```

---

### 2. Function Verification (14 Functions)

#### Common Functions (5)
| # | Function Name | Purpose |
|---|---------------|---------|
| 1 | `update_timestamp()` | Auto-update `updated_at` column |
| 2 | `log_audit_event()` | Comprehensive audit trail logging |
| 3 | `prevent_audit_modification()` | Enforce audit log immutability |
| 4 | `prevent_process_deletion()` | Protect processes with execution history |
| 5 | `prevent_user_deletion()` | Protect users with process data |

#### Table-Specific Functions (9)
| # | Function Name | Purpose |
|---|---------------|---------|
| 6 | `generate_lot_number()` | Auto-generate LOT number (WF-KR-YYMMDD{D\|N}-nnn) |
| 7 | `validate_lot_status_transition()` | Enforce LOT state machine |
| 8 | `auto_close_lot()` | Set `closed_at` when LOT completes |
| 9 | `generate_serial_number()` | Auto-generate serial number |
| 10 | `validate_lot_capacity()` | Enforce max 100 serials per LOT |
| 11 | `validate_serial_status_transition()` | Enforce serial state machine |
| 12 | `update_lot_quantities()` | Auto-update LOT quantity counters |
| 13 | `calculate_process_duration()` | Calculate process execution time |
| 14 | `validate_process_sequence()` | Enforce process order 1→2→3→...→8 |

**Expected Result:**
```
PASS: All functions present (14/14)
```

---

### 3. Table Verification (7 Tables)

| # | Table Name | Purpose | Columns | Type |
|---|------------|---------|---------|------|
| 1 | `product_models` | Product model definitions | 8 | Regular |
| 2 | `processes` | 8 manufacturing process definitions | 11 | Regular |
| 3 | `users` | User authentication and roles | 10 | Regular |
| 4 | `lots` | Production batch tracking (max 100 units) | 11 | Regular |
| 5 | `serials` | Individual unit tracking | 8 | Regular |
| 6 | `process_data` | Process execution records (transactional) | 13 | Regular |
| 7 | `audit_logs` | Immutable audit trail | 10 | **Partitioned** |

**Expected Result:**
```
PASS: All tables present (7/7)
```

---

### 4. Constraint Verification

#### 4.1 Primary Key Constraints (7 Expected)
All tables must have primary keys:
- `product_models.id`
- `processes.id`
- `users.id`
- `lots.id`
- `serials.id`
- `process_data.id`
- `audit_logs.id` (composite with `created_at` for partitioning)

#### 4.2 Foreign Key Constraints (7 Relationships)
| From Table | Column | To Table | Column | Referential Action |
|------------|--------|----------|--------|-------------------|
| `lots` | `product_model_id` | `product_models` | `id` | RESTRICT / CASCADE |
| `serials` | `lot_id` | `lots` | `id` | RESTRICT / CASCADE |
| `process_data` | `lot_id` | `lots` | `id` | RESTRICT / CASCADE |
| `process_data` | `serial_id` | `serials` | `id` | RESTRICT / CASCADE |
| `process_data` | `process_id` | `processes` | `id` | RESTRICT / CASCADE |
| `process_data` | `operator_id` | `users` | `id` | RESTRICT / CASCADE |
| `audit_logs` | `user_id` | `users` | `id` | RESTRICT / CASCADE |

#### 4.3 Unique Constraints (10+ Expected)
Key unique constraints:
- `product_models.model_code` (UNIQUE)
- `processes.process_number` (UNIQUE)
- `processes.process_code` (UNIQUE)
- `users.username` (UNIQUE)
- `users.email` (UNIQUE)
- `lots.lot_number` (UNIQUE)
- `serials.serial_number` (UNIQUE)
- `serials.(lot_id, sequence_in_lot)` (UNIQUE composite)

#### 4.4 Check Constraints (20+ Expected)
Examples:
- Status enumerations (e.g., `lots.status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED')`)
- Process number range (1-8)
- Quantity validations
- Email format validation
- Timestamp ordering

**Expected Result:**
```
PASS: All primary keys present (7/7)
PASS: Foreign keys found (7+)
PASS: Unique constraints found (10+)
PASS: Check constraints found (20+)
```

---

### 5. Index Verification (50+ Indexes)

#### Index Categories

**A. Primary Key Indexes (7)**
- Auto-created with primary key constraints

**B. Foreign Key Indexes (7+)**
- `idx_lots_product_model`
- `idx_serials_lot`
- `idx_process_data_lot`
- `idx_process_data_serial`
- `idx_process_data_process`
- `idx_process_data_operator`
- `idx_audit_logs_user`

**C. GIN Indexes on JSONB Columns (5+)**
| Table | Column | Index Name | Purpose |
|-------|--------|------------|---------|
| `product_models` | `specifications` | `idx_product_models_specifications` | JSON queries |
| `processes` | `quality_criteria` | `idx_processes_quality_criteria` | JSON queries |
| `process_data` | `measurements` | `idx_process_data_measurements` | JSON queries |
| `process_data` | `defects` | `idx_process_data_defects` | JSON queries |
| `audit_logs` | `old_values` | `idx_audit_logs_old_values` | JSON queries |
| `audit_logs` | `new_values` | `idx_audit_logs_new_values` | JSON queries |

**D. Partial Indexes (15+)**
Examples:
- `idx_product_models_status WHERE status = 'ACTIVE'`
- `idx_lots_active WHERE status IN ('CREATED', 'IN_PROGRESS')`
- `idx_serials_active WHERE status IN ('CREATED', 'IN_PROGRESS')`
- `idx_serials_failed WHERE status = 'FAILED'`

**E. Composite Indexes (20+)**
Examples:
- `idx_lots_model_date_shift(product_model_id, production_date, shift)`
- `idx_process_data_serial_process(serial_id, process_id, result)`
- `idx_audit_logs_entity_history(entity_type, entity_id, created_at DESC)`

**Expected Result:**
```
PASS: 50+ indexes found
PASS: GIN indexes on JSONB columns verified
PASS: Partial indexes verified
```

---

### 6. Trigger Verification (20+ Triggers)

#### Triggers by Table

**product_models (3 triggers)**
1. `trg_product_models_updated_at` - Auto-update timestamp
2. `trg_product_models_audit` - Audit logging
3. (Additional triggers as needed)

**processes (4 triggers)**
1. `trg_processes_updated_at` - Auto-update timestamp
2. `trg_processes_audit` - Audit logging
3. `trg_processes_prevent_delete` - Prevent deletion with data

**users (3 triggers)**
1. `trg_users_updated_at` - Auto-update timestamp
2. `trg_users_audit` - Audit logging
3. `trg_users_prevent_delete` - Prevent deletion with data

**lots (5 triggers)**
1. `trg_lots_generate_number` - Auto-generate LOT number
2. `trg_lots_updated_at` - Auto-update timestamp
3. `trg_lots_validate_status` - Validate status transitions
4. `trg_lots_auto_close` - Auto-close when completed
5. `trg_lots_audit` - Audit logging

**serials (6 triggers)**
1. `trg_serials_generate_number` - Auto-generate serial number
2. `trg_serials_updated_at` - Auto-update timestamp
3. `trg_serials_validate_status` - Validate status transitions
4. `trg_serials_update_lot_quantities` - Update LOT counters
5. `trg_serials_validate_lot_capacity` - Enforce capacity limit
6. `trg_serials_audit` - Audit logging

**process_data (4 triggers)**
1. `trg_process_data_calculate_duration` - Calculate duration
2. `trg_process_data_validate_sequence` - Enforce process order
3. `trg_process_data_update_serial_status` - Update serial status
4. `trg_process_data_audit` - Audit logging

**audit_logs (1 trigger)**
1. `trg_audit_logs_immutable` - Prevent UPDATE/DELETE

**Expected Result:**
```
PASS: 20+ triggers found
```

---

### 7. Master Data Verification (8 Processes)

#### Expected Process Data

| # | Process Code | Korean Name | English Name |
|---|--------------|-------------|--------------|
| 1 | `LASER_MARKING` | 레이저 마킹 | Laser Marking |
| 2 | `LMA_ASSEMBLY` | LMA 조립 | LMA Assembly |
| 3 | `SENSOR_INSPECTION` | 센서 검사 | Sensor Inspection |
| 4 | `FIRMWARE_UPLOAD` | 펌웨어 업로드 | Firmware Upload |
| 5 | `ROBOT_ASSEMBLY` | 로봇 조립 | Robot Assembly |
| 6 | `PERFORMANCE_TEST` | 성능검사 | Performance Test |
| 7 | `LABEL_PRINTING` | 라벨 프린팅 | Label Printing |
| 8 | `PACKAGING_INSPECTION` | 포장 + 외관검사 | Packaging & Visual Inspection |

**Verification Points:**
- All 8 processes exist
- Process numbers are 1-8
- Process codes match specification
- All processes are active (`is_active = TRUE`)
- Quality criteria JSONB is populated

**Expected Result:**
```
PASS: All 8 processes present
```

---

### 8. Partition Verification (audit_logs)

#### Partitioning Configuration

**Table Type:** Range Partitioned on `created_at`

**Initial Partitions (3 minimum):**
1. `audit_logs_y2025m11` - November 2025
2. `audit_logs_y2025m12` - December 2025
3. `audit_logs_y2026m01` - January 2026

**Partition Management Functions:**
1. `create_monthly_audit_partition(DATE)` - Create single partition
2. `create_future_audit_partitions(INTEGER)` - Create N months ahead
3. `drop_old_audit_partitions(INTEGER)` - Drop old partitions (3-year retention)

**Maintenance Procedure:**
- `maintain_audit_partitions()` - Monthly maintenance automation

**Expected Result:**
```
PASS: audit_logs is partitioned table
PASS: 3+ partitions found
PASS: Partition management functions exist
```

---

### 9. View Verification (Optional)

**Expected Views (if implemented):**
- 8 process-specific views (e.g., `v_laser_marking_data`, `v_lma_assembly_data`)
- Analytics views
- Dashboard views

**Expected Result:**
```
INFO: Process views found (optional feature)
```

---

## Interpreting Results

### PASS Status
```
PASS: Component verified successfully
```
All checks passed. Component is correctly deployed.

### WARNING Status
```
WARNING: Component found but count is lower than expected
```
Component exists but may be incomplete. Review the detailed output.

### FAIL Status
```
FAIL: Component missing or incorrect
```
Critical issue. Component must be fixed before production use.

---

## Troubleshooting

### Common Issues

#### Issue 1: Database Not Found
```sql
FAIL: Database f2x_neurohub_mes does not exist
```

**Solution:**
```bash
# Create database
psql -U postgres -c "CREATE DATABASE f2x_neurohub_mes WITH ENCODING 'UTF8';"

# Run deployment scripts
psql -U postgres -d f2x_neurohub_mes -f ddl/01_functions/*.sql
psql -U postgres -d f2x_neurohub_mes -f ddl/02_tables/*.sql
```

#### Issue 2: Missing Functions
```sql
FAIL: Missing X functions
```

**Solution:**
```bash
# Deploy functions
cd database/ddl/01_functions
for file in *.sql; do
    echo "Deploying $file..."
    psql -U postgres -d f2x_neurohub_mes -f "$file"
done
```

#### Issue 3: Missing Tables
```sql
FAIL: Missing X tables
```

**Solution:**
```bash
# Deploy tables in order
cd database/ddl/02_tables
for file in *.sql; do
    echo "Deploying $file..."
    psql -U postgres -d f2x_neurohub_mes -f "$file"
done
```

#### Issue 4: No Process Master Data
```sql
FAIL: No processes found in processes table
```

**Solution:**
The processes table DDL includes INSERT statements for the 8 processes. Re-run:
```bash
psql -U postgres -d f2x_neurohub_mes -f ddl/02_tables/02_processes.sql
```

#### Issue 5: Missing Partitions
```sql
WARNING: Only 0 partitions found
```

**Solution:**
```sql
-- Create initial partitions
SELECT create_future_audit_partitions(3);
```

---

## Complete Deployment Checklist

Use this checklist to ensure proper deployment:

- [ ] **Database Created** - `f2x_neurohub_mes` with UTF8 encoding
- [ ] **Functions Deployed** - All 14 functions present
- [ ] **Tables Created** - All 7 tables present
- [ ] **Constraints Applied** - PKs, FKs, Unique, Check constraints
- [ ] **Indexes Created** - 50+ indexes including GIN and partial
- [ ] **Triggers Attached** - 20+ triggers for automation
- [ ] **Master Data Loaded** - 8 processes inserted
- [ ] **Partitions Created** - 3+ audit_logs partitions
- [ ] **Permissions Granted** - Application roles configured
- [ ] **Verification Passed** - `verify.sql` returns PASS

---

## Automated Verification

### Using in CI/CD Pipeline

```bash
#!/bin/bash
# verify_deployment.sh

# Run verification
psql -U postgres -d f2x_neurohub_mes -f verify.sql > verification_report.txt 2>&1

# Check for failures
if grep -q "OVERALL STATUS: FAIL" verification_report.txt; then
    echo "Database verification FAILED"
    cat verification_report.txt
    exit 1
else
    echo "Database verification PASSED"
    exit 0
fi
```

### GitHub Actions Example

```yaml
name: Database Verification

on: [push, pull_request]

jobs:
  verify-database:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Database
        run: |
          # Deploy DDL scripts
          ./deploy.sh
      - name: Verify Database
        run: |
          psql -h localhost -U postgres -d f2x_neurohub_mes -f database/verify.sql
```

---

## Performance Metrics

After verification passes, consider running performance checks:

```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
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

-- Check missing indexes (NULL scans on large tables)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND seq_scan > 1000
AND idx_scan = 0
ORDER BY seq_tup_read DESC;
```

---

## Support and Documentation

### Related Documentation
- **Schema Design**: `database/docs/SCHEMA_DESIGN.md`
- **API Documentation**: `database/docs/API_GUIDE.md`
- **Deployment Guide**: `database/docs/DEPLOYMENT.md`

### Contact
For issues or questions:
- Database Team: database@f2x.com
- GitHub Issues: https://github.com/f2x/neurohub-mes

---

**Last Updated:** 2025-11-18
**Version:** 1.0
**Database Version:** PostgreSQL 14+
