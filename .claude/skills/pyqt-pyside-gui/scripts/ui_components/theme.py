"""
Design System Theme

Centralized theme configuration for consistent UI design.
All colors, fonts, spacing, and styling rules in one place.
"""

from enum import Enum


class ColorPalette:
    """Color palette - modify these to change your app's theme"""
    
    # Primary colors
    PRIMARY = "#3498db"          # Bright blue
    PRIMARY_DARK = "#2980b9"     # Darker blue
    PRIMARY_LIGHT = "#5dade2"    # Lighter blue
    
    # Secondary colors
    SECONDARY = "#95a5a6"        # Gray
    SECONDARY_DARK = "#7f8c8d"   # Darker gray
    SECONDARY_LIGHT = "#bdc3c7"  # Light gray
    
    # Semantic colors
    SUCCESS = "#2ecc71"          # Green
    SUCCESS_DARK = "#27ae60"
    SUCCESS_LIGHT = "#58d68d"
    
    DANGER = "#e74c3c"           # Red
    DANGER_DARK = "#c0392b"
    DANGER_LIGHT = "#ec7063"
    
    WARNING = "#f39c12"          # Orange
    WARNING_DARK = "#e67e22"
    WARNING_LIGHT = "#f8b739"
    
    INFO = "#3498db"             # Blue (same as primary)
    INFO_DARK = "#2980b9"
    INFO_LIGHT = "#5dade2"
    
    # Text colors
    TEXT_PRIMARY = "#2c3e50"     # Dark blue-gray
    TEXT_SECONDARY = "#7f8c8d"   # Medium gray
    TEXT_DISABLED = "#bdc3c7"    # Light gray
    TEXT_ON_PRIMARY = "#ffffff"  # White text on primary colors
    
    # Background colors
    BACKGROUND = "#ecf0f1"       # Light gray background
    SURFACE = "#ffffff"          # White surface
    SURFACE_HOVER = "#f8f9fa"    # Slightly darker on hover
    
    # Border colors
    BORDER = "#bdc3c7"           # Light gray border
    BORDER_DARK = "#95a5a6"      # Darker border
    BORDER_FOCUS = PRIMARY       # Primary color on focus
    
    # Special colors
    OVERLAY = "rgba(44, 62, 80, 0.5)"  # Semi-transparent overlay


class Typography:
    """Typography system"""
    
    # Font families
    FONT_FAMILY = "Segoe UI, Roboto, Arial, sans-serif"
    FONT_FAMILY_MONO = "Consolas, Monaco, Courier New, monospace"
    
    # Font sizes
    FONT_SIZE_XLARGE = 24
    FONT_SIZE_LARGE = 18
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_SMALL = 12
    FONT_SIZE_XSMALL = 10
    
    # Font weights
    FONT_WEIGHT_LIGHT = 300
    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_BOLD = 700
    
    # Line heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.8


class Spacing:
    """Spacing system (in pixels)"""
    
    NONE = 0
    XXSMALL = 2
    XSMALL = 4
    SMALL = 8
    NORMAL = 12
    MEDIUM = 16
    LARGE = 24
    XLARGE = 32
    XXLARGE = 48


class BorderRadius:
    """Border radius values"""
    
    NONE = 0
    SMALL = 2
    NORMAL = 4
    MEDIUM = 6
    LARGE = 8
    XLARGE = 12
    ROUND = 9999  # Fully rounded


class Shadow:
    """Shadow definitions"""
    
    NONE = "none"
    SMALL = "0 1px 3px rgba(0, 0, 0, 0.12)"
    NORMAL = "0 2px 6px rgba(0, 0, 0, 0.15)"
    LARGE = "0 4px 12px rgba(0, 0, 0, 0.15)"
    XLARGE = "0 8px 24px rgba(0, 0, 0, 0.15)"


class Transitions:
    """Animation transition durations (in milliseconds)"""
    
    FAST = 150
    NORMAL = 250
    SLOW = 350


class ButtonVariant(Enum):
    """Button style variants"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    OUTLINE = "outline"
    TEXT = "text"


class Theme:
    """Main theme class with pre-built stylesheets"""
    
    @staticmethod
    def button(variant=ButtonVariant.PRIMARY, size="normal"):
        """Get button stylesheet"""
        
        # Color mapping
        color_map = {
            ButtonVariant.PRIMARY: (ColorPalette.PRIMARY, ColorPalette.PRIMARY_DARK),
            ButtonVariant.SECONDARY: (ColorPalette.SECONDARY, ColorPalette.SECONDARY_DARK),
            ButtonVariant.SUCCESS: (ColorPalette.SUCCESS, ColorPalette.SUCCESS_DARK),
            ButtonVariant.DANGER: (ColorPalette.DANGER, ColorPalette.DANGER_DARK),
            ButtonVariant.WARNING: (ColorPalette.WARNING, ColorPalette.WARNING_DARK),
            ButtonVariant.INFO: (ColorPalette.INFO, ColorPalette.INFO_DARK),
        }
        
        # Size mapping
        size_map = {
            "small": (Spacing.XSMALL, Spacing.NORMAL, Typography.FONT_SIZE_SMALL),
            "normal": (Spacing.SMALL, Spacing.MEDIUM, Typography.FONT_SIZE_NORMAL),
            "large": (Spacing.MEDIUM, Spacing.LARGE, Typography.FONT_SIZE_LARGE),
        }
        
        padding_v, padding_h, font_size = size_map.get(size, size_map["normal"])
        
        if variant == ButtonVariant.OUTLINE:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {ColorPalette.PRIMARY};
                    border: 2px solid {ColorPalette.PRIMARY};
                    border-radius: {BorderRadius.NORMAL}px;
                    padding: {padding_v}px {padding_h}px;
                    font-size: {font_size}px;
                    font-weight: {Typography.FONT_WEIGHT_MEDIUM};
                    font-family: {Typography.FONT_FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {ColorPalette.PRIMARY_LIGHT};
                    color: white;
                    border-color: {ColorPalette.PRIMARY_LIGHT};
                }}
                QPushButton:pressed {{
                    background-color: {ColorPalette.PRIMARY_DARK};
                    border-color: {ColorPalette.PRIMARY_DARK};
                }}
                QPushButton:disabled {{
                    background-color: transparent;
                    color: {ColorPalette.TEXT_DISABLED};
                    border-color: {ColorPalette.BORDER};
                }}
            """
        
        elif variant == ButtonVariant.TEXT:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {ColorPalette.PRIMARY};
                    border: none;
                    padding: {padding_v}px {padding_h}px;
                    font-size: {font_size}px;
                    font-weight: {Typography.FONT_WEIGHT_MEDIUM};
                    font-family: {Typography.FONT_FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {ColorPalette.SURFACE_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {ColorPalette.BORDER};
                }}
                QPushButton:disabled {{
                    color: {ColorPalette.TEXT_DISABLED};
                }}
            """
        
        else:
            bg_color, bg_hover = color_map.get(variant, color_map[ButtonVariant.PRIMARY])
            
            return f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {ColorPalette.TEXT_ON_PRIMARY};
                    border: none;
                    border-radius: {BorderRadius.NORMAL}px;
                    padding: {padding_v}px {padding_h}px;
                    font-size: {font_size}px;
                    font-weight: {Typography.FONT_WEIGHT_MEDIUM};
                    font-family: {Typography.FONT_FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                }}
                QPushButton:pressed {{
                    background-color: {bg_hover};
                }}
                QPushButton:disabled {{
                    background-color: {ColorPalette.BORDER};
                    color: {ColorPalette.TEXT_DISABLED};
                }}
            """
    
    @staticmethod
    def input():
        """Get input field stylesheet"""
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {ColorPalette.SURFACE};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 2px solid {ColorPalette.BORDER};
                border-radius: {BorderRadius.NORMAL}px;
                padding: {Spacing.SMALL}px;
                font-size: {Typography.FONT_SIZE_NORMAL}px;
                font-family: {Typography.FONT_FAMILY};
                selection-background-color: {ColorPalette.PRIMARY};
                selection-color: {ColorPalette.TEXT_ON_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {ColorPalette.BORDER_FOCUS};
            }}
            QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                background-color: {ColorPalette.BACKGROUND};
                color: {ColorPalette.TEXT_DISABLED};
                border-color: {ColorPalette.BORDER};
            }}
        """
    
    @staticmethod
    def label(variant="normal"):
        """Get label stylesheet"""
        variants = {
            "title": (Typography.FONT_SIZE_XLARGE, Typography.FONT_WEIGHT_BOLD),
            "heading": (Typography.FONT_SIZE_LARGE, Typography.FONT_WEIGHT_BOLD),
            "normal": (Typography.FONT_SIZE_NORMAL, Typography.FONT_WEIGHT_NORMAL),
            "small": (Typography.FONT_SIZE_SMALL, Typography.FONT_WEIGHT_NORMAL),
            "caption": (Typography.FONT_SIZE_XSMALL, Typography.FONT_WEIGHT_NORMAL),
        }
        
        font_size, font_weight = variants.get(variant, variants["normal"])
        
        return f"""
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: {font_size}px;
                font-weight: {font_weight};
                font-family: {Typography.FONT_FAMILY};
            }}
        """
    
    @staticmethod
    def card():
        """Get card/panel stylesheet"""
        return f"""
            QWidget {{
                background-color: {ColorPalette.SURFACE};
                border: 1px solid {ColorPalette.BORDER};
                border-radius: {BorderRadius.MEDIUM}px;
            }}
        """
    
    @staticmethod
    def table():
        """Get table stylesheet"""
        return f"""
            QTableWidget, QTableView {{
                background-color: {ColorPalette.SURFACE};
                alternate-background-color: {ColorPalette.BACKGROUND};
                gridline-color: {ColorPalette.BORDER};
                border: 1px solid {ColorPalette.BORDER};
                border-radius: {BorderRadius.NORMAL}px;
                selection-background-color: {ColorPalette.PRIMARY_LIGHT};
                selection-color: {ColorPalette.TEXT_PRIMARY};
            }}
            QTableWidget::item, QTableView::item {{
                padding: {Spacing.SMALL}px;
            }}
            QTableWidget::item:hover, QTableView::item:hover {{
                background-color: {ColorPalette.SURFACE_HOVER};
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.BACKGROUND};
                color: {ColorPalette.TEXT_PRIMARY};
                padding: {Spacing.SMALL}px;
                border: none;
                border-bottom: 2px solid {ColorPalette.BORDER_DARK};
                font-weight: {Typography.FONT_WEIGHT_MEDIUM};
            }}
        """
    
    @staticmethod
    def combo_box():
        """Get combo box stylesheet"""
        return f"""
            QComboBox {{
                background-color: {ColorPalette.SURFACE};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 2px solid {ColorPalette.BORDER};
                border-radius: {BorderRadius.NORMAL}px;
                padding: {Spacing.SMALL}px;
                font-size: {Typography.FONT_SIZE_NORMAL}px;
                font-family: {Typography.FONT_FAMILY};
            }}
            QComboBox:hover {{
                border-color: {ColorPalette.PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {ColorPalette.BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {ColorPalette.SURFACE};
                border: 1px solid {ColorPalette.BORDER};
                selection-background-color: {ColorPalette.PRIMARY};
                selection-color: {ColorPalette.TEXT_ON_PRIMARY};
            }}
        """


# Convenience function
def apply_theme_to_app(app):
    """Apply global theme to QApplication"""
    global_style = f"""
        * {{
            font-family: {Typography.FONT_FAMILY};
        }}
        
        QWidget {{
            background-color: {ColorPalette.BACKGROUND};
            color: {ColorPalette.TEXT_PRIMARY};
        }}
        
        QMainWindow {{
            background-color: {ColorPalette.BACKGROUND};
        }}
        
        QToolTip {{
            background-color: {ColorPalette.TEXT_PRIMARY};
            color: {ColorPalette.TEXT_ON_PRIMARY};
            border: none;
            padding: {Spacing.XSMALL}px {Spacing.SMALL}px;
            border-radius: {BorderRadius.SMALL}px;
        }}
    """
    
    app.setStyleSheet(global_style)
