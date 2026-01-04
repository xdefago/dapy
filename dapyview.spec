# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for building dapyview standalone executable
#
# Usage:
#   pyinstaller dapyview.spec
#
# This creates a standalone executable in dist/dapyview (or dapyview.exe on Windows)
# that can be distributed without requiring Python installation.
#
# Note: This only packages dapyview (the GUI trace viewer).
# The dapy library is still available separately via pip/uv for algorithm development.

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys

block_cipher = None

# Collect all dapy and dapyview modules
dapy_hidden_imports = collect_submodules('dapy')
dapyview_hidden_imports = collect_submodules('dapyview')

a = Analysis(
    ['src/dapyview/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include dapy source (needed by dapyview at runtime)
        ('src/dapy', 'dapy'),
        # Include dapyview source
        ('src/dapyview', 'dapyview'),
    ],
    hiddenimports=[
        # Qt/PySide6 modules
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        
        # Required packages
        'classifiedjson',
        'networkx',
        'numpy',
        
        # Dapy modules (needed for trace loading)
        *dapy_hidden_imports,
        *dapyview_hidden_imports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'pytest',
        'black',
        'isort',
        'ruff',
        'pdoc',
        'tkinter',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dapyview',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression for smaller file size
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,  # macOS: enable drag-and-drop
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file: 'resources/icon.icns' (macOS) or 'resources/icon.ico' (Windows)
)

# macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='dapyview.app',
        icon=None,  # TODO: Add 'resources/icon.icns'
        bundle_identifier='com.github.xdefago.dapyview',
        info_plist={
            'CFBundleName': 'Dapyview',
            'CFBundleDisplayName': 'Dapy Trace Viewer',
            'CFBundleGetInfoString': 'Trace viewer for distributed algorithms',
            'CFBundleVersion': '0.2.0',
            'CFBundleShortVersionString': '0.2.0',
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support Dark Mode
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Dapy Trace File',
                    'CFBundleTypeRole': 'Viewer',
                    'LSHandlerRank': 'Owner',
                    'LSItemContentTypes': ['public.json'],
                    'CFBundleTypeExtensions': ['json'],
                }
            ],
        },
    )
