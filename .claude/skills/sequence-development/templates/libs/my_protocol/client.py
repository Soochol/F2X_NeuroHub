"""
{{PROTOCOL_NAME}} Client

고수준 프로토콜 클라이언트.
"""

import logging
import struct
from typing import Any, Dict, List, Optional, Tuple

from .transport import {{TRANSPORT_CLASS}}
from .exceptions import NAKError, ProtocolError, TimeoutError

logger = logging.getLogger(__name__)


class {{CLIENT_CLASS}}:
    """
    {{PROTOCOL_NAME}} Protocol Client.

    {{PROTOCOL_DESCRIPTION}}

    Example:
        transport = {{TRANSPORT_CLASS}}(port="/dev/ttyUSB0")
        client = {{CLIENT_CLASS}}(transport)

        transport.open()
        try:
            version = client.ping()
            print(f"Firmware: {version}")

            result = client.measure()
            print(f"Value: {result}")
        finally:
            transport.close()
    """

    # Protocol constants
    STX = 0x02  # Start of text
    ETX = 0x03  # End of text
    ACK = 0x06  # Acknowledge
    NAK = 0x15  # Negative acknowledge

    def __init__(
        self,
        transport: {{TRANSPORT_CLASS}},
        response_timeout: float = 5.0,
    ):
        """
        Initialize client.

        Args:
            transport: Transport instance
            response_timeout: Response timeout in seconds
        """
        self.transport = transport
        self.response_timeout = response_timeout

    def ping(self) -> Tuple[int, int, int]:
        """
        Send PING and get firmware version.

        Returns:
            Tuple of (major, minor, patch) version numbers
        """
        response = self._send_command(b"PING")
        # Parse version from response (e.g., "1.0.0")
        parts = response.decode().strip().split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def identify(self) -> str:
        """
        Get device identification.

        Returns:
            Device ID string
        """
        response = self._send_command(b"*IDN?")
        return response.decode().strip()

    def measure(self) -> float:
        """
        Measure value.

        Returns:
            Measured value
        """
        response = self._send_command(b"MEAS?")
        return float(response.decode().strip())

    def set_output(self, value: float) -> bool:
        """
        Set output value.

        Args:
            value: Value to set

        Returns:
            True if successful
        """
        cmd = f"OUT {value:.4f}".encode()
        response = self._send_command(cmd)
        return response == b"OK"

    def get_status(self) -> Dict[str, Any]:
        """
        Get device status.

        Returns:
            Status dictionary
        """
        response = self._send_command(b"STATUS?")
        # Parse status response
        data = response.decode().strip()
        # TODO: Parse actual status format
        return {"raw": data}

    # === Low-level protocol methods ===

    def _send_command(self, command: bytes) -> bytes:
        """
        Send command and receive response.

        Args:
            command: Command bytes (without framing)

        Returns:
            Response bytes (without framing)

        Raises:
            NAKError: Device returned NAK
            TimeoutError: Response timeout
            ProtocolError: Invalid response format
        """
        # Build frame: STX + command + ETX
        frame = bytes([self.STX]) + command + bytes([self.ETX])

        # Flush buffers
        self.transport.flush()

        # Send command
        self.transport.write(frame)
        logger.debug(f"TX: {command}")

        # Read response
        response = self._read_response()
        logger.debug(f"RX: {response}")

        return response

    def _read_response(self) -> bytes:
        """
        Read and parse response.

        Returns:
            Response data bytes

        Raises:
            NAKError: NAK received
            TimeoutError: Response timeout
            ProtocolError: Invalid frame
        """
        # Read STX
        header = self.transport.read(1)
        if header[0] == self.NAK:
            raise NAKError("Device returned NAK")
        if header[0] != self.STX:
            raise ProtocolError(f"Expected STX, got 0x{header[0]:02X}")

        # Read until ETX
        data = b""
        while True:
            byte = self.transport.read(1)
            if byte[0] == self.ETX:
                break
            data += byte

            # Safety limit
            if len(data) > 4096:
                raise ProtocolError("Response too long")

        return data

    def _calculate_checksum(self, data: bytes) -> int:
        """
        Calculate checksum (XOR of all bytes).

        Args:
            data: Data bytes

        Returns:
            Checksum byte
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
