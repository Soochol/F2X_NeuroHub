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

### POST /api/v1/lots

Create new lot.

**Request Body**:
```json
{
  "lot_number": "LOT-2025-001",
  "product_model_id": 1,
  "target_quantity": 50,
  "work_order": "WO-2025-001"
}
```

### GET /api/v1/lots/{lot_id}

Get lot details with related data.

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

**Last Updated**: 2025-11-18
