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
    
    # Set up the scene with appropriate dimensions based on volcano type
    # Each volcano type needs different viewing parameters to show their proportions
    if volcano_type == 'shield':
        # Shield volcanoes are very wide with gentle slopes
        x_range = [-20, 20]  # Wide viewing range
        y_range = [-20, 20]  
        z_range = [-8, 15]   # Less height needed
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes are tall with narrower base
        x_range = [-15, 15]
        y_range = [-15, 15]
        z_range = [-10, 25]  # Need more height for tall eruption columns
    elif volcano_type == 'caldera':
        # Calderas are wide with a depression
        x_range = [-20, 20]
        y_range = [-20, 20]
        z_range = [-8, 25]   # Need height for large eruption columns
    elif volcano_type == 'cinder_cone':
        # Cinder cones are small
        x_range = [-8, 8]
        y_range = [-8, 8]
        z_range = [-5, 15]   # Less height overall
    elif volcano_type == 'lava_dome':
        # Lava domes are small but can have tall eruption columns
        x_range = [-8, 8]
        y_range = [-8, 8]
        z_range = [-8, 15]
    else:
        # Default dimensions
        x_range = [-15, 15]
        y_range = [-15, 15]
        z_range = [-8, 20]  # Extra height for ash clouds and eruption columns
    
    # Generate ground surface based on volcano type
    resolution = 50
    x = np.linspace(x_range[0], x_range[1], resolution)
    y = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x, y)
    
    # Calculate distance from center
    R = np.sqrt(X**2 + Y**2)
    
    # Base surface shape depends on volcano type with more realistic proportions
    if volcano_type == 'shield':
        # Shield volcanoes: Very wide base with gently sloping sides (like Hawaiian volcanoes)
        # Typically 1:20 height to width ratio
        base_width = 20.0  # Wide base
        height = 3.0       # Moderate height
        Z_surface = height * np.exp(-0.02 * (R**2 / base_width))
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes: Steep conical shape with height to width ratio of 1:3 (like Mt. Fuji)
        base_width = 8.0   # Medium-wide base
        height = 7.0       # Tall
        # More realistic steep sides with slightly concave shape
        Z_surface = height * np.exp(-0.2 * (R**2 / base_width))
    elif volcano_type == 'caldera':
        # Calderas: Wide with a depression in the middle (like Yellowstone)
        base_width = 15.0  # Wide base
        rim_height = 2.5   # Moderate rim height
        depression_width = 6.0  # Size of the central depression
        # Rim with central depression
        Z_surface = rim_height * np.exp(-0.05 * (R**2 / base_width)) - 2.0 * np.exp(-1.0 * (R**2 / depression_width))
    elif volcano_type == 'cinder_cone':
        # Cinder cones: Small, steep sides, height to width ratio around 1:4 (like Paricutin)
        base_width = 4.0   # Narrow base
        height = 3.0       # Small height
        # Steep sides with very small summit crater
        Z_surface = height * np.exp(-0.5 * (R**2 / base_width)) - 0.5 * np.exp(-10.0 * R**2)
    elif volcano_type == 'lava_dome':
        # Lava domes: Small, bulbous, steep-sided (like Mount St. Helens dome)
        base_width = 3.0   # Very narrow base
        height = 2.5       # Small height
        # Bulbous shape with steep sides
        Z_surface = height * (np.exp(-0.8 * (R**2 / base_width)) + 0.3 * np.exp(-4.0 * R**2))
    else:
        # Default - generic volcano shape
        Z_surface = 5 * np.exp(-0.1 * R**2)
    
    # Generate comprehensive volcanic plumbing system with realistic dimensions
    # Based on research from "Volcanic and igneous plumbing systems"
    
    # Initialize default values for all parameters to avoid any unbound variables
    chamber_depth = -5  
    chamber_width = 6   
    chamber_height = 2  
    has_deep_reservoir = False
    deep_reservoir_depth = -10
    deep_reservoir_width = 8
    deep_reservoir_height = 3
    has_shallow_chamber = False
    shallow_chamber_depth = -2
    shallow_chamber_width = 4
    shallow_chamber_height = 1
    conduit_complexity = "simple"
    
    # Then set specific values based on volcano type
    if volcano_type == 'stratovolcano':
        # Stratovolcano plumbing systems typically have:
        # 1. Deep crustal reservoir (magma generation zone)
        # 2. Mid-crustal storage zone (main magma chamber)
        # 3. Shallow holding area (subsidiary chamber)
        # 4. Complex conduit system
        
        # Main magma chamber (mid-crustal)
        chamber_depth = -8  # Deep magma chamber
        chamber_width = 7   # Wide chamber but not as wide as shield volcanoes
        chamber_height = 3  # Tall chamber for rising magma bodies
        
        # Secondary features
        has_deep_reservoir = True
        deep_reservoir_depth = -15
        deep_reservoir_width = 12
        deep_reservoir_height = 4
        
        has_shallow_chamber = True
        shallow_chamber_depth = -3
        shallow_chamber_width = 3
        shallow_chamber_height = 1
        
        conduit_complexity = "complex"  # Can be "simple", "complex", or "network"
        
    elif volcano_type == 'shield':
        # Shield volcano plumbing systems typically have:
        # 1. Deeper primary magma reservoir
        # 2. Shallow, laterally extensive sill-like chamber
        # 3. Rift zones (lateral magma movement)
        
        # Main shallow, sill-like chamber
        chamber_depth = -4  # Shallow magma chamber for shield volcanoes
        chamber_width = 15  # Very wide, horizontally extensive chamber
        chamber_height = 2  # Relatively flat chamber (high width to height ratio)
        
        # Secondary features
        has_deep_reservoir = True
        deep_reservoir_depth = -12
        deep_reservoir_width = 10
        deep_reservoir_height = 3
        
        has_shallow_chamber = False  # Shield volcanoes often lack distinct shallow chambers
        shallow_chamber_depth = -2  # Initialize even if not used
        shallow_chamber_width = 3
        shallow_chamber_height = 1
        
        conduit_complexity = "network"  # Shield volcanoes often have complex rift zone systems
        
    elif volcano_type == 'caldera':
        # Caldera systems have:
        # 1. Large, shallow magma chambers
        # 2. Often multiple interconnected chambers
        # 3. Ring fracture systems
        
        # Main large, shallow chamber
        chamber_depth = -5  # Moderate depth for calderas
        chamber_width = 14  # Very wide chamber system
        chamber_height = 4  # Substantial vertical extent
        
        # Secondary features
        has_deep_reservoir = True
        deep_reservoir_depth = -14
        deep_reservoir_width = 18
        deep_reservoir_height = 5
        
        has_shallow_chamber = True
        shallow_chamber_depth = -2
        shallow_chamber_width = 8
        shallow_chamber_height = 2
        
        conduit_complexity = "network"  # Ring fractures with multiple paths
        
    elif volcano_type == 'cinder_cone':
        # Cinder cones have:
        # 1. Small, shallow magma source
        # 2. Simple, direct conduit
        # 3. Often monogenetic (single eruption history)
        
        # Small, shallow chamber
        chamber_depth = -3  # Very shallow for cinder cones
        chamber_width = 2   # Small chamber for cinder cones
        chamber_height = 1  # Small vertical extent
        
        # Secondary features
        has_deep_reservoir = False  # Cinder cones often lack deep reservoirs
        deep_reservoir_depth = -6   # Initialize even if not used
        deep_reservoir_width = 3
        deep_reservoir_height = 1
        
        has_shallow_chamber = False  # Single simple chamber is sufficient
        shallow_chamber_depth = -1.5  # Initialize even if not used
        shallow_chamber_width = 1
        shallow_chamber_height = 0.5
        
        conduit_complexity = "simple"  # Direct path from chamber to surface
        
    elif volcano_type == 'lava_dome':
        # Lava dome plumbing systems have:
        # 1. Moderately deep, viscous magma source
        # 2. Often complex conduit system with multiple branches
        
        # Moderately deep chamber
        chamber_depth = -6  # Moderately deep for lava domes
        chamber_width = 4   # Medium width chamber
        chamber_height = 2  # Medium height
        
        # Secondary features
        has_deep_reservoir = True
        deep_reservoir_depth = -12
        deep_reservoir_width = 6
        deep_reservoir_height = 3
        
        has_shallow_chamber = True
        shallow_chamber_depth = -2
        shallow_chamber_width = 2
        shallow_chamber_height = 1
        
        conduit_complexity = "complex"  # Often has multiple branches
    
    # Create a detailed magma chamber with more points for better visibility
    chamber_x = np.linspace(-chamber_width, chamber_width, 40)
    chamber_y = np.linspace(-chamber_width, chamber_width, 40)
    chamber_X, chamber_Y = np.meshgrid(chamber_x, chamber_y)
    chamber_R = np.sqrt(chamber_X**2 + chamber_Y**2)
    
    # Create the chamber shape with variable dimensions based on volcano type
    chamber_Z = chamber_depth - chamber_height * np.exp(-0.15 * (chamber_R**2) / (chamber_width*0.5))
    
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
    
    # Generate conduit system between magma chamber(s) and surface
    # The conduit complexity varies by volcano type and plumbing system
    conduit_coords = []
    
    # Main conduit from magma chamber to surface
    if conduit_complexity == "simple":
        # Simple, straight conduit
        theta = np.linspace(0, 2*np.pi, 15)
        conduit_heights = np.linspace(chamber_depth, summit_height, 25)
        
        for h in conduit_heights:
            # Conduit radius varies with height (wider near chamber, narrower near surface)
            radius_factor = (h - chamber_depth) / (summit_height - chamber_depth)
            r = conduit_radius * (1 - 0.5 * radius_factor)
            for t in theta:
                x = r * np.cos(t)
                y = r * np.sin(t)
                conduit_coords.append((x, y, h))
    
    elif conduit_complexity == "complex":
        # Complex conduit with some bends and variations
        theta = np.linspace(0, 2*np.pi, 15)
        conduit_heights = np.linspace(chamber_depth, summit_height, 30)
        
        # Main conduit with slight sinusoidal offset
        for h_idx, h in enumerate(conduit_heights):
            # Add horizontal offset that varies with height
            height_fraction = h_idx / len(conduit_heights)
            offset_x = 0.6 * np.sin(height_fraction * 3 * np.pi) * (1 - height_fraction)
            offset_y = 0.3 * np.cos(height_fraction * 2 * np.pi) * (1 - height_fraction)
            
            # Conduit radius varies with height
            radius_factor = (h - chamber_depth) / (summit_height - chamber_depth)
            r = conduit_radius * (1 - 0.3 * radius_factor)
            
            for t in theta:
                x = offset_x + r * np.cos(t)
                y = offset_y + r * np.sin(t)
                conduit_coords.append((x, y, h))
        
        # Add a secondary branch if the volcano has a shallow chamber
        if has_shallow_chamber:
            # Get the midpoint of the main conduit
            mid_height_idx = len(conduit_heights) // 2
            mid_height = conduit_heights[mid_height_idx]
            
            # Create branch from midpoint to shallow chamber
            branch_heights = np.linspace(mid_height, shallow_chamber_depth, 10)
            
            for h_idx, h in enumerate(branch_heights):
                # Calculate horizontal offset for the branch
                branch_progress = h_idx / len(branch_heights)
                branch_x = 1.0 * branch_progress
                branch_y = 0.5 * branch_progress
                
                # Branch radius
                r = conduit_radius * 0.7
                
                for t in theta:
                    x = branch_x + r * np.cos(t)
                    y = branch_y + r * np.sin(t)
                    conduit_coords.append((x, y, h))
    
    elif conduit_complexity == "network":
        # Network of conduits with multiple branches (for shield volcanoes and calderas)
        theta = np.linspace(0, 2*np.pi, 12)
        conduit_heights = np.linspace(chamber_depth, summit_height, 25)
        
        # Main central conduit
        for h in conduit_heights:
            radius_factor = (h - chamber_depth) / (summit_height - chamber_depth)
            r = conduit_radius * (1 - 0.5 * radius_factor)
            for t in theta:
                x = r * np.cos(t)
                y = r * np.sin(t)
                conduit_coords.append((x, y, h))
        
        # Add lateral rift zones/dikes (especially for shield volcanoes)
        if volcano_type == 'shield':
            # Create two main rift zones in opposite directions
            for direction in [0, np.pi]:
                # Heights for the rift zone
                rift_heights = np.linspace(chamber_depth + 1, chamber_depth + 2, 8)
                
                for h in rift_heights:
                    # Distance ranges along the rift
                    distances = np.linspace(1, chamber_width * 0.7, 10)
                    
                    for dist in distances:
                        # Create a tube-like structure along the rift
                        for t in np.linspace(0, 2*np.pi, 10):
                            small_r = conduit_radius * 0.4
                            x = dist * np.cos(direction) + small_r * np.cos(t)
                            y = dist * np.sin(direction) + small_r * np.sin(t)
                            conduit_coords.append((x, y, h))
        
        # For calderas, add ring dike structures
        elif volcano_type == 'caldera':
            # Create ring dike at a distance from center
            ring_radius = chamber_width * 0.4
            ring_heights = np.linspace(chamber_depth, chamber_depth + 3, 10)
            
            for h in ring_heights:
                for angle in np.linspace(0, 2*np.pi, 40):
                    x = ring_radius * np.cos(angle)
                    y = ring_radius * np.sin(angle)
                    
                    # Add some points to create thickness
                    for r_offset in np.linspace(-0.3, 0.3, 3):
                        adjusted_r = ring_radius + r_offset
                        x = adjusted_r * np.cos(angle)
                        y = adjusted_r * np.sin(angle)
                        conduit_coords.append((x, y, h))
    
    else:
        # Fallback to simple conduit
        theta = np.linspace(0, 2*np.pi, 15)
        conduit_heights = np.linspace(chamber_depth, summit_height, 25)
        
        for h in conduit_heights:
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
        
        # 2. Deep magma reservoir (if present)
        if has_deep_reservoir:
            # Create deep reservoir - larger and deeper
            deep_res_x = np.linspace(-deep_reservoir_width, deep_reservoir_width, 40)
            deep_res_y = np.linspace(-deep_reservoir_width, deep_reservoir_width, 40)
            deep_res_X, deep_res_Y = np.meshgrid(deep_res_x, deep_res_y)
            deep_res_R = np.sqrt(deep_res_X**2 + deep_res_Y**2)
            
            # Calculate deep reservoir surface
            deep_res_Z = deep_reservoir_depth - deep_reservoir_height * np.exp(-0.15 * (deep_res_R**2) / (deep_reservoir_width*0.5))
            
            # Deep reservoir is shown more translucent
            frame_data.append(
                go.Surface(
                    x=deep_res_X, y=deep_res_Y, z=deep_res_Z,
                    colorscale=[[0, 'rgb(255, 30, 0)'], [1, 'rgb(255, 30, 0)']],  # Deeper red for deep magma
                    showscale=False,
                    opacity=0.6  # More translucent
                )
            )
            
            # Add connection between deep reservoir and main chamber
            if phase != 'initial' or np.random.random() < 0.3:  # Show connections more prominently during active phases
                connection_x = []
                connection_y = []
                connection_z = []
                
                # Create connection points
                connection_points = 15
                for i in range(connection_points):
                    # Interpolate position between deep reservoir and main chamber
                    t = i / (connection_points - 1)
                    
                    # Random offset to make it look more natural
                    rand_offset_x = np.random.uniform(-0.5, 0.5)
                    rand_offset_y = np.random.uniform(-0.5, 0.5)
                    
                    # Position
                    x = rand_offset_x
                    y = rand_offset_y
                    z = deep_reservoir_depth * (1 - t) + chamber_depth * t
                    
                    connection_x.append(x)
                    connection_y.append(y)
                    connection_z.append(z)
                
                # Add the connection as a scatter3d
                frame_data.append(
                    go.Scatter3d(
                        x=connection_x, y=connection_y, z=connection_z,
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=magma_color,
                            opacity=0.7
                        ),
                        showlegend=False
                    )
                )
        
        # 3. Main magma chamber (constant through animation)
        frame_data.append(
            go.Surface(
                x=chamber_X, y=chamber_Y, z=chamber_Z,
                colorscale=[[0, magma_color], [1, magma_color]],
                showscale=False,
                opacity=0.8
            )
        )
        
        # 4. Shallow subsidiary chamber (if present)
        if has_shallow_chamber:
            # Create shallow chamber - smaller and near surface
            shallow_x = np.linspace(-shallow_chamber_width, shallow_chamber_width, 30)
            shallow_y = np.linspace(-shallow_chamber_width, shallow_chamber_width, 30)
            shallow_X, shallow_Y = np.meshgrid(shallow_x, shallow_y)
            shallow_R = np.sqrt(shallow_X**2 + shallow_Y**2)
            
            # Calculate shallow chamber surface
            shallow_Z = shallow_chamber_depth - shallow_chamber_height * np.exp(-0.2 * (shallow_R**2) / (shallow_chamber_width*0.4))
            
            # Shallow chamber is brighter
            frame_data.append(
                go.Surface(
                    x=shallow_X, y=shallow_Y, z=shallow_Z,
                    colorscale=[[0, 'rgb(255, 100, 0)'], [1, 'rgb(255, 100, 0)']],  # Brighter orange for shallow magma
                    showscale=False,
                    opacity=0.75
                )
            )
            
            # Add connection between main chamber and shallow chamber
            connection2_x = []
            connection2_y = []
            connection2_z = []
            
            # Create connection points
            connection_points = 10
            for i in range(connection_points):
                # Interpolate position
                t = i / (connection_points - 1)
                
                # Small random offset
                rand_offset_x = np.random.uniform(-0.3, 0.3)
                rand_offset_y = np.random.uniform(-0.3, 0.3)
                
                # Position
                x = rand_offset_x
                y = rand_offset_y
                z = chamber_depth * (1 - t) + shallow_chamber_depth * t
                
                connection2_x.append(x)
                connection2_y.append(y)
                connection2_z.append(z)
            
            # Add the connection as a scatter3d
            frame_data.append(
                go.Scatter3d(
                    x=connection2_x, y=connection2_y, z=connection2_z,
                    mode='markers',
                    marker=dict(
                        size=6,
                        color=magma_color,
                        opacity=0.8
                    ),
                    showlegend=False
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
            
            # Add points for ash cloud at the top with directional dispersal
            if ash_density > 0:
                cloud_height = summit_height + eruption_height
                cloud_radius = vent_radius * 3 * ash_density
                n_ash_points = int(150 * ash_density)  # More points for denser visualization
                
                # Create a prevailing wind direction for ash dispersal
                # Primarily eastward (positive x) with slight northern (negative y) component
                wind_direction_x = 0.8  # Positive x direction (east)
                wind_direction_y = -0.3  # Slight negative y (north)
                
                # Normalize the wind vector
                wind_mag = np.sqrt(wind_direction_x**2 + wind_direction_y**2)
                wind_direction_x /= wind_mag
                wind_direction_y /= wind_mag
                
                # Generate ash cloud with directional bias
                for _ in range(n_ash_points):
                    # Base position at eruption column top
                    base_x = 0
                    base_y = 0
                    base_z = cloud_height
                    
                    # Distance from the center, farther points for more ash spread
                    dist = np.random.exponential(scale=cloud_radius * 1.5)
                    
                    # Wind influence increases with distance
                    wind_influence = min(1.0, dist / (cloud_radius * 2))
                    
                    # Angle with wind bias (more points in wind direction)
                    angle_bias = np.random.triangular(0, np.pi, 2*np.pi)
                    if np.random.random() < 0.7:  # 70% of particles follow wind
                        # Calculate position with wind influence
                        dx = dist * (wind_direction_x * wind_influence + 
                                    np.cos(angle_bias) * (1 - wind_influence))
                        dy = dist * (wind_direction_y * wind_influence + 
                                    np.sin(angle_bias) * (1 - wind_influence))
                    else:
                        # Some random dispersion in other directions
                        dx = dist * np.cos(angle_bias)
                        dy = dist * np.sin(angle_bias)
                    
                    # Height decreases with distance from center (ash falling)
                    height_decay = np.random.uniform(0.1, 0.5) * dist / cloud_radius
                    dz = np.random.uniform(-2, 1) * ash_density - height_decay
                    
                    # Final position
                    x = base_x + dx
                    y = base_y + dy
                    z = base_z + dz
                    
                    column_points.append((x, y, z))
                
                # Add ash fallout beneath the cloud
                fallout_points = int(50 * ash_density)
                max_fallout_dist = cloud_radius * 4  # How far the ash falls
                
                for _ in range(fallout_points):
                    # Distance from center, following the wind direction
                    dist = np.random.uniform(cloud_radius * 0.5, max_fallout_dist)
                    
                    # Position biased in wind direction
                    angle_jitter = np.random.uniform(-0.5, 0.5)
                    wind_angle = np.arctan2(wind_direction_y, wind_direction_x)
                    angle = wind_angle + angle_jitter
                    
                    # Calculate position
                    x = dist * np.cos(angle)
                    y = dist * np.sin(angle)
                    
                    # Height decreases with distance (ash is falling)
                    height_factor = 1 - (dist / max_fallout_dist)
                    z_max = cloud_height * height_factor
                    z = np.random.uniform(0, z_max)
                    
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
    # Calculate appropriate aspect ratios based on volcano type
    if volcano_type == 'shield':
        # Shield volcanoes are very wide with gentle slopes
        # Need to exaggerate vertical scale slightly for better visualization
        aspect_ratio = dict(x=1, y=1, z=0.8)
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes are tall with steeper sides
        aspect_ratio = dict(x=1, y=1, z=1.5)
    elif volcano_type == 'caldera':
        # Calderas are wide with a depression
        aspect_ratio = dict(x=1, y=1, z=1.0)
    elif volcano_type == 'cinder_cone':
        # Cinder cones are steep but small
        aspect_ratio = dict(x=1, y=1, z=1.2)
    elif volcano_type == 'lava_dome':
        # Lava domes are small but tall
        aspect_ratio = dict(x=1, y=1, z=1.4)
    else:
        # Default aspect ratio
        aspect_ratio = dict(x=1, y=1, z=1.2)
    
    fig.update_layout(
        title=f"{volcano_name} ({volcano_type.replace('_', ' ').title()}) Eruption Animation",
        autosize=True,
        width=900,
        height=700,
        scene=dict(
            xaxis=dict(range=x_range, autorange=False),
            yaxis=dict(range=y_range, autorange=False),
            zaxis=dict(range=z_range, autorange=False),
            aspectratio=aspect_ratio,
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
                        'frame': {'duration': 350, 'redraw': True},  # Much slower - 350ms per frame
                        'fromcurrent': True,
                        'transition': {'duration': 150}  # Smoother transitions
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