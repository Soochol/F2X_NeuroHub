# F2X NeuroHub MES - Backend API

## Project Overview

F2X NeuroHub Manufacturing Execution System (MES) backend API built with FastAPI, providing comprehensive tracking and management for 8 manufacturing processes.

### Manufacturing Processes
1. **레이저 마킹** (Laser Marking) - Process 1
2. **LMA 조립** (LMA Assembly) - Process 2
3. **센서 검사** (Sensor Inspection) - Process 3
4. **펌웨어 업로드** (Firmware Upload) - Process 4
5. **로봇 조립** (Robot Assembly) - Process 5
6. **성능검사** (Performance Testing) - Process 6
7. **라벨 프린팅** (Label Printing) - Process 7
8. **포장 + 외관검사** (Packaging + Visual Inspection) - Process 8

### Key Features
- JWT-based authentication with role-based access control (RBAC)
- LOT and serial number tracking (max 100 units per LOT)
- Flexible process data collection with JSONB fields
- Immutable audit trail with automatic logging
- Real-time analytics and dashboard metrics
- Comprehensive quality tracking with rework support (max 3 reworks)
- RESTful API with automatic OpenAPI documentation

## Technology Stack

### Core Framework
- **FastAPI 0.104.1** - Modern async Python web framework
- **Uvicorn 0.24.0** - ASGI server with WebSocket support
- **Python 3.11+** - Programming language

### Database
- **PostgreSQL 14+** - Primary database
- **SQLAlchemy 2.0.23** - ORM with new syntax (mapped_column, Mapped[type])
- **psycopg2-binary 2.9.9** - PostgreSQL adapter

### Security & Authentication
- **python-jose 3.3.0** - JWT encoding/decoding
- **passlib 1.7.4** - Password hashing (bcrypt)
- **python-multipart** - OAuth2 form data support

### Validation & Serialization
- **Pydantic 2.5.2** - Data validation with ConfigDict
- **email-validator** - Email validation support

## API Endpoints Summary

**Total: 80+ endpoints across 9 router groups**

- **Authentication**: 5 endpoints (login, me, refresh, logout)
- **Analytics**: 6 endpoints (dashboard, production stats, process performance, quality metrics, operator performance, realtime status)
- **Product Models**: 8 endpoints (CRUD + search variants)
- **Processes**: 8 endpoints (CRUD + search variants)
- **Users**: 8 endpoints (CRUD + role filtering, ADMIN only)
- **LOTs**: 10 endpoints (CRUD + status tracking, date filtering)
- **Serials**: 10 endpoints (CRUD + rework management)
- **Process Data**: 9 endpoints (CRUD + multi-level filtering)
- **Audit Logs**: 7 endpoints (read-only, ADMIN only)

## Development Setup

### Prerequisites

- Python 3.11+
- **Docker & Docker Compose** (Recommended - easiest setup)
- OR PostgreSQL 14+ (if not using Docker)
- pip or uv package manager

### 🐳 Quick Start with Docker (Recommended)

**1. Start PostgreSQL Database**

```bash
# From project root (F2X_NeuroHub/)
docker-compose up -d

# Wait for initialization (~30 seconds)
# Check logs for "✅ Database Initialization Completed Successfully!"
docker-compose logs -f postgres
```

This automatically:
- ✅ Starts PostgreSQL 14 + pgAdmin
- ✅ Creates database `f2x_neurohub_mes`
- ✅ Deploys full schema (14 functions, 7 tables, 50+ indexes, 20+ triggers)
- ✅ Creates initial users (system, admin, operator1)
- ✅ Sets up audit log partitions

**2. Setup Python Environment**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

**3. Configure Environment**

```bash
# Copy template
cp .env.example .env

# .env is already configured for Docker!
# DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes
```

**Optional: Generate Strong Secret Key**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Update SECRET_KEY in .env
```

**4. Load Test Data (Optional)**

```bash
# From project root
docker exec -it f2x-postgres psql -U postgres -d f2x_neurohub_mes -f /sql/test_data.sql
```

This loads:
- 3 product models (PSA-1000, PSA-2000, PSA-3000)
- 5 LOTs with various statuses
- 50+ serials
- 100+ process records

**5. Start API Server**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**6. Access Services**

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Docs (Swagger)** | http://localhost:8000/docs | - |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | - |
| **pgAdmin** | http://localhost:5050 | admin@f2x.com / admin123 |
| **PostgreSQL** | localhost:5432 | postgres / postgres123 |

**7. Test Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 💻 Manual Setup (Without Docker)

1. **Install PostgreSQL 14+**

2. **Create database**
   ```bash
   createdb -U postgres f2x_neurohub_mes
   ```

3. **Deploy schema**
   ```bash
   psql -U postgres -d f2x_neurohub_mes -f ../database/deploy.sql
   ```

4. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and update DATABASE_URL if needed
   ```

7. **Run development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Security & Authentication

### Role-Based Access Control (RBAC)

**Role Hierarchy**: ADMIN > MANAGER > OPERATOR

| Role | Permissions |
|------|-------------|
| **OPERATOR** | Create/update process data, serials. View own records. |
| **MANAGER** | OPERATOR + Create/update LOTs, product models, processes. View all records. |
| **ADMIN** | MANAGER + User management, delete operations, audit logs access. |

### Authentication Flow

1. POST to `/api/v1/auth/login` with username/password
2. Receive JWT access token (expires in 30 minutes)
3. Include token in header: `Authorization: Bearer <token>`
4. Refresh token before expiration if needed

### Password Security

- **Hashing**: bcrypt with cost factor 12
- **Validation**: Minimum 8 characters, must contain uppercase, lowercase, and digit
- **Storage**: Only password_hash stored in database
- **API Response**: password_hash never returned in responses

## API Usage Examples

### 1. Authentication

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin123"

# Response: {"access_token": "eyJhbG...", "token_type": "bearer"}

# Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <token>"
```

### 2. Create Product Model (MANAGER+)

```bash
curl -X POST "http://localhost:8000/api/v1/product-models" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_code": "NH-2024-A1",
    "model_name": "NeuroHub Standard",
    "category": "Standard",
    "specifications": {
      "sensor_type": "IMU",
      "battery_capacity": "2000mAh",
      "wireless": "BLE 5.0"
    }
  }'
```

### 3. Create LOT (MANAGER+)

```bash
curl -X POST "http://localhost:8000/api/v1/lots" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "lot_number": "WF-KR-241118D-001",
    "product_model_id": 1,
    "target_quantity": 100,
    "shift": "DAY",
    "manager_id": 2
  }'
```

### 4. Create Serial (OPERATOR+)

```bash
curl -X POST "http://localhost:8000/api/v1/serials" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "serial_number": "SN-241118-001",
    "lot_id": 1,
    "sequence_in_lot": 1
  }'
```

### 5. Record Process Data (OPERATOR+)

```bash
curl -X POST "http://localhost:8000/api/v1/process-data" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "process_id": 1,
    "serial_id": 1,
    "lot_id": 1,
    "data_level": "SERIAL",
    "result": "PASS",
    "measurements": {
      "marking_quality": "A",
      "marking_depth": "0.05mm",
      "position_x": "10.2",
      "position_y": "20.5"
    },
    "operator_id": 3,
    "process_order": 1,
    "cycle_time_seconds": 45
  }'
```

### 6. Get Dashboard Analytics

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "lot_statistics": {
    "total_lots": 150,
    "lots_today": 5,
    "lots_this_week": 23,
    "active_lots": 8
  },
  "serial_statistics": {
    "total_serials": 14523,
    "serials_today": 487,
    "in_progress": 156,
    "passed": 13890,
    "failed": 477
  },
  "quality_metrics": {
    "overall_pass_rate": 95.6,
    "defect_rate": 3.3,
    "rework_rate": 1.1
  },
  "process_performance": {
    "total_executions": 115000,
    "avg_cycle_time_seconds": 42.5,
    "total_failures": 3800
  }
}
```

### 7. Get Process Performance

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/process-performance" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "processes": [
    {
      "process_id": 1,
      "process_code": "P01_LASER_MARKING",
      "process_name": "레이저 마킹",
      "total_executions": 14500,
      "success_count": 13920,
      "failure_count": 580,
      "avg_cycle_time_seconds": 45.2,
      "success_rate": 96.0
    }
    // ... 7 more processes
  ]
}
```

### 8. Get Quality Metrics

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/quality-metrics?days=7" \
  -H "Authorization: Bearer <token>"
```

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/f2x_neurohub_mes
DB_ECHO=False

# Security
SECRET_KEY=your-secret-key-min-32-characters-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=F2X NeuroHub MES API
APP_VERSION=1.0.0
DEBUG=True
API_V1_PREFIX=/api/v1

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

### Production Configuration

For production deployment:

1. **Generate secure SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Update .env for production**
   ```env
   SECRET_KEY=<generated-secure-key>
   DEBUG=False
   DATABASE_URL=postgresql://user:password@db-host:5432/database?sslmode=require
   CORS_ORIGINS=["https://your-production-domain.com"]
   ```

3. **Run with production server**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Legacy dependency wrapper
│   │   └── v1/
│   │       ├── __init__.py         # Router exports
│   │       ├── auth.py             # Authentication endpoints (5)
│   │       ├── analytics.py        # Dashboard metrics (6)
│   │       ├── product_models.py   # Product management (8)
│   │       ├── processes.py        # Process definitions (8)
│   │       ├── users.py            # User management (8)
│   │       ├── lots.py             # LOT tracking (10)
│   │       ├── serials.py          # Serial tracking (10)
│   │       ├── process_data.py     # Process execution (9)
│   │       └── audit_logs.py       # Audit logs (7, read-only)
│   ├── core/
│   │   ├── deps.py                 # Dependency injection
│   │   └── security.py             # JWT & password hashing
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── product_model.py        # ProductModel CRUD
│   │   ├── process.py              # Process CRUD
│   │   ├── user.py                 # User CRUD with auth
│   │   ├── lot.py                  # LOT CRUD
│   │   ├── serial.py               # Serial CRUD
│   │   ├── process_data.py         # ProcessData CRUD
│   │   └── audit_log.py            # AuditLog read-only
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product_model.py        # ProductModel ORM
│   │   ├── process.py              # Process ORM
│   │   ├── user.py                 # User ORM with UserRole
│   │   ├── lot.py                  # Lot ORM with LotStatus
│   │   ├── serial.py               # Serial ORM with SerialStatus
│   │   ├── process_data.py         # ProcessData ORM
│   │   └── audit_log.py            # AuditLog ORM (partitioned)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── product_model.py        # 4 schemas
│   │   ├── process.py              # 4 schemas
│   │   ├── user.py                 # 5 schemas (includes UserLogin)
│   │   ├── lot.py                  # 4 schemas + LotStatus + Shift
│   │   ├── serial.py               # 4 schemas + SerialStatus
│   │   ├── process_data.py         # 4 schemas + DataLevel + ProcessResult
│   │   └── audit_log.py            # 2 schemas + AuditAction
│   ├── config.py                   # Settings (Pydantic BaseSettings)
│   ├── database.py                 # SQLAlchemy session management
│   └── main.py                     # FastAPI application entry point
├── requirements.txt                # Production dependencies
└── README.md                       # This file
```

## Database Schema

### 7 Main Tables

1. **product_models** - Product definitions
   - Primary Key: id (serial)
   - Unique: model_code (VARCHAR 50)
   - JSONB: specifications (GIN indexed)
   - Soft delete: deleted_at (timestamp)

2. **processes** - 8 manufacturing processes
   - Primary Key: id (serial)
   - Unique: process_number (1-8), process_code
   - JSONB: quality_criteria
   - Constraint: CHECK (process_number BETWEEN 1 AND 8)

3. **users** - Authentication and RBAC
   - Primary Key: id (serial)
   - Unique: username (VARCHAR 50)
   - Enum: role (ADMIN, MANAGER, OPERATOR)
   - Password: password_hash (bcrypt)

4. **lots** - Production batches (max 100 units)
   - Primary Key: id (serial)
   - Unique: lot_number (WF-KR-YYMMDD{D|N}-nnn)
   - Status: CREATED → IN_PROGRESS → COMPLETED → CLOSED
   - Foreign Keys: product_model_id, manager_id

5. **serials** - Individual units
   - Primary Key: id (serial)
   - Unique: serial_number
   - Status: CREATED → IN_PROGRESS → PASSED/FAILED
   - Constraint: rework_count (0-3)
   - Foreign Keys: lot_id

6. **process_data** - Process execution records
   - Primary Key: id (serial)
   - JSONB: measurements, defects (GIN indexed)
   - Enums: data_level (LOT/SERIAL), result (PASS/FAIL/REWORK)
   - Foreign Keys: process_id, lot_id, serial_id, operator_id

7. **audit_logs** - Immutable audit trail (partitioned by month)
   - Primary Key: id (bigserial), recorded_at (timestamp)
   - JSONB: old_values, new_values
   - Partitioned: RANGE (recorded_at)
   - Immutable: No UPDATE/DELETE allowed

### Relationships

```
product_models (1) ----< (N) lots
lots (1) ----< (N) serials
lots (N) >---- (1) users (manager)
processes (1) ----< (N) process_data
lots (1) ----< (N) process_data
serials (1) ----< (N) process_data
users (1) ----< (N) process_data (operator)
```

## Performance Optimization

### Database Indexing

All critical queries are optimized with indexes:
- `product_models.model_code` - UNIQUE index
- `product_models.specifications` - GIN index (JSONB)
- `users.username` - UNIQUE index
- `lots.lot_number` - UNIQUE index
- `serials.serial_number` - UNIQUE index
- `process_data.measurements`, `process_data.defects` - GIN indexes

### Query Optimization

- Use `skip`/`limit` pagination for large result sets
- Analytics endpoints use database-level aggregations (SQLAlchemy `func`)
- Eager loading for relationships with `joinedload()`

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before use
    pool_size=10,            # Maintain 10 connections
    max_overflow=20,         # Allow 20 additional connections
)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Coverage Goals

- Unit tests: 90%+ coverage
- Integration tests: All API endpoints
- Security tests: Authentication and authorization
- Performance tests: Database queries under 100ms

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
Solution: Verify PostgreSQL is running and DATABASE_URL is correct

**2. Authentication Failed**
```
401 Unauthorized: Could not validate credentials
```
Solution: Check token expiration, verify SECRET_KEY matches

**3. Import Error**
```
ModuleNotFoundError: No module named 'app'
```
Solution: Run from backend directory, ensure virtual environment is activated

**4. CORS Error in Browser**
```
Access to fetch blocked by CORS policy
```
Solution: Add frontend URL to CORS_ORIGINS in .env

## Next Steps

### Phase 2.10: Code Review & Testing (Pending)
- [ ] Unit tests for all CRUD modules
- [ ] Integration tests for API endpoints
- [ ] Security testing (authentication, authorization)
- [ ] Load testing with realistic data volumes
- [ ] Code quality review with pylint/mypy

### Phase 3: Frontend Development (Future)
- [ ] Vite + React + TypeScript setup
- [ ] Dashboard UI with analytics charts
- [ ] 8 process data entry forms
- [ ] Real-time monitoring with WebSocket
- [ ] UI/UX polish and responsive design
- [ ] Frontend testing (Jest, React Testing Library)

### Additional Enhancements
- [ ] WebSocket support for real-time updates
- [ ] Export functionality (PDF reports, Excel)
- [ ] Email notifications for critical events
- [ ] Advanced analytics (ML-based quality prediction)
- [ ] Mobile app integration
- [ ] Multi-language support (i18n)

## Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Documentation Files
- **[API Endpoints](docs/api/API_ENDPOINTS.md)** - Complete API reference
- **[Development Guide](docs/guides/DEVELOPMENT.md)** - Development workflow and best practices
- **[Deployment Guide](docs/guides/DEPLOYMENT.md)** - Production deployment instructions
- **[Test Plan](docs/testing/TEST_PLAN.md)** - Testing strategy and coverage
- **[Test Report](docs/testing/BACKEND_TEST_COMPLETION_REPORT.md)** - Latest test results
- **Database Schema**: [../database/README.md](../database/README.md)

## Support

For issues and questions, please refer to the project documentation or contact the development team.

---

**Version**: 1.0.0
**Status**: ✅ Backend Complete (80+ endpoints, JWT auth, Analytics)
**Generated**: 2024-11-18
