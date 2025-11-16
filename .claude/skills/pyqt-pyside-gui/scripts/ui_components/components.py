"""
UI Components Library

Reusable, themed components for consistent UI development.
Components use JSON themes loaded via theme_loader.

Usage:
    from ui_components import load_theme, Button, FormField
    
    # Load theme
    app = QApplication(sys.argv)
    theme = load_theme(app, "default")  # or "dark"
    
    # Create themed components
    btn = Button("Click Me", variant="primary")
    layout.addWidget(btn.widget)
"""

from typing import Optional, Callable, List, Dict, Any, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFrame, QGroupBox, QCheckBox, QRadioButton, QComboBox,
    QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QIcon

from .theme_loader import ThemeLoader
from .constants import (
    ColorPalette, Typography, Spacing, BorderRadius,
    ButtonVariant, InputVariant, LabelVariant
)


def get_current_theme():
    """Get currently loaded theme"""
    theme = ThemeLoader.get_current_theme()
    if theme is None:
        # Load default theme if none loaded
        theme = ThemeLoader.load_theme("default")
    return theme


class BaseComponent(QObject):
    """Base class for all components"""
    
    def __init__(self):
        super().__init__()
        self.widget = None
        self._created = False
    
    def create(self):
        """Create the widget - override in subclasses"""
        raise NotImplementedError
    
    def get_widget(self):
        """Get the widget instance (lazy creation)"""
        if not self._created:
            self.widget = self.create()
            self._created = True
        return self.widget
    
    def show(self):
        """Show the widget"""
        self.get_widget().show()
    
    def hide(self):
        """Hide the widget"""
        self.get_widget().hide()
    
    def set_enabled(self, enabled):
        """Enable/disable the widget"""
        self.get_widget().setEnabled(enabled)


class Button(BaseComponent):
    """Themed button component"""
    
    clicked = Signal()
    
    def __init__(self, text, variant="primary", size="normal", 
                 icon=None, min_width=None):
        super().__init__()
        self.text = text
        self.variant = variant
        self.size = size
        self.icon = icon
        self.min_width = min_width
    
    def create(self):
        """Create button widget"""
        button = QPushButton(self.text)
        button.setObjectName(f"btn_{self.text.lower().replace(' ', '_')}")
        
        # Get theme and generate QSS
        theme = get_current_theme()
        qss = ThemeLoader.generate_qss("button", self.variant, theme)
        
        # Apply size modifications if not normal
        if self.size != "normal":
            size_style = theme.get_component_style("button", f"sizes.{self.size}")
            if size_style:
                # Add size-specific styles
                size_qss_parts = []
                for key, value in size_style.items():
                    if not isinstance(value, dict):
                        css_key = ThemeLoader._camel_to_kebab(key)
                        size_qss_parts.append(f"{css_key}: {value}")
                
                if size_qss_parts:
                    size_qss = "QPushButton { " + "; ".join(size_qss_parts) + "; }"
                    qss = qss + "\n" + size_qss
        
        button.setStyleSheet(qss)
        
        # Set icon if provided
        if self.icon:
            button.setIcon(self.icon)
        
        # Set minimum width
        if self.min_width:
            button.setMinimumWidth(self.min_width)
        
        # Connect signal
        button.clicked.connect(self.clicked.emit)
        
        return button
    
    def set_text(self, text):
        """Change button text"""
        self.get_widget().setText(text)


class Input(BaseComponent):
    """Themed input field component"""
    
    textChanged = Signal(str)
    returnPressed = Signal()
    
    def __init__(self, placeholder="", password=False, multiline=False, 
                 max_length=None, read_only=False):
        super().__init__()
        self.placeholder = placeholder
        self.password = password
        self.multiline = multiline
        self.max_length = max_length
        self.read_only = read_only
    
    def create(self):
        """Create input widget"""
        if self.multiline:
            widget = QTextEdit()
            widget.setPlaceholderText(self.placeholder)
            if self.read_only:
                widget.setReadOnly(True)
            widget.textChanged.connect(lambda: self.textChanged.emit(widget.toPlainText()))
        else:
            widget = QLineEdit()
            widget.setPlaceholderText(self.placeholder)
            
            if self.password:
                widget.setEchoMode(QLineEdit.Password)
            
            if self.max_length:
                widget.setMaxLength(self.max_length)
            
            if self.read_only:
                widget.setReadOnly(True)
            
            widget.textChanged.connect(self.textChanged.emit)
            widget.returnPressed.connect(self.returnPressed.emit)
        
        widget.setObjectName(f"input_{self.placeholder.lower().replace(' ', '_')}")
        
        # Apply theme
        theme = get_current_theme()
        qss = ThemeLoader.generate_qss("input", "default", theme)
        widget.setStyleSheet(qss)
        
        return widget
    
    def get_value(self):
        """Get current value"""
        if isinstance(self.widget, QTextEdit):
            return self.widget.toPlainText()
        return self.widget.text()
    
    def set_value(self, value):
        """Set value"""
        if isinstance(self.widget, QTextEdit):
            self.widget.setPlainText(str(value))
        else:
            self.widget.setText(str(value))
    
    def clear(self):
        """Clear input"""
        if isinstance(self.widget, QTextEdit):
            self.widget.clear()
        else:
            self.widget.clear()


class Label(BaseComponent):
    """Themed label component"""
    
    def __init__(self, text, variant="normal", alignment=Qt.AlignLeft):
        super().__init__()
        self.text = text
        self.variant = variant
        self.alignment = alignment
    
    def create(self):
        """Create label widget"""
        label = QLabel(self.text)
        label.setObjectName(f"label_{self.text.lower().replace(' ', '_')[:20]}")

        # Apply theme
        theme = get_current_theme()
        qss = ThemeLoader.generate_qss("label", self.variant, theme)
        label.setStyleSheet(qss)
        label.setAlignment(self.alignment)
        label.setWordWrap(True)

        return label
    
    def set_text(self, text):
        """Change label text"""
        self.get_widget().setText(text)


class FormField(BaseComponent):
    """Complete form field with label and input"""
    
    valueChanged = Signal(str)
    
    def __init__(self, label, input_type="text", placeholder="",
                 required=False, validator=None, help_text=""):
        super().__init__()
        self.label_text = label
        self.input_type = input_type
        self.placeholder = placeholder
        self.required = required
        self.validator = validator
        self.help_text = help_text

        # Keep reference to Input component to prevent garbage collection
        self.input_component = None
        self.input_widget = None
        self.error_label = None
    
    def create(self):
        """Create form field widget"""
        container = QWidget()
        container.setObjectName(f"form_field_{self.label_text.lower().replace(' ', '_')}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, Spacing.NORMAL)
        layout.setSpacing(Spacing.XSMALL)
        
        # Label
        label_text = self.label_text
        if self.required:
            label_text += " *"
        
        label = Label(label_text, variant="normal").get_widget()
        layout.addWidget(label)
        
        # Input based on type
        # IMPORTANT: Keep reference to Input component to prevent garbage collection
        if self.input_type == "text":
            self.input_component = Input(self.placeholder)
            self.input_widget = self.input_component.get_widget()
        elif self.input_type == "password":
            self.input_component = Input(self.placeholder, password=True)
            self.input_widget = self.input_component.get_widget()
        elif self.input_type == "multiline":
            self.input_component = Input(self.placeholder, multiline=True)
            self.input_widget = self.input_component.get_widget()
        elif self.input_type == "number":
            self.input_widget = QSpinBox()
            theme = get_current_theme()
            qss = ThemeLoader.generate_qss("input", "default", theme)
            self.input_widget.setStyleSheet(qss)
        elif self.input_type == "decimal":
            self.input_widget = QDoubleSpinBox()
            theme = get_current_theme()
            qss = ThemeLoader.generate_qss("input", "default", theme)
            self.input_widget.setStyleSheet(qss)
        elif self.input_type == "combo":
            self.input_widget = QComboBox()
            theme = get_current_theme()
            qss = ThemeLoader.generate_qss("comboBox", "default", theme)
            self.input_widget.setStyleSheet(qss)
        
        self.input_widget.setObjectName(f"input_{self.label_text.lower().replace(' ', '_')}")
        layout.addWidget(self.input_widget)
        
        # Help text
        if self.help_text:
            help_label = QLabel(self.help_text)
            help_label.setStyleSheet(f"""
                QLabel {{
                    color: {ColorPalette.TEXT_SECONDARY};
                    font-size: {Typography.FONT_SIZE_SMALL}px;
                }}
            """)
            layout.addWidget(help_label)
        
        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.DANGER};
                font-size: {Typography.FONT_SIZE_SMALL}px;
            }}
        """)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Connect value changed
        if hasattr(self.input_widget, 'textChanged'):
            self.input_widget.textChanged.connect(lambda: self._on_value_changed())
        
        return container
    
    def _on_value_changed(self):
        """Handle value change"""
        self.validate()
        self.valueChanged.emit(self.get_value())
    
    def get_value(self):
        """Get field value"""
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            if isinstance(self.input_widget, QTextEdit):
                return self.input_widget.toPlainText()
            return self.input_widget.text()
        elif isinstance(self.input_widget, (QSpinBox, QDoubleSpinBox)):
            return self.input_widget.value()
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        return None
    
    def set_value(self, value):
        """Set field value"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(str(value))
        elif isinstance(self.input_widget, (QSpinBox, QDoubleSpinBox)):
            self.input_widget.setValue(value)
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
    
    def validate(self):
        """Validate field value"""
        value = self.get_value()
        
        # Required validation
        if self.required and (not value or (isinstance(value, str) and not value.strip())):
            self.show_error("This field is required")
            return False
        
        # Custom validator
        if self.validator and value:
            is_valid, error_msg = self.validator(value)
            if not is_valid:
                self.show_error(error_msg)
                return False
        
        self.clear_error()
        return True
    
    def show_error(self, message: str) -> None:
        """Show validation error"""
        self.error_label.setText(message)
        self.error_label.show()

        # Highlight input
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            theme = get_current_theme()
            base_qss = ThemeLoader.generate_qss("input", "default", theme)
            error_qss = f"""
                {base_qss}
                QLineEdit, QTextEdit {{
                    border-color: {ColorPalette.DANGER};
                }}
            """
            self.input_widget.setStyleSheet(error_qss)
    
    def clear_error(self) -> None:
        """Clear validation error"""
        self.error_label.hide()

        # Reset input style
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            theme = get_current_theme()
            qss = ThemeLoader.generate_qss("input", "default", theme)
            self.input_widget.setStyleSheet(qss)


class Card(BaseComponent):
    """Themed card/panel component"""
    
    def __init__(self, title=None, padding=Spacing.MEDIUM):
        super().__init__()
        self.title = title
        self.padding = padding
        self.content_layout = None
    
    def create(self):
        """Create card widget"""
        container = QFrame()
        container.setObjectName("card")

        # Apply theme
        theme = get_current_theme()
        qss = ThemeLoader.generate_qss("card", "default", theme)
        container.setStyleSheet(qss)

        layout = QVBoxLayout(container)
        padding = self.padding
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(Spacing.NORMAL)
        
        # Title if provided
        if self.title:
            title_label = Label(self.title, variant="heading").get_widget()
            layout.addWidget(title_label)
            
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.BORDER};
                    max-height: 1px;
                }}
            """)
            layout.addWidget(separator)
        
        # Content layout
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(Spacing.NORMAL)
        layout.addLayout(self.content_layout)
        
        return container
    
    def add_widget(self, widget):
        """Add widget to card content"""
        self.get_widget()  # Ensure created
        self.content_layout.addWidget(widget)
    
    def add_component(self, component):
        """Add component to card content"""
        self.add_widget(component.get_widget())


class ButtonGroup(BaseComponent):
    """Group of buttons with consistent styling"""
    
    def __init__(self, buttons, alignment="right", spacing=Spacing.SMALL):
        super().__init__()
        self.buttons = buttons  # List of (text, variant, callback)
        self.alignment = alignment
        self.spacing = spacing
        self.button_widgets = {}
    
    def create(self):
        """Create button group"""
        container = QWidget()
        container.setObjectName("button_group")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.spacing)
        
        # Add stretch based on alignment
        if self.alignment == "right":
            layout.addStretch()
        
        # Create buttons
        for btn_config in self.buttons:
            text = btn_config.get("text", "Button")
            variant = btn_config.get("variant", ButtonVariant.SECONDARY)
            callback = btn_config.get("callback")
            min_width = btn_config.get("min_width", 100)
            
            button = Button(text, variant, min_width=min_width)
            
            if callback:
                button.clicked.connect(callback)
            
            layout.addWidget(button.get_widget())
            self.button_widgets[text] = button
        
        # Add stretch for other alignments
        if self.alignment == "left":
            layout.addStretch()
        elif self.alignment == "center":
            layout.insertStretch(0)
            layout.addStretch()
        
        return container
    
    def get_button(self, text):
        """Get button by text"""
        return self.button_widgets.get(text)


# Convenience functions
def create_form_layout(*fields):
    """Create vertical layout with form fields"""
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setSpacing(Spacing.MEDIUM)
    layout.setContentsMargins(0, 0, 0, 0)
    
    for field in fields:
        if isinstance(field, BaseComponent):
            layout.addWidget(field.get_widget())
        else:
            layout.addWidget(field)
    
    return container


def create_horizontal_group(*items, spacing=Spacing.NORMAL):
    """Create horizontal layout with items"""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setSpacing(spacing)
    layout.setContentsMargins(0, 0, 0, 0)
    
    for item in items:
        if isinstance(item, BaseComponent):
            layout.addWidget(item.get_widget())
        elif isinstance(item, str) and item == "stretch":
            layout.addStretch()
        else:
            layout.addWidget(item)
    
    return container
