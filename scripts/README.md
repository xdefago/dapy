# Build Scripts

This directory contains scripts for building and packaging dapyview.

## Building Dapyview Standalone Executable

### Quick Build (Local Platform)

```bash
./scripts/build-dapyview.sh
```

This will:
1. Install PyInstaller if needed
2. Build dapyview executable for your platform
3. Place the result in `dist/`

### Manual Build

```bash
# Using the spec file (recommended)
uv run pyinstaller dapyview.spec

# Or using PyInstaller directly
uv run pyinstaller --onefile --windowed src/dapyview/main.py -n dapyview
```

### Output

The build produces platform-specific executables:

- **macOS**: `dist/dapyview-macos-arm64` or `dist/dapyview-macos-x86_64`
- **Linux**: `dist/dapyview-linux-x86_64`
- **Windows**: `dist/dapyview-windows-x86_64.exe`

### Testing

```bash
# Test the built executable
./dist/dapyview-macos-arm64 examples/sample_trace.json
```

### Distribution

Upload the executable from `dist/` to GitHub Releases or distribute directly.

## Automated Builds

For multi-platform builds, use GitHub Actions:

1. Push a version tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

2. GitHub Actions automatically builds for all platforms and creates a release

See `.github/workflows/release-dapyview.yml` for details.

## Notes

- The standalone executable includes both dapy and dapyview code
- dapy library is still available separately for algorithm development
- Users can download just the executable (no Python needed) to view traces
- Users who write algorithms need to install dapy via pip/uv
