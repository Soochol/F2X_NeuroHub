"""Unit tests for hardware drivers."""

import pytest

from sequences.example_test.drivers.base import BaseDriver
from sequences.example_test.drivers.mock_dmm import MockDMM


class TestBaseDriver:
    """Tests for BaseDriver abstract class."""

    def test_cannot_instantiate_directly(self) -> None:
        """Test that BaseDriver cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseDriver()  # type: ignore

    def test_concrete_implementation(self) -> None:
        """Test that concrete implementation works."""
        dmm = MockDMM()
        assert isinstance(dmm, BaseDriver)


class TestMockDMM:
    """Tests for MockDMM driver."""

    @pytest.fixture
    def dmm(self) -> MockDMM:
        """Create a MockDMM instance."""
        return MockDMM(config={"port": "/dev/test", "measurement_delay": 0.01})

    def test_init_defaults(self) -> None:
        """Test initialization with default values."""
        dmm = MockDMM()
        assert dmm.port == "/dev/ttyUSB0"
        assert dmm.measurement_delay == 0.1
        assert dmm.name == "MockDMM"

    def test_init_custom_config(self, dmm: MockDMM) -> None:
        """Test initialization with custom config."""
        assert dmm.port == "/dev/test"
        assert dmm.measurement_delay == 0.01

    @pytest.mark.asyncio
    async def test_connect(self, dmm: MockDMM) -> None:
        """Test connection."""
        result = await dmm.connect()
        assert result is True
        assert await dmm.is_connected() is True

    @pytest.mark.asyncio
    async def test_disconnect(self, dmm: MockDMM) -> None:
        """Test disconnection."""
        await dmm.connect()
        await dmm.disconnect()
        assert await dmm.is_connected() is False

    @pytest.mark.asyncio
    async def test_identify(self, dmm: MockDMM) -> None:
        """Test identification string."""
        idn = await dmm.identify()
        assert "MockInstruments" in idn
        assert "MockDMM-3000" in idn

    @pytest.mark.asyncio
    async def test_reset(self, dmm: MockDMM) -> None:
        """Test reset when connected."""
        await dmm.connect()
        await dmm.reset()
        assert dmm.current_mode == "DC_VOLTAGE"

    @pytest.mark.asyncio
    async def test_reset_not_connected(self, dmm: MockDMM) -> None:
        """Test reset when not connected raises error."""
        with pytest.raises(RuntimeError, match="not connected"):
            await dmm.reset()

    @pytest.mark.asyncio
    async def test_measure_voltage_dc(self, dmm: MockDMM) -> None:
        """Test DC voltage measurement."""
        await dmm.connect()
        voltage = await dmm.measure_voltage(mode="DC")
        # Mock generates values around 3.3V with noise
        assert 2.5 < voltage < 4.0

    @pytest.mark.asyncio
    async def test_measure_voltage_ac(self, dmm: MockDMM) -> None:
        """Test AC voltage measurement."""
        await dmm.connect()
        voltage = await dmm.measure_voltage(mode="AC")
        # Mock generates values around 120V with noise
        assert 100 < voltage < 140

    @pytest.mark.asyncio
    async def test_measure_voltage_not_connected(self, dmm: MockDMM) -> None:
        """Test voltage measurement when not connected."""
        with pytest.raises(RuntimeError, match="not connected"):
            await dmm.measure_voltage()

    @pytest.mark.asyncio
    async def test_measure_current(self, dmm: MockDMM) -> None:
        """Test current measurement."""
        await dmm.connect()
        current = await dmm.measure_current(mode="DC")
        assert 0.05 < current < 0.15

    @pytest.mark.asyncio
    async def test_measure_resistance(self, dmm: MockDMM) -> None:
        """Test resistance measurement."""
        await dmm.connect()
        resistance = await dmm.measure_resistance()
        # Mock generates values around 1000 ohms with noise
        assert 900 < resistance < 1100

    @pytest.mark.asyncio
    async def test_set_mode(self, dmm: MockDMM) -> None:
        """Test setting measurement mode."""
        await dmm.connect()
        await dmm.set_mode("AC_VOLTAGE")
        assert dmm.current_mode == "AC_VOLTAGE"

    @pytest.mark.asyncio
    async def test_set_invalid_mode(self, dmm: MockDMM) -> None:
        """Test setting invalid measurement mode."""
        await dmm.connect()
        with pytest.raises(ValueError, match="Invalid mode"):
            await dmm.set_mode("INVALID_MODE")

    def test_repr(self, dmm: MockDMM) -> None:
        """Test string representation."""
        repr_str = repr(dmm)
        assert "MockDMM" in repr_str
        assert "connected=False" in repr_str
