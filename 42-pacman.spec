# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller recipe for the packaged 42 Pac-Man executable."""

import sys


datas = [
    ("resources", "resources"),
    ("config.json", "."),
    ("README.md", "."),
]

a = Analysis(
    ["pac-man.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["flake8", "mypy"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="42-pacman",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="42-pacman.app",
        icon=None,
        bundle_identifier="com.pacman.42",
    )
