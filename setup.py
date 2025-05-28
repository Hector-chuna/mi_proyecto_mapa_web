import os
import sys
from PyInstaller.__main__ import run

# Define el directorio base del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))

# Rutas importantes del proyecto
resources_app_path = os.path.join(project_root, 'app', 'resources')
mapa_base_html_path = os.path.join(project_root, 'mapa_base.html')
main_script_path = os.path.join(project_root, 'app', 'main.py')

# Archivos de configuración críticos (CORREGIDO: db_config.json está en app/)
db_config_path = os.path.join(project_root, 'app', 'db_config.json')
css_path = os.path.join(project_root, 'app', 'resources', 'css')

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_requeridos = [
        (main_script_path, "Script principal"),
        (mapa_base_html_path, "Archivo HTML del mapa"),
        (db_config_path, "Archivo de configuración de BD (en app/)"),
    ]
    
    directorios_requeridos = [
        (resources_app_path, "Directorio de recursos"),
        (css_path, "Directorio CSS"),
    ]
    
    print("=== VERIFICACIÓN DE ARCHIVOS ===")
    
    # Verificar archivos
    for ruta, descripcion in archivos_requeridos:
        if os.path.exists(ruta):
            print(f"✓ {descripcion}: {ruta}")
        else:
            print(f"✗ FALTA: {descripcion}: {ruta}")
    
    # Verificar directorios
    for ruta, descripcion in directorios_requeridos:
        if os.path.exists(ruta):
            print(f"✓ {descripcion}: {ruta}")
            # Listar contenido del directorio
            try:
                contenido = os.listdir(ruta)
                if contenido:
                    print(f"  → Contenido: {', '.join(contenido[:5])}{'...' if len(contenido) > 5 else ''}")
                else:
                    print(f"  → Directorio vacío")
            except:
                pass
        else:
            print(f"✗ FALTA: {descripcion}: {ruta}")
    
    print("=" * 35)

if __name__ == "__main__":
    print("🚀 INICIANDO CONSTRUCCIÓN DEL EJECUTABLE")
    print(f"📁 Directorio raíz: {project_root}")
    
    # Verificar archivos antes de construir
    verificar_archivos()
    
    # Preguntar si continuar
    respuesta = input("\n¿Continuar con la construcción? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'y', 'yes']:
        print("Construcción cancelada.")
        sys.exit(0)
    
    print(f"\n🔧 Construyendo ejecutable...")
    print(f"📝 Script principal: {main_script_path}")

    pyinstaller_args = [
        '--onefile',          # Genera un único archivo ejecutable
        # '--windowed',       # Descomentado para debuggear - verás la consola
        '--name=MapaInteractivo',
        '--clean',            # Limpia cache de construcciones anteriores
        
        # ARCHIVOS DE DATOS CRÍTICOS
        f'--add-data={mapa_base_html_path};.',          # HTML en raíz
        f'--add-data={db_config_path};app',             # Config de BD en app/
        
        # DIRECTORIO COMPLETO DE RECURSOS
        f'--add-data={resources_app_path};app/resources',  # Mantiene estructura completa
        
        # TODOS LOS ARCHIVOS CSS ESPECÍFICAMENTE
        f'--add-data={css_path};app/resources/css',
        
        # HIDDEN IMPORTS PARA PYQT5
        '--hidden-import=PyQt5.QtWebEngineWidgets',
        '--hidden-import=PyQt5.QtWebChannel',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtGui',
        
        # HIDDEN IMPORTS PARA MYSQL (ajusta según tu conector)
        '--hidden-import=mysql.connector',
        '--hidden-import=mysql.connector.locales.eng',
        '--hidden-import=mysql.connector.plugins.mysql_native_password',
        '--hidden-import=mysql.connector.authentication',
        '--hidden-import=mysql.connector.cursor',
        '--hidden-import=mysql.connector.pooling',
        
        # Si usas PyMySQL en lugar de mysql.connector:
        # '--hidden-import=pymysql',
        # '--hidden-import=pymysql.cursors',
        
        # OTROS IMPORTS COMUNES
        '--hidden-import=json',
        '--hidden-import=threading',
        '--hidden-import=queue',
        
        # CONFIGURACIÓN DE PATHS
        '--paths=.',
        '--workpath=build',   # Directorio de trabajo temporal
        '--distpath=dist',    # Directorio de salida
        
        main_script_path
    ]

    try:
        print("⚙️  Ejecutando PyInstaller...")
        run(pyinstaller_args)
        
        print("\n🎉 ¡CONSTRUCCIÓN COMPLETADA!")
        print(f"📦 Ejecutable creado en: {os.path.join(project_root, 'dist', 'MapaInteractivo.exe')}")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecuta el .exe y revisa si aparecen errores en la consola")
        print("2. Si todo funciona, descomenta '--windowed' y reconstruye")
        print("3. Si hay errores, revisa que todos los archivos estén en las rutas correctas")
        
        # Verificar que el ejecutable se creó
        exe_path = os.path.join(project_root, 'dist', 'MapaInteractivo.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✅ Ejecutable encontrado: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la construcción: {e}")
        print("\n🔍 POSIBLES SOLUCIONES:")
        print("- Verifica que todos los archivos existan en las rutas mostradas arriba")
        print("- Asegúrate de que db_config.json esté en la raíz del proyecto")
        print("- Revisa que el directorio app/resources/css contenga styles.css")
        sys.exit(1)