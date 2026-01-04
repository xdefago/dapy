# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Package initialization for dapyview."""

try:
    from importlib.metadata import version
    __version__ = version("dapy")  # Read version from pyproject.toml
except Exception:
    __version__ = "0.0.0"  # Fallback if not installed

__all__ = ["TraceViewerApp", "TraceWindow"]

from dapyview.app import TraceViewerApp
from dapyview.trace_window import TraceWindow
