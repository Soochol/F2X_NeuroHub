# F2X NeuroHub MES 구현 가이드

**개발자를 위한 기술 참조 문서**

**Version:** 1.0
**작성일:** 2025.11.10
**대상:** Backend/Frontend 개발자, DevOps 엔지니어

---

## 📋 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [데이터베이스 구현](#2-데이터베이스-구현)
3. [Backend API 구현](#3-backend-api-구현)
4. [Frontend 구현](#4-frontend-구현)
5. [보안 구현](#5-보안-구현)
6. [테스트 구현](#6-테스트-구현)
7. [배포 및 운영](#7-배포-및-운영)

---

## 1. 개발 환경 설정

### 1.1 필수 소프트웨어

```bash
# Python 3.11+
python --version  # Python 3.11.0 이상

# Node.js 18+ (Dashboard용)
node --version    # v18.0.0 이상

# PostgreSQL 15+
psql --version    # PostgreSQL 15.0 이상

# Git
git --version

# Docker & Docker Compose
docker --version
docker-compose --version
```

### 1.2 프로젝트 구조

```
f2x-neurohub-mes/
├── backend/                    # FastAPI Backend
│   ├── alembic/               # DB 마이그레이션
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 앱
│   │   ├── core/              # 핵심 설정
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/            # SQLAlchemy 모델
│   │   │   ├── lot.py
│   │   │   ├── serial.py
│   │   │   └── process.py
│   │   ├── schemas/           # Pydantic 스키마
│   │   │   ├── lot.py
│   │   │   └── process.py
│   │   ├── api/               # API 엔드포인트
│   │   │   ├── v1/
│   │   │   │   ├── lots.py
│   │   │   │   ├── serials.py
│   │   │   │   └── processes.py
│   │   │   └── deps.py        # 의존성
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── lot_service.py
│   │   │   └── process_service.py
│   │   └── utils/             # 유틸리티
│   │       ├── errors.py
│   │       └── validators.py
│   ├── tests/                 # 테스트
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── alembic.ini
│
├── frontend-pc/               # PyQt5 작업 PC 앱
│   ├── main.py
│   ├── ui/
│   │   ├── main_window.py
│   │   └── process_forms/
│   │       ├── spring_input.py
│   │       ├── lma_assembly.py
│   │       └── ...
│   ├── services/
│   │   ├── api_client.py
│   │   └── offline_queue.py
│   └── requirements.txt
│
├── frontend-dashboard/        # React 관리자 대시보드
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Lots.tsx
│   │   │   └── Reports.tsx
│   │   └── utils/
│   ├── package.json
│   └── tsconfig.json
│
├── docker/                    # Docker 설정
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── scripts/                   # 운영 스크립트
│   ├── backup.sh
│   ├── deploy.sh
│   └── init-db.sql
│
├── docs/                      # 문서
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .gitignore
└── README.md
```

### 1.3 로컬 개발 환경 구축

#### 1.3.1 Backend 설정

```bash
# 1. 가상 환경 생성
cd backend
python -m venv venv

# 2. 가상 환경 활성화
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 5. 데이터베이스 마이그레이션
alembic upgrade head

# 6. 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 1.3.2 환경 변수 (.env)

```bash
# .env
# Database
DATABASE_URL=postgresql://mes_user:mes_password@localhost:5432/mes_db

# JWT
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Environment
ENVIRONMENT=development  # development, staging, production

# Logging
LOG_LEVEL=INFO
```

#### 1.3.3 Frontend Dashboard 설정

```bash
cd frontend-dashboard

# 1. 의존성 설치
npm install

# 2. 환경 변수 설정
cp .env.example .env.local
# .env.local 편집

# 3. 개발 서버 실행
npm run dev  # http://localhost:5173
```

#### 1.3.4 Docker Compose로 전체 환경 실행

```bash
# 개발 환경 전체 실행
docker-compose -f docker-compose.dev.yml up

# 서비스:
# - PostgreSQL: localhost:5432
# - Backend API: http://localhost:8000
# - Dashboard: http://localhost:3000
# - pgAdmin: http://localhost:5050
```

**docker-compose.dev.yml:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: mes_user
      POSTGRES_PASSWORD: mes_password
      POSTGRES_DB: mes_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://mes_user:mes_password@postgres:5432/mes_db
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@mes.local
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"

volumes:
  postgres_data:
```

---

## 2. 데이터베이스 구현

### 2.1 전체 DDL 스크립트

```sql
-- scripts/init-db.sql

-- ============================================
-- 1. 공정 마스터
-- ============================================
CREATE TABLE processes (
    id SERIAL PRIMARY KEY,
    process_code VARCHAR(20) UNIQUE NOT NULL,
    process_name VARCHAR(100) NOT NULL,
    sequence_order INTEGER NOT NULL,
    description TEXT,
    standard_cycle_time INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 기본 데이터
INSERT INTO processes (process_code, process_name, sequence_order, standard_cycle_time) VALUES
('SPRING', '스프링 투입', 1, 120),
('LMA', 'LMA 조립', 2, 180),
('LASER', '레이저 마킹', 3, 60),
('EOL', 'EOL 검사', 4, 300),
('ROBOT', '로봇 성능검사', 5, 180),
('PRINT', '프린팅', 6, 60),
('PACK', '포장', 7, 120);

CREATE INDEX idx_processes_sequence ON processes(sequence_order);

-- ============================================
-- 2. 제품 모델 마스터
-- ============================================
CREATE TABLE product_models (
    id SERIAL PRIMARY KEY,
    model_code VARCHAR(50) UNIQUE NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    specification JSONB,
    target_cycle_time INTEGER,
    bom JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 기본 데이터
INSERT INTO product_models (model_code, model_name, specification, target_cycle_time) VALUES
('NH-F2X-001', 'F2X Wearable Robot Standard',
 '{"weight": "2.5kg", "battery": "Li-ion 5000mAh", "color": "Black"}'::jsonb,
 900);

CREATE INDEX idx_product_models_code ON product_models(model_code);

-- ============================================
-- 3. LOT 정보
-- ============================================
CREATE TABLE lots (
    id BIGSERIAL PRIMARY KEY,
    lot_number VARCHAR(50) UNIQUE NOT NULL,

    plant_code VARCHAR(10) NOT NULL,
    product_model_id INTEGER NOT NULL REFERENCES product_models(id),
    shift VARCHAR(1) NOT NULL CHECK (shift IN ('D', 'N')),
    production_date DATE NOT NULL,

    target_quantity INTEGER NOT NULL CHECK (target_quantity > 0),
    actual_quantity INTEGER DEFAULT 0 CHECK (actual_quantity >= 0),
    defect_quantity INTEGER DEFAULT 0 CHECK (defect_quantity >= 0),

    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    priority VARCHAR(20) DEFAULT 'NORMAL',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(50),
    notes TEXT,

    CONSTRAINT check_quantity CHECK (actual_quantity + defect_quantity <= target_quantity)
);

CREATE INDEX idx_lots_lot_number ON lots(lot_number);
CREATE INDEX idx_lots_status ON lots(status);
CREATE INDEX idx_lots_plant_date ON lots(plant_code, production_date);
CREATE INDEX idx_lots_priority ON lots(priority, created_at);
CREATE INDEX idx_lots_created_at ON lots(created_at DESC);

-- ============================================
-- 4. 시리얼 번호
-- ============================================
CREATE TABLE serials (
    id BIGSERIAL PRIMARY KEY,
    serial_number VARCHAR(100) UNIQUE NOT NULL,

    lot_id BIGINT NOT NULL REFERENCES lots(id) ON DELETE CASCADE,
    sequence_in_lot INTEGER NOT NULL,
    checksum VARCHAR(2) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    current_process_id INTEGER REFERENCES processes(id),

    is_defective BOOLEAN DEFAULT FALSE,
    defect_code VARCHAR(50),
    defect_description TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(lot_id, sequence_in_lot)
);

CREATE INDEX idx_serials_serial_number ON serials(serial_number);
CREATE INDEX idx_serials_lot_id ON serials(lot_id);
CREATE INDEX idx_serials_status ON serials(status);
CREATE INDEX idx_serials_created_at ON serials(created_at DESC);
CREATE INDEX idx_serials_defective ON serials(is_defective) WHERE is_defective = TRUE;

-- ============================================
-- 5. 통합 공정 데이터
-- ============================================
CREATE TABLE process_data (
    id BIGSERIAL PRIMARY KEY,

    serial_id BIGINT NOT NULL REFERENCES serials(id),
    process_id INTEGER NOT NULL REFERENCES processes(id),
    work_order INTEGER NOT NULL DEFAULT 1,

    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    cycle_time INTEGER,

    operator_id VARCHAR(50),
    equipment_id VARCHAR(50),

    status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
    is_pass BOOLEAN,

    process_specific_data JSONB,
    inspection_result JSONB,

    defect_code VARCHAR(50),
    defect_description TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_serial_process_order UNIQUE(serial_id, process_id, work_order)
);

CREATE INDEX idx_process_data_serial ON process_data(serial_id);
CREATE INDEX idx_process_data_process ON process_data(process_id);
CREATE INDEX idx_process_data_started ON process_data(started_at DESC);
CREATE INDEX idx_process_data_status ON process_data(status);
CREATE INDEX idx_process_data_operator ON process_data(operator_id);
CREATE INDEX idx_process_data_jsonb_gin ON process_data USING GIN (process_specific_data);

-- ============================================
-- 6. 상태 변경 이력
-- ============================================
CREATE TABLE status_history (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,
    entity_id BIGINT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(50),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT
);

CREATE INDEX idx_status_history_entity ON status_history(entity_type, entity_id);
CREATE INDEX idx_status_history_changed_at ON status_history(changed_at DESC);

-- ============================================
-- 7. 감사 로그
-- ============================================
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id BIGINT NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(50),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX idx_audit_log_changed_by ON audit_log(changed_by);

-- ============================================
-- 8. 사용자 및 권한
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(20) NOT NULL,
    UNIQUE(role, resource, action)
);

-- 기본 권한 설정
INSERT INTO permissions (role, resource, action) VALUES
('OPERATOR', 'PROCESS', 'CREATE'),
('OPERATOR', 'PROCESS', 'READ'),
('SUPERVISOR', 'PROCESS', 'CREATE'),
('SUPERVISOR', 'PROCESS', 'READ'),
('SUPERVISOR', 'PROCESS', 'UPDATE'),
('SUPERVISOR', 'REPORT', 'READ'),
('SUPERVISOR', 'LOT', 'CREATE'),
('SUPERVISOR', 'LOT', 'READ'),
('ADMIN', 'LOT', 'CREATE'),
('ADMIN', 'LOT', 'READ'),
('ADMIN', 'LOT', 'UPDATE'),
('ADMIN', 'LOT', 'DELETE'),
('ADMIN', 'SERIAL', 'CREATE'),
('ADMIN', 'SERIAL', 'READ'),
('ADMIN', 'SERIAL', 'UPDATE'),
('ADMIN', 'SERIAL', 'DELETE'),
('ADMIN', 'USER', 'CREATE'),
('ADMIN', 'USER', 'READ'),
('ADMIN', 'USER', 'UPDATE'),
('ADMIN', 'USER', 'DELETE'),
('ADMIN', 'REPORT', 'READ');

-- ============================================
-- 9. 불량 코드 마스터
-- ============================================
CREATE TABLE defect_codes (
    id SERIAL PRIMARY KEY,
    defect_code VARCHAR(50) UNIQUE NOT NULL,
    defect_name VARCHAR(100) NOT NULL,
    process_id INTEGER REFERENCES processes(id),
    severity VARCHAR(20),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO defect_codes (defect_code, defect_name, process_id, severity) VALUES
('D001', '스프링 불량', 1, 'MAJOR'),
('D002', 'LMA 조립 불량', 2, 'CRITICAL'),
('D003', '마킹 품질 불량', 3, 'MINOR'),
('D004', '온도센서 이상', 4, 'CRITICAL'),
('D005', 'TOF 센서 이상', 4, 'CRITICAL'),
('D006', '펌웨어 업로드 실패', 4, 'CRITICAL'),
('D007', '로봇 동작 불량', 5, 'CRITICAL'),
('D008', '프린팅 불량', 6, 'MINOR');

CREATE INDEX idx_defect_codes_process ON defect_codes(process_id);

-- ============================================
-- 10. 재작업 (Rework)
-- ============================================
CREATE TABLE reworks (
    id BIGSERIAL PRIMARY KEY,
    serial_id BIGINT NOT NULL REFERENCES serials(id),
    original_process_id INTEGER NOT NULL REFERENCES processes(id),
    defect_code VARCHAR(50) NOT NULL,
    rework_reason TEXT,
    rework_started_at TIMESTAMP WITH TIME ZONE,
    rework_completed_at TIMESTAMP WITH TIME ZONE,
    rework_operator VARCHAR(50),
    is_completed BOOLEAN DEFAULT FALSE,
    final_result VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reworks_serial ON reworks(serial_id);
CREATE INDEX idx_reworks_process ON reworks(original_process_id);
CREATE INDEX idx_reworks_completed ON reworks(is_completed);

-- ============================================
-- 11. 에러 로그
-- ============================================
CREATE TABLE error_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_code VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    stack_trace TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(50),
    notes TEXT
);

CREATE INDEX idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX idx_error_logs_severity ON error_logs(severity);
CREATE INDEX idx_error_logs_resolved ON error_logs(resolved) WHERE resolved = FALSE;

-- ============================================
-- 12. 접근 로그
-- ============================================
CREATE TABLE access_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(50),
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    status_code INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_access_logs_user ON access_logs(user_id);
CREATE INDEX idx_access_logs_timestamp ON access_logs(timestamp DESC);

-- ============================================
-- 트리거 함수
-- ============================================

-- 감사 로그 트리거 함수
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, record_id, action, new_data, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW)::jsonb, current_user);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE',
                row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb, current_user);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_data, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD)::jsonb, current_user);
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 상태 변경 이력 트리거 함수
CREATE OR REPLACE FUNCTION status_history_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO status_history (entity_type, entity_id, old_status, new_status, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, OLD.status, NEW.status, current_user);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 적용
CREATE TRIGGER lots_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON lots
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER serials_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON serials
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER lots_status_history_trigger
    AFTER UPDATE ON lots
    FOR EACH ROW EXECUTE FUNCTION status_history_trigger_func();

CREATE TRIGGER serials_status_history_trigger
    AFTER UPDATE ON serials
    FOR EACH ROW EXECUTE FUNCTION status_history_trigger_func();

-- ============================================
-- 뷰 (Views)
-- ============================================

-- 생산 현황 요약 뷰
CREATE OR REPLACE VIEW v_production_summary AS
SELECT
    l.id AS lot_id,
    l.lot_number,
    l.production_date,
    l.shift,
    pm.model_name AS product_model,
    l.target_quantity,
    l.actual_quantity,
    l.defect_quantity,
    ROUND(l.actual_quantity::numeric / NULLIF(l.target_quantity, 0) * 100, 2) AS completion_rate,
    ROUND(l.defect_quantity::numeric / NULLIF(l.actual_quantity, 0) * 100, 2) AS defect_rate,
    l.status,
    l.created_at,
    l.started_at,
    l.completed_at
FROM lots l
JOIN product_models pm ON l.product_model_id = pm.id
ORDER BY l.created_at DESC;

-- 공정별 진행 현황 뷰
CREATE OR REPLACE VIEW v_process_progress AS
SELECT
    p.process_name,
    COUNT(DISTINCT pd.serial_id) AS total_processed,
    COUNT(DISTINCT CASE WHEN pd.is_pass = TRUE THEN pd.serial_id END) AS passed,
    COUNT(DISTINCT CASE WHEN pd.is_pass = FALSE THEN pd.serial_id END) AS failed,
    ROUND(AVG(pd.cycle_time), 2) AS avg_cycle_time,
    MIN(pd.cycle_time) AS min_cycle_time,
    MAX(pd.cycle_time) AS max_cycle_time
FROM process_data pd
JOIN processes p ON pd.process_id = p.id
WHERE pd.started_at >= CURRENT_DATE
GROUP BY p.id, p.process_name
ORDER BY p.sequence_order;
```

### 2.2 Alembic 마이그레이션

```python
# backend/alembic/versions/001_initial.py
"""Initial migration

Revision ID: 001
Create Date: 2025-11-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 여기에 위 DDL 스크립트 내용을 Python 코드로 변환
    # (실제로는 scripts/init-db.sql을 직접 실행하거나,
    #  Alembic으로 테이블 생성 코드 작성)

    # 예시: processes 테이블
    op.create_table(
        'processes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('process_code', sa.String(20), nullable=False),
        sa.Column('process_name', sa.String(100), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('standard_cycle_time', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('process_code')
    )

    # ... (나머지 테이블들)

def downgrade():
    op.drop_table('processes')
    # ... (나머지 테이블들)
```

---

## 3. Backend API 구현

### 3.1 프로젝트 설정

#### 3.1.1 requirements.txt

```txt
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Redis
redis==5.0.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

#### 3.1.2 requirements-dev.txt

```txt
# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Linting & Formatting
black==23.12.1
flake8==7.0.0
mypy==1.8.0
isort==5.13.2

# Development
ipython==8.20.0
```

### 3.2 핵심 모듈 구현

#### 3.2.1 Database 설정 (backend/app/core/database.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """FastAPI dependency for database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### 3.2.2 Config 설정 (backend/app/core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "F2X NeuroHub MES"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 3.2.3 Security (backend/app/core/security.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """JWT 토큰 디코딩"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """현재 사용자 조회 (Dependency)"""
    token = credentials.credentials
    payload = decode_token(token)

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return payload
```

#### 3.2.4 LOT Model (backend/app/models/lot.py)

```python
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, Boolean, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Lot(Base):
    __tablename__ = "lots"

    id = Column(BigInteger, primary_key=True, index=True)
    lot_number = Column(String(50), unique=True, nullable=False, index=True)

    plant_code = Column(String(10), nullable=False)
    product_model_id = Column(Integer, nullable=False)
    shift = Column(String(1), nullable=False)
    production_date = Column(Date, nullable=False)

    target_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, default=0)
    defect_quantity = Column(Integer, default=0)

    status = Column(String(20), nullable=False, default='CREATED', index=True)
    priority = Column(String(20), default='NORMAL')

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_by = Column(String(50))
    notes = Column(Text)

    # Relationships
    serials = relationship("Serial", back_populates="lot", cascade="all, delete-orphan")
```

#### 3.2.5 LOT Schema (backend/app/schemas/lot.py)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime

class LotCreate(BaseModel):
    plant_code: str = Field(..., max_length=10, description="공장 코드")
    product_model_code: str = Field(..., max_length=50, description="제품 모델 코드")
    shift: str = Field(..., pattern=r'^[DN]$', description="교대 (D/N)")
    target_quantity: int = Field(..., gt=0, description="목표 수량")
    priority: str = Field(default="NORMAL", pattern=r'^(URGENT|HIGH|NORMAL|LOW)$')

    @validator('shift')
    def validate_shift(cls, v):
        if v not in ['D', 'N']:
            raise ValueError('교대는 D(주간) 또는 N(야간)만 가능합니다')
        return v

class LotResponse(BaseModel):
    id: int
    lot_number: str
    plant_code: str
    production_date: date
    shift: str
    target_quantity: int
    actual_quantity: int
    defect_quantity: int
    status: str
    priority: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class LotDetail(LotResponse):
    """LOT 상세 정보 (시리얼 포함)"""
    serials: list  # Simplified, 실제로는 SerialResponse 사용
    completion_rate: float
    defect_rate: float

    @validator('completion_rate', always=True)
    def calc_completion_rate(cls, v, values):
        target = values.get('target_quantity', 0)
        actual = values.get('actual_quantity', 0)
        return round(actual / target * 100, 2) if target > 0 else 0.0

    @validator('defect_rate', always=True)
    def calc_defect_rate(cls, v, values):
        actual = values.get('actual_quantity', 0)
        defect = values.get('defect_quantity', 0)
        return round(defect / actual * 100, 2) if actual > 0 else 0.0
```

#### 3.2.6 LOT Service (backend/app/services/lot_service.py)

```python
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.lot import Lot
from app.models.product import ProductModel
from app.schemas.lot import LotCreate

class LotService:
    @staticmethod
    async def generate_lot_number(
        db: AsyncSession,
        plant_code: str,
        shift: str
    ) -> str:
        """LOT 번호 생성"""
        today = date.today().strftime("%Y%m%d")

        # 오늘 해당 공장/교대의 최대 시퀀스 조회
        result = await db.execute(
            select(func.max(Lot.lot_number)).where(
                Lot.plant_code == plant_code,
                Lot.production_date == date.today(),
                Lot.shift == shift
            )
        )
        max_lot = result.scalar()

        if max_lot:
            # 기존 LOT가 있으면 시퀀스 증가
            last_seq = int(max_lot.split('-')[-1])
            new_seq = last_seq + 1
        else:
            # 첫 LOT
            new_seq = 1

        lot_number = f"FN-{plant_code}-{today}-{shift}-{new_seq:06d}"
        return lot_number

    @staticmethod
    async def create_lot(
        db: AsyncSession,
        lot_data: LotCreate,
        current_user: dict
    ) -> Lot:
        """LOT 생성"""
        # 1. 제품 모델 조회
        product = await db.execute(
            select(ProductModel).where(
                ProductModel.model_code == lot_data.product_model_code
            )
        )
        product_model = product.scalar_one_or_none()
        if not product_model:
            raise ValueError(f"제품 모델을 찾을 수 없습니다: {lot_data.product_model_code}")

        # 2. LOT 번호 생성
        lot_number = await LotService.generate_lot_number(
            db, lot_data.plant_code, lot_data.shift
        )

        # 3. LOT 생성
        new_lot = Lot(
            lot_number=lot_number,
            plant_code=lot_data.plant_code,
            product_model_id=product_model.id,
            shift=lot_data.shift,
            production_date=date.today(),
            target_quantity=lot_data.target_quantity,
            priority=lot_data.priority,
            status='CREATED',
            created_by=current_user.get('sub')
        )

        db.add(new_lot)
        await db.commit()
        await db.refresh(new_lot)

        return new_lot

    @staticmethod
    async def get_lot_by_number(
        db: AsyncSession,
        lot_number: str
    ) -> Lot:
        """LOT 번호로 조회"""
        result = await db.execute(
            select(Lot).where(Lot.lot_number == lot_number)
        )
        lot = result.scalar_one_or_none()
        if not lot:
            raise ValueError(f"LOT를 찾을 수 없습니다: {lot_number}")
        return lot
```

#### 3.2.7 LOT API (backend/app/api/v1/lots.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.lot import LotCreate, LotResponse, LotDetail
from app.services.lot_service import LotService

router = APIRouter()

@router.post("/", response_model=LotResponse, status_code=status.HTTP_201_CREATED)
async def create_lot(
    lot_data: LotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    새 LOT 생성

    - **plant_code**: 공장 코드 (예: KR01)
    - **product_model_code**: 제품 모델 코드
    - **shift**: 교대 (D=Day, N=Night)
    - **target_quantity**: 목표 수량
    """
    try:
        lot = await LotService.create_lot(db, lot_data, current_user)
        return lot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{lot_number}", response_model=LotDetail)
async def get_lot(
    lot_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """LOT 상세 조회"""
    try:
        lot = await LotService.get_lot_by_number(db, lot_number)
        return lot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[LotResponse])
async def list_lots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """LOT 목록 조회 (페이지네이션)"""
    # 구현 생략 (LotService에 list_lots 메서드 추가)
    pass
```

#### 3.2.8 Main App (backend/app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import lots, serials, processes, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(lots.router, prefix=f"{settings.API_V1_STR}/lots", tags=["lots"])
app.include_router(serials.router, prefix=f"{settings.API_V1_STR}/serials", tags=["serials"])
app.include_router(processes.router, prefix=f"{settings.API_V1_STR}/processes", tags=["processes"])

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 4. Frontend 구현

### 4.1 PyQt5 작업 PC 앱

#### 4.1.1 메인 윈도우 (frontend-pc/ui/main_window.py)

```python
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from services.api_client import APIClient
from services.offline_queue import OfflineQueue

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.offline_queue = OfflineQueue()

        self.init_ui()
        self.setup_barcode_scanner()
        self.start_queue_processor()

    def init_ui(self):
        self.setWindowTitle("F2X MES - 공정 데이터 입력")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 시리얼 번호 입력
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("시리얼 번호:"))
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("바코드 스캔 또는 직접 입력")
        self.serial_input.returnPressed.connect(self.on_serial_scanned)
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # 공정 선택
        process_layout = QHBoxLayout()
        process_layout.addWidget(QLabel("공정:"))
        self.process_combo = QComboBox()
        self.process_combo.addItems([
            "스프링 투입", "LMA 조립", "레이저 마킹",
            "EOL 검사", "로봇 성능검사", "프린팅", "포장"
        ])
        process_layout.addWidget(self.process_combo)
        layout.addLayout(process_layout)

        # 데이터 입력 영역 (동적 생성)
        self.data_input_widget = QWidget()
        self.data_input_layout = QVBoxLayout()
        self.data_input_widget.setLayout(self.data_input_layout)
        layout.addWidget(self.data_input_widget)

        # 버튼
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("착공")
        self.start_btn.clicked.connect(self.on_start_process)
        self.complete_btn = QPushButton("완공")
        self.complete_btn.clicked.connect(self.on_complete_process)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.complete_btn)
        layout.addLayout(button_layout)

        # 로그
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(QLabel("로그:"))
        layout.addWidget(self.log_text)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_connection_status()

    def setup_barcode_scanner(self):
        """바코드 스캐너 설정 (키보드 입력 감지)"""
        self.barcode_buffer = ""
        self.barcode_timer = QTimer()
        self.barcode_timer.setSingleShot(True)
        self.barcode_timer.timeout.connect(self.reset_barcode_buffer)

    def keyPressEvent(self, event):
        """바코드 스캐너는 빠른 속도로 키 입력"""
        if event.key() == Qt.Key_Return:
            if len(self.barcode_buffer) > 5:  # 바코드로 판단
                self.serial_input.setText(self.barcode_buffer)
                self.on_serial_scanned()
                self.reset_barcode_buffer()
        else:
            self.barcode_buffer += event.text()
            self.barcode_timer.start(100)  # 100ms 후 버퍼 리셋

    def reset_barcode_buffer(self):
        self.barcode_buffer = ""

    def on_serial_scanned(self):
        """시리얼 번호 스캔 처리"""
        serial_number = self.serial_input.text().strip()
        if not serial_number:
            return

        self.log(f"시리얼 번호 스캔: {serial_number}")

        # 시리얼 정보 조회
        try:
            serial_info = self.api_client.get_serial(serial_number)
            self.log(f"현재 공정: {serial_info['current_process']}")
            # 공정 자동 선택
            # self.process_combo.setCurrentText(serial_info['current_process'])
        except Exception as e:
            self.log(f"오류: {str(e)}")
            # 오프라인 모드
            self.log("오프라인 모드로 작업합니다")

    def on_start_process(self):
        """
        공정 착공 (바코드 스캔 → API 호출)

        ✅ 착공 처리 프로세스:
        1. 작업자 바코드 스캔 → operator_id
        2. 제품 시리얼 번호 바코드 스캔 → serial_number
        3. 자동 정보 수집 (process_code, equipment_id, workstation)
        4. Backend API 호출 → 즉시 응답
        5. UI 피드백 표시
        """
        serial_number = self.serial_input.text().strip()
        process = self.process_combo.currentText()

        if not serial_number:
            QMessageBox.warning(self, "경고", "시리얼 번호를 입력하세요")
            return

        # 착공 데이터 구성
        data = {
            "serial_number": serial_number,
            "process_code": self.get_process_code(process),
            "operator_id": self.config.get("operator_id", "OPERATOR01"),  # 실제로는 로그인 정보 또는 바코드 스캔
            "equipment_id": self.config.get("equipment_id"),  # 작업 PC 설정 파일에서 로드 (선택)
            "workstation": self.config.get("workstation")     # 작업 PC 설정 파일에서 로드 (선택)
        }

        try:
            # 동기 API 호출 (즉시 응답)
            result = self.api_client.start_process(data)
            self.log(f"착공 완료: {result['data']}")
            QMessageBox.information(
                self,
                "착공 성공",
                f"공정 착공이 완료되었습니다.\n시리얼: {serial_number}\n시작 시각: {result['data']['started_at']}"
            )
        except Exception as e:
            # 오프라인 큐에 저장
            self.offline_queue.enqueue("/api/v1/process/start", "POST", data)
            self.log(f"오프라인 큐에 저장: {data}")
            QMessageBox.warning(self, "오프라인 모드", "서버 연결 실패. 재연결 시 자동 전송됩니다")

    def on_complete_process(self):
        """공정 완공"""
        # 구현 생략 (on_start_process와 유사)
        pass

    def get_process_code(self, process_name):
        """공정 이름 → 코드 변환"""
        mapping = {
            "스프링 투입": "SPRING",
            "LMA 조립": "LMA",
            "레이저 마킹": "LASER",
            "EOL 검사": "EOL",
            "로봇 성능검사": "ROBOT",
            "프린팅": "PRINT",
            "포장": "PACK"
        }
        return mapping.get(process_name, "UNKNOWN")

    def log(self, message):
        """로그 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def update_connection_status(self):
        """연결 상태 업데이트"""
        try:
            self.api_client.health_check()
            self.status_bar.showMessage("🟢 서버 연결됨", 5000)
        except:
            self.status_bar.showMessage("🔴 서버 연결 끊김 (오프라인 모드)", 5000)

        # 5초마다 체크
        QTimer.singleShot(5000, self.update_connection_status)

    def start_queue_processor(self):
        """오프라인 큐 처리 (백그라운드)"""
        def process_queue():
            self.offline_queue.process_queue(self.api_client)
            # 10초마다 체크
            QTimer.singleShot(10000, process_queue)

        process_queue()
```

#### 4.1.2 API Client (frontend-pc/services/api_client.py)

```python
import requests
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url="http://192.168.1.100:8000/api/v1"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()

    def login(self, username: str, password: str):
        """로그인"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["data"]["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}"
        })

    def health_check(self):
        """헬스 체크"""
        response = self.session.get(f"{self.base_url}/../health", timeout=2)
        response.raise_for_status()

    def get_serial(self, serial_number: str) -> Dict[str, Any]:
        """시리얼 조회"""
        response = self.session.get(f"{self.base_url}/serials/{serial_number}")
        response.raise_for_status()
        return response.json()["data"]

    def start_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """공정 착공"""
        response = self.session.post(f"{self.base_url}/process/start", json=data)
        response.raise_for_status()
        return response.json()["data"]

    def complete_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """공정 완공"""
        response = self.session.post(f"{self.base_url}/process/complete", json=data)
        response.raise_for_status()
        return response.json()["data"]
```

#### 4.1.3 Offline Queue (frontend-pc/services/offline_queue.py)

```python
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class OfflineQueue:
    def __init__(self, db_path="offline_queue.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint VARCHAR(200) NOT NULL,
                method VARCHAR(10) NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                last_error TEXT,
                status VARCHAR(20) DEFAULT 'PENDING'
            )
        """)
        conn.commit()
        conn.close()

    def enqueue(self, endpoint: str, method: str, payload: Dict[str, Any]):
        """큐에 추가"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO queue (endpoint, method, payload)
            VALUES (?, ?, ?)
            """,
            (endpoint, method, json.dumps(payload))
        )
        conn.commit()
        conn.close()

    def process_queue(self, api_client):
        """큐 처리"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT id, endpoint, method, payload
            FROM queue
            WHERE status = 'PENDING' AND retry_count < 5
            ORDER BY created_at
            LIMIT 100
            """
        )

        for row in cursor.fetchall():
            queue_id, endpoint, method, payload = row
            try:
                # 서버로 전송 시도
                if method == "POST":
                    api_client.session.post(
                        f"{api_client.base_url}{endpoint}",
                        json=json.loads(payload)
                    ).raise_for_status()

                # 성공 시 큐에서 제거
                conn.execute("DELETE FROM queue WHERE id = ?", (queue_id,))
            except Exception as e:
                # 실패 시 재시도 카운트 증가
                conn.execute(
                    """
                    UPDATE queue
                    SET retry_count = retry_count + 1,
                        last_error = ?,
                        status = CASE WHEN retry_count >= 4 THEN 'FAILED' ELSE 'PENDING' END
                    WHERE id = ?
                    """,
                    (str(e), queue_id)
                )

        conn.commit()
        conn.close()
```

#### 4.1.4 JSON 파일 모니터링 서비스 (frontend-pc/services/json_file_monitor.py)

**⚠️ 중요: 외부 공정 앱과의 통신 - 완공(COMPLETE) 전용**

이 서비스는 외부 업체가 개발한 공정 앱(7개, 각기 다름)이 생성하는 **완공(COMPLETE) JSON 파일**을 자동으로 감지하고 처리합니다.

**착공 vs 완공 처리 방식:**
- ✅ **착공(START)**: **바코드 스캐너 + UI 직접 입력** (주요 방법, Section 4.1.1 참조)
  - 작업자가 바코드 리더기로 LOT 스캔 → 즉시 UI 피드백
  - JSON 파일 모니터링은 백업 용도로만 사용 가능 (선택사항)
- ✅ **완공(COMPLETE)**: **JSON 파일 모니터링** (이 섹션의 주요 목적)
  - 공정 앱은 수정 불가능 (소스코드 접근 불가)
  - JSON 파일 방식이 유일한 통신 수단
  - 폴더 위치: `C:\F2X\input\complete\`

**설계 근거:**
- 착공 시에는 작업자가 PC 앞에 있어 즉각적인 피드백이 가능하고 필요함
- 완공 시에는 외부 공정 앱이 자동으로 처리하므로 비동기 파일 모니터링이 적합함

```python
import os
import json
import shutil
import time
import msvcrt
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jsonschema import validate, ValidationError
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('json_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JSONFileMonitor:
    """JSON 파일 모니터링 및 처리 서비스"""

    # JSON 스키마 정의
    START_SCHEMA = {
        "type": "object",
        "required": ["serial_number", "process_code", "operator_id", "equipment_id", "timestamp"],
        "properties": {
            "serial_number": {"type": "string", "minLength": 10},
            "process_code": {"type": "string", "enum": ["SPRING", "LMA", "LASER", "EOL", "ROBOT", "PRINT", "PACK"]},
            "operator_id": {"type": "string"},
            "equipment_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"}
        }
    }

    COMPLETE_SCHEMA = {
        "type": "object",
        "required": ["serial_number", "process_code", "operator_id", "is_pass", "timestamp"],
        "properties": {
            "serial_number": {"type": "string", "minLength": 10},
            "process_code": {"type": "string", "enum": ["SPRING", "LMA", "LASER", "EOL", "ROBOT", "PRINT", "PACK"]},
            "operator_id": {"type": "string"},
            "is_pass": {"type": "boolean"},
            "cycle_time": {"type": "number"},
            "process_specific_data": {"type": "object"},
            "inspection_result": {"type": "object"},
            "defect_code": {"type": ["string", "null"]},
            "timestamp": {"type": "string", "format": "date-time"}
        }
    }

    def __init__(self, api_client, offline_queue):
        """
        Args:
            api_client: APIClient 인스턴스
            offline_queue: OfflineQueue 인스턴스
        """
        self.api_client = api_client
        self.offline_queue = offline_queue

        # 폴더 경로 설정
        self.base_path = Path("C:/F2X")
        self.input_start_path = self.base_path / "input" / "start"
        self.input_complete_path = self.base_path / "input" / "complete"
        self.processed_path = self.base_path / "processed"
        self.error_path = self.base_path / "error"

        # 폴더 생성
        self._create_folders()

        # watchdog 설정
        self.observer = Observer()

    def _create_folders(self):
        """필요한 폴더 생성"""
        for path in [self.input_start_path, self.input_complete_path,
                     self.processed_path, self.error_path]:
            path.mkdir(parents=True, exist_ok=True)
        logger.info(f"폴더 구조 생성 완료: {self.base_path}")

    def start(self):
        """파일 모니터링 시작"""

        # [선택사항] start 폴더 모니터링 (백업용)
        # 주의: 착공은 바코드 UI가 주요 방법이며, JSON 모니터링은 백업 용도
        # 필요하지 않다면 이 부분을 주석 처리 가능
        start_handler = JSONFileHandler(
            monitor=self,
            operation_type='START',
            schema=self.START_SCHEMA
        )
        self.observer.schedule(start_handler, str(self.input_start_path), recursive=False)

        # [필수] complete 폴더 모니터링 (주요 기능)
        # 외부 공정 앱이 생성하는 완공 JSON 파일 처리
        complete_handler = JSONFileHandler(
            monitor=self,
            operation_type='COMPLETE',
            schema=self.COMPLETE_SCHEMA
        )
        self.observer.schedule(complete_handler, str(self.input_complete_path), recursive=False)

        self.observer.start()
        logger.info("JSON 파일 모니터링 시작")
        logger.info(f"  - START: {self.input_start_path} (백업용, 선택사항)")
        logger.info(f"  - COMPLETE: {self.input_complete_path} (주요 기능, 필수)")

    def stop(self):
        """파일 모니터링 종료"""
        self.observer.stop()
        self.observer.join()
        logger.info("JSON 파일 모니터링 종료")

    def read_json_file_safe(self, file_path: Path, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        파일을 안전하게 읽기 (파일 락 처리)

        Args:
            file_path: 읽을 파일 경로
            max_retries: 최대 재시도 횟수

        Returns:
            파싱된 JSON 데이터 또는 None (실패 시)
        """
        for attempt in range(max_retries):
            try:
                # 파일이 완전히 쓰여질 때까지 대기 (크기 체크)
                initial_size = file_path.stat().st_size
                time.sleep(0.1)
                current_size = file_path.stat().st_size

                if initial_size != current_size:
                    logger.debug(f"파일 쓰기 진행 중, 대기... ({file_path.name})")
                    time.sleep(0.5)
                    continue

                # 파일 읽기 (Windows 파일 락 고려)
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Windows에서 파일 락 시도
                    if os.name == 'nt':
                        try:
                            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                        except IOError:
                            logger.warning(f"파일 락 획득 실패, 재시도... ({file_path.name})")
                            time.sleep(0.5)
                            continue

                    content = f.read()

                    # 파일 락 해제
                    if os.name == 'nt':
                        try:
                            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                        except:
                            pass

                # JSON 파싱
                data = json.loads(content)
                logger.info(f"파일 읽기 성공: {file_path.name}")
                return data

            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {file_path.name} - {str(e)}")
                return None
            except Exception as e:
                logger.warning(f"파일 읽기 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(0.5)

        logger.error(f"파일 읽기 최종 실패: {file_path.name}")
        return None

    def validate_json(self, data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        JSON 데이터 검증

        Returns:
            (검증 성공 여부, 에러 메시지)
        """
        try:
            validate(instance=data, schema=schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def process_json_file(self, file_path: Path, operation_type: str, schema: Dict[str, Any]):
        """
        JSON 파일 처리 메인 로직

        Args:
            file_path: 처리할 파일 경로
            operation_type: 'START' 또는 'COMPLETE'
            schema: 검증할 JSON 스키마
        """
        logger.info(f"파일 처리 시작: {file_path.name} (타입: {operation_type})")

        try:
            # 1. 파일 읽기
            data = self.read_json_file_safe(file_path)
            if data is None:
                raise Exception("파일 읽기 실패")

            # 2. JSON 스키마 검증
            is_valid, error_msg = self.validate_json(data, schema)
            if not is_valid:
                raise Exception(f"JSON 검증 실패: {error_msg}")

            # 3. 서버로 전송
            endpoint = f"/api/v1/process/{'start' if operation_type == 'START' else 'complete'}"

            try:
                if operation_type == 'START':
                    result = self.api_client.start_process(data)
                else:
                    result = self.api_client.complete_process(data)

                logger.info(f"서버 전송 성공: {data['serial_number']} - {operation_type}")

                # 4. 처리 완료 폴더로 이동
                self.move_to_processed(file_path, operation_type)

            except Exception as e:
                # 서버 연결 실패 → 오프라인 큐에 저장
                logger.warning(f"서버 연결 실패, 오프라인 큐 저장: {str(e)}")
                self.offline_queue.enqueue(endpoint, "POST", data)

                # 처리 완료 폴더로 이동 (큐에 저장됨)
                self.move_to_processed(file_path, operation_type)

        except Exception as e:
            # 파일 처리 오류 → error 폴더로 이동
            logger.error(f"파일 처리 오류: {file_path.name} - {str(e)}")
            self.move_to_error(file_path, operation_type, str(e))

    def move_to_processed(self, file_path: Path, operation_type: str):
        """처리 완료된 파일을 processed 폴더로 이동"""
        try:
            # 타임스탬프 추가하여 중복 방지
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            new_name = f"{operation_type}_{timestamp}_{file_path.name}"
            dest_path = self.processed_path / new_name

            shutil.move(str(file_path), str(dest_path))
            logger.info(f"파일 이동 완료: {file_path.name} → processed/{new_name}")
        except Exception as e:
            logger.error(f"파일 이동 실패: {str(e)}")

    def move_to_error(self, file_path: Path, operation_type: str, error_msg: str):
        """에러 발생한 파일을 error 폴더로 이동"""
        try:
            # 에러 정보 파일 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            new_name = f"{operation_type}_{timestamp}_{file_path.name}"
            dest_path = self.error_path / new_name
            error_info_path = self.error_path / f"{new_name}.error.txt"

            # 원본 파일 이동
            shutil.move(str(file_path), str(dest_path))

            # 에러 정보 저장
            with open(error_info_path, 'w', encoding='utf-8') as f:
                f.write(f"Error Time: {datetime.now().isoformat()}\n")
                f.write(f"Operation Type: {operation_type}\n")
                f.write(f"Original File: {file_path.name}\n")
                f.write(f"Error Message:\n{error_msg}\n")

            logger.info(f"에러 파일 이동: {file_path.name} → error/{new_name}")
        except Exception as e:
            logger.error(f"에러 파일 이동 실패: {str(e)}")


class JSONFileHandler(FileSystemEventHandler):
    """watchdog 파일 이벤트 핸들러"""

    def __init__(self, monitor: JSONFileMonitor, operation_type: str, schema: Dict[str, Any]):
        super().__init__()
        self.monitor = monitor
        self.operation_type = operation_type
        self.schema = schema

    def on_created(self, event):
        """파일 생성 이벤트"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # JSON 파일만 처리
        if file_path.suffix.lower() != '.json':
            logger.debug(f"JSON 파일 아님, 무시: {file_path.name}")
            return

        # 임시 파일 무시 (예: ~로 시작하는 파일)
        if file_path.name.startswith('~') or file_path.name.startswith('.'):
            logger.debug(f"임시 파일 무시: {file_path.name}")
            return

        logger.info(f"새 JSON 파일 감지: {file_path.name} (타입: {self.operation_type})")

        # 파일 처리 (약간의 지연 후 - 파일 쓰기 완료 대기)
        time.sleep(0.2)
        self.monitor.process_json_file(file_path, self.operation_type, self.schema)
```

#### 4.1.5 메인 앱에 JSON 모니터링 통합 (frontend-pc/main.py)

```python
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.api_client import APIClient
from services.offline_queue import OfflineQueue
from services.json_file_monitor import JSONFileMonitor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Frontend App 메인 진입점"""
    app = QApplication(sys.argv)

    # 서비스 초기화
    api_client = APIClient()
    offline_queue = OfflineQueue()

    # JSON 파일 모니터링 시작
    json_monitor = JSONFileMonitor(api_client, offline_queue)
    json_monitor.start()

    logger.info("=== F2X MES Frontend App 시작 ===")
    logger.info("- 착공 방식: 바코드 스캐너 + UI (주요)")
    logger.info("- 완공 방식: JSON 파일 모니터링")
    logger.info("  → 완공 폴더: C:\\F2X\\input\\complete\\ (주요 감시)")
    logger.info("  → 착공 폴더: C:\\F2X\\input\\start\\ (백업용, 선택)")

    # 메인 윈도우 실행
    window = MainWindow()
    window.api_client = api_client
    window.offline_queue = offline_queue
    window.json_monitor = json_monitor
    window.show()

    # 종료 시 모니터링 정리
    exit_code = app.exec_()
    json_monitor.stop()

    logger.info("=== F2X MES Frontend App 종료 ===")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
```

#### 4.1.6 외부 공정 앱 개발 가이드

**외부 업체용 JSON 파일 작성 가이드**

```python
# 외부 공정 앱 예시 코드 (참고용)
# 실제 구현은 각 업체의 개발 환경에 맞게 작성

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path


def write_start_json(serial_number: str, process_code: str, operator_id: str, equipment_id: str):
    """
    공정 착공 JSON 파일 작성

    ⚠️ 중요:
    - 파일 위치: C:\F2X\input\start\
    - 파일명: 자유 (예: {공정}_{timestamp}.json, 또는 임의)
    - 원자적 쓰기: 임시 파일 → rename (파일 락 방지)
    """
    # 1. JSON 데이터 생성
    data = {
        "serial_number": serial_number,
        "process_code": process_code,
        "operator_id": operator_id,
        "equipment_id": equipment_id,
        "timestamp": datetime.now().astimezone().isoformat()
    }

    # 2. 대상 폴더
    target_dir = Path("C:/F2X/input/start")
    target_dir.mkdir(parents=True, exist_ok=True)

    # 3. 임시 파일에 먼저 쓰기 (원자적 쓰기)
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        suffix='.json',
        dir=str(target_dir),
        delete=False
    )

    try:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()

        # 4. 최종 파일명으로 rename
        final_filename = f"{process_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        final_path = target_dir / final_filename

        os.rename(temp_file.name, str(final_path))
        print(f"착공 JSON 파일 생성 완료: {final_path}")

    except Exception as e:
        # 에러 발생 시 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


def write_complete_json(serial_number: str, process_code: str, operator_id: str,
                       is_pass: bool, cycle_time: int, process_data: dict):
    """
    공정 완공 JSON 파일 작성

    ⚠️ 중요:
    - 파일 위치: C:\F2X\input\complete\
    - process_data: 공정별 특화 데이터 (JSON 객체)
    """
    data = {
        "serial_number": serial_number,
        "process_code": process_code,
        "operator_id": operator_id,
        "is_pass": is_pass,
        "cycle_time": cycle_time,
        "process_specific_data": process_data,
        "inspection_result": {},  # 검사 데이터가 있다면 추가
        "defect_code": None if is_pass else "DEFECT_CODE_HERE",
        "timestamp": datetime.now().astimezone().isoformat()
    }

    target_dir = Path("C:/F2X/input/complete")
    target_dir.mkdir(parents=True, exist_ok=True)

    # 임시 파일 → rename (동일한 패턴)
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        suffix='.json',
        dir=str(target_dir),
        delete=False
    )

    try:
        json.dump(data, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()

        final_filename = f"{process_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        final_path = target_dir / final_filename

        os.rename(temp_file.name, str(final_path))
        print(f"완공 JSON 파일 생성 완료: {final_path}")

    except Exception as e:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


# 사용 예시
if __name__ == '__main__':
    # 착공 예시
    write_start_json(
        serial_number="FN-KR-251110D-001-0001",
        process_code="LMA",
        operator_id="W002",
        equipment_id="LMA-STATION-01"
    )

    # 완공 예시
    write_complete_json(
        serial_number="FN-KR-251110D-001-0001",
        process_code="LMA",
        operator_id="W002",
        is_pass=True,
        cycle_time=185,
        process_data={
            "lma_model": "LMA-2024-V2",
            "assembly_complete": True,
            "torque_test": 5.2
        }
    )
```

**외부 업체 체크리스트**

✅ **필수 구현 사항**
- [ ] UTF-8 인코딩으로 JSON 파일 작성
- [ ] 착공: `C:\F2X\input\start\` 폴더에 파일 생성
- [ ] 완공: `C:\F2X\input\complete\` 폴더에 파일 생성
- [ ] 임시 파일 → rename 패턴 사용 (원자적 쓰기)
- [ ] JSON 스키마 준수 (필수 필드 모두 포함)
- [ ] timestamp는 ISO 8601 형식 (timezone 포함)

✅ **권장 사항**
- [ ] 파일명에 공정 코드 포함 (디버깅 용이)
- [ ] 파일명에 타임스탬프 포함 (중복 방지)
- [ ] 에러 발생 시 임시 파일 정리
- [ ] 로컬 로그 파일 작성 (문제 추적용)

### 4.2 React Dashboard (간략)

#### 4.2.1 API Client (frontend-dashboard/src/api/client.ts)

```typescript
import axios, { AxiosInstance } from 'axios';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = 'http://192.168.1.100:8000/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
    });

    // Request interceptor (토큰 추가)
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor (에러 처리)
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // 토큰 만료 → 로그인 페이지로
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username,
      password,
    });
    this.token = response.data.access_token;
    localStorage.setItem('token', this.token!);
    return response;
  }

  async getLots(page: number = 1, pageSize: number = 20) {
    return this.client.get('/lots', {
      params: { page, page_size: pageSize },
    });
  }

  async getDashboardSummary() {
    return this.client.get('/dashboard/summary');
  }
}

export default new APIClient();
```

#### 4.2.2 Dashboard Page (frontend-dashboard/src/pages/Dashboard.tsx)

```typescript
import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { Line } from '@ant-design/charts';
import apiClient from '../api/client';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    loadSummary();
    // 10초마다 갱신
    const interval = setInterval(loadSummary, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadSummary = async () => {
    const data = await apiClient.getDashboardSummary();
    setSummary(data.data);
  };

  if (!summary) return <div>Loading...</div>;

  return (
    <div>
      <h1>생산 현황 대시보드</h1>

      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="금일 LOT 수"
              value={summary.total_lots}
              suffix="개"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="완료율"
              value={summary.completion_rate}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="불량률"
              value={summary.defect_rate}
              suffix="%"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="진행 중"
              value={summary.active_lots}
              suffix="LOT"
            />
          </Card>
        </Col>
      </Row>

      {/* 공정별 차트 등 추가 */}
    </div>
  );
};

export default Dashboard;
```

---

## 5. 보안 구현

(내용은 앞서 작성한 부분과 유사하므로 생략)

---

## 6. 테스트 구현

### 6.1 단위 테스트 예시

```python
# tests/unit/test_lot_service.py
import pytest
from app.services.lot_service import LotService
from app.schemas.lot import LotCreate

@pytest.mark.asyncio
async def test_generate_lot_number(test_db):
    lot_number = await LotService.generate_lot_number(
        test_db, "KR01", "D"
    )
    assert lot_number.startswith("FN-KR01")
    assert "-D-" in lot_number

@pytest.mark.asyncio
async def test_create_lot(test_db, test_user):
    lot_data = LotCreate(
        plant_code="KR01",
        product_model_code="NH-F2X-001",
        shift="D",
        target_quantity=100
    )

    lot = await LotService.create_lot(test_db, lot_data, test_user)

    assert lot.id is not None
    assert lot.lot_number.startswith("FN-KR01")
    assert lot.target_quantity == 100
    assert lot.status == 'CREATED'
```

### 6.2 통합 테스트 예시

```python
# tests/integration/test_process_flow.py
@pytest.mark.asyncio
async def test_complete_process_flow(client, test_db):
    # 1. 로그인
    login_response = await client.post("/api/v1/auth/login", json={
        "username": "operator01",
        "password": "password123"
    })
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. LOT 생성
    lot_response = await client.post("/api/v1/lots", json={
        "plant_code": "KR01",
        "product_model_code": "NH-F2X-001",
        "shift": "D",
        "target_quantity": 10
    }, headers=headers)
    lot_id = lot_response.json()["data"]["id"]

    # 3. 시리얼 생성
    serial_response = await client.post(
        f"/api/v1/lots/{lot_id}/serials/generate",
        json={"quantity": 1},
        headers=headers
    )
    serial_number = serial_response.json()["data"]["serials"][0]

    # 4. 7개 공정 순차 실행
    processes = ["SPRING", "LMA", "LASER", "EOL", "ROBOT", "PRINT", "PACK"]
    for process in processes:
        # 착공
        start_response = await client.post("/api/v1/process/start", json={
            "serial_number": serial_number,
            "process_code": process,
            "operator_id": "operator01"
        }, headers=headers)
        assert start_response.status_code == 201

        # 완공
        process_data_id = start_response.json()["data"]["process_data_id"]
        complete_response = await client.post("/api/v1/process/complete", json={
            "process_data_id": process_data_id,
            "is_pass": True,
            "process_specific_data": {}
        }, headers=headers)
        assert complete_response.status_code == 200

    # 5. 최종 상태 확인
    final_response = await client.get(
        f"/api/v1/serials/{serial_number}",
        headers=headers
    )
    assert final_response.json()["data"]["status"] == "COMPLETED"
```

---

## 7. 배포 및 운영

### 7.1 Docker 배포

```dockerfile
# docker/backend.Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY backend/ .

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (운영 환경)
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 7.2 백업 스크립트

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="mes_db"

echo "=== Backup started at $(date) ==="

# PostgreSQL 백업
pg_dump -h localhost -U mes_user -d $DB_NAME --format=custom \
    --file="$BACKUP_DIR/mes_db_$DATE.dump"

# 압축
gzip "$BACKUP_DIR/mes_db_$DATE.dump"

# 파일 스토리지 백업
tar -czf "$BACKUP_DIR/storage_$DATE.tar.gz" /var/mes/storage/

# 30일 이상 백업 삭제
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "=== Backup completed at $(date) ==="
```

---

**END OF GUIDE**

이 구현 가이드는 실제 개발 시 참고할 수 있는 핵심 코드와 구조를 제공합니다. 더 자세한 내용은 각 기술의 공식 문서를 참조하세요.
