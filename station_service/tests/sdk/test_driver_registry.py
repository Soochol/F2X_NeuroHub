"""
DriverRegistry 테스트.

테스트 대상: station_service/sdk/driver_registry.py
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from station_service.sdk.driver_registry import (
    DriverRegistry,
    DriverLoadError,
    DriverConnectionError,
)
from station_service.sdk.manifest import (
    HardwareDefinition,
    SequenceManifest,
    EntryPoint,
    StepDefinition,
)


class TestDriverRegistry:
    """DriverRegistry 클래스 테스트."""

    @pytest.fixture
    def registry(self):
        """테스트용 DriverRegistry 인스턴스."""
        return DriverRegistry()

    @pytest.fixture
    def mock_hardware_def(self):
        """테스트용 HardwareDefinition."""
        return HardwareDefinition(
            display_name="Test Device",
            driver="test_driver",
            **{"class": "TestDriver"},
            config_schema=None,
        )

    @pytest.fixture
    def mock_manifest(self, mock_hardware_def):
        """테스트용 SequenceManifest."""
        return SequenceManifest(
            name="test_sequence",
            version="1.0.0",
            entry_point=EntryPoint(module="sequence", **{"class": "TestSequence"}),
            hardware={"test_device": mock_hardware_def},
            steps=[
                StepDefinition(name="step1", display_name="Step 1", order=1),
            ],
        )

    @pytest.fixture
    def mock_driver_class(self):
        """Mock 드라이버 클래스."""
        class MockDriver:
            def __init__(self, name: str, config: dict):
                self.name = name
                self.config = config
                self._connected = False

            async def connect(self):
                self._connected = True
                return True

            async def disconnect(self):
                self._connected = False

            @property
            def connected(self):
                return self._connected

        return MockDriver

    # =========================================================================
    # DR-01: 유효한 드라이버 클래스 로드
    # =========================================================================
    @pytest.mark.asyncio
    async def test_load_valid_driver_class(self, registry, mock_hardware_def, mock_driver_class):
        """DR-01: 유효한 시퀀스/드라이버 클래스 로드 시 드라이버 클래스 반환."""
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.TestDriver = mock_driver_class
            mock_import.return_value = mock_module

            driver_class = await registry.load_driver_class(
                sequence_name="test_sequence",
                hardware_id="test_device",
                hardware_def=mock_hardware_def,
            )

            assert driver_class is not None
            assert driver_class == mock_driver_class

    # =========================================================================
    # DR-02: 존재하지 않는 드라이버 로드
    # =========================================================================
    @pytest.mark.asyncio
    async def test_load_invalid_driver_raises_error(self, registry, mock_hardware_def):
        """DR-02: 존재하지 않는 드라이버 로드 시 DriverLoadError 발생."""
        # No mocking - let it try to actually import (will fail)
        with pytest.raises(DriverLoadError) as exc_info:
            await registry.load_driver_class(
                sequence_name="nonexistent_sequence",
                hardware_id="invalid_hw",
                hardware_def=mock_hardware_def,
            )

        assert "Failed to load driver" in str(exc_info.value)

    # =========================================================================
    # DR-03: 드라이버 인스턴스 생성
    # =========================================================================
    @pytest.mark.asyncio
    async def test_create_driver_instance(self, registry, mock_driver_class):
        """DR-03: 드라이버 인스턴스 생성 시 설정된 인스턴스 반환."""
        config = {"port": "/dev/ttyUSB0", "baudrate": 115200}

        driver = await registry.create_driver_instance(
            driver_class=mock_driver_class,
            name="test_device",
            config=config,
        )

        assert driver is not None
        assert driver.name == "test_device"
        assert driver.config == config

    # =========================================================================
    # DR-04: 모든 하드웨어 연결
    # =========================================================================
    @pytest.mark.asyncio
    async def test_connect_all_hardware(self, registry, mock_manifest, mock_driver_class):
        """DR-04: connect_hardware 호출 시 모든 하드웨어 연결, Dict 반환."""
        hardware_config = {
            "test_device": {"port": "/dev/ttyUSB0"}
        }

        with patch.object(registry, "load_driver_class", return_value=mock_driver_class):
            drivers = await registry.connect_hardware(
                manifest=mock_manifest,
                sequence_path=Path("/tmp/test_sequence"),
                hardware_config=hardware_config,
            )

            assert "test_device" in drivers
            assert drivers["test_device"].connected is True

    # =========================================================================
    # DR-05: 일부 하드웨어 연결 실패
    # =========================================================================
    @pytest.mark.asyncio
    async def test_partial_connection_failure(self, registry, mock_manifest):
        """DR-05: 일부 하드웨어 연결 실패 시 DriverConnectionError 발생."""
        class FailingDriver:
            def __init__(self, name: str, config: dict):
                self.name = name
                self._connected = False

            async def connect(self):
                raise ConnectionError("Connection refused")

            async def disconnect(self):
                pass

        with patch.object(registry, "load_driver_class", return_value=FailingDriver):
            with pytest.raises(DriverConnectionError) as exc_info:
                await registry.connect_hardware(
                    manifest=mock_manifest,
                    sequence_path=Path("/tmp/test_sequence"),
                    hardware_config={},
                )

            assert "Connection errors" in str(exc_info.value)

    # =========================================================================
    # DR-06: 모든 드라이버 연결 해제
    # =========================================================================
    @pytest.mark.asyncio
    async def test_disconnect_all_drivers(self, registry, mock_driver_class):
        """DR-06: disconnect_all 호출 시 예외 없이 완료."""
        driver1 = mock_driver_class(name="device1", config={})
        driver2 = mock_driver_class(name="device2", config={})
        await driver1.connect()
        await driver2.connect()

        drivers = {"device1": driver1, "device2": driver2}

        # Should not raise
        await registry.disconnect_all(drivers)

        assert driver1.connected is False
        assert driver2.connected is False

    # =========================================================================
    # DR-07: disconnect 중 예외 발생
    # =========================================================================
    @pytest.mark.asyncio
    async def test_disconnect_continues_on_error(self, registry):
        """DR-07: disconnect 중 예외 발생 시에도 모든 드라이버 disconnect 시도."""
        disconnect_calls = []

        class DriverWithError:
            def __init__(self, name: str, should_fail: bool = False):
                self.name = name
                self.should_fail = should_fail

            async def disconnect(self):
                disconnect_calls.append(self.name)
                if self.should_fail:
                    raise RuntimeError("Disconnect error")

        driver1 = DriverWithError("device1", should_fail=True)
        driver2 = DriverWithError("device2", should_fail=False)
        driver3 = DriverWithError("device3", should_fail=False)

        drivers = {"device1": driver1, "device2": driver2, "device3": driver3}

        # Should not raise despite error in device1
        await registry.disconnect_all(drivers)

        # All drivers should have been attempted
        assert "device1" in disconnect_calls
        assert "device2" in disconnect_calls
        assert "device3" in disconnect_calls


class TestDriverRegistryCaching:
    """드라이버 클래스 캐싱 테스트."""

    @pytest.fixture
    def registry(self):
        return DriverRegistry()

    @pytest.fixture
    def mock_hardware_def(self):
        """테스트용 HardwareDefinition."""
        return HardwareDefinition(
            display_name="Test Device",
            driver="test_driver",
            **{"class": "TestDriver"},
        )

    @pytest.mark.asyncio
    async def test_driver_class_caching(self, registry, mock_hardware_def):
        """동일한 드라이버 클래스는 캐싱되어야 함."""
        mock_class = MagicMock()

        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.TestDriver = mock_class
            mock_import.return_value = mock_module

            # 첫 번째 호출
            await registry.load_driver_class(
                "seq1", "hw1", mock_hardware_def
            )
            # 두 번째 호출 (동일)
            await registry.load_driver_class(
                "seq1", "hw1", mock_hardware_def
            )

            # importlib.import_module은 한 번만 호출되어야 함 (캐싱)
            assert mock_import.call_count == 1

    @pytest.mark.asyncio
    async def test_clear_cache(self, registry, mock_hardware_def):
        """캐시 클리어 테스트."""
        mock_class = MagicMock()

        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.TestDriver = mock_class
            mock_import.return_value = mock_module

            # 첫 번째 호출
            await registry.load_driver_class("seq1", "hw1", mock_hardware_def)

            # 캐시 클리어
            registry.clear_cache()

            # 두 번째 호출 - 캐시가 클리어됐으므로 다시 import 해야 함
            await registry.load_driver_class("seq1", "hw1", mock_hardware_def)

            # import가 두 번 호출되어야 함
            assert mock_import.call_count == 2
