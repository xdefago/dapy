---
layout: default
title: Dapy Library
nav_order: 2
has_children: true
---

# Dapy Library

The **dapy library** is the core framework for defining and simulating distributed algorithms.

## Getting Started

Learn how to:

1. [Write algorithms](sample-algorithm.md) - Define your distributed algorithm
2. [Define executions](sample-execution.md) - Create and run simulations

## Key Concepts

- **Algorithms**: Define the behavior of processes in your system
- **Simulation**: Execute algorithms deterministically with detailed tracing
- **Traces**: Inspect execution logs to debug and understand algorithm behavior
- **Visualization**: Use Dapyview to visualize traces as time-space diagrams

## Using Dapy

For detailed API documentation, see the [API Reference](/dapy/api/dapy/).

## Installation

```bash
# From GitHub
pip install "git+https://github.com/xdefago/dapy.git"

# Or using uv
uv add "git+https://github.com/xdefago/dapy.git"
```

## Next Steps

- Start with [Writing Algorithms](sample-algorithm.md)
- For visualization, see [Dapyview Installation](dapyview-install.md)
- For development, see [Developer Guide](DEVELOPERS.md)
