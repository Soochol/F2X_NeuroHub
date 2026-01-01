# API Convention Guide

This document establishes API design conventions for F2X NeuroHub to ensure consistency across Python backends and TypeScript frontends.

## Key Naming Conventions

### Backend (Python)
- Use `snake_case` for all API field names
- Pydantic models should use `snake_case` natively
- Response keys: `batch_id`, `step_index`, `hardware_status`

### Frontend (TypeScript)
- Use `camelCase` in TypeScript code
- Transform API responses from `snake_case` to `camelCase`
- Use `transformKeys()` utility for automatic conversion

---

## ID-Keyed Dictionary Pattern

### Problem
When API returns dictionaries where keys are IDs (not field names), naive snake_case to camelCase conversion breaks lookups.

```typescript
// API Response (from Python)
{ "sensor_inspection": { "total_count": 10 } }

// After naive transformKeys()
{ "sensorInspection": { "totalCount": 10 } }  // WRONG! Key is batch_id, not field

// Looking up by batch.id
statistics.get("sensor_inspection")  // Returns undefined!
```

### Solution
Use `preserveTopLevelKeys: true` for ID-keyed dictionaries:

```typescript
import { transformKeys } from '../utils/transform';

// Correct usage for ID-keyed dictionaries
const statistics = transformKeys<Record<string, BatchStatistics>>(data, {
  preserveTopLevelKeys: true,  // Keep "sensor_inspection" as-is
});

// Result: { "sensor_inspection": { totalCount: 10, passRate: 0.95 } }
```

### Where to Apply

| API Endpoint | Response Type | preserveTopLevelKeys |
|-------------|---------------|---------------------|
| `GET /batches/statistics` | `Record<batch_id, Statistics>` | **true** |
| `GET /batches/{id}` (hardware field) | `Record<hardware_id, Status>` | **true** |
| `GET /batches` | `BatchSummary[]` | false (array) |
| `GET /system/info` | `SystemInfo` | false |

---

## Implementation Guidelines

### 1. Pydantic Schema Consistency

All Pydantic models should follow the same pattern. **Do not mix** `alias_generator=to_camel` with native snake_case.

**Recommended Pattern** (snake_case throughout):
```python
# station_service/api/schemas/batch.py
from pydantic import BaseModel

class BatchStatus(BaseModel):
    batch_id: str
    step_index: int
    current_step: str | None = None
```

**Avoid mixing patterns:**
```python
# DON'T DO THIS - inconsistent with other schemas
class SequenceStep(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)  # Avoid
```

### 2. Frontend Transform Utility

Location: `station_ui/src/utils/transform.ts`

```typescript
export interface TransformKeysOptions {
  /** Preserve top-level keys (for ID-keyed dictionaries) */
  preserveTopLevelKeys?: boolean;
}

export function transformKeys<T>(
  obj: unknown,
  options?: TransformKeysOptions
): T {
  // Implementation handles arrays, objects, primitives
  // Top-level keys preserved when option is set
  // Child objects always get full transformation
}
```

### 3. API Client Interceptor

The global interceptor in `station_ui/src/api/client.ts` transforms all responses. For ID-keyed dictionaries, use `camelToSnake()` to restore keys.

```typescript
// api/endpoints/batches.ts
import { camelToSnake } from '../../utils/transform';

export async function getAllBatchStatistics(): Promise<Record<string, BatchStatistics>> {
  const response = await apiClient.get<ApiResponse<Record<string, BatchStatistics>>>(
    '/batches/statistics'
  );
  const data = extractData(response);

  // Global interceptor already transformed values to camelCase
  // Use camelToSnake() to restore original snake_case keys
  const result: Record<string, BatchStatistics> = {};
  for (const [key, value] of Object.entries(data)) {
    result[camelToSnake(key)] = value;
  }
  return result;
}
```

### 4. Utility Functions

Location: `station_ui/src/utils/transform.ts`

| Function | Purpose | Example |
|----------|---------|---------|
| `snakeToCamel(str)` | API → Frontend | `batch_id` → `batchId` |
| `camelToSnake(str)` | Restore ID keys | `batchId` → `batch_id` |
| `transformKeys(obj, options?)` | Recursive transform | `{ preserveTopLevelKeys: true }` |

---

## Checklist for New Endpoints

When adding new API endpoints:

1. **Backend**
   - [ ] Use snake_case for all field names
   - [ ] Match existing Pydantic schema patterns
   - [ ] Document if response contains ID-keyed dictionaries

2. **Frontend**
   - [ ] Check if response has ID-keyed dictionaries
   - [ ] Apply `preserveTopLevelKeys` where needed
   - [ ] Add TypeScript types that match transformed response

3. **Testing**
   - [ ] Verify key consistency in browser console
   - [ ] Test with IDs containing underscores (e.g., `sensor_inspection`)

---

## Common Patterns

### Batch Statistics (ID-keyed)
```python
# Backend response
{
    "sensor_inspection": {"total_count": 10, "pass_rate": 0.95},
    "health": {"total_count": 5, "pass_rate": 1.0}
}
```

```typescript
// Frontend usage
const stats = await getAllBatchStatistics();
const batchStats = stats["sensor_inspection"];  // Works correctly
```

### Hardware Status (ID-keyed, nested)
```python
# Backend response
{
    "multimeter": {"status": "connected", "last_reading": 5.2},
    "power_supply": {"status": "connected", "voltage": 12.0}
}
```

```typescript
// Frontend: preserve hardware IDs
const hardware = transformKeys<Record<string, HardwareStatus>>(
  response.data.hardware,
  { preserveTopLevelKeys: true }
);
```

---

## Migration Notes

### Existing Code Audit

Files that needed ID-key preservation:
- `station_ui/src/api/endpoints/batches.ts` - `getAllBatchStatistics()` ✅ Fixed
- `frontend/src/api/endpoints/stationApi.ts` - `getBatchStatistics()` ✅ Fixed
- `station_ui/src/api/endpoints/batches.ts` - `getBatch()` hardware field ✅ Fixed

### Breaking Change Prevention

1. Always test with batch IDs containing underscores
2. Check Map/Object lookups match original API keys
3. Add integration tests for ID-keyed responses
