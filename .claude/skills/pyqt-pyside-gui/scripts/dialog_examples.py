"""
Common Dialog Patterns

Demonstrates various dialog types:
- Custom dialogs
- Input dialogs
- File dialogs
- Message boxes
- Modal and non-modal dialogs
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QDialogButtonBox, QLabel, QLineEdit,
    QTextEdit, QFormLayout, QFileDialog, QMessageBox, QInputDialog,
    QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt


class CustomDialog(QDialog):
    """Custom dialog with form inputs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Custom Dialog")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)
        
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(25)
        form_layout.addRow("Age:", self.age_spin)
        
        self.department_combo = QComboBox()
        self.department_combo.addItems([
            "Engineering", "Marketing", "Sales", "HR", "Finance"
        ])
        form_layout.addRow("Department:", self.department_combo)
        
        self.active_check = QCheckBox("Active")
        self.active_check.setChecked(True)
        form_layout.addRow("Status:", self.active_check)
        
        layout.addLayout(form_layout)
        
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        layout.addWidget(self.notes_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_data(self):
        """Get form data"""
        return {
            "name": self.name_edit.text(),
            "email": self.email_edit.text(),
            "age": self.age_spin.value(),
            "department": self.department_combo.currentText(),
            "active": self.active_check.isChecked(),
            "notes": self.notes_edit.toPlainText()
        }


class ProgressDialog(QDialog):
    """Custom progress dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 100)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Processing, please wait...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        from PySide6.QtWidgets import QProgressBar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
    def set_progress(self, value):
        """Update progress value"""
        self.progress.setValue(value)
        
    def set_message(self, message):
        """Update message"""
        self.label.setText(message)


class MainWindow(QMainWindow):
    """Main window demonstrating various dialog patterns"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Dialog Examples")
        self.setGeometry(100, 100, 500, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Dialog Pattern Examples")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Result display
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.result_text)
        
        # Custom dialogs
        layout.addWidget(QLabel("Custom Dialogs:"))
        custom_btn = QPushButton("Show Custom Dialog")
        custom_btn.clicked.connect(self.show_custom_dialog)
        layout.addWidget(custom_btn)
        
        # Standard dialogs
        layout.addWidget(QLabel("Standard Dialogs:"))
        
        btn_layout = QVBoxLayout()
        
        file_btn = QPushButton("File Open Dialog")
        file_btn.clicked.connect(self.show_file_dialog)
        btn_layout.addWidget(file_btn)
        
        save_btn = QPushButton("File Save Dialog")
        save_btn.clicked.connect(self.show_save_dialog)
        btn_layout.addWidget(save_btn)
        
        dir_btn = QPushButton("Directory Dialog")
        dir_btn.clicked.connect(self.show_directory_dialog)
        btn_layout.addWidget(dir_btn)
        
        layout.addLayout(btn_layout)
        
        # Message boxes
        layout.addWidget(QLabel("Message Boxes:"))
        
        msg_layout = QHBoxLayout()
        
        info_btn = QPushButton("Information")
        info_btn.clicked.connect(self.show_info_message)
        msg_layout.addWidget(info_btn)
        
        warn_btn = QPushButton("Warning")
        warn_btn.clicked.connect(self.show_warning_message)
        msg_layout.addWidget(warn_btn)
        
        error_btn = QPushButton("Error")
        error_btn.clicked.connect(self.show_error_message)
        msg_layout.addWidget(error_btn)
        
        question_btn = QPushButton("Question")
        question_btn.clicked.connect(self.show_question_message)
        msg_layout.addWidget(question_btn)
        
        layout.addLayout(msg_layout)
        
        # Input dialogs
        layout.addWidget(QLabel("Input Dialogs:"))
        
        input_layout = QHBoxLayout()
        
        text_input_btn = QPushButton("Text Input")
        text_input_btn.clicked.connect(self.show_text_input)
        input_layout.addWidget(text_input_btn)
        
        int_input_btn = QPushButton("Integer Input")
        int_input_btn.clicked.connect(self.show_int_input)
        input_layout.addWidget(int_input_btn)
        
        item_input_btn = QPushButton("Item Selection")
        item_input_btn.clicked.connect(self.show_item_input)
        input_layout.addWidget(item_input_btn)
        
        layout.addLayout(input_layout)
        layout.addStretch()
        
    def log_result(self, message):
        """Log result to text area"""
        self.result_text.append(message)
        
    def show_custom_dialog(self):
        """Show custom dialog"""
        dialog = CustomDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.log_result(f"Custom dialog data: {data}")
        else:
            self.log_result("Custom dialog cancelled")
            
    def show_file_dialog(self):
        """Show file open dialog"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if filename:
            self.log_result(f"Selected file: {filename}")
            
    def show_save_dialog(self):
        """Show file save dialog"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            self.log_result(f"Save to: {filename}")
            
    def show_directory_dialog(self):
        """Show directory selection dialog"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory"
        )
        if directory:
            self.log_result(f"Selected directory: {directory}")
            
    def show_info_message(self):
        """Show information message box"""
        QMessageBox.information(
            self,
            "Information",
            "This is an information message."
        )
        self.log_result("Showed information message")
        
    def show_warning_message(self):
        """Show warning message box"""
        QMessageBox.warning(
            self,
            "Warning",
            "This is a warning message!"
        )
        self.log_result("Showed warning message")
        
    def show_error_message(self):
        """Show error message box"""
        QMessageBox.critical(
            self,
            "Error",
            "This is an error message!"
        )
        self.log_result("Showed error message")
        
    def show_question_message(self):
        """Show question message box"""
        reply = QMessageBox.question(
            self,
            "Question",
            "Do you want to proceed?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            self.log_result("User clicked Yes")
        elif reply == QMessageBox.No:
            self.log_result("User clicked No")
        else:
            self.log_result("User clicked Cancel")
            
    def show_text_input(self):
        """Show text input dialog"""
        text, ok = QInputDialog.getText(
            self,
            "Text Input",
            "Enter your name:"
        )
        if ok and text:
            self.log_result(f"Entered text: {text}")
            
    def show_int_input(self):
        """Show integer input dialog"""
        value, ok = QInputDialog.getInt(
            self,
            "Integer Input",
            "Enter a number:",
            25,  # default value
            0,   # minimum
            100  # maximum
        )
        if ok:
            self.log_result(f"Entered number: {value}")
            
    def show_item_input(self):
        """Show item selection dialog"""
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]
        item, ok = QInputDialog.getItem(
            self,
            "Item Selection",
            "Choose an option:",
            items,
            0,     # default index
            False  # not editable
        )
        if ok and item:
            self.log_result(f"Selected item: {item}")


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
