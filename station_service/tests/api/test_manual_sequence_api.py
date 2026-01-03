"""
Manual Sequence API 테스트.

테스트 대상: station_service/api/routes/manual_sequence.py
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from station_service.api.routes.manual_sequence import get_manual_executor
from station_service.sdk.manual_executor import (
    ManualSession,
    ManualSessionStatus,
    ManualStepState,
    ManualStepStatus,
    HardwareState,
    CommandResult,
)
from station_service.sdk import PackageError


@pytest.fixture
def mock_session():
    """Mock ManualSession for testing."""
    return ManualSession(
        id="test-session-123",
        sequence_name="test_sequence",
        sequence_version="1.0.0",
        status=ManualSessionStatus.CREATED,
        steps=[
            ManualStepState(
                name="initialize",
                display_name="Initialize",
                order=1,
                skippable=False,
            ),
            ManualStepState(
                name="test_step",
                display_name="Test Step",
                order=2,
                skippable=True,
            ),
        ],
        hardware=[
            HardwareState(
                id="test_device",
                display_name="Test Device",
            )
        ],
    )


@pytest.fixture
def api_mock_executor(mock_session):
    """Mock ManualSequenceExecutor for API testing."""
    executor = MagicMock()

    executor.create_session = AsyncMock(return_value=mock_session)
    executor.get_session = MagicMock(return_value=mock_session)
    executor.list_sessions = MagicMock(return_value=[mock_session])
    executor.delete_session = AsyncMock(return_value=True)
    executor.initialize_session = AsyncMock(return_value=mock_session)
    executor.finalize_session = AsyncMock(return_value=mock_session)
    executor.abort_session = AsyncMock(return_value=mock_session)
    executor.run_step = AsyncMock(
        return_value=ManualStepState(
            name="test_step",
            display_name="Test Step",
            order=1,
            skippable=True,
            status=ManualStepStatus.PASSED,
            duration=0.5,
            result={"test": "passed"},
        )
    )
    executor.skip_step = AsyncMock(
        return_value=ManualStepState(
            name="test_step",
            display_name="Test Step",
            order=1,
            skippable=True,
            status=ManualStepStatus.SKIPPED,
        )
    )
    executor.execute_hardware_command = AsyncMock(
        return_value=CommandResult(
            success=True,
            hardware_id="test_device",
            command="ping",
            result={"status": "ok"},
            duration=0.05,
        )
    )
    executor.get_hardware_commands = AsyncMock(
        return_value=[
            {"name": "ping", "display_name": "Ping", "parameters": []},
            {"name": "reset", "display_name": "Reset", "parameters": []},
        ]
    )

    return executor


class TestManualSequenceSessionsAPI:
    """세션 관리 API 테스트."""

    # =========================================================================
    # API-01: 세션 생성
    # =========================================================================
    @pytest.mark.asyncio
    async def test_create_session_success(self, test_app, api_mock_executor):
        """API-01: 유효한 시퀀스로 세션 생성 시 201 응답."""
        from httpx import AsyncClient, ASGITransport

        # Use dependency override
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions",
                    json={"sequence_name": "test_sequence"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == "test-session-123"
            assert data["data"]["status"] == "created"
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-02: 존재하지 않는 시퀀스로 세션 생성
    # =========================================================================
    @pytest.mark.asyncio
    async def test_create_session_sequence_not_found(self, test_app, api_mock_executor):
        """API-02: 존재하지 않는 시퀀스로 세션 생성 시 404 응답."""
        from httpx import AsyncClient, ASGITransport

        api_mock_executor.create_session.side_effect = PackageError("Sequence not found")
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions",
                    json={"sequence_name": "nonexistent"},
                )

            assert response.status_code == 404
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-03: 세션 목록 조회
    # =========================================================================
    @pytest.mark.asyncio
    async def test_list_sessions(self, test_app, api_mock_executor):
        """API-03: 세션 목록 조회 시 200 응답, 세션 배열."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/api/manual-sequence/sessions")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-04: 세션 조회
    # =========================================================================
    @pytest.mark.asyncio
    async def test_get_session(self, test_app, api_mock_executor):
        """API-04: 존재하는 세션 조회 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/manual-sequence/sessions/test-session-123"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == "test-session-123"
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-05: 존재하지 않는 세션 조회
    # =========================================================================
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, test_app, api_mock_executor):
        """API-05: 존재하지 않는 세션 조회 시 404 응답."""
        from httpx import AsyncClient, ASGITransport

        api_mock_executor.get_session.return_value = None
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/manual-sequence/sessions/nonexistent"
                )

            assert response.status_code == 404
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-06: 세션 삭제
    # =========================================================================
    @pytest.mark.asyncio
    async def test_delete_session(self, test_app, api_mock_executor):
        """API-06: 세션 삭제 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(
                    "/api/manual-sequence/sessions/test-session-123"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        finally:
            test_app.dependency_overrides.clear()


class TestManualSequenceLifecycleAPI:
    """라이프사이클 API 테스트."""

    # =========================================================================
    # API-07: 세션 초기화
    # =========================================================================
    @pytest.mark.asyncio
    async def test_initialize_session(self, test_app, api_mock_executor, mock_session):
        """API-07: created 상태에서 초기화 시 200 응답, 상태=ready."""
        from httpx import AsyncClient, ASGITransport

        # 초기화 후 상태 변경
        mock_session.status = ManualSessionStatus.READY
        api_mock_executor.initialize_session.return_value = mock_session
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/initialize"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "ready"
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-08: 이미 초기화된 세션
    # =========================================================================
    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, test_app, api_mock_executor):
        """API-08: 이미 초기화된 세션 초기화 시 409 응답."""
        from httpx import AsyncClient, ASGITransport

        api_mock_executor.initialize_session.side_effect = ValueError("Already initialized")
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/initialize"
                )

            assert response.status_code == 409
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-09: 세션 종료
    # =========================================================================
    @pytest.mark.asyncio
    async def test_finalize_session(self, test_app, api_mock_executor):
        """API-09: ready/running 상태에서 종료 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/finalize"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-10: 세션 중단
    # =========================================================================
    @pytest.mark.asyncio
    async def test_abort_session(self, test_app, api_mock_executor, mock_session):
        """API-10: 실행 중 세션 중단 시 200 응답, 상태=aborted."""
        from httpx import AsyncClient, ASGITransport

        mock_session.status = ManualSessionStatus.ABORTED
        api_mock_executor.abort_session.return_value = mock_session
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/abort"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "aborted"
        finally:
            test_app.dependency_overrides.clear()


class TestManualSequenceStepsAPI:
    """스텝 실행 API 테스트."""

    # =========================================================================
    # API-11: 스텝 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_run_step(self, test_app, api_mock_executor):
        """API-11: 스텝 실행 시 200 응답, 스텝 상태."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/steps/test_step/run"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "passed"
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-12: 잘못된 스텝 이름
    # =========================================================================
    @pytest.mark.asyncio
    async def test_run_step_not_found(self, test_app, api_mock_executor):
        """API-12: 잘못된 스텝 이름으로 실행 시 404 응답."""
        from httpx import AsyncClient, ASGITransport

        api_mock_executor.run_step.side_effect = ValueError("Step not found")
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/steps/invalid_step/run"
                )

            assert response.status_code == 404
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-13: 스텝 건너뛰기
    # =========================================================================
    @pytest.mark.asyncio
    async def test_skip_step(self, test_app, api_mock_executor):
        """API-13: 스텝 건너뛰기 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/steps/test_step/skip"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "skipped"
        finally:
            test_app.dependency_overrides.clear()


class TestManualSequenceHardwareAPI:
    """하드웨어 API 테스트."""

    # =========================================================================
    # API-14: 하드웨어 목록
    # =========================================================================
    @pytest.mark.asyncio
    async def test_get_hardware_list(self, test_app, api_mock_executor, mock_session):
        """API-14: 하드웨어 목록 조회 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        api_mock_executor.get_session.return_value = mock_session
        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/manual-sequence/sessions/test-session-123/hardware"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-15: 명령 목록
    # =========================================================================
    @pytest.mark.asyncio
    async def test_get_hardware_commands(self, test_app, api_mock_executor):
        """API-15: 명령 목록 조회 시 200 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(
                    "/api/manual-sequence/sessions/test-session-123/hardware/test_device/commands"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
        finally:
            test_app.dependency_overrides.clear()

    # =========================================================================
    # API-16: 명령 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_execute_hardware_command(self, test_app, api_mock_executor):
        """API-16: 명령 실행 시 200 응답, CommandResult."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/hardware/test_device/execute",
                    json={"command": "ping"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["success"] is True
            assert data["data"]["command"] == "ping"
        finally:
            test_app.dependency_overrides.clear()


class TestManualSequenceAPIValidation:
    """요청 유효성 검사 테스트."""

    @pytest.mark.asyncio
    async def test_create_session_missing_sequence_name(self, test_app, api_mock_executor):
        """sequence_name 누락 시 422 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions",
                    json={},
                )

            assert response.status_code == 422
        finally:
            test_app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_execute_command_missing_command(self, test_app, api_mock_executor):
        """command 누락 시 422 응답."""
        from httpx import AsyncClient, ASGITransport

        test_app.dependency_overrides[get_manual_executor] = lambda: api_mock_executor

        try:
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/manual-sequence/sessions/test-session-123/hardware/test_device/execute",
                    json={},
                )

            assert response.status_code == 422
        finally:
            test_app.dependency_overrides.clear()
