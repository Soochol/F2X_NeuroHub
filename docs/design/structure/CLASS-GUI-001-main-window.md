---
id: CLASS-GUI-001
module: gui
title: MainWindow Class Design
type: class_structure
status: Draft
created_date: 2025-11-12T22:48:16Z
---

# MainWindow Class Design

## Overview

This document defines the class structure and design for the `MainWindow` class, which is the main application window for SimplePySideApp. It inherits from `QMainWindow` and is responsible for setting up the UI, managing the window state, and coordinating interactions between menus and action handlers.

## Class Diagram (Text Format)

```
┌─────────────────────────────────────────────────────────────┐
│                    <<Qt Class>>                             │
│                    QMainWindow                              │
│              (from PySide6.QtWidgets)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ inherits
                            ▲
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                      MainWindow                             │
├─────────────────────────────────────────────────────────────┤
│  Attributes:                                                │
│  - _file_handler: FileActionHandler                         │
│  - _edit_handler: EditActionHandler                         │
│  - _help_handler: HelpActionHandler                         │
│  - _central_widget: QWidget                                 │
│  - _menu_bar: QMenuBar                                      │
│                                                             │
│  Constants:                                                 │
│  + WINDOW_TITLE: str = "SimplePySideApp"                    │
│  + DEFAULT_WIDTH: int = 800                                 │
│  + DEFAULT_HEIGHT: int = 600                                │
│  + MIN_WIDTH: int = 400                                     │
│  + MIN_HEIGHT: int = 300                                    │
├─────────────────────────────────────────────────────────────┤
│  Methods:                                                   │
│  + __init__() -> None                                       │
│  - _init_ui() -> None                                       │
│  - _setup_window_properties() -> None                       │
│  - _create_central_widget() -> None                         │
│  - _create_menu_bar() -> None                               │
│  - _connect_actions() -> None                               │
│  + closeEvent(event: QCloseEvent) -> None                   │
└─────────────────────────────────────────────────────────────┘
           │
           │ creates
           ▼
┌──────────────────────────────────────────────────────────┐
│                   QWidget                                │
│              (Central Widget)                            │
│                [Empty Area]                              │
└──────────────────────────────────────────────────────────┘

           │
           │ creates
           ▼
┌──────────────────────────────────────────────────────────┐
│                   QMenuBar                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ FileMenu    │  │ EditMenu    │  │ HelpMenu    │    │
│  │ (QMenu)     │  │ (QMenu)     │  │ (QMenu)     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└──────────────────────────────────────────────────────────┘

           │
           │ creates
           ▼
┌──────────────────────────────────────────────────────────┐
│              Action Handlers                             │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │FileActionHandler │  │EditActionHandler │            │
│  └──────────────────┘  └──────────────────┘            │
│  ┌──────────────────┐                                   │
│  │HelpActionHandler │                                   │
│  └──────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

## Class Definition

### MainWindow

**Inherits**: `QMainWindow` (from PySide6.QtWidgets)

**Responsibility**: Main application window, coordinates UI setup and action handling

**File**: `app/presentation/main_window.py`

## Attributes

### Instance Attributes

```python
_file_handler: FileActionHandler
```
**Type**: `FileActionHandler`
**Visibility**: Private
**Description**: Handler for File menu actions (New, Open, Save, Exit)
**Initialized**: In `__init__()` after UI setup

```python
_edit_handler: EditActionHandler
```
**Type**: `EditActionHandler`
**Visibility**: Private
**Description**: Handler for Edit menu actions (Undo, Redo)
**Initialized**: In `__init__()` after UI setup

```python
_help_handler: HelpActionHandler
```
**Type**: `HelpActionHandler`
**Visibility**: Private
**Description**: Handler for Help menu actions (About)
**Initialized**: In `__init__()` after UI setup

```python
_central_widget: QWidget
```
**Type**: `QWidget`
**Visibility**: Private
**Description**: Empty central widget (placeholder for future content)
**Initialized**: In `_create_central_widget()`

```python
_menu_bar: QMenuBar
```
**Type**: `QMenuBar`
**Visibility**: Private
**Description**: Menu bar containing File, Edit, Help menus
**Initialized**: In `_create_menu_bar()`

### Class Constants

```python
WINDOW_TITLE: str = "SimplePySideApp"
```
**Description**: Default window title

```python
DEFAULT_WIDTH: int = 800
```
**Description**: Default window width in pixels

```python
DEFAULT_HEIGHT: int = 600
```
**Description**: Default window height in pixels

```python
MIN_WIDTH: int = 400
```
**Description**: Minimum window width in pixels (from BR-GUI-002)

```python
MIN_HEIGHT: int = 300
```
**Description**: Minimum window height in pixels (from BR-GUI-002)

## Methods

### Public Methods

#### `__init__(self) -> None`

**Purpose**: Initialize MainWindow and set up UI

**Parameters**: None

**Returns**: None

**Behavior**:
1. Call `super().__init__()` to initialize QMainWindow
2. Call `_init_ui()` to set up UI components
3. Initialize action handlers
4. Connect signals to slots

**Example**:
```python
def __init__(self):
    """Initialize the main window."""
    super().__init__()
    self._init_ui()
```

**Requirements**: FR-GUI-001 (AC-GUI-001-01)

---

#### `closeEvent(self, event: QCloseEvent) -> None`

**Purpose**: Handle window close event (override QMainWindow method)

**Parameters**:
- `event` (QCloseEvent): Close event object

**Returns**: None

**Behavior**:
1. Accept the close event
2. Trigger application exit (QApplication.quit())
3. Ensure clean termination (BR-GUI-001)

**Example**:
```python
def closeEvent(self, event: QCloseEvent) -> None:
    """Handle window close event."""
    event.accept()
    # Exit action handler will clean up
```

**Requirements**: FR-GUI-001 (BR-GUI-001), FR-GUI-002 (AC-GUI-002-05)

---

### Private Methods

#### `_init_ui(self) -> None`

**Purpose**: Initialize all UI components

**Parameters**: None

**Returns**: None

**Behavior**:
1. Call `_setup_window_properties()`
2. Call `_create_central_widget()`
3. Call `_create_menu_bar()`
4. Call `_connect_actions()`

**Example**:
```python
def _init_ui(self) -> None:
    """Initialize UI components."""
    self._setup_window_properties()
    self._create_central_widget()
    self._create_menu_bar()
    self._connect_actions()
```

---

#### `_setup_window_properties(self) -> None`

**Purpose**: Set window title, size, and constraints

**Parameters**: None

**Returns**: None

**Behavior**:
1. Set window title to `WINDOW_TITLE`
2. Set default size to `DEFAULT_WIDTH` x `DEFAULT_HEIGHT`
3. Set minimum size to `MIN_WIDTH` x `MIN_HEIGHT`
4. Center window on screen (optional)

**Example**:
```python
def _setup_window_properties(self) -> None:
    """Set up window properties."""
    self.setWindowTitle(self.WINDOW_TITLE)
    self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
    self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
```

**Requirements**: FR-GUI-001 (AC-GUI-001-01, BR-GUI-002)

---

#### `_create_central_widget(self) -> None`

**Purpose**: Create and set empty central widget

**Parameters**: None

**Returns**: None

**Behavior**:
1. Create QWidget instance
2. Set as central widget using `setCentralWidget()`

**Example**:
```python
def _create_central_widget(self) -> None:
    """Create central widget."""
    self._central_widget = QWidget()
    self.setCentralWidget(self._central_widget)
```

**Requirements**: FR-GUI-001 (AC-GUI-001-01), FR-GUI-003 (AC-GUI-003-19)

---

#### `_create_menu_bar(self) -> None`

**Purpose**: Create menu bar with File, Edit, Help menus

**Parameters**: None

**Returns**: None

**Behavior**:
1. Import `create_menu_bar` from `menu_bar.py`
2. Call `create_menu_bar(self)` to get configured QMenuBar
3. Set menu bar using `setMenuBar()`
4. Store reference in `_menu_bar`

**Example**:
```python
def _create_menu_bar(self) -> None:
    """Create menu bar."""
    from app.presentation.menu_bar import create_menu_bar
    self._menu_bar = create_menu_bar(self)
    self.setMenuBar(self._menu_bar)
```

**Requirements**: FR-GUI-002 (AC-GUI-002-01 through AC-GUI-002-09)

---

#### `_connect_actions(self) -> None`

**Purpose**: Connect menu actions to handler methods

**Parameters**: None

**Returns**: None

**Behavior**:
1. Create `FileActionHandler` instance
2. Create `EditActionHandler` instance
3. Create `HelpActionHandler` instance
4. Find QAction objects in menus by name
5. Connect `triggered` signals to handler methods

**Example**:
```python
def _connect_actions(self) -> None:
    """Connect menu actions to handlers."""
    from app.handlers.file_actions import FileActionHandler
    from app.handlers.edit_actions import EditActionHandler
    from app.handlers.help_actions import HelpActionHandler

    self._file_handler = FileActionHandler(self)
    self._edit_handler = EditActionHandler(self)
    self._help_handler = HelpActionHandler(self)

    # Connect File menu actions
    file_menu = self._menu_bar.findChild(QMenu, "File")
    for action in file_menu.actions():
        if action.text() == "New":
            action.triggered.connect(self._file_handler.on_new)
        elif action.text() == "Open":
            action.triggered.connect(self._file_handler.on_open)
        # ... etc
```

**Requirements**: All FR-GUI-002 acceptance criteria

---

## Method Call Sequence

### Application Startup

```
main.py: main()
    ↓
MainWindow.__init__()
    ↓
MainWindow._init_ui()
    ├─→ _setup_window_properties()
    │   └─→ setWindowTitle(), resize(), setMinimumSize()
    │
    ├─→ _create_central_widget()
    │   └─→ QWidget(), setCentralWidget()
    │
    ├─→ _create_menu_bar()
    │   └─→ create_menu_bar(self)
    │       └─→ create_file_menu(), create_edit_menu(), create_help_menu()
    │
    └─→ _connect_actions()
        ├─→ FileActionHandler(self)
        ├─→ EditActionHandler(self)
        ├─→ HelpActionHandler(self)
        └─→ action.triggered.connect(handler.method)
```

### Window Close

```
User clicks close button
    ↓
MainWindow.closeEvent(event)
    ↓
event.accept()
    ↓
QApplication.quit()
    ↓
Exit event loop
```

## Dependencies

### Imports Required

```python
from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QMenu
from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent

from app.presentation.menu_bar import create_menu_bar
from app.handlers.file_actions import FileActionHandler
from app.handlers.edit_actions import EditActionHandler
from app.handlers.help_actions import HelpActionHandler
```

## State Management

### Window States

| State | Description | Method |
|-------|-------------|--------|
| **Normal** | Default window state (800x600) | `showNormal()` |
| **Minimized** | Hidden in taskbar | `showMinimized()` |
| **Maximized** | Fills screen | `showMaximized()` |
| **Closing** | Cleanup and exit | `closeEvent()` |

### State Transitions

```
Normal ←→ Minimized (user clicks minimize/restore)
Normal ←→ Maximized (user clicks maximize/restore)
Any State → Closing (user clicks close or Exit action)
```

## Error Handling

### Initialization Errors

```python
def __init__(self):
    """Initialize the main window."""
    try:
        super().__init__()
        self._init_ui()
    except Exception as e:
        print(f"Failed to initialize window: {e}")
        raise
```

### Close Event Errors

```python
def closeEvent(self, event: QCloseEvent) -> None:
    """Handle window close event."""
    try:
        event.accept()
        # Cleanup if needed
    except Exception as e:
        print(f"Error during window close: {e}")
        event.accept()  # Close anyway
```

## Design Patterns Applied

### 1. Facade Pattern
**Application**: `MainWindow` acts as facade for entire UI
- Hides complexity of menu creation, action handlers
- Provides simple interface: `MainWindow().show()`

### 2. Coordinator Pattern
**Application**: `MainWindow` coordinates UI components
- Menus don't know about handlers
- Handlers don't know about menu creation
- `MainWindow` connects them

### 3. Dependency Injection
**Application**: Action handlers injected via constructor
- `FileActionHandler(self)` receives parent window
- Enables testing with mock parent

## Testing Strategy

### Unit Tests

```python
def test_window_initialization(qtbot):
    """Test MainWindow initializes correctly."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.windowTitle() == "SimplePySideApp"
    assert window.width() == 800
    assert window.height() == 600
    assert window.minimumWidth() == 400
    assert window.minimumHeight() == 300
```

### Integration Tests

```python
def test_menu_bar_creation(qtbot):
    """Test MainWindow creates menu bar."""
    window = MainWindow()
    qtbot.addWidget(window)

    menu_bar = window.menuBar()
    assert menu_bar is not None

    menus = [action.text() for action in menu_bar.actions()]
    assert "File" in menus
    assert "Edit" in menus
    assert "Help" in menus
```

## Example Implementation

### Complete MainWindow Class

```python
"""
Main application window for SimplePySideApp.

Requirements:
    - FR-GUI-001: Main Window and Application Structure
    - FR-GUI-002: Menu System and Actions
"""

from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtGui import QCloseEvent

from app.presentation.menu_bar import create_menu_bar
from app.handlers.file_actions import FileActionHandler
from app.handlers.edit_actions import EditActionHandler
from app.handlers.help_actions import HelpActionHandler


class MainWindow(QMainWindow):
    """Main application window."""

    WINDOW_TITLE = "SimplePySideApp"
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    MIN_WIDTH = 400
    MIN_HEIGHT = 300

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        self._setup_window_properties()
        self._create_central_widget()
        self._create_menu_bar()
        self._connect_actions()

    def _setup_window_properties(self) -> None:
        """Set up window properties."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

    def _create_central_widget(self) -> None:
        """Create central widget."""
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)

    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        self._menu_bar = create_menu_bar(self)
        self.setMenuBar(self._menu_bar)

    def _connect_actions(self) -> None:
        """Connect menu actions to handlers."""
        self._file_handler = FileActionHandler(self)
        self._edit_handler = EditActionHandler(self)
        self._help_handler = HelpActionHandler(self)

        # File menu connections
        file_menu = self.menuBar().actions()[0].menu()
        for action in file_menu.actions():
            if not action.isSeparator():
                text = action.text().replace("&", "")
                if text == "New":
                    action.triggered.connect(self._file_handler.on_new)
                elif text == "Open":
                    action.triggered.connect(self._file_handler.on_open)
                elif text == "Save":
                    action.triggered.connect(self._file_handler.on_save)
                elif text == "Exit":
                    action.triggered.connect(self._file_handler.on_exit)

        # Edit menu connections
        edit_menu = self.menuBar().actions()[1].menu()
        for action in edit_menu.actions():
            text = action.text().replace("&", "")
            if text == "Undo":
                action.triggered.connect(self._edit_handler.on_undo)
            elif text == "Redo":
                action.triggered.connect(self._edit_handler.on_redo)

        # Help menu connections
        help_menu = self.menuBar().actions()[2].menu()
        for action in help_menu.actions():
            text = action.text().replace("&", "")
            if text == "About":
                action.triggered.connect(self._help_handler.on_about)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        event.accept()
```

## Revision History

| Version | Date       | Author        | Changes                          |
|---------|------------|---------------|----------------------------------|
| 1.0     | 2025-11-12 | Design Agent  | Initial MainWindow class design  |
