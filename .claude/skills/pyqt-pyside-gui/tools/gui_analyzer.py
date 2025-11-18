"""
GUI Code Analyzer - Static Analysis Tool for PySide6/PyQt6 UI Files

Analyzes .py files containing PySide6/PyQt6 UI code and generates:
- Widget tree structure
- Property analysis for each widget
- Layout analysis
- Issue detection (overlapping, hidden widgets, size issues)
- Best practices validation
- Comprehensive HTML report

Usage:
    python gui_analyzer.py <path_to_ui_file.py>
    python gui_analyzer.py views/main_window.py

Features:
- 🌳 Automatic widget tree generation
- 🔍 Property extraction (geometry, visibility, styling)
- ⚠️ Issue detection (overlapping, hidden, size problems)
- 📊 Layout analysis
- 📋 HTML report generation
- ✅ skill.md best practices validation
"""

import ast
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from itertools import combinations


@dataclass
class WidgetInfo:
    """Information about a widget."""
    name: str
    var_name: str
    widget_type: str
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    properties: Dict[str, any] = field(default_factory=dict)
    geometry: Optional[Tuple[int, int, int, int]] = None
    stylesheet: Optional[str] = None
    visible: bool = True
    enabled: bool = True
    layout_type: Optional[str] = None
    issues: List[str] = field(default_factory=list)
    line_number: int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    file_path: str
    widgets: Dict[str, WidgetInfo]
    widget_tree: Dict[str, List[str]]
    issues: List[Dict[str, any]]
    statistics: Dict[str, any]
    best_practices: Dict[str, bool]
    alignment_analysis: Dict[str, any] = field(default_factory=dict)
    layout_suggestions: List[Dict[str, any]] = field(default_factory=list)
    z_order_analysis: List[Dict[str, any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class GUICodeAnalyzer:
    """Analyzes PySide6/PyQt6 UI code files."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.tree = None
        self.widgets: Dict[str, WidgetInfo] = {}
        self.current_class = None
        self.issues: List[Dict[str, any]] = []

        # Qt widget types to detect
        self.qt_widgets = {
            'QMainWindow', 'QWidget', 'QDialog', 'QLabel', 'QPushButton',
            'QLineEdit', 'QTextEdit', 'QComboBox', 'QCheckBox', 'QRadioButton',
            'QSpinBox', 'QDoubleSpinBox', 'QSlider', 'QProgressBar',
            'QListWidget', 'QTreeWidget', 'QTableWidget', 'QTabWidget',
            'QGroupBox', 'QFrame', 'QScrollArea', 'QSplitter',
            'QMenuBar', 'QToolBar', 'QStatusBar', 'QDockWidget',
            'QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout',
            'ThemedCard', 'ThemedLabel', 'ThemedButton', 'InfoCard',
            'StatusIndicator', 'StatBadge', 'LotDisplayCard', 'StatsCard'
        }

        # Layout types
        self.layout_types = {
            'QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout',
            'QStackedLayout'
        }

    def analyze(self) -> AnalysisResult:
        """Perform complete analysis."""
        print(f"🔍 Analyzing: {self.file_path}")

        # Load file
        self._load_file()

        # Parse AST
        self._parse_ast()

        # Extract widgets
        self._extract_widgets()

        # Build widget tree
        tree = self._build_widget_tree()

        # Detect issues
        self._detect_issues()

        # Validate best practices
        best_practices = self._validate_best_practices()

        # Generate statistics
        stats = self._generate_statistics()

        # NEW: Advanced layout analysis
        alignment_analysis = self._analyze_alignment()
        layout_suggestions = self._generate_layout_suggestions()
        z_order_analysis = self._analyze_z_order()

        result = AnalysisResult(
            file_path=str(self.file_path),
            widgets=self.widgets,
            widget_tree=tree,
            issues=self.issues,
            statistics=stats,
            best_practices=best_practices,
            alignment_analysis=alignment_analysis,
            layout_suggestions=layout_suggestions,
            z_order_analysis=z_order_analysis
        )

        print(f"✅ Analysis complete: {len(self.widgets)} widgets, {len(self.issues)} issues")
        return result

    def _load_file(self):
        """Load Python file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def _parse_ast(self):
        """Parse file into AST."""
        try:
            self.tree = ast.parse(self.content)
        except SyntaxError as e:
            raise SyntaxError(f"Failed to parse {self.file_path}: {e}")

    def _extract_widgets(self):
        """Extract widget information from AST."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.current_class = node.name
                self._analyze_class(node)

    def _analyze_class(self, class_node: ast.ClassDef):
        """Analyze a class definition."""
        # Check if it's a Qt widget class
        is_qt_class = any(
            base.id in self.qt_widgets if isinstance(base, ast.Name) else False
            for base in class_node.bases
        )

        if not is_qt_class:
            return

        # Analyze methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                self._analyze_method(node)

    def _analyze_method(self, method_node: ast.FunctionDef):
        """Analyze a method for widget creation."""
        for node in ast.walk(method_node):
            # Detect widget assignment: self.widget = QWidget()
            if isinstance(node, ast.Assign):
                self._analyze_assignment(node)

            # Detect method calls: widget.setGeometry(...)
            elif isinstance(node, ast.Call):
                self._analyze_method_call(node)

    def _analyze_assignment(self, assign_node: ast.Assign):
        """Analyze assignment for widget creation."""
        if not isinstance(assign_node.value, ast.Call):
            return

        # Get function name
        func = assign_node.value.func
        if isinstance(func, ast.Name):
            widget_type = func.id
        elif isinstance(func, ast.Attribute):
            widget_type = func.attr
        else:
            return

        if widget_type not in self.qt_widgets:
            return

        # Get variable name
        for target in assign_node.targets:
            if isinstance(target, ast.Attribute):
                var_name = target.attr

                # Create widget info
                widget = WidgetInfo(
                    name=var_name,
                    var_name=f"self.{var_name}",
                    widget_type=widget_type,
                    line_number=assign_node.lineno
                )

                # Extract parent from constructor args
                for keyword in assign_node.value.keywords:
                    if keyword.arg == 'parent' and isinstance(keyword.value, ast.Attribute):
                        widget.parent = keyword.value.attr

                self.widgets[var_name] = widget

    def _analyze_method_call(self, call_node: ast.Call):
        """Analyze method calls for property setting."""
        if not isinstance(call_node.func, ast.Attribute):
            return

        method_name = call_node.func.attr

        # Get widget name
        if isinstance(call_node.func.value, ast.Attribute):
            widget_name = call_node.func.value.attr
        else:
            return

        if widget_name not in self.widgets:
            return

        widget = self.widgets[widget_name]

        # Extract property based on method name
        if method_name == 'setGeometry' and len(call_node.args) >= 4:
            try:
                x = self._get_constant_value(call_node.args[0])
                y = self._get_constant_value(call_node.args[1])
                w = self._get_constant_value(call_node.args[2])
                h = self._get_constant_value(call_node.args[3])
                widget.geometry = (x, y, w, h)
            except:
                pass

        elif method_name == 'setMinimumSize' and len(call_node.args) >= 2:
            try:
                w = self._get_constant_value(call_node.args[0])
                h = self._get_constant_value(call_node.args[1])
                widget.properties['min_size'] = (w, h)
            except:
                pass

        elif method_name == 'setMaximumSize' and len(call_node.args) >= 2:
            try:
                w = self._get_constant_value(call_node.args[0])
                h = self._get_constant_value(call_node.args[1])
                widget.properties['max_size'] = (w, h)
            except:
                pass

        elif method_name == 'setStyleSheet' and len(call_node.args) >= 1:
            try:
                stylesheet = self._get_constant_value(call_node.args[0])
                widget.stylesheet = stylesheet
            except:
                pass

        elif method_name == 'setVisible' and len(call_node.args) >= 1:
            try:
                visible = self._get_constant_value(call_node.args[0])
                widget.visible = visible
            except:
                pass

        elif method_name == 'setEnabled' and len(call_node.args) >= 1:
            try:
                enabled = self._get_constant_value(call_node.args[0])
                widget.enabled = enabled
            except:
                pass

        elif method_name == 'setLayout' and len(call_node.args) >= 1:
            # Detect layout assignment
            if isinstance(call_node.args[0], ast.Name):
                layout_var = call_node.args[0].id
                # Try to find layout type from previous assignments
                widget.layout_type = "Layout (detected)"

        elif method_name == 'addWidget' and len(call_node.args) >= 1:
            # Detect parent-child relationship through layout.addWidget
            if isinstance(call_node.args[0], ast.Attribute):
                child_name = call_node.args[0].attr
                if child_name in self.widgets:
                    self.widgets[child_name].parent = widget_name
                    widget.children.append(child_name)

    def _get_constant_value(self, node):
        """Extract constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.NameConstant):
            return node.value
        else:
            raise ValueError("Not a constant")

    def _build_widget_tree(self) -> Dict[str, List[str]]:
        """Build widget tree structure."""
        tree = {}

        for name, widget in self.widgets.items():
            parent = widget.parent or "ROOT"
            if parent not in tree:
                tree[parent] = []
            tree[parent].append(name)

        return tree

    def _detect_issues(self):
        """Detect potential issues in UI code."""
        self._check_size_issues()
        self._check_visibility_issues()
        self._check_overlapping_widgets()
        self._check_layout_issues()
        self._check_naming_issues()

    def _check_size_issues(self):
        """Check for size-related issues."""
        for name, widget in self.widgets.items():
            # Check for very small widgets
            if widget.geometry:
                x, y, w, h = widget.geometry
                if w < 10 or h < 10:
                    self.issues.append({
                        'severity': 'warning',
                        'category': 'size',
                        'widget': name,
                        'message': f"Widget is very small ({w}x{h}px), may be invisible",
                        'line': widget.line_number
                    })
                    widget.issues.append("Very small size")

            # Check min/max size conflicts
            if 'min_size' in widget.properties and 'max_size' in widget.properties:
                min_w, min_h = widget.properties['min_size']
                max_w, max_h = widget.properties['max_size']
                if min_w > max_w or min_h > max_h:
                    self.issues.append({
                        'severity': 'error',
                        'category': 'size',
                        'widget': name,
                        'message': f"Min size ({min_w}x{min_h}) exceeds max size ({max_w}x{max_h})",
                        'line': widget.line_number
                    })
                    widget.issues.append("Min/Max size conflict")

    def _check_visibility_issues(self):
        """Check for visibility issues."""
        for name, widget in self.widgets.items():
            if not widget.visible:
                self.issues.append({
                    'severity': 'info',
                    'category': 'visibility',
                    'widget': name,
                    'message': "Widget is explicitly hidden",
                    'line': widget.line_number
                })
                widget.issues.append("Hidden by setVisible(False)")

    def _check_overlapping_widgets(self):
        """Check for overlapping widgets."""
        widgets_with_geometry = [
            (name, w) for name, w in self.widgets.items()
            if w.geometry is not None
        ]

        for i, (name1, w1) in enumerate(widgets_with_geometry):
            x1, y1, width1, height1 = w1.geometry

            for name2, w2 in widgets_with_geometry[i+1:]:
                x2, y2, width2, height2 = w2.geometry

                # Check if rectangles overlap
                if self._rectangles_overlap(
                    (x1, y1, width1, height1),
                    (x2, y2, width2, height2)
                ):
                    self.issues.append({
                        'severity': 'warning',
                        'category': 'overlap',
                        'widget': f"{name1} & {name2}",
                        'message': f"Widgets may overlap: {name1} and {name2}",
                        'line': w1.line_number
                    })
                    w1.issues.append(f"May overlap with {name2}")
                    w2.issues.append(f"May overlap with {name1}")

    def _rectangles_overlap(self, rect1, rect2) -> bool:
        """Check if two rectangles overlap."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2

        return not (x1 + w1 < x2 or x2 + w2 < x1 or
                   y1 + h1 < y2 or y2 + h2 < y1)

    def _check_layout_issues(self):
        """Check for layout-related issues."""
        # Check for widgets without parent or layout
        for name, widget in self.widgets.items():
            if widget.parent is None and widget.widget_type not in ['QMainWindow', 'QDialog']:
                self.issues.append({
                    'severity': 'warning',
                    'category': 'layout',
                    'widget': name,
                    'message': "Widget has no parent (may cause memory leak)",
                    'line': widget.line_number
                })
                widget.issues.append("No parent widget")

    def _check_naming_issues(self):
        """Check for naming convention issues."""
        for name, widget in self.widgets.items():
            # Check if name is meaningful
            if name.startswith('widget') or name.startswith('var'):
                self.issues.append({
                    'severity': 'info',
                    'category': 'naming',
                    'widget': name,
                    'message': f"Consider using a more descriptive name than '{name}'",
                    'line': widget.line_number
                })
                widget.issues.append("Generic name")

    def _validate_best_practices(self) -> Dict[str, bool]:
        """Validate skill.md best practices."""
        checks = {}

        # Check for theme manager usage
        checks['uses_theme_manager'] = 'get_theme()' in self.content

        # Check for themed components
        themed_components = ['ThemedCard', 'ThemedLabel', 'ThemedButton']
        checks['uses_themed_components'] = any(comp in self.content for comp in themed_components)

        # Check for hardcoded colors
        color_pattern = r'#[0-9A-Fa-f]{6}'
        hardcoded_colors = re.findall(color_pattern, self.content)
        checks['no_hardcoded_colors'] = len(hardcoded_colors) == 0
        checks['hardcoded_colors_found'] = hardcoded_colors if hardcoded_colors else []

        # Check for object names
        checks['uses_object_names'] = 'setObjectName' in self.content

        # Check for docstrings
        checks['has_docstrings'] = '"""' in self.content or "'''" in self.content

        # ===== Architecture Patterns =====
        # Check for proper signal/slot usage
        checks['uses_signals'] = 'Signal(' in self.content or '@Slot' in self.content or '.connect(' in self.content

        # Check for threading (responsive UI)
        checks['uses_threading'] = 'QThread' in self.content or 'Worker(' in self.content

        # Check for MVVM/MVC pattern
        checks['uses_mvvm_mvc'] = 'ViewModel' in self.content or 'viewmodel' in self.content.lower() or 'controller' in self.content.lower()

        # ===== Layout Management =====
        # Check for proper layout usage
        layout_classes = ['QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout', 'QStackedLayout']
        checks['uses_layouts'] = any(layout in self.content for layout in layout_classes)

        # Check for manual positioning (bad practice)
        checks['avoids_manual_positioning'] = 'setGeometry' not in self.content

        # Check for spacers/stretches
        checks['uses_spacers'] = 'addStretch' in self.content or 'QSpacerItem' in self.content

        # ===== Resource Management =====
        # Check for cleanup pattern
        checks['has_cleanup'] = 'closeEvent' in self.content

        # Check for proper parent-child relationships
        checks['sets_parent'] = 'parent=' in self.content or ', self)' in self.content

        # ===== PySide6 vs PyQt6 =====
        # Check framework choice (PySide6 preferred)
        has_pyside = 'from PySide6' in self.content or 'import PySide6' in self.content
        has_pyqt = 'from PyQt6' in self.content or 'import PyQt6' in self.content
        checks['uses_pyside6'] = has_pyside and not has_pyqt

        # ===== Signal/Slot Best Practices =====
        # Check for lambda usage
        checks['uses_lambda_slots'] = 'lambda:' in self.content or 'lambda ' in self.content

        # Check for functools.partial
        checks['uses_partial'] = 'from functools import partial' in self.content or 'partial(' in self.content

        # ===== Common Pitfalls =====
        # Check for blocking operations (bad)
        blocking_patterns = ['time.sleep', 'requests.get', 'urllib.request']
        checks['avoids_blocking_ui'] = not any(pattern in self.content for pattern in blocking_patterns)

        # Check for Qt Resource System usage
        checks['uses_qt_resources'] = ':/' in self.content and 'QIcon' in self.content

        return checks

    def _generate_statistics(self) -> Dict[str, any]:
        """Generate statistics."""
        widget_types = {}
        for widget in self.widgets.values():
            widget_types[widget.widget_type] = widget_types.get(widget.widget_type, 0) + 1

        return {
            'total_widgets': len(self.widgets),
            'widget_types': widget_types,
            'total_issues': len(self.issues),
            'issues_by_severity': {
                'error': len([i for i in self.issues if i['severity'] == 'error']),
                'warning': len([i for i in self.issues if i['severity'] == 'warning']),
                'info': len([i for i in self.issues if i['severity'] == 'info'])
            },
            'lines_of_code': len(self.content.split('\n'))
        }

    def _analyze_alignment(self) -> Dict[str, any]:
        """Analyze X/Y axis alignment and consistent spacing."""
        widgets_with_geometry = [
            w for w in self.widgets.values() if w.geometry
        ]

        if not widgets_with_geometry:
            return {'x_groups': {}, 'y_groups': {}, 'spacing_analysis': {}, 'suggestions': []}

        # Group widgets by X coordinate
        x_groups = defaultdict(list)
        for widget in widgets_with_geometry:
            x = widget.geometry[0]
            x_groups[x].append(widget.name)

        # Group widgets by Y coordinate
        y_groups = defaultdict(list)
        for widget in widgets_with_geometry:
            y = widget.geometry[1]
            y_groups[y].append(widget.name)

        # Analyze horizontal spacing between widgets
        horizontal_spacings = []
        sorted_widgets = sorted(widgets_with_geometry, key=lambda w: (w.geometry[1], w.geometry[0]))

        for i in range(len(sorted_widgets) - 1):
            w1, w2 = sorted_widgets[i], sorted_widgets[i+1]
            if w1.geometry and w2.geometry:
                # Same row (similar Y coordinate)
                if abs(w1.geometry[1] - w2.geometry[1]) < 10:
                    spacing = w2.geometry[0] - (w1.geometry[0] + w1.geometry[2])
                    if spacing > 0:
                        horizontal_spacings.append(spacing)

        # Analyze vertical spacing
        vertical_spacings = []
        sorted_by_y = sorted(widgets_with_geometry, key=lambda w: w.geometry[1])

        for i in range(len(sorted_by_y) - 1):
            w1, w2 = sorted_by_y[i], sorted_by_y[i+1]
            spacing = w2.geometry[1] - (w1.geometry[1] + w1.geometry[3])
            if spacing > 0:
                vertical_spacings.append(spacing)

        # Check for consistent spacing
        spacing_analysis = {}
        suggestions = []

        if horizontal_spacings:
            unique_spacings = set(horizontal_spacings)
            spacing_analysis['horizontal'] = {
                'spacings': list(unique_spacings),
                'consistent': len(unique_spacings) == 1
            }
            if len(unique_spacings) > 1:
                most_common = max(set(horizontal_spacings), key=horizontal_spacings.count)
                suggestions.append({
                    'type': 'spacing',
                    'message': f'Inconsistent horizontal spacing detected: {unique_spacings}',
                    'recommendation': f'Consider using consistent spacing of {most_common}px'
                })

        if vertical_spacings:
            unique_spacings = set(vertical_spacings)
            spacing_analysis['vertical'] = {
                'spacings': list(unique_spacings),
                'consistent': len(unique_spacings) == 1
            }
            if len(unique_spacings) > 1:
                most_common = max(set(vertical_spacings), key=vertical_spacings.count)
                suggestions.append({
                    'type': 'spacing',
                    'message': f'Inconsistent vertical spacing detected: {unique_spacings}',
                    'recommendation': f'Consider using consistent spacing of {most_common}px'
                })

        # Check for alignment opportunities
        x_aligned = {x: widgets for x, widgets in x_groups.items() if len(widgets) >= 3}
        y_aligned = {y: widgets for y, widgets in y_groups.items() if len(widgets) >= 3}

        if x_aligned:
            for x, widgets in x_aligned.items():
                suggestions.append({
                    'type': 'alignment',
                    'message': f'{len(widgets)} widgets aligned at x={x}',
                    'widgets': widgets,
                    'recommendation': 'Consider using QVBoxLayout for vertical stacking'
                })

        if y_aligned:
            for y, widgets in y_aligned.items():
                suggestions.append({
                    'type': 'alignment',
                    'message': f'{len(widgets)} widgets aligned at y={y}',
                    'widgets': widgets,
                    'recommendation': 'Consider using QHBoxLayout for horizontal arrangement'
                })

        return {
            'x_groups': {k: v for k, v in x_groups.items() if len(v) > 1},
            'y_groups': {k: v for k, v in y_groups.items() if len(v) > 1},
            'spacing_analysis': spacing_analysis,
            'suggestions': suggestions
        }

    def _generate_layout_suggestions(self) -> List[Dict[str, any]]:
        """Generate layout optimization suggestions."""
        suggestions = []
        widgets_with_geometry = [
            w for w in self.widgets.values() if w.geometry
        ]

        if not widgets_with_geometry:
            return suggestions

        # Detect manual positioning (setGeometry usage)
        manual_positioned = [w for w in widgets_with_geometry if w.geometry]

        if len(manual_positioned) >= 3:
            # Check if widgets form a grid pattern
            grid_detected = self._detect_grid_pattern(widgets_with_geometry)
            if grid_detected:
                suggestions.append({
                    'severity': 'info',
                    'category': 'layout',
                    'message': f'Grid pattern detected: {grid_detected["rows"]}x{grid_detected["cols"]}',
                    'widgets': [w.name for w in widgets_with_geometry],
                    'recommendation': 'Consider using QGridLayout instead of manual positioning',
                    'benefit': 'Automatic responsive layout and easier maintenance'
                })

            # Check for vertical stacking
            sorted_by_y = sorted(widgets_with_geometry, key=lambda w: w.geometry[1])
            if self._is_vertical_stack(sorted_by_y):
                suggestions.append({
                    'severity': 'info',
                    'category': 'layout',
                    'message': f'{len(sorted_by_y)} widgets are vertically stacked',
                    'widgets': [w.name for w in sorted_by_y],
                    'recommendation': 'Use QVBoxLayout for vertical stacking',
                    'benefit': 'Automatic spacing and responsive behavior'
                })

            # Check for horizontal arrangement
            sorted_by_x = sorted(widgets_with_geometry, key=lambda w: w.geometry[0])
            if self._is_horizontal_row(sorted_by_x):
                suggestions.append({
                    'severity': 'info',
                    'category': 'layout',
                    'message': f'{len(sorted_by_x)} widgets are horizontally arranged',
                    'widgets': [w.name for w in sorted_by_x],
                    'recommendation': 'Use QHBoxLayout for horizontal arrangement',
                    'benefit': 'Automatic spacing and responsive behavior'
                })

        # Check for widgets using layouts properly
        layout_users = [w for w in self.widgets.values() if w.layout_type]
        non_layout_users = [w for w in self.widgets.values() if not w.layout_type and w.geometry]

        if layout_users and non_layout_users:
            suggestions.append({
                'severity': 'warning',
                'category': 'layout',
                'message': f'Mixed layout approach: {len(layout_users)} widgets use layouts, {len(non_layout_users)} use manual positioning',
                'recommendation': 'Use consistent layout approach throughout the UI',
                'benefit': 'Better maintainability and responsive behavior'
            })

        return suggestions

    def _detect_grid_pattern(self, widgets: List[WidgetInfo]) -> Optional[Dict[str, int]]:
        """Detect if widgets form a grid pattern."""
        if len(widgets) < 4:
            return None

        # Get unique X and Y coordinates
        x_coords = sorted(set(w.geometry[0] for w in widgets))
        y_coords = sorted(set(w.geometry[1] for w in widgets))

        # Check if we have at least 2x2 grid
        if len(x_coords) >= 2 and len(y_coords) >= 2:
            # Count widgets at each grid position
            grid_count = 0
            for x in x_coords:
                for y in y_coords:
                    if any(w.geometry[0] == x and w.geometry[1] == y for w in widgets):
                        grid_count += 1

            # If more than 70% of grid positions are filled, it's a grid
            total_positions = len(x_coords) * len(y_coords)
            if grid_count / total_positions > 0.7:
                return {'rows': len(y_coords), 'cols': len(x_coords)}

        return None

    def _is_vertical_stack(self, widgets: List[WidgetInfo]) -> bool:
        """Check if widgets are vertically stacked."""
        if len(widgets) < 3:
            return False

        # Check if X coordinates are similar (within 20px tolerance)
        x_coords = [w.geometry[0] for w in widgets]
        x_variance = max(x_coords) - min(x_coords)

        return x_variance < 20

    def _is_horizontal_row(self, widgets: List[WidgetInfo]) -> bool:
        """Check if widgets are in a horizontal row."""
        if len(widgets) < 3:
            return False

        # Check if Y coordinates are similar (within 20px tolerance)
        y_coords = [w.geometry[1] for w in widgets]
        y_variance = max(y_coords) - min(y_coords)

        return y_variance < 20

    def _analyze_z_order(self) -> List[Dict[str, any]]:
        """Analyze Z-order and widget occlusion."""
        z_order_issues = []
        widgets_with_geometry = [
            w for w in self.widgets.values() if w.geometry
        ]

        if not widgets_with_geometry:
            return z_order_issues

        # Check all pairs for overlapping
        for w1, w2 in combinations(widgets_with_geometry, 2):
            if self._rectangles_overlap(w1.geometry, w2.geometry):
                # Determine which widget is on top (later in code = on top)
                top_widget = w2 if w2.line_number > w1.line_number else w1
                bottom_widget = w1 if w2.line_number > w1.line_number else w2

                # Calculate overlap area
                overlap_area = self._calculate_overlap_area(w1.geometry, w2.geometry)
                w1_area = w1.geometry[2] * w1.geometry[3]
                w2_area = w2.geometry[2] * w2.geometry[3]

                w1_covered_pct = (overlap_area / w1_area * 100) if w1_area > 0 else 0
                w2_covered_pct = (overlap_area / w2_area * 100) if w2_area > 0 else 0

                z_order_issues.append({
                    'top_widget': top_widget.name,
                    'bottom_widget': bottom_widget.name,
                    'overlap_area': overlap_area,
                    'bottom_covered_percent': w1_covered_pct if bottom_widget == w1 else w2_covered_pct,
                    'message': f'{top_widget.name} (line {top_widget.line_number}) will cover {bottom_widget.name} (line {bottom_widget.line_number})',
                    'severity': 'warning' if max(w1_covered_pct, w2_covered_pct) > 50 else 'info',
                    'recommendation': 'Review z-order or adjust positions to avoid occlusion' if max(w1_covered_pct, w2_covered_pct) > 50 else 'Minor overlap detected'
                })

        return z_order_issues

    def _rectangles_overlap(self, rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int]) -> bool:
        """Check if two rectangles overlap."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2

        return not (x1 + w1 < x2 or x2 + w2 < x1 or
                   y1 + h1 < y2 or y2 + h2 < y1)

    def _calculate_overlap_area(self, rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int]) -> int:
        """Calculate the overlapping area between two rectangles."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2

        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return 0

        return (x_right - x_left) * (y_bottom - y_top)


def print_detailed_report(result: AnalysisResult):
    """Print detailed analysis report to console for AI consumption."""
    print(f"\n{'='*80}")
    print(f"📊 GUI CODE ANALYSIS REPORT")
    print(f"{'='*80}")
    print(f"File: {result.file_path}")
    print(f"Timestamp: {result.timestamp}")
    print(f"{'='*80}\n")

    # Statistics
    print("📈 STATISTICS")
    print(f"{'─'*80}")
    print(f"Total Widgets: {result.statistics['total_widgets']}")
    print(f"Total Issues: {result.statistics['total_issues']}")
    print(f"  • Errors: {result.statistics['issues_by_severity']['error']}")
    print(f"  • Warnings: {result.statistics['issues_by_severity']['warning']}")
    print(f"  • Info: {result.statistics['issues_by_severity']['info']}")
    print(f"Lines of Code: {result.statistics['lines_of_code']}\n")

    # Widget Tree
    print("🌳 WIDGET TREE")
    print(f"{'─'*80}")
    _print_tree(result.widget_tree, result.widgets, "ROOT", 0)
    print()

    # Widget Details
    print("📋 WIDGET DETAILS")
    print(f"{'─'*80}")
    for name, widget in result.widgets.items():
        print(f"\n[{widget.widget_type}] {name}")
        print(f"  Line: {widget.line_number}")
        if widget.parent:
            print(f"  Parent: {widget.parent}")
        if widget.children:
            print(f"  Children: {', '.join(widget.children)}")
        if widget.geometry:
            x, y, w, h = widget.geometry
            print(f"  Geometry: x={x}, y={y}, width={w}, height={h}")
        if 'min_size' in widget.properties:
            print(f"  Min Size: {widget.properties['min_size']}")
        if 'max_size' in widget.properties:
            print(f"  Max Size: {widget.properties['max_size']}")
        print(f"  Visible: {widget.visible}")
        print(f"  Enabled: {widget.enabled}")
        if widget.stylesheet:
            print(f"  Stylesheet: {widget.stylesheet[:100]}...")
        if widget.issues:
            print(f"  ⚠️  Issues: {', '.join(widget.issues)}")

    # Issues
    if result.issues:
        print(f"\n⚠️  DETECTED ISSUES ({len(result.issues)})")
        print(f"{'─'*80}")

        errors = [i for i in result.issues if i['severity'] == 'error']
        warnings = [i for i in result.issues if i['severity'] == 'warning']
        infos = [i for i in result.issues if i['severity'] == 'info']

        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"\n  • [{issue['category'].upper()}] {issue['widget']}")
                print(f"    {issue['message']}")
                print(f"    Line {issue['line']}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"\n  • [{issue['category'].upper()}] {issue['widget']}")
                print(f"    {issue['message']}")
                print(f"    Line {issue['line']}")

        if infos:
            print(f"\nℹ️  INFO ({len(infos)}):")
            for issue in infos:
                print(f"\n  • [{issue['category'].upper()}] {issue['widget']}")
                print(f"    {issue['message']}")
                print(f"    Line {issue['line']}")
    else:
        print(f"\n✅ NO ISSUES DETECTED")

    # Best Practices & Design Principles
    print(f"\n✅ BEST PRACTICES & DESIGN PRINCIPLES (skill.md)")
    print(f"{'─'*80}")

    print("\n📋 Theme System:")
    theme_checks = {
        'uses_theme_manager': 'Uses Theme Manager (get_theme())',
        'uses_themed_components': 'Uses Themed Components',
        'no_hardcoded_colors': 'No Hardcoded Colors'
    }
    for key, label in theme_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")
        if key == 'no_hardcoded_colors' and not result.best_practices.get(key, False):
            colors = result.best_practices.get('hardcoded_colors_found', [])
            if colors:
                print(f"      Found: {', '.join(colors[:5])}")

    print("\n📋 Code Quality:")
    quality_checks = {
        'uses_object_names': 'Uses Object Names (setObjectName)',
        'has_docstrings': 'Has Docstrings'
    }
    for key, label in quality_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")

    print("\n📋 Architecture Patterns:")
    arch_checks = {
        'uses_signals': 'Uses Signal/Slot Pattern',
        'uses_mvvm_mvc': 'Uses MVVM/MVC Pattern',
        'uses_threading': 'Uses Threading (Responsive UI)'
    }
    for key, label in arch_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")

    print("\n📋 Layout Management:")
    layout_checks = {
        'uses_layouts': 'Uses Layout Managers',
        'avoids_manual_positioning': 'Avoids Manual Positioning (setGeometry)',
        'uses_spacers': 'Uses Spacers/Stretches'
    }
    for key, label in layout_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")

    print("\n📋 Resource Management:")
    resource_checks = {
        'has_cleanup': 'Has Cleanup (closeEvent)',
        'sets_parent': 'Sets Widget Parents'
    }
    for key, label in resource_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")

    print("\n📋 Framework & Best Practices:")
    framework_checks = {
        'uses_pyside6': 'Uses PySide6 (Preferred)',
        'uses_lambda_slots': 'Uses Lambda for Slots',
        'uses_partial': 'Uses functools.partial',
        'avoids_blocking_ui': 'Avoids Blocking UI Thread'
    }
    for key, label in framework_checks.items():
        status = '✅' if result.best_practices.get(key, False) else '❌'
        print(f"  {status} {label}")

    # Widget Type Distribution
    print(f"\n📊 WIDGET TYPE DISTRIBUTION")
    print(f"{'─'*80}")
    for widget_type, count in sorted(result.statistics['widget_types'].items(),
                                     key=lambda x: x[1], reverse=True):
        bar = '█' * count
        print(f"{widget_type:30} {count:3} {bar}")

    # NEW: Alignment Analysis
    if result.alignment_analysis.get('suggestions'):
        print(f"\n📐 ALIGNMENT & SPACING ANALYSIS")
        print(f"{'─'*80}")

        spacing = result.alignment_analysis.get('spacing_analysis', {})
        if spacing:
            if 'horizontal' in spacing:
                h = spacing['horizontal']
                status = '✅' if h['consistent'] else '⚠️'
                print(f"\nHorizontal Spacing: {status}")
                if h['consistent']:
                    print(f"  Consistent spacing of {list(h['spacings'])[0]}px")
                else:
                    print(f"  Inconsistent: {h['spacings']}")

            if 'vertical' in spacing:
                v = spacing['vertical']
                status = '✅' if v['consistent'] else '⚠️'
                print(f"\nVertical Spacing: {status}")
                if v['consistent']:
                    print(f"  Consistent spacing of {list(v['spacings'])[0]}px")
                else:
                    print(f"  Inconsistent: {v['spacings']}")

        print(f"\nSuggestions:")
        for suggestion in result.alignment_analysis['suggestions']:
            print(f"  • {suggestion['message']}")
            print(f"    → {suggestion['recommendation']}")

    # NEW: Layout Optimization Suggestions
    if result.layout_suggestions:
        print(f"\n🏗️  LAYOUT OPTIMIZATION SUGGESTIONS")
        print(f"{'─'*80}")
        for suggestion in result.layout_suggestions:
            severity_icon = {'warning': '⚠️', 'info': 'ℹ️', 'error': '❌'}.get(suggestion['severity'], 'ℹ️')
            print(f"\n{severity_icon}  {suggestion['message']}")
            print(f"  Widgets: {', '.join(suggestion['widgets'][:5])}")
            if len(suggestion['widgets']) > 5:
                print(f"           ... and {len(suggestion['widgets']) - 5} more")
            print(f"  → {suggestion['recommendation']}")
            if 'benefit' in suggestion:
                print(f"  ✨ Benefit: {suggestion['benefit']}")

    # NEW: Z-Order Analysis
    if result.z_order_analysis:
        print(f"\n🔺 Z-ORDER & OCCLUSION ANALYSIS")
        print(f"{'─'*80}")
        print(f"Found {len(result.z_order_analysis)} overlapping widget pairs:\n")

        for z_issue in result.z_order_analysis[:5]:  # Show first 5
            severity_icon = '⚠️' if z_issue['severity'] == 'warning' else 'ℹ️'
            print(f"{severity_icon}  {z_issue['message']}")
            print(f"  Overlap area: {z_issue['overlap_area']}px² ({z_issue['bottom_covered_percent']:.1f}% of bottom widget)")
            print(f"  → {z_issue['recommendation']}\n")

        if len(result.z_order_analysis) > 5:
            print(f"... and {len(result.z_order_analysis) - 5} more overlapping pairs")

    # Comprehensive Improvement Summary
    total_suggestions = (
        len(result.alignment_analysis.get('suggestions', [])) +
        len(result.layout_suggestions) +
        len(result.z_order_analysis)
    )

    if total_suggestions > 0:
        print(f"\n💡 COMPREHENSIVE IMPROVEMENT SUMMARY")
        print(f"{'─'*80}")
        print(f"Total Improvement Opportunities: {total_suggestions}")
        print(f"  • Alignment & Spacing: {len(result.alignment_analysis.get('suggestions', []))}")
        print(f"  • Layout Optimization: {len(result.layout_suggestions)}")
        print(f"  • Z-Order Issues: {len(result.z_order_analysis)}")

    print(f"\n{'='*80}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")


def _print_tree(tree: Dict, widgets: Dict, node: str, level: int):
    """Print widget tree recursively."""
    indent = "  " * level
    widget = widgets.get(node)

    if widget:
        issues_marker = f" ⚠️ ({len(widget.issues)})" if widget.issues else ""
        print(f"{indent}├─ [{widget.widget_type}] {node}{issues_marker}")
    else:
        print(f"{indent}├─ {node}")

    if node in tree:
        for child in tree[node]:
            _print_tree(tree, widgets, child, level + 1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='GUI Code Analyzer - Static Analysis for PySide6/PyQt6')
    parser.add_argument('file', help='Path to Python UI file to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    try:
        # Analyze
        analyzer = GUICodeAnalyzer(args.file)
        result = analyzer.analyze()

        # Output format
        if args.json:
            # JSON output for programmatic use
            import json
            output = {
                'file_path': result.file_path,
                'timestamp': result.timestamp,
                'statistics': result.statistics,
                'widgets': {name: {
                    'type': w.widget_type,
                    'line': w.line_number,
                    'parent': w.parent,
                    'children': w.children,
                    'issues': w.issues
                } for name, w in result.widgets.items()},
                'issues': result.issues,
                'best_practices': result.best_practices
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Default: Detailed console output
            print_detailed_report(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()