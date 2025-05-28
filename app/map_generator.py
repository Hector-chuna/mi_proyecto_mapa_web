# map_generator.py (VERSIÓN CON DELEGACIÓN DE EVENTOS)

from collections import defaultdict
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, date, timedelta
from app.color_calculator import calculate_colors_and_shapes_for_all_points
import numpy as np
import folium.elements

# --- CSS GLOBAL para los popups (sin cambios) ---
POPUP_GLOBAL_CSS = """
    <style>
        .popup-content {
            font-family: Arial, sans-serif;
            font-size: 13px;
            line-height: 1.4;
            width: 280px; /* Ancho fijo para el popup */
        }
        .popup-content h4 {
            margin-top: 5px;
            margin-bottom: 10px;
            color: #1f77b4;
            text-align: center;
        }
        .popup-content p {
            margin: 2px 0;
        }
        .popup-content strong {
            color: #333;
        }
        .popup-content hr {
            border: 0;
            height: 1px;
            background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
            margin: 10px 0;
        }
        .hidden-content {
            display: none;
            max-height: 200px;
            overflow-y: auto;
            border-top: 1px dashed #ccc;
            padding-top: 5px;
            margin-top: 5px;
        }
        .toggle-button {
            background-color: #007bff;
            border: none;
            color: white;
            padding: 5px 10px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            margin-top: 10px;
            cursor: pointer;
            border-radius: 4px;
            width: 100%;
        }
        .toggle-button:hover {
            background-color: #0056b3;
        }
    </style>
"""

# JavaScript para la DELEGACIÓN DE EVENTOS
# Este script se ejecutará una sola vez en el iframe principal del mapa.
POPUP_TOGGLE_JS_TEMPLATE = """
    console.log("¡JavaScript de delegación de eventos cargado GLOBALMENTE!");

    // Función que alterna la visibilidad y el texto del botón
    function toggleContent(targetId, buttonElement) {
        var element = document.getElementById(targetId);
        if (element) {
            if (element.style.display === "none" || element.style.display === "") {
                element.style.display = "block";
                buttonElement.innerText = "Ocultar Detalles de Mercadería";
            } else {
                element.style.display = "none";
                buttonElement.innerText = "Ver Más Detalles de Mercadería";
            }
            console.log("Contenido alternado para ID:", targetId);
        } else {
            console.warn("Elemento con ID " + targetId + " no encontrado para alternar.");
        }
    }

    // Delegación de eventos: Escuchar clics en el cuerpo del documento
    // Cuando se hace clic en cualquier parte, verificamos si el clic fue en un botón de alternancia.
    document.body.addEventListener('click', function(event) {
        // console.log("Clic detectado en el body."); // Para depuración
        var target = event.target;

        // Si el elemento clicado tiene la clase 'toggle-button'
        if (target && target.classList.contains('toggle-button')) {
            var targetId = target.getAttribute('data-target-id');
            if (targetId) {
                console.log("Botón de popup clicado. Target ID:", targetId);
                toggleContent(targetId, target);
            }
        }
    });
"""

def process_points_for_map(puntos_preventa_1_raw, puntos_preventa_no_1_raw, filters_dict):
    # ... (esta función no cambia) ...
    print("--- [map_generator.py] Iniciando procesamiento de puntos para el mapa ---")

    if not isinstance(puntos_preventa_1_raw, list):
        print("--- [map_generator.py] Convirtiendo puntos_preventa_1_raw a lista.")
        puntos_preventa_1_raw = list(puntos_preventa_1_raw)
    if not isinstance(puntos_preventa_no_1_raw, list):
        print("--- [map_generator.py] Convirtiendo puntos_preventa_no_1_raw a lista.")
        puntos_preventa_no_1_raw = list(puntos_preventa_no_1_raw)

    print("--- [map_generator.py] Llamando a calculate_colors_and_shapes_for_all_points para combinar y procesar puntos.")
    all_processed_points = calculate_colors_and_shapes_for_all_points(puntos_preventa_1_raw, puntos_preventa_no_1_raw)
    print(f"--- [map_generator.py] Puntos después de asignar colores y formas: {len(all_processed_points)} ---")

    df_map_points = pd.DataFrame()
    statistics = {}

    if not all_processed_points:
        print("--- [map_generator.py] No hay puntos válidos después de asignar colores y formas. Retornando DataFrame vacío y estadísticas vacías.")
        statistics = {
            'total_general_clientes': 0,
            'total_circles': 0, 'circles_green': 0, 'circles_orange': 0, 'circles_red': 0, 'circles_black': 0,
            'total_diamonds': 0, 'diamonds_green': 0, 'diamonds_orange': 0, 'diamonds_red': 0, 'diamonds_black': 0
        }
        return df_map_points, statistics

    print("--- [map_generator.py] Convirtiendo la lista de puntos a DataFrame.")
    df_map_points = pd.DataFrame(all_processed_points)

    df_map_points['LATITUD'] = pd.to_numeric(df_map_points['LATITUD'], errors='coerce')
    df_map_points['LONGITUD'] = pd.to_numeric(df_map_points['LONGITUD'], errors='coerce')
    df_map_points.dropna(subset=['LATITUD', 'LONGITUD'], inplace=True)

    print("--- [map_generator.py] Calculando estadísticas de los puntos.")
    statistics = calculate_statistics(all_processed_points)

    print("--- [map_generator.py] Procesamiento de puntos para el mapa completado ---")
    return df_map_points, statistics


def generate_folium_map(df_map_points):
    """
    Genera un objeto mapa de Folium a partir de un DataFrame de puntos.
    """
    print("--- [map_generator.py] Iniciando creación del objeto mapa de Folium ---")
    print(f"--- [map_generator.py] DataFrame de entrada para el mapa (shape): {df_map_points.shape} ---")

    if not df_map_points.empty and 'LATITUD' in df_map_points.columns and 'LONGITUD' in df_map_points.columns:
        print("--- [map_generator.py] Calculando centro del mapa basado en puntos existentes.")
        center_lat = df_map_points['LATITUD'].mean()
        center_lon = df_map_points['LONGITUD'].mean()
    else:
        print("--- [map_generator.py] DataFrame de puntos vacío o sin coordenadas válidas. Centrando en Paraguay.")
        center_lat, center_lon = -23.4425, -58.4438

    print(f"--- [map_generator.py] Centro del mapa: LAT={center_lat}, LON={center_lon}, Zoom=6 ---")
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
    print("--- [map_generator.py] Objeto folium.Map creado.")

    # INYECTAR SÓLO EL CSS GLOBAL
    m.get_root().header.add_child(folium.elements.Element(POPUP_GLOBAL_CSS))
    print("--- [map_generator.py] CSS global inyectado en el mapa. ---")

    # ¡¡¡INYECCIÓN GLOBAL DEL JAVASCRIPT CON DELEGACIÓN DE EVENTOS!!!
    # Se inyecta el script dentro de las etiquetas <script> en el body del mapa.
    # Esto asegura que el listener esté disponible globalmente.
    js_global_injection = f"<script>{POPUP_TOGGLE_JS_TEMPLATE}</script>"
    m.get_root().html.add_child(folium.elements.Element(js_global_injection))
    print("--- [map_generator.py] JavaScript global de delegación de eventos inyectado en el mapa. ---")


    marker_cluster = MarkerCluster().add_to(m)
    print("--- [map_generator.py] MarkerCluster añadido al mapa. ---")

    points_added_count = 0
    for idx, row in df_map_points.iterrows():
        lat = row.get('LATITUD')
        lon = row.get('LONGITUD')

        if pd.isna(lat) or pd.isna(lon) or not isinstance(lat, (float, int)) or not isinstance(lon, (float, int)):
            print(f"Advertencia: Saltando punto con coordenadas inválidas/nulas para ID_CLIENTE {row.get('ID_CLIENTE', 'N/A')}: Lat={lat}, lon={lon}")
            continue

        color = row['color']
        shape = row['shape']

        # El popup_html ya viene con los IDs formateados desde color_calculator
        # y ahora NO CONTIENE EL ONCLICK (el JS lo maneja).
        popup_html_content = row['popup_html']

        first_letter_vend = row.get('first_letter_vend', '?')

        icon_size = (24, 24)
        icon_anchor = (icon_size[0] // 2, icon_size[1] // 2)

        icon_html = ""

        # Crear el objeto Popup.
        # ¡¡¡AHORA SOLO PASAMOS EL HTML PURO!!!
        # El JS global se encarga de los eventos.
        popup = folium.Popup(
            popup_html_content, # ¡No más folium.Html(..., script=...) aquí!
            max_width=300
        )

        if shape == 'circle':
            icon_html = f"""
            <div style="
                width: {icon_size[0]}px;
                height: {icon_size[1]}px;
                background-color: {color};
                border-radius: 50%;
                border: 1px solid white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                color: white;
                line-height: 1;
            ">{first_letter_vend}</div>
            """

            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=icon_size,
                    icon_anchor=icon_anchor,
                    html=icon_html
                ),
                popup=popup
            ).add_to(marker_cluster)

        elif shape == 'diamond':
            icon_html = f"""
            <div style="
                font-family: Arial, sans-serif;
                font-weight: bold;
                font-size: 14px;
                color: white;
                background-color: {color};
                width: {icon_size[0]}px;
                height: {icon_size[1]}px;
                border-radius: 4px;
                transform: rotate(45deg);
                display: flex;
                justify-content: center;
                align-items: center;
                border: 2px solid white;
                box-shadow: 0 0 5px rgba(0,0,0,0.5);
            ">
                <span style="transform: rotate(-45deg); display: inline-block; line-height: 1;">{first_letter_vend}</span>
            </div>
            """

            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=icon_size,
                    icon_anchor=icon_anchor,
                    html=icon_html
                ),
                popup=popup
            ).add_to(marker_cluster)

        points_added_count += 1

    print(f"--- [map_generator.py] Total de puntos añadidos al mapa: {points_added_count} ---")
    print("--- [map_generator.py] Objeto mapa de Folium creado y configurado. Retornando 'm'. ---")
    return m


def calculate_statistics(puntos_para_mapa):
    # ... (esta función no cambia) ...
    """
    Calcula las estadísticas de círculos y diamantes a partir de los puntos ya procesados
    (que ya tienen 'color' y 'shape' asignados).
    """
    print("--- [map_generator.py] Calculando estadísticas a partir de puntos procesados...")

    conteo_circle = defaultdict(int)
    conteo_diamond = defaultdict(int)

    clientes_unicos = set()
    for punto in puntos_para_mapa:
        if isinstance(punto, dict) and punto.get("id_cliente") is not None:
            clientes_unicos.add(punto["id_cliente"])

    total_clientes = len(clientes_unicos)

    for punto in puntos_para_mapa:
        if isinstance(punto, dict) and 'color' in punto and 'shape' in punto:
            color = punto["color"]
            shape = punto["shape"]

            if shape == "circle":
                conteo_circle[color] += 1
            elif shape == "diamond":
                conteo_diamond[color] += 1

    print(f"--- [map_generator.py] Total de puntos procesados para estadísticas: {len(puntos_para_mapa)}")
    print("--- [map_generator.py] Estadísticas calculadas. ---")

    return {
        'total_general_clientes': total_clientes,
        'total_circles': sum(conteo_circle.values()),
        'circles_green': conteo_circle.get('green', 0),
        'circles_orange': conteo_circle.get('orange', 0),
        'circles_red': conteo_circle.get('red', 0),
        'circles_black': conteo_circle.get('black', 0),
        'total_diamonds': sum(conteo_diamond.values()),
        'diamonds_green': conteo_diamond.get('green', 0),
        'diamonds_orange': conteo_diamond.get('orange', 0),
        'diamonds_red': conteo_diamond.get('red', 0),
        'diamonds_black': conteo_diamond.get('black', 0)
    }