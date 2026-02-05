#!/bin/bash

# Generate API documentation for dapy using pdoc
# Output: docs/api/

set -e

echo "Generating API documentation for dapy..."
uv run pdoc dapy --output-dir docs/api

echo "✓ API documentation generated successfully!"
echo "Output directory: docs/api/"
