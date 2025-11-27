"""
Configuration management using JSON file for Production Tracker App.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, cast


class AppConfig:
    """Application configuration using JSON file."""

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

    # Default configuration
    DEFAULT_CONFIG: Dict[str, Any] = {
        "api": {
            "base_url": "http://localhost"
        },
        "process": {
            "db_id": 0,
            "number": 1,
            "code": "",
            "name": "",
            "name_en": ""
        },
        "file": {
            "watch_folder": "C:/neurohub_work"
        },
        "equipment": {
            "id": 0,
            "code": "",
            "name": ""
        },
        "line": {
            "id": 0,
            "code": "",
            "name": ""
        },
        "app": {
            "first_run_completed": False
        },
        "auth": {
            "token": "",
            "username": "",
            "recent_usernames": []
        },
        "tcp": {
            "port": 9000
        },
        "printer": {
            "queue": "",
            "zpl_template": ""
        }
    }

    def __init__(self) -> None:
        # Config file path (same directory as this module's parent)
        self._config_dir = Path(__file__).parent.parent
        self._config_file = self._config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from JSON file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                # Merge with defaults for any missing keys
                self._config = self._merge_defaults(self._config, self.DEFAULT_CONFIG)
            except (json.JSONDecodeError, IOError):
                self._config = self.DEFAULT_CONFIG.copy()
                self._save()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self._save()

    def _merge_defaults(self, config: Dict, defaults: Dict) -> Dict:
        """Recursively merge defaults into config for missing keys."""
        result = defaults.copy()
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_defaults(value, result[key])
            else:
                result[key] = value
        return result

    def _save(self) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save config: {e}")

    def _get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(section, {}).get(key, default)

    def _set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value and save."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._save()

    # API Configuration
    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        return self._get("api", "base_url", "http://localhost")

    @api_base_url.setter
    def api_base_url(self, value: str) -> None:
        """Set API base URL."""
        self._set("api", "base_url", value)

    # Process Configuration
    @property
    def process_db_id(self) -> int:
        """Get process database primary key."""
        return int(self._get("process", "db_id", 0))

    @process_db_id.setter
    def process_db_id(self, value: int) -> None:
        """Set process database primary key."""
        self._set("process", "db_id", value)

    @property
    def process_number(self) -> int:
        """Get process number (1-8)."""
        return int(self._get("process", "number", 1))

    @process_number.setter
    def process_number(self, value: int) -> None:
        """Set process number (1-8)."""
        if not 1 <= value <= 8:
            raise ValueError("Process number must be between 1 and 8")
        self._set("process", "number", value)

    @property
    def process_code(self) -> str:
        """Get process code (e.g., LASER_MARKING)."""
        return self._get("process", "code", "")

    @process_code.setter
    def process_code(self, value: str) -> None:
        """Set process code."""
        self._set("process", "code", value)

    @property
    def process_id(self) -> str:
        """Get process ID string (PROC-001 ~ PROC-008) - computed from number."""
        return f"PROC-{self.process_number:03d}"

    @property
    def process_name(self) -> str:
        """Get process name in Korean."""
        saved_name = self._get("process", "name", "")
        return saved_name if saved_name else self.PROCESS_NAMES.get(self.process_number, "미지정")

    @process_name.setter
    def process_name(self, value: str) -> None:
        """Set process name in Korean."""
        self._set("process", "name", value)

    @property
    def process_name_en(self) -> str:
        """Get process name in English."""
        return self._get("process", "name_en", "")

    @process_name_en.setter
    def process_name_en(self, value: str) -> None:
        """Set process name in English."""
        self._set("process", "name_en", value)

    # File Watcher Configuration
    @property
    def watch_folder(self) -> str:
        """Get file watch folder path."""
        return self._get("file", "watch_folder", "C:/neurohub_work")

    @watch_folder.setter
    def watch_folder(self, value: str) -> None:
        """Set file watch folder path."""
        self._set("file", "watch_folder", value)

    # Equipment Configuration
    @property
    def equipment_id(self) -> int:
        """Get equipment ID (database primary key)."""
        return int(self._get("equipment", "id", 0))

    @equipment_id.setter
    def equipment_id(self, value: int) -> None:
        """Set equipment ID (database primary key)."""
        self._set("equipment", "id", value)

    @property
    def equipment_code(self) -> str:
        """Get equipment code."""
        return self._get("equipment", "code", "")

    @equipment_code.setter
    def equipment_code(self, value: str) -> None:
        """Set equipment code."""
        self._set("equipment", "code", value)

    @property
    def equipment_name(self) -> str:
        """Get equipment name."""
        return self._get("equipment", "name", "")

    @equipment_name.setter
    def equipment_name(self, value: str) -> None:
        """Set equipment name."""
        self._set("equipment", "name", value)

    # Line Configuration
    @property
    def line_id(self) -> int:
        """Get production line ID (database primary key)."""
        return int(self._get("line", "id", 0))

    @line_id.setter
    def line_id(self, value: int) -> None:
        """Set production line ID (database primary key)."""
        self._set("line", "id", value)

    @property
    def line_code(self) -> str:
        """Get production line code (e.g., KR-001)."""
        return self._get("line", "code", "")

    @line_code.setter
    def line_code(self, value: str) -> None:
        """Set production line code."""
        self._set("line", "code", value)

    @property
    def line_name(self) -> str:
        """Get production line name."""
        return self._get("line", "name", "")

    @line_name.setter
    def line_name(self, value: str) -> None:
        """Set production line name."""
        self._set("line", "name", value)

    # First Run Flag
    @property
    def first_run_completed(self) -> bool:
        """Check if first run login has been completed."""
        return bool(self._get("app", "first_run_completed", False))

    @first_run_completed.setter
    def first_run_completed(self, value: bool) -> None:
        """Set first run completed flag."""
        self._set("app", "first_run_completed", value)

    # Auto-login Configuration (DISABLED - Always require login)
    @property
    def auto_login_enabled(self) -> bool:
        """Check if auto-login is enabled (disabled - always requires login)."""
        return False

    @auto_login_enabled.setter
    def auto_login_enabled(self, value: bool) -> None:
        """Auto-login is disabled - this setter does nothing."""
        _ = value  # Unused

    @property
    def saved_token(self) -> str:
        """Get saved JWT token."""
        return self._get("auth", "token", "")

    @saved_token.setter
    def saved_token(self, value: str) -> None:
        """Save JWT token."""
        self._set("auth", "token", value)

    @property
    def saved_username(self) -> str:
        """Get saved username."""
        return self._get("auth", "username", "")

    @saved_username.setter
    def saved_username(self, value: str) -> None:
        """Save username."""
        self._set("auth", "username", value)

    @property
    def recent_usernames(self) -> List[str]:
        """Get list of recent usernames (max 5)."""
        usernames = self._get("auth", "recent_usernames", [])
        if isinstance(usernames, str):
            return [usernames] if usernames else []
        return usernames if usernames else []

    @recent_usernames.setter
    def recent_usernames(self, value: List[str]) -> None:
        """Save list of recent usernames."""
        self._set("auth", "recent_usernames", value[:5])

    def add_recent_username(self, username: str) -> None:
        """Add username to recent list (max 5, most recent first)."""
        if not username:
            return
        usernames = self.recent_usernames
        # Remove if already exists
        if username in usernames:
            usernames.remove(username)
        # Add to front
        usernames.insert(0, username)
        # Keep only 5
        self.recent_usernames = usernames[:5]

    def clear_auth(self) -> None:
        """Clear all authentication data."""
        self.saved_token = ""
        self.saved_username = ""

    def reset_first_run(self) -> None:
        """Reset first run flag for testing purposes."""
        self._set("app", "first_run_completed", False)
        self.clear_auth()

    # TCP Server Configuration
    @property
    def tcp_port(self) -> int:
        """Get TCP server port."""
        return int(self._get("tcp", "port", 9000))

    @tcp_port.setter
    def tcp_port(self, value: int) -> None:
        """Set TCP server port."""
        if not 1 <= value <= 65535:
            raise ValueError("TCP port must be between 1 and 65535")
        self._set("tcp", "port", value)

    # Printer Configuration (for Process 7 - Label Printing)
    @property
    def printer_queue(self) -> str:
        """Get printer queue name."""
        return self._get("printer", "queue", "")

    @printer_queue.setter
    def printer_queue(self, value: str) -> None:
        """Set printer queue name."""
        self._set("printer", "queue", value)

    @property
    def zpl_template_path(self) -> str:
        """Get ZPL template file path."""
        return self._get("printer", "zpl_template", "")

    @zpl_template_path.setter
    def zpl_template_path(self, value: str) -> None:
        """Set ZPL template file path."""
        self._set("printer", "zpl_template", value)

    @property
    def is_label_printing_process(self) -> bool:
        """Check if current process is Label Printing (Process 7)."""
        return self.process_number == 7

    @property
    def config_file_path(self) -> str:
        """Get the path to the config file (for debugging)."""
        return str(self._config_file)
