import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster

def create_volcano_map(volcano_df):
    """
    Create an interactive folium map with volcano markers
    
    Args:
        volcano_df (pd.DataFrame): DataFrame containing volcano data
        
    Returns:
        folium.Map: An interactive map with volcano markers
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
        attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        attr='Map tiles by <a href="https://carto.com/">CartoDB</a>, under <a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    # Create a marker cluster group
    marker_cluster = MarkerCluster().add_to(m)
    
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
