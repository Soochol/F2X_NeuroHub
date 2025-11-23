"""
Database Performance Testing Suite.

This module provides comprehensive performance testing for database operations including:
- Query performance benchmarks
- Operation timing assertions
- Query count tracking
- Index effectiveness testing
- Batch operation performance
- Connection pool testing
"""

import os
import sys
import time
import pytest
import random
import string
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager
from functools import wraps

from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool, NullPool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.models import (
    User, UserRole, ProductModel, Process, Lot, WIPItem,
    Serial, ProcessData, WIPProcessHistory, AuditLog, Alert,
    ProductionLine, Equipment, ErrorLog, PrintLog
)


def timeit(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        execution_time = end - start
        if hasattr(wrapper, 'execution_times'):
            wrapper.execution_times.append(execution_time)
        else:
            wrapper.execution_times = [execution_time]
        return result
    return wrapper


class QueryCounter:
    """Context manager to count database queries."""

    def __init__(self, session: Session):
        self.session = session
        self.query_count = 0
        self.queries = []

    def __enter__(self):
        @event.listens_for(self.session.get_bind(), "before_execute")
        def receive_before_execute(conn, clauseelement, multiparams, params, execution_options):
            self.query_count += 1
            self.queries.append(str(clauseelement))

        self.handler = receive_before_execute
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        event.remove(self.session.get_bind(), "before_execute", self.handler)


class PerformanceMetrics:
    """Helper class to track and assert performance metrics."""

    def __init__(self):
        self.metrics = {}

    def record(self, operation: str, duration: float, queries: int = 0):
        """Record performance metrics for an operation."""
        if operation not in self.metrics:
            self.metrics[operation] = {
                'durations': [],
                'query_counts': []
            }
        self.metrics[operation]['durations'].append(duration)
        if queries:
            self.metrics[operation]['query_counts'].append(queries)

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self.metrics:
            return {}

        durations = self.metrics[operation]['durations']
        query_counts = self.metrics[operation]['query_counts']

        stats = {
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_duration': statistics.mean(durations),
            'median_duration': statistics.median(durations),
            'total_runs': len(durations)
        }

        if query_counts:
            stats.update({
                'min_queries': min(query_counts),
                'max_queries': max(query_counts),
                'avg_queries': statistics.mean(query_counts),
            })

        if len(durations) > 1:
            stats['std_dev'] = statistics.stdev(durations)

        return stats

    def assert_performance(self, operation: str, max_duration: float = None,
                          max_queries: int = None, max_avg_duration: float = None):
        """Assert performance requirements for an operation."""
        stats = self.get_stats(operation)

        if max_duration is not None:
            assert stats['max_duration'] <= max_duration, \
                f"{operation}: Max duration {stats['max_duration']:.3f}s exceeds limit {max_duration}s"

        if max_avg_duration is not None:
            assert stats['avg_duration'] <= max_avg_duration, \
                f"{operation}: Avg duration {stats['avg_duration']:.3f}s exceeds limit {max_avg_duration}s"

        if max_queries is not None and 'max_queries' in stats:
            assert stats['max_queries'] <= max_queries, \
                f"{operation}: Max queries {stats['max_queries']} exceeds limit {max_queries}"


class TestDatabasePerformance:
    """Core database performance tests."""

    @pytest.fixture(scope="class")
    def performance_db(self):
        """Create a performance testing database with larger dataset."""
        # Use in-memory SQLite for consistent performance testing
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=NullPool
        )

        # Create tables
        Base.metadata.create_all(bind=engine)

        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Populate with test data
        self._populate_performance_data(session)

        yield session

        session.close()
        engine.dispose()

    def _populate_performance_data(self, session: Session):
        """Populate database with performance test data."""
        # Create users
        users = []
        for i in range(100):
            user = User(
                username=f"perf_user_{i}",
                email=f"user{i}@perf.test",
                hashed_password="hashed_password",
                full_name=f"Performance User {i}",
                role=random.choice(list(UserRole)),
                is_active=random.choice([True, False]),
                department=random.choice(["Production", "Quality", "Engineering"])
            )
            users.append(user)
        session.add_all(users)
        session.flush()

        # Create product models
        products = []
        for i in range(50):
            product = ProductModel(
                part_number=f"PERF-{i:04d}",
                revision=random.choice(["A", "B", "C"]),
                description=f"Performance Test Product {i}",
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            products.append(product)
        session.add_all(products)
        session.flush()

        # Create processes
        processes = []
        for i in range(20):
            process = Process(
                name=f"Process {i}",
                description=f"Performance Test Process {i}",
                order=i,
                is_active=True,
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            processes.append(process)
        session.add_all(processes)
        session.flush()

        # Create lots
        lots = []
        for i in range(200):
            product = random.choice(products)
            lot = Lot(
                lot_number=f"LOT-PERF-{i:06d}",
                part_number=product.part_number,
                revision=product.revision,
                quantity=random.randint(100, 1000),
                status=random.choice(["ACTIVE", "COMPLETED", "ON_HOLD"]),
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            lots.append(lot)
        session.add_all(lots)
        session.flush()

        # Create WIP items
        wip_items = []
        for i in range(500):
            lot = random.choice(lots)
            wip = WIPItem(
                wip_id=f"WIP-PERF-{i:06d}",
                lot_number=lot.lot_number,
                current_process_id=random.choice(processes).id,
                status=random.choice(["ACTIVE", "COMPLETED", "ON_HOLD", "SCRAPPED"]),
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            wip_items.append(wip)
        session.add_all(wip_items)
        session.flush()

        # Create serials
        serials = []
        for i in range(1000):
            wip = random.choice(wip_items)
            serial = Serial(
                serial_number=f"SN-PERF-{i:08d}",
                wip_id=wip.wip_id,
                status=random.choice(["ACTIVE", "COMPLETED", "SCRAPPED"]),
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            serials.append(serial)
        session.add_all(serials)
        session.flush()

        # Create process data
        process_data_records = []
        for i in range(5000):
            serial = random.choice(serials) if random.random() > 0.3 else None
            wip = random.choice(wip_items) if not serial else None

            process_data = ProcessData(
                process_id=random.choice(processes).id,
                serial_number=serial.serial_number if serial else None,
                wip_id=wip.wip_id if wip else None,
                data_type=random.choice(["MEASUREMENT", "TEST", "INSPECTION"]),
                data_value=str(random.uniform(0, 100)),
                status=random.choice(["PASS", "FAIL", "PENDING"]),
                created_by_id=random.choice(users).id,
                updated_by_id=random.choice(users).id
            )
            process_data_records.append(process_data)

            # Add in batches to avoid memory issues
            if len(process_data_records) >= 500:
                session.add_all(process_data_records)
                session.flush()
                process_data_records = []

        if process_data_records:
            session.add_all(process_data_records)
            session.flush()

        session.commit()

    @pytest.fixture
    def metrics(self):
        """Performance metrics tracker."""
        return PerformanceMetrics()

    def test_simple_query_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of simple queries."""
        # Test single record fetch by primary key
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            user = performance_db.query(User).filter_by(id=1).first()
            duration = time.perf_counter() - start

        metrics.record("fetch_by_id", duration, counter.query_count)
        assert counter.query_count == 1, "Simple fetch should execute one query"
        assert duration < 0.01, f"Simple query took {duration:.3f}s, should be < 0.01s"

        # Test multiple simple queries
        for i in range(10):
            with QueryCounter(performance_db) as counter:
                start = time.perf_counter()
                user = performance_db.query(User).filter_by(username=f"perf_user_{i}").first()
                duration = time.perf_counter() - start

            metrics.record("fetch_by_username", duration, counter.query_count)

        metrics.assert_performance("fetch_by_username", max_avg_duration=0.005, max_queries=1)

    def test_join_query_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of join queries."""
        # Test join between WIP items and Lots
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            results = performance_db.query(WIPItem).join(Lot).filter(
                Lot.status == "ACTIVE"
            ).limit(100).all()
            duration = time.perf_counter() - start

        metrics.record("join_wip_lot", duration, counter.query_count)
        assert counter.query_count <= 2, f"Join query executed {counter.query_count} queries"
        assert duration < 0.05, f"Join query took {duration:.3f}s, should be < 0.05s"

        # Test multi-table join
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            results = performance_db.query(Serial).join(WIPItem).join(Lot).join(ProductModel).filter(
                ProductModel.part_number.like("PERF-%"),
                Lot.status == "ACTIVE"
            ).limit(50).all()
            duration = time.perf_counter() - start

        metrics.record("multi_join", duration, counter.query_count)
        assert counter.query_count <= 3, f"Multi-join executed {counter.query_count} queries"
        assert duration < 0.1, f"Multi-join took {duration:.3f}s, should be < 0.1s"

    def test_aggregation_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of aggregation queries."""
        from sqlalchemy import func

        # Test COUNT aggregation
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            count = performance_db.query(func.count(ProcessData.id)).scalar()
            duration = time.perf_counter() - start

        metrics.record("count_all", duration, counter.query_count)
        assert counter.query_count == 1, "Count should execute one query"
        assert duration < 0.02, f"Count took {duration:.3f}s, should be < 0.02s"

        # Test GROUP BY with aggregation
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            results = performance_db.query(
                ProcessData.process_id,
                func.count(ProcessData.id).label('count'),
                func.avg(func.cast(ProcessData.data_value, type_=float)).label('avg_value')
            ).group_by(ProcessData.process_id).all()
            duration = time.perf_counter() - start

        metrics.record("group_by_aggregate", duration, counter.query_count)
        assert counter.query_count == 1, "GROUP BY should execute one query"
        assert duration < 0.1, f"GROUP BY took {duration:.3f}s, should be < 0.1s"

    def test_bulk_insert_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of bulk insert operations."""
        # Prepare bulk data
        bulk_users = []
        for i in range(1000):
            bulk_users.append({
                'username': f'bulk_user_{i}',
                'email': f'bulk{i}@test.com',
                'hashed_password': 'hashed',
                'full_name': f'Bulk User {i}',
                'role': 'OPERATOR',
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })

        # Test bulk insert with ORM
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            performance_db.bulk_insert_mappings(User, bulk_users)
            performance_db.commit()
            duration = time.perf_counter() - start

        metrics.record("bulk_insert_orm", duration, counter.query_count)
        assert duration < 1.0, f"Bulk insert of 1000 records took {duration:.3f}s, should be < 1.0s"

        # Test bulk insert with Core
        bulk_products = []
        for i in range(1000):
            bulk_products.append({
                'part_number': f'BULK-{i:04d}',
                'revision': 'A',
                'description': f'Bulk Product {i}',
                'created_by_id': 1,
                'updated_by_id': 1,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })

        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            performance_db.execute(
                ProductModel.__table__.insert(),
                bulk_products
            )
            performance_db.commit()
            duration = time.perf_counter() - start

        metrics.record("bulk_insert_core", duration, counter.query_count)
        assert duration < 0.5, f"Core bulk insert took {duration:.3f}s, should be < 0.5s"

    def test_bulk_update_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of bulk update operations."""
        # Test bulk update with ORM
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            performance_db.query(User).filter(
                User.username.like("bulk_user_%")
            ).update(
                {"department": "Bulk Department"},
                synchronize_session=False
            )
            performance_db.commit()
            duration = time.perf_counter() - start

        metrics.record("bulk_update_orm", duration, counter.query_count)
        assert duration < 0.5, f"Bulk update took {duration:.3f}s, should be < 0.5s"

    def test_pagination_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test performance of paginated queries."""
        page_size = 50

        # Test offset-based pagination
        for page in range(5):
            with QueryCounter(performance_db) as counter:
                start = time.perf_counter()
                results = performance_db.query(ProcessData).offset(
                    page * page_size
                ).limit(page_size).all()
                duration = time.perf_counter() - start

            metrics.record(f"pagination_offset_page_{page}", duration, counter.query_count)

        # Test keyset pagination (more efficient for large datasets)
        last_id = 0
        for page in range(5):
            with QueryCounter(performance_db) as counter:
                start = time.perf_counter()
                results = performance_db.query(ProcessData).filter(
                    ProcessData.id > last_id
                ).limit(page_size).all()
                duration = time.perf_counter() - start

            if results:
                last_id = results[-1].id

            metrics.record(f"pagination_keyset_page_{page}", duration, counter.query_count)

        # Assert keyset is faster than offset for later pages
        offset_page_4 = metrics.get_stats("pagination_offset_page_4")['avg_duration']
        keyset_page_4 = metrics.get_stats("pagination_keyset_page_4")['avg_duration']
        assert keyset_page_4 <= offset_page_4, "Keyset pagination should be faster for later pages"

    def test_index_effectiveness(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test that indexes are being used effectively."""
        # Test query on indexed column (primary key)
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            result = performance_db.query(User).filter_by(id=50).first()
            indexed_duration = time.perf_counter() - start

        # Test query on non-indexed column (assuming department is not indexed)
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            result = performance_db.query(User).filter_by(department="Production").all()
            non_indexed_duration = time.perf_counter() - start

        # Primary key lookup should be significantly faster
        assert indexed_duration < non_indexed_duration / 2, \
            "Indexed query not significantly faster than non-indexed"

    def test_n_plus_one_detection(self, performance_db: Session):
        """Test for N+1 query problems."""
        # Bad pattern - N+1 queries
        with QueryCounter(performance_db) as counter:
            lots = performance_db.query(Lot).limit(10).all()
            for lot in lots:
                # This triggers a new query for each lot
                _ = lot.wip_items

        n_plus_one_queries = counter.query_count
        assert n_plus_one_queries > 10, "N+1 pattern should generate many queries"

        # Good pattern - eager loading
        with QueryCounter(performance_db) as counter:
            from sqlalchemy.orm import joinedload
            lots = performance_db.query(Lot).options(
                joinedload(Lot.wip_items)
            ).limit(10).all()
            for lot in lots:
                _ = lot.wip_items

        eager_load_queries = counter.query_count
        assert eager_load_queries <= 2, f"Eager loading generated {eager_load_queries} queries"
        assert eager_load_queries < n_plus_one_queries / 5, "Eager loading should use far fewer queries"

    def test_transaction_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test transaction commit performance."""
        # Test small transactions
        small_transaction_times = []
        for i in range(10):
            start = time.perf_counter()
            user = User(
                username=f"trans_user_{i}",
                email=f"trans{i}@test.com",
                hashed_password="hashed",
                full_name=f"Transaction User {i}",
                role=UserRole.OPERATOR,
                is_active=True
            )
            performance_db.add(user)
            performance_db.commit()
            duration = time.perf_counter() - start
            small_transaction_times.append(duration)

        avg_small = statistics.mean(small_transaction_times)

        # Test large transaction
        start = time.perf_counter()
        for i in range(100):
            user = User(
                username=f"batch_trans_user_{i}",
                email=f"batch_trans{i}@test.com",
                hashed_password="hashed",
                full_name=f"Batch Transaction User {i}",
                role=UserRole.OPERATOR,
                is_active=True
            )
            performance_db.add(user)
        performance_db.commit()
        large_transaction_time = time.perf_counter() - start

        # Large transaction should be more efficient per record
        per_record_small = avg_small
        per_record_large = large_transaction_time / 100

        assert per_record_large < per_record_small / 2, \
            "Large transaction not more efficient per record"

    def test_connection_pool_performance(self):
        """Test connection pool performance."""
        # Create engine with connection pool
        pooled_engine = create_engine(
            "sqlite:///:memory:",
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10
        )

        # Create engine without connection pool
        non_pooled_engine = create_engine(
            "sqlite:///:memory:",
            poolclass=NullPool
        )

        Base.metadata.create_all(bind=pooled_engine)
        Base.metadata.create_all(bind=non_pooled_engine)

        # Test pooled connections
        pooled_times = []
        for i in range(50):
            start = time.perf_counter()
            with pooled_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
            pooled_times.append(time.perf_counter() - start)

        # Test non-pooled connections
        non_pooled_times = []
        for i in range(50):
            start = time.perf_counter()
            with non_pooled_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
            non_pooled_times.append(time.perf_counter() - start)

        avg_pooled = statistics.mean(pooled_times)
        avg_non_pooled = statistics.mean(non_pooled_times)

        # Connection pooling should be faster (for non-memory databases this difference is larger)
        assert avg_pooled <= avg_non_pooled * 1.5, \
            f"Pooled connections not faster: {avg_pooled:.4f}s vs {avg_non_pooled:.4f}s"

    def test_query_caching_performance(self, performance_db: Session, metrics: PerformanceMetrics):
        """Test query result caching performance."""
        # First query - no cache
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            result1 = performance_db.query(User).filter_by(username="perf_user_1").first()
            first_duration = time.perf_counter() - start
            first_queries = counter.query_count

        # Same query - should use identity map (session cache)
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            result2 = performance_db.query(User).filter_by(username="perf_user_1").first()
            cached_duration = time.perf_counter() - start
            cached_queries = counter.query_count

        # Should be same object (identity map)
        assert result1 is result2, "Should return same object from identity map"

        # Note: SQLAlchemy doesn't cache query results by default,
        # but the identity map prevents loading the same object twice

    def test_concurrent_query_performance(self, performance_db: Session):
        """Test performance under concurrent load."""
        import threading
        import queue

        results_queue = queue.Queue()

        def run_queries(session_factory, num_queries, thread_id):
            session = session_factory()
            times = []
            try:
                for i in range(num_queries):
                    start = time.perf_counter()
                    result = session.query(ProcessData).filter_by(
                        status="PASS"
                    ).limit(10).all()
                    times.append(time.perf_counter() - start)
            finally:
                session.close()

            results_queue.put((thread_id, times))

        # Create session factory
        engine = performance_db.get_bind()
        SessionFactory = sessionmaker(bind=engine)

        # Run concurrent queries
        threads = []
        num_threads = 5
        queries_per_thread = 20

        start_time = time.perf_counter()
        for i in range(num_threads):
            thread = threading.Thread(
                target=run_queries,
                args=(SessionFactory, queries_per_thread, i)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_time = time.perf_counter() - start_time

        # Collect results
        all_times = []
        while not results_queue.empty():
            thread_id, times = results_queue.get()
            all_times.extend(times)

        avg_query_time = statistics.mean(all_times)
        max_query_time = max(all_times)

        # Performance assertions
        assert total_time < 2.0, f"Concurrent queries took {total_time:.2f}s"
        assert avg_query_time < 0.05, f"Average query time {avg_query_time:.3f}s under load"
        assert max_query_time < 0.2, f"Max query time {max_query_time:.3f}s under load"


class TestOptimizationComparison:
    """Compare performance before and after optimizations."""

    def create_unoptimized_query(self, session: Session):
        """Create an intentionally unoptimized query."""
        # Bad: Multiple queries, no eager loading
        results = []
        wip_items = session.query(WIPItem).all()
        for wip in wip_items[:10]:
            lot = session.query(Lot).filter_by(lot_number=wip.lot_number).first()
            serials = session.query(Serial).filter_by(wip_id=wip.wip_id).all()
            results.append({
                'wip': wip,
                'lot': lot,
                'serials': serials
            })
        return results

    def create_optimized_query(self, session: Session):
        """Create an optimized version of the same query."""
        from sqlalchemy.orm import joinedload

        # Good: Single query with eager loading
        results = []
        wip_items = session.query(WIPItem).options(
            joinedload(WIPItem.lot),
            joinedload(WIPItem.serials)
        ).limit(10).all()

        for wip in wip_items:
            results.append({
                'wip': wip,
                'lot': wip.lot,
                'serials': wip.serials
            })
        return results

    def test_optimization_comparison(self, performance_db: Session):
        """Compare unoptimized vs optimized query performance."""
        # Measure unoptimized
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            unoptimized_results = self.create_unoptimized_query(performance_db)
            unoptimized_time = time.perf_counter() - start
            unoptimized_queries = counter.query_count

        # Clear session to ensure fair comparison
        performance_db.expire_all()

        # Measure optimized
        with QueryCounter(performance_db) as counter:
            start = time.perf_counter()
            optimized_results = self.create_optimized_query(performance_db)
            optimized_time = time.perf_counter() - start
            optimized_queries = counter.query_count

        # Assertions
        assert optimized_queries < unoptimized_queries / 5, \
            f"Optimized uses {optimized_queries} queries vs {unoptimized_queries}"

        assert optimized_time < unoptimized_time / 2, \
            f"Optimized takes {optimized_time:.3f}s vs {unoptimized_time:.3f}s"

        # Calculate improvement
        query_reduction = (1 - optimized_queries / unoptimized_queries) * 100
        time_reduction = (1 - optimized_time / unoptimized_time) * 100

        print(f"Query reduction: {query_reduction:.1f}%")
        print(f"Time reduction: {time_reduction:.1f}%")

        # Ensure we get same results
        assert len(optimized_results) == len(unoptimized_results)