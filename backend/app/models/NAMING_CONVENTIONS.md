# Database Naming Conventions

## Overview

This document defines the standardized naming conventions for database objects in the F2X NeuroHub MES system. Following these conventions ensures consistency, readability, and maintainability across all database models.

## Index Naming Standards

### 1. Regular Indexes
**Pattern:** `idx_{table}_{columns}`

- Use lowercase table name (without 's' suffix if plural)
- Join multiple columns with underscore
- Keep names concise but descriptive

**Examples:**
```python
Index("idx_lots_status", "status")
Index("idx_lots_production_date", "production_date")
Index("idx_serials_lot_status", "lot_id", "status")
```

### 2. Unique Constraints
**Pattern:** `uk_{table}_{columns}`

- Use for explicit unique constraints (beyond primary keys)
- Follow same column naming rules as indexes

**Examples:**
```python
UniqueConstraint("lot_number", name="uk_lots_lot_number")
UniqueConstraint("serial_number", name="uk_serials_serial_number")
UniqueConstraint("process_number", name="uk_processes_process_number")
```

### 3. Foreign Key Constraints
**Pattern:** `fk_{table}_{ref_table}`

- Use source table name (where FK is defined)
- Use referenced table name (without 's' suffix)
- For multiple FKs to same table, add discriminator

**Examples:**
```python
ForeignKey("lots.id", name="fk_serials_lot")
ForeignKey("users.id", name="fk_audit_logs_user")
ForeignKey("equipment.id", name="fk_process_data_equipment")
```

### 4. Check Constraints
**Pattern:** `chk_{table}_{name}`

- Use descriptive name for the constraint logic
- Keep names short but meaningful

**Examples:**
```python
CheckConstraint("status IN ('CREATED', 'IN_PROGRESS', 'COMPLETED')",
                name="chk_lots_status")
CheckConstraint("rework_count >= 0 AND rework_count <= 3",
                name="chk_serials_rework_count")
CheckConstraint("process_number >= 1 AND process_number <= 10",
                name="chk_processes_process_number")
```

### 5. Composite/Partial Indexes
**Pattern:** `idx_{table}_{purpose}` or `idx_{table}_{columns}_{condition}`

- Use purpose-based naming for complex indexes
- Include condition hint for partial indexes

**Examples:**
```python
# Purpose-based
Index("idx_lots_active", "status", "production_date")
Index("idx_serials_failed", "lot_id", "failure_reason")

# Partial index with condition hint
Index("idx_serials_rework", "rework_count")  # WHERE rework_count > 0
Index("idx_lots_closed", "closed_at")  # WHERE closed_at IS NOT NULL
```

## Rationale for Each Convention

### Why `idx_` prefix?
- Industry standard prefix
- Immediately identifies object type
- Groups indexes together alphabetically
- Avoids naming conflicts with columns

### Why table name without 's'?
- Consistency across singular/plural table names
- Shorter, cleaner names
- Aligns with entity naming (Lot, Serial, Process)

### Why underscore separators?
- PostgreSQL standard (lowercase_underscore)
- Better readability than camelCase
- Consistent with Python naming conventions

### Why explicit constraint names?
- Predictable error messages
- Easier debugging and maintenance
- Platform-independent (works across databases)
- Prevents auto-generated cryptic names

## Refactoring Checklist

When refactoring existing models to follow these conventions:

1. **Audit Current Names**
   - List all existing indexes, constraints
   - Identify non-conforming names
   - Document any special cases

2. **Create Migration Plan**
   - Generate rename migrations
   - Test in development environment
   - Plan for zero-downtime deployment

3. **Update Model Definitions**
   - Update `__table_args__` in each model
   - Ensure all indexes have explicit names
   - Add missing check constraints

4. **Validation Steps**
   - Run schema comparison tools
   - Verify index usage in queries
   - Check constraint enforcement
   - Test error messages

5. **Documentation**
   - Update model docstrings
   - Document any exceptions to conventions
   - Update ERD diagrams if needed

## Common Patterns by Table

### Lots Table
```python
idx_lots_status              # Status queries
idx_lots_production_date     # Date range queries
idx_lots_product_model       # FK index
idx_lots_active              # Active lots (composite)
uk_lots_lot_number           # Unique lot number
chk_lots_status              # Status validation
```

### Serials Table
```python
idx_serials_lot              # FK to lots
idx_serials_status           # Status queries
idx_serials_active           # Active serials
idx_serials_failed           # Failed analysis
uk_serials_serial_number     # Unique serial
chk_serials_rework_count     # Rework limit
```

### Process Data Table
```python
idx_process_data_serial      # FK to serials
idx_process_data_wip         # FK to wip_items
idx_process_data_process     # FK to processes
idx_process_data_timestamp   # Time-based queries
chk_process_data_result      # Result validation
```

## Migration Example

### Before (Non-standard):
```python
Index("lot_status_idx", "status")
Index("SerialLotFK", "lot_id")
CheckConstraint("status = 'VALID'", name="status_check")
```

### After (Standardized):
```python
Index("idx_lots_status", "status")
Index("idx_serials_lot", "lot_id")
CheckConstraint("status IN ('CREATED', 'COMPLETED')",
                name="chk_lots_status")
```

## Exceptions

Some legacy indexes may be retained temporarily for:
- Production database compatibility
- Third-party integration requirements
- Performance-critical queries with proven index names

Document all exceptions in model docstrings with rationale.

## Tools and Validation

### Naming Validation Script
```python
# validate_naming.py
import re

def validate_index_name(name, table):
    pattern = r'^idx_{}_\w+$'.format(table.rstrip('s'))
    return bool(re.match(pattern, name))

def validate_constraint_name(name, table, constraint_type):
    patterns = {
        'unique': r'^uk_{}_\w+$',
        'foreign': r'^fk_{}_\w+$',
        'check': r'^chk_{}_\w+$'
    }
    pattern = patterns[constraint_type].format(table.rstrip('s'))
    return bool(re.match(pattern, name))
```

## References

- PostgreSQL Naming Conventions
- SQLAlchemy 2.0 Best Practices
- Database Index Design Principles
- F2X NeuroHub Architecture Guidelines