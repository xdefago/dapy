# My Distributed Algorithm Project

A template project for developing distributed algorithms using the [dapy](https://github.com/xdefago/dapy) framework.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Setup

1. **Use this template** (if on GitHub):
   - Click the "Use this template" button
   - Or copy this directory structure to your own project

2. **Install dependencies**:
   ```bash
   # Using uv (recommended - fast and reliable)
   uv sync
   ```
   
   <details>
   <summary>Alternative: Using pip</summary>
   
   ```bash
   pip install -r requirements.txt
   ```
   </details>

3. **Verify installation**:
   ```bash
   python -c "import dapy; print(dapy.__version__)"
   ```

## Project Structure

```
.
├── README.md           # This file
├── pyproject.toml      # Project configuration and dependencies
├── requirements.txt    # Generated dependencies (for pip)
├── broadcast/          # Example: Broadcast algorithm
│   ├── __init__.py
│   ├── run_bcast.py        # Simulation runner
│   └── algo/
│       ├── __init__.py
│       └── algorithm.py    # Algorithm implementation
├── my_algo/            # Template for your algorithm
│   ├── __init__.py
│   ├── algorithm.py        # Your algorithm (template)
│   └── run_my_algo.py      # Your simulation runner
├── tests/              # Unit tests
│   └── test_algorithm.py
└── traces/             # Directory for trace outputs
```

## Quick Start

### 1. Run the Example Broadcast Algorithm

```bash
uv run run-bcast
```

This will:
- Run a simple broadcast algorithm simulation
- Save a trace file to `traces/broadcast_trace.pkl`
- Print simulation results

### 2. Visualize the Trace

```bash
dapyview traces/broadcast_trace.pkl
```

Or simply run `dapyview` without arguments to open a file selector.

### 3. Modify the Template

Edit files in `src/my_algo/`:
- `algorithm.py` - Define your state, messages, and algorithm logic
- `run.py` - Configure topology and run simulations

## What's Included

### 1. Working Example: Broadcast Algorithm (`broadcast/`)

A complete flooding broadcast implementation demonstrating:
- State definition with frozen dataclasses
- Message and signal types
- Algorithm implementation with `initial_state` and `on_event`
- System topology creation (Ring of 5 processes)
- Running simulations and saving traces (pickle format by default)

### 2. Template for Your Algorithm (`my_algo/`)

A starter template with:
- Comprehensive comments explaining each component
- Placeholder classes for State, Messages, Signals
- Pattern matching examples in `on_event()`
- Detailed simulation runner with configuration options

Study the broadcast example, then implement your own algorithm in `my_algo/`!

## Documentation

- **Dapy Documentation**: https://xdefago.github.io/dapy
- **Dapyview User Guide**: https://xdefago.github.io/dapy/dapyview-guide.html
- **Sample Algorithms**: https://xdefago.github.io/dapy/sample-algorithm.html

## Development

### Running Tests

```bash
# Using uv
uv run pytest

# Run with coverage
uv run pytest --cov=src
```

<details>
<summary>Alternative: Using pip/pytest directly</summary>

```bash
pytest
pytest --cov=src
```
</details>

### Project Checklist

- [ ] Rename `my_algo` package to your algorithm name
- [ ] Define your state in `algorithm.py`
- [ ] Define your message/signal types
- [ ] Implement algorithm logic in `on_event`
- [ ] Update topology and initial events in `run.py`
- [ ] Write tests in `tests/`
- [ ] Run and visualize!

## Tips

- Use frozen dataclasses for immutable state
- Use `state.cloned_with(...)` to create modified state copies
- Test with small topologies first (3-5 processes)
- Use logical time mode in dapyview to see causality
- Save intermediate traces during development

## Contributing

Found a bug or want to improve the template? Contributions welcome at https://github.com/xdefago/dapy

## License

This template is provided as-is for use with the dapy framework.
Your algorithm code is yours - use any license you prefer.
