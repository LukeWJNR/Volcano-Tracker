"""
Cinematic Volcano Eruption Animation for the Volcano Monitoring Dashboard.

This page aims to provide a visualization of a volcanic eruption, showing
the complete process from magma buildup through seismic activity to eruption,
lava flows, and ash cloud formation.
"""
import sys
import os
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Explicitly set the path to the utils directory
utils_path = "/workspaces/Volcano-Tracker/"

# Add ../utils to sys.path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file))
utils_path = os.path.join(project_root, "utils")

if utils_path not in sys.path:
    sys.path.insert(0, utils_path)


from api import get_volcano_data
from animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS
from cinematic_animation import generate_cinematic_eruption
from volcano_types import Volcano
from animation_utils import animate_eruptive_sequence
from magma_chamber_viz import draw_magma_chamber


def app():
    # Load volcano data
    volcanoes_df = get_volcano_data()

    # Sidebar for region and volcano selection
    st.sidebar.title("Volcano Selection")
    regions = ["All"] + sorted(volcanoes_df["region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region:", regions)

    # Filter volcanoes by region
    if selected_region != "All":
        filtered_df = volcanoes_df[volcanoes_df["region"] == selected_region]
    else:
        filtered_df = volcanoes_df

    # Volcano selection
    volcano_names = sorted(filtered_df["name"].unique().tolist())
    selected_volcano_name = st.sidebar.selectbox("Select Volcano:", volcano_names)

    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = volcano_type if 'volcano_type' in locals() else 'stratovolcano'
    volcano_type = determine_volcano_type(selected_volcano)

    # Display volcano information
    st.title("Cinematic Eruption Animation")
    st.markdown(f"**Name:** {selected_volcano_name}")
    st.markdown(f"**Type:** {volcano_type.replace('_', ' ').title()}")
    st.markdown(f"**Region:** {selected_volcano.get('region', 'Unknown')}")
    st.markdown(f"**Country:** {selected_volcano.get('country', 'Unknown')}")

    # Add more app logic here...
    st.markdown(f"""
    ### Magma Characteristics
    - **Viscosity:** {VOLCANO_TYPES[volcano_type]['magma_viscosity']}
    - **Temperature:** {VOLCANO_TYPES[volcano_type].get('temperature', '700-1200°C')}
    - **Gas Content:** {VOLCANO_TYPES[volcano_type].get('gas_content', 'Variable')}
    """)
        ### Similar Volcanoes
    {', '.join(VOLCANO_TYPES[volcano_type]['examples'])}

        ### Eruption Style
    {VOLCANO_TYPES[volcano_type]['eruption_style']}

        ### Monitoring Implications
    """    
    Different volcano types require different monitoring approaches. {volcano_type.replace('_', ' ').title()} 
    volcanoes typically show distinctive deformation patterns before eruption,
    which can be detected through InSAR and GPS measurements.
        """

    st.markdown("""
        ### References
        1. USGS Volcano Hazards Program
        2. Global Volcanism Program, Smithsonian Institution
        3. Sigurdsson, H. (2015). The Encyclopedia of Volcanoes. Academic Press.
        4. Parfitt, E. A., & Wilson, L. (2008). Fundamentals of Physical Volcanology.
        """)
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
if  selected_region != "All":
    filtered_df = volcanoes_df[volcanoes_df["region"] == selected_region]
else:
    filtered_df = volcanoes_df

# Ensure this section is executed before using selected_volcano_name
volcano_names = sorted(filtered_df["name"].unique().tolist())
selected_volcano_name = st.sidebar.selectbox(
    "Select Volcano:", 
    volcano_names
)

# Get selected volcano data
selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
     # Before main animation
    
if st.checkbox("Show magma chamber buildup"):
        chamber_fig = draw_magma_chamber(selected_volcano)
        st.plotly_chart(chamber_fig, use_container_width=True)
    
if st.checkbox("Show surface deformation map"):
        show_deformation_sim(selected_volcano)

def draw_magma_chamber(volcano, chamber_radius_km=2.0, chamber_depth_km=5.0):
    x, y, z = np.mgrid[-1:1:40j, -1:1:40j, -1:1:40j]
    chamber = (x**2 + y**2 + z**2) < 1

    fig = go.Figure(data=go.Isosurface(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten() - chamber_depth_km,
        value=chamber.flatten().astype(int),
        isomin=0.5,
        isomax=1,
        surface_count=1,
        colorscale='OrRd',
        opacity=0.4
    ))

    fig.update_layout(title="Subsurface Magma Chamber", scene=dict(
        zaxis=dict(title='Depth (km)', autorange='reversed'),
        xaxis=dict(title='X (km)'),
        yaxis=dict(title='Y (km)')
    ))

    return fig

# Add the required imports
import matplotlib.pyplot as plt
import numpy as np

# Define the deformation simulation function
def show_deformation_sim(volcano):
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    # Toy deformation function: a 2D Gaussian bulge
    Z = np.exp(-((X)**2 + (Y)**2) / 2) * volcano["chamber_pressure_mpa"]

    fig, ax = plt.subplots()
    contour = ax.contourf(X, Y, Z, cmap='hot')
    ax.set_title(f"Surface Uplift (Simulated)\n{volcano['name']}")
    ax.set_xlabel("km")
    ax.set_ylabel("km")
    st.pyplot(fig)

# Integrate the deformation simulation into the app
def app():
    st.title("Cinematic Eruption Animation")
    
    # ...existing code...
    
    # Add a checkbox to show deformation simulation
    if st.checkbox("Show surface deformation simulation"):
        if "chamber_pressure_mpa" in selected_volcano:
            show_deformation_sim(selected_volcano)
        else:
            st.warning("Chamber pressure data is not available for this volcano.")
    
    # ...existing code...

    # Animation settings
    st.sidebar.title("Animation Settings")
    
    animation_speed = st.sidebar.slider(
        "Animation Speed",
        min_value=50,
        max_value=500,
        value=200,  # Default to a slower animation
        step=50,
        help="Higher values = faster animation (larger numbers = slower playback)"
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
            
            # Add phase indicators to show where in the eruption process we are
            anim_data = eruption_animation['animation_data']
            unique_phases = list(dict.fromkeys(anim_data['phase']))
            
            # Create a progress bar / timeline visualization to show eruption phases
            st.markdown("### Eruption Phase Timeline")
            st.write("This timeline shows the progression through different phases of the eruption:")
            
            # Determine colors for phases
            phase_colors = {
                'initial': "#3366CC",       # Blue - calm state
                'buildup': "#FF9900",       # Orange - increasing pressure
                'initial_eruption': "#FF6600",  # Darker orange - initial eruption
                'main_eruption': "#CC0000",     # Red - main eruption
                'waning': "#9966CC"         # Purple - declining activity
            }
            
            # Count frames in each phase
            phase_counts = {}
            for phase in unique_phases:
                phase_counts[phase] = anim_data['phase'].count(phase)
            
            # Calculate percentages for visualization
            total_frames = len(anim_data['phase'])
            phase_percentages = {phase: count/total_frames*100 for phase, count in phase_counts.items()}
            
            # Display the timeline
            cols = st.columns(len(unique_phases))
            for i, (col, phase) in enumerate(zip(cols, unique_phases)):
                with col:
                    # Display the phase name and percentage
                    st.markdown(f"**{phase.replace('_', ' ').title()}**")
                    st.markdown(f"{phase_percentages[phase]:.1f}% of animation")
                    
                    # Create a colored box showing the phase
                    html_color = f"""
                    <div style="
                        background-color: {phase_colors.get(phase, '#888888')};
                        width: 100%;
                        height: 20px;
                        border-radius: 5px;
                    "></div>
                    """
                    st.markdown(html_color, unsafe_allow_html=True)
            
            # Add a slider to manually control the animation (for exploring specific phases)
            st.markdown("### Animation Control")
            selected_frame = st.slider(
                "Manually explore the eruption process:",
                min_value=0,
                max_value=frame_count-1,
                value=0,
                help="Drag to see a specific point in the eruption process"
            )
            
            # Display the current phase info
            current_phase = anim_data['phase'][selected_frame]
            st.markdown(f"**Current Phase:** {current_phase.replace('_', ' ').title()}")
            
            # Show phase-specific descriptions
            if current_phase == 'initial':
                st.markdown("The volcano is in its initial state. Magma is deep within the chamber with minimal surface activity.")
            elif current_phase == 'buildup':
                st.markdown("Pressure is building as magma rises. The ground is deforming and seismic activity is increasing.")
            elif current_phase == 'initial_eruption':
                st.markdown("The initial eruption has begun. Magma has reached the surface and eruptive activity is starting.")
            elif current_phase == 'main_eruption':
                st.markdown("The main eruption phase is underway with significant eruptive activity, characteristic of this volcano type.")
            elif current_phase == 'waning':
                st.markdown("The eruption is waning as pressure decreases and magma supply diminishes.")
    
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
        ## {determine_volcano_type(selected_volcano).replace('_', ' ').title()} Volcano Processes
        
        {VOLCANO_TYPES[determine_volcano_type(selected_volcano)]['description']}
        
        ### Magma Characteristics
        - **Viscosity:** {VOLCANO_TYPES[determine_volcano_type(selected_volcano)]['magma_viscosity']}
        - **Temperature:** {VOLCANO_TYPES[determine_volcano_type(selected_volcano)].get('temperature', '700-1200°C')}
        - **Gas Content:** {VOLCANO_TYPES[determine_volcano_type(selected_volcano)].get('gas_content', 'Variable')}
        
        ### Similar Volcanoes
        {', '.join(VOLCANO_TYPES[determine_volcano_type(selected_volcano)]['examples'])}
        
        ### Eruption Style
        {VOLCANO_TYPES[determine_volcano_type(selected_volcano)]['eruption_style']}
        
        ### Monitoring Implications
        Different volcano types require different monitoring approaches. {volcano_type.replace('_', ' ').title()} 
        volcanoes typically show distinctive deformation patterns before eruption,
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
