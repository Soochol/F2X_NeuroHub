"""
Test suite for Alembic database migrations.

This module provides comprehensive tests for database migrations including:
- Forward migration testing
- Rollback/downgrade testing
- Migration chain integrity
- Data preservation during migrations
- Schema validation
"""

import os
import sys
import pytest
import tempfile
from typing import Generator
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timedelta

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import (
    User, UserRole, ProductModel, Process, Lot, WIPItem,
    Serial, ProcessData, WIPProcessHistory, AuditLog, Alert,
    ProductionLine, Equipment, ErrorLog, PrintLog
)


class TestMigrations:
    """Test suite for Alembic database migrations."""

    @pytest.fixture(scope="function")
    def alembic_config(self, tmp_path) -> Config:
        """
        Create Alembic configuration for testing.

        Args:
            tmp_path: Pytest tmp_path fixture

        Returns:
            Alembic Config object configured for testing
        """
        # Create test database
        db_path = tmp_path / "test_migrations.db"
        db_url = f"sqlite:///{db_path}"

        # Get alembic.ini path
        backend_dir = Path(__file__).parent.parent
        alembic_ini = backend_dir / "alembic.ini"

        # Create config
        config = Config(str(alembic_ini))
        config.set_main_option("sqlalchemy.url", db_url)
        config.set_main_option("script_location", str(backend_dir / "alembic"))

        # Set test database in environment
        os.environ["TEST_DATABASE_URL"] = db_url

        return config

    @pytest.fixture(scope="function")
    def test_engine(self, alembic_config: Config):
        """
        Create test database engine.

        Args:
            alembic_config: Alembic configuration

        Returns:
            SQLAlchemy Engine for test database
        """
        db_url = alembic_config.get_main_option("sqlalchemy.url")
        engine = create_engine(
            db_url,
            poolclass=NullPool,
            connect_args={"check_same_thread": False}
        )
        yield engine
        engine.dispose()

    @pytest.fixture(scope="function")
    def test_session(self, test_engine) -> Generator[Session, None, None]:
        """
        Create test database session.

        Args:
            test_engine: Test database engine

        Yields:
            SQLAlchemy Session
        """
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = SessionLocal()
        yield session
        session.close()

    @contextmanager
    def migration_context(self, engine):
        """
        Create migration context for testing.

        Args:
            engine: SQLAlchemy engine

        Yields:
            Alembic MigrationContext
        """
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            yield context

    def test_alembic_init(self, alembic_config: Config):
        """Test that Alembic can be initialized properly."""
        # Check that script directory can be loaded
        script_dir = ScriptDirectory.from_config(alembic_config)
        assert script_dir is not None

        # Check that we have migrations
        revisions = list(script_dir.walk_revisions())
        assert len(revisions) > 0, "No migrations found"

        # Check head revision exists
        head_revision = script_dir.get_current_head()
        assert head_revision is not None, "No head revision found"

    def test_migration_chain_integrity(self, alembic_config: Config):
        """Test that migration chain is continuous without gaps."""
        script_dir = ScriptDirectory.from_config(alembic_config)

        # Get all revisions
        revisions = list(script_dir.walk_revisions())

        # Check each revision has proper down_revision
        for rev in revisions:
            if rev.down_revision:
                # Check that down_revision exists
                down_rev = script_dir.get_revision(rev.down_revision)
                assert down_rev is not None, f"Missing down_revision {rev.down_revision} for {rev.revision}"

                # Check that the down revision points back to this one
                if isinstance(down_rev.nextrev, set):
                    assert rev.revision in down_rev.nextrev
                else:
                    assert rev.revision == down_rev.nextrev

    def test_migrate_up_to_head(self, alembic_config: Config, test_engine):
        """Test forward migration from empty database to head."""
        # Run migrations to head
        command.upgrade(alembic_config, "head")

        # Verify database structure
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()

        # Check that all expected tables exist
        expected_tables = [
            'alembic_version',
            'users',
            'product_models',
            'processes',
            'lots',
            'wip_items',
            'serials',
            'process_data',
            'wip_process_history',
            'audit_logs',
            'alerts',
            'production_lines',
            'equipment',
            'error_logs',
            'print_logs'
        ]

        for table in expected_tables:
            assert table in tables, f"Table {table} not found after migration"

        # Check current revision
        with self.migration_context(test_engine) as context:
            current_rev = context.get_current_revision()
            assert current_rev is not None, "No current revision after upgrade"

    def test_migrate_down_to_base(self, alembic_config: Config, test_engine):
        """Test downgrade from head to base."""
        # First migrate up
        command.upgrade(alembic_config, "head")

        # Then migrate down
        command.downgrade(alembic_config, "base")

        # Check that only alembic_version table remains
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()

        # After downgrade to base, no application tables should exist
        assert 'users' not in tables, "Users table still exists after downgrade"
        assert 'product_models' not in tables, "Product models table still exists"

    def test_migration_up_down_up(self, alembic_config: Config, test_engine):
        """Test that migrations can be applied, rolled back, and reapplied."""
        # Migrate up
        command.upgrade(alembic_config, "head")

        # Get current revision
        with self.migration_context(test_engine) as context:
            head_rev = context.get_current_revision()

        # Migrate down one step
        command.downgrade(alembic_config, "-1")

        # Check we're not at head anymore
        with self.migration_context(test_engine) as context:
            current_rev = context.get_current_revision()
            assert current_rev != head_rev, "Still at head after downgrade"

        # Migrate back up
        command.upgrade(alembic_config, "head")

        # Check we're back at head
        with self.migration_context(test_engine) as context:
            final_rev = context.get_current_revision()
            assert final_rev == head_rev, "Not at head after re-upgrade"

    def test_data_preservation_during_migration(self, alembic_config: Config, test_engine, test_session):
        """Test that data is preserved during migrations."""
        # Migrate to head
        command.upgrade(alembic_config, "head")

        # Insert test data
        test_user = User(
            username="test_migration_user",
            email="test@migration.com",
            hashed_password="hashed_test_password",
            full_name="Migration Test User",
            role=UserRole.OPERATOR,
            is_active=True
        )
        test_session.add(test_user)
        test_session.commit()

        # Get user ID
        user_id = test_user.id

        # Downgrade one step
        command.downgrade(alembic_config, "-1")

        # Upgrade back to head
        command.upgrade(alembic_config, "head")

        # Check that user still exists
        preserved_user = test_session.query(User).filter_by(id=user_id).first()
        assert preserved_user is not None, "User data lost during migration"
        assert preserved_user.username == "test_migration_user"
        assert preserved_user.email == "test@migration.com"

    def test_migration_with_complex_data(self, alembic_config: Config, test_engine, test_session):
        """Test migrations with complex relational data."""
        # Migrate to head
        command.upgrade(alembic_config, "head")

        # Create complex test data
        # Create user
        user = User(
            username="complex_test_user",
            email="complex@test.com",
            hashed_password="hashed_password",
            full_name="Complex Test User",
            role=UserRole.ADMIN,
            is_active=True
        )
        test_session.add(user)
        test_session.flush()

        # Create product model
        product = ProductModel(
            part_number="TEST-001",
            revision="A",
            description="Test Product",
            created_by_id=user.id,
            updated_by_id=user.id
        )
        test_session.add(product)
        test_session.flush()

        # Create process
        process = Process(
            name="Test Process",
            description="Test Process Description",
            order=1,
            is_active=True,
            created_by_id=user.id,
            updated_by_id=user.id
        )
        test_session.add(process)
        test_session.flush()

        # Create lot
        lot = Lot(
            lot_number="LOT-TEST-001",
            part_number=product.part_number,
            revision=product.revision,
            quantity=100,
            status="ACTIVE",
            created_by_id=user.id,
            updated_by_id=user.id
        )
        test_session.add(lot)
        test_session.flush()

        # Create WIP item
        wip = WIPItem(
            wip_id="WIP-TEST-001",
            lot_number=lot.lot_number,
            current_process_id=process.id,
            status="ACTIVE",
            created_by_id=user.id,
            updated_by_id=user.id
        )
        test_session.add(wip)
        test_session.commit()

        # Store IDs
        user_id = user.id
        product_pn = product.part_number
        process_id = process.id
        lot_number = lot.lot_number
        wip_id = wip.wip_id

        # Perform migration down and up
        command.downgrade(alembic_config, "-1")
        command.upgrade(alembic_config, "head")

        # Verify all data is preserved
        preserved_user = test_session.query(User).filter_by(id=user_id).first()
        assert preserved_user is not None

        preserved_product = test_session.query(ProductModel).filter_by(part_number=product_pn).first()
        assert preserved_product is not None

        preserved_process = test_session.query(Process).filter_by(id=process_id).first()
        assert preserved_process is not None

        preserved_lot = test_session.query(Lot).filter_by(lot_number=lot_number).first()
        assert preserved_lot is not None

        preserved_wip = test_session.query(WIPItem).filter_by(wip_id=wip_id).first()
        assert preserved_wip is not None

    def test_migration_rollback_on_error(self, alembic_config: Config, test_engine):
        """Test that migrations properly rollback on error."""
        # This test would require a migration with an intentional error
        # For now, we'll test that the mechanism works

        # Upgrade to head
        command.upgrade(alembic_config, "head")

        with self.migration_context(test_engine) as context:
            head_rev = context.get_current_revision()

        # Attempt to upgrade to non-existent revision (should fail)
        with pytest.raises(Exception):
            command.upgrade(alembic_config, "nonexistent")

        # Verify we're still at head (transaction rolled back)
        with self.migration_context(test_engine) as context:
            current_rev = context.get_current_revision()
            assert current_rev == head_rev, "Migration state changed after failed upgrade"

    def test_migration_performance(self, alembic_config: Config, test_engine, test_session):
        """Test migration performance with large dataset."""
        import time

        # Migrate to head
        command.upgrade(alembic_config, "head")

        # Create large dataset
        batch_size = 1000
        num_users = 5000

        start_time = time.time()

        # Batch insert users
        for i in range(0, num_users, batch_size):
            users = []
            for j in range(batch_size):
                if i + j >= num_users:
                    break
                users.append({
                    'username': f'perf_user_{i+j}',
                    'email': f'user{i+j}@perf.test',
                    'hashed_password': 'hashed_password',
                    'full_name': f'Performance User {i+j}',
                    'role': 'OPERATOR',
                    'is_active': True,
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })

            if users:
                test_session.execute(text(
                    "INSERT INTO users (username, email, hashed_password, full_name, role, is_active, created_at, updated_at) "
                    "VALUES (:username, :email, :hashed_password, :full_name, :role, :is_active, :created_at, :updated_at)"
                ), users)
                test_session.commit()

        insert_time = time.time() - start_time

        # Time migration down
        start_time = time.time()
        command.downgrade(alembic_config, "-1")
        downgrade_time = time.time() - start_time

        # Time migration up
        start_time = time.time()
        command.upgrade(alembic_config, "head")
        upgrade_time = time.time() - start_time

        # Performance assertions
        assert insert_time < 10, f"Insert took too long: {insert_time}s"
        assert downgrade_time < 5, f"Downgrade took too long: {downgrade_time}s"
        assert upgrade_time < 5, f"Upgrade took too long: {upgrade_time}s"

        # Verify data count
        user_count = test_session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        assert user_count == num_users, f"Expected {num_users} users, got {user_count}"

    def test_concurrent_migrations(self, alembic_config: Config, test_engine):
        """Test that concurrent migrations are properly handled."""
        import threading
        import time

        # Upgrade to head
        command.upgrade(alembic_config, "head")

        errors = []

        def run_migration(config, direction):
            try:
                if direction == "up":
                    command.upgrade(config, "head")
                else:
                    command.downgrade(config, "-1")
            except Exception as e:
                errors.append(str(e))

        # Try to run migrations concurrently (should be prevented by Alembic)
        threads = []
        for i in range(3):
            direction = "down" if i % 2 == 0 else "up"
            thread = threading.Thread(target=run_migration, args=(alembic_config, direction))
            threads.append(thread)
            thread.start()
            time.sleep(0.1)  # Small delay between starts

        for thread in threads:
            thread.join()

        # At least some operations should have been blocked/errored
        # This is expected behavior - Alembic uses table locks
        assert len(errors) > 0, "Expected some concurrent operations to be blocked"

    def test_migration_idempotency(self, alembic_config: Config, test_engine):
        """Test that migrations are idempotent."""
        # Upgrade to head
        command.upgrade(alembic_config, "head")

        # Get table structure
        inspector = inspect(test_engine)
        tables_before = set(inspector.get_table_names())

        # Get column structure for each table
        columns_before = {}
        for table in tables_before:
            columns_before[table] = set(
                col['name'] for col in inspector.get_columns(table)
            )

        # Run upgrade again (should be no-op)
        command.upgrade(alembic_config, "head")

        # Check structure is unchanged
        tables_after = set(inspector.get_table_names())
        assert tables_before == tables_after, "Tables changed after idempotent upgrade"

        columns_after = {}
        for table in tables_after:
            columns_after[table] = set(
                col['name'] for col in inspector.get_columns(table)
            )

        assert columns_before == columns_after, "Columns changed after idempotent upgrade"

    def test_schema_validation(self, alembic_config: Config, test_engine):
        """Test that migrated schema matches model definitions."""
        # Upgrade to head
        command.upgrade(alembic_config, "head")

        # Get actual schema from database
        inspector = inspect(test_engine)

        # Compare with model definitions
        metadata = MetaData()
        metadata.reflect(bind=test_engine)

        # Check each model's table exists and has correct columns
        for table_obj in Base.metadata.tables.values():
            table_name = table_obj.name

            # Check table exists
            assert table_name in inspector.get_table_names(), f"Table {table_name} not in database"

            # Get model columns
            model_columns = set(col.name for col in table_obj.columns)

            # Get database columns
            db_columns = set(
                col['name'] for col in inspector.get_columns(table_name)
            )

            # Check all model columns exist in database
            missing_columns = model_columns - db_columns
            assert not missing_columns, f"Missing columns in {table_name}: {missing_columns}"

            # Note: We don't check for extra columns as migrations might add columns
            # that aren't in the current model (for backward compatibility)


class TestMigrationContent:
    """Test specific migration content and transformations."""

    def test_initial_migration_creates_all_tables(self, alembic_config: Config, test_engine):
        """Test that initial migration creates all required tables."""
        # Run only the first migration
        script_dir = ScriptDirectory.from_config(alembic_config)
        revisions = list(script_dir.walk_revisions())

        # Find the initial migration (the one with no down_revision)
        initial_rev = None
        for rev in revisions:
            if rev.down_revision is None:
                initial_rev = rev.revision
                break

        assert initial_rev is not None, "No initial migration found"

        # Upgrade to initial migration only
        command.upgrade(alembic_config, initial_rev)

        # Check core tables exist
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()

        core_tables = ['users', 'product_models', 'processes', 'lots']
        for table in core_tables:
            assert table in tables, f"Core table {table} not created by initial migration"

    def test_wip_support_migration(self, alembic_config: Config, test_engine, test_session):
        """Test WIP support migration adds correct columns and constraints."""
        # This tests a specific migration that adds WIP support
        # Upgrade to head
        command.upgrade(alembic_config, "head")

        # Check that process_data table has WIP columns
        inspector = inspect(test_engine)
        process_data_columns = {
            col['name'] for col in inspector.get_columns('process_data')
        }

        # Check WIP-related columns exist
        assert 'wip_id' in process_data_columns, "wip_id column not found in process_data"

        # Check indexes
        indexes = inspector.get_indexes('process_data')
        index_names = {idx['name'] for idx in indexes}

        # Should have index on wip_id for performance
        wip_index_exists = any(
            'wip_id' in idx.get('column_names', [])
            for idx in indexes
        )
        assert wip_index_exists, "No index on wip_id column"