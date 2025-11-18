"""
Configuration management using QSettings for Production Tracker App.
"""
from PySide6.QtCore import QSettings


class AppConfig:
    """Application configuration using QSettings."""

    # Process names mapping
    PROCESS_NAMES = {
        1: "레이저 마킹",
        2: "LMA 조립",
        3: "센서 검사",
        4: "펌웨어 업로드",
        5: "로봇 조립",
        6: "성능검사",
        7: "라벨 프린팅",
        8: "포장+외관검사"
    }

    def __init__(self):
        self.settings = QSettings("F2X", "ProductionTracker")

    # API Configuration
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self.settings.value("api/base_url", "http://localhost:8000")

    @api_base_url.setter
    def api_base_url(self, value: str):
        """Set API base URL."""
        self.settings.setValue("api/base_url", value)

    # Process Configuration
    @property
    def process_number(self) -> int:
        """Get process number (1-8)."""
        return self.settings.value("process/number", 1, type=int)

    @process_number.setter
    def process_number(self, value: int):
        """Set process number (1-8)."""
        if not 1 <= value <= 8:
            raise ValueError("Process number must be between 1 and 8")
        self.settings.setValue("process/number", value)

    @property
    def process_id(self) -> str:
        """Get process ID (PROC-001 ~ PROC-008)."""
        return f"PROC-{self.process_number:03d}"

    @property
    def process_name(self) -> str:
        """Get process name in Korean."""
        return self.PROCESS_NAMES.get(self.process_number, "미지정")

    # File Watcher Configuration
    @property
    def watch_folder(self) -> str:
        """Get file watch folder path."""
        return self.settings.value("file/watch_folder", "C:/neurohub_work")

    @watch_folder.setter
    def watch_folder(self, value: str):
        """Set file watch folder path."""
        self.settings.setValue("file/watch_folder", value)

    # Equipment Configuration
    @property
    def equipment_id(self) -> str:
        """Get equipment ID."""
        return self.settings.value("equipment/id", "EQUIP-001")

    @equipment_id.setter
    def equipment_id(self, value: str):
        """Set equipment ID."""
        self.settings.setValue("equipment/id", value)

    # Line Configuration
    @property
    def line_id(self) -> str:
        """Get production line ID."""
        return self.settings.value("line/id", "LINE-A")

    @line_id.setter
    def line_id(self, value: str):
        """Set production line ID."""
        self.settings.setValue("line/id", value)

    # Auto-login Configuration
    @property
    def auto_login_enabled(self) -> bool:
        """Check if auto-login is enabled."""
        return self.settings.value("auth/auto_login", True, type=bool)

    @auto_login_enabled.setter
    def auto_login_enabled(self, value: bool):
        """Enable or disable auto-login."""
        self.settings.setValue("auth/auto_login", value)

    @property
    def saved_token(self) -> str:
        """Get saved JWT token."""
        return self.settings.value("auth/token", "")

    @saved_token.setter
    def saved_token(self, value: str):
        """Save JWT token."""
        self.settings.setValue("auth/token", value)

    @property
    def saved_username(self) -> str:
        """Get saved username."""
        return self.settings.value("auth/username", "")

    @saved_username.setter
    def saved_username(self, value: str):
        """Save username."""
        self.settings.setValue("auth/username", value)

    def clear_auth(self):
        """Clear all authentication data."""
        self.saved_token = ""
        self.saved_username = ""
