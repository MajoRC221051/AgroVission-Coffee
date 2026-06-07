import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium

from datetime import datetime, timedelta

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from io import BytesIO

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="AgroVision Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"]{
    font-family:'DM Sans',sans-serif;
}

.stApp{
    background:linear-gradient(
        135deg,
        #1b1208 0%,
        #24180b 40%,
        #1f2d12 100%
    );
}

.hero-title{
    font-family:'Playfair Display',serif;
    font-size:3rem;
    font-weight:700;
    background:linear-gradient(
        135deg,
        #d4a843,
        #8ab85a
    );
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.hero-sub{
    color:#cbb58a;
    letter-spacing:2px;
}

.metric-card{
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(212,168,67,0.2);
    border-radius:15px;
    padding:20px;
    text-align:center;
}

.metric-value{
    font-size:2rem;
    color:#d4a843;
    font-weight:bold;
}

.metric-label{
    color:#bca77c;
}

.section-title{
    color:#d4a843;
    font-size:1.4rem;
    font-weight:600;
    margin-top:20px;
}

.info-box{
    background:rgba(138,184,90,0.1);
    border:1px solid rgba(138,184,90,0.3);
    padding:15px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CONSTANTS
# =====================================================

ALTA_VERAPAZ_LAT = 15.47
ALTA_VERAPAZ_LON = -90.37

COFFEE_OPTIMAL = {
    "temp_min":18,
    "temp_max":24,
    "soil_min":0.25,
    "soil_max":0.65
}

# =====================================================
# DATA
# =====================================================

@st.cache_data(ttl=3600)
def fetch_climate_data(days=90):

    end_date = datetime.now() - timedelta(days=180)
    start_date = end_date - timedelta(days=days)

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude":ALTA_VERAPAZ_LAT,
        "longitude":ALTA_VERAPAZ_LON,
        "start_date":start_date.strftime("%Y-%m-%d"),
        "end_date":end_date.strftime("%Y-%m-%d"),
        "daily":[
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "et0_fao_evapotranspiration"
        ],
        "timezone":"America/Guatemala"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame({
            "date":pd.to_datetime(data["daily"]["time"]),
            "temp_max":data["daily"]["temperature_2m_max"],
            "temp_min":data["daily"]["temperature_2m_min"],
            "temp_mean":data["daily"]["temperature_2m_mean"],
            "precip":data["daily"]["precipitation_sum"],
            "et0":data["daily"]["et0_fao_evapotranspiration"]
        })

        balance = (df["precip"] - df["et0"]).cumsum()

        balance = (
            balance - balance.min()
        ) / (
            balance.max() - balance.min() + 1e-6
        )

        df["soil_moisture"] = (
            0.25 + balance * 0.40
        )

        return df, True

    except Exception as e:

        dates = pd.date_range(
            end=datetime.now(),
            periods=days
        )

        np.random.seed(42)

        df = pd.DataFrame({
            "date":dates,
            "temp_max":np.random.normal(26,2,days),
            "temp_min":np.random.normal(16,2,days),
            "temp_mean":np.random.normal(21,1.5,days),
            "precip":np.random.exponential(4,days),
            "et0":np.random.normal(3,0.5,days),
            "soil_moisture":np.random.uniform(
                0.30,
                0.60,
                days
            )
        })

        return df, False

# =====================================================
# HEADER
# =====================================================

st.markdown(
    '<div class="hero-title">☕ AgroVision Coffee</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-sub">Virtual Coffee Greenhouse powered by Copernicus</div>',
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("⚙️ Escenario Climático")

    temp_delta = st.slider(
        "Incremento temperatura °C",
        -2.0,
        5.0,
        0.0,
        0.1
    )

    precip_change = st.slider(
        "Cambio precipitación %",
        -80,
        50,
        0
    )

    horizon = st.selectbox(
        "Horizonte",
        [
            "2030",
            "2050",
            "2070"
        ]
    )

    st.divider()

    st.markdown("""
    ### 📍 Región

    Alta Verapaz

    Guatemala

    ☕ Coffea Arabica
    """)

# =====================================================
# LOAD DATA
# =====================================================

df, real_data = fetch_climate_data()

if real_data:
    st.success("Datos Copernicus/Open-Meteo cargados")
else:
    st.warning("Modo demostración usando datos simulados")

# =====================================================
# SIMULADOR CLIMÁTICO
# =====================================================

df_sim = df.copy()

precip_factor = 1 + precip_change / 100

df_sim["temp_mean_sim"] = (
    df["temp_mean"] + temp_delta
)

df_sim["temp_max_sim"] = (
    df["temp_max"] + temp_delta
)

df_sim["temp_min_sim"] = (
    df["temp_min"] + temp_delta
)

df_sim["precip_sim"] = (
    df["precip"] * precip_factor
).clip(lower=0)

df_sim["soil_sim"] = (
    df["soil_moisture"] *
    (0.5 + precip_factor * 0.5)
).clip(0.05,0.95)

# =====================================================
# STRESS TERMICO
# =====================================================

def thermal_stress(temp):

    if temp < 10:
        return 1

    if temp > 30:
        return 1

    if 18 <= temp <= 24:
        return 0

    if temp < 18:
        return (18-temp)/8

    return (temp-24)/6


df_sim["thermal_stress"] = (
    df_sim["temp_mean_sim"]
    .apply(thermal_stress)
)

# =====================================================
# STRESS HIDRICO
# =====================================================

def moisture_stress(sm):

    if sm < 0.25:
        return min(
            1,
            (0.25-sm)/0.25
        )

    if sm > 0.65:
        return min(
            1,
            (sm-0.65)/0.35
        )

    return 0


df_sim["water_stress"] = (
    df_sim["soil_sim"]
    .apply(moisture_stress)
)

# =====================================================
# SALUD CULTIVO
# =====================================================

df_sim["crop_health"] = (
    1 -
    (
        df_sim["thermal_stress"]*0.6 +
        df_sim["water_stress"]*0.4
    )
) * 100

df_sim["crop_health"] = (
    df_sim["crop_health"]
    .clip(0,100)
)

# =====================================================
# NDVI PROXY
# =====================================================

df_sim["ndvi"] = (
    0.3 +
    (
        df_sim["crop_health"]/100
    ) * 0.55
)

df_sim["ndvi"] = (
    df_sim["ndvi"]
    .clip(0.1,0.9)
)

# =====================================================
# PRODUCTIVIDAD
# =====================================================

avg_health = (
    df_sim["crop_health"]
    .mean()
)

productivity = (
    max(
        0,
        (avg_health-50)/50
    )
) * 100

# =====================================================
# RIESGOS
# =====================================================

df_sim["drought_risk"] = (
    df_sim["water_stress"] * 100
)

df_sim["heat_risk"] = (
    df_sim["thermal_stress"] * 100
)

avg_drought = (
    df_sim["drought_risk"]
    .mean()
)

avg_heat = (
    df_sim["heat_risk"]
    .mean()
)

# =====================================================
# KPI CARDS
# =====================================================

st.markdown(
    '<div class="section-title">🌿 Estado del Invernadero Virtual</div>',
    unsafe_allow_html=True
)

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            {avg_health:.0f}
        </div>
        <div class="metric-label">
            Salud del Cultivo
        </div>
    </div>
    """,unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            {productivity:.0f}%
        </div>
        <div class="metric-label">
            Productividad
        </div>
    </div>
    """,unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            {avg_drought:.0f}%
        </div>
        <div class="metric-label">
            Riesgo Sequía
        </div>
    </div>
    """,unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">
            {avg_heat:.0f}%
        </div>
        <div class="metric-label">
            Riesgo Calor
        </div>
    </div>
    """,unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🌿 Invernadero Virtual",
    "📈 Clima",
    "💧 Suelo",
    "🛰️ NDVI"
])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.markdown(
        '<div class="section-title">🌿 Salud del Cultivo</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_hrect(
        y0=70,
        y1=100,
        fillcolor="rgba(138,184,90,0.12)",
        line_width=0
    )

    fig.add_hrect(
        y0=0,
        y1=40,
        fillcolor="rgba(224,80,80,0.10)",
        line_width=0
    )

    fig.add_trace(
        go.Scatter(
            x=df_sim["date"],
            y=df_sim["crop_health"],
            mode="lines",
            fill="tozeroy",
            name="Salud cultivo",
            line=dict(
                width=3,
                color="#8AB85A"
            )
        )
    )

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        yaxis_title="Salud (%)",
        xaxis_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("### 📋 Interpretación")

    if avg_health >= 75:

        st.success("""
        El cultivo se encuentra en condiciones óptimas.
        La combinación de temperatura y humedad favorece
        el desarrollo del café.
        """)

    elif avg_health >= 50:

        st.warning("""
        Se detectan señales moderadas de estrés.
        Es recomendable monitorear disponibilidad hídrica.
        """)

    else:

        st.error("""
        Riesgo elevado para la productividad.
        Considere medidas de adaptación climática.
        """)

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.markdown(
        '<div class="section-title">🌡️ Temperatura</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["temp_mean"],
            name="Histórico",
            line=dict(
                dash="dot",
                color="#888888"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_sim["date"],
            y=df_sim["temp_mean_sim"],
            name="Escenario",
            line=dict(
                width=3,
                color="#D4A843"
            )
        )
    )

    fig.add_hrect(
        y0=18,
        y1=24,
        fillcolor="rgba(138,184,90,0.12)",
        line_width=0
    )

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown(
        '<div class="section-title">🌧️ Precipitación</div>',
        unsafe_allow_html=True
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x=df_sim["date"],
            y=df_sim["precip_sim"],
            marker_color="#4A90E2"
        )
    )

    fig2.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =====================================================
# TAB 3
# =====================================================

with tab3:

    st.markdown(
        '<div class="section-title">💧 Humedad del Suelo</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_hrect(
        y0=0.25,
        y1=0.65,
        fillcolor="rgba(138,184,90,0.12)",
        line_width=0
    )

    fig.add_trace(
        go.Scatter(
            x=df_sim["date"],
            y=df_sim["soil_sim"],
            fill="tozeroy",
            line=dict(
                width=3,
                color="#4A90E2"
            )
        )
    )

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    col1,col2 = st.columns(2)

    with col1:

        st.metric(
            "Promedio humedad",
            f"{df_sim['soil_sim'].mean():.2f}"
        )

    with col2:

        st.metric(
            "Máximo humedad",
            f"{df_sim['soil_sim'].max():.2f}"
        )

# =====================================================
# TAB 4
# =====================================================

with tab4:

    st.markdown(
        '<div class="section-title">🌿 Índice NDVI</div>',
        unsafe_allow_html=True
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_sim["date"],
            y=df_sim["ndvi"],
            fill="tozeroy",
            line=dict(
                width=3,
                color="#6FBF4A"
            )
        )
    )

    fig.add_hline(
        y=0.6,
        line_dash="dot"
    )

    fig.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.metric(
        "NDVI promedio",
        f"{df_sim['ndvi'].mean():.2f}"
    )

# =====================================================
# TAB MAPA
# =====================================================

with tab4:

    st.markdown(
        '<div class="section-title">🗺️ Mapa Climático</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Simulación espacial para plantaciones
    de café en Alta Verapaz.
    """)

    # ----------------------------------
    # GENERAR PUNTOS
    # ----------------------------------

    np.random.seed(42)

    n_points = 40

    latitudes = (
        ALTA_VERAPAZ_LAT +
        np.random.normal(
            0,
            0.25,
            n_points
        )
    )

    longitudes = (
        ALTA_VERAPAZ_LON +
        np.random.normal(
            0,
            0.25,
            n_points
        )
    )

    base_health = (
        np.random.uniform(
            50,
            95,
            n_points
        )
    )

    scenario_penalty = (
        temp_delta * 5 +
        max(0,-precip_change) * 0.2
    )

    health_values = (
        base_health -
        scenario_penalty
    ).clip(0,100)

    # ----------------------------------
    # MAPA
    # ----------------------------------

    m = folium.Map(

        location=[
            ALTA_VERAPAZ_LAT,
            ALTA_VERAPAZ_LON
        ],

        zoom_start=8,

        tiles="CartoDB dark_matter"
    )

    # ----------------------------------
    # CENTRO
    # ----------------------------------

    folium.Marker(

        location=[
            ALTA_VERAPAZ_LAT,
            ALTA_VERAPAZ_LON
        ],

        popup="Alta Verapaz",

        tooltip="Zona de estudio",

        icon=folium.Icon(
            color="green",
            icon="leaf"
        )

    ).add_to(m)

    # ----------------------------------
    # PUNTOS
    # ----------------------------------

    for lat, lon, health in zip(
        latitudes,
        longitudes,
        health_values
    ):

        if health >= 70:

            color = "green"

        elif health >= 40:

            color = "orange"

        else:

            color = "red"

        folium.CircleMarker(

            location=[lat, lon],

            radius=8,

            color=color,

            fill=True,

            fill_opacity=0.8,

            popup=f"""
            Salud cultivo:
            {health:.0f}%
            """

        ).add_to(m)

    st_folium(
        m,
        width=None,
        height=550
    )

st.markdown(
    '<div class="section-title">📊 Resumen Espacial</div>',
    unsafe_allow_html=True
)

c1,c2,c3 = st.columns(3)

with c1:

    st.metric(
        "Salud promedio",
        f"{health_values.mean():.0f}%"
    )

with c2:

    st.metric(
        "Mejor zona",
        f"{health_values.max():.0f}%"
    )

with c3:

    st.metric(
        "Zona crítica",
        f"{health_values.min():.0f}%"
    )

fig = px.histogram(

    x=health_values,

    nbins=10,

    title="Distribución de Salud del Cultivo"
)

fig.update_layout(

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    font=dict(color="white")
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# TAB RIESGOS
# =====================================================

with tab5:

    st.markdown(
        '<div class="section-title">🚨 Evaluación de Riesgos</div>',
        unsafe_allow_html=True
    )

    avg_drought = df_sim["drought_risk"].mean()
    avg_heat = df_sim["heat_risk"].mean()

    # -----------------------------------
    # GAUGE SEQUÍA
    # -----------------------------------

    col1, col2 = st.columns(2)

    with col1:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_drought,
            title={"text":"Riesgo de Sequía"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"orange"},
                "steps":[
                    {"range":[0,30],"color":"lightgreen"},
                    {"range":[30,60],"color":"gold"},
                    {"range":[60,100],"color":"red"}
                ]
            }
        ))

        fig.update_layout(
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------
    # GAUGE CALOR
    # -----------------------------------

    with col2:

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_heat,
            title={"text":"Estrés Térmico"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":"crimson"},
                "steps":[
                    {"range":[0,30],"color":"lightgreen"},
                    {"range":[30,60],"color":"gold"},
                    {"range":[60,100],"color":"red"}
                ]
            }
        ))

        fig.update_layout(
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------------
# RECOMENDACIONES
# -----------------------------------

st.markdown(
    '<div class="section-title">💡 Recomendaciones</div>',
    unsafe_allow_html=True
)

recommendations = []

if avg_heat > 50:

    recommendations.append(
        "Implementar árboles de sombra para reducir temperatura."
    )

if avg_drought > 50:

    recommendations.append(
        "Evaluar sistemas de riego suplementario."
    )

if productivity < 60:

    recommendations.append(
        "Considerar variedades más resistentes al clima."
    )

if avg_health < 50:

    recommendations.append(
        "Realizar monitoreo agronómico intensivo."
    )

if len(recommendations) == 0:

    recommendations.append(
        "Las condiciones actuales son favorables para el cultivo."
    )

for rec in recommendations:

    st.info(rec)

st.markdown("""
<div style="
background:rgba(255,255,255,0.03);
padding:20px;
border-radius:15px;
border:1px solid rgba(212,168,67,0.2);
">

<h2 style="
color:#D4A843;
margin-bottom:0px;
">
☕ AgroVision Coffee
</h2>

<p style="
color:#CBB58A;
">
Virtual Coffee Greenhouse powered by Copernicus
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

