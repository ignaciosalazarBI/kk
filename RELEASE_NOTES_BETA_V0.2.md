# Control Pyme Beta v0.2.0

## Objetivo
Congelar una versión estable de la Beta pública antes de aumentar el tráfico de validación.

## Runtime fijado
- Python 3.12
- Streamlit 1.62.0
- pandas 3.0.5
- Plotly 6.9.0
- requests 2.34.2

## QA obligatorio
El pipeline valida instalación, versiones exactas, compilación, ejecución real de la portada, ejecución de todos los módulos, ausencia de Streamlit Secrets en el repositorio y ausencia de referencias a la service-role key.

## Rollback
Después de aprobar y fusionar esta versión se crea una rama de release apuntando exactamente al commit aprobado de producción. Esa referencia no debe moverse y sirve como punto de rollback de Beta v0.2.0.
