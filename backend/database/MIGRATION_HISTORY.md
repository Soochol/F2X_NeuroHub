# Migration History

## Overview

This document tracks the complete migration history for the F2X NeuroHub database, including when migrations were applied, their purpose, and rollback procedures.

## Migration Chain

```
0001_initial
    ↓
0002_add_wip_support_to_process_data
    ↓
0003_add_wip_unique_index
```

## Detailed Migration History

### 0001_initial
- **Revision ID**: 0001_initial
- **Applied**: 2025-11-23 (via Alembic initialization)
- **Purpose**: Initial database schema creation
- **Tables Created**:
  - users
  - product_models
  - production_lines
  - processes
  - equipment
  - lots
  - wip_items
  - serials
  - process_data
  - wip_process_history
  - audit_log
  - alerts
  - error_log
  - print_log
- **Dependencies**: None (base migration)
- **Rollback**: `alembic downgrade -1` (WARNING: Drops all tables)

### 0002_add_wip_support_to_process_data
- **Revision ID**: 0002_add_wip_support
- **Applied**: 2025-11-23 (consolidated from manual migrations)
- **Original Manual Application**: 2025-11-22 to 2025-11-23
- **Purpose**: Add comprehensive WIP support to process_data table
- **Changes**:
  - Added lot_id column (BIGINT, NOT NULL)
  - Added foreign key constraint to lots table
  - Updated data_level constraint to support 'LOT', 'WIP', 'SERIAL'
  - Added consistency check constraint for data_level combinations
  - Added performance indexes for lot_id queries
- **Dependencies**: Requires 0001_initial
- **Rollback Procedure**:
  ```bash
  alembic downgrade 0001_initial
  ```
  **WARNING**: Rollback will remove LOT-level process data

### 0003_add_wip_unique_index
- **Revision ID**: 0003_add_wip_unique_index
- **Applied**: 2025-11-23 (consolidated from manual migration)
- **Original Manual Application**: 2025-11-23
- **Purpose**: Add unique constraint for WIP-level process tracking
- **Changes**:
  - Added unique partial index: uq_process_data_lot_process_wip
  - Index on (lot_id, process_id, wip_id) WHERE wip_id IS NOT NULL
  - Prevents duplicate WIP process entries
  - Allows multiple LOT-level entries for same process
- **Dependencies**: Requires 0002_add_wip_support
- **Rollback Procedure**:
  ```bash
  alembic downgrade 0002_add_wip_support
  ```
  **Note**: Safe rollback, only removes index

## Database Compatibility

All migrations support both:
- **PostgreSQL**: Full feature support with partial indexes
- **SQLite**: Compatible with table recreation strategy for schema changes

## Migration Commands

### Check Current Version
```bash
alembic current
```

### Apply All Migrations
```bash
alembic upgrade head
```

### Apply Specific Migration
```bash
alembic upgrade 0002_add_wip_support
```

### Rollback One Migration
```bash
alembic downgrade -1
```

### Rollback to Specific Version
```bash
alembic downgrade 0001_initial
```

### View Migration History
```bash
alembic history
```

## Important Notes

1. **Production Rollbacks**: Always backup database before rollback operations
2. **Data Loss**: Some rollbacks may cause data loss (especially 0002 rollback)
3. **Manual Migrations**: The original manual migrations (now .bak files) should NOT be executed
4. **Version Tracking**: The alembic_version table tracks applied migrations

## Troubleshooting

### If Alembic version is out of sync:
1. Check actual database state
2. Manually update alembic_version table if needed:
   ```sql
   UPDATE alembic_version SET version_num = '0003_add_wip_unique_index';
   ```

### If migration fails:
1. Check error logs
2. Verify database connectivity
3. Ensure proper permissions
4. Check for conflicting data

## Future Migrations

All new migrations should:
1. Use Alembic format
2. Include both upgrade() and downgrade() functions
3. Support both PostgreSQL and SQLite
4. Document changes in this file
5. Test rollback procedures before production deployment