"""
Verify Alembic migration setup.

This script checks that Alembic is properly configured and can access
the database. Run from the backend directory: python verify_alembic.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def verify_alembic_setup():
    """Verify that Alembic is properly configured."""
    print("F2X NeuroHub - Alembic Migration System Verification")
    print("=" * 60)

    # 1. Check Alembic installation
    try:
        import alembic  # noqa: F401
        from alembic.config import Config
        from alembic import command  # noqa: F401
        print("[OK] Alembic is installed")
    except ImportError as e:
        print(f"[ERROR] Alembic not found: {e}")
        return False

    # 2. Check configuration file
    config_file = backend_dir / "alembic.ini"
    if config_file.exists():
        print(f"[OK] Configuration file found: {config_file}")
    else:
        print(f"[ERROR] Configuration file not found: {config_file}")
        return False

    # 3. Check env.py
    env_file = backend_dir / "alembic" / "env.py"
    if env_file.exists():
        print(f"[OK] Environment file found: {env_file}")
    else:
        print(f"[ERROR] Environment file not found: {env_file}")
        return False

    # 4. Check migrations directory
    versions_dir = backend_dir / "alembic" / "versions"
    if versions_dir.exists():
        migrations = list(versions_dir.glob("*.py"))
        if not migrations:
            print(f"[WARNING] No migrations found in: {versions_dir}")
        else:
            print(f"[OK] Found {len(migrations)} migration(s):")
            for m in sorted(migrations):
                print(f"  - {m.name}")
    else:
        print(f"[ERROR] Versions directory not found: {versions_dir}")
        return False

    # 5. Check database configuration
    print("\nDatabase Configuration:")
    print("-" * 40)
    try:
        from app.config import settings
        db_url_preview = settings.DATABASE_URL[:30] + "..."
        print(f"[OK] Database URL configured: {db_url_preview}")
        db_type = 'SQLite' if 'sqlite' in settings.DATABASE_URL else 'PostgreSQL'
        print(f"  Database type: {db_type}")
    except ImportError as e:
        print(f"[ERROR] Could not import settings: {e}")
        return False

    # 6. Check model imports
    print("\nModel Registration:")
    print("-" * 40)
    try:
        from app.database import Base
        from app.models import (  # noqa: F401
            User, ProductModel, Process, Lot, WIPItem, Serial,
            ProcessData, WIPProcessHistory, AuditLog, Alert,
            ProductionLine, Equipment, ErrorLog, PrintLog
        )

        # Count registered tables
        tables = Base.metadata.tables
        print(f"[OK] {len(tables)} tables registered with SQLAlchemy:")
        for table_name in sorted(tables.keys()):
            print(f"  - {table_name}")
    except ImportError as e:
        print(f"[ERROR] Could not import models: {e}")
        return False

    # 7. Test Alembic configuration
    print("\nAlembic Configuration Test:")
    print("-" * 40)
    try:
        alembic_cfg = Config(str(config_file))

        # Try to get current revision (won't work if DB doesn't exist yet)
        try:
            from alembic.runtime.migration import MigrationContext
            from sqlalchemy import create_engine

            engine = create_engine(settings.DATABASE_URL)
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                if current_rev:
                    print(f"[OK] Current database revision: {current_rev}")
                else:
                    print("[OK] Database is not yet initialized (no revision)")
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"[WARNING] Could not check current revision: {error_msg}")

        # List available migrations
        from alembic.script import ScriptDirectory
        scripts = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(scripts.walk_revisions())

        if revisions:
            print("[OK] Available migrations:")
            for rev in reversed(revisions):
                arrow = "->" if rev.down_revision else "**"
                print(f"  {arrow} {rev.revision[:12]} - {rev.doc}")
        else:
            print("[WARNING] No migrations available")

    except Exception as e:
        print(f"[ERROR] Alembic configuration error: {e}")
        return False

    print("\n" + "=" * 60)
    print("[OK] Alembic setup verification complete!")
    print("\nNext steps:")
    print("1. Create the database (if not exists)")
    print("2. Run: alembic upgrade head")
    print("3. Check: alembic current")

    return True


if __name__ == "__main__":
    success = verify_alembic_setup()
    sys.exit(0 if success else 1)