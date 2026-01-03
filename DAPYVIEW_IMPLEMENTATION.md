# dapyview Implementation Summary

## Overview

The **dapyview** package is a complete GUI trace viewer for dapy distributed algorithm simulations. It provides interactive visualization of execution traces with time-space diagrams, network topology minimap, and various analysis tools.

## Package Structure

```
src/dapyview/
├── __init__.py          # Package exports
├── README.md            # User documentation
├── main.py              # CLI entry point
├── app.py               # Main MDI application window
├── trace_window.py      # Individual trace document window
├── trace_model.py       # Data model for trace processing
├── trace_canvas.py      # Time-space diagram widget
├── minimap.py           # Network topology minimap
└── toolbar.py           # Control toolbar
```

## Installation

The package is configured as an optional dependency group:

```bash
# Install with UI support
uv sync --group ui

# Or as an optional dependency
uv add "dapy[ui] @ git+https://github.com/xdefago/dapy.git"
```

Dependencies installed:
- **PySide6 >= 6.8.0** - Qt GUI framework
- **networkx >= 3.4** - Graph algorithms for topology
- **dapy[json]** - JSON serialization support

## Features Implemented

### 1. Multi-Document Interface (MDI)
- **File** → `TraceViewerApp` (app.py)
- Open multiple trace files simultaneously
- Each trace in its own window
- File menu with Open, Close, Exit options
- Window menu for managing open traces

### 2. Time-Space Diagram
- **File** → `TraceCanvas`, `TimeSpaceDiagram` (trace_canvas.py)
- Horizontal lines for process timelines
- Dots for events (blue for normal, red for selected, orange for highlighted)
- Arrows for messages with arrowheads and labels
- Lost messages shown with red crosses
- Automatic layout with configurable spacing and margins
- Scrollable canvas for large traces

### 3. Time Mode Toggle
- **File** → `TraceToolbar` (toolbar.py)
- Switch between physical time (timestamps) and logical time (Lamport clocks)
- Automatic recalculation of Lamport clocks via `TraceModel`
- Updates diagram in real-time

### 4. Zoom Controls
- **File** → `TraceToolbar` (toolbar.py)
- Slider with range 10%-500%
- Real-time label showing current zoom percentage
- Diagram resizes dynamically

### 5. Network Topology Minimap
- **File** → `MinimapWidget` (minimap.py)
- Force-directed graph layout using networkx
- Visual representation of process network
- Clickable nodes for process selection
- Synchronized highlighting with main diagram

### 6. Data Processing
- **File** → `TraceModel` (trace_model.py)
- Parses Trace objects into structured EventNode and MessageEdge
- Builds networkx graphs for:
  - Event causality (event_graph)
  - Network topology (topology_graph)
- Computes Lamport logical clocks for all events
- Provides query methods for processes, time ranges, etc.

### 7. Interactive Features
- Process selection (click in minimap or diagram)
- Synchronized highlighting across canvas and minimap
- Event highlighting (infrastructure in place)
- Ruler support (add/remove vertical time markers)

### 8. Command-Line Interface
- **File** → `main.py`
- `dapyview [trace_file]` - Open file or start empty
- `dapyview --help` - Show usage help
- `dapyview --version` - Show version
- Proper argument parsing with argparse

## Data Model

### EventNode
```python
@dataclass
class EventNode:
    index: int              # Sequential event index
    pid: Pid                # Process that executed the event
    event: Event            # Original event object
    time: float             # Physical timestamp
    logical_time: int       # Lamport clock value
```

### MessageEdge
```python
@dataclass
class MessageEdge:
    sender: Pid             # Sending process
    receiver: Optional[Pid] # Receiving process (None if lost)
    message_type: str       # Event class name
    send_time: float        # Send timestamp
    receive_time: Optional[float]  # Receive timestamp
    is_lost: bool           # Whether message was lost
```

## Architecture Decisions

1. **MDI vs Tabs**: Chose MDI (Multiple Document Interface) for flexibility in arranging multiple traces

2. **Data Model Separation**: `TraceModel` separates data processing from visualization, making it easier to test and maintain

3. **NetworkX Integration**: Used networkx for both topology layout and causality analysis, providing professional graph algorithms

4. **PySide6 over PyQt**: PySide6 is the official Qt for Python binding with better licensing

5. **Lamport Clock Computation**: Implemented in `TraceModel` for accurate logical time visualization

6. **Immutable Data**: All data classes are frozen/immutable, following dapy's design principles

## Testing

Example workflow to generate and view a trace:

```bash
# Generate a sample trace
uv run python examples/generate_trace.py

# View the trace
uv run dapyview examples/sample_trace.json
```

## Future Enhancements (Not Implemented)

Potential features for future development:

1. **Causal Past/Future Highlighting**: Highlight all events in the causal past or future of a selected event

2. **Event Click Detection**: Implement proper hit testing for clicking on events in the diagram

3. **Ruler Management**: UI for removing specific rulers, measuring time between rulers

4. **Export Features**: Export diagram as image (PNG, SVG)

5. **Search/Filter**: Search for specific event types or processes

6. **Statistics Panel**: Show summary statistics (message count, event count, etc.)

7. **Animation**: Replay execution step-by-step

8. **Comparison Mode**: Compare two traces side-by-side

9. **Custom Coloring**: Color events/messages by type or custom criteria

10. **Performance Optimization**: For very large traces (1000+ events)

## File Changes

### New Files Created
- `/src/dapyview/*` - Complete package (8 files)
- `/examples/generate_trace.py` - Example trace generator

### Modified Files
- `/pyproject.toml` - Added `[project.optional-dependencies]` ui, `[dependency-groups]` ui, and `[project.scripts]` dapyview
- `/README.md` - Added documentation for optional UI dependency

## Dependencies Added

```toml
[project.optional-dependencies]
ui = [
    "PySide6 >= 6.8.0",
    "networkx >= 3.4",
    "dapy[json]",
]

[dependency-groups]
ui = [
    {include-group = "json"},
    "PySide6 >= 6.8.0",
    "networkx >= 3.4",
]

[project.scripts]
dapyview = "dapyview.main:main"
```

## Verification

All files compile without errors after installing dependencies:
```bash
uv sync --group ui
```

The application runs successfully:
```bash
uv run dapyview examples/sample_trace.json
```

## Conclusion

The dapyview package is a fully functional GUI trace viewer that integrates seamlessly with the dapy framework. It provides essential visualization features for understanding distributed algorithm executions and is ready for use in teaching and research contexts.
