# Alembic Setup Instructions

## Overview
The Alembic migration system has been successfully configured for the F2X NeuroHub project. All necessary files have been created and are ready to use.

## Setup Completed

### 1. Configuration Files Created
- **`backend/alembic.ini`** - Main Alembic configuration file
- **`backend/alembic/env.py`** - Environment configuration that integrates with app settings
- **`backend/alembic/script.py.mako`** - Template for new migrations
- **`backend/alembic/versions/`** - Directory containing migration files

### 2. Migrations Created
- **`0001_initial.py`** - Initial migration creating all 17 tables:
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

- **`add_auto_print_label_to_processes.py`** - Adds auto-print label configuration

### 3. Helper Scripts Created
- **`backend/manage_db.py`** - Database management without CLI
- **`backend/verify_alembic.py`** - Verification script
- **`backend/database/README_MIGRATIONS.md`** - Detailed migration guide

## Installation Requirements

Before using Alembic, you need to install the Python dependencies:

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt
```

Key dependencies:
- alembic==1.13.0
- sqlalchemy==2.0.23
- pydantic-settings==2.1.0

## Quick Start

### Option 1: Using Alembic CLI (after installing dependencies)

```bash
cd backend

# Check current database version
alembic current

# Apply all migrations
alembic upgrade head

# View migration history
alembic history
```

### Option 2: Using manage_db.py script

```bash
cd backend

# Initialize database (creates all tables)
python manage_db.py init

# Or use Alembic migrations
python manage_db.py upgrade
python manage_db.py current
python manage_db.py history
```

## Features Configured

### 1. Database Support
- **SQLite**: For local development (default)
- **PostgreSQL**: For production deployment
- Auto-detection based on DATABASE_URL

### 2. SQLAlchemy 2.0 Integration
- Uses modern declarative style
- Proper type hints
- JSONB support for both SQLite and PostgreSQL

### 3. Model Auto-Detection
- Automatically imports all 17 models
- Detects schema changes when using `--autogenerate`
- Proper foreign key relationships

### 4. Migration Features
- Batch operations for SQLite compatibility
- Compare types and server defaults
- Proper index and constraint handling

## Configuration Details

### Database URL
Set in `.env` file or environment:
```env
# SQLite (Development)
DATABASE_URL=sqlite:///./dev.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/f2x_neurohub
```

### Alembic Configuration
The system reads database URL from `app.config.settings`, which loads from:
1. Environment variables
2. `.env` file
3. Default values in `app/config.py`

## Migration Workflow

### Creating New Migrations

1. **Modify your models** in `app/models/`

2. **Generate migration automatically**:
   ```bash
   alembic revision --autogenerate -m "description"
   ```

3. **Review the generated file** in `alembic/versions/`

4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

### Manual Migrations

For complex changes:
```bash
alembic revision -m "custom_migration"
```

Then edit the file to add custom upgrade/downgrade logic.

## Verification

To verify the setup:
```bash
python verify_alembic.py
```

This will check:
- Alembic installation
- Configuration files
- Model imports
- Database connection
- Available migrations

## Troubleshooting

### "No module named alembic"
Install dependencies: `pip install -r requirements.txt`

### "No module named pydantic_settings"
Install dependencies: `pip install pydantic-settings==2.1.0`

### Database doesn't exist
1. Create it with: `python manage_db.py init`
2. Or use migrations: `alembic upgrade head`

### Permission errors on Windows
Run command prompt as Administrator or use WSL.

## Next Steps

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python manage_db.py init
   # or
   alembic upgrade head
   ```

3. **Verify the setup**:
   ```bash
   alembic current
   ```

4. **Start using migrations** for any schema changes!

## Summary

The Alembic migration system is now fully configured and ready to use. All necessary files have been created with:

- Proper SQLAlchemy 2.0 support
- Both SQLite and PostgreSQL compatibility
- All 17 models included in initial migration
- Helper scripts for easier management
- Comprehensive documentation

Once dependencies are installed, the system is ready for database versioning and migrations.