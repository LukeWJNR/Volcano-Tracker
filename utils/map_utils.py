"""
Map utilities for the Volcano Monitoring Dashboard.

This module provides functions for creating maps, markers, popups,
and other map-related visualizations using Folium.
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd
from typing import Dict, List, Any
import random
import json

def create_volcano_map(df: pd.DataFrame, include_monitoring_data: bool = False):
    """
    Create a folium map with volcano markers based on the provided DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing volcano data
        include_monitoring_data (bool): Whether to include monitoring data layers
        
    Returns:
        folium.Map: Folium map object with volcano markers
    """
    # Create a map centered on the mean of coordinates
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # If we don't have any volcanoes in the filtered list, use a default center
    if pd.isna(center_lat) or pd.isna(center_lon):
        center_lat, center_lon = 0, 0
    
    # Create the map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=3,
        tiles="CartoDB positron",
        control_scale=True
    )
    
    # Add alternative tile layers
    folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.TileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='Satellite'
    ).add_to(m)
    
    # Create a marker cluster for better performance with many markers
    marker_cluster = MarkerCluster(name="Volcanoes").add_to(m)
    
    # Add each volcano as a marker
    for _, row in df.iterrows():
        # Skip rows with missing coordinates
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            continue
            
        # Determine marker color based on alert level
        alert_level = row.get('alert_level', 'Unknown')
        marker_color = {
            'Normal': 'green',
            'Advisory': 'blue',
            'Watch': 'orange',
            'Warning': 'red',
            'Unknown': 'gray'
        }.get(alert_level, 'gray')
        
        # Create popup content with HTML
        popup_content = create_popup_html(row)
        
        # Create marker with popup
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=row['name'],
            icon=folium.Icon(color=marker_color, icon="fire", prefix="fa")
        ).add_to(marker_cluster)
    
    # Add monitoring data layers if requested
    if include_monitoring_data:
        # Add global SO2 layer
        so2_layer = folium.WmsTileLayer(
            url="https://giovanni.gsfc.nasa.gov/giovanni/daac-bin/wms_ag4?",
            layers="OMI_SO2_003",
            transparent=True,
            control=True,
            name="NASA AIRS SO2 Column",
            overlay=True,
            show=False,
            fmt="image/png"
        )
        so2_layer.add_to(m)
        
        # Add simulated volcano monitoring points (normally from real API)
        # In a real implementation, this would fetch data from monitoring APIs
        add_monitoring_points(m, df)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_popup_html(volcano: pd.Series) -> str:
    """
    Create HTML content for volcano popup.
    
    Args:
        volcano (pd.Series): Row from volcano DataFrame
        
    Returns:
        str: HTML content for popup
    """
    # Get alert level color
    alert_level = volcano.get('alert_level', 'Unknown')
    alert_color = {
        'Normal': '#4CAF50',
        'Advisory': '#2196F3',
        'Watch': '#FF9800',
        'Warning': '#F44336',
        'Unknown': '#9E9E9E'
    }.get(alert_level, '#9E9E9E')
    
    # Create HTML content
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 300px;">
        <h3 style="margin-bottom: 5px;">{volcano['name']}</h3>
        <div style="margin-bottom: 10px;">
            <span style="background-color: {alert_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">
                {alert_level}
            </span>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
            <tr>
                <td style="font-weight: bold; padding: 3px; border-bottom: 1px solid #eee;">Type:</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;">{volcano.get('type', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 3px; border-bottom: 1px solid #eee;">Elevation:</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;">{volcano.get('elevation', 'Unknown')} m</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 3px; border-bottom: 1px solid #eee;">Status:</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;">{volcano.get('status', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 3px; border-bottom: 1px solid #eee;">Last Eruption:</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;">{volcano.get('last_eruption', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 3px; border-bottom: 1px solid #eee;">Country:</td>
                <td style="padding: 3px; border-bottom: 1px solid #eee;">{volcano.get('country', 'Unknown')}</td>
            </tr>
            <tr>
                <td style="font-weight: bold; padding: 3px;">Region:</td>
                <td style="padding: 3px;">{volcano.get('region', 'Unknown')}</td>
            </tr>
        </table>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">
            <strong>Data Source:</strong> USGS Volcano Hazards Program
        </div>
    </div>
    """
    
    return html

def add_monitoring_points(m: folium.Map, volcanoes_df: pd.DataFrame):
    """
    Add simulated monitoring data points to the map.
    
    In a production environment, this would fetch real-time data from
    monitoring APIs and satellite sources.
    
    Args:
        m (folium.Map): Folium map to add points to
        volcanoes_df (pd.DataFrame): DataFrame of volcanoes for reference
    """
    # Create feature groups for different data types
    so2_group = folium.FeatureGroup(name="SO2 Emissions", show=False)
    ash_group = folium.FeatureGroup(name="Volcanic Ash", show=False)
    radon_group = folium.FeatureGroup(name="Radon Gas Levels", show=False)
    
    # Select up to 10 of the most active volcanoes to show monitoring data
    active_volcanoes = volcanoes_df[volcanoes_df['alert_level'].isin(['Warning', 'Watch', 'Advisory'])]
    if len(active_volcanoes) > 10:
        active_volcanoes = active_volcanoes.sample(10)
    elif len(active_volcanoes) == 0:
        # If no active volcanoes, use up to 5 random ones
        active_volcanoes = volcanoes_df.sample(min(5, len(volcanoes_df)))
    
    # Add SO2 emission points
    for _, volcano in active_volcanoes.iterrows():
        # Skip rows with missing coordinates
        if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
            continue
            
        # Randomize location slightly to simulate emission plume
        lat_offset = random.uniform(-0.5, 0.5)
        lon_offset = random.uniform(-0.5, 0.5)
        
        # Create SO2 marker with appropriate popup
        so2_level = random.randint(10, 1000)
        so2_popup = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4>SO2 Emission</h4>
            <p><strong>Near:</strong> {volcano['name']}</p>
            <p><strong>Level:</strong> {so2_level} DU</p>
            <p><strong>Detected:</strong> Recent satellite pass</p>
        </div>
        """
        
        # Determine marker color based on SO2 level
        so2_color = 'green'
        if so2_level > 300:
            so2_color = 'red'
        elif so2_level > 100:
            so2_color = 'orange'
        elif so2_level > 50:
            so2_color = 'blue'
        
        folium.CircleMarker(
            location=[volcano['latitude'] + lat_offset, volcano['longitude'] + lon_offset],
            radius=so2_level / 50,  # Size based on level
            color=so2_color,
            fill=True,
            fill_color=so2_color,
            fill_opacity=0.4,
            popup=folium.Popup(so2_popup, max_width=200),
            tooltip=f"SO2: {so2_level} DU"
        ).add_to(so2_group)
    
    # Add ash advisory areas for volcanoes with Warning or Watch alert levels
    warning_volcanoes = active_volcanoes[active_volcanoes['alert_level'].isin(['Warning', 'Watch'])]
    for _, volcano in warning_volcanoes.iterrows():
        # Skip rows with missing coordinates
        if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
            continue
            
        # Create ash cloud polygon (simplified for demo)
        wind_direction = random.uniform(0, 360)  # Random wind direction
        wind_speed = random.uniform(5, 30)       # Random wind speed in km/h
        
        # Calculate ash cloud polygon based on wind
        ash_distance = wind_speed * 20  # Simplified: speed * arbitrary factor
        ash_width = ash_distance / 3    # Width of plume
        
        # Convert direction to radians and calculate coordinates
        import math
        rad = math.radians(wind_direction)
        dx = math.sin(rad) * ash_distance
        dy = math.cos(rad) * ash_distance
        
        # Create polygon coordinates (simple elongated triangle)
        base_lat = volcano['latitude']
        base_lon = volcano['longitude']
        
        # Calculate points for triangle
        dx_perp = math.sin(rad + math.pi/2) * ash_width/2
        dy_perp = math.cos(rad + math.pi/2) * ash_width/2
        
        ash_coords = [
            [base_lat, base_lon],  # Volcano location (apex)
            [base_lat + dy_perp + dy, base_lon + dx_perp + dx],  # End point 1
            [base_lat - dy_perp + dy, base_lon - dx_perp + dx],  # End point 2
        ]
        
        # Add ash cloud polygon
        ash_popup = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4>Volcanic Ash Advisory</h4>
            <p><strong>Source:</strong> {volcano['name']}</p>
            <p><strong>Wind Direction:</strong> {int(wind_direction)}°</p>
            <p><strong>Wind Speed:</strong> {int(wind_speed)} km/h</p>
            <p><strong>Status:</strong> Active ash emission</p>
        </div>
        """
        
        folium.Polygon(
            locations=ash_coords,
            color='purple',
            fill=True,
            fill_color='purple',
            fill_opacity=0.2,
            popup=folium.Popup(ash_popup, max_width=200),
            tooltip=f"Ash from {volcano['name']}"
        ).add_to(ash_group)
    
    # Add radon gas monitoring stations
    for _, volcano in active_volcanoes.iterrows():
        # Skip rows with missing coordinates
        if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
            continue
            
        # Add 1-3 monitoring stations near the volcano
        num_stations = random.randint(1, 3)
        for i in range(num_stations):
            # Randomize location to simulate monitoring stations
            lat_offset = random.uniform(-0.2, 0.2)
            lon_offset = random.uniform(-0.2, 0.2)
            
            # Generate random radon level (in Bq/m³)
            radon_level = random.randint(20, 500)
            
            # Determine color based on radon level
            if radon_level > 300:
                radon_color = 'red'
                status = 'Elevated'
            elif radon_level > 100:
                radon_color = 'orange'
                status = 'Above normal'
            else:
                radon_color = 'green'
                status = 'Normal'
            
            # Create popup content
            radon_popup = f"""
            <div style="font-family: Arial, sans-serif;">
                <h4>Radon Monitoring Station #{i+1}</h4>
                <p><strong>Near:</strong> {volcano['name']}</p>
                <p><strong>Radon level:</strong> {radon_level} Bq/m³</p>
                <p><strong>Status:</strong> {status}</p>
                <p><small>Updated: Recently</small></p>
            </div>
            """
            
            folium.Marker(
                location=[volcano['latitude'] + lat_offset, volcano['longitude'] + lon_offset],
                popup=folium.Popup(radon_popup, max_width=200),
                tooltip=f"Radon: {radon_level} Bq/m³",
                icon=folium.Icon(color=radon_color, icon="flask", prefix="fa")
            ).add_to(radon_group)
    
    # Add the feature groups to the map
    so2_group.add_to(m)
    ash_group.add_to(m)
    radon_group.add_to(m)