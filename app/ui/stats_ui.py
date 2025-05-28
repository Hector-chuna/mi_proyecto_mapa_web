from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

def setup_stats(window):
    """
    Configura los botones flotantes para estadísticas, posicionándolos debajo de los filtros.
    :param window: La ventana principal (MainWindow).
    """
    print("- Configurando contenedores flotantes para estadísticas -")

    # Calcular la altura aproximada de la barra de filtros
    filter_bar_height = 40  # Ajusta este valor según la altura real de tu barra de filtros

    # Posición inicial vertical para el primer widget de estadísticas
    initial_y_position = 20 + filter_bar_height + 10  # Deja un pequeño espacio debajo de los filtros

    # Widget para Total de Clientes
    window.total_clientes_widget = QWidget(window)
    window.total_clientes_widget.setObjectName("totalClientesWidget")
    total_clientes_layout = QVBoxLayout(window.total_clientes_widget)
    total_clientes_layout.setContentsMargins(5, 5, 5, 5)  # Márgenes reducidos
    total_clientes_layout.setSpacing(0)  # Sin espacio entre elementos
    window.total_clientes_widget.setLayout(total_clientes_layout)
    window.total_clientes_widget.setAttribute(Qt.WA_StyledBackground, True)  # Permite aplicar CSS al fondo

    window.total_clientes_button = QPushButton("TOTAL CLIENTES\n0")
    window.total_clientes_button.setObjectName("total_clientes_button")
    window.total_clientes_button.setStyleSheet("""
        background-color: #1e90ff; /* Azul claro */
        color: white;
        font-weight: bold;
        padding: 5px;
        text-align: center;
        border-radius: 5px;
    """)
    window.total_clientes_button.setFixedSize(200, 80)  # Tamaño ajustado
    total_clientes_layout.addWidget(window.total_clientes_button)

    window.total_clientes_widget.adjustSize()  # Ajustar tamaño del contenedor
    window.total_clientes_widget.move(20, initial_y_position)  # Posición inicial
    window.total_clientes_widget.raise_()

    # Widget para Círculos
    window.circulos_widget = QWidget(window)
    window.circulos_widget.setObjectName("circulosWidget")
    circulos_layout = QVBoxLayout(window.circulos_widget)
    circulos_layout.setContentsMargins(5, 5, 5, 5)  # Márgenes reducidos
    circulos_layout.setSpacing(0)  # Sin espacio entre elementos
    window.circulos_widget.setLayout(circulos_layout)
    window.circulos_widget.setAttribute(Qt.WA_StyledBackground, True)  # Permite aplicar CSS al fondo

    window.circulos_button = QPushButton("CÍRCULOS\nPts. SIN Mercadería\nVerde: 0\nNaranja: 0\nRojo: 0\nNegro: 0")
    window.circulos_button.setObjectName("circulos_button")
    window.circulos_button.setStyleSheet("""
        background-color: #4682b4; /* Azul marino */
        color: white;
        font-weight: bold;
        padding: 5px;
        text-align: left;
        border-radius: 5px;
    """)
    window.circulos_button.setFixedSize(200, 120)  # Tamaño ajustado
    circulos_layout.addWidget(window.circulos_button)

    window.circulos_widget.adjustSize()  # Ajustar tamaño del contenedor
    window.circulos_widget.move(20, initial_y_position + 90)  # Debajo del primer botón
    window.circulos_widget.raise_()

    # Widget para Diamantes
    window.diamantes_widget = QWidget(window)
    window.diamantes_widget.setObjectName("diamantesWidget")
    diamantes_layout = QVBoxLayout(window.diamantes_widget)
    diamantes_layout.setContentsMargins(5, 5, 5, 5)  # Márgenes reducidos
    diamantes_layout.setSpacing(0)  # Sin espacio entre elementos
    window.diamantes_widget.setLayout(diamantes_layout)
    window.diamantes_widget.setAttribute(Qt.WA_StyledBackground, True)  # Permite aplicar CSS al fondo

    window.diamantes_button = QPushButton("DIAMANTES\nPts. CON/Merc. en Tránsito\nVerde: 0\nNaranja: 0\nRojo: 0\nNegro: 0")
    window.diamantes_button.setObjectName("diamantes_button")
    window.diamantes_button.setStyleSheet("""
        background-color: #ff6347; /* Rojo anaranjado */
        color: white;
        font-weight: bold;
        padding: 5px;
        text-align: left;
        border-radius: 5px;
    """)
    window.diamantes_button.setFixedSize(200, 120)  # Tamaño ajustado
    diamantes_layout.addWidget(window.diamantes_button)

    window.diamantes_widget.adjustSize()  # Ajustar tamaño del contenedor
    window.diamantes_widget.move(20, initial_y_position + 220)  # Debajo del segundo botón
    window.diamantes_widget.raise_()

    # Función para actualizar las estadísticas dinámicamente
    def update_stats():
        try:
            # Verificar que las estadísticas existan en la ventana principal
            if not hasattr(window, "total_clientes") or not hasattr(window, "conteo_circle") or not hasattr(window, "conteo_diamond"):
                print("Error: Las estadísticas no están definidas en la ventana principal.")
                return

            # Actualizar Total de Clientes
            total_clientes_text = f"TOTAL CLIENTES\n{window.total_clientes}"
            window.total_clientes_button.setText(total_clientes_text)

            # Imprimir los diccionarios antes de actualizar los botones
            print("Contenido de window.conteo_circle en update_stats:", window.conteo_circle)
            print("Contenido de window.conteo_diamond en update_stats:", window.conteo_diamond)

            # Actualizar Círculos
            circulos_text = (
                "CÍRCULOS\nPts. SIN/Merc. en Tránsito"
                f"\nVerde: {window.conteo_circle.get('green', 0)}"  # Clave en inglés
                f"\nNaranja: {window.conteo_circle.get('orange', 0)}" # Clave en inglés
                f"\nRojo: {window.conteo_circle.get('red', 0)}"    # Clave en inglés
                f"\nNegro: {window.conteo_circle.get('black', 0)}"  # Clave en inglés
            )
            window.circulos_button.setText(circulos_text)

            # Actualizar Diamantes
            diamantes_text = (
                "DIAMANTES\nPts. CON/Merc. en Tránsito"
                f"\nVerde: {window.conteo_diamond.get('green', 0)}"  # Clave en inglés
                f"\nNaranja: {window.conteo_diamond.get('orange', 0)}" # Clave en inglés
                f"\nRojo: {window.conteo_diamond.get('red', 0)}"    # Clave en inglés
                f"\nNegro: {window.conteo_diamond.get('black', 0)}"  # Clave en inglés
            )
            window.diamantes_button.setText(diamantes_text)

        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
            QMessageBox.warning(window, "Error", "Ocurrió un error al actualizar las estadísticas.")

    # Guardar la función de actualización en la ventana principal
    window.update_stats = update_stats

    # Llamar a la función de actualización inicialmente
    update_stats()
