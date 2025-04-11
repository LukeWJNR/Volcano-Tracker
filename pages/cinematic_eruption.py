"""
Cinematic Volcano Eruption Animation for the Volcano Monitoring Dashboard.

This page provides a movie-like visualization of a volcanic eruption, showing
the complete process from magma buildup through seismic activity to eruption,
lava flows, and ash cloud formation.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.api import get_volcano_data
from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS
from utils.cinematic_animation import generate_cinematic_eruption

def app():
    st.title("Cinematic Eruption Animation")
    
    st.markdown("""
    ## 3D Movie-Style Volcano Eruption Visualization
    
    This page provides a cinematic animation of volcanic eruptions, showing the complete
    cycle from magma buildup to eruption, lava flows, and ash cloud formation.
    
    The animation is rendered in 3D with realistic physics and volcano-specific behaviors,
    similar to what you might see in a documentary or educational film.
    """)
    
    # Load volcano data
    volcanoes_df = get_volcano_data()
    
    # Sidebar for volcano selection and settings
    st.sidebar.title("Volcano Selection")
    
    # Region filter
    regions = ["All"] + sorted(volcanoes_df["region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region:", regions)
    
    # Filter by region if not "All"
    if selected_region != "All":
        filtered_df = volcanoes_df[volcanoes_df["region"] == selected_region]
    else:
        filtered_df = volcanoes_df
    
    # Volcano name filter - show all volcanoes in selected region
    volcano_names = sorted(filtered_df["name"].unique().tolist())
    selected_volcano_name = st.sidebar.selectbox(
        "Select Volcano:", 
        volcano_names
    )
    
    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = determine_volcano_type(selected_volcano)
    
    # Animation settings
    st.sidebar.title("Animation Settings")
    
    animation_speed = st.sidebar.slider(
        "Animation Speed",
        min_value=50,
        max_value=500,
        value=100,
        step=50,
        help="Higher values = faster animation"
    )
    
    frame_count = st.sidebar.slider(
        "Animation Detail",
        min_value=60,
        max_value=240,
        value=120,
        step=20,
        help="Higher values = smoother animation but slower loading"
    )
    
    # Camera angle options
    camera_options = {
        "Side View": {"x": 15, "y": 0, "z": 5},
        "Aerial View": {"x": 5, "y": 5, "z": 15},
        "Ground Level": {"x": 12, "y": 12, "z": 3},
        "Front View": {"x": 0, "y": 15, "z": 5}
    }
    
    selected_camera = st.sidebar.selectbox(
        "Camera Angle:",
        list(camera_options.keys())
    )
    
    # Main content area with volcano info and animation
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Volcano Information")
        st.markdown(f"**Name:** {selected_volcano_name}")
        st.markdown(f"**Type:** {volcano_type.replace('_', ' ').title()}")
        st.markdown(f"**Country:** {selected_volcano.get('country', 'Unknown')}")
        st.markdown(f"**Region:** {selected_volcano.get('region', 'Unknown')}")
        
        # Volcanic hazards specific to this type
        st.markdown("### Typical Hazards")
        
        if volcano_type == 'shield':
            st.markdown("""
            - Lava flows (primary hazard)
            - Vog (volcanic smog)
            - Ground deformation
            - Limited explosive activity
            """)
        elif volcano_type == 'stratovolcano':
            st.markdown("""
            - Pyroclastic flows
            - Lahars (volcanic mudflows)
            - Volcanic ash and tephra
            - Volcanic gases
            - Lava flows
            """)
        elif volcano_type == 'caldera':
            st.markdown("""
            - Large explosive eruptions
            - Widespread ash fall
            - Pyroclastic flows
            - Caldera collapse
            - Post-eruption activity (geothermal)
            """)
        elif volcano_type == 'cinder_cone':
            st.markdown("""
            - Localized tephra fall
            - Limited lava flows
            - Strombolian eruptions
            - Volcanic bombs
            """)
        elif volcano_type == 'lava_dome':
            st.markdown("""
            - Dome collapse events
            - Pyroclastic density currents
            - Volcanic gases
            - Localized ash fall
            - Explosive decompression events
            """)
        
        # Add educational information
        with st.expander("About This Animation"):
            st.markdown("""
            This animation shows a scientifically accurate representation of how volcanoes erupt.
            Each volcano type has characteristic behaviors that influence:
            
            - How magma moves through the volcanic system
            - The style and intensity of the eruption
            - The types of volcanic products (lava, ash, gases)
            - The shape and evolution of the volcanic edifice
            
            The animation progresses through several phases:
            1. **Magma Buildup**: Magma accumulates in the chamber, causing ground deformation
            2. **Initial Activity**: Early signs of eruption with increased seismicity and initial venting
            3. **Main Eruption**: Peak activity with characteristic eruption style for this volcano type
            4. **Waning Phase**: Decreasing activity as the eruption energy dissipates
            
            All animations are based on real-world volcanic processes and scientific research.
            """)
    
    with col2:
        # Main animation display area
        st.subheader(f"{selected_volcano_name} Eruption Animation")
        
        # Generate the cinematic eruption animation
        with st.spinner("Generating cinematic eruption animation..."):
            eruption_animation = generate_cinematic_eruption(
                selected_volcano,
                frames=frame_count
            )
            
            # Apply selected camera angle
            camera_pos = camera_options[selected_camera]
            eruption_animation['figure'].update_layout(
                scene=dict(
                    camera=dict(
                        eye=dict(x=camera_pos["x"], y=camera_pos["y"], z=camera_pos["z"]),
                        center=dict(x=0, y=0, z=0 if volcano_type != 'stratovolcano' else 5)
                    )
                )
            )
            
            # Apply animation speed
            eruption_animation['figure'].update_layout(
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [
                        {
                            'label': 'Play',
                            'method': 'animate',
                            'args': [None, {
                                'frame': {'duration': animation_speed, 'redraw': True},
                                'fromcurrent': True,
                                'transition': {'duration': animation_speed // 2}
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
            
            st.plotly_chart(eruption_animation['figure'], use_container_width=True)
    
    # Timeline of volcanic processes
    st.subheader("Understanding the Eruption Timeline")
    
    # Create eruption phases based on volcano type
    if volcano_type == 'shield':
        phases = [
            {"name": "Magma Buildup", "description": "Magma accumulates beneath the surface, causing subtle inflation."},
            {"name": "Initial Fissures", "description": "Cracks form at the surface as magma rises and pressure increases."},
            {"name": "Lava Fountaining", "description": "Lava erupts in fountains as gases escape and magma reaches the surface."},
            {"name": "Flow Development", "description": "Lava flows extend from the vent, typically traveling long distances."},
            {"name": "Sustained Effusion", "description": "Continued steady output of low-viscosity lava creates extensive flow fields."},
            {"name": "Waning Activity", "description": "Eruption slows as magma pressure decreases, with diminishing lava output."}
        ]
    elif volcano_type == 'stratovolcano':
        phases = [
            {"name": "Magma Buildup", "description": "High-viscosity magma accumulates beneath the volcano, causing significant deformation."},
            {"name": "Increased Seismicity", "description": "Earthquake activity increases as magma forces its way upward."},
            {"name": "Initial Explosions", "description": "Phreatic (steam) explosions occur as rising magma interacts with groundwater."},
            {"name": "Dome Growth", "description": "Viscous lava may form a dome at the vent, increasing pressure."},
            {"name": "Major Explosive Phase", "description": "Pressure release leads to violent eruption with ash column and pyroclastic flows."},
            {"name": "Ash Fallout", "description": "Widespread ash deposition occurs downwind from the eruption."}
        ]
    elif volcano_type == 'caldera':
        phases = [
            {"name": "Magma Buildup", "description": "Large volumes of magma accumulate in a shallow reservoir."},
            {"name": "Ground Deformation", "description": "Significant uplift occurs as the magma chamber expands."},
            {"name": "Increased Seismicity", "description": "Ring-like pattern of earthquakes may develop around the chamber."},
            {"name": "Initial Vent Opening", "description": "Initial explosive activity begins along ring fractures."},
            {"name": "Major Explosive Phase", "description": "Catastrophic eruption with enormous ash column and pyroclastic density currents."},
            {"name": "Caldera Collapse", "description": "The overlying ground collapses into the partially emptied magma chamber."},
            {"name": "Post-Collapse Activity", "description": "Secondary eruptions may continue within the new caldera."}
        ]
    elif volcano_type == 'cinder_cone':
        phases = [
            {"name": "Magma Buildup", "description": "Relatively small volume of magma rises toward the surface."},
            {"name": "Initial Vent Formation", "description": "A new vent forms as magma breaks through to the surface."},
            {"name": "Strombolian Activity", "description": "Rhythmic explosions eject incandescent cinder, building a cone."},
            {"name": "Cone Growth", "description": "Accumulated tephra builds a steep-sided cone around the vent."},
            {"name": "Late-Stage Lava Flow", "description": "As gas content decreases, effusive activity may produce lava flows."},
            {"name": "Activity Cessation", "description": "Eruption ends as magma supply is exhausted."}
        ]
    elif volcano_type == 'lava_dome':
        phases = [
            {"name": "Magma Buildup", "description": "Highly viscous magma rises slowly toward the surface."},
            {"name": "Initial Extrusion", "description": "Magma reaches the surface and begins to pile up as a dome."},
            {"name": "Dome Growth", "description": "The dome expands as new magma is added, creating a bulbous structure."},
            {"name": "Periodic Collapses", "description": "Parts of the unstable dome collapse, generating pyroclastic density currents."},
            {"name": "Explosive Activity", "description": "Gas pressure buildup may cause explosive decompression events."},
            {"name": "Stabilization", "description": "Activity decreases and the dome solidifies as magma supply diminishes."}
        ]
    else:
        phases = [
            {"name": "Magma Buildup", "description": "Magma accumulates beneath the surface."},
            {"name": "Initial Activity", "description": "Early signs of eruption begin."},
            {"name": "Main Eruption", "description": "Peak eruptive activity occurs."},
            {"name": "Waning Phase", "description": "Activity gradually diminishes."}
        ]
    
    # Display the phases in a timeline
    cols = st.columns(len(phases))
    for i, (col, phase) in enumerate(zip(cols, phases)):
        with col:
            st.markdown(f"**{i+1}. {phase['name']}**")
            st.markdown(phase['description'])
    
    # Educational content on volcanic processes
    with st.expander("Related Volcanic Processes", expanded=False):
        st.markdown(f"""
        ## {volcano_type.replace('_', ' ').title()} Volcano Processes
        
        {VOLCANO_TYPES[volcano_type]['description']}
        
        ### Magma Characteristics
        - **Viscosity:** {VOLCANO_TYPES[volcano_type]['magma_viscosity']}
        - **Temperature:** {VOLCANO_TYPES[volcano_type].get('temperature', '700-1200°C')}
        - **Gas Content:** {VOLCANO_TYPES[volcano_type].get('gas_content', 'Variable')}
        
        ### Similar Volcanoes
        {', '.join(VOLCANO_TYPES[volcano_type]['examples'])}
        
        ### Eruption Style
        {VOLCANO_TYPES[volcano_type]['eruption_style']}
        
        ### Monitoring Implications
        Different volcano types require different monitoring approaches. {volcano_type.replace('_', ' ').title()} 
        volcanoes typically show {VOLCANO_TYPES[volcano_type]['deformation_pattern']} before eruption,
        which can be detected through InSAR and GPS measurements.
        """)
        
        st.markdown("""
        ### References
        
        1. USGS Volcano Hazards Program
        2. Global Volcanism Program, Smithsonian Institution
        3. Sigurdsson, H. (2015). The Encyclopedia of Volcanoes. Academic Press.
        4. Parfitt, E. A., & Wilson, L. (2008). Fundamentals of Physical Volcanology.
        """)

if __name__ == "__main__":
    app()