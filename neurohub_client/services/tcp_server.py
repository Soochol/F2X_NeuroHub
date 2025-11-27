"""
TCP Server Service for receiving measurement data from equipment.

Listens for JSON data from inspection/assembly equipment and emits signals
when data is received.

Supports two message types:
- START: Work start notification
- COMPLETE: Work complete with measurement data
"""
import json
import logging
import socket
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from utils.logger import setup_logger

logger = setup_logger()

class MessageType(Enum):
    """Message type enum for TCP communication."""
    START = "START"
    COMPLETE = "COMPLETE"


@dataclass
class MeasurementSpec:
    """Specification for a measurement."""
    min: Optional[float] = None
    max: Optional[float] = None
    target: Optional[float] = None


@dataclass
class MeasurementItem:
    """Single measurement item from equipment."""
    code: str
    name: str
    value: float
    unit: Optional[str] = None
    spec: Optional[MeasurementSpec] = None
    result: str = "PASS"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeasurementItem":
        spec = None
        if data.get("spec"):
            spec = MeasurementSpec(
                min=data["spec"].get("min"),
                max=data["spec"].get("max"),
                target=data["spec"].get("target"),
            )
        return cls(
            code=data["code"],
            name=data["name"],
            value=data["value"],
            unit=data.get("unit"),
            spec=spec,
            result=data.get("result", "PASS"),
        )


@dataclass
class DefectItem:
    """Defect information."""
    code: str
    reason: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DefectItem":
        return cls(
            code=data["code"],
            reason=data["reason"],
        )


@dataclass
class StartData:
    """Data for work start notification from equipment (START message).

    Equipment sends only:
    - message_type: "START"
    - wip_id: WIP ID (e.g., WIP-KR01PSA2511-001)

    Other fields (worker_id, process_id, equipment_id) are filled by Client.
    """
    message_type: str = "START"
    wip_id: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StartData":
        # Support both 'wip_id' and legacy 'serial_number' field
        wip_id = data.get("wip_id") or data.get("serial_number", "")
        return cls(
            message_type=data.get("message_type", "START"),
            wip_id=wip_id,
        )

@dataclass
class EquipmentData:
    """Data received from equipment (COMPLETE message)."""
    message_type: str
    wip_id: str
    result: str
    measurements: List[MeasurementItem]
    defects: List[DefectItem]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EquipmentData":
        measurements = [
            MeasurementItem.from_dict(m) for m in data.get("measurements", [])
        ]
        defects = [
            DefectItem.from_dict(d) for d in data.get("defects", [])
        ]
        # Support both 'wip_id' and legacy 'serial_number' field
        wip_id = data.get("wip_id") or data.get("serial_number", "")
        return cls(
            message_type=data.get("message_type", "COMPLETE"),
            wip_id=wip_id,
            result=data.get("result", "PASS"),
            measurements=measurements,
            defects=defects,
        )

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to format suitable for API transmission."""
        return {
            "items": [
                {
                    "code": m.code,
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "spec": {
                        "min": m.spec.min,
                        "max": m.spec.max,
                        "target": m.spec.target,
                    } if m.spec else None,
                    "result": m.result,
                }
                for m in self.measurements
            ]
        }


class TCPServerSignals(QObject):
    """Qt signals for TCP server events."""
    data_received = Signal(object)      # EquipmentData (complete)
    start_received = Signal(object)     # StartData (start)
    client_connected = Signal(str)      # client address
    client_disconnected = Signal(str)  # client address
    error_occurred = Signal(str)  # error message
    server_started = Signal(int)  # port
    server_stopped = Signal()


class TCPServer:
    """
    TCP Server for receiving measurement data from equipment.

    Usage:
        server = TCPServer(port=9000)
        server.signals.data_received.connect(handle_data)
        server.start()
    """

    def __init__(self, port: int = 9000, host: str = "0.0.0.0") -> None:
        self.host: str = host
        self.port: int = port
        self.signals: TCPServerSignals = TCPServerSignals()

        self._server_socket: Optional[socket.socket] = None
        self._running: bool = False
        self._server_thread: Optional[threading.Thread] = None
        self._buffer_size: int = 65536  # 64KB buffer

        # Service references for synchronous API calls
        self._work_service: Optional[Any] = None
        self._auth_service: Optional[Any] = None

    def set_services(self, work_service: Any, auth_service: Any) -> None:
        """Set service references for synchronous API calls."""
        self._work_service = work_service
        self._auth_service = auth_service
        logger.info("TCP server services configured")

    def start(self) -> bool:
        """Start the TCP server in a background thread."""
        if self._running:
            logger.warning("TCP server is already running")
            return False

        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)  # For graceful shutdown

            self._running = True
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()

            logger.info(f"TCP server started on {self.host}:{self.port}")
            self.signals.server_started.emit(self.port)
            return True

        except Exception as e:
            logger.error(f"Failed to start TCP server: {e}")
            self.signals.error_occurred.emit(f"서버 시작 실패: {e}")
            return False

    def stop(self) -> None:
        """Stop the TCP server."""
        if not self._running:
            return

        self._running = False

        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        if self._server_thread:
            self._server_thread.join(timeout=2.0)
            self._server_thread = None

        logger.info("TCP server stopped")
        self.signals.server_stopped.emit()

    def _run_server(self) -> None:
        """Server main loop running in background thread."""
        while self._running:
            try:
                client_socket, client_address = self._server_socket.accept()
                client_addr_str = f"{client_address[0]}:{client_address[1]}"
                logger.info(f"Client connected: {client_addr_str}")
                self.signals.client_connected.emit(client_addr_str)

                # Handle client in same thread (simple implementation)
                self._handle_client(client_socket, client_addr_str)

            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.error(f"Server accept error: {e}")

    def _handle_client(self, client_socket: socket.socket, client_addr: str) -> None:
        """Handle a single client connection."""
        try:
            # Receive data with length header
            data = self._receive_data(client_socket)

            if data:
                # Parse JSON
                try:
                    json_data = json.loads(data)

                    # Determine message type (default COMPLETE for backward compatibility)
                    msg_type = json_data.get("message_type", "COMPLETE").upper()

                    if msg_type == MessageType.START.value:
                        # Handle START message
                        start_data = StartData.from_dict(json_data)
                        logger.info(
                            f"Received START: wip_id={start_data.wip_id}"
                        )

                        # Call Backend API synchronously before ACK
                        if self._work_service and self._auth_service:
                            worker_id = self._auth_service.get_current_user_id()
                            api_result = self._work_service.start_work_sync(
                                worker_id=worker_id,
                                wip_id=start_data.wip_id
                            )

                            if api_result.get("success"):
                                logger.info(
                                    f"START API success: {start_data.wip_id}"
                                )
                                self.signals.start_received.emit(start_data)
                                response = json.dumps({
                                    "status": "OK",
                                    "message": "Start work registered",
                                    "message_type": "START"
                                })
                            else:
                                error_msg = api_result.get("error", "Unknown error")
                                logger.error(
                                    f"START API failed: {error_msg}"
                                )
                                self.signals.error_occurred.emit(error_msg)
                                response = json.dumps({
                                    "status": "ERROR",
                                    "message": error_msg,
                                    "message_type": "START"
                                })
                        else:
                            # Fallback: no services configured
                            logger.warning("TCP server services not configured")
                            self.signals.start_received.emit(start_data)
                            response = json.dumps({
                                "status": "OK",
                                "message": "Start data received (no API call)",
                                "message_type": "START"
                            })
                    else:
                        # Handle COMPLETE message (default)
                        equipment_data = EquipmentData.from_dict(json_data)
                        logger.info(
                            f"Received COMPLETE: wip_id={equipment_data.wip_id}, "
                            f"result={equipment_data.result}, "
                            f"measurements={len(equipment_data.measurements)}"
                        )
                        self.signals.data_received.emit(equipment_data)
                        response = json.dumps({
                            "status": "OK",
                            "message": "Complete data received",
                            "message_type": "COMPLETE"
                        })

                    client_socket.sendall(response.encode('utf-8'))

                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                    self.signals.error_occurred.emit(f"JSON 파싱 오류: {e}")
                    response = json.dumps({"status": "ERROR", "message": str(e)})
                    client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            logger.error(f"Client handling error: {e}")
            self.signals.error_occurred.emit(f"클라이언트 처리 오류: {e}")

        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            logger.info(f"Client disconnected: {client_addr}")
            self.signals.client_disconnected.emit(client_addr)

    def _receive_data(self, client_socket: socket.socket) -> Optional[str]:
        """
        Receive data from client.

        Supports two modes:
        1. Length-prefixed: First 4 bytes indicate data length
        2. Direct: Receive until connection closes
        """
        client_socket.settimeout(10.0)

        try:
            # Try to read first 4 bytes as length header
            header = client_socket.recv(4)
            if not header:
                return None

            # Check if it looks like a length header (big-endian int)
            if len(header) == 4:
                try:
                    length = int.from_bytes(header, 'big')
                    # Sanity check: length should be reasonable
                    if 0 < length < 1024 * 1024:  # Max 1MB
                        # Length-prefixed mode
                        data = b""
                        while len(data) < length:
                            chunk = client_socket.recv(min(length - len(data), self._buffer_size))
                            if not chunk:
                                break
                            data += chunk
                        return data.decode('utf-8')
                except (ValueError, OverflowError):
                    pass

            # Direct mode: header is actually data
            data = header
            while True:
                try:
                    chunk = client_socket.recv(self._buffer_size)
                    if not chunk:
                        break
                    data += chunk
                except socket.timeout:
                    break

            return data.decode('utf-8') if data else None

        except socket.timeout:
            logger.warning("Client receive timeout")
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return None

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
