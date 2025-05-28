from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QUrl
import os

def setup_map(window):
    """
    Configura el visor de mapas en la interfaz.
    """
    print("- Configurando el visor de mapas -")

    # Utilizar el QWebEngineView ya creado en MainWindow
    web_view = window.map_view
    web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Ruta AL ABSOLUTO al archivo mapa_base.html
    map_html_path = "C:/Users/User/Documents/SISTEMA/mi_proyecto_mapa/mapa_base.html"
    if os.path.exists(map_html_path):
        print(f"- Archivo mapa_base.html encontrado: {map_html_path}")
        mapa_url = QUrl.fromLocalFile(map_html_path)
        web_view.load(mapa_url)
    else:
        print(f"- Error: Archivo mapa_base.html NO encontrado en la ruta: {map_html_path}")
        # Aquí podrías mostrar un mensaje de error al usuario usando QMessageBox
        # Por ejemplo:
        # from PyQt5.QtWidgets import QMessageBox
        # QMessageBox.critical(window, "Error", f"No se encontró el archivo del mapa en: {map_html_path}")

    # Ya no es necesario añadir el visor al layout aquí, ya se hizo en MainWindow.__init__
    # window.main_layout.addWidget(web_view)
