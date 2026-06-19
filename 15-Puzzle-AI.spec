# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('app.py', '.'), ('core', 'core'), ('algorithms', 'algorithms'), ('ui', 'ui'), ('app-screenshot.png', '.'), ('puzzle-v2.png', '.')]
datas += collect_data_files('streamlit')
datas += copy_metadata('streamlit')
datas += copy_metadata('altair')
datas += copy_metadata('pydeck')


a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['streamlit.web.bootstrap', 'watchdog.observers.winapi', 'webview', 'webview.platforms.edgechromium'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'plotly', 'pytest', 'pyarrow.tests', 'pandas.tests'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='15-Puzzle-AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='15-Puzzle-AI',
)
