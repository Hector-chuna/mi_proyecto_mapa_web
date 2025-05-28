import streamlit as st
import os
import pandas as pd
import folium
from streamlit_folium import folium_static # Asegurado de usar folium_static
from folium.plugins import MarkerCluster
import json
import sys

# Importar tus módulos existentes
from app.database import (
    connect_to_database,
    fetch_categorias,
    fetch_marcas,
    fetch_vendedores,
    fetch_departamentos,
    fetch_ciudades,
    fetch_points_with_last_sale_preventa_1,
    fetch_points_with_last_sale_preventa_no_1
)
# Asegúrate de importar generate_folium_map desde map_generator
from app.map_generator import process_points_for_map, generate_folium_map
# --- 1. Funciones de Utilidad (get_resource_path y load_db_config_streamlit) ---

def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso, compatible con Streamlit Cloud.
    Cuando se despliega, los archivos están en el directorio raíz del app.
    """
    print(f"--- [app.py] Buscando recurso: {relative_path} ---")
    if os.path.exists(os.path.join(os.path.dirname(__file__), relative_path)):
        base_path = os.path.dirname(__file__)
        print(f"--- [app.py] Ruta base encontrada (directorio actual): {base_path} ---")
    elif os.path.exists(os.path.join(os.path.dirname(__file__), 'app', relative_path)):
        base_path = os.path.join(os.path.dirname(__file__), 'app')
        print(f"--- [app.py] Ruta base encontrada (subdirectorio 'app'): {base_path} ---")
    else:
        base_path = os.getcwd()
        print(f"--- [app.py] Ruta base por defecto (directorio de trabajo): {base_path} ---")

    full_path = os.path.join(base_path, relative_path)
    print(f"--- [app.py] Ruta completa del recurso: {full_path} ---")
    return full_path
def load_db_config_streamlit():
    """
    Carga la configuración de la base de datos EXCLUSIVAMENTE desde Streamlit Secrets.
    """
    print("--- [app.py] Intentando cargar configuración de DB desde Streamlit Secrets. ---")
    if "HOST" in st.secrets: # Usamos st.secrets en lugar de os.environ
        st.info("Cargando configuración de DB desde Streamlit Secrets.")
        print("--- [app.py] Configuración de DB cargada desde Streamlit Secrets. ---")
        return {
            "host": st.secrets["HOST"], # st.secrets en lugar de os.environ
            "port": st.secrets["PORT"],  # st.secrets en lugar de os.environ
            "user": st.secrets["USER"],  # st.secrets en lugar de os.environ
            "password": st.secrets["PASSWORD"], # st.secrets en lugar de os.environ
            "database": st.secrets["DATABASE"] # st.secrets en lugar de os.environ
        }
    else:
        st.error("Error: No se encontraron las variables de configuración de la base de datos en Streamlit Secrets.")
        print("--- [app.py] ERROR: No se encontraron las variables de configuración de la base de datos en Streamlit Secrets. ---")
        st.stop()


# --- 3. Conexión a la Base de Datos Cacheada con st.cache_resource ---

@st.cache_resource(ttl="1h", show_spinner="Conectando a la base de datos...")
def get_database_connection(db_config_streamlit):
    """
    Función cacheada para obtener la conexión a la base de datos.
    Reutiliza la conexión a través de las reruns de la aplicación.
    """
    print("--- [app.py] Intentando obtener conexión a la base de datos... ---")
    conn = connect_to_database(db_config_streamlit)
    if not conn:
        st.error("❌ No se pudo establecer conexión a la base de datos.")
        st.warning("🔧 Verifica la configuración en `app/db_config.json` o las Streamlit Secret Variables.")
        print("--- [app.py] ERROR: Falló la conexión a la base de datos. ---")
        st.stop()
    print("--- [app.py] Conexión a la base de datos establecida exitosamente. ---")
    return conn

# --- Funciones para cargar opciones de selectbox (CACHED) ---
# AÑADIMOS '_' AL PARÁMETRO 'conn' para que Streamlit NO intente hashear la conexión
@st.cache_data(ttl="1h", show_spinner=False)
def get_categorias_options(_conn):
    print("--- [app.py] Cargando opciones de categorías... ---")
    categorias_raw = fetch_categorias(_conn)
    categorias_map = {c[1]: c[0] for c in categorias_raw}
    print(f"--- [app.py] Categorías cargadas: {len(categorias_map)} ---")
    return ["Todas"] + sorted(list(categorias_map.keys())), categorias_map

@st.cache_data(ttl="1h", show_spinner=False)
def get_marcas_options(_conn, id_categoria):
    print(f"--- [app.py] Cargando opciones de marcas para categoría ID: {id_categoria}... ---")
    marcas_raw = fetch_marcas(_conn, id_categoria=id_categoria)
    marcas_map = {m[1]: m[0] for m in marcas_raw}
    print(f"--- [app.py] Marcas cargadas: {len(marcas_map)} ---")
    return ["Todas"] + sorted(list(marcas_map.keys())), marcas_map

@st.cache_data(ttl="1h", show_spinner=False)
def get_vendedores_options(_conn, id_categoria):
    print(f"--- [app.py] Cargando opciones de vendedores para categoría ID: {id_categoria}... ---")
    vendedores_raw = fetch_vendedores(_conn, id_categoria=id_categoria)
    vendedores_map = {v[1]: v[0] for v in vendedores_raw}
    print(f"--- [app.py] Vendedores cargados: {len(vendedores_map)} ---")
    return ["Todos"] + sorted(list(vendedores_map.keys())), vendedores_map

@st.cache_data(ttl="1h", show_spinner=False)
def get_departamentos_options(_conn):
    print("--- [app.py] Cargando opciones de departamentos... ---")
    departamentos_raw = fetch_departamentos(_conn)
    departamentos_map = {d[1]: d[0] for d in departamentos_raw}
    print(f"--- [app.py] Departamentos cargados: {len(departamentos_map)} ---")
    return ["Todos"] + sorted(list(departamentos_map.keys())), departamentos_map

@st.cache_data(ttl="1h", show_spinner=False)
def get_ciudades_options(_conn, id_dpto):
    print(f"--- [app.py] Cargando opciones de ciudades para departamento ID: {id_dpto}... ---")
    ciudades_raw = fetch_ciudades(_conn, id_dpto=id_dpto)
    ciudades_map = {c[1]: c[0] for c in ciudades_raw}
    print(f"--- [app.py] Ciudades cargadas: {len(ciudades_map)} ---")
    return ["Todas"] + sorted(list(ciudades_map.keys())), ciudades_map

# --- Configuración de la página y CSS (sin cambios) ---

st.set_page_config(
    page_title="Mapa Interactivo - Mi Empresa",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)
print("--- [app.py] Configuración de la página Streamlit aplicada. ---")

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.success-message {
    color: #28a745;
    font-weight: bold;
}
.error-message {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
print("--- [app.py] Estilos CSS personalizados inyectados. ---")

# --- Funciones de Autenticación (sin cambios) ---

def authenticate_user(username, password):
    """Función simple de autenticación"""
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "mapa123456"
    return username == VALID_USERNAME and password == VALID_PASSWORD

def show_login_page():
    """Muestra la página de login"""
    print("--- [app.py] Mostrando página de login. ---")
    st.markdown('<h1 class="main-header">🔐 Acceso al Sistema</h1>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            with st.form("login_form"):
                st.subheader("Iniciar Sesión")
                username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
                password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
                submitted = st.form_submit_button("🚀 Entrar", use_container_width=True)
                if submitted:
                    print("--- [app.py] Formulario de login enviado. ---")
                    if username and password:
                        if authenticate_user(username, password):
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.success("✅ ¡Login exitoso! Redirigiendo...")
                            print("--- [app.py] Login exitoso. ---")
                            st.rerun() # Para recargar la página y mostrar la app principal
                        else:
                            st.error("❌ Usuario o contraseña incorrectos")
                            print("--- [app.py] Login fallido: credenciales incorrectas. ---")
                    else:
                        st.warning("⚠️ Por favor, complete todos los campos")
                        print("--- [app.py] Login fallido: campos vacíos. ---")
            st.markdown('</div>', unsafe_allow_html=True)
            with st.expander("ℹ️ Información"):
                st.info("""
                **Credenciales de acceso:**
                - Usuario: admin
                - Contraseña: mapa123456

                Si tienes problemas para acceder, contacta al administrador del sistema.
                """)
    print("--- [app.py] Página de login renderizada. ---")

# --- Función Principal de la Aplicación (show_main_app) ---

def show_main_app():
    """Muestra la aplicación principal después del login"""
    print("--- [app.py] Mostrando la aplicación principal. ---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<h1 class="main-header">🗺️ Mapa Interactivo - Mi Empresa</h1>', unsafe_allow_html=True)
    with col3:
        st.write(f"👤 Usuario: **{st.session_state.username}**")
        if st.button("🚪 Cerrar Sesión"):
            print("--- [app.py] Botón 'Cerrar Sesión' presionado. ---")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.divider()
    st.subheader("🎛️ Panel de Control")
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗺️ Mapa", "⚙️ Configuración"])

    # Obtener la conexión a la base de datos una sola vez al inicio de show_main_app
    print("--- [app.py] Cargando configuración de DB para la aplicación principal. ---")
    db_config_streamlit = load_db_config_streamlit()
    conn = get_database_connection(db_config_streamlit) 

    with tab1:
        st.subheader("Dashboard Principal")
        print("--- [app.py] Mostrando Dashboard. ---")
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM puntos_venta")
                    total_registros = cursor.fetchone()[0]
                    st.metric("Total Puntos de Venta", total_registros)
                    print(f"--- [app.py] Total Puntos de Venta: {total_registros} ---")
                st.metric("Usuarios Conectados", "1")
                st.metric("Estado Sistema", "✅ Activo")
            except Exception as e:
                st.error(f"Error al obtener métricas del Dashboard: {e}")
                st.info("Verifica las tablas y datos de la base de datos.")
                print(f"--- [app.py] ERROR al obtener métricas del Dashboard: {e} ---")
        else:
            st.warning("No hay conexión a la base de datos para mostrar métricas.")
            print("--- [app.py] No hay conexión a la base de datos para el Dashboard. ---")

    with tab2:
        st.subheader("🗺️ Mapa Interactivo")
        st.info("🚧 Aquí verás los puntos de venta según los filtros aplicados.")
        print("--- [app.py] Mostrando pestaña de Mapa. ---")

        # --- Sidebar para filtros ---
        st.sidebar.header("Filtros de Mapa")
        print("--- [app.py] Sidebar de filtros inicializado. ---")

        # Inicializar st.session_state para los selectbox si no existen
        if 'selected_categoria_desc' not in st.session_state:
            st.session_state.selected_categoria_desc = "Todas"
        if 'selected_marca_desc' not in st.session_state:
            st.session_state.selected_marca_desc = "Todas"
        if 'selected_vendedor_desc' not in st.session_state:
            st.session_state.selected_vendedor_desc = "Todos"
        if 'selected_dpto_desc' not in st.session_state:
            st.session_state.selected_dpto_desc = "Todos"
        if 'selected_ciudad_desc' not in st.session_state:
            st.session_state.selected_ciudad_desc = "Todas"
        
        # Obtener opciones para Categoría y Departamento (siempre las mismas)
        # NOTA: Pasamos `conn` como `_conn` a las funciones cacheada
        categorias_opts, categorias_map = get_categorias_options(conn)
        departamentos_opts, departamentos_map = get_departamentos_options(conn)

        # 1. Filtro de Categoría
        selected_categoria_desc = st.sidebar.selectbox(
            "Categoría:",
            categorias_opts,
            key="sb_cat",
            index=categorias_opts.index(st.session_state.selected_categoria_desc) if st.session_state.selected_categoria_desc in categorias_opts else 0
        )
        # Actualizar el session_state inmediatamente si el usuario cambia la selección
        if st.session_state.selected_categoria_desc != selected_categoria_desc:
            print(f"--- [app.py] Categoría cambiada de '{st.session_state.selected_categoria_desc}' a '{selected_categoria_desc}'. ---")
            st.session_state.selected_categoria_desc = selected_categoria_desc
            # Resetear marcas y vendedores si la categoría cambia
            st.session_state.selected_marca_desc = "Todas"
            st.session_state.selected_vendedor_desc = "Todos"
            st.rerun() # Disparar un rerun para actualizar las opciones de marcas y vendedores

        selected_categoria_id_for_filters = categorias_map.get(selected_categoria_desc) if selected_categoria_desc != "Todas" else None
        
        # 2. Filtro de Marca (dependiente de Categoría)
        marcas_opts, marcas_map = get_marcas_options(conn, id_categoria=selected_categoria_id_for_filters)
        selected_marca_desc = st.sidebar.selectbox(
            "Marca:",
            marcas_opts,
            key="sb_marca",
            index=marcas_opts.index(st.session_state.selected_marca_desc) if st.session_state.selected_marca_desc in marcas_opts else 0
        )
        if st.session_state.selected_marca_desc != selected_marca_desc:
            print(f"--- [app.py] Marca cambiada de '{st.session_state.selected_marca_desc}' a '{selected_marca_desc}'. ---")
            st.session_state.selected_marca_desc = selected_marca_desc
            # No se necesita rerun aquí a menos que otros filtros dependan de la marca.

        # 3. Filtro de Vendedor (dependiente de Categoría)
        vendedores_opts, vendedores_map = get_vendedores_options(conn, id_categoria=selected_categoria_id_for_filters)
        selected_vendedor_desc = st.sidebar.selectbox(
            "Vendedor:",
            vendedores_opts,
            key="sb_vend",
            index=vendedores_opts.index(st.session_state.selected_vendedor_desc) if st.session_state.selected_vendedor_desc in vendedores_opts else 0
        )
        if st.session_state.selected_vendedor_desc != selected_vendedor_desc:
            print(f"--- [app.py] Vendedor cambiado de '{st.session_state.selected_vendedor_desc}' a '{selected_vendedor_desc}'. ---")
            st.session_state.selected_vendedor_desc = selected_vendedor_desc
            # No se necesita rerun aquí.

        # 4. Filtro de Departamento (controlador de la cascada Departamento-Ciudad)
        selected_dpto_desc = st.sidebar.selectbox(
            "Departamento:",
            departamentos_opts,
            key="sb_dpto",
            index=departamentos_opts.index(st.session_state.selected_dpto_desc) if st.session_state.selected_dpto_desc in departamentos_opts else 0
        )
        if st.session_state.selected_dpto_desc != selected_dpto_desc:
            print(f"--- [app.py] Departamento cambiado de '{st.session_state.selected_dpto_desc}' a '{selected_dpto_desc}'. ---")
            st.session_state.selected_dpto_desc = selected_dpto_desc
            st.session_state.selected_ciudad_desc = "Todas" # Resetear ciudad si el departamento cambia
            st.rerun() # Disparar un rerun para actualizar las opciones de ciudades

        selected_dpto_id_for_cities = departamentos_map.get(selected_dpto_desc) if selected_dpto_desc != "Todos" else None
        
        # 5. Filtro de Ciudad (dependiente de Departamento)
        ciudades_opts, ciudades_map = get_ciudades_options(conn, id_dpto=selected_dpto_id_for_cities)
        selected_ciudad_desc = st.sidebar.selectbox(
            "Ciudad:",
            ciudades_opts,
            key="sb_ciudad",
            index=ciudades_opts.index(st.session_state.selected_ciudad_desc) if st.session_state.selected_ciudad_desc in ciudades_opts else 0
        )
        if st.session_state.selected_ciudad_desc != selected_ciudad_desc:
            print(f"--- [app.py] Ciudad cambiada de '{st.session_state.selected_ciudad_desc}' a '{selected_ciudad_desc}'. ---")
            st.session_state.selected_ciudad_desc = selected_ciudad_desc
            # No se necesita rerun aquí.

        apply_button = st.sidebar.button("Aplicar Filtros", key="btn_apply_filters")
        reset_button = st.sidebar.button("Reiniciar Filtros", key="btn_reset_filters")

        # Inicializar current_filters si no existe
        if 'current_filters' not in st.session_state:
            st.session_state['current_filters'] = {}
            print("--- [app.py] 'current_filters' inicializado en session_state. ---")

        if reset_button:
            print("--- [app.py] Botón 'Reiniciar Filtros' presionado. ---")
            # Resetear directamente los valores de session_state que controlan los selectbox
            st.session_state.selected_categoria_desc = "Todas"
            st.session_state.selected_marca_desc = "Todas"
            st.session_state.selected_vendedor_desc = "Todos"
            st.session_state.selected_dpto_desc = "Todos"
            st.session_state.selected_ciudad_desc = "Todas"
            st.session_state['current_filters'] = {} # También limpiar los filtros aplicados
            print("--- [app.py] Filtros reseteados. Rerunning... ---")
            st.rerun()
        elif apply_button:
            print("--- [app.py] Botón 'Aplicar Filtros' presionado. ---")
            # Mapear descripciones a IDs para pasarlas a las funciones de base de datos
            st.session_state['current_filters'] = {
                "categoria_id": categorias_map.get(selected_categoria_desc) if selected_categoria_desc != "Todas" else None,
                "marca_id": marcas_map.get(selected_marca_desc) if selected_marca_desc != "Todas" else None,
                "vendedor_desc": selected_vendedor_desc if selected_vendedor_desc != "Todos" else None,
                "departamento_id": departamentos_map.get(selected_dpto_desc) if selected_dpto_desc != "Todos" else None,
                "ciudad_id": ciudades_map.get(selected_ciudad_desc) if selected_ciudad_desc != "Todas" else None,
            }
            print(f"--- [app.py] Filtros aplicados: {st.session_state['current_filters']} ---")

        # Asegurarse de que 'current_filters' tiene valores por defecto al inicio si no se ha aplicado nada
        if not st.session_state['current_filters'] and not apply_button:
            print("--- [app.py] Inicializando 'current_filters' con valores por defecto (primera carga o después de reinicio). ---")
            st.session_state['current_filters'] = {
                "categoria_id": categorias_map.get(selected_categoria_desc) if selected_categoria_desc != "Todas" else None,
                "marca_id": marcas_map.get(selected_marca_desc) if selected_marca_desc != "Todas" else None,
                "vendedor_desc": selected_vendedor_desc if selected_vendedor_desc != "Todos" else None,
                "departamento_id": departamentos_map.get(selected_dpto_desc) if selected_dpto_desc != "Todos" else None,
                "ciudad_id": ciudades_map.get(selected_ciudad_desc) if selected_ciudad_desc != "Todas" else None,
            }

        # Cargar y procesar datos del mapa
        # AÑADIMOS '_' AL PARÁMETRO 'conn_data' para que Streamlit NO intente hashear la conexión
        @st.cache_data(show_spinner="Cargando y procesando datos del mapa...", ttl="1h")
        def load_and_process_map_data_cached(_conn_data, filters_dict):
            print(f"--- [app.py] [CACHED] Ejecutando load_and_process_map_data_cached con filtros: {filters_dict} ---")
            points_preventa_1_raw = fetch_points_with_last_sale_preventa_1(
                _conn_data,
                id_categoria=filters_dict.get('categoria_id'),
                id_marca=filters_dict.get('marca_id'),
                descripcion_vend=filters_dict.get('vendedor_desc'),
                id_dpto=filters_dict.get('departamento_id'),
                id_ciudad=filters_dict.get('ciudad_id')
            )
            print(f"--- [app.py] [CACHED] fetched {len(points_preventa_1_raw) if points_preventa_1_raw else 0} points_preventa_1_raw ---")
            
            points_preventa_no_1_raw = fetch_points_with_last_sale_preventa_no_1(
                _conn_data,
                ids_marcas=None # Esto sigue siendo None, asumiendo que no necesitas filtrar por marca aquí
            )
            print(f"--- [app.py] [CACHED] fetched {len(points_preventa_no_1_raw) if points_preventa_no_1_raw else 0} points_preventa_no_1_raw ---")
            
            all_points_df, stats_dict = process_points_for_map(
                points_preventa_1_raw,
                points_preventa_no_1_raw,
                filters_dict
            )
            print(f"--- [app.py] [CACHED] process_points_for_map retornó {len(all_points_df)} puntos y estadísticas. ---")
            return all_points_df, stats_dict

        # Al llamar a la función, pasamos la conexión directamente
        all_points_data, stats_data = load_and_process_map_data_cached(conn, st.session_state['current_filters'])
        print(f"--- [app.py] Datos del mapa cargados. Total de puntos: {len(all_points_data)} ---")

        if not all_points_data.empty:
            # --- Visualización del Mapa con Folium ---
            # Aseguramos que las columnas de latitud y longitud sean numéricas y no nulas
            print("--- [app.py] Preparando datos para el mapa: convirtiendo lat/lon a numérico y eliminando nulos. ---")
            all_points_data['LATITUD'] = pd.to_numeric(all_points_data['LATITUD'], errors='coerce')
            all_points_data['LONGITUD'] = pd.to_numeric(all_points_data['LONGITUD'], errors='coerce')
            all_points_data.dropna(subset=['LATITUD', 'LONGITUD'], inplace=True)
            print(f"--- [app.py] Puntos válidos para el mapa después de limpieza: {len(all_points_data)} ---")

            if not all_points_data.empty:
                print("--- [app.py] Llamando a generate_folium_map para obtener el objeto mapa. ---")
                # LA LÍNEA CRUCIAL: Capturamos el objeto mapa que retorna generate_folium_map
                folium_map_object = generate_folium_map(all_points_data) # stats_data ya no es un parámetro aquí
                
                print("--- [app.py] Objeto mapa recibido. Renderizando con folium_static. ---")
                # Renderizamos el objeto mapa usando folium_static AQUÍ en app.py
                folium_static(folium_map_object, width=900, height=600) 
                print("--- [app.py] Mapa Folium renderizado en Streamlit. ---")

                # --- Mostrar Estadísticas ---
                st.subheader("Estadísticas del Mapa")
                print("--- [app.py] Mostrando estadísticas del mapa. ---")
                if stats_data:
                    st.write(f"**TOTAL GRAL. CLIENTES:** {stats_data.get('total_general_clientes', 0)}")
                    st.write(f"**CÍRCULOS (SIN MERCADERÍA EN TRÁNSITO):** {stats_data.get('total_circles', 0)}")
                    st.write(f"   Verde: {stats_data.get('circles_green', 0)}")
                    st.write(f"   Naranja: {stats_data.get('circles_orange', 0)}")
                    st.write(f"   Rojo: {stats_data.get('circles_red', 0)}")
                    st.write(f"   Negro: {stats_data.get('circles_black', 0)}")

                    st.write(f"**DIAMANTES (CON MERCADERÍA EN TRÁNSITO):** {stats_data.get('total_diamonds', 0)}")
                    st.write(f"   Verde: {stats_data.get('diamonds_green', 0)}")
                    st.write(f"   Naranja: {stats_data.get('diamonds_orange', 0)}")
                    st.write(f"   Rojo: {stats_data.get('diamonds_red', 0)}")
                    st.write(f"   Negro: {stats_data.get('diamonds_black', 0)}")
                    print("--- [app.py] Estadísticas mostradas. ---")
                else:
                    st.info("No hay estadísticas disponibles.")
                    print("--- [app.py] No hay estadísticas para mostrar. ---")
            else:
                st.warning("No hay datos de clientes con coordenadas válidas para mostrar en el mapa.")
                print("--- [app.py] No hay puntos con coordenadas válidas para el mapa. ---")
        else:
            st.warning("No hay datos para mostrar en el mapa con los filtros actuales.")
            print("--- [app.py] No hay datos de puntos después de aplicar filtros. ---")

    with tab3:
        st.subheader("Configuración del Sistema")
        print("--- [app.py] Mostrando pestaña de Configuración. ---")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("🎨 Tema", ["Claro", "Oscuro"])
            st.selectbox("🌍 Idioma", ["Español", "English"])
        with col2:
            st.checkbox("📧 Notificaciones por email")
            st.checkbox("🔄 Auto-actualización")
        if st.button("💾 Guardar Configuración"):
            st.success("✅ Configuración guardada exitosamente")
            print("--- [app.py] Configuración guardada (simulado). ---")

# --- Función Principal de la Aplicación (main) ---
def main():
    """Función principal de la aplicación"""
    print("--- [app.py] Iniciando función main. ---")
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        print("--- [app.py] Estado de autenticación inicializado en False. ---")

    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()
    print("--- [app.py] Fin de la ejecución de main. ---")

if __name__ == "__main__":
    main()