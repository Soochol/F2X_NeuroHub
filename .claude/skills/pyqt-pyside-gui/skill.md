---
name: pyqt-pyside-gui
description: Comprehensive guide for building desktop GUI applications using PyQt6/PySide6. Use when the user requests to create, modify, or debug Qt-based desktop applications, needs GUI components like windows, dialogs, widgets, signals/slots, layouts, or asks about PyQt/PySide development patterns, MVC/MVP architecture, threading, or cross-platform desktop app development.
---

# PyQt/PySide GUI Development

Build professional desktop applications using PyQt6 or PySide6 with proper architecture patterns, clean code structure, and best practices.

## Core Development Workflow

1. **Determine framework choice**: Use PySide6 (LGPL, official Qt) by default unless user specifies PyQt6
2. **Set up development environment**: Use hot reload and visual debugger for instant feedback
3. **Plan application structure**: Separate UI logic from business logic using MVC/MVP patterns
4. **Design UI layout**: Choose appropriate layout managers (QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout)
5. **Implement signal/slot connections**: Connect user interactions to application logic
6. **Handle threading**: Keep UI responsive by moving long operations to QThread
7. **Debug visually**: Use visual debugger to inspect widgets, layouts, and find issues
8. **Test and refine**: Ensure proper cleanup and resource management

## AI-Friendly Development Workflow

When developing with AI assistance, use these tools for better results:

### JSON Theme System (RECOMMENDED)
Define and customize your entire app theme in JSON:
```python
from ui_components import load_theme, list_themes

app = QApplication(sys.argv)

# Load theme from JSON file
theme = load_theme(app, "default")  # or "dark"

# List available themes
print(list_themes())  # ['default', 'dark', ...]
```

**Benefits:**
- ✅ Entire theme controlled by JSON file
- ✅ Switch themes at runtime
- ✅ AI can easily modify JSON structure
- ✅ Variable references for consistency
- ✅ Multiple theme management (light/dark/custom)

See `references/json_theme_guide.md` for complete JSON theme documentation.

### Component Library
Use pre-built, themed components for consistent UI:
```python
from ui_components import Button, FormField, Card, ButtonGroup

# Components automatically use loaded theme
button = Button("Save", variant="primary")
email = FormField("Email", required=True)
card = Card(title="User Info")

# Button group with multiple variants
buttons = ButtonGroup([
    {"text": "Submit", "variant": "success", "callback": submit},
    {"text": "Cancel", "variant": "secondary", "callback": cancel}
])
```

**Benefits:**
- Consistent design across entire app
- Built-in validation and error handling
- Automatic theme application
- AI can use components reliably
- Reduces layout/styling issues

See `references/component_library_guide.md` for complete documentation.

### Hot Reload Preview
Instantly see changes without restarting:
```bash
python hot_reload_preview.py your_app.py

# With visual debugger
python hot_reload_preview.py your_app.py --debug
```

### Visual Debugger
Interactive GUI debugger that shows:
- Widget tree with real-time status
- Inspector panel with detailed widget information
- Visual overlay highlighting selected widgets
- Automatic issue detection
- Layout problem diagnosis

Usage:
```python
from visual_debugger import launch_with_debugger

app = QApplication(sys.argv)
window = MainWindow()
debugger = launch_with_debugger(window)
sys.exit(app.exec())
```

Features:
- Click widgets in tree to inspect them
- See them highlighted in your app
- Check "Show All Borders" to visualize all widgets
- Use "Issues" tab to find common problems
- Export screenshots and reports

### GUI Code Analyzer - Static Analysis (NEW!)
Analyze UI code files without running the app:
```bash
cd .claude/skills/pyqt-pyside-gui/tools
python gui_analyzer.py views/main_window.py
```

**What it does:**
- 🌳 Automatically extracts widget tree from code
- 🔍 Analyzes each widget's properties (geometry, visibility, styling)
- ⚠️ Detects issues: overlapping widgets, hidden widgets, size problems
- ✅ Validates skill.md best practices (theme usage, hardcoded colors, naming)
- 📊 Generates comprehensive HTML report

**Key Features:**
1. **Overlapping Detection**: Finds widgets that may overlap based on geometry
2. **Size Issues**: Detects too-small widgets (<10px) or min/max conflicts
3. **Layout Problems**: Finds widgets without parents (memory leaks)
4. **Best Practices Check**:
   - Uses Theme Manager (`get_theme()`)
   - Uses Themed Components
   - No hardcoded colors (#RRGGBB)
   - Object names set (`setObjectName`)
   - Has docstrings

**Output:** HTML report with:
- Widget tree visualization
- Property tables
- Issues list (error/warning/info)
- Best practices checklist
- Widget type distribution

**Use Cases:**
- Code review before PR
- Finding layout issues early
- Validating theme system usage
- Documentation generation

See `README_GUI_ANALYZER.md` for full documentation.

### AI Coding Best Practices

When requesting GUI changes from AI, use specific, component-based language:

#### ❌ Bad Requests
```
"로그인 화면 만들어줘"
"색상이 이상해"
"버튼을 파란색으로 만들어줘"
"폼이 이상해 보여"
```

#### ✅ Good Requests
```python
# Specific component-based request
"PySide6로 로그인 화면 만들어줘:
- ui_components 사용
- load_theme(app, 'default')로 테마 로드
- Card 안에 FormField 2개 (email, password)
- ButtonGroup으로 버튼
- 창 크기 400x350"

# Theme modification request
"scripts/ui_components/themes/default.json에서
colors.primary.main을 #9C27B0 (보라색)으로 변경해줘"

# Visual debugger feedback
"비주얼 디버거를 보니 button의 색상이 #95a5a6로 표시됨.
이것을 themes/default.json에서
colors.primary.main으로 변경해줘."

# Component variant change
"Button의 variant를 'secondary'에서 'primary'로 변경해줘"

# Layout spacing change
"layout spacing을 Spacing.NORMAL에서 Spacing.LARGE로 변경해줘"
```

**Why This Works:**
- ✅ Uses exact component names and APIs
- ✅ References actual file paths
- ✅ Specifies variant/color values precisely
- ✅ Leverages visual debugger output
- ✅ AI can make changes without guessing

## Application Architecture

### Project Structure

```
app_name/
├── main.py              # Application entry point
├── ui/
│   ├── main_window.py   # Main window class
│   ├── dialogs.py       # Custom dialogs
│   └── widgets.py       # Custom widgets
├── models/
│   └── data_model.py    # Data models
├── controllers/
│   └── controller.py    # Business logic
├── resources/
│   ├── icons/           # Icon files
│   └── styles.qss       # Qt stylesheets
└── utils/
    └── helpers.py       # Utility functions
```

### Clean Architecture Pattern

Separate concerns into three layers:

1. **View (UI)**: QMainWindow, QWidget subclasses - handle display only
2. **Model**: Data structures and business logic
3. **Controller/Presenter**: Mediate between View and Model

## Essential Patterns

### Basic Application Template

See `scripts/basic_app.py` for a complete minimal application template.

### Signal/Slot Best Practices

```python
# Good: Use lambda for simple parameter passing
button.clicked.connect(lambda: self.process_data(param))

# Good: Use functools.partial for multiple parameters
from functools import partial
button.clicked.connect(partial(self.update_value, key, value))

# Good: Custom signals for inter-widget communication
class Worker(QObject):
    progress = Signal(int)
    finished = Signal(str)
```

### Layout Management

- **QVBoxLayout/QHBoxLayout**: Linear layouts
- **QGridLayout**: Grid-based positioning
- **QFormLayout**: Label-field pairs
- **Spacers**: Use `addStretch()` or `QSpacerItem` for flexible spacing
- **Nested layouts**: Combine layouts for complex UIs

### Threading for Responsive UI

```python
class Worker(QThread):
    progress = Signal(int)
    result = Signal(object)
    
    def run(self):
        # Long-running operation
        for i in range(100):
            time.sleep(0.1)
            self.progress.emit(i)
        self.result.emit(final_result)

# In main window
self.worker = Worker()
self.worker.progress.connect(self.update_progress)
self.worker.result.connect(self.handle_result)
self.worker.start()
```

## Common Components

### Widgets

- **Input**: QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox
- **Display**: QLabel, QTextBrowser, QTableWidget, QTreeWidget, QListWidget
- **Buttons**: QPushButton, QRadioButton, QCheckBox, QToolButton
- **Containers**: QGroupBox, QTabWidget, QStackedWidget, QScrollArea
- **Advanced**: QTableView (with models), QTreeView, QListView

### Dialogs

```python
# File dialogs
filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")

# Message boxes
QMessageBox.information(self, "Title", "Message")
QMessageBox.warning(self, "Title", "Warning")
QMessageBox.critical(self, "Title", "Error")
result = QMessageBox.question(self, "Title", "Question?")

# Input dialog
text, ok = QInputDialog.getText(self, "Input", "Enter name:")
```

### Menus and Toolbars

```python
# Menu bar
menu_bar = self.menuBar()
file_menu = menu_bar.addMenu("&File")
file_menu.addAction("&Open", self.open_file, "Ctrl+O")

# Toolbar
toolbar = self.addToolBar("Main Toolbar")
toolbar.addAction(QIcon("icon.png"), "Action", self.action_handler)
```

## Styling

### Qt Stylesheets (QSS)

See `references/qss_guide.md` for comprehensive styling examples.

Basic syntax:
```css
QPushButton {
    background-color: #2196F3;
    color: white;
    border-radius: 5px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #1976D2;
}
```

Apply styles:
```python
widget.setStyleSheet("QLabel { color: red; }")
app.setStyleSheet(Path("styles.qss").read_text())
```

## Model/View Architecture

For complex data display, use Model/View:

```python
# Model
model = QStandardItemModel()
model.setHorizontalHeaderLabels(['Column 1', 'Column 2'])

# Add data
item = QStandardItem("Data")
model.appendRow([item, QStandardItem("More data")])

# View
table_view = QTableView()
table_view.setModel(model)
```

## Resource Management

### Cleanup Pattern

```python
def closeEvent(self, event):
    """Override to cleanup resources"""
    if self.worker and self.worker.isRunning():
        self.worker.terminate()
        self.worker.wait()
    event.accept()
```

### Qt Resource System

For embedding resources (icons, images):
```python
# Create .qrc file, compile with pyside6-rcc
# Use in code:
icon = QIcon(":/icons/app_icon.png")
```

## Common Pitfalls

1. **Blocking UI thread**: Always use QThread for long operations
2. **Circular references**: Properly parent widgets to avoid memory leaks
3. **Signal connection**: Use `connect()` not `emit()` for connections
4. **Layout conflicts**: Don't mix manual positioning with layouts
5. **Resource cleanup**: Override `closeEvent()` for proper shutdown

## PyQt6 vs PySide6 Differences

Key import differences:
```python
# PyQt6
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, pyqtSlot

# PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, Slot
```

**Default recommendation**: Use PySide6 (official, LGPL license, better Qt compatibility)

## References

- **JSON Theme Guide**: `references/json_theme_guide.md` - JSON-based theme system (RECOMMENDED)
- **Component Library Guide**: `references/component_library_guide.md` - Complete component library documentation
- **AI-Friendly Patterns**: `references/ai_friendly_patterns.md` - Best practices for AI-assisted development
- **QSS Styling Guide**: `references/qss_guide.md` - Complete stylesheet reference
- **Widget Examples**: `references/widget_examples.md` - Common widget usage patterns
- **Advanced Patterns**: `references/advanced_patterns.md` - Custom widgets, painting, animations

## Scripts

### Examples
- **json_theme_example.py**: Complete example with JSON theme switching
- **component_example.py**: Component library usage example
- **basic_app.py**: Minimal application template
- **threaded_app.py**: Background worker thread example
- **table_model.py**: Custom model for QTableView
- **dialog_examples.py**: Common dialog patterns

### Development Tools
- **visual_debugger.py**: Interactive visual debugger with widget inspector
- **hot_reload_preview.py**: Auto-reload system for rapid development

### Component Library
- **ui_components/**: Centralized component library with JSON theming
  - `__init__.py`: Main exports (load_theme, Button, FormField, etc.)
  - `theme_loader.py`: JSON theme loader and manager
  - `components.py`: Reusable UI components
  - `theme.py`: Legacy Python-based theme (for reference)
  - `themes/default.json`: Default light theme
  - `themes/dark.json`: Dark theme

## Practical Tips

### 1. Always Load Theme First

```python
# ✅ Correct order
app = QApplication(sys.argv)
load_theme(app, "default")  # Load theme FIRST
window = MainWindow()
window.show()

# ❌ Wrong order - theme won't apply properly
app = QApplication(sys.argv)
window = MainWindow()
load_theme(app, "default")  # Too late!
```

### 2. Use Components, Not Raw Qt Widgets

```python
# ❌ Don't create widgets directly
button = QPushButton("Click")
button.setStyleSheet("background: #3498db")  # Hard to maintain

# ✅ Use themed components
button = Button("Click", variant="primary")  # Automatically themed
```

### 3. Manage Colors in JSON, Not Code

```python
# ❌ Hard-coded colors in code
button.setStyleSheet("background: #3498db; color: white;")

# ✅ Use JSON theme system
# Edit themes/default.json:
# "colors": { "primary": { "main": "#3498db" } }
# Components use theme automatically
```

### 4. Leverage Hot Reload During Development

```bash
# Always use hot reload when developing
python hot_reload_preview.py app.py --debug

# Benefits:
# - See changes instantly (no restart needed)
# - Visual debugger shows widget info
# - Saves time on every edit
```

### 5. Use Visual Debugger for Problem Solving

```python
# When something looks wrong:
# 1. Open visual debugger
# 2. Click the problematic widget in tree
# 3. Check Inspector panel for exact values
# 4. Report specific values to AI for fixing

# Example feedback:
"비주얼 디버거에서 보니:
- Widget: QPushButton
- Background: #95a5a6 (should be #3498db)
- Font size: 12px (should be 14px)
themes/default.json에서 수정해줘"
```

### 6. Component-First Development

```python
# ✅ Start with components
card = Card(title="Settings")
name_field = FormField("Name", required=True)
card.add_component(name_field)

# ❌ Don't mix raw widgets with components
# This creates styling inconsistencies
```

### 7. Use Spacing Constants

```python
# ❌ Magic numbers
layout.setSpacing(12)
layout.setContentsMargins(16, 16, 16, 16)

# ✅ Named constants
layout.setSpacing(Spacing.NORMAL)
layout.setContentsMargins(
    Spacing.MEDIUM, Spacing.MEDIUM,
    Spacing.MEDIUM, Spacing.MEDIUM
)
```

### 8. Validate Forms Properly

```python
# ✅ Validate all fields before processing
fields = [email_field, password_field, name_field]
if all(field.validate() for field in fields):
    # All valid - proceed
    process_form()
else:
    # Some fields invalid - errors shown automatically
    return
```

## Quick Reference

### Complete Workflow Example (Component Library)

```python
# 1. Import
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

sys.path.insert(0, '/path/to/scripts')
from ui_components import *

# 2. Create app and load theme
app = QApplication(sys.argv)
theme = load_theme(app, "default")  # IMPORTANT: Load theme first!

# 3. Build UI with components
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 500, 400)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(Spacing.LARGE)
        layout.setContentsMargins(
            Spacing.LARGE, Spacing.LARGE,
            Spacing.LARGE, Spacing.LARGE
        )

        # Title
        title = Label("Welcome", variant="title", alignment=Qt.AlignCenter)
        layout.addWidget(title.get_widget())

        # Form card
        card = Card(title="Login Form")

        self.email = FormField("Email", required=True)
        card.add_component(self.email)

        self.password = FormField("Password", input_type="password", required=True)
        card.add_component(self.password)

        layout.addWidget(card.get_widget())
        layout.addStretch()

        # Buttons
        buttons = ButtonGroup([
            {"text": "Login", "variant": "primary", "callback": self.login},
            {"text": "Cancel", "variant": "secondary", "callback": self.close}
        ])
        layout.addWidget(buttons.get_widget())

    def login(self):
        if self.email.validate() and self.password.validate():
            print(f"Login: {self.email.get_value()}")

# 4. Run app
window = MainWindow()
window.show()
sys.exit(app.exec())
```

### Minimal Example (Component Library)

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

sys.path.insert(0, '/path/to/scripts')
from ui_components import load_theme, Button, FormField, Card

app = QApplication(sys.argv)
theme = load_theme(app, "default")  # Load theme first

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Name")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Use components
        card = Card(title="User Info")
        self.email = FormField("Email", required=True)
        card.add_component(self.email)
        layout.addWidget(card.get_widget())

window = MainWindow()
window.show()
sys.exit(app.exec())
```

### Standard PySide6 Imports
```python
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QIcon, QAction, QFont
```

### Basic Structure (Without Components)
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("App Name")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```
