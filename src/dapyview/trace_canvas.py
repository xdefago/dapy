# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Canvas widget for rendering time-space diagram."""

import math
from typing import Optional, Set, List, Tuple

from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont, QFontMetrics
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QToolTip, QSizePolicy

from dapy.core import Pid

from dapyview.trace_model import TraceModel, EventNode, MessageEdge

# ============================================================================
# Color Constants
# ============================================================================

# Background and basic UI
COLOR_BACKGROUND = QColor(50, 50, 50)
COLOR_PROCESS_LINE = QColor(180, 180, 180)
COLOR_PROCESS_LINE_SELECTED = QColor(255, 165, 0)
COLOR_PROCESS_LABEL = QColor(220, 220, 220)

# Events
COLOR_EVENT_SEND = QColor(0, 0, 0)  # Black
COLOR_EVENT_RECEIVE = QColor(0, 0, 0)  # Black
COLOR_EVENT_LOCAL = QColor(100, 100, 100)  # Gray
COLOR_EVENT_SELECTED = QColor(255, 0, 0)  # Red
COLOR_EVENT_PAST = QColor(100, 200, 255)  # Light blue
COLOR_EVENT_FUTURE = QColor(255, 180, 100)  # Light orange
COLOR_EVENT_HIGHLIGHTED = QColor(255, 165, 0)  # Orange
COLOR_EVENT_BORDER = QColor(0, 0, 0)  # Black border

# Messages/Lines
COLOR_MESSAGE_LINE = QColor(150, 150, 150)
COLOR_MESSAGE_LINE_SELECTED = QColor(255, 165, 0)  # Orange when selected
COLOR_MESSAGE_LABEL = QColor(200, 200, 200)

# Rulers
COLOR_RULER_LINE = QColor(200, 50, 50)  # Red
COLOR_RULER_LABEL = QColor(200, 50, 50)  # Red

# ============================================================================
# Font Constants
# ============================================================================

FONT_PROCESS_LABEL = QFont("Arial", 14, QFont.Weight.Bold)
FONT_MESSAGE_LABEL = QFont("Arial", 10)
FONT_RULER_LABEL = QFont("Arial", 9)

# ============================================================================
# Line width/size Constants
# ============================================================================

PEN_WIDTH_PROCESS_LINE = 2
PEN_WIDTH_PROCESS_LINE_SELECTED = 3
PEN_WIDTH_MESSAGE_LINE = 2
PEN_WIDTH_MESSAGE_LINE_SELECTED = 3
PEN_WIDTH_RULER_LINE = 2
PEN_WIDTH_EVENT_BORDER = 1
PEN_STYLE_RULER = Qt.PenStyle.DashLine

class TimeSpaceDiagram(QWidget):
    """Widget that draws the time-space diagram."""
    
    # Signals
    process_selected = Signal(Pid)
    event_selected = Signal(int)  # Event index
    message_selected = Signal(int)  # Message index
    
    def __init__(self, model: TraceModel) -> None:
        """Initialize the diagram widget.
        
        Args:
            model: The trace model to visualize.
        """
        super().__init__()
        
        self.model = model
        self.use_logical_time = True  # Default to logical time mode
        self.zoom_factor = 1.0
        
        # Highlighting - start with empty sets (no initial highlights)
        self.highlighted_processes: Set[Pid] = set()
        self.highlighted_events: Set[int] = set()
        self.highlighted_messages: Set[int] = set()
        self.selected_event: Optional[int] = None
        self.selected_message: Optional[int] = None
        self.selected_process: Optional[Pid] = None
        
        # Causal relations cache
        self._causal_past: Set[int] = set()
        self._causal_future: Set[int] = set()
        
        # Vertical rulers: list of (time, dragging) tuples
        self.rulers: List[float] = []
        self._dragging_ruler_idx: Optional[int] = None
        self._ruler_drag_offset: float = 0
        
        # Layout parameters
        self.process_spacing = 120  # Vertical spacing between processes
        self.time_scale = 63  # Pixels per time unit (calibrated so 100% zoom matches good visual spacing)
        self.margin_left = 100
        self.margin_top = 80
        self.margin_right = 100
        self.margin_bottom = 80
        self.event_radius = 7
        
        # Minimum content dimensions
        self._min_content_width = 800
        self._min_content_height = 600
        
        self.setMouseTracking(True)
        
        # Allow widget to expand
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), COLOR_BACKGROUND)
        self.setPalette(palette)
        
        # Calculate initial size
        self._update_size()
    
    def sizeHint(self) -> QSize:
        """Return the recommended size for the widget."""
        return QSize(self._min_content_width, self._min_content_height)
    
    def minimumSizeHint(self) -> QSize:
        """Return the minimum size for the widget."""
        return QSize(400, 300)
    
    def resizeEvent(self, event) -> None:
        """Handle resize events - update content width to match viewport."""
        super().resizeEvent(event)
        # When widget is resized (e.g., by scroll area), update our understanding
        # of available space. The diagram should at minimum fill the viewport.
        self.update()
    
    def _update_size(self) -> None:
        """Update widget size based on content."""
        processes = self.model.get_processes_sorted()
        
        if self.use_logical_time:
            min_time, max_time = self.model.get_logical_time_range()
        else:
            min_time, max_time = self.model.get_time_range()
        
        time_span = max_time - min_time
        content_width = int(time_span * self.time_scale * self.zoom_factor) + self.margin_left + self.margin_right
        content_height = len(processes) * self.process_spacing + self.margin_top + self.margin_bottom
        
        self._min_content_width = max(400, content_width)
        self._min_content_height = max(300, content_height)
        
        # Set minimum size to force scrollbars when content exceeds viewport
        self.setMinimumSize(self._min_content_width, self._min_content_height)
        self.updateGeometry()
        self.update()
    
    def set_time_mode(self, use_logical: bool) -> None:
        """Set whether to use logical time or physical time.
        
        Args:
            use_logical: True for Lamport clocks, False for timestamps.
        """
        self.use_logical_time = use_logical
        self._update_size()
        self.update()
    
    def set_zoom(self, factor: float) -> None:
        """Set zoom factor.
        
        Args:
            factor: Zoom factor (1.0 = 100%).
        """
        self.zoom_factor = factor
        self._update_size()
        self.update()
    
    def highlight_process(self, pid: Pid) -> None:
        """Highlight a specific process.
        
        Args:
            pid: Process to highlight.
        """
        self.highlighted_processes = {pid}
        self.selected_process = pid
        self.update()
    
    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.highlighted_processes.clear()
        self.highlighted_events.clear()
        self.highlighted_messages.clear()
        self._causal_past.clear()
        self._causal_future.clear()
        self.selected_event = None
        self.selected_message = None
        self.selected_process = None
        self.update()
    
    def _compute_causal_relations(self, event_idx: int) -> None:
        """Compute causal past and future for an event using vector clocks.
        
        Uses vector clocks to determine causality precisely.
        
        Args:
            event_idx: Index of the selected event.
        """
        self._causal_past.clear()
        self._causal_future.clear()
        
        if event_idx < 0 or event_idx >= len(self.model.events):
            return
        
        selected_event = self.model.events[event_idx]
        
        # Use vector clocks to determine causal past and future
        causal_past_events = self.model.get_causal_past(selected_event)
        causal_future_events = self.model.get_causal_future(selected_event)
        
        # Store indices
        self._causal_past = {evt.index for evt in causal_past_events}
        self._causal_future = {evt.index for evt in causal_future_events}
    
    def add_ruler(self, time: float) -> None:
        """Add a vertical ruler at the specified time.
        
        Args:
            time: Time position for the ruler.
        """
        self.rulers.append(time)
        self.update()
    
    def add_ruler_at_center(self) -> None:
        """Add a ruler at the center of the current view."""
        if self.use_logical_time:
            min_time, max_time = self.model.get_logical_time_range()
        else:
            min_time, max_time = self.model.get_time_range()
        center_time = (min_time + max_time) / 2
        self.add_ruler(center_time)
    
    def remove_ruler(self, index: int) -> None:
        """Remove a vertical ruler by index.
        
        Args:
            index: Index of the ruler to remove.
        """
        if 0 <= index < len(self.rulers):
            del self.rulers[index]
            self.update()
    
    def _find_ruler_at(self, x: float) -> Optional[int]:
        """Find ruler index at given x coordinate.
        
        Args:
            x: X coordinate in pixels.
            
        Returns:
            Ruler index if found within 8 pixels, None otherwise.
        """
        for i, time in enumerate(self.rulers):
            ruler_x = self._time_to_x(time)
            if abs(x - ruler_x) < 8:
                return i
        return None
    
    def _time_to_x(self, time: float) -> float:
        """Convert time to x coordinate.
        
        Args:
            time: Time value.
            
        Returns:
            X coordinate in pixels.
        """
        if self.use_logical_time:
            min_time, _ = self.model.get_logical_time_range()
        else:
            min_time, _ = self.model.get_time_range()
        
        return self.margin_left + (time - min_time) * self.time_scale * self.zoom_factor
    
    def _x_to_time(self, x: float) -> float:
        """Convert x coordinate to time.
        
        Args:
            x: X coordinate in pixels.
            
        Returns:
            Time value.
        """
        if self.use_logical_time:
            min_time, _ = self.model.get_logical_time_range()
        else:
            min_time, _ = self.model.get_time_range()
        
        return min_time + (x - self.margin_left) / (self.time_scale * self.zoom_factor)
    
    def _process_to_y(self, pid: Pid) -> float:
        """Convert process ID to y coordinate.
        
        Args:
            pid: Process identifier.
            
        Returns:
            Y coordinate in pixels.
        """
        processes = self.model.get_processes_sorted()
        try:
            index = processes.index(pid)
        except ValueError:
            index = 0
        return self.margin_top + index * self.process_spacing
    
    def _y_to_process(self, y: float) -> Optional[Pid]:
        """Convert y coordinate to process.
        
        Args:
            y: Y coordinate in pixels.
            
        Returns:
            Process ID or None if outside process lines.
        """
        processes = self.model.get_processes_sorted()
        if not processes:
            return None
        
        index = round((y - self.margin_top) / self.process_spacing)
        if 0 <= index < len(processes):
            return processes[index]
        return None
    
    def paintEvent(self, event) -> None:
        """Paint the time-space diagram."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), COLOR_BACKGROUND)
        
        # Draw rulers (behind everything)
        self._draw_rulers(painter)
        
        # Draw process lines
        self._draw_process_lines(painter)
        
        # Draw message arrows
        self._draw_messages(painter)
        
        # Draw events
        self._draw_events(painter)
    
    def _draw_process_lines(self, painter: QPainter) -> None:
        """Draw horizontal lines for each process."""
        processes = self.model.get_processes_sorted()
        
        if self.use_logical_time:
            min_time, max_time = self.model.get_logical_time_range()
        else:
            min_time, max_time = self.model.get_time_range()
        
        # Extend process lines to include all events with proper margins
        x_start = self._time_to_x(min_time) - 10
        x_end = self._time_to_x(max_time) + 10
        
        for pid in processes:
            y = self._process_to_y(pid)
            
            # Highlight if selected
            if pid in self.highlighted_processes or pid == self.selected_process:
                pen = QPen(COLOR_PROCESS_LINE_SELECTED, PEN_WIDTH_PROCESS_LINE_SELECTED)
            else:
                pen = QPen(COLOR_PROCESS_LINE, PEN_WIDTH_PROCESS_LINE)
            
            painter.setPen(pen)
            painter.drawLine(int(x_start), int(y), int(x_end), int(y))
            
            # Draw process label - positioned closer to line start
            painter.setFont(FONT_PROCESS_LABEL)
            painter.setPen(QPen(COLOR_PROCESS_LABEL))
            
            # Position label just to the left of the line start
            label_x = int(x_start - 55)
            painter.drawText(label_x, int(y + 5), str(pid))
    
    def _draw_events(self, painter: QPainter) -> None:
        """Draw event dots."""
        for event in self.model.events:
            # Use end_time for event position (when event occurs/is processed)
            if self.use_logical_time:
                time = int(event.logical_time)
            else:
                time = event.end_time
            
            x = self._time_to_x(time)
            y = self._process_to_y(event.pid)
            
            # Determine color based on selection/highlighting
            if event.index == self.selected_event:
                color = COLOR_EVENT_SELECTED
                radius = 10
            elif event.index in self._causal_past:
                color = COLOR_EVENT_PAST
                radius = 9
            elif event.index in self._causal_future:
                color = COLOR_EVENT_FUTURE
                radius = 9
            elif event.index in self.highlighted_events:
                color = COLOR_EVENT_HIGHLIGHTED
                radius = 8
            else:
                # Default colors for concurrent or non-highlighted events
                if event.is_receive:
                    color = COLOR_EVENT_RECEIVE    
                elif event.is_send:
                    color = COLOR_EVENT_SEND
                else:
                    color = COLOR_EVENT_LOCAL
                radius = self.event_radius
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(COLOR_EVENT_BORDER, PEN_WIDTH_EVENT_BORDER))
            painter.drawEllipse(QPointF(x, y), radius, radius)
    
    def _draw_messages(self, painter: QPainter) -> None:
        """Draw message transmission arrows."""
        for idx, msg in enumerate(self.model.messages):
            self._draw_message_arrow(painter, msg, idx)
    
    def _draw_message_arrow(self, painter: QPainter, msg: MessageEdge, index: int) -> None:
        """Draw an arrow for a message."""
        # Use logical or physical time based on mode
        if self.use_logical_time:
            send_time = int(msg.send_logical_time)
            recv_time = int(msg.receive_logical_time)
        else:
            send_time = msg.send_time
            recv_time = msg.receive_time
        
        x1 = self._time_to_x(send_time)
        y1 = self._process_to_y(msg.sender)
        x2 = self._time_to_x(recv_time)
        y2 = self._process_to_y(msg.receiver)
        
        # Highlight if selected
        if index == self.selected_message or index in self.highlighted_messages:
            pen = QPen(COLOR_MESSAGE_LINE_SELECTED, PEN_WIDTH_MESSAGE_LINE_SELECTED)
        else:
            pen = QPen(COLOR_MESSAGE_LINE, PEN_WIDTH_MESSAGE_LINE)
        
        painter.setPen(pen)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw arrowhead
        self._draw_arrowhead(painter, QPointF(x2, y2), QPointF(x1, y1), pen.color())
        
        # Draw message label parallel to the line
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Calculate angle of the line
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        angle_deg = math.degrees(angle)
        
        # Adjust angle so text is always readable (not upside down)
        if angle_deg > 90:
            angle_deg -= 180
        elif angle_deg < -90:
            angle_deg += 180
        
        painter.setFont(FONT_MESSAGE_LABEL)
        painter.setPen(QPen(COLOR_MESSAGE_LABEL))
        
        # Save painter state, translate and rotate for text
        painter.save()
        painter.translate(mid_x, mid_y)
        painter.rotate(angle_deg)
        
        # Draw text slightly above the line
        fm = QFontMetrics(FONT_MESSAGE_LABEL)
        text_width = fm.horizontalAdvance(msg.message_type)
        painter.drawText(int(-text_width / 2), -8, msg.message_type)
        
        painter.restore()
    
    def _draw_arrowhead(self, painter: QPainter, tip: QPointF, from_point: QPointF, color: QColor) -> None:
        """Draw an arrowhead at the tip of a line."""
        arrow_size = 10
        
        dx = tip.x() - from_point.x()
        dy = tip.y() - from_point.y()
        angle = math.atan2(dy, dx)
        
        p1 = QPointF(
            tip.x() - arrow_size * math.cos(angle - math.pi / 6),
            tip.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        p2 = QPointF(
            tip.x() - arrow_size * math.cos(angle + math.pi / 6),
            tip.y() - arrow_size * math.sin(angle + math.pi / 6)
        )
        
        path = QPainterPath()
        path.moveTo(tip)
        path.lineTo(p1)
        path.lineTo(p2)
        path.closeSubpath()
        
        painter.fillPath(path, color)
    
    def _draw_rulers(self, painter: QPainter) -> None:
        """Draw vertical rulers."""
        pen = QPen(COLOR_RULER_LINE, PEN_WIDTH_RULER_LINE, PEN_STYLE_RULER)
        painter.setPen(pen)
        
        for time in self.rulers:
            x = self._time_to_x(time)
            painter.drawLine(int(x), 0, int(x), self.height())
            
            # Draw time label at top
            painter.setFont(FONT_RULER_LABEL)
            painter.setPen(QPen(COLOR_RULER_LABEL))
            if self.use_logical_time:
                label = f"t={int(time)}"
            else:
                label = f"t={time:.3f}s"
            painter.drawText(int(x + 3), 15, label)
            painter.setPen(pen)
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events for selection and ruler dragging."""
        x = event.position().x()
        y = event.position().y()
        
        # Right-click to delete rulers
        if event.button() == Qt.MouseButton.RightButton:
            ruler_idx = self._find_ruler_at(x)
            if ruler_idx is not None:
                self.remove_ruler(ruler_idx)
            return
        
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        # Check if clicked on a ruler for dragging
        ruler_idx = self._find_ruler_at(x)
        if ruler_idx is not None:
            self._dragging_ruler_idx = ruler_idx
            self._ruler_drag_offset = x - self._time_to_x(self.rulers[ruler_idx])
            return
        
        time = self._x_to_time(x)
        
        # Check if clicked on an event
        clicked_event = self._find_event_at(x, y)
        if clicked_event is not None:
            self.clear_highlights()
            self.selected_event = clicked_event.index
            # Compute causal past and future
            self._compute_causal_relations(clicked_event.index)
            self.event_selected.emit(clicked_event.index)
            self.update()
            return
        
        # Check if clicked on a message line
        clicked_msg_idx = self._find_message_at(x, y)
        if clicked_msg_idx is not None:
            self.clear_highlights()
            self.selected_message = clicked_msg_idx
            self.highlighted_messages.add(clicked_msg_idx)
            self.message_selected.emit(clicked_msg_idx)
            self.update()
            return
        
        # Check if clicked on a process line
        process = self._y_to_process(y)
        if process is not None:
            # Check if x is within the process line range
            if self.use_logical_time:
                min_time, max_time = self.model.get_logical_time_range()
            else:
                min_time, max_time = self.model.get_time_range()
            
            x_start = self._time_to_x(min_time) - 10
            x_end = self._time_to_x(max_time) + 10
            
            if x_start <= x <= x_end:
                proc_y = self._process_to_y(process)
                if abs(y - proc_y) < 15:  # Within 15 pixels of line
                    self.clear_highlights()
                    self.highlighted_processes = {process}
                    self.selected_process = process
                    self.process_selected.emit(process)
                    self.update()
                    return
        
        # Click on empty area - clear highlights
        self.clear_highlights()
    
    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_ruler_idx = None
    
    def _find_event_at(self, x: float, y: float) -> Optional[EventNode]:
        """Find an event at the given pixel coordinates."""
        for event in self.model.events:
            if self.use_logical_time:
                time = int(event.logical_time)
            else:
                time = event.end_time
            
            ex = self._time_to_x(time)
            ey = self._process_to_y(event.pid)
            
            dist_sq = (x - ex) ** 2 + (y - ey) ** 2
            if dist_sq <= (self.event_radius + 5) ** 2:
                return event
        return None
    
    def _find_message_at(self, x: float, y: float) -> Optional[int]:
        """Find a message at the given pixel coordinates."""
        for idx, msg in enumerate(self.model.messages):
            if self.use_logical_time:
                send_time = int(msg.send_logical_time)
                recv_time = int(msg.receive_logical_time)
            else:
                send_time = msg.send_time
                recv_time = msg.receive_time
            
            x1 = self._time_to_x(send_time)
            y1 = self._process_to_y(msg.sender)
            x2 = self._time_to_x(recv_time)
            y2 = self._process_to_y(msg.receiver)
            
            # Check distance from point to line segment
            dist = self._point_to_segment_distance(x, y, x1, y1, x2, y2)
            if dist < 8:  # Within 8 pixels of line
                return idx
        return None
    
    def _point_to_segment_distance(self, px: float, py: float, 
                                    x1: float, y1: float, 
                                    x2: float, y2: float) -> float:
        """Calculate distance from point to line segment."""
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for tooltips and ruler dragging."""
        x = event.position().x()
        y = event.position().y()
        
        # Handle ruler dragging
        if self._dragging_ruler_idx is not None:
            new_time = self._x_to_time(x - self._ruler_drag_offset)
            self.rulers[self._dragging_ruler_idx] = new_time
            self.update()
            return
        
        # Change cursor when hovering over a ruler
        ruler_idx = self._find_ruler_at(x)
        if ruler_idx is not None:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Check for event under cursor
        evt = self._find_event_at(x, y)
        if evt is not None:
            tooltip = f"Event: {evt.event_type}\nProcess: {evt.pid}\n"
            if self.use_logical_time:
                tooltip += f"Logical Time: {evt.logical_time}"
            else:
                tooltip += f"Time: {evt.time:.4f}s - {evt.end_time:.4f}s"
            QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
            return
        
        # Check for message under cursor
        msg_idx = self._find_message_at(x, y)
        if msg_idx is not None:
            msg = self.model.messages[msg_idx]
            tooltip = f"Message: {msg.message_type}\n"
            tooltip += f"From: {msg.sender} → {msg.receiver}\n"
            if self.use_logical_time:
                tooltip += f"Logical Time: {msg.send_logical_time} → {msg.receive_logical_time}"
            else:
                tooltip += f"Time: {msg.send_time:.4f}s → {msg.receive_time:.4f}s"
            QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
            return
        
        # Check for process line
        process = self._y_to_process(y)
        if process is not None:
            proc_y = self._process_to_y(process)
            if abs(y - proc_y) < 15:
                tooltip = f"Process: {process}"
                QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
                return
        
        QToolTip.hideText()


class TraceCanvas(QScrollArea):
    """Scrollable canvas for the time-space diagram."""
    
    # Forward signals
    process_selected = Signal(Pid)
    event_selected = Signal(int)
    message_selected = Signal(int)
    ruler_added = Signal(float)
    
    def __init__(self, model: TraceModel) -> None:
        """Initialize the trace canvas.
        
        Args:
            model: The trace model to visualize.
        """
        super().__init__()
        
        self.diagram = TimeSpaceDiagram(model)
        self.setWidget(self.diagram)
        
        # setWidgetResizable(True) tells the scroll area to resize the widget
        # to fill available space when content is smaller than viewport.
        # When content is larger, scrollbars appear automatically.
        self.setWidgetResizable(True)
        
        # Ensure scrollbars appear when content exceeds viewport
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set size policy to make the scroll area expand to fill available space
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Set dark background for scroll area and its viewport using stylesheet
        # This ensures consistent appearance across platforms
        self.setStyleSheet("""
            QScrollArea {
                background-color: rgb(50, 50, 50);
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: rgb(50, 50, 50);
            }
            QScrollBar:horizontal, QScrollBar:vertical {
                background-color: rgb(60, 60, 60);
            }
        """)
        
        # Also set the viewport background directly
        self.viewport().setAutoFillBackground(True)
        viewport_palette = self.viewport().palette()
        viewport_palette.setColor(self.viewport().backgroundRole(), QColor(50, 50, 50))
        self.viewport().setPalette(viewport_palette)
        
        # Forward signals
        self.diagram.process_selected.connect(self.process_selected.emit)
        self.diagram.event_selected.connect(self.event_selected.emit)
        self.diagram.message_selected.connect(self.message_selected.emit)
    
    def set_time_mode(self, use_logical: bool) -> None:
        """Set time mode."""
        self.diagram.set_time_mode(use_logical)
    
    def set_zoom(self, factor: float) -> None:
        """Set zoom factor."""
        self.diagram.set_zoom(factor)
    
    def highlight_process(self, pid: Pid) -> None:
        """Highlight a process."""
        self.diagram.highlight_process(pid)
    
    def add_ruler(self) -> None:
        """Add a ruler at the center of the view."""
        self.diagram.add_ruler_at_center()
    
    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.diagram.clear_highlights()
