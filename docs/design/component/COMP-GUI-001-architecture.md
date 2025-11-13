---
id: COMP-GUI-001
module: gui
title: Component Architecture and Interactions
type: component_architecture
status: Draft
created_date: 2025-11-12T22:48:16Z
---

# Component Architecture and Interactions

## Overview

This document defines the component architecture for SimplePySideApp, including component interactions, data flow, signal/slot connections, and event handling mechanisms. The architecture follows Qt's signal/slot pattern combined with the Model-View-Presenter (MVP) design pattern.

## High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Operating System                           │
│         (Windows, macOS, Linux)                             │
└───────────────────────┬─────────────────────────────────────┘
                        │ System Events
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Qt Event Loop                            │
│                   (QApplication)                            │
│  - Process system events (mouse, keyboard, window)          │
│  - Dispatch to widgets                                      │
│  - Execute signal/slot connections                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   MainWindow                                │
│                 (QMainWindow)                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  QMenuBar                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │FileMenu  │  │EditMenu  │  │HelpMenu  │          │  │
│  │  │(QMenu)   │  │(QMenu)   │  │(QMenu)   │          │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │  │
│  │       │             │             │                  │  │
│  │  ┌────▼────────┬────▼─────┬──────▼──────┐          │  │
│  │  │QAction (7)  │QAction(2)│QAction (1)  │          │  │
│  │  │New,Open,    │Undo,Redo │About        │          │  │
│  │  │Save,Exit    │          │             │          │  │
│  │  └─────────────┴──────────┴─────────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Central Widget (QWidget)                   │  │
│  │              [Empty Area]                            │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ QAction.triggered signals
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Action Handlers (Presenters)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │FileAction    │  │EditAction    │  │HelpAction    │     │
│  │Handler       │  │Handler       │  │Handler       │     │
│  │              │  │              │  │              │     │
│  │- on_new()    │  │- on_undo()   │  │- on_about()  │     │
│  │- on_open()   │  │- on_redo()   │  │              │     │
│  │- on_save()   │  │              │  │              │     │
│  │- on_exit()   │  │              │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                            ▼                                │
│                  ┌─────────────────┐                        │
│                  │  QMessageBox    │                        │
│                  │  QApplication   │                        │
│                  └─────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### 1. QApplication (Qt Event Loop)

**Type**: Qt Framework Component

**Responsibilities**:
- Initialize Qt framework
- Create and manage event loop
- Process system events (mouse, keyboard, window events)
- Dispatch events to widgets
- Execute signal/slot connections
- Manage application-wide resources

**Lifecycle**:
```python
app = QApplication(sys.argv)  # Initialize
window = MainWindow()         # Create window
window.show()                 # Show window
sys.exit(app.exec())         # Enter event loop, block until quit
```

**Key Methods**:
- `QApplication(args)` - Constructor
- `exec()` - Enter event loop (blocks)
- `quit()` - Exit event loop
- `instance()` - Get singleton instance

**Events Handled**:
- Mouse events (click, move, wheel)
- Keyboard events (key press, release)
- Window events (resize, move, close, focus)
- System events (theme change, display change)

---

### 2. MainWindow (View Coordinator)

**Type**: Application Component (QMainWindow)

**File**: `app/presentation/main_window.py`

**Responsibilities**:
- Create and configure window
- Set up menu bar
- Create central widget
- Instantiate action handlers
- Connect signals to slots
- Coordinate UI components

**Dependencies**:
- Depends on: `menu_bar.py` (menu creation)
- Depends on: `file_actions.py`, `edit_actions.py`, `help_actions.py` (handlers)
- Inherits: `QMainWindow` (Qt)

**Initialization Sequence**:
```
MainWindow.__init__()
    ↓
_init_ui()
    ├─→ _setup_window_properties()
    │   └─→ setWindowTitle(), resize(), setMinimumSize()
    │
    ├─→ _create_central_widget()
    │   └─→ QWidget(), setCentralWidget()
    │
    ├─→ _create_menu_bar()
    │   └─→ create_menu_bar(self)
    │
    └─→ _connect_actions()
        ├─→ Create handler instances
        └─→ Connect QAction.triggered to handler methods
```

**Key Interactions**:
- Creates menus via `create_menu_bar()`
- Creates action handlers
- Connects menu actions to handlers
- Receives close event → triggers exit

---

### 3. Menu Bar and Menus (View)

**Type**: Application Component (Qt Widgets)

**File**: `app/presentation/menu_bar.py`

**Components**:
- `QMenuBar` - Top-level menu container
- `QMenu` - Individual menus (File, Edit, Help)
- `QAction` - Menu items with shortcuts

**Responsibilities**:
- Display menus and menu items
- Handle menu open/close
- Emit signals when actions triggered
- Display keyboard shortcuts
- Provide visual feedback (hover, focus)

**Menu Structure**:
```
QMenuBar
├── File (QMenu)
│   ├── New (QAction) → triggered signal
│   ├── Open (QAction) → triggered signal
│   ├── Save (QAction) → triggered signal
│   ├── [Separator]
│   └── Exit (QAction) → triggered signal
│
├── Edit (QMenu)
│   ├── Undo (QAction) → triggered signal
│   └── Redo (QAction) → triggered signal
│
└── Help (QMenu)
    └── About (QAction) → triggered signal
```

**Signal Flow**:
```
User Action (Click/Keyboard)
    ↓
QAction receives event
    ↓
QAction emits triggered signal
    ↓
Connected slot (handler method) executes
```

---

### 4. Action Handlers (Presenters)

**Type**: Application Components (Python Classes)

**Files**:
- `app/handlers/file_actions.py` - FileActionHandler
- `app/handlers/edit_actions.py` - EditActionHandler
- `app/handlers/help_actions.py` - HelpActionHandler

**Responsibilities**:
- Handle user actions (menu clicks, shortcuts)
- Execute action logic (show messages, exit app)
- Manage errors gracefully
- Update view if needed (future)
- Update model if needed (future)

**Handler Pattern**:
```python
class FileActionHandler:
    def __init__(self, parent: QWidget):
        self.parent = parent

    def on_action(self) -> None:
        try:
            # Action logic
            QMessageBox.information(...)
        except Exception as e:
            self._handle_error("context", e)

    def _handle_error(self, context: str, error: Exception):
        # Log and show error dialog
```

**Action Flow**:
```
QAction.triggered signal
    ↓
Handler method (slot)
    ↓
Try-except block
    ├─→ Success: Show message or perform action
    └─→ Error: Log and show error dialog
```

---

### 5. Qt Dialogs (Modal UI)

**Type**: Qt Framework Components

**Components**:
- `QMessageBox.information()` - Info dialogs
- `QMessageBox.critical()` - Error dialogs

**Responsibilities**:
- Display modal messages
- Block UI until dismissed
- Provide OK button for dismissal

**Usage Pattern**:
```python
QMessageBox.information(
    parent,        # Parent window
    "Title",       # Dialog title
    "Message"      # Dialog message
)
```

**Modal Behavior**:
- Blocks parent window interaction
- User must click OK to dismiss
- Prevents multiple dialogs stacking (sequential)

---

## Signal/Slot Connection Patterns

### Pattern 1: Direct Connection

**Use Case**: Connect QAction to handler method

**Example**:
```python
# In MainWindow._connect_actions()
new_action.triggered.connect(self._file_handler.on_new)
```

**Signal**: `QAction.triggered` (emitted when action activated)
**Slot**: `FileActionHandler.on_new()` (method to execute)

**Flow**:
```
User clicks New → new_action.triggered emitted → on_new() executed
User presses Ctrl+N → new_action.triggered emitted → on_new() executed
```

---

### Pattern 2: Multiple Connections

**Use Case**: Same signal to multiple slots (future)

**Example**:
```python
# Connect same action to multiple handlers
action.triggered.connect(handler1.method)
action.triggered.connect(handler2.method)
# Both methods execute when action triggered
```

---

### Pattern 3: Lambda Connections (if needed)

**Use Case**: Pass parameters to slot

**Example**:
```python
# Pass action name to generic handler
action.triggered.connect(lambda: handler.on_action("New"))
```

---

## Data Flow Diagrams

### Flow 1: File → New Action

```
┌──────────────────┐
│   User Action    │
│ Click File→New   │
│  or Ctrl+N       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    QAction       │
│  (New action)    │
│ triggered signal │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FileAction      │
│  Handler         │
│  on_new()        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QMessageBox     │
│  .information()  │
│  "New clicked"   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ User clicks OK   │
│ Dialog dismissed │
└──────────────────┘
```

---

### Flow 2: File → Exit Action

```
┌──────────────────┐
│   User Action    │
│ Click File→Exit  │
│  or Ctrl+Q       │
│ or Close Window  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    QAction       │
│  (Exit action)   │
│ triggered signal │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FileAction      │
│  Handler         │
│  on_exit()       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QApplication    │
│  .quit()         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Event Loop      │
│  Exits           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Process         │
│  Terminates      │
│  Exit Code: 0    │
└──────────────────┘
```

---

### Flow 3: Window Close Event

```
┌──────────────────┐
│   User Action    │
│ Click Close (X)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Qt Event        │
│  QCloseEvent     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  MainWindow      │
│  closeEvent()    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  event.accept()  │
│  (allow close)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Window Closes   │
│  App Terminates  │
└──────────────────┘
```

---

### Flow 4: Keyboard Shortcut

```
┌──────────────────┐
│   User Action    │
│  Press Ctrl+S    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Qt Event Loop   │
│  Detects keypress│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QAction         │
│  (Save action)   │
│  Shortcut match  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  triggered signal│
│  emitted         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FileAction      │
│  Handler         │
│  on_save()       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  QMessageBox     │
│  "Save clicked"  │
└──────────────────┘
```

---

## Event Handling Flow

### Mouse Events

```
User moves mouse over menu item
    ↓
Qt Event Loop captures mouse move event
    ↓
QMenu receives event
    ↓
QMenu updates hover state (highlight item)
    ↓
Visual feedback shown to user
```

### Keyboard Events

```
User presses Ctrl+N
    ↓
Qt Event Loop captures key press event
    ↓
QApplication checks for matching shortcuts
    ↓
QAction (New) shortcut matches
    ↓
QAction emits triggered signal
    ↓
Connected slot executes (on_new)
```

### Window Events

```
User drags window edge to resize
    ↓
Qt Event Loop captures resize event
    ↓
QMainWindow receives resize event
    ↓
QMainWindow validates new size (min/max constraints)
    ↓
QMainWindow updates geometry
    ↓
Child widgets (menu bar, central widget) resize
    ↓
Window repaints
```

---

## Component Interaction Matrix

| Component | Interacts With | Interaction Type | Purpose |
|-----------|---------------|------------------|---------|
| **QApplication** | OS | System events | Receive mouse, keyboard, window events |
| **QApplication** | MainWindow | Event dispatch | Send events to widgets |
| **MainWindow** | QMenuBar | Composition | Create and manage menu bar |
| **MainWindow** | QWidget | Composition | Create central widget |
| **MainWindow** | ActionHandlers | Composition | Create and manage handlers |
| **QMenuBar** | QMenu | Composition | Contain menus |
| **QMenu** | QAction | Composition | Contain actions |
| **QAction** | ActionHandler | Signal/Slot | Emit triggered → execute handler |
| **ActionHandler** | QMessageBox | Function call | Show dialog |
| **ActionHandler** | QApplication | Function call | Quit application |
| **ActionHandler** | MainWindow | Reference | Access parent window |

---

## Component Lifecycle

### Application Lifecycle

```
1. Process Start
   ↓
2. Import PySide6 modules
   ↓
3. Create QApplication instance
   ↓
4. Create MainWindow instance
   ├─→ Initialize UI
   ├─→ Create menus
   ├─→ Create handlers
   └─→ Connect signals
   ↓
5. Show MainWindow
   ↓
6. Enter event loop (app.exec())
   ├─→ Process events continuously
   ├─→ Dispatch to widgets
   └─→ Execute signal/slot connections
   ↓
7. User triggers Exit
   ↓
8. QApplication.quit() called
   ↓
9. Event loop exits
   ↓
10. Process terminates
```

### Component Creation Order

```
QApplication (first)
    ↓
MainWindow
    ├─→ QWidget (central widget)
    ├─→ QMenuBar
    │   ├─→ FileMenu (QMenu)
    │   │   └─→ QActions (New, Open, Save, Exit)
    │   ├─→ EditMenu (QMenu)
    │   │   └─→ QActions (Undo, Redo)
    │   └─→ HelpMenu (QMenu)
    │       └─→ QAction (About)
    │
    └─→ Action Handlers
        ├─→ FileActionHandler
        ├─→ EditActionHandler
        └─→ HelpActionHandler
```

---

## Cross-Platform Event Handling

### Platform-Specific Differences

| Aspect | Windows | macOS | Linux |
|--------|---------|-------|-------|
| **Keyboard Modifier** | Ctrl | Cmd (Qt auto-converts) | Ctrl |
| **Close Button** | X (right) | Red dot (left) | X (position varies) |
| **Menu Bar** | In window | System menu bar | In window |
| **Shortcuts Display** | Ctrl+N | Cmd+N (auto-converted) | Ctrl+N |
| **Theme** | Windows native | Aqua | GTK/KDE |

### Qt Abstraction Layer

Qt handles platform differences automatically:

```
Application uses QKeySequence.New (cross-platform)
    ↓
Qt translates to platform-specific shortcut:
    ├─→ Windows/Linux: Ctrl+N
    └─→ macOS: Cmd+N
```

---

## Error Propagation

### Error Handling Hierarchy

```
┌─────────────────────────────────────┐
│  Qt Event Loop                      │
│  - Catches unhandled exceptions     │
│  - Prevents crash                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Action Handler                     │
│  try-except around action logic     │
└─────────────────┬───────────────────┘
                  │
                  ├─→ Success: Normal flow
                  │
                  └─→ Exception:
                      ├─→ Log error
                      ├─→ Show error dialog
                      └─→ Continue running
```

### Error Flow Example

```
User triggers action
    ↓
Handler method executes
    ↓
Exception occurs
    ↓
Caught by try-except
    ↓
_handle_error() called
    ├─→ Print to console
    └─→ QMessageBox.critical()
    ↓
User sees error dialog
    ↓
User clicks OK
    ↓
Application continues running
```

---

## Performance Considerations

### UI Thread

All Qt UI operations run on main thread:
```
Event Loop (Main Thread)
    ├─→ Process events
    ├─→ Update UI
    ├─→ Execute slots
    └─→ Repaint widgets
```

**Rule**: Never block UI thread with long operations

### Event Queue

```
User clicks button rapidly (5 times)
    ↓
5 events added to queue
    ↓
Events processed sequentially
    ├─→ Event 1: Show message box (blocks)
    ├─→ User clicks OK
    ├─→ Event 2: Show message box (blocks)
    ├─→ User clicks OK
    └─→ ... etc
```

**Modal dialogs block event processing until dismissed**

---

## Security Considerations

### Current Phase
- No network access
- No file system access (beyond Python imports)
- No user data storage
- No elevated privileges

### Input Validation
- Qt handles UI input validation automatically
- Window geometry validated by Qt
- No user-provided data in this phase

---

## Future Extensions

### Adding New Components

**Add New Menu**:
1. Create menu in `menu_bar.py`
2. Create handler class in `handlers/`
3. Connect in `MainWindow._connect_actions()`

**Add Business Logic**:
1. Create service class in `services/` (new layer)
2. Call from action handlers
3. Keep handlers thin (presenter pattern)

**Add Data Persistence**:
1. Create model classes in `models/`
2. Create repository classes in `repositories/` (new layer)
3. Update handlers to save/load via repositories

---

## Component Diagram Summary

```
┌───────────────────────────────────────────────────────┐
│                   Presentation Layer                  │
│        (MainWindow, Menus, Actions)                   │
└────────────────────┬──────────────────────────────────┘
                     │ signals
                     ▼
┌───────────────────────────────────────────────────────┐
│                   Presenter Layer                     │
│             (Action Handlers)                         │
└────────────────────┬──────────────────────────────────┘
                     │ updates (future)
                     ▼
┌───────────────────────────────────────────────────────┐
│                   Model Layer                         │
│             (Application State)                       │
│              [Future Enhancement]                     │
└───────────────────────────────────────────────────────┘
```

**Key Interaction**: View emits signals → Presenter handles → Model updates (future)

---

## References

- [Qt Signals and Slots](https://doc.qt.io/qt-6/signalsandslots.html)
- [Qt Event System](https://doc.qt.io/qt-6/eventsandfilters.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)

---

## Revision History

| Version | Date       | Author        | Changes                          |
|---------|------------|---------------|----------------------------------|
| 1.0     | 2025-11-12 | Design Agent  | Initial component architecture   |
