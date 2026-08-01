# Nutri Verificador

Aplicación Streamlit para verificar tablas nutricionales desde fotos, extraer texto con OCR y comparar sellos frontales esperados vs observados.

## Estructura

- `core/`: lógica de OCR, parsing, reglas y reportes.
- `ui/`: entrada principal de Streamlit.
- `tests/`: pruebas unitarias básicas.
- `.streamlit/`: configuración de Streamlit.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run ui/streamlit_app.py
```

## Despliegue

Repositorio listo para GitHub y compatible con Streamlit Community Cloud usando como archivo principal `ui/streamlit_app.py`.
