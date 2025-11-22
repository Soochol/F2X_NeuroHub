# API Endpoints Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.f2x-neurohub.com
```

## API Version

Current Version: **v1** (`/api/v1`)

## Authentication

All protected endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔐 Authentication Endpoints

### POST /api/v1/auth/login

User login with credentials.

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200 OK):
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "ADMIN"
  }
}
```

### GET /api/v1/auth/me

Get current authenticated user.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "ADMIN",
  "is_active": true
}
```

### POST /api/v1/auth/refresh

Refresh access token.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### POST /api/v1/auth/logout

Logout current user.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## 👥 User Management

### GET /api/v1/users

List all users with pagination and filters.

**Authentication**: Required (ADMIN, MANAGER)

**Query Parameters**:
- `skip`: int (default: 0)
- `limit`: int (default: 100)
- `role`: UserRole (ADMIN, MANAGER, OPERATOR)
- `is_active`: boolean

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "ADMIN",
    "department": "IT",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### GET /api/v1/users/{user_id}

Get user by ID.

**Authentication**: Required

### POST /api/v1/users

Create new user.

**Authentication**: Required (ADMIN)

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role": "OPERATOR",
  "department": "Production"
}
```

### PUT /api/v1/users/{user_id}

Update user.

**Authentication**: Required (ADMIN)

### DELETE /api/v1/users/{user_id}

Delete user.

**Authentication**: Required (ADMIN)

---

## 📦 Product Models

### GET /api/v1/product-models

List all product models.

**Query Parameters**:
- `skip`: int
- `limit`: int
- `is_active`: boolean

### POST /api/v1/product-models

Create new product model.

**Authentication**: Required (ADMIN, MANAGER)

**Request Body**:
```json
{
  "model_code": "NH-1000",
  "model_name": "NeuroHub Pro",
  "description": "Professional model",
  "bom_data": {},
  "specifications": {},
  "is_active": true
}
```

---

## 📋 Process Management

### GET /api/v1/processes

List all manufacturing processes.

**Response**:
```json
[
  {
    "id": 1,
    "process_number": 1,
    "process_code": "P001",
    "process_name_ko": "검사",
    "process_name_en": "Inspection",
    "description": "Initial inspection",
    "estimated_duration_seconds": 300,
    "is_active": true
  }
]
```

### GET /api/v1/processes/{process_id}

Get process by ID.

---

## 🏭 Lot Management

### GET /api/v1/lots

List all lots with filters.

**Query Parameters**:
- `skip`: int
- `limit`: int
- `status`: LotStatus (CREATED, IN_PROGRESS, COMPLETED, CANCELLED)
- `product_model_id`: int

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "lot_number": "KR01PSA2511001",
    "product_model_id": 1,
    "target_quantity": 100,
    "status": "CREATED",
    "created_at": "2025-11-21T00:00:00Z"
  }
]
```

### POST /api/v1/lots

Create new lot.

**Request Body**:
```json
{
  "lot_number": "KR01PSA2511001",
  "product_model_id": 1,
  "target_quantity": 100,
  "shift": "D"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "lot_number": "KR01PSA2511001",
  "product_model_id": 1,
  "target_quantity": 100,
  "status": "CREATED",
  "created_at": "2025-11-21T00:00:00Z"
}
```

### GET /api/v1/lots/{lot_id}

Get lot details with related data.

**Response** (200 OK):
```json
{
  "id": 1,
  "lot_number": "KR01PSA2511001",
  "product_model_id": 1,
  "target_quantity": 100,
  "status": "IN_PROGRESS",
  "wip_items_count": 50,
  "serials_count": 30,
  "created_at": "2025-11-21T00:00:00Z"
}
```

### POST /api/v1/lots/{lot_id}/start-wip-generation

Start WIP generation for a lot (공정 1 시작).

**Authentication**: Required (MANAGER, OPERATOR)

**Request Body**:
```json
{
  "operator_id": 1,
  "equipment_id": "LASER-001"
}
```

**Response** (200 OK):
```json
{
  "message": "WIP generation started",
  "lot_id": 1,
  "lot_number": "KR01PSA2511001",
  "target_quantity": 100
}
```

**Business Logic**:
- LOT 상태가 CREATED일 때만 가능
- 공정 1(레이저 마킹) 착공 가능 상태로 변경
- LOT 상태 자동 변경: CREATED → IN_PROGRESS

---

## 🔧 WIP Management (Work In Progress)

### Overview

**WIP ID 개념**: LOT 생성 후 공정 1에서 생성되는 작업 중인 제품 식별자

**WIP 생명 주기**:
```
LOT 생성 → WIP 생성 (공정 1) → 공정 2~6 작업 → Serial 전환 (공정 7) → 공정 8 완료
```

**WIP ID 포맷**: `WIP-{LOT}-{SEQ:03d}`
- 예: `WIP-KR01PSA251101-001` (LOT KR01PSA251101의 첫 번째 WIP)

### POST /api/v1/wip-items

Create WIP item (공정 1에서 자동 생성).

**Authentication**: Required (OPERATOR)

**Request Body**:
```json
{
  "lot_id": 1,
  "operator_id": 1,
  "equipment_id": "LASER-001"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "wip_id": "KR01PSA2511001-W0001",
  "lot_id": 1,
  "sequence_in_lot": 1,
  "status": "CREATED",
  "created_at": "2025-11-21T09:00:00Z"
}
```

### GET /api/v1/wip-items

List WIP items with filters.

**Query Parameters**:
- `lot_id`: int - Filter by LOT
- `status`: WipStatus (CREATED, IN_PROGRESS, COMPLETED, CONVERTED)
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "wip_id": "KR01PSA2511001-W0001",
    "lot_id": 1,
    "sequence_in_lot": 1,
    "status": "IN_PROGRESS",
    "current_process": 3,
    "created_at": "2025-11-21T09:00:00Z"
  }
]
```

### GET /api/v1/wip-items/{wip_id}

Get WIP item details with process history.

**Response** (200 OK):
```json
{
  "id": 1,
  "wip_id": "KR01PSA2511001-W0001",
  "lot_id": 1,
  "lot_number": "KR01PSA2511001",
  "sequence_in_lot": 1,
  "status": "IN_PROGRESS",
  "current_process": 3,
  "process_history": [
    {
      "process_id": 1,
      "process_name": "레이저 마킹",
      "result": "PASS",
      "started_at": "2025-11-21T09:00:00Z",
      "completed_at": "2025-11-21T09:01:00Z"
    },
    {
      "process_id": 2,
      "process_name": "LMA 조립",
      "result": "PASS",
      "started_at": "2025-11-21T09:05:00Z",
      "completed_at": "2025-11-21T10:05:00Z"
    }
  ],
  "created_at": "2025-11-21T09:00:00Z"
}
```

### POST /api/v1/wip-items/{wip_id}/scan

Scan WIP barcode (공정 2~6 진입 시).

**Authentication**: Required (OPERATOR)

**Request Body**:
```json
{
  "process_id": 2,
  "operator_id": 1
}
```

**Response** (200 OK):
```json
{
  "wip_id": "KR01PSA2511001-W0001",
  "lot_number": "KR01PSA2511001",
  "current_status": "IN_PROGRESS",
  "next_process": {
    "id": 2,
    "name": "LMA 조립",
    "can_start": true
  }
}
```

**Error Responses**:
- `404 WIP_NOT_FOUND`: WIP ID가 존재하지 않음
- `400 PREVIOUS_PROCESS_NOT_COMPLETED`: 이전 공정 미완료
- `409 ALREADY_CONVERTED`: 이미 Serial로 전환됨

### POST /api/v1/wip-items/{wip_id}/start-process

Start process for WIP (공정 착공).

**Authentication**: Required (OPERATOR)

**Request Body**:
```json
{
  "process_id": 2,
  "operator_id": 1,
  "equipment_id": "EQ-002",
  "line_id": "LINE-A"
}
```

**Response** (201 Created):
```json
{
  "id": 123,
  "wip_id": "KR01PSA2511001-W0001",
  "process_id": 2,
  "process_name": "LMA 조립",
  "started_at": "2025-11-21T09:05:00Z",
  "operator_id": 1,
  "equipment_id": "EQ-002"
}
```

### POST /api/v1/wip-items/{wip_id}/complete-process

Complete process for WIP (공정 완공).

**Authentication**: Required (OPERATOR)

**Request Body**:
```json
{
  "process_id": 2,
  "result": "PASS",
  "process_data": {
    "notes": "조립 완료",
    "quality_check": true
  }
}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "wip_id": "KR01PSA2511001-W0001",
  "process_id": 2,
  "result": "PASS",
  "completed_at": "2025-11-21T10:05:00Z",
  "next_process": {
    "id": 3,
    "name": "센서 검사",
    "can_start": true
  }
}
```

**Result Values**:
- `PASS`: 합격
- `FAIL`: 불합격
- `REWORK`: 재작업

### POST /api/v1/wip-items/{wip_id}/convert-to-serial

Convert WIP to Serial (공정 7 라벨 프린팅 시).

**Authentication**: Required (OPERATOR)

**Request Body**:
```json
{
  "operator_id": 1,
  "printer_id": "ZEBRA-001"
}
```

**Response** (200 OK):
```json
{
  "wip_id": "KR01PSA2511001-W0001",
  "serial_number": "KR01PSA25110010001",
  "serial_id": 1,
  "label_printed": true,
  "converted_at": "2025-11-21T11:00:00Z"
}
```

**Business Logic**:
- 공정 1~6이 모두 PASS 완료되어야 함
- WIP 상태 자동 변경: IN_PROGRESS → CONVERTED
- Serial Number 자동 생성 및 할당
- 바코드 라벨 자동 출력

**Error Responses**:
- `400 PROCESSES_NOT_COMPLETED`: 공정 1~6 미완료
- `409 ALREADY_CONVERTED`: 이미 Serial로 전환됨
- `503 PRINTER_NOT_AVAILABLE`: 프린터 사용 불가

---

## 🔢 Serial Management

### GET /api/v1/serials

List all serials.

**Query Parameters**:
- `lot_id`: int
- `status`: SerialStatus
- `skip`: int
- `limit`: int

### POST /api/v1/serials

Create new serial.

**Request Body**:
```json
{
  "serial_number": "SN-2025-001-001",
  "lot_id": 1,
  "sequence_in_lot": 1
}
```

---

## 📊 Process Data

### GET /api/v1/process-data

List process execution records.

**Query Parameters**:
- `lot_id`: int
- `serial_id`: int
- `process_id`: int
- `data_level`: DataLevel (LOT, SERIAL)

### POST /api/v1/process-data

Record process execution data.

**Request Body**:
```json
{
  "lot_id": 1,
  "serial_id": 1,
  "process_id": 1,
  "operator_id": 1,
  "data_level": "SERIAL",
  "measurement_data": {
    "temperature": 25.5,
    "humidity": 60
  },
  "result": "PASS"
}
```

---

## 🏭 Process Operations

### POST /api/v1/process-operations/start

Start a process (착공) for a lot or serial.

**Authentication**: Required

**Request Body**:
```json
{
  "lot_number": "KR01PSA2511001",
  "serial_number": "KR01PSA25110010001",
  "process_id": "1",
  "worker_id": "OP001",
  "equipment_id": "LASER-001",
  "line_id": "LINE-A"
}
```

**Parameters**:

- `lot_number` (required): LOT number
- `serial_number` (optional): Serial number (required for processes 7-8)
- `process_id` (required): Process ID to start
- `worker_id` (required): Worker/Operator ID
- `equipment_id` (optional): Equipment code (e.g., "LASER-001") - saved to process_data.equipment_id
- `line_id` (optional): Production line code (e.g., "LINE-A") - assigns to lots.production_line_id on first process start

**Business Rules**:

- On first process start (착공), the `line_id` is assigned to `lots.production_line_id`
- `equipment_id` is resolved to the equipment table's ID and saved to `process_data.equipment_id`
- Previous process must be PASS before starting next process (Trigger BR-002)
- Serial status automatically updates based on process result (Trigger BR-003)

**Response** (201 Created):
```json
{
  "id": 1,
  "lot_id": 1,
  "serial_id": 1,
  "process_id": 1,
  "line_id": "LINE-A",
  "equipment_id": 1,
  "worker_id": "OP001",
  "start_time": "2025-11-10T09:00:00Z",
  "complete_time": null,
  "result": null,
  "is_rework": false
}
```

### POST /api/v1/process-operations/complete

Complete a process (완공) with result.

**Authentication**: Required

**Request Body**:
```json
{
  "process_data_id": 1,
  "result": "PASS",
  "process_specific_data": {
    "temp_sensor": {"measured_value": 60.5, "result": "PASS"},
    "tof_sensor": {"measured_distance": 195.2, "result": "PASS"}
  }
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "result": "PASS",
  "complete_time": "2025-11-10T09:05:00Z"
}
```

---

## 📈 Analytics

### GET /api/v1/analytics/overview

Get production overview metrics.

**Authentication**: Required

**Response**:
```json
{
  "total_lots": 100,
  "active_lots": 25,
  "total_serials": 5000,
  "passed_serials": 4850,
  "failed_serials": 150,
  "pass_rate": 97.0
}
```

### GET /api/v1/analytics/process-efficiency

Get process efficiency metrics.

### GET /api/v1/analytics/quality-metrics

Get quality control metrics.

---

## 📝 Audit Logs

### GET /api/v1/audit-logs

List audit log entries.

**Authentication**: Required (ADMIN)

**Query Parameters**:
- `user_id`: int
- `entity_type`: string
- `action`: AuditAction (CREATE, UPDATE, DELETE)
- `start_date`: datetime
- `end_date`: datetime

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. This may be added in future versions.

## Versioning

The API uses URL-based versioning. Current version is `v1`.

Future versions will be accessible via `/api/v2`, etc.

---

**Last Updated**: 2025-11-20
