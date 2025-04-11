"""
SAR Animations page for the Volcano Monitoring Dashboard.

This page allows users to explore synthetic aperture radar (SAR) data and animations
from the COMET Volcano Portal, showing ground deformation patterns over time for various volcanoes.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

from utils.api import get_known_volcano_data
from utils.comet_utils import (
    get_comet_volcano_list,
    get_comet_volcano_by_name,
    get_comet_volcano_sar_data,
    display_comet_sar_animation,
    get_comet_url_for_volcano,
    get_matching_comet_volcano
)

def app():
    st.title("Volcano SAR Animations")
    
    st.markdown("""
    ## Synthetic Aperture Radar (SAR) Animations
    
    This page provides access to SAR data and animations from the 
    [COMET Volcano Portal](https://comet.nerc.ac.uk/comet-volcano-portal/), 
    showing ground deformation patterns over time for various volcanoes.
    
    SAR interferometry (InSAR) is a powerful technique for monitoring ground deformation at volcanoes,
    which can indicate magma movement, inflation, or other precursors to volcanic activity.
    
    ### How to Use
    
    1. Select a volcano from the dropdown menu
    2. View available SAR datasets
    3. Explore the animations showing deformation patterns over time
    
    *Data source: Centre for Observation and Modelling of Earthquakes, Volcanoes and Tectonics (COMET)*
    """)
    
    # Create two tabs for different ways to browse
    tab1, tab2 = st.tabs(["Search by Volcano", "Browse COMET Database"])
    
    with tab1:
        st.header("Search by Volcano Name")
        
        # Get volcano data from our main database
        try:
            volcanoes_df = get_known_volcano_data()
            
            # Sort volcanoes by name
            volcanoes_df = volcanoes_df.sort_values(by='name')
            
            # Volcano selection dropdown
            selected_volcano_name = st.selectbox(
                "Select a volcano:",
                options=volcanoes_df['name'].unique(),
                key="volcano_sar_selector"
            )
            
            if selected_volcano_name:
                # Get the selected volcano data
                selected_volcano = volcanoes_df[volcanoes_df['name'] == selected_volcano_name].iloc[0].to_dict()
                
                # Display basic volcano info
                st.subheader(f"{selected_volcano['name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Type:** {selected_volcano.get('type', 'Unknown')}")
                    st.markdown(f"**Region:** {selected_volcano.get('region', 'Unknown')}")
                
                with col2:
                    st.markdown(f"**Country:** {selected_volcano.get('country', 'Unknown')}")
                    st.markdown(f"**Alert Level:** {selected_volcano.get('alert_level', 'Unknown')}")
                
                # Get latitude and longitude
                location = {
                    'latitude': selected_volcano.get('latitude'),
                    'longitude': selected_volcano.get('longitude')
                }
                
                # Find matching volcano in COMET database
                with st.spinner("Searching for SAR data in COMET database..."):
                    comet_volcano = get_matching_comet_volcano(selected_volcano['name'], location)
                
                if comet_volcano and 'id' in comet_volcano:
                    # Success! Display COMET SAR data
                    st.success(f"Found matching volcano in COMET database: {comet_volcano['name']}")
                    
                    # Get SAR data for this volcano
                    with st.spinner("Loading SAR datasets..."):
                        sar_data = get_comet_volcano_sar_data(comet_volcano['id'])
                    
                    if sar_data and len(sar_data) > 0:
                        st.markdown(f"Found {len(sar_data)} SAR datasets available")
                        
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
                            key="sar_dataset_selector"
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
                        
                        # Display animation
                        st.subheader("SAR Animation")
                        st.markdown("*Animation shows ground deformation patterns over time. Each color cycle (fringe) represents approximately 2.8 cm of displacement.*")
                        
                        # Display animation in a container
                        display_comet_sar_animation(comet_volcano['id'], selected_dataset['id'])
                        
                        # Add explanatory text about SAR interpretation
                        with st.expander("How to Interpret SAR Animations", expanded=False):
                            st.markdown("""
                            ### Interpreting SAR Animations
                            
                            In these animations:
                            
                            - **Color cycles (fringes)** represent ground displacement
                            - Each complete color cycle typically equals 2.8 cm of movement
                            - Concentric rings of color often indicate inflation or deflation
                            - **Red to blue** typically shows movement away from the satellite
                            - **Blue to red** typically shows movement toward the satellite
                            
                            Ground deformation patterns can indicate:
                            
                            - **Inflation:** Magma rising or accumulating beneath the volcano
                            - **Deflation:** Magma withdrawal or post-eruption contraction
                            - **Asymmetric patterns:** May indicate complex magma plumbing or faulting
                            
                            *Note: Interpretation requires expertise and consideration of local context.*
                            """)
                    else:
                        st.info("No SAR data available for this volcano in the COMET database.")
                    
                    # Link to COMET volcano page
                    comet_url = f"https://comet.nerc.ac.uk/comet-volcano-portal/volcano/{comet_volcano['id']}/"
                    st.markdown(f"[View in COMET Volcano Portal]({comet_url})")
                else:
                    st.warning(f"No matching volcano found in the COMET database for {selected_volcano_name}.")
                    st.markdown("The COMET Volcano Portal may not cover this volcano, or it might be listed under a different name.")
                    st.markdown(f"[Search COMET Volcano Portal directly](https://comet.nerc.ac.uk/comet-volcano-portal/)")
        
        except Exception as e:
            st.error(f"Error loading volcano data: {str(e)}")
    
    with tab2:
        st.header("Browse COMET Database")
        
        # Load COMET volcano list
        with st.spinner("Loading COMET volcano database..."):
            comet_volcanoes = get_comet_volcano_list()
        
        if comet_volcanoes and len(comet_volcanoes) > 0:
            # Convert to dataframe for easier handling
            comet_df = pd.DataFrame(comet_volcanoes)
            
            # Add some columns if missing
            if 'country' not in comet_df.columns:
                comet_df['country'] = 'Unknown'
                
            # Display total count
            st.markdown(f"Found {len(comet_df)} volcanoes in the COMET database")
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                # Filter by name
                name_filter = st.text_input("Filter by volcano name:", key="comet_name_filter")
                
            with col2:
                # Filter by country if available
                available_countries = sorted(comet_df['country'].unique())
                selected_country = st.selectbox(
                    "Filter by country:",
                    options=["All"] + list(available_countries),
                    key="comet_country_filter"
                )
            
            # Apply filters
            filtered_df = comet_df.copy()
            
            if name_filter:
                filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False)]
                
            if selected_country != "All":
                filtered_df = filtered_df[filtered_df['country'] == selected_country]
                
            # Show filtered results count
            st.markdown(f"Showing {len(filtered_df)} volcanoes")
            
            # Paginate results to avoid overwhelming the UI
            items_per_page = 10
            total_pages = max(1, (len(filtered_df) + items_per_page - 1) // items_per_page)
            
            # Create page selection on a single line
            col1, col2 = st.columns([3, 1])
            with col2:
                page = st.number_input(
                    "Page",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="comet_page_selector"
                )
            
            # Calculate slice for current page
            start_idx = (page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(filtered_df))
            
            # Display current page items
            page_df = filtered_df.iloc[start_idx:end_idx]
            
            # Display as cards
            for _, volcano in page_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h3>{volcano['name']}</h3>
                        <p><strong>Country:</strong> {volcano.get('country', 'Unknown')}</p>
                        <p><strong>COMET ID:</strong> {volcano['id']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # View SAR data button
                        if st.button(f"View SAR Data", key=f"view_sar_{volcano['id']}"):
                            # Get SAR data for this volcano
                            with st.spinner("Loading SAR datasets..."):
                                sar_data = get_comet_volcano_sar_data(volcano['id'])
                            
                            if sar_data and len(sar_data) > 0:
                                st.success(f"Found {len(sar_data)} SAR datasets")
                                
                                # Display the first dataset
                                dataset = sar_data[0]
                                display_comet_sar_animation(volcano['id'], dataset['id'])
                            else:
                                st.info("No SAR data available for this volcano.")
                    
                    with col2:
                        # Link to COMET portal
                        comet_url = f"https://comet.nerc.ac.uk/comet-volcano-portal/volcano/{volcano['id']}/"
                        st.markdown(f"[Open in COMET Portal]({comet_url})")
                    
                    st.markdown("---")
            
            # Display pagination info
            st.caption(f"Page {page} of {total_pages}")
        else:
            st.error("Failed to load COMET volcano database. Please try again later.")
            st.markdown("[Visit COMET Volcano Portal directly](https://comet.nerc.ac.uk/comet-volcano-portal/)")

if __name__ == "__main__":
    app()