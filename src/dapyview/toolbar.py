# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Toolbar widget for trace viewer controls."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QToolBar, QLabel, QSlider, QPushButton, QCheckBox,
)
from PySide6.QtCore import Qt


class TraceToolbar(QToolBar):
    """Toolbar with trace viewer controls."""
    
    # Signals
    time_mode_changed = Signal(bool)  # True = logical, False = physical
    zoom_changed = Signal(float)  # Zoom factor
    ruler_requested = Signal()  # User wants to add a ruler
    
    def __init__(self) -> None:
        """Initialize the toolbar."""
        super().__init__()
        
        self.setMovable(False)
        
        # Time mode toggle
        self.addWidget(QLabel("Time Mode:"))
        self.time_mode_checkbox = QCheckBox("Logical Time")
        self.time_mode_checkbox.setChecked(False)
        self.time_mode_checkbox.stateChanged.connect(self._on_time_mode_changed)
        self.addWidget(self.time_mode_checkbox)
        
        self.addSeparator()
        
        # Zoom controls
        self.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10%
        self.zoom_slider.setMaximum(500)  # 500%
        self.zoom_slider.setValue(100)  # 100%
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.setTickInterval(50)
        self.zoom_slider.setMaximumWidth(200)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        self.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.addWidget(self.zoom_label)
        
        self.addSeparator()
        
        # Ruler controls
        self.ruler_button = QPushButton("Add Ruler")
        self.ruler_button.clicked.connect(self.ruler_requested.emit)
        self.addWidget(self.ruler_button)
    
    def _on_time_mode_changed(self, state: int) -> None:
        """Handle time mode checkbox change."""
        use_logical = (state == Qt.CheckState.Checked.value)
        self.time_mode_changed.emit(use_logical)
    
    def _on_zoom_changed(self, value: int) -> None:
        """Handle zoom slider change."""
        zoom_factor = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.zoom_changed.emit(zoom_factor)
