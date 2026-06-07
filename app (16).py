# app.py
# Cambio principal: eliminar soil_moisture_0_to_7cm del endpoint Archive
# y generar una estimación simple de humedad de suelo para evitar el error 400.

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

ALTA_VERAPAZ_LAT = 15.47
ALTA_VERAPAZ_LON = -90.37

@st.cache_data(ttl=3600)
def fetch_open_meteo_data(lat=ALTA_VERAPAZ_LAT, lon=ALTA_VERAPAZ_LON, days_back=90):

    era5_end = datetime.now() - timedelta(days=180)
    era5_start = era5_end - timedelta(days=days_back)

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": era5_start.strftime("%Y-%m-%d"),
        "end_date": era5_end.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "et0_fao_evapotranspiration"
        ],
        "timezone": "America/Guatemala"
    }

    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()

    data = r.json()

    df = pd.DataFrame({
        "date": pd.to_datetime(data["daily"]["time"]),
        "temp_max": data["daily"]["temperature_2m_max"],
        "temp_min": data["daily"]["temperature_2m_min"],
        "temp_mean": data["daily"]["temperature_2m_mean"],
        "precip": data["daily"]["precipitation_sum"],
        "et0": data["daily"]["et0_fao_evapotranspiration"]
    })

    water_balance = (df["precip"] - df["et0"]).cumsum()
    water_balance = (water_balance - water_balance.min()) / (
        water_balance.max() - water_balance.min() + 1e-6
    )

    df["soil_moisture"] = 0.25 + water_balance * 0.40

    return df

st.title("AgroVision Coffee")

try:
    df = fetch_open_meteo_data()

    st.success("Datos cargados correctamente desde Open-Meteo")
    st.dataframe(df.head())

    st.line_chart(
        df.set_index("date")[["temp_mean", "precip", "soil_moisture"]]
    )

except Exception as e:
    st.error(f"Error: {e}")
