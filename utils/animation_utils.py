"""
Animation utilities for the Volcano Monitoring Dashboard.

This module provides functions to generate animation data and visualizations
for various volcano types and eruption phases.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional

# Volcano type definitions
VOLCANO_TYPES = {
    "shield": {
        "description": "Broad, gently sloping volcano with basaltic lava flows",
        "examples": ["Mauna Loa", "Kilauea"],
        "eruption_style": "Effusive",
        "magma_viscosity": "Low",
        "explosivity": "Low",
        "dome_formation": False,
        "caldera_formation": False,
        "plume_height_avg": 2.5,  # in km
        "plume_height_max": 8.0,  # in km
        "lava_flow_rate_avg": 50.0,  # in m³/s
        "magma_temperature": 1200,  # in °C
        "magma_composition": "Basaltic",
        "magma_chamber_depth": 3.5,  # in km
        "secondary_chambers": True
    },
    "stratovolcano": {
        "description": "Steep-sided, symmetrical cone with alternating layers of lava and pyroclastics",
        "examples": ["Mount Fuji", "Mount St. Helens"],
        "eruption_style": "Explosive",
        "magma_viscosity": "High",
        "explosivity": "High",
        "dome_formation": True,
        "caldera_formation": False,
        "plume_height_avg": 15.0,  # in km
        "plume_height_max": 25.0,  # in km
        "lava_flow_rate_avg": 10.0,  # in m³/s
        "magma_temperature": 950,  # in °C
        "magma_composition": "Andesitic to Dacitic",
        "magma_chamber_depth": 5.0,  # in km
        "secondary_chambers": True
    },
    "caldera": {
        "description": "Large, basin-shaped depression formed by collapse",
        "examples": ["Yellowstone", "Toba"],
        "eruption_style": "Highly Explosive",
        "magma_viscosity": "Very High",
        "explosivity": "Very High",
        "dome_formation": True,
        "caldera_formation": True,
        "plume_height_avg": 25.0,  # in km
        "plume_height_max": 40.0,  # in km
        "lava_flow_rate_avg": 5.0,  # in m³/s
        "magma_temperature": 850,  # in °C
        "magma_composition": "Rhyolitic",
        "magma_chamber_depth": 8.0,  # in km
        "secondary_chambers": True
    },
    "cinder_cone": {
        "description": "Small, steep-sided cone built from ejected lava fragments",
        "examples": ["Paricutin", "Cerro Negro"],
        "eruption_style": "Mild to Moderate Explosive",
        "magma_viscosity": "Moderate",
        "explosivity": "Moderate",
        "dome_formation": False,
        "caldera_formation": False,
        "plume_height_avg": 5.0,  # in km
        "plume_height_max": 10.0,  # in km
        "lava_flow_rate_avg": 15.0,  # in m³/s
        "magma_temperature": 1050,  # in °C
        "magma_composition": "Basaltic to Andesitic",
        "magma_chamber_depth": 2.0,  # in km
        "secondary_chambers": False
    },
    "lava_dome": {
        "description": "Rounded, steep-sided mass formed by viscous lava",
        "examples": ["Soufrière Hills", "Mount St. Helens Dome"],
        "eruption_style": "Effusive to Explosive",
        "magma_viscosity": "Very High",
        "explosivity": "Moderate",
        "dome_formation": True,
        "caldera_formation": False,
        "plume_height_avg": 8.0,  # in km
        "plume_height_max": 15.0,  # in km
        "lava_flow_rate_avg": 2.0,  # in m³/s
        "magma_temperature": 800,  # in °C
        "magma_composition": "Dacitic to Rhyolitic",
        "magma_chamber_depth": 4.0,  # in km
        "secondary_chambers": False
    }
}

# Alert level definitions
ALERT_LEVELS = {
    "Normal": {
        "description": "Volcano is in typical background, non-eruptive state",
        "color": "green",
        "hazard_radius_km": 0,
        "evacuation_recommended": False,
        "monitoring_level": "Routine",
        "update_frequency": "Monthly"
    },
    "Advisory": {
        "description": "Volcano is exhibiting signs of elevated unrest above known background level",
        "color": "yellow",
        "hazard_radius_km": 2,
        "evacuation_recommended": False,
        "monitoring_level": "Heightened",
        "update_frequency": "Weekly"
    },
    "Watch": {
        "description": "Volcano is exhibiting heightened or escalating unrest with increased potential of eruption",
        "color": "orange",
        "hazard_radius_km": 5,
        "evacuation_recommended": "Prepare",
        "monitoring_level": "Elevated",
        "update_frequency": "Daily"
    },
    "Warning": {
        "description": "Hazardous eruption is imminent, underway, or suspected",
        "color": "red",
        "hazard_radius_km": 10,
        "evacuation_recommended": True,
        "monitoring_level": "Maximum",
        "update_frequency": "Multiple times daily"
    }
}

def determine_volcano_type(volcano_data: Dict[str, Any]) -> str:
    """
    Determine the volcano type based on its characteristics.
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano information
        
    Returns:
        str: Volcano type (shield, stratovolcano, caldera, cinder_cone, lava_dome)
    """
    volcano_type = volcano_data.get('type', '').lower()
    
    # Check for specific keywords in the type field
    if 'shield' in volcano_type:
        return 'shield'
    elif any(x in volcano_type for x in ['strato', 'composite', 'stratovol']):
        return 'stratovolcano'
    elif any(x in volcano_type for x in ['caldera', 'collapse']):
        return 'caldera'
    elif any(x in volcano_type for x in ['cinder', 'scoria', 'cone']):
        return 'cinder_cone'
    elif any(x in volcano_type for x in ['dome', 'lava dome']):
        return 'lava_dome'
    
    # Default to stratovolcano as the most common type
    return 'stratovolcano'

def get_eruption_probability(volcano_data: Dict[str, Any]) -> float:
    """
    Calculate eruption probability based on volcano characteristics.
    
    Args:
        volcano_data (Dict[str, Any]): Dictionary containing volcano information
        
    Returns:
        float: Eruption probability (0-100)
    """
    # Start with a base probability
    base_probability = 5.0
    
    # Adjust based on alert level
    alert_level = volcano_data.get('alert_level', 'Normal')
    alert_adjustments = {
        'Normal': 0,
        'Advisory': 15,
        'Watch': 35,
        'Warning': 60
    }
    
    probability = base_probability + alert_adjustments.get(alert_level, 0)
    
    # Adjust based on time since last eruption
    last_eruption = volcano_data.get('last_eruption')
    if last_eruption:
        try:
            # Convert to year if it's a date string
            if isinstance(last_eruption, str) and '-' in last_eruption:
                year = int(last_eruption.split('-')[0])
            else:
                year = int(last_eruption)
                
            years_since = 2025 - year  # Current year minus last eruption year
            
            # Volcanoes that have been quiet for very long might be less likely to erupt
            # unless they're in an active phase
            if years_since < 10:
                probability += 15  # Recently active
            elif years_since < 50:
                probability += 5   # Active in living memory
            elif years_since < 200:
                probability -= 2   # Long dormant
            else:
                probability -= 5   # Very long dormant
                
        except (ValueError, TypeError):
            # If we can't parse the date, don't adjust
            pass
    
    # Ensure probability is within 0-100 range
    return max(0, min(100, probability))

def generate_eruption_timeline(
    volcano_type: str, 
    eruption_probability: float, 
    days: int = 30
) -> Dict[str, List[Any]]:
    """
    Generate a timeline of eruption events and precursors.
    
    Args:
        volcano_type (str): Type of volcano
        eruption_probability (float): Probability of eruption (0-100)
        days (int): Number of days to simulate
        
    Returns:
        Dict[str, List[Any]]: Dictionary containing timeline series data
    """
    # Determine if an eruption will occur based on probability
    eruption_occurs = np.random.random() * 100 < eruption_probability
    
    # Create time points for each day
    time_points = np.arange(days)
    
    # Initialize data series
    seismic_activity = np.zeros(days)
    gas_emissions = np.zeros(days)
    deformation = np.zeros(days)
    temperature = np.zeros(days)
    eruption_intensity = np.zeros(days)
    
    if not eruption_occurs:
        # No eruption, just random background noise
        seismic_activity = np.random.normal(5, 2, days)
        gas_emissions = np.random.normal(10, 3, days)
        deformation = np.random.normal(2, 0.5, days)
        temperature = np.random.normal(15, 2, days)
        
        # Ensure non-negative values
        seismic_activity = np.maximum(seismic_activity, 0)
        gas_emissions = np.maximum(gas_emissions, 0)
        deformation = np.maximum(deformation, 0)
        temperature = np.maximum(temperature, 0)
    else:
        # Determine eruption day based on timeline
        eruption_day = int(days * 0.6)  # Eruption at 60% of timeline
        
        # Generate precursor data
        for i in range(days):
            # Pre-eruption build-up
            if i < eruption_day:
                # Exponential increase in activity leading up to eruption
                progress = i / eruption_day
                
                # Each volcano type has different precursor patterns
                if volcano_type == 'shield':
                    # Shield volcanoes often have more gradual build-up
                    seismic_activity[i] = 5 + 15 * progress**2
                    gas_emissions[i] = 10 + 30 * progress**1.5
                    deformation[i] = 2 + 8 * progress**2
                    temperature[i] = 15 + 25 * progress
                    
                elif volcano_type == 'stratovolcano':
                    # Stratovolcanoes often have sharper increase before eruption
                    seismic_activity[i] = 5 + 25 * progress**3
                    gas_emissions[i] = 10 + 50 * progress**2
                    deformation[i] = 2 + 12 * progress**1.5
                    temperature[i] = 15 + 35 * progress**1.2
                    
                elif volcano_type == 'caldera':
                    # Calderas can have massive build-up
                    seismic_activity[i] = 5 + 35 * progress**2.5
                    gas_emissions[i] = 10 + 70 * progress**2
                    deformation[i] = 2 + 18 * progress**2
                    temperature[i] = 15 + 45 * progress**1.5
                    
                elif volcano_type == 'cinder_cone':
                    # Cinder cones often have less obvious precursors
                    seismic_activity[i] = 5 + 10 * progress**1.5
                    gas_emissions[i] = 10 + 20 * progress
                    deformation[i] = 2 + 5 * progress
                    temperature[i] = 15 + 15 * progress
                    
                elif volcano_type == 'lava_dome':
                    # Lava domes often show deformation and temperature changes
                    seismic_activity[i] = 5 + 15 * progress**2
                    gas_emissions[i] = 10 + 25 * progress**1.5
                    deformation[i] = 2 + 15 * progress**1.8
                    temperature[i] = 15 + 40 * progress**1.5
                
                # Add some random noise to make it more realistic
                seismic_activity[i] += np.random.normal(0, 2)
                gas_emissions[i] += np.random.normal(0, 3)
                deformation[i] += np.random.normal(0, 0.5)
                temperature[i] += np.random.normal(0, 2)
                
            # Eruption and post-eruption
            else:
                # Days since eruption start
                days_since = i - eruption_day
                
                # Eruption intensity varies by volcano type
                if volcano_type == 'shield':
                    # Shield volcanoes: longer, less explosive eruptions
                    max_intensity = 60
                    decay_rate = 0.1  # Slower decay
                    
                elif volcano_type == 'stratovolcano':
                    # Stratovolcanoes: intense, explosive eruptions
                    max_intensity = 85
                    decay_rate = 0.3
                    
                elif volcano_type == 'caldera':
                    # Calderas: most intense eruptions
                    max_intensity = 95
                    decay_rate = 0.2
                    
                elif volcano_type == 'cinder_cone':
                    # Cinder cones: moderate eruptions
                    max_intensity = 65
                    decay_rate = 0.4  # Faster decay
                    
                elif volcano_type == 'lava_dome':
                    # Lava domes: less explosive, longer-lasting
                    max_intensity = 50
                    decay_rate = 0.1  # Much slower decay
                    
                else:
                    # Default values
                    max_intensity = 70
                    decay_rate = 0.2
                
                # Calculate eruption intensity with decay over time
                eruption_intensity[i] = max_intensity * np.exp(-decay_rate * days_since)
                
                # During eruption, other indicators behave differently
                seismic_activity[i] = 20 + eruption_intensity[i] * 0.5 + np.random.normal(0, 5)
                gas_emissions[i] = 40 + eruption_intensity[i] * 0.7 + np.random.normal(0, 7)
                deformation[i] = 10 - days_since * 0.5 + np.random.normal(0, 1)  # Decreases after eruption
                temperature[i] = 30 + eruption_intensity[i] * 0.6 + np.random.normal(0, 4)
                
                # Ensure deformation doesn't go negative
                deformation[i] = max(deformation[i], 0)
        
        # Ensure non-negative values for all series
        seismic_activity = np.maximum(seismic_activity, 0)
        gas_emissions = np.maximum(gas_emissions, 0)
        deformation = np.maximum(deformation, 0)
        temperature = np.maximum(temperature, 0)
    
    # Return the time series data
    return {
        'time': time_points.tolist(),
        'seismic_activity': seismic_activity.tolist(),
        'gas_emissions': gas_emissions.tolist(),
        'deformation': deformation.tolist(),
        'temperature': temperature.tolist(),
        'eruption_intensity': eruption_intensity.tolist(),
        'eruption_occurred': eruption_occurs
    }