"""
Completion Watcher for JSON file monitoring.
"""
from PySide6.QtCore import QObject, Signal, QTimer, QFileSystemWatcher
from pathlib import Path
import json
import shutil
import logging

logger = logging.getLogger(__name__)


class CompletionWatcher(QObject):
    """Monitor folder for JSON completion files."""

    completion_detected = Signal(dict)  # JSON completion data
    file_processed = Signal(str)        # Processed filename
    error_occurred = Signal(str)        # Error message

    def __init__(self, watch_path: str, process_id: str):
        super().__init__()
        self.watch_path = Path(watch_path)
        self.process_id = process_id

        # Create directory structure
        self.pending_dir = self.watch_path / "pending"
        self.completed_dir = self.watch_path / "completed"
        self.error_dir = self.watch_path / "error"
        self._create_directories()

        # File system watcher
        self.fs_watcher = QFileSystemWatcher()
        if self.pending_dir.exists():
            self.fs_watcher.addPath(str(self.pending_dir))
            self.fs_watcher.directoryChanged.connect(self._on_directory_changed)

        # Periodic scan timer (every 3 seconds)
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self._scan_pending_files)
        self.scan_timer.start(3000)

        logger.info(f"CompletionWatcher initialized for process {process_id}")
        logger.info(f"Watching: {self.pending_dir}")

    def _create_directories(self):
        """Create required directories if they don't exist."""
        for directory in [self.pending_dir, self.completed_dir, self.error_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {directory}")

    def _on_directory_changed(self, path: str):
        """Handle directory change event."""
        logger.debug(f"Directory changed: {path}")
        self._scan_pending_files()

    def _scan_pending_files(self):
        """Scan for JSON files matching current process."""
        try:
            # Look for JSON files
            for json_file in self.pending_dir.glob("*.json"):
                self._process_json_file(json_file)
        except Exception as e:
            logger.error(f"Error scanning pending files: {e}")

    def _process_json_file(self, file_path: Path):
        """
        Process single JSON file.

        Args:
            file_path: Path to JSON file
        """
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate process_id matches
            file_process_id = data.get("process_id")
            if file_process_id == self.process_id:
                logger.info(f"Processing completion file: {file_path.name}")
                self.completion_detected.emit(data)

                # Move to completed
                dest = self.completed_dir / file_path.name
                shutil.move(str(file_path), str(dest))
                logger.info(f"Moved to completed: {file_path.name}")
                self.file_processed.emit(file_path.name)
            else:
                logger.debug(f"Process ID mismatch: expected {self.process_id}, got {file_process_id}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path.name}: {e}")
            self._move_to_error(file_path, f"JSON 파싱 오류: {str(e)}")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            self._move_to_error(file_path, f"처리 실패: {str(e)}")

    def _move_to_error(self, file_path: Path, error_msg: str):
        """
        Move file to error folder.

        Args:
            file_path: Path to file
            error_msg: Error message
        """
        try:
            dest = self.error_dir / file_path.name
            shutil.move(str(file_path), str(dest))
            logger.error(f"Moved to error: {file_path.name}")
            self.error_occurred.emit(error_msg)
        except Exception as e:
            logger.error(f"Failed to move file to error folder: {e}")

    def stop(self):
        """Stop monitoring."""
        self.scan_timer.stop()
        logger.info("CompletionWatcher stopped")
