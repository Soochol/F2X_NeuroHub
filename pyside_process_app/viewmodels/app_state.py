"""Application State - Global application state management (Singleton)"""

from PySide6.QtCore import QObject, Signal
from typing import Optional


class AppState(QObject):
    """전역 앱 상태 관리 (Singleton)"""

    _instance = None

    user_changed = Signal(object)  # User object or None
    current_lot_changed = Signal(object)  # Lot object or None
    current_serial_changed = Signal(object)  # Serial object or None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._current_user = None
            self._current_lot = None
            self._current_serial = None
            self._initialized = True

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, user):
        self._current_user = user
        self.user_changed.emit(user)

    @property
    def current_lot(self):
        return self._current_lot

    @current_lot.setter
    def current_lot(self, lot):
        self._current_lot = lot
        self.current_lot_changed.emit(lot)

    @property
    def current_serial(self):
        return self._current_serial

    @current_serial.setter
    def current_serial(self, serial):
        self._current_serial = serial
        self.current_serial_changed.emit(serial)

    def is_authenticated(self) -> bool:
        return self._current_user is not None