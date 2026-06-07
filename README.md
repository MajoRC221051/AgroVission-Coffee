# ☕ AgroVision Coffee — Invernadero Virtual Predictivo

Prototipo de plataforma de simulación climática para cultivos de café en **Alta Verapaz, Guatemala**, usando datos de observación terrestre de **Copernicus ERA5**.

## 🛰️ Fuentes de Datos

| Fuente | Variable | Acceso |
|--------|----------|--------|
| Copernicus ERA5 (via Open-Meteo) | Temperatura, precipitación, ETo | Gratuito, sin API key |
| Open-Meteo Forecast API | Condiciones actuales, humedad suelo | Gratuito, sin API key |
| Parámetros agronómicos | Umbrales óptimos café Arabica | CGIAR / Bunn et al. 2015 |

> **Open-Meteo** sirve datos del reanálisis ERA5 de Copernicus/ECMWF de forma gratuita y sin necesidad de registro. 
> Para acceso directo a Sentinel Hub (imágenes satelitales), ver sección de expansión abajo.

## 🚀 Instalación y Ejecución

```bash
# 1. Clonar o descargar el proyecto
cd agrovision

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py
```

La app abrirá automáticamente en `http://localhost:8501`

## 🌿 Funcionalidades

- **📡 Datos en tiempo real**: temperatura, humedad, precipitación actual en Alta Verapaz
- **📈 Series históricas ERA5**: hasta 180 días de datos del reanálisis Copernicus
- **🌿 Invernadero virtual**: simulación de escenarios climáticos ajustando temperatura y precipitación
- **💧 Análisis de humedad del suelo**: estrés hídrico, riesgo de sequía e inundación
- **🗺️ Mapa de riesgo**: distribución espacial de salud del cultivo en la región
- **📊 NDVI proxy**: estimación del vigor vegetativo basado en condiciones climáticas

## ⚙️ Parámetros agronómicos del café Arabica

| Variable | Mínimo óptimo | Máximo óptimo | Crítico |
|----------|--------------|--------------|---------|
| Temperatura | 18°C | 24°C | <10°C / >30°C |
| Precipitación anual | 1,500 mm | 3,000 mm | — |
| Humedad del suelo | 0.25 m³/m³ | 0.65 m³/m³ | — |

## 🔮 Expansión con Sentinel Hub (opcional)

Para integrar imágenes reales de Sentinel-2 (NDVI real), añadir:

```python
# En fetch_sentinel_ndvi():
url = "https://services.sentinel-hub.com/api/v1/process"
headers = {"Authorization": f"Bearer {SENTINEL_HUB_TOKEN}"}
# Solicitar banda NDVI para bbox de Alta Verapaz
bbox = [ALTA_VERAPAZ_LON - 0.5, ALTA_VERAPAZ_LAT - 0.5,
        ALTA_VERAPAZ_LON + 0.5, ALTA_VERAPAZ_LAT + 0.5]
```

Registrar cuenta gratuita en: https://www.sentinel-hub.com/

## 📚 Referencias

- Bunn et al. (2015). A bitter cup: Climate change profile of global production of Arabica and Robusta coffee.
- Läderach et al. (2017). The impact of climate change on coffee production in Central America.
- Copernicus Climate Change Service (2024). ERA5 reanalysis data.
- Open-Meteo (2024). Free Weather API. https://open-meteo.com
