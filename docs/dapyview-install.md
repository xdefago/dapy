# Installing Dapyview

Dapyview is a GUI tool for visualizing execution traces of distributed algorithms.

> **Note**: Dapyview is for **viewing** trace files. To **create** traces, you need to install the dapy library (see Option 2 or 3 below). The standalone executable (Option 1) is only for visualization.

## Option 1: Download Standalone Executable (Recommended for Viewing Only)

**No Python installation required!** Download and run immediately.

### macOS

1. **Download** the appropriate file from [releases](https://github.com/xdefago/dapy/releases):
   - Apple Silicon (M1/M2/M3/...): `dapyview-v0.2.0-macos-arm64`
   - Intel Mac: `dapyview-v0.2.0-macos-x86_64`

2. **Make it executable**:
   ```bash
   chmod +x dapyview-v0.2.0-macos-arm64
   ```

3. **Run**:
   ```bash
   ./dapyview-v0.2.0-macos-arm64 trace.json
   ```

4. **Optional** - Install to PATH for easy access:
   ```bash
   sudo mv dapyview-v0.2.0-macos-arm64 /usr/local/bin/dapyview
   # Now you can just run: dapyview (opens file selector)
   # Or: dapyview trace.pkl
   ```

**Note**: macOS may show a security warning for downloaded apps. If you see "cannot be opened because it is from an unidentified developer":
- Right-click the file and select "Open"
- Or go to System Preferences → Security & Privacy → General, and click "Open Anyway"

### Linux

1. **Download** from [releases](https://github.com/xdefago/dapy/releases):
   ```bash
   wget https://github.com/xdefago/dapy/releases/download/v0.2.0/dapyview-v0.2.0-linux-x86_64
   ```

2. **Make it executable**:
   ```bash
   chmod +x dapyview-v0.2.0-linux-x86_64
   ```

3. **Run**:
   ```bash
   ./dapyview-v0.2.0-linux-x86_64 trace.json
   ```

4. **Optional** - Install to PATH:
   ```bash
   sudo mv dapyview-v0.2.0-linux-x86_64 /usr/local/bin/dapyview
   ```

**Troubleshooting**: If you get library errors, install Qt dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install xcb-util-cursor
```

### Windows

1. **Download** from [releases](https://github.com/xdefago/dapy/releases):
   - `dapyview-v0.2.0-windows-x86_64.exe`

2. **Run**:
   ```powershell
   .\dapyview-v0.2.0-windows-x86_64.exe trace.json
   ```

**Note**: Windows may show a SmartScreen warning. Click "More info" → "Run anyway"

---

## Option 2: Install from GitHub with pip (For Algorithm Development + Viewing)

If you have Python 3.11+ installed and want to both **create algorithms and view traces**:

```bash
pip install "git+https://github.com/xdefago/dapy.git"
```

This installs:
- The `dapy` library for writing distributed algorithms
- The `dapyview` command for viewing traces
- All dependencies (including PySide6 for the GUI)

Then run:
```bash
dapyview              # Open file selector
dapyview trace.pkl    # Open specific file
```

---

## Option 3: Install from GitHub with uv (Recommended for Algorithm Development + Viewing)

```bash
uv add "dapy @ git+https://github.com/xdefago/dapy.git"
```

This installs:
- The `dapy` library for writing distributed algorithms  
- The `dapyview` command for viewing traces
- All dependencies (including PySide6 for the GUI)

Then run:
```bash
dapyview              # Open file selector
dapyview trace.pkl    # Open specific file
```

---

## Option 4: Clone Repository (For Dapy Developers)

If you want to **modify dapy itself** or contribute to development:

```bash
git clone https://github.com/xdefago/dapy.git
cd dapy
pip install --editable .
```

The `--editable` flag means changes to the source code are immediately reflected without reinstalling.

---

## Which Option Should I Choose?

| Use Case | Recommended Option |
|----------|-------------------|
| **Only viewing trace files** (someone else creates them) | Option 1: Standalone executable |
| **Creating algorithms + viewing traces** | Option 2 or 3: Install dapy[ui] |
| **Development/Contributing to dapy** | Clone repo + `uv sync --all-groups` |

---

## Verifying Installation

After installation, verify it works:

```bash
dapyview --version
# Should output: dapyview 0.2.0
```

---

## Usage

```bash
# Basic usage
dapyview path/to/trace.json

# Example with sample trace
dapyview examples/sample_trace.json
```

---

## Next Steps

- **Read the [User Guide](dapyview-guide.md)** for complete documentation
- **Check the [Quick Reference](dapyview-quickref.md)** for common tasks
- **See [sample-execution.md](sample-execution.md)** to learn how to generate trace files

---

## Getting Help

- **Documentation**: [docs/dapyview-guide.md](dapyview-guide.md)
- **Issues**: https://github.com/xdefago/dapy/issues
- **Repository**: https://github.com/xdefago/dapy

---

## Uninstalling

### Standalone Executable
Simply delete the downloaded file:
```bash
sudo rm /usr/local/bin/dapyview  # If you installed to PATH
```

### Python Installation
```bash
pip uninstall dapy
# or: uv remove dapy
```
