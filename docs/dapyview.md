---
layout: default
title: Dapyview
nav_order: 3
has_children: true
---

# Dapyview - Trace Visualization

**Dapyview** is a graphical trace viewer for visualizing execution traces of distributed algorithms created with the Dapy framework. It displays time-space diagrams showing process timelines, message exchanges, and causality relationships.

## Features

- **Time-Space Diagrams**: Visualize process timelines and message exchanges
- **Interactive Exploration**: Click to select events and highlight causality
- **Logical Time Mode**: View events ordered by Lamport clocks to understand causality
- **Color-Coded Events**: Distinguish between message sends, receives, and local events
- **Cross-Platform**: Available as standalone executable for Windows, macOS, and Linux

## Quick Access

- [Installation Guide](dapyview-install.md) - Set up Dapyview on your system
- [User Guide](dapyview-guide.md) - Complete reference for using Dapyview
- [Quick Reference](dapyview-quickref.md) - Keyboard shortcuts and controls

## Two Ways to Use

### Option 1: Standalone Executable (No Python Required)

Download pre-built executables from [GitHub Releases](https://github.com/xdefago/dapy/releases). Perfect for viewing trace files without any setup.

→ [Installation Guide](dapyview-install.md)

### Option 2: Python Installation (With dapy library)

Install via pip/uv to get both dapy and dapyview:

```bash
pip install "git+https://github.com/xdefago/dapy.git"
```

Then run:

```bash
dapyview trace.pkl
```

## Workflow

1. **Create traces** using [dapy library](dapy-library.md)
2. **Visualize** with Dapyview to:
   - Debug algorithms
   - Understand causality and timing
   - Present results
