"""
Component Library Usage Example

Complete example showing how to use the centralized component library.
This ensures consistent design across your entire application.

Run with hot reload:
    python hot_reload_preview.py component_example.py --debug
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt

# Import the component library
sys.path.insert(0, '/home/claude/pyqt-pyside-gui/scripts')
from ui_components import *


class MainWindow(QMainWindow):
    """Example application using component library"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Component Library Example")
        self.setGeometry(100, 100, 600, 700)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Build UI using components"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(Spacing.LARGE)
        main_layout.setContentsMargins(
            Spacing.LARGE, Spacing.LARGE, 
            Spacing.LARGE, Spacing.LARGE
        )
        
        # Header
        title = Label("User Registration", variant="title", alignment=Qt.AlignCenter)
        main_layout.addWidget(title.get_widget())
        
        subtitle = Label(
            "Fill in the form below to create your account",
            variant="small",
            alignment=Qt.AlignCenter
        )
        main_layout.addWidget(subtitle.get_widget())
        
        # User Info Card
        user_card = Card(title="Personal Information")
        
        self.name_field = FormField(
            "Full Name",
            placeholder="John Doe",
            required=True
        )
        user_card.add_component(self.name_field)
        
        self.email_field = FormField(
            "Email Address",
            placeholder="john@example.com",
            required=True,
            validator=self.validate_email,
            help_text="We'll never share your email with anyone"
        )
        user_card.add_component(self.email_field)
        
        self.phone_field = FormField(
            "Phone Number",
            placeholder="+82-10-1234-5678"
        )
        user_card.add_component(self.phone_field)
        
        main_layout.addWidget(user_card.get_widget())
        
        # Account Card
        account_card = Card(title="Account Settings")
        
        self.username_field = FormField(
            "Username",
            placeholder="johndoe",
            required=True,
            help_text="Only letters, numbers, and underscores"
        )
        account_card.add_component(self.username_field)
        
        self.password_field = FormField(
            "Password",
            input_type="password",
            placeholder="Enter strong password",
            required=True,
            validator=self.validate_password,
            help_text="At least 8 characters"
        )
        account_card.add_component(self.password_field)
        
        self.confirm_password_field = FormField(
            "Confirm Password",
            input_type="password",
            placeholder="Re-enter password",
            required=True
        )
        account_card.add_component(self.confirm_password_field)
        
        main_layout.addWidget(account_card.get_widget())
        
        # Bio Card
        bio_card = Card(title="About You (Optional)")
        
        self.bio_field = FormField(
            "Bio",
            input_type="multiline",
            placeholder="Tell us about yourself..."
        )
        bio_card.add_component(self.bio_field)
        
        main_layout.addWidget(bio_card.get_widget())
        
        main_layout.addStretch()
        
        # Button Group
        buttons = ButtonGroup([
            {
                "text": "Register",
                "variant": ButtonVariant.SUCCESS,
                "callback": self.on_register,
                "min_width": 120
            },
            {
                "text": "Clear",
                "variant": ButtonVariant.SECONDARY,
                "callback": self.on_clear,
                "min_width": 120
            }
        ])
        
        main_layout.addWidget(buttons.get_widget())
    
    def validate_email(self, email):
        """Email validator"""
        if "@" not in email or "." not in email:
            return False, "Please enter a valid email address"
        return True, ""
    
    def validate_password(self, password):
        """Password validator"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        return True, ""
    
    def on_register(self):
        """Handle registration"""
        # Validate all fields
        fields = [
            self.name_field,
            self.email_field,
            self.username_field,
            self.password_field,
            self.confirm_password_field
        ]
        
        is_valid = True
        for field in fields:
            if not field.validate():
                is_valid = False
        
        if not is_valid:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please correct the errors in the form"
            )
            return
        
        # Check password match
        if self.password_field.get_value() != self.confirm_password_field.get_value():
            self.confirm_password_field.show_error("Passwords do not match")
            QMessageBox.warning(
                self,
                "Validation Error",
                "Passwords do not match"
            )
            return
        
        # Collect data
        data = {
            "name": self.name_field.get_value(),
            "email": self.email_field.get_value(),
            "phone": self.phone_field.get_value(),
            "username": self.username_field.get_value(),
            "password": self.password_field.get_value(),
            "bio": self.bio_field.get_value()
        }
        
        # Show success
        QMessageBox.information(
            self,
            "Success",
            f"Account created successfully for {data['name']}!"
        )
        
        print("Registration data:", data)
    
    def on_clear(self):
        """Clear all fields"""
        self.name_field.set_value("")
        self.email_field.set_value("")
        self.phone_field.set_value("")
        self.username_field.set_value("")
        self.password_field.set_value("")
        self.confirm_password_field.set_value("")
        self.bio_field.set_value("")


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Apply global theme
    apply_theme_to_app(app)
    
    # Create and show window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
