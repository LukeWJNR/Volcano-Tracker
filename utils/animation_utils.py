"""
Utility functions for creating volcano animations based on InSAR data and scientific models.

This module provides functionality to generate animated visualizations of different volcano types,
eruption processes, and deformation patterns derived from real InSAR data. It also includes
comprehensive eruption sequence animations showing the full lifecycle from magma buildup to eruption.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import time
import json
import os
from datetime import datetime, timedelta

from utils.comet_utils import (
    get_matching_comet_volcano,
    get_comet_volcano_sar_data,
    display_comet_sar_animation
)

# Constants for different volcano types - Updated based on scientific research
VOLCANO_TYPES = {
    "shield": {
        "description": "Broad, gently sloping volcanoes built by fluid lava flows, with extensive volcanic plumbing systems featuring connected shallow and deep magma reservoirs",
        "examples": ["Mauna Loa", "Kilauea", "Fernandina"],
        "magma_viscosity": "low",
        "eruption_style": "effusive",
        "deformation_pattern": "radial expansion",
        "chamber_depth": "5-7 km (shallow chamber), 15-20 km (deep reservoir)",
        "conduit_type": "Complex network with central and lateral dikes",
        "plumbing_system": "Deep crustal reservoir feeding a shallow magma chamber, with complex dike networks allowing lateral magma transport",
        "secondary_features": "Rift zones with lateral dike swarms"
    },
    "stratovolcano": {
        "description": "Steep-sided, symmetrical cones built by alternating layers of lava flows, ash, and blocks, with vertically-oriented magmatic plumbing systems",
        "examples": ["Mount Fuji", "Mount St. Helens", "Mount Vesuvius"],
        "magma_viscosity": "high",
        "eruption_style": "explosive",
        "deformation_pattern": "asymmetric inflation",
        "chamber_depth": "5-10 km (shallow chamber), 15-25 km (deep reservoir)",
        "conduit_type": "Central conduit with potential satellite dykes",
        "plumbing_system": "Deep magma reservoir feeding into a shallow chamber with complex internal structure; vertical transport dominates",
        "secondary_features": "Potential sills and secondary vents on flanks"
    },
    "caldera": {
        "description": "Circular depression formed by collapse of the surface into an emptied magma chamber, with large-volume, complex magmatic systems",
        "examples": ["Yellowstone", "Santorini", "Crater Lake"],
        "magma_viscosity": "variable",
        "eruption_style": "highly explosive",
        "deformation_pattern": "complex uplift/subsidence",
        "chamber_depth": "3-5 km (shallow chamber), 10-15 km (deep reservoir)",
        "conduit_type": "Ring fracture system with multiple vents",
        "plumbing_system": "Large, extensive magma reservoir with ring-shaped fracture system and multiple pathways",
        "secondary_features": "Ring dikes, cone sheets, and satellite vents"
    },
    "cinder_cone": {
        "description": "Small, steep-sided cones built from ejected lava fragments, typically with simple, short-lived plumbing systems",
        "examples": ["Paricutin", "Cerro Negro", "SP Crater"],
        "magma_viscosity": "moderate",
        "eruption_style": "strombolian",
        "deformation_pattern": "localized uplift",
        "chamber_depth": "2-5 km (typically shallow system)",
        "conduit_type": "Single central conduit",
        "plumbing_system": "Simple direct connection to a shallow magma pocket, often as an offshoot from a larger system",
        "secondary_features": "Limited satellite vents possible"
    },
    "lava_dome": {
        "description": "Rounded, steep-sided mass of viscous lava extruded from a volcanic vent, with complex magmatic plumbing featuring multiple interacting reservoirs",
        "examples": ["Mount St. Helens dome", "Soufriere Hills", "Santiaguito"],
        "magma_viscosity": "very high",
        "eruption_style": "effusive to explosive",
        "deformation_pattern": "localized uplift with radial fracturing",
        "chamber_depth": "4-7 km (main chamber), with potential deeper reservoirs",
        "conduit_type": "Narrow, often partly crystallized conduit",
        "plumbing_system": "Complex system with magma storage at multiple levels and potential gas accumulation beneath solidified plugs",
        "secondary_features": "Spine formations, internal dykes, and gas pocket development"
    }
}

# Constants for alert levels and their properties
ALERT_LEVELS = {
    "Normal": {
        "color": "green",
        "description": "Volcano is in typical background, non-eruptive state",
        "deformation_rate": "minimal",
        "activity": "low"
    },
    "Advisory": {
        "color": "yellow",
        "description": "Volcano is exhibiting signs of elevated unrest above known background level",
        "deformation_rate": "slight",
        "activity": "moderate"
    },
    "Watch": {
        "color": "orange",
        "description": "Volcano is exhibiting heightened or escalating unrest with increased potential of eruption",
        "deformation_rate": "significant",
        "activity": "high"
    },
    "Warning": {
        "color": "red",
        "description": "Hazardous eruption is imminent, underway, or suspected",
        "deformation_rate": "extreme",
        "activity": "very high"
    }
}

def determine_volcano_type(volcano_data: Dict) -> str:
    """
    Determine the volcano type from the volcano data
    
    Args:
        volcano_data (Dict): Volcano information dictionary
        
    Returns:
        str: Volcano type category
    """
    volcano_type = volcano_data.get('type', '').lower()
    
    # Match the type to our defined categories
    if 'shield' in volcano_type:
        return 'shield'
    elif 'strato' in volcano_type or 'composite' in volcano_type:
        return 'stratovolcano'
    elif 'caldera' in volcano_type:
        return 'caldera'
    elif 'cinder' in volcano_type or 'cone' in volcano_type:
        return 'cinder_cone'
    elif 'dome' in volcano_type:
        return 'lava_dome'
    else:
        # Default to stratovolcano as the most common type
        return 'stratovolcano'

def generate_magma_chamber_animation(volcano_type: str, 
                                     alert_level: str, 
                                     num_frames: int = 100,
                                     time_period_days: int = 30) -> Dict:
    """
    Generate an animation of magma chamber dynamics for a specific volcano type and alert level
    
    Args:
        volcano_type (str): Type of volcano
        alert_level (str): Current alert level
        num_frames (int): Number of frames in the animation
        time_period_days (int): Time period covered by the animation in days
        
    Returns:
        Dict: Dictionary with animation figure and metadata
    """
    # Get parameters based on volcano type and alert level
    v_params = VOLCANO_TYPES.get(volcano_type, VOLCANO_TYPES['stratovolcano'])
    a_params = ALERT_LEVELS.get(alert_level, ALERT_LEVELS['Normal'])
    
    # Base deformation rate multiplier based on alert level
    deformation_rates = {
        "Normal": 0.1,
        "Advisory": 0.5,
        "Watch": 1.0,
        "Warning": 2.0
    }
    deformation_rate = deformation_rates.get(alert_level, 0.1)
    
    # Time related parameters
    dates = [datetime.now() + timedelta(days=i*time_period_days/num_frames) for i in range(num_frames)]
    date_strings = [d.strftime("%Y-%m-%d") for d in dates]
    
    # Prepare data structure for animation
    magma_volume = []
    surface_displacement = []
    pressure = []
    
    # Base pattern depends on volcano type
    if volcano_type == 'shield':
        # Shield volcanoes show gradual, steady magma accumulation
        base_pattern = np.linspace(0, 1, num_frames) * deformation_rate
        noise = np.random.normal(0, 0.05, num_frames)
        trend = base_pattern + noise
        
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes show more episodic accumulation
        base_pattern = np.cumsum(np.random.exponential(0.1, num_frames)) * deformation_rate
        base_pattern = base_pattern / np.max(base_pattern)  # Normalize
        noise = np.random.normal(0, 0.1, num_frames)
        trend = base_pattern + noise
        
    elif volcano_type == 'caldera':
        # Calderas can show complex patterns of inflation and deflation
        t = np.linspace(0, 4*np.pi, num_frames)
        base_pattern = (np.sin(t) * 0.3 + np.cumsum(np.random.exponential(0.05, num_frames))) * deformation_rate
        base_pattern = base_pattern / np.max(np.abs(base_pattern)) # Normalize
        noise = np.random.normal(0, 0.15, num_frames)
        trend = base_pattern + noise
        
    elif volcano_type == 'cinder_cone':
        # Cinder cones show rapid, pulsating changes
        base_pattern = np.cumsum(np.random.exponential(0.15, num_frames)) * deformation_rate
        base_pattern = base_pattern / np.max(base_pattern)  # Normalize
        pulsations = np.sin(np.linspace(0, 8*np.pi, num_frames)) * 0.2
        trend = base_pattern + pulsations
        
    elif volcano_type == 'lava_dome':
        # Lava domes show steady pressure buildup with potential drops
        base_pattern = np.linspace(0, 1, num_frames) * deformation_rate
        
        # Add random pressure drops
        for i in range(3):
            drop_point = np.random.randint(num_frames//4, num_frames-10)
            drop_amount = np.random.uniform(0.1, 0.3)
            base_pattern[drop_point:] -= drop_amount
            
        noise = np.random.normal(0, 0.07, num_frames)
        trend = base_pattern + noise
        
    else:
        # Default pattern
        trend = np.cumsum(np.random.normal(0, 0.05, num_frames)) * deformation_rate
    
    # Ensure trend is positive and normalized
    trend = trend - np.min(trend)
    if np.max(trend) > 0:
        trend = trend / np.max(trend)
    
    # Generate the derived values based on the trend
    for i in range(num_frames):
        t = trend[i]
        
        # Magma volume follows the trend directly
        volume = t
        magma_volume.append(volume)
        
        # Surface displacement is related to volume but with a lag
        if i > 5:
            disp = trend[i-5] * 0.8
        else:
            disp = trend[i] * 0.5
        surface_displacement.append(disp)
        
        # Pressure is more variable and reflects instantaneous changes
        if i > 0:
            pres = (trend[i] - trend[i-1]) * 5 + trend[i] * 0.5
        else:
            pres = trend[i] * 0.5
        pressure.append(pres)
    
    # Create data frame for plotting
    df = pd.DataFrame({
        'Date': date_strings,
        'Magma Volume': magma_volume,
        'Surface Displacement': surface_displacement,
        'Pressure': pressure
    })
    
    # Create animated plot
    fig = make_subplots(rows=3, cols=1, 
                        shared_xaxes=True,
                        subplot_titles=('Magma Chamber Volume', 'Surface Displacement', 'Pressure'),
                        vertical_spacing=0.1)
    
    # Define the color scale based on alert level
    alert_colors = {
        'Normal': 'green',
        'Advisory': 'yellow',
        'Watch': 'orange',
        'Warning': 'red'
    }
    color = alert_colors.get(alert_level, 'blue')
    
    # Add traces for each parameter
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Magma Volume'],
            mode='lines',
            name='Magma Volume',
            line=dict(color=color, width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Surface Displacement'],
            mode='lines',
            name='Surface Displacement',
            line=dict(color=color, width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Pressure'],
            mode='lines',
            name='Pressure',
            line=dict(color=color, width=2)
        ),
        row=3, col=1
    )
    
    # Add moving marker for animation
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][0]],
            y=[df['Magma Volume'][0]],
            mode='markers',
            marker=dict(size=10, color=color, line=dict(width=2, color='white')),
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][0]],
            y=[df['Surface Displacement'][0]],
            mode='markers',
            marker=dict(size=10, color=color, line=dict(width=2, color='white')),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][0]],
            y=[df['Pressure'][0]],
            mode='markers',
            marker=dict(size=10, color=color, line=dict(width=2, color='white')),
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Create animation frames
    frames = []
    for i in range(num_frames):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=df['Date'][:i+1],
                        y=df['Magma Volume'][:i+1],
                        mode='lines',
                        line=dict(color=color, width=2)
                    ),
                    go.Scatter(
                        x=df['Date'][:i+1],
                        y=df['Surface Displacement'][:i+1],
                        mode='lines',
                        line=dict(color=color, width=2)
                    ),
                    go.Scatter(
                        x=df['Date'][:i+1],
                        y=df['Pressure'][:i+1],
                        mode='lines',
                        line=dict(color=color, width=2)
                    ),
                    go.Scatter(
                        x=[df['Date'][i]],
                        y=[df['Magma Volume'][i]],
                        mode='markers',
                        marker=dict(size=10, color=color, line=dict(width=2, color='white'))
                    ),
                    go.Scatter(
                        x=[df['Date'][i]],
                        y=[df['Surface Displacement'][i]],
                        mode='markers',
                        marker=dict(size=10, color=color, line=dict(width=2, color='white'))
                    ),
                    go.Scatter(
                        x=[df['Date'][i]],
                        y=[df['Pressure'][i]],
                        mode='markers',
                        marker=dict(size=10, color=color, line=dict(width=2, color='white'))
                    )
                ],
                traces=[0, 1, 2, 3, 4, 5]
            )
        )
    
    # Update layout and add animation
    fig.update_layout(
        title=f"{volcano_type.replace('_', ' ').title()} Volcano - {alert_level} Alert Level",
        height=600,
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 50, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 0}
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }
            ],
            'x': 0.1,
            'y': 1.15
        }]
    )
    
    fig.frames = frames
    
    # Prepare output dictionary
    animation_data = {
        'figure': fig,
        'volcano_type': volcano_type,
        'alert_level': alert_level,
        'v_params': v_params,
        'a_params': a_params,
        'data': df.to_dict(orient='list')
    }
    
    return animation_data

def generate_deformation_plot(volcano_data: Dict, alert_level: str = None) -> Dict:
    """
    Generate a surface deformation plot for a volcano using InSAR-like visualization
    
    Args:
        volcano_data (Dict): Volcano data dictionary
        alert_level (str, optional): Alert level to use. If None, uses the level from volcano_data
        
    Returns:
        Dict: Dictionary with deformation figure and metadata
    """
    # Use provided alert level or get from volcano data
    if alert_level is None:
        alert_level = volcano_data.get('alert_level', 'Normal')
    
    # Determine volcano type
    volcano_type = determine_volcano_type(volcano_data)
    v_params = VOLCANO_TYPES.get(volcano_type, VOLCANO_TYPES['stratovolcano'])
    
    # Set up grid for deformation pattern
    n = 100  # Grid size
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    X, Y = np.meshgrid(x, y)
    
    # Distance from center
    R = np.sqrt(X**2 + Y**2)
    
    # Base deformation pattern based on volcano type
    if volcano_type == 'shield':
        # Shield volcanoes typically show radial, symmetric deformation
        Z = np.exp(-0.5 * R**2) * np.cos(R * 2)
        
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes can show more asymmetric patterns
        # Introduce asymmetry by adding a directional component
        theta = np.arctan2(Y, X)
        asymmetry = 0.5 * np.cos(theta * 3)
        Z = np.exp(-0.4 * R**2) * np.cos(R * 2.5) * (1 + asymmetry)
        
    elif volcano_type == 'caldera':
        # Calderas often show complex ring-like patterns
        Z = np.exp(-0.3 * (R - 2.5)**2) * np.cos(R * 3)
        
    elif volcano_type == 'cinder_cone':
        # Cinder cones show very localized deformation
        Z = np.exp(-R**2) * np.cos(R * 1.5)
        
    elif volcano_type == 'lava_dome':
        # Lava domes show concentrated deformation with radial fractures
        Z = np.exp(-0.7 * R**2) * np.cos(R * 3.5)
        # Add radial fracture patterns
        theta = np.arctan2(Y, X)
        fractures = 0.3 * np.sin(theta * 6)**2
        Z = Z * (1 - fractures)
        
    else:
        # Default pattern
        Z = np.exp(-0.5 * R**2) * np.cos(R * 2)
    
    # Scale deformation amplitude based on alert level
    deformation_scale = {
        "Normal": 0.3,
        "Advisory": 0.6,
        "Watch": 1.0,
        "Warning": 1.5
    }
    scale = deformation_scale.get(alert_level, 0.3)
    Z = Z * scale
    
    # Create InSAR-like colorized wrapped phase visualization
    # Wrap the phase to simulate interferometric fringes
    Z_wrapped = np.angle(np.exp(1j * Z * 6))
    
    # Create plot
    fig = go.Figure(data=go.Contour(
        z=Z_wrapped,
        x=x,
        y=y,
        colorscale='Jet',
        contours=dict(
            start=-np.pi,
            end=np.pi,
            size=np.pi/4,
            showlabels=True,
            labelfont=dict(
                size=10,
                color='white'
            )
        ),
        colorbar=dict(
            title='Phase (rad)',
            tickvals=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi],
            ticktext=['-π', '-π/2', '0', 'π/2', 'π']
        )
    ))
    
    # Add title and axis labels
    fig.update_layout(
        title=f"Simulated InSAR Deformation Pattern - {volcano_data['name']} ({volcano_type.replace('_', ' ').title()})",
        xaxis_title="East-West Distance (km)",
        yaxis_title="North-South Distance (km)",
        width=700,
        height=600
    )
    
    # Create 3D surface visualization of unwrapped deformation
    fig3d = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale='Viridis')])
    fig3d.update_layout(
        title=f"3D Surface Deformation - {volcano_data['name']} ({volcano_type.replace('_', ' ').title()})",
        scene=dict(
            xaxis_title="East-West Distance (km)",
            yaxis_title="North-South Distance (km)",
            zaxis_title="Displacement (cm)",
            camera=dict(
                eye=dict(x=1.5, y=-1.5, z=1.2)
            )
        ),
        width=700,
        height=600
    )
    
    # Prepare output dictionary
    deformation_data = {
        '2d_figure': fig,
        '3d_figure': fig3d,
        'volcano_type': volcano_type,
        'alert_level': alert_level,
        'v_params': v_params,
        'max_deformation': np.max(np.abs(Z)) * 2.8  # Convert to cm (one fringe ≈ 2.8 cm)
    }
    
    return deformation_data

def generate_eruption_sequence_animation(volcano_data: Dict, time_steps: int = 50) -> Dict:
    """
    Generate an animated sequence showing the progression of a volcanic eruption
    
    Args:
        volcano_data (Dict): Volcano data dictionary
        time_steps (int): Number of time steps in the animation
        
    Returns:
        Dict: Dictionary with animation figures and metadata
    """
    # Determine volcano type
    volcano_type = determine_volcano_type(volcano_data)
    v_params = VOLCANO_TYPES.get(volcano_type, VOLCANO_TYPES['stratovolcano'])
    
    # Create timeline of eruption phases
    phases = []
    if volcano_type == 'shield':
        phases = [
            {'name': 'Initial Fissure Formation', 'duration': 0.1},
            {'name': 'Lava Fountaining', 'duration': 0.2},
            {'name': 'Main Effusive Phase', 'duration': 0.5},
            {'name': 'Waning Activity', 'duration': 0.2}
        ]
    elif volcano_type == 'stratovolcano':
        phases = [
            {'name': 'Phreatic Explosions', 'duration': 0.1},
            {'name': 'Dome Growth', 'duration': 0.2},
            {'name': 'Explosive Eruption', 'duration': 0.3},
            {'name': 'Pyroclastic Flows', 'duration': 0.2},
            {'name': 'Ash Fallout', 'duration': 0.2}
        ]
    elif volcano_type == 'caldera':
        phases = [
            {'name': 'Initial Venting', 'duration': 0.05},
            {'name': 'Plinian Eruption', 'duration': 0.25},
            {'name': 'Caldera Collapse', 'duration': 0.2},
            {'name': 'Pyroclastic Density Currents', 'duration': 0.3},
            {'name': 'Ash Fallout', 'duration': 0.2}
        ]
    elif volcano_type == 'cinder_cone':
        phases = [
            {'name': 'Initial Vent Opening', 'duration': 0.1},
            {'name': 'Strombolian Explosions', 'duration': 0.5},
            {'name': 'Cone Building', 'duration': 0.3},
            {'name': 'Terminal Lava Flow', 'duration': 0.1}
        ]
    elif volcano_type == 'lava_dome':
        phases = [
            {'name': 'Initial Extrusion', 'duration': 0.2},
            {'name': 'Dome Growth', 'duration': 0.4},
            {'name': 'Partial Collapse', 'duration': 0.1},
            {'name': 'Renewed Extrusion', 'duration': 0.3}
        ]
    
    # Calculate cumulative time points
    cumulative = 0
    for phase in phases:
        phase['start'] = cumulative
        cumulative += phase['duration']
        phase['end'] = cumulative
    
    # Normalize to ensure total is 1.0
    for phase in phases:
        phase['start'] /= cumulative
        phase['end'] /= cumulative
    
    # Generate data for the animation
    time_points = np.linspace(0, 1, time_steps)
    current_phases = []
    
    for t in time_points:
        current_phase = next((p['name'] for p in phases if p['start'] <= t < p['end']), 'Post-Eruption')
        current_phases.append(current_phase)
    
    # Create activity metrics for each time point
    # These will be different based on volcano type
    lava_flux = []
    ash_emission = []
    seismicity = []
    deformation = []
    gas_emission = []
    
    for i, t in enumerate(time_points):
        phase = current_phases[i]
        
        # Base pattern - rise and fall
        base_curve = np.sin(t * np.pi) if t <= 1 else 0
        
        # Add variations based on volcano type and phase
        if volcano_type == 'shield':
            # Shield volcanoes: high lava flux, low explosivity
            lava_component = base_curve * 1.0 + 0.2 * np.sin(t * 20)
            ash_component = base_curve * 0.3 + 0.1 * np.sin(t * 15)
            seismic_component = base_curve * 0.5 + 0.3 * np.sin(t * 10)
            deform_component = 0.8 * np.cos(t * np.pi/2) if t <= 1 else 0
            gas_component = base_curve * 0.7 + 0.2 * np.sin(t * 8)
            
        elif volcano_type == 'stratovolcano':
            # Stratovolcanoes: explosive with moderate lava
            lava_component = base_curve * 0.6 + 0.2 * np.sin(t * 12)
            ash_component = base_curve * 0.9 + 0.3 * np.sin(t * 8)
            seismic_component = base_curve * 0.8 + 0.4 * np.sin(t * 15)
            deform_component = 0.9 * np.exp(-3 * t) * np.cos(t * 5)
            gas_component = base_curve * 0.8 + 0.3 * np.sin(t * 10)
            
        elif volcano_type == 'caldera':
            # Calderas: highly explosive, complex patterns
            lava_component = base_curve * 0.4 + 0.3 * np.sin(t * 18)
            ash_component = base_curve * 1.0 + 0.5 * np.sin(t * 12)
            seismic_component = base_curve * 0.9 + 0.6 * np.sin(t * 20)
            # Complex deformation with inflation followed by collapse
            if t < 0.4:
                deform_component = 0.8 * t * 2.5
            else:
                deform_component = 0.8 * (1 - (t - 0.4) * 1.67)
            gas_component = base_curve * 0.9 + 0.4 * np.sin(t * 15)
            
        elif volcano_type == 'cinder_cone':
            # Cinder cones: intermittent explosivity, moderate lava
            lava_component = base_curve * 0.5 + 0.3 * np.sin(t * 25)
            ash_component = base_curve * 0.7 + 0.4 * np.sin(t * 20)
            # More pulsating seismicity
            seismic_component = base_curve * 0.6 + 0.5 * np.sin(t * 30)
            deform_component = 0.7 * np.exp(-2 * t) * np.cos(t * 8)
            gas_component = base_curve * 0.6 + 0.3 * np.sin(t * 12)
            
        elif volcano_type == 'lava_dome':
            # Lava domes: high viscosity, low flux, occasional explosions
            lava_component = base_curve * 0.4 + 0.1 * np.sin(t * 10)
            ash_component = base_curve * 0.5 + 0.6 * np.sin(t * 30)  # Spiky from collapses
            seismic_component = base_curve * 0.7 + 0.5 * np.sin(t * 25)
            deform_component = 0.6 * np.exp(-1 * t) * np.cos(t * 3)
            gas_component = base_curve * 0.5 + 0.2 * np.sin(t * 15)
        
        else:
            # Default patterns
            lava_component = base_curve * 0.7 + 0.2 * np.sin(t * 15)
            ash_component = base_curve * 0.7 + 0.2 * np.sin(t * 15)
            seismic_component = base_curve * 0.7 + 0.2 * np.sin(t * 15)
            deform_component = 0.7 * np.exp(-2 * t) * np.cos(t * 6)
            gas_component = base_curve * 0.7 + 0.2 * np.sin(t * 15)
        
        # Ensure values are positive or zero
        lava_flux.append(max(0, lava_component))
        ash_emission.append(max(0, ash_component))
        seismicity.append(max(0, seismic_component))
        deformation.append(deform_component)  # Can be negative (deflation)
        gas_emission.append(max(0, gas_component))
    
    # Create time labels (e.g., "Day 1", "Day 2", etc.)
    time_labels = [f"Day {int(i*30/time_steps)+1}" for i in range(time_steps)]
    
    # Create dataframe for plotting
    df = pd.DataFrame({
        'Time': time_labels,
        'Phase': current_phases,
        'Lava Flux': lava_flux,
        'Ash Emission': ash_emission,
        'Seismicity': seismicity,
        'Deformation': deformation,
        'Gas Emission': gas_emission
    })
    
    # Create animation plot
    fig = make_subplots(rows=5, cols=1, 
                        shared_xaxes=True,
                        subplot_titles=('Lava Flux', 'Ash Emission', 'Seismicity', 'Deformation', 'Gas Emission'),
                        vertical_spacing=0.05,
                        row_heights=[0.2, 0.2, 0.2, 0.2, 0.2])
    
    # Add traces for each parameter
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Lava Flux'],
            mode='lines',
            name='Lava Flux',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Ash Emission'],
            mode='lines',
            name='Ash Emission',
            line=dict(color='gray', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Seismicity'],
            mode='lines',
            name='Seismicity',
            line=dict(color='purple', width=2)
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Deformation'],
            mode='lines',
            name='Deformation',
            line=dict(color='blue', width=2)
        ),
        row=4, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Time'],
            y=df['Gas Emission'],
            mode='lines',
            name='Gas Emission',
            line=dict(color='yellow', width=2)
        ),
        row=5, col=1
    )
    
    # Add markers for current position
    for i in range(5):
        fig.add_trace(
            go.Scatter(
                x=[df['Time'][0]],
                y=[df[['Lava Flux', 'Ash Emission', 'Seismicity', 'Deformation', 'Gas Emission'][i]][0]],
                mode='markers',
                marker=dict(size=10, color='white', line=dict(width=2, color='black')),
                showlegend=False
            ),
            row=i+1, col=1
        )
    
    # Add phase indicator
    current_phase_text = df['Phase'][0]
    fig.add_annotation(
        x=0.5,
        y=1.12,
        xref="paper",
        yref="paper",
        text=f"Current Phase: {current_phase_text}",
        showarrow=False,
        font=dict(size=16),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1,
        borderpad=4
    )
    
    # Create animation frames
    frames = []
    for i in range(time_steps):
        frames.append(
            go.Frame(
                data=[
                    # Line traces
                    go.Scatter(
                        x=df['Time'][:i+1],
                        y=df['Lava Flux'][:i+1],
                        mode='lines',
                        line=dict(color='red', width=2)
                    ),
                    go.Scatter(
                        x=df['Time'][:i+1],
                        y=df['Ash Emission'][:i+1],
                        mode='lines',
                        line=dict(color='gray', width=2)
                    ),
                    go.Scatter(
                        x=df['Time'][:i+1],
                        y=df['Seismicity'][:i+1],
                        mode='lines',
                        line=dict(color='purple', width=2)
                    ),
                    go.Scatter(
                        x=df['Time'][:i+1],
                        y=df['Deformation'][:i+1],
                        mode='lines',
                        line=dict(color='blue', width=2)
                    ),
                    go.Scatter(
                        x=df['Time'][:i+1],
                        y=df['Gas Emission'][:i+1],
                        mode='lines',
                        line=dict(color='yellow', width=2)
                    ),
                    # Marker traces
                    go.Scatter(
                        x=[df['Time'][i]],
                        y=[df['Lava Flux'][i]],
                        mode='markers',
                        marker=dict(size=10, color='white', line=dict(width=2, color='black'))
                    ),
                    go.Scatter(
                        x=[df['Time'][i]],
                        y=[df['Ash Emission'][i]],
                        mode='markers',
                        marker=dict(size=10, color='white', line=dict(width=2, color='black'))
                    ),
                    go.Scatter(
                        x=[df['Time'][i]],
                        y=[df['Seismicity'][i]],
                        mode='markers',
                        marker=dict(size=10, color='white', line=dict(width=2, color='black'))
                    ),
                    go.Scatter(
                        x=[df['Time'][i]],
                        y=[df['Deformation'][i]],
                        mode='markers',
                        marker=dict(size=10, color='white', line=dict(width=2, color='black'))
                    ),
                    go.Scatter(
                        x=[df['Time'][i]],
                        y=[df['Gas Emission'][i]],
                        mode='markers',
                        marker=dict(size=10, color='white', line=dict(width=2, color='black'))
                    )
                ],
                traces=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                layout=go.Layout(
                    annotations=[
                        dict(
                            x=0.5,
                            y=1.12,
                            xref="paper",
                            yref="paper",
                            text=f"Current Phase: {df['Phase'][i]}",
                            showarrow=False,
                            font=dict(size=16),
                            bgcolor="rgba(255, 255, 255, 0.8)",
                            bordercolor="black",
                            borderwidth=1,
                            borderpad=4
                        )
                    ]
                )
            )
        )
    
    # Update layout and add animation
    fig.update_layout(
        title=f"Eruption Sequence - {volcano_data['name']} ({volcano_type.replace('_', ' ').title()})",
        height=800,
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 0}
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }
            ],
            'x': 0.1,
            'y': 1.15
        }]
    )
    
    fig.frames = frames
    
    # Prepare output dictionary
    animation_data = {
        'figure': fig,
        'volcano_type': volcano_type,
        'v_params': v_params,
        'phases': phases,
        'data': df.to_dict(orient='list')
    }
    
    return animation_data