# dapyview - GUI Trace Viewer for dapy

A graphical user interface for visualizing execution traces from dapy distributed algorithm simulations.

## Features

- **Time-Space Diagram**: Visualize distributed algorithm execution with:
  - Process timelines (horizontal lines)
  - Events (dots on process lines)
  - Messages (arrows between processes)
  - Support for both physical and logical (Lamport) time

- **Interactive Controls**:
  - Toggle between physical time and logical time (Lamport clocks)
  - Zoom in/out of the diagram
  - Add vertical rulers to measure time intervals
  - Click on events and processes for highlighting

- **Network Topology Minimap**:
  - Visual representation of the process network
  - Force-directed graph layout
  - Synchronized highlighting with main diagram

- **Multi-Document Interface**:
  - Open and view multiple traces simultaneously
  - Each trace in its own window

## Installation

Install with the UI optional dependencies:

```bash
uv sync --group ui
# or
uv pip install dapy[ui]
```

This will install:
- `PySide6` (Qt GUI framework)
- `networkx` (graph algorithms for topology layout)
- `dapy[json]` (JSON serialization support)

## Usage

### Command Line

```bash
# View a single trace file
dapyview path/to/trace.json

# Start the application without opening a file
dapyview
```

**Important**: The trace file must be generated from algorithms whose modules are importable. The built-in `dapy.algo.learn` module is automatically imported, but if you use custom algorithms, you may need to ensure they're installed in the same environment.

### Generating Trace Files

To generate a trace file from a dapy simulation, enable tracing in the settings:

```python
from dapy.sim import Simulator, Settings
from dapy.core import System, Ring, Asynchronous
from dapy.algo.learn import LearnGraphAlgorithm, Start
from dapy.core import Pid
from datetime import timedelta

# Enable trace collection
settings = Settings(enable_trace=True)

# Create your system
system = System(
    topology=Ring.of_size(5),
    synchrony=Asynchronous(),
)

# Create simulator
algorithm = LearnGraphAlgorithm(system)
sim = Simulator.from_system(system, algorithm, settings=settings)

# Run simulation
sim.start()
sim.schedule_event(timedelta(seconds=0), Start(target=Pid(1)))
sim.run_to_completion()

# Save trace
with open('trace.json', 'w') as f:
    f.write(sim.trace.dump_json())
```

Then open the trace file with dapyview:

```bash
dapyview trace.json
```

### GUI Controls

- **Time Mode**: Toggle between "Physical Time" (actual timestamps) and "Logical Time" (Lamport clocks)
- **Zoom**: Use the slider to zoom in/out of the time-space diagram
- **Rulers**: Click "Add Ruler" to place a vertical ruler at the current position
- **Process Selection**: Click on a process in the minimap or diagram to highlight it
- **Event Selection**: Click on events to select and highlight them

### Time-Space Diagram

The main visualization shows:

- **Horizontal Lines**: Each line represents a process's timeline
- **Black Dots**: Send/receive events occurring at processes
- **Gray Dots**: Local events (no message)
- **Black Arrows**: Messages sent between processes
- **Labels**: Process IDs on the left, message types on arrows

### Minimap

The minimap shows the network topology:

- **Circles**: Processes
- **Lines**: Communication channels between processes
- **Highlighted Processes**: Shows which process is currently selected

## Example

See [examples/generate_trace.py](../examples/generate_trace.py) for a complete example of generating and viewing a trace.

## Architecture

The dapyview package consists of:

- `main.py`: Application entry point and command-line argument handling
- `app.py`: Main MDI application window with menus
- `trace_window.py`: Individual trace document window
- `trace_model.py`: Data model for processing trace data
- `trace_canvas.py`: Time-space diagram rendering widget
- `minimap.py`: Network topology minimap widget
- `toolbar.py`: Toolbar with viewer controls

## Requirements

- Python 3.13+
- PySide6 >= 6.8.0
- networkx >= 3.4
- dapy (with JSON support)

## License

Same as dapy main package.
