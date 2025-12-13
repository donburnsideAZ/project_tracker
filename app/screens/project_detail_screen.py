"""
Project Detail Screen - View/edit project, TMs, and time log
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTabWidget, QFormLayout, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDialog,
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from pathlib import Path

from ..data_service import data_service
from ..models import Project, TimeEntry



class DetailsTab(QWidget):
    """Tab showing project details with edit capability"""
    
    project_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._project: Project = None
        self._edit_mode = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        self.form_layout.setSpacing(12)
        
        # Course Information section
        section_label = QLabel("Course Information")
        section_font = QFont()
        section_font.setBold(True)
        section_label.setFont(section_font)
        self.form_layout.addRow(section_label)
        
        self.course_id_edit = QLineEdit()
        self.form_layout.addRow("Course ID:", self.course_id_edit)
        
        self.name_edit = QLineEdit()
        self.form_layout.addRow("Course Name:", self.name_edit)
        
        self.campus_combo = QComboBox()
        self.campus_combo.setEditable(True)
        self.form_layout.addRow("Campus:", self.campus_combo)
        
        self.offer_combo = QComboBox()
        self.offer_combo.setEditable(True)
        self.form_layout.addRow("Offer:", self.offer_combo)
        
        self.sub_offer_combo = QComboBox()
        self.sub_offer_combo.setEditable(True)
        self.form_layout.addRow("Sub-Offer:", self.sub_offer_combo)
        
        self.effort_type_combo = QComboBox()
        self.form_layout.addRow("Effort Type:", self.effort_type_combo)
        
        self.course_type_combo = QComboBox()
        self.form_layout.addRow("Course Type:", self.course_type_combo)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 9999)
        self.duration_spin.setSuffix(" minutes")
        self.form_layout.addRow("Course Duration:", self.duration_spin)
        
        self.target_hours_spin = QDoubleSpinBox()
        self.target_hours_spin.setRange(0, 9999)
        self.target_hours_spin.setSuffix(" hours")
        self.target_hours_spin.setDecimals(1)
        self.form_layout.addRow("Target Hours:", self.target_hours_spin)
        
        # Team section
        team_label = QLabel("Team Assignments")
        team_label.setFont(section_font)
        self.form_layout.addRow("", QLabel(""))  # Spacer
        self.form_layout.addRow(team_label)
        
        self.lpo_combo = QComboBox()
        self.lpo_combo.setEditable(True)
        self.form_layout.addRow("LPO:", self.lpo_combo)
        
        self.sme_combo = QComboBox()
        self.sme_combo.setEditable(True)
        self.form_layout.addRow("SME:", self.sme_combo)
        
        self.lxo_combo = QComboBox()
        self.lxo_combo.setEditable(True)
        self.form_layout.addRow("LXO:", self.lxo_combo)
        
        self.status_combo = QComboBox()
        self.form_layout.addRow("Status:", self.status_combo)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll, 1)
        
        # Initially read-only
        self._set_edit_mode(False)
    
    def _populate_dropdowns(self):
        """Populate combo boxes from team_data"""
        if not data_service.team_data:
            return
        
        td = data_service.team_data
        
        # Clear and populate
        self.campus_combo.clear()
        self.campus_combo.addItem("")
        self.campus_combo.addItems(td.campuses)
        
        self.offer_combo.clear()
        self.offer_combo.addItem("")
        self.offer_combo.addItems(td.offers)
        
        self.sub_offer_combo.clear()
        self.sub_offer_combo.addItem("")
        self.sub_offer_combo.addItems(td.sub_offers)
        
        self.effort_type_combo.clear()
        self.effort_type_combo.addItems(td.effort_types)
        
        self.course_type_combo.clear()
        self.course_type_combo.addItems(td.course_types)
        
        self.status_combo.clear()
        self.status_combo.addItems(td.project_statuses)
        
        # Employee combos
        emp_names = [""]
        for emp in td.employees:
            if isinstance(emp, dict):
                emp_names.append(f"{emp.get('name', '')} ({emp.get('id', '')})")
        
        self.lpo_combo.clear()
        self.lpo_combo.addItems(emp_names)
        
        self.sme_combo.clear()
        self.sme_combo.addItems(emp_names)
        
        self.lxo_combo.clear()
        self.lxo_combo.addItems(emp_names)
    
    def _set_edit_mode(self, enabled: bool):
        """Enable or disable editing"""
        self._edit_mode = enabled
        
        widgets = [
            self.course_id_edit, self.name_edit, self.campus_combo,
            self.offer_combo, self.sub_offer_combo, self.effort_type_combo,
            self.course_type_combo, self.duration_spin, self.target_hours_spin,
            self.lpo_combo, self.sme_combo, self.lxo_combo, self.status_combo
        ]
        
        for w in widgets:
            w.setEnabled(enabled)
    
    def set_project(self, project: Project):
        """Load a project into the form"""
        self._project = project
        self._populate_dropdowns()
        
        if not project:
            return
        
        self.course_id_edit.setText(project.course_id or "")
        self.name_edit.setText(project.name or "")
        
        # Set combo values
        self.campus_combo.setCurrentText(project.campus or "")
        self.offer_combo.setCurrentText(project.offer or "")
        self.sub_offer_combo.setCurrentText(project.sub_offer or "")
        self.effort_type_combo.setCurrentText(project.effort_type or "")
        self.course_type_combo.setCurrentText(project.course_type or "")
        self.status_combo.setCurrentText(project.status or "Not Started")
        
        self.duration_spin.setValue(project.course_duration_minutes or 0)
        self.target_hours_spin.setValue(project.target_hours or 0)
        
        # Team - need to find matching employee
        self._set_employee_combo(self.lpo_combo, project.lpo)
        self._set_employee_combo(self.sme_combo, project.sme)
        self._set_employee_combo(self.lxo_combo, project.lxo)
    
    def _set_employee_combo(self, combo: QComboBox, emp_id: str):
        """Set employee combo to match an ID"""
        if not emp_id:
            combo.setCurrentIndex(0)
            return
        
        for i in range(combo.count()):
            if emp_id in combo.itemText(i):
                combo.setCurrentIndex(i)
                return
        
        combo.setCurrentText(emp_id)
    
    def _get_employee_id(self, combo: QComboBox) -> str:
        """Extract employee ID from combo selection"""
        text = combo.currentText()
        if "(" in text and ")" in text:
            # Extract ID from "Name (id)" format
            return text.split("(")[-1].rstrip(")")
        return text
    
    def get_project_data(self) -> dict:
        """Get current form values as a dict"""
        return {
            'course_id': self.course_id_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'campus': self.campus_combo.currentText().strip(),
            'offer': self.offer_combo.currentText().strip(),
            'sub_offer': self.sub_offer_combo.currentText().strip(),
            'effort_type': self.effort_type_combo.currentText(),
            'course_type': self.course_type_combo.currentText(),
            'course_duration_minutes': self.duration_spin.value(),
            'target_hours': self.target_hours_spin.value(),
            'lpo': self._get_employee_id(self.lpo_combo),
            'sme': self._get_employee_id(self.sme_combo),
            'lxo': self._get_employee_id(self.lxo_combo),
            'status': self.status_combo.currentText()
        }
    
    def enable_edit(self):
        self._set_edit_mode(True)
    
    def disable_edit(self):
        self._set_edit_mode(False)
    
    @property
    def edit_mode(self):
        return self._edit_mode


class TMCard(QFrame):
    """A card for a single Training Module"""
    
    clicked = pyqtSignal(int)  # Emits TM number
    
    def __init__(self, number: int, name: str = "", status: str = "Not Started"):
        super().__init__()
        
        self.number = number
        self.tm_name = name
        self.status = status
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        
        # Style based on status
        self._update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Header row
        header = QHBoxLayout()
        
        tm_label = QLabel(f"TM{self.number}")
        tm_font = QFont()
        tm_font.setBold(True)
        tm_label.setFont(tm_font)
        header.addWidget(tm_label)
        
        header.addStretch()
        
        self.status_label = QLabel(self.status)
        self.status_label.setStyleSheet("font-size: 10px;")
        header.addWidget(self.status_label)
        
        layout.addLayout(header)
        
        # Name
        self.name_label = QLabel(self.tm_name or "(unnamed)")
        self.name_label.setStyleSheet("color: #495057;")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        layout.addStretch()
    
    def _update_style(self):
        if self.status == "Complete":
            bg = "#d4edda"
            border = "#28a745"
        elif self.status == "In Progress":
            bg = "#fff3cd"
            border = "#ffc107"
        else:
            bg = "#f8f9fa"
            border = "#dee2e6"
        
        self.setStyleSheet(f"""
            TMCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            TMCard:hover {{
                border-width: 2px;
            }}
        """)
    
    def update_data(self, name: str, status: str):
        """Update the card data"""
        self.tm_name = name
        self.status = status
        self.name_label.setText(name or "(unnamed)")
        self.status_label.setText(status)
        self._update_style()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.number)


class EditTMDialog(QDialog):
    """Dialog for editing a Training Module"""
    
    def __init__(self, parent, number: int, name: str = "", status: str = "Not Started", allow_delete: bool = False):
        super().__init__(parent)
        
        self.delete_requested = False
        
        self.setWindowTitle(f"Edit TM{number}")
        self.setMinimumWidth(350)
        
        layout = QFormLayout(self)
        
        # TM Number (read-only display)
        number_label = QLabel(f"TM{number}")
        number_font = QFont()
        number_font.setBold(True)
        number_label.setFont(number_font)
        layout.addRow("Module:", number_label)
        
        # Name
        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Module name...")
        layout.addRow("Name:", self.name_edit)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Not Started", "In Progress", "Complete"])
        self.status_combo.setCurrentText(status)
        layout.addRow("Status:", self.status_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        if allow_delete:
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("color: #dc3545;")
            delete_btn.clicked.connect(self._on_delete)
            btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
    
    def _on_delete(self):
        """Handle delete button"""
        self.delete_requested = True
        self.reject()
    
    def get_values(self):
        return {
            'name': self.name_edit.text().strip(),
            'status': self.status_combo.currentText()
        }


class TMsTab(QWidget):
    """Tab showing Training Modules / Chunking Guide"""
    
    project_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._project: Project = None
        self._tm_cards: list[TMCard] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Chunking Guide")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        header.addWidget(title)
        
        header.addStretch()
        
        self.add_btn = QPushButton("+ Add TM")
        self.add_btn.clicked.connect(self._on_add_tm)
        header.addWidget(self.add_btn)
        
        layout.addLayout(header)
        layout.addSpacing(12)
        
        # Scroll area for TM cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Empty state label
        self.empty_label = QLabel("No training modules yet.\nClick '+ Add TM' to create one.")
        self.empty_label.setStyleSheet("color: #6c757d; padding: 40px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.empty_label, 0, 0, 1, 2)
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll, 1)
    
    def set_project(self, project: Project):
        """Load project TMs into cards"""
        self._project = project
        self._rebuild_cards()
    
    def _rebuild_cards(self):
        """Rebuild all TM cards from project data"""
        # Clear existing cards
        for card in self._tm_cards:
            card.deleteLater()
        self._tm_cards.clear()
        
        # Get TMs from project
        tms = []
        if self._project and self._project.tms:
            tms = sorted(self._project.tms, key=lambda t: t.get('number', 0) if isinstance(t, dict) else 0)
        
        # Show/hide empty state
        self.empty_label.setVisible(len(tms) == 0)
        
        # Create cards
        for i, tm in enumerate(tms):
            if isinstance(tm, dict):
                number = tm.get('number', i + 1)
                name = tm.get('name', '')
                status = tm.get('status', 'Not Started')
                
                card = TMCard(number, name, status)
                card.clicked.connect(self._on_tm_clicked)
                self._tm_cards.append(card)
                
                row = i // 2
                col = i % 2
                self.grid_layout.addWidget(card, row + 1, col)  # +1 to leave room for empty label row
    
    def _on_add_tm(self):
        """Add a new TM"""
        if not self._project:
            return
        
        # Determine next TM number
        existing_numbers = set()
        if self._project.tms:
            for tm in self._project.tms:
                if isinstance(tm, dict):
                    existing_numbers.add(tm.get('number', 0))
        
        next_number = 1
        while next_number in existing_numbers:
            next_number += 1
        
        # Show dialog for new TM
        dialog = EditTMDialog(self, next_number, "", "Not Started", allow_delete=False)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            
            # Add to project
            if not self._project.tms:
                self._project.tms = []
            
            self._project.tms.append({
                'number': next_number,
                'name': values['name'],
                'status': values['status']
            })
            
            self._rebuild_cards()
            self.project_updated.emit()
    
    def _on_tm_clicked(self, number: int):
        """Handle TM card click - edit or delete"""
        if not self._project:
            return
        
        # Find current TM data
        current_name = ""
        current_status = "Not Started"
        
        if self._project.tms:
            for tm in self._project.tms:
                if isinstance(tm, dict) and tm.get('number') == number:
                    current_name = tm.get('name', '')
                    current_status = tm.get('status', 'Not Started')
                    break
        
        # Show edit dialog with delete option
        dialog = EditTMDialog(self, number, current_name, current_status, allow_delete=True)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            self._update_tm(number, values['name'], values['status'])
        elif dialog.delete_requested:
            self._delete_tm(number)
    
    def _update_tm(self, number: int, name: str, status: str):
        """Update a TM in the project"""
        if not self._project or not self._project.tms:
            return
        
        for tm in self._project.tms:
            if isinstance(tm, dict) and tm.get('number') == number:
                tm['name'] = name
                tm['status'] = status
                break
        
        self._rebuild_cards()
        self.project_updated.emit()
    
    def _delete_tm(self, number: int):
        """Delete a TM from the project"""
        if not self._project or not self._project.tms:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete TM",
            f"Delete TM{number}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._project.tms = [
                tm for tm in self._project.tms 
                if not (isinstance(tm, dict) and tm.get('number') == number)
            ]
            self._rebuild_cards()
            self.project_updated.emit()


class TimeLogTab(QWidget):
    """Tab showing time entries for this project"""
    
    def __init__(self):
        super().__init__()
        self._project: Project = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header with total
        header = QHBoxLayout()
        
        title = QLabel("Time Log")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        header.addWidget(title)
        
        header.addStretch()
        
        self.total_label = QLabel("Total: 0.0 hrs")
        self.total_label.setStyleSheet("font-weight: bold;")
        header.addWidget(self.total_label)
        
        layout.addLayout(header)
        layout.addSpacing(12)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "User", "Work Type", "Duration", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table, 1)
    
    def set_project(self, project: Project):
        """Load time entries for this project"""
        self._project = project
        self._load_entries()
    
    def _load_entries(self):
        """Load all time entries for this project"""
        self.table.setRowCount(0)
        
        if not self._project or not data_service.data_folder:
            self.total_label.setText("Total: 0.0 hrs")
            return
        
        # Scan all time files for entries matching this project
        time_dir = data_service.data_folder / "time"
        if not time_dir.exists():
            return
        
        entries = []
        for file_path in time_dir.glob("*.json"):
            try:
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                user_id = data.get('user_id', '')
                for entry in data.get('entries', []):
                    if entry.get('project_id') == self._project.id:
                        # Support both new 'hours' and legacy 'duration_minutes'
                        if 'hours' in entry:
                            hours = entry.get('hours', 0)
                        else:
                            hours = entry.get('duration_minutes', 0) // 60
                        
                        # Get date from new 'date' field or legacy 'start_time'
                        entry_date = entry.get('date') or entry.get('start_time', '')[:10]
                        
                        entries.append({
                            'user_id': user_id,
                            'date': entry_date,
                            'work_type': entry.get('work_type', ''),
                            'hours': hours,
                            'notes': entry.get('notes', '')
                        })
            except:
                continue
        
        # Sort by date descending
        entries.sort(key=lambda e: e['date'], reverse=True)
        
        # Populate table
        total_hours = 0
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(entry['date']))
            self.table.setItem(row, 1, QTableWidgetItem(entry['user_id']))
            self.table.setItem(row, 2, QTableWidgetItem(entry['work_type']))
            
            hours = entry['hours']
            self.table.setItem(row, 3, QTableWidgetItem(f"{hours} hrs"))
            
            self.table.setItem(row, 4, QTableWidgetItem(entry['notes']))
            
            total_hours += entry['hours']
        
        self.total_label.setText(f"Total: {total_hours} hrs")
    
    def refresh(self):
        """Refresh the time log"""
        self._load_entries()


class ProjectDetailScreen(QWidget):
    """Project detail screen with tabs"""
    
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        self._project: Project = None
        self._is_new = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Project info bar
        self.info_bar = self._create_info_bar()
        layout.addWidget(self.info_bar)
        
        # Action buttons
        actions = self._create_actions()
        layout.addWidget(actions)
        
        # Tabs
        self.tabs = QTabWidget()
        
        self.details_tab = DetailsTab()
        self.details_tab.project_updated.connect(self._on_project_updated)
        self.tabs.addTab(self.details_tab, "Details")
        
        self.tms_tab = TMsTab()
        self.tms_tab.project_updated.connect(self._on_project_updated)
        self.tabs.addTab(self.tms_tab, "Chunking Guide")
        
        self.time_log_tab = TimeLogTab()
        self.tabs.addTab(self.time_log_tab, "Time Log")
        
        layout.addWidget(self.tabs, 1)
        
        # Status bar
        status = self._create_status_bar()
        layout.addWidget(status)
    
    def _create_header(self):
        """Create header with back button"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 8px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self._on_back)
        layout.addWidget(back_btn)
        
        title = QLabel("PROJECT TRACKER")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # User label
        self.user_label = QLabel()
        self._update_user_label()
        layout.addWidget(self.user_label)
        
        return header
    
    def _create_info_bar(self):
        """Create project info display"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #dee2e6;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        
        # Row 1: Name and status
        row1 = QHBoxLayout()
        
        self.project_name_label = QLabel("New Project")
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        self.project_name_label.setFont(name_font)
        row1.addWidget(self.project_name_label)
        
        row1.addStretch()
        
        self.status_badge = QLabel("Not Started")
        self.status_badge.setStyleSheet("""
            QLabel {
                background-color: #6c757d;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        row1.addWidget(self.status_badge)
        
        # Save button (next to status, same size, green) - hidden until edit mode
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setVisible(False)
        row1.addWidget(self.save_btn)
        
        # Cancel button - also hidden until edit mode
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_btn.clicked.connect(self._on_cancel_edit)
        self.cancel_btn.setVisible(False)
        row1.addWidget(self.cancel_btn)
        
        layout.addLayout(row1)
        
        # Row 2: Course ID and breadcrumb
        row2 = QHBoxLayout()
        
        self.course_id_label = QLabel("")
        self.course_id_label.setStyleSheet("color: #6c757d;")
        row2.addWidget(self.course_id_label)
        
        row2.addSpacing(20)
        
        self.breadcrumb_label = QLabel("")
        self.breadcrumb_label.setStyleSheet("color: #6c757d;")
        row2.addWidget(self.breadcrumb_label)
        
        row2.addStretch()
        layout.addLayout(row2)
        
        # Row 3: Stats
        stats_row = QHBoxLayout()
        stats_row.setSpacing(40)
        
        self.logged_stat = self._create_stat("0.0", "Logged")
        stats_row.addLayout(self.logged_stat)
        
        self.target_stat = self._create_stat("0.0", "Target")
        stats_row.addLayout(self.target_stat)
        
        self.ratio_stat = self._create_stat("0.00", "Ratio")
        stats_row.addLayout(self.ratio_stat)
        
        self.lead_time_stat = self._create_stat("—", "Lead Time")
        stats_row.addLayout(self.lead_time_stat)
        
        stats_row.addStretch()
        layout.addLayout(stats_row)
        
        return frame
    
    def _create_stat(self, value: str, label: str) -> QVBoxLayout:
        """Create a stat display"""
        layout = QVBoxLayout()
        layout.setSpacing(2)
        
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        value_label.setFont(value_font)
        layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(label_label)
        
        # Store reference to value label for updates
        layout.value_label = value_label
        
        return layout
    
    def _create_actions(self):
        """Create action buttons"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 8px 16px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit)
        layout.addWidget(self.edit_btn)
        
        layout.addStretch()
        
        return frame
    
    def _create_status_bar(self):
        """Create status bar"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #e9ecef;
                border-top: 1px solid #dee2e6;
                padding: 6px 16px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.modified_label = QLabel("")
        self.modified_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        layout.addWidget(self.modified_label)
        
        layout.addStretch()
        
        return frame
    
    def _update_user_label(self):
        """Update user display"""
        user = data_service.current_user
        if user:
            self.user_label.setText(f"👤 {user.name} ({user.role})")
        else:
            self.user_label.setText(f"👤 {data_service.get_os_username()}")
    
    def set_project(self, project: Project, is_new: bool = False):
        """Load a project for viewing/editing"""
        self._project = project
        self._is_new = is_new
        
        # Update header info
        self._update_info_bar()
        
        # Load into tabs
        self.details_tab.set_project(project)
        self.tms_tab.set_project(project)
        self.time_log_tab.set_project(project)
        
        # Update status bar
        if project and project.modified_at:
            try:
                mod_dt = datetime.fromisoformat(project.modified_at.replace('Z', '+00:00'))
                mod_str = mod_dt.strftime("%b %d, %Y")
                modifier = project.modified_by or "unknown"
                self.modified_label.setText(f"Last modified: {mod_str} by {modifier}")
            except:
                self.modified_label.setText("")
        else:
            self.modified_label.setText("")
        
        # If new, enable edit mode
        if is_new:
            self._on_edit()
    
    def _update_info_bar(self):
        """Update the info bar with project data"""
        if not self._project:
            return
        
        p = self._project
        
        self.project_name_label.setText(p.name or "New Project")
        self.course_id_label.setText(p.course_id or p.id or "")
        
        # Breadcrumb
        crumbs = []
        if p.campus:
            crumbs.append(p.campus)
        if p.offer:
            crumbs.append(p.offer)
        if p.sub_offer:
            crumbs.append(p.sub_offer)
        
        extra = []
        if p.course_type:
            extra.append(p.course_type)
        if p.effort_type:
            extra.append(p.effort_type)
        
        breadcrumb = " › ".join(crumbs)
        if extra:
            breadcrumb += " • " + " • ".join(extra)
        
        self.breadcrumb_label.setText(breadcrumb)
        
        # Status badge color
        status = p.status or "Not Started"
        self.status_badge.setText(status)
        
        if status == "Complete":
            color = "#28a745"
        elif status == "In Progress":
            color = "#ffc107"
        else:
            color = "#6c757d"
        
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: {'black' if status == 'In Progress' else 'white'};
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
        """)
        
        # Stats
        logged = data_service.get_project_total_hours(p.id)
        target = p.target_hours or 0
        
        self.logged_stat.value_label.setText(f"{logged:.1f}")
        self.target_stat.value_label.setText(f"{target:.1f}")
        
        if target > 0:
            ratio = logged / target
            self.ratio_stat.value_label.setText(f"{ratio:.2f}")
            # Color red if over
            if ratio > 1:
                self.ratio_stat.value_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            else:
                self.ratio_stat.value_label.setStyleSheet("")
        else:
            self.ratio_stat.value_label.setText("—")
        
        # Lead time would require analyzing time entries - simplified for now
        self.lead_time_stat.value_label.setText("—")
    
    def _on_back(self):
        """Go back to home"""
        if self.details_tab.edit_mode:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.main_window.navigate_to("home")
    
    def _on_edit(self):
        """Enable edit mode"""
        self.details_tab.enable_edit()
        self.edit_btn.setVisible(False)
        self.save_btn.setVisible(True)
        self.cancel_btn.setVisible(True)
        self.tabs.setCurrentIndex(0)  # Switch to details tab
    
    def _on_cancel_edit(self):
        """Cancel editing"""
        if self._is_new:
            self.main_window.navigate_to("home")
            return
        
        # Reload project data
        self.details_tab.set_project(self._project)
        self.details_tab.disable_edit()
        
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
    
    def _on_save(self):
        """Save the project"""
        data = self.details_tab.get_project_data()
        
        # Validate required fields
        if not data['name']:
            QMessageBox.warning(self, "Validation Error", "Course Name is required.")
            return
        
        # Update project object
        if self._is_new:
            # Generate ID if needed
            if data['course_id']:
                self._project.id = data['course_id']
                self._project.course_id = data['course_id']
            else:
                self._project.id = Project.generate_id()
            
            self._project.created_at = datetime.now().isoformat()
            self._project.created_by = data_service.current_user_id
        
        # Apply form data
        self._project.name = data['name']
        self._project.course_id = data['course_id']
        self._project.campus = data['campus']
        self._project.offer = data['offer']
        self._project.sub_offer = data['sub_offer']
        self._project.effort_type = data['effort_type']
        self._project.course_type = data['course_type']
        self._project.course_duration_minutes = data['course_duration_minutes']
        self._project.target_hours = data['target_hours']
        self._project.lpo = data['lpo']
        self._project.sme = data['sme']
        self._project.lxo = data['lxo']
        self._project.status = data['status']
        
        # Save
        data_service.save_project(self._project)
        
        # Update UI
        self._is_new = False
        self._update_info_bar()
        self.details_tab.disable_edit()
        
        self.edit_btn.setVisible(True)
        self.save_btn.setVisible(False)
        self.cancel_btn.setVisible(False)
        
        # Update status bar
        self.modified_label.setText(f"Last modified: just now by {data_service.current_user_id}")
    
    def _on_project_updated(self):
        """Handle project update from tabs (e.g., TM changes)"""
        if self._project:
            data_service.save_project(self._project)
            self.modified_label.setText(f"Last modified: just now by {data_service.current_user_id}")
    
    def refresh(self):
        """Refresh the screen"""
        self._update_user_label()
        if self._project:
            self._update_info_bar()
            self.time_log_tab.refresh()
