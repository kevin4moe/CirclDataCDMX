"""
Módulo Independiente: Modelo Predictivo de Generación de Residuos
Basado en Regresión Lineal Múltiple con Estrategia de Valorización (Reciclaje)
"""

import base64
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


def load_brand_logo() -> str:
    """Return the project logo as a base64 data URL."""
    logo_path = Path(__file__).resolve().parent / "src" / "imports" / "CirclData_CDMX.png"
    if not logo_path.exists():
        return ""

    encoded_logo = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded_logo}"


def inject_prediction_styles() -> None:
    """Apply the same visual language used by the main dashboard."""
    st.markdown(
        """
        <style>
            :root {
                --bg: #f7faf9;
                --bg-soft: #edf5f1;
                --panel: rgba(255, 255, 255, 0.96);
                --panel-border: rgba(148, 163, 184, 0.14);
                --text: #243248;
                --muted: #64748b;
                --accent: #0ea36f;
                --accent-2: #3b82f6;
                --accent-3: #f59e0b;
                --danger: #ef4444;
                --radius-xl: 28px;
                --radius-lg: 22px;
                --shadow-lg: 0 14px 32px rgba(15, 23, 42, 0.08);
            }

            .stApp {
                background: linear-gradient(180deg, #f9fcfa 0%, #eef6f1 100%);
                color: var(--text);
                font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            [data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {
                visibility: hidden;
                height: 0;
            }

            section.main > div {
                padding-top: 0.8rem;
            }

            .block-container {
                max-width: 1260px;
                padding-top: 0.6rem;
                padding-bottom: 2.5rem;
            }

            [data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.98);
                border-right: 1px solid rgba(148, 163, 184, 0.12);
                box-shadow: 10px 0 24px rgba(15, 23, 42, 0.05);
            }

            [data-testid="stSidebar"] > div {
                padding-top: 1.4rem;
            }

            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span {
                color: var(--text) !important;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] > div,
            [data-testid="stSidebar"] div[data-baseweb="select"] [role="combobox"],
            [data-testid="stSidebar"] div[data-baseweb="input"] > div,
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea {
                background: rgba(255, 255, 255, 0.98) !important;
                color: #243248 !important;
                border-radius: 18px !important;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] > div,
            [data-testid="stSidebar"] div[data-baseweb="input"] > div {
                border: 1px solid rgba(203, 213, 225, 0.95) !important;
                box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] svg,
            [data-testid="stSidebar"] div[data-baseweb="input"] svg,
            [data-testid="stSidebar"] button svg {
                color: #64748b !important;
            }

            [data-testid="stSidebar"] div[data-baseweb="select"] [role="combobox"]:focus,
            [data-testid="stSidebar"] div[data-baseweb="input"]:focus-within,
            [data-testid="stSidebar"] input:focus,
            [data-testid="stSidebar"] textarea:focus {
                border-color: rgba(16, 163, 109, 0.55) !important;
                box-shadow: 0 0 0 4px rgba(16, 163, 109, 0.10) !important;
                outline: none !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                width: 100%;
            }

            .top-nav {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 0.8rem 1rem;
                margin-bottom: 1rem;
                border-radius: 24px;
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(226, 232, 240, 0.88);
                box-shadow: var(--shadow-lg);
                backdrop-filter: blur(14px);
            }

            .top-brand {
                display: flex;
                align-items: center;
                gap: 0.85rem;
            }

            .top-brand img {
                height: 2.5rem;
                width: auto;
            }

            .top-copy {
                display: flex;
                flex-direction: column;
                line-height: 1.15;
            }

            .top-copy strong {
                font-size: 0.95rem;
                color: var(--text);
            }

            .top-copy span {
                font-size: 0.74rem;
                color: var(--muted);
            }

            .hero-card {
                border: 1px solid rgba(226, 232, 240, 0.96);
                border-radius: var(--radius-xl);
                background: linear-gradient(180deg, rgba(247, 252, 249, 0.98), rgba(241, 248, 244, 0.98));
                box-shadow: var(--shadow-lg);
                padding: 1.7rem 1.4rem 1.5rem;
                margin-bottom: 1rem;
                position: relative;
                overflow: hidden;
                text-align: center;
            }

            .hero-card::after {
                content: '';
                position: absolute;
                inset: -2rem auto auto 50%;
                transform: translateX(-50%);
                width: 14rem;
                height: 14rem;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(16, 163, 109, 0.12), transparent 64%);
                filter: blur(5px);
                pointer-events: none;
            }

            .hero-kicker {
                letter-spacing: 0.14em;
                text-transform: uppercase;
                color: var(--accent);
                font-size: 0.69rem;
                font-weight: 700;
                margin-bottom: 0.8rem;
            }

            .hero-title {
                font-size: clamp(1.6rem, 3vw, 2.5rem);
                line-height: 1.06;
                font-weight: 700;
                color: #30455f;
                margin: 0;
            }

            .hero-subtitle {
                margin-top: 0.75rem;
                color: var(--muted);
                font-size: 0.96rem;
                max-width: 66ch;
                margin-left: auto;
                margin-right: auto;
            }

            .hero-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
                margin-top: 1.2rem;
                justify-content: center;
            }

            .hero-chip {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                border: 1px solid rgba(148, 163, 184, 0.14);
                background: rgba(255, 255, 255, 0.96);
                color: #475569;
                border-radius: 999px;
                padding: 0.45rem 0.8rem;
                font-size: 0.82rem;
                box-shadow: 0 8px 16px rgba(15, 23, 42, 0.05);
            }

            .section-label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #25344c;
                font-size: 1.18rem;
                font-weight: 700;
                margin: 0 0 0.35rem 0;
            }

            .section-label::before {
                content: '';
                width: 10px;
                height: 10px;
                border-radius: 999px;
                display: inline-block;
                background: linear-gradient(135deg, rgba(16, 163, 109, 0.96), rgba(50, 116, 255, 0.9));
                box-shadow: 0 0 0 5px rgba(16, 163, 109, 0.08);
            }

            .section-panel {
                margin-bottom: 0.85rem;
            }

            .section-subtitle {
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.5;
                margin-bottom: 0.55rem;
            }

            div[data-testid="metric-container"] {
                border: 1px solid rgba(226, 232, 240, 0.92);
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.97);
                padding: 0.95rem 0.95rem 0.75rem;
                box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
            }

            div[data-testid="metric-container"] label {
                color: var(--muted) !important;
                font-size: 0.8rem !important;
            }

            div[data-testid="metric-container"] [data-testid="stMetricValue"] {
                color: #25344c;
                font-size: 2rem;
                font-weight: 800;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 16px !important;
                border: 1px solid rgba(16, 163, 109, 0.22) !important;
                background: linear-gradient(135deg, #17c58c, #0fa56f) !important;
                color: white !important;
                font-weight: 700 !important;
                box-shadow: 0 14px 28px rgba(16, 163, 109, 0.16);
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                transform: translateY(-1px);
                border-color: rgba(16, 163, 109, 0.45) !important;
            }

            .stAlert {
                border-radius: 22px;
            }

            [data-testid="stAlert"] {
                border: 1px solid rgba(191, 219, 254, 0.85) !important;
                background: linear-gradient(180deg, rgba(239, 246, 255, 0.94), rgba(224, 242, 254, 0.94)) !important;
                color: #1e3a5f !important;
                border-radius: 22px !important;
                box-shadow: 0 10px 22px rgba(37, 99, 235, 0.07) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_section() -> None:
    """Render the dashboard hero and summary chips."""
    logo_data = load_brand_logo()
    logo_html = f'<img src="{logo_data}" alt="CirclData CDMX" />' if logo_data else "<div></div>"

    st.markdown(
        f"""
        <div class="top-nav">
            <div class="top-brand">
                {logo_html}
                <div class="top-copy">
                    <strong>CirclData CDMX</strong>
                    <span>Inteligencia para la Economía Circular</span>
                </div>
            </div>
        </div>
        <div class="hero-card">
            <div class="hero-kicker">Sistema Inteligente de Gestión de Residuos - Mundial 2026</div>
            <h1 class="hero-title">Predicción clara de residuos urbanos</h1>
            <div class="hero-subtitle">
                Modelo operativo para estimar generación bruta, recuperación y costo final con una lectura visual limpia.
            </div>
            <div class="hero-meta">
                <span class="hero-chip">♻️ Residuos + valorización</span>
                <span class="hero-chip">📍 CDMX 2026</span>
                <span class="hero-chip">📊 Escenario configurable</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(title: str, subtitle: str = "") -> None:
    """Render a styled section intro."""
    subtitle_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-panel">
            <div class="section-label">{title}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================================
# LÓGICA DEL MODELO PREDICTIVO (HÍBRIDO ESTADÍSTICO)
# ============================================================================
def calcular_tonelaje_predicho(aforo, flotante, duracion, indice_comercio, lluvia_mm, tipo_evento):
    """
    Simula un modelo lineal híbrido calibrado con parámetros del reporte.
    Ajusta dinámicamente el intercepto y los coeficientes según la agresividad del evento.
    """
    # 1. Ajuste de coeficientes según la naturaleza del evento
    if tipo_evento == "Festival Musical / Concierto":
        # Eventos con alto consumo, stands de comida y mercadotecnia libre
        beta_0 = 3500 
        base_coef_aforo = 0.80
        multiplicador_duracion = 0.60
    else: 
        # "Partido Deportivo (Fútbol)" - Entorno más controlado
        beta_0 = 1800
        base_coef_aforo = 0.30
        multiplicador_duracion = 0.40

    # 2. Cálculo de basura interna escalada por la duración
    factor_duracion_interno = min(duracion / 6, 1.0)
    coef_aforo = base_coef_aforo + (multiplicador_duracion * factor_duracion_interno)
    basura_interna = aforo * coef_aforo
    
    # 3. Variables exógenas (Periferia, comercio y clima)
    coef_flotante = 0.22
    basura_flotante = flotante * coef_flotante
    
    basura_comercio = indice_comercio * 120
    basura_pluvial = lluvia_mm * 180
    
    # 4. Sumatoria total
    total_kg = beta_0 + basura_interna + basura_flotante + basura_comercio + basura_pluvial
    toneladas_totales = total_kg / 1000
    
    return toneladas_totales, coef_aforo


# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================
def render_prediction_page():
    inject_prediction_styles()

    render_hero_section()
    render_section_label(
        "Variables de Generación",
        "Ajusta la asistencia, el flujo flotante y el contexto operativo del evento."
    )

    col1, col2 = st.columns([1, 1.2])

    with col1:
        # Selector Dinámico de Tipo de Evento
        tipo_evento = st.selectbox(
            "Categoría del Evento",
            ["Partido Deportivo (Fútbol)", "Festival Musical / Concierto"],
            help="Los festivales musicales tienen una tasa de generación de residuos per cápita mucho más agresiva que los eventos deportivos."
        )
        st.markdown("---")

        aforo = st.number_input(
            "Aforo oficial efectivo",
            min_value=0,
            max_value=150000,
            value=83000,
            step=1000,
        )

        flotante = st.number_input(
            "Población flotante / fan zones",
            min_value=0,
            max_value=200000,
            value=45000,
            step=1000,
        )

        duracion = st.slider(
            "Duración del evento y pre-concentración (horas)",
            min_value=2.0,
            max_value=12.0,
            value=6.0,
            step=0.5,
        )

        indice_comercio = st.slider(
            "Índice de comercio informal (1 - 100)",
            min_value=0,
            max_value=100,
            value=75,
        )

        lluvia_mm = st.slider(
            "Precipitación proyectada (mm)",
            min_value=0,
            max_value=50,
            value=15,
            help="El reporte destaca junio-julio como temporada crítica de lluvias en CDMX."
        )

        render_section_label(
            "Economía Circular",
            "La recuperación permite estimar cuánto volumen no termina en disposición final."
        )

        tasa_recuperacion = st.slider(
            "Porcentaje del total rescatado para reciclaje (%)",
            min_value=0,
            max_value=100,
            value=30,
            help="Del 100% de la basura generada, ¿cuánto lograremos separar antes de que llegue al camión de basura?"
        )

        # Constantes del mercado de reciclaje
        costo_mitigacion_tonelada = 4000.00
        precio_aluminio_ton = 22000.00
        precio_carton_ton = 1500.00
        precio_pet_ton = 5000.00

    with col2:
        # Ejecutar modelo enviando la variable tipo_evento
        toneladas, coef_real = calcular_tonelaje_predicho(aforo, flotante, duracion, indice_comercio, lluvia_mm, tipo_evento)
        
        toneladas_recuperadas = toneladas * (tasa_recuperacion / 100)
        toneladas_a_disposicion = toneladas - toneladas_recuperadas

        # Distribución de volumen recuperado: 20% Aluminio, 60% Cartón, 20% PET
        toneladas_aluminio = toneladas_recuperadas * 0.20
        toneladas_carton = toneladas_recuperadas * 0.60
        toneladas_pet = toneladas_recuperadas * 0.20

        ingreso_aluminio = toneladas_aluminio * precio_aluminio_ton
        ingreso_carton = toneladas_carton * precio_carton_ton
        ingreso_pet = toneladas_pet * precio_pet_ton
        ingresos_totales = ingreso_aluminio + ingreso_carton + ingreso_pet

        costo_sin_reciclar = toneladas * costo_mitigacion_tonelada
        costo_operativo_bruto = toneladas_a_disposicion * costo_mitigacion_tonelada
        balance_financiero_final = costo_operativo_bruto - ingresos_totales
        impuesto_pigouviano = (balance_financiero_final / aforo) if (aforo > 0 and balance_financiero_final > 0) else 0

        render_section_label(
            "Resultados de la Inferencia",
            "La salida prioriza cifras críticas y una lectura rápida del impacto económico y ambiental."
        )

        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Generación bruta", value=f"{toneladas:,.1f} Ton", delta="Volumen total")
        m2.metric(
            label="Desecho real a relleno",
            value=f"{toneladas_a_disposicion:,.1f} Ton",
            delta=f"-{toneladas_recuperadas:,.1f} Ton recuperadas",
            delta_color="normal",
        )
        m3.metric(
            label="Costo sin reciclar",
            value=f"${costo_sin_reciclar:,.2f}",
            delta=f"Coef. aforo: {coef_real:.2f} kg/persona",
            delta_color="inverse",
        )

        # Tarjeta HTML destacada para los Ingresos + Letras chiquitas
        st.markdown(f"""
        <div style="background-color: #f0fdf4; padding: 25px; border-radius: 12px; text-align: center; border: 2px solid #22c55e; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 1rem;">
            <h4 style="color: #166534; margin-bottom: 0px; font-weight: 600;">💰 Ingresos por Economía Circular</h4>
            <h1 style="color: #15803d; font-size: 3.5rem; margin-top: 10px; margin-bottom: 10px;">${ingresos_totales:,.2f} MXN</h1>
            <p style="color: #166534; font-size: 1.1rem; margin-bottom: 0px;">Valorización de Aluminio, Cartón y PET</p>
        </div>
        <p style="text-align: center; font-size: 0.85rem; color: #6b7280; margin-top: 8px;">
            <i>* Se reciclaron exitosamente un total de <b>{toneladas_recuperadas:,.1f} toneladas</b> de residuos sólidos.</i>
        </p>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**Desglose de materiales recuperados y proyección de ingresos:**")
        df_reciclaje = pd.DataFrame({
            "Material": ["Aluminio (Latas)", "Cartón/Papel", "PET (Botellas plásticas)", "Total Ingresos"],
            "Toneladas Capturadas": [toneladas_aluminio, toneladas_carton, toneladas_pet, toneladas_aluminio + toneladas_carton + toneladas_pet],
            "Ingreso Estimado (MXN)": [ingreso_aluminio, ingreso_carton, ingreso_pet, ingreso_aluminio + ingreso_carton + ingreso_pet],
        })

        st.dataframe(
            df_reciclaje.style.format({
                "Toneladas Capturadas": "{:,.2f}",
                "Ingreso Estimado (MXN)": "${:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )


def main():
    st.set_page_config(
        page_title="Predicción de Residuos - CDMX 2026",
        page_icon="♻️",
        layout="wide"
    )
    render_prediction_page()


if __name__ == "__main__":
    main()
