# API 마이그레이션 가이드

## 개요

이 문서는 기존 HTTPException을 표준화된 커스텀 예외로 마이그레이션하는 방법을 설명합니다.

## 마이그레이션 패턴

### 1. Import 추가

각 API 파일 상단에 필요한 커스텀 예외를 import합니다:

```python
# 기존
from fastapi import APIRouter, Depends, HTTPException, Query, status

# 추가
from app.core.exceptions import (
    ResourceNotFoundException,
    LotNotFoundException,
    SerialNotFoundException,
    ValidationException,
    InvalidDataFormatException,
    DuplicateResourceException,
    BusinessRuleException,
)
```

### 2. 404 Not Found 에러 변환

**Before:**
```python
obj = crud.get(db, id=id)
if not obj:
    raise HTTPException(
        status_code=404,
        detail=f"Resource with ID {id} not found"
    )
```

**After:**
```python
obj = crud.get(db, id=id)
if not obj:
    raise ResourceNotFoundException("Resource", id)
```

**리소스별 전용 예외:**
- `LotNotFoundException(lot_id)`
- `SerialNotFoundException(serial_id)`
- `ProcessNotFoundException(process_id)`
- `EquipmentNotFoundException(equipment_id)`

### 3. 400 Validation 에러 변환

**Before:**
```python
if not field:
    raise HTTPException(
        status_code=400,
        detail="Field is required"
    )
```

**After:**
```python
if not field:
    raise ValidationException("Field is required")
```

**필드별 상세 에러:**
```python
from app.schemas.error import ErrorDetail

raise ValidationException(
    message="Validation failed",
    details=[
        ErrorDetail(field="field_name", message="Field is required", code="missing")
    ]
)
```

### 4. 409 Conflict 에러 변환

**Before:**
```python
except IntegrityError:
    raise HTTPException(
        status_code=409,
        detail="Resource already exists"
    )
```

**After:**
```python
# IntegrityError는 글로벌 handler가 자동 처리
# 명시적으로 처리하려면:
raise DuplicateResourceException("Resource", "identifier")
```

### 5. 비즈니스 규칙 위반

**Before:**
```python
if not is_valid_sequence(process):
    raise HTTPException(
        status_code=400,
        detail="Invalid process sequence"
    )
```

**After:**
```python
if not is_valid_sequence(process):
    raise BusinessRuleException("Process must be executed in sequence")
```

## 마이그레이션 체크리스트

### 우선순위 높음 (즉시 마이그레이션)
- [x] `backend/app/api/v1/lots.py` - LOT 관리 API
- [x] `backend/app/api/v1/process_data.py` - 공정 데이터 API
- [ ] `backend/app/api/v1/serials.py` - 시리얼 관리 API

### 우선순위 중간 (점진적 마이그레이션)
- [ ] `backend/app/api/v1/product_models.py`
- [ ] `backend/app/api/v1/processes.py`
- [ ] `backend/app/api/v1/equipment.py`
- [ ] `backend/app/api/v1/production_lines.py`

### 우선순위 낮음 (선택적 마이그레이션)
- [ ] `backend/app/api/v1/users.py`
- [ ] `backend/app/api/v1/auth.py`
- [ ] `backend/app/api/v1/audit_logs.py`
- [ ] `backend/app/api/v1/alerts.py`
- [ ] `backend/app/api/v1/analytics.py`
- [ ] `backend/app/api/v1/dashboard.py`

## 마이그레이션 스크립트

빠른 마이그레이션을 위한 검색/치환 패턴:

### 패턴 1: 단순 404 에러
**검색:**
```python
if not \w+:
    raise HTTPException\(
        status_code=404,
        detail=.*
    \)
```

**치환 템플릿:**
```python
if not {obj}:
    raise ResourceNotFoundException("{resource_type}", {id})
```

### 패턴 2: Validation 에러
**검색:**
```python
raise HTTPException\(status_code=400, detail=(.+)\)
```

**치환 템플릿:**
```python
raise ValidationException(\1)
```

## 테스트 방법

### 1. 단위 테스트

기존 테스트는 그대로 동작해야 합니다 (HTTP 상태 코드는 동일):

```python
def test_get_nonexistent_lot(client):
    response = client.get("/api/v1/lots/99999")
    assert response.status_code == 404
    assert response.json()["error_code"] == "RES_002"  # 새로운 필드
```

### 2. curl 테스트

```bash
# 404 Not Found 테스트
curl http://localhost:8000/api/v1/lots/99999 | jq

# 예상 응답:
{
  "error_code": "RES_002",
  "message": "Lot with ID 99999 not found",
  "timestamp": "2025-11-20T...",
  "path": "/api/v1/lots/99999",
  "trace_id": "..."
}

# Validation 에러 테스트
curl -X POST http://localhost:8000/api/v1/lots/ \
  -H "Content-Type: application/json" \
  -d '{}' | jq

# 예상 응답:
{
  "error_code": "VAL_001",
  "message": "Request validation failed",
  "details": [
    {"field": "product_model_id", "message": "Field required", "code": "missing"}
  ],
  ...
}
```

## FAQ

### Q: 기존 HTTPException을 모두 변경해야 하나요?
A: 아니요. 글로벌 exception handler가 HTTPException도 처리하므로 점진적으로 마이그레이션할 수 있습니다. 하지만 표준 포맷의 장점을 활용하려면 커스텀 예외 사용을 권장합니다.

### Q: 새로운 에러 코드를 추가하려면?
A:
1. `backend/app/schemas/error.py`의 `ErrorCode` enum에 추가
2. `backend/app/core/errors.py`의 HTTP 매핑 추가
3. `frontend/src/types/error.ts`의 enum과 메시지 매핑 추가

### Q: 프론트엔드는 어떻게 변경하나요?
A: 프론트엔드는 변경 불필요합니다. API 클라이언트의 인터셉터가 자동으로 표준 에러를 처리합니다.

## 참고 자료

- [backend/app/core/exceptions.py](backend/app/core/exceptions.py) - 커스텀 예외 클래스
- [backend/app/schemas/error.py](backend/app/schemas/error.py) - 에러 스키마
- [frontend/src/types/error.ts](frontend/src/types/error.ts) - 프론트엔드 타입
- [frontend/src/utils/errorHandler.ts](frontend/src/utils/errorHandler.ts) - 에러 핸들링 유틸
