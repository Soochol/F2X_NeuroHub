# Testing Infrastructure Documentation

## Overview

This document describes the comprehensive testing infrastructure for database migrations and performance in the F2X NeuroHub system.

## Test Files

### 1. `test_migrations.py`

Comprehensive test suite for Alembic database migrations.

#### Test Classes

- **`TestMigrations`**: Core migration testing functionality
  - `test_alembic_init`: Validates Alembic initialization
  - `test_migration_chain_integrity`: Verifies migration chain has no gaps
  - `test_migrate_up_to_head`: Tests forward migration to latest
  - `test_migrate_down_to_base`: Tests complete rollback
  - `test_migration_up_down_up`: Tests migration reversibility
  - `test_data_preservation_during_migration`: Ensures data integrity
  - `test_migration_with_complex_data`: Tests with relational data
  - `test_migration_rollback_on_error`: Validates error handling
  - `test_migration_performance`: Benchmarks migration speed
  - `test_concurrent_migrations`: Tests migration locking
  - `test_migration_idempotency`: Ensures migrations are idempotent
  - `test_schema_validation`: Validates schema matches models

- **`TestMigrationContent`**: Tests specific migration content
  - `test_initial_migration_creates_all_tables`: Validates initial setup
  - `test_wip_support_migration`: Tests WIP-specific migrations

#### Key Features

- **Data Integrity Testing**: Ensures data is preserved during migrations
- **Performance Benchmarks**: Measures migration execution time
- **Schema Validation**: Compares database schema with SQLAlchemy models
- **Rollback Testing**: Verifies migrations can be safely rolled back

### 2. `test_database_performance.py`

Performance testing suite for database operations.

#### Test Classes

- **`TestDatabasePerformance`**: Core performance tests
  - `test_simple_query_performance`: Benchmarks basic queries
  - `test_join_query_performance`: Tests JOIN operation speed
  - `test_aggregation_performance`: Measures aggregation performance
  - `test_bulk_insert_performance`: Tests bulk insert operations
  - `test_bulk_update_performance`: Tests bulk update operations
  - `test_pagination_performance`: Compares pagination strategies
  - `test_index_effectiveness`: Validates index usage
  - `test_n_plus_one_detection`: Identifies N+1 query problems
  - `test_transaction_performance`: Measures transaction overhead
  - `test_connection_pool_performance`: Tests connection pooling
  - `test_query_caching_performance`: Validates caching mechanisms
  - `test_concurrent_query_performance`: Tests under concurrent load

- **`TestOptimizationComparison`**: Before/after optimization comparison
  - `test_optimization_comparison`: Compares optimized vs unoptimized queries

#### Performance Metrics

- **Query Count Tracking**: Monitors number of SQL queries
- **Execution Time**: Measures operation duration
- **Concurrency Testing**: Tests performance under load
- **Memory Usage**: Monitors resource consumption (indirect)

#### Helper Classes

- **`QueryCounter`**: Context manager for counting SQL queries
- **`PerformanceMetrics`**: Tracks and asserts performance requirements
- **`timeit`**: Decorator for measuring function execution time

## Test Scripts

### 1. `run_migration_tests.sh` (Linux/Mac)

Comprehensive shell script for running migration tests.

#### Features

- **Prerequisites Check**: Validates required tools are installed
- **Test Database Setup**: Creates isolated test environment
- **Test Suite Execution**: Runs all migration tests
- **Performance Testing**: Optional performance benchmarks
- **Coverage Generation**: Optional code coverage reports
- **Report Generation**: Creates detailed test reports
- **Cleanup**: Removes test artifacts

#### Usage

```bash
# Basic usage
./run_migration_tests.sh

# With verbose output
./run_migration_tests.sh -v

# Include performance tests
./run_migration_tests.sh -p

# Generate coverage report
./run_migration_tests.sh -c

# All options
./run_migration_tests.sh -v -p -c
```

### 2. `run_migration_tests.bat` (Windows)

Windows batch script equivalent of the shell script.

#### Usage

```batch
REM Basic usage
run_migration_tests.bat

REM With verbose output
run_migration_tests.bat -v

REM Include performance tests
run_migration_tests.bat -p

REM Generate coverage report
run_migration_tests.bat -c

REM All options
run_migration_tests.bat -v -p -c
```

## Test Coverage

### Migration Testing Coverage

- **Schema Operations**
  - Table creation/deletion
  - Column addition/removal
  - Index management
  - Constraint handling

- **Data Operations**
  - Data preservation
  - Data transformation
  - Bulk operations
  - Transaction handling

- **Error Handling**
  - Rollback on error
  - Concurrent migration prevention
  - Invalid migration detection

### Performance Testing Coverage

- **Query Operations**
  - Simple queries (SELECT, WHERE)
  - Complex queries (JOIN, GROUP BY)
  - Aggregations (COUNT, AVG, SUM)
  - Pagination strategies

- **Write Operations**
  - Single inserts
  - Bulk inserts
  - Updates (single and bulk)
  - Deletes

- **Optimization Techniques**
  - Index usage
  - Query optimization
  - N+1 query prevention
  - Connection pooling

## Running Tests

### Local Development

```bash
# Run all migration tests
pytest backend/tests/test_migrations.py -v

# Run specific test
pytest backend/tests/test_migrations.py::TestMigrations::test_migrate_up_to_head -v

# Run all performance tests
pytest backend/tests/test_database_performance.py -v

# Run with coverage
pytest backend/tests/test_migrations.py --cov=alembic --cov-report=html
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Migration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run migration tests
        run: |
          cd backend
          ./scripts/run_migration_tests.sh -c
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Performance Baselines

### Expected Performance Metrics

| Operation | Max Duration | Max Queries |
|-----------|-------------|-------------|
| Simple Query | 10ms | 1 |
| Join Query | 50ms | 2 |
| Bulk Insert (1000 records) | 1s | - |
| Migration Up/Down | 5s | - |
| Pagination (50 records) | 20ms | 1 |
| Aggregation | 100ms | 1 |

### Performance Assertions

```python
# Example performance assertion
metrics.assert_performance(
    operation="fetch_by_id",
    max_duration=0.01,  # 10ms
    max_queries=1
)
```

## Troubleshooting

### Common Issues

1. **Test Database Connection Failed**
   - Check DATABASE_URL environment variable
   - Ensure test database exists
   - Verify database permissions

2. **Migration Tests Fail**
   - Check Alembic configuration
   - Verify all models are imported in env.py
   - Ensure migrations are up to date

3. **Performance Tests Timeout**
   - Increase timeout values
   - Check database indexes
   - Review query optimization

4. **Coverage Not Generated**
   - Install pytest-cov: `pip install pytest-cov`
   - Check coverage configuration in pytest.ini
   - Verify source paths are correct

## Best Practices

### Writing Migration Tests

1. **Test Both Directions**: Always test upgrade and downgrade
2. **Use Transactions**: Wrap tests in transactions for isolation
3. **Test with Data**: Include data preservation tests
4. **Check Schema**: Validate resulting schema matches expectations

### Writing Performance Tests

1. **Use Realistic Data**: Create representative test datasets
2. **Measure Consistently**: Use same timing methods throughout
3. **Set Baselines**: Establish performance requirements
4. **Test at Scale**: Include tests with larger datasets
5. **Monitor Queries**: Track query count and complexity

### CI/CD Integration

1. **Run on Every PR**: Include in pull request checks
2. **Fail Fast**: Stop on first critical failure
3. **Generate Reports**: Create artifacts for review
4. **Track Trends**: Monitor performance over time
5. **Parallel Execution**: Run independent tests in parallel

## Maintenance

### Updating Tests

When adding new migrations:
1. Add specific migration tests if needed
2. Update schema validation tests
3. Review performance baselines
4. Update documentation

When modifying models:
1. Update test fixtures
2. Review affected performance tests
3. Update migration tests
4. Verify data preservation

### Performance Monitoring

Regular tasks:
- Review test execution times monthly
- Update performance baselines quarterly
- Profile slow tests and optimize
- Add new performance tests for new features

## Summary Statistics

### Test Coverage Summary

- **Migration Tests**: 16 test methods
- **Performance Tests**: 14 test methods
- **Total Test Cases**: 30+
- **Code Coverage Target**: 90%+

### Execution Time

- **Full Test Suite**: ~2-3 minutes
- **Migration Tests Only**: ~1 minute
- **Performance Tests Only**: ~1-2 minutes
- **With Coverage**: +30 seconds

## Contact

For questions or issues with the testing infrastructure, please contact the development team or create an issue in the project repository.