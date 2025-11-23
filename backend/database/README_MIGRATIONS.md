# Database Migrations Guide

This document explains how to use Alembic migrations for the F2X NeuroHub MES database.

## Overview

We use Alembic for database schema versioning and migrations. Alembic tracks changes to the database schema and provides a way to upgrade and downgrade the database in a controlled manner.

## Configuration

- **Config File**: `backend/alembic.ini` - Main Alembic configuration
- **Environment**: `backend/alembic/env.py` - Runtime configuration that reads from `app.config.settings`
- **Migrations**: `backend/alembic/versions/` - Directory containing all migration files
- **Template**: `backend/alembic/script.py.mako` - Template for new migration files

## Common Commands

All commands should be run from the `backend/` directory.

### Check Current Database Version
```bash
alembic current
```

### View Migration History
```bash
alembic history
```

### Apply All Migrations (Upgrade to Latest)
```bash
alembic upgrade head
```

### Apply Specific Migration
```bash
alembic upgrade <revision>
# Example: alembic upgrade 0001_initial
```

### Rollback One Migration
```bash
alembic downgrade -1
```

### Rollback to Specific Migration
```bash
alembic downgrade <revision>
# Example: alembic downgrade 0001_initial
```

### Generate New Migration (Auto-detect Changes)
```bash
alembic revision --autogenerate -m "description of changes"
# Example: alembic revision --autogenerate -m "add_user_preferences_table"
```

### Create Empty Migration (Manual)
```bash
alembic revision -m "description of changes"
# Example: alembic revision -m "add_custom_indexes"
```

### Show SQL Without Applying
```bash
# Show SQL for upgrade
alembic upgrade head --sql

# Show SQL for specific migration
alembic upgrade <revision> --sql
```

## Creating New Migrations

### 1. Auto-Generated Migrations (Recommended)

When you modify SQLAlchemy models, Alembic can detect the changes:

```bash
# 1. Make changes to your models in app/models/
# 2. Generate migration
alembic revision --autogenerate -m "add_new_field_to_user"
# 3. Review the generated file in alembic/versions/
# 4. Apply the migration
alembic upgrade head
```

**Note**: Always review auto-generated migrations! Alembic may not detect all changes correctly, especially:
- Column type changes
- Column name changes (detected as drop + add)
- Table name changes
- Custom constraints or indexes

### 2. Manual Migrations

For complex changes or data migrations:

```bash
# Create empty migration
alembic revision -m "migrate_user_data"
```

Then edit the generated file:

```python
def upgrade() -> None:
    # Add your upgrade logic
    op.execute("UPDATE users SET role='viewer' WHERE role IS NULL")

def downgrade() -> None:
    # Add your downgrade logic
    op.execute("UPDATE users SET role=NULL WHERE role='viewer'")
```

## Best Practices

### 1. Always Review Auto-Generated Migrations
- Check that all intended changes are included
- Verify that no unintended changes are present
- Ensure proper handling of existing data

### 2. Test Migrations
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 3. Handle Data Migrations Carefully
- Always backup data before running migrations in production
- Test with a copy of production data if possible
- Consider the impact on existing data
- Provide safe rollback procedures

### 4. Migration Naming Convention
Use descriptive names that indicate what the migration does:
- `add_<table>_table` - Creating a new table
- `add_<column>_to_<table>` - Adding a column
- `remove_<column>_from_<table>` - Removing a column
- `rename_<old>_to_<new>` - Renaming tables/columns
- `add_index_to_<table>_<column>` - Adding indexes
- `migrate_<description>` - Data migrations

### 5. Never Edit Applied Migrations
Once a migration has been applied to any environment (dev, staging, production), never edit it. Create a new migration instead.

### 6. Coordinate Team Migrations
- Communicate when creating new migrations
- Pull latest migrations before creating new ones
- Resolve conflicts in migration order if they occur

## Troubleshooting

### Migration Conflicts
If two developers create migrations simultaneously:
1. One migration needs to update its `down_revision`
2. Test both migrations in sequence
3. Ensure both upgrades and downgrades work

### Failed Migration
If a migration fails:
1. Check the error message
2. Manually fix the database if partially applied
3. Mark the migration as applied if needed: `alembic stamp <revision>`

### Reset Database (Development Only)
```bash
# Drop all tables (PostgreSQL)
psql -d dbname -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Drop all tables (SQLite)
rm dev.db

# Recreate from migrations
alembic upgrade head
```

## Database Support

The migration system supports both:
- **SQLite**: For local development
- **PostgreSQL**: For production deployment

The system automatically detects the database type from `DATABASE_URL` and applies appropriate settings:
- SQLite uses batch operations for schema changes
- PostgreSQL supports more advanced features like JSONB

## Migration Files

Current migrations:
1. `0001_initial.py` - Initial database schema with all 17 tables
2. `add_auto_print_label_to_processes.py` - Adds auto-print label configuration to processes

## Environment Variables

Set in `.env` file:
```env
# SQLite (Development)
DATABASE_URL=sqlite:///./dev.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/f2x_neurohub
```

## Python Script Usage

You can also run migrations from Python code:

```python
from alembic import command
from alembic.config import Config

# Load configuration
alembic_cfg = Config("alembic.ini")

# Upgrade to latest
command.upgrade(alembic_cfg, "head")

# Get current revision
command.current(alembic_cfg)

# Downgrade one revision
command.downgrade(alembic_cfg, "-1")
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- Project Models: `backend/app/models/`
- Database Configuration: `backend/app/database.py`