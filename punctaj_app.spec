# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    [r'd:\punctaj\punctaj.py'],
    pathex=[],
    binaries=[],
    datas=[
        (r'd:\punctaj\data', 'data'),
        (r'd:\punctaj\arhiva', 'arhiva'),
        (r'd:\punctaj\logs', 'logs'),
        (r'd:\punctaj\supabase_config.ini', '.'),
        (r'd:\punctaj\discord_config.ini', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'supabase',
        'supabase.lib.query_options',
        'realtime',
        'postgrest',
        'requests',
        'schedule',
        'discord',
        'json',
        'csv',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='punctaj',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='punctaj'
)
