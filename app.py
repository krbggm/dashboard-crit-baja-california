import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CRIT BC | Visualización de bajas", page_icon="📊", layout="wide")

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
years = sorted(tables["anual"]["anio"].dropna().astype(int).unique().tolist())
if not years:
    st.error("No hay datos agregados disponibles.")
    st.stop()

st.title("Plataforma de visualización de datos para el control del abandono terapéutico")
st.caption("CRIT Baja California · Prototipo académico · Registros de pacientes con baja administrativa")
st.warning(
    "Alcance de interpretación: la base contiene registros con estatus administrativo BAJA. "
    "Esto no confirma por sí solo abandono terapéutico. Las cifras de servicios/estados pueden "
    "contar a una misma persona en más de una categoría."
)

with st.sidebar:
    st.header("Filtros")
    selected_years = st.multiselect("Año de baja", years, default=years)
    municipalities = sorted(tables["municipio"]["municipio"].dropna().astype(str).unique().tolist())
    selected_municipality = st.selectbox("Municipio (para distribuciones compatibles)", ["Todos"] + municipalities)
    services = sorted(tables["servicio"]["servicio"].dropna().astype(str).unique().tolist())
    selected_service = st.selectbox("Servicio (para distribuciones compatibles)", ["Todos"] + services)
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

st.info(
    "Los indicadores de pacientes por mes cuentan pacientes únicos dentro de cada mes. "
    "Los conteos por servicio, municipio, clínica y estado son distribuciones independientes; "
    "no deben sumarse entre categorías para obtener el total general."
)

st.subheader("Indicadores de seguimiento")
row1 = st.columns(5)
row1[0].metric("Pacientes únicos con baja administrativa", f"{total_patients:,}")
row1[1].metric("Meses con datos visibles", f"{months_count:,}")
row1[2].metric("Servicios representados", f"{services_count:,}")
row1[3].metric("Municipios representados", f"{municipalities_count:,}")
row1[4].metric("Clínicas representadas", f"{clinics_count:,}")
row2 = st.columns(4)
row2[0].metric("Pacientes con registro de inasistencia", f"{status_patients('INASISTENCIA'):,}")
row2[1].metric("Pacientes con registro TOMADA", f"{status_patients('TOMADA'):,}")
row2[2].metric("Pacientes con registro CANCELADA", f"{status_patients('CANCELADA'):,}")
row2[3].metric("Pacientes con registro POSPUESTA", f"{status_patients('POSPUESTA'):,}")

st.subheader("1. Evolución mensual de pacientes con baja administrativa")
if monthly.empty:
    st.info("No hay grupos que mostrar para la selección actual.")
else:
    monthly["periodo"] = pd.to_datetime(
        monthly["anio"].astype(int).astype(str) + "-" + monthly["mes"].astype(int).astype(str).str.zfill(2) + "-01"
    )
    fig = px.line(monthly.sort_values("periodo"), x="periodo", y="pacientes_unicos", markers=True,
                  labels={"periodo":"Mes de baja", "pacientes_unicos":"Pacientes únicos"})
    fig.update_layout(margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("2. Pacientes únicos por servicio")
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
                     labels={"pacientes_unicos":"Pacientes únicos en el grupo", "servicio":"Servicio"})
        fig.update_layout(margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("3. Pacientes únicos por municipio")
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
                     labels={"pacientes_unicos":"Pacientes únicos en el grupo", "municipio":"Municipio"})
        fig.update_layout(margin=dict(l=10,r=10,t=20,b=10), xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader("4. Estados de servicio registrados")
    d = status.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum()
    if selected_service != "Todos":
        d2 = ss[ss["servicio"].astype(str) == selected_service]
        d = d2.groupby("estatus_servicio", as_index=False)["pacientes_unicos"].sum()
    if d.empty:
        st.info("No hay grupos visibles para esta selección.")
    else:
        fig = px.bar(d.sort_values("pacientes_unicos", ascending=False), x="estatus_servicio", y="pacientes_unicos",
                     labels={"pacientes_unicos":"Pacientes con al menos un registro", "estatus_servicio":"Estado"})
        fig.update_layout(margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("5. Distribución por clínica")
    d = clinic.groupby("clinica", as_index=False)["pacientes_unicos"].sum().sort_values("pacientes_unicos", ascending=False)
    if d.empty:
        st.info("No hay grupos visibles para esta selección.")
    else:
        fig = px.bar(d, x="clinica", y="pacientes_unicos",
                     labels={"pacientes_unicos":"Pacientes únicos en el grupo", "clinica":"Clínica"})
        fig.update_layout(margin=dict(l=10,r=10,t=20,b=10), xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

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
