import streamlit as st

from prediccion_residuos import render_prediction_page

st.set_page_config(
    page_title="Prediccion de Residuos - CDMX 2026",
    page_icon="♻️",
    layout="wide",
)

render_prediction_page()
