# Deprecated Manual Migrations

## Overview

The following manual migration scripts have been deprecated and replaced with proper Alembic migrations as part of the migration system consolidation effort on 2025-11-23.

## Deprecated Scripts

### 1. add_wip_to_process_data.py.bak
- **Original Purpose**: Added wip_id column to process_data table with foreign key and index
- **Replaced By**: `alembic/versions/0002_add_wip_support_to_process_data.py`
- **Applied**: Manually on 2025-11-22

### 2. manual_add_wip_to_process_data.py.bak
- **Original Purpose**: Alternative manual script with enhanced error handling for adding wip_id
- **Replaced By**: `alembic/versions/0002_add_wip_support_to_process_data.py`
- **Applied**: Used as backup script on 2025-11-22

### 3. add_wip_unique_index.py.bak
- **Original Purpose**: Added unique partial index on (lot_id, process_id, wip_id)
- **Replaced By**: `alembic/versions/0003_add_wip_unique_index.py`
- **Applied**: Manually on 2025-11-23

### 4. update_process_data_constraints.py.bak
- **Original Purpose**: Updated process_data constraints to support LOT/WIP/SERIAL data levels
- **Replaced By**: `alembic/versions/0002_add_wip_support_to_process_data.py`
- **Applied**: Manually on 2025-11-23

## Why These Were Deprecated

1. **Lack of Version Control**: Manual scripts didn't track migration history
2. **No Rollback Support**: Limited or no downgrade functionality
3. **Inconsistent Format**: Each script had different structure and approach
4. **Database Compatibility**: Scripts were specific to either SQLite or PostgreSQL

## Migration to Alembic

These scripts have been consolidated into two Alembic migrations:

1. **0002_add_wip_support_to_process_data.py**:
   - Adds lot_id column
   - Adds wip_id support
   - Updates constraints for LOT/WIP/SERIAL data levels
   - Handles both SQLite and PostgreSQL

2. **0003_add_wip_unique_index.py**:
   - Adds unique partial index for WIP tracking
   - Supports both database systems

## Important Notes

- The `.bak` files are preserved for historical reference only
- DO NOT execute these scripts directly
- All future migrations should use Alembic
- The database already has these changes applied; the Alembic migrations are for tracking purposes

## Recovery

If you need to reference the original scripts:
1. They are preserved with `.bak` extension in this directory
2. Review but DO NOT execute them
3. Use Alembic migrations for any rollback needs