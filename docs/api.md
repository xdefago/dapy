---
layout: default
title: API Reference
nav_order: 4
---

# API Reference

Complete API documentation for the dapy library.

## Modules

### Core Module (`dapy.core`)

Contains the fundamental classes and interfaces for defining distributed algorithms:

- **Algorithm**: Base class for implementing distributed algorithms
- **State**: Base class for defining process state
- **Message, Signal**: Base classes for defining messages and signals
- **System**: Runtime system for executing simulations
- **ProcessSet, ChannelSet**: Utility classes for managing processes and channels

### Algorithm Module (`dapy.algo`)

Pre-built algorithms and learning utilities:

- **learn**: Collection of example algorithms

### Simulation Module (`dapy.sim`)

Simulation engine and execution trace management:

- **Simulator**: Main simulation executor
- **Configuration**: Simulation settings
- **Trace**: Trace data structures and I/O

### Dapyview Module (`dapy.dapyview`)

GUI application for visualizing traces (requires PySide6).

---

## Full API Documentation

For complete API documentation with source code examples, visit:

👉 **[Generated API Docs](/dapy/api/dapy/)**

This includes detailed docstrings, class hierarchies, and method signatures for all public APIs.

---

## Quick Links

- [dapy.core](api/dapy/core/) - Core framework classes
- [dapy.algo](api/dapy/algo/) - Example algorithms
- [dapy.sim](api/dapy/sim/) - Simulation engine
- [dapy.dapyview](api/dapy/dapyview/) - GUI application

---

## Getting Started with the API

Start with the [Dapy Library](dapy-library.md) section for tutorials and examples, then refer to the API documentation for detailed class and method information.
