# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\app\\main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\mapa_base.html', '.'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\app\\db_config.json', 'app'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\app\\resources', 'app/resources'), ('C:\\Users\\User\\Documents\\SISTEMA\\mi_proyecto_mapa\\app\\resources\\css', 'app/resources/css')],
    hiddenimports=['PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebChannel', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'mysql.connector', 'mysql.connector.locales.eng', 'mysql.connector.plugins.mysql_native_password', 'mysql.connector.authentication', 'mysql.connector.cursor', 'mysql.connector.pooling', 'json', 'threading', 'queue'],
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
    name='MapaInteractivo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
