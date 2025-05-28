# C:\Users\User\Documents\SISTEMA\mi_proyecto_mapa\app\main.py
import os
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from app.ui.main_window import MainWindow # Importa directamente la clase MainWindow

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta al recurso, funciona tanto en desarrollo como en el ejecutable.
    :param relative_path: Ruta relativa del recurso.
    :return: Ruta absoluta al recurso.
    """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """
    Función principal del programa.
    Crea la aplicación Qt y la ventana principal.
    """
    print("Iniciando la aplicación...")
    app = QApplication(sys.argv)

    try:
        # Crear e iniciar la interfaz gráfica
        print("Creando la ventana principal...")
        window = MainWindow()
        window.show() # Mostrar la ventana

        print("Aplicación lista. Ejecutando ciclo de eventos...")
        sys.exit(app.exec_()) # Iniciar el ciclo de eventos de la aplicación

    except Exception as e:
        # Manejar cualquier error crítico durante la inicialización o ejecución
        print(f"Error crítico durante la ejecución de la aplicación: {e}")
        QMessageBox.critical(None, "Error de Aplicación", f"Ocurrió un error crítico: {e}")
        sys.exit(1) # Salir con código de error

if __name__ == "__main__":
    main()