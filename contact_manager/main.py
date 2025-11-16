"""
Contact Manager Application

Entry point for the contact manager application.
Usage: python main.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Add ui_components to path
UI_COMPONENTS_PATH = Path(__file__).parent.parent / ".claude" / "skills" / "pyqt-pyside-gui" / "scripts"
sys.path.insert(0, str(UI_COMPONENTS_PATH))

from ui_components import load_theme
from contact_manager import ContactManager


def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)

    # IMPORTANT: Load theme BEFORE creating windows
    # Using custom contact-manager theme
    load_theme(app, "contact-manager")

    # Create and show main window
    window = ContactManager()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
