# Development Guide

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 13+ (for production)
- SQLite (for testing)
- pip or uv for package management

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd F2X_NeuroHub/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations** (if using Alembic)
   ```bash
   alembic upgrade head
   ```

6. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   │
│   ├── api/                 # API layer
│   │   ├── deps.py         # Shared dependencies
│   │   └── v1/             # API v1 endpoints
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── lots.py
│   │       ├── serials.py
│   │       ├── processes.py
│   │       ├── process_data.py
│   │       ├── product_models.py
│   │       ├── audit_logs.py
│   │       └── analytics.py
│   │
│   ├── core/               # Core functionality
│   │   ├── deps.py        # Dependency injection
│   │   └── security.py    # Authentication & security
│   │
│   ├── crud/              # Database operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lot.py
│   │   ├── serial.py
│   │   ├── process.py
│   │   ├── process_data.py
│   │   ├── product_model.py
│   │   └── audit_log.py
│   │
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lot.py
│   │   ├── serial.py
│   │   ├── process.py
│   │   ├── process_data.py
│   │   ├── product_model.py
│   │   └── audit_log.py
│   │
│   ├── schemas/           # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── lot.py
│   │   ├── serial.py
│   │   ├── process.py
│   │   ├── process_data.py
│   │   ├── product_model.py
│   │   └── audit_log.py
│   │
│   └── database.py        # Database configuration
│
├── tests/                 # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
│
├── docs/                  # Documentation
├── .env.example          # Environment template
├── pytest.ini            # Pytest configuration
├── requirements.txt      # Python dependencies
└── README.md            # Project README
```

## Development Workflow

### 1. Creating a New Feature

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow the layer structure**:
   - Define **Pydantic schemas** in `app/schemas/`
   - Create **SQLAlchemy models** in `app/models/`
   - Implement **CRUD operations** in `app/crud/`
   - Add **API endpoints** in `app/api/v1/`

3. **Write tests**:
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`

4. **Run tests**
   ```bash
   pytest
   ```

5. **Check code quality**
   ```bash
   black .
   isort .
   flake8
   mypy app/
   ```

### 2. Adding a New Model

**Example: Adding a "Department" model**

1. **Create schema** (`app/schemas/department.py`):
   ```python
   from pydantic import BaseModel

   class DepartmentBase(BaseModel):
       name: str
       code: str

   class DepartmentCreate(DepartmentBase):
       pass

   class DepartmentUpdate(DepartmentBase):
       pass

   class DepartmentInDB(DepartmentBase):
       id: int

       class Config:
           from_attributes = True
   ```

2. **Create model** (`app/models/department.py`):
   ```python
   from sqlalchemy import String
   from sqlalchemy.orm import Mapped, mapped_column
   from app.database import Base

   class Department(Base):
       __tablename__ = "departments"

       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str] = mapped_column(String(100))
       code: Mapped[str] = mapped_column(String(20), unique=True)
   ```

3. **Create CRUD** (`app/crud/department.py`):
   ```python
   from sqlalchemy.orm import Session
   from app.models import Department
   from app.schemas import DepartmentCreate, DepartmentUpdate

   def create(db: Session, *, obj_in: DepartmentCreate) -> Department:
       db_obj = Department(**obj_in.model_dump())
       db.add(db_obj)
       db.commit()
       db.refresh(db_obj)
       return db_obj

   def get(db: Session, *, id: int) -> Department | None:
       return db.query(Department).filter(Department.id == id).first()
   ```

4. **Create API endpoint** (`app/api/v1/departments.py`):
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.api import deps
   from app.crud import department as department_crud
   from app.schemas import DepartmentCreate, DepartmentInDB

   router = APIRouter()

   @router.post("/", response_model=DepartmentInDB)
   def create_department(
       *,
       db: Session = Depends(deps.get_db),
       department_in: DepartmentCreate,
   ):
       return department_crud.create(db, obj_in=department_in)
   ```

5. **Register router** in `app/api/v1/__init__.py`:
   ```python
   from app.api.v1 import departments

   api_router.include_router(
       departments.router,
       prefix="/departments",
       tags=["departments"]
   )
   ```

### 3. Writing Tests

**Unit Test Example** (`tests/unit/test_crud_department.py`):
```python
import pytest
from app.crud import department as department_crud
from app.schemas import DepartmentCreate

def test_create_department(db):
    dept_in = DepartmentCreate(name="Engineering", code="ENG")
    dept = department_crud.create(db, obj_in=dept_in)

    assert dept.name == "Engineering"
    assert dept.code == "ENG"
    assert dept.id is not None
```

**Integration Test Example** (`tests/integration/test_api_departments.py`):
```python
def test_create_department_api(client, test_admin_token):
    response = client.post(
        "/api/v1/departments/",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={"name": "Engineering", "code": "ENG"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering"
```

## Code Style

### Python Style Guide

Follow PEP 8 with these tools:

- **Black**: Code formatter (line length: 88)
  ```bash
  black app/ tests/
  ```

- **isort**: Import sorter
  ```bash
  isort app/ tests/
  ```

- **flake8**: Linter
  ```bash
  flake8 app/ tests/
  ```

- **mypy**: Type checker
  ```bash
  mypy app/
  ```

### Type Hints

Always use type hints:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import User

def get_users(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[User]:
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.offset(skip).limit(limit).all()
```

### Naming Conventions

- **Files/Modules**: `snake_case` (e.g., `user_service.py`)
- **Classes**: `PascalCase` (e.g., `UserCreate`)
- **Functions/Variables**: `snake_case` (e.g., `get_user_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_VERSION`)
- **Private**: Prefix with `_` (e.g., `_internal_function`)

## Database Migrations

Using Alembic for database migrations:

1. **Create migration**
   ```bash
   alembic revision --autogenerate -m "Add department table"
   ```

2. **Review migration** in `alembic/versions/`

3. **Apply migration**
   ```bash
   alembic upgrade head
   ```

4. **Rollback**
   ```bash
   alembic downgrade -1
   ```

## Testing Strategy

### Test Coverage Goals

- **Minimum**: 80% coverage
- **Target**: 90% coverage

Run coverage report:
```bash
pytest --cov=app --cov-report=html
```

### Test Categories

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test API endpoints
3. **Database Tests**: Test CRUD operations

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_crud_user.py

# Specific test
pytest tests/unit/test_crud_user.py::test_create_user

# With coverage
pytest --cov=app --cov-report=term-missing

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

## Debugging

### Local Development

1. **Add breakpoint**:
   ```python
   import pdb; pdb.set_trace()
   ```

2. **Use logging**:
   ```python
   import logging

   logger = logging.getLogger(__name__)
   logger.info("Debug message")
   ```

3. **Check database queries**:
   ```python
   from sqlalchemy import event
   from sqlalchemy.engine import Engine

   @event.listens_for(Engine, "before_cursor_execute")
   def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
       print("SQL:", statement)
   ```

### VS Code Configuration

Add to `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload"
      ],
      "jinja": true
    }
  ]
}
```

## Common Tasks

### Add New Dependency

1. Add to `requirements.txt`
2. Install: `pip install -r requirements.txt`
3. Freeze: `pip freeze > requirements.txt`

### Update Database Schema

1. Modify model in `app/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration
4. Apply: `alembic upgrade head`

### Add Authentication to Endpoint

```python
from app.core.deps import get_current_active_user
from app.models import User

@router.get("/protected")
def protected_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.username}"}
```

## Performance Tips

1. **Use database indexes** for frequently queried fields
2. **Lazy load relationships** when appropriate
3. **Use pagination** for large datasets
4. **Cache frequently accessed data**
5. **Profile slow queries** with SQLAlchemy echo

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Validate all input** with Pydantic
4. **Use parameterized queries** (SQLAlchemy does this)
5. **Hash passwords** with bcrypt (cost factor 12)
6. **Use JWT tokens** with reasonable expiration
7. **Implement CORS** properly

## CI/CD Integration

Add to `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Last Updated**: 2025-11-18
