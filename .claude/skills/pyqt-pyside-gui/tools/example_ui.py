"""
Example UI file for GUI Analyzer testing.

This file demonstrates various widget patterns and potential issues
that the GUI Analyzer can detect.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QGroupBox, QCheckBox, QRadioButton, QComboBox
)
from PySide6.QtCore import Qt


class ExampleWindow(QMainWindow):
    """Example window with various widgets and intentional issues."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example UI - GUI Analyzer Test")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        self.title_label = QLabel("Example UI Window")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #3ECF8E;
                padding: 10px;
            }
        """)
        layout.addWidget(self.title_label)

        # Form section
        form_group = self.create_form_section()
        layout.addWidget(form_group)

        # Button section with intentional issues
        button_section = self.create_button_section()
        layout.addWidget(button_section)

        # Issue 1: Widget without parent (memory leak risk)
        self.orphan_widget = QLabel("I have no parent!")

        # Issue 2: Very small widget
        self.tiny_widget = QWidget()
        self.tiny_widget.setGeometry(10, 10, 5, 5)  # Too small!
        layout.addWidget(self.tiny_widget)

        # Issue 3: Hidden widget
        self.hidden_label = QLabel("You can't see me")
        self.hidden_label.setVisible(False)
        layout.addWidget(self.hidden_label)

        # Issue 4: Overlapping widgets (manual positioning)
        self.overlap1 = QPushButton("Button 1")
        self.overlap1.setGeometry(100, 100, 150, 50)

        self.overlap2 = QPushButton("Button 2")
        self.overlap2.setGeometry(120, 110, 150, 50)  # Overlaps with overlap1!

        layout.addStretch()

    def create_form_section(self):
        """Create form section with inputs."""
        group = QGroupBox("User Information")
        layout = QVBoxLayout(group)

        # Name field
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # Email field
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Bio field
        self.bio_label = QLabel("Bio:")
        self.bio_text = QTextEdit()
        self.bio_text.setPlaceholderText("Tell us about yourself...")
        self.bio_text.setMaximumHeight(100)
        layout.addWidget(self.bio_label)
        layout.addWidget(self.bio_text)

        return group

    def create_button_section(self):
        """Create button section."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Submit button with hardcoded color (bad practice!)
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet("background-color: #3498db; color: white;")
        layout.addWidget(self.submit_button)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color: #e74c3c; color: white;")
        layout.addWidget(self.cancel_button)

        # Generic widget names (bad practice!)
        self.widget1 = QPushButton("Widget 1")
        layout.addWidget(self.widget1)

        self.var2 = QPushButton("Var 2")
        layout.addWidget(self.var2)

        return widget

    def on_submit_clicked(self):
        """Handle submit button click."""
        name = self.name_input.text()
        email = self.email_input.text()
        bio = self.bio_text.toPlainText()
        print(f"Name: {name}, Email: {email}, Bio: {bio}")

    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.close()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())
