"""
Threaded PySide6 Application

Demonstrates proper threading for long-running operations:
- QThread for background processing
- Signal/slot communication between threads
- Progress updates
- Proper thread cleanup
"""

import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QThread


class Worker(QThread):
    """Worker thread for long-running operations"""
    
    # Define signals
    progress = Signal(int)  # Progress percentage
    status = Signal(str)    # Status message
    result = Signal(object) # Result data
    finished = Signal()     # Completion signal
    error = Signal(str)     # Error signal
    
    def __init__(self, task_type="default"):
        super().__init__()
        self.task_type = task_type
        self._is_running = True
        
    def run(self):
        """Execute the background task"""
        try:
            if self.task_type == "counter":
                self.run_counter_task()
            elif self.task_type == "processor":
                self.run_processing_task()
            else:
                self.run_default_task()
                
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
            
    def run_counter_task(self):
        """Simple counting task"""
        for i in range(101):
            if not self._is_running:
                break
                
            time.sleep(0.05)
            self.progress.emit(i)
            self.status.emit(f"Processing: {i}%")
            
        self.result.emit("Counter task completed!")
        
    def run_processing_task(self):
        """Simulated data processing task"""
        steps = ["Loading data", "Processing", "Analyzing", "Finalizing"]
        
        for idx, step in enumerate(steps):
            if not self._is_running:
                break
                
            self.status.emit(step)
            
            # Simulate work
            for i in range(25):
                if not self._is_running:
                    break
                time.sleep(0.02)
                progress = (idx * 25) + i
                self.progress.emit(progress)
                
        self.result.emit({
            "status": "success",
            "processed_items": 1000,
            "duration": "2.5 seconds"
        })
        
    def run_default_task(self):
        """Default task"""
        for i in range(101):
            if not self._is_running:
                break
                
            time.sleep(0.03)
            self.progress.emit(i)
            
        self.result.emit("Default task completed!")
        
    def stop(self):
        """Stop the worker thread"""
        self._is_running = False


class MainWindow(QMainWindow):
    """Main window with threaded operations"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Threaded Application Example")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Background Thread Example")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_area)
        
        # Control buttons
        self.start_counter_btn = QPushButton("Start Counter Task")
        self.start_counter_btn.clicked.connect(self.start_counter_task)
        layout.addWidget(self.start_counter_btn)
        
        self.start_processor_btn = QPushButton("Start Processing Task")
        self.start_processor_btn.clicked.connect(self.start_processing_task)
        layout.addWidget(self.start_processor_btn)
        
        self.stop_btn = QPushButton("Stop Task")
        self.stop_btn.clicked.connect(self.stop_task)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.log_area.clear)
        layout.addWidget(self.clear_btn)
        
    def log(self, message):
        """Add message to log"""
        self.log_area.append(message)
        
    @Slot()
    def start_counter_task(self):
        """Start counter task in background thread"""
        self.start_task("counter")
        
    @Slot()
    def start_processing_task(self):
        """Start processing task in background thread"""
        self.start_task("processor")
        
    def start_task(self, task_type):
        """Start a background task"""
        # Stop existing worker if running
        if self.worker and self.worker.isRunning():
            self.log("Task already running!")
            return
            
        # Create worker thread
        self.worker = Worker(task_type)
        
        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(self.task_finished)
        self.worker.error.connect(self.handle_error)
        
        # Update UI
        self.start_counter_btn.setEnabled(False)
        self.start_processor_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Start worker
        self.worker.start()
        self.log(f"Started {task_type} task")
        
    @Slot()
    def stop_task(self):
        """Stop the current task"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.log("Task stopped by user")
            self.task_finished()
            
    @Slot(int)
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    @Slot(str)
    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)
        
    @Slot(object)
    def handle_result(self, result):
        """Handle task result"""
        if isinstance(result, dict):
            self.log(f"Result: {result}")
        else:
            self.log(f"Result: {result}")
            
    @Slot()
    def task_finished(self):
        """Handle task completion"""
        self.start_counter_btn.setEnabled(True)
        self.start_processor_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Task completed")
        self.log("Task finished")
        
    @Slot(str)
    def handle_error(self, error_msg):
        """Handle task error"""
        self.log(f"Error: {error_msg}")
        self.status_label.setText(f"Error: {error_msg}")
        self.task_finished()
        
    def closeEvent(self, event):
        """Cleanup on close"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
