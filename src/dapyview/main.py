# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Dapy Trace Viewer - Main Application Entry Point."""

import sys
import argparse
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from .trace_window import TraceWindow


def main() -> int:
    """Main entry point for dapyview application.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Enable high DPI scaling for Retina displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    parser = argparse.ArgumentParser(
        prog='dapyview',
        description='dapyview - GUI Trace Viewer for dapy distributed algorithms',
        epilog='Example: dapyview trace.json'
    )
    parser.add_argument(
        'trace_file',
        nargs='?',
        type=Path,
        help='Path to the trace JSON file to open (optional)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='dapyview 0.2.0'
    )
    
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Dapy Trace Viewer")
    app.setOrganizationName("Dapy")
    
    # Open trace file if provided, otherwise show error
    if args.trace_file:
        if args.trace_file.exists():
            try:
                window = TraceWindow(args.trace_file)
                window.show()
            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Error Opening Trace",
                    f"Failed to open trace file:\n{args.trace_file}\n\nError: {str(e)}"
                )
                return 1
        else:
            print(f"Error: File not found: {args.trace_file}", file=sys.stderr)
            return 1
    else:
        # No file specified - show a message or empty window
        QMessageBox.information(
            None,
            "Dapy Trace Viewer",
            "Usage: dapyview <trace_file.json>\n\n"
            "Please specify a trace file to open."
        )
        return 0
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
