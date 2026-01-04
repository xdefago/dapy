# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Main application window for dapy trace viewer."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMdiArea, QMenuBar, QMessageBox

from dapyview.trace_window import TraceWindow


class TraceViewerApp(QMainWindow):
    """Main application window supporting multiple trace documents."""
    
    def __init__(self) -> None:
        """Initialize the trace viewer application."""
        super().__init__()
        
        self.setWindowTitle("Dapy Trace Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create MDI area for multiple document windows
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        # Set up menus
        self._create_menus()
        
        # Track open trace windows
        self.trace_windows: list[TraceWindow] = []
    
    def _create_menus(self) -> None:
        """Create application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Trace...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_trace_dialog)
        file_menu.addAction(open_action)
        
        close_action = QAction("&Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_current_window)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Window menu
        window_menu = menubar.addMenu("&Window")
        
        cascade_action = QAction("&Cascade", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_action)
        
        tile_action = QAction("&Tile", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_trace_dialog(self) -> None:
        """Show file dialog to open a trace file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Trace File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.open_trace_file(Path(file_path))
    
    def open_trace_file(self, file_path: Path) -> Optional[TraceWindow]:
        """Open a trace file in a new window.
        
        Args:
            file_path: Path to the trace JSON file.
            
        Returns:
            The created trace window, or None if opening failed.
        """
        try:
            # Create trace window
            trace_window = TraceWindow(file_path)
            
            # Add to MDI area
            sub_window = self.mdi_area.addSubWindow(trace_window)
            sub_window.setWindowTitle(file_path.name)
            sub_window.resize(1000, 700)  # Set initial size for the subwindow
            sub_window.show()
            
            # Track window
            self.trace_windows.append(trace_window)
            
            return trace_window
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening Trace",
                f"Failed to open trace file:\n{file_path}\n\nError: {str(e)}"
            )
            return None
    
    def close_current_window(self) -> None:
        """Close the currently active MDI window."""
        active_window = self.mdi_area.activeSubWindow()
        if active_window:
            active_window.close()
    
    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Dapy Trace Viewer",
            "<h2>Dapy Trace Viewer</h2>"
            "<p>A visualization tool for distributed algorithm execution traces.</p>"
            "<p>Part of the Dapy framework for simulating distributed algorithms.</p>"
            "<p><a href='https://github.com/xdefago/dapy'>github.com/xdefago/dapy</a></p>"
        )
