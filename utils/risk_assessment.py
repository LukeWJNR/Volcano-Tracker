"""
Utility functions for volcano risk assessment and predictive heat maps

This module contains logic for calculating volcanic risk levels based on 
various factors and generating heat map visualizations. It also includes 
specialized metrics like the Lava Build-Up Index that quantify specific 
aspects of volcanic hazards.
"""
import pandas as pd
import numpy as np
import math
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
            # Handle different types of last_eruption values
            if last_eruption is None:
                # No eruption data available
                years_since = 10000  # Very old (default high value)
            elif isinstance(last_eruption, (int, float)):
                # If it's already a number, use it directly
                if not math.isnan(float(last_eruption)):  # Check for NaN
                    last_year = int(float(last_eruption))
                    current_year = datetime.now().year
                    years_since = current_year - last_year
                else:
                    years_since = 10000  # NaN value, treat as very old
            else:
                # Convert to string for parsing if it's not already
                if not isinstance(last_eruption, str):
                    last_eruption = str(last_eruption)
                
                # Skip if it's "Unknown" or empty
                if last_eruption.lower() in ("unknown", "none", "", "nan"):
                    years_since = 10000  # No data, treat as very old
                # Try to parse the last eruption as a year
                elif '-' in last_eruption:  # Might be a date range like "2020-2021"
                    last_year = int(last_eruption.split('-')[-1])
                    current_year = datetime.now().year
                    years_since = current_year - last_year
                else:
                    # Try to parse as a simple year
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

def calculate_lava_buildup_index(volcano_data: Dict[str, Any], earthquake_data: List = None) -> float:
    """
    Calculate the Lava Build-Up Index for a volcano based on various indicators.
    This index quantifies the potential for lava accumulation in the volcano's magma 
    chamber and conduits, which can be a precursor to eruptions.
    
    The formula is based on three key factors:
    1. Thermal anomaly count (indicator of heat from magma)
    2. Deformation rate (indicator of ground movement from magma pressure)
    3. Local earthquake sum (indicator of seismic activity near the volcano)
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano data
        earthquake_data (List, optional): List of earthquake data from USGS. If None, will fetch from API.
        
    Returns:
        float: Lava Build-Up Index on a scale of 0.0 to 10.0
    """
    # If no earthquake data provided, fetch it (this is less efficient)
    if earthquake_data is None:
        try:
            from utils.map_utils import fetch_usgs_earthquake_data
            earthquake_data = fetch_usgs_earthquake_data()
        except Exception as e:
            print(f"Error fetching earthquake data: {e}")
            earthquake_data = []
    
    # Generate a thermal anomaly count based on volcano characteristics
    # In production, this would come from satellite thermal imaging
    thermal_anomaly_count = 0
    
    # Base thermal anomaly count on volcano type and alert level
    volcano_type = str(volcano_data.get('type', '')).lower()
    alert_level = str(volcano_data.get('alert_level', 'Unknown'))
    
    # Volcano types with typically high thermal signatures
    high_thermal_types = ['stratovolcano', 'caldera', 'complex volcano', 'lava dome']
    medium_thermal_types = ['shield volcano', 'pyroclastic shield', 'volcanic field']
    
    # Base thermal anomaly count on volcano type
    if any(thermal_type in volcano_type for thermal_type in high_thermal_types):
        thermal_anomaly_count += 5
    elif any(thermal_type in volcano_type for thermal_type in medium_thermal_types):
        thermal_anomaly_count += 3
    else:
        thermal_anomaly_count += 1
    
    # Adjust based on alert level
    if alert_level == 'Warning':
        thermal_anomaly_count += 5
    elif alert_level == 'Watch':
        thermal_anomaly_count += 3
    elif alert_level == 'Advisory':
        thermal_anomaly_count += 2
    
    # Generate a deformation rate based on volcano activity
    # In production, this would come from InSAR or ground-based measurements
    deformation_rate = 0
    
    # Base deformation on recency of eruptions (more recent = more likely to have deformation)
    last_eruption = volcano_data.get('last_eruption', 'Unknown')
    years_since = 100  # Default value for unknown
    
    if isinstance(last_eruption, (int, float)) and not math.isnan(float(last_eruption)):
        try:
            last_year = int(float(last_eruption))
            current_year = datetime.now().year
            years_since = current_year - last_year
        except (ValueError, TypeError):
            pass
    elif isinstance(last_eruption, str) and last_eruption.lower() not in ("unknown", "none", "", "nan"):
        try:
            if '-' in last_eruption:  # Date range like "2020-2021"
                last_year = int(last_eruption.split('-')[-1])
                current_year = datetime.now().year
                years_since = current_year - last_year
            else:
                last_year = int(last_eruption)
                current_year = datetime.now().year
                years_since = current_year - last_year
        except (ValueError, TypeError):
            pass
    
    # Calculate deformation rate based on eruption recency
    if years_since <= 2:
        deformation_rate = 15  # Very recent eruption - likely still deforming
    elif years_since <= 10:
        deformation_rate = 10  # Recent enough that system may be deforming
    elif years_since <= 30:
        deformation_rate = 5   # Moderate time for build-up
    else:
        deformation_rate = 2   # Older eruptions have less deformation typically
    
    # Adjust based on alert level
    if alert_level == 'Warning':
        deformation_rate *= 1.5
    elif alert_level == 'Watch':
        deformation_rate *= 1.3
    
    # Calculate local earthquake sum around the volcano
    # Get the volcano's coordinates
    lat = volcano_data.get('latitude')
    lon = volcano_data.get('longitude')
    
    # Sum up earthquake magnitudes near the volcano
    local_quake_sum = 0
    
    if lat is not None and lon is not None and earthquake_data:
        for quake in earthquake_data:
            try:
                # Extract earthquake coordinates (USGS format is [longitude, latitude, depth])
                quake_coords = quake['geometry']['coordinates']
                quake_lon = quake_coords[0]
                quake_lat = quake_coords[1]
                
                # Calculate distance between volcano and earthquake (simple Euclidean distance)
                distance = ((quake_lat - lat) ** 2 + (quake_lon - lon) ** 2) ** 0.5
                
                # If earthquake is within ~200km (approximately 2 degrees), add its magnitude to sum
                if distance < 2:
                    magnitude = quake['properties'].get('mag', 0)
                    if magnitude:
                        local_quake_sum += magnitude
            except (KeyError, IndexError, TypeError):
                # Skip problematic earthquake entries
                continue
    
    # Calculate the Lava Build-Up Index using the formula
    # This mirrors the TypeScript implementation: (thermalAnomalyCount * deformationRate * localQuakeSum) / 10
    # We apply a small base value to ensure non-zero results even when data is missing
    base_value = 1
    
    # Scale the quake sum to avoid excessive values
    scaled_quake_sum = min(10, local_quake_sum / 5)
    
    # Formula: (thermal_anomaly_count * deformation_rate * scaled_quake_sum) / 10
    lava_buildup_raw = (thermal_anomaly_count * deformation_rate * max(1, scaled_quake_sum)) / 10
    
    # Adjust with base value to ensure minimal values
    lava_buildup_index = base_value + lava_buildup_raw
    
    # Ensure index is between 0 and 10
    lava_buildup_index = max(0.0, min(10.0, lava_buildup_index))
    
    # Round to one decimal place for display
    return round(lava_buildup_index, 1)

def calculate_volcano_metrics(volcanoes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate additional volcano risk metrics and indicators
    
    Args:
        volcanoes_df (pd.DataFrame): DataFrame containing volcano data
        
    Returns:
        pd.DataFrame: DataFrame with added metrics columns
    """
    from utils.map_utils import fetch_usgs_earthquake_data
    
    # Create a copy to avoid modifying the original
    df = volcanoes_df.copy()
    
    # Calculate risk levels if not already present
    if 'risk_factor' not in df.columns:
        df = generate_risk_levels(df)
    
    # Fetch earthquake data once for all volcanoes
    try:
        # Get earthquake data from USGS API
        earthquake_data = fetch_usgs_earthquake_data()
    except Exception as e:
        print(f"Error fetching earthquake data: {e}")
        earthquake_data = []
    
    # Calculate Lava Build-Up Index for each volcano with shared earthquake data
    def calculate_lbi_with_shared_data(row):
        row_dict = row.to_dict()
        # Create a function that uses the shared earthquake data
        return calculate_lava_buildup_index(row_dict, earthquake_data)
    
    # Apply the calculation with shared earthquake data
    df['lava_buildup_index'] = df.apply(calculate_lbi_with_shared_data, axis=1)
    
    # Add more metrics here as needed
    
    return df