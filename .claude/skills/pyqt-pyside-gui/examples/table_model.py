"""
Custom Table Model Example

Demonstrates Model/View architecture:
- Custom QAbstractTableModel implementation
- Data editing and updates
- Row/column operations
- Custom delegates (optional)
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableView, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QColor


class CustomTableModel(QAbstractTableModel):
    """Custom table model for displaying and editing data"""
    
    dataChanged = Signal()
    
    def __init__(self, data=None, headers=None):
        super().__init__()
        self._data = data or []
        self._headers = headers or []
        
    def rowCount(self, parent=QModelIndex()):
        """Return number of rows"""
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()):
        """Return number of columns"""
        if self._data:
            return len(self._data[0])
        return len(self._headers)
        
    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role"""
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data[index.row()][index.column()]
            
        elif role == Qt.BackgroundRole:
            # Alternate row colors
            if index.row() % 2 == 0:
                return QColor(240, 240, 240)
            return QColor(255, 255, 255)
            
        elif role == Qt.TextAlignmentRole:
            # Center align numeric columns
            value = self._data[index.row()][index.column()]
            if isinstance(value, (int, float)):
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
        
    def setData(self, index, value, role=Qt.EditRole):
        """Set data at given index"""
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        try:
            # Try to maintain data type
            original_value = self._data[index.row()][index.column()]
            if isinstance(original_value, int):
                value = int(value)
            elif isinstance(original_value, float):
                value = float(value)
            else:
                value = str(value)
                
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
            
        except (ValueError, TypeError):
            return False
            
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
                return f"Column {section + 1}"
            else:
                return str(section + 1)
        return None
        
    def flags(self, index):
        """Return item flags"""
        if not index.isValid():
            return Qt.ItemIsEnabled
            
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        
    def insertRows(self, row, count, parent=QModelIndex()):
        """Insert rows"""
        self.beginInsertRows(parent, row, row + count - 1)
        
        for _ in range(count):
            # Create empty row with same column count
            new_row = [""] * self.columnCount()
            self._data.insert(row, new_row)
            
        self.endInsertRows()
        return True
        
    def removeRows(self, row, count, parent=QModelIndex()):
        """Remove rows"""
        self.beginRemoveRows(parent, row, row + count - 1)
        
        for _ in range(count):
            if row < len(self._data):
                del self._data[row]
                
        self.endRemoveRows()
        return True
        
    def get_data(self):
        """Get all data"""
        return self._data
        
    def set_data(self, data):
        """Set all data"""
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class MainWindow(QMainWindow):
    """Main window with custom table model"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Custom Table Model Example")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create table view
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)
        
        # Create model
        headers = ["ID", "Name", "Age", "Department", "Salary"]
        self.model = CustomTableModel(headers=headers)
        self.table_view.setModel(self.model)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_row)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.load_sample_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def load_sample_data(self):
        """Load sample data into model"""
        sample_data = [
            [1, "Alice Johnson", 28, "Engineering", 85000],
            [2, "Bob Smith", 35, "Marketing", 72000],
            [3, "Carol White", 42, "Sales", 95000],
            [4, "David Brown", 31, "Engineering", 88000],
            [5, "Eve Davis", 29, "HR", 68000],
            [6, "Frank Miller", 38, "Finance", 92000],
            [7, "Grace Wilson", 33, "Engineering", 90000],
            [8, "Henry Moore", 45, "Management", 115000],
        ]
        self.model.set_data(sample_data)
        
    def add_row(self):
        """Add new row at the end"""
        row_count = self.model.rowCount()
        self.model.insertRows(row_count, 1)
        
        # Set default values
        new_id = row_count + 1
        self.model.setData(self.model.index(row_count, 0), new_id)
        self.model.setData(self.model.index(row_count, 1), "New Employee")
        self.model.setData(self.model.index(row_count, 2), 25)
        self.model.setData(self.model.index(row_count, 3), "Department")
        self.model.setData(self.model.index(row_count, 4), 50000)
        
    def remove_selected(self):
        """Remove selected rows"""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.information(self, "Info", "No rows selected")
            return
            
        # Get selected rows (unique)
        rows = set(index.row() for index in selection.selectedIndexes())
        
        # Remove rows (from bottom to top to maintain indices)
        for row in sorted(rows, reverse=True):
            self.model.removeRows(row, 1)
            
    def clear_all(self):
        """Clear all data"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to clear all data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.model.set_data([])


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
