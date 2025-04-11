"""
Cinematic volcano eruption animation utilities.

This module provides functions to create movie-like animated visualizations
of volcanic eruptions, showing the complete process from magma buildup to eruption.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import math

from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS

def generate_cinematic_eruption(volcano_data: Dict, frames: int = 120) -> Dict:
    """
    Generate a cinematic animation of a volcanic eruption from magma buildup to ash cloud.
    
    Args:
        volcano_data (Dict): Volcano data dictionary
        frames (int): Number of frames in the animation
        
    Returns:
        Dict: Dictionary with animation data and metadata
    """
    # Determine volcano type
    volcano_type = determine_volcano_type(volcano_data)
    volcano_name = volcano_data.get('name', 'Volcano')
    
    # Create figure with appropriate aspect ratio for cinematic view
    fig = go.Figure()
    
    # Set up the scene with appropriate dimensions
    # For most volcanoes, we need more vertical space
    x_range = [-10, 10]
    y_range = [-10, 10]
    z_range = [-8, 20]  # Extra height for ash clouds and eruption columns
    
    # Generate ground surface based on volcano type
    resolution = 50
    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)
    
    # Calculate distance from center
    R = np.sqrt(X**2 + Y**2)
    
    # Base surface shape depends on volcano type
    if volcano_type == 'shield':
        # Shield volcanoes have gently sloping sides
        Z_surface = 5 * np.exp(-0.05 * R**2)
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes are steeper
        Z_surface = 10 * np.exp(-0.15 * R**2)
    elif volcano_type == 'caldera':
        # Calderas have a depression
        Z_surface = 4 * np.exp(-0.05 * R**2) - 2 * np.exp(-0.5 * R**2)
    elif volcano_type == 'cinder_cone':
        # Cinder cones are steep and smaller
        Z_surface = 6 * np.exp(-0.3 * R**2) - 2 * np.exp(-2.0 * R**2)
    elif volcano_type == 'lava_dome':
        # Lava domes are bulbous
        Z_surface = 4 * np.exp(-0.25 * R**2)
    else:
        # Default
        Z_surface = 8 * np.exp(-0.1 * R**2)
    
    # Generate magma chamber
    chamber_depth = -5 if volcano_type == 'stratovolcano' else -3
    chamber_x = np.linspace(-4, 4, 30)
    chamber_y = np.linspace(-4, 4, 30)
    chamber_X, chamber_Y = np.meshgrid(chamber_x, chamber_y)
    chamber_R = np.sqrt(chamber_X**2 + chamber_Y**2)
    chamber_Z = chamber_depth - 1.5 * np.exp(-0.15 * chamber_R**2)
    
    # Conduit parameters
    if volcano_type == 'shield':
        conduit_radius = 0.5
        vent_radius = 0.8
    elif volcano_type == 'stratovolcano':
        conduit_radius = 0.4
        vent_radius = 0.6
    elif volcano_type == 'caldera':
        conduit_radius = 0.6
        vent_radius = 1.0
    elif volcano_type == 'cinder_cone':
        conduit_radius = 0.3
        vent_radius = 0.5
    elif volcano_type == 'lava_dome':
        conduit_radius = 0.7
        vent_radius = 0.9
    else:
        conduit_radius = 0.5
        vent_radius = 0.7
    
    # Get the summit height
    summit_height = np.max(Z_surface)
    
    # Generate conduit between magma chamber and surface
    theta = np.linspace(0, 2*np.pi, 20)
    conduit_heights = np.linspace(chamber_depth, summit_height, 30)
    conduit_coords = []
    for h in conduit_heights:
        # Conduit radius varies with height (wider near chamber, narrower near surface)
        radius_factor = (h - chamber_depth) / (summit_height - chamber_depth)
        r = conduit_radius * (1 - 0.5 * radius_factor)
        for t in theta:
            x = r * np.cos(t)
            y = r * np.sin(t)
            conduit_coords.append((x, y, h))
    
    # Define frames for the animation sequence
    # Each frame needs to show changes in the volcano state
    
    # We'll divide the animation into phases:
    # 1. Initial state (10% of frames)
    # 2. Magma buildup and deformation (30% of frames)
    # 3. Initial eruption (15% of frames)
    # 4. Main eruption phase (30% of frames)
    # 5. Waning activity (15% of frames)
    
    phase_frames = {
        'initial': int(frames * 0.1),
        'buildup': int(frames * 0.3),
        'initial_eruption': int(frames * 0.15),
        'main_eruption': int(frames * 0.3),
        'waning': frames - int(frames * 0.1) - int(frames * 0.3) - int(frames * 0.15) - int(frames * 0.3)
    }
    
    # Parameters that change during animation
    animation_data = {
        'frame': list(range(frames)),
        'phase': [],
        'deformation': [],
        'magma_level': [],
        'eruption_height': [],
        'lava_flow': [],
        'ash_density': []
    }
    
    # Deformation - how much the ground surface bulges
    deformation_max = 1.0 if volcano_type in ['stratovolcano', 'shield'] else 0.5
    
    # Magma level - how high the magma reaches in the conduit
    magma_level_max = summit_height if volcano_type != 'caldera' else summit_height - 1
    
    # Eruption height - how high the eruption column goes
    if volcano_type == 'stratovolcano':
        eruption_height_max = 15
    elif volcano_type == 'shield':
        eruption_height_max = 8
    elif volcano_type == 'caldera':
        eruption_height_max = 18
    elif volcano_type == 'cinder_cone':
        eruption_height_max = 12
    else:
        eruption_height_max = 10
    
    # Lava flow - extent of lava flows (for shield volcanoes this is higher)
    lava_flow_max = 8 if volcano_type == 'shield' else 4
    
    # Ash density - amount of ash produced (higher for explosive eruptions)
    if volcano_type in ['stratovolcano', 'caldera']:
        ash_density_max = 1.0
    elif volcano_type == 'cinder_cone':
        ash_density_max = 0.7
    elif volcano_type == 'lava_dome':
        ash_density_max = 0.5
    else:
        ash_density_max = 0.2  # Shield volcanoes produce less ash
    
    # Generate data for each frame
    current_frame = 0
    
    # Initial state phase
    for i in range(phase_frames['initial']):
        animation_data['phase'].append('initial')
        animation_data['deformation'].append(0)
        animation_data['magma_level'].append(chamber_depth * 0.8)  # Start with magma deep down
        animation_data['eruption_height'].append(0)
        animation_data['lava_flow'].append(0)
        animation_data['ash_density'].append(0)
        current_frame += 1
    
    # Buildup phase - increasing deformation and magma level
    for i in range(phase_frames['buildup']):
        progress = i / phase_frames['buildup']
        animation_data['phase'].append('buildup')
        animation_data['deformation'].append(progress * deformation_max * 0.8)  # 80% of max deformation
        animation_data['magma_level'].append(
            chamber_depth + progress * (summit_height * 0.9 - chamber_depth)
        )  # Magma rises toward surface
        animation_data['eruption_height'].append(0)
        animation_data['lava_flow'].append(0)
        animation_data['ash_density'].append(0)
        current_frame += 1
    
    # Initial eruption phase
    for i in range(phase_frames['initial_eruption']):
        progress = i / phase_frames['initial_eruption']
        animation_data['phase'].append('initial_eruption')
        
        # Deformation may decrease as pressure is released
        deform_factor = 0.8 - progress * 0.3
        animation_data['deformation'].append(deformation_max * deform_factor)
        
        # Magma reaches and slightly exceeds surface
        animation_data['magma_level'].append(summit_height + progress * 1.0)
        
        # Initial eruption column
        animation_data['eruption_height'].append(progress * eruption_height_max * 0.4)
        
        # Initial lava flows
        animation_data['lava_flow'].append(progress * lava_flow_max * 0.3)
        
        # Initial ash
        animation_data['ash_density'].append(progress * ash_density_max * 0.4)
        current_frame += 1
    
    # Main eruption phase
    for i in range(phase_frames['main_eruption']):
        progress = i / phase_frames['main_eruption']
        animation_data['phase'].append('main_eruption')
        
        # Deformation continues to decrease
        deform_factor = 0.5 - progress * 0.3
        animation_data['deformation'].append(max(0, deformation_max * deform_factor))
        
        # Magma level fluctuates slightly during eruption
        fluctuation = 0.5 * np.sin(progress * 6 * np.pi)
        animation_data['magma_level'].append(summit_height + 1.0 + fluctuation)
        
        # Eruption column reaches maximum then may fluctuate
        eruption_pattern = 0.7 + 0.3 * np.sin(progress * 4 * np.pi)
        animation_data['eruption_height'].append(eruption_height_max * eruption_pattern)
        
        # Lava flows increase steadily
        animation_data['lava_flow'].append(0.3 * lava_flow_max + progress * lava_flow_max * 0.7)
        
        # Ash density reaches peak then may fluctuate
        ash_pattern = 0.7 + 0.3 * np.sin(progress * 4 * np.pi)
        animation_data['ash_density'].append(ash_density_max * ash_pattern)
        current_frame += 1
    
    # Waning phase
    for i in range(phase_frames['waning']):
        progress = i / phase_frames['waning']
        animation_data['phase'].append('waning')
        
        # Deformation may increase slightly as magma drains back
        animation_data['deformation'].append(max(0, 0.2 * deformation_max * (1 - progress)))
        
        # Magma level drops
        animation_data['magma_level'].append(summit_height - progress * (summit_height - chamber_depth) * 0.5)
        
        # Eruption column decreases
        animation_data['eruption_height'].append(eruption_height_max * (1 - progress * 0.9))
        
        # Lava flows slow
        animation_data['lava_flow'].append(lava_flow_max * (1 - progress * 0.7))
        
        # Ash decreases
        animation_data['ash_density'].append(ash_density_max * (1 - progress * 0.8))
        current_frame += 1
    
    # Create the animation frames
    animation_frames = []
    
    # Colors for different elements
    ground_color = 'rgb(120, 108, 89)'  # Brown for ground
    magma_color = 'rgb(255, 69, 0)'     # Orange-red for magma
    lava_color = 'rgb(255, 0, 0)'       # Red for fresh lava
    eruption_color = 'rgba(255, 69, 0, 0.8)'  # Semi-transparent orange-red for eruption column
    ash_color = 'rgba(105, 105, 105, 0.7)'  # Semi-transparent gray for ash
    
    for frame_idx in range(frames):
        # Get data for this frame
        phase = animation_data['phase'][frame_idx]
        deformation = animation_data['deformation'][frame_idx]
        magma_level = animation_data['magma_level'][frame_idx]
        eruption_height = animation_data['eruption_height'][frame_idx]
        lava_flow = animation_data['lava_flow'][frame_idx]
        ash_density = animation_data['ash_density'][frame_idx]
        
        # Create frame data
        frame_data = []
        
        # 1. Ground surface with deformation
        Z_deformed = Z_surface.copy()
        if deformation > 0:
            # Apply deformation centered on the volcano
            bulge = deformation * np.exp(-0.2 * R**2)
            Z_deformed += bulge
        
        frame_data.append(
            go.Surface(
                x=X, y=Y, z=Z_deformed,
                colorscale=[[0, ground_color], [1, ground_color]],
                showscale=False,
                opacity=1.0
            )
        )
        
        # 2. Magma chamber (constant through animation)
        frame_data.append(
            go.Surface(
                x=chamber_X, y=chamber_Y, z=chamber_Z,
                colorscale=[[0, magma_color], [1, magma_color]],
                showscale=False,
                opacity=0.8
            )
        )
        
        # 3. Magma in conduit up to current magma level
        # Filter conduit points up to current level
        visible_conduit = [c for c in conduit_coords if c[2] <= magma_level]
        if visible_conduit:
            conduit_x = [c[0] for c in visible_conduit]
            conduit_y = [c[1] for c in visible_conduit]
            conduit_z = [c[2] for c in visible_conduit]
            
            frame_data.append(
                go.Scatter3d(
                    x=conduit_x, y=conduit_y, z=conduit_z,
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=magma_color,
                        opacity=0.9
                    ),
                    showlegend=False
                )
            )
        
        # 4. Eruption column if present
        if eruption_height > 0:
            # Create eruption column shape (wider at top)
            column_points = []
            column_heights = np.linspace(summit_height, summit_height + eruption_height, 20)
            
            for h_idx, h in enumerate(column_heights):
                # Column gets wider as it goes up
                height_fraction = h_idx / len(column_heights)
                r = vent_radius * (1 + height_fraction * 2.5)
                
                # More particles near the top for the eruption cloud
                if height_fraction > 0.7:
                    n_points = 30  # More points near top
                else:
                    n_points = 15
                
                for _ in range(n_points):
                    angle = np.random.uniform(0, 2*np.pi)
                    # Add randomness to radius
                    rand_r = r * np.random.uniform(0.7, 1.0)
                    x = rand_r * np.cos(angle)
                    y = rand_r * np.sin(angle)
                    # Add randomness to height
                    rand_h = h + np.random.uniform(-0.5, 0.5)
                    column_points.append((x, y, rand_h))
            
            # Add points for ash cloud at the top
            if ash_density > 0:
                cloud_height = summit_height + eruption_height
                cloud_radius = vent_radius * 3 * ash_density
                n_ash_points = int(100 * ash_density)
                
                for _ in range(n_ash_points):
                    angle = np.random.uniform(0, 2*np.pi)
                    # More spread at higher ash density
                    r = cloud_radius * np.random.uniform(0.5, 1.5) 
                    x = r * np.cos(angle)
                    y = r * np.sin(angle)
                    # Ash cloud has vertical dispersion too
                    z = cloud_height + np.random.uniform(-2, 2) * ash_density
                    column_points.append((x, y, z))
            
            # Add eruption column to frame
            if column_points:
                col_x = [p[0] for p in column_points]
                col_y = [p[1] for p in column_points]
                col_z = [p[2] for p in column_points]
                
                # Color mix between eruption color and ash color based on height
                colors = []
                for z in col_z:
                    if z < summit_height + eruption_height * 0.7:
                        colors.append(eruption_color)
                    else:
                        colors.append(ash_color)
                
                frame_data.append(
                    go.Scatter3d(
                        x=col_x, y=col_y, z=col_z,
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=colors,
                            opacity=0.8
                        ),
                        showlegend=False
                    )
                )
        
        # 5. Lava flows if present
        if lava_flow > 0:
            # Generate lava flow points radiating from summit
            flow_points = []
            
            # Number of flow directions depends on volcano type
            if volcano_type == 'shield':
                flow_directions = 8  # More flows for shield
            elif volcano_type == 'caldera':
                flow_directions = 6  # Multiple flows for caldera
            elif volcano_type == 'stratovolcano':
                flow_directions = 4  # Fewer, channelized flows
            else:
                flow_directions = 2  # Minimal flows for dome or cinder cone
            
            # Create flows in different directions
            for direction in range(flow_directions):
                angle = direction * (2 * np.pi / flow_directions)
                
                # Flow length depends on lava_flow parameter
                flow_length = lava_flow
                
                # Points along flow path
                n_points = 15
                for i in range(n_points):
                    # Distance from center
                    dist = flow_length * ((i+1) / n_points)
                    
                    # Add some randomness to flow path
                    angle_jitter = angle + np.random.uniform(-0.2, 0.2)
                    dist_jitter = dist * np.random.uniform(0.8, 1.2)
                    
                    # Calculate position
                    x = dist_jitter * np.cos(angle_jitter)
                    y = dist_jitter * np.sin(angle_jitter)
                    
                    # Calculate z based on ground elevation at this point
                    # Simplified - just follow slope downward
                    r = np.sqrt(x**2 + y**2)
                    
                    # Find approximate surface height at this position
                    # For simplicity, we use the radial function
                    if volcano_type == 'shield':
                        z = 5 * np.exp(-0.05 * r**2)
                    elif volcano_type == 'stratovolcano':
                        z = 10 * np.exp(-0.15 * r**2)
                    elif volcano_type == 'caldera':
                        z = 4 * np.exp(-0.05 * r**2) - 2 * np.exp(-0.5 * r**2)
                    elif volcano_type == 'cinder_cone':
                        z = 6 * np.exp(-0.3 * r**2) - 2 * np.exp(-2.0 * r**2)
                    elif volcano_type == 'lava_dome':
                        z = 4 * np.exp(-0.25 * r**2)
                    else:
                        z = 8 * np.exp(-0.1 * r**2)
                    
                    # Add small offset for visibility
                    z += 0.1
                    
                    # Multiple points across flow width
                    width_points = 3
                    for w in range(width_points):
                        # Perpendicular to flow direction
                        width_offset = 0.3 * (w - (width_points-1)/2)
                        perp_x = width_offset * np.cos(angle_jitter + np.pi/2)
                        perp_y = width_offset * np.sin(angle_jitter + np.pi/2)
                        
                        flow_points.append((x + perp_x, y + perp_y, z))
            
            # Add lava flows to frame
            if flow_points:
                flow_x = [p[0] for p in flow_points]
                flow_y = [p[1] for p in flow_points]
                flow_z = [p[2] for p in flow_points]
                
                frame_data.append(
                    go.Scatter3d(
                        x=flow_x, y=flow_y, z=flow_z,
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=lava_color,
                            opacity=0.9
                        ),
                        showlegend=False
                    )
                )
        
        # Create the animation frame
        animation_frames.append(
            go.Frame(
                data=frame_data,
                name=f"frame{frame_idx}"
            )
        )
    
    # Add frames to figure
    fig.frames = animation_frames
    
    # Set initial data (first frame)
    fig.add_traces(animation_frames[0].data)
    
    # Add camera position for cinematic view
    # Different view angles for different volcano types
    if volcano_type == 'shield':
        camera = dict(
            eye=dict(x=12, y=10, z=15),
            center=dict(x=0, y=0, z=0)
        )
    elif volcano_type == 'stratovolcano':
        camera = dict(
            eye=dict(x=14, y=12, z=12),
            center=dict(x=0, y=0, z=5)
        )
    elif volcano_type == 'caldera':
        camera = dict(
            eye=dict(x=10, y=-10, z=15),
            center=dict(x=0, y=0, z=0)
        )
    else:
        camera = dict(
            eye=dict(x=12, y=12, z=12),
            center=dict(x=0, y=0, z=2)
        )
    
    # Update layout
    fig.update_layout(
        title=f"{volcano_name} ({volcano_type.replace('_', ' ').title()}) Eruption Animation",
        autosize=True,
        width=900,
        height=700,
        scene=dict(
            xaxis=dict(range=x_range, autorange=False),
            yaxis=dict(range=y_range, autorange=False),
            zaxis=dict(range=z_range, autorange=False),
            aspectratio=dict(x=1, y=1, z=1.2),
            camera=camera
        ),
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
                        'transition': {'duration': 50}
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
            'y': 0
        }]
    )
    
    # Return data
    result = {
        'figure': fig,
        'volcano_type': volcano_type,
        'animation_data': animation_data,
        'volcano_name': volcano_name
    }
    
    return result