#!/bin/bash
# Code formatting and linting script
# Applies ruff (linting + import sorting + formatting) and black (code formatting)
# All configuration is read from pyproject.toml
# Usage: ./scripts/format-code.sh [options]
# Options:
#   --check    Run in check mode (no modifications)
#   --verbose  Show detailed output

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CHECK_MODE=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./scripts/format-code.sh [--check] [--verbose]"
            exit 1
            ;;
    esac
done

cd "$ROOT_DIR"

echo "==============================================="
echo "Code Formatting and Linting Script"
echo "==============================================="
echo ""

# Determine mode
if [ "$CHECK_MODE" = true ]; then
    echo "Running in CHECK mode (no files will be modified)"
else
    echo "Running in MODIFY mode (files will be updated)"
fi

VERBOSE_FLAG=""
if [ "$VERBOSE" = true ]; then
    VERBOSE_FLAG="--verbose"
fi

echo ""

# Step 1: Run ruff linter
echo "→ Running ruff check (linting)..."
RUFF_CMD="uv run ruff check src tests examples"
if [ "$CHECK_MODE" = true ]; then
    # In check mode, just show issues without fixing
    if $RUFF_CMD $VERBOSE_FLAG; then
        echo "  ✓ Ruff linting passed"
    else
        echo "  ✗ Ruff linting found issues"
        exit 1
    fi
else
    # In modify mode, fix issues
    RUFF_CMD="$RUFF_CMD --fix"
    if $RUFF_CMD $VERBOSE_FLAG; then
        echo "  ✓ Ruff linting and fixes completed"
    fi
fi

echo ""

# Step 2: Run ruff formatter
echo "→ Running ruff format..."
if uv run ruff format src tests examples $VERBOSE_FLAG; then
    echo "  ✓ Ruff formatting completed"
else
    echo "  ✗ Ruff format failed"
    exit 1
fi

echo ""

# Step 3: Run black for code formatting
echo "→ Running black (code formatting)..."
BLACK_CMD="uv run black src tests examples"
if [ "$CHECK_MODE" = true ]; then
    if $BLACK_CMD --check $VERBOSE_FLAG; then
        echo "  ✓ Black formatting check passed"
    else
        echo "  ✗ Black formatting check failed"
        exit 1
    fi
else
    if $BLACK_CMD $VERBOSE_FLAG; then
        echo "  ✓ Black code formatting completed"
    fi
fi

echo ""
echo "==============================================="
if [ "$CHECK_MODE" = true ]; then
    echo "✓ All checks passed!"
else
    echo "✓ Code formatting completed successfully!"
fi
echo "==============================================="
