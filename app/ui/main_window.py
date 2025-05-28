import os
import sys
import json
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

# Importar funciones y clases necesarias desde tus módulos
from app import database # Importar el módulo database completo
from app.color_calculator import calculate_colors_and_shapes_for_all_points
from app.map_generator import calculate_statistics

# --- CLASE DataWorker para el hilo separado ---
class DataWorker(QThread):
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, filter_params):
        super().__init__()
        self.filter_params = filter_params

    def run(self):
        conexion = None
        try:
            conexion = database.connect_to_database()
            if conexion is None:
                self.error_occurred.emit("No se pudo conectar a la base de datos en el hilo de datos.")
                return

            print("\n- Cargando y procesando datos en hilo separado -")

            id_categoria = self.filter_params.get('id_categoria')
            id_marca = self.filter_params.get('id_marca')
            descripcion_vend_filtro = self.filter_params.get('descripcion_vend')
            id_dpto = self.filter_params.get('id_dpto')
            id_ciudad = self.filter_params.get('id_ciudad')

            print("- Buscando puntos PREVENTA=1 de la base de datos...")
            puntos_circulos = database.fetch_points_with_last_sale_preventa_1(
                conexion,
                id_categoria=id_categoria,
                id_marca=id_marca,
                descripcion_vend=descripcion_vend_filtro,
                id_dpto=id_dpto,
                id_ciudad=id_ciudad
            )
            print(f"- Encontrados {len(puntos_circulos)} puntos PREVENTA=1.")

            ids_marcas_en_circulos = list(set([p.get('ID_MARCA') for p in puntos_circulos if p.get('ID_MARCA') is not None]))
            print(f"- IDs de marcas únicas en PREVENTA=1 para filtrar diamantes: {len(ids_marcas_en_circulos)}")

            print("- Buscando puntos PREVENTA!=1 de la base de datos...")
            puntos_diamantes = database.fetch_points_with_last_sale_preventa_no_1(
                conexion, ids_marcas=ids_marcas_en_circulos
            )
            print(f"- Encontrados {len(puntos_diamantes)} puntos PREVENTA!=1.")

            print("- Procesando puntos para asignar colores y formas (usando color_calculator)...")
            puntos_para_mapa = calculate_colors_and_shapes_for_all_points(puntos_circulos, puntos_diamantes)
            print(f"- {len(puntos_para_mapa)} puntos listos para el mapa.")

            print("- Calculando estadísticas a partir de puntos procesados (usando map_generator)...")
            estadisticas = calculate_statistics(puntos_para_mapa)

            self.data_loaded.emit({
                'puntos_para_mapa': puntos_para_mapa,
                'estadisticas': estadisticas
            })

        except Exception as e:
            error_msg = f"Error en el hilo de datos: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            if conexion:
                database.close_database_connection(conexion)
                print("- Conexión a la base de datos cerrada en el hilo de datos. -")


# --- CLASE Bridge para la comunicación entre Python y JavaScript ---
class Bridge(QObject):
    filters_applied = pyqtSignal(dict)

    @pyqtSlot(result=str)
    def getInitialFilterData(self):
        print("JS solicitó datos iniciales para los filtros.")
        conexion = None
        try:
            conexion = database.connect_to_database()
            if conexion is None: # Corregido de '==' a 'is' para None
                return json.dumps({"error": "No se pudo conectar a la base de datos para filtros."})

            categorias_raw = database.fetch_categorias(conexion)
            marcas_raw = database.fetch_marcas(conexion)
            vendedores_raw = database.fetch_vendedores(conexion)
            departamentos_raw = database.fetch_departamentos(conexion)
            ciudades_raw = database.fetch_ciudades(conexion)

            # Transformar tuplas a diccionarios para JS
            categorias_formatted = [{"id": item[0], "descripcion": item[1]} for item in categorias_raw]
            marcas_formatted = [{"id": item[0], "descripcion": item[1]} for item in marcas_raw]
            vendedores_formatted = [{"id": item[0], "descripcion": item[1]} for item in vendedores_raw]
            departamentos_formatted = [{"id": item[0], "descripcion": item[1]} for item in departamentos_raw]
            ciudades_formatted = [{"id": item[0], "descripcion": item[1]} for item in ciudades_raw]

            data = {
                "categorias": categorias_formatted,
                "marcas": marcas_formatted,
                "vendedores": vendedores_formatted,
                "departamentos": departamentos_formatted,
                "ciudades": ciudades_formatted
            }
            return json.dumps(data)
        except Exception as e:
            print(f"Error al obtener datos iniciales de filtros: {e}")
            return json.dumps({"error": f"Error al obtener datos iniciales de filtros: {e}"})
        finally:
            if conexion:
                database.close_database_connection(conexion)

    @pyqtSlot(str, result=str)
    def applyFilters(self, json_filter_params):
        print(f"JS llamó a applyFilters con: {json_filter_params}")
        try:
            filter_params = json.loads(json_filter_params)
            
            # Limpiar valores vacíos ('' o 'undefined') a None para que DataWorker los ignore
            for key, value in filter_params.items():
                if value == '' or value == 'undefined':
                    filter_params[key] = None

            self.filters_applied.emit(filter_params)
            return json.dumps({"status": "success", "message": "Filtros aplicados."})
        except Exception as e:
            print(f"Error al procesar applyFilters desde JS: {e}")
            return json.dumps({"status": "error", "message": f"Error al aplicar filtros: {e}"})

    @pyqtSlot(result=str)
    def resetFilters(self):
        print("JS llamó a resetFilters.")
        try:
            self.filters_applied.emit({})
            return json.dumps({"status": "success", "message": "Filtros reiniciados."})
        except Exception as e:
            print(f"Error al procesar resetFilters desde JS: {e}")
            return json.dumps({"status": "error", "message": f"Error al reiniciar filtros: {e}"})

    @pyqtSlot(str, result=str)
    def getFilteredMarcas(self, id_categoria_str):
        print(f"JS solicitó marcas filtradas para categoría: {id_categoria_str}")
        conexion = None
        try:
            conexion = database.connect_to_database()
            if conexion is None:
                return json.dumps({"error": "No se pudo conectar a la base de datos para marcas filtradas."})
            
            id_categoria = int(id_categoria_str) if id_categoria_str and id_categoria_str.isdigit() else None
            
            marcas_raw = database.fetch_marcas(conexion, id_categoria=id_categoria)
            marcas_formatted = [{"id": item[0], "descripcion": item[1]} for item in marcas_raw]
            return json.dumps({"status": "success", "data": marcas_formatted})
        except Exception as e:
            print(f"Error al obtener marcas filtradas: {e}")
            return json.dumps({"status": "error", "message": f"Error al obtener marcas filtradas: {e}"})
        finally:
            if conexion:
                database.close_database_connection(conexion)

    @pyqtSlot(str, result=str)
    def getFilteredVendedores(self, id_categoria_str):
        print(f"JS solicitó vendedores filtrados para categoría: {id_categoria_str}")
        conexion = None
        try:
            conexion = database.connect_to_database()
            if conexion is None:
                return json.dumps({"error": "No se pudo conectar a la base de datos para vendedores filtrados."})
            
            id_categoria = int(id_categoria_str) if id_categoria_str and id_categoria_str.isdigit() else None
            
            vendedores_raw = database.fetch_vendedores(conexion, id_categoria=id_categoria)
            # Ya fetch_vendedores devuelve el formato adecuado (None, descripcion)
            vendedores_formatted = [{"id": item[0], "descripcion": item[1]} for item in vendedores_raw]
            return json.dumps({"status": "success", "data": vendedores_formatted})
        except Exception as e:
            print(f"Error al obtener vendedores filtrados: {e}")
            return json.dumps({"status": "error", "message": f"Error al obtener vendedores filtrados: {e}"})
        finally:
            if conexion:
                database.close_database_connection(conexion)

    @pyqtSlot(str, result=str)
    def getFilteredCiudades(self, id_dpto_str):
        print(f"JS solicitó ciudades filtradas para departamento: {id_dpto_str}")
        conexion = None
        try:
            conexion = database.connect_to_database()
            if conexion is None:
                return json.dumps({"error": "No se pudo conectar a la base de datos para ciudades filtradas."})
            
            id_dpto = int(id_dpto_str) if id_dpto_str and id_dpto_str.isdigit() else None
            
            ciudades_raw = database.fetch_ciudades(conexion, id_dpto=id_dpto)
            ciudades_formatted = [{"id": item[0], "descripcion": item[1]} for item in ciudades_raw]
            return json.dumps({"status": "success", "data": ciudades_formatted})
        except Exception as e:
            print(f"Error al obtener ciudades filtradas: {e}")
            return json.dumps({"status": "error", "message": f"Error al obtener ciudades filtradas: {e}"})
        finally:
            if conexion:
                database.close_database_connection(conexion)


# --- CLASE MainWindow ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa Interactivo")
        self.setGeometry(100, 100, 1200, 800)

        self.data_worker = None
        self.map_loaded_and_ready = False
        self.loaded_data_from_worker = None
        self.current_filter_params = {}

        self.init_ui()
        self.apply_stylesheet()

    def init_ui(self):
        print("- Configurando componentes principales de la UI -")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        print("- Configurando el visor de mapas (QWebEngineView) -")
        self.browser = QWebEngineView()

        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        self.bridge.filters_applied.connect(self.on_apply_filters)

        map_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mapa_base.html')
        map_path = os.path.abspath(map_path)

        if not os.path.exists(map_path):
            print(f"Error: Archivo mapa_base.html no encontrado en {map_path}")
            QMessageBox.critical(self, "Error de Archivo", f"El archivo 'mapa_base.html' no se encuentra en la ruta esperada: {map_path}")
            sys.exit(1)

        print(f"- Archivo mapa_base.html encontrado: {map_path}")
        self.browser.setUrl(QUrl.fromLocalFile(map_path))
        main_layout.addWidget(self.browser)

        self.browser.loadFinished.connect(self.on_map_load_finished)

    def apply_stylesheet(self):
        css_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'css', 'styles.css')
        css_path = os.path.abspath(css_path)

        print(f"- Intentando cargar hoja de estilo CSS desde: {css_path}")
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            print("- Archivo CSS encontrado y aplicado.")
        else:
            print(f"Advertencia: Archivo CSS no encontrado en {css_path}")

    def on_map_load_finished(self, ok):
        if ok:
            print(f"- Mapa HTML cargado completamente. Listo para recibir datos.")
            self.map_loaded_and_ready = True
            # Llama a initPythonBridge en el JS para inicializar la comunicación y cargar los filtros iniciales
            self.browser.page().runJavaScript("window.initPythonBridge();")
            # Inicia la carga inicial de datos (sin filtros al inicio)
            self.on_apply_filters({})
        else:
            print("- Error al cargar el mapa HTML.")
            QMessageBox.warning(self, "Error", "Ocurrió un error al cargar la página del mapa.")

    def on_apply_filters(self, filter_params):
        print("\n- Aplicando filtros (desde JS o inicial). Iniciando carga de datos en hilo de fondo -")
        self.current_filter_params = filter_params
        print(f"Filtros recibidos: {self.current_filter_params}")
        self._start_data_worker(self.current_filter_params)

    def _start_data_worker(self, filter_params):
        if self.data_worker and self.data_worker.isRunning():
            print("Deteniendo worker anterior...")
            self.data_worker.quit()
            self.data_worker.wait()
            print("Worker anterior detenido.")

        self.data_worker = DataWorker(filter_params)
        self.data_worker.data_loaded.connect(self.handle_data_loaded)
        self.data_worker.error_occurred.connect(self.handle_data_error)

        self.data_worker.start()

    def handle_data_loaded(self, data):
        print("\n- Datos recibidos del hilo de fondo. Actualizando UI y mapa -")
        self.loaded_data_from_worker = data
        self.send_data_to_map(data['puntos_para_mapa'], data['estadisticas'])

    def handle_data_error(self, error_message):
        QMessageBox.critical(self, "Error de Carga de Datos", error_message)
        print(f"Error en carga de datos desde hilo: {error_message}")

    def send_data_to_map(self, puntos_para_mapa, estadisticas):
        if not self.map_loaded_and_ready:
            print("Advertencia: Intento de enviar datos antes de que el mapa esté listo.")
            return

        js_data_puntos = json.dumps(puntos_para_mapa)
        js_data_stats = json.dumps(estadisticas)

        print("- Enviando datos filtrados al mapa mediante JavaScript -")

        self.browser.page().runJavaScript(f"window.updateMapAndStats({js_data_puntos}, {js_data_stats});")
        self.browser.page().runJavaScript(f"console.log('Datos de marcadores y estadísticas enviados a JS.');")
        print("- Datos enviados al mapa correctamente.")

    def closeEvent(self, event):
        print("- Cerrando la aplicación -")
        if self.data_worker and self.data_worker.isRunning():
            print("Deteniendo hilo de carga de datos...")
            self.data_worker.quit()
            self.data_worker.wait()
        event.accept()