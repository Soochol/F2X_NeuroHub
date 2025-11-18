"""JSON File Watcher Service for automatic completion data processing"""

from PySide6.QtCore import QObject, Signal, QFileSystemWatcher, QTimer
import json
from pathlib import Path
from typing import Dict, Any
import shutil


class FileWatcherService(QObject):
    """Watches for JSON files in pending folder and processes them"""

    json_file_detected = Signal(dict)  # Emit JSON data
    error_occurred = Signal(str)       # Emit error message
    file_processed = Signal(str)       # Emit filename when processed

    def __init__(self, watch_path: str, parent=None):
        super().__init__(parent)
        self.watch_path = Path(watch_path)
        self.pending_dir = self.watch_path / "pending"
        self.completed_dir = self.watch_path / "completed"
        self.error_dir = self.watch_path / "error"

        # Create directories
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.error_dir.mkdir(parents=True, exist_ok=True)

        # QFileSystemWatcher setup
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(str(self.pending_dir))
        self.watcher.directoryChanged.connect(self._on_directory_changed)

        # Scan timer (every 5 seconds)
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self._scan_pending_files)
        self.scan_timer.start(5000)

    def _on_directory_changed(self, path: str):
        """Directory change detected"""
        self._scan_pending_files()

    def _scan_pending_files(self):
        """Scan pending folder for JSON files"""
        for json_file in self.pending_dir.glob("*.json"):
            self._process_json_file(json_file)

    def _process_json_file(self, file_path: Path):
        """Process a single JSON file"""
        try:
            # Read JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate
            if self._validate_json_data(data):
                # Emit signal for processing
                self.json_file_detected.emit(data)

                # Move to completed
                completed_path = self.completed_dir / file_path.name
                shutil.move(str(file_path), str(completed_path))
                self.file_processed.emit(file_path.name)
            else:
                raise ValueError("JSON validation failed")

        except Exception as e:
            # Move to error
            error_path = self.error_dir / file_path.name
            shutil.move(str(file_path), str(error_path))
            self.error_occurred.emit(f"JSON 처리 실패 ({file_path.name}): {str(e)}")

    def _validate_json_data(self, data: Dict[str, Any]) -> bool:
        """Validate JSON schema"""
        required_fields = [
            'lot_number',
            'process_id',
            'equipment_id',
            'worker_id',
            'start_time',
            'complete_time',
            'process_data'
        ]
        return all(field in data for field in required_fields)