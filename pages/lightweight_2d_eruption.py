"""
Lightweight 2D Eruption Visualization for the Volcano Monitoring Dashboard.

This page provides a scientifically accurate, low-resource visualization of
the complete eruption cycle using 2D canvas rendering for improved performance
in embedded views and on lower-powered devices.
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
from utils.api import get_volcano_data
from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS

def app():
    st.title("Lightweight 2D Eruption Cycle")
    
    st.markdown("""
    This page provides a scientifically accurate 2D visualization of
    the complete eruption cycle, optimized for performance when embedded.
    
    ### Eruption Phases Visualization:
    - **Magma Buildup**: Watch deep and shallow magma chambers fill over time
    - **Increased Seismicity**: Observe seismic activity as pressure increases
    - **Initial Eruption**: See the beginning stages of eruption as magma reaches the surface
    - **Main Eruption**: Witness the peak eruption with characteristic behavior for the selected volcano type
    - **Waning Activity**: Observe the gradual decline of eruptive activity
    """)
    
    # Load volcano data
    volcanoes_df = get_volcano_data()
    
    # Sidebar for volcano selection
    st.sidebar.title("Volcano Selection")
    
    # Region filter
    regions = ["All"] + sorted(volcanoes_df["region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region:", regions)
    
    # Filter by region if not "All"
    if selected_region != "All":
        filtered_df = volcanoes_df[volcanoes_df["region"] == selected_region]
    else:
        filtered_df = volcanoes_df
    
    # Volcano name filter
    volcano_names = sorted(filtered_df["name"].unique().tolist())
    selected_volcano_name = st.sidebar.selectbox(
        "Select Volcano:", 
        volcano_names
    )
    
    # Animation controls
    st.sidebar.subheader("Animation Controls")
    
    # Animation speed
    animation_speed = st.sidebar.slider(
        "Animation Speed",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1,
        help="Control how fast the eruption animation plays"
    )
    
    # Visualization options
    st.sidebar.subheader("Visualization Options")
    show_metrics = st.sidebar.checkbox("Show Eruption Metrics", value=True)
    show_plumbing = st.sidebar.checkbox("Show Magma Plumbing", value=True)
    show_cross_section = st.sidebar.checkbox("Show Cross-Section View", value=True)
    
    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = determine_volcano_type(selected_volcano)
    
    # Eruption phase selection
    st.subheader("Select Eruption Phase")
    phases = ["Magma Buildup", "Seismic Activity", "Initial Eruption", "Main Eruption", "Waning Activity"]
    phases_dict = {
        "Magma Buildup": "buildup",
        "Seismic Activity": "initial",
        "Initial Eruption": "initial_eruption",
        "Main Eruption": "main_eruption",
        "Waning Activity": "waning"
    }
    
    cols = st.columns(len(phases))
    for i, phase in enumerate(phases):
        with cols[i]:
            if st.button(phase, key=f"phase_{i}", use_container_width=True):
                st.session_state["eruption_phase"] = phases_dict[phase]
    
    # Initialize phase if not in session state
    if "eruption_phase" not in st.session_state:
        st.session_state["eruption_phase"] = "buildup"  # Default
    
    current_phase = st.session_state["eruption_phase"]
    
    # Display current phase
    st.markdown(f"""
    <div style="text-align: center; margin: 10px 0; padding: 10px; background-color: #f0f2f6; border-radius: 5px;">
        <h3 style="margin: 0;">Current Phase: {current_phase.replace('_', ' ').title()}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Function to generate eruption data for visualization
    def generate_eruption_data(volcano_type, phase):
        # Base values
        time_points = np.linspace(0, 100, 60)
        magma_chamber_level = np.zeros_like(time_points)
        surface_deformation = np.zeros_like(time_points)
        eruption_height = np.zeros_like(time_points)
        lava_flow_rate = np.zeros_like(time_points)
        seismic_activity = np.zeros_like(time_points)
        
        # Phase specific values
        if phase == "buildup":
            # Gradual magma chamber filling
            magma_chamber_level = np.minimum(70 * (time_points / 100)**1.5, 70)
            surface_deformation = np.minimum(20 * (time_points / 100)**2, 20)
            seismic_activity = 10 * np.sin(time_points/10)**2
            
        elif phase == "initial":
            # Increased seismicity
            magma_chamber_level = 70 + (time_points / 100) * 10
            surface_deformation = 20 + (time_points / 100) * 15
            seismic_activity = 10 + 40 * (time_points / 100)**2
            
        elif phase == "initial_eruption":
            # Initial eruption phase
            magma_chamber_level = 80 - (time_points / 100) * 10
            surface_deformation = 35 * np.exp(-(time_points - 50)**2 / 1000)
            eruption_height = np.minimum(40 * (time_points / 100)**1.5, 40)
            lava_flow_rate = np.minimum(30 * (time_points / 100), 30)
            seismic_activity = 50 * np.exp(-(time_points - 30)**2 / 500) + 10
            
        elif phase == "main_eruption":
            # Main eruption phase - type specific
            if volcano_type == "shield":
                # Shield volcanoes: less explosive, higher lava flow
                magma_chamber_level = 70 - (time_points / 100) * 40
                eruption_height = 30 + 10 * np.sin(time_points/10)
                lava_flow_rate = 60 + 20 * np.sin(time_points/5)
                
            elif volcano_type == "stratovolcano":
                # Stratovolcanoes: more explosive, less lava flow
                magma_chamber_level = 70 - (time_points / 100) * 50
                eruption_height = 60 + 20 * np.sin(time_points/8)
                lava_flow_rate = 30 + 10 * np.sin(time_points/6)
                
            elif volcano_type == "caldera":
                # Calderas: most explosive
                magma_chamber_level = 70 - (time_points / 100) * 60
                eruption_height = 80 + 15 * np.sin(time_points/7)
                lava_flow_rate = 20 + 15 * np.sin(time_points/5)
                
            else:
                # Default
                magma_chamber_level = 70 - (time_points / 100) * 45
                eruption_height = 50 + 15 * np.sin(time_points/9)
                lava_flow_rate = 40 + 15 * np.sin(time_points/7)
                
            surface_deformation = 30 * np.exp(-(time_points - 50)**2 / 2000)
            seismic_activity = 40 * np.exp(-(time_points - 20)**2 / 1000) + 20
            
        elif phase == "waning":
            # Waning activity
            magma_chamber_level = 30 - (time_points / 100) * 20
            eruption_height = 40 * np.exp(-(time_points - 10)**2 / 2000)
            lava_flow_rate = 30 * np.exp(-(time_points - 20)**2 / 3000)
            surface_deformation = 15 * np.exp(-(time_points - 30)**2 / 4000)
            seismic_activity = 10 * np.exp(-(time_points - 40)**2 / 5000)
        
        # Ensure non-negative values
        magma_chamber_level = np.maximum(magma_chamber_level, 0)
        surface_deformation = np.maximum(surface_deformation, 0)
        eruption_height = np.maximum(eruption_height, 0)
        lava_flow_rate = np.maximum(lava_flow_rate, 0)
        seismic_activity = np.maximum(seismic_activity, 0)
        
        return {
            "time": time_points,
            "magma_level": magma_chamber_level,
            "deformation": surface_deformation,
            "eruption_height": eruption_height,
            "lava_flow": lava_flow_rate,
            "seismic": seismic_activity
        }
    
    # Generate data based on volcano type and current phase
    eruption_data = generate_eruption_data(volcano_type, current_phase)
    
    # Show visualization of eruption metrics
    if show_metrics:
        st.subheader("Eruption Metrics Over Time")
        
        # Create multi-line plot for metrics
        fig = go.Figure()
        
        # Add each metric as a separate line
        fig.add_trace(go.Scatter(
            x=eruption_data["time"], 
            y=eruption_data["magma_level"],
            mode='lines',
            name='Magma Chamber Level (%)',
            line=dict(color='#FF4500', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=eruption_data["time"], 
            y=eruption_data["deformation"],
            mode='lines',
            name='Surface Deformation (cm)',
            line=dict(color='#32CD32', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=eruption_data["time"], 
            y=eruption_data["eruption_height"],
            mode='lines',
            name='Eruption Column Height (km)',
            line=dict(color='#4169E1', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=eruption_data["time"], 
            y=eruption_data["lava_flow"],
            mode='lines',
            name='Lava Flow Rate (m³/s)',
            line=dict(color='#FF8C00', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=eruption_data["time"], 
            y=eruption_data["seismic"],
            mode='lines',
            name='Seismic Activity',
            line=dict(color='#9932CC', width=2)
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=30, b=20),
            height=300,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Create 2D visualization of volcano cross-section
    st.subheader("Volcano Cross-Section Visualization")
    
    # Get values at the midpoint of the data for current state
    midpoint_idx = len(eruption_data["time"]) // 2
    magma_level = eruption_data["magma_level"][midpoint_idx]
    deformation = eruption_data["deformation"][midpoint_idx]
    eruption_height = eruption_data["eruption_height"][midpoint_idx]
    lava_flow = eruption_data["lava_flow"][midpoint_idx]
    seismic = eruption_data["seismic"][midpoint_idx]
    
    # Create 2D cross-section plot
    def create_cross_section_plot(volcano_type, eruption_values):
        """Create a 2D cross-section visualization of the volcano"""
        
        # Create figure
        fig = go.Figure()
        
        # Define the volcano shape based on type
        x_ground = np.linspace(-200, 200, 100)
        
        if volcano_type == "shield":
            # Shield volcano: wide with gentle slopes
            y_ground = 100 - 0.005 * x_ground**2
            caldera_width = 20
            chamber_depth = 30
            chamber_width = 70
            conduit_width = 10
            deep_chamber_depth = 150
        
        elif volcano_type == "stratovolcano":
            # Stratovolcano: steeper sides
            y_ground = 150 - 0.02 * x_ground**2
            caldera_width = 15
            chamber_depth = 40
            chamber_width = 50
            conduit_width = 8
            deep_chamber_depth = 170
        
        elif volcano_type == "caldera":
            # Caldera: depression at the top
            base_height = 120 - 0.01 * x_ground**2
            # Add caldera depression
            caldera_mask = np.abs(x_ground) < 50
            base_height[caldera_mask] = base_height[caldera_mask] - 40 * (1 - (np.abs(x_ground[caldera_mask]) / 50)**2)
            y_ground = base_height
            caldera_width = 50
            chamber_depth = 50
            chamber_width = 90
            conduit_width = 15
            deep_chamber_depth = 180
        
        elif volcano_type == "cinder_cone":
            # Cinder cone: steep with small base
            y_ground = 100 - 0.04 * x_ground**2
            y_ground[np.abs(x_ground) > 75] = 0
            caldera_width = 10
            chamber_depth = 25
            chamber_width = 30
            conduit_width = 5
            deep_chamber_depth = 120
        
        else:
            # Default
            y_ground = 120 - 0.015 * x_ground**2
            caldera_width = 15
            chamber_depth = 35
            chamber_width = 60
            conduit_width = 10
            deep_chamber_depth = 160
        
        # Ensure non-negative ground height
        y_ground = np.maximum(y_ground, 0)
        
        # Ground surface with deformation
        if eruption_values["deformation"] > 0:
            # Add deformation bulge
            deformation_mask = np.abs(x_ground) < 50
            deformation_factor = eruption_values["deformation"] / 10  # Scale appropriately
            y_ground[deformation_mask] += deformation_factor * (1 - (np.abs(x_ground[deformation_mask]) / 50)**2)
        
        # Add ground (volcano shape)
        fig.add_trace(go.Scatter(
            x=x_ground,
            y=y_ground,
            fill='tozeroy',
            fillcolor='rgba(139, 69, 19, 0.6)',
            line=dict(color='rgb(139, 69, 19)', width=2),
            name='Volcano Surface'
        ))
        
        # Add underground (below surface)
        fig.add_trace(go.Scatter(
            x=x_ground,
            y=np.zeros_like(x_ground),
            fill='tonexty',
            fillcolor='rgba(101, 67, 33, 0.4)',
            line=dict(color='rgba(101, 67, 33, 0.5)', width=1),
            name='Underground'
        ))
        
        # Define conduit_top here for use in eruption visualization, regardless of whether plumbing is shown
        conduit_top = max(y_ground[np.abs(x_ground) < conduit_width/2])
        
        # Add magma chambers if enabled
        if show_plumbing:
            # Magma chamber parameters
            chamber_y = -chamber_depth
            chamber_x_range = np.linspace(-chamber_width/2, chamber_width/2, 50)
            chamber_y_values = chamber_y - 20 + 20 * np.cos(np.pi * chamber_x_range / chamber_width)
            
            # Deep magma reservoir
            deep_reservoir_y = -deep_chamber_depth
            deep_reservoir_width = chamber_width * 1.5
            deep_x_range = np.linspace(-deep_reservoir_width/2, deep_reservoir_width/2, 50)
            deep_y_values = deep_reservoir_y - 30 + 30 * np.cos(np.pi * deep_x_range / deep_reservoir_width)
            
            # Fill level based on magma_level (0-100%)
            fill_percent = eruption_values["magma_level"] / 100
            fill_threshold = chamber_y + (min(chamber_y_values) - chamber_y) * fill_percent
            
            # Magma conduit
            conduit_left = -conduit_width/2
            conduit_right = conduit_width/2
            # conduit_top is now defined outside the if block to be available for all visualizations
            conduit_bottom = chamber_y
            
            # Draw magma conduit
            fig.add_trace(go.Scatter(
                x=[conduit_left, conduit_left, conduit_right, conduit_right],
                y=[conduit_bottom, conduit_top, conduit_top, conduit_bottom],
                fill='toself',
                fillcolor='rgba(255, 69, 0, 0.6)',
                line=dict(color='rgba(255, 69, 0, 0.8)', width=1),
                name='Magma Conduit'
            ))
            
            # Draw chamber outline
            fig.add_trace(go.Scatter(
                x=chamber_x_range,
                y=chamber_y_values,
                line=dict(color='rgba(255, 140, 0, 0.8)', width=2),
                name='Magma Chamber'
            ))
            
            # Draw deep reservoir outline
            fig.add_trace(go.Scatter(
                x=deep_x_range,
                y=deep_y_values,
                line=dict(color='rgba(255, 140, 0, 0.8)', width=2),
                name='Deep Magma Reservoir'
            ))
            
            # Connection between chambers
            fig.add_trace(go.Scatter(
                x=[0, 0],
                y=[min(chamber_y_values), max(deep_y_values)],
                line=dict(color='rgba(255, 69, 0, 0.7)', width=conduit_width/2),
                name='Magma Connection'
            ))
            
            # Fill magma chamber based on level
            chamber_fill_x = []
            chamber_fill_y = []
            
            for i, x in enumerate(chamber_x_range):
                if chamber_y_values[i] <= fill_threshold:
                    chamber_fill_x.append(x)
                    chamber_fill_y.append(chamber_y_values[i])
            
            if len(chamber_fill_x) > 0:
                # Add bottom line to close the shape
                bottom_y = min(chamber_y_values)
                chamber_fill_x = [chamber_fill_x[0]] + chamber_fill_x + [chamber_fill_x[-1]]
                chamber_fill_y = [bottom_y] + chamber_fill_y + [bottom_y]
                
                fig.add_trace(go.Scatter(
                    x=chamber_fill_x,
                    y=chamber_fill_y,
                    fill='toself',
                    fillcolor='rgba(255, 69, 0, 0.7)',
                    line=dict(color='rgba(255, 69, 0, 0.8)', width=1),
                    name='Magma in Chamber'
                ))
            
            # Fill deep reservoir (always filled)
            fig.add_trace(go.Scatter(
                x=deep_x_range,
                y=deep_y_values,
                fill='toself',
                fillcolor='rgba(255, 69, 0, 0.5)',
                line=dict(color='rgba(255, 69, 0, 0.6)', width=1),
                name='Deep Magma'
            ))
        
        # Add eruption column if in eruption phase
        if eruption_values["eruption_height"] > 0:
            # Eruption column
            column_height = eruption_values["eruption_height"] * 5  # Scale for visibility
            column_width = 30 + eruption_values["eruption_height"] / 2
            
            column_x = np.linspace(-column_width/2, column_width/2, 50)
            column_top_y = conduit_top + column_height
            
            # Create expanding column shape
            column_y = conduit_top + (column_top_y - conduit_top) * (1 - (np.abs(column_x)/(column_width/2))**0.5)
            
            fig.add_trace(go.Scatter(
                x=column_x,
                y=column_y,
                fill='tozeroy',
                fillcolor='rgba(169, 169, 169, 0.7)',
                line=dict(color='rgba(105, 105, 105, 0.9)', width=1),
                name='Eruption Column'
            ))
            
            # Add ash cloud at the top
            if column_height > 50:
                cloud_width = column_width * 2
                cloud_x = np.linspace(-cloud_width/2, cloud_width/2, 100)
                cloud_height = 30
                
                # Create cloud shape with randomness
                np.random.seed(0)  # Fixed seed for reproducibility
                noise = np.random.normal(0, 5, len(cloud_x))
                cloud_y = column_top_y + cloud_height * np.sin(np.pi * cloud_x / cloud_width) + noise
                
                fig.add_trace(go.Scatter(
                    x=cloud_x,
                    y=cloud_y,
                    fill='tozeroy',
                    fillcolor='rgba(130, 130, 130, 0.6)',
                    line=dict(color='rgba(105, 105, 105, 0.8)', width=1),
                    name='Ash Cloud'
                ))
        
        # Add lava flows if present
        if eruption_values["lava_flow"] > 0:
            flow_length = eruption_values["lava_flow"] * 3  # Scale for visibility
            flow_thickness = 5 + eruption_values["lava_flow"] / 10
            
            # Determine flow direction based on volcano type
            if volcano_type == "shield":
                # Shield volcanoes have longer, thinner flows
                flow_length *= 1.5
                flow_thickness *= 0.7
                
                # Both sides flow
                fig.add_trace(go.Scatter(
                    x=[0, flow_length, flow_length, 0],
                    y=[conduit_top, 0, flow_thickness, conduit_top],
                    fill='toself',
                    fillcolor='rgba(255, 69, 0, 0.7)',
                    line=dict(color='rgba(255, 69, 0, 0.8)', width=1),
                    name='Lava Flow Right'
                ))
                
                fig.add_trace(go.Scatter(
                    x=[0, -flow_length, -flow_length, 0],
                    y=[conduit_top, 0, flow_thickness, conduit_top],
                    fill='toself',
                    fillcolor='rgba(255, 69, 0, 0.7)',
                    line=dict(color='rgba(255, 69, 0, 0.8)', width=1),
                    name='Lava Flow Left'
                ))
                
            else:
                # Other volcanoes have more localized flows
                # Determine crater edge points
                right_edge_idx = np.abs(x_ground - caldera_width/2).argmin()
                left_edge_idx = np.abs(x_ground + caldera_width/2).argmin()
                
                right_edge_x = x_ground[right_edge_idx]
                right_edge_y = y_ground[right_edge_idx]
                
                # Flow down one side
                fig.add_trace(go.Scatter(
                    x=[right_edge_x, right_edge_x + flow_length, right_edge_x + flow_length, right_edge_x],
                    y=[right_edge_y, 0, flow_thickness, right_edge_y],
                    fill='toself',
                    fillcolor='rgba(255, 69, 0, 0.7)',
                    line=dict(color='rgba(255, 69, 0, 0.8)', width=1),
                    name='Lava Flow'
                ))
        
        # Add seismic activity indicators
        if eruption_values["seismic"] > 0:
            seismic_level = eruption_values["seismic"]
            num_markers = int(seismic_level / 5) + 1  # Scale number of indicators
            
            # Generate random positions for seismic events
            np.random.seed(1)  # Fixed seed for reproducibility
            seismic_x = np.random.uniform(-chamber_width, chamber_width, num_markers)
            seismic_y = np.random.uniform(-deep_chamber_depth, -20, num_markers)
            seismic_sizes = np.random.uniform(5, 10 + seismic_level/5, num_markers)
            
            fig.add_trace(go.Scatter(
                x=seismic_x,
                y=seismic_y,
                mode='markers',
                marker=dict(
                    color='rgba(255, 0, 0, 0.6)',
                    size=seismic_sizes,
                    line=dict(color='rgba(255, 0, 0, 0.8)', width=1)
                ),
                name='Seismic Events'
            ))
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            xaxis=dict(
                range=[-200, 200],
                title="Distance (m)",
                zeroline=False,
            ),
            yaxis=dict(
                range=[-deep_chamber_depth - 50, 200 + eruption_values["eruption_height"] * 5],
                title="Elevation (m)",
                zeroline=False,
                scaleanchor="x",
                scaleratio=1,
            ),
            margin=dict(l=20, r=20, t=20, b=20),
            height=600,
            template="plotly_white"
        )
        
        return fig
    
    # Create and display the cross-section plot
    cross_section_fig = create_cross_section_plot(
        volcano_type, 
        {
            "magma_level": magma_level,
            "deformation": deformation,
            "eruption_height": eruption_height,
            "lava_flow": lava_flow,
            "seismic": seismic
        }
    )
    
    st.plotly_chart(cross_section_fig, use_container_width=True)
    
    # Show key metrics for current phase
    st.subheader("Current Eruption Metrics")
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    with metrics_col1:
        st.metric(
            "Magma Chamber Level", 
            f"{magma_level:.1f}%",
            f"{eruption_data['magma_level'][-1] - eruption_data['magma_level'][0]:.1f}%"
        )
        st.metric(
            "Seismic Activity", 
            f"{seismic:.1f}", 
            f"{eruption_data['seismic'][-1] - eruption_data['seismic'][0]:.1f}"
        )
        
    with metrics_col2:
        st.metric(
            "Surface Deformation", 
            f"{deformation:.1f} cm", 
            f"{eruption_data['deformation'][-1] - eruption_data['deformation'][0]:.1f} cm"
        )
        st.metric(
            "Magma Temperature", 
            f"{900 + magma_level * 3:.0f} °C", 
            None
        )
        
    with metrics_col3:
        st.metric(
            "Eruption Column Height", 
            f"{eruption_height:.1f} km", 
            f"{eruption_data['eruption_height'][-1] - eruption_data['eruption_height'][0]:.1f} km"
        )
        st.metric(
            "Lava Flow Rate", 
            f"{lava_flow:.1f} m³/s", 
            f"{eruption_data['lava_flow'][-1] - eruption_data['lava_flow'][0]:.1f} m³/s"
        )
    
    # Provide volcano-type specific information
    st.subheader(f"About {volcano_type.replace('_', ' ').title()} Volcanoes")
    
    if volcano_type == "shield":
        st.markdown("""
        **Shield volcanoes** are characterized by:
        - Broad, gentle slopes formed by highly fluid lava flows
        - Low-viscosity basaltic magma that flows easily
        - Less explosive eruptions with extensive lava flows
        - Examples include Mauna Loa and Kilauea in Hawaii
        """)
        
    elif volcano_type == "stratovolcano":
        st.markdown("""
        **Stratovolcanoes** are characterized by:
        - Steep, symmetrical cones built up by alternating layers of lava, ash, and rock
        - Higher-viscosity magma that doesn't flow as easily
        - More explosive eruptions with ash columns and pyroclastic flows
        - Examples include Mount Fuji in Japan and Mount St. Helens in the USA
        """)
        
    elif volcano_type == "caldera":
        st.markdown("""
        **Caldera volcanoes** are characterized by:
        - Large, basin-shaped depressions formed by the collapse of the magma chamber
        - Extremely large magma reservoirs
        - Potential for the most explosive eruptions
        - Examples include Yellowstone in the USA and Lake Toba in Indonesia
        """)
        
    elif volcano_type == "cinder_cone":
        st.markdown("""
        **Cinder cone volcanoes** are characterized by:
        - Small, steep-sided cones built from ejected lava fragments
        - Typically have a single vent
        - Relatively small and short-lived eruptions
        - Examples include Paricutin in Mexico and Cerro Negro in Nicaragua
        """)
        
    elif volcano_type == "lava_dome":
        st.markdown("""
        **Lava dome volcanoes** are characterized by:
        - Rounded, steep-sided mounds formed by highly viscous lava
        - Very thick, slow-moving lava that barely flows
        - Potential for explosive eruptions when pressure builds up
        - Examples include Mount St. Helens' dome (USA) and Soufrière Hills (Montserrat)
        """)
    
    # Add embedding guide
    with st.expander("For Website Embedding"):
        st.markdown("""
        This 2D visualization is optimized for embedding in websites. To embed it, use this code:
        
        ```html
        <iframe 
          src="YOUR_REPLIT_APP_URL/lightweight_2d_eruption?embed=true" 
          width="100%" 
          height="800px" 
          style="border:none;" 
          allow="fullscreen"
          title="Volcano Eruption Visualization">
        </iframe>
        ```
        
        This 2D version uses significantly fewer resources than the 3D visualization.
        """)