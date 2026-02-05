---
layout: default
title: Development
nav_order: 5
has_children: true
---

# Development

Documentation for contributing to and maintaining the dapy project.

## For Contributors

- [Developer Guide](DEVELOPERS.md) - Setup, testing, and contribution workflow

## For Maintainers

- [Packaging Guide](dapyview-packaging.md) - Building standalone executables
- [Release Process](DEVELOPERS.md#release-process) - Creating releases

## Project Structure

The dapy project consists of two main components:

1. **dapy library** (`src/dapy/`) - Core framework for defining and simulating distributed algorithms
2. **dapyview application** (`src/dapyview/`) - Standalone GUI trace viewer

## Quick Links

- **Repository**: [github.com/xdefago/dapy](https://github.com/xdefago/dapy)
- **Report Issues**: [GitHub Issues](https://github.com/xdefago/dapy/issues)
- **PyPI Package**: [dapy on PyPI](https://pypi.org/project/dapy)

## Development Setup

```bash
# Clone the repository
git clone https://github.com/xdefago/dapy.git
cd dapy

# Install dependencies with uv
uv sync --all-groups

# Run tests
uv run pytest

# Format and lint code
uv run black src/
uv run ruff check --fix src/
```

See [Developer Guide](DEVELOPERS.md) for detailed setup and workflow instructions.
