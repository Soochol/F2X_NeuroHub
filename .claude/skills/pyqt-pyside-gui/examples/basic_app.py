"""
Basic PySide6 Application Template

A minimal but complete application structure demonstrating:
- Proper initialization and cleanup
- Signal/slot connections
- Layout management
- Menu and toolbar setup
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QMenuBar, QToolBar,
    QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon


class MainWindow(QMainWindow):
    """Main application window with proper structure"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PySide6 Application")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Welcome to PySide6")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title)
        
        # Input section
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter text here...")
        self.input_field.returnPressed.connect(self.process_input)
        input_layout.addWidget(QLabel("Input:"))
        input_layout.addWidget(self.input_field)
        main_layout.addLayout(input_layout)
        
        # Button section
        button_layout = QHBoxLayout()
        self.process_btn = QPushButton("Process")
        self.process_btn.clicked.connect(self.process_input)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_output)
        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Output section
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        main_layout.addWidget(QLabel("Output:"))
        main_layout.addWidget(self.output_area)
        
    def create_actions(self):
        """Create actions for menus and toolbars"""
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setStatusTip("Create a new file")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction("&Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Open an existing file")
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save the current file")
        self.save_action.triggered.connect(self.save_file)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("About this application")
        self.about_action.triggered.connect(self.show_about)
        
    def create_menus(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_action)
        
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        
    def create_statusbar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
        
    @Slot()
    def process_input(self):
        """Process user input"""
        text = self.input_field.text()
        if text:
            self.output_area.append(f"Processed: {text}")
            self.statusBar().showMessage(f"Processed: {text}", 3000)
        else:
            QMessageBox.warning(self, "Warning", "Please enter some text")
            
    @Slot()
    def clear_output(self):
        """Clear output area"""
        self.output_area.clear()
        self.input_field.clear()
        self.statusBar().showMessage("Cleared", 2000)
        
    @Slot()
    def new_file(self):
        """Create new file"""
        self.statusBar().showMessage("New file created", 2000)
        
    @Slot()
    def open_file(self):
        """Open file"""
        self.statusBar().showMessage("Open file", 2000)
        
    @Slot()
    def save_file(self):
        """Save file"""
        self.statusBar().showMessage("File saved", 2000)
        
    @Slot()
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Application",
            "PySide6 Basic Application Template\n\n"
            "A minimal example demonstrating:\n"
            "• Proper application structure\n"
            "• Signal/slot connections\n"
            "• Layout management\n"
            "• Menus and toolbars"
        )
        
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Perform cleanup here if needed
            event.accept()
        else:
            event.ignore()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PySide6 Basic App")
    app.setOrganizationName("Your Organization")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
