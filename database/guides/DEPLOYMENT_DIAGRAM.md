# F2X NeuroHub MES - Deployment Execution Diagram

## Overview

This document provides visual representations of the deployment execution order and dependencies.

## Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STEP 1: DATABASE CREATION (Optional)             │
│                                                                     │
│  CREATE DATABASE f2x_neurohub_mes WITH ENCODING 'UTF8';            │
│                                                                     │
│  Duration: < 1 second                                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STEP 2: COMMON FUNCTIONS (Parallel-Safe)               │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐   │
│  │ update_timestamp()   │  │ prevent_audit_modification()     │   │
│  └──────────────────────┘  └──────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐   │
│  │ log_audit_event()    │  │ prevent_process_deletion()       │   │
│  └──────────────────────┘  └──────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────┐                              │
│  │ prevent_user_deletion()          │                              │
│  └──────────────────────────────────┘                              │
│                                                                     │
│  Objects: 5 functions                                               │
│  Duration: 2-3 seconds                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 3: INDEPENDENT TABLES - Group A (Parallel-Safe)        │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ product_models  │  │    processes    │  │      users      │   │
│  │   (Master)      │  │  (8 processes)  │  │   (Operators)   │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                     │
│  Objects: 3 tables                                                  │
│  Initial Data: 8 process records                                    │
│  Duration: 8-12 seconds                                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 4: FIRST-LEVEL DEPENDENCIES - Group B                  │
│                                                                     │
│                     ┌─────────────────┐                             │
│                     │      lots       │                             │
│                     │  (Production    │                             │
│                     │   Batches)      │                             │
│                     └─────────────────┘                             │
│                             │                                       │
│                             │ FK: product_model_id                  │
│                             │                                       │
│                             ▼                                       │
│                     product_models                                  │
│                                                                     │
│  Objects: 1 table                                                   │
│  Duration: < 5 seconds                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│        STEP 5: SECOND-LEVEL DEPENDENCIES - Group C                  │
│                                                                     │
│                     ┌─────────────────┐                             │
│                     │     serials     │                             │
│                     │  (Individual    │                             │
│                     │     Units)      │                             │
│                     └─────────────────┘                             │
│                             │                                       │
│                             │ FK: lot_id                            │
│                             │                                       │
│                             ▼                                       │
│                          lots                                       │
│                                                                     │
│  Objects: 1 table                                                   │
│  Duration: < 5 seconds                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│         STEP 6: THIRD-LEVEL DEPENDENCIES - Group D                  │
│                                                                     │
│                   ┌─────────────────────┐                           │
│                   │   process_data      │                           │
│                   │  (Process Records)  │                           │
│                   └─────────────────────┘                           │
│                            │                                        │
│         ┌──────────────────┼──────────────────┬────────────┐       │
│         │                  │                  │            │       │
│    FK: lot_id        FK: serial_id     FK: process_id  FK: operator_id
│         │                  │                  │            │       │
│         ▼                  ▼                  ▼            ▼       │
│       lots             serials            processes      users     │
│                                                                     │
│  Objects: 1 table                                                   │
│  Duration: < 5 seconds                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│             STEP 7: FINAL DEPENDENCIES - Group E                    │
│                                                                     │
│                     ┌─────────────────┐                             │
│                     │   audit_logs    │                             │
│                     │ (Audit Trail +  │                             │
│                     │   3 Partitions) │                             │
│                     └─────────────────┘                             │
│                             │                                       │
│                             │ FK: user_id                           │
│                             │                                       │
│                             ▼                                       │
│                          users                                      │
│                                                                     │
│  Objects: 1 table + 3 partitions                                    │
│  Partitions: y2025m11, y2025m12, y2026m01                          │
│  Duration: < 5 seconds                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                STEP 8: VIEWS (Optional - Skipped)                   │
│                                                                     │
│  No views to create (files not found)                              │
│                                                                     │
│  Duration: N/A                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  FINAL VERIFICATION & SUMMARY                       │
│                                                                     │
│  ✓ Functions: 5                                                     │
│  ✓ Tables: 7                                                        │
│  ✓ Partitions: 3                                                    │
│  ✓ Initial Data: 8 process records                                  │
│  ✓ Foreign Keys: 6 relationships                                    │
│  ✓ Triggers: ~30 triggers                                           │
│                                                                     │
│  Total Duration: 15-25 seconds                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Dependency Graph

```
                    ┌──────────────────────┐
                    │    FUNCTIONS (5)     │
                    │  (No Dependencies)   │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
    │ product_models  │ │processes │ │     users       │
    │   (Group A)     │ │(Group A) │ │   (Group A)     │
    └────────┬────────┘ └────┬─────┘ └────────┬────────┘
             │               │                 │
             ▼               │                 │
    ┌─────────────────┐     │                 │
    │      lots       │     │                 │
    │   (Group B)     │     │                 │
    └────────┬────────┘     │                 │
             │               │                 │
             ▼               │                 │
    ┌─────────────────┐     │                 │
    │    serials      │     │                 │
    │   (Group C)     │     │                 │
    └────────┬────────┘     │                 │
             │               │                 │
             └───────┬───────┘                 │
                     │                         │
                     ▼                         │
            ┌─────────────────┐                │
            │ process_data    │◄───────────────┤
            │   (Group D)     │                │
            └─────────────────┘                │
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │   audit_logs    │
                                      │   (Group E)     │
                                      └─────────────────┘
```

## Foreign Key Relationships

```
product_models (id)
    └──> lots (product_model_id)
            └──> serials (lot_id)
                    └──> process_data (serial_id)

lots (id)
    └──> process_data (lot_id)

processes (id)
    └──> process_data (process_id)

users (id)
    ├──> process_data (operator_id)
    └──> audit_logs (user_id)
```

## Table Characteristics

| Table | Type | Indexes | Triggers | Partitioned | Initial Data |
|-------|------|---------|----------|-------------|--------------|
| product_models | Master | 4 | 2 | No | 0 rows |
| processes | Master | 4 | 3 | No | 8 rows |
| users | Master | 5 | 3 | No | 0 rows |
| lots | Transaction | 6 | 4 | No | 0 rows |
| serials | Transaction | 6 | 5 | No | 0 rows |
| process_data | Transaction | 11 | 4 | No (future) | 0 rows |
| audit_logs | Audit | 9 | 1 | Yes (monthly) | 0 rows |

## Transaction Boundaries

```
┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_functions;                            │
│  ├─ Create 5 functions                                  │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_independent_tables;                   │
│  ├─ Create product_models                               │
│  ├─ Create processes (+ INSERT 8 rows)                  │
│  ├─ Create users                                        │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_lots_table;                           │
│  ├─ Create lots                                         │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_serials_table;                        │
│  ├─ Create serials                                      │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_process_data_table;                   │
│  ├─ Create process_data                                 │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─ BEGIN TRANSACTION ─────────────────────────────────────┐
│                                                          │
│  SAVEPOINT before_audit_logs_table;                     │
│  ├─ Create audit_logs                                   │
│  ├─ Create partition y2025m11                           │
│  ├─ Create partition y2025m12                           │
│  ├─ Create partition y2026m01                           │
│  └─ COMMIT (or ROLLBACK on error)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Error Recovery Strategy

```
Error in Step 2 (Functions)?
  └─> ROLLBACK to before_functions
      └─> Fix function SQL
          └─> Retry from Step 2

Error in Step 3 (Independent Tables)?
  └─> ROLLBACK to before_independent_tables
      └─> Fix table SQL
          └─> Retry from Step 3

Error in Step 4 (lots)?
  └─> ROLLBACK to before_lots_table
      └─> Verify product_models exists
          └─> Fix lots SQL
              └─> Retry from Step 4

... (similar pattern for other steps)
```

## Performance Timeline

```
Time (seconds)
0s    ─┬─ START
      │
      ├─ [0-1s]   Database creation (if needed)
      │
1s    ├─ [1-3s]   Create 5 functions
      │
3s    ├─ [3-15s]  Create 3 tables + indexes + triggers + 8 process records
      │
15s   ├─ [15-18s] Create lots table
      │
18s   ├─ [18-21s] Create serials table
      │
21s   ├─ [21-24s] Create process_data table
      │
24s   ├─ [24-27s] Create audit_logs + 3 partitions
      │
27s   ├─ [27-30s] Verification queries
      │
30s   ─┴─ END (Total: 15-25 seconds typical)
```

## Rollback Scenarios

### Full Rollback (Clean State)

```sql
-- WARNING: Destroys all data!
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Then re-run deployment
\i deploy.sql
```

### Partial Rollback (Specific Table)

```sql
-- Example: Rollback just the audit_logs table
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS audit_logs_y2025m11;
DROP TABLE IF EXISTS audit_logs_y2025m12;
DROP TABLE IF EXISTS audit_logs_y2026m01;

-- Then re-create just that table
\i ddl/02_tables/07_audit_logs.sql
```

### Continue from Savepoint

```sql
-- If error occurred during transaction
ROLLBACK TO SAVEPOINT before_lots_table;

-- Fix the issue, then continue
\i ddl/02_tables/04_lots.sql
COMMIT;
```

## Best Practices

1. **Always backup before deployment** (if deploying to existing database)
   ```bash
   pg_dump f2x_neurohub_mes > backup_before_deploy.sql
   ```

2. **Test deployment on dev/staging first**
   ```bash
   createdb f2x_neurohub_mes_test
   psql -d f2x_neurohub_mes_test -f deploy.sql
   ```

3. **Monitor deployment progress**
   ```bash
   psql -d f2x_neurohub_mes -f deploy.sql 2>&1 | tee deployment.log
   ```

4. **Verify after deployment**
   ```sql
   SELECT COUNT(*) FROM processes;  -- Should be 8
   SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';  -- Should be 10
   ```

5. **Check for errors in log**
   ```bash
   grep -i "error\|failed\|exception" deployment.log
   ```

---

**Diagram Version**: 1.0
**Last Updated**: 2025-11-18
**Compatible with**: deploy.sql v1.0
