# Dapy: Distributed Algorithms in Python

<p style="font-style:italic">
IMPORTANT:
This project is in a very early stage of development; use at your own risks.
</p>

## Description

This is a simple (simplistic) programming framework to simulate the execution of distributed algorithms.



## How to begin

### For External Users (Using dapy as a library)

If you want to use `dapy` in your own Python project without modifying the dapy source code:

1. **Install dapy** from GitHub (dapy is not yet published to PyPI):
   
   **Using uv (recommended):**
   ```shell
   uv add "dapy @ git+https://github.com/xdefago/dapy.git"
   ```
   
   **Using pip:**
   ```shell
   pip install git+https://github.com/xdefago/dapy.git
   ```
   
   **Using poetry:**
   ```shell
   poetry add git+https://github.com/xdefago/dapy.git
   ```

2. **In your Python code**, import and use dapy components:
   ```python
   from dapy.core import Pid, System, Ring, Asynchronous, Algorithm, State, Event
   from dapy.sim import Simulator, Settings
   from dataclasses import dataclass
   
   # Define your algorithm by subclassing Algorithm
   @dataclass(frozen=True)
   class MyAlgorithm(Algorithm[MyState]):
       # ... implement your algorithm
       pass
   
   # Create and run a simulation
   system = System(topology=Ring.of_size(4), synchrony=Asynchronous())
   algorithm = MyAlgorithm(system)
   sim = Simulator.from_system(system, algorithm)
   sim.start()
   sim.run_to_completion()
   ```

3. **See the documentation** for detailed examples:
   - [How to write an algorithm](https://xdefago.github.io/dapy/sample-algorithm.html)
   - [How to define an execution](https://xdefago.github.io/dapy/sample-execution.html)
   - [API documentation](https://xdefago.github.io/dapy/api)

### For Development / Contributing

If you want to modify the dapy framework itself:

The project is currently under active development with many changes to come in the near future.
Therefore, it is not yet recommended to rely on a fixed version during this period.

### Requirements

Python 3.13 or higher is required.

**For external users:** A standard Python package manager (pip, uv, poetry, etc.) is sufficient.

**For development:** It is recommended to use [uv](https://docs.astral.sh/uv/) for dependency management and building.

### Setup: For Development

To set up a development environment to contribute to dapy:

1. Clone this repository:
    ```shell
    git clone https://github.com/xdefago/dapy.git
    cd dapy
    ```

2. Install `uv` if you haven't already:
    ```shell
    brew install uv # on Mac
    ```
    _check the page ["Installing uv"](https://docs.astral.sh/uv/getting-started/installation/) for other environments._
    
3. Synchronize dependencies (omit `--all-groups` for a more lightweight install):
    ```shell
    uv sync --all-groups
    ```

4. Verify the setup by running an example:
    ```shell
    uv run python examples/example.py
    ```
    The output should show some execution trace of the "Learn the Topology" algorithm in a ring of four processes.

### Getting Started

For a comprehensive tutorial on using dapy, see the annotated examples:

* **[Quickstart Guide](QUICKSTART.md)** - Get up and running in 5 minutes (recommended for new users)
* **[Part 1: How to write an algorithm](docs/sample-algorithm.md)** - Learn how to define the state, messages/signals, and algorithm logic
* **[Part 2: How to define an execution](docs/sample-execution.md)** - Learn how to set up and run simulations
* **[Template](examples/template.py)** - A complete code template to start your own algorithm
* **[API Documentation](https://xdefago.github.io/dapy/api)** - Full API reference for all dapy classes

### Core Concepts & API Reference

**Core Modules:**
- **`dapy.core`** - Core abstractions (State, Algorithm, Event, Message, Signal, Pid, ProcessSet, ChannelSet, System, Topology)
- **`dapy.sim`** - Simulation engine (Simulator, Trace, Configuration, Settings)
- **`dapy.algo`** - Built-in algorithms (e.g., LearnGraphAlgorithm for topology learning)

**Key Classes:**
- `Algorithm[StateT]` - Base class for distributed algorithms. Subclass this with your state type and implement:
  - `initial_state(pid: Pid) -> StateT` - Create initial state
  - `on_event(old_state: StateT, event: Event) -> tuple[StateT, Sequence[Event]]` - Handle events
- `System` - Defines network topology and synchrony model
- `Simulator` - Runs the simulation and collects execution traces
- `State` - Base class for process states (must be immutable, frozen dataclass)
- `Event`, `Message`, `Signal` - Event types for inter-process communication

### Optional Dependencies

Additional features are available through optional dependencies:

* **`json`** - Enables serialization/deserialization of `Trace` objects to/from JSON strings using `dump_json()` and `load_json()` methods.

* **`ui`** - Installs the **dapyview** GUI trace viewer for interactive visualization of execution traces:
  - Time-space diagrams showing process timelines, events, and messages
  - Toggle between physical time and logical time (Lamport clocks)
  - Interactive network topology minimap
  - Zoom, rulers, and highlighting features
  - See [src/dapyview/README.md](src/dapyview/README.md) for details

To install dapy with optional dependencies:

**Using uv:**
```shell
# For JSON support only
uv add "dapy[json] @ git+https://github.com/xdefago/dapy.git"

# For GUI viewer (includes JSON support)
uv add "dapy[ui] @ git+https://github.com/xdefago/dapy.git"

# For both during development
uv sync --group ui
```

**Using pip:**
```shell
pip install "git+https://github.com/xdefago/dapy.git#egg=dapy[json]"
```

**Using poetry:**
```shell
poetry add dapy[json] @ git+https://github.com/xdefago/dapy.git
```

### Contributing to dapy Development

1. Sync all dependencies including dev tools:
    ```shell
    uv sync --all-groups
    ```

2. Run tests:
    ```shell
    uv run pytest
    ```

3. Run linting and formatting:
    ```shell
    uv run ruff check src --fix
    uv run ruff format src
    ```

4. Install pre-commit hooks:
    ```shell
    uv pip install pre-commit
    pre-commit install
    ```
