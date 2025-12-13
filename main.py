#!/usr/bin/env python3
"""
Project Tracker - Time tracking for training development projects
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app.main_window import MainWindow


def main():
    # Enable high DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("Project Tracker")
    app.setOrganizationName("Axway")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
