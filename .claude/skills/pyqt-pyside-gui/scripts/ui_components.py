"""
UI Components Library

Centralized, reusable UI components with consistent theming.
Import and use these components to maintain design consistency across your app.

Usage:
    from ui_components import (
        AppTheme,
        FormField, 
        PrimaryButton,
        Card,
        HeaderSection
    )
    
    # Use in your app
    field = FormField("Username")
    button = PrimaryButton("Login")
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QGroupBox,
    QComboBox, QSpinBox, QCheckBox, QRadioButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon


# ============================================================================
# THEME CONFIGURATION
# ============================================================================

class AppTheme:
    """Centralized theme configuration"""
    
    # Color Palette - Modern Blue Theme
    PRIMARY = "#2563eb"          # Blue 600
    PRIMARY_HOVER = "#1d4ed8"    # Blue 700
    PRIMARY_PRESSED = "#1e40af"  # Blue 800
    PRIMARY_LIGHT = "#dbeafe"    # Blue 100
    
    SECONDARY = "#64748b"        # Slate 500
    SECONDARY_HOVER = "#475569"  # Slate 600
    SECONDARY_PRESSED = "#334155" # Slate 700
    
    SUCCESS = "#16a34a"          # Green 600
    SUCCESS_HOVER = "#15803d"    # Green 700
    SUCCESS_LIGHT = "#dcfce7"    # Green 100
    
    WARNING = "#ea580c"          # Orange 600
    WARNING_HOVER = "#c2410c"    # Orange 700
    WARNING_LIGHT = "#ffedd5"    # Orange 100
    
    DANGER = "#dc2626"           # Red 600
    DANGER_HOVER = "#b91c1c"     # Red 700
    DANGER_LIGHT = "#fee2e2"     # Red 100
    
    # Neutral Colors
    TEXT_PRIMARY = "#0f172a"     # Slate 900
    TEXT_SECONDARY = "#64748b"   # Slate 500
    TEXT_TERTIARY = "#94a3b8"    # Slate 400
    TEXT_DISABLED = "#cbd5e1"    # Slate 300
    
    BACKGROUND = "#f8fafc"       # Slate 50
    SURFACE = "#ffffff"          # White
    SURFACE_HOVER = "#f1f5f9"    # Slate 100
    
    BORDER = "#e2e8f0"           # Slate 200
    BORDER_DARK = "#cbd5e1"      # Slate 300
    
    # Typography
    FONT_FAMILY = "Segoe UI, -apple-system, sans-serif"
    FONT_SIZE_XL = 20
    FONT_SIZE_LG = 16
    FONT_SIZE_BASE = 14
    FONT_SIZE_SM = 12
    FONT_SIZE_XS = 11
    
    # Spacing
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_2XL = 32
    
    # Border Radius
    RADIUS_SM = 4
    RADIUS_MD = 6
    RADIUS_LG = 8
    RADIUS_XL = 12
    RADIUS_FULL = 9999
    
    # Shadows
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    
    @staticmethod
    def get_button_style(variant="primary", size="medium"):
        """Get button stylesheet based on variant and size"""
        
        # Color variants
        colors = {
            "primary": (AppTheme.PRIMARY, AppTheme.PRIMARY_HOVER, AppTheme.PRIMARY_PRESSED, "#ffffff"),
            "secondary": (AppTheme.SECONDARY, AppTheme.SECONDARY_HOVER, AppTheme.SECONDARY_PRESSED, "#ffffff"),
            "success": (AppTheme.SUCCESS, AppTheme.SUCCESS_HOVER, AppTheme.SUCCESS, "#ffffff"),
            "danger": (AppTheme.DANGER, AppTheme.DANGER_HOVER, AppTheme.DANGER, "#ffffff"),
            "outline": (AppTheme.SURFACE, AppTheme.SURFACE_HOVER, AppTheme.SURFACE_HOVER, AppTheme.TEXT_PRIMARY),
        }
        
        bg, hover, pressed, text = colors.get(variant, colors["primary"])
        
        # Size variants
        sizes = {
            "small": (AppTheme.SPACING_SM, AppTheme.SPACING_MD, AppTheme.FONT_SIZE_SM, 32),
            "medium": (AppTheme.SPACING_MD, AppTheme.SPACING_LG, AppTheme.FONT_SIZE_BASE, 40),
            "large": (AppTheme.SPACING_LG, AppTheme.SPACING_XL, AppTheme.FONT_SIZE_LG, 48),
        }
        
        padding_v, padding_h, font_size, min_height = sizes.get(size, sizes["medium"])
        
        border = f"2px solid {AppTheme.BORDER}" if variant == "outline" else "none"
        
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: {border};
                border-radius: {AppTheme.RADIUS_MD}px;
                padding: {padding_v}px {padding_h}px;
                font-family: {AppTheme.FONT_FAMILY};
                font-size: {font_size}px;
                font-weight: 600;
                min-height: {min_height}px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.BORDER};
                color: {AppTheme.TEXT_DISABLED};
            }}
        """
    
    @staticmethod
    def get_input_style():
        """Get input field stylesheet"""
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {AppTheme.SURFACE};
                color: {AppTheme.TEXT_PRIMARY};
                border: 2px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS_MD}px;
                padding: {AppTheme.SPACING_MD}px;
                font-family: {AppTheme.FONT_FAMILY};
                font-size: {AppTheme.FONT_SIZE_BASE}px;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {AppTheme.PRIMARY};
                outline: none;
            }}
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {AppTheme.SURFACE_HOVER};
                color: {AppTheme.TEXT_DISABLED};
            }}
        """


# ============================================================================
# BASE COMPONENTS
# ============================================================================

class BaseComponent:
    """Base class for all UI components"""
    
    def __init__(self):
        self.widget = None
        
    def create(self):
        """Create and return widget - override in subclasses"""
        raise NotImplementedError
        
    def get_widget(self):
        """Get widget instance"""
        if self.widget is None:
            self.widget = self.create()
        return self.widget


# ============================================================================
# BUTTON COMPONENTS
# ============================================================================

class PrimaryButton(QPushButton):
    """Primary action button"""
    
    def __init__(self, text="", size="medium", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(AppTheme.get_button_style("primary", size))
        self.setCursor(Qt.PointingHandCursor)


class SecondaryButton(QPushButton):
    """Secondary action button"""
    
    def __init__(self, text="", size="medium", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(AppTheme.get_button_style("secondary", size))
        self.setCursor(Qt.PointingHandCursor)


class SuccessButton(QPushButton):
    """Success/confirm button"""
    
    def __init__(self, text="", size="medium", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(AppTheme.get_button_style("success", size))
        self.setCursor(Qt.PointingHandCursor)


class DangerButton(QPushButton):
    """Danger/delete button"""
    
    def __init__(self, text="", size="medium", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(AppTheme.get_button_style("danger", size))
        self.setCursor(Qt.PointingHandCursor)


class OutlineButton(QPushButton):
    """Outline button"""
    
    def __init__(self, text="", size="medium", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(AppTheme.get_button_style("outline", size))
        self.setCursor(Qt.PointingHandCursor)


# ============================================================================
# INPUT COMPONENTS
# ============================================================================

class FormField(BaseComponent):
    """Form field with label and input"""
    
    def __init__(self, label, field_type="line", placeholder="", required=False, 
                 help_text="", error_text=""):
        super().__init__()
        self.label_text = label
        self.field_type = field_type
        self.placeholder = placeholder
        self.required = required
        self.help_text = help_text
        self.error_text = error_text
        self.field = None
        self.error_label = None
        
    def create(self):
        container = QWidget()
        container.setObjectName(f"form_field_{self.label_text.lower().replace(' ', '_')}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, AppTheme.SPACING_MD)
        layout.setSpacing(AppTheme.SPACING_SM)
        
        # Label
        label_text = self.label_text
        if self.required:
            label_text += " *"
        
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.TEXT_PRIMARY};
                font-family: {AppTheme.FONT_FAMILY};
                font-size: {AppTheme.FONT_SIZE_SM}px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(label)
        
        # Input field
        if self.field_type == "line":
            self.field = QLineEdit()
            self.field.setPlaceholderText(self.placeholder)
        elif self.field_type == "text":
            self.field = QTextEdit()
            self.field.setPlaceholderText(self.placeholder)
            self.field.setMaximumHeight(120)
        elif self.field_type == "password":
            self.field = QLineEdit()
            self.field.setEchoMode(QLineEdit.Password)
            self.field.setPlaceholderText(self.placeholder)
        elif self.field_type == "number":
            self.field = QSpinBox()
            self.field.setRange(0, 999999)
        elif self.field_type == "combo":
            self.field = QComboBox()
        
        self.field.setObjectName(f"input_{self.label_text.lower().replace(' ', '_')}")
        self.field.setStyleSheet(AppTheme.get_input_style())
        layout.addWidget(self.field)
        
        # Help text
        if self.help_text:
            help_label = QLabel(self.help_text)
            help_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppTheme.TEXT_SECONDARY};
                    font-size: {AppTheme.FONT_SIZE_XS}px;
                }}
            """)
            layout.addWidget(help_label)
        
        # Error message (hidden by default)
        self.error_label = QLabel(self.error_text)
        self.error_label.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.DANGER};
                font-size: {AppTheme.FONT_SIZE_XS}px;
            }}
        """)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        return container
    
    def get_value(self):
        """Get field value"""
        if isinstance(self.field, (QLineEdit, QTextEdit)):
            return self.field.text() if isinstance(self.field, QLineEdit) else self.field.toPlainText()
        elif isinstance(self.field, QSpinBox):
            return self.field.value()
        elif isinstance(self.field, QComboBox):
            return self.field.currentText()
        return None
    
    def set_value(self, value):
        """Set field value"""
        if isinstance(self.field, QLineEdit):
            self.field.setText(str(value))
        elif isinstance(self.field, QTextEdit):
            self.field.setPlainText(str(value))
        elif isinstance(self.field, QSpinBox):
            self.field.setValue(int(value))
        elif isinstance(self.field, QComboBox):
            self.field.setCurrentText(str(value))
    
    def is_valid(self):
        """Check if field is valid"""
        if self.required:
            value = self.get_value()
            if value is None or (isinstance(value, str) and not value.strip()):
                return False
        return True
    
    def show_error(self, message=None):
        """Show error message"""
        if message:
            self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.field.setStyleSheet(f"""
            QLineEdit, QTextEdit {{
                border: 2px solid {AppTheme.DANGER};
            }}
        """)
    
    def clear_error(self):
        """Clear error message"""
        self.error_label.setVisible(False)
        self.field.setStyleSheet(AppTheme.get_input_style())


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

class Card(QFrame):
    """Card container with shadow and rounded corners"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setup_ui(title)
        
    def setup_ui(self, title):
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.BORDER};
                border-radius: {AppTheme.RADIUS_LG}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            AppTheme.SPACING_LG, AppTheme.SPACING_LG,
            AppTheme.SPACING_LG, AppTheme.SPACING_LG
        )
        layout.setSpacing(AppTheme.SPACING_MD)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppTheme.TEXT_PRIMARY};
                    font-size: {AppTheme.FONT_SIZE_LG}px;
                    font-weight: 700;
                }}
            """)
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_widget(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add layout to card content"""
        self.content_layout.addLayout(layout)


class HeaderSection(BaseComponent):
    """Page header with title and optional subtitle"""
    
    def __init__(self, title, subtitle=""):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        
    def create(self):
        container = QWidget()
        container.setObjectName("header_section")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, AppTheme.SPACING_LG)
        layout.setSpacing(AppTheme.SPACING_SM)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.TEXT_PRIMARY};
                font-size: {AppTheme.FONT_SIZE_XL}px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title_label)
        
        # Subtitle
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {AppTheme.TEXT_SECONDARY};
                    font-size: {AppTheme.FONT_SIZE_BASE}px;
                }}
            """)
            layout.addWidget(subtitle_label)
        
        return container


class Divider(QFrame):
    """Horizontal divider line"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BORDER};
                max-height: 1px;
            }}
        """)


class Spacer(QWidget):
    """Vertical spacer"""
    
    def __init__(self, size="medium", parent=None):
        super().__init__(parent)
        sizes = {
            "small": AppTheme.SPACING_SM,
            "medium": AppTheme.SPACING_LG,
            "large": AppTheme.SPACING_XL,
        }
        height = sizes.get(size, AppTheme.SPACING_LG)
        self.setFixedHeight(height)


# ============================================================================
# UTILITY COMPONENTS
# ============================================================================

class Alert(QFrame):
    """Alert/notification box"""
    
    def __init__(self, message, alert_type="info", parent=None):
        super().__init__(parent)
        self.setup_ui(message, alert_type)
        
    def setup_ui(self, message, alert_type):
        colors = {
            "info": (AppTheme.PRIMARY_LIGHT, AppTheme.PRIMARY),
            "success": (AppTheme.SUCCESS_LIGHT, AppTheme.SUCCESS),
            "warning": (AppTheme.WARNING_LIGHT, AppTheme.WARNING),
            "danger": (AppTheme.DANGER_LIGHT, AppTheme.DANGER),
        }
        
        bg_color, text_color = colors.get(alert_type, colors["info"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 4px solid {text_color};
                border-radius: {AppTheme.RADIUS_MD}px;
                padding: {AppTheme.SPACING_MD}px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            AppTheme.SPACING_MD, AppTheme.SPACING_MD,
            AppTheme.SPACING_MD, AppTheme.SPACING_MD
        )
        
        # Icon (you can add icons here)
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠",
            "danger": "✗",
        }
        
        icon_label = QLabel(icons.get(alert_type, "ℹ️"))
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: {AppTheme.FONT_SIZE_LG}px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: {AppTheme.FONT_SIZE_BASE}px;
            }}
        """)
        layout.addWidget(message_label, stretch=1)


class ButtonGroup(BaseComponent):
    """Group of buttons with consistent spacing"""
    
    def __init__(self, buttons_config, alignment="right"):
        super().__init__()
        self.buttons_config = buttons_config  # [{"text": "Save", "type": "primary"}, ...]
        self.alignment = alignment
        self.buttons = {}
        
    def create(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AppTheme.SPACING_MD)
        
        if self.alignment == "right":
            layout.addStretch()
        
        for btn_config in self.buttons_config:
            btn_type = btn_config.get("type", "secondary")
            btn_size = btn_config.get("size", "medium")
            btn_text = btn_config.get("text", "Button")
            
            if btn_type == "primary":
                button = PrimaryButton(btn_text, btn_size)
            elif btn_type == "success":
                button = SuccessButton(btn_text, btn_size)
            elif btn_type == "danger":
                button = DangerButton(btn_text, btn_size)
            elif btn_type == "outline":
                button = OutlineButton(btn_text, btn_size)
            else:
                button = SecondaryButton(btn_text, btn_size)
            
            layout.addWidget(button)
            self.buttons[btn_text] = button
        
        if self.alignment == "left":
            layout.addStretch()
        
        return container
    
    def connect(self, button_text, callback):
        """Connect button to callback"""
        if button_text in self.buttons:
            self.buttons[button_text].clicked.connect(callback)
    
    def get_button(self, button_text):
        """Get button by text"""
        return self.buttons.get(button_text)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QScrollArea
    
    class DemoWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("UI Components Demo")
            self.setGeometry(100, 100, 800, 900)
            
            # Scroll area for content
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(f"background-color: {AppTheme.BACKGROUND};")
            self.setCentralWidget(scroll)
            
            # Main container
            container = QWidget()
            main_layout = QVBoxLayout(container)
            main_layout.setContentsMargins(
                AppTheme.SPACING_XL, AppTheme.SPACING_XL,
                AppTheme.SPACING_XL, AppTheme.SPACING_XL
            )
            main_layout.setSpacing(AppTheme.SPACING_LG)
            
            # Header
            header = HeaderSection(
                "UI Components Library",
                "Reusable components with consistent theming"
            )
            main_layout.addWidget(header.get_widget())
            
            # Buttons Card
            buttons_card = Card("Buttons")
            button_layout = QHBoxLayout()
            button_layout.addWidget(PrimaryButton("Primary"))
            button_layout.addWidget(SecondaryButton("Secondary"))
            button_layout.addWidget(SuccessButton("Success"))
            button_layout.addWidget(DangerButton("Danger"))
            button_layout.addWidget(OutlineButton("Outline"))
            buttons_card.add_layout(button_layout)
            main_layout.addWidget(buttons_card)
            
            # Form Card
            form_card = Card("Form Example")
            
            name_field = FormField("Name", required=True, placeholder="Enter your name")
            form_card.add_widget(name_field.get_widget())
            
            email_field = FormField("Email", field_type="line", placeholder="user@example.com",
                                   help_text="We'll never share your email")
            form_card.add_widget(email_field.get_widget())
            
            password_field = FormField("Password", field_type="password", required=True)
            form_card.add_widget(password_field.get_widget())
            
            message_field = FormField("Message", field_type="text", 
                                     placeholder="Enter your message...")
            form_card.add_widget(message_field.get_widget())
            
            button_group = ButtonGroup([
                {"text": "Submit", "type": "primary"},
                {"text": "Cancel", "type": "outline"}
            ])
            form_card.add_widget(button_group.get_widget())
            
            main_layout.addWidget(form_card)
            
            # Alerts Card
            alerts_card = Card("Alerts")
            alerts_card.add_widget(Alert("This is an info message", "info"))
            alerts_card.add_widget(Spacer("small"))
            alerts_card.add_widget(Alert("Success! Your action was completed", "success"))
            alerts_card.add_widget(Spacer("small"))
            alerts_card.add_widget(Alert("Warning: Please check your input", "warning"))
            alerts_card.add_widget(Spacer("small"))
            alerts_card.add_widget(Alert("Error: Something went wrong", "danger"))
            main_layout.addWidget(alerts_card)
            
            main_layout.addStretch()
            scroll.setWidget(container)
    
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
