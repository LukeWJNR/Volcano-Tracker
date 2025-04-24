"""
Volcano Animations page for the Volcano Monitoring Dashboard.

This page provides interactive animations of different volcano types and eruption processes,
using scientific models and InSAR data to visualize volcanic activity patterns.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import get_volcano_data, get_volcano_details
from utils.animation_utils import (
    generate_magma_chamber_animation,
    generate_deformation_plot,
    generate_eruption_sequence_animation,
    determine_volcano_type,
    VOLCANO_TYPES,
    ALERT_LEVELS
)
from utils.magma_chamber_viz import (
    generate_3d_magma_chamber,
    generate_animated_magma_flow
)
from utils.comet_utils import (
    get_matching_comet_volcano,
    get_comet_volcano_sar_data,
    display_comet_sar_animation
)

def app():
    st.title("Volcano Animations")
    
    st.markdown("""
    ## Interactive Volcano Visualization
    
    This page provides scientifically accurate animations of different volcano types and eruption processes.
    The visualizations combine real InSAR data with computational models to help understand volcanic activity patterns.
    
    ### Explore Different Types of Visualizations:
    
    1. **Surface Deformation Patterns** - View InSAR-like visualizations showing ground movement
    2. **Magma Chamber Dynamics** - Explore the behavior of magma within the volcano
    3. **Eruption Sequence** - See how key metrics change throughout a volcanic eruption
    4. **Real InSAR Data** - Compare with actual satellite radar interferometry data
    
    *The animations are based on scientific models and real-world volcano behavior patterns.*
    """)
    
    # Load volcano data
    try:
        volcanoes_df = get_volcano_data()
        volcanoes_df = volcanoes_df.sort_values(by='name')
    except Exception as e:
        st.error(f"Error loading volcano data: {str(e)}")
        st.stop()
    
    # Create tabs for different visualization types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Surface Deformation", 
        "Magma Chamber Dynamics", 
        "Eruption Sequence",
        "Real InSAR Comparison"
    ])
    
    with tab1:
        st.header("Surface Deformation Patterns")
        
        st.markdown("""
        This visualization shows simulated InSAR interferometry patterns for different volcano types.
        
        In InSAR data:
        - Each complete color cycle (fringe) represents ~2.8 cm of ground displacement
        - Concentric patterns often indicate inflation or deflation of a magma reservoir
        - The pattern shape reveals information about the magma chamber's depth and geometry
        
        Choose a volcano to see its characteristic deformation pattern based on its type and alert level.
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Volcano selection
            selected_volcano_name = st.selectbox(
                "Select a volcano:",
                options=volcanoes_df['name'].unique(),
                key="deform_volcano_selector"
            )
            
            if selected_volcano_name:
                # Get volcano data
                selected_volcano = volcanoes_df[volcanoes_df['name'] == selected_volcano_name].iloc[0].to_dict()
                volcano_type = determine_volcano_type(selected_volcano)
                alert_level = selected_volcano.get('alert_level', 'Normal')
                
                # Display volcano info
                st.markdown(f"**Selected Volcano:** {selected_volcano_name}")
                st.markdown(f"**Type:** {volcano_type.replace('_', ' ').title()}")
                st.markdown(f"**Alert Level:** {alert_level}")
                
                # Option to override alert level for simulation
                override_alert = st.checkbox("Override alert level", key="deform_override_alert")
                
                if override_alert:
                    alert_level = st.selectbox(
                        "Select alert level for simulation:",
                        options=list(ALERT_LEVELS.keys()),
                        key="deform_alert_selector"
                    )
                
                # Generate deformation plot
                # Extract volcano_type as string for the function
                volcano_type_str = determine_volcano_type(selected_volcano)
                # Convert alert level to numeric steps (Normal=10, Advisory=25, Watch=40, Warning=50)
                alert_time_steps = {"Normal": 10, "Advisory": 25, "Watch": 40, "Warning": 50}.get(alert_level, 25)
                deformation_data = generate_deformation_plot(volcano_type_str, alert_time_steps, 50)
                print(deformation_data)  # Debugging step to inspect the outputdeformation_data = generate_deformation_plot(volcano_type_str, alert_time_steps, 50)
                
                # Technical information
                with st.expander("Technical Details", expanded=False):
                    st.markdown(f"""
                    **Volcano Type:** {volcano_type.replace('_', ' ').title()}
                    
                    **Characteristic Deformation Pattern:** {VOLCANO_TYPES[volcano_type]['deformation_pattern']}
                    
                    **Max Displacement:** {deformation_data['max_deformation']:.2f} cm
                    
                    **Typical Examples:** {', '.join(VOLCANO_TYPES[volcano_type]['examples'])}
                    
                    **Description:** {VOLCANO_TYPES[volcano_type]['description']}
                    """)
        
            if '2d_figure' in deformation_data:
                st.markdown("### InSAR-like Interferogram")
                st.plotly_chart(deformation_data['2d_figure'], use_container_width=True)
                try:
                    st.plotly_chart(deformation_data['2d_figure'], use_container_width=True)
                except KeyError as e:
                    st.error(f"KeyError: {str(e)} - The deformation data might be incomplete.")
                else:
                    st.error("The deformation plot could not be generated. Please check your input parameters.")
                    st.plotly_chart(deformation_data['2d_figure'], use_container_width=True)
        
        # Add 3D visualization in full width below
        if 'deformation_data' in locals() and '3d_figure' in deformation_data:
            st.markdown("### 3D Surface Deformation")
            st.plotly_chart(deformation_data['3d_figure'], use_container_width=True)
        else:
            st.warning("3D deformation data is not available for the selected volcano.")
            
            st.markdown("""
            **How to interpret:**
            - The 3D plot shows the actual ground displacement (unwrapped)
            - Upward movement (inflation) appears as peaks
            - Downward movement (deflation) appears as depressions
            - The pattern shape is related to the magma chamber's characteristics
            
            *Drag to rotate the 3D model for different perspectives*
            """)
    
    with tab2:
        st.header("Magma Chamber Dynamics")
        
        st.markdown("""
        This animation shows how magma accumulates in a volcano's magmatic system over time,
        and the resulting changes in surface displacement and pressure.
        
        The patterns differ based on the volcano type and current alert level, reflecting real
        monitoring data patterns observed at active volcanoes around the world.
        """)
        
        # Create subtabs for different magma chamber visualizations
        subtab1, subtab2, subtab3 = st.tabs([
            "Time Series Data", 
            "3D Magma Chamber Model", 
            "Animated Magma Flow"
        ])
        
        # Sidebar controls for all tabs
        st.sidebar.markdown("### Magma Chamber Parameters")
        
        # Volcano type selection
        volcano_type_options = list(VOLCANO_TYPES.keys())
        selected_volcano_type = st.sidebar.selectbox(
            "Select volcano type:",
            options=volcano_type_options,
            format_func=lambda x: x.replace('_', ' ').title(),
            key="chamber_type_selector"
        )
        
        # Alert level selection
        alert_level = st.sidebar.selectbox(
            "Select alert level:",
            options=list(ALERT_LEVELS.keys()),
            key="chamber_alert_selector"
        )
        
        # Time period for simulation
        time_period = st.sidebar.slider(
            "Simulation period (days):",
            min_value=7,
            max_value=90,
            value=30,
            step=1,
            key="chamber_time_slider_main"
        )
        
        # Information about selected volcano type
        with st.sidebar.expander("Volcano Type Information", expanded=False):
            st.markdown(f"""
            **{selected_volcano_type.replace('_', ' ').title()} Volcanoes**
            
            {VOLCANO_TYPES[selected_volcano_type]['description']}
            
            **Examples:** {', '.join(VOLCANO_TYPES[selected_volcano_type]['examples'])}
            
            **Magma Viscosity:** {VOLCANO_TYPES[selected_volcano_type]['magma_viscosity']}
            
            **Typical Eruption Style:** {VOLCANO_TYPES[selected_volcano_type]['eruption_style']}
            
            **Characteristic Deformation:** {VOLCANO_TYPES[selected_volcano_type]['deformation_pattern']}
            """)
        
        # Information about selected alert level
        with st.sidebar.expander("Alert Level Information", expanded=False):
            alert_info = ALERT_LEVELS[alert_level]
            st.markdown(f"""
            **{alert_level} Alert Level**
            
            {alert_info['description']}
            
            **Expected Deformation Rate:** {alert_info.get('deformation_rate', 'Not Available')}
            
            **Activity Level:** {alert_info.get('activity', 'Not Available')}
            """)
        
        # Time Series Animation Tab
        with subtab1:
            st.subheader("Magma Chamber Time Series")
            
            # Generate and display magma chamber animation
time_period = st.sidebar.slider(
    "Simulation period (days):",
    min_value=7,
    max_value=90,
    value=30,
    step=1,
    key="chamber_time_slider"
)

# Generate magma chamber animation
magma_animation = generate_magma_chamber_animation(
    selected_volcano_type, 
    alert_level,
    simulation_days=time_period
)

st.plotly_chart(magma_animation['figure'], use_container_width=True, key="magma_time_series")

st.markdown("""
            **How to interpret:**
            - **Magma Volume:** Shows magma accumulation in the chamber
            - **Surface Displacement:** Ground movement detected at the surface
            - **Pressure:** Internal pressure changes in the magmatic system
            
            *Click Play to start the animation*
            """)
        
        # 3D Magma Chamber Model Tab
with subtab2:
            st.subheader("3D Magma Chamber Model")
            
            st.markdown("""
            This 3D model shows the internal structure of the volcano's magmatic system based on 
            its type and current alert level. The visualization depicts:
            
            - **Surface morphology:** The characteristic shape of this volcano type
            - **Magma chamber:** The subsurface reservoir where magma accumulates
            - **Conduit system:** Pathways that magma follows to reach the surface
            
            *Drag to rotate, zoom, and pan the 3D model for different perspectives*
            """)
            
            # Generate 3D magma chamber model and get chamber metrics
            chamber_3d_fig, chamber_metrics_3d = generate_3d_magma_chamber(selected_volcano_type, alert_level)
            st.plotly_chart(chamber_3d_fig, use_container_width=True, key="magma_chamber_3d")
            
            # Additional information about the volcano structure
            with st.expander("Structure Details", expanded=False):
                st.markdown(f"""
                **{selected_volcano_type.replace('_', ' ').title()} Structure Characteristics**
                
                - **Chamber Depth:** {VOLCANO_TYPES[selected_volcano_type].get('chamber_depth', 'Variable')}
                - **Conduit System:** {VOLCANO_TYPES[selected_volcano_type].get('conduit_type', 'Simple vertical')}
                - **Secondary Features:** {VOLCANO_TYPES[selected_volcano_type].get('secondary_features', 'None')}
                
                The coloration represents the thermal state of the magma, with warmer colors
                indicating higher temperatures or more active/mobile magma regions. The alert level
                affects both the volume and activity level of the displayed magma system.
                """)
        
        # Animated Magma Flow Tab
with subtab3:
            st.subheader("Animated Magma Flow")
            
            st.markdown("""
            This animation shows the flow of magma through the volcano's plumbing system.
            The particles represent packets of magma moving through the system based on:
            
            - The physical properties of the volcano type
            - Current alert level (affects flow rate and pathways)
            - Pressure conditions in the magmatic system
            
            *Click Play to start the animation. Note how flow patterns differ with volcano type and alert level.*
            """)
            
            # Generate animated magma flow visualization and get chamber metrics
            flow_animation, chamber_metrics = generate_animated_magma_flow(selected_volcano_type, alert_level, frames=60)
            st.plotly_chart(flow_animation, use_container_width=True, key="magma_flow_animation")
            
            # Display chamber metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Magma Chamber Properties")
                metrics_table = {
                    "Property": ["Chamber Width", "Chamber Height", "Chamber Depth", "Magma Volume", "Accumulation Rate"],
                    "Value": [
                        f"{chamber_metrics['chamber_width']:.1f} km",
                        f"{chamber_metrics['chamber_height']:.1f} km",
                        f"{chamber_metrics['chamber_depth']:.1f} km",
                        f"{chamber_metrics['magma_volume']:.1f} km³",
                        f"{chamber_metrics['accumulation_rate']:.2f} km³/month"
                    ]
                }
                st.dataframe(metrics_table, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("Eruption Potential")
                # Display probability and other risk metrics
                st.markdown(f"""
                - **Probability:** {chamber_metrics['eruption_probability']}
                - **Potential VEI Range:** {chamber_metrics['est_vei_range']}
                - **Fill State:** {100 * float(chamber_metrics['magma_volume']) / (chamber_metrics['chamber_width'] * chamber_metrics['chamber_height'] * 2):.1f}%
                """)
                
                # Add volcano-specific details based on type
                if selected_volcano_type == 'shield':
                    st.markdown("**System characteristics:** Broad, shallow chamber with potential lateral dike intrusions")
                elif selected_volcano_type == 'stratovolcano':
                    if chamber_metrics.get('secondary_chamber', False):
                        st.markdown("**System characteristics:** Deep primary chamber with active secondary chamber")
                    else:
                        st.markdown("**System characteristics:** Deep primary chamber with simple plumbing")
                elif selected_volcano_type == 'caldera':
                    st.markdown(f"**System characteristics:** Large reservoir with {chamber_metrics.get('active_conduits', 2)} active conduits")
                elif selected_volcano_type == 'lava_dome':
                    if chamber_metrics.get('extrusion_volume', 0) > 0:
                        st.markdown(f"**System characteristics:** Viscous magma with active extrusion ({chamber_metrics['extrusion_volume']:.1f} km³)")
                    else:
                        st.markdown("**System characteristics:** Viscous magma with minimal extrusion")
            
            st.markdown("""
            **How to interpret:**
            - Moving particles represent magma flow through the system
            - Flow rate increases with higher alert levels
            - Different volcano types show characteristic flow patterns:
              - Shield volcanoes may show lateral flow through dikes
              - Stratovolcanoes typically have more focused vertical flow
              - Calderas may display complex, distributed flow patterns
              - Lava domes show slow, viscous movement in the upper conduit
            """)
            
            # Technical details
            with st.expander("Flow Physics", expanded=False):
                st.markdown(f"""
                **Magma Flow Properties**
                
                - **Viscosity:** {VOLCANO_TYPES[selected_volcano_type]['magma_viscosity']}
                - **Temperature Range:** {VOLCANO_TYPES[selected_volcano_type].get('temperature', '700-1200°C')}
                - **Gas Content:** {VOLCANO_TYPES[selected_volcano_type].get('gas_content', 'Variable')}
                - **Flow Rate ({alert_level}):** {ALERT_LEVELS[alert_level].get('flow_rate', 'Variable')}
                
                The animation models key aspects of magma rheology and flow dynamics in a simplified form,
                focusing on the most distinctive and educationally relevant behaviors.
                """)
    
with tab3:
        st.header("Eruption Sequence Animation")
        
        st.markdown("""
        This visualization shows how different monitoring parameters change throughout
        a volcanic eruption sequence, with patterns specific to each volcano type.
        
        The animation progresses through different eruption phases, showing characteristic
        patterns in lava flux, ash emission, seismicity, deformation, and gas emission.
        """)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Volcano selection
            selected_volcano_name = st.selectbox(
                "Select a volcano:",
                options=volcanoes_df['name'].unique(),
                key="eruption_volcano_selector"
            )
            
            if selected_volcano_name:
                # Get volcano data
                selected_volcano = volcanoes_df[volcanoes_df['name'] == selected_volcano_name].iloc[0].to_dict()
                volcano_type = determine_volcano_type(selected_volcano)
                
                # Display volcano info
                st.markdown(f"**Selected Volcano:** {selected_volcano_name}")
                st.markdown(f"**Type:** {volcano_type.replace('_', ' ').title()}")
                st.markdown(f"**Region:** {selected_volcano.get('region', 'Unknown')}")
                st.markdown(f"**Country:** {selected_volcano.get('country', 'Unknown')}")
                
                # Time steps slider
                time_steps = st.slider(
                    "Animation detail level:",
                    min_value=25,
                    max_value=150,
                    value=75,
                    step=25,
                    key="eruption_time_steps"
                )
                
                # Information about selected volcano type
                with st.expander("Eruption Style Information", expanded=False):
                    st.markdown(f"""
                    **{volcano_type.replace('_', ' ').title()} Volcanoes**
                    
                    {VOLCANO_TYPES[volcano_type]['description']}
                    
                    **Examples:** {', '.join(VOLCANO_TYPES[volcano_type]['examples'])}
                    
                    **Magma Viscosity:** {VOLCANO_TYPES[volcano_type]['magma_viscosity']}
                    
                    **Typical Eruption Style:** {VOLCANO_TYPES[volcano_type]['eruption_style']}
                    """)
        
        with col2:
            if 'selected_volcano' in locals():
                # Generate and display eruption sequence animation
                eruption_animation = generate_eruption_sequence_animation(
                    selected_volcano,
                    time_steps=time_steps
                )
                
                st.plotly_chart(eruption_animation['figure'], use_container_width=True)
                
                st.markdown("""
                **How to interpret:**
                - The animation shows the progression of a typical eruption for this volcano type
                - Different phases of the eruption are highlighted at the top
                - Each metric represents a different monitoring parameter:
                  - **Lava Flux:** Rate of lava emission
                  - **Ash Emission:** Amount of ash being ejected
                  - **Seismicity:** Earthquake activity
                  - **Deformation:** Ground movement (positive = inflation, negative = deflation)
                  - **Gas Emission:** Rate of gas release
                
                *The patterns are based on scientific studies of historical eruptions*
                """)
    
with tab4:
        st.header("Real InSAR Data Comparison")
        
        st.markdown("""
        Compare the simulated deformation patterns with real InSAR data from the COMET Volcano Portal.
        
        The Centre for Observation and Modelling of Earthquakes, Volcanoes and Tectonics (COMET)
        provides synthetic aperture radar (SAR) data showing actual ground deformation at volcanoes.
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Volcano selection
            selected_volcano_name = st.selectbox(
                "Select a volcano:",
                options=volcanoes_df['name'].unique(),
                key="insar_volcano_selector"
            )
            
            if selected_volcano_name:
                # Get volcano data
                selected_volcano = volcanoes_df[volcanoes_df['name'] == selected_volcano_name].iloc[0].to_dict()
                
                # Display volcano info
                st.markdown(f"**Selected Volcano:** {selected_volcano_name}")
                
                # Get location data for COMET matching
                location = {
                    'latitude': selected_volcano.get('latitude'),
                    'longitude': selected_volcano.get('longitude')
                }
                
                # Try to find matching volcano in COMET database
                with st.spinner("Searching for matching COMET data..."):
                    comet_volcano = get_matching_comet_volcano(selected_volcano['name'], location)
                
                if comet_volcano and 'id' in comet_volcano:
                    st.success(f"Found matching volcano in COMET database: {comet_volcano['name']}")
                    
                    # Get SAR data for this volcano
                    with st.spinner("Loading SAR datasets..."):
                        sar_data = get_comet_volcano_sar_data(comet_volcano['id'])
                    
                    if sar_data and len(sar_data) > 0:
                        st.info(f"Found {len(sar_data)} SAR datasets available")
                        
                        # Sort by date if available
                        if 'processingDatetime' in sar_data[0]:
                            sar_data = sorted(sar_data, key=lambda x: x.get('processingDatetime', ''), reverse=True)
                        
                        # Create a dropdown for selecting datasets if there are multiple
                        dataset_labels = []
                        for i, dataset in enumerate(sar_data):
                            label = f"Dataset {i+1}"
                            if 'processingDatetime' in dataset:
                                # Extract just the date part if it's a full datetime
                                date_str = dataset['processingDatetime'].split('T')[0] if 'T' in dataset['processingDatetime'] else dataset['processingDatetime']
                                label += f" ({date_str})"
                            if 'title' in dataset and dataset['title']:
                                label += f" - {dataset['title']}"
                            dataset_labels.append(label)
                        
                        selected_dataset_idx = st.selectbox(
                            "Select a SAR dataset:",
                            options=range(len(dataset_labels)),
                            format_func=lambda x: dataset_labels[x],
                            key="insar_dataset_selector"
                        )
                        
                        # Display the selected dataset
                        selected_dataset = sar_data[selected_dataset_idx]
                        
                        # Show dataset details
                        st.subheader("Dataset Details")
                        
                        if 'processingDatetime' in selected_dataset:
                            st.markdown(f"**Processing Date:** {selected_dataset['processingDatetime']}")
                        if 'title' in selected_dataset and selected_dataset['title']:
                            st.markdown(f"**Title:** {selected_dataset['title']}")
                        if 'sourceData' in selected_dataset and selected_dataset['sourceData']:
                            st.markdown(f"**Source Data:** {selected_dataset['sourceData']}")
                        if 'processingMethod' in selected_dataset and selected_dataset['processingMethod']:
                            st.markdown(f"**Processing Method:** {selected_dataset['processingMethod']}")
                    else:
                        st.warning("No SAR data available for this volcano in the COMET database.")
                else:
                    st.warning(f"No matching volcano found in the COMET database for {selected_volcano_name}.")
        
        with col2:
            if 'selected_volcano' in locals():
                # First, show the simulated deformation pattern
                st.subheader("Simulated Deformation Pattern")
                
                # Generate deformation plot
                volcano_type_str = determine_volcano_type(selected_volcano)
                alert_level = selected_volcano.get('alert_level', 'Normal')
                # Convert alert level to numeric steps (Normal=10, Advisory=25, Watch=40, Warning=50)
                alert_time_steps = {"Normal": 10, "Advisory": 25, "Watch": 40, "Warning": 50}.get(alert_level, 25)
                # Adding max_steps parameter (default to 50 for typical animation steps)
                deformation_data = generate_deformation_plot(volcano_type_str, alert_time_steps, 50)
                
                # Display 2D InSAR-like visualization
                st.plotly_chart(deformation_data['2d_figure'], use_container_width=True, key="deform_2d_plot")
                
                # If real COMET data is available, show it for comparison
                if 'comet_volcano' in locals() and 'selected_dataset' in locals():
                    st.subheader("Real COMET SAR Animation")
                    st.markdown("*Animation shows actual ground deformation patterns over time.*")
                    
                    # Display COMET SAR animation
                    display_comet_sar_animation(comet_volcano['id'], selected_dataset['id'])
    
    # Educational information about InSAR and volcano monitoring
with st.expander("About InSAR and Volcano Monitoring", expanded=False):
        st.markdown("""
        ### Interferometric Synthetic Aperture Radar (InSAR)
        
        InSAR is a radar technique used to detect and measure ground surface displacement with centimeter-to-millimeter precision. 
        It works by comparing the phase of radar waves reflected from Earth across multiple satellite passes.
        
        **Key concepts:**
        
        - **Interferogram:** A visualization showing ground displacement as a pattern of colored fringes
        - **Fringe:** One complete color cycle, typically representing 2.8 cm of displacement
        - **Line-of-sight (LOS):** Measurements are along the satellite's viewing angle
        
        ### Volcanological Applications
        
        InSAR is particularly useful for volcano monitoring because:
        
        1. **Magma Detection:** Can detect subsurface magma movement before visible signs appear
        2. **Wide Coverage:** Can monitor remote volcanoes over large areas
        3. **Historical Analysis:** Archives of SAR data allow analysis of past deformation events
        4. **Hazard Assessment:** Helps identify areas at risk from future activity
        
        ### Interpreting Patterns
        
        Different volcano types exhibit characteristic deformation patterns:
        
        - **Shield volcanoes:** Tend to show broad, radial inflation during magma accumulation
        - **Stratovolcanoes:** Often display asymmetric patterns due to complex structure
        - **Calderas:** May show ring-like patterns and complex subsidence/uplift interactions
        - **Dome complexes:** Typically produce very localized, high-gradient deformation
        
        *The animations on this page are based on scientific models that incorporate these patterns.*
        """)

if __name__ == "__main__":
    app()
