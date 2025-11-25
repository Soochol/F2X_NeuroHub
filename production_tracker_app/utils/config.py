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
    def process_db_id(self) -> int:
        """Get process database primary key."""
        return self.settings.value("process/db_id", 0, type=int)

    @process_db_id.setter
    def process_db_id(self, value: int):
        """Set process database primary key."""
        self.settings.setValue("process/db_id", value)

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
    def process_code(self) -> str:
        """Get process code (e.g., LASER_MARKING)."""
        return self.settings.value("process/code", "")

    @process_code.setter
    def process_code(self, value: str):
        """Set process code."""
        self.settings.setValue("process/code", value)

    @property
    def process_id(self) -> str:
        """Get process ID string (PROC-001 ~ PROC-008) - computed from number."""
        return f"PROC-{self.process_number:03d}"

    @property
    def process_name(self) -> str:
        """Get process name in Korean."""
        return self.settings.value("process/name", self.PROCESS_NAMES.get(self.process_number, "미지정"))

    @process_name.setter
    def process_name(self, value: str):
        """Set process name in Korean."""
        self.settings.setValue("process/name", value)

    @property
    def process_name_en(self) -> str:
        """Get process name in English."""
        return self.settings.value("process/name_en", "")

    @process_name_en.setter
    def process_name_en(self, value: str):
        """Set process name in English."""
        self.settings.setValue("process/name_en", value)

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
    def equipment_id(self) -> int:
        """Get equipment ID (database primary key)."""
        return self.settings.value("equipment/id", 0, type=int)

    @equipment_id.setter
    def equipment_id(self, value: int):
        """Set equipment ID (database primary key)."""
        self.settings.setValue("equipment/id", value)

    @property
    def equipment_code(self) -> str:
        """Get equipment code."""
        return self.settings.value("equipment/code", "")

    @equipment_code.setter
    def equipment_code(self, value: str):
        """Set equipment code."""
        self.settings.setValue("equipment/code", value)

    @property
    def equipment_name(self) -> str:
        """Get equipment name."""
        return self.settings.value("equipment/name", "")

    @equipment_name.setter
    def equipment_name(self, value: str):
        """Set equipment name."""
        self.settings.setValue("equipment/name", value)

    # Line Configuration
    @property
    def line_id(self) -> int:
        """Get production line ID (database primary key)."""
        return self.settings.value("line/id", 0, type=int)

    @line_id.setter
    def line_id(self, value: int):
        """Set production line ID (database primary key)."""
        self.settings.setValue("line/id", value)

    @property
    def line_code(self) -> str:
        """Get production line code (e.g., KR-001)."""
        return self.settings.value("line/code", "")

    @line_code.setter
    def line_code(self, value: str):
        """Set production line code."""
        self.settings.setValue("line/code", value)

    @property
    def line_name(self) -> str:
        """Get production line name."""
        return self.settings.value("line/name", "")

    @line_name.setter
    def line_name(self, value: str):
        """Set production line name."""
        self.settings.setValue("line/name", value)

    # First Run Flag
    @property
    def first_run_completed(self) -> bool:
        """Check if first run login has been completed."""
        return self.settings.value("app/first_run_completed", False, type=bool)

    @first_run_completed.setter
    def first_run_completed(self, value: bool):
        """Set first run completed flag."""
        self.settings.setValue("app/first_run_completed", value)

    # Auto-login Configuration (DISABLED - Always require login)
    @property
    def auto_login_enabled(self) -> bool:
        """Check if auto-login is enabled (disabled - always requires login)."""
        return False

    @auto_login_enabled.setter
    def auto_login_enabled(self, value: bool):
        """Auto-login is disabled - this setter does nothing."""
        pass

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

    def reset_first_run(self):
        """Reset first run flag for testing purposes."""
        self.settings.setValue("app/first_run_completed", False)
        self.clear_auth()

    # TCP Server Configuration
    @property
    def tcp_port(self) -> int:
        """Get TCP server port."""
        return self.settings.value("tcp/port", 9000, type=int)

    @tcp_port.setter
    def tcp_port(self, value: int):
        """Set TCP server port."""
        if not 1 <= value <= 65535:
            raise ValueError("TCP port must be between 1 and 65535")
        self.settings.setValue("tcp/port", value)

    # Printer Configuration (for Process 7 - Label Printing)
    @property
    def printer_queue(self) -> str:
        """Get printer queue name."""
        return self.settings.value("printer/queue", "")

    @printer_queue.setter
    def printer_queue(self, value: str):
        """Set printer queue name."""
        self.settings.setValue("printer/queue", value)

    @property
    def zpl_template_path(self) -> str:
        """Get ZPL template file path."""
        return self.settings.value("printer/zpl_template", "")

    @zpl_template_path.setter
    def zpl_template_path(self, value: str):
        """Set ZPL template file path."""
        self.settings.setValue("printer/zpl_template", value)

    @property
    def is_label_printing_process(self) -> bool:
        """Check if current process is Label Printing (Process 7)."""
        return self.process_number == 7
