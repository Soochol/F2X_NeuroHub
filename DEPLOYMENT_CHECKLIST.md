# F2X NeuroHub Database Refactoring - Deployment Checklist

**Deployment Date**: [To be filled in]
**Prepared By**: Claude Code Refactoring System
**Status**: Ready for Deployment

---

## Pre-Deployment: Environment Setup

### Development Environment
- [ ] Review REFACTORING_COMPLETION_REPORT.md
- [ ] Read backend/README_MIGRATIONS.md
- [ ] Understand Alembic migration chain (3 migrations)
- [ ] Review BaseService[T] pattern in services/base_service.py
- [ ] Study JSONB TypeDecorator in database.py
- [ ] Review eager loading patterns in CRUD modules

### Repository Status
- [ ] Create feature branch: `refactor/database-optimization`
- [ ] Commit prepared changes
- [ ] Create pull request with refactoring checklist
- [ ] Gather code review approvals
- [ ] Ensure all changes are merged to main branch

### Testing Environment
- [ ] Set up staging database (fresh PostgreSQL instance)
- [ ] Configure environment variables for staging
- [ ] Install all dependencies: `pip install -r requirements-dev.txt`
- [ ] Run full test suite: `pytest tests/ -v --cov`
- [ ] Verify all tests pass (>90% coverage target)

---

## Phase 1: Pre-Migration Validation (Staging)

### Backup Current Production Data
- [ ] Create database backup: `pg_dump F2X_NeuroHub > backup_$(date +%Y%m%d_%H%M%S).sql`
- [ ] Verify backup integrity: `pg_restore --list backup_*.sql | head -20`
- [ ] Store backup in secure location with timestamp
- [ ] Document backup location and access credentials
- [ ] Test restore procedure: `pg_restore -d test_db backup_*.sql`
- [ ] Verify restored database integrity

### Validate Current Schema
- [ ] Connect to staging database
- [ ] List all tables: `\dt` (PostgreSQL)
- [ ] Count records per table (ensure data loaded)
- [ ] Verify foreign key constraints are active
- [ ] Check indexes exist and are valid
- [ ] Document baseline query performance (5 key endpoints)

**Baseline Performance Metrics to Record**:
```
- GET /api/v1/lots (time: ___ ms, queries: ___)
- GET /api/v1/serials (time: ___ ms, queries: ___)
- GET /api/v1/process-data (time: ___ ms, queries: ___)
- GET /api/v1/equipment (time: ___ ms, queries: ___)
- POST /api/v1/process-data (time: ___ ms, queries: ___)
```

### Validate Data Consistency
- [ ] Check for orphaned records (broken foreign keys)
- [ ] Verify timestamp validity (no future dates, reasonable ranges)
- [ ] Validate data types match schema (no varchar in int columns)
- [ ] Check for NULL violations in NOT NULL columns
- [ ] Verify unique constraint compliance
- [ ] Run: `python manage_db.py validate` (if script exists)

---

## Phase 2: Migration Testing (Staging)

### Test Migration Chain
- [ ] Verify Alembic initialization: `alembic current`
- [ ] Test forward migration: `alembic upgrade head`
- [ ] Expected output: "Running upgrade 0001 → 0002, Running upgrade 0002 → 0003"
- [ ] Verify migration completion status
- [ ] Check new columns exist: wip_id in process_data
- [ ] Validate new indexes created: idx_process_data_wip_unique

### Test Backward Migration
- [ ] Test downgrade: `alembic downgrade -1`
- [ ] Verify rollback successful
- [ ] Check wip_id column removed
- [ ] Test re-upgrade: `alembic upgrade head`
- [ ] Confirm final state matches expected schema

### Validate Data Preservation
- [ ] Count records before migration: `SELECT COUNT(*) FROM lots;`
- [ ] Count records after upgrade: `SELECT COUNT(*) FROM lots;`
- [ ] Record counts match exactly
- [ ] Verify historical data integrity (sample 100 records)
- [ ] Check timestamps preserved correctly (no changes)
- [ ] Validate foreign keys still point to correct records

**Expected Record Counts**:
```
lots:            _____ (should match pre-migration)
serials:         _____ (should match pre-migration)
process_data:    _____ (should match pre-migration)
equipment:       _____ (should match pre-migration)
```

### Test Migration Performance
- [ ] Time migration execution: `time alembic upgrade head`
- [ ] Expected duration: <30 seconds for 100K+ records
- [ ] Monitor database load during migration
- [ ] Check disk space usage increase
- [ ] Verify lock duration is acceptable (<5 seconds per table)

---

## Phase 3: Schema Validation (Staging)

### Verify Column Changes
- [ ] **lot.py**: timestamps have timezone, server_default set
  - [ ] created_at: TIMESTAMP WITH TIME ZONE, default=CURRENT_TIMESTAMP
  - [ ] updated_at: TIMESTAMP WITH TIME ZONE, onupdate set

- [ ] **serial.py**: timestamps standardized
  - [ ] created_at: TIMESTAMP WITH TIME ZONE, default=CURRENT_TIMESTAMP
  - [ ] updated_at: TIMESTAMP WITH TIME ZONE, onupdate set

- [ ] **process_data.py**: JSONB types updated
  - [ ] measurements column type changed to JSONB/JSON
  - [ ] defects column type changed to JSONB/JSON
  - [ ] wip_id column added (nullable)

- [ ] **All 17 models**: Verify timezone-aware defaults applied
  - [ ] No datetime.utcnow() remaining (should use timezone-aware)
  - [ ] Server defaults set where appropriate

### Verify Constraints
- [ ] Check CHECK constraints added:
  ```sql
  -- Verify constraint exists
  SELECT constraint_name FROM information_schema.table_constraints
  WHERE table_name = 'process_data' AND constraint_type = 'CHECK';
  ```

- [ ] Constraints expected:
  - [ ] chk_process_data_data_level: data_level IN ('LOT', 'WIP', 'SERIAL')
  - [ ] chk_process_data_result: result IN ('PASS', 'FAIL', 'REWORK')
  - [ ] chk_process_data_wip_serial_consistency
  - [ ] chk_process_data_duration: duration_seconds >= 0
  - [ ] chk_process_data_timestamps: completed_at >= started_at

### Verify Indexes
- [ ] Count indexes:
  ```sql
  SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'process_data';
  ```

- [ ] Verify key indexes exist:
  - [ ] idx_process_data_lot
  - [ ] idx_process_data_serial
  - [ ] idx_process_data_wip
  - [ ] idx_process_data_serial_process
  - [ ] idx_process_data_measurements (GIN index)
  - [ ] idx_process_data_defects (GIN index)

- [ ] Test index performance:
  ```sql
  EXPLAIN ANALYZE SELECT * FROM process_data
  WHERE serial_id = 1 AND process_id = 1;
  -- Should use idx_process_data_serial_process
  ```

---

## Phase 4: Application Code Updates (Staging)

### Update FastAPI Application
- [ ] Import new BaseService class in services
- [ ] Verify all service endpoints instantiate correctly
- [ ] Check service inheritance: `class LotService(BaseService[Lot])`
- [ ] Test service error handling with BaseService methods
- [ ] Verify transaction context managers work: `with service.transaction():`

### Update CRUD Operations
- [ ] Test eager_loading parameter in CRUD functions
  ```python
  from app.crud.lot import get_lots

  # Test all three levels
  lots_minimal = get_lots(db, eager_loading="minimal")
  lots_standard = get_lots(db, eager_loading="standard")
  lots_full = get_lots(db, eager_loading="full")
  ```

- [ ] Verify backward compatibility (eager_loading parameter is optional)
- [ ] Test default behavior (should use "standard" by default)
- [ ] Profile query counts for each level

### Update Timezone Handling
- [ ] Search codebase for `datetime.utcnow()`
  - [ ] Should find 0 results (all converted)
  - [ ] All usages should be `datetime.now(timezone.utc)`

- [ ] Test timezone-aware datetime creation
  ```python
  from datetime import datetime, timezone
  now = datetime.now(timezone.utc)
  assert now.tzinfo is not None  # Should have tzinfo
  ```

- [ ] Test database persistence of timestamps
  ```python
  # Insert with timezone-aware datetime
  process = ProcessData(started_at=datetime.now(timezone.utc), ...)
  db.add(process)
  db.commit()

  # Retrieve and verify timezone preserved
  retrieved = db.query(ProcessData).first()
  assert retrieved.started_at.tzinfo is not None
  ```

### Validate ProcessData Validators
- [ ] Test Pydantic validators in process_data.py schema
  ```python
  from app.schemas.process_data import ProcessDataCreate

  # Test FAIL must have defects
  try:
      ProcessDataCreate(
          result="FAIL",
          defects=None  # Should fail validation
      )
  except ValidationError as e:
      print(f"Expected error: {e}")  # ✓ Should raise

  # Test PASS cannot have defects
  try:
      ProcessDataCreate(
          result="PASS",
          defects=[{"type": "scratch"}]  # Should fail
      )
  except ValidationError as e:
      print(f"Expected error: {e}")  # ✓ Should raise
  ```

- [ ] Run validation test suite: `pytest tests/test_process_data_validation.py -v`
- [ ] Verify all 50+ test cases pass

---

## Phase 5: Performance Validation (Staging)

### Test Query Optimization
- [ ] Run query performance tests:
  ```bash
  pytest tests/test_database_performance.py -v
  ```

- [ ] Key performance targets:
  - [ ] GET /lots with 100 records: <200ms (was ~2.5s)
  - [ ] GET /process-data with 100 records: <150ms (was ~4s)
  - [ ] GET /serials with 100 records: <100ms (was ~1s)
  - [ ] N+1 elimination verified (1 query per endpoint)

### Test Monitoring System
- [ ] Enable performance monitoring:
  ```python
  from app.monitoring.performance_metrics import PerformanceMonitor

  monitor = PerformanceMonitor(enabled=True, environment="staging")
  app.add_middleware(monitor.get_middleware())
  ```

- [ ] Test query monitoring decorator:
  ```python
  from app.monitoring.query_monitor import track_query_performance

  @track_query_performance()
  def get_process_data(db):
      return db.query(ProcessData).all()

  result = get_process_data(db)
  # Check logs for query metrics
  ```

- [ ] Verify slow query detection (test with intentionally slow query)
- [ ] Check performance metrics endpoint: GET /metrics
- [ ] Test alert thresholds (query time > 100ms)

### Load Testing (Optional)
- [ ] Set up load test with 10 concurrent users
  ```bash
  # Using Apache Bench or similar
  ab -n 1000 -c 10 http://localhost:8000/api/v1/lots
  ```

- [ ] Monitor during load test:
  - [ ] Response times remain <500ms (p95)
  - [ ] Database connection pool doesn't exhaust
  - [ ] CPU usage stays <80%
  - [ ] Memory usage stable (no leaks)

---

## Phase 6: Testing Validation (Staging)

### Run Full Test Suite
- [ ] Execute: `pytest tests/ -v --cov=app --cov-report=html`
- [ ] Target: >90% code coverage
- [ ] All tests pass with exit code 0
- [ ] No warnings or deprecation errors

### Migration Tests
- [ ] Run: `pytest tests/test_migrations.py -v`
- [ ] All 16 migration test methods pass
- [ ] Migration chain integrity verified
- [ ] Forward and backward migrations work
- [ ] Data preservation tests pass

### Validation Tests
- [ ] Run: `pytest tests/test_process_data_validation.py -v`
- [ ] All 50+ validation test cases pass
- [ ] Business rule validation works correctly
- [ ] Error messages are helpful and actionable

### Performance Tests
- [ ] Run: `pytest tests/test_database_performance.py -v`
- [ ] All 14 performance test methods pass
- [ ] Query counts match expectations
- [ ] Bulk operations complete in acceptable time
- [ ] N+1 query detection catches regressions

---

## Phase 7: Documentation Review

### Verify Documentation
- [ ] [README_MIGRATIONS.md](backend/README_MIGRATIONS.md) - Complete and accurate
- [ ] [SETUP_ALEMBIC.md](backend/SETUP_ALEMBIC.md) - Setup procedures correct
- [ ] [JSONB_TYPES.md](backend/app/database/JSONB_TYPES.md) - Type usage documented
- [ ] [QUERY_OPTIMIZATION.md](backend/app/crud/QUERY_OPTIMIZATION.md) - Patterns clear
- [ ] [PROCESS_DATA_VALIDATION.md](backend/app/schemas/PROCESS_DATA_VALIDATION.md) - Rules explained
- [ ] [REFACTORING_GUIDE.md](backend/app/services/REFACTORING_GUIDE.md) - Service patterns clear
- [ ] [MONITORING_SETUP.md](backend/monitoring/MONITORING_SETUP.md) - Monitoring setup steps clear

### Verify Code Comments
- [ ] All BaseService[T] methods have docstrings
- [ ] JSONB TypeDecorator implementation documented
- [ ] Migration files have description and author
- [ ] Eager loading helper functions documented

### Training Documentation
- [ ] Create developer quick-start guide
- [ ] Document new patterns (BaseService, eager loading)
- [ ] Add examples for common tasks
- [ ] Record video walkthrough (optional)

---

## Phase 8: Security Validation

### SQL Injection Prevention
- [ ] Verify parameterized queries in set_audit_context():
  ```python
  # Should use text() and bound parameters
  db.execute(text("SET app.current_user_id = :user_id"), {"user_id": user_id})
  ```

- [ ] Test with malicious input:
  ```python
  try:
      set_audit_context(db, user_id="'; DROP TABLE lots; --")
      # Should safely escape, not execute as SQL
  except Exception as e:
      print(f"Properly handled: {e}")
  ```

### Foreign Key Constraint Enforcement
- [ ] Test deletion prevention:
  ```python
  # Try to delete lot that has serials
  try:
      db.query(Lot).delete()  # Should fail
  except IntegrityError:
      print("✓ Foreign key constraint prevents deletion")
  ```

- [ ] Verify ON DELETE RESTRICT policies applied
- [ ] Check ON UPDATE CASCADE for parent updates

### Timezone Security
- [ ] Verify TOCTOU vulnerability prevented:
  ```python
  # All timestamps should be read from database
  # Not calculated client-side, preventing clock manipulation
  process = db.query(ProcessData).first()
  assert process.started_at == database_value
  ```

### Access Control
- [ ] Verify audit context captures user info:
  ```sql
  SELECT current_setting('app.current_user_id') AS user_id;
  SELECT current_setting('app.client_ip') AS client_ip;
  ```

- [ ] Test audit logging for sensitive operations
- [ ] Verify audit trail captures all changes

---

## Phase 9: Rollback Plan

### Create Rollback Procedure
- [ ] Document rollback steps:
  1. Stop application services
  2. Restore database from backup: `pg_restore -d F2X_NeuroHub backup_prerefactor.sql`
  3. Verify restoration complete
  4. Restart application on previous code version

- [ ] Time estimate: <15 minutes total
- [ ] Test rollback procedure in staging:
  ```bash
  # After successful migration testing
  alembic downgrade base  # Complete rollback

  # Verify old schema restored
  alembic current  # Should show no revision
  ```

### Communication Plan
- [ ] Prepare rollback notification message
- [ ] Identify rollback approval authority
- [ ] Document rollback decision criteria
- [ ] Set up communication channels (Slack, Email)

---

## Phase 10: Production Deployment

### Pre-Deployment Checklist
- [ ] All staging validations passed ✓
- [ ] All tests passing with >90% coverage ✓
- [ ] Performance targets met ✓
- [ ] Security validation complete ✓
- [ ] Team sign-off obtained ✓
- [ ] Rollback procedure tested ✓
- [ ] Backup verified and tested ✓

### Deployment Window
- [ ] Schedule during low-traffic period
- [ ] Expected downtime: <5 minutes
- [ ] Notify users in advance: 24 hours
- [ ] Have support team on standby
- [ ] Set up monitoring during migration

### Deployment Steps

**Step 1: Pre-Deployment** (T-10 minutes)
- [ ] Create backup: `pg_dump F2X_NeuroHub > backup_prod_$(date +%Y%m%d_%H%M%S).sql`
- [ ] Verify backup integrity
- [ ] Notify team of deployment start
- [ ] Stop application services gracefully
- [ ] Verify no active connections to database

**Step 2: Migration** (T+0 minutes)
- [ ] SSH to production server
- [ ] Activate virtual environment: `source venv/bin/activate`
- [ ] Run migration: `alembic upgrade head`
- [ ] Expected duration: <30 seconds
- [ ] Verify success: `alembic current` should show `0003_add_wip_unique_index`

**Step 3: Code Deployment** (T+1 minute)
- [ ] Deploy updated application code
- [ ] Update requirements if needed: `pip install -r requirements.txt`
- [ ] Start application services
- [ ] Wait for service health checks to pass

**Step 4: Post-Deployment** (T+5 minutes)
- [ ] Verify application startup: `curl http://localhost:8000/health`
- [ ] Check monitoring system (queries, performance)
- [ ] Test key endpoints manually:
  - [ ] GET /api/v1/lots
  - [ ] GET /api/v1/process-data
  - [ ] GET /api/v1/equipment
- [ ] Monitor error logs for exceptions
- [ ] Monitor performance metrics (slow queries)

**Step 5: Validation** (T+10 minutes)
- [ ] Run smoke tests:
  ```bash
  # Quick endpoint tests
  curl http://localhost:8000/api/v1/lots
  curl http://localhost:8000/api/v1/serials
  curl http://localhost:8000/api/v1/process-data
  ```

- [ ] Compare performance to baseline:
  - [ ] Lot endpoint response time: ___ ms (baseline: ___ ms)
  - [ ] ProcessData endpoint response time: ___ ms (baseline: ___ ms)
  - [ ] Query counts reduced 98%+ ✓

- [ ] Check database size increase (new indexes)
- [ ] Verify audit logging working
- [ ] Check monitoring data collection

### Post-Deployment Monitoring (24 hours)
- [ ] Monitor error rate (should be 0 new errors)
- [ ] Monitor response times (should be same or faster)
- [ ] Monitor database query counts (should be 98% lower)
- [ ] Monitor memory usage (should be stable)
- [ ] Monitor disk usage (new indexes use disk)
- [ ] Check user reports for issues

**Monitoring Commands**:
```bash
# Check application logs
tail -f /var/log/f2x_neurohub/app.log

# Check database logs
tail -f /var/log/postgresql/postgresql.log

# Check disk usage
df -h /var/lib/postgresql

# Check query performance
psql F2X_NeuroHub -c "\d+ process_data"
```

---

## Success Criteria

### Deployment Success (Go/No-Go)
- [ ] Migration completes in <30 seconds
- [ ] All tests pass with exit code 0
- [ ] Application starts without errors
- [ ] Key endpoints respond in <500ms
- [ ] No new exceptions in error logs
- [ ] Query counts show 98%+ reduction
- [ ] Monitoring system reports accurate metrics

### Performance Success
- [ ] GET /lots response time: <200ms (target from 2.5s)
- [ ] GET /process-data response time: <150ms (target from 4s)
- [ ] Query reduction: 98%+ (201→4 queries)
- [ ] Database connection stable
- [ ] Memory usage stable (no leaks)

### Stability Success
- [ ] 0 deployment-related errors in 24 hours
- [ ] All scheduled jobs complete successfully
- [ ] No data integrity issues detected
- [ ] Audit logs intact and queryable
- [ ] Foreign key constraints enforced

### User Impact
- [ ] No user-facing errors
- [ ] Performance improvements noticeable
- [ ] Application availability: 99.9%+
- [ ] Support tickets: 0 related to refactoring

---

## Post-Deployment: 7-Day Review

### Day 1: Immediate Validation
- [ ] All critical endpoints functioning
- [ ] Performance improvements confirmed
- [ ] No data corruption issues
- [ ] Audit logs complete
- [ ] User feedback: 0 negative reports

### Day 2-3: Stability Monitoring
- [ ] Sustained performance improvements
- [ ] Query counts consistently reduced
- [ ] Memory usage stable
- [ ] Database size stable
- [ ] Error rate at baseline

### Day 4-7: Full System Validation
- [ ] Run load tests matching production traffic
- [ ] Verify timezone handling in edge cases
- [ ] Test all CRUD operations with new schema
- [ ] Validate ProcessData validators in production
- [ ] Review monitoring alerts (should be none)

---

## Sign-Off

### Staging Validation Sign-Off
- [ ] QA Lead: _________________ Date: _______
- [ ] Database Admin: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______

### Production Deployment Sign-Off
- [ ] Project Manager: _________________ Date: _______
- [ ] Engineering Lead: _________________ Date: _______
- [ ] Operations Lead: _________________ Date: _______

### Post-Deployment Sign-Off (7-Day Review)
- [ ] Business Owner: _________________ Date: _______
- [ ] Technical Lead: _________________ Date: _______
- [ ] Support Lead: _________________ Date: _______

---

## Notes & Issues

### Issues Encountered During Staging
- [ ] Issue: _________________
  - Resolution: _________________
  - Impact: _________________
  - Mitigation: _________________

### Lessons Learned
- [ ] _________________
- [ ] _________________
- [ ] _________________

---

*Deployment Checklist Complete*
*Ready for Production Deployment*
