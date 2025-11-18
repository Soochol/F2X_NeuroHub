"""
Test script for verifying threaded operations in production_tracker_app.
This script tests that UI remains responsive during network operations.
"""
import sys
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QTimer

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from production_tracker_app.services.api_client import APIClient
from production_tracker_app.services.workers import (
    LoginWorker, StartWorkWorker, CompleteWorkWorker, StatsWorker
)
from production_tracker_app.config import Config


class ThreadingTestWidget(QWidget):
    """Test widget to verify threading implementation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threading Test - Production Tracker")
        self.resize(500, 400)

        # Create API client
        self.api_client = APIClient("http://localhost:8000")
        self.config = Config()

        # UI Setup
        layout = QVBoxLayout(self)

        self.status_label = QLabel("Ready to test threading...")
        layout.addWidget(self.status_label)

        # Test buttons
        test_login_btn = QPushButton("Test Login (Threaded)")
        test_login_btn.clicked.connect(self.test_login)
        layout.addWidget(test_login_btn)

        test_start_work_btn = QPushButton("Test Start Work (Threaded)")
        test_start_work_btn.clicked.connect(self.test_start_work)
        layout.addWidget(test_start_work_btn)

        test_stats_btn = QPushButton("Test Stats Fetch (Threaded)")
        test_stats_btn.clicked.connect(self.test_stats)
        layout.addWidget(test_stats_btn)

        # UI responsiveness test
        self.counter = 0
        self.counter_label = QLabel(f"UI Counter: {self.counter}")
        layout.addWidget(self.counter_label)

        # Timer to update counter - proves UI is responsive
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_counter)
        self.timer.start(100)  # Update every 100ms

        layout.addStretch()

        self.workers = []

    def update_counter(self):
        """Update counter to prove UI responsiveness."""
        self.counter += 1
        self.counter_label.setText(f"UI Counter: {self.counter} (updates = UI responsive)")

    def test_login(self):
        """Test threaded login operation."""
        self.status_label.setText("Testing Login... (UI should remain responsive)")

        worker = LoginWorker(self.api_client, "testuser", "testpass")
        worker.login_success.connect(self.on_login_success)
        worker.login_failed.connect(self.on_login_failed)
        worker.finished.connect(lambda: self.cleanup_worker(worker))

        self.workers.append(worker)
        worker.start()

    def test_start_work(self):
        """Test threaded start work operation."""
        self.status_label.setText("Testing Start Work... (UI should remain responsive)")

        worker = StartWorkWorker(
            self.api_client,
            "WF-KR-251110D-001",
            "worker123",
            self.config
        )
        worker.work_started.connect(self.on_work_started)
        worker.work_failed.connect(self.on_work_failed)
        worker.finished.connect(lambda: self.cleanup_worker(worker))

        self.workers.append(worker)
        worker.start()

    def test_stats(self):
        """Test threaded stats fetch operation."""
        self.status_label.setText("Testing Stats Fetch... (UI should remain responsive)")

        worker = StatsWorker(self.api_client, self.config.process_id)
        worker.stats_ready.connect(self.on_stats_ready)
        worker.finished.connect(lambda: self.cleanup_worker(worker))

        self.workers.append(worker)
        worker.start()

    def on_login_success(self, response):
        """Handle login success."""
        self.status_label.setText(f"Login SUCCESS: {response.get('user', {}).get('username')}")

    def on_login_failed(self, error):
        """Handle login failure."""
        self.status_label.setText(f"Login FAILED: {error}")

    def on_work_started(self, response):
        """Handle work started."""
        self.status_label.setText(f"Work Started SUCCESS: {response.get('lot_number')}")

    def on_work_failed(self, error):
        """Handle work start failure."""
        self.status_label.setText(f"Work Start FAILED: {error}")

    def on_stats_ready(self, stats):
        """Handle stats ready."""
        self.status_label.setText(f"Stats SUCCESS: {stats.get('completed', 0)} completed")

    def cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self.workers:
            self.workers.remove(worker)
        worker.deleteLater()

    def closeEvent(self, event):
        """Clean up on close."""
        print("Cleaning up workers...")
        for worker in self.workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
        self.workers.clear()
        event.accept()


def main():
    """Run threading test."""
    print("=" * 60)
    print("THREADING TEST - Production Tracker App")
    print("=" * 60)
    print("\nThis test verifies that:")
    print("1. Network operations run in background threads")
    print("2. UI remains responsive during operations")
    print("3. Thread cleanup works properly")
    print("\nWatch the 'UI Counter' - it should keep incrementing")
    print("even when buttons are clicked and operations are running.")
    print("\nNOTE: Backend server must be running at http://localhost:8000")
    print("=" * 60)

    app = QApplication(sys.argv)
    widget = ThreadingTestWidget()
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
