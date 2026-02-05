---
layout: default
title: Packaging Guide
parent: Development
nav_order: 2
---

# Dapyview Packaging Guide

This document provides recommendations for packaging **dapyview** (the GUI trace viewer) as a standalone executable that users can download and run without cloning the repository or installing Python dependencies.

## Important Notes

This packaging is specifically for **dapyview** (the GUI trace viewer). The **dapy** library/framework remains available independently:

- **For algorithm developers**: Install dapy via pip/uv to write and run distributed algorithms
- **For trace visualization**: Download the standalone dapyview executable to view trace files

The two components work together but can be used independently:
- Use dapy to create algorithms and generate traces (requires Python)
- Use dapyview to visualize trace files (standalone executable, no Python required)

## Packaging Options

### Option 1: PyInstaller (Recommended for Single Executables)

**PyInstaller** creates standalone executables for Windows, macOS, and Linux.

#### Advantages:
- Single-file executables possible
- Cross-platform support
- Users don't need Python installed
- Relatively small file sizes (50-150 MB)

#### Setup:

1. **Install PyInstaller**:
   ```bash
   uv add --dev pyinstaller
   # or: pip install pyinstaller
   ```

2. **Build using the provided spec file** (already configured for this project):
   
   The repository includes `dapyview.spec` pre-configured for building dapyview.

   **Quick build** (uses the build script):
   ```bash
   ./scripts/build-dapyview.sh
   ```

   **Manual build**:
   ```bash
   uv run pyinstaller dapyview.spec
   ```

3. **Test the executable**:
   ```bash
   # On macOS/Linux
   ./dist/dapyview-macos-arm64 examples/sample_trace.pkl
   # or: ./dist/dapyview-linux-x86_64 examples/sample_trace.pkl
   
   # On Windows
   dist\dapyview-windows-x86_64.exe examples\sample_trace.pkl
   ```

4. **Distribute**:
   - Upload `dist/dapyview` (or `dist/dapyview.exe` on Windows) to GitHub Releases
   - Compress for smaller downloads: `zip dapyview-macos.zip dist/dapyview`
   - Create releases for each platform: `dapyview-macos-arm64.zip`, `dapyview-linux-x86_64.zip`, `dapyview-windows.zip`

---

### Option 2: Briefcase (Recommended for Native Apps)

**Briefcase** from BeeWare creates platform-native applications (.app for macOS, .exe installer for Windows, .deb/.rpm for Linux).

#### Advantages:
- Native platform integration
- Proper installers
- Code signing support
- Better user experience

#### Setup:

1. **Install Briefcase**:
   ```bash
   uv add --dev briefcase
   ```

2. **Update pyproject.toml**:
   ```toml
   [tool.briefcase]
   project_name = "dapyview"
   bundle = "com.github.xdefago"
   version = "0.2.0"
   url = "https://github.com/xdefago/dapy"
   license = "MIT"
   author = "Xavier Défago"
   author_email = "defago@c.titech.ac.jp"
   
   [tool.briefcase.app.dapyview]
   formal_name = "Dapy Trace Viewer"
   description = "GUI trace viewer for distributed algorithm executions"
   icon = "resources/icon"  # Will generate platform-specific icons
   sources = ["src/dapyview", "src/dapy"]
   requires = [
       "PySide6>=6.10",
       "networkx>=3.6",
       "numpy>=2.4",
       "classifiedjson>=1.1",
   ]
   
   [tool.briefcase.app.dapyview.macOS]
   requires = []
   
   [tool.briefcase.app.dapyview.linux]
   requires = []
   system_requires = []
   
   [tool.briefcase.app.dapyview.windows]
   requires = []
   ```

3. **Create the app**:
   ```bash
   uv run briefcase create
   ```

4. **Build the app**:
   ```bash
   # macOS: creates .app bundle
   uv run briefcase build
   
   # Package for distribution
   uv run briefcase package
   ```

5. **Distribute**:
   - macOS: `macOS/dapyview-0.2.0.dmg`
   - Windows: `windows/dapyview-0.2.0.msi`
   - Linux: `linux/dapyview-0.2.0.AppImage`

---

### Option 3: Py2App (macOS Only)

For macOS-specific distribution with native look and feel.

#### Setup:

1. **Install py2app**:
   ```bash
   uv add --dev py2app
   ```

2. **Create setup.py**:
   ```python
   # setup_py2app.py
   from setuptools import setup
   
   APP = ['src/dapyview/main.py']
   DATA_FILES = []
   OPTIONS = {
       'argv_emulation': False,
       'packages': ['PySide6', 'dapy', 'dapyview', 'classifiedjson', 'networkx'],
       'iconfile': 'resources/icon.icns',
       'plist': {
           'CFBundleName': 'Dapyview',
           'CFBundleDisplayName': 'Dapy Trace Viewer',
           'CFBundleGetInfoString': 'Trace viewer for distributed algorithms',
           'CFBundleIdentifier': 'com.github.xdefago.dapyview',
           'CFBundleVersion': '0.2.0',
           'CFBundleShortVersionString': '0.2.0',
           'NSHumanReadableCopyright': 'Copyright © 2025-2026 Xavier Défago',
           'NSHighResolutionCapable': True,
       }
   }
   
   setup(
       app=APP,
       data_files=DATA_FILES,
       options={'py2app': OPTIONS},
       setup_requires=['py2app'],
   )
   ```

3. **Build**:
   ```bash
   uv run python setup_py2app.py py2app
   ```

4. **Result**: `dist/Dapyview.app`

---

### Option 4: Platform-Specific Wheels

Distribute as Python wheels that users install with pip, but pre-bundle all dependencies.

#### Advantages:
- Familiar Python ecosystem
- Smaller downloads
- Architecture-independent Python code

#### Setup:

1. **Build wheel**:
   ```bash
   uv build
   ```

2. **Upload to GitHub Releases**:
   ```bash
   # Creates dist/dapy-0.3.0-py3-none-any.whl
   # Upload this to GitHub Releases
   ```

3. **Users install**:
   ```bash
   pip install https://github.com/xdefago/dapy/releases/download/v0.3.0/dapy-0.3.0-py3-none-any.whl[ui]
   ```

---

## Recommended Approach: Multi-Platform Strategy

### For Best User Experience:

1. **Primary: PyInstaller Single Executables**
   - Build on each platform (macOS, Linux, Windows)
   - Upload to GitHub Releases
   - Users download and run immediately
   - File naming: `dapyview-v0.2.0-macos-arm64`, `dapyview-v0.2.0-windows-x86_64.exe`, `dapyview-v0.2.0-linux-x86_64`

2. **Secondary: Python Wheel**
   - For users comfortable with Python
   - Single cross-platform file
   - Install with: `pip install <wheel>[ui]`

### Release Workflow:

```bash
# 1. Update version in pyproject.toml
# 2. Build wheel
uv build

# 3. Build platform executables
# On macOS
uv run pyinstaller dapyview.spec
mv dist/dapyview dist/dapyview-v0.2.0-macos-$(uname -m)

# On Linux (in Docker or VM)
uv run pyinstaller dapyview.spec
mv dist/dapyview dist/dapyview-v0.2.0-linux-x86_64

# On Windows (in VM or GitHub Actions)
uv run pyinstaller dapyview.spec
move dist\dapyview.exe dist\dapyview-v0.2.0-windows-x86_64.exe

# 4. Create GitHub Release
gh release create v0.2.0 \
  dist/dapyview-v0.2.0-* \
  dist/dapy-*.whl \
  --title "Dapyview v0.2.0" \
  --notes "Release notes here"
```

---

## GitHub Actions Automation

Automate building for all platforms using GitHub Actions:

**`.github/workflows/release.yml`**:

```yaml
name: Build Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync --all-groups
      - name: Build executable
        run: |
          uv run pyinstaller dapyview.spec
          mv dist/dapyview dist/dapyview-${{ github.ref_name }}-macos-$(uname -m)
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dapyview-macos
          path: dist/dapyview-*

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0
          uv sync --all-groups
      - name: Build executable
        run: |
          uv run pyinstaller dapyview.spec
          mv dist/dapyview dist/dapyview-${{ github.ref_name }}-linux-x86_64
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dapyview-linux
          path: dist/dapyview-*

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install uv
        run: irm https://astral.sh/uv/install.ps1 | iex
      - name: Install dependencies
        run: uv sync --all-groups
      - name: Build executable
        run: |
          uv run pyinstaller dapyview.spec
          move dist\dapyview.exe dist\dapyview-${{ github.ref_name }}-windows-x86_64.exe
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dapyview-windows
          path: dist/dapyview-*

  create-release:
    needs: [build-macos, build-linux, build-windows]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: dist
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/**/*
          draft: false
          prerelease: false
```

---

## Distribution Checklist

### Before Release:

- [ ] Update version in `pyproject.toml`
- [ ] Update version in `main.py` (--version flag)
- [ ] Test on all target platforms
- [ ] Create release notes
- [ ] Test executables with sample traces
- [ ] Verify file sizes are reasonable (<200 MB)

### Release Assets:

- [ ] `dapyview-v0.2.0-macos-arm64` (Apple Silicon)
- [ ] `dapyview-v0.2.0-macos-x86_64` (Intel Mac)
- [ ] `dapyview-v0.2.0-linux-x86_64` (Linux)
- [ ] `dapyview-v0.2.0-windows-x86_64.exe` (Windows)
- [ ] `dapy-0.3.0-py3-none-any.whl` (Python wheel)
- [ ] `README.txt` (Installation instructions)

### Documentation:

- [ ] Update download links in README.md
- [ ] Add installation instructions for each platform
- [ ] Include example trace file
- [ ] Link to user guide

---

## Platform-Specific Notes

### macOS

- **Code signing**: Required for distribution outside Mac App Store
- **Notarization**: Required for macOS 10.15+
- **Universal binary**: Build for both Intel and ARM architectures

```bash
# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/dapyview.app

# Notarize
xcrun notarytool submit dist/dapyview.dmg \
  --apple-id your@email.com \
  --password @keychain:AC_PASSWORD \
  --team-id TEAM_ID
```

### Linux

- **AppImage**: More portable than standalone executables
- **Dependencies**: Ensure all Qt dependencies are bundled
- **Desktop file**: Include .desktop file for menu integration

### Windows

- **Antivirus**: Executables may trigger false positives
- **VC++ Redistributables**: Users may need to install
- **Installer**: Consider using NSIS or Inno Setup for proper installer

---

## File Size Optimization

Reduce executable size:

1. **Exclude unnecessary modules**:
   ```python
   # In PyInstaller spec
   excludes=['matplotlib', 'scipy', 'pandas', 'IPython']
   ```

2. **Use UPX compression**:
   ```bash
   pyinstaller --upx-dir=/path/to/upx ...
   ```

3. **Strip binaries**:
   ```bash
   strip dist/dapyview  # On Unix-like systems
   ```

4. **Compress for distribution**:
   ```bash
   # macOS/Linux
   tar -czf dapyview-v0.2.0-macos.tar.gz dist/dapyview
   
   # Windows
   zip dapyview-v0.2.0-windows.zip dist/dapyview.exe
   ```

---

## User Installation

### Downloaded Executable:

**macOS**:
```bash
# Download
curl -L -o dapyview https://github.com/xdefago/dapy/releases/download/v0.2.0/dapyview-v0.2.0-macos-arm64

# Make executable
chmod +x dapyview

# Run
./dapyview trace.pkl

# Optional: Move to PATH
sudo mv dapyview /usr/local/bin/
```

**Linux**:
```bash
# Download
wget https://github.com/xdefago/dapy/releases/download/v0.2.0/dapyview-v0.2.0-linux-x86_64

# Make executable
chmod +x dapyview-v0.2.0-linux-x86_64

# Run
./dapyview-v0.2.0-linux-x86_64 trace.pkl
```

**Windows**:
```powershell
# Download from GitHub releases page

# Run
.\dapyview.exe trace.pkl
```

---

## Conclusion

**Recommended approach**: Use **PyInstaller** with **GitHub Actions** to automatically build and release platform-specific executables for macOS, Linux, and Windows.

This provides:
- ✅ Users don't need Python
- ✅ Single download, ready to run
- ✅ Automated build process
- ✅ Cross-platform support
- ✅ Reasonable file sizes (50-150 MB)

Users can simply download the executable for their platform and run `dapyview trace.pkl` without any installation steps.
