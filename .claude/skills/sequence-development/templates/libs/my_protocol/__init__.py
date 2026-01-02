"""
{{PROTOCOL_NAME}} Protocol Package

{{PROTOCOL_DESCRIPTION}}

Example:
    from my_protocol import MyClient, MyTransport

    transport = MyTransport(port="/dev/ttyUSB0", baudrate=115200)
    client = MyClient(transport)
    client.connect()
    result = client.send_command("TEST")
"""

from .transport import {{TRANSPORT_CLASS}}
from .client import {{CLIENT_CLASS}}
from .exceptions import {{PROTOCOL_NAME}}Error, TimeoutError, NAKError

__all__ = [
    "{{TRANSPORT_CLASS}}",
    "{{CLIENT_CLASS}}",
    "{{PROTOCOL_NAME}}Error",
    "TimeoutError",
    "NAKError",
]

__version__ = "1.0.0"
