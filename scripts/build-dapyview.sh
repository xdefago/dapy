#!/bin/bash
# Build script for dapyview standalone executables
# Usage: ./scripts/build-dapyview.sh [platform]
# Platform: macos, linux, windows, or all (default: current platform)

set -e

PLATFORM="${1:-auto}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "===================================="
echo "Dapyview Build Script"
echo "===================================="
echo "Platform: $PLATFORM"
echo "Root: $ROOT_DIR"
echo ""

cd "$ROOT_DIR"

# Detect current platform
if [ "$PLATFORM" = "auto" ]; then
    case "$(uname -s)" in
        Darwin*) PLATFORM="macos" ;;
        Linux*)  PLATFORM="linux" ;;
        MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
        *) echo "Unknown platform: $(uname -s)"; exit 1 ;;
    esac
fi

# Check if pyinstaller is available
if ! uv run pyinstaller --version >/dev/null 2>&1; then
    echo "PyInstaller not found. Installing..."
    uv add --dev pyinstaller
fi

echo "Building dapyview executable for $PLATFORM..."
echo ""

# Build with PyInstaller
uv run pyinstaller dapyview.spec

# Rename based on platform and architecture
case "$PLATFORM" in
    macos)
        ARCH=$(uname -m)
        if [ -f "dist/dapyview" ]; then
            mv dist/dapyview "dist/dapyview-macos-${ARCH}"
            echo "✓ Built: dist/dapyview-macos-${ARCH}"
        elif [ -d "dist/dapyview.app" ]; then
            echo "✓ Built: dist/dapyview.app"
        fi
        ;;
    linux)
        if [ -f "dist/dapyview" ]; then
            mv dist/dapyview "dist/dapyview-linux-x86_64"
            echo "✓ Built: dist/dapyview-linux-x86_64"
        fi
        ;;
    windows)
        if [ -f "dist/dapyview.exe" ]; then
            mv dist/dapyview.exe "dist/dapyview-windows-x86_64.exe"
            echo "✓ Built: dist/dapyview-windows-x86_64.exe"
        fi
        ;;
esac

echo ""
echo "===================================="
echo "Build complete!"
echo "===================================="
echo ""
echo "Test the executable:"
case "$PLATFORM" in
    macos)
        echo "  ./dist/dapyview-macos-${ARCH} examples/sample_trace.json"
        ;;
    linux)
        echo "  ./dist/dapyview-linux-x86_64 examples/sample_trace.json"
        ;;
    windows)
        echo "  dist/dapyview-windows-x86_64.exe examples/sample_trace.json"
        ;;
esac
echo ""
echo "Distribute the executable from dist/ directory"
echo ""
