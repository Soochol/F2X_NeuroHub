#!/usr/bin/env python
"""
Database management script for F2X NeuroHub.

This script provides database operations without requiring the Alembic CLI.
It can be used when Alembic is installed but the CLI is not available.

Usage:
    python manage_db.py init        # Initialize database with all tables
    python manage_db.py current     # Show current revision
    python manage_db.py upgrade     # Upgrade to latest
    python manage_db.py downgrade   # Downgrade one revision
    python manage_db.py history     # Show migration history
"""

import sys
import argparse
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def init_database():
    """Initialize database with all tables using SQLAlchemy."""
    print("Initializing database...")
    try:
        from app.database import Base, engine
        from app.models import (  # noqa: F401
            User, ProductModel, Process, Lot, WIPItem, Serial,
            ProcessData, WIPProcessHistory, AuditLog, Alert,
            ProductionLine, Equipment, ErrorLog, PrintLog
        )

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully!")

        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nCreated {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        return False
    return True


def run_alembic_command(command, *args):
    """Run an Alembic command programmatically."""
    try:
        from alembic.config import Config
        from alembic import command as alembic_cmd

        alembic_cfg = Config(str(backend_dir / "alembic.ini"))

        if command == "current":
            alembic_cmd.current(alembic_cfg)
        elif command == "upgrade":
            target = args[0] if args else "head"
            print(f"Upgrading database to {target}...")
            alembic_cmd.upgrade(alembic_cfg, target)
            print("[OK] Database upgraded successfully!")
        elif command == "downgrade":
            target = args[0] if args else "-1"
            print(f"Downgrading database to {target}...")
            alembic_cmd.downgrade(alembic_cfg, target)
            print("[OK] Database downgraded successfully!")
        elif command == "history":
            alembic_cmd.history(alembic_cfg)
        elif command == "stamp":
            revision = args[0] if args else "head"
            print(f"Stamping database with revision {revision}...")
            alembic_cmd.stamp(alembic_cfg, revision)
            print("[OK] Database stamped successfully!")
        else:
            print(f"[ERROR] Unknown command: {command}")
            return False

    except ImportError:
        print("[ERROR] Alembic is not installed.")
        print("Please install it with: pip install alembic==1.13.0")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to run Alembic command '{command}': {e}")
        return False

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database management for F2X NeuroHub"
    )

    parser.add_argument(
        "command",
        choices=["init", "current", "upgrade", "downgrade", "history", "stamp"],
        help="Command to execute"
    )

    parser.add_argument(
        "target",
        nargs="?",
        help="Target revision (for upgrade/downgrade/stamp)"
    )

    args = parser.parse_args()

    # Print header
    print("F2X NeuroHub - Database Management")
    print("=" * 60)

    # Check database configuration
    try:
        from app.config import settings
        db_type = "SQLite" if "sqlite" in settings.DATABASE_URL else "PostgreSQL"
        print(f"Database: {db_type}")
        print(f"URL: {settings.DATABASE_URL[:50]}...")
        print("-" * 60)
    except ImportError as e:
        print(f"[ERROR] Could not import settings: {e}")
        sys.exit(1)

    # Execute command
    if args.command == "init":
        success = init_database()
    elif args.command == "stamp":
        success = run_alembic_command("stamp", args.target)
    else:
        success = run_alembic_command(args.command, args.target)

    if success:
        print("\n[OK] Operation completed successfully!")
    else:
        print("\n[ERROR] Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__)
    else:
        main()