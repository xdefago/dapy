---
layout: default
title: Developer Guide
parent: Development
nav_order: 1
---

# Developer Documentation

This guide is for contributors and maintainers of the dapy project.

## Project Structure

The dapy project consists of two main components:

1. **dapy library** (`src/dapy/`) - Core framework for defining and simulating distributed algorithms
2. **dapyview application** (`src/dapyview/`) - Standalone GUI trace viewer

## Development Setup

### Prerequisites

- Git
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Python 3.13 or higher _(not necessary if using `uv`)_

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xdefago/dapy.git
   cd dapy
   ```

2. **Install dependencies with uv**:
   ```bash
   uv sync --all-groups
   ```
   
   This installs all dependencies including dev tools (pytest, black, ruff, pdoc).

3. **Verify installation**:
   ```bash
   python example.py
   uv run dapyview examples/sample_trace.pkl
   ```

### Alternative: Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with all extras
pip install -e ".[dev,ui]"
```

## Building Dapyview Executables

Dapyview standalone executables are built using PyInstaller and distributed via GitHub releases.

### Local Build

Build for your current platform:

```bash
./scripts/build-dapyview.sh
```

This creates platform-specific executables in `dist/`:
- macOS: `dapyview-macos-arm64` or `dapyview-macos-x86_64`
- Linux: `dapyview-linux-x86_64`
- Windows: `dapyview-windows-x86_64.exe`

### Testing Local Build

```bash
# macOS
./dist/dapyview-macos-arm64 examples/sample_trace.pkl

# Linux
./dist/dapyview-linux-x86_64 examples/sample_trace.pkl

# Windows
dist\dapyview-windows-x86_64.exe examples\sample_trace.pkl
```

## Release Process

The project uses GitHub Actions to automatically build multi-platform executables when you push a version tag.

### Creating a Release

1. **Update version number** in `pyproject.toml`:
   ```toml
   [project]
   version = "0.3.0"
   ```

2. **Commit the version change**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.3.0"
   ```

3. **Create and push a git tag**:
   ```bash
   git tag -a v0.3.0 -m "Release version 0.3.0"
   git push origin main
   git push origin v0.3.0
   ```

4. **GitHub Actions automatically**:
   - Builds executables for macOS (arm64 + x86_64), Linux (x86_64), and Windows (x86_64)
   - Creates a GitHub Release draft
   - Uploads all executables as release assets

5. **Edit the GitHub Release**:
   - Go to https://github.com/xdefago/dapy/releases
   - Edit the auto-created draft release
   - Add release notes describing changes
   - Publish the release

### What Gets Built

The CI builds the following artifacts:

- `dapyview-v0.3.0-macos-arm64` - macOS Apple Silicon
- `dapyview-v0.3.0-macos-x86_64` - macOS Intel
- `dapyview-v0.3.0-linux-x86_64` - Linux 64-bit
- `dapyview-v0.3.0-windows-x86_64.exe` - Windows 64-bit

Users can download and run these directly without Python installed.

## Distribution Methods

### For End Users (Writing Algorithms)

Install the dapy library from GitHub (no cloning required):

```bash
pip install "git+https://github.com/xdefago/dapy.git"
```

This gives them:
- The `dapy` library for algorithm development
- The `dapyview` CLI command (requires Python and PySide6)

### For Trace Viewers Only

Download the standalone executable from GitHub releases:

https://github.com/xdefago/dapy/releases

No Python installation required - just download and run.

### For Developers

Clone and install in editable mode (as described above in Development Setup).

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/dapy --cov-report=html

# Run specific test file
uv run pytest tests/test_topology.py

# Run with verbose output
uv run pytest -v
```

## Code Quality

### Linting

```bash
# Check code with ruff
uv run ruff check src/

# Auto-fix issues
uv run ruff check --fix src/
```

### Formatting

```bash
# Format code with black
uv run black src/

# Check formatting without changes
uv run black --check src/
```

### Type Checking

```bash
# Run mypy (if configured)
uv run mypy src/dapy
```

## Documentation

### Generate API Documentation

```bash
# Generate HTML docs with pdoc
uv run pdoc dapy --output-dir docs/api

# Serve docs locally
uv run pdoc dapy
```

### Update GitHub Pages

The `docs/` directory contains the Jekyll-based GitHub Pages site. To update:

1. Edit markdown files in `docs/`
2. Test locally if needed (requires Jekyll)
3. Commit and push - GitHub Pages auto-deploys from `main` branch

## PyInstaller Configuration

The `dapyview.spec` file controls how PyInstaller builds the executable. Key configurations:

- **Entry point**: `src/dapyview/main.py`
- **Hidden imports**: All dapy/dapyview modules, PySide6 components
- **Data files**: Source code included for trace loading
- **Excluded packages**: Development tools, testing frameworks (reduces size)
- **UPX compression**: Enabled for smaller executables
- **Console**: Disabled (GUI app)

### Modifying the Build

If you add new dependencies or modules:

1. Update `hiddenimports` list in `dapyview.spec`
2. Test the build locally: `./scripts/build-dapyview.sh`
3. Verify the executable works without Python installed

## Troubleshooting

### Build Fails on macOS

If you get code signing errors:
```bash
# Disable code signing in dapyview.spec
codesign_identity=None
```

### Missing Dependencies in Executable

If the built executable crashes with import errors:

1. Check `hiddenimports` in `dapyview.spec`
2. Add missing modules
3. Rebuild

### CI Build Fails

Check the GitHub Actions logs for:
- Python version mismatch
- Missing system dependencies (Linux)
- uv installation issues

## Contributing

When contributing code:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and linters locally
6. Submit a pull request

See `CONTRIBUTING.md` (if it exists) for detailed guidelines.

## Version Sync

The dapyview version is automatically synced with the dapy library version from `pyproject.toml` using `importlib.metadata`. When you bump the version:

- Update `pyproject.toml`
- Both dapy and dapyview will report the same version
- No need to update version strings elsewhere

Check version:
```bash
python -c "import dapy; print(dapy.__version__)"
uv run dapyview --version
```

## Maintenance Tasks

### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
uv lock --upgrade

# Update specific dependency
uv add --upgrade package-name
```

### Security Audits

```bash
# Check for known vulnerabilities
uv run pip-audit
```

### Cleaning Build Artifacts

```bash
# Remove build directories
rm -rf build/ dist/ *.spec.bak

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Contact

For questions or issues:
- GitHub Issues: https://github.com/xdefago/dapy/issues
- Email: (maintainer contact)
