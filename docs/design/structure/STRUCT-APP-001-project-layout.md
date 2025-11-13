---
id: STRUCT-APP-001
title: SimplePySideApp Project Structure Design
module: gui
type: project_structure
status: Draft
created_date: 2025-11-12T22:48:16Z
architecture: Layered + MVP
language: Python
---

# SimplePySideApp Project Structure Design

## Overview

This document defines the complete project folder structure, module organization, and file layout for SimplePySideApp, a PySide6 desktop GUI application following Layered Architecture with MVP pattern.

## Root Structure

```
SimplePySideApp/
├── app/                        # Application source code
├── tests/                      # Test files
├── docs/                       # Documentation
├── resources/                  # Resources (icons, images, translations)
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup
├── README.md                   # Project overview
└── LICENSE                     # License file
```

## Application Structure (app/)

### Layered Architecture Layout

```
app/
├── __init__.py                 # Package initialization
├── main.py                     # Application entry point
│
├── presentation/               # Presentation Layer (View)
│   ├── __init__.py
│   ├── main_window.py          # MainWindow class (QMainWindow)
│   ├── menu_bar.py             # Menu bar setup and organization
│   └── dialogs/                # Custom dialogs (future)
│       └── __init__.py
│
├── handlers/                   # Event Handlers (Presenter)
│   ├── __init__.py
│   ├── file_actions.py         # File menu action handlers
│   ├── edit_actions.py         # Edit menu action handlers
│   └── help_actions.py         # Help menu action handlers
│
├── models/                     # Application State (Model)
│   ├── __init__.py
│   └── app_state.py            # Application state model (future)
│
└── utils/                      # Utilities
    ├── __init__.py
    ├── validators.py           # Window geometry validation
    └── error_handler.py        # Error handling utilities
```

## Detailed File Descriptions

### app/main.py
**Purpose**: Application entry point

**Responsibilities**:
- Parse command-line arguments (if any)
- Check PySide6 availability
- Initialize QApplication
- Create and show MainWindow
- Enter Qt event loop
- Handle startup errors

**Expected Code Structure**:
```python
#!/usr/bin/env python3
"""
SimplePySideApp - A simple PySide6 desktop application
"""

import sys

def check_dependencies():
    """Check if PySide6 is available."""
    try:
        from PySide6 import QtWidgets
    except ModuleNotFoundError:
        print("PySide6 not found. Install with: pip install PySide6")
        sys.exit(1)

def main():
    """Main application entry point."""
    check_dependencies()

    from PySide6.QtWidgets import QApplication
    from app.presentation.main_window import MainWindow

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Cannot initialize display: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### app/presentation/main_window.py
**Purpose**: Main application window

**Responsibilities**:
- Initialize QMainWindow
- Set window properties (title, size, minimum size)
- Create central widget
- Set up menu bar
- Connect signals to handlers

**Class**: `MainWindow(QMainWindow)`

**Key Methods**:
- `__init__()` - Initialize window
- `_init_ui()` - Set up UI elements
- `_create_menu_bar()` - Create menu bar
- `closeEvent(event)` - Handle window close

### app/presentation/menu_bar.py
**Purpose**: Menu bar setup and configuration

**Responsibilities**:
- Create File, Edit, Help menus
- Create QAction objects for each menu item
- Set keyboard shortcuts
- Add separators
- Return configured QMenuBar

**Functions**:
- `create_menu_bar(parent) -> QMenuBar`
- `create_file_menu(parent) -> QMenu`
- `create_edit_menu(parent) -> QMenu`
- `create_help_menu(parent) -> QMenu`

### app/handlers/file_actions.py
**Purpose**: File menu action handlers

**Responsibilities**:
- Handle File → New action
- Handle File → Open action
- Handle File → Save action
- Handle File → Exit action

**Class**: `FileActionHandler`

**Methods**:
- `__init__(parent)`
- `on_new()` - Show "New clicked" message
- `on_open()` - Show "Open clicked" message
- `on_save()` - Show "Save clicked" message
- `on_exit()` - Close application cleanly

### app/handlers/edit_actions.py
**Purpose**: Edit menu action handlers

**Responsibilities**:
- Handle Edit → Undo action
- Handle Edit → Redo action

**Class**: `EditActionHandler`

**Methods**:
- `__init__(parent)`
- `on_undo()` - Show "Undo clicked" message
- `on_redo()` - Show "Redo clicked" message

### app/handlers/help_actions.py
**Purpose**: Help menu action handlers

**Responsibilities**:
- Handle Help → About action

**Class**: `HelpActionHandler`

**Methods**:
- `__init__(parent)`
- `on_about()` - Show About dialog

### app/utils/validators.py
**Purpose**: Validation utilities

**Responsibilities**:
- Validate window geometry
- Ensure window position is on-screen
- Enforce minimum/maximum size constraints

**Functions**:
- `validate_window_geometry(x, y, width, height, screen_geometry) -> tuple`
- `is_position_on_screen(x, y, screen_geometry) -> bool`

### app/utils/error_handler.py
**Purpose**: Global error handling

**Responsibilities**:
- Log errors
- Show user-friendly error dialogs
- Prevent application crashes

**Functions**:
- `handle_exception(exc_type, exc_value, exc_traceback)`
- `show_error_dialog(title, message)`

## Test Structure (tests/)

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures and configuration
│
├── unit/                       # Unit tests (70% coverage)
│   ├── __init__.py
│   ├── test_main_window.py     # Test MainWindow class
│   ├── test_menu_bar.py        # Test menu bar creation
│   ├── test_file_actions.py    # Test FileActionHandler
│   ├── test_edit_actions.py    # Test EditActionHandler
│   ├── test_help_actions.py    # Test HelpActionHandler
│   └── test_validators.py      # Test validation utilities
│
├── integration/                # Integration tests (20% coverage)
│   ├── __init__.py
│   ├── test_menu_interactions.py     # Test menu click → handler flow
│   ├── test_keyboard_shortcuts.py    # Test shortcuts trigger actions
│   └── test_window_states.py        # Test minimize, maximize, restore
│
└── e2e/                        # End-to-end tests (10% coverage)
    ├── __init__.py
    └── test_complete_workflow.py    # Test full user workflows
```

## Module Organization Principles

### 1. Layered Separation
- **Presentation Layer** (`presentation/`): Pure Qt UI code
- **Presenter Layer** (`handlers/`): Event handling logic
- **Model Layer** (`models/`): Application state (future)
- **Utility Layer** (`utils/`): Shared helpers

### 2. Single Responsibility Principle
- Each file has one clear purpose
- Each class handles one aspect of functionality
- Functions are small and focused

### 3. Dependency Direction
```
main.py
  ↓
presentation/ ←─── handlers/
  ↓                    ↓
models/ ←────────────┘
  ↓
utils/
```

**Rule**: Higher layers can depend on lower layers, but not vice versa.

### 4. Naming Conventions
- **Packages**: lowercase, snake_case (e.g., `file_actions`, `main_window`)
- **Modules**: lowercase, snake_case (e.g., `file_actions.py`)
- **Classes**: PascalCase (e.g., `FileActionHandler`, `MainWindow`)
- **Functions**: lowercase, snake_case (e.g., `create_menu_bar()`)
- **Constants**: UPPER_CASE (e.g., `DEFAULT_WIDTH`, `MIN_HEIGHT`)

### 5. File Organization
- **One main class per file** (unless tightly coupled)
- **Related functions in same file**
- **Keep files small** (< 300 lines)

## Resources Structure (resources/)

```
resources/
├── icons/                      # Application icons (future)
│   ├── app.ico                 # Windows icon
│   ├── app.icns                # macOS icon
│   └── app.png                 # Linux icon
│
├── images/                     # UI images (future)
│   └── about_logo.png
│
└── translations/               # i18n files (future)
    ├── en_US.qm
    └── ko_KR.qm
```

## Documentation Structure (docs/)

```
docs/
├── requirements/               # Requirements documents (from requirements-agent)
│   └── modules/
│       └── gui/
│           ├── FR-GUI-001-main-window-and-application-structure.md
│           ├── FR-GUI-002-menu-system-and-actions.md
│           ├── FR-GUI-003-user-interface-interactions.md
│           └── AC-GUI-001-test-plan.md
│
├── design/                     # Design documents (from design-agent)
│   ├── architecture/
│   │   └── ARCH-APP-001.md
│   ├── structure/
│   │   ├── STRUCT-APP-001-project-layout.md (this file)
│   │   ├── CLASS-GUI-001-main-window.md
│   │   └── CLASS-GUI-002-menu-system.md
│   └── component/
│       └── COMP-GUI-001-architecture.md
│
└── progress/                   # Progress tracking (from all agents)
    ├── requirements/
    │   └── gui/
    ├── design/
    │   └── gui/
    ├── testing/
    │   └── gui/
    └── implementation/
        └── gui/
```

## Configuration Files

### requirements.txt
```txt
PySide6>=6.0.0
```

### requirements-dev.txt
```txt
PySide6>=6.0.0
pytest>=7.0.0
pytest-qt>=4.0.0
pytest-cov>=4.0.0
mypy>=1.0.0
black>=23.0.0
flake8>=6.0.0
```

### .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

## Rationale for Structure

### Why Separate handlers/ from presentation/?
- **Testability**: Handlers can be tested without Qt widgets
- **Single Responsibility**: Presentation creates UI, handlers handle logic
- **Reusability**: Handlers could be reused with different UI frameworks

### Why menu_bar.py separate from main_window.py?
- **Organization**: Menu setup is complex enough to warrant separate file
- **Maintainability**: Easy to find and update menu structure
- **Testability**: Can test menu creation independently

### Why utils/ layer?
- **DRY Principle**: Avoid code duplication
- **Reusability**: Validators and error handlers used across app
- **Clarity**: Clear where to find utility functions

### Why models/ layer (currently unused)?
- **Future-proofing**: Ready for application state management
- **Scalability**: Easy to add models as app grows
- **Architecture**: Completes MVP pattern

## File Size Guidelines

| Layer | Target LOC per File | Rationale |
|-------|-------------------|-----------|
| **main.py** | 50-80 | Entry point, minimal logic |
| **main_window.py** | 100-150 | Window setup, menu connections |
| **menu_bar.py** | 80-120 | Menu creation functions |
| **Action Handlers** | 60-100 each | Simple action methods |
| **Validators** | 50-80 | Utility functions |
| **Test Files** | 150-250 | Multiple test cases per file |

**Rule**: If file exceeds 300 lines, consider splitting into multiple files.

## Import Structure

### Preferred Import Style

```python
# Standard library
import sys
from typing import Optional

# Third-party (PySide6)
from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

# Local application
from app.presentation.menu_bar import create_menu_bar
from app.handlers.file_actions import FileActionHandler
from app.utils.validators import validate_window_geometry
```

**Rules**:
- Group imports: standard library, third-party, local
- Absolute imports preferred over relative
- One import per line for clarity
- Sort imports alphabetically within groups

## Module Dependencies

### Allowed Dependencies

```
presentation/ → handlers/ ✓ (presenters handle view events)
presentation/ → utils/ ✓ (views use validators)
handlers/ → models/ ✓ (presenters update models)
handlers/ → utils/ ✓ (handlers use utilities)
models/ → utils/ ✓ (models use validators)
```

### Forbidden Dependencies

```
handlers/ → presentation/ ✗ (presenters should not import views)
utils/ → handlers/ ✗ (utilities should be independent)
utils/ → presentation/ ✗ (utilities should be independent)
models/ → handlers/ ✗ (models should be independent)
models/ → presentation/ ✗ (models should be independent)
```

## Scalability Considerations

### How to Add New Features

**Add New Menu**:
1. Create new menu function in `menu_bar.py`
2. Create new handler class in `handlers/`
3. Update `main_window.py` to include new menu

**Add Complex Dialog**:
1. Create new dialog class in `presentation/dialogs/`
2. Create handler for dialog in `handlers/`
3. Connect from menu action

**Add Configuration**:
1. Create config model in `models/config.py`
2. Load config in `main.py`
3. Use config in handlers

**Add Persistence**:
1. Create repository classes in `repositories/` (new layer)
2. Call from handlers to save/load state

## Platform-Specific Considerations

### Cross-Platform Compatibility
- All paths use `os.path` or `pathlib` (platform-agnostic)
- No hard-coded file paths
- Resources accessed via resource system (future)

### Platform-Specific Resources
```
resources/
├── windows/
│   └── app.ico
├── macos/
│   └── app.icns
└── linux/
    └── app.desktop
```

## Build and Packaging Structure (Future)

```
SimplePySideApp/
├── setup.py                    # Python package setup
├── pyproject.toml              # Modern Python packaging
├── MANIFEST.in                 # Include non-Python files
├── build/                      # Build artifacts (gitignored)
├── dist/                       # Distribution packages (gitignored)
└── scripts/
    ├── build_windows.py        # Build Windows executable
    ├── build_macos.py          # Build macOS app bundle
    └── build_linux.py          # Build Linux package
```

## Summary

**Key Principles**:
- Clear layer separation (presentation, handlers, models, utils)
- Single Responsibility Principle (one purpose per file)
- Testable architecture (handlers separate from Qt)
- Scalable structure (easy to add features)
- Cross-platform compatibility (no platform-specific paths)

**Next Steps**:
1. Create directory structure
2. Implement main.py and main_window.py
3. Implement menu_bar.py
4. Implement action handlers
5. Write tests for each component

## Revision History

| Version | Date       | Author        | Changes                          |
|---------|------------|---------------|----------------------------------|
| 1.0     | 2025-11-12 | Design Agent  | Initial project structure design |
