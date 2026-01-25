# Dapy Documentation

This directory contains documentation for the Dapy distributed algorithms framework and the Dapyview trace viewer.

## Contents

### Getting Started
- [Dapy Main README](../README.md) - Installation and quick start
- [Sample Algorithm](sample-algorithm.md) - How to write an algorithm
- [Sample Execution](sample-execution.md) - How to run simulations

### Dapyview Trace Viewer
- [Installation Guide](dapyview-install.md) - How to install and run dapyview
- [Dapyview User Guide](dapyview-guide.md) - Complete guide to using the trace viewer
- [Quick Reference](dapyview-quickref.md) - Quick reference card for common tasks
- [Packaging Guide](dapyview-packaging.md) - How to package dapyview as standalone executable

### API Documentation
- [API Reference](api/index.html) - Auto-generated API documentation

## Generate API Documentation

Install pdoc (included in `dev` dependencies):
```shell
uv pip install pdoc
```

Generate the docs:
```shell
uv run pdoc -o docs/api -d google --logo ../logo/dapy-logo.svg --logo-link .. src/dapy
```

Open the docs (using open command on Mac terminal):
```shell
open docs/api/index.html
```
