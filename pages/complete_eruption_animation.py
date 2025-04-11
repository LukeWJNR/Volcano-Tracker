"""
Complete Eruption Animation for the Volcano Monitoring Dashboard.

This page shows a smooth, comprehensive eruption animation that covers the full eruption lifecycle
from magma buildup through seismic events to lava flow and ash emission.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.api import get_volcano_data
from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS
from utils.complete_eruption_animation import generate_complete_eruption_animation

def app():
    st.title("Complete Eruption Animation")
    
    st.markdown("""
    This page provides a comprehensive animation of the complete eruption cycle for different volcanoes.
    The visualization shows the progression from initial magma buildup through seismic activity
    to the eruption phases including lava flows and ash emissions.
    
    Each volcano type has a characteristic eruption pattern based on real-world scientific research.
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
    
    # Volcano name filter - show all volcanoes in selected region
    volcano_names = sorted(filtered_df["name"].unique().tolist())
    selected_volcano_name = st.sidebar.selectbox(
        "Select Volcano:", 
        volcano_names
    )
    
    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = determine_volcano_type(selected_volcano)
    
    # Display volcano information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Volcano Information")
        st.markdown(f"**Name:** {selected_volcano_name}")
        st.markdown(f"**Type:** {volcano_type.replace('_', ' ').title()}")
        st.markdown(f"**Country:** {selected_volcano.get('country', 'Unknown')}")
        st.markdown(f"**Region:** {selected_volcano.get('region', 'Unknown')}")
        
        # Volcano type description
        st.markdown("### Volcano Type Characteristics")
        if volcano_type in VOLCANO_TYPES:
            v_info = VOLCANO_TYPES[volcano_type]
            st.markdown(f"**Description:** {v_info['description']}")
            st.markdown(f"**Magma Viscosity:** {v_info['magma_viscosity']}")
            st.markdown(f"**Typical Eruption Style:** {v_info['eruption_style']}")
            st.markdown(f"**Similar Volcanoes:** {', '.join(v_info['examples'])}")
        
        # Animation settings
        st.markdown("### Animation Settings")
        animation_speed = st.slider(
            "Animation Speed",
            min_value=50,
            max_value=500,
            value=100,
            step=50,
            help="Higher values = faster animation"
        )
        
        detail_level = st.slider(
            "Detail Level",
            min_value=50,
            max_value=200,
            value=100,
            step=10,
            help="Higher values = smoother animation but slower loading"
        )
    
    with col2:
        st.subheader("Complete Eruption Animation")
        st.markdown("""
        This visualization shows the entire eruption cycle, from initial magma buildup
        through different phases including seismic activity, initial eruption, peak activity,
        and declining phases.
        
        The animation includes:
        - Magma volume changes
        - Seismic activity patterns
        - Ground deformation
        - Lava emission rates
        - Ash emission patterns
        - Gas emission levels
        
        Click the Play button to start the animation.
        """)
        
        # Generate and display the comprehensive eruption animation
        with st.spinner("Generating comprehensive eruption animation..."):
            eruption_animation = generate_complete_eruption_animation(
                selected_volcano,
                time_steps=detail_level
            )
            
            # Customize animation speed if needed
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
            
            st.plotly_chart(eruption_animation['figure'], use_container_width=True)
    
    # Scientific explanation section
    with st.expander("Scientific Explanation", expanded=False):
        st.markdown(f"""
        ## Eruption Patterns for {volcano_type.replace('_', ' ').title()} Volcanoes
        
        {VOLCANO_TYPES[volcano_type]['description']}
        
        ### Key Eruption Phases
        
        The typical eruption sequence for this volcano type includes:
        """)
        
        # List the phases specific to this volcano type
        for phase in eruption_animation['phases']:
            st.markdown(f"- **{phase['name']}:** {phase['duration']*100:.0f}% of eruption duration")
        
        st.markdown("""
        ### Parameter Interpretation
        
        - **Magma Volume:** Represents the amount of magma in the chamber
        - **Seismic Activity:** Shows earthquake frequency and intensity
        - **Ground Deformation:** Indicates inflation/deflation of the volcanic edifice
        - **Lava Emission:** Shows the rate of lava extrusion at the surface
        - **Ash Emission:** Represents the amount of ash ejected into the atmosphere
        - **Gas Emission:** Shows the rate of gas (SO2, CO2, etc.) released
        
        The patterns shown in this animation are based on scientific studies of historical eruptions
        and the physical characteristics of different volcano types. The timing and intensity
        of different parameters are interrelated - for example, increased seismic activity often
        precedes changes in ground deformation, which may in turn precede eruptive activity.
        """)
        
        # Add references
        st.markdown("""
        ### References
        
        1. Smithsonian Global Volcanism Program
        2. USGS Volcano Hazards Program
        3. Sigurdsson, H., et al. (2015). The Encyclopedia of Volcanoes. Academic Press.
        4. Parfitt, E. A., & Wilson, L. (2008). Fundamentals of Physical Volcanology. Blackwell Publishing.
        """)

if __name__ == "__main__":
    app()