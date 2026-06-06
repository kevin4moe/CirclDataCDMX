# streamlit run graficas/cdmx_event_simulation.py

"""
CDMX Event Simulation - Streamlit Dashboard
Complete visualization system for mass event simulation with environmental impact analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="CDMX Event Simulation",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Event venues
ESTADIO_AZTECA = {
    "name": "Estadio Azteca",
    "lat": 19.3029,
    "lon": -99.1506,
    "capacity": 87000
}

AUTODROMO_HERMANOS_RODRIGUEZ = {
    "name": "Autódromo Hermanos Rodríguez",
    "lat": 19.4042,
    "lon": -99.0907,
    "capacity": 135000
}

# Zonas específicas para Estadio Azteca (Enfoque Sur)
ZONAS_AZTECA = {
    "coyoacan": {"name": "Coyoacán Centro", "lat": 19.3467, "lon": -99.1618, "type": "cultural", "capacity": 15000},
    "tlalpan": {"name": "Centro de Tlalpan", "lat": 19.2882, "lon": -99.1673, "type": "cultural", "capacity": 10000},
    "xochimilco": {"name": "Xochimilco", "lat": 19.2546, "lon": -99.1036, "type": "cultural", "capacity": 12000},
    "san_angel": {"name": "San Ángel", "lat": 19.3450, "lon": -99.1917, "type": "entertainment", "capacity": 8000},
    "aeropuerto": {"name": "Zona Aeropuerto", "lat": 19.4361, "lon": -99.0719, "type": "commercial", "capacity": 10000}

}

# Zonas específicas para Autódromo (Enfoque Centro/Oriente)
ZONAS_AUTODROMO = {
    "centro_historico": {"name": "Centro Histórico", "lat": 19.4326, "lon": -99.1332, "type": "cultural", "capacity": 20000},
    "zona_rosa": {"name": "Zona Rosa", "lat": 19.4284, "lon": -99.1677, "type": "entertainment", "capacity": 15000},
    "polanco": {"name": "Polanco", "lat": 19.4363, "lon": -99.1910, "type": "commercial", "capacity": 12000},
    "roma": {"name": "Roma Norte", "lat": 19.4196, "lon": -99.1625, "type": "entertainment", "capacity": 15000},
    "condesa": {"name": "Condesa", "lat": 19.4147, "lon": -99.1730, "type": "entertainment", "capacity": 18000}
}

# CDMX boundaries
CDMX_BOUNDS = {
    "north": 19.5926,
    "south": 19.0492,
    "east": -98.9560,
    "west": -99.3654
}

# Color schemes
SEVERITY_COLORS = {
    'high': '#d32f2f',
    'medium': '#f57c00',
    'low': '#388e3c'
}

ZONE_TYPE_COLORS = {
    'entertainment': '#9c27b0',
    'cultural': '#2196f3',
    'commercial': '#ff9800',
    'event': '#f44336'
}

# ============================================================================
# POPULATION GENERATOR
# ============================================================================

class PopulationGenerator:
    """Generate synthetic population for event simulation"""
    
    def __init__(self, target_zones: Dict, seed: int = 42):
        self.target_zones = target_zones
        np.random.seed(seed)
    
    def generate_attendees(self, n_attendees: int = 8300) -> pd.DataFrame:
        """Generate synthetic attendees with realistic distribution"""
        attendees = []
        
        for i in range(n_attendees):
            # Generate home location
            home_cluster = np.random.choice(
                ['north', 'center', 'south', 'east', 'west'], 
                p=[0.2, 0.3, 0.2, 0.15, 0.15]
            )
            
            if home_cluster == 'north':
                home_lat = np.random.normal(19.50, 0.05)
                home_lon = np.random.normal(-99.15, 0.05)
            elif home_cluster == 'center':
                home_lat = np.random.normal(19.43, 0.03)
                home_lon = np.random.normal(-99.13, 0.03)
            elif home_cluster == 'south':
                home_lat = np.random.normal(19.30, 0.05)
                home_lon = np.random.normal(-99.15, 0.05)
            elif home_cluster == 'east':
                home_lat = np.random.normal(19.40, 0.05)
                home_lon = np.random.normal(-99.00, 0.05)
            else:  # west
                home_lat = np.random.normal(19.40, 0.05)
                home_lon = np.random.normal(-99.25, 0.05)
            
            # Clip to CDMX bounds
            home_lat = np.clip(home_lat, CDMX_BOUNDS['south'], CDMX_BOUNDS['north'])
            home_lon = np.clip(home_lon, CDMX_BOUNDS['west'], CDMX_BOUNDS['east'])
            
            # Assign destination zone dynamically
            zone_weights = [z['capacity'] for z in self.target_zones.values()]
            zone_weights = np.array(zone_weights) / sum(zone_weights)
            destination_zone = np.random.choice(list(self.target_zones.keys()), p=zone_weights)
            
            # Transportation mode
            transport_mode = np.random.choice(
                ['metro', 'car', 'bus', 'rideshare', 'walk'],
                p=[0.35, 0.25, 0.20, 0.15, 0.05]
            )
            
            # Age group
            age_group = np.random.choice(
                ['18-25', '26-35', '36-45', '46-60', '60+'],
                p=[0.30, 0.35, 0.20, 0.10, 0.05]
            )
            
            attendees.append({
                'attendee_id': f'ATT_{i:05d}',
                'home_lat': home_lat,
                'home_lon': home_lon,
                'home_cluster': home_cluster,
                'destination_zone': destination_zone,
                'transport_mode': transport_mode,
                'age_group': age_group,
                'waste_factor': np.random.uniform(0.8, 1.2)
            })
        
        return pd.DataFrame(attendees)

# ============================================================================
# EVENT SIMULATOR
# ============================================================================

class EventSimulator:
    """Simulate event attendance and post-event behavior"""
    
    def __init__(self, attendees_df: pd.DataFrame, target_zones: Dict, event_location=None):
        self.attendees = attendees_df
        self.event_location = event_location if event_location else ESTADIO_AZTECA
        self.zones = target_zones
    
    def simulate_event_day(self) -> Dict:
        """Simulate the event day (Day 0)"""
        return {
            'day': 0,
            'timestamp': datetime.now().isoformat(),
            'location': self.event_location['name'],
            'attendees_present': len(self.attendees),
            'concentration': {
                'lat': self.event_location['lat'],
                'lon': self.event_location['lon'],
                'count': len(self.attendees)
            }
        }
    
    def simulate_post_event(self, days_after: int) -> Dict:
        """Simulate attendee distribution after event"""
        decay_factor = np.exp(-days_after / 3)
        zone_distribution = {}
        
        for zone_id, zone_info in self.zones.items():
            zone_attendees = self.attendees[
                self.attendees['destination_zone'] == zone_id
            ]
            active_count = int(len(zone_attendees) * decay_factor)
            
            if active_count > 0:
                zone_distribution[zone_id] = {
                    'name': zone_info['name'],
                    'lat': zone_info['lat'],
                    'lon': zone_info['lon'],
                    'type': zone_info['type'],
                    'attendees_count': active_count,
                    'density': active_count / zone_info['capacity']
                }
        
        return {
            'day': days_after,
            'timestamp': (datetime.now() + timedelta(days=days_after)).isoformat(),
            'total_active_attendees': sum(z['attendees_count'] for z in zone_distribution.values()),
            'zones': zone_distribution,
            'decay_factor': decay_factor
        }

# ============================================================================
# ENVIRONMENTAL IMPACT CALCULATOR
# ============================================================================

class EnvironmentalImpactCalculator:
    """Calculate waste generation and emissions"""
    
    WASTE_PER_PERSON_DAY = {
        'event_day': 0.8,
        'post_event_day1': 0.6,
        'post_event_day3': 0.4,
        'post_event_day7': 0.2
    }
    
    EMISSIONS_PER_KM = {
        'metro': 0.04,
        'car': 0.12,
        'bus': 0.08,
        'rideshare': 0.10,
        'walk': 0.0
    }
    
    def __init__(self, attendees_df: pd.DataFrame):
        self.attendees = attendees_df
    
    def calculate_waste(self, day: int, active_attendees: int) -> Dict:
        """Calculate waste generation"""
        if day == 0:
            waste_coefficient = self.WASTE_PER_PERSON_DAY['event_day']
        elif day == 1:
            waste_coefficient = self.WASTE_PER_PERSON_DAY['post_event_day1']
        elif day <= 3:
            waste_coefficient = self.WASTE_PER_PERSON_DAY['post_event_day3']
        else:
            waste_coefficient = self.WASTE_PER_PERSON_DAY['post_event_day7']
        
        total_waste = active_attendees * waste_coefficient
        
        return {
            'total_kg': round(total_waste, 2),
            'organic_kg': round(total_waste * 0.40, 2),
            'plastic_kg': round(total_waste * 0.30, 2),
            'paper_kg': round(total_waste * 0.15, 2),
            'glass_kg': round(total_waste * 0.08, 2),
            'metal_kg': round(total_waste * 0.05, 2),
            'other_kg': round(total_waste * 0.02, 2)
        }
    
    def calculate_emissions(self, zone_data: Dict) -> Dict:
        """Calculate emissions for zone distribution"""
        total_emissions = 0
        emissions_by_transport = {}
        
        for zone_id, zone_info in zone_data.get('zones', {}).items():
            zone_attendees = self.attendees[
                self.attendees['destination_zone'] == zone_id
            ]
            avg_distance = 15
            
            for transport_mode in ['metro', 'car', 'bus', 'rideshare', 'walk']:
                mode_count = len(zone_attendees[
                    zone_attendees['transport_mode'] == transport_mode
                ])
                mode_emissions = (mode_count * avg_distance * self.EMISSIONS_PER_KM[transport_mode])
                total_emissions += mode_emissions
                emissions_by_transport[transport_mode] = \
                    emissions_by_transport.get(transport_mode, 0) + mode_emissions
        
        return {
            'total_co2_kg': round(total_emissions, 2),
            'by_transport': {k: round(v, 2) for k, v in emissions_by_transport.items()},
            'cars_equivalent': round(total_emissions / 4600, 3)
        }
    
    def identify_critical_points(self, zone_data: Dict, waste_data: Dict) -> List[Dict]:
        """Identify critical pollution points"""
        critical_points = []
        
        for zone_id, zone_info in zone_data.get('zones', {}).items():
            zone_waste = waste_data['total_kg'] * (
                zone_info['attendees_count'] / zone_data['total_active_attendees']
            )
            density = zone_info['density']
            
            if density > 0.7 or zone_waste > 1000:
                severity = 'high'
            elif density > 0.5 or zone_waste > 500:
                severity = 'medium'
            else:
                severity = 'low'
            
            critical_points.append({
                'zone_id': zone_id,
                'zone_name': zone_info['name'],
                'lat': zone_info['lat'],
                'lon': zone_info['lon'],
                'severity': severity,
                'density': round(density, 2),
                'estimated_waste_kg': round(zone_waste, 2),
                'attendees_count': zone_info['attendees_count']
            })
        
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        critical_points.sort(key=lambda x: severity_order[x['severity']])
        
        return critical_points

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_cdmx_map(day_data: Dict, day: int, event_location: Optional[Dict] = None) -> go.Figure:
    """Create interactive map of CDMX with event data"""
    if event_location is None:
        event_location = ESTADIO_AZTECA
    fig = go.Figure()
    
    # Add CDMX boundary
    fig.add_trace(go.Scattermapbox(
        lat=[CDMX_BOUNDS['north'], CDMX_BOUNDS['north'], 
             CDMX_BOUNDS['south'], CDMX_BOUNDS['south'], CDMX_BOUNDS['north']],
        lon=[CDMX_BOUNDS['west'], CDMX_BOUNDS['east'], 
             CDMX_BOUNDS['east'], CDMX_BOUNDS['west'], CDMX_BOUNDS['west']],
        mode='lines',
        line=dict(width=2, color='gray'),
        name='CDMX Límites',
        showlegend=True
    ))
    
    if day == 0:
        # Event day - show Estadio Azteca and crowd simulation
        total_asistentes = day_data['distribution']['attendees_present']
        n_puntos = min(total_asistentes, 2000) # Límite para rendimiento
        
        # Generar distribución aleatoria alrededor del estadio seleccionado
        lats_multitud = np.random.normal(event_location['lat'], 0.003, n_puntos)
        lons_multitud = np.random.normal(event_location['lon'], 0.003, n_puntos)
        
        # 1. Capa de la multitud
        fig.add_trace(go.Scattermapbox(
            lat=lats_multitud,
            lon=lons_multitud,
            mode='markers',
            marker=dict(size=6, color='#d32f2f', opacity=0.4),
            name='Multitud Simulada',
            hoverinfo='none',
            showlegend=False
        ))
        
        # 2. Capa del Venue del Evento
        fig.add_trace(go.Scattermapbox(
            lat=[event_location['lat']],
            lon=[event_location['lon']],
            mode='markers+text',
            marker=dict(size=25, color='gold', symbol='star', opacity=1.0),
            text=[event_location['name']],
            textposition='top center',
            name='Evento Principal',
            hovertemplate='<b>%{text}</b><br>Asistentes Totales: ' +
             f"{total_asistentes:,}<extra></extra>"
        ))
    else:
        # Post-event - show zones
        zones = day_data['distribution']['zones']
        for zone_id, zone_info in zones.items():
            color = 'red' if zone_info['density'] > 0.7 else \
                   'orange' if zone_info['density'] > 0.5 else 'green'
            
            fig.add_trace(go.Scattermapbox(
                lat=[zone_info['lat']],
                lon=[zone_info['lon']],
                mode='markers+text',
                marker=dict(
                    size=15 + zone_info['attendees_count'] / 100,
                    color=color,
                    opacity=0.7
                ),
                text=[zone_info['name']],
                textposition='top center',
                name=zone_info['name'],
                hovertemplate=f"<b>{zone_info['name']}</b><br>" +
                             f"Asistentes: {zone_info['attendees_count']:,}<br>" +
                             f"Densidad: {zone_info['density']:.1%}<extra></extra>"
            ))
    
    # Add critical points
    if 'critical_points' in day_data:
        for cp in day_data['critical_points']:
            fig.add_trace(go.Scattermapbox(
                lat=[cp['lat']],
                lon=[cp['lon']],
                mode='markers',
                marker=dict(
                    size=12,
                    color=SEVERITY_COLORS[cp['severity']],
                    symbol='circle',
                    opacity=0.6
                ),
                name=f"⚠️ {cp['severity'].upper()}",
                hovertemplate=f"<b>⚠️ {cp['zone_name']}</b><br>" +
                             f"Severidad: {cp['severity'].upper()}<br>" +
                             f"Residuos: {cp['estimated_waste_kg']:.1f} kg<br>" +
                             f"Densidad: {cp['density']:.1%}<extra></extra>",
                showlegend=False
            ))
    
    # === LÓGICA DINÁMICA DE CÁMARA ===
    if day == 0:
        map_center = dict(lat=event_location['lat'], lon=event_location['lon'])
        map_zoom = 15.5
    else:
        map_center = dict(lat=19.4326, lon=-99.1332)
        map_zoom = 10.5
        
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=map_center,
            zoom=map_zoom
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        title=f"Mapa CDMX - Día {day}",
        showlegend=True
    )
    
    return fig
    

def create_waste_chart(temporal_data: Dict) -> go.Figure:
    """Create waste generation timeline chart"""
    days = []
    total_waste = []
    organic = []
    plastic = []
    paper = []
    
    for day in [0, 1, 3, 7]:
        day_key = f'day_{day}'
        waste = temporal_data[day_key]['waste']
        days.append(f"Día {day}")
        total_waste.append(waste['total_kg'])
        organic.append(waste['organic_kg'])
        plastic.append(waste['plastic_kg'])
        paper.append(waste['paper_kg'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(name='Orgánico', x=days, y=organic, marker_color='#8bc34a'))
    fig.add_trace(go.Bar(name='Plástico', x=days, y=plastic, marker_color='#ff9800'))
    fig.add_trace(go.Bar(name='Papel', x=days, y=paper, marker_color='#2196f3'))
    
    fig.update_layout(
        title='Generación de Residuos por Tipo',
        xaxis_title='Período',
        yaxis_title='Residuos (kg)',
        barmode='stack',
        height=400
    )
    
    return fig

def create_emissions_chart(temporal_data: Dict) -> go.Figure:
    """Create emissions timeline chart"""
    days = []
    emissions = []
    
    for day in [0, 1, 3, 7]:
        day_key = f'day_{day}'
        days.append(f"Día {day}")
        emissions.append(temporal_data[day_key]['emissions']['total_co2_kg'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=days,
        y=emissions,
        mode='lines+markers',
        line=dict(color='#d32f2f', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(211, 47, 47, 0.2)'
    ))
    
    fig.update_layout(
        title='Emisiones de CO2 en el Tiempo',
        xaxis_title='Período',
        yaxis_title='CO2 (kg)',
        height=400
    )
    
    return fig

def create_density_heatmap(temporal_data: Dict) -> go.Figure:
    """Create density heatmap across zones and time"""
    zones = []
    days = []
    densities = []
    
    for day in [0, 1, 3, 7]:
        day_key = f'day_{day}'
        if day > 0:
            for zone_id, zone_info in temporal_data[day_key]['distribution']['zones'].items():
                zones.append(zone_info['name'])
                days.append(f"Día {day}")
                densities.append(zone_info['density'])
    
    # Pivot data for heatmap
    df = pd.DataFrame({'Zona': zones, 'Día': days, 'Densidad': densities})
    pivot = df.pivot(index='Zona', columns='Día', values='Densidad')
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn_r',
        text=pivot.values,
        texttemplate='%{text:.1%}',
        textfont={"size": 10},
        colorbar=dict(title="Densidad")
    ))
    
    fig.update_layout(
        title='Mapa de Calor: Densidad por Zona y Tiempo',
        xaxis_title='Período',
        yaxis_title='Zona Estratégica',
        height=400
    )
    
    return fig

def create_critical_points_table(critical_points: List[Dict]) -> pd.DataFrame:
    """Create critical points summary table"""
    data = []
    for point in critical_points:
        data.append({
            'Zona': point['zone_name'],
            'Severidad': point['severity'],
            'Asistentes': point['attendees_count'],
            'Densidad': f"{point['density']:.1%}",
            'Residuos (kg)': point['estimated_waste_kg']
        })
    return pd.DataFrame(data)

def create_transport_pie(attendees_df: pd.DataFrame) -> go.Figure:
    """Create transportation mode distribution pie chart"""
    transport_counts = attendees_df['transport_mode'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=transport_counts.index,
        values=transport_counts.values,
        hole=0.3,
        marker=dict(colors=['#2196f3', '#f44336', '#ff9800', '#9c27b0', '#4caf50'])
    )])
    
    fig.update_layout(
        title='Distribución de Modos de Transporte',
        height=400
    )
    
    return fig

# ============================================================================
# MAIN STREAMLIT APP
# ============================================================================

def main():
    # Header
    st.title("🏟️ Simulación de Evento Masivo - Ciudad de México")
    st.markdown("### Análisis de Impacto Ambiental y Movilidad")
    st.markdown("---")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuración de Simulación")
    
    # Event venue selection
    venue_option = st.sidebar.selectbox(
        "Seleccionar Venue",
        ["Estadio Azteca (5000 personas)", "Autódromo Hermanos Rodríguez (7500 personas)"]
    )
    
    # Set attendees and venue based on selection
    if "Autódromo" in venue_option:
        n_attendees = 7500
        selected_venue = AUTODROMO_HERMANOS_RODRIGUEZ
        selected_zones = ZONAS_AUTODROMO
    else:
        n_attendees = 5000
        selected_venue = ESTADIO_AZTECA
        selected_zones = ZONAS_AZTECA
    
    st.sidebar.info(f"📍 Venue: {selected_venue['name']}\n👥 Asistentes: {n_attendees:,}")
    
    seed = st.sidebar.number_input(
        "Semilla Aleatoria",
        min_value=1,
        max_value=1000,
        value=42
    )
    
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        with st.spinner("Generando población sintética..."):
            # Generate population
            pop_gen = PopulationGenerator(target_zones=selected_zones, seed=seed)
            attendees = pop_gen.generate_attendees(n_attendees)
            
            # Initialize simulator with selected venue
            simulator = EventSimulator(attendees, target_zones=selected_zones, event_location=selected_venue)
            impact_calc = EnvironmentalImpactCalculator(attendees)
            
            # Run simulation for all days
            simulation_results = {}
            
            for day in [0, 1, 3, 7]:
                if day == 0:
                    distribution = simulator.simulate_event_day()
                    active_attendees = distribution['attendees_present']
                else:
                    distribution = simulator.simulate_post_event(day)
                    active_attendees = distribution['total_active_attendees']
                
                waste = impact_calc.calculate_waste(day, active_attendees)
                
                if day > 0:
                    emissions = impact_calc.calculate_emissions(distribution)
                    critical_points = impact_calc.identify_critical_points(distribution, waste)
                else:
                    emissions = {'total_co2_kg': 0, 'by_transport': {}, 'cars_equivalent': 0}
                    critical_points = [{
                        'zone_id': 'event_venue',
                        'zone_name': selected_venue['name'],
                        'lat': selected_venue['lat'],
                        'lon': selected_venue['lon'],
                        'severity': 'high',
                        'density': 1.0,
                        'estimated_waste_kg': waste['total_kg'],
                        'attendees_count': active_attendees
                    }]
                
                simulation_results[f'day_{day}'] = {
                    'distribution': distribution,
                    'waste': waste,
                    'emissions': emissions,
                    'critical_points': critical_points
                }
            
            # Store in session state
            st.session_state['simulation_results'] = simulation_results
            st.session_state['attendees'] = attendees
            st.session_state['n_attendees'] = n_attendees
            st.session_state['selected_venue'] = selected_venue
            
        st.sidebar.success("✅ Simulación completada!")
    
    # Display results if available
    if 'simulation_results' in st.session_state:
        results = st.session_state['simulation_results']
        attendees = st.session_state['attendees']
        n_attendees = st.session_state['n_attendees']
        selected_venue = st.session_state.get('selected_venue', ESTADIO_AZTECA)
        
        # Summary metrics
        st.header("📊 Métricas Generales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_waste = sum(results[day]['waste']['total_kg'] for day in results)
        total_emissions = sum(results[day]['emissions']['total_co2_kg'] for day in results)
        
        with col1:
            st.metric("Total Asistentes", f"{n_attendees:,}")
        with col2:
            st.metric("Residuos Totales", f"{total_waste:,.1f} kg")
        with col3:
            st.metric("Emisiones CO2", f"{total_emissions:,.1f} kg")
        with col4:
            critical_high = sum(1 for cp in results['day_1']['critical_points'] 
                              if cp['severity'] == 'high')
            st.metric("Zonas Críticas", critical_high)
        
        st.markdown("---")
        
        # Temporal visualization tabs
        st.header("🗓️ Visualización Temporal")
        
        tab0, tab1, tab3, tab7 = st.tabs(["📅 Día del Evento", "📅 Día +1", "📅 Día +3", "📅 Día +7"])
        
        for tab, day in zip([tab0, tab1, tab3, tab7], [0, 1, 3, 7]):
            with tab:
                day_key = f'day_{day}'
                day_data = results[day_key]
                
                # Map
                st.subheader(f"Mapa de Distribución - Día {day}")
                fig_map = create_cdmx_map(day_data, day, event_location=selected_venue)
                st.plotly_chart(fig_map, use_container_width=True)
                
                # Metrics for this day
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if day == 0:
                        st.metric("Asistentes Presentes", 
                                f"{day_data['distribution']['attendees_present']:,}")
                    else:
                        st.metric("Asistentes Activos", 
                                f"{day_data['distribution']['total_active_attendees']:,}")
                
                with col2:
                    st.metric("Residuos Generados", 
                            f"{day_data['waste']['total_kg']:,.1f} kg")
                
                with col3:
                    st.metric("Emisiones CO2", 
                            f"{day_data['emissions']['total_co2_kg']:,.1f} kg")
                
                # Critical points table
                st.subheader("⚠️ Puntos Críticos")
                critical_df = create_critical_points_table(day_data['critical_points'])
                
                # Color code severity
                def highlight_severity(row):
                    if row['Severidad'] == 'high':
                        return ['background-color: #ffcdd2'] * len(row)
                    elif row['Severidad'] == 'medium':
                        return ['background-color: #ffe0b2'] * len(row)
                    else:
                        return ['background-color: #c8e6c9'] * len(row)
                
                st.dataframe(
                    critical_df.style.apply(highlight_severity, axis=1),
                    use_container_width=True,
                    hide_index=True
                )
        
        st.markdown("---")
        
        # Comparative analysis
        st.header("📈 Análisis Comparativo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_waste_chart(results), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_emissions_chart(results), use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.plotly_chart(create_transport_pie(attendees), use_container_width=True)
        
        with col4:
            st.plotly_chart(create_density_heatmap(results), use_container_width=True)
        
        st.markdown("---")
        
        # Download results
        st.header("💾 Exportar Resultados")
        
        # Exportar a CSV (Los asistentes)
        csv_data = attendees.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos de Asistentes (CSV)",
            data=csv_data,
            file_name=f"asistentes_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Prepare JSON export
        export_data = {
            'metadata': {
                'n_attendees': n_attendees,
                'simulation_date': datetime.now().isoformat(),
                'seed': seed
            },
            'results': {k: {
                'waste': v['waste'],
                'emissions': v['emissions'],
                'critical_points': v['critical_points']
            } for k, v in results.items()}
        }
        
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Descargar Resultados Ambientales (JSON)",
            data=json_str,
            file_name=f"cdmx_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
    else:
        # Welcome message
        st.info("👈 Configura los parámetros en la barra lateral y presiona '🚀 Ejecutar Simulación' para comenzar.")
        
        # Show example information
        st.header("ℹ️ Acerca de esta Simulación")
        
        st.markdown("""
        Esta aplicación simula eventos masivos en la Ciudad de México y analiza:
        
        - 🏠 **Población Sintética**: Genera asistentes con ubicaciones realistas en CDMX
        - 🏟️ **Eventos Masivos**: Simula concentraciones en diferentes venues
          - **Estadio Azteca**: 5,000 personas
          - **Autódromo Hermanos Rodríguez**: 7,500 personas
        - 🚶 **Desplazamiento Post-Evento**: Modela el movimiento hacia zonas estratégicas dinámicas
        - ♻️ **Residuos**: Estima la generación de residuos por tipo
        - 🌍 **Emisiones**: Calcula emisiones de CO2 por modo de transporte
        - ⚠️ **Puntos Críticos**: Identifica zonas de alto impacto ambiental
        
        ### Períodos de Análisis:
        - **Día 0**: Día del evento
        - **Día +1**: Un día después
        - **Día +3**: Tres días después
        - **Día +7**: Una semana después
        """)

if __name__ == "__main__":
    main()

# Made with Bob - CDMX Event Simulation Dashboard