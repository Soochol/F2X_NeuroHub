# 8.2 통합 테스트 가이드

[← 목차로 돌아가기](../README.md)

---

## 목차

- [8.2.1 통합 테스트 개요](#821-통합-테스트-개요)
- [8.2.2 테스트 환경 구성](#822-테스트-환경-구성)
- [8.2.3 데이터베이스 통합 테스트](#823-데이터베이스-통합-테스트)
- [8.2.4 API 통합 테스트](#824-api-통합-테스트)
- [8.2.5 File Watcher 통합 테스트](#825-file-watcher-통합-테스트)
- [8.2.6 외부 시스템 통합 테스트](#826-외부-시스템-통합-테스트)
- [8.2.7 End-to-End 테스트](#827-end-to-end-테스트)
- [8.2.8 CI/CD 파이프라인 통합](#828-cicd-파이프라인-통합)

---

## 8.2.1 통합 테스트 개요

### 목적

개별 컴포넌트 간의 상호작용을 검증하고, 시스템 전체가 요구사항대로 동작하는지 확인합니다.

### 테스트 범위

| 통합 레벨 | 테스트 대상 | 예시 |
|----------|-----------|------|
| **Component 통합** | 모듈 간 연동 | Service ↔ Repository |
| **API 통합** | 엔드포인트 ↔ Database | REST API ↔ PostgreSQL |
| **System 통합** | 외부 시스템 연동 | File Watcher ↔ 외부 앱 |
| **End-to-End** | 전체 워크플로우 | LOT 생성 → 착공 → 완공 |

### 테스트 전략

**원칙:**
- 실제 데이터베이스 사용 (In-memory DB 지양)
- 외부 의존성은 Mock/Stub 사용
- 테스트 데이터 격리 (트랜잭션 롤백)
- CI/CD 파이프라인에서 자동 실행

---

## 8.2.2 테스트 환경 구성

### 테스트 데이터베이스 설정

**Docker Compose로 테스트 DB 구성:**

```yaml
# tests/docker-compose.test.yml
version: '3.8'
services:
  postgres-test:
    image: postgres:15-alpine
    container_name: mes-test-db
    environment:
      POSTGRES_DB: mes_test
      POSTGRES_USER: mes_user
      POSTGRES_PASSWORD: test1234
    ports:
      - "5433:5432"  # 프로덕션 DB와 포트 분리
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    tmpfs:
      - /var/lib/postgresql/data  # 메모리 기반 저장소 (빠른 테스트)

  redis-test:
    image: redis:7-alpine
    container_name: mes-test-redis
    ports:
      - "6380:6379"
```

**테스트 DB 시작:**

```bash
# 테스트 DB 시작
docker-compose -f tests/docker-compose.test.yml up -d

# 테스트 실행
pytest tests/integration/

# 테스트 DB 종료
docker-compose -f tests/docker-compose.test.yml down
```

### pytest 설정

**pytest.ini:**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# 테스트 마커
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests

# 환경 변수
env =
    DATABASE_URL=postgresql+asyncpg://mes_user:test1234@localhost:5433/mes_test
    REDIS_URL=redis://localhost:6380/0
    ENVIRONMENT=test
```

### conftest.py (공통 Fixture)

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 생성 (전체 세션에서 재사용)"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """테스트 DB 엔진 생성"""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine):
    """트랜잭션 기반 DB 세션 (각 테스트마다 롤백)"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # 테스트 후 자동 롤백


@pytest.fixture
async def test_client(db_session):
    """FastAPI TestClient"""
    from httpx import AsyncClient
    from app.main import app
    from app.api.dependencies import get_db

    # DB 의존성 오버라이드
    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

---

## 8.2.3 데이터베이스 통합 테스트

### 테스트 시나리오: LOT 생성 및 상태 전이

```python
# tests/integration/test_lot_lifecycle.py
import pytest
from app.models.lot import Lot
from app.models.serial import Serial
from app.services.lot_service import LotService

@pytest.mark.integration
async def test_lot_creation_and_status_transition(db_session):
    """LOT 생성 및 상태 전이 테스트"""
    service = LotService(db_session)

    # 1. LOT 생성
    lot = await service.create_lot(
        product_model_id=1,
        target_quantity=100,
        shift="D"
    )

    assert lot.status == "CREATED"
    assert lot.lot_number.startswith("WF-KR-")

    # 2. 시리얼 생성 시 LOT 상태 변경 (CREATED → IN_PROGRESS)
    serial = Serial(
        serial_number=f"{lot.lot_number}-0001",
        lot_id=lot.id,
        sequence=1,
        status="CREATED"
    )
    db_session.add(serial)
    await db_session.commit()
    await db_session.refresh(lot)

    assert lot.status == "IN_PROGRESS"  # 트리거에 의해 자동 변경

    # 3. 모든 시리얼 완료 시 LOT 상태 변경 (IN_PROGRESS → COMPLETED)
    serial.status = "PASSED"
    await db_session.commit()

    # LOT 완료 처리
    await service.complete_lot(lot.id)
    await db_session.refresh(lot)

    assert lot.status == "COMPLETED"
    assert lot.completed_at is not None
```

### 테스트 시나리오: 공정 순서 제어

```python
# tests/integration/test_process_sequence.py
import pytest
from app.models.process_data import ProcessData
from app.services.process_service import ProcessService
from app.exceptions import ProcessSequenceError

@pytest.mark.integration
async def test_process_sequence_validation(db_session):
    """공정 순서 제어 검증"""
    service = ProcessService(db_session)

    # 사전 준비: LOT 및 시리얼 생성
    lot = await create_test_lot(db_session)
    serial = await create_test_serial(db_session, lot.id)

    # 1. 첫 번째 공정(라벨 프린팅) 착공 - 성공
    process_data_1 = await service.start_process(
        lot_id=lot.id,
        serial_id=serial.id,
        process_id=1,  # 라벨 프린팅
        worker_id="W001"
    )
    assert process_data_1 is not None

    # 2. 두 번째 공정(조립) 착공 시도 - 실패 (이전 공정 미완료)
    with pytest.raises(ProcessSequenceError) as exc:
        await service.start_process(
            lot_id=lot.id,
            serial_id=serial.id,
            process_id=2,  # 조립
            worker_id="W002"
        )
    assert "PREVIOUS_PROCESS_NOT_COMPLETED" in str(exc.value)

    # 3. 첫 번째 공정 완공 (PASS)
    await service.complete_process(
        process_data_id=process_data_1.id,
        result="PASS",
        measured_data={"temp": 60.5}
    )

    # 4. 두 번째 공정 착공 - 성공 (이전 공정 PASS 완료)
    process_data_2 = await service.start_process(
        lot_id=lot.id,
        serial_id=serial.id,
        process_id=2,
        worker_id="W002"
    )
    assert process_data_2 is not None
```

### 데이터베이스 제약조건 테스트

```python
# tests/integration/test_database_constraints.py
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.serial import Serial

@pytest.mark.integration
async def test_serial_unique_constraint(db_session):
    """시리얼 번호 중복 방지 제약조건 테스트"""
    lot = await create_test_lot(db_session)

    # 첫 번째 시리얼 생성
    serial1 = Serial(
        serial_number="WF-KR-251115D-001-0001",
        lot_id=lot.id,
        sequence=1,
        status="CREATED"
    )
    db_session.add(serial1)
    await db_session.commit()

    # 중복 시리얼 생성 시도
    serial2 = Serial(
        serial_number="WF-KR-251115D-001-0001",  # 중복
        lot_id=lot.id,
        sequence=2,
        status="CREATED"
    )
    db_session.add(serial2)

    with pytest.raises(IntegrityError):
        await db_session.commit()
```

---

## 8.2.4 API 통합 테스트

### 테스트 시나리오: 착공 API

```python
# tests/integration/test_api_start_process.py
import pytest

@pytest.mark.integration
async def test_start_process_api_success(test_client, db_session):
    """착공 API 성공 케이스"""
    # 사전 준비
    lot = await create_test_lot(db_session)

    # 착공 API 호출
    response = await test_client.post(
        "/api/v1/process/start",
        json={
            "lot_number": lot.lot_number,
            "line_id": "LINE-A",
            "process_id": "PROC-001",
            "worker_id": "W001"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    # 검증
    assert response.status_code == 201
    data = response.json()
    assert data["lot_number"] == lot.lot_number
    assert data["process_id"] == "PROC-001"
    assert "start_time" in data


@pytest.mark.integration
async def test_start_process_api_sequence_error(test_client, db_session):
    """공정 순서 위반 시 에러 응답"""
    lot = await create_test_lot(db_session)
    serial = await create_test_serial(db_session, lot.id)

    # 두 번째 공정 착공 시도 (첫 번째 공정 미완료)
    response = await test_client.post(
        "/api/v1/process/start",
        json={
            "lot_number": lot.lot_number,
            "line_id": "LINE-A",
            "process_id": "PROC-002",  # 두 번째 공정
            "worker_id": "W001"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    # 검증
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "PREVIOUS_PROCESS_NOT_COMPLETED"
```

### 테스트 시나리오: 대시보드 API

```python
# tests/integration/test_api_dashboard.py
import pytest

@pytest.mark.integration
async def test_dashboard_summary(test_client, db_session):
    """대시보드 요약 API 테스트"""
    # 테스트 데이터 생성
    lot1 = await create_test_lot(db_session, status="IN_PROGRESS")
    lot2 = await create_test_lot(db_session, status="COMPLETED")
    await create_test_process_data(db_session, lot1.id, result="PASS", count=30)
    await create_test_process_data(db_session, lot1.id, result="FAIL", count=2)

    # 대시보드 API 호출
    response = await test_client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": "Bearer test_token"}
    )

    # 검증
    assert response.status_code == 200
    data = response.json()
    assert data["total_lots"] == 2
    assert data["in_progress_lots"] == 1
    assert data["completed_lots"] == 1
    assert data["pass_count"] == 30
    assert data["fail_count"] == 2
    assert data["defect_rate"] == pytest.approx(6.25)  # 2 / 32 * 100
```

---

## 8.2.5 File Watcher 통합 테스트

### 테스트 시나리오: JSON 파일 처리

```python
# tests/integration/test_file_watcher.py
import pytest
import json
import os
import asyncio
from pathlib import Path

@pytest.mark.integration
async def test_file_watcher_json_processing(db_session, tmp_path):
    """File Watcher JSON 파일 처리 테스트"""
    # 임시 폴더 생성
    pending_dir = tmp_path / "pending"
    completed_dir = tmp_path / "completed"
    pending_dir.mkdir()
    completed_dir.mkdir()

    # 테스트 데이터 준비
    lot = await create_test_lot(db_session)
    serial = await create_test_serial(db_session, lot.id)

    # JSON 파일 생성
    json_data = {
        "schema_version": "1.0",
        "serial_number": serial.serial_number,
        "process_id": "PROC-002",
        "result": "PASS",
        "measured_data": {
            "온도": 60.5,
            "변위": 198.3,
            "힘": 15.2
        },
        "timestamp": "2025-11-15T14:30:00Z"
    }

    json_file = pending_dir / f"{serial.serial_number}_PROC-002.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False)

    # File Watcher 시작
    from app.services.file_watcher import FileWatcher
    watcher = FileWatcher(
        pending_dir=str(pending_dir),
        completed_dir=str(completed_dir),
        db_session=db_session
    )

    # 파일 처리 대기
    await asyncio.sleep(2)  # File Watcher 감지 시간

    # 검증
    # 1. JSON 파일이 completed 폴더로 이동
    assert not json_file.exists()
    assert (completed_dir / json_file.name).exists()

    # 2. 데이터베이스에 완공 데이터 저장
    from app.models.process_data import ProcessData
    result = await db_session.execute(
        select(ProcessData).where(
            ProcessData.serial_id == serial.id,
            ProcessData.process_id == 2
        )
    )
    process_data = result.scalar_one()

    assert process_data.result == "PASS"
    assert process_data.process_specific_data["온도"] == 60.5


@pytest.mark.integration
async def test_file_watcher_error_handling(db_session, tmp_path):
    """File Watcher 에러 처리 테스트"""
    pending_dir = tmp_path / "pending"
    error_dir = tmp_path / "error"
    pending_dir.mkdir()
    error_dir.mkdir()

    # 잘못된 JSON 파일 생성 (필수 필드 누락)
    invalid_json = {
        "schema_version": "1.0",
        # serial_number 누락
        "process_id": "PROC-002",
        "result": "PASS"
    }

    json_file = pending_dir / "invalid.json"
    with open(json_file, "w") as f:
        json.dump(invalid_json, f)

    # File Watcher 처리
    watcher = FileWatcher(
        pending_dir=str(pending_dir),
        completed_dir=str(tmp_path / "completed"),
        error_dir=str(error_dir),
        db_session=db_session
    )

    await asyncio.sleep(2)

    # 검증: 에러 파일이 error 폴더로 이동
    assert not json_file.exists()
    assert (error_dir / json_file.name).exists()
```

---

## 8.2.6 외부 시스템 통합 테스트

### Zebra 프린터 Mock 테스트

```python
# tests/integration/test_printer_integration.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.integration
async def test_label_printing_integration(db_session):
    """라벨 프린터 통합 테스트 (Mock)"""
    lot = await create_test_lot(db_session)

    # Zebra 프린터 Mock
    with patch("app.services.printer.ZebraPrinter.print_label") as mock_print:
        mock_print.return_value = {"status": "success", "job_id": "12345"}

        # 라벨 출력 서비스 호출
        from app.services.printer import PrinterService
        printer_service = PrinterService()

        result = await printer_service.print_lot_label(
            lot_number=lot.lot_number,
            product_model="NH-F2X-001",
            shift="D"
        )

        # 검증
        assert result["status"] == "success"
        mock_print.assert_called_once()

        # 호출된 ZPL 명령어 확인
        call_args = mock_print.call_args[0][0]
        assert lot.lot_number in call_args  # ZPL에 LOT 번호 포함 확인
```

### Circuit Breaker 통합 테스트

```python
# tests/integration/test_circuit_breaker.py
import pytest
from circuitbreaker import CircuitBreakerError
from app.utils.circuit_breaker import upload_firmware_to_device

@pytest.mark.integration
async def test_circuit_breaker_opens_after_failures():
    """Circuit Breaker 장애 후 Open 상태 전환 테스트"""
    # 5회 연속 실패 시뮬레이션
    for i in range(5):
        with pytest.raises(Exception):
            await upload_firmware_to_device("TEST-SERIAL", "/invalid/path")

    # 6번째 요청은 즉시 CircuitBreakerError 발생
    with pytest.raises(CircuitBreakerError):
        await upload_firmware_to_device("TEST-SERIAL", "/invalid/path")
```

---

## 8.2.7 End-to-End 테스트

### 전체 워크플로우 테스트

```python
# tests/e2e/test_lot_complete_workflow.py
import pytest

@pytest.mark.e2e
async def test_complete_lot_workflow(test_client, db_session):
    """LOT 생성부터 완료까지 전체 워크플로우 테스트"""

    # 1. LOT 생성
    create_response = await test_client.post(
        "/api/v1/lots",
        json={
            "product_model_id": 1,
            "target_quantity": 100,
            "shift": "D"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert create_response.status_code == 201
    lot_number = create_response.json()["lot_number"]

    # 2. 첫 번째 공정 착공 (라벨 프린팅)
    start_response = await test_client.post(
        "/api/v1/process/start",
        json={
            "lot_number": lot_number,
            "line_id": "LINE-A",
            "process_id": "PROC-001",
            "worker_id": "W001"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert start_response.status_code == 201
    serial_number = start_response.json()["serial_number"]

    # 3. 첫 번째 공정 완공 (File Watcher 시뮬레이션)
    # (실제로는 JSON 파일 생성하여 처리)

    # 4. 두 번째 공정 착공 (조립)
    start_2_response = await test_client.post(
        "/api/v1/process/start",
        json={
            "lot_number": lot_number,
            "line_id": "LINE-A",
            "process_id": "PROC-002",
            "worker_id": "W002"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert start_2_response.status_code == 201

    # 5. ... 8개 공정 모두 반복

    # 6. LOT 상세 조회
    lot_detail_response = await test_client.get(
        f"/api/v1/lots/{lot_number}",
        headers={"Authorization": "Bearer test_token"}
    )
    assert lot_detail_response.status_code == 200
    lot_data = lot_detail_response.json()
    assert lot_data["status"] == "COMPLETED"

    # 7. 시리얼 추적 조회
    trace_response = await test_client.get(
        f"/api/v1/serials/{serial_number}/trace",
        headers={"Authorization": "Bearer test_token"}
    )
    assert trace_response.status_code == 200
    trace_data = trace_response.json()
    assert len(trace_data["processes"]) == 8  # 8개 공정 이력 존재
```

---

## 8.2.8 CI/CD 파이프라인 통합

### GitHub Actions 설정

```yaml
# .github/workflows/integration-test.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  integration-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: mes_test
          POSTGRES_USER: mes_user
          POSTGRES_PASSWORD: test1234
        ports:
          - 5433:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6380:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run database migrations
        env:
          DATABASE_URL: postgresql+asyncpg://mes_user:test1234@localhost:5433/mes_test
        run: |
          alembic upgrade head

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql+asyncpg://mes_user:test1234@localhost:5433/mes_test
          REDIS_URL: redis://localhost:6380/0
          ENVIRONMENT: test
        run: |
          pytest tests/integration/ -v --cov=app --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: integration
          name: integration-coverage
```

### 테스트 커버리지 설정

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False

fail_under = 80  # 최소 커버리지 80%
```

### Pre-commit Hook 설정

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: integration-tests
        name: Run Integration Tests
        entry: pytest tests/integration/ -v
        language: system
        pass_filenames: false
        always_run: true
```

---

## 테스트 실행 가이드

### 로컬 환경에서 실행

```bash
# 1. 테스트 DB 시작
docker-compose -f tests/docker-compose.test.yml up -d

# 2. 마이그레이션 실행
DATABASE_URL=postgresql+asyncpg://mes_user:test1234@localhost:5433/mes_test \
alembic upgrade head

# 3. 통합 테스트 실행
pytest tests/integration/ -v

# 4. 커버리지 리포트 생성
pytest tests/integration/ --cov=app --cov-report=html

# 5. 커버리지 확인
open htmlcov/index.html  # macOS
# or
start htmlcov/index.html  # Windows

# 6. 테스트 DB 종료
docker-compose -f tests/docker-compose.test.yml down
```

### 특정 테스트만 실행

```bash
# 마커로 필터링
pytest -m integration  # 통합 테스트만
pytest -m e2e          # E2E 테스트만
pytest -m "not slow"   # 느린 테스트 제외

# 파일명으로 필터링
pytest tests/integration/test_lot_lifecycle.py

# 함수명으로 필터링
pytest tests/integration/test_lot_lifecycle.py::test_lot_creation_and_status_transition
```

---

## 관련 문서

- [8.1 성능 테스트 계획](08-1-performance-test.md) - 성능 테스트 전략
- [3.5 기능 검수 항목](../03-requirements/03-3-acceptance.md) - 인수 테스트 기준
- [4.3 기술 스택](../04-architecture/04-3-tech-stack.md) - 백엔드 아키텍처

---

> **이전 섹션:** [8.1 성능 테스트 계획](08-1-performance-test.md)
> **다음 섹션:** [← 목차로 돌아가기](../README.md)

---

[← 목차로 돌아가기](../README.md)
