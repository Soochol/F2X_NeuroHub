# ProcessData Validation Documentation

## Overview

This document describes all validation rules for ProcessData schemas in the F2X NeuroHub Manufacturing Execution System. These rules ensure data integrity, business logic compliance, and provide clear error messages for better user experience.

## Table of Contents

1. [Data Level Validation](#data-level-validation)
2. [Process Result Validation](#process-result-validation)
3. [Defects and Result Consistency](#defects-and-result-consistency)
4. [Timestamp Validation](#timestamp-validation)
5. [JSONB Field Validation](#jsonb-field-validation)
6. [Business Rules Validation](#business-rules-validation)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Data Level Validation

### Overview
Data level determines the granularity of process data tracking: LOT, WIP, or SERIAL.

### Rules

#### LOT Level
- **serial_id**: MUST be `None`
- **wip_id**: MUST be `None`
- **Use Case**: Tracking processes at the lot level (batch operations)

#### WIP Level
- **serial_id**: MUST be `None`
- **wip_id**: MUST be provided (positive integer)
- **Use Case**: Tracking processes for Work-In-Progress items (processes 1-6)

#### SERIAL Level
- **serial_id**: MUST be provided (positive integer)
- **wip_id**: Optional (can be provided for processes that involve WIP items)
- **Use Case**: Tracking processes for individual units (processes 7-8)

### Error Messages

```python
# LOT level with serial_id
"serial_id must be None when data_level='LOT'. Current: serial_id=100, data_level=LOT"

# WIP level without wip_id
"wip_id is required when data_level='WIP'. Current: wip_id=None, data_level=WIP"

# SERIAL level without serial_id
"serial_id is required when data_level='SERIAL'. Current: serial_id=None, data_level=SERIAL"
```

## Process Result Validation

### Valid Values
- **PASS**: Process completed successfully, all quality criteria met
- **FAIL**: Process failed, defects detected
- **REWORK**: Process requires rework/retry

### Rules
- Case-insensitive input (e.g., "pass", "Pass", "PASS" all valid)
- Invalid values trigger clear error messages with valid options

### Error Messages

```python
"Invalid result 'SUCCESS'. Must be one of ['PASS', 'FAIL', 'REWORK']. Current value: 'SUCCESS'"
```

## Defects and Result Consistency

### Core Rules

#### Result = PASS
- **defects**: MUST be `None` or empty dict `{}`
- **notes**: Optional

#### Result = FAIL
- **defects**: MUST be provided with defect details
- **notes**: Recommended (warning issued if missing)

#### Result = REWORK
- **defects**: Optional (can document reason for rework)
- **notes**: Recommended when defects present

### Business Logic

The system enforces that failures must be documented with specific defect information. This ensures:
1. Quality tracking and traceability
2. Root cause analysis capability
3. Process improvement insights

### Error Messages and Warnings

```python
# FAIL without defects (ERROR)
"defects information is required when result='FAIL'. Current: result=FAIL, defects=None. Please provide defect details such as type, location, and severity."

# PASS with defects (ERROR)
"defects should be None or empty when result='PASS'. Current: result=PASS, defects={'type': 'crack'}"

# FAIL without notes (WARNING)
"Notes are recommended when result='FAIL' to provide additional context. Current: result=FAIL, notes=None"

# REWORK with defects but no notes (WARNING)
"Notes are recommended when result='REWORK' with defects to explain the rework reason."
```

## Timestamp Validation

### Rules
1. **started_at**: Required, must be a valid datetime
2. **completed_at**: Optional, must be >= started_at if provided
3. **duration_seconds**: Auto-calculated from timestamps in ProcessDataInDB

### Valid Scenarios
- Process in progress: completed_at = None
- Instant process: completed_at = started_at
- Normal process: completed_at > started_at

### Error Messages

```python
"completed_at must be greater than or equal to started_at. Current: started_at=2024-01-01T10:00:00, completed_at=2024-01-01T09:00:00, invalid duration=-3600 seconds"
```

## JSONB Field Validation

### Measurements Field

#### Structure Requirements
- Must be a dictionary
- Keys must be strings
- Values must be JSON-serializable (str, int, float, bool, list, dict, None)

#### Valid Example
```json
{
  "temperature": 25.5,
  "pressure": 1.0,
  "humidity": 45,
  "status": "stable",
  "sensors": ["s1", "s2"],
  "config": {"mode": "auto", "threshold": 0.5}
}
```

### Defects Field

#### Structure Requirements
- Must be a dictionary (when provided)
- Keys must be strings
- Values must be JSON-serializable
- Empty dict `{}` is converted to `None`

#### Valid Example
```json
{
  "type": "crack",
  "location": "edge",
  "severity": "critical",
  "count": 3,
  "images": ["img1.jpg", "img2.jpg"],
  "dimensions": {"width": 2.5, "length": 5.0}
}
```

### Error Messages

```python
# Invalid type
"measurements must be a dictionary, got str"

# Invalid key type
"measurement keys must be strings, got int for key 123"

# Non-serializable value
"measurement value for 'object' must be JSON-serializable, got CustomClass"
```

## Business Rules Validation

### Comprehensive Validation

The `validate_comprehensive_business_rules` validator performs all business logic checks at once, providing:
1. Clear, actionable error messages
2. Full context of current data state
3. Grouped errors for better debugging

### Core Field Validation
- **lot_id**: Must be positive integer
- **process_id**: Must be positive integer
- **operator_id**: Must be positive integer
- **equipment_id**: Must be positive integer or None
- **serial_id/wip_id**: Must be positive when required by data_level

### Error Message Format

```
Business rules validation failed:
  - Invalid lot_id=-1. Must be a positive integer.
  - Invalid process_id=0. Must be a positive integer.
  - Invalid operator_id=-5. Must be a positive integer.

Current data state:
  data_level: LOT
  result: PASS
  lot_id: -1
  serial_id: None
  wip_id: None
  process_id: 0
  has_defects: False
  has_notes: False
  has_measurements: False
```

### Warnings
Non-critical issues generate warnings instead of errors:
- Missing measurements for a process
- Missing notes for FAIL/REWORK results
- Incomplete documentation

## Error Handling

### API Integration

When validation fails, the API should:

1. **Catch ValidationError**
```python
from pydantic import ValidationError

try:
    process_data = ProcessDataCreate(**request_data)
except ValidationError as e:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": e.errors(),
            "error_summary": str(e)
        }
    )
```

2. **Handle Warnings**
```python
import warnings

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    process_data = ProcessDataCreate(**request_data)

    if w:
        # Log warnings or include in response
        warning_messages = [str(warning.message) for warning in w]
```

3. **Database Context Validation**
```python
# Use the validate_process_data_context helper
validation_result = validate_process_data_context(
    lot_id=request_data["lot_id"],
    serial_id=request_data.get("serial_id"),
    wip_id=request_data.get("wip_id"),
    process_id=request_data["process_id"],
    operator_id=request_data["operator_id"],
    equipment_id=request_data.get("equipment_id"),
    data_level=DataLevel(request_data["data_level"]),
    db_session=db
)

if not validation_result["valid"]:
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Context validation failed",
            "errors": validation_result["errors"],
            "warnings": validation_result["warnings"]
        }
    )
```

## Examples

### Valid LOT-Level Data
```json
{
  "lot_id": 1,
  "serial_id": null,
  "wip_id": null,
  "process_id": 1,
  "operator_id": 1,
  "data_level": "LOT",
  "result": "PASS",
  "measurements": {"temperature": 25.5},
  "defects": null,
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T10:15:00"
}
```

### Valid WIP-Level Data
```json
{
  "lot_id": 1,
  "serial_id": null,
  "wip_id": 50,
  "process_id": 3,
  "operator_id": 2,
  "data_level": "WIP",
  "result": "PASS",
  "measurements": {"pressure": 1.5, "flow_rate": 10.2},
  "started_at": "2024-01-01T11:00:00",
  "completed_at": "2024-01-01T11:30:00"
}
```

### Valid SERIAL-Level FAIL Data
```json
{
  "lot_id": 1,
  "serial_id": 100,
  "wip_id": null,
  "process_id": 7,
  "operator_id": 2,
  "equipment_id": 3,
  "data_level": "SERIAL",
  "result": "FAIL",
  "measurements": {"voltage": 2.8, "current": 0.5},
  "defects": {
    "type": "electrical_fault",
    "location": "connector_A",
    "severity": "critical",
    "voltage_reading": 2.8,
    "expected_voltage": 3.3
  },
  "started_at": "2024-01-01T11:00:00",
  "completed_at": "2024-01-01T11:05:00",
  "notes": "Voltage below threshold, connector damage suspected"
}
```

### Invalid Data Examples

#### Missing Required Fields
```json
{
  "lot_id": 1,
  "data_level": "SERIAL"
  // Missing: process_id, operator_id, serial_id, started_at
}
```
**Error**: Multiple validation errors for required fields

#### Inconsistent Data Level
```json
{
  "lot_id": 1,
  "serial_id": 100,  // Should be null for LOT level
  "process_id": 1,
  "operator_id": 1,
  "data_level": "LOT",
  "started_at": "2024-01-01T10:00:00"
}
```
**Error**: "serial_id must be None when data_level='LOT'"

#### FAIL Without Defects
```json
{
  "lot_id": 1,
  "process_id": 1,
  "operator_id": 1,
  "data_level": "LOT",
  "result": "FAIL",
  "defects": null,  // Required for FAIL
  "started_at": "2024-01-01T10:00:00"
}
```
**Error**: "defects information is required when result='FAIL'"

#### Invalid Timestamp Order
```json
{
  "lot_id": 1,
  "process_id": 1,
  "operator_id": 1,
  "data_level": "LOT",
  "started_at": "2024-01-01T10:00:00",
  "completed_at": "2024-01-01T09:00:00"  // Before started_at
}
```
**Error**: "completed_at must be greater than or equal to started_at"

## Best Practices

1. **Always validate before database operations**
   - Use Pydantic schemas for request validation
   - Use context validation for referential integrity

2. **Handle warnings appropriately**
   - Log warnings for audit trail
   - Consider showing warnings to users as hints

3. **Provide clear feedback**
   - Include current values in error messages
   - Suggest corrections when possible

4. **Test edge cases**
   - Empty dictionaries vs None
   - Case sensitivity
   - Timestamp boundaries
   - Data level transitions

5. **Document process-specific rules**
   - Some processes may require specific measurements
   - Equipment requirements may vary by process
   - Add process-specific validators as needed

## Migration Notes

When updating existing data to comply with new validation rules:

1. **Audit existing data**
   ```sql
   -- Find FAIL results without defects
   SELECT * FROM process_data
   WHERE result = 'FAIL' AND (defects IS NULL OR defects = '{}');

   -- Find PASS results with defects
   SELECT * FROM process_data
   WHERE result = 'PASS' AND defects IS NOT NULL AND defects != '{}';
   ```

2. **Add missing defect information**
   ```python
   # Update FAIL records with placeholder defects
   UPDATE process_data
   SET defects = '{"type": "unspecified", "migrated": true}'
   WHERE result = 'FAIL' AND (defects IS NULL OR defects = '{}');
   ```

3. **Clear defects from PASS records**
   ```python
   UPDATE process_data
   SET defects = NULL
   WHERE result = 'PASS' AND defects IS NOT NULL;
   ```

4. **Validate data consistency**
   - Run validation tests on migrated data
   - Log any remaining inconsistencies
   - Create data correction tasks as needed