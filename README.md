# Dashboard CRIT Baja California — prototipo académico

## Propósito
Prototipo para visualizar registros de pacientes con baja administrativa en el periodo disponible. El diseño se alinea con la tesis de visualización de datos para apoyar el control del abandono terapéutico, sin asumir que toda baja administrativa sea abandono confirmado.

## Archivos
- `app.py`: aplicación Streamlit.
- `data/publica/`: tablas agregadas para la versión pública. No contienen nombres ni carnets.
- `requirements.txt`: dependencias.
- `.gitignore`: excluye Excel y datos de trabajo identificables.

## Ejecutar localmente
1. Instalar Python 3.10 o posterior.
2. Abrir una terminal dentro de esta carpeta.
3. Crear entorno e instalar dependencias:
   `python -m venv .venv`
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
   `pip install -r requirements.txt`
4. Ejecutar:
   `streamlit run app.py`

## Privacidad
No copiar archivos originales ni la base limpia a `data/publica/` ni subirlos a GitHub. La carpeta `data/privada_local/` está excluida del repositorio. Los CSV de `data/publica/` contienen únicamente conteos agregados y omiten grupos con menos de 5 pacientes. Antes de una publicación institucional, solicitar autorización y revisión de privacidad.

## Reglas de interpretación
- Carnet se utiliza solo durante el cálculo local para contar pacientes únicos; nunca se exporta.
- Los pacientes pueden aparecer en más de un servicio o estado, por lo que las distribuciones no son aditivas.
- El año 2026 es parcial.
- “Baja administrativa” no equivale automáticamente a “abandono terapéutico”.
- La interpretación de `fecha_baja`, `fecha_ultima_cita` y de la unidad de cada fila debe validarse con la fuente institucional.

## Alineación con la etapa de tesis
- Capítulo III: documentar Design Thinking por fases, separando actividades realizadas de las pendientes.
- Capítulo IV: describir preparación de datos, estructura, KPI, visualizaciones e interactividad.
- Capítulo V: presentar hallazgos calculados, utilidad potencial y limitaciones; no formular conclusiones finales prematuras.

## Limitación actual
Este es un prototipo funcional inicial basado en agregados. No se considera una validación clínica ni un sistema oficial del CRIT. La publicación final requiere autorización institucional y revisión de las reglas de indicadores.
