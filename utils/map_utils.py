import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster, HeatMap, MeasureControl
from utils.risk_assessment import (
    generate_risk_levels,
    generate_risk_heatmap_data,
    calculate_radius_from_risk
)
from utils.web_scraper import (
    get_so2_data,
    get_volcanic_ash_data,
    get_radon_data
)

def create_volcano_map(volcano_df, include_monitoring_data=False):
    """
    Create an interactive folium map with volcano markers and optional monitoring data
    
    Args:
        volcano_df (pd.DataFrame): DataFrame containing volcano data
        include_monitoring_data (bool): Whether to include SO2, ash, and radon monitoring data
        
    Returns:
        folium.Map: An interactive map with volcano markers and data layers
    """
    # Calculate center of map based on data
    if len(volcano_df) > 0:
        center_lat = volcano_df['latitude'].mean()
        center_lng = volcano_df['longitude'].mean()
    else:
        # Default center (world view)
        center_lat, center_lng = 20.0, 0.0
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=2,
        tiles="OpenStreetMap"
    )
    
    # Add tile layer control with proper attributions
    folium.TileLayer(
        'Stamen Terrain',
        attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors'
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        attr='Map tiles by <a href="https://carto.com/">CartoDB</a>, under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    # Add NASA GIBS satellite imagery for atmospheric SO2 (if available)
    wms_layer = folium.WmsTileLayer(
        url="https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi",
        layers="AIRS_SO2_Total_Column_Day",
        name="NASA AIRS SO2 Column",
        fmt="image/png",
        transparent=True,
        overlay=True,
        opacity=0.6,
        shown=False,
        attr="NASA Earth Observing System Data and Information System (EOSDIS)"
    )
    wms_layer.add_to(m)
    
    # Add measurement tool
    MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    
    # If monitoring data is requested, add the data layers
    if include_monitoring_data:
        try:
            # Create more specific feature groups for different types of monitoring data
            so2_layer = folium.FeatureGroup(name="SO2 Emissions", show=True)
            ash_layer = folium.FeatureGroup(name="Volcanic Ash", show=True)
            radon_layer = folium.FeatureGroup(name="Radon Gas", show=True)
            
            # Color maps for concentration levels
            so2_colors = {
                'low': '#add8e6',      # Light blue
                'moderate': '#4169e1',  # Royal blue
                'high': '#800080',      # Purple
                'very_high': '#9400d3'  # Dark violet
            }
            
            ash_colors = {
                'low': '#c0c0c0',      # Silver
                'moderate': '#808080',  # Gray
                'high': '#696969',      # DimGray
                'very_high': '#2f4f4f'  # DarkSlateGray
            }
            
            radon_colors = {
                'normal': '#98fb98',    # Pale green
                'slight': '#90ee90',    # Light green
                'elevated': '#32cd32',  # Lime green
                'high': '#228b22'       # Forest green
            }
            
            # Get SO2 data
            so2_data = get_so2_data()
            if not so2_data.empty:
                # Add SO2 markers with proper concentration-based visualization
                for _, emission in so2_data.iterrows():
                    if 'latitude' in emission and 'longitude' in emission:
                        # Determine color and radius based on concentration
                        concentration = emission.get('so2_concentration', 0)
                        
                        if concentration > 80:
                            so2_color = so2_colors['very_high']
                            so2_radius = 12
                            level_text = "Very High"
                        elif concentration > 60:
                            so2_color = so2_colors['high']
                            so2_radius = 10
                            level_text = "High"
                        elif concentration > 40:
                            so2_color = so2_colors['moderate']
                            so2_radius = 8
                            level_text = "Moderate"
                        else:
                            so2_color = so2_colors['low']
                            so2_radius = 6
                            level_text = "Low"
                        
                        # Create detailed popup for SO2 emission
                        so2_popup_html = f"""
                        <div style="font-family: Arial; width: 250px;">
                            <h3 style="color: #333; margin-bottom: 10px;">SO<sub>2</sub> Emission</h3>
                            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                                <p style="margin: 5px 0;"><b>Concentration:</b> <span style="color: {so2_color};">{level_text}</span> ({concentration:.1f})</p>
                                <p style="margin: 5px 0;"><b>Volcano:</b> {emission.get('volcano_name', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Detected:</b> {emission.get('acq_date', 'Unknown')}</p>
                                """
                        
                        # Add type-specific details
                        emission_type = emission.get('emission_type', '')
                        if emission_type == 'Volcanic':
                            so2_popup_html += f"""
                                <p style="margin: 5px 0;"><b>Emission Rate:</b> {emission.get('emission_rate_tons_day', 'Unknown')} tons/day</p>
                            """
                        
                        # Add source information
                        so2_popup_html += f"""
                                <p style="margin: 5px 0;"><b>Source:</b> {emission.get('source', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Type:</b> {emission.get('detection_type', 'Unknown')}</p>
                            </div>
                            <p style="font-size: 0.8em; color: #666; font-style: italic;">Sulfur dioxide (SO<sub>2</sub>) is a key indicator of volcanic activity.</p>
                        </div>
                        """
                        
                        # Add marker to SO2 layer with enhanced styling
                        folium.CircleMarker(
                            location=[emission['latitude'], emission['longitude']],
                            radius=so2_radius,
                            color=so2_color,
                            fill=True,
                            fill_color=so2_color,
                            fill_opacity=0.7,
                            weight=2,
                            popup=folium.Popup(so2_popup_html, max_width=300),
                            tooltip=f"{emission.get('volcano_name', 'SO2')}: {level_text}"
                        ).add_to(so2_layer)
            
            # Get volcanic ash data
            ash_data = get_volcanic_ash_data()
            if not ash_data.empty:
                # Add ash cloud markers with enhanced visualization
                for _, ash in ash_data.iterrows():
                    if 'latitude' in ash and 'longitude' in ash:
                        # Determine color and radius based on concentration or ash height
                        concentration = ash.get('ash_concentration', 0)
                        ash_height = ash.get('ash_height_ft', 0)
                        
                        if concentration > 80 or ash_height > 25000:
                            ash_color = ash_colors['very_high']
                            ash_radius = 12
                            level_text = "Very High"
                        elif concentration > 60 or ash_height > 20000:
                            ash_color = ash_colors['high']
                            ash_radius = 10
                            level_text = "High"
                        elif concentration > 40 or ash_height > 15000:
                            ash_color = ash_colors['moderate']
                            ash_radius = 8
                            level_text = "Moderate"
                        else:
                            ash_color = ash_colors['low']
                            ash_radius = 6
                            level_text = "Low"
                        
                        # Create detailed popup with more ash information
                        ash_popup_html = f"""
                        <div style="font-family: Arial; width: 250px;">
                            <h3 style="color: #333; margin-bottom: 10px;">Volcanic Ash</h3>
                            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                                <p style="margin: 5px 0;"><b>Concentration:</b> <span style="color: {ash_color};">{level_text}</span></p>
                                <p style="margin: 5px 0;"><b>Volcano:</b> {ash.get('volcano_name', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Advisory Time:</b> {ash.get('advisory_time', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Ash Height:</b> {ash.get('ash_height_ft', 'Unknown')} ft</p>
                                <p style="margin: 5px 0;"><b>Direction:</b> {ash.get('ash_direction', 'Unknown')}</p>
                        """
                        
                        # Add type-specific details
                        data_type = ash.get('data_type', '')
                        if data_type == 'Forecast':
                            ash_popup_html += f"""
                                <p style="margin: 5px 0;"><b>Forecast Hours:</b> {ash.get('forecast_hours', 'Unknown')} hours</p>
                            """
                        elif data_type == 'Satellite':
                            ash_popup_html += f"""
                                <p style="margin: 5px 0;"><b>Plume Length:</b> {ash.get('plume_length_km', 'Unknown')} km</p>
                                <p style="margin: 5px 0;"><b>Satellite:</b> {ash.get('satellite', 'Unknown')}</p>
                            """
                        
                        # Add source information
                        ash_popup_html += f"""
                                <p style="margin: 5px 0;"><b>Source:</b> {ash.get('source', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Type:</b> {ash.get('data_type', 'Unknown')}</p>
                            </div>
                            <p style="font-size: 0.8em; color: #666; font-style: italic;">Volcanic ash presents hazards to aviation and public health.</p>
                        </div>
                        """
                        
                        # Add marker with improved styling
                        folium.CircleMarker(
                            location=[ash['latitude'], ash['longitude']],
                            radius=ash_radius,
                            color=ash_color,
                            fill=True,
                            fill_color=ash_color,
                            fill_opacity=0.7,
                            weight=2,
                            popup=folium.Popup(ash_popup_html, max_width=300),
                            tooltip=f"Ash: {ash.get('volcano_name', 'Unknown')} ({level_text})"
                        ).add_to(ash_layer)
            
            # Get radon data
            radon_data = get_radon_data()
            if not radon_data.empty:
                # Add radon measurement markers with enhanced visualization
                for _, radon in radon_data.iterrows():
                    if 'latitude' in radon and 'longitude' in radon:
                        # Determine color and radius based on radon level and anomaly
                        radon_level = radon.get('radon_level_bq_m3', 0)
                        anomaly_percent = radon.get('anomaly_percent', 0)
                        status = radon.get('status', '')
                        
                        if 'Highly' in status or anomaly_percent > 90:
                            radon_color = radon_colors['high']
                            radon_radius = 10
                            level_text = "Highly Elevated"
                        elif 'Elevated' in status or anomaly_percent > 60:
                            radon_color = radon_colors['elevated']
                            radon_radius = 8
                            level_text = "Elevated"
                        elif 'Slightly' in status or anomaly_percent > 30:
                            radon_color = radon_colors['slight']
                            radon_radius = 6
                            level_text = "Slightly Elevated"
                        else:
                            radon_color = radon_colors['normal']
                            radon_radius = 5
                            level_text = "Normal"
                        
                        # Create detailed popup for radon measurements
                        radon_popup_html = f"""
                        <div style="font-family: Arial; width: 250px;">
                            <h3 style="color: #333; margin-bottom: 10px;">Radon Gas Monitoring</h3>
                            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                                <p style="margin: 5px 0;"><b>Status:</b> <span style="color: {radon_color};">{level_text}</span></p>
                                <p style="margin: 5px 0;"><b>Station:</b> {radon.get('station_id', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Volcano:</b> {radon.get('volcano_name', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Radon Level:</b> {radon_level} Bq/m³</p>
                                <p style="margin: 5px 0;"><b>Baseline:</b> {radon.get('baseline_bq_m3', 'Unknown')} Bq/m³</p>
                                <p style="margin: 5px 0;"><b>Anomaly:</b> +{anomaly_percent}%</p>
                                <p style="margin: 5px 0;"><b>Measurement:</b> {radon.get('measurement_time', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Source:</b> {radon.get('source', 'Unknown')}</p>
                                <p style="margin: 5px 0;"><b>Method:</b> {radon.get('monitoring_method', 'Unknown')}</p>
                            </div>
                            <p style="font-size: 0.8em; color: #666; font-style: italic;">Radon gas (²²²Rn) increases can precede volcanic activity.</p>
                        </div>
                        """
                        
                        # Add marker with improved styling
                        folium.CircleMarker(
                            location=[radon['latitude'], radon['longitude']],
                            radius=radon_radius,
                            color=radon_color,
                            fill=True,
                            fill_color=radon_color,
                            fill_opacity=0.7,
                            weight=2,
                            popup=folium.Popup(radon_popup_html, max_width=300),
                            tooltip=f"Radon: {radon.get('station_id', 'Unknown')} ({level_text})"
                        ).add_to(radon_layer)
            
            # Add the layers to the map
            so2_layer.add_to(m)
            ash_layer.add_to(m)
            radon_layer.add_to(m)
            
            # Add a legend for the monitoring data
            legend_html = """
            <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 180px; height: 150px; 
                border: 2px solid grey; z-index: 9999; background-color: white;
                padding: 8px; font-size: 14px;">
                <h4 style="margin-top: 0;">Monitoring Data</h4>
                <div style="display: flex; align-items: center; margin: 3px;">
                    <span style="background: #9400d3; width: 15px; height: 15px; display: inline-block; margin-right: 5px; border-radius: 50%;"></span>
                    <span>SO<sub>2</sub> (High)</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px;">
                    <span style="background: #696969; width: 15px; height: 15px; display: inline-block; margin-right: 5px; border-radius: 50%;"></span>
                    <span>Ash Cloud</span>
                </div>
                <div style="display: flex; align-items: center; margin: 3px;">
                    <span style="background: #228b22; width: 15px; height: 15px; display: inline-block; margin-right: 5px; border-radius: 50%;"></span>
                    <span>Radon Station</span>
                </div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))
            
        except Exception as e:
            st.error(f"Error loading monitoring data: {str(e)}")
    
    # Create a marker cluster group for volcanoes
    marker_cluster = MarkerCluster(name="Volcanoes").add_to(m)
    
    # Add volcano markers with enhanced visualization
    for idx, volcano in volcano_df.iterrows():
        # Define icon color based on alert level and add more alert levels for warnings
        alert_level = volcano.get('alert_level', 'Unknown')
        
        # Extended alert level color scheme
        icon_color = {
            'Normal': 'green',
            'Advisory': 'beige',
            'Yellow': 'orange',
            'Orange': 'orange',
            'Watch': 'orange',
            'Red': 'red',
            'Warning': 'red',
            'Eruption': 'darkred',
            'Erupting': 'darkred',
            'Major': 'darkred',
            'Unknown': 'lightgray'
        }.get(alert_level, 'lightgray')
        
        # Icon based on volcano type/status
        icon_type = 'fire'
        if 'Erupting' in alert_level or 'Eruption' in alert_level or 'Major' in alert_level:
            icon_type = 'exclamation-triangle'
        elif 'glacier' in str(volcano.get('type', '')).lower():
            icon_type = 'snowflake-o'
        elif 'submarine' in str(volcano.get('type', '')).lower():
            icon_type = 'ship'
        elif 'caldera' in str(volcano.get('type', '')).lower():
            icon_type = 'dot-circle-o'
            
        # Create enhanced popup HTML
        popup_html = create_popup_html(volcano)
        
        # Create marker with proper color and icon
        marker = folium.Marker(
            location=[volcano['latitude'], volcano['longitude']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{volcano['name']} ({alert_level})",
            icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
        )
        
        # Add click event JavaScript to update Streamlit session state
        marker.add_to(marker_cluster).add_child(
            folium.Element(
                f"""
                <script>
                    var el = document.getElementsByClassName('leaflet-marker-icon leaflet-zoom-animated leaflet-interactive')[{idx}];
                    el.addEventListener('click', function() {{
                        // Send data to Streamlit
                        var volcano = {volcano.to_json()};
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: volcano
                        }}, '*');
                    }});
                </script>
                """
            )
        )
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_popup_html(volcano):
    """
    Create HTML content for the volcano popup with professional styling
    
    Args:
        volcano (pd.Series): Series containing volcano data
        
    Returns:
        str: HTML content for the popup
    """
    # Enhanced alert level with color scale
    alert_level = volcano.get('alert_level', 'Unknown')
    alert_color = {
        'Normal': '#4caf50',      # Green
        'Advisory': '#ffeb3b',    # Yellow
        'Yellow': '#ffeb3b',      # Yellow
        'Orange': '#ff9800',      # Orange
        'Watch': '#ff9800',       # Orange
        'Red': '#f44336',         # Red
        'Warning': '#f44336',     # Red
        'Eruption': '#b71c1c',    # Dark Red
        'Erupting': '#b71c1c',    # Dark Red
        'Major': '#b71c1c',       # Dark Red
        'Unknown': '#9e9e9e'      # Gray
    }.get(alert_level, '#9e9e9e')
    
    # Monitoring indicators with modern SVG icons instead of emojis
    has_insar = volcano.get('has_insar', False)
    has_so2 = volcano.get('has_so2', False)
    has_lava = volcano.get('has_lava', False)
    
    # Get additional volcano properties with fallbacks
    country = volcano.get('country', 'Unknown')
    volcano_type = volcano.get('type', 'Unknown')
    elevation = volcano.get('elevation', 'Unknown')
    last_eruption = volcano.get('last_eruption', 'Unknown')
    population_5km = volcano.get('population_5km', 'N/A')
    population_10km = volcano.get('population_10km', 'N/A')
    population_30km = volcano.get('population_30km', 'N/A')
    population_100km = volcano.get('population_100km', 'N/A')
    
    # Define monitoring SVG icons
    insar_icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1976d2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4.5h18"></path><path d="M5 4.5a9.16 9.16 0 0 1-.5 5.24"></path><path d="M7 4.5a5.89 5.89 0 0 0 .5 5.24"></path><path d="M4.24 10.24a9.45 9.45 0 0 0 7.5 2.75"></path><circle cx="14.5" cy="13" r="4"></circle><path d="m17 15.5 3.5 3.5"></path></svg>'
    so2_icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#673ab7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15a6 6 0 0 0 12 0"></path><path d="M15 15a6 6 0 0 0 12 0"></path><path d="M3 9a6 6 0 0 1 12 0"></path><path d="M15 9a6 6 0 0 1 12 0"></path></svg>'
    lava_icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f44336" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>'
    
    # Construct HTML with professional styling
    html = f"""
    <div style="font-family: Arial, sans-serif; width: 320px;">
        <div style="background-color: #f5f5f5; padding: 10px; border-left: 5px solid {alert_color}; margin-bottom: 10px;">
            <h3 style="margin-top: 0; margin-bottom: 5px; color: #333;">{volcano['name']}</h3>
            <div style="color: #666; font-size: 0.9em; margin-bottom: 5px;">{country} • {volcano_type}</div>
            <div style="display: inline-block; padding: 3px 8px; border-radius: 3px; background-color: {alert_color}; color: white; font-weight: bold; font-size: 0.8em;">
                {alert_level}
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 5px 0; font-weight: bold; width: 40%;">Elevation</td>
                    <td style="padding: 5px 0;">{elevation} m</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 5px 0; font-weight: bold;">Last Eruption</td>
                    <td style="padding: 5px 0;">{last_eruption}</td>
                </tr>
    """
    
    # Add population data if available
    if population_5km != 'N/A' or population_10km != 'N/A' or population_30km != 'N/A' or population_100km != 'N/A':
        html += f"""
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 5px 0; font-weight: bold;">Population (5km)</td>
                    <td style="padding: 5px 0;">{population_5km}</td>
                </tr>
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 5px 0; font-weight: bold;">Population (100km)</td>
                    <td style="padding: 5px 0;">{population_100km}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    """
    
    # Add monitoring indicators section with professional styling
    html += """
        <div style="margin-bottom: 15px;">
            <h4 style="margin-top: 0; margin-bottom: 8px; color: #424242; font-size: 0.95em;">MONITORING DATA</h4>
            <div style="display: flex; gap: 10px;">
    """
    
    # Add icons with tooltips
    if has_insar:
        html += f"""
                <div title="InSAR deformation data available" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background-color: #e3f2fd; border-radius: 4px;">
                    {insar_icon}
                </div>
        """
    
    if has_so2:
        html += f"""
                <div title="SO2 gas monitoring data available" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background-color: #f3e5f5; border-radius: 4px;">
                    {so2_icon}
                </div>
        """
    
    if has_lava:
        html += f"""
                <div title="Lava/eruption monitoring data available" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background-color: #ffebee; border-radius: 4px;">
                    {lava_icon}
                </div>
        """
    
    if not (has_insar or has_so2 or has_lava):
        html += """
                <div style="font-size: 0.9em; color: #757575; padding: 8px 0;">Limited monitoring data available</div>
        """
    
    html += """
            </div>
        </div>
    """
    
    # Add external links with professional styling
    html += """
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">
    """
    
    # Add WOVOdat link if available
    if 'wovodat_id' in volcano and volcano['wovodat_id']:
        html += f"""
            <a href="https://wovodat.org/gvmid/volcano.php?name={volcano['name'].replace(' ', '%20')}" target="_blank" style="text-decoration: none; font-size: 0.85em; color: #1976d2; padding: 5px 10px; border: 1px solid #1976d2; border-radius: 4px; display: inline-flex; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                WOVOdat Data
            </a>
        """
    
    # Add Smithsonian link
    html += f"""
            <a href="https://volcano.si.edu/volcano.cfm?vn={volcano.get('smithsonian_id', volcano['name'].replace(' ', '%20'))}" target="_blank" style="text-decoration: none; font-size: 0.85em; color: #e91e63; padding: 5px 10px; border: 1px solid #e91e63; border-radius: 4px; display: inline-flex; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>
                Smithsonian
            </a>
    """
    
    html += """
        </div>
    """
    
    # Add action button with modern styling
    html += f"""
        <button onclick="selectVolcano()" style="width: 100%; background-color: #2196f3; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            View Complete Data
        </button>
        <script>
            function selectVolcano() {{
                var volcano = {volcano.to_json()};
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: volcano
                }}, '*');
            }}
        </script>
    </div>
    """
    
    return html

def handle_map_click(selected_value):
    """
    Handle the click event from the map
    
    Args:
        selected_value: Data from the clicked volcano
    """
    if selected_value:
        st.session_state.selected_volcano = selected_value
        return True
    return False

def create_risk_heatmap(volcano_df):
    """
    Create a heat map showing predictive volcanic risk
    
    Args:
        volcano_df (pd.DataFrame): DataFrame containing volcano data
        
    Returns:
        folium.Map: A map with heat map overlay of volcanic risk
    """
    # Calculate risk factors
    df_with_risk = generate_risk_levels(volcano_df)
    
    # Calculate center of map based on data
    if len(df_with_risk) > 0:
        center_lat = df_with_risk['latitude'].mean()
        center_lng = df_with_risk['longitude'].mean()
    else:
        # Default center (world view)
        center_lat, center_lng = 20.0, 0.0
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=2,
        tiles="CartoDB positron"
    )
    
    # Add tile layer control with proper attributions
    folium.TileLayer(
        'CartoDB dark_matter',
        attr='Map tiles by <a href="https://carto.com/">CartoDB</a>, under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    folium.TileLayer(
        'OpenStreetMap',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ).add_to(m)
    
    # Generate heat map data
    heatmap_data = generate_risk_heatmap_data(df_with_risk)
    
    # Add heat map layer
    HeatMap(
        data=heatmap_data,
        radius=15,
        blur=10,
        gradient={
            0.0: 'blue',
            0.3: 'lime',
            0.5: 'yellow',
            0.7: 'orange',
            1.0: 'red'
        },
        min_opacity=0.5,
        max_zoom=4,
        name="Volcanic Risk Heat Map"
    ).add_to(m)
    
    # Add marker layer for high-risk volcanoes
    high_risk_layer = folium.FeatureGroup(name="High Risk Volcanoes")
    
    # Filter for only high and very high risk volcanoes
    high_risk_df = df_with_risk[df_with_risk['risk_factor'] >= 0.5]
    
    for _, volcano in high_risk_df.iterrows():
        # Create popup HTML
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h3>{volcano['name']}</h3>
            <p><b>Risk Level:</b> <span style="color: {'red' if volcano['risk_factor'] >= 0.75 else 'orange'}; font-weight: bold;">
                {volcano['risk_level']}
            </span></p>
            <p><b>Risk Factor:</b> {volcano['risk_factor']:.2f}</p>
            <p><b>Alert Level:</b> {volcano.get('alert_level', 'Unknown')}</p>
            <p><b>Last Eruption:</b> {volcano.get('last_eruption', 'Unknown')}</p>
        </div>
        """
        
        # Use risk-based coloring
        if volcano['risk_factor'] >= 0.75:
            icon_color = 'red'
        else:
            icon_color = 'orange'
        
        # Create marker with popup
        folium.CircleMarker(
            location=[volcano['latitude'], volcano['longitude']],
            radius=8,
            color=icon_color,
            fill=True,
            fill_color=icon_color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{volcano['name']} - Risk: {volcano['risk_level']}"
        ).add_to(high_risk_layer)
    
    high_risk_layer.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add a legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0;">Volcanic Risk Levels</h4>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: blue; margin-right: 5px;"></div>
            <div>Low Risk</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: lime; margin-right: 5px;"></div>
            <div>Moderate Risk</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: yellow; margin-right: 5px;"></div>
            <div>Elevated Risk</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="width: 20px; height: 20px; background-color: orange; margin-right: 5px;"></div>
            <div>High Risk</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: red; margin-right: 5px;"></div>
            <div>Very High Risk</div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m, df_with_risk
