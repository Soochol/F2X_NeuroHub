"""Application Configuration Management using QSettings"""

from PySide6.QtCore import QSettings
from typing import Optional


class AppConfig:
    """Application configuration manager using QSettings"""

    def __init__(self):
        self.settings = QSettings("F2X", "NeuroHub_Process")

    # API Configuration
    @property
    def api_base_url(self) -> str:
        return self.settings.value("api/base_url", "http://localhost:8000")

    @api_base_url.setter
    def api_base_url(self, value: str):
        self.settings.setValue("api/base_url", value)

    # Process Configuration
    @property
    def process_number(self) -> int:
        """Current PC's process number (1-8)"""
        return self.settings.value("process/number", 1, type=int)

    @process_number.setter
    def process_number(self, value: int):
        if not 1 <= value <= 8:
            raise ValueError("Process number must be between 1 and 8")
        self.settings.setValue("process/number", value)

    @property
    def process_name(self) -> str:
        """Get process name in Korean"""
        process_names = {
            1: "레이저 마킹",
            2: "LMA 조립",
            3: "센서 검사",
            4: "펌웨어 업로드",
            5: "로봇 조립",
            6: "성능검사",
            7: "라벨 프린팅",
            8: "포장+외관검사"
        }
        return process_names.get(self.process_number, "미지정")

    # Auto-login Configuration
    @property
    def auto_login_enabled(self) -> bool:
        return self.settings.value("auth/auto_login", False, type=bool)

    @auto_login_enabled.setter
    def auto_login_enabled(self, value: bool):
        self.settings.setValue("auth/auto_login", value)

    @property
    def saved_username(self) -> str:
        return self.settings.value("auth/username", "")

    @saved_username.setter
    def saved_username(self, value: str):
        self.settings.setValue("auth/username", value)

    @property
    def saved_token(self) -> str:
        """Get saved JWT token (encrypted storage recommended)"""
        return self.settings.value("auth/token", "")

    @saved_token.setter
    def saved_token(self, value: str):
        self.settings.setValue("auth/token", value)

    # File Watcher Configuration
    @property
    def json_watch_path(self) -> str:
        return self.settings.value("file_watcher/path", "C:/neurohub_work")

    @json_watch_path.setter
    def json_watch_path(self, value: str):
        self.settings.setValue("file_watcher/path", value)

    # UI Configuration
    @property
    def window_geometry(self) -> Optional[bytes]:
        return self.settings.value("ui/window_geometry")

    @window_geometry.setter
    def window_geometry(self, value: bytes):
        self.settings.setValue("ui/window_geometry", value)

    def clear_all(self):
        """Clear all settings (for testing or reset)"""
        self.settings.clear()
