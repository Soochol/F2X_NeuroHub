"""
{{PROTOCOL_NAME}} Transport Layer

저수준 통신 처리 (시리얼, TCP/IP 등).
"""

import logging
from typing import Optional

# 외부 의존성 (manifest.yaml dependencies에 명시)
try:
    import serial
except ImportError:
    serial = None  # type: ignore

from .exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class {{TRANSPORT_CLASS}}:
    """
    {{PROTOCOL_NAME}} Transport.

    시리얼 통신을 통한 데이터 송수신.

    Attributes:
        port: 시리얼 포트 경로
        baudrate: 통신 속도
        timeout: 응답 대기 시간
    """

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 115200,
        timeout: float = 5.0,
    ):
        """
        Initialize transport.

        Args:
            port: Serial port path
            baudrate: Baud rate
            timeout: Read timeout in seconds
        """
        if serial is None:
            raise ImportError("pyserial is required. Install with: pip install pyserial")

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None

    def open(self) -> None:
        """Open serial connection."""
        if self._serial and self._serial.is_open:
            return

        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
            logger.info(f"Opened {self.port} at {self.baudrate} bps")
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to open {self.port}: {e}") from e

    def close(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info(f"Closed {self.port}")
        self._serial = None

    def is_open(self) -> bool:
        """Check if connection is open."""
        return self._serial is not None and self._serial.is_open

    def write(self, data: bytes) -> int:
        """
        Write data to serial port.

        Args:
            data: Bytes to write

        Returns:
            Number of bytes written
        """
        if not self._serial or not self._serial.is_open:
            raise ConnectionError("Transport is not open")

        try:
            return self._serial.write(data)
        except serial.SerialTimeoutException as e:
            raise TimeoutError(f"Write timeout: {e}") from e

    def read(self, size: int = 1) -> bytes:
        """
        Read data from serial port.

        Args:
            size: Number of bytes to read

        Returns:
            Received bytes
        """
        if not self._serial or not self._serial.is_open:
            raise ConnectionError("Transport is not open")

        data = self._serial.read(size)
        if len(data) < size:
            raise TimeoutError(f"Read timeout: expected {size} bytes, got {len(data)}")

        return data

    def read_until(self, terminator: bytes = b"\n") -> bytes:
        """
        Read until terminator is found.

        Args:
            terminator: Terminator byte(s)

        Returns:
            Received bytes including terminator
        """
        if not self._serial or not self._serial.is_open:
            raise ConnectionError("Transport is not open")

        data = self._serial.read_until(terminator)
        if not data.endswith(terminator):
            raise TimeoutError("Read timeout: terminator not found")

        return data

    def flush(self) -> None:
        """Flush input and output buffers."""
        if self._serial and self._serial.is_open:
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
