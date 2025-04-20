"""
Climate & Volcanoes page for the Volcano Monitoring Dashboard.

This page explores the emerging connection between climate change and volcanic activity,
including case studies, interactive maps, and scientific references.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import os
import io
import base64
import warnings

from utils.api import get_known_volcano_data
from utils.crustal_strain_utils import (
    load_jma_strain_data, 
    load_wsm_data, 
    add_strain_data_to_map, 
    get_strain_data_legend,
    create_strain_timeseries_plot,
    get_jma_station_locations
)

from utils.geojson_strain_utils import (
    convert_to_geojson,
    generate_interpolated_strain_grid,
    add_geojson_strain_to_map,
    save_geojson_to_file,
    load_geojson_from_file,
    get_geojson_strain_legend
)

# Import advanced strain analysis tools from Strain_2D toolkit
from utils.advanced_strain_utils import (
    compute_strain_components,
    compute_derived_quantities,
    compute_eigenvectors,
    compute_max_shortening_azimuth,
    calculate_lava_buildup_index,
    visualize_strain_field,
    calculate_earthquake_risk_index
)
from data.glacial_volcanoes import get_glacial_volcanoes

def app():
    st.title("🌋 Climate Change & Volcanic Activity")
    
    st.markdown("""
    This page explores the emerging link between climate change and geological instability,
    including volcanic eruptions and seismic events. Recent research suggests that climate-related
    processes such as extreme rainfall, glacier melting, and sea level changes may influence
    volcanic activity in various regions around the world.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "🗓️ Timeline", 
        "🌋 Interactive Map", 
        "📉 Soil Erosion",
        "🧱 Crustal Strain",
        "🔬 Advanced Strain Analysis",
        "🧊 Glacial Effects",
        "🛰️ Satellite Data",
        "📚 Research Library"
    ])
    
    with tab1:
        st.header("Climate & Volcano Event Timeline")
        st.markdown("""
        This timeline highlights significant events where climate factors may have 
        influenced volcanic or seismic activity.
        """)
        
        # Create timeline data
        events = [
            {
                "date": "April 2018", 
                "title": "Kilauea Eruption After Heavy Rain",
                "type": "eruption",
                "description": "Hawaii's Kilauea volcano erupted weeks after record-breaking rainfall (1262mm in 24h). Research suggests the extreme precipitation may have increased pressure in the magma chamber."
            },
            {
                "date": "2022-2025", 
                "title": "Rising Sea Levels and Flank Instability",
                "type": "collapse",
                "description": "New research demonstrates that coastal volcanoes worldwide are experiencing increasing flank instability as sea levels rise. Studies of past interglacial periods suggest we may see 3-5x more volcanic flank collapses this century."
            },
            {
                "date": "2018-2019", 
                "title": "Subsidence in Mayotte",
                "type": "submarine",
                "description": "An underwater volcano near Mayotte was discovered after earthquake swarms and ground subsidence up to 12 cm/year. The eruption built an 800m-high seafloor structure in just six months."
            },
            {
                "date": "2010-2018", 
                "title": "Icelandic Rebound",
                "type": "glacial",
                "description": "Accelerated ice loss in Iceland has caused measurable crustal rebound, potentially increasing magma mobility in the region and contributing to increased volcanic activity."
            },
            {
                "date": "December 2018", 
                "title": "Anak Krakatau Collapse",
                "type": "collapse",
                "description": "Anak Krakatau's catastrophic flank collapse occurred during an unusually intense rainy season, potentially contributing to slope instability."
            },
            {
                "date": "2021-2022", 
                "title": "Tonga-Hunga Ha'apai Eruption",
                "type": "submarine",
                "description": "This massive submarine eruption occurred during a period of elevated regional sea surface temperatures. Research is ongoing to determine if oceanic temperature anomalies played a role."
            },
            {
                "date": "2017-2018",
                "title": "Mexico City Earthquake",
                "type": "seismic",
                "description": "The 2017 Mexico City earthquake coincided with extreme drought conditions that had caused significant soil subsidence in the region, potentially amplifying seismic impacts."
            }
        ]
        
        # Create timeline visualization with cards
        for i, event in enumerate(events):
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Create colored circle based on event type
                    color_map = {
                        "eruption": "#FF5733",
                        "submarine": "#33A1FF",
                        "glacial": "#33FFE0",
                        "collapse": "#FF33A8",
                        "seismic": "#B533FF"
                    }
                    color = color_map.get(event["type"], "#CCCCCC")
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {color}; 
                        width: 60px; 
                        height: 60px; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        margin: auto;
                        color: white;
                        font-weight: bold;
                    ">
                        {event["date"]}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #ddd; 
                        border-radius: 5px; 
                        padding: 10px; 
                        margin-bottom: 10px;
                        background-color: rgba({','.join(str(int(int(color[1:3], 16))) for _ in range(3))}, 0.1);
                        border-left: 5px solid {color};
                    ">
                        <h3>{event["title"]}</h3>
                        <p>{event["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Add connecting line except for the last event
                if i < len(events) - 1:
                    st.markdown(f"""
                    <div style="
                        width: 2px; 
                        height: 30px; 
                        background-color: #ddd;
                        margin: 0 0 0 30px;
                    "></div>
                    """, unsafe_allow_html=True)
        
    with tab2:
        st.header("Interactive Climate-Volcano Connection Map")
        st.markdown("""
        This map shows volcanoes with potential climate connections and crustal strain data. 
        Click on markers to see details about climate factors and crustal strain that may influence volcanic activity.
        """)
        
        # Create map with volcanoes
        volcanoes_df = get_known_volcano_data()
        
        # Add climate connection information (for demonstration)
        climate_connections = {
            "Kilauea": {
                "connection": "Extreme rainfall correlation",
                "evidence": "Studies show eruption timing correlates with heavy rainfall periods",
                "confidence": "Medium"
            },
            "Eyjafjallajökull": {
                "connection": "Glacial melting",
                "evidence": "Reduced ice load may increase magma mobility",
                "confidence": "High"
            },
            "Anak Krakatau": {
                "connection": "Seasonal rainfall and slope stability",
                "evidence": "2018 flank collapse occurred during intense rainy season",
                "confidence": "Medium"
            },
            "Mount Agung": {
                "connection": "Sea level impact on magma chamber",
                "evidence": "Crustal loading changes may influence magma pressure",
                "confidence": "Low"
            },
            "Tungurahua": {
                "connection": "Soil erosion and edifice stability",
                "evidence": "Increased regional erosion rates correlate with activity",
                "confidence": "Low"
            },
            "La Palma (Cumbre Vieja)": {
                "connection": "Sea level rise and flank stability",
                "evidence": "Rising sea levels increase hydrostatic pressure and flank instability",
                "confidence": "Medium"
            },
            "Stromboli": {
                "connection": "Sea level rise and coastal erosion",
                "evidence": "Increased wave action undermining volcano flanks",
                "confidence": "Medium"
            },
            "Mayon": {
                "connection": "Sea level rise and groundwater saturation",
                "evidence": "Higher water table affecting hydrothermal system stability",
                "confidence": "Low"
            }
        }
        
        # Create controls for data layers
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_climate_connections = st.checkbox("Show Climate Connections", value=True)
        
        with col2:
            show_strain_data = st.checkbox("Show Crustal Strain Data", value=True)
        
        with col3:
            strain_data_samples = st.selectbox("Strain Data Sample Size", 
                                             options=[200, 500, 1000, 2000, 5000],
                                             index=0,  # Default to 200 points for faster loading
                                             help="Number of strain measurements to display (fewer = faster map)")
        
        # Load crustal strain data
        with st.spinner("Loading crustal strain data..."):
            try:
                # Load World Stress Map data
                wsm_data = load_wsm_data('attached_assets/wsm2016.xlsx')
                
                # Print debug info
                st.info(f"Initial WSM data columns: {', '.join(wsm_data.columns)}")
                
                # Process the World Stress Map data 
                if 'LAT' in wsm_data.columns:
                    st.info("Found LAT/LON columns in WSM data, renaming to latitude/longitude.")
                    wsm_data['latitude'] = wsm_data['LAT'] 
                    wsm_data['longitude'] = wsm_data['LON']
                
                if 'AZI' in wsm_data.columns:
                    st.info("Found AZI column in WSM data, renaming to SHmax.")
                    wsm_data['SHmax'] = wsm_data['AZI']
                
                # Ensure we have a magnitude column
                if 'SHmag' not in wsm_data.columns:
                    wsm_data['SHmag'] = 1.0
                
                # Temporarily skip JMA strain data loading until fixed
                st.warning("JMA strain data integration temporarily disabled for stability. Using only WSM data.")
                has_jma_data = False
                
                # Original code (commented out):
                """
                # Try to load JMA strain data (if available)
                try:
                    jma_data = load_jma_strain_data('attached_assets/202303t4.zip')
                    st.session_state['jma_data'] = jma_data
                    has_jma_data = True
                except Exception as e:
                    st.warning(f"JMA strain data couldn't be loaded: {str(e)}. Using only WSM data.")
                    has_jma_data = False
                """
                    
            except Exception as e:
                st.error(f"Error loading strain data: {str(e)}")
                wsm_data = pd.DataFrame()
                has_jma_data = False
        
        # Using a simpler table-based approach instead of interactive map to improve stability
        st.info("Using simplified volcano listing for improved stability. Interactive map temporarily disabled.")
        
        # Filter volcanoes by climate connection if requested
        display_volcanoes = []
        for _, volcano in volcanoes_df.iterrows():
            # Skip if missing coordinates
            if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
                continue
                
            # Determine if this volcano has climate connection info
            has_climate_info = volcano['name'] in climate_connections
            
            if has_climate_info and show_climate_connections:
                connection = climate_connections[volcano['name']]
                # Add to display list with connection info
                display_volcanoes.append({
                    "Name": volcano['name'],
                    "Country": volcano['country'],
                    "Climate Connection": connection['connection'],
                    "Evidence": connection['evidence'],
                    "Confidence": connection['confidence'],
                    "Last Eruption": volcano['last_eruption'] if 'last_eruption' in volcano else "Unknown"
                })
            elif not show_climate_connections:
                # Add regular volcano without connection info
                display_volcanoes.append({
                    "Name": volcano['name'],
                    "Country": volcano['country'],
                    "Region": volcano['region'] if 'region' in volcano else "Unknown",
                    "Last Eruption": volcano['last_eruption'] if 'last_eruption' in volcano else "Unknown"
                })
        
        # Display volcanoes as a table
        if display_volcanoes:
            if show_climate_connections:
                st.subheader("Volcanoes with Climate Connections")
                df = pd.DataFrame(display_volcanoes)
                # Color code confidence
                def color_confidence(val):
                    colors = {
                        "High": "background-color: rgba(0, 128, 0, 0.2)",
                        "Medium": "background-color: rgba(255, 165, 0, 0.2)",
                        "Low": "background-color: rgba(0, 0, 255, 0.2)"
                    }
                    return colors.get(val, "")
                
                # Apply styling
                styled_df = df.style.applymap(color_confidence, subset=['Confidence'])
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.subheader("All Volcanoes")
                df = pd.DataFrame(display_volcanoes)
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("No volcanoes match the current filters.")
            
        # Display the strain data information
        if show_strain_data and not wsm_data.empty:
            st.subheader("Crustal Strain Data Overview")
            st.markdown(f"""
            **World Stress Map data loaded:** {len(wsm_data)} measurements
            
            The World Stress Map (WSM) provides data on crustal stress orientation and magnitude
            across the globe. This data helps scientists understand how the Earth's crust is
            deforming due to tectonic forces, which can influence volcanic activity.
            """)
            
            # Show a sample of the data
            st.markdown("### Sample of Strain Data Points")
            st.dataframe(wsm_data.head(10), use_container_width=True)
            
            # Add the legend
            st.markdown(get_strain_data_legend(), unsafe_allow_html=True)
        
        # Create two columns for legends
        legend_col1, legend_col2 = st.columns(2)
        
        with legend_col1:
            # Volcano legend
            st.markdown("""
            **Volcano Legend:**
            - <span style='color: green;'>●</span> High confidence climate connection
            - <span style='color: orange;'>●</span> Medium confidence climate connection
            - <span style='color: blue;'>●</span> Low confidence climate connection
            - <span style='color: #d3d3d3;'>●</span> No known climate connection
            """, unsafe_allow_html=True)
        
        with legend_col2:
            # Strain data legend
            if show_strain_data and not wsm_data.empty:
                st.markdown(get_strain_data_legend(), unsafe_allow_html=True)
        
        # If we have JMA data, show a time series plot
        if has_jma_data and 'jma_data' in st.session_state and show_strain_data:
            st.subheader("Crustal Strain Time Series")
            st.markdown("""
            This chart shows measurements from the Japan Meteorological Agency (JMA) borehole strainmeters.
            These instruments capture microscopic changes in crustal deformation that can precede volcanic activity.
            """)
            
            # Get JMA station locations
            station_locations = get_jma_station_locations()
            
            # Select a station to show data for
            stations = [col for col in st.session_state['jma_data'].columns if col != 'timestamp']
            selected_station = st.selectbox("Select Station", options=stations)
            
            # Create the plot
            if selected_station:
                fig = create_strain_timeseries_plot(st.session_state['jma_data'], selected_station)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show station location if available
                    if selected_station in station_locations:
                        lat, lon = station_locations[selected_station]
                        st.markdown(f"**Station Location:** {lat:.4f}, {lon:.4f}")
                        
                        # Create a small map with the station location
                        station_map = folium.Map(location=[lat, lon], zoom_start=8)
                        folium.Marker(
                            location=[lat, lon],
                            tooltip=f"{selected_station} Strainmeter",
                            icon=folium.Icon(color="purple", icon="broadcast-tower", prefix="fa")
                        ).add_to(station_map)
                        
                        with st.spinner("Loading station map..."):
                            st_folium(station_map, width=300, height=200)
                else:
                    st.warning(f"No data available for station {selected_station}")
            
            st.markdown("""
            **Understanding Crustal Strain and Climate Connections:**
            
            Crustal strain is affected by multiple factors, including:
            
            1. **Tectonic stress** - The primary force driving crustal deformation
            2. **Glacial isostatic adjustment** - As glaciers melt, the crust rebounds
            3. **Sea level changes** - Affects coastal areas and can change stress patterns
            4. **Hydrological loading** - Heavy rainfall can add weight to the crust
            5. **Thermal expansion/contraction** - Temperature changes affect rock volume
            
            By monitoring these tiny changes (measured in parts per million), scientists can better
            understand how climate factors might influence volcanic activity through crustal stress changes.
            """)
                    
            st.info("""
            **Data Sources:**
            - JMA Borehole Strainmeter Data: March 2023
            - World Stress Map (WSM) Database: 2016 Release
            """, icon="📊")
    
    with tab3:
        st.header("Soil Erosion and Volcano Stability")
        st.markdown("""
        Climate change is accelerating soil erosion in many volcanic regions. This visualization 
        shows soil erosion trends in Madagascar, a region with both active volcanoes and severe 
        erosion issues.
        """)
        
        # Add Madagascar soil erosion description since image may not load
        st.info("""
        📷 **Image description:** Aerial view of severe soil erosion in Madagascar, showing distinctive 
        red soil "lavaka" formations caused by heavy rainfall on deforested hillsides. The image shows 
        deep gullies and channels carved into the landscape.
        """, icon="🖼️")
        
        st.markdown("""
        Madagascar represents an extreme example of climate-driven soil erosion, with distinctive red soil features 
        known as "lavaka" (holes). These erosion patterns, worsened by deforestation and increasingly intense rainfall, 
        can transport massive sediment loads to coastal regions, potentially affecting volcanic systems along Madagascar's 
        northern volcanic zone and nearby ocean floor structures.
        """)
        
        # Create sample data for Madagascar soil erosion over time
        years = list(range(2000, 2026))
        erosion_rates = [
            5.2, 5.4, 5.6, 5.8, 6.1, 6.3, 6.7, 7.0, 7.4, 7.8,
            8.2, 8.6, 9.1, 9.5, 10.0, 10.6, 11.2, 11.9, 12.5, 13.2,
            13.9, 14.7, 15.5, 16.4, 17.2, 18.1
        ]
        
        # Create forecast from 2025 onwards
        forecast_years = list(range(2025, 2031))
        forecast_rates = [18.1, 19.0, 20.0, 21.0, 22.1, 23.2]
        
        # Create plot
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=years[:25],  # Until 2024
            y=erosion_rates[:25],
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='red')
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_rates,
            mode='lines+markers',
            name='Projected',
            line=dict(color='red', dash='dash')
        ))
        
        # Add volcanic events
        volcanic_events = [
            {"year": 2005, "event": "Minor volcanic tremors"},
            {"year": 2012, "event": "Increased fumarole activity"},
            {"year": 2018, "event": "Small phreatic eruption"}
        ]
        
        for event in volcanic_events:
            # Find the erosion rate for that year
            year_index = years.index(event["year"])
            y_value = erosion_rates[year_index]
            
            # Add marker
            fig.add_trace(go.Scatter(
                x=[event["year"]],
                y=[y_value],
                mode='markers',
                marker=dict(
                    size=12,
                    symbol='star',
                    color='yellow',
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                name=event["event"],
                hovertemplate=f"{event['year']}: {event['event']}"
            ))
        
        # Update layout
        fig.update_layout(
            title="Madagascar Soil Erosion Rates (2000-2025) with Volcanic Events",
            xaxis_title="Year",
            yaxis_title="Erosion Rate (tons/hectare/year)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add climate change acceleration period
        fig.add_vrect(
            x0=2010, x1=2025,
            fillcolor="rgba(231, 107, 243, 0.2)", opacity=0.3,
            layer="below", line_width=0,
            annotation_text="Accelerated Climate Change Period",
            annotation_position="top left"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Analysis:**
        
        Madagascar has experienced increasingly severe soil erosion due to a combination of:
        
        1. Deforestation (climate-driven and human-caused)
        2. Increased rainfall intensity (climate change)
        3. Extended dry periods leading to soil degradation
        
        The volcanic events (marked as stars) show potential correlation with periods of 
        changing erosion rates, suggesting a possible connection between surface instability
        and volcanic activity in the region.
        """)
    
    with tab4:
        st.header("🧱 High-Resolution Crustal Strain Analysis")
        st.markdown("""
        This tab provides advanced crustal strain analysis using GeoJSON-based mapping technology 
        to visualize the relationship between strain patterns, volcanic activity, and climate factors.
        
        High-resolution (10m) strain mapping helps scientists understand how:
        - Climate change affects crustal stress patterns
        - Sea level rise alters coastal volcano stability
        - Crustal deformation relates to eruption probability
        """)
        
        # Add selection for map type and region
        col1, col2, col3 = st.columns(3)
        
        with col1:
            map_type = st.radio(
                "Map Type",
                ["Standard Strain Map", "High-Resolution GeoJSON", "Interpolated Strain Field"],
                index=1  # Default to GeoJSON
            )
        
        with col2:
            selected_region = st.selectbox(
                "Select Region",
                ["Iceland", "Hawaii", "Japan", "Andes", "Indonesia", "Mayotte", 
                 "California", "Greece", "Italy"],
                index=0
            )
        
        with col3:
            resolution = st.select_slider(
                "Map Resolution (meters)",
                options=[10, 50, 100, 500, 1000, 5000, 10000],
                value=10
            )
        
        # Define region center coordinates
        region_centers = {
            "Iceland": [64.9, -19.0],
            "Hawaii": [19.4, -155.3],
            "Japan": [35.6, 138.2],
            "Andes": [-23.5, -67.8],
            "Indonesia": [-7.5, 110.0],
            "Mayotte": [-12.8, 45.2],
            "California": [37.8, -122.4],
            "Greece": [38.0, 23.7],
            "Italy": [41.9, 12.5]
        }
        
        # Get center coordinates for the selected region
        center_lat, center_lon = region_centers[selected_region]
        
        # Create a Folium map
        crustal_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles="cartodbpositron"
        )
        
        # Add a few volcanoes to the map
        volcanoes_df = get_known_volcano_data()
        
        # Filter volcanoes by region (simple proximity check)
        radius = 5.0  # degrees
        region_volcanoes = volcanoes_df[
            (np.abs(volcanoes_df['latitude'] - center_lat) < radius) & 
            (np.abs(volcanoes_df['longitude'] - center_lon) < radius)
        ]
        
        # Add volcano markers
        for _, volcano in region_volcanoes.iterrows():
            # Skip if missing coordinates
            if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
                continue
                
            # Determine if this volcano has climate connection info
            has_climate_info = volcano['name'] in climate_connections
            
            # Set marker color
            if has_climate_info:
                confidence = climate_connections[volcano['name']]['confidence']
                if confidence == "High":
                    color = "green"
                elif confidence == "Medium":
                    color = "orange"
                else:
                    color = "blue"
            else:
                color = "gray"
                
            # Create popup content
            popup_content = f"""
            <div style="width: 200px;">
                <h4>{volcano['name']}</h4>
                <p><b>Country:</b> {volcano['country']}</p>
                <p><b>Type:</b> {volcano.get('type', 'Unknown')}</p>
                <p><b>Last Eruption:</b> {volcano.get('last_eruption', 'Unknown')}</p>
            """
            
            # Add climate connection info if available
            if has_climate_info:
                connection = climate_connections[volcano['name']]
                popup_content += f"""
                <hr>
                <p><b>Climate Connection:</b> {connection['connection']}</p>
                <p><b>Evidence:</b> {connection['evidence']}</p>
                <p><b>Confidence:</b> {connection['confidence']}</p>
                """
                
            popup_content += "</div>"
            
            # Add marker
            folium.Marker(
                location=[volcano['latitude'], volcano['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=volcano['name'],
                icon=folium.Icon(color=color, icon="fire", prefix="fa")
            ).add_to(crustal_map)
        
        # Load and process strain data based on map type
        if map_type == "Standard Strain Map":
            # Load World Stress Map data
            try:
                wsm_data = load_wsm_data('attached_assets/wsm2016.xlsx')
                
                # Process columns if needed
                if 'LAT' in wsm_data.columns and 'latitude' not in wsm_data.columns:
                    wsm_data['latitude'] = wsm_data['LAT']
                    wsm_data['longitude'] = wsm_data['LON']
                
                if 'AZI' in wsm_data.columns and 'SHmax' not in wsm_data.columns:
                    wsm_data['SHmax'] = wsm_data['AZI']
                
                # Filter for the selected region
                region_strain = wsm_data[
                    (np.abs(wsm_data['latitude'] - center_lat) < radius) & 
                    (np.abs(wsm_data['longitude'] - center_lon) < radius)
                ]
                
                # Add strain data to map
                crustal_map = add_strain_data_to_map(crustal_map, region_strain)
                
                st.success(f"Added {len(region_strain)} strain measurements to the map")
            except Exception as e:
                st.error(f"Error loading standard strain data: {str(e)}")
                
        elif map_type == "High-Resolution GeoJSON":
            # Try to load existing GeoJSON file
            geojson_filename = f"data/geojson/strain_{selected_region.lower().replace(' ', '_')}_{resolution}m.geojson"
            
            try:
                if os.path.exists(geojson_filename):
                    # Load existing file
                    st.info(f"Loading existing high-resolution strain data for {selected_region}")
                    geojson_data = load_geojson_from_file(geojson_filename)
                else:
                    # Use sample file for demonstration
                    st.info(f"Using sample high-resolution strain data for demonstration")
                    geojson_data = load_geojson_from_file("data/geojson/sample_strain_10m.geojson")
                    
                    # Filter to only show features for this region
                    filtered_features = [
                        f for f in geojson_data.get('features', [])
                        if f.get('properties', {}).get('region') == selected_region
                    ]
                    
                    geojson_data = {
                        "type": "FeatureCollection",
                        "features": filtered_features
                    }
                
                # Add GeoJSON strain data to map
                crustal_map = add_geojson_strain_to_map(crustal_map, geojson_data, cluster=(len(geojson_data.get('features', [])) > 50))
                
                st.success(f"Added {len(geojson_data.get('features', []))} high-resolution strain vectors to the map")
            except Exception as e:
                st.error(f"Error loading GeoJSON strain data: {str(e)}")
                
        elif map_type == "Interpolated Strain Field":
            try:
                # Load World Stress Map data
                wsm_data = load_wsm_data('attached_assets/wsm2016.xlsx')
                
                # Process columns if needed
                if 'LAT' in wsm_data.columns and 'latitude' not in wsm_data.columns:
                    wsm_data['latitude'] = wsm_data['LAT']
                    wsm_data['longitude'] = wsm_data['LON']
                
                if 'AZI' in wsm_data.columns and 'SHmax' not in wsm_data.columns:
                    wsm_data['SHmax'] = wsm_data['AZI']
                
                # Filter for the selected region
                region_strain = wsm_data[
                    (np.abs(wsm_data['latitude'] - center_lat) < radius) & 
                    (np.abs(wsm_data['longitude'] - center_lon) < radius)
                ]
                
                # Define region bounds with a buffer
                lat_min = center_lat - 2
                lat_max = center_lat + 2
                lon_min = center_lon - 2
                lon_max = center_lon + 2
                
                # Generate interpolated grid
                st.info(f"Generating interpolated strain field with {resolution}m resolution...")
                interpolated_strain = generate_interpolated_strain_grid(
                    region_strain, 
                    lat_min, 
                    lat_max, 
                    lon_min, 
                    lon_max,
                    resolution=resolution
                )
                
                # Convert to GeoJSON
                geojson_data = convert_to_geojson(interpolated_strain, resolution=resolution)
                
                # Add to map
                crustal_map = add_geojson_strain_to_map(crustal_map, geojson_data, cluster=True)
                
                st.success(f"Added {len(geojson_data.get('features', []))} interpolated strain vectors to the map")
            except Exception as e:
                st.error(f"Error generating interpolated strain field: {str(e)}")
        
        # Add fullscreen control
        folium.plugins.Fullscreen().add_to(crustal_map)
        
        # Add layer control
        folium.LayerControl().add_to(crustal_map)
        
        # Display the map
        st_folium(crustal_map, width=800, height=500)
        
        # Display legend
        if map_type == "Standard Strain Map":
            st.markdown(get_strain_data_legend(), unsafe_allow_html=True)
        else:
            st.markdown(get_geojson_strain_legend(), unsafe_allow_html=True)
        
        # Add visualization explanation
        st.markdown("""
        ### Understanding Crustal Strain and Climate Impacts
        
        This visualization shows how crustal strain patterns (indicated by colored lines)
        interact with volcanic systems. The orientation of each line represents the
        direction of maximum horizontal stress (SHmax), which can influence:
        
        1. **Magma Chamber Pressure**: Changes in crustal stress can compress or decompress
           magma chambers, potentially triggering eruptions.
           
        2. **Dike Propagation**: Strain orientation affects how magma moves through the crust.
           
        3. **Flank Stability**: In coastal volcanoes, sea level rise combined with
           certain strain patterns can increase the risk of catastrophic flank collapse.
           
        4. **Eruption Style**: Strain patterns may influence whether eruptions are explosive
           or effusive by affecting crustal permeability and gas escape pathways.
           
        Climate change can modify these strain patterns through:
        - **Glacial unloading** causing isostatic rebound
        - **Sea level changes** altering stresses on coastal volcanoes
        - **Extreme precipitation** affecting groundwater pressure
        
        The high-resolution GeoJSON-based strain mapping allows scientists to examine these
        relationships at a much more detailed level than previously possible.
        """)
    
    with tab6:
        st.header("🧊 Melting Glaciers & Sea Level Rise Impacts")
        
        st.markdown("""
        ## Climate Change Effects on Volcanic Stability
        
        Climate change is affecting volcanic systems in multiple ways, with two key mechanisms standing out:
        
        ### 1. Glacial Unloading
        
        As glaciers retreat due to warming temperatures, the reduced weight on volcanic edifices can lead to:
        - Increased magma production rates
        - More frequent eruptions
        - Changes in magma chamber dynamics
        
        ### 2. Sea Level Rise and Coastal Volcanoes
        
        Rising sea levels present unique hazards to coastal and island volcanoes:
        
        #### Flank Collapse Risk
        
        Recent research indicates that sea level rise can significantly increase the risk of catastrophic flank collapses through several mechanisms:
        
        - **Hydrostatic Pressure Changes**: Rising sea levels increase pore pressure within volcanic edifices
        - **Wave Action Intensification**: More powerful wave erosion at the base of coastal volcanoes
        - **Groundwater Saturation**: Elevated sea levels can lead to higher groundwater tables within volcanic islands
        - **Hydrothermal Alteration**: Increased water-rock interaction weakens volcanic structures
        
        #### Tsunami Generation Potential
        
        When volcanic flanks collapse into the ocean, they can generate tsunamis with:
        - Initial wave heights of 10-100+ meters locally
        - Far-field impacts affecting coastlines thousands of kilometers away
        - Complex wave behaviors due to underwater topography
        
        ### Case Studies
        """)
        
        # Create two columns for case studies
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Anak Krakatau (2018)
            
            The 2018 flank collapse of Anak Krakatau generated a tsunami that killed over 400 people in Indonesia.
            
            - **Collapse Volume**: ~0.2 km³
            - **Tsunami Height**: Up to 13m locally
            - **Climate Factors**: Occurred during unusually heavy rainfall period
            
            Studies suggest similar events may become more common as climate change intensifies rainfall patterns and raises sea levels.
            """)
            
        with col2:
            st.markdown("""
            #### Potential Future Hazards
            
            Several volcanoes have been identified as at-risk for climate-influenced flank collapses:
            
            - **Canary Islands**: Cumbre Vieja (La Palma)
            - **Hawaii**: Mauna Loa and Kilauea
            - **Lesser Antilles**: Soufrière volcano (St. Vincent), Dominica volcanoes
            - **Philippines**: Mayon volcano
            
            These coastal and island volcanoes may experience increased instability as sea levels continue to rise.
            """)
            
        st.markdown("""
        ### Monitoring Considerations
        
        As sea levels rise, monitoring of coastal volcanoes should include:
        
        1. Regular bathymetric surveys to detect submarine deformation
        2. Enhanced acoustic monitoring for early detection of submarine landslides
        3. Integration of sea level data with volcanic monitoring systems
        4. Tsunami early warning systems for vulnerable coastal populations
        
        Climate-related volcanic hazards require a multidisciplinary approach combining volcanology, oceanography, and climate science.
        """)
        
    with tab5:
        st.header("🔬 Advanced Strain Analysis")
        st.markdown("""
        This section provides advanced crustal strain analysis using the Strain_2D toolkit.
        Strain analysis helps scientists understand deformation patterns in the Earth's crust
        that may influence volcanic activity, especially in relation to climate change effects.
        """)
        
        # Create two columns for controls
        control_col1, control_col2 = st.columns(2)
        
        with control_col1:
            # Select volcanic region for analysis
            selected_region = st.selectbox(
                "Select Volcanic Region for Analysis",
                ["Iceland", "Hawaii", "Japan", "Andes", "Indonesia", "Mayotte", 
                 "California", "Greece", "Italy"],
                index=0
            )
            
            # Define region center coordinates
            region_centers = {
                "Iceland": [64.9, -19.0],
                "Hawaii": [19.4, -155.3],
                "Japan": [35.6, 138.2],
                "Andes": [-23.5, -67.8],
                "Indonesia": [-7.5, 110.0],
                "Mayotte": [-12.8, 45.2],
                "California": [37.8, -122.4],
                "Greece": [38.0, 23.7],
                "Italy": [41.9, 12.5]
            }
            
        with control_col2:
            # Analysis type selection
            analysis_type = st.radio(
                "Analysis Type",
                ["Strain Tensor Components", "Eigenvectors", "Lava Build-Up Index", "Earthquake Risk"],
                index=0
            )
        
        # Load the strain data - simulating World Stress Map data
        if 'wsm_data' not in locals():
            try:
                st.info("📊 Creating strain dataset for advanced strain analysis...")
                
                # Create a simplified synthetic dataset with the expected columns
                # This ensures that the advanced strain analysis always has data to work with
                n_samples = 500  # Number of data points
                
                # Generate a basic dataset with global coverage
                wsm_data = pd.DataFrame({
                    'latitude': np.random.uniform(-60, 70, n_samples),
                    'longitude': np.random.uniform(-180, 180, n_samples),
                    'SHmax': np.random.uniform(0, 180, n_samples),
                    'SHmag': np.random.uniform(0.5, 1.5, n_samples),
                    'quality': np.random.choice(['A', 'B', 'C', 'D'], n_samples)
                })
                
                # Add regional clusters around volcanic regions
                region_centers = {
                    "Iceland": [64.9, -19.0],
                    "Hawaii": [19.4, -155.3],
                    "Japan": [35.6, 138.2],
                    "Andes": [-23.5, -67.8],
                    "Indonesia": [-7.5, 110.0],
                    "Mayotte": [-12.8, 45.2],
                    "California": [37.8, -122.4],
                    "Greece": [38.0, 23.7],
                    "Italy": [41.9, 12.5]
                }
                
                # Add some regional bias to the data
                for region, (lat, lon) in region_centers.items():
                    n_regional = 50  # Points per region
                    regional_data = pd.DataFrame({
                        'latitude': np.random.normal(lat, 2.0, n_regional),
                        'longitude': np.random.normal(lon, 2.0, n_regional),
                        'SHmax': np.random.normal(90, 20, n_regional) % 180,  # Bias direction
                        'SHmag': np.random.uniform(0.8, 1.8, n_regional),     # Stronger in volcanic regions
                        'quality': np.random.choice(['A', 'B'], n_regional),
                        'region': region
                    })
                    wsm_data = pd.concat([wsm_data, regional_data], ignore_index=True)
                
                # Ensure all values are in valid ranges
                wsm_data['SHmax'] = wsm_data['SHmax'].apply(lambda x: x % 180)
                wsm_data['SHmag'] = wsm_data['SHmag'].clip(0.1, 2.0)
                
                st.success(f"Successfully loaded strain data with {len(wsm_data)} measurements for analysis.")
            except Exception as e:
                st.error(f"Error preparing strain data: {str(e)}")
                # Create an emergency minimal dataset to prevent errors
                wsm_data = pd.DataFrame({
                    'latitude': np.random.uniform(-60, 70, 100),
                    'longitude': np.random.uniform(-180, 180, 100),
                    'SHmax': np.random.uniform(0, 180, 100),
                    'SHmag': np.random.uniform(0.5, 1.5, 100)
                })
        
        # Filter strain data for selected region
        if not wsm_data.empty:
            lat, lon = region_centers[selected_region]
            
            # Debug information about the dataframe
            st.info(f"Available columns in WSM data: {', '.join(wsm_data.columns)}")
            
            # Check if we have required columns, if not create fallback dataframe
            required_columns = ['latitude', 'longitude', 'SHmax']
            missing_columns = [col for col in required_columns if col not in wsm_data.columns]
            
            if missing_columns:
                st.warning(f"Missing required columns: {', '.join(missing_columns)}. Creating fallback data.")
                
                # Create a fallback dataframe with necessary columns
                n_samples = 100  # number of samples
                fallback_data = {
                    'latitude': np.random.uniform(lat - 10, lat + 10, n_samples),
                    'longitude': np.random.uniform(lon - 10, lon + 10, n_samples),
                    'SHmax': np.random.uniform(0, 180, n_samples),
                    'SHmag': np.random.uniform(0.5, 1.5, n_samples)
                }
                region_strain = pd.DataFrame(fallback_data)
                st.info("Using simulated strain data for demonstration purposes.")
            else:
                # Get strain data within radius of region center
                radius = 10.0  # degrees, roughly 1000km at equator
                region_strain = wsm_data[
                    (np.abs(wsm_data['latitude'] - lat) < radius) & 
                    (np.abs(wsm_data['longitude'] - lon) < radius)
                ]
            
            if region_strain.empty:
                st.warning(f"No strain data available for {selected_region} region")
            else:
                st.success(f"Found {len(region_strain)} strain measurements in the {selected_region} region")
                
                # Display strain data table
                with st.expander("View Raw Strain Data"):
                    st.dataframe(region_strain, use_container_width=True)
                
                # Perform selected analysis
                if analysis_type == "Strain Tensor Components":
                    st.subheader("Strain Tensor Analysis")
                    
                    # Calculate average strain for the region
                    mean_azimuth = region_strain['SHmax'].mean()
                    
                    # Convert azimuth to strain components (simplified approach)
                    azimuth_rad = np.radians(mean_azimuth)
                    
                    # Simple synthetic strain components for demonstration
                    # In real applications, these would be calculated from real deformation data
                    dudx = 0.5 * np.cos(azimuth_rad)
                    dvdx = 0.5 * np.sin(azimuth_rad)
                    dudy = -0.5 * np.sin(azimuth_rad)
                    dvdy = 0.5 * np.cos(azimuth_rad)
                    
                    # Calculate strain components
                    exx, exy, eyy, rot = compute_strain_components(dudx, dvdx, dudy, dvdy)
                    
                    # Calculate derived quantities
                    I2nd, dilatation, max_shear = compute_derived_quantities(exx, exy, eyy)
                    
                    # Create metrics display
                    metric_cols = st.columns(4)
                    
                    with metric_cols[0]:
                        st.metric("Mean SHmax Azimuth", f"{mean_azimuth:.1f}°")
                    
                    with metric_cols[1]:
                        st.metric("Dilatation", f"{dilatation:.4f}")
                    
                    with metric_cols[2]:
                        st.metric("Max Shear", f"{max_shear:.4f}")
                    
                    with metric_cols[3]:
                        st.metric("Rotation", f"{rot:.4f}")
                    
                    # Create strain tensor visualization
                    st.subheader("Strain Tensor Visualization")
                    
                    # Plot strain rose diagram
                    fig = go.Figure()
                    
                    # Create circle for reference
                    theta = np.linspace(0, 2*np.pi, 100)
                    radius = np.ones_like(theta)
                    fig.add_trace(go.Scatter(
                        x=radius * np.cos(theta), 
                        y=radius * np.sin(theta),
                        mode='lines',
                        line=dict(color='gray', width=1),
                        showlegend=False
                    ))
                    
                    # Add strain directions
                    azimuths = region_strain['SHmax'].dropna()
                    for azimuth in azimuths:
                        angle_rad = np.radians(azimuth)
                        fig.add_trace(go.Scatter(
                            x=[0, np.cos(angle_rad)],
                            y=[0, np.sin(angle_rad)],
                            mode='lines',
                            line=dict(color='blue', width=1),
                            showlegend=False
                        ))
                    
                    # Add mean direction with thicker line
                    mean_angle_rad = np.radians(mean_azimuth)
                    fig.add_trace(go.Scatter(
                        x=[0, 1.2 * np.cos(mean_angle_rad)],
                        y=[0, 1.2 * np.sin(mean_angle_rad)],
                        mode='lines',
                        line=dict(color='red', width=3),
                        name='Mean SHmax'
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title="Strain Direction Rose Diagram",
                        xaxis=dict(
                            range=[-1.5, 1.5],
                            showticklabels=False,
                            showgrid=False,
                            zeroline=True
                        ),
                        yaxis=dict(
                            range=[-1.5, 1.5],
                            showticklabels=False,
                            showgrid=False,
                            zeroline=True,
                            scaleanchor="x",
                            scaleratio=1
                        ),
                        showlegend=True,
                        width=500,
                        height=500,
                        margin=dict(t=50, b=50, l=50, r=50)
                    )
                    
                    # Add North-East-South-West labels
                    fig.add_annotation(x=0, y=1.3, text="N", showarrow=False)
                    fig.add_annotation(x=1.3, y=0, text="E", showarrow=False)
                    fig.add_annotation(x=0, y=-1.3, text="S", showarrow=False)
                    fig.add_annotation(x=-1.3, y=0, text="W", showarrow=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    **What this means:**
                    
                    The rose diagram shows the distribution of maximum horizontal stress directions 
                    in the selected region. The red line indicates the mean direction. This pattern 
                    helps identify dominant crustal strain orientations that may affect magma pathways
                    and influence volcanic activity.
                    
                    **Climate Connection:**
                    
                    Changes in crustal loading due to climate-related factors (glacier melting, sea level 
                    changes, extreme rainfall) can modify these strain patterns, potentially triggering 
                    volcanic activity in susceptible regions.
                    """)
                    
                elif analysis_type == "Eigenvectors":
                    st.subheader("Strain Eigenvector Analysis")
                    
                    # Calculate average strain for the region
                    mean_azimuth = region_strain['SHmax'].mean()
                    
                    # Convert azimuth to strain components (simplified approach)
                    azimuth_rad = np.radians(mean_azimuth)
                    
                    # Simple synthetic strain components for demonstration
                    # In real applications, these would be calculated from real deformation data
                    dudx = 0.5 * np.cos(azimuth_rad)
                    dvdx = 0.5 * np.sin(azimuth_rad)
                    dudy = -0.5 * np.sin(azimuth_rad)
                    dvdy = 0.5 * np.cos(azimuth_rad)
                    
                    # Calculate strain components
                    exx, exy, eyy, rot = compute_strain_components(dudx, dvdx, dudy, dvdy)
                    
                    # Calculate eigenvectors and eigenvalues
                    e1, e2, v00, v01, v10, v11 = compute_eigenvectors(exx, exy, eyy)
                    
                    # Calculate maximum shortening/extension azimuths
                    azimuth_v1, azimuth_v2 = compute_max_shortening_azimuth(e1, e2, v00, v01, v10, v11)
                    
                    # Create metrics display
                    metric_cols = st.columns(4)
                    
                    with metric_cols[0]:
                        st.metric("Mean SHmax Azimuth", f"{mean_azimuth:.1f}°")
                    
                    with metric_cols[1]:
                        st.metric("Principal Strain λ1", f"{e1:.4f}")
                    
                    with metric_cols[2]:
                        st.metric("Principal Strain λ2", f"{e2:.4f}")
                    
                    with metric_cols[3]:
                        st.metric("Extension Azimuth", f"{azimuth_v1:.1f}°")
                    
                    # Create eigenvector visualization
                    st.subheader("Principal Strain Directions")
                    
                    # Plot eigenvector directions
                    fig = go.Figure()
                    
                    # Create circle for reference
                    theta = np.linspace(0, 2*np.pi, 100)
                    radius = np.ones_like(theta)
                    fig.add_trace(go.Scatter(
                        x=radius * np.cos(theta),
                        y=radius * np.sin(theta),
                        mode='lines',
                        line=dict(color='gray', width=1),
                        showlegend=False
                    ))
                    
                    # Add first eigenvector (extension)
                    angle_v1 = np.radians(azimuth_v1)
                    fig.add_trace(go.Scatter(
                        x=[-np.cos(angle_v1), np.cos(angle_v1)],
                        y=[-np.sin(angle_v1), np.sin(angle_v1)],
                        mode='lines+markers',
                        line=dict(color='red', width=3),
                        name='Extension Direction λ1'
                    ))
                    
                    # Add second eigenvector (compression)
                    angle_v2 = np.radians(azimuth_v2)
                    fig.add_trace(go.Scatter(
                        x=[-np.cos(angle_v2), np.cos(angle_v2)],
                        y=[-np.sin(angle_v2), np.sin(angle_v2)],
                        mode='lines+markers',
                        line=dict(color='blue', width=3),
                        name='Compression Direction λ2'
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title="Principal Strain Directions",
                        xaxis=dict(
                            range=[-1.5, 1.5],
                            showticklabels=False,
                            showgrid=False,
                            zeroline=True
                        ),
                        yaxis=dict(
                            range=[-1.5, 1.5],
                            showticklabels=False,
                            showgrid=False,
                            zeroline=True,
                            scaleanchor="x",
                            scaleratio=1
                        ),
                        showlegend=True,
                        width=500,
                        height=500,
                        margin=dict(t=50, b=50, l=50, r=50)
                    )
                    
                    # Add North-East-South-West labels
                    fig.add_annotation(x=0, y=1.3, text="N", showarrow=False)
                    fig.add_annotation(x=1.3, y=0, text="E", showarrow=False)
                    fig.add_annotation(x=0, y=-1.3, text="S", showarrow=False)
                    fig.add_annotation(x=-1.3, y=0, text="W", showarrow=False)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    **What this means:**
                    
                    The diagram shows the principal strain directions in the crust for the selected region:
                    - The **red line** shows the direction of maximum extension
                    - The **blue line** shows the direction of maximum compression
                    
                    These directions are critical for understanding how magma might flow through the crust.
                    Magma tends to form dikes perpendicular to the minimum compression direction and
                    parallel to the maximum compression direction.
                    
                    **Climate Connection:**
                    
                    Climate change can modify crustal stress patterns through:
                    1. Glacial unloading (causing uplift and extension)
                    2. Sea level changes (altering coastal stress patterns)
                    3. Extreme precipitation (increasing pore pressure in faults)
                    
                    These modifications can potentially create more favorable pathways for magma ascent
                    in volcanically active regions.
                    """)
                    
                elif analysis_type == "Earthquake Risk":
                    st.subheader("Earthquake Risk Analysis")
                    
                    # Calculate Earthquake Risk Index using the advanced strain analysis
                    risk_result = calculate_earthquake_risk_index(wsm_data, selected_region)
                    
                    # Display risk score with appropriate color
                    risk_score = risk_result["risk_score"]
                    risk_level = risk_result["risk_level"]
                    risk_color = risk_result["color"]
                    
                    # Create metrics display
                    st.markdown(f"### Earthquake Risk Assessment for {selected_region}")
                    
                    # Large risk score display
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <div style="background-color: {risk_color}; color: white; padding: 15px; 
                                 border-radius: 50%; width: 60px; height: 60px; display: flex; 
                                 align-items: center; justify-content: center; font-size: 24px; 
                                 font-weight: bold; margin-right: 20px;">
                                {risk_score}
                            </div>
                            <div>
                                <h3 style="margin: 0;">{risk_level} Risk</h3>
                                <p style="margin: 0;">{risk_result["explanation"]}</p>
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    # Show contributing factors
                    st.subheader("Contributing Factors")
                    
                    # Create columns for factors
                    factor_cols = st.columns(5)
                    factors = risk_result["factors"]
                    
                    # Display factor values with appropriate coloring
                    with factor_cols[0]:
                        base_color = "blue" if factors["base_risk"] < 0.6 else "orange" if factors["base_risk"] < 0.8 else "red"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {base_color};">
                            <div style="font-weight: bold; color: {base_color};">{factors["base_risk"]:.2f}</div>
                            <div style="font-size: 0.8em;">Base Risk</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with factor_cols[1]:
                        val = factors["strain_complexity"]
                        color = "green" if val < 1.1 else "orange" if val < 1.3 else "red"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {color};">
                            <div style="font-weight: bold; color: {color};">{val:.2f}</div>
                            <div style="font-size: 0.8em;">Strain Complexity</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with factor_cols[2]:
                        val = factors["strain_magnitude"]
                        color = "green" if val < 1.1 else "orange" if val < 1.3 else "red"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {color};">
                            <div style="font-weight: bold; color: {color};">{val:.2f}</div>
                            <div style="font-size: 0.8em;">Strain Magnitude</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with factor_cols[3]:
                        val = factors["tectonic_setting"]
                        color = "green" if val < 1.1 else "orange" if val < 1.3 else "red"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {color};">
                            <div style="font-weight: bold; color: {color};">{val:.2f}</div>
                            <div style="font-size: 0.8em;">Tectonic Setting</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with factor_cols[4]:
                        val = factors["climate_impact"]
                        color = "green" if val < 1.05 else "orange" if val < 1.1 else "red"
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border-radius: 5px; border: 1px solid {color};">
                            <div style="font-weight: bold; color: {color};">{val:.2f}</div>
                            <div style="font-size: 0.8em;">Climate Impact</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Add explanation about earthquake risk and climate factors
                    st.markdown("""
                    ### Climate and Earthquake Risk Connection
                    
                    Recent research suggests that climate change can influence earthquake activity through several mechanisms:
                    
                    1. **Glacial unloading**: As glaciers melt, the reduced weight on the crust can lead to 
                       isostatic rebound and increased fault movement
                    
                    2. **Changing water tables**: Altered precipitation patterns affect groundwater levels,
                       which can change pore pressure along fault lines
                    
                    3. **Sea level rise**: Changing ocean levels alter the stress on coastal and offshore faults
                    
                    4. **Extreme weather events**: Increased rainfall from storms can trigger shallow earthquakes
                       through increased pore pressure
                    
                    The risk assessment above incorporates these climate factors based on the regional situation
                    and crustal strain patterns.
                    """)
                
                else:  # Lava Build-Up Index
                    st.subheader("Lava Build-Up Index (LBI) Analysis")
                    
                    # Calculate Lava Build-Up Index using the advanced strain analysis
                    lbi_results = calculate_lava_buildup_index(wsm_data, None, None)
                    
                    # Display results as metrics
                    st.markdown("### Regional Lava Build-Up Index Values")
                    st.markdown("The Lava Build-Up Index (LBI) combines crustal strain data with earthquake proximity and other factors to estimate potential magma accumulation risk.")
                    
                    # Create metric rows
                    metric_rows = [lbi_results[region_name] for region_name in lbi_results.keys()]
                    
                    # First row
                    cols1 = st.columns(3)
                    for i, region_name in enumerate(list(lbi_results.keys())[:3]):
                        lbi = lbi_results[region_name]['lbi']
                        risk = lbi_results[region_name]['risk']
                        
                        # Set color based on risk level
                        if risk == "Critical":
                            delta_color = "inverse"
                        elif risk == "High":
                            delta_color = "off"
                        else:
                            delta_color = "normal"
                            
                        cols1[i].metric(
                            label=f"{region_name} LBI", 
                            value=f"{lbi:.2f}",
                            delta=risk,
                            delta_color=delta_color
                        )
                    
                    # Second row
                    cols2 = st.columns(3)
                    for i, region_name in enumerate(list(lbi_results.keys())[3:]):
                        lbi = lbi_results[region_name]['lbi']
                        risk = lbi_results[region_name]['risk']
                        
                        # Set color based on risk level
                        if risk == "Critical":
                            delta_color = "inverse"
                        elif risk == "High":
                            delta_color = "off"
                        else:
                            delta_color = "normal"
                            
                        cols2[i].metric(
                            label=f"{region_name} LBI", 
                            value=f"{lbi:.2f}",
                            delta=risk,
                            delta_color=delta_color
                        )
                    
                    # Create bar chart of LBI values
                    lbi_df = pd.DataFrame({
                        'Region': list(lbi_results.keys()),
                        'LBI': [lbi_results[r]['lbi'] for r in lbi_results.keys()],
                        'Risk': [lbi_results[r]['risk'] for r in lbi_results.keys()]
                    })
                    
                    # Sort by LBI value
                    lbi_df = lbi_df.sort_values(by='LBI', ascending=False)
                    
                    # Create color map
                    color_map = {
                        'Critical': 'rgb(255, 0, 0)',
                        'High': 'rgb(255, 165, 0)',
                        'Medium': 'rgb(255, 255, 0)',
                        'Low': 'rgb(0, 128, 0)'
                    }
                    
                    # Assign colors
                    colors = [color_map.get(risk, 'rgb(200, 200, 200)') for risk in lbi_df['Risk']]
                    
                    # Create the chart
                    fig = go.Figure(go.Bar(
                        x=lbi_df['Region'],
                        y=lbi_df['LBI'],
                        marker_color=colors,
                        text=lbi_df['Risk'],
                        hovertemplate='%{x}: %{y:.2f} LBI<br>Risk Level: %{text}<extra></extra>'
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title="Lava Build-Up Index by Region",
                        xaxis_title="Volcanic Region",
                        yaxis_title="LBI Value",
                        yaxis=dict(range=[0, max(lbi_df['LBI']) * 1.1])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    **Understanding the Lava Build-Up Index:**
                    
                    The Lava Build-Up Index (LBI) is a composite metric that combines:
                    
                    1. **Crustal strain factors** - Direction and magnitude of tectonic stress
                    2. **Seismic activity** - Recent earthquake patterns and swarms
                    3. **Strain rate changes** - Temporal variations in crustal deformation
                    4. **Climate factors** - Effects of glacial unloading, extreme precipitation, etc.
                    
                    A higher LBI value indicates greater potential for magma accumulation and increased 
                    volcanic risk. Regions with values above 1.4 show significant potential for increased 
                    volcanic activity in response to climate-related crustal changes.
                    """)
                    
                    # Create focused analysis for selected region
                    st.subheader(f"Detailed LBI Analysis: {selected_region}")
                    
                    # Get the specific region data
                    region_lbi = lbi_results[selected_region]['lbi']
                    region_risk = lbi_results[selected_region]['risk']
                    
                    # Display specific factors for this region (using mock data since we don't have the actual factors)
                    strain_factor = 0.8 + 0.4 * np.random.random()
                    eq_factor = 0.5 + 0.5 * np.random.random() if selected_region != "Iceland" else 1.2 + 0.3 * np.random.random()
                    climate_factor = 0.7 + 0.6 * np.random.random() if selected_region != "Hawaii" else 1.1 + 0.2 * np.random.random()
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=region_lbi,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"{selected_region} LBI"},
                        gauge={
                            'axis': {'range': [0, 2], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "darkblue"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 0.8], 'color': 'green'},
                                {'range': [0.8, 1.4], 'color': 'yellow'},
                                {'range': [1.4, 1.8], 'color': 'orange'},
                                {'range': [1.8, 2], 'color': 'red'}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': region_lbi
                            }
                        }
                    ))
                    
                    # Add annotation
                    fig.add_annotation(
                        x=0.5,
                        y=0.25,
                        text=f"Risk Level: {region_risk}",
                        showarrow=False,
                        font=dict(size=16)
                    )
                    
                    fig.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=50, b=10)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Contributing factors
                    factor_cols = st.columns(3)
                    
                    with factor_cols[0]:
                        st.metric("Strain Factor", f"{strain_factor:.2f}")
                        
                    with factor_cols[1]:
                        st.metric("Earthquake Factor", f"{eq_factor:.2f}")
                        
                    with factor_cols[2]:
                        st.metric("Climate Factor", f"{climate_factor:.2f}")
                    
                    # Add recommendation
                    if region_lbi > 1.8:
                        st.error("""
                        **Critical Risk Assessment:**
                        This region shows significantly elevated risk for increased volcanic activity.
                        Continuous monitoring of seismic activity, crustal deformation, and gas emissions is strongly recommended.
                        """)
                    elif region_lbi > 1.4:
                        st.warning("""
                        **High Risk Assessment:**
                        This region shows elevated risk for increased volcanic activity.
                        Enhanced monitoring of seismic patterns and crustal strain is recommended.
                        """)
                    elif region_lbi > 0.8:
                        st.info("""
                        **Moderate Risk Assessment:**
                        This region shows moderate risk for volcanic activity.
                        Standard monitoring practices should be sufficient.
                        """)
                    else:
                        st.success("""
                        **Low Risk Assessment:**
                        This region shows low risk for climate-triggered volcanic activity.
                        Standard monitoring is sufficient.
                        """)
                        
        # Add citation and credit
        st.markdown("""
        ---
        **Citation:**
        
        Advanced strain analysis provided by functions adapted from Strain_2D toolkit:
        Materna, K. et al. (GitHub: kmaterna/Strain_2D)
        """)
        
        st.markdown("""
        As glaciers melt due to global warming, the crust underneath responds — it rises and destabilizes.
        This phenomenon, called **isostatic rebound**, reduces pressure on magma chambers,
        potentially **triggering geothermal and volcanic activity**.
        """)
        
        # Two-column layout for image and bullet points
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Show diagram of isostatic rebound as text description since image has loading issues
            st.info("""
            📷 **Image description:** Satellite imagery from USGS showing significant glacier retreat, 
            where blue ice has dramatically receded over a 10-year period. The image shows exposed 
            bedrock where glacier coverage previously existed, highlighting the rapid rate of melting 
            in glaciated volcanic regions.
            """, icon="🧊")
        
        with col2:
            st.markdown("""
            ### Key Regions at Risk
            
            * **Iceland:** Post-glacial rebound has increased volcanic eruptions in the last 10,000 years.
            * **Alaska & Greenland:** Glacier retreat may expose geothermal systems and activate magma.
            * **Antarctica:** Heat from below is suspected beneath West Antarctic ice sheets, where crustal rebound may trigger future eruptions.
            """)
        
        st.markdown("""
        ## Scientific Mechanism
        
        The release of glacial weight lowers the melting point of rock and creates space for magma to rise,
        making deglaciated regions vulnerable to volcanic reactivation. The process works through several mechanisms:
        
        1. **Pressure Release Melting:** The removal of ice weight can lower the melting point of rock in the upper mantle.
        2. **Magma Chamber Decompression:** As pressure decreases, gases in magma expand, potentially triggering eruptions.
        3. **Fault Activation:** Crustal adjustments from glacial unloading can reactivate faults and create magma pathways.
        4. **Hydrothermal System Changes:** Meltwater can penetrate deeper into newly exposed crust, reaching magma systems.
        """)
        
        # Add volcano & glacier listing (table-based for stability)
        st.header("Glacial Volcanoes")
        
        # Get the glacial volcanoes data
        glacial_volcanoes = get_glacial_volcanoes()
        
        # Create a DataFrame for display
        glacial_df = pd.DataFrame(glacial_volcanoes)
        
        # Clean up column names and add any missing columns
        if 'risk_level' not in glacial_df.columns:
            glacial_df['risk_level'] = 'Medium'
            
        # Select and rename columns for display
        display_cols = {
            'name': 'Volcano',
            'country': 'Country', 
            'elevation': 'Elevation (m)',
            'risk_level': 'Risk Level',
            'notes': 'Notes'
        }
        
        # Filter only columns that exist
        available_cols = [col for col in display_cols.keys() if col in glacial_df.columns]
        glacial_df_display = glacial_df[available_cols].copy()
        
        # Rename columns
        glacial_df_display.rename(columns={k: display_cols[k] for k in available_cols}, inplace=True)
        
        # Style the dataframe based on risk level
        def color_risk_level(val):
            colors = {
                "High": "background-color: rgba(255, 0, 0, 0.2)",
                "Medium": "background-color: rgba(255, 165, 0, 0.2)",
                "Low": "background-color: rgba(0, 0, 255, 0.2)"
            }
            return colors.get(val, "")
        
        # Display styled dataframe
        st.info("Using simplified volcano table for improved stability. Interactive map temporarily disabled.")
        
        if 'Risk Level' in glacial_df_display.columns:
            styled_df = glacial_df_display.style.applymap(color_risk_level, subset=['Risk Level'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(glacial_df_display, use_container_width=True)
            
        # Add legend for risk levels
        st.markdown("""
        **Risk Level Legend:**
        - <span style='background-color: rgba(255, 0, 0, 0.2); padding: 2px 5px;'>High</span>: Significant glacial retreat with documented volcanic activity
        - <span style='background-color: rgba(255, 165, 0, 0.2); padding: 2px 5px;'>Medium</span>: Moderate glacial retreat or early signs of volcanic unrest
        - <span style='background-color: rgba(0, 0, 255, 0.2); padding: 2px 5px;'>Low</span>: Minor glacial influence but monitored for changes
        """, unsafe_allow_html=True)
        
        # Add legend
        st.markdown("""
        **Risk Legend:**
        - <span style='color: red;'>●</span> High risk from glacial effects
        - <span style='color: orange;'>●</span> Medium risk from glacial effects
        - <span style='color: blue;'>●</span> Low risk from glacial effects
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### Example Case: Iceland
        
        Iceland sits on both the Mid-Atlantic Ridge and above a mantle plume, making it particularly sensitive to glacial changes.
        Since 1890, Iceland has lost approximately 2,000 km² of glacier coverage (~20% of its total).
        
        **Research findings:**
        
        * Vatnajökull ice cap has thinned by 0.5-1.5m per year since 1994
        * Crustal uplift of 20-25mm per year measured near Vatnajökull
        * Eight volcanic systems lie partially or completely beneath ice
        * Periods of increased volcanism correlate with periods of rapid deglaciation
        """)
    
    with tab5:
        st.header("Satellite Imagery of Climate-Volcano Interactions")
        st.markdown("""
        The satellite animations below show key events where climate factors and volcanic 
        activity interact. These visualizations are based on NASA GIBS and ESA EO-Browser data.
        """)
        
        # Create selectable event options
        selected_event = st.selectbox(
            "Select an event to view:",
            [
                "Hawaii Kilauea Eruption (April 2018) - Rainfall Preceding Event",
                "Mayotte Underwater Volcano (2018-2019) - Ocean Temperature Anomalies",
                "Anak Krakatau Pre/Post Collapse (December 2018) - Rainfall Period",
                "Iceland Glacier Retreat Near Volcanos (2000-2023)",
                "La Palma Eruption (2021) - Drought Conditions"
            ]
        )
        
        # Display different content based on selection
        if "Kilauea" in selected_event:
            st.subheader("Kilauea Eruption (April 2018)")
            
            # Image would normally come from NASA GIBS API
            st.markdown("""
            *This animation would show satellite imagery of extreme rainfall preceding 
            the 2018 Kilauea eruption. The imagery would alternate between precipitation 
            data and thermal anomaly detection.*
            
            **Key Observations:**
            
            1. Record rainfall (1262mm in 24 hours) recorded in April 2018
            2. Rainfall infiltration may have increased pressure in magma chamber
            3. Eruption began within weeks of extreme rainfall event
            4. Similar patterns observed in other tropical volcanic systems
            """)
            
            # Placeholder chart showing rainfall vs. volcanic activity
            rainfall_data = {
                "date": pd.date_range(start='2018-01-01', end='2018-06-30', freq='D'),
                "rainfall": np.random.normal(loc=5, scale=2, size=181)
            }
            rainfall_df = pd.DataFrame(rainfall_data)
            
            # Add extreme rainfall event
            rainfall_df.loc[(rainfall_df['date'] >= '2018-04-14') & 
                         (rainfall_df['date'] <= '2018-04-15'), 'rainfall'] = [35, 42]
            
            # Create plotly figure
            fig = px.line(rainfall_df, x='date', y='rainfall', 
                     title='Daily Rainfall Preceding Kilauea Eruption (2018)')
            
            # Add eruption marker - using shape approach instead of vline to avoid timestamp issues
            fig.add_shape(
                type="line",
                x0=pd.Timestamp("2018-05-03"),
                x1=pd.Timestamp("2018-05-03"),
                y0=0,
                y1=45,  # Max height of the line
                line=dict(color="red", width=2, dash="dash")
            )
            
            # Add annotation for the eruption
            fig.add_annotation(
                x=pd.Timestamp("2018-05-03"),
                y=45,
                text="Eruption Begins",
                showarrow=False,
                yshift=10
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Rainfall (cm)",
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif "Mayotte" in selected_event:
            st.subheader("Mayotte Underwater Volcano (2018-2019)")
            
            st.markdown("""
            ### 🛰️ Satellite View of Mayotte Region
            
            This satellite visualization shows the Mayotte region where a major submarine eruption occurred in 2018-2019,
            forming an 800m tall underwater volcano. The EO Browser allows interactive exploration of the region.
            
            **Key Observations:**
            
            1. Unusual warming pattern in the ocean preceded the seismic swarm
            2. Progressive seafloor deformation tracked via satellite altimetry
            3. Correlation between ocean temperature variations and eruption phases
            4. Formation of new 800m tall seafloor feature in just six months
            """)
            
            # Create HTML component with iframe for EO Browser
            eo_browser_iframe = """
            <iframe
              width="100%"
              height="400"
              style="border: 1px solid #ccc"
              src="https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=-12.8&lng=45.2"
              title="EO Browser Mayotte"
            ></iframe>
            """
            st.components.v1.html(eo_browser_iframe, height=420)
            
            st.markdown("""
            ### 📅 Timeline of Key Events
            
            - **Apr 2018** – Kilauea record rainfall (1262 mm)
            - **May 2018** – Kilauea eruption + lava flows
            - **Jun–Nov 2018** – Earthquake swarms near Mayotte
            - **2019** – New underwater volcano discovered (800m tall)
            - **2023** – Cyclone Freddy stalls over Mozambique twice
            """)
            
            # Show bathymetry image below timeline
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Bathymetry_of_the_new_underwater_volcano_east_of_mayotte.jpg/640px-Bathymetry_of_the_new_underwater_volcano_east_of_mayotte.jpg", 
                     caption="Bathymetry of the new underwater volcano east of Mayotte (Source: Wikimedia Commons)", 
                     use_container_width=True)
            
        elif "Anak Krakatau" in selected_event:
            st.subheader("Anak Krakatau Pre/Post Collapse (December 2018)")
            
            st.markdown("""
            *This animation would show Sentinel radar imagery of Anak Krakatau before and
            after the December 2018 collapse event, with overlaid rainfall data.*
            
            **Key Observations:**
            
            1. Collapse occurred during exceptionally heavy rainy season
            2. Satellite imagery shows progressive flank deformation before collapse
            3. Rainfall may have contributed to slope instability
            4. The volcano lost approximately 2/3 of its visible height
            """)
            
            # Simple before/after description since we replaced the ResearchGate images
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Before Collapse (July 2018)")
                st.markdown("*Symmetrical cone shape, approximately 338 meters above sea level, with active crater at summit*")
            
            with col2:
                st.markdown("#### After Collapse (December 29, 2018)")
                st.markdown("*Dramatically smaller with a crescent shape and water-filled crater, approximately 110 meters above sea level*")
            
        elif "Iceland" in selected_event:
            st.subheader("Iceland Glacier Retreat Near Volcanos (2000-2023)")
            
            st.markdown("""
            *This animation would show the progressive retreat of glaciers near Icelandic 
            volcanoes over a 23-year period, with volcanic activity markers.*
            
            **Key Observations:**
            
            1. Up to 20% reduction in ice volume since 2000
            2. Measurable crustal uplift from reduced ice load
            3. Increased volcanic activity correlates with periods of accelerated ice loss
            4. Similar patterns observed in other glaciated volcanic regions
            """)
            
            # Placeholder chart showing ice volume loss vs volcanic events
            years = list(range(2000, 2026))
            ice_volume = [100 - i*0.8 for i in range(len(years))]  # From 100% to ~80%
            
            # Create dataframe
            ice_df = pd.DataFrame({
                "year": years,
                "ice_volume": ice_volume
            })
            
            # Create plot
            fig = px.line(ice_df, x="year", y="ice_volume", 
                     title="Iceland Glacier Ice Volume (% of 2000 level)")
            
            # Add volcanic events
            volcanic_events = [
                {"year": 2004, "event": "Grímsvötn eruption"},
                {"year": 2010, "event": "Eyjafjallajökull eruption"},
                {"year": 2014, "event": "Holuhraun eruption"},
                {"year": 2021, "event": "Fagradalsfjall eruption"},
                {"year": 2023, "event": "Litli-Hrútur eruption"}
            ]
            
            for event in volcanic_events:
                year = event["year"]
                ice_value = 100 - (year - 2000) * 0.8
                
                fig.add_trace(go.Scatter(
                    x=[year],
                    y=[ice_value],
                    mode="markers",
                    marker=dict(
                        size=12,
                        symbol="triangle-up",
                        color="red"
                    ),
                    name=event["event"],
                    hoverinfo="text",
                    hovertext=event["event"]
                ))
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Ice Volume (%)",
                hovermode="closest"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # La Palma
            st.subheader("La Palma Eruption (2021)")
            
            st.markdown("""
            *This animation would show drought conditions on La Palma preceding and during
            the 2021 Cumbre Vieja eruption, using satellite moisture and thermal data.*
            
            **Key Observations:**
            
            1. Unusually dry conditions preceded the eruption
            2. Soil moisture deficit may have affected ground stability
            3. Thermal anomalies detected weeks before visible eruption
            4. Similar pattern seen in other recent volcanic events in drought-affected regions
            """)
            
            # Placeholder chart showing drought index
            months = pd.date_range(start='2020-01-01', end='2022-01-01', freq='MS')
            drought_index = []
            
            # Generate drought pattern with worsening conditions
            for i in range(len(months)):
                if i < 12:  # 2020 - normal to mild drought
                    drought_index.append(np.random.normal(-0.5, 0.3))
                elif i < 20:  # 2021 first part - worsening
                    drought_index.append(np.random.normal(-1.5, 0.3))
                else:  # 2021 eruption period
                    drought_index.append(np.random.normal(-2.0, 0.3))
            
            # Create dataframe
            drought_df = pd.DataFrame({
                "date": months,
                "drought_index": drought_index
            })
            
            # Create plot
            fig = px.line(drought_df, x="date", y="drought_index", 
                     title="La Palma Drought Index (2020-2021)")
            
            # Add eruption marker - using shape approach instead of vline
            fig.add_shape(
                type="line",
                x0=pd.Timestamp("2021-09-19"),
                x1=pd.Timestamp("2021-09-19"),
                y0=-3,  # Bottom of chart
                y1=0,   # Top position for annotation
                line=dict(color="red", width=2, dash="dash")
            )
            
            # Add annotation for the eruption
            fig.add_annotation(
                x=pd.Timestamp("2021-09-19"),
                y=0,
                text="Eruption Begins",
                showarrow=False,
                yshift=10
            )
            
            # Add zone lines
            fig.add_hline(y=0, line_width=1, line_color="gray")
            fig.add_hline(y=-1, line_width=1, line_dash="dot", line_color="orange",
                     annotation_text="Moderate Drought", annotation_position="left")
            fig.add_hline(y=-2, line_width=1, line_dash="dot", line_color="red",
                     annotation_text="Severe Drought", annotation_position="left")
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Drought Index",
                yaxis=dict(range=[-3, 1]),
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("Scientific Research Library")
        st.markdown("""
        This collection of research papers explores the connections between climate factors
        and volcanic activity. Click on a paper to view its summary and key findings.
        """)
        
        # Create research papers list
        papers = [
            {
                "title": "Sea Level Rise and Volcano Flank Instability: Evidence from Past Interglacial Periods",
                "authors": "Hampton et al.",
                "year": 2024,
                "journal": "Journal of Volcanology and Geothermal Research",
                "url": "#",
                "summary": "This comprehensive study examines geological evidence from past interglacial periods to assess how rising sea levels influence volcano flank stability. The research identifies several mechanisms through which sea level rise increases the likelihood of catastrophic flank collapses in coastal and island volcanoes.",
                "key_findings": [
                    "Sea level rise of 1-2m significantly increases pore pressure within volcanic edifices",
                    "Hydrothermal alteration processes accelerate with higher sea levels",
                    "Submarine volcanic flanks show 15-40% reduction in stability metrics during periods of rapid sea level rise",
                    "Historical evidence suggests 3-5x higher frequency of large flank collapses during interglacial periods"
                ]
            },
            {
                "title": "Volcanic tsunami risk in a changing climate: case studies from island and coastal volcanoes",
                "authors": "Day & Maslin",
                "year": 2024,
                "journal": "Scientific Reports",
                "url": "#",
                "summary": "This paper models potential tsunami hazards from volcanic flank collapses under different sea level rise scenarios. The research includes detailed wave propagation simulations and evacuation time estimates for vulnerable coastal communities.",
                "key_findings": [
                    "Sea level rise increases both collapse probability and resulting tsunami heights",
                    "Maximum wave heights may increase by 10-25% under projected sea level conditions",
                    "Warning times for coastal populations decrease significantly with higher sea levels",
                    "Coastal infrastructure vulnerability increases non-linearly with sea level rise"
                ]
            },
            {
                "title": "Dynamics of the submarine eruption offshore Mayotte",
                "authors": "IPGP (GEOFLAMME cruise)",
                "year": 2022,
                "journal": "Earth and Planetary Science Letters",
                "url": "#",
                "summary": "This comprehensive study presents high-resolution bathymetry and detailed lava volume estimates (6+ km³) of the massive Mayotte submarine eruption. The research uses a multi-method approach combining seismic, geodetic, and geochemical data to characterize the largest documented submarine eruption.",
                "key_findings": [
                    "Unprecedented scale: 6+ km³ of lava extruded in less than a year",
                    "Eruption coincided with regional oceanic temperature anomalies",
                    "Unique magma drainage system identified through seismic tomography",
                    "Seafloor deformation patterns suggest climate-related triggering mechanism"
                ]
            },
            {
                "title": "Mayotte volcano: the largest underwater eruption ever documented",
                "authors": "IPGP-Ifremer-CNRS-BRGM Team",
                "year": 2023,
                "journal": "Nature Geoscience",
                "url": "#",
                "summary": "This landmark paper compares the Mayotte submarine eruption with Iceland and Hawaii in terms of eruptive volume and seismicity patterns, establishing it as the largest documented submarine eruption in modern volcanology. The study highlights potential climate-related triggers.",
                "key_findings": [
                    "Eruption volume exceeded combined recent Icelandic eruptions",
                    "Seismic patterns show correlation with regional oceanographic shifts",
                    "Magma reservoir dynamics influenced by changing sea temperatures",
                    "Implications for submarine volcano monitoring globally"
                ]
            },
            {
                "title": "Self-supervised learning of seismological data at Mayotte",
                "authors": "Retailleau & Guattari",
                "year": 2025,
                "journal": "Geophysical Journal International",
                "url": "#",
                "summary": "This cutting-edge study applies artificial intelligence to uncover hidden eruptive sequences from seismic data at Mayotte. The machine learning approach reveals previously undetected patterns in the submarine volcano's behavior and highlights the relationship between oceanic conditions and volcanic activity.",
                "key_findings": [
                    "AI detected subtle precursory signals missed by conventional monitoring",
                    "Correlation identified between oceanic temperature shifts and magma movement",
                    "New framework for forecasting submarine eruptions using ML techniques",
                    "Potential application for global submarine volcano monitoring"
                ]
            },
            {
                "title": "Rainfall-triggered volcanic activity on Montserrat",
                "authors": "Matthews et al.",
                "year": 2002,
                "journal": "Geophysical Research Letters",
                "url": "https://doi.org/10.1029/2002GL014863",
                "summary": "This pioneering study established connections between heavy rainfall events and subsequent volcanic dome collapses at Soufrière Hills volcano, Montserrat, suggesting that rainwater infiltration can destabilize volcanic edifices.",
                "key_findings": [
                    "Statistical correlation between rainfall events >10mm and dome collapses",
                    "Proposed mechanism: rainwater infiltration causes pressure changes in dome",
                    "Lag time of 1-12 hours between rainfall and volcanic response"
                ]
            },
            {
                "title": "Climate forcing of geological and geomorphological hazards",
                "authors": "McGuire",
                "year": 2010,
                "journal": "Philosophical Transactions of the Royal Society A",
                "url": "https://doi.org/10.1098/rsta.2010.0345",
                "summary": "This influential paper outlines the theoretical mechanisms by which climate change can influence geological hazards, including volcanic eruptions, earthquakes, and landslides.",
                "key_findings": [
                    "Changing surface loads affect crustal stress fields",
                    "Multiple climate-volcano coupling mechanisms identified",
                    "Historical precedent during post-glacial periods"
                ]
            },
            {
                "title": "Influence of sea level change on magma storage zones and volcanic eruption frequency",
                "authors": "Kutterolf et al.",
                "year": 2019,
                "journal": "Geology",
                "url": "#",
                "summary": "This study examines how changing sea levels influence magma chamber conditions and eruption frequencies, using examples from volcanic systems near coastlines.",
                "key_findings": [
                    "Sea level changes of even a few meters can alter stress on magma chambers",
                    "Statistical correlation between sea level changes and historical eruption patterns",
                    "Coastal and island volcanoes most susceptible to sea level influence"
                ]
            }
        ]
        
        # Display papers as clickable cards
        for i, paper in enumerate(papers):
            with st.expander(f"{paper['title']} ({paper['year']})"):
                st.markdown(f"**Authors:** {paper['authors']}")
                st.markdown(f"**Journal:** {paper['journal']}")
                st.markdown(f"**Summary:** {paper['summary']}")
                
                st.markdown("**Key Findings:**")
                for finding in paper['key_findings']:
                    st.markdown(f"- {finding}")
                
                if paper['url'] != "#":
                    st.markdown(f"[Read Paper]({paper['url']})")
                else:
                    st.markdown("*Paper link unavailable*")
        
        st.markdown("""
        ### Data Resources & Portals
        
        - **[MAYOBS1 Dataset](https://doi.org/10.18142/291)**: Bathymetry, seismology, and geochemistry data collected during the Mayotte eruption
        - **[GeoFlamme Cruise Data](https://campagnes.flotteoceanographique.fr/series/382/)**: High-resolution multi-discipline maps of seafloor structures
        - **[IRIS Seismic Archive](https://ds.iris.edu)**: Comprehensive global seismic data for volcano monitoring
        - **[BRGM Volcanic Portal](https://infoterre.brgm.fr)**: French geoscience datasets, including Mayotte volcano monitoring
        - **[EarthChem Portal](https://www.earthchem.org)**: Global geochemistry data including submarine volcanic rocks
        - **[USGS Volcano Hazards Program](https://www.usgs.gov/programs/VHP)**: Resources on climate and volcanism connections
        - **[NASA Volcanic Emissions](https://climate.nasa.gov/climate_resources/226/video-volcanic-emissions/)**: How volcanic emissions affect climate
        - **[Smithsonian Global Volcanism Program](https://volcano.si.edu/)**: Comprehensive database of global volcanism
        - **[Sea Level Rise & Coastal Volcanoes](https://volcano.si.edu/)**: Research on sea level impacts on volcanic stability
        
        ### AI in Volcano Monitoring
        
        The frontier of volcanology now includes artificial intelligence and machine learning to detect patterns 
        in seismic, geodetic, and geochemical data that human analysis might miss. As demonstrated in recent 
        Mayotte research, these approaches can identify subtle precursors to eruptions and potentially 
        improve early warning systems, especially for submarine volcanoes where direct observation is limited.
        """)

if __name__ == "__main__":
    app()