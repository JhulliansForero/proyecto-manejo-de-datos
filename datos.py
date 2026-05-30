#-----------------------------------------
import os               # módulo para construir rutas de archivos
import pandas as pd     # pandas: librería para leer el CSV y trabajar con el DataFrame
#-----------------------------------------


#-----------------------------------------
# ruta del CSV que sube el usuario (se guarda en la misma carpeta que este archivo)
CSV_PATH = os.path.join(os.path.dirname(__file__), "datos_cargados.csv")
#-----------------------------------------


#-----------------------------------------
# tonos de naranja, del más claro al más oscuro (se usan en el mapa de calor)
TONOS = ["#FCEBDD", "#FDD9BD", "#FBBA85", "#F97316", "#EA6C10"]
# días de la semana como vienen en el CSV (en inglés) y su nombre corto en español
DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_ES = {"Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mié", "Thursday": "Jue",
           "Friday": "Vie", "Saturday": "Sáb", "Sunday": "Dom"}
#-----------------------------------------


#-----------------------------------------
# convierte un número grande de pesos en un texto corto (ej. 2540000000 -> "$2.54B")
def formato_dinero(valor):
    if valor >= 1_000_000_000:                      # si es mil millones o más
        return f"${valor / 1_000_000_000:.2f}B"     # lo muestra en "B" (miles de millones)
    if valor >= 1_000_000:                          # si es un millón o más
        return f"${valor / 1_000_000:.1f}M"         # lo muestra en "M" (millones)
    return f"${valor:,.0f}"                          # si es pequeño, el número completo
#-----------------------------------------


#-----------------------------------------
# elige un tono de naranja según dónde cae el valor entre el mínimo y el máximo
def color_calor(valor, minimo, maximo):
    if maximo == minimo:                                         # evita dividir por cero
        proporcion = 0.5
    else:
        proporcion = (valor - minimo) / (maximo - minimo)        # número entre 0 y 1
    indice = min(int(proporcion * len(TONOS)), len(TONOS) - 1)   # elige la posición del tono
    return TONOS[indice]                                          # devuelve el color
#-----------------------------------------


#-----------------------------------------
# función principal: lee el CSV en un DataFrame y calcula todo lo del dashboard
def obtener_metricas() -> dict:
    df = pd.read_csv(CSV_PATH)                                   # carga los 50.000 pedidos en un DataFrame

    # --- Tarjetas (indicadores principales) ---
    total_pedidos = len(df)                                     # cantidad de filas (pedidos)
    ingresos = df["precio_total"].sum()                         # suma de la columna precio_total
    calificacion = df["calificacion"].mean()                    # promedio de la columna calificacion
    tiempo = df["tiempo_preparacion_min"].mean()                # promedio del tiempo de preparación

    # --- Combos más vendidos (los 7 con más pedidos) ---
    conteo = df["nombre_combo"].value_counts().head(7)          # cuenta cuántas veces se vendió cada combo
    maximo_combo = conteo.max()                                 # el combo más vendido (para escalar las barras)
    combos = []                                                 # lista que llenaremos con cada barra
    primero = True                                              # bandera para pintar de naranja la barra más alta
    for nombre, cantidad in conteo.items():                     # recorre cada combo del conteo
        combos.append({
            "nombre": nombre.replace("Combo ", ""),             # nombre corto para la etiqueta de la barra
            "alto": round(cantidad / maximo_combo * 100),       # altura de la barra en porcentaje
            "clase": "barra barra_naranja" if primero else "barra",  # la primera barra va en naranja
        })
        primero = False                                         # las siguientes ya no son la primera

    # --- Métodos de pago (porcentaje de cada uno) ---
    pagos = (df["metodo_pago"].value_counts(normalize=True) * 100).round()  # porcentaje de cada método
    p_app = int(pagos.get("App", 0))                            # porcentaje de pagos por App
    p_tarjeta = int(pagos.get("Tarjeta", 0))                    # porcentaje de pagos con Tarjeta
    p_efectivo = int(pagos.get("Efectivo", 0))                  # porcentaje de pagos en Efectivo
    dona_estilo = (                                             # arma el degradado circular de la dona
        f"conic-gradient("
        f"#F97316 0% {p_app}%, "                                # naranja para App
        f"#57534E {p_app}% {p_app + p_tarjeta}%, "              # gris oscuro para Tarjeta
        f"#D6D3D1 {p_app + p_tarjeta}% 100%)"                   # gris claro para Efectivo
    )

    # --- Mapa de calor: pedidos por día y por hora ---
    df["hora_num"] = df["hora"].str[:2].astype(int)             # toma solo la hora (ej. "21:30" -> 21)
    tabla = df.pivot_table(index="dia_semana", columns="hora_num",
                           values="order_id", aggfunc="count").fillna(0)  # cuenta pedidos por día y hora
    horas = sorted(df["hora_num"].unique())                     # lista de horas (10 a 21)
    minimo_calor = tabla.values.min()                           # el valor más bajo de la tabla
    maximo_calor = tabla.values.max()                           # el valor más alto de la tabla
    heatmap = []                                                # lista de filas (una por día)
    for dia in DIAS:                                            # recorre los días en orden
        celdas = []                                             # los colores de esa fila
        for hora in horas:                                      # recorre cada hora
            valor = tabla.loc[dia, hora] if dia in tabla.index else 0  # pedidos de ese día y hora
            celdas.append(color_calor(valor, minimo_calor, maximo_calor))  # color según la cantidad
        heatmap.append({"dia": DIAS_ES[dia], "celdas": celdas}) # guarda la fila

    # --- Ingresos por mes ---
    df["mes"] = pd.to_datetime(df["fecha"]).dt.to_period("M").astype(str)  # saca el mes de cada fecha
    por_mes = df.groupby("mes")["precio_total"].sum()           # suma de ingresos por mes
    minimo_mes = por_mes.min()                                  # el mes con menos ingresos
    maximo_mes = por_mes.max()                                  # el mes con más ingresos
    n = len(por_mes)                                            # cantidad de meses
    puntos = []                                                 # lista de puntos del gráfico
    for i, valor in enumerate(por_mes):                         # recorre cada mes
        if maximo_mes == minimo_mes:                            # evita dividir por cero
            alto = 50
        else:                                                   # reparte las alturas entre 15% y 85%
            alto = 15 + (float(valor) - minimo_mes) / (maximo_mes - minimo_mes) * 70
        puntos.append({
            "left": round(i / (n - 1) * 100, 1),                # posición horizontal en %
            "bottom": round(float(alto), 1),                    # altura en %
        })

    # --- Rango de fechas (para mostrarlo en el filtro) ---
    fechas = pd.to_datetime(df["fecha"])                        # convierte la columna fecha a tipo fecha
    rango = f"{fechas.min().year} – {fechas.max().year}"        # ej. "2023 – 2024"

    # devuelve todos los datos en un diccionario listo para el HTML
    return {
        "total_pedidos": f"{total_pedidos:,}".replace(",", "."),  # "50.000"
        "ingresos": formato_dinero(ingresos),                     # "$2.54B"
        "calificacion": f"{calificacion:.1f}",                    # "3.8"
        "tiempo": f"{tiempo:.0f} min",                            # "17 min"
        "rango": rango,                                           # "2023 – 2024"
        "combos": combos,                                         # lista de barras
        "p_app": p_app, "p_tarjeta": p_tarjeta, "p_efectivo": p_efectivo,  # % de pagos
        "dona_estilo": dona_estilo,                               # degradado de la dona
        "heatmap": heatmap,                                       # filas del mapa de calor
        "puntos": puntos,                                         # puntos de ingresos por mes
    }
#-----------------------------------------
