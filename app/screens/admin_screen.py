"""
Admin Screen - Manage shared team data and app configuration
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QLineEdit,
    QStackedWidget, QFormLayout, QComboBox, QMessageBox,
    QFileDialog, QSplitter, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path

from ..data_service import data_service


class EditableListPanel(QFrame):
    """A panel for editing a simple list of strings (work types, campuses, etc.)"""
    
    data_changed = pyqtSignal()
    
    def __init__(self, title: str, data_path: str):
        super().__init__()
        
        self.title = title
        self.data_path = data_path  # e.g., "work_types", "campuses"
        
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header.addWidget(title_label)
        
        header.addStretch()
        layout.addLayout(header)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self._on_edit_item)
        layout.addWidget(self.list_widget, 1)
        
        # Add new item row
        add_row = QHBoxLayout()
        
        self.new_item_input = QLineEdit()
        self.new_item_input.setPlaceholderText(f"Add new {self.title.lower()[:-1]}...")
        self.new_item_input.returnPressed.connect(self._on_add_item)
        add_row.addWidget(self.new_item_input)
        
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(40)
        add_btn.clicked.connect(self._on_add_item)
        add_row.addWidget(add_btn)
        
        layout.addLayout(add_row)
        
        # Action buttons
        btn_row = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._on_edit_selected)
        btn_row.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._on_remove_item)
        btn_row.addWidget(remove_btn)
        
        import_btn = QPushButton("📥 Import...")
        import_btn.clicked.connect(self._on_import)
        btn_row.addWidget(import_btn)
        
        btn_row.addStretch()
        
        move_up_btn = QPushButton("↑")
        move_up_btn.setFixedWidth(40)
        move_up_btn.clicked.connect(self._on_move_up)
        btn_row.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓")
        move_down_btn.setFixedWidth(40)
        move_down_btn.clicked.connect(self._on_move_down)
        btn_row.addWidget(move_down_btn)
        
        layout.addLayout(btn_row)
        
        # Data location hint
        hint = QLabel(f"Data: team_data.json → {self.data_path}[]")
        hint.setStyleSheet("color: #6c757d; font-size: 10px;")
        layout.addWidget(hint)
    
    def refresh(self):
        """Refresh the list from data service"""
        self.list_widget.clear()
        
        if not data_service.team_data:
            return
        
        items = getattr(data_service.team_data, self.data_path, [])
        for item in items:
            self.list_widget.addItem(item)
    
    def _get_items(self) -> list:
        """Get all items from the list widget"""
        items = []
        for i in range(self.list_widget.count()):
            items.append(self.list_widget.item(i).text())
        return items
    
    def _save(self):
        """Save changes back to team_data"""
        if not data_service.team_data:
            return
        
        setattr(data_service.team_data, self.data_path, self._get_items())
        data_service.save_team_data(data_service.team_data)
        self.data_changed.emit()
    
    def _on_add_item(self):
        """Add a new item"""
        text = self.new_item_input.text().strip()
        if not text:
            return
        
        # Check for duplicates
        existing = self._get_items()
        if text in existing:
            QMessageBox.warning(self, "Duplicate", f"'{text}' already exists.")
            return
        
        self.list_widget.addItem(text)
        self.new_item_input.clear()
        self._save()
    
    def _on_edit_item(self, item: QListWidgetItem):
        """Edit an item on double-click"""
        old_text = item.text()
        new_text, ok = QInputDialog.getText(
            self, 
            f"Edit {self.title[:-1]}", 
            "Value:",
            QLineEdit.EchoMode.Normal,
            old_text
        )
        
        if ok and new_text.strip():
            item.setText(new_text.strip())
            self._save()
    
    def _on_edit_selected(self):
        """Edit the selected item"""
        item = self.list_widget.currentItem()
        if item:
            self._on_edit_item(item)
    
    def _on_remove_item(self):
        """Remove the selected item"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        
        item = self.list_widget.item(row)
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove '{item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.list_widget.takeItem(row)
            self._save()
    
    def _on_move_up(self):
        """Move selected item up"""
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)
            self._save()
    
    def _on_move_down(self):
        """Move selected item down"""
        row = self.list_widget.currentRow()
        if row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)
            self._save()
    
    def _on_import(self):
        """Import items from CSV or JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Import {self.title}",
            "",
            "All Supported (*.json *.csv);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import json
            import csv
            
            new_items = []
            
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both array of strings and array of objects
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            new_items.append(item.strip())
                        elif isinstance(item, dict):
                            # Try common field names
                            for key in ['name', 'value', 'label', 'title', self.data_path[:-1]]:
                                if key in item:
                                    new_items.append(str(item[key]).strip())
                                    break
            
            elif file_path.lower().endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8', newline='') as f:
                    # Try to detect if there's a header
                    sample = f.read(1024)
                    f.seek(0)
                    
                    # Simple approach: just read first column
                    reader = csv.reader(f)
                    for row in reader:
                        if row and row[0].strip():
                            new_items.append(row[0].strip())
            
            # Filter out duplicates and existing items
            existing = set(self._get_items())
            added = 0
            skipped = 0
            
            for item in new_items:
                if item and item not in existing:
                    self.list_widget.addItem(item)
                    existing.add(item)
                    added += 1
                else:
                    skipped += 1
            
            if added > 0:
                self._save()
            
            QMessageBox.information(
                self,
                "Import Complete",
                f"Added {added} new items.\nSkipped {skipped} duplicates."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import file:\n{str(e)}"
            )


class EmployeesPanel(QFrame):
    """Panel for editing employees (has id, name, role)"""
    
    data_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        title_label = QLabel("Employees")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self._on_edit_employee)
        layout.addWidget(self.list_widget, 1)
        
        # Add new employee form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(8, 8, 8, 8)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("OS username (e.g., dsmith)")
        form_layout.addRow("Username:", self.id_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display name")
        form_layout.addRow("Name:", self.name_input)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["LXO", "LPO", "SME"])
        self.role_combo.setEditable(True)
        form_layout.addRow("Role:", self.role_combo)
        
        add_btn = QPushButton("+ Add Employee")
        add_btn.clicked.connect(self._on_add_employee)
        form_layout.addRow(add_btn)
        
        layout.addWidget(form_frame)
        
        # Action buttons
        btn_row = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._on_edit_selected)
        btn_row.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._on_remove_employee)
        btn_row.addWidget(remove_btn)
        
        import_btn = QPushButton("📥 Import...")
        import_btn.clicked.connect(self._on_import)
        btn_row.addWidget(import_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Data location hint
        hint = QLabel("Data: team_data.json → employees[]")
        hint.setStyleSheet("color: #6c757d; font-size: 10px;")
        layout.addWidget(hint)
    
    def refresh(self):
        """Refresh the list from data service"""
        self.list_widget.clear()
        
        if not data_service.team_data:
            return
        
        for emp in data_service.team_data.employees:
            if isinstance(emp, dict):
                display = f"{emp.get('id', '')}  —  {emp.get('name', '')}  [{emp.get('role', '')}]"
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, emp)
                self.list_widget.addItem(item)
    
    def _save(self):
        """Save changes back to team_data"""
        if not data_service.team_data:
            return
        
        employees = []
        for i in range(self.list_widget.count()):
            emp_data = self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            employees.append(emp_data)
        
        data_service.team_data.employees = employees
        data_service.save_team_data(data_service.team_data)
        self.data_changed.emit()
    
    def _on_add_employee(self):
        """Add a new employee"""
        emp_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        role = self.role_combo.currentText().strip()
        
        if not emp_id or not name:
            QMessageBox.warning(self, "Missing Info", "Username and Name are required.")
            return
        
        # Check for duplicate ID
        for i in range(self.list_widget.count()):
            existing = self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            if existing.get('id') == emp_id:
                QMessageBox.warning(self, "Duplicate", f"Username '{emp_id}' already exists.")
                return
        
        emp_data = {'id': emp_id, 'name': name, 'role': role}
        display = f"{emp_id}  —  {name}  [{role}]"
        item = QListWidgetItem(display)
        item.setData(Qt.ItemDataRole.UserRole, emp_data)
        self.list_widget.addItem(item)
        
        # Clear inputs
        self.id_input.clear()
        self.name_input.clear()
        self.role_combo.setCurrentIndex(0)
        
        self._save()
    
    def _on_edit_employee(self, item: QListWidgetItem):
        """Edit an employee"""
        emp_data = item.data(Qt.ItemDataRole.UserRole)
        
        # Simple dialog for editing
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Employee")
        dialog.setMinimumWidth(300)
        
        layout = QFormLayout(dialog)
        
        id_edit = QLineEdit(emp_data.get('id', ''))
        layout.addRow("Username:", id_edit)
        
        name_edit = QLineEdit(emp_data.get('name', ''))
        layout.addRow("Name:", name_edit)
        
        role_edit = QComboBox()
        role_edit.addItems(["LXO", "LPO", "SME"])
        role_edit.setEditable(True)
        role_edit.setCurrentText(emp_data.get('role', ''))
        layout.addRow("Role:", role_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_id = id_edit.text().strip()
            new_name = name_edit.text().strip()
            new_role = role_edit.currentText().strip()
            
            if new_id and new_name:
                new_data = {'id': new_id, 'name': new_name, 'role': new_role}
                display = f"{new_id}  —  {new_name}  [{new_role}]"
                item.setText(display)
                item.setData(Qt.ItemDataRole.UserRole, new_data)
                self._save()
    
    def _on_edit_selected(self):
        """Edit the selected employee"""
        item = self.list_widget.currentItem()
        if item:
            self._on_edit_employee(item)
    
    def _on_remove_employee(self):
        """Remove the selected employee"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        
        item = self.list_widget.item(row)
        emp_data = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove employee '{emp_data.get('name', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.list_widget.takeItem(row)
            self._save()
    
    def _on_import(self):
        """Import employees from CSV or JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Employees",
            "",
            "All Supported (*.json *.csv);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            import json
            import csv
            
            new_employees = []
            
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Expect array of objects with id, name, role
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'id' in item:
                            new_employees.append({
                                'id': str(item.get('id', '')).strip(),
                                'name': str(item.get('name', '')).strip(),
                                'role': str(item.get('role', 'SME')).strip()
                            })
            
            elif file_path.lower().endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Look for id/username, name, role columns
                        emp_id = row.get('id') or row.get('username') or row.get('ID') or ''
                        emp_name = row.get('name') or row.get('Name') or row.get('display_name') or ''
                        emp_role = row.get('role') or row.get('Role') or 'SME'
                        
                        if emp_id.strip():
                            new_employees.append({
                                'id': emp_id.strip(),
                                'name': emp_name.strip() or emp_id.strip(),
                                'role': emp_role.strip()
                            })
            
            # Get existing IDs
            existing_ids = set()
            for i in range(self.list_widget.count()):
                emp_data = self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                existing_ids.add(emp_data.get('id'))
            
            added = 0
            skipped = 0
            
            for emp in new_employees:
                if emp['id'] and emp['id'] not in existing_ids:
                    display = f"{emp['id']}  —  {emp['name']}  [{emp['role']}]"
                    item = QListWidgetItem(display)
                    item.setData(Qt.ItemDataRole.UserRole, emp)
                    self.list_widget.addItem(item)
                    existing_ids.add(emp['id'])
                    added += 1
                else:
                    skipped += 1
            
            if added > 0:
                self._save()
            
            QMessageBox.information(
                self,
                "Import Complete",
                f"Added {added} new employees.\nSkipped {skipped} duplicates."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import file:\n{str(e)}"
            )


class AdminScreen(QWidget):
    """Admin screen for managing team data and configuration"""
    
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content with sidebar
        content = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel stack (create BEFORE sidebar so panels exist when nav signal fires)
        self.panel_stack = QStackedWidget()
        self._create_panels()
        
        # Sidebar
        sidebar = self._create_sidebar()
        content.addWidget(sidebar)
        
        content.addWidget(self.panel_stack)
        
        # Set splitter sizes (sidebar narrower)
        content.setSizes([200, 600])
        
        layout.addWidget(content, 1)
        
        # Status bar
        status = self._create_status_bar()
        layout.addWidget(status)
    
    def _create_header(self):
        """Create the header with back button and data folder selector"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self._on_back)
        layout.addWidget(back_btn)
        
        # Title
        title = QLabel("Admin Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("Manage shared team data")
        subtitle.setStyleSheet("color: #6c757d;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Data folder selector
        folder_btn = QPushButton("📁 Data Folder...")
        folder_btn.clicked.connect(self._on_change_folder)
        layout.addWidget(folder_btn)
        
        self.folder_label = QLabel()
        self.folder_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        self._update_folder_label()
        layout.addWidget(self.folder_label)
        
        return header
    
    def _create_sidebar(self):
        """Create the sidebar with category navigation"""
        sidebar = QFrame()
        sidebar.setMaximumWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)
        
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px 16px;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #e9ecef;
                color: #212529;
            }
            QListWidget::item:hover {
                background-color: #f1f3f5;
            }
        """)
        
        # Add navigation items with categories
        categories = [
            ("— TEAM —", None),
            ("  Employees", "employees"),
            ("— WORK —", None),
            ("  Work Types", "work_types"),
            ("— PROJECT FIELDS —", None),
            ("  Campuses", "campuses"),
            ("  Offers", "offers"),
            ("  Sub-Offers", "sub_offers"),
            ("  Effort Types", "effort_types"),
            ("  Course Types", "course_types"),
            ("  Statuses", "project_statuses"),
            ("  Tags", "tags"),
        ]
        
        for label, key in categories:
            item = QListWidgetItem(label)
            if key is None:
                # Category header - not selectable
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setForeground(Qt.GlobalColor.gray)
            else:
                item.setData(Qt.ItemDataRole.UserRole, key)
            self.nav_list.addItem(item)
        
        self.nav_list.currentItemChanged.connect(self._on_nav_changed)
        
        # Select first selectable item
        self.nav_list.setCurrentRow(1)
        
        layout.addWidget(self.nav_list, 1)  # stretch factor so list fills space
        
        return sidebar
    
    def _create_panels(self):
        """Create all the editing panels"""
        self.panels = {}
        
        # Employees panel (special - has id/name/role)
        self.panels['employees'] = EmployeesPanel()
        self.panel_stack.addWidget(self.panels['employees'])
        
        # Simple list panels
        simple_panels = [
            ('work_types', 'Work Types'),
            ('campuses', 'Campuses'),
            ('offers', 'Offers'),
            ('sub_offers', 'Sub-Offers'),
            ('effort_types', 'Effort Types'),
            ('course_types', 'Course Types'),
            ('project_statuses', 'Project Statuses'),
            ('tags', 'Tags'),
        ]
        
        for key, title in simple_panels:
            panel = EditableListPanel(title, key)
            self.panels[key] = panel
            self.panel_stack.addWidget(panel)
    
    def _create_status_bar(self):
        """Create the status bar"""
        status = QFrame()
        status.setStyleSheet("""
            QFrame {
                background-color: #e9ecef;
                border-top: 1px solid #dee2e6;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(status)
        layout.setContentsMargins(12, 4, 12, 4)
        
        self.status_label = QLabel("Editing: team_data.json")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.save_indicator = QLabel("✓ Auto-saved")
        self.save_indicator.setStyleSheet("color: #28a745;")
        layout.addWidget(self.save_indicator)
        
        return status
    
    def _update_folder_label(self):
        """Update the data folder label"""
        if data_service.data_folder:
            path_str = str(data_service.data_folder)
            # Truncate if too long
            if len(path_str) > 40:
                path_str = "..." + path_str[-37:]
            self.folder_label.setText(path_str)
        else:
            self.folder_label.setText("No folder selected")
    
    def _on_nav_changed(self, current: QListWidgetItem, previous):
        """Handle navigation item change"""
        if not current:
            return
        
        key = current.data(Qt.ItemDataRole.UserRole)
        if key and key in self.panels:
            self.panel_stack.setCurrentWidget(self.panels[key])
    
    def _on_back(self):
        """Go back to home screen"""
        self.main_window.navigate_to("home")
    
    def _on_change_folder(self):
        """Change the data folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Data Folder",
            str(data_service.data_folder) if data_service.data_folder else "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            data_service.data_folder = Path(folder)
            self._update_folder_label()
            self.refresh()
    
    def refresh(self):
        """Refresh all panels"""
        for panel in self.panels.values():
            panel.refresh()
        self._update_folder_label()
