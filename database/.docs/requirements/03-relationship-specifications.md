# Relationship Specifications
# F2X NeuroHub MES Database

## Overview

This document provides comprehensive specifications for all database relationships in the F2X NeuroHub MES system. Each relationship is defined with foreign key constraints, referential integrity rules, cascading behaviors, and business logic enforcement.

**Total Relationships**: 10 primary relationships
**Design Principle**: Strict referential integrity with RESTRICT delete policy
**Database Engine**: PostgreSQL 14+

---

## Table of Contents

1. [product_models → lots](#31-product_models--lots)
2. [lots → serials](#32-lots--serials)
3. [lots → process_data](#33-lots--process_data)
4. [serials → process_data](#34-serials--process_data)
5. [processes → process_data](#35-processes--process_data)
6. [users → process_data](#36-users--process_data)
7. [users → audit_logs](#37-users--audit_logs)
8. [equipment → process_data](#38-equipment--process_data)
9. [lots → wip_items](#39-lots--wip_items)
10. [wip_items → wip_process_history](#310-wip_items--wip_process_history)

---

## 3.1 product_models → lots

### Relationship Type
**One-to-Many (1:N)**

A single product model can have multiple production LOTs manufactured over time. Each LOT must be associated with exactly one product model.

### Cardinality
```
product_models (1) ────────< (N) lots
```

### Foreign Key Definition

```sql
ALTER TABLE lots
ADD CONSTRAINT fk_lots_product_model
FOREIGN KEY (product_model_id)
REFERENCES product_models(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| product_models.id | lots.product_model_id | BIGINT | Product model identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a product_model if any LOTs reference it
- **Rationale**: Preserve production history and traceability
- **Error Message**: "Cannot delete product_model: active LOTs exist"

```sql
-- Example: This will FAIL if LOTs exist for this product model
DELETE FROM product_models WHERE id = 1;
-- ERROR: update or delete on table "product_models" violates foreign key constraint
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates lots.product_model_id if product_models.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated
- **Note**: Primary keys should rarely change in practice

### Business Logic

1. **LOT Creation Requirements**:
   - product_model_id must reference an ACTIVE product model
   - Product model status checked at application level before LOT creation
   - Specifications inherited from product model at LOT creation time

2. **Product Model Lifecycle**:
   - ACTIVE product models can have new LOTs created
   - INACTIVE product models cannot have new LOTs (application-enforced)
   - DISCONTINUED product models cannot be deleted if historical LOTs exist

3. **Data Consistency**:
   - LOT production specifications should match product_model.specifications
   - Any deviations from standard specs logged in audit_logs
   - Product model changes do not affect existing LOTs (snapshot at creation)

### Example Queries

```sql
-- Get all LOTs for a specific product model
SELECT
    l.lot_number,
    l.production_date,
    l.shift,
    l.status,
    l.actual_quantity,
    l.passed_quantity,
    l.failed_quantity
FROM lots l
WHERE l.product_model_id = 1
ORDER BY l.production_date DESC, l.lot_number DESC;

-- Get product model with LOT statistics
SELECT
    pm.model_code,
    pm.model_name,
    COUNT(l.id) as total_lots,
    SUM(l.actual_quantity) as total_units_produced,
    SUM(l.passed_quantity) as total_passed,
    SUM(l.failed_quantity) as total_failed,
    ROUND(100.0 * SUM(l.passed_quantity) / NULLIF(SUM(l.actual_quantity), 0), 2) as yield_percent
FROM product_models pm
LEFT JOIN lots l ON pm.id = l.product_model_id
WHERE pm.id = 1
GROUP BY pm.id, pm.model_code, pm.model_name;

-- Check if product model can be deleted (no active LOTs)
SELECT
    pm.model_code,
    COUNT(l.id) as lot_count,
    CASE
        WHEN COUNT(l.id) = 0 THEN 'Can delete'
        ELSE 'Cannot delete - LOTs exist'
    END as deletion_status
FROM product_models pm
LEFT JOIN lots l ON pm.id = l.product_model_id
WHERE pm.id = 1
GROUP BY pm.id, pm.model_code;
```

### Validation Trigger

```sql
-- Optional: Validate product model is ACTIVE before LOT creation
CREATE OR REPLACE FUNCTION validate_product_model_for_lot()
RETURNS TRIGGER AS $$
DECLARE
    v_product_status VARCHAR(20);
BEGIN
    SELECT status INTO v_product_status
    FROM product_models
    WHERE id = NEW.product_model_id;

    IF v_product_status != 'ACTIVE' THEN
        RAISE EXCEPTION 'Cannot create LOT: product model % is not ACTIVE (status: %)',
            NEW.product_model_id, v_product_status;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_lots_validate_product_model
BEFORE INSERT ON lots
FOR EACH ROW
EXECUTE FUNCTION validate_product_model_for_lot();
```

### Data Integrity Checklist

- [ ] product_model_id must exist in product_models table
- [ ] Product model must be ACTIVE for new LOT creation
- [ ] LOT inherits specifications from product model at creation time
- [ ] Product model cannot be deleted if LOTs exist
- [ ] Changes to product model do not affect existing LOTs

---

## 3.2 lots → serials

### Relationship Type
**One-to-Many (1:N) with Bounded Cardinality**

A single LOT contains up to 100 individual serial numbers. Each serial must belong to exactly one LOT.

### Cardinality
```
lots (1) ────────< (N, max 100) serials
```

### Foreign Key Definition

```sql
ALTER TABLE serials
ADD CONSTRAINT fk_serials_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| lots.id | serials.lot_id | BIGINT | LOT identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a LOT if any serials reference it
- **Rationale**: Preserve complete production traceability
- **Error Message**: "Cannot delete LOT: serials exist"

```sql
-- Example: This will FAIL if serials exist for this LOT
DELETE FROM lots WHERE id = 1;
-- ERROR: update or delete on table "lots" violates foreign key constraint
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates serials.lot_id if lots.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated
- **Note**: Primary keys should rarely change in practice

### Business Logic

1. **LOT Capacity Constraint**:
   - Maximum 100 serials per LOT (enforced by trigger)
   - Constraint checked before INSERT into serials
   - target_quantity in LOT determines actual limit

```sql
-- Trigger to enforce LOT capacity
CREATE OR REPLACE FUNCTION validate_lot_capacity()
RETURNS TRIGGER AS $$
DECLARE
    v_current_count INTEGER;
    v_target_quantity INTEGER;
BEGIN
    -- Get current serial count and target quantity
    SELECT COUNT(*), l.target_quantity
    INTO v_current_count, v_target_quantity
    FROM serials s
    JOIN lots l ON s.lot_id = l.id
    WHERE s.lot_id = NEW.lot_id
    GROUP BY l.target_quantity;

    -- Check capacity
    IF v_current_count >= v_target_quantity THEN
        RAISE EXCEPTION 'LOT capacity exceeded: maximum % serials allowed (current: %)',
            v_target_quantity, v_current_count;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_serials_validate_lot_capacity
BEFORE INSERT ON serials
FOR EACH ROW
EXECUTE FUNCTION validate_lot_capacity();
```

2. **Serial Number Generation**:
   - Serial number format: `LOT_NUMBER+SEQUENCE` (18 chars total)
   - Example: `KR01PSA25110010001`
   - Sequence auto-increments within LOT (0001-0100)
   - Guaranteed uniqueness within LOT via unique constraint

3. **LOT Status Updates**:
   - LOT status changes based on serial statuses
   - IN_PROGRESS: At least one serial exists
   - COMPLETED: All serials are either PASSED or FAILED
   - Trigger updates LOT quantities based on serial status changes

```sql
-- Trigger to update LOT quantities when serial status changes
CREATE OR REPLACE FUNCTION update_lot_quantities()
RETURNS TRIGGER AS $$
BEGIN
    -- Update LOT actual_quantity, passed_quantity, failed_quantity
    UPDATE lots
    SET
        actual_quantity = (
            SELECT COUNT(*)
            FROM serials
            WHERE lot_id = COALESCE(NEW.lot_id, OLD.lot_id)
        ),
        passed_quantity = (
            SELECT COUNT(*)
            FROM serials
            WHERE lot_id = COALESCE(NEW.lot_id, OLD.lot_id)
              AND status = 'PASSED'
        ),
        failed_quantity = (
            SELECT COUNT(*)
            FROM serials
            WHERE lot_id = COALESCE(NEW.lot_id, OLD.lot_id)
              AND status = 'FAILED'
        ),
        updated_at = NOW()
    WHERE id = COALESCE(NEW.lot_id, OLD.lot_id);

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_serials_update_lot_quantities
AFTER INSERT OR UPDATE OR DELETE ON serials
FOR EACH ROW
EXECUTE FUNCTION update_lot_quantities();
```

4. **Sequence Management**:
   - sequence_in_lot: 1-100 (auto-assigned)
   - Unique constraint: (lot_id, sequence_in_lot)
   - No gaps allowed in sequence
   - First serial in LOT gets sequence = 1

### Example Queries

```sql
-- Get all serials for a specific LOT
SELECT
    s.serial_number,
    s.sequence_in_lot,
    s.status,
    s.rework_count,
    s.created_at,
    s.completed_at
FROM serials s
WHERE s.lot_id = 1
ORDER BY s.sequence_in_lot;

-- Get LOT with serial status breakdown
SELECT
    l.lot_number,
    l.target_quantity,
    l.actual_quantity,
    COUNT(s.id) as total_serials,
    SUM(CASE WHEN s.status = 'CREATED' THEN 1 ELSE 0 END) as created_count,
    SUM(CASE WHEN s.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_count,
    SUM(CASE WHEN s.status = 'PASSED' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN s.status = 'FAILED' THEN 1 ELSE 0 END) as failed_count
FROM lots l
LEFT JOIN serials s ON l.id = s.lot_id
WHERE l.id = 1
GROUP BY l.id, l.lot_number, l.target_quantity, l.actual_quantity;

-- Check LOT completion status
SELECT
    l.lot_number,
    l.target_quantity,
    COUNT(s.id) as actual_serials,
    SUM(CASE WHEN s.status IN ('PASSED', 'FAILED') THEN 1 ELSE 0 END) as completed_serials,
    CASE
        WHEN COUNT(s.id) < l.target_quantity THEN 'Incomplete - Missing serials'
        WHEN SUM(CASE WHEN s.status IN ('PASSED', 'FAILED') THEN 1 ELSE 0 END) = COUNT(s.id)
            THEN 'Complete - All serials finished'
        ELSE 'In Progress'
    END as completion_status
FROM lots l
LEFT JOIN serials s ON l.id = s.lot_id
WHERE l.id = 1
GROUP BY l.id, l.lot_number, l.target_quantity;

-- Find serials with rework
SELECT
    l.lot_number,
    s.serial_number,
    s.status,
    s.rework_count,
    s.failure_reason
FROM serials s
JOIN lots l ON s.lot_id = l.id
WHERE s.lot_id = 1
  AND s.rework_count > 0
ORDER BY s.rework_count DESC, s.sequence_in_lot;
```

### Data Integrity Checklist

- [ ] lot_id must exist in lots table
- [ ] Maximum 100 serials per LOT (enforced by trigger)
- [ ] Serial sequence_in_lot is unique within LOT
- [ ] Serial numbers follow format: {LOT_NUMBER}-{SEQUENCE}
- [ ] LOT quantities automatically updated when serial status changes
- [ ] LOT cannot be deleted if serials exist

---

## 3.3 lots → process_data

### Relationship Type
**One-to-Many (1:N)**

A single LOT can have multiple LOT-level process execution records. Each process_data record with data_level='LOT' must reference exactly one LOT.

### Cardinality
```
lots (1) ────────< (N) process_data (where data_level='LOT')
```

### Foreign Key Definition

```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| lots.id | process_data.lot_id | BIGINT | LOT identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a LOT if any process_data references it
- **Rationale**: Preserve complete manufacturing history
- **Error Message**: "Cannot delete LOT: process data exists"

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates process_data.lot_id if lots.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **LOT-Level vs SERIAL-Level Data**:
   - LOT-level: data_level = 'LOT', serial_id IS NULL
   - SERIAL-level: data_level = 'SERIAL', serial_id IS NOT NULL
   - All process_data must have a valid lot_id (required field)

2. **LOT-Level Process Examples**:
   - Process 8 (PACKAGING): Final packaging of entire LOT
   - Aggregate quality checks performed on batch samples
   - LOT-wide measurements or environmental conditions

3. **Data Consistency**:
   - Each LOT can have multiple process_data records
   - No uniqueness constraint on (lot_id, process_id) for LOT-level data
   - Allows multiple executions of same process at LOT level (e.g., re-packaging)

### Example Queries

```sql
-- Get all LOT-level process data for a specific LOT
SELECT
    l.lot_number,
    p.process_name_ko,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name as operator_name
FROM process_data pd
JOIN lots l ON pd.lot_id = l.id
JOIN processes p ON pd.process_id = p.id
JOIN users u ON pd.operator_id = u.id
WHERE pd.lot_id = 1
  AND pd.data_level = 'LOT'
ORDER BY pd.started_at;

-- Get LOT with process execution summary
SELECT
    l.lot_number,
    COUNT(pd.id) as total_process_executions,
    SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failed_count,
    AVG(pd.duration_seconds) as avg_duration_seconds
FROM lots l
LEFT JOIN process_data pd ON l.id = pd.lot_id AND pd.data_level = 'LOT'
WHERE l.id = 1
GROUP BY l.id, l.lot_number;

-- Check if LOT has packaging process completed
SELECT
    l.lot_number,
    p.process_name_ko,
    pd.result,
    pd.completed_at,
    CASE
        WHEN pd.id IS NULL THEN 'Not started'
        WHEN pd.completed_at IS NULL THEN 'In progress'
        WHEN pd.result = 'PASS' THEN 'Completed successfully'
        ELSE 'Failed'
    END as status
FROM lots l
LEFT JOIN process_data pd ON l.id = pd.lot_id AND pd.data_level = 'LOT'
LEFT JOIN processes p ON pd.process_id = p.id AND p.process_code = 'PACKAGING'
WHERE l.id = 1;
```

### Data Integrity Checklist

- [ ] lot_id must exist in lots table (always required)
- [ ] data_level must be 'LOT' for LOT-level process data
- [ ] serial_id must be NULL for LOT-level data
- [ ] LOT cannot be deleted if process_data references it
- [ ] Multiple process executions allowed per LOT

---

## 3.4 serials → process_data

### Relationship Type
**One-to-Many (1:N) with Expected Cardinality of 8**

A single serial should have exactly 8 process_data records (one per manufacturing process) when complete. Each process_data record with data_level='SERIAL' must reference exactly one serial.

### Cardinality
```
serials (1) ────────< (N=8 expected) process_data (where data_level='SERIAL')
```

### Foreign Key Definition

```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_serial
FOREIGN KEY (serial_id)
REFERENCES serials(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| serials.id | process_data.serial_id | BIGINT | Serial identifier (NULL for LOT-level data) |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a serial if any process_data references it
- **Rationale**: Preserve complete manufacturing traceability
- **Error Message**: "Cannot delete serial: process data exists"

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates process_data.serial_id if serials.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **Expected Process Count**:
   - Each serial must pass through 8 processes (1→8)
   - Complete serial: 8 process_data records with result='PASS'
   - Incomplete serial: < 8 PASS records
   - Failed processes may have multiple attempts (rework)

2. **Process Sequence Enforcement**:
   - Trigger validates process sequence before INSERT
   - Cannot execute process N+2 before process N+1 is complete
   - Example: Cannot do process 5 if process 4 not passed
   - **특별 규칙: 공정 7 (라벨 프린팅)은 공정 1~6 모두 PASS 필수**

```sql
-- Trigger to enforce process sequence
CREATE OR REPLACE FUNCTION validate_process_sequence()
RETURNS TRIGGER AS $$
DECLARE
    v_current_process_number INTEGER;
    v_max_completed_process_number INTEGER;
    v_passed_count INTEGER;
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

    -- Validate sequence
    IF v_current_process_number > v_max_completed_process_number + 1 THEN
        RAISE EXCEPTION 'Process sequence violation: cannot execute process % before completing process %',
            v_current_process_number, v_max_completed_process_number + 1;
    END IF;

    -- Special validation for Process 7 (Label Printing): All processes 1-6 must be PASS
    IF v_current_process_number = 7 THEN
        SELECT COUNT(DISTINCT p.process_number)
        INTO v_passed_count
        FROM process_data pd
        JOIN processes p ON pd.process_id = p.id
        WHERE pd.serial_id = NEW.serial_id
          AND p.process_number BETWEEN 1 AND 6
          AND pd.result = 'PASS';

        IF v_passed_count < 6 THEN
            RAISE EXCEPTION 'Process 7 (Label Printing) requires all previous processes (1-6) to be PASS. Current PASS count: %', v_passed_count;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_process_data_validate_sequence
BEFORE INSERT ON process_data
FOR EACH ROW
EXECUTE FUNCTION validate_process_sequence();
```

3. **Serial Status Updates**:
   - Serial status changes based on process results
   - IN_PROGRESS: At least one process started
   - PASSED: All 8 processes completed with PASS
   - FAILED: Any process failed (can rework)

```sql
-- Trigger to update serial status based on process results
CREATE OR REPLACE FUNCTION update_serial_status_from_process()
RETURNS TRIGGER AS $$
DECLARE
    v_total_passed INTEGER;
    v_any_failed INTEGER;
BEGIN
    -- Only for SERIAL-level data
    IF NEW.data_level != 'SERIAL' OR NEW.serial_id IS NULL THEN
        RETURN NEW;
    END IF;

    -- Count passed processes for this serial
    SELECT COUNT(DISTINCT process_id)
    INTO v_total_passed
    FROM process_data
    WHERE serial_id = NEW.serial_id
      AND result = 'PASS';

    -- Check for any failures
    SELECT COUNT(*)
    INTO v_any_failed
    FROM process_data
    WHERE serial_id = NEW.serial_id
      AND result = 'FAIL'
      AND completed_at > (
          SELECT MAX(completed_at)
          FROM process_data
          WHERE serial_id = NEW.serial_id
            AND result = 'PASS'
      );

    -- Update serial status
    IF v_total_passed = 8 THEN
        -- All processes passed
        UPDATE serials
        SET status = 'PASSED', completed_at = NOW()
        WHERE id = NEW.serial_id;
    ELSIF v_any_failed > 0 AND NEW.result = 'FAIL' THEN
        -- Recent failure
        UPDATE serials
        SET status = 'FAILED'
        WHERE id = NEW.serial_id;
    ELSE
        -- In progress
        UPDATE serials
        SET status = 'IN_PROGRESS'
        WHERE id = NEW.serial_id AND status = 'CREATED';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_process_data_update_serial_status
AFTER INSERT OR UPDATE ON process_data
FOR EACH ROW
EXECUTE FUNCTION update_serial_status_from_process();
```

4. **Rework Handling**:
   - Failed process can be retried (max 3 times)
   - Each attempt creates new process_data record
   - Only latest PASS result counts for completion
   - Rework count tracked in serials table

5. **Uniqueness Constraint**:
   - Partial unique index: (serial_id, process_id) WHERE result='PASS'
   - Prevents multiple PASS records for same serial+process
   - Allows multiple FAIL/REWORK records for rework attempts

```sql
CREATE UNIQUE INDEX uk_process_data_serial_process
ON process_data(serial_id, process_id)
WHERE serial_id IS NOT NULL AND result = 'PASS';
```

### Example Queries

```sql
-- Get all process data for a specific serial
SELECT
    s.serial_number,
    p.process_number,
    p.process_name_ko,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds,
    u.full_name as operator_name
FROM process_data pd
JOIN serials s ON pd.serial_id = s.id
JOIN processes p ON pd.process_id = p.id
JOIN users u ON pd.operator_id = u.id
WHERE pd.serial_id = 1
  AND pd.data_level = 'SERIAL'
ORDER BY p.process_number, pd.started_at;

-- Check serial completion status (8 processes)
SELECT
    s.serial_number,
    s.status,
    COUNT(DISTINCT CASE WHEN pd.result = 'PASS' THEN p.process_number END) as completed_processes,
    CASE
        WHEN COUNT(DISTINCT CASE WHEN pd.result = 'PASS' THEN p.process_number END) = 8
            THEN 'Complete'
        ELSE 'Incomplete'
    END as completion_status,
    ARRAY_AGG(DISTINCT p.process_number ORDER BY p.process_number)
        FILTER (WHERE pd.result = 'PASS') as passed_process_numbers,
    ARRAY_AGG(DISTINCT p.process_number ORDER BY p.process_number)
        FILTER (WHERE pd.result = 'FAIL') as failed_process_numbers
FROM serials s
LEFT JOIN process_data pd ON s.id = pd.serial_id AND pd.data_level = 'SERIAL'
LEFT JOIN processes p ON pd.process_id = p.id
WHERE s.id = 1
GROUP BY s.id, s.serial_number, s.status;

-- Find next process for a serial
SELECT
    s.serial_number,
    COALESCE(MAX(p.process_number), 0) + 1 as next_process_number,
    np.process_name_ko as next_process_name
FROM serials s
LEFT JOIN process_data pd ON s.id = pd.serial_id AND pd.data_level = 'SERIAL' AND pd.result = 'PASS'
LEFT JOIN processes p ON pd.process_id = p.id
LEFT JOIN processes np ON np.process_number = COALESCE(MAX(p.process_number), 0) + 1
WHERE s.id = 1
GROUP BY s.id, s.serial_number, np.process_name_ko;

-- Get rework history for a serial
SELECT
    s.serial_number,
    p.process_name_ko,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.notes,
    u.full_name as operator_name,
    ROW_NUMBER() OVER (PARTITION BY pd.process_id ORDER BY pd.started_at) as attempt_number
FROM process_data pd
JOIN serials s ON pd.serial_id = s.id
JOIN processes p ON pd.process_id = p.id
JOIN users u ON pd.operator_id = u.id
WHERE pd.serial_id = 1
  AND pd.data_level = 'SERIAL'
ORDER BY pd.started_at;
```

### Data Integrity Checklist

- [ ] serial_id must exist in serials table (when data_level='SERIAL')
- [ ] data_level must be 'SERIAL' for unit-level process data
- [ ] Process sequence enforced (1→2→3→4→5→6→7→8)
- [ ] Maximum one PASS record per (serial_id, process_id)
- [ ] Serial status automatically updated based on process results
- [ ] Complete serial has 8 PASS process_data records
- [ ] Serial cannot be deleted if process_data references it

---

## 3.5 processes → process_data

### Relationship Type
**One-to-Many (1:N)**

A single process definition (template) can have many execution records. Each process_data record must reference exactly one process.

### Cardinality
```
processes (1) ────────< (N) process_data
```

### Foreign Key Definition

```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_process
FOREIGN KEY (process_id)
REFERENCES processes(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| processes.id | process_data.process_id | BIGINT | Process definition identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a process if any process_data references it
- **Rationale**: Preserve manufacturing history and process definitions
- **Error Message**: "Cannot delete process: execution data exists"

```sql
-- Trigger to prevent process deletion
CREATE OR REPLACE FUNCTION prevent_process_deletion()
RETURNS TRIGGER AS $$
DECLARE
    v_data_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_data_count
    FROM process_data
    WHERE process_id = OLD.id;

    IF v_data_count > 0 THEN
        RAISE EXCEPTION 'Cannot delete process %: % execution records exist',
            OLD.process_name_ko, v_data_count;
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_processes_prevent_delete
BEFORE DELETE ON processes
FOR EACH ROW
EXECUTE FUNCTION prevent_process_deletion();
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates process_data.process_id if processes.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **Process as Template**:
   - processes table defines the "what" (process definition)
   - process_data records the "when/who/how" (execution details)
   - Process definitions are relatively static (master data)
   - Execution records are high-volume transactional data

2. **Quality Criteria Inheritance**:
   - processes.quality_criteria defines acceptance standards
   - process_data.measurements contains actual measured values
   - Application compares measurements against criteria to determine PASS/FAIL

3. **Process Lifecycle**:
   - New processes can be added (e.g., process 9 for future expansion)
   - Existing processes can be deactivated (is_active = FALSE)
   - Inactive processes not shown in production UI
   - Historical data preserved for inactive processes

4. **Version Control**:
   - Changes to process quality_criteria tracked in audit_logs
   - Execution data references process definition at time of execution
   - Process version can be inferred from audit_logs timestamps

### Example Queries

```sql
-- Get all executions for a specific process
SELECT
    p.process_name_ko,
    COUNT(pd.id) as total_executions,
    SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failed_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) / COUNT(pd.id), 2) as pass_rate,
    AVG(pd.duration_seconds) as avg_duration_seconds,
    MIN(pd.duration_seconds) as min_duration_seconds,
    MAX(pd.duration_seconds) as max_duration_seconds
FROM processes p
LEFT JOIN process_data pd ON p.id = pd.process_id
WHERE p.id = 2  -- ELECTRICAL_TEST
GROUP BY p.id, p.process_name_ko;

-- Get process execution trends over time (daily)
SELECT
    p.process_name_ko,
    DATE(pd.started_at) as execution_date,
    COUNT(pd.id) as execution_count,
    SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) as passed_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) / COUNT(pd.id), 2) as pass_rate,
    AVG(pd.duration_seconds) as avg_duration
FROM processes p
JOIN process_data pd ON p.id = pd.process_id
WHERE p.id = 2
  AND pd.started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.id, p.process_name_ko, DATE(pd.started_at)
ORDER BY execution_date DESC;

-- Compare expected vs actual process duration
SELECT
    p.process_name_ko,
    p.estimated_duration_seconds as expected_duration,
    AVG(pd.duration_seconds) as avg_actual_duration,
    AVG(pd.duration_seconds) - p.estimated_duration_seconds as variance_seconds,
    ROUND(100.0 * (AVG(pd.duration_seconds) - p.estimated_duration_seconds) / NULLIF(p.estimated_duration_seconds, 0), 2) as variance_percent
FROM processes p
LEFT JOIN process_data pd ON p.id = pd.process_id AND pd.completed_at IS NOT NULL
GROUP BY p.id, p.process_name_ko, p.estimated_duration_seconds
ORDER BY p.process_number;

-- Find processes with high failure rates
SELECT
    p.process_number,
    p.process_name_ko,
    COUNT(pd.id) as total_executions,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failure_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) / COUNT(pd.id), 2) as failure_rate
FROM processes p
JOIN process_data pd ON p.id = pd.process_id
WHERE pd.started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.id, p.process_number, p.process_name_ko
HAVING COUNT(pd.id) > 10  -- Minimum sample size
ORDER BY failure_rate DESC;
```

### Analytics Use Cases

1. **Process Performance Monitoring**:
   - Pass/fail rates per process
   - Cycle time analysis (expected vs actual)
   - Bottleneck identification

2. **Quality Control**:
   - Trend analysis for process quality
   - Defect pattern detection
   - Root cause analysis for failures

3. **Operator Performance**:
   - Compare results across operators for same process
   - Training effectiveness measurement
   - Workload balancing

### Data Integrity Checklist

- [ ] process_id must exist in processes table
- [ ] Process cannot be deleted if execution data exists
- [ ] Inactive processes (is_active=FALSE) should not accept new executions
- [ ] Process quality_criteria changes tracked in audit_logs
- [ ] Process definitions preserved for historical data analysis

---

## 3.6 users → process_data

### Relationship Type
**One-to-Many (1:N)**

A single user (operator) can perform many process executions. Each process_data record must be attributed to exactly one user.

### Cardinality
```
users (1) ────────< (N) process_data
```

### Foreign Key Definition

```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_operator
FOREIGN KEY (operator_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| users.id | process_data.operator_id | BIGINT | User identifier (who performed the process) |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a user if any process_data references them
- **Rationale**: Preserve operator accountability and traceability
- **Error Message**: "Cannot delete user: process execution records exist"

```sql
-- Trigger to prevent user deletion
CREATE OR REPLACE FUNCTION prevent_user_deletion()
RETURNS TRIGGER AS $$
DECLARE
    v_data_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_data_count
    FROM process_data
    WHERE operator_id = OLD.id;

    IF v_data_count > 0 THEN
        RAISE EXCEPTION 'Cannot delete user %: % process execution records exist',
            OLD.username, v_data_count;
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_prevent_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION prevent_user_deletion();
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates process_data.operator_id if users.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **Operator Authentication**:
   - User must be authenticated before recording process data
   - Application sets operator_id from current session
   - Cannot assign process execution to different user (audit integrity)

2. **Role-Based Execution**:
   - WORKER role: Can execute processes
   - MANAGER role: Can execute + approve rework
   - ADMIN role: Full access
   - Role validation at application level

3. **User Status**:
   - Only active users (is_active=TRUE) can execute processes
   - Inactive users cannot log in or perform operations
   - Historical data preserved for inactive users

### Example Queries

```sql
-- Get operator performance summary
SELECT
    u.username,
    u.full_name,
    u.role,
    COUNT(pd.id) as total_executions,
    SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failed_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) / COUNT(pd.id), 2) as pass_rate,
    AVG(pd.duration_seconds) as avg_duration_seconds
FROM users u
LEFT JOIN process_data pd ON u.id = pd.operator_id
WHERE u.id = 5
GROUP BY u.id, u.username, u.full_name, u.role;

-- Compare operator performance across processes
SELECT
    u.full_name,
    p.process_name_ko,
    COUNT(pd.id) as execution_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) / COUNT(pd.id), 2) as pass_rate,
    AVG(pd.duration_seconds) as avg_duration
FROM users u
JOIN process_data pd ON u.id = pd.operator_id
JOIN processes p ON pd.process_id = p.id
WHERE u.role = 'WORKER'
  AND pd.started_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.full_name, p.id, p.process_name_ko
ORDER BY u.full_name, p.process_number;

-- Find operators working on a specific date
SELECT DISTINCT
    u.username,
    u.full_name,
    u.department,
    COUNT(pd.id) as operations_count,
    MIN(pd.started_at) as first_operation,
    MAX(pd.completed_at) as last_operation
FROM users u
JOIN process_data pd ON u.id = pd.operator_id
WHERE DATE(pd.started_at) = '2025-11-10'
GROUP BY u.id, u.username, u.full_name, u.department
ORDER BY operations_count DESC;

-- Operator workload distribution (last 7 days)
SELECT
    u.full_name,
    DATE(pd.started_at) as work_date,
    COUNT(pd.id) as daily_operations,
    SUM(pd.duration_seconds) / 3600.0 as total_hours_worked
FROM users u
JOIN process_data pd ON u.id = pd.operator_id
WHERE pd.started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY u.id, u.full_name, DATE(pd.started_at)
ORDER BY work_date DESC, u.full_name;
```

### Performance Tracking Use Cases

1. **Operator Efficiency**:
   - Average process duration per operator
   - Pass rate comparison across operators
   - Identify training needs

2. **Workload Management**:
   - Daily/weekly operation counts per operator
   - Work hour tracking
   - Capacity planning

3. **Quality Accountability**:
   - Track which operator performed failed processes
   - Correlate failures with specific operators
   - Certification and skill validation

### Data Integrity Checklist

- [ ] operator_id must exist in users table
- [ ] User must be active (is_active=TRUE) to perform operations
- [ ] User role appropriate for operation (WORKER can execute)
- [ ] User cannot be deleted if process execution records exist
- [ ] Operator information preserved for audit and accountability

---

## 3.7 users → audit_logs

### Relationship Type
**One-to-Many (1:N)**

A single user can generate many audit log entries. Each audit_log record must be attributed to exactly one user.

### Cardinality
```
users (1) ────────< (N) audit_logs
```

### Foreign Key Definition

```sql
ALTER TABLE audit_logs
ADD CONSTRAINT fk_audit_logs_user
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| users.id | audit_logs.user_id | BIGINT | User who performed the action |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a user if any audit_logs reference them
- **Rationale**: Preserve complete audit trail for compliance
- **Error Message**: "Cannot delete user: audit log entries exist"

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates audit_logs.user_id if users.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **Comprehensive Auditing**:
   - Every CREATE/UPDATE/DELETE operation generates audit log
   - User attribution for all changes (accountability)
   - System user (id=1) for automated operations

2. **Audit Log Generation**:
   - Triggered automatically via database triggers
   - Application sets session variables for user context:
     ```sql
     SET app.current_user_id = '5';
     SET app.client_ip = '192.168.1.100';
     SET app.user_agent = 'Mozilla/5.0...';
     ```
   - Trigger function reads session variables to populate audit_logs

3. **User Context in Triggers**:

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

4. **Immutability**:
   - Audit logs cannot be modified or deleted
   - Enforced by trigger that raises exception
   - Ensures trustworthy audit trail

### Example Queries

```sql
-- Get user activity summary
SELECT
    u.username,
    u.full_name,
    COUNT(al.id) as total_actions,
    SUM(CASE WHEN al.action = 'CREATE' THEN 1 ELSE 0 END) as create_count,
    SUM(CASE WHEN al.action = 'UPDATE' THEN 1 ELSE 0 END) as update_count,
    SUM(CASE WHEN al.action = 'DELETE' THEN 1 ELSE 0 END) as delete_count,
    MIN(al.created_at) as first_action,
    MAX(al.created_at) as last_action
FROM users u
LEFT JOIN audit_logs al ON u.id = al.user_id
WHERE u.id = 5
GROUP BY u.id, u.username, u.full_name;

-- Get recent user activity (last 24 hours)
SELECT
    u.username,
    al.action,
    al.entity_type,
    al.entity_id,
    al.created_at,
    al.ip_address
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.user_id = 5
  AND al.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY al.created_at DESC;

-- Find all changes to a specific entity by user
SELECT
    u.username,
    al.action,
    al.created_at,
    al.old_values,
    al.new_values
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.entity_type = 'lots'
  AND al.entity_id = 1
ORDER BY al.created_at DESC;

-- Detect suspicious activity (many operations in short time)
SELECT
    u.username,
    COUNT(al.id) as action_count,
    MIN(al.created_at) as first_action,
    MAX(al.created_at) as last_action,
    ARRAY_AGG(DISTINCT al.ip_address) as ip_addresses
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.created_at >= NOW() - INTERVAL '1 hour'
GROUP BY u.id, u.username
HAVING COUNT(al.id) > 100
ORDER BY action_count DESC;

-- User activity by entity type (what they modify most)
SELECT
    u.username,
    al.entity_type,
    COUNT(al.id) as modification_count,
    ARRAY_AGG(DISTINCT al.action) as actions_performed
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE u.id = 5
  AND al.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username, al.entity_type
ORDER BY modification_count DESC;
```

### Compliance and Security Use Cases

1. **Regulatory Compliance**:
   - Track all changes for 3-year retention
   - Who changed what, when, and from where
   - Complete change history for audits

2. **Security Monitoring**:
   - Detect unusual activity patterns
   - Track IP addresses for security analysis
   - Identify unauthorized access attempts

3. **Troubleshooting**:
   - Trace changes that caused issues
   - Reconstruct data state at any point in time
   - Identify who made problematic changes

### Data Integrity Checklist

- [ ] user_id must exist in users table
- [ ] Every database change generates audit log entry
- [ ] Audit logs are immutable (no UPDATE/DELETE)
- [ ] User cannot be deleted if audit logs exist
- [ ] Session variables set correctly for user attribution
- [ ] 3-year retention policy enforced

---

## 3.8 equipment → process_data

### Relationship Type
**One-to-Many (1:N)**

A single equipment can be used for many process executions. Each process_data record may optionally reference the equipment used.

### Cardinality
```
equipment (1) ────────< (N) process_data
```

### Foreign Key Definition

```sql
ALTER TABLE process_data
ADD CONSTRAINT fk_process_data_equipment
FOREIGN KEY (equipment_id)
REFERENCES equipment(id)
ON DELETE SET NULL
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| equipment.id | process_data.equipment_id | BIGINT | Equipment used for process execution (optional) |

### Referential Integrity Rules

#### ON DELETE SET NULL
- **Behavior**: Sets equipment_id to NULL if equipment is deleted
- **Rationale**: Preserve process data history even if equipment is removed
- **Note**: Equipment deletion is rare; typically use status change instead

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates process_data.equipment_id if equipment.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated

### Business Logic

1. **Optional Equipment Reference**:
   - equipment_id is nullable (some processes may not track equipment)
   - Equipment tracking enabled during start process (착공)
   - Equipment code from frontend converted to equipment_id

2. **Equipment Utilization Tracking**:
   - Track which equipment performed each process
   - Enable equipment performance and maintenance analysis
   - Support equipment-based quality correlation

3. **Start Process (착공) Workflow**:
   - Accepts `equipment_id` parameter (via equipment_code)
   - Saves to process_data.equipment_id
   - Optional field - not all processes require equipment tracking

### Example Queries

```sql
-- Get process executions for a specific equipment
SELECT
    e.equipment_code,
    e.equipment_name,
    p.process_name_ko,
    pd.result,
    pd.started_at,
    pd.completed_at,
    pd.duration_seconds
FROM process_data pd
JOIN equipment e ON pd.equipment_id = e.id
JOIN processes p ON pd.process_id = p.id
WHERE pd.equipment_id = 1
ORDER BY pd.started_at DESC;

-- Equipment utilization analysis
SELECT
    e.equipment_code,
    e.equipment_name,
    COUNT(pd.id) as total_executions,
    SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failed_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'PASS' THEN 1 ELSE 0 END) / NULLIF(COUNT(pd.id), 0), 2) as pass_rate,
    AVG(pd.duration_seconds) as avg_duration_seconds
FROM equipment e
LEFT JOIN process_data pd ON e.id = pd.equipment_id
WHERE e.id = 1
GROUP BY e.id, e.equipment_code, e.equipment_name;

-- Find equipment with high failure rates
SELECT
    e.equipment_code,
    e.equipment_name,
    p.process_name_ko,
    COUNT(pd.id) as execution_count,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failure_count,
    ROUND(100.0 * SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) / NULLIF(COUNT(pd.id), 0), 2) as failure_rate
FROM equipment e
JOIN process_data pd ON e.id = pd.equipment_id
JOIN processes p ON pd.process_id = p.id
WHERE pd.started_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY e.id, e.equipment_code, e.equipment_name, p.id, p.process_name_ko
HAVING COUNT(pd.id) > 10
ORDER BY failure_rate DESC;

-- Equipment maintenance correlation with failures
SELECT
    e.equipment_code,
    e.last_maintenance_date,
    e.next_maintenance_date,
    COUNT(pd.id) as executions_since_maintenance,
    SUM(CASE WHEN pd.result = 'FAIL' THEN 1 ELSE 0 END) as failures_since_maintenance
FROM equipment e
JOIN process_data pd ON e.id = pd.equipment_id
WHERE pd.started_at >= e.last_maintenance_date
GROUP BY e.id, e.equipment_code, e.last_maintenance_date, e.next_maintenance_date
ORDER BY failures_since_maintenance DESC;
```

### Equipment Tracking Use Cases

1. **Equipment Performance Monitoring**:
   - Pass/fail rates per equipment
   - Cycle time analysis per equipment
   - Identify underperforming equipment

2. **Maintenance Planning**:
   - Correlate failures with maintenance schedules
   - Predict maintenance needs based on utilization
   - Track equipment downtime

3. **Quality Analysis**:
   - Identify equipment-related quality issues
   - Compare performance across similar equipment
   - Root cause analysis for defects

### Data Integrity Checklist

- [ ] equipment_id must exist in equipment table (if not NULL)
- [ ] Equipment status should be ACTIVE for new process executions
- [ ] Equipment deletion sets process_data.equipment_id to NULL
- [ ] Equipment utilization tracked for maintenance planning
- [ ] Historical process data preserved when equipment is removed

---

## 3.9 lots → wip_items

### Relationship Type
**One-to-Many (1:N) with Bounded Cardinality**

하나의 LOT는 진행 상태 추적을 위해 최대 100개의 WIP 항목을 생성합니다.

### Cardinality
```
lots (1) ────────< (N, max 100) wip_items
```

### Foreign Key Definition

```sql
ALTER TABLE wip_items
ADD CONSTRAINT fk_wip_items_lot
FOREIGN KEY (lot_id)
REFERENCES lots(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| lots.id | wip_items.lot_id | BIGINT | LOT identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a LOT if any wip_items reference it
- **Rationale**: Preserve complete production traceability
- **Error Message**: "Cannot delete LOT: WIP items exist"

```sql
-- Example: This will FAIL if wip_items exist for this LOT
DELETE FROM lots WHERE id = 1;
-- ERROR: update or delete on table "lots" violates foreign key constraint
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates wip_items.lot_id if lots.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated
- **Note**: Primary keys should rarely change in practice

### Business Logic

1. **WIP Capacity**:
   - LOT당 최대 100개 WIP 항목
   - INSERT 전 트리거로 검증
   - wip_id 포맷: WIP-{LOT_NUMBER}-{SEQ:03d}

2. **Auto-Generation**:
   - INSERT 시 wip_id 자동 생성
   - LOT당 순번 자동 증가
   - 고유성 보장

3. **Status Management**:
   - WIP 상태는 Serial 상태와 독립적
   - 집계된 진행 상태 추적 가능
   - 배치 단위 제조 지원

### Example Queries

```sql
-- LOT의 모든 WIP 항목 조회
SELECT wip_id, serial_id, status, created_at
FROM wip_items
WHERE lot_id = 1
ORDER BY wip_id;

-- WIP capacity 확인
SELECT COUNT(*) as wip_count, l.target_quantity
FROM wip_items wi
JOIN lots l ON wi.lot_id = l.id
WHERE l.id = 1
GROUP BY l.target_quantity;
```

### Data Integrity Checklist
- [ ] lot_id가 lots 테이블에 존재해야 함
- [ ] LOT당 최대 100개 WIP 항목
- [ ] WIP ID 포맷: WIP-{LOT}-{SEQ}
- [ ] WIP 항목이 존재하면 LOT 삭제 불가

---

## 3.10 wip_items → wip_process_history

### Relationship Type
**One-to-Many (1:N)**

하나의 WIP 항목은 공정 진행을 추적하는 여러 이력 레코드를 가집니다.

### Cardinality
```
wip_items (1) ────────< (N) wip_process_history
```

### Foreign Key Definition

```sql
ALTER TABLE wip_process_history
ADD CONSTRAINT fk_wip_process_history_wip_item
FOREIGN KEY (wip_item_id)
REFERENCES wip_items(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;
```

### Column Specification

| Parent Column | Child Column | Type | Description |
|---------------|--------------|------|-------------|
| wip_items.id | wip_process_history.wip_item_id | BIGINT | WIP item identifier |

### Referential Integrity Rules

#### ON DELETE RESTRICT
- **Behavior**: Prevents deletion of a WIP item if any wip_process_history references it
- **Rationale**: Preserve complete audit trail
- **Error Message**: "Cannot delete WIP item: process history exists"

```sql
-- Example: This will FAIL if history exists for this WIP item
DELETE FROM wip_items WHERE id = 1;
-- ERROR: update or delete on table "wip_items" violates foreign key constraint
```

#### ON UPDATE CASCADE
- **Behavior**: Automatically updates wip_process_history.wip_item_id if wip_items.id changes
- **Rationale**: Maintain consistency if primary keys are regenerated
- **Note**: Primary keys should rarely change in practice

### Business Logic

1. **Complete Audit Trail**:
   - 모든 WIP 상태 전이 기록
   - 공정 단위 추적
   - 결과 캡처 (PASS/FAIL/REWORK)

2. **History Tracking**:
   - 불변 이력 레코드
   - 분석을 위한 시계열 데이터
   - 트렌드 분석 지원

3. **Process Reference**:
   - processes 테이블과 연계
   - 실행된 공정 추적
   - 공정별 리포팅 지원

### Example Queries

```sql
-- WIP 진행 이력 조회
SELECT wph.process_id, wph.result, wph.started_at, wph.completed_at
FROM wip_process_history wph
WHERE wph.wip_item_id = 1
ORDER BY wph.created_at;

-- WIP 완료 타임라인
SELECT wi.wip_id, COUNT(wph.id) as process_count,
       MAX(CASE WHEN wph.result = 'PASS' THEN 1 ELSE 0 END) as passed_processes
FROM wip_items wi
LEFT JOIN wip_process_history wph ON wi.id = wph.wip_item_id
WHERE wi.lot_id = 1
GROUP BY wi.id, wi.wip_id;
```

### Data Integrity Checklist
- [ ] wip_item_id가 wip_items 테이블에 존재해야 함
- [ ] 레코드 불변 (append-only)
- [ ] 이력이 존재하면 WIP 항목 삭제 불가
- [ ] 완전한 감사 추적 보존

---

## Cross-Relationship Integrity Rules

### Global Constraints

1. **Referential Integrity**:
   - All foreign keys use ON DELETE RESTRICT
   - Prevents orphaned records
   - Requires explicit cleanup before deletion

2. **Cascading Updates**:
   - All foreign keys use ON UPDATE CASCADE
   - Ensures consistency if primary keys change
   - Rare in practice (primary keys are stable)

3. **Audit Trail**:
   - All relationships logged via audit_logs
   - User attribution for all changes
   - Complete change history preserved

### Relationship Validation Summary

| Parent Table | Child Table | FK Column | Delete Rule | Update Rule | Uniqueness |
|--------------|-------------|-----------|-------------|-------------|------------|
| product_models | lots | product_model_id | RESTRICT | CASCADE | - |
| lots | serials | lot_id | RESTRICT | CASCADE | (lot_id, sequence_in_lot) |
| lots | process_data | lot_id | RESTRICT | CASCADE | - |
| serials | process_data | serial_id | RESTRICT | CASCADE | (serial_id, process_id) WHERE result='PASS' |
| processes | process_data | process_id | RESTRICT | CASCADE | - |
| users | process_data | operator_id | RESTRICT | CASCADE | - |
| users | audit_logs | user_id | RESTRICT | CASCADE | - |
| equipment | process_data | equipment_id | SET NULL | CASCADE | - |
| lots | wip_items | lot_id | RESTRICT | CASCADE | - |
| wip_items | wip_process_history | wip_item_id | RESTRICT | CASCADE | - |

---

## Best Practices

### 1. Deletion Strategy
- **Do not delete records** - use soft delete (status flags) instead
- If deletion required:
  1. Check for dependent records first
  2. Delete child records before parents
  3. Use transactions for atomicity

### 2. Query Performance
- Always use indexes on foreign key columns
- Use EXPLAIN ANALYZE to verify query plans
- Consider composite indexes for common filter combinations

### 3. Data Integrity
- Let database enforce constraints via foreign keys
- Use triggers for complex validation logic
- Prefer database constraints over application validation

### 4. Audit Compliance
- Set session variables before database operations:
  ```sql
  SET app.current_user_id = '5';
  SET app.client_ip = '192.168.1.100';
  SET app.user_agent = 'Mozilla/5.0...';
  ```
- Review audit_logs regularly for compliance
- Archive old audit logs to maintain performance

---

## Entity Relationship Summary Diagram

```
product_models (1) ──────< (N) lots (1) ──────< (N, max 100) serials
                                 │                        │
                                 │                        │
                                 └────< (N) ──────────────┘
                                         process_data
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                   (N) >─────< (1)       (N) >─────< (1)       (N) >─────< (1)
                      lots              serials              processes


users (1) ──────< (N) process_data
  │
  │
  └──────< (N) audit_logs
```

---

## Migration and Deployment

### DDL Execution Order

```sql
-- 1. Create base tables (no dependencies)
CREATE TABLE product_models (...);
CREATE TABLE processes (...);
CREATE TABLE users (...);

-- 2. Create tables with single dependencies
CREATE TABLE lots (...);
ALTER TABLE lots ADD CONSTRAINT fk_lots_product_model ...;

-- 3. Create tables with multiple dependencies
CREATE TABLE serials (...);
ALTER TABLE serials ADD CONSTRAINT fk_serials_lot ...;

CREATE TABLE process_data (...);
ALTER TABLE process_data ADD CONSTRAINT fk_process_data_lot ...;
ALTER TABLE process_data ADD CONSTRAINT fk_process_data_serial ...;
ALTER TABLE process_data ADD CONSTRAINT fk_process_data_process ...;
ALTER TABLE process_data ADD CONSTRAINT fk_process_data_operator ...;
ALTER TABLE process_data ADD CONSTRAINT fk_process_data_equipment ...;

-- 4. Create audit table (references all entities)
CREATE TABLE audit_logs (...);
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_user ...;

-- 5. Create indexes
CREATE INDEX idx_lots_product_model ON lots(product_model_id);
-- ... all other indexes

-- 6. Create triggers
CREATE TRIGGER trg_lots_generate_number ...;
-- ... all other triggers

-- 7. Load master data
INSERT INTO processes (...) VALUES (...);
INSERT INTO users (...) VALUES (...);
```

---

## Next Steps

1. Review ERD documentation (**01-ERD.md**)
2. Review entity definitions (**02-entity-definitions.md**)
3. Execute DDL scripts to create database schema
4. Load master data (processes, initial users)
5. Implement application layer with session variable management
6. Configure monitoring and alerting
7. Test referential integrity with sample data
8. Conduct performance testing with expected data volumes

---

**Document Version**: 1.1
**Last Updated**: 2025-11-20
**Author**: Database Architecture Team
**Status**: Ready for Implementation
