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
            # Create additional feature groups for monitoring data
            so2_layer = folium.FeatureGroup(name="SO2 Emissions", show=False)
            ash_layer = folium.FeatureGroup(name="Volcanic Ash", show=False)
            radon_layer = folium.FeatureGroup(name="Radon Gas Levels", show=False)
            
            # Get SO2 data
            so2_data = get_so2_data()
            if not so2_data.empty:
                # Add SO2 markers
                for _, emission in so2_data.iterrows():
                    if 'latitude' in emission and 'longitude' in emission:
                        # Create popup for SO2 emission
                        so2_popup_html = f"""
                        <div style="font-family: Arial; width: 200px;">
                            <h3>SO2 Emission</h3>
                            <p><b>Detected:</b> {emission.get('acq_date', 'Unknown')}</p>
                            <p><b>Confidence:</b> {emission.get('confidence', 'Unknown')}%</p>
                            <p><b>Brightness:</b> {emission.get('bright_t31', 'Unknown')} K</p>
                            <p><b>Source:</b> NASA FIRMS</p>
                        </div>
                        """
                        
                        # Add marker to SO2 layer
                        folium.CircleMarker(
                            location=[emission['latitude'], emission['longitude']],
                            radius=5,
                            color='purple',
                            fill=True,
                            fill_color='purple',
                            fill_opacity=0.7,
                            popup=folium.Popup(so2_popup_html, max_width=250),
                            tooltip="SO2 Emission"
                        ).add_to(so2_layer)
            
            # Get volcanic ash data
            ash_data = get_volcanic_ash_data()
            if not ash_data.empty:
                # Add ash cloud markers
                for _, ash in ash_data.iterrows():
                    if 'latitude' in ash and 'longitude' in ash:
                        # Create popup for ash cloud
                        ash_popup_html = f"""
                        <div style="font-family: Arial; width: 200px;">
                            <h3>Volcanic Ash Advisory</h3>
                            <p><b>Volcano:</b> {ash.get('volcano_name', 'Unknown')}</p>
                            <p><b>Advisory Time:</b> {ash.get('advisory_time', 'Unknown')}</p>
                            <p><b>Ash Height:</b> {ash.get('ash_height_ft', 'Unknown')} ft</p>
                            <p><b>Direction:</b> {ash.get('ash_direction', 'Unknown')}</p>
                            <p><b>Source:</b> {ash.get('source', 'VAAC')}</p>
                        </div>
                        """
                        
                        # Add marker to ash layer
                        folium.CircleMarker(
                            location=[ash['latitude'], ash['longitude']],
                            radius=10,
                            color='darkgray',
                            fill=True,
                            fill_color='darkgray',
                            fill_opacity=0.7,
                            popup=folium.Popup(ash_popup_html, max_width=250),
                            tooltip=f"Ash Cloud: {ash.get('volcano_name', 'Unknown')}"
                        ).add_to(ash_layer)
            
            # Get radon data
            radon_data = get_radon_data()
            if not radon_data.empty:
                # Add radon measurement markers
                for _, radon in radon_data.iterrows():
                    if 'latitude' in radon and 'longitude' in radon:
                        # Create popup for radon measurement
                        radon_popup_html = f"""
                        <div style="font-family: Arial; width: 200px;">
                            <h3>Radon Gas Reading</h3>
                            <p><b>Station:</b> {radon.get('station_id', 'Unknown')}</p>
                            <p><b>Volcano:</b> {radon.get('volcano_name', 'Unknown')}</p>
                            <p><b>Radon Level:</b> {radon.get('radon_level_bq_m3', 'Unknown')} Bq/m³</p>
                            <p><b>Measurement Time:</b> {radon.get('measurement_time', 'Unknown')}</p>
                            <p><b>Source:</b> {radon.get('source', 'Unknown')}</p>
                        </div>
                        """
                        
                        # Add marker to radon layer
                        folium.CircleMarker(
                            location=[radon['latitude'], radon['longitude']],
                            radius=7,
                            color='green',
                            fill=True,
                            fill_color='green',
                            fill_opacity=0.7,
                            popup=folium.Popup(radon_popup_html, max_width=250),
                            tooltip=f"Radon: {radon.get('station_id', 'Unknown')}"
                        ).add_to(radon_layer)
            
            # Add the layers to the map
            so2_layer.add_to(m)
            ash_layer.add_to(m)
            radon_layer.add_to(m)
            
        except Exception as e:
            st.error(f"Error loading monitoring data: {str(e)}")
    
    # Create a marker cluster group for volcanoes
    marker_cluster = MarkerCluster(name="Volcanoes").add_to(m)
    
    # Add volcano markers
    for idx, volcano in volcano_df.iterrows():
        # Define icon color based on alert level
        alert_level = volcano.get('alert_level', 'Unknown')
        icon_color = {
            'Normal': 'green',
            'Advisory': 'orange',
            'Watch': 'orange',
            'Warning': 'red',
            'Unknown': 'gray'
        }.get(alert_level, 'gray')
        
        # Create popup HTML
        popup_html = create_popup_html(volcano)
        
        # Create marker
        marker = folium.Marker(
            location=[volcano['latitude'], volcano['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=volcano['name'],
            icon=folium.Icon(color=icon_color, icon='fire', prefix='fa')
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
    Create HTML content for the volcano popup
    
    Args:
        volcano (pd.Series): Series containing volcano data
        
    Returns:
        str: HTML content for the popup
    """
    # Alert level with color
    alert_level = volcano.get('alert_level', 'Unknown')
    alert_color = {
        'Normal': 'green',
        'Advisory': 'orange',
        'Watch': 'orange',
        'Warning': 'red',
        'Unknown': 'gray'
    }.get(alert_level, 'gray')
    
    # Monitoring indicators
    has_insar = volcano.get('has_insar', False)
    has_so2 = volcano.get('has_so2', False)
    has_lava = volcano.get('has_lava', False)
    
    # Construct HTML
    html = f"""
    <div style="font-family: Arial; width: 250px;">
        <h3>{volcano['name']}</h3>
        <p><b>Country:</b> {volcano['country']}</p>
        <p><b>Type:</b> {volcano['type']}</p>
        <p><b>Elevation:</b> {volcano['elevation']} m</p>
        <p><b>Alert Level:</b> <span style="color: {alert_color}; font-weight: bold;">{alert_level}</span></p>
    """
    
    if 'last_eruption' in volcano and volcano['last_eruption']:
        html += f"<p><b>Last Known Eruption:</b> {volcano['last_eruption']}</p>"
    else:
        html += "<p><b>Last Known Eruption:</b> Unknown</p>"
    
    # Add monitoring indicators
    html += "<p><b>Monitoring Data:</b> "
    
    if has_insar or has_so2 or has_lava:
        if has_insar:
            html += '<span title="InSAR data available">📡 </span>'
        if has_so2:
            html += '<span title="SO2 gas data available">☁️ </span>'
        if has_lava:
            html += '<span title="Lava/eruption data available">🔥 </span>'
    else:
        html += "<span>Limited data available</span>"
    
    html += "</p>"
        
    # Add WOVOdat link if available
    if 'wovodat_id' in volcano and volcano['wovodat_id']:
        html += f'<p><a href="https://wovodat.org/gvmid/volcano.php?name={volcano["name"].replace(" ", "%20")}" target="_blank">WOVOdat Profile</a></p>'
    
    # Add a button to select this volcano in the dashboard
    html += f"""
        <button onclick="selectVolcano()" style="background-color: #0366d6; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">View Details</button>
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
