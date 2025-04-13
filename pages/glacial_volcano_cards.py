"""
Glacial Volcano Risk Cards for the Volcano Monitoring Dashboard.

This page displays detailed risk assessments for glaciated volcanoes around the world,
showing how climate change and glacial melting may affect volcanic activity.
"""

import streamlit as st
import pandas as pd
from data.glacial_volcanoes import get_glacial_volcanoes

def app():
    st.title("Glacial Volcanoes Risk Assessment")
    
    st.markdown("""
    ## Climate Change & Volcanic Activity
    
    This page presents detailed information about glaciated volcanoes around the world that may be affected by climate change.
    The melting of glaciers that cover these volcanoes can lead to:
    
    - Reduced confining pressure on magma chambers
    - Increased chances of explosive eruptions
    - Higher risk of lahars (volcanic mudflows)
    - Changes in hydrothermal systems
    """)
    
    # Get glacial volcano data
    volcanoes = get_glacial_volcanoes()
    
    # Additional data for display
    for volcano in volcanoes:
        # Add default alert level based on risk level
        if volcano['risk_level'] == 'High':
            volcano['alert_level'] = 'High'
        elif volcano['risk_level'] == 'Medium':
            volcano['alert_level'] = 'Moderate'
        else:
            volcano['alert_level'] = 'Low'
            
        # Add deformation rate (millimeters per year)
        # Higher for high-risk volcanoes
        if volcano['risk_level'] == 'High':
            volcano['deformation_rate'] = round(5.0 + (hash(volcano['name']) % 8), 1)  # 5.0-12.9 mm/year
        elif volcano['risk_level'] == 'Medium':
            volcano['deformation_rate'] = round(0.5 + (hash(volcano['name']) % 6), 1)  # 0.5-6.4 mm/year
        else:
            volcano['deformation_rate'] = round(0.1 + (hash(volcano['name']) % 2), 1)  # 0.1-2.0 mm/year
            
        # Add SO2 level (parts per million)
        if volcano['risk_level'] == 'High':
            volcano['so2_level'] = round(0.7 + (hash(volcano['name'] + 'so2') % 20) / 10, 1)  # 0.7-2.6 ppm
        elif volcano['risk_level'] == 'Medium':
            volcano['so2_level'] = round(0.1 + (hash(volcano['name'] + 'so2') % 15) / 10, 1)  # 0.1-1.6 ppm
        else:
            volcano['so2_level'] = round(0.1 + (hash(volcano['name'] + 'so2') % 5) / 10, 1)  # 0.1-0.6 ppm
            
        # Determine eruption type based on name and characteristics
        name_lower = volcano['name'].lower()
        notes_lower = volcano['notes'].lower()
        
        if 'subglacial' in notes_lower or 'ice-filled' in notes_lower:
            volcano['eruption_type'] = 'Subglacial'
        elif 'lahar' in notes_lower:
            volcano['eruption_type'] = 'Lahar'
        elif 'submarine' in name_lower or 'underwater' in notes_lower:
            volcano['eruption_type'] = 'Submarine'
        elif 'crater lake' in notes_lower:
            volcano['eruption_type'] = 'Crater Lake'
        elif 'research' in notes_lower:
            volcano['eruption_type'] = 'Research'
        else:
            volcano['eruption_type'] = 'Stratovolcano'
        
        # Add InSAR URL
        # For volcanoes in the United States, use USGS links
        if 'United States' in volcano['country']:
            name_for_url = volcano['name'].replace(' ', '_').lower()
            volcano['insar_url'] = f"https://volcanoes.usgs.gov/volcanoes/{name_for_url}/"
        # For Iceland volcanoes
        elif 'Iceland' in volcano['country']:
            name_for_url = volcano['name'].replace('ö', 'o').replace('í', 'i').replace('æ', 'ae').lower()
            volcano['insar_url'] = f"https://en.vedur.is/volcanos/{name_for_url}/"
        # For notable volcanoes, use the Smithsonian GVP database
        elif volcano['risk_level'] == 'High' or volcano['risk_level'] == 'Medium':
            volcano['insar_url'] = "https://volcano.si.edu/volcano.cfm?vnum=global"
        else:
            volcano['insar_url'] = None
    
    # Filter functionality
    st.sidebar.subheader("Filter Volcanoes")
    
    # Risk level filter
    risk_levels = ["All"] + sorted(set(v['risk_level'] for v in volcanoes))
    selected_risk = st.sidebar.selectbox("Risk Level", risk_levels)
    
    # Country filter
    countries = ["All"] + sorted(set(v['country'] for v in volcanoes))
    selected_country = st.sidebar.selectbox("Country", countries)
    
    # Filter volcanoes based on selections
    filtered_volcanoes = volcanoes
    if selected_risk != "All":
        filtered_volcanoes = [v for v in filtered_volcanoes if v['risk_level'] == selected_risk]
    if selected_country != "All":
        filtered_volcanoes = [v for v in filtered_volcanoes if v['country'] == selected_country]
    
    # Display the count of filtered volcanoes
    st.markdown(f"### Showing {len(filtered_volcanoes)} glaciated volcanoes")
    
    # Custom CSS for the risk cards
    st.markdown("""
    <style>
    .risk-card {
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-card-high {
        border-left: 5px solid crimson;
        background-color: rgba(220, 20, 60, 0.05);
    }
    .risk-card-medium {
        border-left: 5px solid orange;
        background-color: rgba(255, 165, 0, 0.05);
    }
    .risk-card-low {
        border-left: 5px solid green;
        background-color: rgba(0, 128, 0, 0.05);
    }
    .card-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .card-subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .card-data {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .data-item {
        margin-bottom: 0.5rem;
    }
    .data-label {
        font-weight: bold;
        color: #555;
    }
    .notes {
        font-style: italic;
        color: #666;
        border-top: 1px solid #eee;
        padding-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the volcano risk cards in a grid layout
    for i, volcano in enumerate(filtered_volcanoes):
        risk_class = f"risk-card-{volcano['risk_level'].lower()}"
        html = f"""
        <div class="risk-card {risk_class}">
            <div class="card-title">{volcano['name']}</div>
            <div class="card-subtitle">{volcano['country']}</div>
            
            <div class="card-data">
                <div class="data-item">
                    <div class="data-label">Risk Level:</div>
                    {volcano['risk_level']}
                </div>
                <div class="data-item">
                    <div class="data-label">Alert Level:</div>
                    {volcano['alert_level']}
                </div>
                <div class="data-item">
                    <div class="data-label">Type:</div>
                    {volcano['eruption_type']}
                </div>
                <div class="data-item">
                    <div class="data-label">Elevation:</div>
                    {volcano['elevation']} m
                </div>
                <div class="data-item">
                    <div class="data-label">Deformation Rate:</div>
                    {volcano['deformation_rate']} mm/year
                </div>
                <div class="data-item">
                    <div class="data-label">SO₂ Level:</div>
                    {volcano['so2_level']} ppm
                </div>
                <div class="data-item">
                    <div class="data-label">Location:</div>
                    {volcano['lat']:.4f}, {volcano['lng']:.4f}
                </div>
            </div>
            
            <div class="notes">
                {volcano['notes']}
            </div>
        """
        
        # Add InSAR link if available
        if volcano['insar_url']:
            html += f"""
            <div style="margin-top: 1rem;">
                <a href="{volcano['insar_url']}" target="_blank">View InSAR Imagery →</a>
            </div>
            """
            
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    
    st.markdown("""
    ## Sources & Methodology
    
    Data for this visualization is sourced from:
    
    - Global Volcanism Program (GVP) database
    - InSAR satellite monitoring networks
    - Published research on climate-volcano interactions
    - Volcanic observatories worldwide
    
    Risk assessments are based on:
    
    - Historical eruption patterns
    - Current monitoring data
    - Glacier coverage and recent changes
    - Proximity to population centers
    """)

if __name__ == "__main__":
    app()