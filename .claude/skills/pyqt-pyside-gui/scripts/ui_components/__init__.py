"""
UI Components Package

Centralized, reusable UI components with JSON-based theming.

Quick Start:
    from ui_components import *
    
    # Load and apply theme
    app = QApplication(sys.argv)
    theme = load_theme(app, "default")  # or "dark"
    
    # Use components
    button = Button("Click Me", variant="primary")
    input_field = Input(placeholder="Enter text...")
    form_field = FormField("Email", required=True)
    
    # Switch theme at runtime
    load_theme(app, "dark")
"""

from .theme_loader import ThemeLoader, Theme, load_and_apply_theme
from .components import (
    Button,
    Input,
    Label,
    FormField,
    Card,
    ButtonGroup,
    create_form_layout,
    create_horizontal_group
)
from .constants import (
    ColorPalette,
    Typography,
    Spacing,
    BorderRadius,
    ButtonVariant,
    InputVariant,
    LabelVariant,
    ZIndex
)

# Convenience function
def load_theme(app, theme_name: str = "default") -> Theme:
    """Load and apply theme to application"""
    return load_and_apply_theme(app, theme_name)

def list_themes():
    """List available themes"""
    return ThemeLoader.list_available_themes()

def get_theme():
    """Get current theme"""
    return ThemeLoader.get_current_theme()

__all__ = [
    # Theme functions
    'load_theme',
    'list_themes',
    'get_theme',
    'Theme',
    'ThemeLoader',

    # Components
    'Button',
    'Input',
    'Label',
    'FormField',
    'Card',
    'ButtonGroup',
    'create_form_layout',
    'create_horizontal_group',

    # Constants
    'ColorPalette',
    'Typography',
    'Spacing',
    'BorderRadius',
    'ButtonVariant',
    'InputVariant',
    'LabelVariant',
    'ZIndex',
]
