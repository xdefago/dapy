# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""Dapy Trace Viewer - Main Application Entry Point."""

import sys
import argparse
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog

from dapyview.trace_window import TraceWindow


def open_file_selector() -> List[Path]:
    """Show file dialog to select trace files.
    
    Returns:
        List of selected trace file paths (empty if cancelled).
    """
    file_dialog = QFileDialog()
    file_paths, _ = file_dialog.getOpenFileNames(
        None,
        "Open Trace Files",
        "",
        "Trace Files (*.pkl *.pickle *.json);;Pickle Files (*.pkl *.pickle);;JSON Files (*.json);;All Files (*)"
    )
    return [Path(f) for f in file_paths]


def main() -> int:
    """Main entry point for dapyview application.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    # Enable high DPI scaling for Retina displays
    # Note: AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt6
    # High DPI scaling is now enabled by default
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    parser = argparse.ArgumentParser(
        prog='dapyview',
        description='dapyview - GUI Trace Viewer for dapy distributed algorithms',
        epilog='Examples:\n'
               '  dapyview                    # Open file selector\n'
               '  dapyview trace.pkl          # Open single file\n'
               '  dapyview trace1.pkl trace2.pkl  # Open multiple files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'trace_files',
        nargs='*',
        type=Path,
        help='Path(s) to trace file(s) to open (pickle or JSON format). '
             'If omitted, opens file selector dialog.'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='dapyview 0.3.0'
    )
    
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Dapy Trace Viewer")
    app.setOrganizationName("Dapy")
    
    # Determine which files to open
    trace_files: List[Path] = args.trace_files if args.trace_files else []
    
    # If no files provided, open file selector
    if not trace_files:
        trace_files = open_file_selector()
        if not trace_files:
            # User cancelled - exit gracefully
            return 0
    
    # Confirm if opening many files
    if len(trace_files) > 5:
        reply = QMessageBox.question(
            None,
            "Open Multiple Files",
            f"You are about to open {len(trace_files)} trace files.\n"
            f"Each will open in a separate window.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return 0
    
    # Open each trace file in a separate window
    windows = []
    errors = []
    
    for trace_file in trace_files:
        if not trace_file.exists():
            errors.append(f"File not found: {trace_file}")
            continue
        
        try:
            window = TraceWindow(trace_file)
            window.show()
            windows.append(window)
        except Exception as e:
            errors.append(f"{trace_file.name}: {e!s}")
    
    # Show errors if any
    if errors:
        error_msg = "\n".join(errors)
        QMessageBox.warning(
            None,
            "Error Opening Files",
            f"Failed to open some trace files:\n\n{error_msg}"
        )
        
        # If no windows opened successfully, exit
        if not windows:
            return 1
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
