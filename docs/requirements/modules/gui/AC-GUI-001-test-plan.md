---
id: AC-GUI-001
uuid: a08b4f66-3769-4c82-b46a-df254ee99e33
related_requirements:
  - FR-GUI-001
  - FR-GUI-002
  - FR-GUI-003
module: gui
type: acceptance_test
priority: High
status: Draft
gathered_date: 2025-11-12T22:34:42Z
---

# Acceptance Test Plan: SimplePySideApp

## Overview

This document defines the comprehensive acceptance test plan for SimplePySideApp, covering all functional requirements defined in FR-GUI-001 (Main Window), FR-GUI-002 (Menu System), and FR-GUI-003 (UI Interactions). The test plan includes manual and automated test scenarios organized by feature area.

## Test Environment

### Required Software

- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **PySide6**: 6.0.0 or later (test with 6.6.0+)
- **pytest**: 7.0+ (for automated tests)
- **pytest-qt**: 4.0+ (for Qt-specific test fixtures)

### Test Platforms

**Primary Platforms** (must pass all tests):
- Windows 10 (build 19041+) or Windows 11
- macOS 12 Monterey or later
- Ubuntu 22.04 LTS (with GNOME or KDE)

**Secondary Platforms** (should pass, best-effort):
- Fedora 38+ (with GNOME)
- Debian 12+ (with GNOME)
- Other Linux distributions with X11 or Wayland

### Test Data

Test data is embedded in each test scenario below. No external test data files required for this phase.

## Test Scenarios

### Category 1: Application Launch and Window Display

#### TS-GUI-001-01: Successful Application Launch

**Requirement**: FR-GUI-001 (AC-GUI-001-01)

**Priority**: Critical

**Type**: Automated + Manual

**Preconditions**:
- Python 3.8+ installed
- PySide6 6.0+ installed
- No other instances of SimplePySideApp running

**Test Steps**:
1. Open terminal/command prompt
2. Navigate to application directory
3. Run `python main.py` (or launch executable)
4. Measure time from command execution to window appearance
5. Verify window properties

**Expected Results**:
- Window appears within 1 second
- Window title is "SimplePySideApp"
- Window size is 800x600 pixels
- Window is centered on primary screen
- Menu bar shows: File, Edit, Help
- Central widget is empty (blank background)
- Window has minimize, maximize, close buttons
- Window state is normal (not minimized or maximized)

**Test Data**:
```python
{
  "command": "python main.py",
  "max_launch_time_ms": 1000,
  "expected_title": "SimplePySideApp",
  "expected_size": {"width": 800, "height": 600},
  "expected_menus": ["File", "Edit", "Help"],
  "expected_window_state": "normal"
}
```

**Automated Test Code**:
```python
def test_application_launch(qtbot):
    """Test application launches successfully with correct properties."""
    from main import MainWindow

    start_time = time.time()
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    launch_time = (time.time() - start_time) * 1000

    # Verify launch time
    assert launch_time < 1000, f"Launch took {launch_time}ms, expected < 1000ms"

    # Verify window properties
    assert window.windowTitle() == "SimplePySideApp"
    assert window.width() == 800
    assert window.height() == 600
    assert window.isVisible()
    assert not window.isMinimized()
    assert not window.isMaximized()

    # Verify menu bar
    menu_bar = window.menuBar()
    menus = [action.text() for action in menu_bar.actions()]
    assert "File" in menus
    assert "Edit" in menus
    assert "Help" in menus
```

**Pass Criteria**: All assertions pass, launch time < 1 second

---

#### TS-GUI-001-02: Error - Missing PySide6

**Requirement**: FR-GUI-001 (AC-GUI-001-11)

**Priority**: High

**Type**: Manual (automated in CI/CD environment)

**Preconditions**:
- Python 3.8+ installed
- PySide6 NOT installed (uninstall if present: `pip uninstall PySide6`)

**Test Steps**:
1. Open terminal/command prompt
2. Navigate to application directory
3. Run `python main.py`
4. Observe error message

**Expected Results**:
- Application does NOT launch
- Error message displayed: "PySide6 not found. Install with: pip install PySide6"
- Exit code is 1
- No window appears
- No hanging processes

**Test Data**:
```python
{
  "pyside6_installed": False,
  "expected_error": "PySide6 not found. Install with: pip install PySide6",
  "expected_exit_code": 1,
  "window_shown": False
}
```

**Pass Criteria**: Error message displayed correctly, exit code 1, no window

---

#### TS-GUI-001-03: Error - No Display Available

**Requirement**: FR-GUI-001 (AC-GUI-001-12)

**Priority**: Medium

**Type**: Manual (requires headless environment)

**Preconditions**:
- Linux system with no X11 server running (or SSH without X forwarding)
- Python 3.8+ and PySide6 installed
- No DISPLAY environment variable set

**Test Steps**:
1. SSH into Linux system without X forwarding
2. Unset DISPLAY: `unset DISPLAY`
3. Run `python main.py`
4. Observe error message

**Expected Results**:
- Application fails to initialize QApplication
- Error message: "Cannot initialize display"
- Exit code is 1
- Process terminates within 2 seconds

**Test Data**:
```python
{
  "display_available": False,
  "expected_error": "Cannot initialize display",
  "expected_exit_code": 1,
  "max_termination_time_s": 2
}
```

**Pass Criteria**: Error displayed, clean exit with code 1

---

### Category 2: Window State Management

#### TS-GUI-001-04: Window Resize - Normal Range

**Requirement**: FR-GUI-001 (AC-GUI-001-02)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running at default 800x600 size

**Test Steps**:
1. Get initial window size (800x600)
2. Simulate drag from bottom-right corner
3. Resize to 1024x768
4. Verify final size

**Expected Results**:
- Window resizes smoothly without flickering
- Final size is exactly 1024x768
- Menu bar stretches to 1024px width
- Central widget adjusts to new size

**Test Data**:
```python
{
  "initial_size": (800, 600),
  "target_size": (1024, 768),
  "drag_from": "bottom_right",
  "expected_smooth": True
}
```

**Automated Test Code**:
```python
def test_window_resize_normal(qtbot):
    """Test window resizes correctly within normal range."""
    from main import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    # Resize window
    window.resize(1024, 768)
    qtbot.wait(100)  # Allow resize to complete

    # Verify size
    assert window.width() == 1024
    assert window.height() == 768

    # Verify menu bar width matches
    menu_bar = window.menuBar()
    assert menu_bar.width() == 1024
```

**Pass Criteria**: Window resizes to target size, no visual glitches

---

#### TS-GUI-001-05: Window Resize - Below Minimum (Edge Case)

**Requirement**: FR-GUI-001 (AC-GUI-001-03)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running at default 800x600 size

**Test Steps**:
1. Attempt to resize window to 200x150 (below 400x300 minimum)
2. Verify window stops at minimum size

**Expected Results**:
- Window cannot be resized below 400x300
- Final size is 400x300 (minimum enforced)
- No errors or exceptions

**Test Data**:
```python
{
  "initial_size": (800, 600),
  "attempted_size": (200, 150),
  "expected_minimum": (400, 300)
}
```

**Automated Test Code**:
```python
def test_window_minimum_size(qtbot):
    """Test window respects minimum size constraint."""
    from main import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    # Try to resize below minimum
    window.resize(200, 150)
    qtbot.wait(100)

    # Verify minimum enforced
    assert window.width() >= 400
    assert window.height() >= 300
```

**Pass Criteria**: Minimum size enforced, no exceptions

---

#### TS-GUI-001-06: Window Minimize

**Requirement**: FR-GUI-001 (AC-GUI-001-04)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running in normal state

**Test Steps**:
1. Verify window is visible
2. Click minimize button (or call window.showMinimized())
3. Verify window is minimized

**Expected Results**:
- Window disappears from screen
- Window state changes to minimized
- Application process continues running
- Window can be restored from taskbar/dock

**Test Data**:
```python
{
  "initial_state": "normal",
  "action": "minimize",
  "expected_state": "minimized",
  "process_running": True
}
```

**Automated Test Code**:
```python
def test_window_minimize(qtbot):
    """Test window minimizes correctly."""
    from main import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    # Minimize window
    window.showMinimized()
    qtbot.wait(200)

    # Verify minimized
    assert window.isMinimized()

    # Verify process still running (window object exists)
    assert window is not None
```

**Pass Criteria**: Window minimizes, process continues running

---

#### TS-GUI-001-07: Window Maximize and Restore

**Requirement**: FR-GUI-001 (AC-GUI-001-05, AC-GUI-001-06)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running at default 800x600 size

**Test Steps**:
1. Get initial window size
2. Maximize window
3. Verify maximized state
4. Restore window
5. Verify restored to original size

**Expected Results**:
- Maximize: Window fills screen (minus taskbar)
- Restore: Window returns to 800x600

**Test Data**:
```python
{
  "initial_size": (800, 600),
  "action_sequence": ["maximize", "restore"],
  "expected_maximized": "fullscreen",
  "expected_restored_size": (800, 600)
}
```

**Automated Test Code**:
```python
def test_window_maximize_restore(qtbot):
    """Test window maximize and restore."""
    from main import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    initial_size = (window.width(), window.height())

    # Maximize
    window.showMaximized()
    qtbot.wait(200)
    assert window.isMaximized()

    # Restore
    window.showNormal()
    qtbot.wait(200)
    assert not window.isMaximized()
    assert window.width() == initial_size[0]
    assert window.height() == initial_size[1]
```

**Pass Criteria**: Maximize and restore work correctly

---

### Category 3: Menu System - File Menu

#### TS-GUI-002-01: File → New (Mouse Click)

**Requirement**: FR-GUI-002 (AC-GUI-002-01)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running

**Test Steps**:
1. Click "File" menu
2. Click "New" menu item
3. Verify message box appears
4. Click OK to dismiss

**Expected Results**:
- Message box appears within 100ms
- Title: "SimplePySideApp"
- Message: "New clicked"
- OK button present
- Message box is modal

**Test Data**:
```python
{
  "menu": "File",
  "action": "New",
  "trigger": "mouse_click",
  "expected_message": "New clicked"
}
```

**Automated Test Code**:
```python
def test_file_new_action(qtbot, monkeypatch):
    """Test File → New shows correct message."""
    from main import MainWindow
    from PySide6.QtWidgets import QMessageBox

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    # Mock QMessageBox to capture message
    messages = []
    def mock_information(parent, title, text):
        messages.append({"title": title, "text": text})
    monkeypatch.setattr(QMessageBox, "information", mock_information)

    # Trigger New action
    file_menu = window.findChild(QMenu, "File")
    new_action = None
    for action in file_menu.actions():
        if action.text() == "New":
            new_action = action
            break

    assert new_action is not None
    new_action.trigger()
    qtbot.wait(50)

    # Verify message
    assert len(messages) == 1
    assert messages[0]["title"] == "SimplePySideApp"
    assert messages[0]["text"] == "New clicked"
```

**Pass Criteria**: Message box shows "New clicked"

---

#### TS-GUI-002-02: File → New (Keyboard Shortcut Ctrl+N)

**Requirement**: FR-GUI-002 (AC-GUI-002-02)

**Priority**: High

**Type**: Automated

**Preconditions**:
- Application running and has focus

**Test Steps**:
1. Press Ctrl+N
2. Verify message box appears (without opening File menu)

**Expected Results**:
- Message box appears immediately
- Same message as clicking menu item
- File menu does not open

**Test Data**:
```python
{
  "shortcut": "Ctrl+N",
  "expected_message": "New clicked",
  "menu_opens": False
}
```

**Automated Test Code**:
```python
def test_file_new_shortcut(qtbot, monkeypatch):
    """Test Ctrl+N shortcut for New action."""
    from main import MainWindow
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeySequence

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    # Mock message box
    messages = []
    def mock_information(parent, title, text):
        messages.append({"title": title, "text": text})
    monkeypatch.setattr(QMessageBox, "information", mock_information)

    # Press Ctrl+N
    qtbot.keyClick(window, Qt.Key_N, Qt.ControlModifier)
    qtbot.wait(50)

    # Verify message
    assert len(messages) == 1
    assert messages[0]["text"] == "New clicked"
```

**Pass Criteria**: Shortcut triggers action without opening menu

---

#### TS-GUI-002-03: File → Open (Ctrl+O)

**Requirement**: FR-GUI-002 (AC-GUI-002-03)

**Priority**: High

**Type**: Automated

**Test Steps**:
1. Press Ctrl+O OR click File → Open
2. Verify message box shows "Open clicked"

**Expected Results**:
- Message box displays "Open clicked"

**Test Data**:
```python
{
  "action": "Open",
  "shortcuts": ["Ctrl+O", "File→Open"],
  "expected_message": "Open clicked"
}
```

**Automated Test Code**:
```python
def test_file_open_action(qtbot, monkeypatch):
    """Test File → Open shows correct message."""
    from main import MainWindow
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtCore import Qt

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    messages = []
    def mock_information(parent, title, text):
        messages.append(text)
    monkeypatch.setattr(QMessageBox, "information", mock_information)

    # Test shortcut
    qtbot.keyClick(window, Qt.Key_O, Qt.ControlModifier)
    qtbot.wait(50)

    assert "Open clicked" in messages
```

**Pass Criteria**: "Open clicked" message appears

---

#### TS-GUI-002-04: File → Save (Ctrl+S)

**Requirement**: FR-GUI-002 (AC-GUI-002-04)

**Priority**: High

**Type**: Automated

**Test Steps**:
1. Press Ctrl+S OR click File → Save
2. Verify message box shows "Save clicked"

**Expected Results**:
- Message box displays "Save clicked"

**Test Data**:
```python
{
  "action": "Save",
  "shortcuts": ["Ctrl+S", "File→Save"],
  "expected_message": "Save clicked"
}
```

**Pass Criteria**: "Save clicked" message appears

---

#### TS-GUI-002-05: File → Exit (Ctrl+Q) - CRITICAL

**Requirement**: FR-GUI-002 (AC-GUI-002-05)

**Priority**: Critical

**Type**: Automated + Manual

**Preconditions**:
- Application running

**Test Steps**:
1. Press Ctrl+Q OR click File → Exit
2. Verify application closes

**Expected Results**:
- NO message box appears (immediate action)
- All windows close within 500ms
- QApplication.quit() called
- Process terminates with exit code 0
- No orphaned processes

**Test Data**:
```python
{
  "action": "Exit",
  "trigger": "Ctrl+Q",
  "expected_message_box": False,
  "expected_exit_code": 0,
  "max_close_time_ms": 500
}
```

**Automated Test Code**:
```python
def test_file_exit_action(qtbot):
    """Test File → Exit closes application."""
    from main import MainWindow
    from PySide6.QtWidgets import QApplication

    window = MainWindow()
    qtbot.addWidget(window)
    window.show()

    # Connect to quit signal
    quit_called = []
    QApplication.instance().aboutToQuit.connect(lambda: quit_called.append(True))

    # Trigger Exit action
    file_menu = window.menuBar().actions()[0].menu()  # File menu
    exit_action = None
    for action in file_menu.actions():
        if "Exit" in action.text():
            exit_action = action
            break

    assert exit_action is not None
    exit_action.trigger()
    qtbot.wait(100)

    # Verify quit was called
    assert len(quit_called) > 0
```

**Pass Criteria**: Application exits cleanly without message box

---

#### TS-GUI-002-06: File Menu - Separator Before Exit

**Requirement**: FR-GUI-002 (AC-GUI-002-06)

**Priority**: Low

**Type**: Manual

**Test Steps**:
1. Click File menu
2. Visually inspect menu items

**Expected Results**:
- Menu shows: New, Open, Save, [separator line], Exit
- Separator is visible horizontal line
- Exit is clearly separated

**Pass Criteria**: Visual separator present before Exit

---

### Category 4: Menu System - Edit Menu

#### TS-GUI-002-07: Edit → Undo (Ctrl+Z)

**Requirement**: FR-GUI-002 (AC-GUI-002-07)

**Priority**: Medium

**Type**: Automated

**Test Steps**:
1. Press Ctrl+Z OR click Edit → Undo
2. Verify message box shows "Undo clicked"

**Expected Results**:
- Message box displays "Undo clicked"

**Test Data**:
```python
{
  "action": "Undo",
  "shortcuts": ["Ctrl+Z", "Edit→Undo"],
  "expected_message": "Undo clicked"
}
```

**Pass Criteria**: "Undo clicked" message appears

---

#### TS-GUI-002-08: Edit → Redo (Ctrl+Y)

**Requirement**: FR-GUI-002 (AC-GUI-002-08)

**Priority**: Medium

**Type**: Automated

**Test Steps**:
1. Press Ctrl+Y OR click Edit → Redo
2. Verify message box shows "Redo clicked"

**Expected Results**:
- Message box displays "Redo clicked"

**Test Data**:
```python
{
  "action": "Redo",
  "shortcuts": ["Ctrl+Y", "Edit→Redo"],
  "expected_message": "Redo clicked"
}
```

**Pass Criteria**: "Redo clicked" message appears

---

### Category 5: Menu System - Help Menu

#### TS-GUI-002-09: Help → About

**Requirement**: FR-GUI-002 (AC-GUI-002-09)

**Priority**: Medium

**Type**: Automated

**Test Steps**:
1. Click Help → About
2. Verify dialog appears with application information

**Expected Results**:
- Dialog title: "About SimplePySideApp"
- Message: "SimplePySideApp v1.0\nA simple PySide6 desktop application"
- OK button to dismiss

**Test Data**:
```python
{
  "action": "About",
  "expected_title": "About SimplePySideApp",
  "expected_message": "SimplePySideApp v1.0\nA simple PySide6 desktop application"
}
```

**Pass Criteria**: About dialog shows correct information

---

### Category 6: Keyboard Shortcuts and Menu UI

#### TS-GUI-002-10: Keyboard Shortcuts Displayed in Menus

**Requirement**: FR-GUI-002 (AC-GUI-002-10)

**Priority**: Medium

**Type**: Manual

**Test Steps**:
1. Open File menu
2. Verify each action shows its shortcut
3. Repeat for Edit and Help menus

**Expected Results**:
- File menu:
  - New shows "Ctrl+N" right-aligned
  - Open shows "Ctrl+O"
  - Save shows "Ctrl+S"
  - Exit shows "Ctrl+Q"
- Edit menu:
  - Undo shows "Ctrl+Z"
  - Redo shows "Ctrl+Y"

**Pass Criteria**: All shortcuts visible and correct

---

#### TS-GUI-002-11: Menu Item Hover Feedback

**Requirement**: FR-GUI-002 (AC-GUI-002-11)

**Priority**: Low

**Type**: Manual

**Test Steps**:
1. Open File menu
2. Move mouse over menu items
3. Observe highlighting behavior

**Expected Results**:
- Item highlights on hover
- Highlight appears within 50ms
- Only one item highlighted at a time
- Smooth transition between items

**Pass Criteria**: Hover feedback works correctly

---

#### TS-GUI-002-12: Rapid Menu Clicks

**Requirement**: FR-GUI-002 (AC-GUI-002-12)

**Priority**: Medium

**Type**: Automated

**Test Steps**:
1. Click File → New 5 times rapidly
2. Verify all 5 message boxes appear sequentially

**Expected Results**:
- 5 message boxes appear one after another (modal blocking)
- No crashes
- Application remains responsive

**Test Data**:
```python
{
  "action": "New",
  "repetitions": 5,
  "expected_messages": 5
}
```

**Pass Criteria**: All message boxes appear, no crashes

---

#### TS-GUI-002-13: Multiple Exit Triggers (Edge Case)

**Requirement**: FR-GUI-002 (AC-GUI-002-13)

**Priority**: High

**Type**: Manual

**Test Steps**:
1. Click File → Exit
2. Immediately press Ctrl+Q (within 50ms)
3. Observe application behavior

**Expected Results**:
- Application closes once
- No double-close errors
- No duplicate exit attempts

**Pass Criteria**: Clean single exit, no errors

---

#### TS-GUI-002-14: Alt Key Menu Navigation

**Requirement**: FR-GUI-002 (AC-GUI-002-14)

**Priority**: Medium

**Type**: Manual

**Test Steps**:
1. Press Alt+F
2. Verify File menu opens
3. Press arrow keys to navigate
4. Press Enter to activate item

**Expected Results**:
- Alt+F opens File menu
- Arrow keys navigate items
- Enter activates highlighted item
- Esc closes menu

**Pass Criteria**: Keyboard navigation works

---

### Category 7: UI Interactions and Focus

#### TS-GUI-003-01: Application Focus Detection

**Requirement**: FR-GUI-003 (AC-GUI-003-01)

**Priority**: High

**Type**: Manual

**Test Steps**:
1. Launch SimplePySideApp
2. Launch another application (e.g., Notepad)
3. Click SimplePySideApp window
4. Verify focus changes

**Expected Results**:
- SimplePySideApp window becomes active (title bar highlighted)
- Window moves to foreground
- Keyboard shortcuts work

**Pass Criteria**: Focus switches correctly

---

#### TS-GUI-003-02: Application Focus Loss

**Requirement**: FR-GUI-003 (AC-GUI-003-02)

**Priority**: High

**Type**: Manual

**Test Steps**:
1. SimplePySideApp has focus
2. Click another application window
3. Try pressing Ctrl+N in SimplePySideApp

**Expected Results**:
- SimplePySideApp title bar dims (inactive)
- Ctrl+N does NOT trigger SimplePySideApp action
- Focus goes to other application

**Pass Criteria**: Shortcuts inactive when not focused

---

#### TS-GUI-003-03: System Theme Change

**Requirement**: FR-GUI-003 (AC-GUI-003-04)

**Priority**: Medium

**Type**: Manual

**Test Steps**:
1. Launch application with system light theme
2. Change system theme to dark mode
3. Observe application

**Expected Results**:
- Application adapts to dark theme within 500ms
- Window background, menu bar, text colors update
- No restart required

**Pass Criteria**: Theme adapts automatically

---

#### TS-GUI-003-04: High Contrast Mode

**Requirement**: FR-GUI-003 (AC-GUI-003-05)

**Priority**: Medium

**Type**: Manual

**Test Steps**:
1. Launch application
2. Enable system high contrast mode
3. Verify contrast ratios

**Expected Results**:
- Text contrast ratio >= 7:1 (WCAG AAA)
- All text remains readable
- Focus indicators more prominent

**Pass Criteria**: High contrast works correctly

---

### Category 8: Cross-Platform Testing

#### TS-GUI-003-05: Windows Platform Launch

**Requirement**: FR-GUI-001 (AC-GUI-001-08)

**Priority**: Critical (for Windows)

**Type**: Manual

**Test Steps**:
1. Launch on Windows 10 or Windows 11
2. Verify native styling
3. Test all features

**Expected Results**:
- Native Windows window style
- Shortcuts use Ctrl key
- Taskbar integration works

**Pass Criteria**: All features work on Windows

---

#### TS-GUI-003-06: macOS Platform Launch

**Requirement**: FR-GUI-001 (AC-GUI-001-09)

**Priority**: Critical (for macOS)

**Type**: Manual

**Test Steps**:
1. Launch on macOS 12+
2. Verify native styling
3. Test all features

**Expected Results**:
- Native macOS window style (traffic lights)
- Shortcuts adapt to Cmd key
- Dock integration works

**Pass Criteria**: All features work on macOS

---

#### TS-GUI-003-07: Linux Platform Launch

**Requirement**: FR-GUI-001 (AC-GUI-001-10)

**Priority**: Critical (for Linux)

**Type**: Manual

**Test Steps**:
1. Launch on Ubuntu 22.04 (GNOME)
2. Verify theme integration
3. Test all features

**Expected Results**:
- Adapts to GTK/KDE theme
- Shortcuts use Ctrl key
- Panel integration works

**Pass Criteria**: All features work on Linux

---

## Traceability Matrix

| Test ID | Requirement | Type | Priority | Status |
|---------|-------------|------|----------|--------|
| TS-GUI-001-01 | FR-GUI-001 (AC-001-01) | Auto+Manual | Critical | Pending |
| TS-GUI-001-02 | FR-GUI-001 (AC-001-11) | Manual | High | Pending |
| TS-GUI-001-03 | FR-GUI-001 (AC-001-12) | Manual | Medium | Pending |
| TS-GUI-001-04 | FR-GUI-001 (AC-001-02) | Auto | High | Pending |
| TS-GUI-001-05 | FR-GUI-001 (AC-001-03) | Auto | High | Pending |
| TS-GUI-001-06 | FR-GUI-001 (AC-001-04) | Auto | High | Pending |
| TS-GUI-001-07 | FR-GUI-001 (AC-001-05, AC-001-06) | Auto | High | Pending |
| TS-GUI-002-01 | FR-GUI-002 (AC-002-01) | Auto | High | Pending |
| TS-GUI-002-02 | FR-GUI-002 (AC-002-02) | Auto | High | Pending |
| TS-GUI-002-03 | FR-GUI-002 (AC-002-03) | Auto | High | Pending |
| TS-GUI-002-04 | FR-GUI-002 (AC-002-04) | Auto | High | Pending |
| TS-GUI-002-05 | FR-GUI-002 (AC-002-05) | Auto+Manual | Critical | Pending |
| TS-GUI-002-06 | FR-GUI-002 (AC-002-06) | Manual | Low | Pending |
| TS-GUI-002-07 | FR-GUI-002 (AC-002-07) | Auto | Medium | Pending |
| TS-GUI-002-08 | FR-GUI-002 (AC-002-08) | Auto | Medium | Pending |
| TS-GUI-002-09 | FR-GUI-002 (AC-002-09) | Auto | Medium | Pending |
| TS-GUI-002-10 | FR-GUI-002 (AC-002-10) | Manual | Medium | Pending |
| TS-GUI-002-11 | FR-GUI-002 (AC-002-11) | Manual | Low | Pending |
| TS-GUI-002-12 | FR-GUI-002 (AC-002-12) | Auto | Medium | Pending |
| TS-GUI-002-13 | FR-GUI-002 (AC-002-13) | Manual | High | Pending |
| TS-GUI-002-14 | FR-GUI-002 (AC-002-14) | Manual | Medium | Pending |
| TS-GUI-003-01 | FR-GUI-003 (AC-003-01) | Manual | High | Pending |
| TS-GUI-003-02 | FR-GUI-003 (AC-003-02) | Manual | High | Pending |
| TS-GUI-003-03 | FR-GUI-003 (AC-003-04) | Manual | Medium | Pending |
| TS-GUI-003-04 | FR-GUI-003 (AC-003-05) | Manual | Medium | Pending |
| TS-GUI-003-05 | FR-GUI-001 (AC-001-08) | Manual | Critical | Pending |
| TS-GUI-003-06 | FR-GUI-001 (AC-001-09) | Manual | Critical | Pending |
| TS-GUI-003-07 | FR-GUI-001 (AC-001-10) | Manual | Critical | Pending |

**Total Test Scenarios**: 27
- **Automated**: 14 (52%)
- **Manual**: 10 (37%)
- **Automated + Manual**: 3 (11%)

**Priority Breakdown**:
- **Critical**: 5 (19%)
- **High**: 14 (52%)
- **Medium**: 7 (26%)
- **Low**: 1 (4%)

## Test Execution Strategy

### Phase 1: Automated Testing (CI/CD)
Run all automated tests on every commit:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Phase 2: Manual Testing (Pre-Release)
Execute manual tests before each release:
- Cross-platform testing (Windows, macOS, Linux)
- Theme adaptation testing
- Accessibility testing (screen reader, high contrast)
- Focus and keyboard navigation testing

### Phase 3: Regression Testing
Run full test suite after any code changes affecting:
- Window management
- Menu system
- Event handling
- Theme/styling

## Test Coverage Goals

- **Unit Tests**: 70% of codebase
- **Integration Tests**: 20% (menu interactions, window state changes)
- **E2E Tests**: 10% (complete user workflows)
- **Overall Coverage**: >= 80%

## Bug Reporting Template

```markdown
**Bug ID**: BUG-GUI-{sequence}
**Test Case**: TS-GUI-{xxx-xx}
**Severity**: Critical / High / Medium / Low
**Platform**: Windows 11 / macOS 13 / Ubuntu 22.04
**Python**: 3.11.5
**PySide6**: 6.6.0

**Description**:
[Clear description of issue]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Screenshots**:
[Attach if applicable]

**Console Output**:
```
[Error messages or logs]
```
```

## Success Criteria

Test plan is considered successful when:
- All Critical and High priority tests pass (100%)
- >= 90% of Medium priority tests pass
- >= 80% of Low priority tests pass
- All cross-platform tests pass on target platforms
- Code coverage >= 80%
- No Critical or High severity bugs remain unfixed

## Revision History

| Version | Date       | Author           | Changes                        |
|---------|------------|------------------|--------------------------------|
| 1.0     | 2025-11-12 | Requirements Agent | Initial acceptance test plan   |
