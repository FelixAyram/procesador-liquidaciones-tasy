# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None
ICON_FILE = os.path.join(os.path.dirname(SPEC), 'assets', 'app.ico')
MANIFEST = os.path.join(os.path.dirname(SPEC), 'app.manifest')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'pdfplumber',
        'pdfminer',
        'pdfminer.high_level',
        'pdfminer.layout',
        'pdfminer.pdfpage',
        'pdfminer.pdfinterp',
        'pdfminer.converter',
        'openpyxl',
        'openpyxl.cell._writer',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_dpi.py'],
    excludes=[
        'torch', 'tensorflow', 'matplotlib', 'scipy', 'pandas', 'cv2',
        'sklearn', 'IPython', 'jupyter', 'notebook', 'pytest',
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
    name='ProcesadorLiquidacionesTasy',
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
    icon=ICON_FILE,
    manifest=MANIFEST,
)
