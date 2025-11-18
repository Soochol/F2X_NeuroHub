"""Barcode Scanner Input Handler (USB HID Keyboard Emulation)"""

from PySide6.QtCore import QObject, Signal, QTimer


class BarcodeScanner(QObject):
    """Handles barcode scanner input via USB HID keyboard emulation"""

    barcode_scanned = Signal(str)  # Emitted when complete barcode scanned

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timeout)
        self.timeout_ms = 100  # Consider input within 100ms as barcode

    def process_key(self, key: str):
        """
        Process keyboard input
        Called from main window's keyPressEvent
        """
        if key == '\r' or key == '\n':  # Enter key
            if self.buffer:
                self.barcode_scanned.emit(self.buffer)
                self.buffer = ""
                self.timer.stop()
        else:
            self.buffer += key
            self.timer.start(self.timeout_ms)

    def _on_timeout(self):
        """Timeout - not a barcode scan, just normal typing"""
        self.buffer = ""
        self.timer.stop()

    def clear(self):
        """Clear buffer"""
        self.buffer = ""
        self.timer.stop()
