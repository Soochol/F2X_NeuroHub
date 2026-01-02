"""
{{PROTOCOL_NAME}} Protocol Exceptions

프로토콜 통신 중 발생하는 예외 클래스들.
"""


class {{PROTOCOL_NAME}}Error(Exception):
    """Base exception for {{PROTOCOL_NAME}} protocol."""
    pass


class TimeoutError({{PROTOCOL_NAME}}Error):
    """Raised when response timeout occurs."""
    pass


class NAKError({{PROTOCOL_NAME}}Error):
    """Raised when device returns NAK (negative acknowledgment)."""

    def __init__(self, message: str = "NAK received", error_code: int = 0):
        super().__init__(message)
        self.error_code = error_code


class ConnectionError({{PROTOCOL_NAME}}Error):
    """Raised when connection fails."""
    pass


class ProtocolError({{PROTOCOL_NAME}}Error):
    """Raised when protocol violation occurs."""
    pass
