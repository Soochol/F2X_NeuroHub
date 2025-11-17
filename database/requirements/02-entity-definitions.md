# Entity Definitions
# F2X NeuroHub MES Database

## Overview

This document provides comprehensive definitions for all 7 core entities in the F2X NeuroHub MES database. Each entity definition includes:

- Purpose and business context
- Complete schema with column specifications
- Constraints (primary keys, foreign keys, unique, check)
- Indexes for performance optimization
- Triggers for business logic enforcement
- Business rules and validation logic

**Database Engine**: PostgreSQL 14+
**Naming Convention**: snake_case for all identifiers
**Character Set**: UTF-8 (supports Korean characters)

---

## Table of Contents

1. [product_models (제품 모델)](#21-product_models-제품-모델)
2. [lots (생산 LOT)](#22-lots-생산-lot)
3. [serials (시리얼 번호)](#23-serials-시리얼-번호)
4. [processes (제조 공정)](#24-processes-제조-공정)
5. [process_data (공정 실행 데이터)](#25-process_data-공정-실행-데이터)
6. [users (사용자)](#26-users-사용자)
7. [audit_logs (감사 로그)](#27-audit_logs-감사-로그)

---

## 2.1 product_models (제품 모델)

### Purpose
Master data table containing product model definitions and specifications. Each record represents a unique product type (e.g., NH-F2X-001) that can be manufactured. This table serves as the foundation for all production activities.

### Business Context
- Product catalog for the NeuroHub F2X series
- Contains technical specifications, production parameters, and quality standards
- Referenced by LOTs to ensure consistent production

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| model_code | VARCHAR(50) | NOT NULL | - | Unique model identifier (e.g., NH-F2X-001) |
| model_name | VARCHAR(255) | NOT NULL | - | Product name (Korean/English) |
| category | VARCHAR(100) | NULL | NULL | Product category or family |
| production_cycle_days | INTEGER | NULL | NULL | Expected production cycle duration in days |
| specifications | JSONB | NULL | '{}' | Technical specifications in JSON format |
| status | VARCHAR(20) | NOT NULL | 'ACTIVE' | Product lifecycle status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE product_models
ADD CONSTRAINT pk_product_models PRIMARY KEY (id);

-- Unique Constraints
ALTER TABLE product_models
ADD CONSTRAINT uk_product_models_model_code UNIQUE (model_code);

-- Check Constraints
ALTER TABLE product_models
ADD CONSTRAINT chk_product_models_status
CHECK (status IN ('ACTIVE', 'INACTIVE', 'DISCONTINUED'));

ALTER TABLE product_models
ADD CONSTRAINT chk_product_models_cycle_days
CHECK (production_cycle_days IS NULL OR production_cycle_days > 0);
```

### Indexes

```sql
-- Primary key index (automatic)
-- Unique index on model_code (automatic)

-- Status filter index (for active products query)
CREATE INDEX idx_product_models_status
ON product_models(status)
WHERE status = 'ACTIVE';

-- Full-text search index on model name
CREATE INDEX idx_product_models_name_search
ON product_models USING gin(to_tsvector('simple', model_name));

-- GIN index for JSONB specifications
CREATE INDEX idx_product_models_specifications
ON product_models USING gin(specifications);

-- Category classification index
CREATE INDEX idx_product_models_category
ON product_models(category)
WHERE category IS NOT NULL;
```

### Triggers

```sql
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_product_models_updated_at
BEFORE UPDATE ON product_models
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_product_models_audit
AFTER INSERT OR UPDATE OR DELETE ON product_models
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

### Business Rules

1. **Model Code Format**:
   - Pattern: `NH-F2X-XXX` where XXX is a 3-digit number
   - Must be globally unique
   - Immutable after creation (cannot be changed)

2. **Status Transitions**:
   - ACTIVE → INACTIVE (temporary halt)
   - ACTIVE → DISCONTINUED (permanent end)
   - INACTIVE → ACTIVE (reactivation)
   - DISCONTINUED products cannot be reactivated

3. **Specifications Structure** (JSONB):
```json
{
  "dimensions": {
    "width_mm": 100,
    "height_mm": 50,
    "depth_mm": 30
  },
  "weight_grams": 250,
  "electrical": {
    "voltage_range": "3.3V-5V",
    "current_max_ma": 500
  },
  "operating_temp": {
    "min_celsius": -10,
    "max_celsius": 60
  },
  "quality_standards": ["ISO 9001", "CE"]
}
```

4. **Deletion Rules**:
   - Cannot delete if active LOTs exist (enforced by foreign key)
   - Can only delete DISCONTINUED products with no production history
   - Use soft delete (status = 'DISCONTINUED') instead

5. **Validation**:
   - model_name must be non-empty
   - production_cycle_days must be positive if specified
   - specifications must be valid JSON

---

## 2.2 lots (생산 LOT)

### Purpose
Production batch tracking table. Each LOT represents a group of up to 100 units manufactured together on a specific date/shift. LOTs are the primary unit for production planning, scheduling, and quality control.

### Business Context
- One LOT = one production run (typically 100 units)
- LOT number format: `WF-KR-YYMMDD{D|N}-nnn`
- Tracks production progress and quality metrics
- Enables batch-level traceability

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| lot_number | VARCHAR(50) | NOT NULL | AUTO | Auto-generated LOT identifier |
| product_model_id | BIGINT | NOT NULL | - | Foreign key to product_models |
| production_date | DATE | NOT NULL | - | Scheduled/actual production date |
| shift | VARCHAR(1) | NOT NULL | - | Production shift: D (day) or N (night) |
| target_quantity | INTEGER | NOT NULL | 100 | Target production quantity |
| actual_quantity | INTEGER | NOT NULL | 0 | Actual units produced |
| passed_quantity | INTEGER | NOT NULL | 0 | Units that passed all processes |
| failed_quantity | INTEGER | NOT NULL | 0 | Units that failed quality checks |
| status | VARCHAR(20) | NOT NULL | 'CREATED' | LOT lifecycle status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | LOT creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |
| closed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | LOT closure/completion timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE lots
ADD CONSTRAINT pk_lots PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE lots
ADD CONSTRAINT fk_lots_product_model
FOREIGN KEY (product_model_id)
REFERENCES product_models(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Unique Constraints
ALTER TABLE lots
ADD CONSTRAINT uk_lots_lot_number UNIQUE (lot_number);

-- Check Constraints
ALTER TABLE lots
ADD CONSTRAINT chk_lots_status
CHECK (status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED', 'CLOSED'));

ALTER TABLE lots
ADD CONSTRAINT chk_lots_shift
CHECK (shift IN ('D', 'N'));

ALTER TABLE lots
ADD CONSTRAINT chk_lots_target_quantity
CHECK (target_quantity > 0 AND target_quantity <= 100);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_actual_quantity
CHECK (actual_quantity >= 0 AND actual_quantity <= target_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_passed_quantity
CHECK (passed_quantity >= 0 AND passed_quantity <= actual_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_failed_quantity
CHECK (failed_quantity >= 0 AND failed_quantity <= actual_quantity);

ALTER TABLE lots
ADD CONSTRAINT chk_lots_quantity_sum
CHECK (passed_quantity + failed_quantity <= actual_quantity);
```

### Indexes

```sql
-- Primary key index (automatic)
-- Unique index on lot_number (automatic)

-- Foreign key index
CREATE INDEX idx_lots_product_model
ON lots(product_model_id);

-- Status-based queries
CREATE INDEX idx_lots_status
ON lots(status);

-- Active LOTs index (frequently queried)
CREATE INDEX idx_lots_active
ON lots(status, production_date)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- Date range queries
CREATE INDEX idx_lots_production_date
ON lots(production_date DESC);

-- Composite index for filtering
CREATE INDEX idx_lots_model_date_shift
ON lots(product_model_id, production_date, shift);

-- Closed LOTs index (for archival)
CREATE INDEX idx_lots_closed_at
ON lots(closed_at)
WHERE closed_at IS NOT NULL;
```

### Triggers

```sql
-- Auto-generate LOT number
CREATE TRIGGER trg_lots_generate_number
BEFORE INSERT ON lots
FOR EACH ROW
EXECUTE FUNCTION generate_lot_number();

-- Auto-update updated_at timestamp
CREATE TRIGGER trg_lots_updated_at
BEFORE UPDATE ON lots
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Validate status transitions
CREATE TRIGGER trg_lots_validate_status
BEFORE UPDATE ON lots
FOR EACH ROW
EXECUTE FUNCTION validate_lot_status_transition();

-- Auto-close LOT when completed
CREATE TRIGGER trg_lots_auto_close
AFTER UPDATE ON lots
FOR EACH ROW
WHEN (NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED')
EXECUTE FUNCTION auto_close_lot();

-- Audit logging trigger
CREATE TRIGGER trg_lots_audit
AFTER INSERT OR UPDATE OR DELETE ON lots
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

### Trigger Function: generate_lot_number()

```sql
CREATE OR REPLACE FUNCTION generate_lot_number()
RETURNS TRIGGER AS $$
DECLARE
    v_date_part VARCHAR(6);
    v_shift_part VARCHAR(1);
    v_sequence INTEGER;
    v_new_lot_number VARCHAR(50);
BEGIN
    -- Extract date part: YYMMDD
    v_date_part := TO_CHAR(NEW.production_date, 'YYMMDD');

    -- Extract shift part: D or N
    v_shift_part := NEW.shift;

    -- Get next sequence number for this date+shift
    SELECT COALESCE(MAX(
        CAST(
            SUBSTRING(lot_number FROM LENGTH(lot_number) - 2)
            AS INTEGER
        )
    ), 0) + 1
    INTO v_sequence
    FROM lots
    WHERE lot_number LIKE 'WF-KR-' || v_date_part || v_shift_part || '-%';

    -- Generate LOT number: WF-KR-251110D-001
    v_new_lot_number := 'WF-KR-' || v_date_part || v_shift_part || '-' ||
                        LPAD(v_sequence::TEXT, 3, '0');

    -- Assign to NEW record
    NEW.lot_number := v_new_lot_number;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger Function: validate_lot_status_transition()

```sql
CREATE OR REPLACE FUNCTION validate_lot_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Allow transitions:
    -- CREATED → IN_PROGRESS
    -- IN_PROGRESS → COMPLETED
    -- COMPLETED → CLOSED

    IF OLD.status = 'CREATED' AND NEW.status NOT IN ('CREATED', 'IN_PROGRESS') THEN
        RAISE EXCEPTION 'Invalid status transition: CREATED can only transition to IN_PROGRESS';
    END IF;

    IF OLD.status = 'IN_PROGRESS' AND NEW.status NOT IN ('IN_PROGRESS', 'COMPLETED') THEN
        RAISE EXCEPTION 'Invalid status transition: IN_PROGRESS can only transition to COMPLETED';
    END IF;

    IF OLD.status = 'COMPLETED' AND NEW.status NOT IN ('COMPLETED', 'CLOSED') THEN
        RAISE EXCEPTION 'Invalid status transition: COMPLETED can only transition to CLOSED';
    END IF;

    IF OLD.status = 'CLOSED' AND NEW.status != 'CLOSED' THEN
        RAISE EXCEPTION 'Invalid status transition: CLOSED is final, cannot change';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Business Rules

1. **LOT Number Format**:
   - Pattern: `WF-KR-YYMMDD{D|N}-nnn`
   - Example: `WF-KR-251110D-001` (2025-11-10, Day shift, sequence 001)
   - Auto-generated by trigger on INSERT
   - Immutable after creation

2. **Quantity Management**:
   - target_quantity: Always 100 (can be adjusted for partial LOTs)
   - actual_quantity: Increments as serials are created
   - passed_quantity + failed_quantity ≤ actual_quantity
   - Quantities updated automatically by serial status changes

3. **Status Transitions** (State Machine):
```
CREATED → IN_PROGRESS → COMPLETED → CLOSED
```
   - CREATED: LOT created, no production started
   - IN_PROGRESS: At least one serial in production
   - COMPLETED: All serials finished (passed or failed)
   - CLOSED: LOT finalized, no further changes allowed

4. **Production Rules**:
   - One LOT per product model per date per shift
   - Maximum 100 serials per LOT (hard limit)
   - LOT cannot be deleted if serials exist
   - Closed LOTs are read-only (except for audit purposes)

5. **Date/Shift Logic**:
   - production_date: YYYY-MM-DD format
   - shift: 'D' (06:00-18:00) or 'N' (18:00-06:00)
   - LOT numbers are unique per date+shift combination

---

## 2.3 serials (시리얼 번호)

### Purpose
Individual unit tracking table. Each serial represents one physical product unit within a LOT. Serials track the complete manufacturing journey through all 8 processes, including pass/fail results and rework history.

### Business Context
- One serial = one physical unit
- Serial number format: `LOT_NUMBER-XXXX` (XXXX = 0001-0100)
- Tracks unit-level quality and process completion
- Enables item-level traceability for warranty and recalls

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| serial_number | VARCHAR(50) | NOT NULL | AUTO | Auto-generated serial identifier |
| lot_id | BIGINT | NOT NULL | - | Foreign key to lots |
| sequence_in_lot | INTEGER | NOT NULL | AUTO | Sequence within LOT (1-100) |
| status | VARCHAR(20) | NOT NULL | 'CREATED' | Serial lifecycle status |
| rework_count | INTEGER | NOT NULL | 0 | Number of rework attempts |
| failure_reason | TEXT | NULL | NULL | Reason for failure (if status = FAILED) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Serial creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |
| completed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | All processes completed timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE serials
ADD CONSTRAINT pk_serials PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE serials
ADD CONSTRAINT fk_serials_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Unique Constraints
ALTER TABLE serials
ADD CONSTRAINT uk_serials_serial_number UNIQUE (serial_number);

ALTER TABLE serials
ADD CONSTRAINT uk_serials_lot_sequence UNIQUE (lot_id, sequence_in_lot);

-- Check Constraints
ALTER TABLE serials
ADD CONSTRAINT chk_serials_status
CHECK (status IN ('CREATED', 'IN_PROGRESS', 'PASSED', 'FAILED'));

ALTER TABLE serials
ADD CONSTRAINT chk_serials_sequence
CHECK (sequence_in_lot >= 1 AND sequence_in_lot <= 100);

ALTER TABLE serials
ADD CONSTRAINT chk_serials_rework_count
CHECK (rework_count >= 0 AND rework_count <= 3);

ALTER TABLE serials
ADD CONSTRAINT chk_serials_failure_reason
CHECK (
    (status = 'FAILED' AND failure_reason IS NOT NULL) OR
    (status != 'FAILED' AND failure_reason IS NULL)
);
```

### Indexes

```sql
-- Primary key index (automatic)
-- Unique index on serial_number (automatic)
-- Unique index on (lot_id, sequence_in_lot) (automatic)

-- Foreign key index
CREATE INDEX idx_serials_lot
ON serials(lot_id);

-- Status-based queries
CREATE INDEX idx_serials_status
ON serials(status);

-- Active serials index
CREATE INDEX idx_serials_active
ON serials(lot_id, status)
WHERE status IN ('CREATED', 'IN_PROGRESS');

-- Failed serials analysis
CREATE INDEX idx_serials_failed
ON serials(lot_id, failure_reason)
WHERE status = 'FAILED';

-- Rework tracking
CREATE INDEX idx_serials_rework
ON serials(rework_count)
WHERE rework_count > 0;

-- Completion time analysis
CREATE INDEX idx_serials_completed_at
ON serials(completed_at)
WHERE completed_at IS NOT NULL;
```

### Triggers

```sql
-- Auto-generate serial number
CREATE TRIGGER trg_serials_generate_number
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION generate_serial_number();

-- Auto-update updated_at timestamp
CREATE TRIGGER trg_serials_updated_at
BEFORE UPDATE ON serials
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Validate status transitions
CREATE TRIGGER trg_serials_validate_status
BEFORE UPDATE ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_serial_status_transition();

-- Update LOT quantities
CREATE TRIGGER trg_serials_update_lot_quantities
AFTER INSERT OR UPDATE ON serials
FOR EACH ROW
EXECUTE FUNCTION update_lot_quantities();

-- Validate LOT capacity (max 100 serials)
CREATE TRIGGER trg_serials_validate_lot_capacity
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_lot_capacity();

-- Audit logging trigger
CREATE TRIGGER trg_serials_audit
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

### Trigger Function: generate_serial_number()

```sql
CREATE OR REPLACE FUNCTION generate_serial_number()
RETURNS TRIGGER AS $$
DECLARE
    v_lot_number VARCHAR(50);
    v_sequence INTEGER;
    v_new_serial_number VARCHAR(50);
BEGIN
    -- Get LOT number
    SELECT lot_number INTO v_lot_number
    FROM lots
    WHERE id = NEW.lot_id;

    -- Get next sequence in LOT
    SELECT COALESCE(MAX(sequence_in_lot), 0) + 1
    INTO v_sequence
    FROM serials
    WHERE lot_id = NEW.lot_id;

    -- Assign sequence
    NEW.sequence_in_lot := v_sequence;

    -- Generate serial number: WF-KR-251110D-001-0001
    v_new_serial_number := v_lot_number || '-' || LPAD(v_sequence::TEXT, 4, '0');

    -- Assign to NEW record
    NEW.serial_number := v_new_serial_number;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger Function: validate_lot_capacity()

```sql
CREATE OR REPLACE FUNCTION validate_lot_capacity()
RETURNS TRIGGER AS $$
DECLARE
    v_current_count INTEGER;
    v_target_quantity INTEGER;
BEGIN
    -- Get current serial count and target quantity for LOT
    SELECT COUNT(*), l.target_quantity
    INTO v_current_count, v_target_quantity
    FROM serials s
    JOIN lots l ON s.lot_id = l.id
    WHERE s.lot_id = NEW.lot_id
    GROUP BY l.target_quantity;

    -- Check if adding this serial would exceed capacity
    IF v_current_count >= v_target_quantity THEN
        RAISE EXCEPTION 'LOT capacity exceeded: maximum % serials allowed', v_target_quantity;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger Function: validate_serial_status_transition()

```sql
CREATE OR REPLACE FUNCTION validate_serial_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Allow transitions:
    -- CREATED → IN_PROGRESS
    -- IN_PROGRESS → PASSED/FAILED
    -- FAILED → IN_PROGRESS (rework, max 3 times)

    IF OLD.status = 'CREATED' AND NEW.status NOT IN ('CREATED', 'IN_PROGRESS') THEN
        RAISE EXCEPTION 'Invalid status transition: CREATED can only transition to IN_PROGRESS';
    END IF;

    IF OLD.status = 'IN_PROGRESS' AND NEW.status NOT IN ('IN_PROGRESS', 'PASSED', 'FAILED') THEN
        RAISE EXCEPTION 'Invalid status transition: IN_PROGRESS can only transition to PASSED or FAILED';
    END IF;

    -- Rework logic
    IF OLD.status = 'FAILED' AND NEW.status = 'IN_PROGRESS' THEN
        -- Increment rework count
        NEW.rework_count := OLD.rework_count + 1;

        -- Check max rework attempts
        IF NEW.rework_count > 3 THEN
            RAISE EXCEPTION 'Maximum rework attempts (3) exceeded';
        END IF;

        -- Clear failure reason for rework
        NEW.failure_reason := NULL;
    END IF;

    IF OLD.status = 'PASSED' AND NEW.status != 'PASSED' THEN
        RAISE EXCEPTION 'Invalid status transition: PASSED is final, cannot change';
    END IF;

    -- Auto-set completed_at timestamp
    IF NEW.status IN ('PASSED', 'FAILED') AND OLD.status != NEW.status THEN
        NEW.completed_at := NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Business Rules

1. **Serial Number Format**:
   - Pattern: `LOT_NUMBER-XXXX`
   - Example: `WF-KR-251110D-001-0001`
   - Auto-generated by trigger on INSERT
   - Immutable after creation

2. **Sequence Management**:
   - sequence_in_lot: 1-100 (auto-assigned)
   - Unique within each LOT
   - Cannot have gaps (sequential)

3. **Status Transitions** (State Machine):
```
CREATED → IN_PROGRESS → PASSED
                      ↓
                    FAILED → IN_PROGRESS (rework, max 3x)
```
   - CREATED: Serial registered, no processing started
   - IN_PROGRESS: At least one process started
   - PASSED: All 8 processes completed successfully
   - FAILED: Failed quality check (can rework up to 3 times)

4. **Rework Rules**:
   - Maximum 3 rework attempts (rework_count ≤ 3)
   - FAILED → IN_PROGRESS transition increments rework_count
   - Manager approval required for rework (application-level logic)
   - Rework clears failure_reason

5. **Failure Tracking**:
   - failure_reason required when status = FAILED
   - failure_reason must be cleared when reworking
   - Failed serials counted in LOT failed_quantity

6. **Completion Logic**:
   - completed_at set automatically when status → PASSED or FAILED
   - Serial is "complete" when all 8 process_data records exist with PASS result
   - Incomplete serials prevent LOT from reaching COMPLETED status

---

## 2.4 processes (제조 공정)

### Purpose
Master data table defining the 8 manufacturing processes in the F2X NeuroHub production line. Each process has quality criteria, timing estimates, and sequencing information. This table serves as the template for actual process executions.

### Business Context
- 8 fixed processes: 레이저 마킹, LMA 조립, 센서검사, 펌웨어 업로드, 로봇 조립, 성능검사, 라벨 프린팅, 포장 + 외관검사
- Process sequence is strictly enforced (1→2→3→4→5→6→7→8)
- Quality criteria stored as JSONB for flexibility
- Processes are relatively static (master data)

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| process_number | INTEGER | NOT NULL | - | Process sequence number (1-8) |
| process_code | VARCHAR(50) | NOT NULL | - | Unique process code (e.g., LASER_MARKING) |
| process_name_ko | VARCHAR(255) | NOT NULL | - | Process name in Korean |
| process_name_en | VARCHAR(255) | NOT NULL | - | Process name in English |
| description | TEXT | NULL | NULL | Process description and details |
| estimated_duration_seconds | INTEGER | NULL | NULL | Expected duration in seconds |
| quality_criteria | JSONB | NULL | '{}' | Quality standards and acceptance criteria |
| is_active | BOOLEAN | NOT NULL | TRUE | Whether process is currently in use |
| sort_order | INTEGER | NOT NULL | - | Display order (usually same as process_number) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Record creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE processes
ADD CONSTRAINT pk_processes PRIMARY KEY (id);

-- Unique Constraints
ALTER TABLE processes
ADD CONSTRAINT uk_processes_process_number UNIQUE (process_number);

ALTER TABLE processes
ADD CONSTRAINT uk_processes_process_code UNIQUE (process_code);

-- Check Constraints
ALTER TABLE processes
ADD CONSTRAINT chk_processes_process_number
CHECK (process_number >= 1 AND process_number <= 8);

ALTER TABLE processes
ADD CONSTRAINT chk_processes_duration
CHECK (estimated_duration_seconds IS NULL OR estimated_duration_seconds > 0);

ALTER TABLE processes
ADD CONSTRAINT chk_processes_sort_order
CHECK (sort_order > 0);
```

### Indexes

```sql
-- Primary key index (automatic)
-- Unique index on process_number (automatic)
-- Unique index on process_code (automatic)

-- Active processes index
CREATE INDEX idx_processes_active
ON processes(is_active, sort_order)
WHERE is_active = TRUE;

-- GIN index for JSONB quality_criteria
CREATE INDEX idx_processes_quality_criteria
ON processes USING gin(quality_criteria);

-- Sort order for UI display
CREATE INDEX idx_processes_sort_order
ON processes(sort_order);
```

### Triggers

```sql
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_processes_updated_at
BEFORE UPDATE ON processes
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_processes_audit
AFTER INSERT OR UPDATE OR DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- Prevent deletion if process data exists
CREATE TRIGGER trg_processes_prevent_delete
BEFORE DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION prevent_process_deletion();
```

### Business Rules

1. **Process Definitions** (8 Total):

| Number | Code | Korean Name | English Name |
|--------|------|-------------|--------------|
| 1 | LASER_MARKING | 레이저 마킹 | Laser Marking |
| 2 | LMA_ASSEMBLY | LMA 조립 | LMA Assembly |
| 3 | SENSOR_INSPECTION | 센서 검사 | Sensor Inspection |
| 4 | FIRMWARE_UPLOAD | 펌웨어 업로드 | Firmware Upload |
| 5 | ROBOT_ASSEMBLY | 로봇 조립 | Robot Assembly |
| 6 | PERFORMANCE_TEST | 성능검사 | Performance Test |
| 7 | LABEL_PRINTING | 라벨 프린팅 | Label Printing |
| 8 | PACKAGING_INSPECTION | 포장 + 외관검사 | Packaging & Visual Inspection |

2. **Process Sequence**:
   - Must be executed in order: 1→2→3→4→5→6→7→8
   - Cannot skip processes
   - Enforced by trigger in process_data table
   - Rework can restart from any process (with approval)

3. **Quality Criteria Structure** (JSONB):

**Example for LMA_ASSEMBLY**:
```json
{
  "components_required": ["LMA_module", "connector", "screws"],
  "torque_spec": {
    "min": 0.8,
    "max": 1.2,
    "unit": "Nm"
  },
  "alignment_tolerance_mm": 0.1,
  "visual_check": true,
  "assembly_duration_seconds": 180,
  "acceptance_criteria": "All components properly assembled and aligned"
}
```

**Example for SENSOR_INSPECTION**:
```json
{
  "sensor_channels": 8,
  "signal_quality_threshold": 0.85,
  "noise_level_max_db": -40,
  "calibration_required": true,
  "test_patterns": ["baseline", "stimulus", "recovery"]
}
```

**Example for ROBOT_ASSEMBLY**:
```json
{
  "robot_components": ["motor", "encoder", "gear_assembly"],
  "motor_test": {
    "rotation_speed_rpm": 1000,
    "current_draw_ma": 500,
    "torque_nm": 2.5
  },
  "encoder_resolution": 4096,
  "functional_test_required": true,
  "assembly_duration_seconds": 300,
  "acceptance_criteria": "Full mechanical and electrical functionality verified"
}
```

4. **Duration Estimates**:
   - estimated_duration_seconds: Used for production planning
   - Actual duration tracked in process_data
   - Variance analysis for process optimization

5. **Process Management**:
   - Processes cannot be deleted (only deactivated via is_active = FALSE)
   - Inactive processes not shown in production UI
   - Process definitions are version-controlled via audit logs
   - Changes to quality_criteria require manager approval

6. **Master Data Loading**:
```sql
-- Initial data load (executed once during database setup)
INSERT INTO processes (process_number, process_code, process_name_ko, process_name_en, estimated_duration_seconds, quality_criteria, sort_order) VALUES
(1, 'LASER_MARKING', '레이저 마킹', 'Laser Marking', 60, '{"power": "20W", "speed": "100mm/s", "depth": "0.1mm"}', 1),
(2, 'LMA_ASSEMBLY', 'LMA 조립', 'LMA Assembly', 180, '{"components_required": ["LMA_module", "connector", "screws"], "torque_spec": {"min": 0.8, "max": 1.2, "unit": "Nm"}}', 2),
(3, 'SENSOR_INSPECTION', '센서 검사', 'Sensor Inspection', 120, '{"sensor_channels": 8, "signal_quality_threshold": 0.85, "noise_level_max_db": -40}', 3),
(4, 'FIRMWARE_UPLOAD', '펌웨어 업로드', 'Firmware Upload', 300, '{"firmware_version": "2.1.0", "checksum_validation": true}', 4),
(5, 'ROBOT_ASSEMBLY', '로봇 조립', 'Robot Assembly', 300, '{"robot_components": ["motor", "encoder", "gear_assembly"], "functional_test_required": true}', 5),
(6, 'PERFORMANCE_TEST', '성능검사', 'Performance Test', 180, '{"response_time_ms": 50, "accuracy_percent": 95}', 6),
(7, 'LABEL_PRINTING', '라벨 프린팅', 'Label Printing', 30, '{"label_type": "barcode", "resolution": "300dpi", "verification_required": true}', 7),
(8, 'PACKAGING_INSPECTION', '포장 + 외관검사', 'Packaging & Visual Inspection', 90, '{"anti_static_bag": true, "visual_defect_check": true, "label_verification": true}', 8);
```

---

## 2.5 process_data (공정 실행 데이터)

### Purpose
Process execution records table. Captures actual measurements, test results, operator information, and timing for each process execution. This is the core transactional table linking serials/LOTs to processes with detailed JSONB data.

### Business Context
- One record per process execution (per serial or per LOT)
- JSONB measurements allow process-specific data structures
- Tracks pass/fail results and defect information
- Enables process performance analysis and quality control
- Largest table (high volume, time-series data)

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| lot_id | BIGINT | NOT NULL | - | Foreign key to lots |
| serial_id | BIGINT | NULL | NULL | Foreign key to serials (NULL for LOT-level data) |
| process_id | BIGINT | NOT NULL | - | Foreign key to processes |
| operator_id | BIGINT | NOT NULL | - | Foreign key to users (who performed the process) |
| data_level | VARCHAR(10) | NOT NULL | - | Data granularity: LOT or SERIAL |
| result | VARCHAR(10) | NOT NULL | - | Process result: PASS, FAIL, REWORK |
| measurements | JSONB | NULL | '{}' | Process-specific measurement data |
| defects | JSONB | NULL | '[]' | Defect information (if result = FAIL) |
| notes | TEXT | NULL | NULL | Additional comments or observations |
| started_at | TIMESTAMP WITH TIME ZONE | NOT NULL | - | Process start timestamp |
| completed_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | Process completion timestamp |
| duration_seconds | INTEGER | NULL | NULL | Actual process duration (auto-calculated) |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Record creation timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE process_data
ADD CONSTRAINT pk_process_data PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_serial
FOREIGN KEY (serial_id)
REFERENCES serials(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_operator
FOREIGN KEY (operator_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Check Constraints
ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_data_level
CHECK (data_level IN ('LOT', 'SERIAL'));

ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_result
CHECK (result IN ('PASS', 'FAIL', 'REWORK'));

ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_serial_id
CHECK (
    (data_level = 'LOT' AND serial_id IS NULL) OR
    (data_level = 'SERIAL' AND serial_id IS NOT NULL)
);

ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_duration
CHECK (duration_seconds IS NULL OR duration_seconds >= 0);

ALTER TABLE process_data
ADD CONSTRAINT chk_process_data_timestamps
CHECK (completed_at IS NULL OR completed_at >= started_at);

-- Unique Constraints (prevent duplicate process records)
CREATE UNIQUE INDEX uk_process_data_serial_process
ON process_data(serial_id, process_id)
WHERE serial_id IS NOT NULL AND result = 'PASS';

CREATE UNIQUE INDEX uk_process_data_lot_process
ON process_data(lot_id, process_id)
WHERE serial_id IS NULL AND data_level = 'LOT' AND result = 'PASS';
```

### Indexes

```sql
-- Primary key index (automatic)

-- Foreign key indexes
CREATE INDEX idx_process_data_lot
ON process_data(lot_id);

CREATE INDEX idx_process_data_serial
ON process_data(serial_id);

CREATE INDEX idx_process_data_process
ON process_data(process_id);

CREATE INDEX idx_process_data_operator
ON process_data(operator_id);

-- Composite indexes for common queries
CREATE INDEX idx_process_data_serial_process
ON process_data(serial_id, process_id, result);

CREATE INDEX idx_process_data_lot_process
ON process_data(lot_id, process_id, result);

-- Time-based queries (for analytics)
CREATE INDEX idx_process_data_started_at
ON process_data(started_at DESC);

CREATE INDEX idx_process_data_completed_at
ON process_data(completed_at DESC)
WHERE completed_at IS NOT NULL;

-- Result-based queries
CREATE INDEX idx_process_data_result
ON process_data(result, process_id);

-- Failed processes analysis
CREATE INDEX idx_process_data_failed
ON process_data(process_id, started_at)
WHERE result = 'FAIL';

-- GIN indexes for JSONB columns
CREATE INDEX idx_process_data_measurements
ON process_data USING gin(measurements);

CREATE INDEX idx_process_data_defects
ON process_data USING gin(defects);

-- Data level filtering
CREATE INDEX idx_process_data_data_level
ON process_data(data_level, lot_id);

-- Operator performance analysis
CREATE INDEX idx_process_data_operator_performance
ON process_data(operator_id, process_id, result, started_at);

-- Partitioning index (for large datasets)
-- Can partition by started_at (monthly or quarterly)
```

### Partitioning Strategy (for high volume)

```sql
-- Optional: Partition by month for scalability
CREATE TABLE process_data_y2025m11 PARTITION OF process_data
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE process_data_y2025m12 PARTITION OF process_data
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Add partitions as needed
```

### Triggers

```sql
-- Auto-calculate duration
CREATE TRIGGER trg_process_data_calculate_duration
BEFORE INSERT OR UPDATE ON process_data
FOR EACH ROW
EXECUTE FUNCTION calculate_process_duration();

-- Validate process sequence
CREATE TRIGGER trg_process_data_validate_sequence
BEFORE INSERT ON process_data
FOR EACH ROW
EXECUTE FUNCTION validate_process_sequence();

-- Update serial status based on process results
CREATE TRIGGER trg_process_data_update_serial_status
AFTER INSERT OR UPDATE ON process_data
FOR EACH ROW
EXECUTE FUNCTION update_serial_status_from_process();

-- Audit logging trigger
CREATE TRIGGER trg_process_data_audit
AFTER INSERT OR UPDATE OR DELETE ON process_data
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();
```

### Trigger Function: calculate_process_duration()

```sql
CREATE OR REPLACE FUNCTION calculate_process_duration()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate duration if completed_at is set
    IF NEW.completed_at IS NOT NULL THEN
        NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Trigger Function: validate_process_sequence()

```sql
CREATE OR REPLACE FUNCTION validate_process_sequence()
RETURNS TRIGGER AS $$
DECLARE
    v_current_process_number INTEGER;
    v_max_completed_process_number INTEGER;
BEGIN
    -- Only validate for SERIAL-level data
    IF NEW.data_level != 'SERIAL' OR NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Get current process number
    SELECT process_number INTO v_current_process_number
    FROM processes
    WHERE id = NEW.process_id;

    -- Get max completed process number for this serial
    SELECT COALESCE(MAX(p.process_number), 0)
    INTO v_max_completed_process_number
    FROM process_data pd
    JOIN processes p ON pd.process_id = p.id
    WHERE pd.serial_id = NEW.serial_id
      AND pd.result = 'PASS';

    -- Validate sequence (can only do next process or redo failed process)
    IF v_current_process_number > v_max_completed_process_number + 1 THEN
        RAISE EXCEPTION 'Process sequence violation: cannot execute process % before completing process %',
            v_current_process_number, v_max_completed_process_number + 1;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Business Rules

1. **Data Level Logic**:
   - **LOT-level**: Process performed once per LOT (e.g., final packaging)
     - serial_id = NULL
     - data_level = 'LOT'
   - **SERIAL-level**: Process performed per unit (most processes)
     - serial_id = NOT NULL
     - data_level = 'SERIAL'

2. **Process Results**:
   - **PASS**: Process completed successfully
   - **FAIL**: Process failed quality check, requires rework
   - **REWORK**: Process being retried after previous failure

3. **Measurements Structure** (JSONB - Process-Specific):

**LASER_MARKING**:
```json
{
  "marking_quality": "GOOD",
  "readability_score": 0.98,
  "position_offset_mm": 0.05,
  "laser_power_actual": "19.8W",
  "marking_time_seconds": 58
}
```

**LMA_ASSEMBLY**:
```json
{
  "components_installed": ["LMA_module", "connector", "screws"],
  "torque_applied_nm": 1.0,
  "alignment_offset_mm": 0.05,
  "visual_inspection": "PASS",
  "assembly_time_seconds": 175,
  "quality_check": "PASS"
}
```

**SENSOR_INSPECTION**:
```json
{
  "sensor_channels_tested": 8,
  "signal_quality_avg": 0.92,
  "noise_level_db": -45,
  "calibration_offset": [0.01, -0.02, 0.00, 0.01, -0.01, 0.02, 0.00, -0.01],
  "baseline_values": [512, 510, 515, 508, 512, 514, 511, 509]
}
```

**PERFORMANCE_TEST**:
```json
{
  "response_time_ms": 42,
  "accuracy_percent": 96.5,
  "throughput_samples_per_sec": 1000,
  "test_scenarios": [
    {"scenario": "idle", "result": "PASS"},
    {"scenario": "load", "result": "PASS"},
    {"scenario": "stress", "result": "PASS"}
  ]
}
```

**FIRMWARE_UPLOAD**:
```json
{
  "firmware_version": "2.1.0",
  "checksum": "a3f5b2c9d1e8f7a4",
  "upload_duration_seconds": 285,
  "verification_passed": true,
  "device_id": "NH-F2X-001-12345"
}
```

**ROBOT_ASSEMBLY**:
```json
{
  "robot_components_installed": ["motor", "encoder", "gear_assembly"],
  "motor_rotation_speed_rpm": 1005,
  "motor_current_draw_ma": 495,
  "encoder_resolution_verified": 4096,
  "torque_output_nm": 2.48,
  "functional_test_result": "PASS",
  "assembly_time_seconds": 295
}
```

4. **Defects Structure** (JSONB - Array of Defects):
```json
[
  {
    "defect_code": "E001",
    "defect_name": "Voltage out of range",
    "severity": "CRITICAL",
    "measured_value": 3.55,
    "expected_range": "3.2-3.4",
    "action_required": "REWORK"
  },
  {
    "defect_code": "E002",
    "defect_name": "High noise level",
    "severity": "MINOR",
    "measured_value": -38,
    "expected_value": "<-40",
    "action_required": "MONITOR"
  }
]
```

5. **Process Sequence Enforcement**:
   - Processes must be completed in order 1→8
   - Cannot skip processes (trigger validates)
   - Can redo failed processes (rework)
   - Each serial should have exactly 8 PASS records when complete

6. **Timing and Duration**:
   - started_at: Required, when operator begins process
   - completed_at: Set when operator finishes process
   - duration_seconds: Auto-calculated (completed_at - started_at)
   - Used for cycle time analysis and bottleneck identification

7. **Data Retention**:
   - Keep all process_data for 3 years (compliance)
   - Archive old data to separate partition or table
   - Aggregate historical data for analytics

---

## 2.6 users (사용자)

### Purpose
User authentication and authorization table. Stores user credentials, roles, and profile information for system access control. Supports role-based access control (RBAC) with three roles: ADMIN, MANAGER, WORKER.

### Business Context
- Users are operators, managers, and administrators
- Role-based permissions control system access
- Tracks user activity for audit and performance analysis
- Password security via bcrypt hashing

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| username | VARCHAR(50) | NOT NULL | - | Unique login username |
| email | VARCHAR(255) | NOT NULL | - | Unique email address |
| password_hash | VARCHAR(255) | NOT NULL | - | Bcrypt hashed password |
| full_name | VARCHAR(255) | NOT NULL | - | User's full name (Korean or English) |
| role | VARCHAR(20) | NOT NULL | - | User role: ADMIN, MANAGER, WORKER |
| department | VARCHAR(100) | NULL | NULL | Department or team |
| is_active | BOOLEAN | NOT NULL | TRUE | Account active status |
| last_login_at | TIMESTAMP WITH TIME ZONE | NULL | NULL | Last successful login timestamp |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Account creation timestamp |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE users
ADD CONSTRAINT pk_users PRIMARY KEY (id);

-- Unique Constraints
ALTER TABLE users
ADD CONSTRAINT uk_users_username UNIQUE (username);

ALTER TABLE users
ADD CONSTRAINT uk_users_email UNIQUE (email);

-- Check Constraints
ALTER TABLE users
ADD CONSTRAINT chk_users_role
CHECK (role IN ('ADMIN', 'MANAGER', 'WORKER'));

ALTER TABLE users
ADD CONSTRAINT chk_users_email_format
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users
ADD CONSTRAINT chk_users_username_length
CHECK (LENGTH(username) >= 3);
```

### Indexes

```sql
-- Primary key index (automatic)
-- Unique index on username (automatic)
-- Unique index on email (automatic)

-- Active users lookup
CREATE INDEX idx_users_active
ON users(is_active, role)
WHERE is_active = TRUE;

-- Role-based queries
CREATE INDEX idx_users_role
ON users(role);

-- Department filtering
CREATE INDEX idx_users_department
ON users(department)
WHERE department IS NOT NULL;

-- Last login analysis
CREATE INDEX idx_users_last_login
ON users(last_login_at DESC)
WHERE last_login_at IS NOT NULL;
```

### Triggers

```sql
-- Auto-update updated_at timestamp
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Audit logging trigger
CREATE TRIGGER trg_users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION log_audit_event();

-- Prevent deletion if user has process data
CREATE TRIGGER trg_users_prevent_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION prevent_user_deletion();
```

### Business Rules

1. **User Roles and Permissions**:

| Role | Permissions | Description |
|------|-------------|-------------|
| ADMIN | Full system access | Create users, modify master data, access all features |
| MANAGER | Approve rework, view reports, manage LOTs | Production management and oversight |
| WORKER | Execute processes, record data | Operators performing manufacturing processes |

2. **Password Security**:
   - Passwords hashed using bcrypt (cost factor 12)
   - Minimum length: 8 characters (enforced at application level)
   - Password complexity requirements (at application level)
   - Password reset functionality via email

3. **Account Management**:
   - is_active = FALSE for disabled accounts (soft delete)
   - Inactive users cannot log in but data is retained
   - Username and email cannot be changed (data integrity)
   - last_login_at updated on successful authentication

4. **User Lifecycle**:
   - Created by ADMIN users only
   - Initial password set by ADMIN, must be changed on first login
   - Inactive users after 90 days of no login (configurable)
   - Cannot delete users with associated process_data (referential integrity)

5. **Audit Requirements**:
   - All user actions logged to audit_logs
   - User creation/modification requires approval
   - Role changes tracked in audit logs

6. **Initial Admin User**:
```sql
-- Create default admin account (execute once during setup)
INSERT INTO users (username, email, password_hash, full_name, role, department)
VALUES (
    'admin',
    'admin@neurohub.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oPk9LI6Fg9j2', -- bcrypt hash of 'admin123'
    'System Administrator',
    'ADMIN',
    'IT'
);
```

---

## 2.7 audit_logs (감사 로그)

### Purpose
Comprehensive audit trail table capturing all system changes for compliance, security, and traceability. Records CREATE/UPDATE/DELETE operations on all critical entities with before/after snapshots.

### Business Context
- Regulatory compliance (track all changes for 3 years)
- Security monitoring and forensics
- Change history for troubleshooting
- User accountability
- Immutable records (append-only, no updates/deletes)

### Schema

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | BIGSERIAL | NOT NULL | AUTO | Primary key, auto-incrementing |
| user_id | BIGINT | NOT NULL | - | Foreign key to users (who made the change) |
| entity_type | VARCHAR(50) | NOT NULL | - | Table name (e.g., 'lots', 'serials') |
| entity_id | BIGINT | NOT NULL | - | Primary key of affected record |
| action | VARCHAR(10) | NOT NULL | - | Operation type: CREATE, UPDATE, DELETE |
| old_values | JSONB | NULL | NULL | Record state before change (NULL for CREATE) |
| new_values | JSONB | NULL | NULL | Record state after change (NULL for DELETE) |
| ip_address | VARCHAR(45) | NULL | NULL | Client IP address (IPv4 or IPv6) |
| user_agent | TEXT | NULL | NULL | Client user agent string |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Audit log entry timestamp |

### Constraints

```sql
-- Primary Key
ALTER TABLE audit_logs
ADD CONSTRAINT pk_audit_logs PRIMARY KEY (id);

-- Foreign Keys
ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_user
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Check Constraints
ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_action
CHECK (action IN ('CREATE', 'UPDATE', 'DELETE'));

ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_entity_type
CHECK (entity_type IN ('product_models', 'lots', 'serials', 'processes', 'process_data', 'users', 'audit_logs'));

ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_old_values
CHECK (
    (action = 'CREATE' AND old_values IS NULL) OR
    (action IN ('UPDATE', 'DELETE') AND old_values IS NOT NULL)
);

ALTER TABLE audit_logs
ADD CONSTRAINT chk_audit_logs_new_values
CHECK (
    (action = 'DELETE' AND new_values IS NULL) OR
    (action IN ('CREATE', 'UPDATE') AND new_values IS NOT NULL)
);
```

### Indexes

```sql
-- Primary key index (automatic)

-- Foreign key index
CREATE INDEX idx_audit_logs_user
ON audit_logs(user_id);

-- Entity tracking
CREATE INDEX idx_audit_logs_entity
ON audit_logs(entity_type, entity_id);

-- Action type filtering
CREATE INDEX idx_audit_logs_action
ON audit_logs(action, created_at DESC);

-- Time-based queries (most common)
CREATE INDEX idx_audit_logs_created_at
ON audit_logs(created_at DESC);

-- User activity analysis
CREATE INDEX idx_audit_logs_user_activity
ON audit_logs(user_id, created_at DESC);

-- Composite index for entity history
CREATE INDEX idx_audit_logs_entity_history
ON audit_logs(entity_type, entity_id, created_at DESC);

-- GIN indexes for JSONB search
CREATE INDEX idx_audit_logs_old_values
ON audit_logs USING gin(old_values);

CREATE INDEX idx_audit_logs_new_values
ON audit_logs USING gin(new_values);

-- IP-based security analysis
CREATE INDEX idx_audit_logs_ip_address
ON audit_logs(ip_address, created_at DESC)
WHERE ip_address IS NOT NULL;
```

### Partitioning Strategy

```sql
-- Partition by month for efficient archival and query performance
CREATE TABLE audit_logs (
    -- ... columns as above ...
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE audit_logs_y2025m11 PARTITION OF audit_logs
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE audit_logs_y2025m12 PARTITION OF audit_logs
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Automate partition creation (via cron job or extension)
```

### Triggers

```sql
-- Prevent UPDATE and DELETE on audit_logs (immutable)
CREATE TRIGGER trg_audit_logs_immutable
BEFORE UPDATE OR DELETE ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION prevent_audit_modification();
```

### Trigger Function: prevent_audit_modification()

```sql
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;
```

### Business Rules

1. **Audit Scope**:
   - All changes to critical tables: product_models, lots, serials, process_data, users
   - System-level changes (configuration, master data)
   - Authentication and authorization events (application-level)

2. **Data Capture**:
   - **old_values**: Complete record snapshot before change (JSONB)
   - **new_values**: Complete record snapshot after change (JSONB)
   - Only changed fields can be extracted via JSONB queries

3. **JSONB Structure Examples**:

**CREATE action** (new_values only):
```json
{
  "lot_number": "WF-KR-251110D-001",
  "product_model_id": 1,
  "production_date": "2025-11-10",
  "shift": "D",
  "target_quantity": 100,
  "status": "CREATED"
}
```

**UPDATE action** (old_values + new_values):
```json
// old_values
{
  "status": "IN_PROGRESS",
  "actual_quantity": 50,
  "updated_at": "2025-11-10T10:30:00Z"
}

// new_values
{
  "status": "COMPLETED",
  "actual_quantity": 100,
  "passed_quantity": 98,
  "failed_quantity": 2,
  "updated_at": "2025-11-10T18:45:00Z"
}
```

**DELETE action** (old_values only):
```json
{
  "username": "temp_worker",
  "email": "temp@neurohub.com",
  "role": "WORKER",
  "is_active": false,
  "created_at": "2025-10-01T09:00:00Z"
}
```

4. **Retention Policy**:
   - Keep all audit logs for minimum 3 years (compliance requirement)
   - Archive logs older than 1 year to cold storage
   - Partitioning enables efficient archival and deletion

5. **Security and Privacy**:
   - Do not log sensitive data (passwords, even hashed)
   - Mask PII in logs if required
   - Restrict audit log access to ADMIN role only
   - IP address and user_agent for security forensics

6. **Query Examples**:

```sql
-- Get change history for a specific LOT
SELECT *
FROM audit_logs
WHERE entity_type = 'lots'
  AND entity_id = 123
ORDER BY created_at DESC;

-- Find who changed a serial's status to FAILED
SELECT u.username, al.created_at, al.old_values, al.new_values
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'serials'
  AND al.entity_id = 456
  AND al.action = 'UPDATE'
  AND al.new_values->>'status' = 'FAILED';

-- Audit user activity for a specific date
SELECT
    u.username,
    al.action,
    al.entity_type,
    COUNT(*) as change_count
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE DATE(al.created_at) = '2025-11-10'
GROUP BY u.username, al.action, al.entity_type
ORDER BY change_count DESC;

-- Detect suspicious activity (many changes from single IP)
SELECT
    ip_address,
    COUNT(*) as change_count,
    COUNT(DISTINCT user_id) as user_count,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen
FROM audit_logs
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
HAVING COUNT(*) > 100
ORDER BY change_count DESC;
```

7. **Immutability**:
   - Audit logs cannot be updated or deleted (enforced by trigger)
   - Only INSERT operations allowed
   - Ensures trustworthy audit trail

---

## Common Trigger Functions

### update_timestamp()

```sql
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### log_audit_event()

```sql
CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id BIGINT;
    v_action VARCHAR(10);
    v_old_values JSONB;
    v_new_values JSONB;
BEGIN
    -- Get current user ID from session (set by application)
    v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::BIGINT;

    -- Determine action
    IF TG_OP = 'INSERT' THEN
        v_action := 'CREATE';
        v_old_values := NULL;
        v_new_values := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'UPDATE' THEN
        v_action := 'UPDATE';
        v_old_values := row_to_json(OLD)::JSONB;
        v_new_values := row_to_json(NEW)::JSONB;
    ELSIF TG_OP = 'DELETE' THEN
        v_action := 'DELETE';
        v_old_values := row_to_json(OLD)::JSONB;
        v_new_values := NULL;
    END IF;

    -- Insert audit log
    INSERT INTO audit_logs (
        user_id,
        entity_type,
        entity_id,
        action,
        old_values,
        new_values,
        ip_address,
        user_agent
    ) VALUES (
        COALESCE(v_user_id, 1), -- Default to system user if not set
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        v_action,
        v_old_values,
        v_new_values,
        current_setting('app.client_ip', true),
        current_setting('app.user_agent', true)
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## Summary

This document defines all 7 core entities for the F2X NeuroHub MES database with:

- Complete schemas (columns, types, constraints)
- Performance indexes (B-Tree, GIN, composite, partial)
- Business logic triggers (validation, automation, audit)
- Detailed business rules and validation logic
- JSONB data structures for flexible process data
- Scalability considerations (partitioning, archival)

**Next Steps**:
1. Review relationship specifications in **03-relationship-specifications.md**
2. Execute DDL scripts to create database schema
3. Load master data (processes, initial admin user)
4. Implement application-level validation and business logic
5. Configure monitoring and alerting for production

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: Database Architecture Team
**Status**: Ready for Implementation
