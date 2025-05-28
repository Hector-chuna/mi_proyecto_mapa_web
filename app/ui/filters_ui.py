# C:\Users\User\Documents\SISTEMA\mi_proyecto_mapa\app\ui\filters_ui.py

from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QPushButton, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from app.database import (
    connect_to_database,
    close_database_connection,
    fetch_categorias,
    fetch_marcas,
    fetch_vendedores,
    fetch_departamentos,
    fetch_ciudades
)


class FiltersUI(QWidget):
    apply_filters_signal = pyqtSignal(dict)  # Emite los filtros seleccionados
    reset_filters_signal = pyqtSignal()       # Señal cuando se reinician los filtros

    def __init__(self):
        super().__init__()
        print("DEBUG_FILTERS_UI: Inicializando FiltersUI...")
        self._all_categorias = []
        self._all_marcas = []
        self._all_vendedores = []
        self._all_departamentos = []
        self._all_ciudades = []

        self.init_ui()
        print("DEBUG_FILTERS_UI: FiltersUI inicializado.")

    def init_ui(self):
        """Configura la interfaz gráfica de los filtros."""
        print("DEBUG_FILTERS_UI: Configurando la interfaz de filtros...")

        self.filtro_layout = QHBoxLayout(self)
        self.filtro_layout.setContentsMargins(10, 5, 10, 5)
        self.filtro_layout.setSpacing(5)
        self.filtro_layout.setAlignment(Qt.AlignCenter)

        def create_combo_box(placeholder):
            combo = QComboBox()
            combo.addItem(placeholder.upper(), userData=None)
            combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            combo.setFixedHeight(30)
            print(f"DEBUG_FILTERS_UI: ComboBox '{placeholder}' creado.")
            return combo

        self.categoria_combo = create_combo_box("TODAS LAS CATEGORÍAS")
        self.marca_combo = create_combo_box("TODAS LAS MARCAS")
        self.vendedor_combo = create_combo_box("TODOS LOS VENDEDORES")
        self.departamento_combo = create_combo_box("TODOS LOS DEPARTAMENTOS")
        self.ciudad_combo = create_combo_box("TODAS LAS CIUDADES")

        self.filtro_layout.addWidget(self.categoria_combo)
        self.filtro_layout.addWidget(self.marca_combo)
        self.filtro_layout.addWidget(self.vendedor_combo)
        self.filtro_layout.addWidget(self.departamento_combo)
        self.filtro_layout.addWidget(self.ciudad_combo)

        self.aplicar_button = QPushButton("APLICAR FILTROS")
        self.aplicar_button.setObjectName("aplicar_filtro_button")
        self.aplicar_button.setFixedHeight(30)
        self.aplicar_button.clicked.connect(self.on_aplicar_filtros_clicked)
        self.filtro_layout.addWidget(self.aplicar_button)

        self.reset_button = QPushButton("REINICIAR FILTROS")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setFixedHeight(30)
        self.reset_button.clicked.connect(self.on_reset_filters_clicked)
        self.filtro_layout.addWidget(self.reset_button)

        self.categoria_combo.currentIndexChanged.connect(self._update_marca_vendedor_filters)
        self.departamento_combo.currentIndexChanged.connect(self._update_ciudad_filter)

        print("DEBUG_FILTERS_UI: Interfaz de filtros configurada y señales conectadas.")

    def load_initial_data(self, conexion):
        """Carga los datos iniciales para todos los combos de filtro."""
        print("DEBUG_FILTERS_UI: Iniciando carga de datos iniciales para los filtros...")

        try:
            print("DEBUG_FILTERS_UI: Llamando fetch_categorias...")
            self._all_categorias = fetch_categorias(conexion)
            print(f"DEBUG_FILTERS_UI: fetch_categorias regresó: {len(self._all_categorias)} items. Primeros 5: {self._all_categorias[:5]}")

            print("DEBUG_FILTERS_UI: Llamando fetch_marcas...")
            self._all_marcas = fetch_marcas(conexion)
            print(f"DEBUG_FILTERS_UI: fetch_marcas regresó: {len(self._all_marcas)} items. Primeros 5: {self._all_marcas[:5]}")

            print("DEBUG_FILTERS_UI: Llamando fetch_vendedores...")
            self._all_vendedores = fetch_vendedores(conexion)
            print(f"DEBUG_FILTERS_UI: fetch_vendedores regresó: {len(self._all_vendedores)} items. Primeros 5: {self._all_vendedores[:5]}")

            print("DEBUG_FILTERS_UI: Llamando fetch_departamentos...")
            self._all_departamentos = fetch_departamentos(conexion)
            print(f"DEBUG_FILTERS_UI: fetch_departamentos regresó: {len(self._all_departamentos)} items. Primeros 5: {self._all_departamentos[:5]}")

            print("DEBUG_FILTERS_UI: Llamando fetch_ciudades (todas)...")
            self._all_ciudades = fetch_ciudades(conexion)
            print(f"DEBUG_FILTERS_UI: fetch_ciudades regresó: {len(self._all_ciudades)} items. Primeros 5: {self._all_ciudades[:5]}")

            print("DEBUG_FILTERS_UI: Poblado categoria_combo...")
            self._populate_combo_box(self.categoria_combo, self._all_categorias, "TODAS LAS CATEGORÍAS")

            print("DEBUG_FILTERS_UI: Poblado departamento_combo...")
            self._populate_combo_box(self.departamento_combo, self._all_departamentos, "TODOS LOS DEPARTAMENTOS")

            print("DEBUG_FILTERS_UI: Actualizando filtros dependientes (marca/vendedor)...")
            self._update_marca_vendedor_filters()

            print("DEBUG_FILTERS_UI: Actualizando filtro de ciudad...")
            self._update_ciudad_filter()

            print("DEBUG_FILTERS_UI: Datos iniciales de filtros cargados.")

        except Exception as e:
            print(f"ERROR_FILTERS_UI: Error al cargar datos iniciales de los filtros: {e}")

    def _populate_combo_box(self, combo_box, items, placeholder):
        """Rellena un QComboBox con una lista de elementos."""
        print(f"DEBUG_POPULATE: Iniciando _populate_combo_box para '{placeholder}'.")
        original_signal_block_state = combo_box.blockSignals(True)
        print(f"DEBUG_POPULATE: Bloqueando señales para '{placeholder}'.")
        combo_box.clear()
        print(f"DEBUG_POPULATE: ComboBox '{placeholder}' limpiado.")
        combo_box.addItem(placeholder.upper(), userData=None)
        print(f"DEBUG_POPULATE: Placeholder '{placeholder.upper()}' añadido.")
        print(f"DEBUG_POPULATE: Número de ítems a añadir para '{placeholder}': {len(items)}")

        if not items:
            print(f"DEBUG_POPULATE: La lista de ítems para '{placeholder}' está vacía.")

        for i, item in enumerate(items):
            print(f"DEBUG_POPULATE: Procesando ítem {i + 1} para '{placeholder}': {item}")
            if isinstance(item, tuple) and len(item) == 2:
                combo_box.addItem(item[1], userData=item[0])
                print(f"DEBUG_POPULATE: Añadido (tuple): '{item[1]}' con userData='{item[0]}'.")
            elif isinstance(item, dict):
                print(f"DEBUG_POPULATE: Ítem es un diccionario para '{placeholder}': {item}. Intentando extraer id_key/desc_key.")
                try:
                    id_key_candidates = ['id_categoria', 'id_marca', 'id_vend', 'id_dpto', 'id_ciudad']
                    desc_key_candidates = ['descripcion_categoria', 'descripcion_marca', 'descripcion_vend',
                                           'descripcion_dpto', 'descripcion_ciudad']

                    id_key = next((k for k in id_key_candidates if k in item), None)
                    desc_key = next((k for k in desc_key_candidates if k in item), None)

                    if id_key and desc_key:
                        combo_box.addItem(item[desc_key], userData=item[id_key])
                        print(
                            f"DEBUG_POPULATE: Añadido (dict): '{item[desc_key]}' con userData='{item[id_key]}'.")
                    else:
                        print(
                            f"ADVERTENCIA_POPULATE: No se pudieron encontrar id_key o desc_key para el diccionario en '{placeholder}': {item}")
                except Exception as e:
                    print(
                        f"ERROR_POPULATE: Error al procesar diccionario para '{placeholder}': {item}. Error: {e}")
            else:
                print(
                    f"ADVERTENCIA_POPULATE: Formato de ítem inesperado para combo box '{placeholder}': {item}. Tipo: {type(item)}")

        combo_box.blockSignals(original_signal_block_state)
        print(f"DEBUG_POPULATE: Habilitando señales para '{placeholder}'.")
        print(f"DEBUG_POPULATE: Finalizado _populate_combo_box para '{placeholder}'.")

    def _update_marca_vendedor_filters(self):
        """Actualiza los combos de marca y vendedor según la categoría seleccionada."""
        print("DEBUG_FILTERS_UI: Iniciando _update_marca_vendedor_filters...")
        categoria_seleccionada_id = self.categoria_combo.currentData()
        print(f"DEBUG_FILTERS_UI: Categoría seleccionada ID: {categoria_seleccionada_id}")

        marcas_filtradas = self._all_marcas
        vendedores_filtrados = self._all_vendedores

        print("DEBUG_FILTERS_UI: Poblado marca_combo en _update_marca_vendedor_filters...")
        self._populate_combo_box(self.marca_combo, marcas_filtradas, "TODAS LAS MARCAS")

        print("DEBUG_FILTERS_UI: Poblado vendedor_combo en _update_marca_vendedor_filters...")
        self._populate_combo_box(self.vendedor_combo, vendedores_filtrados, "TODOS LOS VENDEDORES")

        print("DEBUG_FILTERS_UI: Finalizado _update_marca_vendedor_filters.")

    def _update_ciudad_filter(self):
        """Actualiza el combo de ciudades según el departamento seleccionado."""
        print("DEBUG_FILTERS_UI: Iniciando _update_ciudad_filter...")
        departamento_seleccionado_id = self.departamento_combo.currentData()
        print(f"DEBUG_FILTERS_UI: Departamento seleccionado ID: {departamento_seleccionado_id}")

        ciudades_filtradas = []

        if departamento_seleccionado_id is not None:
            conexion_local = None
            try:
                print("DEBUG_FILTERS_UI: Conectando localmente para fetch_ciudades...")
                conexion_local = connect_to_database()
                if conexion_local is None:
                    print("ERROR_FILTERS_UI: No se pudo establecer conexión local para actualizar filtros de ciudad.")
                    return
                ciudades_filtradas = fetch_ciudades(conexion_local, departamento_seleccionado_id)
                print(
                    f"DEBUG_FILTERS_UI: fetch_ciudades (filtrado) regresó: {len(ciudades_filtradas)} items. Primeros 5: {ciudades_filtradas[:5]}")
            except Exception as e:
                print(f"ERROR_FILTERS_UI: Error al actualizar filtro de ciudad: {e}")
            finally:
                if conexion_local:
                    close_database_connection(conexion_local)
                    print("DEBUG_FILTERS_UI: Conexión local cerrada.")
        else:
            print("DEBUG_FILTERS_UI: Departamento no seleccionado, usando todas las ciudades.")
            ciudades_filtradas = self._all_ciudades

        print("DEBUG_FILTERS_UI: Poblado ciudad_combo en _update_ciudad_filter...")
        self._populate_combo_box(self.ciudad_combo, ciudades_filtradas, "TODAS LAS CIUDADES")
        print("DEBUG_FILTERS_UI: Finalizado _update_ciudad_filter.")

    def on_aplicar_filtros_clicked(self):
        """Maneja el clic en el botón 'Aplicar Filtros'."""
        filter_params = {
            'id_categoria': self.categoria_combo.currentData(),
            'id_marca': self.marca_combo.currentData(),
            'descripcion_vend': self.vendedor_combo.currentText() if self.vendedor_combo.currentData() is not None else None,
            'id_dpto': self.departamento_combo.currentData(),
            'id_ciudad': self.ciudad_combo.currentData()
        }
        print(f"DEBUG_FILTERS_UI: Filtros aplicados: {filter_params}")
        self.apply_filters_signal.emit(filter_params)

    def on_reset_filters_clicked(self):
        """Maneja el clic en el botón 'Reiniciar Filtros'."""
        print("DEBUG_FILTERS_UI: Reiniciando filtros (on_reset_filters_clicked)...")
        self.reset_filter_comboboxes()
        self.reset_filters_signal.emit()
        print("DEBUG_FILTERS_UI: Señal reset_filters_signal emitida.")

    def reset_filter_comboboxes(self):
        """Reinicia los comboboxes a su estado inicial."""
        print("DEBUG_FILTERS_UI: Iniciando reset_filter_comboboxes...")

        self.categoria_combo.blockSignals(True)
        self.departamento_combo.blockSignals(True)

        self.categoria_combo.setCurrentIndex(0)
        self.departamento_combo.setCurrentIndex(0)

        self.categoria_combo.blockSignals(False)
        self.departamento_combo.blockSignals(False)

        # Forzar actualización de combos dependientes
        print("DEBUG_FILTERS_UI: Forzando actualización de filtros dependientes después de reset.")
        self._update_marca_vendedor_filters()
        self._update_ciudad_filter()

        print("DEBUG_FILTERS_UI: Finalizado reset_filter_comboboxes.")