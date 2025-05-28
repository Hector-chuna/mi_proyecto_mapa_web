# app/color_calculator.py

from datetime import datetime, date
from decimal import Decimal

# ¡LA CONSTANTE POPUP_HEADER_FOOTER_HTML HA SIDO ELIMINADA DE AQUÍ!
# Su contenido (CSS y JS) se inyectará globalmente en map_generator.py si es necesario.

def formatear_info_basica_para_popup(datos_cliente):
    """
    Formatea la información básica de un cliente para el popup.
    Ya NO incluye el CSS ni el JavaScript, ya que se inyectarán globalmente (si aplica para el mapa).
    """
    html_content = "<div class='popup-content'>" # Abrir div principal

    html_content += f"<h4>{datos_cliente.get('descripcion_cliente', 'N/A')} ({datos_cliente.get('id_cliente', 'N/A')})</h4>"

    ultima_venta_str = "No hay ventas de STOCK registradas."
    if datos_cliente.get('ultima_venta_stock_date'):
        if isinstance(datos_cliente['ultima_venta_stock_date'], date):
            ultima_venta_str = datos_cliente['ultima_venta_stock_date'].strftime('%d/%m/%Y')
        else:
            ultima_venta_str = str(datos_cliente['ultima_venta_stock_date'])

    html_content += f"<p><strong>Última Venta STOCK:</strong> {ultima_venta_str}</p>"
    html_content += f"<p><strong>Vendedor:</strong> {datos_cliente.get('descripcion_vend', 'N/A')}</p>"
    html_content += f"<p><strong>Marca (última venta):</strong> {datos_cliente.get('descripcion_marca', 'N/A')}</p>"

    # Usar las nuevas columnas de descripción
    html_content += f"<p><strong>Categoría:</strong> {datos_cliente.get('DESCRIPCION_CATEGORIA', 'N/A')}</p>"
    html_content += f"<p><strong>Departamento:</strong> {datos_cliente.get('DESCRIPCION_DPTO', 'N/A')}</p>"
    html_content += f"<p><strong>Ciudad:</strong> {datos_cliente.get('DESCRIPCION_CIUDAD', 'N/A')}</p>"

    return html_content # Dejamos el cierre del div principal para la función de concatenación

def formatear_ventas_en_transito_para_popup(ventas_cliente): # Eliminado 'point_id' ya que no se usa para IDs de elementos ocultos
    """
    Formatea los detalles de las ventas en tránsito para el popup.
    Muestra la información directamente sin ningún botón de alternancia.
    """
    html_content = ""

    # Subtítulo para la sección de mercadería en tránsito
    html_content += "<hr>" # Línea divisoria para separar del contenido básico
    html_content += "<p><b>Mercadería en Tránsito/Programada:</b></p>"

    if ventas_cliente: # Si hay datos de ventas en tránsito
        for venta in ventas_cliente:
            html_content += f"<p><strong>MARCA:</strong> {venta.get('MARCA', 'N/A')}</p>"
            html_content += "<p>PROGRAMADO:</p>"
            html_content += "<ul>"
            # Asumiendo que 'venta' tiene una lista de programaciones o un campo similar
            if 'PROGRAMACION' in venta and isinstance(venta['PROGRAMACION'], list):
                for prog in venta['PROGRAMACION']:
                    html_content += f"<li>{prog.get('FECHA', 'N/A')}: {prog.get('CANTIDAD', 'N/A')}</li>"
            else:
                 # Si no es una lista de programaciones, asume un solo campo.
                html_content += f"<li>{venta.get('FECHA', 'N/A')}: {venta.get('CANTIDAD', 'N/A')}</li>"
            html_content += "</ul>"
            html_content += "<br>" # Espacio entre diferentes marcas o programaciones

    else:
        html_content += "<p>No hay mercadería en tránsito/programada para este cliente.</p>"

    return html_content


def calculate_colors_and_shapes_for_all_points(puntos_preventa_1, puntos_preventa_no_1):
    """
    Calcula colores y formas para puntos basándose en datos de ventas, incluyendo PREVENTA.
    """
    print("- Procesando puntos para asignar colores y formas -")

    sales_by_client = {}
    print(f"- Puntos PREVENTA=1 recibidos: {len(puntos_preventa_1)}")

    for punto_dict in puntos_preventa_1:
        try:
            id_cliente = punto_dict.get('ID_CLIENTE')
            descripcion_cliente = punto_dict.get('DESCRIPCION_CLIENTE')
            latitud = punto_dict.get('LATITUD')
            longitud = punto_dict.get('LONGITUD')
            fecha_venta = punto_dict.get('ULTIMA_VENTA')
            id_vend = punto_dict.get('ID_VEND')
            descripcion_vend = punto_dict.get('DESCRIPCION_VEND')
            descripcion_marca = punto_dict.get('DESCRIPCION_MARCA')
            preventa = punto_dict.get('PREVENTA')
            id_marca = punto_dict.get('ID_MARCA')
            id_categoria = punto_dict.get('ID_CATEGORIA')

            descripcion_categoria = punto_dict.get('DESCRIPCION_CATEGORIA')
            id_dpto = punto_dict.get('ID_DPTO')
            descripcion_dpto = punto_dict.get('DESCRIPCION_DPTO')
            id_ciudad = punto_dict.get('ID_CIUDAD')
            descripcion_ciudad = punto_dict.get('DESCRIPCION_CIUDAD')

            if id_cliente is None or descripcion_cliente is None or latitud is None or longitud is None:
                print(f"Advertencia: Saltando diccionario PREVENTA=1 con campos requeridos nulos: {punto_dict}")
                continue

            sale_date = None
            if fecha_venta is not None:
                if isinstance(fecha_venta, str):
                    try:
                        sale_date = datetime.strptime(fecha_venta.strip(), "%Y-%m-%d %H:%M:%S").date()
                    except ValueError:
                        try:
                            sale_date = datetime.strptime(fecha_venta.strip(), "%Y-%m-%d").date()
                        except ValueError as ve:
                            print(f"Advertencia: Fecha inválida '{fecha_venta}' para cliente {id_cliente}. Error: {ve}")
                            continue
                elif isinstance(fecha_venta, datetime):
                    sale_date = fecha_venta.date()
                elif isinstance(fecha_venta, date):
                    sale_date = fecha_venta


            if id_cliente not in sales_by_client:
                sales_by_client[id_cliente] = {
                    "id_cliente": id_cliente,
                    "descripcion_cliente": descripcion_cliente,
                    "latitud": latitud,
                    "longitud": longitud,
                    "ultima_venta_stock_date": sale_date,
                    "id_vend": id_vend,
                    "descripcion_vend": descripcion_vend,
                    "descripcion_marca": descripcion_marca,
                    "preventa": preventa,
                    "id_marca": id_marca,
                    "id_categoria": id_categoria,
                    "DESCRIPCION_CATEGORIA": descripcion_categoria,
                    "id_dpto": id_dpto,
                    "DESCRIPCION_DPTO": descripcion_dpto,
                    "id_ciudad": id_ciudad,
                    "DESCRIPCION_CIUDAD": descripcion_ciudad,
                }
            else:
                current_latest_stock_date = sales_by_client[id_cliente]["ultima_venta_stock_date"]
                if current_latest_stock_date is None or (sale_date and sale_date > current_latest_stock_date):
                    sales_by_client[id_cliente]["ultima_venta_stock_date"] = sale_date
                    sales_by_client[id_cliente].update({
                        "id_vend": id_vend,
                        "descripcion_vend": descripcion_vend,
                        "descripcion_marca": descripcion_marca,
                        "preventa": preventa,
                        "DESCRIPCION_CATEGORIA": descripcion_categoria,
                        "DESCRIPCION_DPTO": descripcion_dpto,
                        "DESCRIPCION_CIUDAD": descripcion_ciudad,
                    })

        except Exception as e:
            print(f"Error al procesar diccionario en el paso de PREVENTA=1: {punto_dict}. Error: {e}")
            continue

    print(f"Paso 1 completado. Clientes únicos con ventas PREVENTA=1: {len(sales_by_client)}")

    ventas_en_transito_por_cliente = {}
    print(f"- Puntos PREVENTA!=1 recibidos: {len(puntos_preventa_no_1)}")

    for punto_transito in puntos_preventa_no_1:
        id_cliente_transito = punto_transito.get('ID_CLIENTE')
        if id_cliente_transito:
            if id_cliente_transito not in ventas_en_transito_por_cliente:
                ventas_en_transito_por_cliente[id_cliente_transito] = []
            ventas_en_transito_por_cliente[id_cliente_transito].append(punto_transito)

    print(f"Paso 2 completado. Clientes con ventas en tránsito: {len(ventas_en_transito_por_cliente)}")

    puntos_para_mapa = []

    for id_cliente, datos_cliente in sales_by_client.items():
        try:
            ultima_venta_stock_date = datos_cliente.get("ultima_venta_stock_date")

            base_color = "black"

            if ultima_venta_stock_date is not None:
                dias_desde_ultima_venta_stock = (datetime.now().date() - ultima_venta_stock_date).days
                if dias_desde_ultima_venta_stock <= 30:
                    base_color = "green"
                elif 31 <= dias_desde_ultima_venta_stock <= 60:
                    base_color = "orange"
                elif 61 <= dias_desde_ultima_venta_stock <= 90:
                    base_color = "red"
                # Si supera los 90 días, permanece en 'black' (valor por defecto)


            shape = "circle"
            if id_cliente in ventas_en_transito_por_cliente:
                shape = "diamond"

            # --- Corrección para first_letter_vend ---
            first_letter_vend = '?' # Valor por defecto
            desc_vend = datos_cliente.get("descripcion_vend")

            if desc_vend is not None:
                desc_vend_stripped = str(desc_vend).strip()
                if len(desc_vend_stripped) > 0:
                    first_letter_vend = desc_vend_stripped[0].upper()
            # --- Fin Corrección first_letter_vend ---


            # Generar el HTML del popup completo
            popup_html_content_basic = formatear_info_basica_para_popup(datos_cliente)
            detalles_transito_cliente = ventas_en_transito_por_cliente.get(id_cliente, [])

            # Pasamos solo los detalles de tránsito a la función, ya no necesitamos el point_id aquí.
            popup_html_content_transito = formatear_ventas_en_transito_para_popup(detalles_transito_cliente)

            # Concatenar todo el HTML y cerrar el div principal
            full_popup_html_content = popup_html_content_basic + popup_html_content_transito + "</div>"

            punto_dict = {
                "id_cliente": id_cliente,
                "descripcion_cliente": datos_cliente.get("descripcion_cliente"),
                "LATITUD": float(datos_cliente.get("latitud")) if isinstance(datos_cliente.get("latitud"), Decimal) else datos_cliente.get("latitud"),
                "LONGITUD": float(datos_cliente.get("longitud")) if isinstance(datos_cliente.get("longitud"), Decimal) else datos_cliente.get("longitud"),
                "id_vend": datos_cliente.get("id_vend"),
                "descripcion_vend": datos_cliente.get("descripcion_vend"),
                "descripcion_marca": datos_cliente.get("descripcion_marca"),
                "preventa": datos_cliente.get("preventa"),
                "id_marca": datos_cliente.get("id_marca"),
                "id_categoria": datos_cliente.get("id_categoria"),
                "DESCRIPCION_CATEGORIA": datos_cliente.get("DESCRIPCION_CATEGORIA"),
                "id_dpto": datos_cliente.get("id_dpto"),
                "DESCRIPCION_DPTO": datos_cliente.get("DESCRIPCION_DPTO"),
                "id_ciudad": datos_cliente.get("id_ciudad"),
                "DESCRIPCION_CIUDAD": datos_cliente.get("DESCRIPCION_CIUDAD"),
                "color": base_color,
                "shape": shape,
                "popup_html": full_popup_html_content, # Esto ya contiene todo el HTML
                "first_letter_vend": first_letter_vend # Usar el valor corregido
            }

            puntos_para_mapa.append(punto_dict)

        except Exception as e:
            print(f"Error inesperado al procesar cliente {id_cliente} para el mapa: {e}")
            continue

    print("Paso 3 completado. Total de puntos procesados para visualización:", len(puntos_para_mapa))
    return puntos_para_mapa

# Helper function
def format_date_for_display(date_obj):
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime('%d/%m/%Y')
    return str(date_obj) if date_obj else 'N/A'