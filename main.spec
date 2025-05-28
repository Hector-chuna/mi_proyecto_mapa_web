# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\app\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\mapa_base.html', 'resources/html'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\resources\\css\\Default.css', 'resources/css'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\resources\\css\\leaflet.css', 'resources/css'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\resources\\css\\MarkerCluster.css', 'resources/css'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\resources\\css\\styles.css', 'resources/css')],
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
    name='main',
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
)
