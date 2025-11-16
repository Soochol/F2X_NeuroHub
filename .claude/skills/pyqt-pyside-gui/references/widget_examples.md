# Widget Examples Reference

Common usage patterns for Qt widgets.

## Input Widgets

### QLineEdit

```python
# Basic usage
line_edit = QLineEdit()
line_edit.setPlaceholderText("Enter text...")
line_edit.setText("Initial value")
text = line_edit.text()

# Input validation
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
line_edit.setValidator(QIntValidator(0, 100))  # Only integers 0-100

# Input mask
line_edit.setInputMask("000.000.000.000;_")  # IP address

# Signals
line_edit.textChanged.connect(lambda text: print(f"Changed: {text}"))
line_edit.editingFinished.connect(lambda: print("Editing finished"))
line_edit.returnPressed.connect(lambda: print("Return pressed"))

# Completion
from PySide6.QtWidgets import QCompleter
completer = QCompleter(["Apple", "Banana", "Cherry"])
line_edit.setCompleter(completer)

# Password mode
line_edit.setEchoMode(QLineEdit.Password)
```

### QTextEdit

```python
# Basic usage
text_edit = QTextEdit()
text_edit.setPlainText("Plain text")
text_edit.setHtml("<b>Bold</b> text")
plain_text = text_edit.toPlainText()
html = text_edit.toHtml()

# Read-only
text_edit.setReadOnly(True)

# Text cursor operations
cursor = text_edit.textCursor()
cursor.movePosition(QTextCursor.End)
text_edit.setTextCursor(cursor)

# Append text
text_edit.append("New line")

# Signals
text_edit.textChanged.connect(lambda: print("Text changed"))
```

### QSpinBox / QDoubleSpinBox

```python
# Integer spin box
spin_box = QSpinBox()
spin_box.setRange(0, 100)
spin_box.setValue(50)
spin_box.setSingleStep(5)
spin_box.setPrefix("Value: ")
spin_box.setSuffix(" units")

# Double spin box
double_spin = QDoubleSpinBox()
double_spin.setRange(0.0, 100.0)
double_spin.setDecimals(2)
double_spin.setSingleStep(0.1)

# Signals
spin_box.valueChanged.connect(lambda value: print(f"Value: {value}"))
```

### QComboBox

```python
# Basic usage
combo = QComboBox()
combo.addItem("Option 1")
combo.addItems(["Option 2", "Option 3", "Option 4"])
combo.insertItem(1, "Inserted")

# With data
combo.addItem("Display Text", userData="value1")
current_data = combo.currentData()

# Current selection
current_text = combo.currentText()
current_index = combo.currentIndex()
combo.setCurrentIndex(2)
combo.setCurrentText("Option 3")

# Editable combo box
combo.setEditable(True)
combo.setInsertPolicy(QComboBox.InsertAtTop)

# Signals
combo.currentIndexChanged.connect(lambda index: print(f"Index: {index}"))
combo.currentTextChanged.connect(lambda text: print(f"Text: {text}"))

# Clear and populate
combo.clear()
combo.addItems(new_items)
```

### QCheckBox / QRadioButton

```python
# Checkbox
checkbox = QCheckBox("Enable feature")
checkbox.setChecked(True)
is_checked = checkbox.isChecked()
checkbox.setTristate(True)  # Allow three states

# Radio button group
from PySide6.QtWidgets import QButtonGroup
radio1 = QRadioButton("Option 1")
radio2 = QRadioButton("Option 2")
radio3 = QRadioButton("Option 3")

button_group = QButtonGroup()
button_group.addButton(radio1, 1)
button_group.addButton(radio2, 2)
button_group.addButton(radio3, 3)

# Signals
checkbox.stateChanged.connect(lambda state: print(f"State: {state}"))
radio1.toggled.connect(lambda checked: print(f"Toggled: {checked}"))
button_group.buttonClicked.connect(lambda button: print(f"Clicked: {button.text()}"))
```

## Display Widgets

### QLabel

```python
# Text label
label = QLabel("Text")
label.setText("New text")
label.setAlignment(Qt.AlignCenter)
label.setWordWrap(True)

# Rich text
label.setTextFormat(Qt.RichText)
label.setText("<h1>Title</h1><p>Paragraph</p>")

# Image label
from PySide6.QtGui import QPixmap
pixmap = QPixmap("image.png")
label.setPixmap(pixmap)
label.setScaledContents(True)  # Scale image to fit

# Link handling
label.setOpenExternalLinks(True)
label.setText('<a href="https://example.com">Link</a>')
label.linkActivated.connect(lambda url: print(f"Clicked: {url}"))
```

### QTableWidget

```python
# Create table
table = QTableWidget(5, 3)  # rows, columns
table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

# Add items
from PySide6.QtWidgets import QTableWidgetItem
table.setItem(0, 0, QTableWidgetItem("Data"))

# Get items
item = table.item(0, 0)
if item:
    text = item.text()

# Insert/remove rows
table.insertRow(2)
table.removeRow(2)

# Selection
table.setSelectionBehavior(QTableWidget.SelectRows)
table.setSelectionMode(QTableWidget.SingleSelection)
selected_items = table.selectedItems()

# Resize columns
table.resizeColumnsToContents()
table.horizontalHeader().setStretchLastSection(True)

# Signals
table.itemClicked.connect(lambda item: print(f"Clicked: {item.text()}"))
table.itemChanged.connect(lambda item: print(f"Changed: {item.text()}"))
table.cellClicked.connect(lambda row, col: print(f"Cell: {row}, {col}"))
```

### QListWidget

```python
# Create list
list_widget = QListWidget()
list_widget.addItem("Item 1")
list_widget.addItems(["Item 2", "Item 3", "Item 4"])

# Custom items
from PySide6.QtWidgets import QListWidgetItem
item = QListWidgetItem("Custom Item")
item.setCheckState(Qt.Checked)
list_widget.addItem(item)

# Selection
list_widget.setCurrentRow(0)
current_item = list_widget.currentItem()
selected_items = list_widget.selectedItems()

# Remove items
list_widget.takeItem(0)
list_widget.clear()

# Signals
list_widget.itemClicked.connect(lambda item: print(f"Clicked: {item.text()}"))
list_widget.currentItemChanged.connect(lambda current, previous: print("Changed"))
```

### QTreeWidget

```python
# Create tree
tree = QTreeWidget()
tree.setHeaderLabels(["Name", "Value"])

# Add top-level items
from PySide6.QtWidgets import QTreeWidgetItem
root = QTreeWidgetItem(tree, ["Root", "Value"])

# Add children
child1 = QTreeWidgetItem(root, ["Child 1", "Value 1"])
child2 = QTreeWidgetItem(root, ["Child 2", "Value 2"])

# Expand/collapse
tree.expandAll()
tree.collapseAll()
root.setExpanded(True)

# Selection
tree.setSelectionMode(QTreeWidget.SingleSelection)
selected_items = tree.selectedItems()

# Signals
tree.itemClicked.connect(lambda item, col: print(f"Clicked: {item.text(0)}"))
tree.itemExpanded.connect(lambda item: print("Expanded"))
tree.itemCollapsed.connect(lambda item: print("Collapsed"))
```

## Container Widgets

### QGroupBox

```python
# Create group box
group = QGroupBox("Settings")
layout = QVBoxLayout()
layout.addWidget(QCheckBox("Option 1"))
layout.addWidget(QCheckBox("Option 2"))
group.setLayout(layout)

# Checkable group box
group.setCheckable(True)
group.setChecked(True)
```

### QTabWidget

```python
# Create tabs
tabs = QTabWidget()
tabs.addTab(QWidget(), "Tab 1")
tabs.addTab(QWidget(), "Tab 2")
tabs.addTab(QWidget(), "Tab 3")

# Tab with icon
from PySide6.QtGui import QIcon
tabs.addTab(QWidget(), QIcon("icon.png"), "Tab 4")

# Tab position
tabs.setTabPosition(QTabWidget.North)  # North, South, East, West

# Current tab
tabs.setCurrentIndex(1)
current_widget = tabs.currentWidget()
current_index = tabs.currentIndex()

# Closeable tabs
tabs.setTabsClosable(True)
tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))

# Signals
tabs.currentChanged.connect(lambda index: print(f"Tab: {index}"))
```

### QScrollArea

```python
# Create scroll area
scroll = QScrollArea()
scroll.setWidgetResizable(True)

# Content widget
content = QWidget()
layout = QVBoxLayout(content)
for i in range(50):
    layout.addWidget(QLabel(f"Item {i}"))

scroll.setWidget(content)

# Scroll bar policy
scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
```

### QStackedWidget

```python
# Create stacked widget
stack = QStackedWidget()
stack.addWidget(QWidget())  # Page 0
stack.addWidget(QWidget())  # Page 1
stack.addWidget(QWidget())  # Page 2

# Switch pages
stack.setCurrentIndex(1)
stack.setCurrentWidget(some_widget)

# Signals
stack.currentChanged.connect(lambda index: print(f"Page: {index}"))
```

## Button Widgets

### QPushButton

```python
# Basic button
button = QPushButton("Click Me")
button.setText("New Text")

# Icon button
button.setIcon(QIcon("icon.png"))
button.setIconSize(QSize(24, 24))

# Checkable button
button.setCheckable(True)
button.setChecked(True)
is_checked = button.isChecked()

# Default button
button.setDefault(True)
button.setAutoDefault(True)

# Signals
button.clicked.connect(lambda: print("Clicked"))
button.pressed.connect(lambda: print("Pressed"))
button.released.connect(lambda: print("Released"))
button.toggled.connect(lambda checked: print(f"Toggled: {checked}"))
```

### QToolButton

```python
# Tool button
tool_button = QToolButton()
tool_button.setIcon(QIcon("icon.png"))
tool_button.setToolTip("Tool tip")

# Text beside icon
tool_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
tool_button.setText("Action")

# Popup menu
from PySide6.QtWidgets import QMenu
menu = QMenu()
menu.addAction("Action 1")
menu.addAction("Action 2")
tool_button.setMenu(menu)
tool_button.setPopupMode(QToolButton.InstantPopup)
```

## Slider and Dial

### QSlider

```python
# Horizontal slider
slider = QSlider(Qt.Horizontal)
slider.setRange(0, 100)
slider.setValue(50)
slider.setSingleStep(1)
slider.setPageStep(10)
slider.setTickPosition(QSlider.TicksBelow)
slider.setTickInterval(10)

# Signals
slider.valueChanged.connect(lambda value: print(f"Value: {value}"))
slider.sliderMoved.connect(lambda value: print(f"Moved: {value}"))
slider.sliderPressed.connect(lambda: print("Pressed"))
slider.sliderReleased.connect(lambda: print("Released"))
```

### QDial

```python
# Dial
dial = QDial()
dial.setRange(0, 100)
dial.setValue(50)
dial.setNotchesVisible(True)

# Signals (same as QSlider)
dial.valueChanged.connect(lambda value: print(f"Value: {value}"))
```

## Date and Time

### QDateEdit / QTimeEdit / QDateTimeEdit

```python
from PySide6.QtCore import QDate, QTime, QDateTime

# Date edit
date_edit = QDateEdit()
date_edit.setDate(QDate.currentDate())
date_edit.setDisplayFormat("yyyy-MM-dd")
date_edit.setCalendarPopup(True)

# Time edit
time_edit = QTimeEdit()
time_edit.setTime(QTime.currentTime())
time_edit.setDisplayFormat("HH:mm:ss")

# DateTime edit
datetime_edit = QDateTimeEdit()
datetime_edit.setDateTime(QDateTime.currentDateTime())

# Signals
date_edit.dateChanged.connect(lambda date: print(f"Date: {date.toString()}"))
time_edit.timeChanged.connect(lambda time: print(f"Time: {time.toString()}"))
```
