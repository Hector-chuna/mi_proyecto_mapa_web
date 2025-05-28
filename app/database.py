import pymysql
import json
import os
from datetime import datetime, date
import sys

# NOTA: get_db_path es probablemente para una base de datos SQLite local con PyInstaller.
# Si tu aplicación Streamlit se conecta a un MySQL remoto, esta función
# probablemente no es necesaria para el entorno de Streamlit Cloud.
def get_db_path(db_filename="database.db"):
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
        bundle_dir = os.path.join(bundle_dir, '..')

    db_path = os.path.join(bundle_dir, db_filename)
    print(f"Intentando conectar a la base de datos en: {db_path}")
    return db_path

def connect_to_database(db_config):
    """
    Intenta establecer una conexión con la base de datos MySQL usando los parámetros proporcionados.
    db_config es un diccionario que contiene 'host', 'port', 'user', 'password', 'database'.
    """
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            connect_timeout=10,  # Aumenta el tiempo de espera para la conexión (segundos)
            read_timeout=10,     # Aumenta el tiempo de espera para leer datos (segundos)
            write_timeout=10     # Aumenta el tiempo de espera para escribir datos (segundos)
        )
        print("Conexión a la base de datos exitosa.")
        return connection
    except KeyError as e:
        print(f"Error: Falta una clave requerida en la configuración de la base de datos: {e}. Asegúrate de que 'host', 'port', 'user', 'password', 'database' estén presentes.")
        return None
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def close_database_connection(conexion):
    """
    Cierra la conexión a la base de datos si está abierta.
    """
    if conexion:
        try:
            conexion.close()
            print("Conexión a la base de datos cerrada.")
        except pymysql.ProgrammingError as e:
            print(f"Advertencia: Error al cerrar la conexión a la base de datos (posiblemente ya cerrada): {e}")
        except Exception as e:
            print(f"Error inesperado al cerrar la conexión a la base de datos: {e}")


def fetch_categorias(conexion):
    """
    Recupera todas las categorías de la tabla 'categoria'.
    """
    try:
        with conexion.cursor() as cursor:
            query = "SELECT id_categoria, descripcion_categoria FROM categoria ORDER BY descripcion_categoria;"
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []

def fetch_marcas(conexion, id_categoria=None):
    """
    Recupera marcas, opcionalmente filtradas por ID de categoría.
    """
    try:
        with conexion.cursor() as cursor:
            query = "SELECT id_marca, descripcion_marca FROM marca"
            params = []
            
            if id_categoria is not None and id_categoria != '':
                query += """
                    WHERE id_marca IN (
                        SELECT DISTINCT ID_MARCA FROM ventas
                        WHERE ID_CATEGORIA = %s
                    )
                """
                params.append(id_categoria)

            query += " ORDER BY descripcion_marca;"
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener marcas: {e}")
        return []

def fetch_vendedores(conexion, id_categoria=None):
    """
    Recupera vendedores, opcionalmente filtrados por ID de categoría.
    """
    try:
        with conexion.cursor() as cursor:
            # Asumo que la tabla 'vendedor' tiene un ID_VEND único.
            query = "SELECT ID_VEND, DESCRIPCION_VEND FROM vendedor" # Obtener ID y descripción
            params = []
            
            if id_categoria is not None and id_categoria != '':
                query += """
                    WHERE ID_VEND IN (
                        SELECT DISTINCT v_hist.ID_VEND 
                        FROM ventas v_hist
                        WHERE v_hist.ID_CATEGORIA = %s
                    )
                """
                params.append(id_categoria)
            
            query += " ORDER BY DESCRIPCION_VEND;"
            cursor.execute(query, params)
            # Retorna tuplas (ID, DESCRIPCION)
            return cursor.fetchall() 
    except Exception as e:
        print(f"Error al obtener vendedores: {e}")
        return []

def fetch_departamentos(conexion):
    """
    Recupera todos los departamentos de la tabla 'departamento'.
    """
    try:
        with conexion.cursor() as cursor:
            query = "SELECT id_dpto, descripcion_dpto FROM departamento ORDER BY descripcion_dpto;"
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener departamentos: {e}")
        return []

def fetch_ciudades(conexion, id_dpto=None):
    """
    Recupera ciudades, opcionalmente filtradas por ID de departamento.
    """
    try:
        with conexion.cursor() as cursor:
            query = "SELECT id_ciudad, descripcion_ciudad FROM ciudad"
            params = []
            if id_dpto is not None and id_dpto != '':
                query += " WHERE id_dpto = %s"
                params.append(id_dpto)
            query += " ORDER BY descripcion_ciudad;"
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener ciudades: {e}")
        return []

# --- FUNCIONES CLAVE PARA EL MAPA ---

def fetch_points_with_last_sale_preventa_1(conexion, id_categoria=None, id_marca=None, descripcion_vend=None, id_dpto=None, id_ciudad=None):
    """
    Recupera puntos de venta con la última venta de 'PREVENTA = 1', aplicando varios filtros.
    """
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            # Lista para almacenar los parámetros en el orden correcto de aparición en la consulta
            params = []

            # --- CTE para encontrar la ÚLTIMA FECHA según los filtros de VENTA ---
            cte_where_parts = ["v_sub.PREVENTA = 1"]
            cte_join_parts = []
            
            if id_categoria is not None and id_categoria != '':
                cte_where_parts.append("v_sub.ID_CATEGORIA = %s")
                params.append(id_categoria)
            
            if id_marca is not None and id_marca != '':
                cte_where_parts.append("v_sub.ID_MARCA = %s")
                params.append(id_marca)

            if descripcion_vend is not None and descripcion_vend != '':
                cte_join_parts.append("JOIN vendedor ve_sub ON v_sub.ID_VEND = ve_sub.ID_VEND")
                cte_where_parts.append("ve_sub.DESCRIPCION_VEND = %s")
                params.append(descripcion_vend)

            cte_where_clause = " AND ".join(cte_where_parts)
            cte_joins_clause = " ".join(cte_join_parts)

            cte_definition = f"""
                WITH ultima_venta_preventa_1_por_cliente AS (
                    SELECT
                        v_sub.ID_CLIENTE,
                        MAX(v_sub.FECHA) as ULTIMA_FECHA
                    FROM ventas v_sub
                    {cte_joins_clause}
                    WHERE {cte_where_clause}
                    GROUP BY v_sub.ID_CLIENTE
                )
            """
            
            # --- Cláusula WHERE principal (filtros de puntos_venta y filtros adicionales de v_latest) ---
            main_where_parts = ["pv.LATITUD IS NOT NULL", "pv.LONGITUD IS NOT NULL", "pv.LATITUD != ''", "pv.LONGITUD != ''"]

            if id_dpto is not None and id_dpto != '':
                main_where_parts.append("pv.ID_DPTO = %s")
                params.append(id_dpto)

            if id_ciudad is not None and id_ciudad != '':
                main_where_parts.append("pv.ID_CIUDAD = %s")
                params.append(id_ciudad)

            # Las condiciones de categoría y marca para `v_latest` que aseguran que
            # la venta obtenida por la CTE coincide con los filtros generales.
            if id_categoria is not None and id_categoria != '':
                main_where_parts.append("v_latest.ID_CATEGORIA = %s")
                params.append(id_categoria) # Este es un parámetro repetido, pero necesario si el filtro aplica a v_latest

            if id_marca is not None and id_marca != '':
                main_where_parts.append("v_latest.ID_MARCA = %s")
                params.append(id_marca) # Este es un parámetro repetido, pero necesario si el filtro aplica a v_latest
            
            # Si se filtró por vendedor, la condición para el SELECT final.
            # Esta condición se aplica a la tabla 'vendedor' que se une en el SELECT principal.
            if descripcion_vend is not None and descripcion_vend != '':
                main_where_parts.append("ve.DESCRIPCION_VEND = %s")
                params.append(descripcion_vend) # Este es un parámetro repetido, pero necesario si el filtro aplica a ve


            final_where_clause = " AND ".join(main_where_parts)

            # --- Combinar todas las partes en la consulta final ---
            full_query = f"""
                {cte_definition}
                SELECT
                    pv.ID_CLIENTE,
                    pv.DESCRIPCION_CLIENTE,
                    pv.LATITUD,
                    pv.LONGITUD,
                    v_latest.FECHA AS ULTIMA_VENTA,
                    v_latest.ID_VEND,
                    ve.DESCRIPCION_VEND,
                    m.DESCRIPCION_MARCA,
                    v_latest.PREVENTA,
                    v_latest.ID_MARCA,
                    v_latest.ID_CATEGORIA,
                    cat.DESCRIPCION_CATEGORIA,
                    dpto.DESCRIPCION_DPTO,
                    ciu.DESCRIPCION_CIUDAD
                FROM puntos_venta pv
                JOIN ultima_venta_preventa_1_por_cliente uvp1 ON pv.ID_CLIENTE = uvp1.ID_CLIENTE
                JOIN ventas v_latest ON uvp1.ID_CLIENTE = v_latest.ID_CLIENTE 
                                     AND uvp1.ULTIMA_FECHA = v_latest.FECHA
                                     AND v_latest.PREVENTA = 1 -- Asegurar que la venta es de PREVENTA=1
                LEFT JOIN vendedor ve ON v_latest.ID_VEND = ve.ID_VEND
                LEFT JOIN marca m ON v_latest.ID_MARCA = m.ID_MARCA
                LEFT JOIN categoria cat ON v_latest.ID_CATEGORIA = cat.ID_CATEGORIA
                LEFT JOIN departamento dpto ON pv.ID_DPTO = dpto.ID_DPTO 
                LEFT JOIN ciudad ciu ON pv.ID_CIUDAD = ciu.ID_CIUDAD 
                WHERE {final_where_clause}
                ORDER BY pv.ID_CLIENTE, v_latest.FECHA DESC;
            """
            
            print("\n--- Consulta SQL generada para PREVENTA=1 ---")
            print(full_query)
            print(f"Parámetros de la consulta: {params}")
            print("---------------------------------------------")

            cursor.execute(full_query, tuple(params)) # pymysql espera una tupla de parámetros
            results = cursor.fetchall()
            return results
    except Exception as e:
        print(f"Error al recuperar puntos con última venta (PREVENTA=1) filtrada: {e}")
        return []

def fetch_points_with_last_sale_preventa_no_1(conexion, ids_marcas=None):
    """
    Recupera puntos de venta con 'PREVENTA' diferente de 1 (2 o 3),
    utilizado para identificar mercadería en tránsito o programada.
    """
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
                SELECT
                    v.ID_CLIENTE,
                    v.FECHA,
                    CASE
                        WHEN v.PREVENTA = 2 THEN 'PREVENTA'
                        WHEN v.PREVENTA = 3 THEN 'PROGRAMADO'
                    END AS TIPO,
                    m.DESCRIPCION_MARCA AS MARCA,
                    v.CANTIDAD
                FROM ventas v
                LEFT JOIN marca m ON v.ID_MARCA = m.ID_MARCA
                WHERE v.PREVENTA IN (2, 3)
                    AND v.CANTIDAD > 0
            """

            params = []
            if ids_marcas is not None:
                if ids_marcas:
                    placeholders = ", ".join(["%s"] * len(ids_marcas))
                    query += f" AND v.ID_MARCA IN ({placeholders})"
                    params.extend(ids_marcas)
                else:
                    query += " AND 1=0" # Asegura que no se devuelvan resultados si no hay marcas
            
            query += " ORDER BY v.ID_CLIENTE, v.FECHA DESC;"
            
            print("\n--- Consulta SQL generada para PREVENTA!=1 (revertida) ---")
            print(query)
            print(f"Parámetros de la consulta: {params}")
            print("---------------------------------------------")

            cursor.execute(query, params)
            puntos_en_transito = cursor.fetchall()
            return puntos_en_transito

    except Exception as e:
        print(f"Error al recuperar puntos con ventas en tránsito (PREVENTA ≠ 1): {e}")
        return []