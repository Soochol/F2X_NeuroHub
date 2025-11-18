# F2X NeuroHub MES Database

PostgreSQL database schema for F2X NeuroHub Manufacturing Execution System (MES).

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Navigate to database directory
cd /path/to/F2X_NeuroHub/database

# Run master deployment script
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

**Duration**: 15-25 seconds | See [QUICK_START.md](./guides/QUICK_START.md) for details

### Option 2: Verify Existing Deployment

```bash
psql -U postgres -d f2x_neurohub_mes -f verify.sql
```

Expected output:
```
OVERALL STATUS: PASS
```

## Directory Structure

```
database/
├── README.md                     # This file
│
├── deploy.sql                    # Master deployment script (automated)
├── rollback.sql                  # Complete rollback/teardown script
├── verify.sql                    # Comprehensive verification script
├── quick_check.sql               # Quick status check
│
├── requirements/                 # Database requirements & design docs
│   ├── 01-ERD.md                 # Entity-Relationship Diagram
│   ├── 02-entity-definitions.md  # Table definitions and specifications
│   └── 03-relationship-specifications.md  # Foreign key relationships
│
├── guides/                       # User guides & documentation
│   ├── QUICK_START.md            # Quick deployment guide (5 minutes)
│   ├── DEPLOYMENT_GUIDE.md       # Comprehensive deployment documentation
│   ├── DEPLOYMENT_DIAGRAM.md     # Visual execution flow and dependencies
│   └── VERIFICATION_GUIDE.md     # Verification and testing guide
│
├── ddl/                          # Data Definition Language scripts
│   ├── 01_functions/            # 14 PostgreSQL functions
│   │   ├── update_timestamp.sql
│   │   ├── log_audit_event.sql
│   │   ├── prevent_audit_modification.sql
│   │   ├── prevent_process_deletion.sql
│   │   └── prevent_user_deletion.sql
│   └── 02_tables/               # 7 core tables
│       ├── 01_product_models.sql
│       ├── 02_processes.sql     # 8 manufacturing processes
│       ├── 03_users.sql
│       ├── 04_lots.sql          # Batch tracking (max 100 units)
│       ├── 05_serials.sql       # Individual unit tracking
│       ├── 06_process_data.sql  # Transactional data
│       └── 07_audit_logs.sql    # Partitioned audit trail
│
├── views/                        # Optional analytics views
│   └── process_views/           # 8 process-specific views (JSONB flattening)
│
├── scripts/                      # Deployment and utility scripts
│   └── 01-deploy.sh             # Docker init script for PostgreSQL
│
└── test_data.sql                # Sample test data for development
```

## Database Schema Overview

### Core Tables (7)

| Table | Purpose | Records | Partitioned |
|-------|---------|---------|-------------|
| `product_models` | Product definitions | Master Data | No |
| `processes` | 8 manufacturing processes | 8 rows | No |
| `users` | Authentication & roles | Transactional | No |
| `lots` | Production batches | Transactional | No |
| `serials` | Individual units (max 100/LOT) | Transactional | No |
| `process_data` | Process execution records | High Volume | No |
| `audit_logs` | Immutable audit trail | Very High | **Yes** (by month) |

### Functions (5 common + 9 table-specific)

#### Common Functions (5)
- `update_timestamp()` - Auto-update timestamps
- `log_audit_event()` - Comprehensive audit logging
- `prevent_audit_modification()` - Audit immutability
- `prevent_process_deletion()` - Protect process master data
- `prevent_user_deletion()` - Protect user history

#### Table-Specific Functions (9) - Created by DDL scripts
- `generate_lot_number()` - LOT number: WF-KR-YYMMDD{D|N}-nnn
- `validate_lot_status_transition()` - LOT state machine
- `auto_close_lot()` - Auto-close completed LOTs
- `generate_serial_number()` - Serial number: {LOT_NUMBER}-XXXX
- `validate_lot_capacity()` - Max 100 serials/LOT
- `validate_serial_status_transition()` - Serial state machine
- `update_lot_quantities()` - Auto-update LOT counters
- `calculate_process_duration()` - Process timing
- `validate_process_sequence()` - Enforce 1→2→3→...→8
- Plus audit partition management functions

### Master Data: 8 Manufacturing Processes

| # | Code | Name | Duration |
|---|------|------|----------|
| 1 | `LASER_MARKING` | Laser Marking | 60s |
| 2 | `LMA_ASSEMBLY` | LMA Assembly | 180s |
| 3 | `SENSOR_INSPECTION` | Sensor Inspection | 120s |
| 4 | `FIRMWARE_UPLOAD` | Firmware Upload | 300s |
| 5 | `ROBOT_ASSEMBLY` | Robot Assembly | 300s |
| 6 | `PERFORMANCE_TEST` | Performance Test | 180s |
| 7 | `LABEL_PRINTING` | Label Printing | 30s |
| 8 | `PACKAGING_INSPECTION` | Packaging Inspection | 90s |

## Deployment

### Automated Deployment (Recommended)

The `deploy.sql` master script automates the entire database setup:

```bash
# Navigate to database directory
cd /path/to/F2X_NeuroHub/database

# Create database (if needed)
createdb -U postgres f2x_neurohub_mes

# Run deployment
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

**Features**:
- Executes in correct dependency order
- Transaction management with savepoints
- Error handling and rollback capability
- Timing information for each step
- Comprehensive verification

**See**: [QUICK_START.md](./guides/QUICK_START.md) | [DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md) | [DEPLOYMENT_DIAGRAM.md](./guides/DEPLOYMENT_DIAGRAM.md)

### Rollback

To completely remove all database objects:

```bash
psql -U postgres -d f2x_neurohub_mes -f rollback.sql
```

## Verification Checklist

Run `verify.sql` to check:

- [x] **Database Encoding** - UTF8
- [x] **Functions** - 14+ present (5 common + 9+ table-specific)
- [x] **Tables** - 7 present + 3 partitions
- [x] **Constraints** - PKs, FKs, Unique, Check
- [x] **Indexes** - 50+ indexes (including GIN on JSONB)
- [x] **Triggers** - 20+ automation triggers
- [x] **Master Data** - 8 processes loaded
- [x] **Partitions** - audit_logs partitioned monthly
- [x] **Comments** - Tables and columns documented

## Key Features

### 1. Comprehensive Audit Trail
- **Immutable** audit logs (cannot UPDATE or DELETE)
- **Partitioned** by month for performance
- **Automatic** logging via triggers
- **Complete** before/after snapshots (JSONB)

### 2. Process Sequence Enforcement
- **Ordered** execution: Process 1 → 2 → 3 → ... → 8
- **Validated** by trigger before insert
- **Flexible** rework support (max 3 attempts)

### 3. LOT/Serial Relationship
- **1 LOT** = max **100 serials**
- **LOT Number**: WF-KR-YYMMDD{D|N}-nnn
- **Serial Number**: {LOT_NUMBER}-XXXX
- **Auto-generated** via triggers

### 4. Status State Machines

**LOT Status:**
```
CREATED → IN_PROGRESS → COMPLETED → CLOSED
```

**Serial Status:**
```
CREATED → IN_PROGRESS → PASSED
              ↓
            FAILED → IN_PROGRESS (rework, max 3x)
```

### 5. JSONB Flexibility
- `product_models.specifications` - Product specs
- `processes.quality_criteria` - Quality standards
- `process_data.measurements` - Process measurements
- `process_data.defects` - Defect information
- `audit_logs.old_values` / `new_values` - Change tracking

All JSONB columns have **GIN indexes** for efficient queries.

## Common Queries

### 1. Verify All 8 Processes Exist
```sql
SELECT process_number, process_code, process_name_ko, process_name_en
FROM processes
ORDER BY process_number;
```

### 2. Check LOT Production Status
```sql
SELECT
    lot_number,
    status,
    target_quantity,
    actual_quantity,
    passed_quantity,
    failed_quantity
FROM lots
WHERE production_date = CURRENT_DATE
ORDER BY lot_number;
```

### 3. Serial Production Progress
```sql
SELECT
    s.serial_number,
    s.status,
    s.rework_count,
    COUNT(pd.id) AS completed_processes
FROM serials s
LEFT JOIN process_data pd ON s.id = pd.serial_id AND pd.result = 'PASS'
WHERE s.lot_id = 1
GROUP BY s.id, s.serial_number, s.status, s.rework_count
ORDER BY s.sequence_in_lot;
```

### 4. Audit History for Serial
```sql
SELECT
    al.action,
    al.created_at,
    u.username,
    al.old_values->>'status' AS old_status,
    al.new_values->>'status' AS new_status
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'serials'
  AND al.entity_id = 100
ORDER BY al.created_at DESC;
```

### 5. Process Failure Analysis
```sql
SELECT
    p.process_name_ko,
    COUNT(*) AS failure_count,
    COUNT(DISTINCT pd.serial_id) AS affected_serials
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.result = 'FAIL'
  AND pd.created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.id, p.process_name_ko
ORDER BY failure_count DESC;
```

## Performance Considerations

### Indexes
- **50+ indexes** for query optimization
- **GIN indexes** on all JSONB columns
- **Partial indexes** for common WHERE clauses
- **Composite indexes** for multi-column queries

### Partitioning
- **audit_logs** partitioned by month
- **Automatic partition creation** via functions
- **3-year retention** policy (configurable)

### Triggers
- **20+ triggers** for automation
- **Minimal overhead** (efficient PL/pgSQL)
- **Transaction safety** (all within transactions)

## Troubleshooting

### Issue: Verification Fails

**Solution:**
```bash
# Re-deploy all DDL
cd database/ddl
for dir in 01_functions 02_tables; do
    for file in $dir/*.sql; do
        echo "Deploying $file..."
        psql -U postgres -d f2x_neurohub_mes -f "$file"
    done
done

# Verify again
psql -U postgres -d f2x_neurohub_mes -f verify.sql
```

### Issue: Missing Partitions

**Solution:**
```sql
-- Create partitions for next 3 months
SELECT create_future_audit_partitions(3);
```

### Issue: No Process Master Data

**Solution:**
```bash
# Re-run processes table DDL (includes INSERT statements)
psql -U postgres -d f2x_neurohub_mes -f ddl/02_tables/02_processes.sql
```

## Documentation

### Requirements & Design
- **[01-ERD.md](./requirements/01-ERD.md)** - Entity-Relationship Diagram
- **[02-entity-definitions.md](./requirements/02-entity-definitions.md)** - Complete table specifications
- **[03-relationship-specifications.md](./requirements/03-relationship-specifications.md)** - Foreign key relationships

### Deployment & Operations
- **[QUICK_START.md](./guides/QUICK_START.md)** - 5-minute deployment guide
- **[DEPLOYMENT_GUIDE.md](./guides/DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation
- **[DEPLOYMENT_DIAGRAM.md](./guides/DEPLOYMENT_DIAGRAM.md)** - Visual execution flow and dependencies
- **`deploy.sql`** - Master deployment script (automated, with inline documentation)
- **`rollback.sql`** - Complete rollback script (with safety confirmations)

### Verification & Testing
- **`verify.sql`** - Comprehensive verification script (9 validation sections)
- **`quick_check.sql`** - Quick status check (< 2 seconds)
- **[VERIFICATION_GUIDE.md](./guides/VERIFICATION_GUIDE.md)** - Detailed verification guide

## Support

- **Database Team**: database@f2x.com
- **GitHub**: https://github.com/f2x/neurohub-mes
- **Documentation**: See `requirements/` and `guides/` directories

---

**Version:** 1.0
**PostgreSQL:** 14+
**Last Updated:** 2025-11-18
