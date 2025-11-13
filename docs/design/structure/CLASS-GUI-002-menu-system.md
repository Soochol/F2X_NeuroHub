---
id: CLASS-GUI-002
module: gui
title: Menu System Class Design
type: class_structure
status: Draft
created_date: 2025-11-12T22:48:16Z
---

# Menu System Class Design

## Overview

This document defines the class structure for the menu system in SimplePySideApp, including menu creation functions and action handler classes. The menu system follows the Model-View-Presenter pattern, where menus are the View, action handlers are Presenters, and QActions connect them.

## Class Diagram (Text Format)

```
┌──────────────────────────────────────────────────────────┐
│               Menu Creation Functions                    │
│              (app/presentation/menu_bar.py)              │
├──────────────────────────────────────────────────────────┤
│  + create_menu_bar(parent: QWidget) -> QMenuBar          │
│  + create_file_menu(parent: QWidget) -> QMenu            │
│  + create_edit_menu(parent: QWidget) -> QMenu            │
│  + create_help_menu(parent: QWidget) -> QMenu            │
└──────────────────────────────────────────────────────────┘
                        │ creates
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    QMenuBar                              │
├──────────────────────────────────────────────────────────┤
│  Contains:                                               │
│  - File menu (QMenu)                                     │
│  - Edit menu (QMenu)                                     │
│  - Help menu (QMenu)                                     │
└──────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  FileMenu   │  │  EditMenu   │  │  HelpMenu   │
│  (QMenu)    │  │  (QMenu)    │  │  (QMenu)    │
├─────────────┤  ├─────────────┤  ├─────────────┤
│ - New       │  │ - Undo      │  │ - About     │
│ - Open      │  │ - Redo      │  │             │
│ - Save      │  │             │  │             │
│ - [Sep]     │  │             │  │             │
│ - Exit      │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
    │                │                │
    │ triggered      │ triggered      │ triggered
    ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│FileAction    │  │EditAction    │  │HelpAction    │
│Handler       │  │Handler       │  │Handler       │
├──────────────┤  ├──────────────┤  ├──────────────┤
│- parent      │  │- parent      │  │- parent      │
├──────────────┤  ├──────────────┤  ├──────────────┤
│+ on_new()    │  │+ on_undo()   │  │+ on_about()  │
│+ on_open()   │  │+ on_redo()   │  │              │
│+ on_save()   │  │              │  │              │
│+ on_exit()   │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Menu Creation Functions

### Function: create_menu_bar()

**File**: `app/presentation/menu_bar.py`

**Signature**: `create_menu_bar(parent: QWidget) -> QMenuBar`

**Purpose**: Create and configure the complete menu bar

**Parameters**:
- `parent` (QWidget): Parent widget (MainWindow)

**Returns**: `QMenuBar` - Configured menu bar with all menus

**Behavior**:
1. Create QMenuBar instance
2. Create File, Edit, Help menus
3. Add menus to menu bar
4. Return configured menu bar

**Example**:
```python
def create_menu_bar(parent: QWidget) -> QMenuBar:
    """Create the main menu bar."""
    menu_bar = QMenuBar(parent)

    file_menu = create_file_menu(parent)
    edit_menu = create_edit_menu(parent)
    help_menu = create_help_menu(parent)

    menu_bar.addMenu(file_menu)
    menu_bar.addMenu(edit_menu)
    menu_bar.addMenu(help_menu)

    return menu_bar
```

---

### Function: create_file_menu()

**Signature**: `create_file_menu(parent: QWidget) -> QMenu`

**Purpose**: Create File menu with actions

**Parameters**:
- `parent` (QWidget): Parent widget

**Returns**: `QMenu` - File menu with New, Open, Save, Exit actions

**Menu Structure**:
```
File
├── New       (Ctrl+N)
├── Open      (Ctrl+O)
├── Save      (Ctrl+S)
├── ─────────  (separator)
└── Exit      (Ctrl+Q)
```

**Example**:
```python
def create_file_menu(parent: QWidget) -> QMenu:
    """Create File menu."""
    file_menu = QMenu("&File", parent)

    # New action
    new_action = QAction("&New", parent)
    new_action.setShortcut(QKeySequence.New)  # Ctrl+N
    file_menu.addAction(new_action)

    # Open action
    open_action = QAction("&Open", parent)
    open_action.setShortcut(QKeySequence.Open)  # Ctrl+O
    file_menu.addAction(open_action)

    # Save action
    save_action = QAction("&Save", parent)
    save_action.setShortcut(QKeySequence.Save)  # Ctrl+S
    file_menu.addAction(save_action)

    # Separator
    file_menu.addSeparator()

    # Exit action
    exit_action = QAction("E&xit", parent)
    exit_action.setShortcut(QKeySequence.Quit)  # Ctrl+Q
    file_menu.addAction(exit_action)

    return file_menu
```

**Requirements**: FR-GUI-002 (AC-GUI-002-01 through AC-GUI-002-06)

---

### Function: create_edit_menu()

**Signature**: `create_edit_menu(parent: QWidget) -> QMenu`

**Purpose**: Create Edit menu with actions

**Parameters**:
- `parent` (QWidget): Parent widget

**Returns**: `QMenu` - Edit menu with Undo, Redo actions

**Menu Structure**:
```
Edit
├── Undo      (Ctrl+Z)
└── Redo      (Ctrl+Y)
```

**Example**:
```python
def create_edit_menu(parent: QWidget) -> QMenu:
    """Create Edit menu."""
    edit_menu = QMenu("&Edit", parent)

    # Undo action
    undo_action = QAction("&Undo", parent)
    undo_action.setShortcut(QKeySequence.Undo)  # Ctrl+Z
    edit_menu.addAction(undo_action)

    # Redo action
    redo_action = QAction("&Redo", parent)
    redo_action.setShortcut(QKeySequence.Redo)  # Ctrl+Y (or Ctrl+Shift+Z)
    edit_menu.addAction(redo_action)

    return edit_menu
```

**Requirements**: FR-GUI-002 (AC-GUI-002-07, AC-GUI-002-08)

---

### Function: create_help_menu()

**Signature**: `create_help_menu(parent: QWidget) -> QMenu`

**Purpose**: Create Help menu with actions

**Parameters**:
- `parent` (QWidget): Parent widget

**Returns**: `QMenu` - Help menu with About action

**Menu Structure**:
```
Help
└── About
```

**Example**:
```python
def create_help_menu(parent: QWidget) -> QMenu:
    """Create Help menu."""
    help_menu = QMenu("&Help", parent)

    # About action
    about_action = QAction("&About", parent)
    help_menu.addAction(about_action)

    return help_menu
```

**Requirements**: FR-GUI-002 (AC-GUI-002-09)

---

## Action Handler Classes

### Class: FileActionHandler

**File**: `app/handlers/file_actions.py`

**Responsibility**: Handle File menu actions

**Attributes**:
```python
parent: QWidget  # Parent window reference
```

**Methods**:

#### `__init__(self, parent: QWidget)`
**Purpose**: Initialize handler with parent reference

```python
def __init__(self, parent: QWidget):
    """Initialize File action handler."""
    self.parent = parent
```

#### `on_new(self) -> None`
**Purpose**: Handle File → New action

**Behavior**:
- Show message box with "New clicked"
- Modal dialog blocks until OK clicked

**Example**:
```python
def on_new(self) -> None:
    """Handle New action."""
    try:
        QMessageBox.information(
            self.parent,
            "SimplePySideApp",
            "New clicked"
        )
    except Exception as e:
        self._handle_error("New action failed", e)
```

**Requirements**: FR-GUI-002 (AC-GUI-002-01, AC-GUI-002-02)

#### `on_open(self) -> None`
**Purpose**: Handle File → Open action

**Behavior**: Show message box with "Open clicked"

**Requirements**: FR-GUI-002 (AC-GUI-002-03)

#### `on_save(self) -> None`
**Purpose**: Handle File → Save action

**Behavior**: Show message box with "Save clicked"

**Requirements**: FR-GUI-002 (AC-GUI-002-04)

#### `on_exit(self) -> None`
**Purpose**: Handle File → Exit action (CRITICAL)

**Behavior**:
- Close all windows
- Call `QApplication.quit()`
- Exit event loop
- Terminate process with exit code 0

**Example**:
```python
def on_exit(self) -> None:
    """Handle Exit action."""
    try:
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
    except Exception as e:
        print(f"Error during exit: {e}")
        sys.exit(1)
```

**Requirements**: FR-GUI-002 (AC-GUI-002-05), BR-GUI-001

#### `_handle_error(self, context: str, error: Exception) -> None`
**Purpose**: Handle errors in action handlers

**Behavior**:
- Log error to console
- Show error dialog to user
- Allow application to continue

**Example**:
```python
def _handle_error(self, context: str, error: Exception) -> None:
    """Handle action error."""
    print(f"Error in {context}: {error}")
    QMessageBox.critical(
        self.parent,
        "Error",
        f"An error occurred: {context}"
    )
```

---

### Class: EditActionHandler

**File**: `app/handlers/edit_actions.py`

**Responsibility**: Handle Edit menu actions

**Attributes**:
```python
parent: QWidget
```

**Methods**:

#### `__init__(self, parent: QWidget)`
**Purpose**: Initialize handler

#### `on_undo(self) -> None`
**Purpose**: Handle Edit → Undo action

**Behavior**: Show message box with "Undo clicked"

**Example**:
```python
def on_undo(self) -> None:
    """Handle Undo action."""
    try:
        QMessageBox.information(
            self.parent,
            "SimplePySideApp",
            "Undo clicked"
        )
    except Exception as e:
        self._handle_error("Undo action failed", e)
```

**Requirements**: FR-GUI-002 (AC-GUI-002-07)

#### `on_redo(self) -> None`
**Purpose**: Handle Edit → Redo action

**Behavior**: Show message box with "Redo clicked"

**Requirements**: FR-GUI-002 (AC-GUI-002-08)

---

### Class: HelpActionHandler

**File**: `app/handlers/help_actions.py`

**Responsibility**: Handle Help menu actions

**Attributes**:
```python
parent: QWidget
```

**Methods**:

#### `__init__(self, parent: QWidget)`
**Purpose**: Initialize handler

#### `on_about(self) -> None`
**Purpose**: Handle Help → About action

**Behavior**:
- Show dialog with title "About SimplePySideApp"
- Display message: "SimplePySideApp v1.0\nA simple PySide6 desktop application"

**Example**:
```python
def on_about(self) -> None:
    """Handle About action."""
    try:
        QMessageBox.information(
            self.parent,
            "About SimplePySideApp",
            "SimplePySideApp v1.0\nA simple PySide6 desktop application"
        )
    except Exception as e:
        self._handle_error("About action failed", e)
```

**Requirements**: FR-GUI-002 (AC-GUI-002-09)

---

## Signal/Slot Connections

### Connection Pattern

```python
# In MainWindow._connect_actions()
action.triggered.connect(handler.method)
```

### Example Connections

```python
# File menu
new_action.triggered.connect(self._file_handler.on_new)
open_action.triggered.connect(self._file_handler.on_open)
save_action.triggered.connect(self._file_handler.on_save)
exit_action.triggered.connect(self._file_handler.on_exit)

# Edit menu
undo_action.triggered.connect(self._edit_handler.on_undo)
redo_action.triggered.connect(self._edit_handler.on_redo)

# Help menu
about_action.triggered.connect(self._help_handler.on_about)
```

## Keyboard Shortcuts

### QKeySequence Standard Keys

| Action | QKeySequence | Windows/Linux | macOS |
|--------|--------------|---------------|-------|
| **New** | `QKeySequence.New` | Ctrl+N | Cmd+N |
| **Open** | `QKeySequence.Open` | Ctrl+O | Cmd+O |
| **Save** | `QKeySequence.Save` | Ctrl+S | Cmd+S |
| **Quit** | `QKeySequence.Quit` | Ctrl+Q | Cmd+Q |
| **Undo** | `QKeySequence.Undo` | Ctrl+Z | Cmd+Z |
| **Redo** | `QKeySequence.Redo` | Ctrl+Y or Ctrl+Shift+Z | Cmd+Shift+Z |

**Benefits of QKeySequence**:
- Automatic platform translation (Ctrl → Cmd on macOS)
- Standard shortcuts familiar to users
- Localization support

## Design Patterns Applied

### 1. Factory Pattern
**Application**: Menu creation functions
- `create_menu_bar()` is factory for menu bar
- `create_file_menu()`, etc. are factories for menus
- Encapsulates menu construction logic

### 2. Command Pattern
**Application**: QAction objects
- Each action encapsulates a command
- Actions can be triggered from menu or shortcut
- Supports undo/redo (future)

### 3. Observer Pattern
**Application**: Qt signals and slots
- QAction emits `triggered` signal (observable)
- Action handler method is observer (slot)
- Decouples action from handler

### 4. Presenter Pattern (MVP)
**Application**: Action handlers are presenters
- View: QMenu, QAction
- Presenter: FileActionHandler, etc.
- Model: Application state (future)

## Error Handling

### Action Handler Error Strategy

```python
def on_action(self) -> None:
    """Handle action."""
    try:
        # Action logic
        QMessageBox.information(...)
    except Exception as e:
        self._handle_error("Action context", e)
```

### Error Handler Implementation

```python
def _handle_error(self, context: str, error: Exception) -> None:
    """Handle action error."""
    # Log to console
    print(f"ERROR [{context}]: {error}")

    # Show error dialog
    QMessageBox.critical(
        self.parent,
        "Error",
        f"An error occurred in {context}.\n\nDetails: {str(error)}"
    )
```

## Testing Strategy

### Unit Tests for Menu Creation

```python
def test_create_file_menu():
    """Test File menu creation."""
    from PySide6.QtWidgets import QWidget
    from app.presentation.menu_bar import create_file_menu

    parent = QWidget()
    file_menu = create_file_menu(parent)

    assert file_menu.title() == "&File"

    actions = [a.text() for a in file_menu.actions() if not a.isSeparator()]
    assert "&New" in actions
    assert "&Open" in actions
    assert "&Save" in actions
    assert "E&xit" in actions
```

### Unit Tests for Action Handlers

```python
def test_file_new_action(monkeypatch):
    """Test File New action handler."""
    from PySide6.QtWidgets import QWidget, QMessageBox
    from app.handlers.file_actions import FileActionHandler

    parent = QWidget()
    handler = FileActionHandler(parent)

    # Mock QMessageBox
    messages = []
    def mock_information(parent, title, text):
        messages.append({"title": title, "text": text})
    monkeypatch.setattr(QMessageBox, "information", mock_information)

    # Trigger action
    handler.on_new()

    # Verify
    assert len(messages) == 1
    assert messages[0]["title"] == "SimplePySideApp"
    assert messages[0]["text"] == "New clicked"
```

### Integration Tests

```python
def test_menu_action_integration(qtbot):
    """Test menu action triggers handler."""
    from app.presentation.main_window import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)

    # Find File menu
    file_menu = window.menuBar().actions()[0].menu()

    # Find New action
    new_action = None
    for action in file_menu.actions():
        if "New" in action.text():
            new_action = action
            break

    assert new_action is not None

    # Trigger action (would show message box)
    # In real test, mock QMessageBox first
    new_action.trigger()
```

## Complete Example Implementation

### app/presentation/menu_bar.py

```python
"""
Menu bar creation for SimplePySideApp.

Requirements:
    - FR-GUI-002: Menu System and Actions
"""

from PySide6.QtWidgets import QMenuBar, QMenu, QWidget
from PySide6.QtGui import QAction, QKeySequence


def create_menu_bar(parent: QWidget) -> QMenuBar:
    """Create the main menu bar with File, Edit, Help menus."""
    menu_bar = QMenuBar(parent)

    file_menu = create_file_menu(parent)
    edit_menu = create_edit_menu(parent)
    help_menu = create_help_menu(parent)

    menu_bar.addMenu(file_menu)
    menu_bar.addMenu(edit_menu)
    menu_bar.addMenu(help_menu)

    return menu_bar


def create_file_menu(parent: QWidget) -> QMenu:
    """Create File menu with New, Open, Save, Exit actions."""
    file_menu = QMenu("&File", parent)

    new_action = QAction("&New", parent)
    new_action.setShortcut(QKeySequence.New)
    file_menu.addAction(new_action)

    open_action = QAction("&Open", parent)
    open_action.setShortcut(QKeySequence.Open)
    file_menu.addAction(open_action)

    save_action = QAction("&Save", parent)
    save_action.setShortcut(QKeySequence.Save)
    file_menu.addAction(save_action)

    file_menu.addSeparator()

    exit_action = QAction("E&xit", parent)
    exit_action.setShortcut(QKeySequence.Quit)
    file_menu.addAction(exit_action)

    return file_menu


def create_edit_menu(parent: QWidget) -> QMenu:
    """Create Edit menu with Undo, Redo actions."""
    edit_menu = QMenu("&Edit", parent)

    undo_action = QAction("&Undo", parent)
    undo_action.setShortcut(QKeySequence.Undo)
    edit_menu.addAction(undo_action)

    redo_action = QAction("&Redo", parent)
    redo_action.setShortcut(QKeySequence.Redo)
    edit_menu.addAction(redo_action)

    return edit_menu


def create_help_menu(parent: QWidget) -> QMenu:
    """Create Help menu with About action."""
    help_menu = QMenu("&Help", parent)

    about_action = QAction("&About", parent)
    help_menu.addAction(about_action)

    return help_menu
```

### app/handlers/file_actions.py

```python
"""
File menu action handlers.

Requirements:
    - FR-GUI-002: Menu System and Actions (File menu)
    - BR-GUI-001: Exit action must cleanly terminate application
"""

from PySide6.QtWidgets import QWidget, QMessageBox, QApplication


class FileActionHandler:
    """Handler for File menu actions."""

    def __init__(self, parent: QWidget):
        """Initialize handler with parent window reference."""
        self.parent = parent

    def on_new(self) -> None:
        """Handle File → New action."""
        try:
            QMessageBox.information(
                self.parent,
                "SimplePySideApp",
                "New clicked"
            )
        except Exception as e:
            self._handle_error("New action", e)

    def on_open(self) -> None:
        """Handle File → Open action."""
        try:
            QMessageBox.information(
                self.parent,
                "SimplePySideApp",
                "Open clicked"
            )
        except Exception as e:
            self._handle_error("Open action", e)

    def on_save(self) -> None:
        """Handle File → Save action."""
        try:
            QMessageBox.information(
                self.parent,
                "SimplePySideApp",
                "Save clicked"
            )
        except Exception as e:
            self._handle_error("Save action", e)

    def on_exit(self) -> None:
        """Handle File → Exit action. Closes application cleanly."""
        try:
            QApplication.quit()
        except Exception as e:
            print(f"Error during exit: {e}")
            import sys
            sys.exit(1)

    def _handle_error(self, context: str, error: Exception) -> None:
        """Handle action errors."""
        print(f"ERROR [{context}]: {error}")
        QMessageBox.critical(
            self.parent,
            "Error",
            f"An error occurred: {context}"
        )
```

## Revision History

| Version | Date       | Author        | Changes                          |
|---------|------------|---------------|----------------------------------|
| 1.0     | 2025-11-12 | Design Agent  | Initial menu system class design |
