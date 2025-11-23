# WIP Tracking System Implementation Guide

**F2X NeuroHub MES - Team 2 Database Development**

**Author**: F2X Database Team
**Date**: 2025-11-21
**Version**: 1.0.0
**Status**: ✅ Implementation Complete

---

## 📋 Executive Summary

Successfully implemented comprehensive WIP (Work In Progress) tracking system for F2X NeuroHub MES. The system provides temporary ID management for products during manufacturing processes 1-6, before serial number generation at process 7.

### Key Features Delivered

✅ **WIP Item Tracking** - Individual unit tracking with temporary IDs
✅ **Process History** - Detailed execution records for processes 1-6
✅ **Database Integration** - Seamless integration with existing tables
✅ **Analytics Views** - Real-time dashboards and queue monitoring
✅ **Performance Optimization** - Comprehensive indexing and partitioning strategy
✅ **ORM Models** - Python SQLAlchemy 2.0 models ready for use

---

## 🗄️ Database Schema

### 1. wip_items Table

**Purpose**: Track individual products during processes 1-6 using temporary WIP IDs

**Location**: `database/ddl/02_tables/11_wip_items.sql`

#### Core Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `wip_id` | VARCHAR(50) | Auto-generated WIP identifier (WIP-{LOT}-{SEQ}) |
| `lot_id` | BIGINT | Foreign key to parent LOT |
| `serial_id` | BIGINT | Linked serial (NULL until process 7) |
| `sequence_in_lot` | INTEGER | Position in LOT (1-100) |
| `status` | VARCHAR(20) | CREATED, IN_PROGRESS, COMPLETED, FAILED |
| `current_process_id` | BIGINT | Current/last process location |
| `created_at` | TIMESTAMPTZ | WIP creation time |
| `updated_at` | TIMESTAMPTZ | Last update time |
| `completed_at` | TIMESTAMPTZ | Serial generation time (process 7) |

#### WIP ID Format

```
WIP-{LOT_NUMBER}-{SEQUENCE}

Example: WIP-KR01PSA2511-001
- Prefix: "WIP-"
- LOT_NUMBER: KR01PSA2511 (14 chars)
- Separator: "-"
- Sequence: 001 (3 digits, zero-padded, 001-100)

Total Length: 22 characters
```

#### Status State Machine

```
CREATED → IN_PROGRESS → COMPLETED (or FAILED)
              ↓
           FAILED → IN_PROGRESS (rework)
```

#### Constraints

- **UNIQUE**: `wip_id` (globally unique)
- **UNIQUE**: `(lot_id, sequence_in_lot)` (unique within LOT)
- **CHECK**: `sequence_in_lot BETWEEN 1 AND 100`
- **CHECK**: `status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')`

#### Indexes

1. `idx_wip_items_lot` - Foreign key lookup
2. `idx_wip_items_status` - Status filtering
3. `idx_wip_items_active` - Active WIP queries (partial index)
4. `idx_wip_items_lot_status_process` - Composite LOT-level queries
5. `idx_wip_items_process_queue` - Process station queuing

---

### 2. wip_process_history Table

**Purpose**: Detailed process execution history for WIP items (processes 1-6)

**Location**: `database/ddl/02_tables/12_wip_process_history.sql`

#### Core Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `wip_id` | BIGINT | WIP item reference (FK) |
| `process_id` | BIGINT | Process reference (FK) |
| `operator_id` | BIGINT | Operator who performed work (FK) |
| `equipment_id` | BIGINT | Equipment used (FK, nullable) |
| `result` | VARCHAR(10) | PASS, FAIL, REWORK |
| `measurements` | JSONB | Process measurement data |
| `defects` | JSONB | Defect information array |
| `notes` | TEXT | Operator notes |
| `started_at` | TIMESTAMPTZ | Process start timestamp |
| `completed_at` | TIMESTAMPTZ | Process completion timestamp |
| `duration_seconds` | INTEGER | Calculated duration |
| `scan_timestamp` | TIMESTAMPTZ | Barcode scan timestamp |

#### JSONB Data Examples

**Measurements (LASER_MARKING - Process 1)**:
```json
{
    "marking_quality": "GOOD",
    "readability_score": 0.98,
    "position_offset_mm": 0.05,
    "laser_power_actual": "19.8W",
    "marking_time_seconds": 58
}
```

**Defects Array (when result = FAIL)**:
```json
[
    {
        "defect_code": "WIP-E001",
        "defect_name": "Poor laser marking quality",
        "severity": "CRITICAL",
        "measured_value": 0.65,
        "expected_value": ">0.85",
        "action_required": "REWORK"
    }
]
```

#### Indexes

1. `idx_wip_process_history_wip` - WIP item lookup
2. `idx_wip_process_history_wip_process` - Traceability queries
3. `idx_wip_process_history_failed` - Failed process analysis (partial)
4. `idx_wip_process_history_measurements` - GIN index for JSONB queries
5. `idx_wip_process_history_defects` - GIN index for defect queries

---

### 3. process_data Table Integration

**Purpose**: Add WIP tracking compatibility to existing process_data table

**Location**: `database/ddl/03_migrations/add_wip_tracking.sql`

#### Changes Applied

1. **New Column**: `wip_id BIGINT` (nullable, FK to wip_items)
2. **Foreign Key**: `fk_process_data_wip`
3. **Check Constraint**: `wip_id OR serial_id must be set`
4. **Indexes**:
   - `idx_process_data_wip` - WIP lookups
   - `idx_process_data_wip_process` - Composite traceability
   - `idx_process_data_wip_result` - Result filtering

#### Helper Function

```sql
migrate_wip_to_serial_process_data(p_wip_id BIGINT, p_serial_id BIGINT)
```

**Purpose**: Migrate process_data records from WIP to Serial tracking when WIP transitions to Serial at process 7.

**Returns**: Number of records updated

---

## 📊 Analytics Views

### 1. mv_wip_status_dashboard

**Purpose**: Real-time WIP status overview for production dashboards

**Location**: `database/views/wip_views/01_mv_wip_status_dashboard.sql`

**Type**: Materialized View (CONCURRENT refresh enabled)

#### Key Metrics

- WIP count by status (CREATED, IN_PROGRESS, COMPLETED, FAILED)
- Process location distribution (processes 1-6)
- Completion rate percentage
- Failure rate percentage
- Average cycle time per WIP item
- First WIP created and last WIP completed timestamps

#### Refresh Strategy

```sql
-- Manual refresh
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_wip_status_dashboard;

-- Automated (using pg_cron)
SELECT cron.schedule('refresh-wip-dashboard', '*/5 * * * *',
    'SELECT refresh_wip_status_dashboard()');
```

**Recommended Interval**: Every 1-5 minutes during production hours

#### Sample Query

```sql
SELECT
    lot_number,
    total_wip_count,
    in_progress_count,
    completed_count,
    completion_rate_pct,
    avg_cycle_time_seconds
FROM mv_wip_status_dashboard
WHERE production_date = CURRENT_DATE
ORDER BY lot_number;
```

---

### 2. mv_process_wip_queue

**Purpose**: Process-level WIP queue monitoring for bottleneck detection

**Location**: `database/views/wip_views/02_mv_process_wip_queue.sql`

**Type**: Materialized View (CONCURRENT refresh enabled)

#### Key Metrics

- WIP count waiting at each process station
- Average wait time at each process
- Maximum wait time (oldest WIP alert)
- Throughput metrics (last hour)
- Pass rate percentage
- Estimated queue clearance time
- Alert flags (stuck WIP, bottleneck detection)

#### Alert Flags

- `has_stuck_wip`: TRUE if any WIP waiting > 1 hour
- `is_bottleneck`: TRUE if queue has > 50 WIP items

#### Sample Query

```sql
-- Identify current bottlenecks
SELECT
    process_number,
    process_code,
    process_name_en,
    wip_count_at_process,
    estimated_queue_time_hours
FROM mv_process_wip_queue
WHERE is_bottleneck = true
ORDER BY wip_count_at_process DESC;
```

---

## 🔄 Triggers & Functions

### Auto-Generated Functions

| Function | Purpose | Trigger Point |
|----------|---------|---------------|
| `generate_wip_id()` | Auto-generate WIP ID | BEFORE INSERT on wip_items |
| `validate_wip_status_transition()` | Enforce state machine | BEFORE UPDATE on wip_items |
| `auto_complete_wip_on_serial_creation()` | Mark COMPLETED when serial_id set | BEFORE UPDATE on wip_items |
| `calculate_wip_process_duration()` | Calculate duration_seconds | BEFORE INSERT/UPDATE on wip_process_history |
| `update_wip_current_process()` | Update WIP current_process_id | AFTER INSERT on wip_process_history |
| `migrate_wip_to_serial_process_data()` | Migrate records to serial tracking | Helper function (manual call) |
| `refresh_wip_status_dashboard()` | Refresh dashboard view | Helper function (scheduled) |
| `refresh_process_wip_queue()` | Refresh queue view | Helper function (scheduled) |
| `refresh_all_wip_views()` | Refresh all WIP views | Helper function (scheduled) |

---

## 🚀 Deployment

### Prerequisites

1. ✅ PostgreSQL 14+
2. ✅ Base schema deployed (lots, serials, processes, process_data)
3. ✅ Master data loaded (8 processes)

### Deployment Script

**Location**: `database/deploy_wip_tracking.sql`

**Execution**:

```bash
cd /path/to/F2X_NeuroHub/database
psql -U postgres -d f2x_neurohub_mes -f deploy_wip_tracking.sql
```

**Duration**: ~30-60 seconds

### Deployment Phases

1. **Phase 1**: Deploy core tables (wip_items, wip_process_history)
2. **Phase 2**: Integrate with existing tables (process_data)
3. **Phase 3**: Deploy analytics views (materialized views)
4. **Phase 4**: Verification and summary

### Rollback

See `database/ddl/03_migrations/add_wip_tracking.sql` for rollback script (commented at bottom).

---

## 💻 Python ORM Models

### WipItem Model

**Location**: `backend/app/models/wip_item.py`

**Status**: ✅ Already implemented

#### Key Features

- SQLAlchemy 2.0 compatible
- Enum-based status management (`WipStatus`)
- Relationship mapping to Lot, Serial, Process, WipProcessHistory
- Helper methods: `can_transition_to()`, `is_active()`, `can_start_process()`
- Dictionary serialization: `to_dict()`

#### Usage Example

```python
from app.models.wip_item import WipItem, WipStatus

# Query active WIP items for a LOT
active_wips = session.query(WipItem).filter(
    WipItem.lot_id == 5,
    WipItem.status.in_([WipStatus.CREATED, WipStatus.IN_PROGRESS])
).all()

# Check if WIP can transition to new status
if wip_item.can_transition_to(WipStatus.COMPLETED):
    wip_item.status = WipStatus.COMPLETED
    wip_item.completed_at = datetime.utcnow()
    session.commit()
```

---

### WipProcessHistory Model

**Location**: `backend/app/models/wip_process_history.py`

**Status**: ✅ Already implemented

#### Key Features

- JSONB support for measurements and defects
- Relationship mapping to WipItem, Process, User, Equipment
- Helper methods: `is_successful()`, `calculate_duration()`, `defect_count`
- Dictionary serialization: `to_dict()`

#### Usage Example

```python
from app.models.wip_process_history import WipProcessHistory, ProcessResult

# Record process execution
history = WipProcessHistory(
    wip_item_id=42,
    process_id=3,  # Sensor Inspection
    operator_id=5,
    equipment_id=12,
    result=ProcessResult.PASS,
    measurements={
        "sensor_channels_tested": 8,
        "signal_quality_avg": 0.92,
        "noise_level_db": -45
    },
    started_at=datetime.utcnow(),
    completed_at=datetime.utcnow(),
)
session.add(history)
session.commit()
```

---

## 📈 Performance Optimization

### Indexing Strategy

**Total Indexes Created**: 20+ specialized indexes

#### Index Types

1. **B-Tree Indexes**: Foreign keys, status columns, timestamps
2. **Partial Indexes**: Active WIP, failed processes (WHERE clauses)
3. **Composite Indexes**: Multi-column queries (lot_id + status + process_id)
4. **GIN Indexes**: JSONB columns (measurements, defects)
5. **Unique Indexes**: Constraint enforcement (wip_id, lot_sequence)

#### Index Usage Monitoring

```sql
-- Check index usage statistics
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename LIKE 'wip%'
ORDER BY idx_scan DESC;
```

---

### Partitioning Strategy

**Status**: 🔄 Optional (commented out in DDL)

**Target Table**: `wip_process_history`

**Trigger Condition**: > 1M records per month

#### Partitioning Plan

- **Method**: RANGE partitioning by `started_at`
- **Interval**: Monthly partitions
- **Retention**: 12-24 months active, then archive
- **Auto-creation**: Function `create_wip_history_monthly_partition()`

#### Enable Partitioning

See `database/ddl/02_tables/12_wip_process_history.sql` line 420+ for commented partitioning code.

---

## 🔍 Verification Queries

### Check Deployment Status

```sql
-- Verify tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE 'wip%';

-- Verify functions
SELECT routine_name
FROM information_schema.routines
WHERE routine_name LIKE '%wip%';

-- Verify indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename LIKE 'wip%';

-- Verify materialized views
SELECT matviewname
FROM pg_matviews
WHERE matviewname LIKE '%wip%';
```

---

### Test WIP Workflow

```sql
-- 1. Create test LOT
INSERT INTO lots (lot_number, product_model_id, production_date, shift, target_quantity)
VALUES ('KR01PSA2511', 1, CURRENT_DATE, 'D', 10);

-- 2. Create WIP items for LOT
INSERT INTO wip_items (lot_id, sequence_in_lot)
SELECT
    (SELECT id FROM lots WHERE lot_number = 'KR01PSA2511'),
    generate_series(1, 10);

-- 3. Verify WIP IDs auto-generated
SELECT wip_id, sequence_in_lot, status
FROM wip_items
WHERE lot_id = (SELECT id FROM lots WHERE lot_number = 'KR01PSA2511')
ORDER BY sequence_in_lot;

-- Expected output:
-- WIP-KR01PSA2511-001 | 1 | CREATED
-- WIP-KR01PSA2511-002 | 2 | CREATED
-- ...
-- WIP-KR01PSA2511-010 | 10 | CREATED

-- 4. Record process execution
INSERT INTO wip_process_history (
    wip_id, process_id, operator_id, result,
    measurements, started_at, completed_at
)
SELECT
    id,
    1,  -- Process 1: Laser Marking
    1,  -- Test operator
    'PASS',
    '{"marking_quality": "GOOD", "readability_score": 0.98}'::jsonb,
    NOW(),
    NOW() + INTERVAL '1 minute'
FROM wip_items
WHERE lot_id = (SELECT id FROM lots WHERE lot_number = 'KR01PSA2511')
LIMIT 1;

-- 5. Check WIP updated
SELECT wip_id, status, current_process_id
FROM wip_items
WHERE lot_id = (SELECT id FROM lots WHERE lot_number = 'KR01PSA2511');

-- Expected: status = 'IN_PROGRESS', current_process_id = 1
```

---

## 📚 Integration with Application

### Required Code Changes

#### 1. LOT Creation Hook

**Location**: `backend/app/crud/lot.py` or `backend/app/services/lot_service.py`

**Action**: Auto-generate WIP items when LOT is created

```python
# When creating a new LOT
lot = create_lot(lot_data)  # Existing code

# NEW: Generate WIP items for this LOT
for seq in range(1, lot.target_quantity + 1):
    wip_item = WipItem(
        lot_id=lot.id,
        sequence_in_lot=seq,
        status=WipStatus.CREATED
    )
    session.add(wip_item)

session.commit()
```

---

#### 2. Process Execution (Processes 1-6)

**Location**: `backend/app/api/v1/processes.py` or process execution endpoints

**Action**: Use WIP ID instead of Serial ID for processes 1-6

```python
# OLD (processes 1-6 using serial_id)
process_data = ProcessData(
    lot_id=lot_id,
    serial_id=serial_id,  # ❌ Should be NULL for processes 1-6
    process_id=process_id,
    ...
)

# NEW (processes 1-6 using wip_id)
process_data = ProcessData(
    lot_id=lot_id,
    wip_id=wip_id,  # ✅ Use WIP ID
    serial_id=None,  # NULL for processes 1-6
    process_id=process_id,
    ...
)

# Also record in WIP process history
wip_history = WipProcessHistory(
    wip_item_id=wip_item.id,
    process_id=process_id,
    operator_id=operator_id,
    result=result,
    measurements=measurements,
    ...
)
session.add(wip_history)
```

---

#### 3. Process 7 (Label Printing) - WIP → Serial Transition

**Location**: `backend/app/api/v1/processes.py` - Process 7 endpoint

**Action**: Generate Serial and link to WIP item

```python
# Process 7: Label Printing - Generate Serial
if process_number == 7:
    # 1. Generate serial number
    serial = Serial(
        lot_id=lot_id,
        sequence_in_lot=wip_item.sequence_in_lot,
        status=SerialStatus.CREATED
    )
    session.add(serial)
    session.flush()  # Get serial.id

    # 2. Link WIP to Serial
    wip_item.serial_id = serial.id
    wip_item.status = WipStatus.COMPLETED
    wip_item.completed_at = datetime.utcnow()

    # 3. Migrate process_data records from WIP to Serial
    from sqlalchemy import text
    session.execute(
        text("SELECT migrate_wip_to_serial_process_data(:wip_id, :serial_id)"),
        {"wip_id": wip_item.id, "serial_id": serial.id}
    )

    # 4. Record in process_data with both wip_id and serial_id
    process_data = ProcessData(
        lot_id=lot_id,
        wip_id=wip_item.id,
        serial_id=serial.id,  # ✅ Now has serial
        process_id=process_id,
        ...
    )

    session.commit()
```

---

#### 4. Dashboard API Endpoints

**Location**: `backend/app/api/v1/dashboard.py` (new or existing)

**Action**: Expose WIP analytics views

```python
from app.database import get_db_session

@router.get("/wip/status-dashboard")
def get_wip_status_dashboard(
    production_date: Optional[date] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get WIP status dashboard for specified production date.
    Uses materialized view mv_wip_status_dashboard.
    """
    query = db.execute(
        text("""
            SELECT * FROM mv_wip_status_dashboard
            WHERE (:prod_date IS NULL OR production_date = :prod_date)
            ORDER BY production_date DESC, lot_number
        """),
        {"prod_date": production_date}
    )
    return [dict(row) for row in query]

@router.get("/wip/process-queue")
def get_process_wip_queue(db: Session = Depends(get_db_session)):
    """
    Get WIP queue status for all process stations.
    Uses materialized view mv_process_wip_queue.
    """
    query = db.execute(text("SELECT * FROM mv_process_wip_queue ORDER BY process_number"))
    return [dict(row) for row in query]
```

---

## 🧪 Testing Checklist

### Database Layer Tests

- [ ] WIP ID auto-generation on LOT creation
- [ ] WIP status state machine transitions
- [ ] WIP → Serial transition at process 7
- [ ] Foreign key constraints enforcement
- [ ] Check constraints validation
- [ ] Unique constraints (wip_id, lot_sequence)
- [ ] Trigger execution (generate_wip_id, auto_complete, etc.)
- [ ] JSONB data insertion and querying
- [ ] Materialized view refresh performance

---

### Application Layer Tests

- [ ] LOT creation generates WIP items
- [ ] Process 1-6 execution uses WIP IDs
- [ ] Process 7 generates Serial and links to WIP
- [ ] process_data migration function works
- [ ] WIP status updates correctly
- [ ] Dashboard API endpoints return correct data
- [ ] WIP traceability queries work end-to-end

---

### Performance Tests

- [ ] Index usage verification (pg_stat_user_indexes)
- [ ] Query performance benchmarks (EXPLAIN ANALYZE)
- [ ] Materialized view refresh time < 5 seconds
- [ ] WIP item creation batch performance (100 items < 1s)
- [ ] Process history insertion rate (> 100 records/s)

---

## 📦 Deliverables Summary

### Database Scripts ✅

| File | Status | Description |
|------|--------|-------------|
| `database/ddl/02_tables/11_wip_items.sql` | ✅ | WIP items table DDL |
| `database/ddl/02_tables/12_wip_process_history.sql` | ✅ | WIP process history table DDL |
| `database/ddl/03_migrations/add_wip_tracking.sql` | ✅ | process_data integration migration |
| `database/views/wip_views/01_mv_wip_status_dashboard.sql` | ✅ | WIP status dashboard view |
| `database/views/wip_views/02_mv_process_wip_queue.sql` | ✅ | Process queue monitoring view |
| `database/deploy_wip_tracking.sql` | ✅ | Master deployment script |

### Python ORM Models ✅

| File | Status | Description |
|------|--------|-------------|
| `backend/app/models/wip_item.py` | ✅ | WipItem ORM model |
| `backend/app/models/wip_process_history.py` | ✅ | WipProcessHistory ORM model |

### Documentation ✅

| File | Status | Description |
|------|--------|-------------|
| `database/WIP_TRACKING_IMPLEMENTATION.md` | ✅ | This implementation guide |

---

## 🎯 Business Rules Implemented

### BR-001: WIP ID Generation
✅ Auto-generate WIP ID in format `WIP-{LOT_NUMBER}-{SEQUENCE}`
✅ Sequence is unique within LOT (1-100)
✅ WIP ID is globally unique

### BR-002: WIP Status Lifecycle
✅ CREATED → IN_PROGRESS (start processing)
✅ IN_PROGRESS → COMPLETED (serial generated at process 7)
✅ IN_PROGRESS → FAILED (quality failure)
✅ FAILED → IN_PROGRESS (rework attempt)

### BR-003: Process Tracking
✅ Processes 1-6 tracked via WIP ID
✅ Process 7+ tracked via Serial ID
✅ WIP → Serial transition at process 7

### BR-004: Process Sequence Enforcement
✅ Process execution must follow sequence (1→2→...→6)
✅ Process 7 requires all processes 1-6 to be PASS

### BR-005: Data Integrity
✅ Foreign key constraints to lots, serials, processes
✅ Check constraints for status, sequence range
✅ Unique constraints prevent duplicates
✅ Triggers enforce state machine rules

---

## 🚨 Known Limitations

1. **Partitioning**: Optional, not enabled by default. Enable if wip_process_history exceeds 1M records/month.

2. **Rework Tracking**: Current implementation tracks rework attempts via multiple wip_process_history records with result='REWORK'. No explicit rework_count column in wip_items.

3. **Materialized View Lag**: Views show data as of last refresh (not real-time). Refresh interval determines data freshness.

---

## 📞 Support

For questions or issues related to WIP tracking implementation:

- **Database Team**: database@f2x.com
- **GitHub Issues**: https://github.com/f2x/neurohub-mes/issues
- **Documentation**: `database/` directory

---

## 🔄 Future Enhancements

1. **Auto-refresh**: Implement pg_cron scheduled view refresh
2. **Partitioning**: Enable partitioning for wip_process_history when volume increases
3. **Additional Views**: Add views for defect analysis, operator performance, equipment utilization
4. **Data Archival**: Implement archival policy for completed WIP items
5. **Real-time Alerts**: Add database-level alerts for stuck WIP items and bottlenecks

---

**Implementation Status**: ✅ **COMPLETE**
**Ready for Production**: ✅ **YES** (after application integration)
**Next Steps**: Application code integration and testing

---

_Last Updated: 2025-11-21 by F2X Database Team_
