import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import json
import time

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgroVision Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

    /* Base */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #1a1208 0%, #2d1f0e 40%, #1e2d0e 100%);
        color: #f0e8d0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0a04 0%, #1a1208 100%) !important;
        border-right: 1px solid #3d2b0f;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
        color: #c8b080 !important;
    }

    /* Header */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #d4a843 0%, #8ab85a 60%, #d4a843 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #8a7a5a;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 300;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(212, 168, 67, 0.2);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(8px);
    }
    .metric-card:hover {
        border-color: rgba(212, 168, 67, 0.5);
        background: rgba(255,255,255,0.07);
    }
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #d4a843;
        display: block;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #8a7a5a;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.3rem;
        display: block;
    }
    .metric-status {
        font-size: 0.85rem;
        margin-top: 0.4rem;
        display: block;
    }
    .status-ok { color: #8ab85a; }
    .status-warn { color: #f0c040; }
    .status-danger { color: #e05050; }

    /* Section headers */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        color: #d4a843;
        border-bottom: 1px solid rgba(212, 168, 67, 0.3);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Risk badge */
    .risk-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 500;
        letter-spacing: 0.05em;
    }
    .risk-low { background: rgba(138,184,90,0.2); color: #8ab85a; border: 1px solid #8ab85a; }
    .risk-medium { background: rgba(240,192,64,0.2); color: #f0c040; border: 1px solid #f0c040; }
    .risk-high { background: rgba(224,80,80,0.2); color: #e05050; border: 1px solid #e05050; }

    /* Info boxes */
    .info-box {
        background: rgba(138, 184, 90, 0.08);
        border: 1px solid rgba(138, 184, 90, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #c8d8a0;
    }
    .warning-box {
        background: rgba(240, 192, 64, 0.08);
        border: 1px solid rgba(240, 192, 64, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #e0d090;
    }
    .danger-box {
        background: rgba(224, 80, 80, 0.08);
        border: 1px solid rgba(224, 80, 80, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #e0a0a0;
    }

    /* Sliders and widgets */
    .stSlider > div > div > div > div {
        background: #d4a843 !important;
    }

    /* Plotly charts background */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }

    /* Data source tag */
    .data-source-tag {
        font-size: 0.72rem;
        color: #6a5a3a;
        text-align: right;
        font-style: italic;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 0.3rem;
        gap: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8a7a5a !important;
        border-radius: 8px;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(212, 168, 67, 0.15) !important;
        color: #d4a843 !important;
    }

    /* Divider */
    hr { border-color: rgba(212, 168, 67, 0.15); }

    /* Selectbox */
    .stSelectbox select {
        background: #1a1208;
        color: #f0e8d0;
    }
</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
# Alta Verapaz coordinates (Cobán region)
ALTA_VERAPAZ_LAT = 15.47
ALTA_VERAPAZ_LON = -90.37

# Coffee optimal parameters
COFFEE_OPTIMAL = {
    "temp_min": 18.0,   # °C
    "temp_max": 24.0,
    "temp_critical_high": 30.0,
    "temp_critical_low": 10.0,
    "precip_min_annual": 1500,  # mm/year
    "precip_max_annual": 3000,
    "soil_moisture_min": 0.25,
    "soil_moisture_max": 0.65,
}


# ─── DATA FETCHING FUNCTIONS ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_open_meteo_data(lat=ALTA_VERAPAZ_LAT, lon=ALTA_VERAPAZ_LON, days_back=90):
    """
    Fetch real historical climate data from Open-Meteo (ERA5 reanalysis).
    Open-Meteo is free, no key needed, and uses Copernicus ERA5 data.
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm",
        ],
        "timezone": "America/Guatemala",
        "models": "era5"
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        df = pd.DataFrame({
            "date": pd.to_datetime(data["daily"]["time"]),
            "temp_max": data["daily"]["temperature_2m_max"],
            "temp_min": data["daily"]["temperature_2m_min"],
            "temp_mean": data["daily"]["temperature_2m_mean"],
            "precip": data["daily"]["precipitation_sum"],
            "et0": data["daily"]["et0_fao_evapotranspiration"],
            "soil_moisture": data["daily"]["soil_moisture_0_to_7cm"],
        })
        df = df.dropna(subset=["temp_mean"])
        return df, True
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=3600)
def fetch_current_weather(lat=ALTA_VERAPAZ_LAT, lon=ALTA_VERAPAZ_LON):
    """Fetch current conditions from Open-Meteo forecast API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "soil_moisture_0_to_1cm",
            "cloud_cover",
        ],
        "timezone": "America/Guatemala"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["current"], True
    except Exception as e:
        return None, str(e)


def simulate_scenario(df_base, temp_delta, precip_factor, scenario_months=12):
    """
    Apply climate scenario modifications to historical data and
    calculate coffee crop health indicators.
    """
    if df_base is None:
        return None

    df = df_base.copy()

    # Apply scenario
    df["temp_mean_sim"] = df["temp_mean"] + temp_delta
    df["temp_max_sim"] = df["temp_max"] + temp_delta
    df["temp_min_sim"] = df["temp_min"] + temp_delta
    df["precip_sim"] = (df["precip"] * precip_factor).clip(lower=0)
    df["soil_moisture_sim"] = (df["soil_moisture"] * (0.5 + precip_factor * 0.5)).clip(0.01, 0.95)

    # ── Health indicators ──
    opt = COFFEE_OPTIMAL

    # Thermal stress (0=perfect, 1=critical)
    def thermal_stress(t):
        if t < opt["temp_critical_low"]:
            return min(1.0, (opt["temp_critical_low"] - t) / 8)
        elif t > opt["temp_critical_high"]:
            return min(1.0, (t - opt["temp_critical_high"]) / 8)
        elif opt["temp_min"] <= t <= opt["temp_max"]:
            return 0.0
        elif t < opt["temp_min"]:
            return (opt["temp_min"] - t) / (opt["temp_min"] - opt["temp_critical_low"])
        else:
            return (t - opt["temp_max"]) / (opt["temp_critical_high"] - opt["temp_max"])

    df["thermal_stress"] = df["temp_mean_sim"].apply(thermal_stress)

    # Soil moisture stress
    def moisture_stress(sm):
        if sm is None or np.isnan(sm):
            return 0.3
        if opt["soil_moisture_min"] <= sm <= opt["soil_moisture_max"]:
            return 0.0
        elif sm < opt["soil_moisture_min"]:
            return min(1.0, (opt["soil_moisture_min"] - sm) / opt["soil_moisture_min"])
        else:
            return min(1.0, (sm - opt["soil_moisture_max"]) / (1 - opt["soil_moisture_max"]))

    df["moisture_stress"] = df["soil_moisture_sim"].apply(moisture_stress)

    # Overall crop health (0=dead, 100=perfect)
    df["crop_health"] = (1 - (df["thermal_stress"] * 0.6 + df["moisture_stress"] * 0.4)) * 100
    df["crop_health"] = df["crop_health"].clip(0, 100)

    # NDVI proxy (vegetation index based on conditions)
    df["ndvi_proxy"] = 0.3 + (df["crop_health"] / 100) * 0.55
    df["ndvi_proxy"] = df["ndvi_proxy"].clip(0.1, 0.9)

    # Drought risk
    df["drought_risk"] = df["moisture_stress"].clip(0, 1)
    df["flood_risk"] = ((df["precip_sim"] > 50) * (df["precip_sim"] - 50) / 100).clip(0, 1)

    return df


def compute_summary_stats(df_sim, df_base):
    """Compute summary statistics for display."""
    if df_sim is None:
        return {}

    avg_health_sim = df_sim["crop_health"].mean()
    avg_health_base = (1 - (df_base["soil_moisture"].apply(
        lambda sm: min(1.0, abs(sm - 0.45) / 0.2) if not np.isnan(sm) else 0.3
    ) * 0.4)) * 100
    avg_health_base = avg_health_base.mean()

    productivity_sim = max(0, (avg_health_sim - 50) / 50) * 100 if avg_health_sim > 50 else 0
    productivity_base = max(0, (avg_health_base - 50) / 50) * 100 if avg_health_base > 50 else 0

    drought_days = (df_sim["drought_risk"] > 0.6).sum()
    heat_stress_days = (df_sim["thermal_stress"] > 0.5).sum()

    return {
        "avg_health": avg_health_sim,
        "avg_health_base": avg_health_base,
        "productivity": productivity_sim,
        "productivity_base": productivity_base,
        "drought_days": int(drought_days),
        "heat_stress_days": int(heat_stress_days),
        "avg_temp": df_sim["temp_mean_sim"].mean(),
        "avg_precip_monthly": df_sim["precip_sim"].sum() / (len(df_sim) / 30),
    }


def get_risk_level(health_score):
    if health_score >= 70:
        return "BAJO", "risk-low"
    elif health_score >= 45:
        return "MODERADO", "risk-medium"
    else:
        return "ALTO", "risk-high"


# ─── CHART HELPERS ───────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c8b080", family="DM Sans"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified",
)


# ─── MAIN APP ────────────────────────────────────────────────────────────────────
def main():
    # ── HEADER ──────────────────────────────────────────────────────────────────
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.markdown("<div style='font-size:3.5rem; text-align:center; margin-top:0.3rem'>☕</div>", unsafe_allow_html=True)
    with col_title:
        st.markdown('<div class="hero-title">AgroVision Coffee</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Invernadero Virtual Predictivo · Alta Verapaz, Guatemala</div>', unsafe_allow_html=True)

    st.markdown('<div class="data-source-tag">Datos: Copernicus ERA5 via Open-Meteo · Coordenadas: 15.47°N, 90.37°W</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── SIDEBAR ─────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="section-header">⚙️ Parámetros del Escenario</div>', unsafe_allow_html=True)

        st.markdown("**🌡️ Temperatura**")
        temp_delta = st.slider(
            "Incremento de temperatura (°C)",
            min_value=-2.0, max_value=5.0, value=0.0, step=0.1,
            help="Modifica la temperatura media histórica de Alta Verapaz"
        )

        st.markdown("**🌧️ Precipitación**")
        precip_pct = st.slider(
            "Cambio en precipitación (%)",
            min_value=-80, max_value=50, value=0, step=5,
            help="Porcentaje de cambio respecto a la precipitación histórica"
        )
        precip_factor = 1 + precip_pct / 100

        st.markdown("**📅 Ventana de análisis**")
        days_back = st.selectbox(
            "Datos históricos a analizar",
            options=[30, 60, 90, 180],
            index=2,
            format_func=lambda x: f"Últimos {x} días"
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📍 Zona de Estudio</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.82rem; color:#8a7a5a; line-height:1.7'>
        🌿 <b style='color:#c8b080'>Región:</b> Alta Verapaz<br>
        🗺️ <b style='color:#c8b080'>Municipio ref.:</b> Cobán<br>
        📡 <b style='color:#c8b080'>Lat:</b> 15.47°N · <b style='color:#c8b080'>Lon:</b> 90.37°W<br>
        ⛰️ <b style='color:#c8b080'>Altitud aprox.:</b> 1,300 – 2,000 m<br>
        ☕ <b style='color:#c8b080'>Variedad:</b> Arabica (Coffea arabica)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.75rem; color:#5a4a2a; line-height:1.6'>
        🛰️ Fuente de datos:<br>
        • Copernicus ERA5 (ECMWF)<br>
        • Open-Meteo Archive API<br>
        • Parámetros agronómicos CGIAR
        </div>
        """, unsafe_allow_html=True)

    # ── FETCH DATA ───────────────────────────────────────────────────────────────
    with st.spinner("🛰️ Conectando a datos ERA5 de Copernicus..."):
        df_base, data_ok = fetch_open_meteo_data(days_back=days_back)
        current, curr_ok = fetch_current_weather()

    if data_ok is not True:
        st.error(f"⚠️ No se pudo conectar a la API de Open-Meteo: {data_ok}. Usando datos simulados.")
        # Fallback synthetic data
        dates = pd.date_range(end=datetime.now(), periods=days_back, freq='D')
        np.random.seed(42)
        df_base = pd.DataFrame({
            "date": dates,
            "temp_max": np.random.normal(26, 2, days_back),
            "temp_min": np.random.normal(16, 2, days_back),
            "temp_mean": np.random.normal(21, 1.5, days_back),
            "precip": np.random.exponential(4, days_back),
            "et0": np.random.normal(3, 0.5, days_back),
            "soil_moisture": np.random.beta(3, 4, days_back) * 0.5 + 0.2,
        })
        data_ok = True

    # ── SIMULATE SCENARIO ────────────────────────────────────────────────────────
    df_sim = simulate_scenario(df_base, temp_delta, precip_factor)
    stats = compute_summary_stats(df_sim, df_base)

    # ── CURRENT CONDITIONS ROW ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">📡 Condiciones Actuales — Alta Verapaz</div>', unsafe_allow_html=True)

    # Current reading from API or fallback from last row
    if curr_ok is True and current:
        curr_temp = current.get("temperature_2m", df_base["temp_mean"].iloc[-1])
        curr_hum = current.get("relative_humidity_2m", 75)
        curr_precip = current.get("precipitation", df_base["precip"].iloc[-1])
        curr_sm = current.get("soil_moisture_0_to_1cm", df_base["soil_moisture"].iloc[-1])
    else:
        curr_temp = df_base["temp_mean"].iloc[-1]
        curr_hum = 78
        curr_precip = df_base["precip"].iloc[-1]
        curr_sm = df_base["soil_moisture"].iloc[-1] if not np.isnan(df_base["soil_moisture"].iloc[-1]) else 0.38

    # Determine status strings
    def temp_status(t):
        if 18 <= t <= 24: return "✅ Óptima para café", "status-ok"
        elif 15 <= t < 18 or 24 < t <= 28: return "⚠️ Tolerable", "status-warn"
        else: return "🔴 Estrés térmico", "status-danger"

    def sm_status(sm):
        if 0.25 <= sm <= 0.65: return "✅ Humedad óptima", "status-ok"
        elif sm < 0.25: return "⚠️ Déficit hídrico", "status-warn"
        else: return "💧 Exceso de agua", "status-warn"

    ts, ts_class = temp_status(curr_temp)
    ss, ss_class = sm_status(curr_sm if curr_sm else 0.38)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, f"{curr_temp:.1f}°C", "Temperatura actual", ts, ts_class),
        (c2, f"{curr_hum:.0f}%", "Humedad relativa", "💧 Medición directa", "status-ok"),
        (c3, f"{curr_precip:.1f} mm", "Precipitación (hoy)", "🌧️ Acumulado", "status-ok"),
        (c4, f"{curr_sm:.2f}" if curr_sm else "N/D", "Humedad del suelo", ss, ss_class),
    ]
    for col, val, label, status, status_cls in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-value">{val}</span>
                <span class="metric-label">{label}</span>
                <span class="metric-status {status_cls}">{status}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌿 Invernadero Virtual",
        "📈 Análisis Climático",
        "💧 Humedad & Suelo",
        "🗺️ Mapa de Riesgo"
    ])

    # ═══ TAB 1: INVERNADERO VIRTUAL ════════════════════════════════════════════
    with tab1:
        # Scenario header
        scenario_label = ""
        if temp_delta == 0 and precip_pct == 0:
            scenario_label = "📊 Escenario Base (condiciones históricas actuales)"
            sc_box_class = "info-box"
        elif temp_delta <= 1 and precip_pct >= -20:
            scenario_label = f"🌤️ Escenario Moderado: +{temp_delta}°C · Precipitación {precip_pct:+d}%"
            sc_box_class = "warning-box"
        elif temp_delta <= 2.5:
            scenario_label = f"⚠️ Escenario Intermedio: +{temp_delta}°C · Precipitación {precip_pct:+d}%"
            sc_box_class = "warning-box"
        else:
            scenario_label = f"🔴 Escenario Crítico: +{temp_delta}°C · Precipitación {precip_pct:+d}%"
            sc_box_class = "danger-box"

        st.markdown(f'<div class="{sc_box_class}">🛰️ <b>{scenario_label}</b></div>', unsafe_allow_html=True)

        # Summary metrics for scenario
        risk_label, risk_class = get_risk_level(stats["avg_health"])
        health_delta = stats["avg_health"] - stats["avg_health_base"]
        prod_delta = stats["productivity"] - stats["productivity_base"]

        col_a, col_b, col_c, col_d = st.columns(4)
        sim_metrics = [
            (col_a, f"{stats['avg_health']:.0f}/100", "Salud del Cultivo",
             f"{'↑' if health_delta >= 0 else '↓'} {abs(health_delta):.0f} vs base",
             "status-ok" if health_delta >= 0 else "status-danger"),
            (col_b, f"{stats['productivity']:.0f}%", "Productividad Estimada",
             f"{'↑' if prod_delta >= 0 else '↓'} {abs(prod_delta):.0f}% vs base",
             "status-ok" if prod_delta >= 0 else "status-warn"),
            (col_c, str(stats["drought_days"]), "Días con Riesgo de Sequía",
             "🌵 En ventana analizada", "status-warn" if stats["drought_days"] > 10 else "status-ok"),
            (col_d, str(stats["heat_stress_days"]), "Días con Estrés Térmico",
             "🌡️ Días críticos", "status-danger" if stats["heat_stress_days"] > 15 else "status-ok"),
        ]
        for col, val, label, status, status_cls in sim_metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <span class="metric-value">{val}</span>
                    <span class="metric-label">{label}</span>
                    <span class="metric-status {status_cls}">{status}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='text-align:center; margin: 1.2rem 0 0.5rem;'>
            Nivel de riesgo global: <span class="risk-badge {risk_class}">● {risk_label}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Crop health timeline
        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem; margin-bottom:0.5rem">SALUD DEL CULTIVO EN EL TIEMPO</div>', unsafe_allow_html=True)
            fig = go.Figure()
            # Optimal zone
            fig.add_hrect(y0=70, y1=100, fillcolor="rgba(138,184,90,0.07)",
                          line_width=0, annotation_text="Zona óptima",
                          annotation_position="right", annotation_font_color="#8ab85a",
                          annotation_font_size=10)
            fig.add_hrect(y0=0, y1=45, fillcolor="rgba(224,80,80,0.06)", line_width=0)
            # Base line
            base_health = (1 - (df_base["soil_moisture"].apply(
                lambda sm: min(1.0, abs(sm - 0.45) / 0.2) if not np.isnan(sm) else 0.3
            ) * 0.4)) * 100
            fig.add_trace(go.Scatter(
                x=df_base["date"], y=base_health.clip(0, 100),
                mode="lines", name="Base histórico",
                line=dict(color="#6a5a3a", dash="dot", width=1.5),
                opacity=0.6
            ))
            # Simulated
            fig.add_trace(go.Scatter(
                x=df_sim["date"], y=df_sim["crop_health"],
                mode="lines", name="Escenario simulado",
                fill="tozeroy", fillcolor="rgba(138,184,90,0.12)",
                line=dict(color="#8ab85a", width=2.5)
            ))
            fig.update_layout(**CHART_LAYOUT, height=260,
                              yaxis_title="Índice de salud",
                              yaxis_range=[0, 105],
                              legend=dict(orientation="h", y=1.1, font_size=11))
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem; margin-bottom:0.5rem">NDVI PROXY (VIGOR VEGETATIVO)</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_sim["date"], y=df_sim["ndvi_proxy"],
                mode="lines", fill="tozeroy",
                fillcolor="rgba(100,160,60,0.15)",
                line=dict(color="#6ab040", width=2)
            ))
            # NDVI threshold lines
            fig2.add_hline(y=0.6, line_dash="dot", line_color="#8ab85a",
                           annotation_text="Saludable (>0.6)", annotation_font_color="#8ab85a",
                           annotation_font_size=9)
            fig2.add_hline(y=0.4, line_dash="dot", line_color="#f0c040",
                           annotation_text="Estrés (0.4)", annotation_font_color="#f0c040",
                           annotation_font_size=9)
            fig2.update_layout(**CHART_LAYOUT, height=260,
                               yaxis_title="NDVI", yaxis_range=[0, 1])
            st.plotly_chart(fig2, use_container_width=True)

        # ── Interpretation box
        health = stats["avg_health"]
        if health >= 70:
            st.markdown("""
            <div class="info-box">
            ✅ <b>El cultivo se encuentra en condiciones favorables.</b> Las condiciones simuladas son 
            compatibles con un buen desarrollo del café en Alta Verapaz. 
            Se recomienda monitoreo rutinario y mantener prácticas de gestión hídrica actuales.
            </div>""", unsafe_allow_html=True)
        elif health >= 45:
            st.markdown(f"""
            <div class="warning-box">
            ⚠️ <b>Condiciones de estrés moderado detectadas.</b> El escenario proyectado 
            ({stats['heat_stress_days']} días con estrés térmico, {stats['drought_days']} días con déficit hídrico) 
            puede afectar la productividad. Se sugiere evaluar sistemas de riego suplementario 
            y variedades más tolerantes al calor.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="danger-box">
            🔴 <b>Riesgo alto para el cultivo de café.</b> Las condiciones simuladas exceden 
            los límites tolerables. Con {stats['heat_stress_days']} días de estrés térmico severo y un 
            déficit hídrico pronunciado, la productividad podría caer drásticamente. 
            Se recomienda planificar estrategias de adaptación urgentes: sombra artificial, 
            riego eficiente, cambio de variedades o altitud.
            </div>""", unsafe_allow_html=True)

    # ═══ TAB 2: ANÁLISIS CLIMÁTICO ════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-header">📈 Variables Climáticas — ERA5 Copernicus</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">TEMPERATURA (°C)</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_base["date"], y=df_base["temp_max"],
                mode="lines", name="Máx. histórica",
                line=dict(color="#d4a843", width=1, dash="dot"), opacity=0.5
            ))
            fig.add_trace(go.Scatter(
                x=df_base["date"], y=df_base["temp_min"],
                mode="lines", name="Mín. histórica",
                line=dict(color="#6a8a3a", width=1, dash="dot"), opacity=0.5
            ))
            fig.add_trace(go.Scatter(
                x=df_sim["date"], y=df_sim["temp_mean_sim"],
                mode="lines", name="Media simulada",
                line=dict(color="#e07040", width=2.5)
            ))
            # Optimal range band
            fig.add_hrect(y0=18, y1=24, fillcolor="rgba(138,184,90,0.1)",
                          line_width=0, annotation_text="Rango óptimo café",
                          annotation_font_color="#8ab85a", annotation_font_size=9)
            fig.update_layout(**CHART_LAYOUT, height=280,
                              legend=dict(orientation="h", y=1.12, font_size=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">PRECIPITACIÓN DIARIA (mm)</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_base["date"], y=df_base["precip"],
                name="Histórica", marker_color="rgba(100,150,200,0.4)"
            ))
            fig.add_trace(go.Bar(
                x=df_sim["date"], y=df_sim["precip_sim"],
                name="Simulada", marker_color="rgba(70,130,230,0.7)"
            ))
            fig.update_layout(**CHART_LAYOUT, height=280, barmode="overlay",
                              legend=dict(orientation="h", y=1.12, font_size=10))
            st.plotly_chart(fig, use_container_width=True)

        # Monthly aggregates
        st.markdown('<div style="color:#8a7a5a; font-size:0.82rem; margin-top:0.5rem">RESUMEN MENSUAL</div>', unsafe_allow_html=True)
        df_monthly = df_sim.copy()
        df_monthly["month"] = df_monthly["date"].dt.to_period("M").astype(str)
        monthly = df_monthly.groupby("month").agg(
            temp_media=("temp_mean_sim", "mean"),
            precip_total=("precip_sim", "sum"),
            salud_media=("crop_health", "mean"),
            dias_sequía=("drought_risk", lambda x: (x > 0.6).sum())
        ).reset_index()

        fig = make_subplots(rows=1, cols=2, subplot_titles=["Temperatura Media Mensual (°C)", "Precipitación Mensual (mm)"])
        fig.add_trace(go.Bar(x=monthly["month"], y=monthly["temp_media"],
                             marker_color="#d4a843", name="Temp. media"), row=1, col=1)
        fig.add_hline(y=18, line_dash="dot", line_color="#8ab85a", row=1, col=1)
        fig.add_hline(y=24, line_dash="dot", line_color="#8ab85a", row=1, col=1)
        fig.add_trace(go.Bar(x=monthly["month"], y=monthly["precip_total"],
                             marker_color="#4080c0", name="Precip. total"), row=1, col=2)
        fig.update_layout(**CHART_LAYOUT, height=260, showlegend=False)
        fig.update_xaxes(tickfont=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="data-source-tag">
        Fuente: Copernicus ERA5 reanalysis via Open-Meteo Archive API | 
        Región: Alta Verapaz (15.47°N, 90.37°W) | Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
        </div>
        """, unsafe_allow_html=True)

    # ═══ TAB 3: HUMEDAD & SUELO ════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header">💧 Humedad del Suelo & Estrés Hídrico</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">ÍNDICE DE HUMEDAD DEL SUELO (SWI proxy)</div>', unsafe_allow_html=True)
            fig = go.Figure()
            # Optimal zone
            fig.add_hrect(y0=0.25, y1=0.65, fillcolor="rgba(100,180,100,0.1)",
                          line_width=0, annotation_text="Zona óptima café",
                          annotation_font_color="#8ab85a", annotation_font_size=9)
            valid_base = df_base.dropna(subset=["soil_moisture"])
            fig.add_trace(go.Scatter(
                x=valid_base["date"], y=valid_base["soil_moisture"],
                mode="lines", name="Histórico",
                line=dict(color="#6a8a5a", dash="dot", width=1.5), opacity=0.6
            ))
            valid_sim = df_sim.dropna(subset=["soil_moisture_sim"])
            fig.add_trace(go.Scatter(
                x=valid_sim["date"], y=valid_sim["soil_moisture_sim"],
                mode="lines", name="Simulado",
                fill="tozeroy", fillcolor="rgba(70,140,200,0.1)",
                line=dict(color="#5090d0", width=2.5)
            ))
            fig.update_layout(**CHART_LAYOUT, height=280,
                              yaxis_title="Fracción de humedad (m³/m³)",
                              legend=dict(orientation="h", y=1.12, font_size=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">ESTRÉS HÍDRICO Y TÉRMICO</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_sim["date"], y=df_sim["moisture_stress"] * 100,
                mode="lines", name="Estrés hídrico",
                fill="tozeroy", fillcolor="rgba(240,160,60,0.15)",
                line=dict(color="#f0a040", width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df_sim["date"], y=df_sim["thermal_stress"] * 100,
                mode="lines", name="Estrés térmico",
                fill="tozeroy", fillcolor="rgba(224,80,80,0.15)",
                line=dict(color="#e05050", width=2)
            ))
            fig.add_hline(y=50, line_dash="dash", line_color="rgba(255,255,255,0.2)",
                          annotation_text="Umbral crítico", annotation_font_size=9,
                          annotation_font_color="rgba(200,180,150,0.7)")
            fig.update_layout(**CHART_LAYOUT, height=280,
                              yaxis_title="Nivel de estrés (%)",
                              yaxis_range=[0, 105],
                              legend=dict(orientation="h", y=1.12, font_size=10))
            st.plotly_chart(fig, use_container_width=True)

        # Drought & flood risk timeline
        st.markdown('<div style="color:#8a7a5a; font-size:0.82rem; margin-top:0.5rem">RIESGO DE SEQUÍA E INUNDACIÓN</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_sim["date"], y=df_sim["drought_risk"] * 100,
            name="Riesgo sequía", marker_color="rgba(220,140,40,0.7)"
        ))
        fig.add_trace(go.Bar(
            x=df_sim["date"], y=df_sim["flood_risk"] * 100,
            name="Riesgo inundación", marker_color="rgba(60,120,200,0.7)"
        ))
        fig.add_hline(y=60, line_dash="dot", line_color="#e05050",
                      annotation_text="Umbral alerta", annotation_font_color="#e05050", annotation_font_size=9)
        fig.update_layout(**CHART_LAYOUT, height=230, barmode="group",
                          yaxis_title="Nivel de riesgo (%)",
                          legend=dict(orientation="h", y=1.12, font_size=10))
        st.plotly_chart(fig, use_container_width=True)

        # Water budget table
        st.markdown('<div style="color:#8a7a5a; font-size:0.82rem; margin-top:0.5rem">BALANCE HÍDRICO ESTIMADO</div>', unsafe_allow_html=True)
        df_wb = df_sim.copy()
        df_wb["month"] = df_wb["date"].dt.to_period("M").astype(str)
        wb = df_wb.groupby("month").agg(
            precip_mm=("precip_sim", "sum"),
            et0_mm=("et0", "sum"),
        ).reset_index()
        wb["balance_mm"] = wb["precip_mm"] - wb["et0_mm"]
        wb["estado"] = wb["balance_mm"].apply(
            lambda x: "✅ Superávit" if x > 20 else ("⚠️ Neutro" if x > -30 else "🔴 Déficit")
        )
        wb.columns = ["Mes", "Precipitación (mm)", "ETo (mm)", "Balance (mm)", "Estado"]
        st.dataframe(wb, use_container_width=True, hide_index=True)

    # ═══ TAB 4: MAPA DE RIESGO ═════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-header">🗺️ Visualización Espacial — Alta Verapaz</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        📡 El mapa muestra la localización del área de estudio en Alta Verapaz y simula 
        gradientes de riesgo climático para plantaciones de café en la región. 
        Los puntos representan zonas de monitoreo con datos ERA5 de Copernicus.
        </div>
        """, unsafe_allow_html=True)

        # Generate simulated spatial risk points around Alta Verapaz
        np.random.seed(12)
        n_pts = 40
        lats = ALTA_VERAPAZ_LAT + np.random.normal(0, 0.3, n_pts)
        lons = ALTA_VERAPAZ_LON + np.random.normal(0, 0.35, n_pts)
        base_risk = np.random.beta(2, 3, n_pts)

        # Apply scenario effect
        scenario_effect = (temp_delta / 5) * 0.5 + max(0, -precip_pct / 80) * 0.3
        risk_vals = (base_risk + scenario_effect).clip(0, 1)
        health_vals = (1 - risk_vals) * 100

        map_df = pd.DataFrame({
            "lat": lats, "lon": lons,
            "risk": risk_vals,
            "health": health_vals,
            "ndvi": 0.3 + (1 - risk_vals) * 0.5,
        })

        fig_map = go.Figure()
        # Risk scatter
        fig_map.add_trace(go.Scattermapbox(
            lat=map_df["lat"], lon=map_df["lon"],
            mode="markers",
            marker=dict(
                size=12,
                color=map_df["health"],
                colorscale=[[0, "#e05050"], [0.4, "#f0c040"], [0.7, "#8ab85a"], [1, "#2d7a1a"]],
                cmin=0, cmax=100,
                colorbar=dict(title="Salud<br>cultivo", titlefont=dict(color="#c8b080"),
                              tickfont=dict(color="#c8b080")),
                opacity=0.85
            ),
            text=[f"Salud: {h:.0f}% | NDVI: {n:.2f} | Riesgo: {r:.0%}"
                  for h, n, r in zip(map_df["health"], map_df["ndvi"], map_df["risk"])],
            hoverinfo="text",
            name="Puntos de monitoreo"
        ))
        # Main reference point
        fig_map.add_trace(go.Scattermapbox(
            lat=[ALTA_VERAPAZ_LAT], lon=[ALTA_VERAPAZ_LON],
            mode="markers+text",
            marker=dict(size=18, color="#d4a843", symbol="circle"),
            text=["☕ Cobán — Ref. ERA5"],
            textposition="top right",
            textfont=dict(color="#d4a843", size=12),
            hovertext="Alta Verapaz — Punto de referencia ERA5",
            name="Estación referencia"
        ))

        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=ALTA_VERAPAZ_LAT, lon=ALTA_VERAPAZ_LON),
                zoom=8
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c8b080"),
            height=480,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(font=dict(color="#c8b080"), bgcolor="rgba(0,0,0,0.4)")
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # Risk distribution
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">DISTRIBUCIÓN DE SALUD DEL CULTIVO (ZONA)</div>', unsafe_allow_html=True)
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=map_df["health"], nbinsx=10,
                marker_color="#8ab85a", opacity=0.75,
                name="Distribución"
            ))
            fig_hist.add_vline(x=70, line_dash="dot", line_color="#f0c040",
                               annotation_text="Umbral óptimo", annotation_font_color="#f0c040", annotation_font_size=9)
            fig_hist.update_layout(**CHART_LAYOUT, height=220,
                                   xaxis_title="Índice salud", yaxis_title="# zonas")
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_r2:
            st.markdown('<div style="color:#8a7a5a; font-size:0.82rem">NDVI PROXY — DISTRIBUCIÓN ESPACIAL</div>', unsafe_allow_html=True)
            fig_ndvi = go.Figure()
            fig_ndvi.add_trace(go.Violin(
                y=map_df["ndvi"], box_visible=True, meanline_visible=True,
                fillcolor="rgba(100,180,60,0.3)", line_color="#8ab85a",
                name="NDVI"
            ))
            fig_ndvi.add_hline(y=0.6, line_dash="dot", line_color="#d4a843",
                               annotation_text="Buena salud", annotation_font_color="#d4a843", annotation_font_size=9)
            fig_ndvi.update_layout(**CHART_LAYOUT, height=220, yaxis_title="NDVI", showlegend=False)
            st.plotly_chart(fig_ndvi, use_container_width=True)

    # ── FOOTER ──────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; color:#5a4a2a; font-size:0.78rem; padding: 0.5rem 0 1rem'>
    ☕ <b style='color:#8a7a5a'>AgroVision Coffee</b> · Prototipo v1.0 · 
    Datos: Copernicus ERA5 / Open-Meteo · 
    Parámetros agronómicos: CGIAR / Bunn et al. 2015 · Läderach et al. 2017<br>
    Región de estudio: Alta Verapaz, Guatemala · Desarrollado para demostración de observación terrestre
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
