# Advanced Patterns

Advanced techniques for Qt application development.

## Custom Widgets

### Basic Custom Widget

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal

class CustomWidget(QWidget):
    """Custom widget with encapsulated functionality"""
    
    # Custom signals
    valueChanged = Signal(int)
    actionTriggered = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Custom Widget")
        layout.addWidget(self.label)
        
        button = QPushButton("Action")
        button.clicked.connect(self.on_action)
        layout.addWidget(button)
        
    def on_action(self):
        """Handle action"""
        self.actionTriggered.emit("action_performed")
        
    def set_value(self, value):
        """Set value and emit signal"""
        self._value = value
        self.label.setText(f"Value: {value}")
        self.valueChanged.emit(value)
```

### Widget with Painting

```python
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRect

class CustomPaintWidget(QWidget):
    """Widget with custom painting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self._value = 50
        
    def set_value(self, value):
        """Update value and repaint"""
        self._value = max(0, min(100, value))
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Custom painting"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # Draw circle
        rect = QRect(10, 10, self.width() - 20, self.height() - 20)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(100, 150, 250))
        painter.drawEllipse(rect)
        
        # Draw text
        painter.setPen(Qt.white)
        painter.drawText(rect, Qt.AlignCenter, f"{self._value}%")
```

## Drag and Drop

### Enable Drag and Drop

```python
from PySide6.QtWidgets import QListWidget, QAbstractItemView
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag

class DragDropListWidget(QListWidget):
    """List widget with drag and drop support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle drop"""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            self.addItem(text)
            event.acceptProposedAction()
```

### Custom Drag Source

```python
class DragSourceWidget(QWidget):
    """Widget that can be dragged from"""
    
    def mousePressEvent(self, event):
        """Start drag on mouse press"""
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText("Dragged data")
            drag.setMimeData(mime_data)
            
            # Optional: set drag pixmap
            # drag.setPixmap(QPixmap("icon.png"))
            
            drag.exec(Qt.CopyAction | Qt.MoveAction)
```

## Animations

### Property Animation

```python
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

class AnimatedWidget(QWidget):
    """Widget with animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button = QPushButton("Animate", self)
        self.button.clicked.connect(self.start_animation)
        
    def start_animation(self):
        """Start animation"""
        # Animate geometry
        animation = QPropertyAnimation(self.button, b"geometry")
        animation.setDuration(1000)  # milliseconds
        animation.setStartValue(QRect(0, 0, 100, 30))
        animation.setEndValue(QRect(200, 100, 100, 30))
        animation.setEasingCurve(QEasingCurve.OutBounce)
        animation.start()
        
        # Animate opacity
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        effect = QGraphicsOpacityEffect(self.button)
        self.button.setGraphicsEffect(effect)
        
        opacity_animation = QPropertyAnimation(effect, b"opacity")
        opacity_animation.setDuration(1000)
        opacity_animation.setStartValue(1.0)
        opacity_animation.setEndValue(0.0)
        opacity_animation.start()
```

### Animation Group

```python
from PySide6.QtCore import QParallelAnimationGroup, QSequentialAnimationGroup

def create_animation_group():
    """Create parallel animations"""
    group = QParallelAnimationGroup()
    
    # Add multiple animations
    anim1 = QPropertyAnimation(widget1, b"pos")
    anim2 = QPropertyAnimation(widget2, b"size")
    
    group.addAnimation(anim1)
    group.addAnimation(anim2)
    
    group.start()
    
def create_sequential_animation():
    """Create sequential animations"""
    group = QSequentialAnimationGroup()
    
    anim1 = QPropertyAnimation(widget, b"pos")
    anim1.setDuration(1000)
    
    anim2 = QPropertyAnimation(widget, b"size")
    anim2.setDuration(1000)
    
    group.addAnimation(anim1)
    group.addAnimation(anim2)
    
    group.start()
```

## Resource System

### Creating Resource Files

```xml
<!-- resources.qrc -->
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="/">
        <file>icons/app_icon.png</file>
        <file>icons/close.png</file>
        <file>styles/style.qss</file>
    </qresource>
</RCC>
```

### Compiling Resources

```bash
# PySide6
pyside6-rcc resources.qrc -o resources_rc.py

# PyQt6
pyrcc6 resources.qrc -o resources_rc.py
```

### Using Resources

```python
import resources_rc  # Import compiled resources

# Use resources
icon = QIcon(":/icons/app_icon.png")
stylesheet = QFile(":/styles/style.qss")
stylesheet.open(QFile.ReadOnly)
app.setStyleSheet(str(stylesheet.readAll(), encoding='utf-8'))
```

## Settings and Configuration

### Using QSettings

```python
from PySide6.QtCore import QSettings

class Application:
    """Application with persistent settings"""
    
    def __init__(self):
        self.settings = QSettings("MyCompany", "MyApp")
        self.load_settings()
        
    def load_settings(self):
        """Load settings"""
        window_size = self.settings.value("window/size", QSize(800, 600))
        window_pos = self.settings.value("window/position", QPoint(100, 100))
        recent_files = self.settings.value("recent_files", [])
        
    def save_settings(self):
        """Save settings"""
        self.settings.setValue("window/size", self.window.size())
        self.settings.setValue("window/position", self.window.pos())
        self.settings.setValue("recent_files", self.recent_files)
        
    def closeEvent(self, event):
        """Save settings on close"""
        self.save_settings()
        event.accept()
```

## Event Filtering

### Event Filter

```python
from PySide6.QtCore import QEvent

class EventFilterWidget(QWidget):
    """Widget with event filtering"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Install event filter on child widget
        self.child = QLineEdit(self)
        self.child.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Filter events"""
        if obj == self.child:
            if event.type() == QEvent.KeyPress:
                # Handle key press
                if event.key() == Qt.Key_Return:
                    print("Return pressed in child")
                    return True  # Event handled
                    
        return super().eventFilter(obj, event)
```

## Multi-Threading Patterns

### QThreadPool with QRunnable

```python
from PySide6.QtCore import QRunnable, QThreadPool, Signal, QObject

class WorkerSignals(QObject):
    """Signals for worker"""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)

class Worker(QRunnable):
    """Worker for thread pool"""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    def run(self):
        """Execute the worker"""
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class Application:
    """Application using thread pool"""
    
    def __init__(self):
        self.threadpool = QThreadPool()
        
    def execute_task(self):
        """Execute task in thread pool"""
        worker = Worker(self.long_running_task)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        worker.signals.finished.connect(self.task_finished)
        
        self.threadpool.start(worker)
        
    def long_running_task(self):
        """Task to run in background"""
        # Do work
        return result
```

## Context Menus

### Custom Context Menu

```python
class ContextMenuWidget(QWidget):
    """Widget with context menu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        action1 = menu.addAction("Action 1")
        action2 = menu.addAction("Action 2")
        menu.addSeparator()
        
        submenu = menu.addMenu("Submenu")
        submenu.addAction("Sub Action 1")
        submenu.addAction("Sub Action 2")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == action1:
            self.handle_action1()
        elif action == action2:
            self.handle_action2()
```

## Internationalization

### Using Translations

```python
from PySide6.QtCore import QTranslator

app = QApplication(sys.argv)

# Load translation
translator = QTranslator()
if translator.load("app_ko.qm"):
    app.installTranslator(translator)

# In code, mark strings for translation
button = QPushButton(self.tr("Click Me"))
label = QLabel(self.tr("Welcome"))
```

### Creating Translation Files

```bash
# Extract strings
pylupdate6 *.py -ts translations/app_ko.ts

# Edit .ts file with Qt Linguist

# Compile translation
lrelease translations/app_ko.ts
```
