"""
Home Screen - Main workspace with quick entry and project list
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QComboBox, QSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, date

from ..data_service import data_service
from ..models import Project, TimeEntry


class ProjectCard(QFrame):
    """A card displaying a single project in the list"""
    
    clicked = pyqtSignal(str)  # Emits project_id
    star_toggled = pyqtSignal(str, bool)  # Emits project_id, is_starred
    
    def __init__(self, project: Project, hours_logged: float, is_starred: bool = False):
        super().__init__()
        
        self.project_id = project.id
        self._is_starred = is_starred
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "card")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Top row: star, name and hours
        top_row = QHBoxLayout()
        
        # Star button
        self.star_btn = QPushButton()
        self.star_btn.setFixedSize(28, 28)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_star_button()
        self.star_btn.clicked.connect(self._on_star_clicked)
        top_row.addWidget(self.star_btn)
        
        name_label = QLabel(project.name)
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        top_row.addWidget(name_label)
        
        top_row.addStretch()
        
        hours_label = QLabel(f"{hours_logged} hrs")
        top_row.addWidget(hours_label)
        
        layout.addLayout(top_row)
        
        # Bottom row: breadcrumb and target
        bottom_row = QHBoxLayout()
        
        # Build breadcrumb from custom fields or legacy fields
        crumbs = []
        if project.custom_fields:
            # Use first few custom fields for breadcrumb
            for key in list(project.custom_fields.keys())[:3]:
                val = project.custom_fields.get(key)
                if val:
                    crumbs.append(val)
        if not crumbs:
            # Fall back to legacy fields
            if project.campus:
                crumbs.append(project.campus)
            if project.offer:
                crumbs.append(project.offer)
            if project.sub_offer:
                crumbs.append(project.sub_offer)
        
        breadcrumb = " › ".join(crumbs) if crumbs else "No category"
        crumb_label = QLabel(breadcrumb)
        crumb_label.setProperty("class", "muted")
        bottom_row.addWidget(crumb_label)
        
        bottom_row.addStretch()
        
        if project.target_hours > 0:
            target_label = QLabel(f"of {project.target_hours:.0f} target")
            target_label.setProperty("class", "muted")
            bottom_row.addWidget(target_label)
        
        layout.addLayout(bottom_row)
    
    def _update_star_button(self):
        """Update star button appearance based on starred state"""
        if self._is_starred:
            self.star_btn.setText("★")
            self.star_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #fbbf24;
                    font-size: 18px;
                    padding: 0px;
                }
                QPushButton:hover {
                    color: #f59e0b;
                }
            """)
        else:
            self.star_btn.setText("☆")
            self.star_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: #9ca3af;
                    font-size: 18px;
                    padding: 0px;
                }
                QPushButton:hover {
                    color: #fbbf24;
                }
            """)
    
    def _on_star_clicked(self):
        """Handle star button click"""
        self._is_starred = not self._is_starred
        self._update_star_button()
        self.star_toggled.emit(self.project_id, self._is_starred)
    
    def mousePressEvent(self, event):
        """Handle click on the card"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Don't trigger if clicking the star button
            star_rect = self.star_btn.geometry()
            if not star_rect.contains(event.pos()):
                self.clicked.emit(self.project_id)


class HomeScreen(QWidget):
    """Main home screen with quick entry and project list"""
    
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (dark bar, edge-to-edge)
        header = self._create_header()
        layout.addWidget(header)
        
        # Quick entry section
        quick_entry = self._create_quick_entry()
        layout.addWidget(quick_entry)
        
        # Project list (with padding)
        projects_section = self._create_project_list()
        layout.addWidget(projects_section, 1)  # Stretch
        
        # Status bar
        status = self._create_status_bar()
        layout.addWidget(status)
    
    def _create_header(self):
        """Create the header with title and user info"""
        header = QFrame()
        header.setObjectName("headerFrame")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        title = QLabel("PROJECT TRACKER")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Navigation buttons
        reports_btn = QPushButton("Reports")
        reports_btn.clicked.connect(self._on_reports)
        header_layout.addWidget(reports_btn)
        
        admin_btn = QPushButton("Admin")
        admin_btn.clicked.connect(self._on_admin)
        header_layout.addWidget(admin_btn)
        
        header_layout.addSpacing(12)
        
        # User badge
        self.user_label = QLabel()
        self._update_user_label()
        header_layout.addWidget(self.user_label)
        
        return header
    
    def _update_user_label(self):
        """Update the user label with current user info"""
        user = data_service.current_user
        if user:
            self.user_label.setText(f"{user.name} ({user.role})")
        else:
            username = data_service.get_os_username()
            self.user_label.setText(f"{username}")
    
    def _create_quick_entry(self):
        """Create the quick time entry section"""
        frame = QFrame()
        frame.setProperty("class", "card")
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Hours spinbox (first in order)
        hours_label = QLabel("Hours:")
        hours_label.setStyleSheet("color: dimgray; font-weight: bold; border: none;")
        layout.addWidget(hours_label)
        
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(1, 8)
        self.hours_spin.setValue(1)
        self.hours_spin.setMinimumWidth(50)
        self.hours_spin.setMinimumHeight(36)
        self.hours_spin.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 4px 8px;
                border: 1px solid silver;
                border-radius: 4px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0;
                border: none;
            }
        """)
        layout.addWidget(self.hours_spin)
        
        layout.addSpacing(8)
        
        # Project dropdown (second)
        project_label = QLabel("Project:")
        project_label.setStyleSheet("color: dimgray; font-weight: bold; border: none;")
        layout.addWidget(project_label)
        
        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select project...")
        self.project_combo.setMinimumWidth(200)
        self.project_combo.setMinimumHeight(36)
        self.project_combo.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                padding: 4px 8px;
                border: 1px solid silver;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.project_combo)
        
        layout.addSpacing(8)
        
        # Work type dropdown (third)
        work_type_label = QLabel("Work Type:")
        work_type_label.setStyleSheet("color: dimgray; font-weight: bold; border: none;")
        layout.addWidget(work_type_label)
        
        self.work_type_combo = QComboBox()
        self.work_type_combo.setPlaceholderText("Select type...")
        self.work_type_combo.setMinimumWidth(160)
        self.work_type_combo.setMinimumHeight(36)
        self.work_type_combo.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                padding: 4px 8px;
                border: 1px solid silver;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.work_type_combo)
        
        layout.addSpacing(8)
        
        # Date picker (defaults to today)
        date_label = QLabel("Date:")
        date_label.setStyleSheet("color: dimgray; font-weight: bold; border: none;")
        layout.addWidget(date_label)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumHeight(36)
        self.date_edit.setMinimumWidth(110)
        self.date_edit.setDisplayFormat("MMM d, yyyy")
        layout.addWidget(self.date_edit)
        
        layout.addSpacing(12)
        
        # Log button (fourth)
        self.log_btn = QPushButton("Log")
        self.log_btn.setMinimumHeight(36)
        self.log_btn.setMinimumWidth(80)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
            QPushButton:pressed {
                background-color: darkgreen;
            }
        """)
        self.log_btn.clicked.connect(self._on_log_time)
        layout.addWidget(self.log_btn)
        
        layout.addStretch()
        
        # New Project button (right side)
        self.new_project_btn = QPushButton("+ New Project")
        self.new_project_btn.setMinimumHeight(36)
        self.new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid gray;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: gainsboro;
                border-color: dimgray;
            }
            QPushButton:pressed {
                background-color: lightgray;
            }
        """)
        self.new_project_btn.clicked.connect(self._on_new_project)
        layout.addWidget(self.new_project_btn)
        
        return frame
    
    def _create_project_list(self):
        """Create the scrollable project list"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        self.project_list_widget = QWidget()
        self.project_list_widget.setStyleSheet("background-color: white;")
        self.project_list_layout = QVBoxLayout(self.project_list_widget)
        self.project_list_layout.setSpacing(8)
        self.project_list_layout.setContentsMargins(20, 16, 20, 16)
        self.project_list_layout.addStretch()
        
        scroll.setWidget(self.project_list_widget)
        
        return scroll
    
    def _create_status_bar(self):
        """Create the status bar"""
        frame = QFrame()
        frame.setObjectName("footerFrame")
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 8, 20, 8)
        
        self.project_count_label = QLabel("0 projects")
        layout.addWidget(self.project_count_label)
        
        layout.addStretch()
        
        self.today_total_label = QLabel("Today: 0.0 hrs")
        layout.addWidget(self.today_total_label)
        
        return frame
    
    # =========================================================================
    # Actions
    # =========================================================================
    
    def _on_log_time(self):
        """Handle the Log button - save a time entry"""
        project_id = self.project_combo.currentData()
        work_type = self.work_type_combo.currentText()
        hours = self.hours_spin.value()
        selected_date = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Validate
        if not project_id:
            return
        if not work_type:
            return
        if hours < 1:
            return
        
        # Create and save entry
        entry = TimeEntry.create_simple(
            project_id=project_id,
            work_type=work_type,
            hours=hours,
            entry_date=selected_date
        )
        
        data_service.save_time_entry(entry)
        
        # Reset the form
        self.hours_spin.setValue(1)
        self.project_combo.setCurrentIndex(-1)
        self.work_type_combo.setCurrentIndex(-1)
        self.date_edit.setDate(QDate.currentDate())
        
        # Refresh display
        self.refresh()
    
    def _on_project_clicked(self, project_id: str):
        """Handle click on a project card"""
        project = data_service.get_project(project_id)
        if project:
            self.main_window.show_project(project)
    
    def _on_new_project(self):
        """Handle new project button"""
        from ..models import Project
        new_project = Project(
            id="",
            name=""
        )
        self.main_window.show_project(new_project, is_new=True)
    
    def _on_admin(self):
        """Navigate to admin screen"""
        self.main_window.navigate_to("admin")
    
    def _on_reports(self):
        """Navigate to reports screen"""
        self.main_window.navigate_to("reports")
    
    # =========================================================================
    # Refresh
    # =========================================================================
    
    def refresh(self):
        """Refresh all data and UI"""
        if not data_service.is_configured():
            return
        
        self._update_user_label()
        self._refresh_dropdowns()
        self._refresh_project_list()
        self._refresh_status_bar()
    
    def _refresh_dropdowns(self):
        """Refresh the project and work type dropdowns"""
        # Save current selections
        current_project = self.project_combo.currentData()
        current_work_type = self.work_type_combo.currentText()
        
        # Refresh projects
        self.project_combo.clear()
        projects = data_service.get_all_projects()
        for project in projects:
            self.project_combo.addItem(project.name, project.id)
        
        # Restore selection if still valid
        if current_project:
            idx = self.project_combo.findData(current_project)
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
        
        # Refresh work types
        self.work_type_combo.clear()
        if data_service.team_data:
            for wt in data_service.team_data.work_types:
                self.work_type_combo.addItem(wt)
        
        # Restore selection if still valid
        if current_work_type:
            idx = self.work_type_combo.findText(current_work_type)
            if idx >= 0:
                self.work_type_combo.setCurrentIndex(idx)
    
    def _refresh_project_list(self):
        """Refresh the project list with starred and other sections"""
        # Clear existing widgets
        while self.project_list_layout.count() > 1:  # Keep the stretch
            item = self.project_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get all projects and starred set
        projects = data_service.get_all_projects()
        starred_ids = data_service.get_starred_projects()
        
        # Split into starred and other
        starred_projects = [p for p in projects if p.id in starred_ids]
        other_projects = [p for p in projects if p.id not in starred_ids]
        
        insert_index = 0
        
        # Starred section (only if there are starred projects)
        if starred_projects:
            # Section header
            starred_header = QLabel("★ Priority")
            starred_header.setStyleSheet("""
                color: dimgray; 
                font-weight: bold; 
                font-size: 11px;
                padding: 4px 0;
            """)
            self.project_list_layout.insertWidget(insert_index, starred_header)
            insert_index += 1
            
            # Starred project cards
            for project in starred_projects:
                hours = data_service.get_project_total_hours(project.id)
                card = ProjectCard(project, hours, is_starred=True)
                card.clicked.connect(self._on_project_clicked)
                card.star_toggled.connect(self._on_star_toggled)
                self.project_list_layout.insertWidget(insert_index, card)
                insert_index += 1
            
            # Divider
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setStyleSheet("background-color: silver; margin: 8px 0;")
            divider.setFixedHeight(1)
            self.project_list_layout.insertWidget(insert_index, divider)
            insert_index += 1
        
        # Other projects section
        if other_projects:
            # Section header
            other_header = QLabel("Other Projects")
            other_header.setStyleSheet("""
                color: dimgray; 
                font-weight: bold; 
                font-size: 11px;
                padding: 4px 0;
            """)
            self.project_list_layout.insertWidget(insert_index, other_header)
            insert_index += 1
            
            # Other project cards
            for project in other_projects:
                hours = data_service.get_project_total_hours(project.id)
                card = ProjectCard(project, hours, is_starred=False)
                card.clicked.connect(self._on_project_clicked)
                card.star_toggled.connect(self._on_star_toggled)
                self.project_list_layout.insertWidget(insert_index, card)
                insert_index += 1
    
    def _on_star_toggled(self, project_id: str, is_starred: bool):
        """Handle star toggle on a project card"""
        data_service.set_project_starred(project_id, is_starred)
        # Refresh the list to move the card to the right section
        self._refresh_project_list()
    
    def _refresh_status_bar(self):
        """Refresh the status bar"""
        projects = data_service.get_all_projects()
        self.project_count_label.setText(f"{len(projects)} projects")
        
        today_hours = data_service.get_today_total_hours()
        self.today_total_label.setText(f"Today: {today_hours} hrs")
