"""
Theme Manager for Project Tracker
Provides predefined color themes and custom theme support
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class Theme:
    """Color theme definition"""
    name: str
    
    # Primary color (buttons, active tabs, links)
    primary: str
    primary_hover: str
    primary_text: str  # Text on primary-colored backgrounds
    
    # Accent color (sidebar selection, highlights)
    accent: str
    accent_hover: str
    accent_text: str
    
    # Header and footer
    header_bg: str
    header_text: str
    footer_bg: str
    footer_text: str
    
    # Sidebar
    sidebar_bg: str
    sidebar_text: str
    sidebar_selected_bg: str
    sidebar_selected_text: str
    sidebar_hover_bg: str
    
    # Content area
    content_bg: str
    content_alt_bg: str  # Alternating rows, cards
    text: str
    text_muted: str
    border: str
    
    # Status colors
    success: str
    warning: str
    error: str
    
    # Input fields
    input_bg: str
    input_border: str
    input_focus_border: str


# Predefined themes
THEMES = {
    "blue": Theme(
        name="Blue",
        primary="#2563eb",
        primary_hover="#1d4ed8",
        primary_text="#ffffff",
        accent="#f97316",
        accent_hover="#ea580c",
        accent_text="#ffffff",
        header_bg="#1f2937",
        header_text="#ffffff",
        footer_bg="#1f2937",
        footer_text="#ffffff",
        sidebar_bg="#f3f4f6",
        sidebar_text="#374151",
        sidebar_selected_bg="#dbeafe",
        sidebar_selected_text="#1e40af",
        sidebar_hover_bg="#e5e7eb",
        content_bg="#ffffff",
        content_alt_bg="#f9fafb",
        text="#111827",
        text_muted="#6b7280",
        border="#d1d5db",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        input_bg="#ffffff",
        input_border="#d1d5db",
        input_focus_border="#2563eb",
    ),
    
    "red": Theme(
        name="Red",
        primary="#dc2626",
        primary_hover="#b91c1c",
        primary_text="#ffffff",
        accent="#ea580c",
        accent_hover="#c2410c",
        accent_text="#ffffff",
        header_bg="#1f2937",
        header_text="#ffffff",
        footer_bg="#1f2937",
        footer_text="#ffffff",
        sidebar_bg="#fef2f2",
        sidebar_text="#374151",
        sidebar_selected_bg="#fecaca",
        sidebar_selected_text="#991b1b",
        sidebar_hover_bg="#fee2e2",
        content_bg="#ffffff",
        content_alt_bg="#fef2f2",
        text="#111827",
        text_muted="#6b7280",
        border="#d1d5db",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        input_bg="#ffffff",
        input_border="#d1d5db",
        input_focus_border="#dc2626",
    ),
    
    "green": Theme(
        name="Green",
        primary="#16a34a",
        primary_hover="#15803d",
        primary_text="#ffffff",
        accent="#0d9488",
        accent_hover="#0f766e",
        accent_text="#ffffff",
        header_bg="#1f2937",
        header_text="#ffffff",
        footer_bg="#1f2937",
        footer_text="#ffffff",
        sidebar_bg="#f0fdf4",
        sidebar_text="#374151",
        sidebar_selected_bg="#bbf7d0",
        sidebar_selected_text="#166534",
        sidebar_hover_bg="#dcfce7",
        content_bg="#ffffff",
        content_alt_bg="#f0fdf4",
        text="#111827",
        text_muted="#6b7280",
        border="#d1d5db",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        input_bg="#ffffff",
        input_border="#d1d5db",
        input_focus_border="#16a34a",
    ),
    
    "mono": Theme(
        name="Mono",
        primary="#18181b",
        primary_hover="#27272a",
        primary_text="#ffffff",
        accent="#52525b",
        accent_hover="#3f3f46",
        accent_text="#ffffff",
        header_bg="#18181b",
        header_text="#ffffff",
        footer_bg="#18181b",
        footer_text="#ffffff",
        sidebar_bg="#f4f4f5",
        sidebar_text="#27272a",
        sidebar_selected_bg="#e4e4e7",
        sidebar_selected_text="#18181b",
        sidebar_hover_bg="#e4e4e7",
        content_bg="#ffffff",
        content_alt_bg="#fafafa",
        text="#18181b",
        text_muted="#71717a",
        border="#d4d4d8",
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        input_bg="#ffffff",
        input_border="#d4d4d8",
        input_focus_border="#18181b",
    ),
}


class ThemeManager:
    """Manages theme loading, saving, and application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config_dir = Path.home() / ".projecttracker"
        self._theme_file = self._config_dir / "theme.json"
        self._current_theme_id = "blue"
        self._custom_theme: Optional[Theme] = None
        
        self._load_theme_preference()
    
    def _load_theme_preference(self):
        """Load saved theme preference"""
        self._config_dir.mkdir(exist_ok=True)
        
        if self._theme_file.exists():
            try:
                with open(self._theme_file, 'r') as f:
                    data = json.load(f)
                    self._current_theme_id = data.get('theme_id', 'blue')
                    if 'custom_theme' in data:
                        self._custom_theme = Theme(**data['custom_theme'])
            except (json.JSONDecodeError, TypeError):
                self._current_theme_id = "blue"
    
    def _save_theme_preference(self):
        """Save theme preference"""
        data = {'theme_id': self._current_theme_id}
        if self._custom_theme:
            data['custom_theme'] = asdict(self._custom_theme)
        
        with open(self._theme_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    @property
    def current_theme_id(self) -> str:
        return self._current_theme_id
    
    @property
    def current_theme(self) -> Theme:
        if self._current_theme_id == "custom" and self._custom_theme:
            return self._custom_theme
        return THEMES.get(self._current_theme_id, THEMES["blue"])
    
    @property
    def available_themes(self) -> list:
        """Get list of available theme IDs"""
        return list(THEMES.keys()) + ["custom"]
    
    def set_theme(self, theme_id: str):
        """Set the current theme"""
        if theme_id in THEMES or (theme_id == "custom" and self._custom_theme):
            self._current_theme_id = theme_id
            self._save_theme_preference()
    
    def set_custom_theme(self, theme: Theme):
        """Set custom theme colors"""
        self._custom_theme = theme
        self._current_theme_id = "custom"
        self._save_theme_preference()
    
    def get_custom_theme(self) -> Optional[Theme]:
        """Get the custom theme if defined"""
        return self._custom_theme
    
    def generate_stylesheet(self) -> str:
        """Generate QSS stylesheet from current theme"""
        t = self.current_theme
        
        return f"""
            /* ========== Global ========== */
            QWidget {{
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: {t.text};
                background-color: {t.content_bg};
            }}
            
            QLabel {{
                background-color: transparent;
            }}
            
            /* ========== Header Frame ========== */
            QFrame#headerFrame {{
                background-color: {t.header_bg};
                border: none;
                border-bottom: 1px solid {t.border};
            }}
            
            QFrame#headerFrame QLabel {{
                color: {t.header_text};
            }}
            
            QFrame#headerFrame QPushButton {{
                background-color: transparent;
                color: {t.header_text};
                border: 1px solid {t.header_text};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            
            QFrame#headerFrame QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            /* ========== Footer/Status Frame ========== */
            QFrame#footerFrame, QFrame#statusFrame {{
                background-color: {t.footer_bg};
                border: none;
                border-top: 1px solid {t.border};
            }}
            
            QFrame#footerFrame QLabel, QFrame#statusFrame QLabel {{
                color: {t.footer_text};
            }}
            
            /* ========== Sidebar ========== */
            QFrame#sidebarFrame {{
                background-color: {t.sidebar_bg};
                border: none;
                border-right: 1px solid {t.border};
            }}
            
            QFrame#sidebarFrame QListWidget {{
                background-color: transparent;
                border: none;
                color: {t.sidebar_text};
            }}
            
            QFrame#sidebarFrame QListWidget::item {{
                padding: 10px 16px;
                border: none;
            }}
            
            QFrame#sidebarFrame QListWidget::item:selected {{
                background-color: {t.sidebar_selected_bg};
                color: {t.sidebar_selected_text};
            }}
            
            QFrame#sidebarFrame QListWidget::item:hover:!selected {{
                background-color: {t.sidebar_hover_bg};
            }}
            
            /* ========== Primary Buttons ========== */
            QPushButton {{
                background-color: {t.primary};
                color: {t.primary_text};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {t.primary_hover};
            }}
            
            QPushButton:pressed {{
                background-color: {t.primary_hover};
            }}
            
            QPushButton:disabled {{
                background-color: {t.border};
                color: {t.text_muted};
            }}
            
            /* Format buttons (Notes tab) */
            QPushButton#formatBtn {{
                background-color: #374151;
                color: #ffffff;
                border: 1px solid #4b5563;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10pt;
            }}
            
            QPushButton#formatBtn:hover {{
                background-color: #4b5563;
                color: #ffffff;
            }}
            
            QPushButton#formatBtn:checked {{
                background-color: #1f2937;
                color: #ffffff;
            }}
            
            /* Secondary/Ghost Buttons */
            QPushButton.secondary, QPushButton[flat="true"] {{
                background-color: transparent;
                color: {t.text};
                border: 1px solid {t.border};
            }}
            
            QPushButton.secondary:hover, QPushButton[flat="true"]:hover {{
                background-color: {t.content_alt_bg};
            }}
            
            /* Small Buttons */
            QPushButton.small {{
                padding: 4px 8px;
                font-size: 9pt;
            }}
            
            /* ========== Input Fields ========== */
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
                background-color: {t.input_bg};
                border: 1px solid {t.input_border};
                border-radius: 4px;
                padding: 6px 10px;
                color: {t.text};
            }}
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
                border-color: {t.input_focus_border};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {t.input_bg};
                border: 1px solid {t.input_border};
                selection-background-color: {t.primary};
                selection-color: {t.primary_text};
            }}
            
            /* ========== Lists and Tables ========== */
            QListWidget, QTableWidget {{
                background-color: {t.content_bg};
                alternate-background-color: {t.content_alt_bg};
                border: 1px solid {t.border};
                border-radius: 4px;
            }}
            
            QListWidget::item {{
                padding: 8px;
            }}
            
            QListWidget::item:selected, QTableWidget::item:selected {{
                background-color: {t.primary};
                color: {t.primary_text};
            }}
            
            QHeaderView::section {{
                background-color: {t.content_alt_bg};
                color: {t.text};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {t.border};
                font-weight: bold;
            }}
            
            /* ========== Tabs ========== */
            QTabWidget::pane {{
                border: 1px solid {t.border};
                border-radius: 4px;
                background-color: {t.content_bg};
            }}
            
            QTabBar::tab {{
                background-color: {t.content_alt_bg};
                color: {t.text_muted};
                border: 1px solid {t.border};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {t.content_bg};
                color: {t.primary};
                border-bottom: 2px solid {t.primary};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {t.sidebar_hover_bg};
            }}
            
            /* ========== Scroll Bars ========== */
            QScrollBar:vertical {{
                background-color: {t.content_alt_bg};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {t.border};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {t.text_muted};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {t.content_alt_bg};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {t.border};
                border-radius: 6px;
                min-width: 30px;
            }}
            
            /* ========== Cards/Frames ========== */
            QFrame.card {{
                background-color: {t.content_alt_bg};
                border: 1px solid {t.border};
                border-radius: 6px;
            }}
            
            /* ========== Status Colors ========== */
            QLabel.success {{
                color: {t.success};
            }}
            
            QLabel.warning {{
                color: {t.warning};
            }}
            
            QLabel.error {{
                color: {t.error};
            }}
            
            /* ========== Muted Text ========== */
            QLabel.muted {{
                color: {t.text_muted};
            }}
            
            /* ========== Dialogs ========== */
            QDialog {{
                background-color: {t.content_bg};
            }}
            
            QMessageBox {{
                background-color: {t.content_bg};
            }}
            
            /* ========== Splitter ========== */
            QSplitter::handle {{
                background-color: {t.border};
            }}
            
            QSplitter::handle:hover {{
                background-color: {t.primary};
            }}
            
            /* ========== Tool Tips ========== */
            QToolTip {{
                background-color: {t.header_bg};
                color: {t.header_text};
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
            }}
        """


# Global instance
theme_manager = ThemeManager()
