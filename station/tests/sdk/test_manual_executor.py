"""
ManualSequenceExecutor 테스트.

테스트 대상: station_service/sdk/manual_executor.py
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from station_service.sdk.manual_executor import (
    ManualSequenceExecutor,
    ManualSession,
    ManualSessionStatus,
    ManualStepStatus,
    ManualStepState,
    HardwareState,
    CommandResult,
)
from station_service.sdk.manifest import (
    SequenceManifest,
    HardwareDefinition,
    EntryPoint,
    StepDefinition,
    ManualConfig,
    Modes,
)


class TestManualSequenceExecutor:
    """ManualSequenceExecutor 클래스 테스트."""

    @pytest.fixture
    def mock_manifest(self):
        """테스트용 SequenceManifest (CLI mode로 설정하여 manifest steps 사용)."""
        hw_def = HardwareDefinition(
            display_name="Test Device",
            driver="test_driver",
            **{"class": "TestDriver"},
        )
        return SequenceManifest(
            name="test_sequence",
            version="1.0.0",
            entry_point=EntryPoint(module="sequence", **{"class": "TestSequence"}),
            modes=Modes(cli=True),  # CLI mode로 manifest steps 사용
            hardware={"test_device": hw_def},
            steps=[
                StepDefinition(
                    name="initialize",
                    display_name="Initialize",
                    order=1,
                    manual=ManualConfig(skippable=False),
                ),
                StepDefinition(
                    name="test_sensor",
                    display_name="Test Sensor",
                    order=2,
                    manual=ManualConfig(skippable=True),
                ),
                StepDefinition(
                    name="finalize",
                    display_name="Finalize",
                    order=3,
                    manual=ManualConfig(skippable=False),
                ),
            ],
        )

    @pytest.fixture
    def mock_sequence_class(self):
        """Mock 시퀀스 클래스."""
        class MockSequence:
            def __init__(self, **kwargs):
                # Accept any kwargs like a real sequence
                self.context = kwargs.get('context')
                self.hardware_config = kwargs.get('hardware_config', {})
                self.parameters = kwargs.get('parameters', {})
                self.output_strategy = kwargs.get('output_strategy')

            async def setup(self):
                pass

            async def teardown(self):
                pass

            async def initialize(self):
                return {"initialized": True}

            async def test_sensor(self):
                return {"sensor_ok": True, "value": 42.5}

            async def finalize(self):
                return {"finalized": True}

        return MockSequence

    @pytest.fixture
    def mock_sequence_loader(self, mock_manifest, mock_sequence_class):
        """Mock SequenceLoader."""
        loader = MagicMock()
        loader.sequences_dir = Path("sequences")
        loader.load_package = AsyncMock(return_value=mock_manifest)
        loader.get_package_path = MagicMock(return_value=Path("sequences/test_sequence"))
        loader.load_sequence_class = AsyncMock(return_value=mock_sequence_class)
        return loader

    @pytest.fixture
    def executor(self, mock_sequence_loader):
        """테스트용 executor 인스턴스."""
        return ManualSequenceExecutor(sequence_loader=mock_sequence_loader)

    @pytest.fixture
    def mock_driver(self):
        """Mock 드라이버."""
        driver = AsyncMock()
        driver.connect = AsyncMock(return_value=True)
        driver.disconnect = AsyncMock()
        driver.connected = True
        driver.ping = AsyncMock(return_value={"status": "ok"})
        return driver

    # =========================================================================
    # ME-01: 세션 생성
    # =========================================================================
    @pytest.mark.asyncio
    async def test_create_session(self, executor):
        """ME-01: create_session 호출 시 상태=created, 스텝 목록 포함."""
        session = await executor.create_session(
            sequence_name="test_sequence",
            hardware_config={},
            parameters={},
        )

        assert session.status == ManualSessionStatus.CREATED
        assert len(session.steps) == 3
        assert session.steps[0].name == "initialize"
        assert session.steps[1].name == "test_sensor"
        assert session.steps[2].name == "finalize"
        assert session.current_step_index == 0

    # =========================================================================
    # ME-02: 존재하지 않는 시퀀스로 세션 생성
    # =========================================================================
    @pytest.mark.asyncio
    async def test_create_session_invalid_sequence(self, mock_sequence_loader):
        """ME-02: 존재하지 않는 시퀀스로 세션 생성 시 예외 발생."""
        from station_service.sdk.loader import PackageError

        mock_sequence_loader.load_package = AsyncMock(
            side_effect=PackageError("nonexistent", "Package not found")
        )
        executor = ManualSequenceExecutor(sequence_loader=mock_sequence_loader)

        with pytest.raises(PackageError):
            await executor.create_session(
                sequence_name="nonexistent_sequence",
                hardware_config={},
                parameters={},
            )

    # =========================================================================
    # ME-03: 세션 초기화
    # =========================================================================
    @pytest.mark.asyncio
    async def test_initialize_session(self, executor, mock_driver):
        """ME-03: initialize_session 호출 시 하드웨어 연결, setup() 실행, 상태=ready."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            session = await executor.initialize_session(session.id)

            assert session.status == ManualSessionStatus.READY
            assert len([h for h in session.hardware if h.connected]) > 0

    # =========================================================================
    # ME-04: 초기화 중 하드웨어 연결 실패
    # =========================================================================
    @pytest.mark.asyncio
    async def test_initialize_session_connection_failure(self, executor):
        """ME-04: 초기화 중 하드웨어 연결 실패 시 DriverConnectionError 발생."""
        from station_service.sdk.driver_registry import DriverConnectionError

        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            side_effect=DriverConnectionError("test_device", "Connection refused"),
        ):
            # 예외가 발생해야 함
            with pytest.raises(DriverConnectionError) as exc_info:
                await executor.initialize_session(session.id)

            assert "test_device" in str(exc_info.value)

    # =========================================================================
    # ME-05: 스텝 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_run_step(self, executor, mock_driver):
        """ME-05: run_step 호출 시 스텝 상태=passed/failed, 결과 포함."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            # Run step
            step_result = await executor.run_step(session.id, "initialize")

            assert step_result.status in [ManualStepStatus.PASSED, ManualStepStatus.FAILED]
            assert step_result.duration >= 0

    # =========================================================================
    # ME-06: 잘못된 스텝 이름으로 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_run_step_invalid_name(self, executor, mock_driver):
        """ME-06: 잘못된 스텝 이름으로 실행 시 예외 발생."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            with pytest.raises(ValueError) as exc_info:
                await executor.run_step(session.id, "nonexistent_step")

            assert "not found" in str(exc_info.value).lower()

    # =========================================================================
    # ME-07: 스텝 건너뛰기
    # =========================================================================
    @pytest.mark.asyncio
    async def test_skip_step(self, executor, mock_driver):
        """ME-07: skip_step 호출 시 스텝 상태=skipped."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            # test_sensor is skippable
            step_result = await executor.skip_step(session.id, "test_sensor")

            assert step_result.status == ManualStepStatus.SKIPPED

    # =========================================================================
    # ME-08: 건너뛸 수 없는 스텝 건너뛰기
    # =========================================================================
    @pytest.mark.asyncio
    async def test_skip_non_skippable_step(self, executor, mock_driver):
        """ME-08: 건너뛸 수 없는 스텝 건너뛰기 시 예외 발생."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            # initialize is NOT skippable
            with pytest.raises(ValueError) as exc_info:
                await executor.skip_step(session.id, "initialize")

            assert "skip" in str(exc_info.value).lower()

    # =========================================================================
    # ME-09: 하드웨어 명령 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_execute_hardware_command(self, executor, mock_driver):
        """ME-09: execute_hardware_command 호출 시 CommandResult 반환."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            result = await executor.execute_hardware_command(
                session_id=session.id,
                hardware_id="test_device",
                command="ping",
                parameters={},
            )

            assert isinstance(result, CommandResult)
            assert result.hardware_id == "test_device"
            assert result.command == "ping"

    # =========================================================================
    # ME-10: 존재하지 않는 하드웨어에 명령 실행
    # =========================================================================
    @pytest.mark.asyncio
    async def test_execute_command_invalid_hardware(self, executor, mock_driver):
        """ME-10: 존재하지 않는 하드웨어에 명령 실행 시 예외 발생."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)

            with pytest.raises(ValueError) as exc_info:
                await executor.execute_hardware_command(
                    session_id=session.id,
                    hardware_id="nonexistent_device",
                    command="ping",
                    parameters={},
                )

            assert "not found" in str(exc_info.value).lower()

    # =========================================================================
    # ME-11: 세션 종료
    # =========================================================================
    @pytest.mark.asyncio
    async def test_finalize_session(self, executor, mock_driver):
        """ME-11: finalize_session 호출 시 teardown() 실행, 연결 해제."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)
            session = await executor.finalize_session(session.id)

            assert session.status in [ManualSessionStatus.COMPLETED, ManualSessionStatus.FAILED]
            mock_driver.disconnect.assert_called()

    # =========================================================================
    # ME-12: 세션 중단
    # =========================================================================
    @pytest.mark.asyncio
    async def test_abort_session(self, executor, mock_driver):
        """ME-12: abort_session 호출 시 즉시 중단, 상태=aborted."""
        session = await executor.create_session("test_sequence")

        with patch.object(
            executor.driver_registry,
            "connect_hardware",
            return_value={"test_device": mock_driver},
        ):
            await executor.initialize_session(session.id)
            session = await executor.abort_session(session.id)

            assert session.status == ManualSessionStatus.ABORTED

    # =========================================================================
    # ME-13: 세션 삭제
    # =========================================================================
    @pytest.mark.asyncio
    async def test_delete_session(self, executor):
        """ME-13: delete_session 호출 시 세션 제거."""
        session = await executor.create_session("test_sequence")
        session_id = session.id

        await executor.delete_session(session_id)

        # 세션이 더 이상 존재하지 않아야 함 (None 반환)
        result = executor.get_session(session_id)
        assert result is None


class TestManualSequenceExecutorStepFlow:
    """스텝 실행 플로우 테스트."""

    @pytest.fixture
    def mock_manifest(self):
        """테스트용 SequenceManifest (CLI mode, 하드웨어 없음)."""
        return SequenceManifest(
            name="test",
            version="1.0.0",
            entry_point=EntryPoint(module="sequence", **{"class": "TestSequence"}),
            modes=Modes(cli=True),
            hardware={},
            steps=[
                StepDefinition(name="step1", display_name="Step 1", order=1),
                StepDefinition(name="step2", display_name="Step 2", order=2),
            ],
        )

    @pytest.fixture
    def mock_sequence_class(self):
        """Mock 시퀀스 클래스."""
        class MockSequence:
            def __init__(self, **kwargs):
                self.context = kwargs.get('context')
                self.hardware_config = kwargs.get('hardware_config', {})
                self.parameters = kwargs.get('parameters', {})
                self.output_strategy = kwargs.get('output_strategy')

            async def setup(self):
                pass

            async def teardown(self):
                pass

            async def step1(self):
                return {"ok": True}

            async def step2(self):
                return {"ok": True}

        return MockSequence

    @pytest.fixture
    def mock_sequence_loader(self, mock_manifest, mock_sequence_class):
        """Mock SequenceLoader."""
        loader = MagicMock()
        loader.sequences_dir = Path("sequences")
        loader.load_package = AsyncMock(return_value=mock_manifest)
        loader.get_package_path = MagicMock(return_value=Path("sequences/test"))
        loader.load_sequence_class = AsyncMock(return_value=mock_sequence_class)
        return loader

    @pytest.fixture
    def executor(self, mock_sequence_loader):
        return ManualSequenceExecutor(sequence_loader=mock_sequence_loader)

    @pytest.mark.asyncio
    async def test_step_order_tracking(self, executor):
        """스텝 실행 시 스텝 상태가 올바르게 업데이트되는지 확인."""
        session = await executor.create_session("test")
        assert session.current_step_index == 0

        with patch.object(executor.driver_registry, "connect_hardware", return_value={}):
            await executor.initialize_session(session.id)

            # Run first step
            step_result = await executor.run_step(session.id, "step1")
            assert step_result.status == ManualStepStatus.PASSED

            session = executor.get_session(session.id)
            # After first step, one step is done
            assert session.steps[0].status == ManualStepStatus.PASSED
            assert session.steps[1].status == ManualStepStatus.PENDING

            # Run second step
            step_result = await executor.run_step(session.id, "step2")
            assert step_result.status == ManualStepStatus.PASSED

            session = executor.get_session(session.id)
            # After second step, session should be completed
            assert session.steps[0].status == ManualStepStatus.PASSED
            assert session.steps[1].status == ManualStepStatus.PASSED
            assert session.status == ManualSessionStatus.COMPLETED


class TestManualSessionDataclasses:
    """데이터클래스 테스트."""

    def test_manual_step_state_defaults(self):
        """ManualStepState 기본값 확인."""
        step = ManualStepState(
            name="test",
            display_name="Test Step",
            order=1,
            skippable=True,
        )
        assert step.status == ManualStepStatus.PENDING
        assert step.duration == 0.0
        assert step.result is None
        assert step.measurements == {}
        assert step.error is None

    def test_hardware_state_defaults(self):
        """HardwareState 기본값 확인."""
        hw = HardwareState(
            id="device1",
            display_name="Device 1",
        )
        assert hw.connected is False
        assert hw.commands == []
        assert hw.error is None

    def test_command_result(self):
        """CommandResult 생성 확인."""
        result = CommandResult(
            success=True,
            hardware_id="device1",
            command="ping",
            result={"status": "ok"},
            duration=0.05,
        )
        assert result.success is True
        assert result.error is None
