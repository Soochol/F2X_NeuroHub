# Manual Test 기능 테스트 계획

## 개요

**테스트 대상**: Manual Test 탭 (Batch 없이 실제 하드웨어로 시퀀스 수동 실행)

**테스트 범위**:
- Backend SDK Layer (DriverRegistry, ManualSequenceExecutor)
- Backend API Layer (/api/manual-sequence/)
- Frontend (API, Hooks, UI Components)
- E2E 통합 테스트

---

## 1. Backend SDK Layer 테스트

### 1.1 DriverRegistry 테스트

| ID | 테스트 케이스 | 예상 결과 | 우선순위 |
|----|--------------|----------|---------|
| DR-01 | 유효한 시퀀스/드라이버 클래스 로드 | 드라이버 클래스 반환 | P0 |
| DR-02 | 존재하지 않는 시퀀스 드라이버 로드 | `DriverLoadError` 발생 | P0 |
| DR-03 | 드라이버 인스턴스 생성 | 설정된 드라이버 인스턴스 반환 | P0 |
| DR-04 | 모든 하드웨어 연결 (`connect_hardware`) | Dict[str, driver] 반환 | P0 |
| DR-05 | 일부 하드웨어 연결 실패 | `DriverConnectionError` 발생, 부분 정리 | P1 |
| DR-06 | 모든 드라이버 연결 해제 (`disconnect_all`) | 예외 없이 완료 | P0 |
| DR-07 | disconnect 중 예외 발생 시 계속 진행 | 모든 드라이버 disconnect 시도 | P1 |

```python
# 테스트 파일: tests/sdk/test_driver_registry.py

import pytest
from station_service.sdk import DriverRegistry, DriverLoadError, DriverConnectionError

class TestDriverRegistry:
    @pytest.fixture
    def registry(self):
        return DriverRegistry()

    async def test_load_valid_driver_class(self, registry):
        """DR-01: 유효한 드라이버 클래스 로드"""
        driver_class = await registry.load_driver_class(
            sequence_name="psa_sensor_test",
            hardware_id="psa_mcu",
            hardware_def={"driver": "psa_mcu_driver.PsaMcuDriver"}
        )
        assert driver_class is not None

    async def test_load_invalid_driver_raises_error(self, registry):
        """DR-02: 존재하지 않는 드라이버 로드 시 에러"""
        with pytest.raises(DriverLoadError):
            await registry.load_driver_class(
                sequence_name="nonexistent",
                hardware_id="test",
                hardware_def={"driver": "invalid.Driver"}
            )
```

### 1.2 ManualSequenceExecutor 테스트

| ID | 테스트 케이스 | 예상 결과 | 우선순위 |
|----|--------------|----------|---------|
| ME-01 | 세션 생성 (`create_session`) | 상태=created, 스텝 목록 포함 | P0 |
| ME-02 | 존재하지 않는 시퀀스로 세션 생성 | 예외 발생 | P0 |
| ME-03 | 세션 초기화 (`initialize_session`) | 하드웨어 연결, setup() 실행, 상태=ready | P0 |
| ME-04 | 초기화 중 하드웨어 연결 실패 | 상태=failed, 에러 메시지 포함 | P1 |
| ME-05 | 스텝 실행 (`run_step`) | 스텝 상태=passed/failed, 결과 포함 | P0 |
| ME-06 | 잘못된 스텝 이름으로 실행 | 예외 발생 | P1 |
| ME-07 | 스텝 건너뛰기 (`skip_step`) | 스텝 상태=skipped | P0 |
| ME-08 | 건너뛸 수 없는 스텝 건너뛰기 | 예외 발생 | P1 |
| ME-09 | 하드웨어 명령 실행 (`execute_hardware_command`) | CommandResult 반환 | P0 |
| ME-10 | 존재하지 않는 하드웨어에 명령 실행 | 예외 발생 | P1 |
| ME-11 | 세션 종료 (`finalize_session`) | teardown() 실행, 연결 해제 | P0 |
| ME-12 | 세션 중단 (`abort_session`) | 즉시 중단, 상태=aborted | P0 |
| ME-13 | 세션 삭제 (`delete_session`) | 세션 제거, 정리 완료 | P0 |
| ME-14 | 동시 세션 수 제한 | 최대 10개 세션 | P2 |

```python
# 테스트 파일: tests/sdk/test_manual_executor.py

import pytest
from station_service.sdk import ManualSequenceExecutor, ManualSessionStatus

class TestManualSequenceExecutor:
    @pytest.fixture
    def executor(self):
        return ManualSequenceExecutor()

    async def test_create_session(self, executor):
        """ME-01: 세션 생성"""
        session = await executor.create_session(
            sequence_name="psa_sensor_test",
            hardware_config={},
            parameters={}
        )
        assert session.status == ManualSessionStatus.CREATED
        assert len(session.steps) > 0

    async def test_session_lifecycle(self, executor):
        """ME-03, ME-05, ME-11: 전체 세션 라이프사이클"""
        # 생성
        session = await executor.create_session("psa_sensor_test")
        assert session.status == ManualSessionStatus.CREATED

        # 초기화
        session = await executor.initialize_session(session.id)
        assert session.status == ManualSessionStatus.READY

        # 스텝 실행
        step = await executor.run_step(session.id, "initialize")
        assert step.status in ["passed", "failed"]

        # 종료
        session = await executor.finalize_session(session.id)
        assert session.status == ManualSessionStatus.COMPLETED
```

---

## 2. Backend API Layer 테스트

### 2.1 세션 관리 API

| ID | 엔드포인트 | 메서드 | 테스트 케이스 | 예상 응답 |
|----|-----------|-------|--------------|----------|
| API-01 | `/sessions` | POST | 유효한 시퀀스로 세션 생성 | 201, 세션 상세 |
| API-02 | `/sessions` | POST | 존재하지 않는 시퀀스 | 404 |
| API-03 | `/sessions` | GET | 세션 목록 조회 | 200, 세션 배열 |
| API-04 | `/sessions/{id}` | GET | 존재하는 세션 조회 | 200, 세션 상세 |
| API-05 | `/sessions/{id}` | GET | 존재하지 않는 세션 | 404 |
| API-06 | `/sessions/{id}` | DELETE | 세션 삭제 | 200 |

### 2.2 라이프사이클 API

| ID | 엔드포인트 | 메서드 | 테스트 케이스 | 예상 응답 |
|----|-----------|-------|--------------|----------|
| API-07 | `/sessions/{id}/initialize` | POST | created 상태에서 초기화 | 200, 상태=ready |
| API-08 | `/sessions/{id}/initialize` | POST | 이미 초기화된 세션 | 400 |
| API-09 | `/sessions/{id}/finalize` | POST | ready/running 상태에서 종료 | 200 |
| API-10 | `/sessions/{id}/abort` | POST | 실행 중 세션 중단 | 200, 상태=aborted |

### 2.3 스텝 실행 API

| ID | 엔드포인트 | 메서드 | 테스트 케이스 | 예상 응답 |
|----|-----------|-------|--------------|----------|
| API-11 | `/sessions/{id}/steps/{name}/run` | POST | 스텝 실행 | 200, 스텝 상태 |
| API-12 | `/sessions/{id}/steps/{name}/run` | POST | 잘못된 스텝 이름 | 404 |
| API-13 | `/sessions/{id}/steps/{name}/skip` | POST | 스텝 건너뛰기 | 200 |

### 2.4 하드웨어 API

| ID | 엔드포인트 | 메서드 | 테스트 케이스 | 예상 응답 |
|----|-----------|-------|--------------|----------|
| API-14 | `/sessions/{id}/hardware` | GET | 하드웨어 목록 | 200, HardwareState[] |
| API-15 | `/sessions/{id}/hardware/{hw}/commands` | GET | 명령 목록 | 200, CommandDefinition[] |
| API-16 | `/sessions/{id}/hardware/{hw}/execute` | POST | 명령 실행 | 200, CommandResult |

```python
# 테스트 파일: tests/api/test_manual_sequence_api.py

import pytest
from httpx import AsyncClient

class TestManualSequenceAPI:
    @pytest.fixture
    async def client(self, app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    async def test_create_session(self, client):
        """API-01: 세션 생성"""
        response = await client.post("/api/manual-sequence/sessions", json={
            "sequence_name": "psa_sensor_test"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "created"

    async def test_session_not_found(self, client):
        """API-05: 존재하지 않는 세션"""
        response = await client.get("/api/manual-sequence/sessions/nonexistent")
        assert response.status_code == 404
```

---

## 3. Frontend 테스트

### 3.1 API Client 테스트

| ID | 함수 | 테스트 케이스 | 우선순위 |
|----|-----|--------------|---------|
| FE-01 | `createManualSession` | 성공 응답 처리 | P0 |
| FE-02 | `createManualSession` | 에러 응답 처리 | P1 |
| FE-03 | `getManualSession` | 세션 데이터 반환 | P0 |
| FE-04 | `runManualStep` | 스텝 결과 반환 | P0 |
| FE-05 | `executeHardwareCommand` | 명령 결과 반환 | P0 |

### 3.2 React Hooks 테스트

| ID | Hook | 테스트 케이스 | 우선순위 |
|----|------|--------------|---------|
| FE-06 | `useManualSession` | 세션 데이터 로드 | P0 |
| FE-07 | `useCreateManualSession` | mutation 성공 | P0 |
| FE-08 | `useRunManualSequenceStep` | 스텝 실행 및 캐시 무효화 | P0 |
| FE-09 | `useExecuteHardwareCommand` | 명령 실행 | P0 |

```typescript
// 테스트 파일: station_ui/src/hooks/__tests__/useManualSequence.test.ts

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useManualSession, useCreateManualSession } from '../useManualSequence';

describe('useManualSequence hooks', () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('FE-06: should load session data', async () => {
    const { result } = renderHook(() => useManualSession('test-session-id'), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
  });

  it('FE-07: should create session', async () => {
    const { result } = renderHook(() => useCreateManualSession(), { wrapper });
    await result.current.mutateAsync({ sequenceName: 'psa_sensor_test' });
    expect(result.current.isSuccess).toBe(true);
  });
});
```

### 3.3 UI Component 테스트

| ID | 컴포넌트 | 테스트 케이스 | 우선순위 |
|----|---------|--------------|---------|
| UI-01 | ManualTestTab | 초기 렌더링 (시퀀스 선택) | P0 |
| UI-02 | ManualTestTab | 세션 생성 후 UI 업데이트 | P0 |
| UI-03 | ManualTestTab | Initialize 버튼 클릭 | P0 |
| UI-04 | ManualTestTab | 하드웨어 상태 표시 | P1 |
| UI-05 | ManualTestTab | 진행률 바 업데이트 | P1 |
| UI-06 | ManualTestStepCard | 스텝 상태별 스타일 | P0 |
| UI-07 | ManualTestStepCard | Run/Skip 버튼 동작 | P0 |
| UI-08 | ManualTestStepCard | 확장/축소 토글 | P1 |

```typescript
// 테스트 파일: station_ui/src/pages/__tests__/ManualControlPage.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ManualControlPage } from '../ManualControlPage';

describe('ManualTestTab', () => {
  it('UI-01: should render sequence selection', () => {
    render(<ManualControlPage />);
    fireEvent.click(screen.getByText('Manual Test'));
    expect(screen.getByText('Select Sequence')).toBeInTheDocument();
  });

  it('UI-02: should show session controls after creation', async () => {
    render(<ManualControlPage />);
    fireEvent.click(screen.getByText('Manual Test'));

    // Select sequence and create session
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'psa_sensor_test' } });
    fireEvent.click(screen.getByText('Create Session'));

    await waitFor(() => {
      expect(screen.getByText('Connect & Initialize')).toBeInTheDocument();
    });
  });
});
```

---

## 4. E2E 통합 테스트

### 4.1 시나리오 테스트

| ID | 시나리오 | 단계 | 예상 결과 |
|----|---------|-----|----------|
| E2E-01 | 전체 워크플로우 | 1. Manual Test 탭 클릭<br>2. 시퀀스 선택<br>3. Create Session<br>4. Initialize<br>5. 각 스텝 Run<br>6. Finalize | 모든 스텝 passed, 세션 completed |
| E2E-02 | 스텝 건너뛰기 | 1~4 동일<br>5. 일부 스텝 Skip<br>6. Finalize | 스킵된 스텝 상태=skipped |
| E2E-03 | 세션 중단 | 1~5 중 Abort 클릭 | 상태=aborted, 하드웨어 연결 해제 |
| E2E-04 | 하드웨어 직접 명령 | 1~4 동일<br>5. 하드웨어 선택<br>6. 명령 실행 | 명령 결과 표시 |
| E2E-05 | 세션 리셋 | 1~4 동일<br>5. Reset 클릭 | 초기 상태로 복귀 |

```typescript
// 테스트 파일: station_ui/e2e/manual-test.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Manual Test E2E', () => {
  test('E2E-01: complete workflow', async ({ page }) => {
    await page.goto('/ui/manual');

    // 1. Click Manual Test tab
    await page.click('text=Manual Test');

    // 2. Select sequence
    await page.selectOption('select', 'psa_sensor_test');

    // 3. Create session
    await page.click('text=Create Session');
    await expect(page.locator('text=Connect & Initialize')).toBeVisible();

    // 4. Initialize
    await page.click('text=Connect & Initialize');
    await expect(page.locator('text=ready')).toBeVisible({ timeout: 30000 });

    // 5. Run all steps
    await page.click('text=Run All Remaining');
    await expect(page.locator('[data-status="passed"]')).toHaveCount(4, { timeout: 60000 });

    // 6. Finalize
    await page.click('text=Finalize');
    await expect(page.locator('text=completed')).toBeVisible();
  });

  test('E2E-04: hardware direct command', async ({ page }) => {
    // Setup session...

    // Select hardware
    await page.selectOption('[data-testid="hardware-select"]', 'psa_mcu');

    // Execute command
    await page.click('text=ping');
    await expect(page.locator('text=Success')).toBeVisible();
  });
});
```

---

## 5. 테스트 환경 설정

### 5.1 Mock 설정

```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_driver():
    """Mock 드라이버 생성"""
    driver = AsyncMock()
    driver.connect = AsyncMock(return_value=True)
    driver.disconnect = AsyncMock()
    driver.ping = AsyncMock(return_value={"status": "ok"})
    return driver

@pytest.fixture
def mock_sequence():
    """Mock 시퀀스 생성"""
    class MockSequence:
        async def setup(self, hw):
            pass
        async def teardown(self, hw):
            pass
        async def initialize(self, hw):
            return {"initialized": True}
    return MockSequence()
```

### 5.2 테스트 데이터

```yaml
# tests/fixtures/test_sequence/manifest.yaml
name: test_sequence
display_name: Test Sequence
version: "1.0.0"

hardware:
  mock_device:
    display_name: Mock Device
    driver: mock_driver.MockDriver
    config:
      port: /dev/null

steps:
  - name: test_step
    display_name: Test Step
    method: test_step
    skippable: true
```

---

## 6. 테스트 실행 방법

### Backend 테스트
```bash
cd station_service
pytest tests/sdk/test_driver_registry.py -v
pytest tests/sdk/test_manual_executor.py -v
pytest tests/api/test_manual_sequence_api.py -v
```

### Frontend 테스트
```bash
cd station_ui
npm run test -- --grep "useManualSequence"
npm run test -- --grep "ManualTestTab"
```

### E2E 테스트
```bash
cd station_ui
npx playwright test manual-test.spec.ts
```

---

## 7. 테스트 우선순위

### P0 (필수) - 릴리스 전 통과 필수
- 세션 생성/초기화/종료 라이프사이클
- 스텝 실행/건너뛰기
- 하드웨어 명령 실행
- UI 기본 동작

### P1 (중요) - 릴리스 전 권장
- 에러 핸들링
- 상태 전환 검증
- UI 피드백 (로딩, 에러 메시지)

### P2 (보통) - 추후 추가
- 동시성 테스트
- 성능 테스트
- 엣지 케이스

---

## 8. 버그 리포트 템플릿

```markdown
### 버그 제목
[ManualTest] 간단한 설명

### 재현 단계
1. Manual Test 탭 클릭
2. ...

### 예상 결과
...

### 실제 결과
...

### 환경
- 브라우저: Chrome 120
- OS: Ubuntu 24.04
- Station Service 버전: ...
```
