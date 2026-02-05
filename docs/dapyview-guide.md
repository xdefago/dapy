---
layout: default
title: User Guide
parent: Dapyview
nav_order: 2
---

# Dapyview User Guide

**Dapyview** is a graphical trace viewer for visualizing execution traces of distributed algorithms created with the Dapy framework. It displays time-space diagrams showing process timelines, message exchanges, and causality relationships.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Complete Workflow](#complete-workflow)
- [User Interface](#user-interface)
- [Features and Functionality](#features-and-functionality)
- [Keyboard and Mouse Controls](#keyboard-and-mouse-controls)
- [Color Scheme](#color-scheme)
- [Tips and Best Practices](#tips-and-best-practices)

---

## Quick Start

**Prerequisites**: Dapy installed from GitHub (includes dapyview):

```bash
pip install "git+https://github.com/xdefago/dapy.git"
```

**Or** download standalone dapyview from [GitHub Releases](https://github.com/xdefago/dapy/releases) (no Python needed).

---

1. **Run your algorithm and save a trace:**
   ```python
   from dapy.sim import Simulator
   # ... create your system and algorithm ...
   sim = Simulator.from_system(system, algorithm)
   sim.start()
   sim.run_to_completion()
   sim.save_trace("my_trace.pkl")  # Pickle format (default)
   ```

2. **Launch the viewer:**
   ```bash
   dapyview my_trace.pkl
   ```

---

## Installation

### Prerequisites

- Python 3.11 or higher

### Installing Dapy (includes Dapyview)

The recommended way is to use the [template repository](https://github.com/xdefago/dapy-template):

```bash
git clone https://github.com/xdefago/dapy-template
cd dapy-template
uv sync
```

Alternatively, install directly via pip:
```bash
pip install "git+https://github.com/xdefago/dapy.git"
```

**Using uv (recommended):**
```bash
uv add "dapy @ git+https://github.com/xdefago/dapy.git"
```

This installs both the dapy framework and dapyview GUI viewer. The `dapyview` command will be available in your environment.

**For developers** modifying dapy itself:
```bash
git clone https://github.com/xdefago/dapy.git
cd dapy
pip install --editable .
```

**For development:**
```bash
git clone https://github.com/xdefago/dapy.git
cd dapy
uv sync --all-groups
```

### Verifying Installation

After installation, verify that `dapyview` is available:
```bash
dapyview --version
```

---

## Complete Workflow

This section walks through the entire process from writing an algorithm to visualizing its execution.

### Step 1: Write Your Distributed Algorithm

Create a Python file with your algorithm. Use the template structure:

```python
# my_algorithm.py
from dataclasses import dataclass
from typing import Sequence
from dapy.core import Algorithm, Event, Message, Pid, Signal, State, System, Ring, Asynchronous

@dataclass(frozen=True)
class MyState(State):
    """State for each process."""
    counter: int = 0
    received_from: set[Pid] = field(default_factory=set)

@dataclass(frozen=True)
class MyMessage(Message):
    """Message sent between processes."""
    value: int = 0

@dataclass(frozen=True)
class MyAlgorithm(Algorithm[MyState]):
    """A simple algorithm that broadcasts a value."""
    
    algorithm_name: str = "Broadcast Example"
    
    def initial_state(self, pid: Pid) -> MyState:
        return MyState(pid=pid)
    
    def on_event(self, old_state: MyState, event: Event) -> tuple[MyState, Sequence[Event]]:
        if isinstance(event, MyMessage):
            # Process received message
            new_state = old_state.cloned_with(
                counter=old_state.counter + event.value,
                received_from=old_state.received_from | {event.sender}
            )
            # Forward to neighbors
            messages = [
                MyMessage(target=neighbor, sender=old_state.pid, value=event.value)
                for neighbor in self.system.topology.neighbors(old_state.pid)
                if neighbor not in new_state.received_from
            ]
            return new_state, messages
        return old_state, []
```

### Step 2: Create and Run a Simulation

Create an execution script that runs your algorithm and saves a trace:

```python
# run_simulation.py
from dapy.core import System, Ring, Asynchronous
from dapy.sim import Simulator, Settings
from my_algorithm import MyAlgorithm, MyMessage

# Create system topology
system = System(
    topology=Ring.of_size(5),  # 5 processes in a ring
    synchrony=Asynchronous()
)

# Create algorithm instance
algorithm = MyAlgorithm(system)

# Create simulator with custom settings
settings = Settings(
    max_steps=100,  # Maximum simulation steps
    time_scale=1.0   # Time scaling factor
)
sim = Simulator.from_system(system, algorithm, settings=settings)

# Initialize and start simulation
sim.start()

# Schedule initial event (process p1 initiates)
from dapy.core import Pid
initial_msg = MyMessage(target=Pid(1), sender=Pid(1), value=42)
sim.schedule(initial_msg, delay=0.0)

# Run to completion
sim.run_to_completion()

# Save trace for visualization (pickle format is default - compact and fast)
sim.save_trace("broadcast_trace.pkl")
print("Trace saved to broadcast_trace.pkl")
```

### Step 3: Execute Your Simulation

Run the simulation to generate a trace file:

```bash
uv run python run_simulation.py
# or: python run_simulation.py
```

This creates `broadcast_trace.pkl` containing the execution trace.

### Step 4: Visualize with Dapyview

Open the trace in the viewer:

```bash
dapyview broadcast_trace.pkl
# Or open file selector:
dapyview
```

The viewer window will display your algorithm's execution as a time-space diagram.

---

## User Interface

### Main Window Layout

The dapyview window consists of:

1. **Menu Bar** (top)
   - **File**: Open trace, Close window, Quit
   - **Help**: About dialog

2. **Toolbar** (below menu)
   - **Time Mode**: Toggle between physical time and logical time
   - **Zoom**: Adjust horizontal scaling (10%-500%)
   - **Add Ruler**: Insert vertical measurement rulers
   - **Algorithm Name**: Displays the algorithm name from the trace

3. **Main Canvas** (center)
   - Displays the time-space diagram
   - Horizontal axis: time (physical or logical)
   - Vertical axis: processes
   - Process timelines as horizontal lines
   - Events as colored circles on timelines
   - Messages as diagonal arrows between processes

4. **Minimap** (top-right corner)
   - Small overview of entire trace
   - Shows current viewport position
   - Click to navigate to different parts of the trace

### Time-Space Diagram

The main visualization shows:

- **Horizontal Process Lines**: Each process has a horizontal timeline
- **Process Labels**: Process IDs (p1, p2, p3...) on the left
- **Event Markers**: Circles on timelines representing events
- **Message Arrows**: Lines connecting send and receive events
- **Message Labels**: Hover over arrows to see message details

---

## Features and Functionality

### Time Modes

**Physical Time Mode** (default):
- Events positioned according to real simulation time
- Shows actual timing of events in the simulation
- Time axis shows seconds (or simulation time units)

**Logical Time Mode**:
- Events positioned by Lamport logical clock values
- Shows causality order independent of physical timing
- Gaps in logical time indicate concurrent events
- Time axis shows Lamport clock values (1, 2, 3...)

Toggle between modes using the **"Logical Time"** checkbox in the toolbar.

### Zoom Control

Adjust the horizontal zoom level to see more or less detail:

- **Slider**: Drag to adjust zoom (10% to 500%)
- **Mouse Wheel**: Scroll up/down to zoom in/out
- **Display**: Current zoom percentage shown next to slider

Zooming affects only the horizontal (time) axis, not vertical (process) spacing.

### Causality Highlighting

**Click on any event** to highlight its causal relationships:

- **Red circle**: The selected event
- **Light blue circles**: Events in the causal past (all events that happened-before the selected event)
- **Light orange circles**: Events in the causal future (all events that happen-after the selected event)
- **Default colors**: Concurrent events (not causally related to the selected event)

This feature helps visualize:
- Message causality chains
- Concurrent vs. sequential events
- Propagation of information through the system

**Click elsewhere** or press `Escape` to clear highlighting.

### Vertical Rulers

Add vertical measurement rulers to compare timing:

1. **Click "Add Ruler"** in the toolbar (adds ruler at center)
2. **Ruler appears** as a vertical line across all processes
3. **Drag rulers** by clicking and moving them
4. **Multiple rulers** can be added for comparison

Rulers help measure:
- Time intervals between events
- Message transmission delays
- Algorithm phases or rounds

### Minimap Navigation

The minimap in the top-right corner provides:

- **Topology**: See the network topology
- **Quick selection**: Click on a process to highlight it; click on an edge to highlight all messages going through it
- **Drag move**: Drag the minimap to any of the four corners
- **Zoom context**: Understand your position in large traces

### Opening Multiple Traces

You can open multiple trace files simultaneously:

1. **File → Open Trace...**: Opens a new window
2. **Each trace** in its own independent window
3. **Compare executions** side-by-side
4. **Close individual windows** (Ctrl+W) or all at once (Ctrl+Q)

---

## Keyboard and Mouse Controls

### Mouse Controls

| Action | Description |
|--------|-------------|
| **Left Click (event)** | Select event and show causality |
| **Left Click (canvas)** | Clear selection |
| **Left Click (ruler)** | Start dragging ruler |
| **Mouse Wheel** | Zoom in/out horizontally |
| **Hover (message arrow)** | Show message type/details (future) |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+O** | Open trace file |
| **Ctrl+W** | Close current window |
| **Ctrl+Q** | Quit application |
| **Escape** | Clear event selection |

---

## Color Scheme

### Event Colors (Default - No Selection)

| Color | Event Type | Description |
|-------|------------|-------------|
| **Black** | Send/Receive event | Process sending or receiving a message |
| **Gray** | Local event | Internal computation (no message) |

### Event Colors (With Selection)

When an event is selected, colors indicate causality:

| Color | Relationship | Description |
|-------|--------------|-------------|
| **Red** | Selected event | The event you clicked |
| **Light Blue** | Causal past | Events that happened-before selected |
| **Light Orange** | Causal future | Events that happen-after selected |
| **Orange** | Highlighted | Other highlights (search, filter - future) |
| **Black** | Concurrent send/receive | Send/receive events concurrent with selected |
| **Gray** | Concurrent local | Local events concurrent with selected |

### Message Arrows

| Style | Description |
|-------|-------------|
| **Black line** | Normal message |
| **Arrow head** | Points to receiving process |
| **Label** | Message type (on hover - future) |

### Other Elements

| Element | Color/Style | Description |
|---------|-------------|-------------|
| **Process lines** | Light gray | Horizontal timeline |
| **Process labels** | Black text | Process IDs (p1, p2, ...) |
| **Rulers** | Dashed line | Vertical measurement marks |
| **Minimap viewport** | Red rectangle | Current visible area |

---

## Tips and Best Practices

### Performance with Large Traces

For traces with many events (>1000):

- **Use logical time mode** for clearer causality visualization
- **Zoom in** to focus on specific regions
- **Use the minimap** for quick navigation
- **Close causality highlighting** when not needed (click elsewhere)

### Understanding Causality

- **Causal past** (light blue) = all events that could have influenced the selected event
- **Causal future** (light orange) = all events influenced by the selected event
- **Concurrent events** (default colors) = could happen in any order
- **Message chains** are always part of causality

### Debugging with Dapyview

1. **Verify message ordering**: Check that messages arrive in expected order
2. **Identify deadlocks**: Look for processes stuck without events
3. **Trace information flow**: Follow causal chains through highlights
4. **Compare runs**: Open multiple traces to compare different executions
5. **Measure timing**: Use rulers to check delays and synchronization

### Generating Good Traces

For best visualization results:

- **Limit execution length**: Keep traces focused (use `max_steps` in Settings)
- **Use meaningful names**: Set `algorithm_name` in your Algorithm class
- **Include docstrings**: Algorithm descriptions appear in traces
- **Test with small topologies**: Start with 3-5 processes for clarity
- **Save intermediate states**: Generate traces at different execution points

### Common Issues

**Issue**: Trace file won't open
- **Check**: File is valid pickle (`.pkl`) or JSON (`.json`) generated by dapy Simulator
- **Try**: Re-run simulation and regenerate trace
- **Verify**: For pickle, check file is not corrupted; for JSON (optional dependency), use a JSON validator

**Issue**: Events overlap or appear incorrect
- **Switch to logical time mode** for clearer layout
- **Zoom in** to see individual events better
- **Check**: Your algorithm's `on_event` logic is correct

**Issue**: Missing causality relationships
- **Ensure**: Vector clocks are computed (automatic in dapy)
- **Verify**: Messages are properly sent/received pairs
- **Check**: Algorithm uses Message class correctly

---

## Advanced Topics

### Trace File Formats

**Pickle Format (Default)**

Traces are saved as pickle files (`.pkl`) by default:
- **Compact**: Smaller file size
- **Fast**: Quick to save and load
- **No dependencies**: Works with base dapy installation

**JSON Format (Optional)**

For human-readable traces, install the optional JSON dependency:

```bash
uv pip install "dapy[json]"
# or: pip install "dapy[json]"
```

Then save traces as JSON:

```python
sim.save_trace("trace.json", format="json")
```

JSON traces have this structure:

```json
{
  "algorithm_name": "My Algorithm",
  "algorithm_description": "...",
  "topology": {...},
  "events_list": [
    {
      "event": {...},
      "start": "PT0.123S",
      "end": "PT0.456S"
    },
    ...
  ]
}
```

- **algorithm_name**: Displayed in toolbar
- **topology**: Network graph structure
- **events_list**: Chronological list of timed events
- **start/end**: ISO 8601 duration format

### Custom Event Types

Dapyview automatically handles:
- **Message**: Two-process communication (send/receive pair)
- **Signal**: Single-process event (local)
- **Custom subclasses**: Automatically detected and visualized

### Extending Dapyview

Dapyview is open source and can be extended:

- **Source code**: `src/dapyview/` directory
- **Main window**: `trace_window.py`
- **Canvas rendering**: `trace_canvas.py`
- **Clock computations**: `trace_model.py`

Contributions welcome at: https://github.com/xdefago/dapy

---

## Troubleshooting

### Installation Issues

**Problem**: `dapyview` command not found
```bash
# Solution 1: Install dapy from GitHub
pip install "git+https://github.com/xdefago/dapy.git"

# Solution 2: Use standalone executable
# Download from: https://github.com/xdefago/dapy/releases
# No Python installation required

# Verify installation
which dapyview
dapyview --version
```

**Problem**: Qt/PySide6 errors
```bash
# Solution: Reinstall UI dependencies
pip install --force-reinstall PySide6
```

### Runtime Issues

**Problem**: "No module named dapyview"
```bash
# Solution: Use correct invocation
dapyview trace.pkl  # Not: python -m dapyview
```

**Problem**: Trace won't load
- Ensure trace was saved with `sim.save_trace()`
- Check file permissions
- Validate JSON syntax
- Try opening in a JSON viewer first

### Getting Help

- **Documentation**: https://xdefago.github.io/dapy
- **Repository**: https://github.com/xdefago/dapy
- **Issues**: https://github.com/xdefago/dapy/issues

---

## Version History

- **v0.2.0** (2026-01): Added logical time mode, causality highlighting, rulers
- **v0.1.0** (2025-12): Initial release with basic time-space diagrams

---

## License

Dapyview is part of Dapy, released under the MIT License.

Copyright (c) 2025-2026 Xavier Défago
