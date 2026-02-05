---
layout: default
title: Home
nav_order: 1
description: "Dapy: Simulate, prototype, and visualize distributed algorithms in Python"
permalink: /
---

# 🚀 Dapy: Simulating Distributed Algorithms in Python

![Dapy logo](assets/logo/dapy-logo.svg)

**Dapy** is a lightweight Python framework for prototyping, simulating, and visualizing distributed algorithms in a controlled environment. Perfect for education, research, and experimentation with distributed computing concepts.

## What is Dapy?

Dapy provides:

- **Simple Algorithm Definition**: Specify algorithms using a clean, intuitive API
- **Simulation Engine**: Execute algorithms in a deterministic, repeatable environment
- **Execution Traces**: Detailed logs of all events (sends, receives, local operations)
- **Visual Debugging**: **Dapyview** GUI for interactive visualization of traces with time-space diagrams

Whether you're teaching distributed computing or exploring new algorithms, Dapy streamlines the prototyping process.

### Two Components

Dapy is split into two independent parts:

- **[dapy library](dapy-library.md)** - The core framework for defining and simulating algorithms.
- **[dapyview](dapyview.md)** - An optional GUI trace viewer for visualizing execution traces.

---

## 🎯 Quick Start

### Installation

Dapy is currently under active development and not yet published on PyPI.

**Recommended: Use the Template Repository**

The fastest way to get started is using our project template:

1. **Use the GitHub template**:
   - Go to https://github.com/xdefago/dapy-template
   - Click **Use this template** to create your own repository
   - It includes pre-configured project structure, example algorithm, and ready-to-use setup

2. **Clone and install**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   uv sync
   ```

3. **Run the example**:
   ```bash
   uv run run-bcast
   dapyview              # Opens file selector, or:
   dapyview traces/broadcast_trace.pkl
   ```

See the [template README](https://github.com/xdefago/dapy-template) for complete instructions.

**Alternative: Install dapy as a dependency**

For existing projects, install dapy directly from GitHub:

```bash
# Using uv (recommended)
uv add "dapy @ git+https://github.com/xdefago/dapy.git"

# Or using pip
pip install "git+https://github.com/xdefago/dapy.git"
```

This installs:
- The `dapy` library for writing and simulating distributed algorithms
- The `dapyview` GUI viewer (included automatically)

**For dapy developers** who want to modify dapy itself:

See the [Developer Documentation](DEVELOPERS.md) for setup with editable install.

### Your First Algorithm

```python
from dapy.core import Algorithm, State, Message, Pid
from dataclasses import dataclass

@dataclass(frozen=True)
class MyState(State):
    received: bool = False

class SimpleAlgorithm(Algorithm):
    def get_initial_state(self, pid: Pid, **kwargs) -> MyState:
        return MyState(received=False)
    
    def on_init(self, state, pid, topology, message_pool):
        if pid == 0:
            message_pool.add_message(message=str("hello"), sender=0, receiver=1)
    
    def on_message(self, state, msg, sender):
        return state.__class__(received=True)
```

### Visualize Your Trace

1. Run your algorithm and save a trace
2. Open the trace with **Dapyview**:
   ```bash
   dapyview              # Opens file selector
   dapyview trace.pkl    # Opens specific file
   ```
3. Explore message flows, causality relationships, and timing

---

## 📚 Documentation

### For Users

- **[Dapyview User Guide](dapyview-guide.md)** - Complete guide to the GUI trace viewer
  - Installation and setup
  - User interface tutorial
  - Color scheme explanation
  - Tips and best practices

### For Developers

- **[Sample Algorithm](sample-algorithm.md)** - Learn how to define an algorithm
  - State definition
  - Message and signal types
  - Algorithm implementation

- **[Sample Execution](sample-execution.md)** - Learn how to run simulations
  - Setting up topologies
  - Running executions
  - Saving and loading traces

- **[API Reference](api.md)** - Complete API documentation
  - Generated from source code docstrings
  - All public classes and functions

---

## 🎨 Dapyview: Visual Trace Viewer

**Dapyview** is an interactive GUI for visualizing execution traces of distributed algorithms.

### Key Features

- **Time-Space Diagrams**: Visualize process timelines and message exchanges
- **Dual Clock System**: Switch between physical time and logical (Lamport) time
- **Causality Highlighting**: Click events to highlight causal past/future
- **Interactive Controls**: Zoom, pan, add measurement rulers
- **Minimap**: Overview widget for large traces

### Getting Started with Dapyview

```bash
# Run dapyview with a trace file
dapyview examples/sample_trace.pkl

# Or start without a file (open via menu)
dapyview
```

See the **[Dapyview User Guide](dapyview-guide.md)** for detailed documentation.

---

## 🏗️ Project Structure

```
dapy/
├── src/
│   ├── dapy/           # Main framework
│   │   ├── core/       # Core abstractions (Algorithm, State, Message, etc.)
│   │   ├── sim/        # Simulation engine
│   │   └── algo/       # Example algorithms
│   └── dapyview/       # GUI trace viewer (optional)
├── examples/           # Example algorithms and traces
├── tests/              # Test suite
├── docs/               # This documentation
└── pyproject.toml      # Project configuration
```

---

## 🔍 Features at a Glance

| Feature | Description |
|---------|-------------|
| **Algorithm Abstraction** | Simple API for defining distributed algorithms |
| **Deterministic Simulation** | Repeatable execution for consistent debugging |
| **Message Traces** | Complete records of all communication and events |
| **Causality Analysis** | Vector clock-based causal relationships |
| **Interactive Visualization** | Dapyview GUI with time-space diagrams |
| **Educational Focus** | Designed for teaching distributed computing |

---

## 💡 Use Cases

- **Education**: Teach distributed algorithms in a hands-on, visual way
- **Research**: Prototype and test new algorithm designs
- **Experimentation**: Explore algorithm behavior under different conditions
- **Visualization**: Understand complex message flows and timing

---

## 📖 More Information

- **Homepage**: [GitHub Repository](https://github.com/xdefago/dapy)
- **License**: MIT

---

## 🤝 Contributing

Interested in contributing? We welcome:
- Bug reports and feature requests
- Documentation improvements
- Algorithm examples
- Performance enhancements

Check the repository for contribution guidelines.

---

<p align="center">
  <strong>Start simulating your distributed algorithms today!</strong>
</p>
