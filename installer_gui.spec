# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Punctaj Manager GUI Installer

a = Analysis(
    ['installer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('discord_config.ini', '.'),
        ('supabase_config.ini', '.'),
        ('json_encryptor.py', '.'),
        ('dist/punctaj.exe', '.'),  # Include main app executable in bundle
    ],
    hiddenimports=[
        'tkinter',
        'winreg',
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
    name='Punctaj_Manager_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # NO CONSOLE WINDOW!
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
