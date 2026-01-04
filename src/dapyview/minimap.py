# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Minimap widget showing network topology."""

from enum import Enum
from typing import Dict, Optional, Set

import networkx as nx
from PySide6.QtCore import QPoint, QPointF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from dapy.core import Pid
from dapyview.trace_model import TraceModel


class Corner(Enum):
    """Corner positions for minimap placement."""
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


class MinimapWidget(QWidget):
    """Widget displaying network topology as a minimap overlay."""
    
    # Signals
    process_selected = Signal(Pid)
    edge_selected = Signal(Pid, Pid)  # sender, receiver
    corner_changed = Signal(Corner)  # Emitted when minimap is dragged to new corner
    
    def __init__(self, model: TraceModel, parent: Optional[QWidget] = None) -> None:
        """Initialize the minimap widget.
        
        Args:
            model: The trace model to visualize.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.model = model
        self.highlighted_processes: Set[Pid] = set()
        self.highlighted_edges: Set[tuple[Pid, Pid]] = set()
        
        # Current corner position
        self.current_corner = Corner.TOP_RIGHT
        
        # Dragging state
        self._dragging = False
        self._drag_start_pos: Optional[QPoint] = None
        
        # Layout
        self.node_positions: Dict[Pid, tuple[float, float]] = {}
        self._compute_layout()
        
        # Make widget semi-transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setWindowOpacity(0.85)  # 85% opacity
        
        # Compute required size based on content
        self._update_size()
        
        # Enable mouse tracking for drag cursor
        self.setMouseTracking(True)
    
    def _compute_layout(self) -> None:
        """Compute node positions using force-directed layout."""
        G = self.model.topology_graph
        
        if len(G.nodes()) == 0:
            return
        
        # Use spring layout for nice positioning
        pos = nx.spring_layout(G, seed=42)
        
        # Scale to widget coordinates
        self.node_positions = {
            pid: (x, y) for pid, (x, y) in pos.items()
        }
    
    def _update_size(self) -> None:
        """Update widget size based on number of nodes."""
        num_nodes = len(self.node_positions)
        # Scale size based on node count, with min/max bounds
        size = max(150, min(250, 100 + num_nodes * 25))
        self.setFixedSize(size, size)
    
    def highlight_process(self, pid: Pid) -> None:
        """Highlight a specific process.
        
        Args:
            pid: Process to highlight.
        """
        self.highlighted_processes = {pid}
        self.update()
    
    def highlight_edge(self, sender: Pid, receiver: Pid) -> None:
        """Highlight a specific edge.
        
        Args:
            sender: Source process.
            receiver: Destination process.
        """
        self.highlighted_edges = {(sender, receiver), (receiver, sender)}
        self.update()
    
    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.highlighted_processes.clear()
        self.highlighted_edges.clear()
        self.update()
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the minimap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent background
        painter.fillRect(self.rect(), QColor(240, 240, 240, 220))
        
        # Draw border
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # Draw drag handle indicator in corner
        self._draw_drag_handle(painter)
        
        # Draw edges
        self._draw_edges(painter)
        
        # Draw nodes
        self._draw_nodes(painter)
        
        # Draw synchrony model label at bottom
        self._draw_synchrony_label(painter)
    
    def _draw_synchrony_label(self, painter: QPainter) -> None:
        """Draw synchrony model label at the bottom of the minimap."""
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.setPen(QPen(QColor(60, 60, 60)))
        
        # Get synchrony model name
        sync_name = self.model.synchrony_model_name
        
        # Draw centered at bottom
        text_rect = painter.fontMetrics().boundingRect(sync_name)
        x = (self.width() - text_rect.width()) // 2
        y = self.height() - 8
        painter.drawText(x, y, sync_name)
    
    def _draw_drag_handle(self, painter: QPainter) -> None:
        """Draw a small drag handle in the corner to indicate draggability."""
        handle_size = 12
        margin = 4
        
        # Draw three small dots in corner
        painter.setBrush(QBrush(QColor(150, 150, 150)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i in range(3):
            for j in range(3 - i):
                x = self.width() - margin - handle_size + i * 4 + 2
                y = self.height() - margin - 2 - j * 4
                painter.drawEllipse(QPointF(x, y), 1.5, 1.5)
    
    def _draw_edges(self, painter: QPainter) -> None:
        """Draw edges between connected processes."""
        G = self.model.topology_graph
        
        for sender, receiver in G.edges():
            if sender in self.node_positions and receiver in self.node_positions:
                x1, y1 = self._scale_position(*self.node_positions[sender])
                x2, y2 = self._scale_position(*self.node_positions[receiver])
                
                # Check if highlighted
                if (sender, receiver) in self.highlighted_edges or (receiver, sender) in self.highlighted_edges:
                    pen = QPen(QColor(255, 165, 0), 3)
                else:
                    pen = QPen(QColor(120, 120, 120), 1)
                
                painter.setPen(pen)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def _draw_nodes(self, painter: QPainter) -> None:
        """Draw process nodes."""
        radius = 12
        
        for pid, (x, y) in self.node_positions.items():
            sx, sy = self._scale_position(x, y)
            
            # Determine color
            if pid in self.highlighted_processes:
                color = QColor(255, 165, 0)  # Orange
            else:
                color = QColor(70, 130, 200)  # Steel blue
            
            # Draw node
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(40, 40, 40), 2))
            painter.drawEllipse(QPointF(sx, sy), radius, radius)
            
            # Draw label inside node
            font = QFont("Arial", 9, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(Qt.GlobalColor.white))
            
            # Center the text
            label = str(pid.id) if hasattr(pid, 'id') else str(pid)
            text_rect = painter.fontMetrics().boundingRect(label)
            painter.drawText(
                int(sx - text_rect.width() / 2),
                int(sy + text_rect.height() / 4),
                label
            )
    
    def _scale_position(self, x: float, y: float) -> tuple[float, float]:
        """Scale normalized position (-1 to 1) to widget coordinates.
        
        Args:
            x: Normalized x coordinate.
            y: Normalized y coordinate.
            
        Returns:
            Scaled (x, y) coordinates.
        """
        margin = 30
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        # Convert from [-1, 1] to widget coordinates
        sx = margin + (x + 1) * width / 2
        sy = margin + (y + 1) * height / 2
        
        return sx, sy
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse clicks to select processes or edges, or start dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            click_x = event.position().x()
            click_y = event.position().y()
            
            # First check if clicking on a node
            for pid, (x, y) in self.node_positions.items():
                sx, sy = self._scale_position(x, y)
                dist_sq = (click_x - sx) ** 2 + (click_y - sy) ** 2
                if dist_sq <= 15 ** 2:
                    self.clear_highlights()
                    self.highlighted_processes = {pid}
                    self.process_selected.emit(pid)
                    self.update()
                    return
            
            # Check edges
            G = self.model.topology_graph
            for sender, receiver in G.edges():
                if sender in self.node_positions and receiver in self.node_positions:
                    x1, y1 = self._scale_position(*self.node_positions[sender])
                    x2, y2 = self._scale_position(*self.node_positions[receiver])
                    dist = self._point_to_segment_distance(click_x, click_y, x1, y1, x2, y2)
                    if dist < 8:
                        self.clear_highlights()
                        self.highlighted_edges = {(sender, receiver), (receiver, sender)}
                        self.edge_selected.emit(sender, receiver)
                        self.update()
                        return
            
            # If not clicking on node or edge, start dragging the entire minimap
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movement for dragging and cursor changes."""
        if self._dragging and self._drag_start_pos is not None:
            # Actually move the widget during drag
            parent = self.parentWidget()
            if parent:
                global_pos = event.globalPosition().toPoint()
                parent_pos = parent.mapFromGlobal(global_pos)
                
                # Move widget to follow mouse (offset by half size to center under cursor)
                new_x = parent_pos.x() - self.width() // 2
                new_y = parent_pos.y() - self.height() // 2
                
                # Constrain to parent bounds
                margin = 15
                new_x = max(margin, min(parent.width() - self.width() - margin, new_x))
                new_y = max(margin, min(parent.height() - self.height() - margin, new_y))
                
                self.move(new_x, new_y)
        else:
            # Update cursor based on position - entire widget is draggable
            self.setCursor(Qt.CursorShape.OpenHandCursor)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release to snap to nearest corner."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self._drag_start_pos = None
            
            # Snap to nearest corner
            parent = self.parentWidget()
            if parent:
                center_x = self.x() + self.width() // 2
                center_y = self.y() + self.height() // 2
                parent_center_x = parent.width() // 2
                parent_center_y = parent.height() // 2
                
                if center_x < parent_center_x:
                    if center_y < parent_center_y:
                        new_corner = Corner.TOP_LEFT
                    else:
                        new_corner = Corner.BOTTOM_LEFT
                else:
                    if center_y < parent_center_y:
                        new_corner = Corner.TOP_RIGHT
                    else:
                        new_corner = Corner.BOTTOM_RIGHT
                
                self.current_corner = new_corner
                self.corner_changed.emit(new_corner)
    
    def _point_to_segment_distance(self, px: float, py: float,
                                    x1: float, y1: float,
                                    x2: float, y2: float) -> float:
        """Calculate distance from point to line segment."""
        import math
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)
