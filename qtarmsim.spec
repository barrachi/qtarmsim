# -*- mode: python ; coding: utf-8 -*-
# qtarmsim.spec — PyInstaller spec for all platforms
#
# Run from the project root:
#   pyinstaller qtarmsim.spec

import sys
import os
import platform as _platform

# ── Platform-specific gcc-arm subdirectory ────────────────────────────────────
if sys.platform == 'win32':
    _gcc_arch = 'win64'
elif sys.platform == 'darwin':
    _gcc_arch = 'macosARM' if _platform.machine() == 'arm64' else 'macos'
else:
    _m = _platform.machine()
    if _m == 'aarch64':
        _gcc_arch = 'linuxARM'
    elif _m == 'i686':
        _gcc_arch = 'linux32'
    else:
        _gcc_arch = 'linux64'

_src = 'src/qtarmsim'
_gcc_src = os.path.join(_src, 'gcc-arm', _gcc_arch)

datas = [
    # In-process simulator firmware
    (os.path.join(_src, 'armsim', 'armsim_module', 'Firmware.o'),
     'qtarmsim/armsim/armsim_module'),
    # Example programs
    (os.path.join(_src, 'examples'), 'qtarmsim/examples'),
    # Built-in help
    (os.path.join(_src, 'html'),     'qtarmsim/html'),
    # Translations
    (os.path.join(_src, 'lang'),     'qtarmsim/lang'),
]

# Include the ARM cross-compiler for this platform if present
if os.path.isdir(_gcc_src):
    datas.append((_gcc_src, f'qtarmsim/gcc-arm/{_gcc_arch}'))

a = Analysis(
    [os.path.join(_src, '__init__.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='qtarmsim',
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
    icon=os.path.join(_src, 'res', 'images', 'qtarmsim.ico') if sys.platform == 'win32' else None,
)
