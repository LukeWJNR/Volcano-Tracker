"""
Utility functions for volcano risk assessment and predictive heat maps

This module contains logic for calculating volcanic risk levels based on 
various factors and generating heat map visualizations.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

def calculate_risk_factor(volcano_data: Dict[str, Any]) -> float:
    """
    Calculate a risk factor for a volcano based on various indicators
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano data
        
    Returns:
        float: Risk factor (0-1 scale where 1 is highest risk)
    """
    risk_score = 0.0
    total_weight = 0.0
    
    # Factor 1: Alert level (highest weight)
    alert_levels = {
        'Normal': 0.1,
        'Advisory': 0.4,
        'Watch': 0.7,
        'Warning': 1.0,
        'Unknown': 0.3  # Default to moderate risk if unknown
    }
    alert_weight = 0.35
    
    # Ensure alert_level is a string and use 'Unknown' as fallback
    alert_level = volcano_data.get('alert_level')
    if alert_level is None or not isinstance(alert_level, str):
        alert_level = 'Unknown'
        
    risk_score += alert_levels.get(alert_level, 0.3) * alert_weight
    total_weight += alert_weight
    
    # Factor 2: Recent eruption history
    eruption_weight = 0.25
    last_eruption = volcano_data.get('last_eruption', 'Unknown')
    
    # Try to determine how recently the volcano erupted
    if last_eruption == 'Unknown':
        eruption_score = 0.3  # Moderate if unknown
    else:
        try:
            # Convert to string if it's not already
            if not isinstance(last_eruption, str):
                last_eruption = str(last_eruption)
                
            # Try to parse the last eruption as a year
            if '-' in last_eruption:  # Might be a date range like "2020-2021"
                last_year = int(last_eruption.split('-')[-1])
            else:
                last_year = int(last_eruption)
                
            current_year = datetime.now().year
            years_since = current_year - last_year
            
            if years_since <= 1:
                eruption_score = 1.0  # Very recent (within a year)
            elif years_since <= 5:
                eruption_score = 0.8  # Recent (within 5 years)
            elif years_since <= 10:
                eruption_score = 0.6  # Somewhat recent (within 10 years)
            elif years_since <= 50:
                eruption_score = 0.4  # Not recent (within 50 years)
            elif years_since <= 100:
                eruption_score = 0.2  # Historic (within 100 years)
            else:
                eruption_score = 0.1  # Very old eruption
        except (ValueError, TypeError, AttributeError):
            # If we can't parse it as a year, assign moderate risk
            eruption_score = 0.3
    
    risk_score += eruption_score * eruption_weight
    total_weight += eruption_weight
    
    # Factor 3: Volcano type
    type_weight = 0.15
    high_risk_types = ['stratovolcano', 'caldera', 'complex volcano']
    medium_risk_types = ['shield volcano', 'pyroclastic shield', 'volcanic field']
    low_risk_types = ['cinder cone', 'fissure vent', 'lava dome']
    
    volcano_type = str(volcano_data.get('type', '')).lower()
    
    if any(risk_type in volcano_type for risk_type in high_risk_types):
        type_score = 0.9
    elif any(risk_type in volcano_type for risk_type in medium_risk_types):
        type_score = 0.5
    elif any(risk_type in volcano_type for risk_type in low_risk_types):
        type_score = 0.2
    else:
        type_score = 0.4  # Default if type is unknown or not categorized
    
    risk_score += type_score * type_weight
    total_weight += type_weight
    
    # Factor 4: Monitoring availability (inverse relationship - better monitoring reduces risk)
    monitoring_weight = 0.15
    
    # Default monitoring factors
    has_insar = volcano_data.get('has_insar', False)
    has_so2 = volcano_data.get('has_so2', False)
    has_lava = volcano_data.get('has_lava', False)
    
    # Count how many monitoring systems are available
    monitoring_count = sum([has_insar, has_so2, has_lava])
    
    if monitoring_count == 0:
        # No monitoring - higher risk due to lack of early warning
        monitoring_score = 0.9
    elif monitoring_count == 1:
        monitoring_score = 0.6
    elif monitoring_count == 2:
        monitoring_score = 0.4
    else:
        monitoring_score = 0.2  # Well monitored - lower risk due to early warning
    
    risk_score += monitoring_score * monitoring_weight
    total_weight += monitoring_weight
    
    # Factor 5: Regional activity (Iceland volcanoes currently have higher activity)
    region_weight = 0.1
    
    high_activity_regions = ['iceland', 'indonesia', 'philippines', 'kamchatka']
    medium_activity_regions = ['alaska', 'hawaii', 'japan', 'italy']
    
    region = str(volcano_data.get('region', '')).lower()
    country = str(volcano_data.get('country', '')).lower()
    
    if any(high_region in region for high_region in high_activity_regions) or \
       any(high_region in country for high_region in high_activity_regions):
        region_score = 0.9
    elif any(medium_region in region for medium_region in medium_activity_regions) or \
         any(medium_region in country for medium_region in medium_activity_regions):
        region_score = 0.6
    else:
        region_score = 0.3
    
    risk_score += region_score * region_weight
    total_weight += region_weight
    
    # Normalize the score if weights don't add up to 1
    if total_weight > 0:
        risk_score = risk_score / total_weight
    
    # Ensure the score is between 0 and 1
    return max(0.0, min(1.0, risk_score))

def generate_risk_levels(volcanoes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate risk levels for all volcanoes in the dataframe
    
    Args:
        volcanoes_df (pd.DataFrame): DataFrame containing volcano data
        
    Returns:
        pd.DataFrame: DataFrame with added risk_level and risk_factor columns
    """
    # Create a copy to avoid modifying the original
    df = volcanoes_df.copy()
    
    # Calculate risk factor for each volcano
    df['risk_factor'] = df.apply(lambda row: calculate_risk_factor(row.to_dict()), axis=1)
    
    # Categorize risk levels
    df['risk_level'] = pd.cut(
        df['risk_factor'], 
        bins=[0, 0.25, 0.5, 0.75, 1.0], 
        labels=['Low', 'Moderate', 'High', 'Very High']
    )
    
    return df

def calculate_radius_from_risk(risk_factor: float, base_radius: int = 50000) -> int:
    """
    Calculate a heatmap radius based on the risk factor
    
    Args:
        risk_factor (float): Risk factor (0-1)
        base_radius (int): Base radius in meters
        
    Returns:
        int: Radius scaled by risk factor
    """
    # Scale the radius linearly with risk factor, with a minimum of 30% of base radius
    min_radius = base_radius * 0.3
    return int(min_radius + risk_factor * (base_radius - min_radius))

def generate_risk_heatmap_data(volcanoes_df: pd.DataFrame) -> List[List[float]]:
    """
    Generate heat map data points based on volcano locations and risk factors
    
    Args:
        volcanoes_df (pd.DataFrame): DataFrame with volcano data including risk_factor
        
    Returns:
        List[List[float]]: List of [lat, lng, intensity] for each point
    """
    heatmap_data = []
    
    # Ensure risk_factor is present
    if 'risk_factor' not in volcanoes_df.columns:
        volcanoes_df = generate_risk_levels(volcanoes_df)
    
    # Create heat map data points
    for _, volcano in volcanoes_df.iterrows():
        # Each point is [latitude, longitude, intensity]
        # Intensity is the risk factor (0-1)
        heatmap_data.append([
            volcano['latitude'],
            volcano['longitude'],
            volcano['risk_factor']
        ])
    
    return heatmap_data