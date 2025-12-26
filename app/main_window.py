"""
Main window for Project Tracker
"""

from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout, 
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt

from .data_service import data_service
from .themes import theme_manager
from .screens.home_screen import HomeScreen
from .screens.admin_screen import AdminScreen
from .screens.project_detail_screen import ProjectDetailScreen
from .screens.reports_screen import ReportsScreen


class MainWindow(QMainWindow):
    """Main application window with screen navigation"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Project Tracker")
        self.setMinimumSize(900, 700)
        
        # Apply theme
        self.apply_theme()
        
        # Central widget with stacked screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Initialize screens
        self.home_screen = HomeScreen(self)
        self.stack.addWidget(self.home_screen)
        
        self.admin_screen = AdminScreen(self)
        self.stack.addWidget(self.admin_screen)
        
        self.project_detail_screen = ProjectDetailScreen(self)
        self.stack.addWidget(self.project_detail_screen)
        
        self.reports_screen = ReportsScreen(self)
        self.stack.addWidget(self.reports_screen)
        
        # Check if configured, prompt for data folder if not
        if not data_service.is_configured():
            self._prompt_for_data_folder()
        else:
            data_service.reload_all()
            self.home_screen.refresh()
    
    def apply_theme(self):
        """Apply the current theme stylesheet"""
        stylesheet = theme_manager.generate_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def _prompt_for_data_folder(self):
        """Prompt user to select a data folder on first run"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Welcome to Project Tracker")
        msg.setText("Please select a folder for your project data.\n\n"
                   "This should be a shared folder (like OneDrive) if you want "
                   "to collaborate with your team.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Data Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            from pathlib import Path
            data_service.data_folder = Path(folder)
            self.home_screen.refresh()
        else:
            # No folder selected - app will be limited
            QMessageBox.warning(
                self,
                "No Folder Selected",
                "You can set a data folder later from the Admin screen."
            )
    
    def navigate_to(self, screen_name: str, **kwargs):
        """Navigate to a different screen"""
        if screen_name == "home":
            self.stack.setCurrentWidget(self.home_screen)
            self.home_screen.refresh()
        elif screen_name == "admin":
            self.stack.setCurrentWidget(self.admin_screen)
            self.admin_screen.refresh()
        elif screen_name == "project_detail":
            project = kwargs.get('project')
            is_new = kwargs.get('is_new', False)
            if project:
                self.project_detail_screen.set_project(project, is_new=is_new)
            self.stack.setCurrentWidget(self.project_detail_screen)
        elif screen_name == "reports":
            self.stack.setCurrentWidget(self.reports_screen)
            self.reports_screen.refresh()
    
    def show_admin(self):
        """Show admin screen"""
        self.navigate_to("admin")
    
    def show_project(self, project, is_new=False):
        """Show project detail screen"""
        self.navigate_to("project_detail", project=project, is_new=is_new)
    
    def show_reports(self):
        """Show reports screen"""
        self.navigate_to("reports")
