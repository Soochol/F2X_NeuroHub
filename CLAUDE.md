# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

F2X NeuroHub MES (Manufacturing Execution System) - A full-stack application for tracking 8 manufacturing processes in a production line. The system handles LOT and serial number management, process data collection, real-time analytics, and audit logging.

### Manufacturing Processes (8 steps)
1. Laser Marking (레이저 마킹)
2. LMA Assembly (LMA 조립)
3. Sensor Inspection (센서 검사)
4. Firmware Upload (펌웨어 업로드)
5. Robot Assembly (로봇 조립)
6. Performance Testing (성능검사)
7. Label Printing (라벨 프린팅)
8. Packaging + Visual Inspection (포장 + 외관검사)

## Architecture

```
F2X_NeuroHub/
├── backend/              # FastAPI REST API (main MES server)
├── frontend/             # React + Vite dashboard (Ant Design)
├── tablet-scanner/       # React PWA for QR scanning (antd-mobile, Tailwind)
├── neurohub_client/      # PySide6 desktop application
├── station_service/      # FastAPI service for test sequence execution
├── station_ui/           # React UI for station service (Tailwind)
├── sequences/            # Python test sequence definitions
└── database/             # PostgreSQL DDL scripts and views
```

### Backend (FastAPI)
- Entry: `backend/app/main.py`
- API routes: `backend/app/api/v1/` (auth, analytics, lots, serials, process_data, etc.)
- Models: `backend/app/models/` (SQLAlchemy 2.0)
- Schemas: `backend/app/schemas/` (Pydantic v2)
- CRUD: `backend/app/crud/`
- Database: PostgreSQL with SQLAlchemy, Alembic migrations in `backend/alembic/`

### Station Service (Test Sequence Executor)
- Entry: `station_service/main.py`
- Executes test sequences defined in `sequences/`
- IPC communication with hardware via `station_service/ipc/`
- WebSocket for real-time updates
- SQLite for local storage, syncs to backend

### Frontend Applications
All use React + TypeScript + Vite:
- **frontend**: Main dashboard with Ant Design, React Query, Recharts
- **tablet-scanner**: Mobile QR scanner with antd-mobile, Zustand, PWA support
- **station_ui**: Station monitoring with Tailwind, Zustand, socket.io-client

## Development Commands

### Backend
```bash
cd backend
source venv/bin/activate
pip install -e ".[dev]"              # Install with dev dependencies
uvicorn app.main:app --reload        # Dev server on :8000
pytest                               # Run all tests
pytest tests/unit/test_security.py -v  # Run specific test
pytest --cov=app --cov-report=html   # Coverage report
```

### Frontend
```bash
cd frontend
npm install
npm run dev                          # Dev server on :5173
npm run build                        # Build (tsc + vite)
npm run lint                         # ESLint
npm run test                         # Vitest
npm run test:coverage                # Coverage
npm run storybook                    # Storybook on :6006
```

### Tablet Scanner
```bash
cd tablet-scanner
npm install
npm run dev                          # Dev server with SSL (for camera access)
npm run build
npm run lint
```

### Station Service
```bash
cd station_service
python -m station_service.main       # Run directly
uvicorn station_service.main:app --host 0.0.0.0 --port 8080
STATION_CONFIG=/path/to/config.yaml python -m station_service.main
```

### Station UI
```bash
cd station_ui
npm install
npm run dev
npm run build
npm run lint
```

### Docker
```bash
docker-compose up -d                 # Start all services
docker-compose -f docker-compose.dev.yml up -d  # Development mode
docker-compose logs -f backend       # View logs
docker exec -it f2x-postgres psql -U postgres -d f2x_neurohub_mes
```

### Database
```bash
cd backend
alembic upgrade head                 # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

## Key Concepts

### LOT & Serial Tracking
- LOT: Production batch (max 100 units), format: `WF-KR-YYMMDD{D|N}-nnn`
- Serial: Individual unit within a LOT
- Status flow: CREATED → IN_PROGRESS → PASSED/FAILED

### WIP (Work In Progress)
- Tracks items currently being processed
- Links LOT/Serial to current process step

### Process Data
- JSONB fields for flexible `measurements` and `defects`
- Data level: LOT or SERIAL
- Result: PASS, FAIL, or REWORK (max 3 reworks)

### Role-Based Access Control
- ADMIN: Full access including user management and audit logs
- MANAGER: LOT/product management, view all records
- OPERATOR: Process data entry, serial management

## Tech Stack

| Component | Technologies |
|-----------|-------------|
| Backend | FastAPI, SQLAlchemy 2.0, Pydantic v2, PostgreSQL, Alembic |
| Frontend | React 19, Vite 7, Ant Design 5, React Query, Recharts |
| Tablet Scanner | React 19, antd-mobile, Zustand, Tailwind CSS 4, PWA |
| Station Service | FastAPI, SQLite, WebSocket, asyncio |
| Station UI | React 18, Tailwind CSS 3, Zustand, socket.io |
| Desktop Client | PySide6 (Qt) |

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/f2x_neurohub_mes
SECRET_KEY=your-secret-key
DEBUG=True
API_V1_PREFIX=/api/v1
```

### Station Service
```
STATION_CONFIG=/path/to/station.yaml
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## API Documentation
- Backend Swagger: http://localhost:8000/api/v1/docs
- Backend ReDoc: http://localhost:8000/api/v1/redoc
- Station Service: http://localhost:8080/docs

## Testing

### Backend Tests
```bash
cd backend
pytest                               # All tests
pytest -x                            # Stop on first failure
pytest -k "test_auth"               # Run tests matching pattern
pytest tests/integration/ -v         # Integration tests only
```

### Frontend Tests
```bash
cd frontend
npm run test                         # Watch mode
npm run test:coverage               # With coverage
npm run test:e2e                    # Playwright E2E tests
```

## MCP Tools

### Chrome DevTools MCP
An MCP server is connected that allows direct control of the Chrome browser. Use it for the following tasks:
- Taking page snapshots/screenshots
- UI interactions such as clicking, typing, and filling forms
- Checking network requests/console logs
- Performance trace analysis
- E2E testing and debugging

**Key Tools:**
- `take_snapshot`: Page accessibility tree snapshot
- `take_screenshot`: Take screenshots
- `click`, `fill`, `hover`: UI interactions
- `list_network_requests`, `list_console_messages`: Debugging
- `performance_start_trace`: Performance analysis

## SuperClaude Rules
When /sc: commands are detected by hooks, ALWAYS use Skill tool FIRST.
Never attempt to handle these commands directly.

## Code Style

### Python
- Black for formatting (88 char line length)
- isort for import sorting
- Type hints required for function signatures
- Docstrings for public APIs

### TypeScript
- ESLint with React hooks rules
- Strict TypeScript configuration
- Prefer functional components with hooks
