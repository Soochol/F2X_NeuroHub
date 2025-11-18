"""
JSON Theme System Example

Demonstrates how to use JSON-based theming system.
Switch between themes at runtime!

Run with:
    python json_theme_example.py
    
Hot reload:
    python hot_reload_preview.py json_theme_example.py --debug
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt

# Import the component library
sys.path.insert(0, '/home/claude/pyqt-pyside-gui/scripts')
from ui_components import *


class ThemeDemo(QMainWindow):
    """Demo application showing JSON theme system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Theme System Demo")
        self.setGeometry(100, 100, 700, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Build UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with theme selector
        header_layout = QHBoxLayout()
        
        title = Label("JSON Theme System", variant="title")
        header_layout.addWidget(title.get_widget())
        
        header_layout.addStretch()
        
        # Theme selector
        theme_label = Label("Theme:", variant="normal")
        header_layout.addWidget(theme_label.get_widget())
        
        self.theme_selector = QComboBox()
        available_themes = list_themes()
        self.theme_selector.addItems(available_themes)
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        header_layout.addWidget(self.theme_selector)
        
        main_layout.addLayout(header_layout)
        
        # Description
        desc = Label(
            "JSON 파일로 테마를 정의하고 실시간으로 변경할 수 있습니다.",
            variant="normal"
        )
        main_layout.addWidget(desc.get_widget())
        
        # Button variants card
        button_card = Card(title="Button Variants")
        
        buttons_layout = QVBoxLayout()
        
        # Primary, Secondary, Success, Danger
        row1 = QHBoxLayout()
        row1.addWidget(Button("Primary", variant="primary").get_widget())
        row1.addWidget(Button("Secondary", variant="secondary").get_widget())
        row1.addWidget(Button("Success", variant="success").get_widget())
        row1.addWidget(Button("Danger", variant="danger").get_widget())
        buttons_layout.addLayout(row1)
        
        # Outline, Text
        row2 = QHBoxLayout()
        row2.addWidget(Button("Outline", variant="outline").get_widget())
        row2.addWidget(Button("Text Only", variant="text").get_widget())
        row2.addStretch()
        buttons_layout.addLayout(row2)
        
        # Sizes
        size_label = Label("Button Sizes:", variant="small")
        buttons_layout.addWidget(size_label.get_widget())
        
        row3 = QHBoxLayout()
        row3.addWidget(Button("Small", variant="primary", size="small").get_widget())
        row3.addWidget(Button("Normal", variant="primary", size="normal").get_widget())
        row3.addWidget(Button("Large", variant="primary", size="large").get_widget())
        row3.addStretch()
        buttons_layout.addLayout(row3)
        
        # Add to card
        for i in range(buttons_layout.count()):
            item = buttons_layout.itemAt(i)
            if item.widget():
                button_card.add_widget(item.widget())
            elif item.layout():
                container = QWidget()
                container.setLayout(item.layout())
                button_card.add_widget(container)
        
        main_layout.addWidget(button_card.get_widget())
        
        # Form card
        form_card = Card(title="Form Fields")
        
        self.name_field = FormField("Name", required=True)
        form_card.add_component(self.name_field)
        
        self.email_field = FormField(
            "Email",
            required=True,
            validator=self.validate_email,
            help_text="Enter your email address"
        )
        form_card.add_component(self.email_field)
        
        self.message_field = FormField(
            "Message",
            input_type="multiline"
        )
        form_card.add_component(self.message_field)
        
        main_layout.addWidget(form_card.get_widget())
        
        # Labels card
        label_card = Card(title="Typography")
        
        label_variants = QVBoxLayout()
        label_variants.addWidget(Label("Title Text", variant="title").get_widget())
        label_variants.addWidget(Label("Heading Text", variant="heading").get_widget())
        label_variants.addWidget(Label("Normal Text", variant="normal").get_widget())
        label_variants.addWidget(Label("Small Text", variant="small").get_widget())
        label_variants.addWidget(Label("Caption Text", variant="caption").get_widget())
        
        label_container = QWidget()
        label_container.setLayout(label_variants)
        label_card.add_widget(label_container)
        
        main_layout.addWidget(label_card.get_widget())
        
        main_layout.addStretch()
        
        # Action buttons
        buttons = ButtonGroup([
            {
                "text": "Submit",
                "variant": "success",
                "callback": self.submit_form,
                "min_width": 120
            },
            {
                "text": "Clear",
                "variant": "secondary",
                "callback": self.clear_form,
                "min_width": 120
            }
        ])
        main_layout.addWidget(buttons.get_widget())
        
        # Info footer
        footer = Label(
            "테마는 scripts/ui_components/themes/ 폴더의 JSON 파일에서 수정할 수 있습니다.",
            variant="caption"
        )
        footer.get_widget().setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer.get_widget())
    
    def change_theme(self, theme_name):
        """Change theme dynamically"""
        try:
            # Reload app with new theme
            load_theme(QApplication.instance(), theme_name)
            
            # Recreate UI to apply new theme
            self.setup_ui()
            
            QMessageBox.information(
                self,
                "Theme Changed",
                f"Switched to '{theme_name}' theme!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load theme: {e}"
            )
    
    def validate_email(self, value):
        """Email validator"""
        if "@" not in value or "." not in value:
            return False, "Invalid email format"
        return True, ""
    
    def submit_form(self):
        """Submit form"""
        if self.name_field.validate() and self.email_field.validate():
            data = {
                "name": self.name_field.get_value(),
                "email": self.email_field.get_value(),
                "message": self.message_field.get_value()
            }
            
            QMessageBox.information(
                self,
                "Success",
                f"Form submitted!\n\nName: {data['name']}\nEmail: {data['email']}"
            )
    
    def clear_form(self):
        """Clear form"""
        self.name_field.set_value("")
        self.email_field.set_value("")
        self.message_field.set_value("")


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Load default theme
    print("Available themes:", list_themes())
    theme = load_theme(app, "default")
    print(f"Loaded theme: {theme.name}")
    
    # Create and show window
    window = ThemeDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
