"""
UI Component Constants

Design system constants for consistent spacing, colors, typography, and variants.
These values should match the JSON theme structure for consistency.
"""

from typing import Final


class ColorPalette:
    """Color constants - fallback values when theme is not loaded"""
    # Primary colors
    PRIMARY: Final[str] = "#3498db"
    PRIMARY_DARK: Final[str] = "#2980b9"
    PRIMARY_LIGHT: Final[str] = "#5dade2"

    # Secondary colors
    SECONDARY: Final[str] = "#95a5a6"
    SECONDARY_DARK: Final[str] = "#7f8c8d"
    SECONDARY_LIGHT: Final[str] = "#bdc3c7"

    # Semantic colors
    SUCCESS: Final[str] = "#2ecc71"
    DANGER: Final[str] = "#e74c3c"
    WARNING: Final[str] = "#f39c12"
    INFO: Final[str] = "#3498db"

    # Background colors
    BACKGROUND: Final[str] = "#ecf0f1"
    BACKGROUND_PAPER: Final[str] = "#ffffff"

    # Text colors
    TEXT_PRIMARY: Final[str] = "#2c3e50"
    TEXT_SECONDARY: Final[str] = "#7f8c8d"
    TEXT_DISABLED: Final[str] = "#bdc3c7"
    TEXT_CONTRAST: Final[str] = "#ffffff"

    # Border colors
    BORDER: Final[str] = "#bdc3c7"
    BORDER_LIGHT: Final[str] = "#ecf0f1"
    BORDER_DARK: Final[str] = "#95a5a6"


class Typography:
    """Typography constants"""
    # Font families
    FONT_FAMILY: Final[str] = "Segoe UI, Arial, sans-serif"
    FONT_FAMILY_MONO: Final[str] = "Consolas, Monaco, monospace"

    # Font sizes
    FONT_SIZE_XLARGE: Final[int] = 28
    FONT_SIZE_LARGE: Final[int] = 20
    FONT_SIZE_MEDIUM: Final[int] = 16
    FONT_SIZE_NORMAL: Final[int] = 14
    FONT_SIZE_SMALL: Final[int] = 12
    FONT_SIZE_XSMALL: Final[int] = 10

    # Font weights
    FONT_WEIGHT_LIGHT: Final[int] = 300
    FONT_WEIGHT_NORMAL: Final[int] = 400
    FONT_WEIGHT_MEDIUM: Final[int] = 500
    FONT_WEIGHT_BOLD: Final[int] = 700

    # Line heights
    LINE_HEIGHT_TIGHT: Final[float] = 1.2
    LINE_HEIGHT_NORMAL: Final[float] = 1.5
    LINE_HEIGHT_RELAXED: Final[float] = 1.8


class Spacing:
    """Spacing constants (in pixels)"""
    NONE: Final[int] = 0
    XXSMALL: Final[int] = 2
    XSMALL: Final[int] = 4
    SMALL: Final[int] = 8
    NORMAL: Final[int] = 12
    MEDIUM: Final[int] = 16
    LARGE: Final[int] = 24
    XLARGE: Final[int] = 32
    XXLARGE: Final[int] = 48


class BorderRadius:
    """Border radius constants (in pixels)"""
    NONE: Final[int] = 0
    SMALL: Final[int] = 2
    NORMAL: Final[int] = 4
    MEDIUM: Final[int] = 6
    LARGE: Final[int] = 8
    XLARGE: Final[int] = 12
    ROUND: Final[int] = 9999


class ButtonVariant:
    """Button variant constants"""
    PRIMARY: Final[str] = "primary"
    SECONDARY: Final[str] = "secondary"
    SUCCESS: Final[str] = "success"
    DANGER: Final[str] = "danger"
    WARNING: Final[str] = "warning"
    INFO: Final[str] = "info"
    OUTLINE: Final[str] = "outline"
    TEXT: Final[str] = "text"


class InputVariant:
    """Input variant constants"""
    DEFAULT: Final[str] = "default"
    ERROR: Final[str] = "error"
    SUCCESS: Final[str] = "success"


class LabelVariant:
    """Label variant constants"""
    NORMAL: Final[str] = "normal"
    HEADING: Final[str] = "heading"
    TITLE: Final[str] = "title"
    SUBTITLE: Final[str] = "subtitle"
    CAPTION: Final[str] = "caption"


class ZIndex:
    """Z-index constants for layering"""
    BASE: Final[int] = 0
    DROPDOWN: Final[int] = 1000
    MODAL_BACKDROP: Final[int] = 1040
    MODAL: Final[int] = 1050
    POPOVER: Final[int] = 1060
    TOOLTIP: Final[int] = 1070


# Convenience exports
__all__ = [
    'ColorPalette',
    'Typography',
    'Spacing',
    'BorderRadius',
    'ButtonVariant',
    'InputVariant',
    'LabelVariant',
    'ZIndex',
]
