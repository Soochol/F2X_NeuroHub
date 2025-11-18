"""F2X NeuroHub MES - UI Constants

Centralized constants for spacing, typography, colors, and other UI values.
"""


class Spacing:
    """Spacing constants (pixels)"""
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
    """Border radius constants (pixels)"""
    NONE = 0
    SMALL = 2
    NORMAL = 4
    MEDIUM = 6
    LARGE = 8
    XLARGE = 12
    ROUND = 9999


class Typography:
    """Typography constants"""
    FONT_FAMILY = "맑은 고딕, Malgun Gothic, sans-serif"

    # Font sizes
    SIZE_SMALL = 11
    SIZE_NORMAL = 13
    SIZE_MEDIUM = 14
    SIZE_LARGE = 16
    SIZE_XLARGE = 20
    SIZE_XXLARGE = 24
    SIZE_HUGE = 32

    # Font weights
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


class ColorPalette:
    """F2X MES Color Palette"""

    # Primary colors
    PRIMARY_MAIN = "#1976d2"
    PRIMARY_DARK = "#1565c0"
    PRIMARY_LIGHT = "#42a5f5"
    PRIMARY_CONTRAST = "#ffffff"

    # Success (착공 - 작업 시작)
    SUCCESS_MAIN = "#2e7d32"
    SUCCESS_DARK = "#1b5e20"
    SUCCESS_LIGHT = "#4caf50"
    SUCCESS_CONTRAST = "#ffffff"

    # Completed (완공 - 작업 완료)
    COMPLETED_MAIN = "#f57c00"
    COMPLETED_DARK = "#e65100"
    COMPLETED_LIGHT = "#ff9800"
    COMPLETED_CONTRAST = "#ffffff"

    # Danger (불합격 - 실패)
    DANGER_MAIN = "#d32f2f"
    DANGER_DARK = "#c62828"
    DANGER_LIGHT = "#f44336"
    DANGER_CONTRAST = "#ffffff"

    # In Progress (진행중)
    IN_PROGRESS_MAIN = "#0288d1"
    IN_PROGRESS_DARK = "#01579b"
    IN_PROGRESS_LIGHT = "#03a9f4"
    IN_PROGRESS_CONTRAST = "#ffffff"

    # Neutral
    GREY_50 = "#fafafa"
    GREY_100 = "#f5f5f5"
    GREY_200 = "#eeeeee"
    GREY_300 = "#e0e0e0"
    GREY_400 = "#bdbdbd"
    GREY_500 = "#9e9e9e"
    GREY_600 = "#757575"
    GREY_700 = "#616161"
    GREY_800 = "#424242"
    GREY_900 = "#212121"

    # Background
    BG_DEFAULT = "#f5f5f5"
    BG_PAPER = "#ffffff"
    BG_HOVER = "#eeeeee"
    BG_SIDEBAR = "#263238"
    BG_SIDEBAR_HOVER = "#37474f"

    # Text
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#bdbdbd"
    TEXT_ON_DARK = "#ffffff"

    # Borders
    BORDER_DEFAULT = "#e0e0e0"
    BORDER_DARK = "#bdbdbd"


class Layout:
    """Layout constants"""
    SIDEBAR_WIDTH = 220
    HEADER_HEIGHT = 64
    FOOTER_HEIGHT = 32
    CONTENT_MAX_WIDTH = 1200
