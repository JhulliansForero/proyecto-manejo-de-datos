import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="SmartBite",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Tokens (del wireframe) ────────────────────────────────────────────────────
BG        = "#f5f5f4"
WHITE     = "#ffffff"
INK       = "#1c1917"
INK_MID   = "#57534e"
INK_SOFT  = "#a8a29e"
ACCENT    = "#f97316"
ACCENT_T  = "#fff7ed"
ACCENT_S  = "#fed7aa"
LINE      = "#d6d3d1"
LINE_S    = "#e7e5e4"
FILL      = "#e7e5e4"

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: {INK};
}}
.stApp {{
    background-color: {BG} !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

/* Tarjeta de login/registro */
.login-card [data-testid="stForm"] {{
    background: {WHITE};
    border: 1px solid {LINE_S};
    border-radius: 12px;
    padding: 32px 36px 28px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}}
.login-card [data-testid="stFormSubmitButton"] > button {{
    margin-top: 8px;
}}
section[data-testid="stSidebar"] {{
    background: {WHITE};
    border-right: 1px solid {LINE_S};
}}

/* Inputs */
.stTextInput > div > div > input {{
    border: 1px solid {LINE};
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    background: {WHITE};
    color: {INK};
    font-size: 13px;
}}
.stTextInput > div > div > input:focus {{
    border-color: {ACCENT};
    box-shadow: 0 0 0 2px rgba(249,115,22,0.15);
}}
.stTextInput label {{
    font-size: 11px !important;
    font-weight: 600 !important;
    color: {INK_MID} !important;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}

/* Selectbox */
.stSelectbox > div > div {{
    border: 1px solid {LINE};
    border-radius: 6px;
    background: {WHITE};
}}
.stSelectbox label, .stMultiSelect label, .stDateInput label {{
    font-size: 11px !important;
    font-weight: 600 !important;
    color: {INK_MID} !important;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}

/* Buttons */
.stButton > button {{
    background: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    height: 42px;
    width: 100%;
    font-size: 14px;
    transition: opacity .15s;
}}
.stButton > button:hover {{
    background: {ACCENT};
    opacity: 0.88;
    border: none;
}}
.stButton > button:active {{
    background: {ACCENT};
    border: none;
}}

/* Form submit */
[data-testid="stFormSubmitButton"] > button {{
    background: {ACCENT} !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    height: 44px !important;
    width: 100% !important;
    font-size: 14px !important;
}}

/* File uploader */
[data-testid="stFileUploader"] {{
    background: {ACCENT_T};
    border: 2px dashed {ACCENT};
    border-radius: 12px;
    padding: 8px;
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
    border: 1px solid {LINE_S};
    border-radius: 8px;
    overflow: hidden;
}}

/* Expander */
[data-testid="stExpander"] {{
    border: 1px solid {LINE_S};
    border-radius: 8px;
    background: {WHITE};
}}

/* Radio sidebar */
.stRadio > div {{
    gap: 2px;
}}
.stRadio > div > label {{
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 13px;
    color: {INK_MID};
    cursor: pointer;
}}
.stRadio > div > label:has(input:checked) {{
    background: {ACCENT_T};
    color: {INK};
    font-weight: 600;
}}

/* Metrics */
[data-testid="metric-container"] {{
    background: {WHITE};
    border: 1px solid {LINE_S};
    border-radius: 10px;
    padding: 16px 20px;
}}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "page": "login",
    "authenticated": False,
    "df": None,
    "user_name": "",
    "user_email": "",
    "sucursal": "Norte",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def logo_html(size=28):
    fs = int(size * 0.5)
    return (
        f'<div style="display:flex;align-items:center;gap:10px">'
        f'<div style="width:{size}px;height:{size}px;background:{INK};color:{ACCENT};'
        f'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        f'font-weight:800;font-size:{fs}px;letter-spacing:-1px;flex-shrink:0">SB</div>'
        f'<span style="font-weight:700;font-size:{int(size*0.6)}px;color:{INK};letter-spacing:-0.3px">'
        f'Smart<span style="color:{ACCENT}">Bite</span></span></div>'
    )

def kpi_html(label, value, delta, positive=True):
    dcolor = ACCENT if positive else "#ef4444"
    return (
        f'<div style="background:{WHITE};border:1px solid {LINE_S};border-radius:10px;padding:16px 20px">'
        f'<div style="font-size:10px;color:{INK_MID};text-transform:uppercase;letter-spacing:0.5px;font-weight:500">{label}</div>'
        f'<div style="font-size:24px;font-weight:700;color:{INK};margin:6px 0 4px;letter-spacing:-0.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{value}</div>'
        f'<div style="font-size:11px;color:{dcolor};font-weight:600;font-family:\'JetBrains Mono\',monospace">{delta}</div>'
        f'</div>'
    )

def section_title(title, subtitle=""):
    st.markdown(
        f'<div style="margin-bottom:6px">'
        f'<span style="font-size:15px;font-weight:700;color:{INK};letter-spacing:-0.3px">{title}</span>'
        + (f' <span style="font-size:11px;color:{INK_SOFT}">{subtitle}</span>' if subtitle else "")
        + "</div>",
        unsafe_allow_html=True,
    )

def topbar_html(right_content=""):
    st.markdown(
        f'<div style="background:{WHITE};border-bottom:1px solid {LINE_S};padding:14px 28px;'
        f'display:flex;align-items:center;justify-content:space-between">'
        f'{logo_html(24)}'
        f'<div style="font-size:12px;color:{INK_MID}">{right_content}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Page: Login ───────────────────────────────────────────────────────────────
def page_login():
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        # Marca la columna como login-card para el CSS de la tarjeta
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        with st.form("login_form"):
            # Logo + título dentro del form (= dentro de la tarjeta)
            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:center;margin-bottom:24px">'
                f'<div style="width:56px;height:56px;background:{INK};color:{ACCENT};border-radius:14px;'
                f'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:22px;'
                f'letter-spacing:-1px;margin-bottom:14px">SB</div>'
                f'<div style="font-size:20px;font-weight:700;color:{INK};letter-spacing:-0.4px;text-align:center">Bienvenido de vuelta</div>'
                f'<div style="font-size:12px;color:{INK_MID};margin-top:6px;text-align:center">Inicia sesión para ver tus analíticas</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            email    = st.text_input("Email", placeholder="tu@restaurante.com")
            password = st.text_input("Contraseña", placeholder="••••••••", type="password")
            ok = st.form_submit_button("Iniciar sesión")
            if ok:
                if email and password:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name  = email.split("@")[0].capitalize()
                    st.session_state.page = "upload"
                    st.rerun()
                else:
                    st.error("Ingresa tu email y contraseña.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="text-align:center;font-size:12px;color:{INK_MID};margin-top:12px">¿No tienes cuenta?</div>',
            unsafe_allow_html=True,
        )
        if st.button("Crear cuenta →", key="to_register"):
            st.session_state.page = "register"
            st.rerun()

# ── Page: Register ────────────────────────────────────────────────────────────
def page_register():
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        with st.form("register_form"):
            st.markdown(
                f'<div style="margin-bottom:20px">'
                f'<div style="font-size:22px;font-weight:700;color:{INK};letter-spacing:-0.5px">Crear cuenta</div>'
                f'<div style="font-size:12px;color:{INK_MID};margin-top:6px">Configura tu cuenta y selecciona tu sucursal</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            name     = st.text_input("Nombre completo", placeholder="Juan Pérez")
            email    = st.text_input("Email corporativo", placeholder="juan@smartbite.co")
            password = st.text_input("Contraseña", placeholder="Mínimo 8 caracteres", type="password")
            sucursal = st.selectbox("Sucursal", ["Norte", "Sur", "Centro", "El Lago", "Portal"])
            rol      = st.selectbox("Rol en la sucursal", ["Administrador", "Analista", "Gerente"])
            ok = st.form_submit_button("Crear cuenta")
            if ok:
                if name and email and len(password) >= 8:
                    st.session_state.authenticated = True
                    st.session_state.user_name     = name
                    st.session_state.user_email    = email
                    st.session_state.sucursal      = sucursal
                    st.session_state.page = "upload"
                    st.rerun()
                elif len(password) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                else:
                    st.error("Completa todos los campos.")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("← Ya tengo cuenta", key="to_login"):
            st.session_state.page = "login"
            st.rerun()

# ── Page: Upload ──────────────────────────────────────────────────────────────
def page_upload():
    topbar_html(
        f'Hola, <strong style="color:{INK}">{st.session_state.user_name}</strong>'
        f'&nbsp;&nbsp;·&nbsp;&nbsp;Sucursal {st.session_state.sucursal}'
    )

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2.2, 1])
    with col:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:28px">'
            f'<div style="font-size:26px;font-weight:700;color:{INK};letter-spacing:-0.5px">Cargar pedidos</div>'
            f'<div style="font-size:13px;color:{INK_MID};margin-top:8px">'
            f'Sube tu archivo de pedidos y SmartBite analizará todo automáticamente.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Arrastra tu archivo CSV aquí · .csv · .xlsx · max 100 MB",
            type=["csv", "xlsx"],
        )

        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.session_state.df = df

                st.markdown(
                    f'<div style="background:{WHITE};border:1px solid {LINE_S};border-radius:8px;'
                    f'padding:14px 20px;margin:16px 0;display:flex;align-items:center;gap:14px">'
                    f'<div style="width:38px;height:38px;background:{ACCENT_T};border-radius:8px;'
                    f'display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">📄</div>'
                    f'<div>'
                    f'<div style="font-weight:600;font-size:13px;color:{INK}">{uploaded.name}</div>'
                    f'<div style="font-size:11px;color:{INK_SOFT};font-family:\'JetBrains Mono\',monospace">'
                    f'{len(df):,} filas &nbsp;·&nbsp; {len(df.columns)} columnas</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div style="font-size:12px;font-weight:600;color:{INK_MID};margin-bottom:6px">Vista previa</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(df.head(6), use_container_width=True, hide_index=True)

                if st.button("Analizar datos →"):
                    st.session_state.page = "dashboard"
                    st.rerun()

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
        else:
            st.markdown(
                f'<div style="text-align:center;margin-top:12px">'
                f'<span style="font-size:12px;color:{INK_SOFT}">Formatos soportados: '
                f'<code style="background:{FILL};padding:2px 6px;border-radius:4px">.csv</code> '
                f'<code style="background:{FILL};padding:2px 6px;border-radius:4px">.xlsx</code></span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("← Cerrar sesión", key="logout"):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()

# ── Page: Dashboard ───────────────────────────────────────────────────────────
def page_dashboard():
    df_raw: pd.DataFrame = st.session_state.df

    if "fecha" in df_raw.columns:
        df_raw["fecha"] = pd.to_datetime(df_raw["fecha"], errors="coerce")

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f'<div style="padding:8px 0 20px">{logo_html(22)}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="font-size:10px;color:{INK_SOFT};letter-spacing:1px;font-weight:600;'
            f'text-transform:uppercase;margin-bottom:6px">Análisis</div>',
            unsafe_allow_html=True,
        )
        st.radio("nav", ["Dashboard", "Cargar datos", "Combos", "Sucursales", "Tiempos", "Empleados"], label_visibility="collapsed")

        st.markdown(f'<div style="border-top:1px solid {LINE_S};margin:16px 0"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:10px;color:{INK_SOFT};letter-spacing:1px;font-weight:600;'
            f'text-transform:uppercase;margin-bottom:8px">Filtros</div>',
            unsafe_allow_html=True,
        )

        sucursales = (["Todas"] + sorted(df_raw["sucursal"].dropna().unique().tolist())
                      if "sucursal" in df_raw.columns else ["Todas"])
        suc_sel = st.selectbox("Sucursal", sucursales)

        fecha_range = None
        if "fecha" in df_raw.columns:
            fecha_min = df_raw["fecha"].min().date()
            fecha_max = df_raw["fecha"].max().date()
            fecha_range = st.date_input("Rango de fechas", value=(fecha_min, fecha_max),
                                        min_value=fecha_min, max_value=fecha_max)

        cat_sel = None
        if "categoria" in df_raw.columns:
            cats = sorted(df_raw["categoria"].dropna().unique().tolist())
            cat_sel = st.multiselect("Categoría", cats, default=cats)

        st.markdown(f'<div style="border-top:1px solid {LINE_S};margin:16px 0"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:12px;color:{ACCENT};font-weight:700">{len(df_raw):,} pedidos</div>'
            f'<div style="font-size:11px;color:{INK_SOFT}">en el dataset cargado</div>',
            unsafe_allow_html=True,
        )
        if st.button("← Cargar otro archivo", key="new_file"):
            st.session_state.df = None
            st.session_state.page = "upload"
            st.rerun()

    # ── Apply filters ─────────────────────────────────────────────────────────
    dff = df_raw.copy()
    if suc_sel != "Todas" and "sucursal" in dff.columns:
        dff = dff[dff["sucursal"] == suc_sel]
    if fecha_range and len(fecha_range) == 2 and "fecha" in dff.columns:
        dff = dff[(dff["fecha"].dt.date >= fecha_range[0]) & (dff["fecha"].dt.date <= fecha_range[1])]
    if cat_sel is not None and "categoria" in dff.columns:
        dff = dff[dff["categoria"].isin(cat_sel)]

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="padding:20px 28px 0">'
        f'<div style="font-size:22px;font-weight:700;color:{INK};letter-spacing:-0.4px">Dashboard</div>'
        f'<div style="font-size:12px;color:{INK_MID};margin-top:4px">'
        f'Resumen general · <span style="font-family:\'JetBrains Mono\',monospace">{len(dff):,}</span> pedidos analizados</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_pedidos = len(dff)
    ingresos      = dff["precio_total"].sum()           if "precio_total"           in dff.columns else 0
    calificacion  = dff["calificacion"].mean()          if "calificacion"           in dff.columns else 0
    tiempo        = dff["tiempo_preparacion_min"].mean() if "tiempo_preparacion_min" in dff.columns else 0
    std_precio    = dff["precio_total"].std()           if "precio_total"           in dff.columns else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_html("Total pedidos",      f"{total_pedidos:,}",          "+12.4%"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_html("Ingresos totales",   f"$ {ingresos/1e9:.2f} B",     "+8.2%"),  unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_html("Calificación prom.", f"{calificacion:.2f} ⭐",       "+0.2"),   unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_html("Tiempo prom. prep.", f"{tiempo:.0f} min",           "-1.2 min", positive=False), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Estadísticas descriptivas ─────────────────────────────────────────────
    with st.expander("📊 Estadísticas descriptivas — media, desviación estándar, min, max"):
        num_cols = dff.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            st.dataframe(dff[num_cols].describe().round(2), use_container_width=True)
        else:
            st.info("No hay columnas numéricas en el dataset filtrado.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Combos + Métodos de pago ──────────────────────────────────────────────
    col_bar, col_pie = st.columns([1.5, 1])

    with col_bar:
        section_title("Combos más vendidos", "top 10")
        if "nombre_combo" in dff.columns:
            counts = dff["nombre_combo"].value_counts().head(10).reset_index()
            counts.columns = ["Combo", "Pedidos"]
            colors = [ACCENT if i == 0 else FILL for i in range(len(counts))]
            fig = go.Figure(go.Bar(
                x=counts["Pedidos"], y=counts["Combo"],
                orientation="h",
                marker_color=colors,
                text=counts["Pedidos"],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color=INK_MID),
            ))
            fig.update_layout(
                height=320,
                margin=dict(l=0, r=20, t=4, b=0),
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                font=dict(family="Inter", color=INK, size=12),
                yaxis=dict(autorange="reversed", gridcolor=LINE_S),
                xaxis=dict(gridcolor=LINE_S, gridwidth=0.5),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columna 'nombre_combo' no encontrada.")

    with col_pie:
        section_title("Métodos de pago", "distribución %")
        if "metodo_pago" in dff.columns:
            pago = dff["metodo_pago"].value_counts().reset_index()
            pago.columns = ["Método", "Pedidos"]
            fig2 = go.Figure(go.Pie(
                labels=pago["Método"], values=pago["Pedidos"],
                hole=0.42,
                marker=dict(colors=[ACCENT, INK, ACCENT_S, LINE]),
                textfont=dict(family="Inter", size=12),
            ))
            fig2.update_layout(
                height=320,
                margin=dict(l=0, r=0, t=4, b=0),
                paper_bgcolor=WHITE,
                font=dict(family="Inter", color=INK),
                legend=dict(orientation="v", yanchor="middle", y=0.5, font=dict(size=11)),
                showlegend=True,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Columna 'metodo_pago' no encontrada.")

    # ── Mapa de calor ─────────────────────────────────────────────────────────
    section_title("Ventas por hora y día de la semana", "pedidos / hora · el naranja indica mayor actividad")
    if "hora" in dff.columns and "dia_semana" in dff.columns:
        dff2 = dff.copy()
        dff2["hora_num"] = dff2["hora"].astype(str).str.split(":").str[0].astype(int, errors="ignore")

        dia_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dia_es    = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
                     "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}

        heat = dff2.groupby(["dia_semana", "hora_num"]).size().reset_index(name="pedidos")
        pivot = heat.pivot(index="dia_semana", columns="hora_num", values="pedidos").fillna(0)
        available = [d for d in dia_order if d in pivot.index]
        pivot = pivot.reindex(available)
        pivot.index = [dia_es.get(d, d) for d in pivot.index]

        fig3 = px.imshow(
            pivot,
            color_continuous_scale=[[0, WHITE], [0.2, ACCENT_T], [0.6, ACCENT_S], [1, ACCENT]],
            aspect="auto",
            labels=dict(x="Hora del día", y="Día", color="Pedidos"),
        )
        fig3.update_layout(
            height=270,
            margin=dict(l=0, r=0, t=4, b=0),
            paper_bgcolor=WHITE,
            plot_bgcolor=WHITE,
            font=dict(family="Inter", color=INK, size=11),
            coloraxis_showscale=True,
        )
        fig3.update_xaxes(side="bottom")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Columnas 'hora' y 'dia_semana' no encontradas.")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Ingresos por mes + Top combos ─────────────────────────────────────────
    col_line, col_top = st.columns([1.6, 1])

    with col_line:
        section_title("Ingresos por mes", "$ COP — tendencia")
        if "fecha" in dff.columns and "precio_total" in dff.columns:
            dff3 = dff.copy()
            dff3["mes"] = dff3["fecha"].dt.to_period("M").astype(str)
            monthly = dff3.groupby("mes")["precio_total"].sum().reset_index()
            monthly.columns = ["Mes", "Ingresos"]

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=monthly["Mes"], y=monthly["Ingresos"],
                mode="lines+markers",
                line=dict(color=ACCENT, width=2.5),
                marker=dict(size=5, color=WHITE, line=dict(color=ACCENT, width=2)),
                fill="tozeroy",
                fillcolor="rgba(249,115,22,0.08)",
            ))
            fig4.update_layout(
                height=280,
                margin=dict(l=0, r=0, t=4, b=0),
                plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                font=dict(family="Inter", color=INK, size=11),
                xaxis=dict(tickangle=-30, gridcolor=LINE_S),
                yaxis=dict(gridcolor=LINE_S, tickformat=".2s"),
                showlegend=False,
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Columnas 'fecha' o 'precio_total' no encontradas.")

    with col_top:
        section_title("Top 5 combos por rating", "media ⭐")
        if "nombre_combo" in dff.columns and "calificacion" in dff.columns:
            top = (
                dff.groupby("nombre_combo")
                   .agg(Rating=("calificacion", "mean"), Pedidos=("calificacion", "count"))
                   .sort_values("Rating", ascending=False)
                   .head(5)
                   .round(2)
                   .reset_index()
                   .rename(columns={"nombre_combo": "Combo"})
            )
            st.dataframe(top, use_container_width=True, hide_index=True)
        else:
            st.info("Columnas necesarias no encontradas.")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Bebidas + Estadísticas extra ──────────────────────────────────────────
    col_beb, col_extra = st.columns([1, 1.6])

    with col_beb:
        section_title("Bebidas favoritas", "pedidos")
        if "bebida" in dff.columns:
            beb = dff["bebida"].value_counts().reset_index()
            beb.columns = ["Bebida", "Pedidos"]
            fig5 = go.Figure(go.Pie(
                labels=beb["Bebida"], values=beb["Pedidos"],
                hole=0.42,
                marker=dict(colors=[ACCENT, INK, ACCENT_S, LINE, "#78716c"]),
                textfont=dict(family="Inter", size=11),
            ))
            fig5.update_layout(
                height=260,
                margin=dict(l=0, r=0, t=4, b=0),
                paper_bgcolor=WHITE,
                font=dict(family="Inter", color=INK),
                legend=dict(orientation="v", y=0.5, font=dict(size=10)),
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Columna 'bebida' no encontrada.")

    with col_extra:
        section_title("Resumen estadístico completo", "media · desv. estándar · mín · máx")
        num_cols = ["precio_total", "calificacion", "tiempo_preparacion_min", "cantidad", "precio_base"]
        existing = [c for c in num_cols if c in dff.columns]
        if existing:
            stats = dff[existing].describe().round(2)
            stats.index = ["Conteo", "Media", "Desv. Est.", "Mín", "Q1 (25%)", "Mediana", "Q3 (75%)", "Máx"]
            st.dataframe(stats, use_container_width=True)
        else:
            st.info("No hay columnas numéricas disponibles.")

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "login":
    page_login()
elif page == "register":
    page_register()
elif page == "upload":
    if not st.session_state.authenticated:
        st.session_state.page = "login"
        st.rerun()
    page_upload()
elif page == "dashboard":
    if st.session_state.df is None:
        st.session_state.page = "upload"
        st.rerun()
    page_dashboard()
