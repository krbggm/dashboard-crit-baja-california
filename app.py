import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CRIT BC | Visualización de bajas", page_icon="📊", layout="wide")

st.markdown("""
<style>
:root { --navy:#192E68; --navy2:#253F82; --purple:#5542B8; --lavender:#EDEBFF; --pale:#F7F8FE; --ink:#1D2B57; --muted:#7380A3; --line:#DDE4F5; }
.stApp { background: #F7F8FE; color: var(--ink); }
[data-testid="stHeader"] { background: rgba(247,248,254,.96); }
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1600px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#192E68 0%,#263E7D 78%,#5542B8 100%); border-right: 0; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#DDE5FF !important; }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.22); }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.65rem; }
h1,h2,h3 { color:var(--navy) !important; letter-spacing:-.025em; }
h1 { font-weight:800 !important; }
[data-testid="stCaptionContainer"] { color:var(--muted); }
[data-testid="stMetric"] { background:linear-gradient(145deg,#FFFFFF 0%,#F0EEFF 100%); border:1px solid #DCD8FA; border-radius:13px; padding:13px 14px; box-shadow:0 3px 12px rgba(39,55,115,.06); min-height:100px; }
[data-testid="stMetricLabel"] p { color:#59658E !important; font-size:.78rem !important; line-height:1.25 !important; }
[data-testid="stMetricValue"] { color:var(--purple) !important; font-weight:800 !important; font-size:1.8rem !important; }
[data-testid="stAlert"] { border-radius:10px; border-left-width:4px; }
div[data-baseweb="select"] > div, div[data-baseweb="popover"] { border-radius:9px; }
.stButton > button { background:var(--purple); color:white; border:0; border-radius:9px; }
hr { border-color:var(--line); }
[data-testid="stExpander"] { border:1px solid var(--line); border-radius:11px; background:white; }
[data-testid="stPlotlyChart"] { background:#FFFFFF; border:1px solid #E2E7F5; border-radius:13px; padding:8px 8px 0 8px; }
/* Horizontal filter band */
.filter-band { background:#FFFFFF; border:1px solid #DFE5F4; border-radius:14px; padding:13px 16px 3px 16px; margin:8px 0 16px 0; box-shadow:0 3px 12px rgba(39,55,115,.04); }
.small-kicker { color:#DCD8FF; font-size:.7rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "publica"

@st.cache_data
def load_data():
    files = {
        "mensual": "serie_mensual.csv",
        "servicio": "por_servicio.csv",
        "municipio": "por_municipio.csv",
        "clinica": "por_clinica.csv",
        "estatus": "por_estatus_servicio.csv",
        "servicio_municipio": "servicio_municipio.csv",
        "servicio_estatus": "servicio_estatus.csv",
        "anual": "resumen_anual.csv",
        "estatus_anio": "estatus_por_anio.csv",
    }
    tables = {k: pd.read_csv(DATA / v) for k, v in files.items()}
    meta = json.loads((DATA / "metadatos.json").read_text(encoding="utf-8"))
    return tables, meta

tables, meta = load_data()
PURPLE_SEQUENCE = ["#512879", "#7851A9", "#A58BC4", "#C8B4DE", "#6F4C8E", "#D9CBE8"]
years = sorted(tables["anual"]["anio"].dropna().astype(int).unique().tolist())
if not years:
    st.error("No hay datos agregados disponibles.")
    st.stop()

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:8px 4px 16px 4px'><div style='font-size:2rem'>✿</div><div style='font-size:1.2rem;font-weight:850;letter-spacing:.05em'>CRIT</div><div style='font-size:.72rem;color:#DDE5FF'>BAJA CALIFORNIA</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ▦  Navegación")
    page = st.radio(
        "Ir a sección",
        ["Resumen", "Indicadores", "Tendencias", "Distribuciones", "Metodología"],
        key="navigation_page",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Prototipo académico · Datos agregados")

st.markdown("""<div style='background:linear-gradient(110deg,#FFFFFF 0%,#F0EEFF 100%);border:1px solid #E1E4F5;border-radius:15px;padding:16px 22px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:16px;box-shadow:0 4px 14px rgba(29,46,104,.05)'><div><div style='font-size:.72rem;font-weight:800;letter-spacing:.12em;color:#5542B8;text-transform:uppercase'>CRIT Baja California · Prototipo académico</div><div style='font-size:clamp(1.35rem,2.5vw,2rem);font-weight:850;line-height:1.15;color:#192E68;margin-top:6px'>Plataforma de visualización de datos</div><div style='font-size:.95rem;color:#59658E;margin-top:5px'>Control y seguimiento de bajas administrativas</div></div><div style='min-width:150px;text-align:right;color:#5542B8;font-size:.8rem;font-weight:700'>PANEL DE SEGUIMIENTO<br><span style='font-weight:400;color:#7380A3'>2022–2026 · periodo parcial</span></div></div>""", unsafe_allow_html=True)
st.caption("Herramienta de apoyo al análisis y a la toma de decisiones · Registros con estatus administrativo BAJA")
st.warning(
    "Alcance de interpretación: la base contiene registros con estatus administrativo BAJA. "
    "Esto no confirma por sí solo abandono terapéutico. Las cifras de servicios/estados pueden "
    "contar a una misma persona en más de una categoría."
)

municipalities = sorted(tables["municipio"]["municipio"].dropna().astype(str).unique().tolist())
services = sorted(tables["servicio"]["servicio"].dropna().astype(str).unique().tolist())
st.markdown("<div class='filter-band'><div style='font-size:.78rem;font-weight:800;color:#192E68;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px'>⌕  Filtros de consulta</div>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([1.2, 1, 1.5])
with f1:
    selected_years = st.multiselect("Periodo de baja", years, default=years)
with f2:
    selected_municipality = st.selectbox("Municipio", ["Todos"] + municipalities)
with f3:
    selected_service = st.selectbox("Servicio", ["Todos"] + services)
st.markdown("</div>", unsafe_allow_html=True)
st.caption("Las distribuciones con dimensiones combinadas solo muestran grupos con 5 o más pacientes.")

def filter_year(d):
    return d[d["anio"].isin(selected_years)].copy()

# Core metrics based on independent aggregate tables. Avoid summing across services.
monthly = filter_year(tables["mensual"])
service = filter_year(tables["servicio"])
municipality = filter_year(tables["municipio"])
clinic = filter_year(tables["clinica"])
status = filter_year(tables["estatus"])
sm = filter_year(tables["servicio_municipio"])
ss = filter_year(tables["servicio_estatus"])

annual_selected = tables["anual"][tables["anual"]["anio"].isin(selected_years)]
total_patients = int(annual_selected["pacientes_unicos"].sum()) if not annual_selected.empty else 0
months_count = int(monthly[["anio", "mes"]].drop_duplicates().shape[0]) if not monthly.empty else 0
services_count = int(service["servicio"].nunique()) if not service.empty else 0
municipalities_count = int(municipality["municipio"].nunique()) if not municipality.empty else 0
clinics_count = int(clinic["clinica"].nunique()) if not clinic.empty else 0
status_y = tables["estatus_anio"][tables["estatus_anio"]["anio"].isin(selected_years)]
def status_patients(label):
    d = status_y[status_y["estatus_servicio"].astype(str).str.upper() == label]
    return int(d["pacientes_unicos"].sum()) if not d.empty else 0

if page in ["Resumen", "Indicadores"]:
    st.info(
        "Los indicadores de pacientes por mes cuentan pacientes únicos dentro de cada mes. "
        "Los conteos por servicio, municipio, clínica y estado son distribuciones independientes; "
        "no deben sumarse entre categorías para obtener el total general."
    )

    st.subheader("Indicadores de seguimiento")
    row1 = st.columns(6)
    row1[0].metric("Pacientes con baja administrativa", f"{total_patients:,}")
    row1[1].metric("Servicios analizados", f"{services_count:,}")
    row1[2].metric("Meses con datos", f"{months_count:,}")
    row1[3].metric("Registros con inasistencia", f"{status_patients('INASISTENCIA'):,}")
    row1[4].metric("Municipios representados", f"{municipalities_count:,}")
    row1[5].metric("Clínicas representadas", f"{clinics_count:,}")
    with st.expander("Otros estados de cita registrados"):
        row2 = st.columns(3)
        row2[0].metric("Registro TOMADA", f"{status_patients('TOMADA'):,}")
        row2[1].metric("Registro CANCELADA", f"{status_patients('CANCELADA'):,}")
        row2[2].metric("Registro POSPUESTA", f"{status_patients('POSPUESTA'):,}")

if page in ["Resumen", "Tendencias"]:
    st.subheader("1. Evolución de bajas por mes")
    if monthly.empty:
        st.info("No hay grupos que mostrar para la selección actual.")
    else:
        monthly["periodo"] = pd.to_datetime(
            monthly["anio"].astype(int).astype(str) + "-" + monthly["mes"].astype(int).astype(str).str.zfill(2) + "-01"
        )
        fig = px.line(monthly.sort_values("periodo"), x="periodo", y="pacientes_unicos", markers=True,
                      labels={"periodo":"Mes de baja", "pacientes_unicos":"Pacientes únicos"}, color_discrete_sequence=PURPLE_SEQUENCE)
        fig.update_layout(template="plotly_white", colorway=PURPLE_SEQUENCE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#443650", family="Arial"), margin=dict(l=10,r=10,t=20,b=10), hoverlabel=dict(bgcolor="#512879", font_color="white"))
        st.plotly_chart(fig, use_container_width=True)

if page == "Distribuciones":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("2. Distribución por servicio")
        if selected_municipality != "Todos":
            d = sm[sm["municipio"].astype(str) == selected_municipality]
            if selected_service != "Todos":
                d = d[d["servicio"].astype(str) == selected_service]
            d = d.groupby("servicio", as_index=False)["pacientes_unicos"].sum()
        else:
            d = service.groupby("servicio", as_index=False)["pacientes_unicos"].sum()
            if selected_service != "Todos":
                d = d[d["servicio"].astype(str) == selected_service]
        d = d.sort_values("pacientes_unicos", ascending=False).head(15)
        if d.empty:
            st.info("No hay grupos visibles con la combinación seleccionada.")
        else:
            fig = px.bar(d.sort_values("pacientes_unicos"), x="pacientes_unicos", y="servicio", orientation="h",
                         labels={"pacientes_unicos":"Pacientes únicos en el grupo", "servicio":"Servicio"}, color_discrete_sequence=["#7851A9"])
            fig.update_layout(template="plotly_white", colorway=PURPLE_SEQUENCE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#443650", family="Arial"), margin=dict(l=10,r=10,t=20,b=10), hoverlabel=dict(bgcolor="#512879", font_color="white"))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("3. Bajas por municipio")
        if selected_service != "Todos":
            d = sm[sm["servicio"].astype(str) == selected_service]
            if selected_municipality != "Todos":
                d = d[d["municipio"].astype(str) == selected_municipality]
            d = d.groupby("municipio", as_index=False)["pacientes_unicos"].sum()
        else:
            d = municipality.groupby("municipio", as_index=False)["pacientes_unicos"].sum()
            if selected_municipality != "Todos":
                d = d[d["municipio"].astype(str) == selected_municipality]
        d = d.sort_values("pacientes_unicos", ascending=False)
        if d.empty:
            st.info("No hay grupos visibles con la combinación seleccionada.")
        else:
            fig = px.bar(d, x="municipio", y="pacientes_unicos",
                         labels={"pacientes_unicos":"Pacientes únicos en el grupo", "municipio":"Municipio"}, color_discrete_sequence=["#7851A9"])
            fig.update_layout(template="plotly_white", colorway=PURPLE_SEQUENCE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#443650", family="Arial"), margin=dict(l=10,r=10,t=20,b=10), xaxis_tickangle=-30, hoverlabel=dict(bgcolor="#512879", font_color="white"))
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("4. Estados de servicio")
        d = status.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum()
        if selected_service != "Todos":
            d2 = ss[ss["servicio"].astype(str) == selected_service]
            d = d2.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum()
        if d.empty:
            st.info("No hay grupos visibles para esta selección.")
        else:
            fig = px.bar(d.sort_values("pacientes_unicos", ascending=False), x="estatus_servicio", y="pacientes_unicos",
                         labels={"pacientes_unicos":"Pacientes con al menos un registro", "estatus_servicio":"Estado"}, color_discrete_sequence=["#7851A9"])
            fig.update_layout(template="plotly_white", colorway=PURPLE_SEQUENCE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#443650", family="Arial"), margin=dict(l=10,r=10,t=20,b=10), hoverlabel=dict(bgcolor="#512879", font_color="white"))
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("5. Distribución por clínica")
        d = clinic.groupby("clinica", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False)
        if d.empty:
            st.info("No hay grupos visibles para esta selección.")
        else:
            fig = px.bar(d, x="clinica", y="pacientes_unicos",
                         labels={"pacientes_unicos":"Pacientes únicos en el grupo", "clinica":"Clínica"}, color_discrete_sequence=["#7851A9"])
            fig.update_layout(template="plotly_white", colorway=PURPLE_SEQUENCE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#443650", family="Arial"), margin=dict(l=10,r=10,t=20,b=10), xaxis_tickangle=-30, hoverlabel=dict(bgcolor="#512879", font_color="white"))
            st.plotly_chart(fig, use_container_width=True)

if page == "Metodología":
    with st.expander("Criterios metodológicos y limitaciones"):
        st.markdown("""
        - **Unidad de análisis:** el paciente se cuenta como único dentro de cada grupo mediante carnet durante el cálculo local; el carnet no se publica.
        - **No aditividad:** una persona puede aparecer en varios servicios o estados. No se deben sumar esas distribuciones para inferir pacientes totales.
        - **Supresión:** los grupos con menos de 5 pacientes no se exportan a los archivos públicos.
        - **Periodo:** 2026 es parcial según las fechas disponibles y no debe compararse como año completo.
        - **Interpretación:** la baja administrativa no demuestra por sí sola abandono terapéutico.
        - **Validación pendiente:** confirmar con la fuente institucional el significado de fecha_baja, fecha_ultima_cita y la granularidad de cada fila.
        """)

st.caption("Prototipo de apoyo a la toma de decisiones. No sustituye el expediente clínico ni constituye una herramienta diagnóstica.")
