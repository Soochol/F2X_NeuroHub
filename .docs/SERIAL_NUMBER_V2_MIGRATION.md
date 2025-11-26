# Serial Number Format Refactoring Guide

> **⚠️ HISTORICAL DOCUMENT**: This document describes the V2 format migration (2025-11-20).
> **CURRENT FORMAT** (as of 2025-11-22): V3 with 13-char LOT numbers and 16-char Serial numbers.
> - LOT: `KR01PSA251101` (13 chars with sequence number)
> - Serial: `KR01PSA251101001` (16 chars)
> See database DDL and CRUD files for current implementation.

## Overview

This document describes the refactored serial number format implementation. The system has migrated from a legacy format to a new compressed format that is now the standard.

**Date**: 2025-11-20
**Status**: Superseded by V3 format (2025-11-22)

---

## Format Comparison

### Legacy Format (Historical Reference)
- **Format**: `PSA10-KR001-251110D-001-0001`
- **Length**: 28 characters (with hyphens)
- **Structure**: `{MODEL}-{LINE}-{YYMMDD}{SHIFT}-{LOT_SEQ}-{SERIAL_SEQ}`
- **Components**:
  - Model code: PSA10 (variable length)
  - Line code: KR001 (5 chars)
  - Date: 251110 (6 chars - YYMMDD)
  - Shift: D (1 char - D/N)
  - LOT sequence: 001 (3 chars)
  - Serial sequence: 0001 (4 chars)

### Standard Format (Current)
- **Format**: `KR01PSA2511001` (Serial) / `KR01PSA2511` (LOT)
- **Length**: 14 characters (Serial), 11 characters (LOT)
- **Structure**: `{COUNTRY}{LINE}{MODEL}{YYMM}{SEQUENCE}`
- **Components**:
  - Country code: KR (2 chars)
  - Line number: 01 (2 chars)
  - Model code: PSA (3 chars - abbreviated)
  - Production month: 2511 (4 chars - YYMM)
  - Sequence: 001 (3 chars)

**Size Reduction**: 28 chars → 14 chars (50% compression for Serial), 24 chars → 11 chars (54% compression for LOT)

---

## Key Changes

### 1. Date Granularity
- **Legacy**: Full date with day (YYMMDD)
- **Standard**: Month only (YYMM)
- **Rationale**: Production planning is done monthly, daily tracking adds unnecessary complexity

### 2. Shift Indicator Removed
- **Legacy**: Included shift (D/N)
- **Standard**: No shift indicator
- **Rationale**: Shift information is already in LOT number, redundant in serial

### 3. Line Number Format
- **Legacy**: KR001 (5 chars - country + 3-digit number)
- **Standard**: KR01 (4 chars - country + 2-digit number)
- **Rationale**: Supports up to 99 production lines, sufficient for current scale

### 4. Model Code Abbreviation
- **Legacy**: Full model name (variable length)
- **Standard**: 3-character abbreviation
- **Implementation**: New `model_code_mapping` table

| Full Model Code | Abbreviation |
|-----------------|--------------|
| PSA10           | PSA          |
| Withforce       | WFO          |

### 5. No Separators
- **Legacy**: Uses hyphens for readability
- **Standard**: No hyphens (compact for barcode/QR)
- **Display**: Hyphens added only for human display: `KR01-PSA-2511` (LOT) or `KR01-PSA-2511-001` (Serial)

---

## Database Changes

### 1. New Table: `model_code_mapping`

```sql
CREATE TABLE model_code_mapping (
    id SERIAL PRIMARY KEY,
    model_code VARCHAR(20) NOT NULL UNIQUE,  -- PSA10, Withforce
    short_code CHAR(3) NOT NULL UNIQUE,      -- PSA, WFO
    description VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO model_code_mapping (model_code, short_code, description)
VALUES
    ('PSA10', 'PSA', 'PSA10 모델'),
    ('Withforce', 'WFO', 'Withforce 모델');
```

### 2. Updated Table: `serials`

```sql
-- Added format_version column
ALTER TABLE serials ADD COLUMN format_version SMALLINT DEFAULT 2;

-- Updated serial_number column size
ALTER TABLE serials ALTER COLUMN serial_number TYPE VARCHAR(30);

-- Version tracking
-- 1 = Legacy format (28 chars with hyphens)
-- 2 = Standard format (14 chars no hyphens)
```

### 3. Trigger Functions

**Serial Number Generation (Standard)**:
```sql
CREATE OR REPLACE FUNCTION generate_serial_number() RETURNS TRIGGER AS $$
DECLARE
    v_line_code VARCHAR(4);
    v_model_short VARCHAR(3);
    v_month_part VARCHAR(4);
    v_sequence VARCHAR(3);
BEGIN
    -- Extract line code: KR01
    SELECT CONCAT(
        SUBSTRING(pl.line_code, 1, 2),
        LPAD(SUBSTRING(pl.line_code, 3)::INTEGER::TEXT, 2, '0')
    ) INTO v_line_code
    FROM lots l
    JOIN production_lines pl ON l.production_line_id = pl.id
    WHERE l.id = NEW.lot_id;

    -- Get 3-char model code
    SELECT mcm.short_code INTO v_model_short
    FROM lots l
    JOIN product_models pm ON l.product_model_id = pm.id
    JOIN model_code_mapping mcm ON pm.model_code = mcm.model_code
    WHERE l.id = NEW.lot_id;

    -- Production month (YYMM)
    SELECT TO_CHAR(l.production_date, 'YYMM') INTO v_month_part
    FROM lots l WHERE l.id = NEW.lot_id;

    -- Sequence (001-999)
    v_sequence := LPAD(NEW.sequence_in_lot::TEXT, 3, '0');

    -- Build serial: KR01PSA2511001
    NEW.serial_number := v_line_code || v_model_short || v_month_part || v_sequence;
    NEW.format_version := 2;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**LOT Number Generation (Standard)**:
```sql
CREATE OR REPLACE FUNCTION generate_lot_number() RETURNS TRIGGER AS $$
DECLARE
    v_line_code VARCHAR(4);
    v_model_short VARCHAR(3);
    v_month_part VARCHAR(4);
    v_sequence VARCHAR(3);
BEGIN
    -- Line code (KR01)
    SELECT CONCAT(
        SUBSTRING(line_code, 1, 2),
        LPAD(SUBSTRING(line_code, 3)::INTEGER::TEXT, 2, '0')
    ) INTO v_line_code
    FROM production_lines WHERE id = NEW.production_line_id;

    -- Model short code
    SELECT mcm.short_code INTO v_model_short
    FROM product_models pm
    JOIN model_code_mapping mcm ON pm.model_code = mcm.model_code
    WHERE pm.id = NEW.product_model_id;

    -- Production month
    v_month_part := TO_CHAR(NEW.production_date, 'YYMM');

    -- Sequence (001-999)
    v_sequence := LPAD(NEW.sequence_number::TEXT, 3, '0');

    -- LOT format: KR01PSA2511 (11 chars)
    NEW.lot_number := v_line_code || v_model_short || v_month_part || v_sequence;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## Backend Changes

### 1. New Utility Module

**File**: `backend/app/utils/serial_number.py`

**Key Classes**:
- `SerialNumber`: Standard format handler
  - `validate(serial)`: Validate standard format
  - `parse(serial)`: Parse into components
  - `format_display(serial)`: Format with hyphens
  - `get_full_info(serial)`: Complete parsing with metadata

- `LegacySerialNumber`: Legacy format handler (backward compatibility)
  - `validate(serial)`: Validate legacy format
  - `parse(serial)`: Parse legacy components

- `detect_serial_version(serial)`: Auto-detect version (1, 2, or None)

**Usage Example**:
```python
from app.utils.serial_number import SerialNumber

# Validate
is_valid = SerialNumber.validate("KR01PSA2511001")  # True

# Parse
components = SerialNumber.parse("KR01PSA2511001")
# {
#     "country_code": "KR",
#     "line_number": "01",
#     "model_code": "PSA",
#     "production_month": "2511",
#     "sequence": "001"
# }

# Format for display
formatted = SerialNumber.format_display("KR01PSA2511001")
# "KR01-PSA-2511-001"
```

### 2. Updated Pydantic Schemas

**File**: `backend/app/schemas/serial.py`

**Changes**:
- Added `format_version` field to `SerialInDB`
- Added computed field `serial_number_formatted` (human-readable)
- Added computed field `is_standard_format` (boolean)

```python
class SerialInDB(SerialBase):
    format_version: Optional[int] = 2

    @computed_field
    @property
    def serial_number_formatted(self) -> str:
        """Auto-format based on version"""
        if self.format_version == 2:
            return SerialNumber.format_display(self.serial_number)
        return self.serial_number

    @computed_field
    @property
    def is_standard_format(self) -> bool:
        return self.format_version == 2
```

### 3. API Endpoint

**Endpoint**: `GET /api/v1/serials/parse/{serial_number}`

**Purpose**: Parse and validate serial number (supports both legacy and standard formats)

**Request**:
```http
GET /api/v1/serials/parse/KR01PSA2511001
```

**Response (Standard format)**:
```json
{
  "serial_number": "KR01PSA2511001",
  "formatted": "KR01-PSA-2511-001",
  "valid": true,
  "version": 2,
  "components": {
    "country_code": "KR",
    "line_number": "01",
    "model_code": "PSA",
    "production_month": "2511",
    "sequence": "001"
  },
  "production_date": "2025-11-01T00:00:00"
}
```

---

## Frontend Changes

### New Utility Module

**File**: `frontend/src/utils/serialNumber.ts`

**Key Functions**:
- `formatSerialNumber(serial)`: Auto-detect and format
- `validateSerialNumber(serial)`: Standard validation
- `parseSerialNumber(serial)`: Parse standard components
- `detectSerialVersion(serial)`: Detect version (1, 2, or null)
- `getSerialInfo(serial)`: Complete parsing with metadata

**Usage Example**:
```typescript
import { formatSerialNumber, parseSerialNumber } from '@/utils/serialNumber';

// Auto-format (adds hyphens for standard format)
const formatted = formatSerialNumber("KR01PSA2511001");
// "KR01-PSA-2511-001"

// Parse components
const components = parseSerialNumber("KR01PSA2511001");
// {
//   countryCode: "KR",
//   lineNumber: "01",
//   modelCode: "PSA",
//   productionMonth: "2511",
//   sequence: "001"
// }
```

---

## Implementation Status

### Completed Implementation
- ✅ Create `model_code_mapping` table
- ✅ Add `format_version` column to `serials`
- ✅ Create standard format trigger functions
- ✅ Implement backend utilities
- ✅ Implement frontend utilities
- ✅ Add API endpoint for parsing
- ✅ Activate standard format triggers
- ✅ Test and validate production runs

### Current Operation
- ✅ Standard format is active (format_version=2)
- ✅ Legacy format supported for backward compatibility
- ✅ All new serials use standard format
- ✅ Frontend displays both formats correctly

### Rollback Capability (If Needed)

**Note**: Standard format is now the default. Rollback should only be used in emergency situations.

1. **Deactivate Standard Format Triggers**:
```sql
-- Restore legacy triggers (emergency only)
DROP TRIGGER IF EXISTS trg_generate_serial_number ON serials;
CREATE TRIGGER trg_generate_serial_number
    BEFORE INSERT ON serials
    FOR EACH ROW
    WHEN (NEW.serial_number IS NULL)
    EXECUTE FUNCTION generate_serial_number_legacy();

-- Same for LOT trigger
DROP TRIGGER IF EXISTS trg_generate_lot_number ON lots;
CREATE TRIGGER trg_generate_lot_number
    BEFORE INSERT ON lots
    FOR EACH ROW
    WHEN (NEW.lot_number IS NULL)
    EXECUTE FUNCTION generate_lot_number_legacy();
```

2. **Update Configuration**:
```env
# backend/.env
SERIAL_NUMBER_FORMAT_VERSION=1
```

3. **Monitor and Validate**:
   - Create test LOT
   - Verify serial number generation
   - Check barcode scanning
   - Test label printing

---

## Validation & Testing

### Backend Tests

```python
# Test standard format validation
def test_validate_standard_format():
    assert SerialNumber.validate("KR01PSA2511001") == True
    assert SerialNumber.validate("INVALID") == False

# Test parsing
def test_parse_standard_format():
    components = SerialNumber.parse("KR01PSA2511001")
    assert components["country_code"] == "KR"
    assert components["line_number"] == "01"
    assert components["model_code"] == "PSA"
    assert components["production_month"] == "2511"
    assert components["sequence"] == "001"

# Test formatting
def test_format_display():
    formatted = SerialNumber.format_display("KR01PSA2511001")
    assert formatted == "KR01-PSA-2511-001"
```

### Frontend Tests

```typescript
describe('Serial Number Standard Format', () => {
  it('should validate standard format', () => {
    expect(validateSerialNumber("KR01PSA2511001")).toBe(true);
    expect(validateSerialNumber("INVALID")).toBe(false);
  });

  it('should format serial numbers', () => {
    const formatted = formatSerialNumber("KR01PSA2511001");
    expect(formatted).toBe("KR01-PSA-2511-001");
  });

  it('should parse components', () => {
    const components = parseSerialNumber("KR01PSA2511001");
    expect(components.countryCode).toBe("KR");
    expect(components.lineNumber).toBe("01");
    expect(components.modelCode).toBe("PSA");
  });
});
```

### Manual Testing Checklist

- [x] Create new LOT (standard format - verified)
- [x] Verify LOT number format
- [x] Create serial within LOT
- [x] Verify serial number format
- [x] Test barcode scanning
- [x] Test label printing
- [x] Test serial lookup API
- [x] Test parse API endpoint
- [x] Verify frontend display

---

## FAQs

### Q: Will legacy format serials still work?
**A**: Yes, all existing legacy serials remain valid. The system supports both formats for backward compatibility.

### Q: Do I need to migrate existing serials?
**A**: No, migration is not required. Legacy serials will continue to work indefinitely.

### Q: How do I know which format a serial uses?
**A**: Check the `format_version` field in the database or use the detection functions. Standard format is version 2.

### Q: Can I switch back to legacy format after using standard format?
**A**: Yes, triggers can be swapped in emergency situations. However, standard format serials created will remain standard format.

### Q: What if my line number is > 99?
**A**: The current 2-digit line number supports 00-99. If you need more, extend to 3 digits (requires schema update).

### Q: How does this affect traceability?
**A**: Traceability is fully maintained. Month-level granularity is sufficient for production tracking as confirmed by operations team.

---

## Support & Contact

For questions or issues:
- **Technical**: Check code comments in `backend/app/utils/serial_number.py`
- **Documentation**: This file (`SERIAL_NUMBER_V2_MIGRATION.md`)
- **Testing**: Run test suite for validation

---

**Last Updated**: 2025-11-21 (Corrected all format specifications from 18-char to 14-char)
**Version**: 2.0
**Status**: Implemented and Active
