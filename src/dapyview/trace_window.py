# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Trace window displaying time-space diagram visualization."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSizePolicy, QFileDialog, QMessageBox

from dapy.sim import Trace

# Import common algorithm modules so classifiedjson can deserialize them
# Users may need to import their custom algorithm modules before loading traces
try:
    import dapy.algo.learn  # For LearnGraphAlgorithm traces
except ImportError:
    pass  # Module might not be available

from dapyview.trace_model import TraceModel
from dapyview.trace_canvas import TraceCanvas
from dapyview.minimap import MinimapWidget, Corner
from dapyview.toolbar import TraceToolbar


class TraceWindow(QMainWindow):
    """Native window displaying a single trace visualization."""
    
    # Class variable to track all open windows
    _open_windows: list['TraceWindow'] = []
    
    def __init__(self, trace_file: Path) -> None:
        """Initialize trace window.
        
        Args:
            trace_file: Path to the trace JSON file.
        """
        super().__init__()
        
        self.trace_file = trace_file
        
        # Load trace
        with open(trace_file, 'r') as f:
            trace_json = f.read()
        self.trace = Trace.load_json(trace_json)
        
        # Create trace model
        self.model = TraceModel(self.trace)
        
        # Set window title
        self.setWindowTitle(f"{trace_file.name} - Dapy Trace Viewer")
        
        # Set up menus
        self._create_menus()
        
        # Set up UI
        self._setup_ui()
        
        # Set initial window size
        self.resize(1000, 700)
        
        # Track this window
        TraceWindow._open_windows.append(self)
    
    def _create_menus(self) -> None:
        """Create window menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Trace...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_trace_dialog)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("&Close Window", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self._quit_app)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _open_trace_dialog(self) -> None:
        """Show file dialog to open a trace file in a new window."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Trace File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                new_window = TraceWindow(Path(file_path))
                new_window.show()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Opening Trace",
                    f"Failed to open trace file:\n{file_path}\n\nError: {str(e)}"
                )
    
    def _quit_app(self) -> None:
        """Quit the application by closing all windows."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Dapy Trace Viewer",
            "<h2>Dapy Trace Viewer</h2>"
            "<p>A visualization tool for distributed algorithm execution traces.</p>"
            "<p>Part of the Dapy framework for simulating distributed algorithms.</p>"
            "<p><a href='https://github.com/xdefago/dapy'>github.com/xdefago/dapy</a></p>"
        )
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Create central widget for QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add toolbar
        self.toolbar = TraceToolbar()
        self.toolbar.set_algorithm_name(self.model.algorithm_name)
        layout.addWidget(self.toolbar)
        
        # Main trace canvas (fills remaining space)
        self.canvas = TraceCanvas(self.model)
        layout.addWidget(self.canvas, stretch=1)
        
        # Create minimap as overlay (child of viewport for proper positioning)
        self.minimap = MinimapWidget(self.model, self.canvas.viewport())
        self.minimap.raise_()  # Ensure it's on top
        
        # Position minimap after layout is complete (use timer to ensure viewport has size)
        QTimer.singleShot(0, self._position_minimap)
        
        # Connect signals
        self.toolbar.time_mode_changed.connect(self.canvas.set_time_mode)
        self.toolbar.zoom_changed.connect(self.canvas.set_zoom)
        self.toolbar.ruler_requested.connect(self._add_ruler)
        
        # Canvas <-> Minimap process highlighting
        self.canvas.process_selected.connect(self.minimap.highlight_process)
        self.minimap.process_selected.connect(self.canvas.highlight_process)
        
        # Edge selection in minimap highlights related messages
        self.minimap.edge_selected.connect(self._on_edge_selected)
        
        # Minimap corner dragging
        self.minimap.corner_changed.connect(self._on_minimap_corner_changed)
    
    def _position_minimap(self) -> None:
        """Position the minimap based on current corner setting."""
        margin = 15
        
        # Get the viewport dimensions
        viewport = self.canvas.viewport()
        vp_width = viewport.width()
        vp_height = viewport.height()
        
        # Ensure we have valid dimensions
        if vp_width < 100 or vp_height < 100:
            # Viewport not ready yet, schedule another attempt
            QTimer.singleShot(50, self._position_minimap)
            return
        
        corner = self.minimap.current_corner
        mm_width = self.minimap.width()
        mm_height = self.minimap.height()
        
        if corner == Corner.TOP_LEFT:
            x = margin
            y = margin
        elif corner == Corner.TOP_RIGHT:
            x = vp_width - mm_width - margin
            y = margin
        elif corner == Corner.BOTTOM_LEFT:
            x = margin
            y = vp_height - mm_height - margin
        else:  # BOTTOM_RIGHT
            x = vp_width - mm_width - margin
            y = vp_height - mm_height - margin
        
        self.minimap.move(x, y)
    
    def _on_minimap_corner_changed(self, corner: Corner) -> None:
        """Handle minimap being dragged to a new corner."""
        self._position_minimap()
    
    def _add_ruler(self) -> None:
        """Add a ruler to the canvas."""
        self.canvas.add_ruler()
    
    def _on_edge_selected(self, sender, receiver) -> None:
        """Handle edge selection in minimap by highlighting related messages."""
        # Highlight all messages between these two processes
        self.canvas.diagram.clear_highlights()
        for idx, msg in enumerate(self.model.messages):
            if (msg.sender == sender and msg.receiver == receiver) or \
               (msg.sender == receiver and msg.receiver == sender):
                self.canvas.diagram.highlighted_messages.add(idx)
        self.canvas.diagram.update()
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize to reposition minimap overlay."""
        super().resizeEvent(event)
        self._position_minimap()
    
    def closeEvent(self, event) -> None:
        """Handle window close to track open windows."""
        if self in TraceWindow._open_windows:
            TraceWindow._open_windows.remove(self)
        super().closeEvent(event)
