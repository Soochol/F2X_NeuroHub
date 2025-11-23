# JSONB Type Documentation

## Overview

The F2X NeuroHub backend uses custom TypeDecorator classes to provide seamless JSONB support across different database backends (PostgreSQL and SQLite). This ensures consistent JSON storage and retrieval behavior while leveraging database-specific optimizations where available.

## Type Classes

### JSONBType

Base TypeDecorator that automatically selects the appropriate JSON storage type based on the database dialect:
- **PostgreSQL**: Uses native JSONB for efficient binary JSON storage with indexing capabilities
- **SQLite**: Falls back to TEXT-based JSON storage with automatic serialization/deserialization
- **Other databases**: Uses their native JSON type if available

```python
from app.database import JSONBType

class MyModel(Base):
    __tablename__ = 'my_table'
    data: Mapped[Union[dict, list]] = mapped_column(JSONBType, nullable=True)
```

### JSONBDict

Specialized version of JSONBType for dictionary/object storage with built-in validation:
- Ensures values are dictionaries before storage
- Provides better type hints for static analysis
- Raises `TypeError` if non-dict values are provided

```python
from app.database import JSONBDict

class Process(Base):
    __tablename__ = 'processes'
    quality_criteria: Mapped[dict] = mapped_column(JSONBDict, default=dict)
    specifications: Mapped[Optional[dict]] = mapped_column(JSONBDict, nullable=True)
```

### JSONBList

Specialized version of JSONBType for list/array storage with built-in validation:
- Ensures values are lists before storage
- Provides better type hints for static analysis
- Raises `TypeError` if non-list values are provided

```python
from app.database import JSONBList

class ProcessData(Base):
    __tablename__ = 'process_data'
    defects: Mapped[Optional[list]] = mapped_column(JSONBList, nullable=True, default=list)
    measurements: Mapped[list] = mapped_column(JSONBList, default=list)
```

## Migration from Legacy Approach

### Old Approach (Deprecated)
```python
# Previously used function-based type selection
from app.database import JSONB

class MyModel(Base):
    data: Mapped[dict] = mapped_column(JSONB)  # Type checker can't determine exact type
```

### New Approach (Recommended)
```python
# Use specific TypeDecorator classes
from app.database import JSONBDict, JSONBList

class MyModel(Base):
    config: Mapped[dict] = mapped_column(JSONBDict)  # Clear type hints
    items: Mapped[list] = mapped_column(JSONBList)   # Validated list type
```

## Benefits of TypeDecorator Pattern

1. **Type Safety**: Proper type hints work with mypy and IDE type checkers
2. **Runtime Validation**: Catches type mismatches during data binding
3. **Database Agnostic**: Same code works across PostgreSQL and SQLite
4. **Performance**: Leverages PostgreSQL JSONB indexing when available
5. **Cache Friendly**: `cache_ok = True` enables SQLAlchemy statement caching

## Querying JSONB in PostgreSQL

### Basic JSON Operators

```python
from sqlalchemy import func
from app.models import ProcessData

# Access nested JSON field
query = db.query(ProcessData).filter(
    ProcessData.measurements['temperature'].astext.cast(Float) > 100.0
)

# Check if key exists
query = db.query(ProcessData).filter(
    ProcessData.measurements.has_key('temperature')
)

# Array contains element
query = db.query(ProcessData).filter(
    ProcessData.defects.contains(['SCRATCH'])
)

# JSON path query
query = db.query(ProcessData).filter(
    func.jsonb_path_exists(
        ProcessData.measurements,
        '$.sensors[*] ? (@.value > 100)'
    )
)
```

### GIN Index Usage

PostgreSQL automatically uses GIN indexes for JSONB queries when available:

```sql
-- Created by migrations
CREATE INDEX idx_process_data_measurements ON process_data USING GIN (measurements);
CREATE INDEX idx_process_data_defects ON process_data USING GIN (defects);
```

## SQLite JSON Limitations

When using SQLite, be aware of these limitations:

1. **No Native JSONB**: SQLite stores JSON as TEXT with JSON1 extension functions
2. **Limited Operators**: Complex JSON path queries not available
3. **No GIN Indexes**: JSON queries may be slower on large datasets
4. **Type Coercion**: JSON values always returned as Python dict/list

### SQLite JSON Functions

```python
# SQLite JSON functions available via func
from sqlalchemy import func

# Extract JSON value
query = db.query(ProcessData).filter(
    func.json_extract(ProcessData.measurements, '$.temperature') > 100
)

# Get JSON type
query = db.query(
    func.json_type(ProcessData.measurements, '$.temperature')
).all()
```

## Best Practices

1. **Use Specific Types**: Prefer `JSONBDict` or `JSONBList` over generic `JSONBType`
2. **Set Defaults**: Always provide default factory functions (`default=dict` or `default=list`)
3. **Validate Input**: Validate JSON structure before storing complex nested data
4. **Index Strategically**: Create GIN indexes only on frequently queried JSONB columns
5. **Consider Normalization**: For frequently accessed fields, consider normalized columns

## Example: Complete Model Definition

```python
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, JSONBDict, JSONBList

class Equipment(Base):
    __tablename__ = 'equipment'

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_code: Mapped[str] = mapped_column(String(50), unique=True)

    # Dictionary data with JSONBDict
    specifications: Mapped[Optional[dict]] = mapped_column(
        JSONBDict,
        nullable=True,
        default=dict,
        comment="Technical specifications in JSONB format"
    )

    maintenance_schedule: Mapped[dict] = mapped_column(
        JSONBDict,
        nullable=False,
        default=dict,
        comment="Maintenance procedures and schedule"
    )

    # List data with JSONBList
    maintenance_history: Mapped[Optional[list]] = mapped_column(
        JSONBList,
        nullable=True,
        default=list,
        comment="Historical maintenance records"
    )
```

## Testing Considerations

When writing tests, ensure compatibility across databases:

```python
import pytest
from app.database import SessionLocal, JSONBDict
from app.models import ProcessData

def test_jsonb_storage():
    db = SessionLocal()
    try:
        # Create test data
        data = ProcessData(
            measurements={'temp': 100.5, 'pressure': 2.3},
            defects=['SCRATCH', 'DENT']
        )
        db.add(data)
        db.commit()

        # Query and verify
        result = db.query(ProcessData).filter(
            ProcessData.id == data.id
        ).first()

        assert isinstance(result.measurements, dict)
        assert result.measurements['temp'] == 100.5
        assert isinstance(result.defects, list)
        assert 'SCRATCH' in result.defects

    finally:
        db.close()
```

## Troubleshooting

### Common Issues

1. **TypeError on Insert**: Ensure you're passing dict to JSONBDict and list to JSONBList
2. **Query Performance**: Check if GIN indexes exist for frequently queried JSONB columns
3. **Migration Failures**: Ensure both old and new type imports are available during migration
4. **Type Checker Warnings**: Update type hints to use `Mapped[dict]` or `Mapped[list]`

### Debug Logging

Enable SQLAlchemy echo to see generated SQL:

```python
# In settings
DB_ECHO = True  # Shows all SQL statements

# Or programmatically
from app.database import engine
engine.echo = True
```

## References

- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)
- [SQLAlchemy TypeDecorator](https://docs.sqlalchemy.org/en/20/core/custom_types.html#sqlalchemy.types.TypeDecorator)
- [SQLite JSON1 Extension](https://www.sqlite.org/json1.html)
- [SQLAlchemy JSON Type](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.JSON)