import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="CRIT Baja California | Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).parent
DATA = ROOT / "data" / "publica"

NAVY = "#172E68"
NAVY2 = "#243F82"
PURPLE = "#5540B7"
PURPLE2 = "#7A62D3"
LAVENDER = "#EEEAFE"
PALE = "#F6F8FE"
INK = "#26365F"
MUTED = "#7784A8"
LINE = "#DDE4F3"
TEAL = "#4BAEAA"
CORAL = "#F17C87"
GOLD = "#F0C75E"

st.markdown(f"""
<style>
:root {{ --navy:{NAVY}; --navy2:{NAVY2}; --purple:{PURPLE}; --pale:{PALE}; --ink:{INK}; --muted:{MUTED}; --line:{LINE}; }}
.stApp {{ background:var(--pale); color:var(--ink); }}
[data-testid="stHeader"] {{ background:rgba(246,248,254,.96); }}
.block-container {{ max-width:1600px; padding-top:1.0rem; padding-bottom:2rem; }}
[data-testid="stSidebar"] {{ background:linear-gradient(180deg,#192F68 0%,#253F7E 74%,#5744B8 100%); border-right:3px solid #D6D0F7; }}
[data-testid="stSidebar"] * {{ color:#fff !important; }}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color:#E1E8FF !important; }}
[data-testid="stSidebar"] hr {{ border-color:rgba(255,255,255,.25); }}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{ padding:5px 7px; border-radius:8px; }}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{ background:rgba(255,255,255,.12); }}
h1,h2,h3,h4 {{ color:{NAVY} !important; letter-spacing:-.025em; }}
h1 {{ font-size:1.65rem !important; font-weight:850 !important; }}
h2 {{ font-size:1.12rem !important; font-weight:800 !important; }}
h3 {{ font-size:1rem !important; font-weight:750 !important; }}
[data-testid="stCaptionContainer"] {{ color:{MUTED}; }}
[data-testid="stMetric"] {{ background:linear-gradient(145deg,#FFFFFF 0%,#F0EEFF 100%); border:1px solid #DDD8F8; border-radius:13px; padding:12px 13px; box-shadow:0 3px 12px rgba(35,53,111,.055); min-height:102px; }}
[data-testid="stMetricLabel"] p {{ color:#5C6990 !important; font-size:.74rem !important; line-height:1.2 !important; }}
[data-testid="stMetricValue"] {{ color:{PURPLE} !important; font-weight:850 !important; font-size:1.7rem !important; }}
[data-testid="stPlotlyChart"] {{ background:#fff; border:1px solid #E1E7F5; border-radius:13px; padding:5px; box-shadow:0 2px 8px rgba(35,53,111,.035); }}
[data-testid="stAlert"] {{ border-radius:10px; }}
div[data-baseweb="select"] > div {{ border-radius:9px; background:#F0F2F7; border-color:#E5E9F3; }}
hr {{ border-color:{LINE}; }}
.brand-header {{ display:flex; align-items:center; justify-content:space-between; gap:14px; background:linear-gradient(100deg,#FFFFFF 0%,#F0EEFF 100%); border:1px solid #E0E5F4; border-radius:15px; padding:13px 18px; margin:0 0 9px 0; box-shadow:0 4px 13px rgba(29,46,104,.05); }}
.brand-left {{ display:flex; align-items:center; gap:12px; }}
.brand-mark {{ display:flex; align-items:center; justify-content:center; width:50px; height:50px; border-radius:13px; background:{NAVY}; color:#fff; font-size:26px; flex-shrink:0; }}
.brand-name {{ font-size:1.08rem; font-weight:850; color:{NAVY}; line-height:1.1; }}
.brand-sub {{ font-size:.75rem; color:{MUTED}; margin-top:4px; }}
.brand-title {{ font-size:1.35rem; font-weight:850; color:{NAVY}; line-height:1.18; }}
.brand-meta {{ text-align:right; font-size:.75rem; color:{PURPLE}; font-weight:800; min-width:145px; }}
.brand-meta span {{ font-weight:400; color:{MUTED}; }}
.section-kicker {{ color:{NAVY}; font-size:.76rem; font-weight:850; letter-spacing:.09em; text-transform:uppercase; background:#fff; border:1px solid {LINE}; border-radius:11px; padding:10px 13px; margin:8px 0 10px 0; }}
.filter-note {{ font-size:.75rem; color:{MUTED}; margin:0 0 12px 0; }}
.footer-note {{ font-size:.72rem; color:{MUTED}; border-top:1px solid {LINE}; padding-top:10px; margin-top:16px; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    names = {
        "mensual":"serie_mensual.csv", "servicio":"por_servicio.csv", "municipio":"por_municipio.csv",
        "clinica":"por_clinica.csv", "estatus":"por_estatus_servicio.csv", "sm":"servicio_municipio.csv",
        "ss":"servicio_estatus.csv", "anual":"resumen_anual.csv", "estatus_anio":"estatus_por_anio.csv"
    }
    tables = {k: pd.read_csv(DATA / v) for k, v in names.items()}
    meta_path = DATA / "metadatos.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    return tables, meta

try:
    T, META = load_data()
except Exception as exc:
    st.error("No se pudieron cargar los archivos agregados. Verifica que exista la carpeta data/publica con sus CSV.")
    st.code(str(exc))
    st.stop()

years = sorted(T["anual"]["anio"].dropna().astype(int).unique().tolist())
if not years:
    st.error("No hay datos agregados disponibles.")
    st.stop()

with st.sidebar:
    st.markdown(f"""<div style='text-align:center;padding:14px 4px 19px 4px'>
    <div style='font-size:2.1rem;line-height:1.1'>✿</div><div style='font-size:1.45rem;font-weight:900;letter-spacing:.08em;margin-top:4px'>CRIT</div>
    <div style='font-size:.72rem;letter-spacing:.04em;color:#DDE5FF'>BAJA CALIFORNIA</div></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ▦ Navegación")
    page = st.radio("Sección", ["Resumen", "Indicadores", "Tendencias", "Distribuciones", "Metodología"], key="page", label_visibility="collapsed", format_func=lambda x: {"Resumen":"⌂  Resumen", "Indicadores":"◉  Indicadores", "Tendencias":"◷  Tendencias", "Distribuciones":"▥  Distribuciones", "Metodología":"♡  Metodología"}[x])
    st.markdown("---")
    st.markdown("<div style='font-size:.72rem;color:#DDE5FF'>Prototipo académico<br>Datos agregados · Sin identificadores</div>", unsafe_allow_html=True)

st.markdown(f"""<div class='brand-header'><div class='brand-left'><div class='brand-mark'>✿</div><div><div class='brand-name'>CRIT <span style='font-weight:500'>| Baja California</span></div><div class='brand-sub'>Plataforma de Visualización de Datos · Control del Abandono Terapéutico*</div></div></div><div><div class='brand-title'>Panel de seguimiento</div><div class='brand-sub'>Prototipo académico · Bajas administrativas</div></div><div class='brand-meta'>PERIODO DE ANÁLISIS<br><span>2022–2026 · 2026 parcial</span></div></div>""", unsafe_allow_html=True)

st.markdown("<div class='filter-note'>*La base disponible identifica bajas administrativas; no confirma por sí sola abandono terapéutico.</div>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>⌕ &nbsp; Filtros de consulta</div>", unsafe_allow_html=True)
municipalities = sorted(T["municipio"]["municipio"].dropna().astype(str).unique().tolist())
services = sorted(T["servicio"]["servicio"].dropna().astype(str).unique().tolist())
f1, f2, f3 = st.columns([1.15, 1, 1.55])
with f1:
    selected_years = st.multiselect("Periodo de baja", years, default=years, key="years")
with f2:
    selected_municipality = st.selectbox("Municipio", ["Todos"] + municipalities, key="municipality")
with f3:
    selected_service = st.selectbox("Servicio", ["Todos"] + services, key="service")
st.markdown("<div class='filter-note'>Las distribuciones combinadas muestran únicamente grupos con al menos 5 pacientes. Los conteos por categoría pueden superponerse.</div>", unsafe_allow_html=True)

# Filters by selected year
sel = set(int(y) for y in selected_years)
def fy(key):
    return T[key][T[key]["anio"].astype(int).isin(sel)].copy()
monthly, service, municipality, clinic, status, sm, ss = [fy(k) for k in ["mensual","servicio","municipio","clinica","estatus","sm","ss"]]
annual = T["anual"][T["anual"]["anio"].astype(int).isin(sel)]
status_y = T["estatus_anio"][T["estatus_anio"]["anio"].astype(int).isin(sel)]
if selected_municipality != "Todos":
    sm = sm[sm["municipio"].astype(str) == selected_municipality]
if selected_service != "Todos":
    service = service[service["servicio"].astype(str) == selected_service]
    sm = sm[sm["servicio"].astype(str) == selected_service]
    ss = ss[ss["servicio"].astype(str) == selected_service]

patients = int(annual["pacientes_unicos"].sum()) if not annual.empty else 0
months = int(monthly[["anio","mes"]].drop_duplicates().shape[0]) if not monthly.empty else 0
n_services = int(service["servicio"].nunique()) if not service.empty else 0
n_munis = int(municipality["municipio"].nunique()) if not municipality.empty else 0
n_clinics = int(clinic["clinica"].nunique()) if not clinic.empty else 0
def status_count(label):
    d = status_y[status_y["estatus_servicio"].astype(str).str.upper() == label]
    return int(d["pacientes_unicos"].sum()) if not d.empty else 0

if page == "Resumen":
    st.markdown("<div class='section-kicker'>◉ &nbsp; Indicadores de seguimiento</div>", unsafe_allow_html=True)
    kpi_cols = st.columns(6)
    kpis = [
        ("Total de pacientes con baja", f"{patients:,}", "Únicos por año"),
        ("Pacientes con baja en registros", f"{patients:,}", "Base administrativa"),
        ("Total de citas/meses", f"{months:,}", "Meses con datos"),
        ("Registros de inasistencia", f"{status_count('INASISTENCIA'):,}", "Distribución de estado"),
        ("Servicios analizados", f"{n_services:,}", "Representados"),
        ("Municipios representados", f"{n_munis:,}", "En los datos"),
    ]
    for col, (label, value, helptext) in zip(kpi_cols, kpis):
        with col:
            st.metric(label, value, help=helptext)
    st.caption("Las cifras de estados, servicios y municipios son distribuciones independientes y no deben sumarse para obtener el total de pacientes.")

    # First row: monthly line and service donut
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("### Evolución de bajas por año/mes")
        if monthly.empty:
            st.info("Sin datos para los filtros seleccionados.")
        else:
            monthly["periodo"] = pd.to_datetime(monthly["anio"].astype(int).astype(str) + "-" + monthly["mes"].astype(int).astype(str).str.zfill(2) + "-01")
            monthly = monthly.sort_values("periodo")
            fig = px.line(monthly, x="periodo", y="pacientes_unicos", markers=True, labels={"periodo":"Mes","pacientes_unicos":"Pacientes únicos"}, color_discrete_sequence=[PURPLE])
            fig.update_traces(line=dict(width=3), marker=dict(size=5))
            fig.update_layout(height=270, margin=dict(l=8,r=8,t=8,b=8), template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=INK), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("### Distribución por servicio")
        d = service.groupby("servicio", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False).head(6)
        if d.empty:
            st.info("Sin datos para los filtros seleccionados.")
        else:
            fig = px.pie(d, names="servicio", values="pacientes_unicos", hole=.58, color_discrete_sequence=[NAVY,PURPLE,PURPLE2,TEAL,CORAL,GOLD])
            fig.update_layout(height=270, margin=dict(l=8,r=8,t=8,b=8), template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=INK), legend=dict(font=dict(size=9)))
            fig.add_annotation(text=f"{patients:,}<br><sup>pacientes</sup>", x=.5, y=.5, showarrow=False, font=dict(size=16,color=NAVY))
            st.plotly_chart(fig, use_container_width=True)

    # Second row: municipality bar and status distribution
    c3, c4 = st.columns([1.05, 1])
    with c3:
        st.markdown("### Bajas por municipio")
        d = municipality.groupby("municipio", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False).head(8)
        if selected_municipality != "Todos": d = d[d["municipio"].astype(str) == selected_municipality]
        if d.empty:
            st.info("Sin datos para los filtros seleccionados.")
        else:
            fig = px.bar(d.sort_values("pacientes_unicos"), x="pacientes_unicos", y="municipio", orientation="h", labels={"pacientes_unicos":"Pacientes únicos en el grupo","municipio":"Municipio"}, color_discrete_sequence=[PURPLE2])
            fig.update_layout(height=250, margin=dict(l=8,r=8,t=8,b=8), template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=INK), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.markdown("### Distribución de estados de servicio")
        d = status.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False)
        if selected_service != "Todos":
            d = ss.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False)
        if d.empty:
            st.info("Sin datos para los filtros seleccionados.")
        else:
            fig = px.bar(d, x="estatus_servicio", y="pacientes_unicos", labels={"pacientes_unicos":"Pacientes con registro","estatus_servicio":"Estado"}, color="estatus_servicio", color_discrete_sequence=[PURPLE,NAVY,TEAL,CORAL,GOLD])
            fig.update_layout(height=250, margin=dict(l=8,r=8,t=8,b=8), template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=INK), showlegend=False, xaxis_tickangle=-15)
            st.plotly_chart(fig, use_container_width=True)

    c5, c6 = st.columns([1,1])
    with c5:
        st.markdown("### Distribución por clínica")
        d = clinic.groupby("clinica", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False).head(8)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            fig = px.bar(d.sort_values("pacientes_unicos"), x="pacientes_unicos", y="clinica", orientation="h", labels={"pacientes_unicos":"Pacientes únicos en el grupo","clinica":"Clínica"}, color_discrete_sequence=[TEAL])
            fig.update_layout(height=240, margin=dict(l=8,r=8,t=8,b=8), template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=INK), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    with c6:
        st.markdown("### Servicios con más registros")
        d = service.groupby("servicio", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False).head(8)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            d = d.rename(columns={"servicio":"Servicio", "pacientes_unicos":"Pacientes únicos en el grupo"})
            st.dataframe(d, use_container_width=True, hide_index=True, height=240)

elif page == "Indicadores":
    st.markdown("<div class='section-kicker'>◉ &nbsp; Indicadores de seguimiento</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    items = [("Pacientes con baja administrativa",patients),("Meses con datos",months),("Servicios representados",n_services),("Municipios representados",n_munis),("Clínicas representadas",n_clinics),("Registros de inasistencia",status_count("INASISTENCIA")),("Registros TOMADA",status_count("TOMADA")),("Registros CANCELADA",status_count("CANCELADA")),("Registros POSPUESTA",status_count("POSPUESTA"))]
    for i,(label,val) in enumerate(items):
        with cols[i%3]: st.metric(label, f"{val:,}")
    st.warning("Estos indicadores describen registros de bajas administrativas y estados de servicio. No constituyen una tasa confirmada de abandono terapéutico.")

elif page == "Tendencias":
    st.markdown("<div class='section-kicker'>◷ &nbsp; Tendencias en el tiempo</div>", unsafe_allow_html=True)
    if monthly.empty: st.info("Sin datos para mostrar.")
    else:
        monthly["periodo"] = pd.to_datetime(monthly["anio"].astype(int).astype(str)+"-"+monthly["mes"].astype(int).astype(str).str.zfill(2)+"-01")
        fig = px.line(monthly.sort_values("periodo"), x="periodo", y="pacientes_unicos", color=monthly["anio"].astype(str), markers=True, labels={"periodo":"Mes de baja","pacientes_unicos":"Pacientes únicos","color":"Año"}, color_discrete_sequence=[NAVY,PURPLE,PURPLE2,TEAL,CORAL])
        fig.update_layout(height=430, template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=INK))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("El año 2026 es parcial y debe interpretarse con cautela frente a años completos.")

elif page == "Distribuciones":
    st.markdown("<div class='section-kicker'>▥ &nbsp; Distribuciones por dimensión</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Por servicio")
        d = service.groupby("servicio",as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos",ascending=False).head(15)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            fig=px.bar(d.sort_values("pacientes_unicos"),x="pacientes_unicos",y="servicio",orientation="h",labels={"pacientes_unicos":"Pacientes únicos en el grupo","servicio":"Servicio"},color_discrete_sequence=[PURPLE])
            fig.update_layout(height=470,template="plotly_white",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=INK))
            st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown("### Por municipio")
        d=municipality.groupby("municipio",as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos",ascending=False)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            fig=px.bar(d,x="municipio",y="pacientes_unicos",labels={"pacientes_unicos":"Pacientes únicos en el grupo","municipio":"Municipio"},color_discrete_sequence=[TEAL])
            fig.update_layout(height=470,template="plotly_white",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=INK),xaxis_tickangle=-30)
            st.plotly_chart(fig,use_container_width=True)
    c3,c4=st.columns(2)
    with c3:
        st.markdown("### Por clínica")
        d=clinic.groupby("clinica",as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos",ascending=False)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            fig=px.bar(d,x="clinica",y="pacientes_unicos",labels={"pacientes_unicos":"Pacientes únicos en el grupo","clinica":"Clínica"},color_discrete_sequence=[PURPLE2])
            fig.update_layout(height=350,template="plotly_white",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color=INK),xaxis_tickangle=-30)
            st.plotly_chart(fig,use_container_width=True)
    with c4:
        st.markdown("### Por estado de servicio")
        d=status.groupby("estatus_servicio",as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos",ascending=False)
        if d.empty: st.info("Sin datos para mostrar.")
        else:
            fig=px.pie(d,names="estatus_servicio",values="pacientes_unicos",hole=.48,color_discrete_sequence=[NAVY,PURPLE,TEAL,CORAL,GOLD])
            fig.update_layout(height=350,template="plotly_white",paper_bgcolor="rgba(0,0,0,0)",font=dict(color=INK))
            st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown("<div class='section-kicker'>♡ &nbsp; Metodología y uso responsable</div>", unsafe_allow_html=True)
    st.markdown("### Alcance de los datos")
    st.write("La versión pública utiliza tablas agregadas. No publica nombres, carnets ni registros individuales de pacientes.")
    st.markdown("### Criterios de interpretación")
    st.markdown("- **Baja administrativa no equivale necesariamente a abandono terapéutico.** Para estimar una tasa de abandono se requiere una definición institucional validada y un denominador apropiado.\n- **No aditividad:** un paciente puede aparecer en más de un servicio o estado; las categorías no deben sumarse para obtener un total general.\n- **Privacidad:** las tablas combinadas se prepararon con supresión de grupos pequeños; aun así, la publicación requiere autorización institucional.\n- **Periodo parcial:** los datos de 2026 no representan necesariamente un año completo.\n- **Validación pendiente:** confirmar con el CRIT el significado operativo de las fechas y estados de servicio.")
    st.markdown("### Decisiones que puede apoyar")
    st.write("Explorar patrones temporales y diferencias agregadas entre servicios, municipios, clínicas y estados de servicio para orientar preguntas de seguimiento. No sustituye la revisión institucional ni el expediente clínico.")

st.markdown("<div class='footer-note'>Fuente: base institucional de bajas, procesada para presentación agregada · Prototipo académico de apoyo a la toma de decisiones · No es una herramienta diagnóstica.</div>", unsafe_allow_html=True)

