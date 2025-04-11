"""
Utility functions for accessing and displaying SAR data from the COMET Volcano Portal.

This module provides functionality to access and visualize synthetic aperture radar (SAR)
data from the Centre for Observation and Modelling of Earthquakes, Volcanoes and Tectonics
(COMET) Volcano Portal.
"""

import streamlit as st
import requests
from typing import Dict, List, Optional, Union
import os
import base64
from io import BytesIO
from PIL import Image
import json
import pandas as pd
from datetime import datetime
import time

# Base URL for the COMET Volcano Portal
COMET_BASE_URL = "https://comet.nerc.ac.uk/comet-volcano-portal/"
COMET_API_URL = "https://comet.nerc.ac.uk/api/v1/volcanos/"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cache', 'comet')
os.makedirs(CACHE_DIR, exist_ok=True)

# Cache timeout in seconds (24 hours)
CACHE_TIMEOUT = 86400

def get_comet_volcano_list() -> List[Dict]:
    """
    Fetches the list of volcanoes available in the COMET Volcano Portal.
    
    Returns:
        List[Dict]: List of volcano data from COMET
    """
    cache_file = os.path.join(CACHE_DIR, 'volcano_list.json')
    
    # Check if we have a cached version that's not too old
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < CACHE_TIMEOUT:
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error loading cached COMET volcano list: {str(e)}")
    
    try:
        response = requests.get(COMET_API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                st.warning(f"Error caching COMET volcano list: {str(e)}")
                
            return data
        else:
            st.error(f"Failed to fetch COMET volcano list. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching COMET volcano list: {str(e)}")
        return []

def get_comet_volcano_by_name(volcano_name: str) -> Optional[Dict]:
    """
    Find a volcano in the COMET database by name.
    
    Args:
        volcano_name (str): Volcano name to search for
        
    Returns:
        Optional[Dict]: Volcano data if found, None otherwise
    """
    volcanoes = get_comet_volcano_list()
    
    # Try exact match first
    for volcano in volcanoes:
        if volcano['name'].lower() == volcano_name.lower():
            return volcano
    
    # Try contains match
    for volcano in volcanoes:
        if volcano_name.lower() in volcano['name'].lower():
            return volcano
            
    return None

def get_comet_volcano_sar_data(volcano_id: Union[str, int]) -> List[Dict]:
    """
    Fetches SAR data for a specific volcano from the COMET Volcano Portal.
    
    Args:
        volcano_id (Union[str, int]): COMET volcano ID
        
    Returns:
        List[Dict]: List of SAR data entries for the volcano
    """
    cache_file = os.path.join(CACHE_DIR, f'volcano_{volcano_id}_sar.json')
    
    # Check if we have a cached version that's not too old
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < CACHE_TIMEOUT:
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error loading cached COMET SAR data: {str(e)}")
    
    url = f"{COMET_API_URL}{volcano_id}/sar/"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Cache the results
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                st.warning(f"Error caching COMET SAR data: {str(e)}")
                
            return data
        else:
            st.error(f"Failed to fetch COMET SAR data. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching COMET SAR data: {str(e)}")
        return []

def get_comet_sar_animation_url(volcano_id: Union[str, int], sar_id: Union[str, int]) -> str:
    """
    Generates URL for SAR animation for a specific volcano and SAR dataset.
    
    Args:
        volcano_id (Union[str, int]): COMET volcano ID
        sar_id (Union[str, int]): SAR dataset ID
        
    Returns:
        str: URL to the SAR animation
    """
    return f"{COMET_BASE_URL}volcano/{volcano_id}/sar/{sar_id}/"

def get_matching_comet_volcano(usgs_volcano_name: str, usgs_location: Dict = None) -> Optional[Dict]:
    """
    Attempts to find a matching volcano in the COMET database for a USGS volcano.
    
    Args:
        usgs_volcano_name (str): Name of the volcano from USGS
        usgs_location (Dict, optional): Location data for the USGS volcano
        
    Returns:
        Optional[Dict]: Matching COMET volcano data if found, None otherwise
    """
    # First try direct name match
    comet_volcano = get_comet_volcano_by_name(usgs_volcano_name)
    if comet_volcano:
        return comet_volcano
    
    # If we have location data, we could try to find the closest COMET volcano
    # This would require calculating distances between coordinates
    if usgs_location and 'latitude' in usgs_location and 'longitude' in usgs_location:
        comet_volcanoes = get_comet_volcano_list()
        if not comet_volcanoes:
            return None
            
        # Convert to dataframe for easier processing
        comet_df = pd.DataFrame(comet_volcanoes)
        
        # Calculate distance (simple Euclidean for quick comparison)
        if 'latitude' in comet_df.columns and 'longitude' in comet_df.columns:
            comet_df['distance'] = ((comet_df['latitude'] - usgs_location['latitude'])**2 + 
                                    (comet_df['longitude'] - usgs_location['longitude'])**2).apply(lambda x: x**0.5)
            
            # Get closest volcano
            closest = comet_df.loc[comet_df['distance'].idxmin()].to_dict()
            
            # Only return if it's relatively close (within ~50km)
            # This is a very rough approximation, could be improved
            if closest['distance'] < 0.5:  # ~50km at equator
                return closest
    
    return None

def display_comet_sar_animation(volcano_id: Union[str, int], sar_id: Union[str, int]) -> None:
    """
    Displays a SAR animation from the COMET Volcano Portal in Streamlit.
    
    Args:
        volcano_id (Union[str, int]): COMET volcano ID
        sar_id (Union[str, int]): SAR dataset ID
    """
    animation_url = get_comet_sar_animation_url(volcano_id, sar_id)
    
    # Display in an iframe with proper sizing
    st.markdown(f"""
    <div style="position: relative; padding-bottom: 75%; height: 0; overflow: hidden;">
      <iframe src="{animation_url}" 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:none;"
        allowfullscreen>
      </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    # Add direct link below
    st.markdown(f"[Open in COMET Volcano Portal]({animation_url})")

def get_comet_url_for_volcano(volcano_name: str, location: Dict = None) -> Optional[str]:
    """
    Generates a URL to the COMET Volcano Portal for a specific volcano.
    
    Args:
        volcano_name (str): Name of the volcano
        location (Dict, optional): Location data for the volcano
        
    Returns:
        Optional[str]: URL to the COMET page for the volcano, or None if not found
    """
    comet_volcano = get_matching_comet_volcano(volcano_name, location)
    
    if comet_volcano and 'id' in comet_volcano:
        return f"{COMET_BASE_URL}volcano/{comet_volcano['id']}/"
    
    return None

def display_comet_data_section(volcano_data: Dict) -> None:
    """
    Displays a section with COMET SAR data for a volcano in the dashboard.
    
    Args:
        volcano_data (Dict): Volcano data dictionary from the main dashboard
    """
    st.subheader("COMET SAR Data")
    
    try:
        location = {
            'latitude': volcano_data.get('latitude'),
            'longitude': volcano_data.get('longitude')
        }
        
        # Get matching COMET volcano
        comet_volcano = get_matching_comet_volcano(volcano_data['name'], location)
        
        if comet_volcano and 'id' in comet_volcano:
            st.success(f"Found matching volcano in COMET database: {comet_volcano['name']}")
            
            # Display basic info about the COMET entry
            st.markdown(f"**COMET ID:** {comet_volcano['id']}")
            if 'country' in comet_volcano:
                st.markdown(f"**Country:** {comet_volcano['country']}")
            
            # Get SAR data for this volcano
            sar_data = get_comet_volcano_sar_data(comet_volcano['id'])
            
            if sar_data and len(sar_data) > 0:
                st.markdown(f"Found {len(sar_data)} SAR datasets available")
                
                # Create tabs for different datasets if there are multiple
                if len(sar_data) > 1:
                    # Sort by date if available
                    if 'processingDatetime' in sar_data[0]:
                        sar_data = sorted(sar_data, key=lambda x: x.get('processingDatetime', ''), reverse=True)
                    
                    tabs = st.tabs([f"Dataset {i+1}" for i in range(min(5, len(sar_data)))])
                    
                    for i, tab in enumerate(tabs):
                        if i < len(sar_data):
                            with tab:
                                dataset = sar_data[i]
                                
                                # Display dataset info
                                if 'processingDatetime' in dataset:
                                    st.markdown(f"**Processing Date:** {dataset['processingDatetime']}")
                                if 'title' in dataset:
                                    st.markdown(f"**Title:** {dataset['title']}")
                                
                                # Link to animation
                                animation_url = get_comet_sar_animation_url(comet_volcano['id'], dataset['id'])
                                st.markdown(f"[View SAR Animation]({animation_url})")
                                
                                # Show embedded animation
                                with st.expander("Show Animation", expanded=i==0):
                                    display_comet_sar_animation(comet_volcano['id'], dataset['id'])
                else:
                    # Only one dataset, display it directly
                    dataset = sar_data[0]
                    
                    # Display dataset info
                    if 'processingDatetime' in dataset:
                        st.markdown(f"**Processing Date:** {dataset['processingDatetime']}")
                    if 'title' in dataset:
                        st.markdown(f"**Title:** {dataset['title']}")
                    
                    # Show embedded animation
                    with st.expander("Show SAR Animation", expanded=True):
                        display_comet_sar_animation(comet_volcano['id'], dataset['id'])
            else:
                st.info("No SAR data available for this volcano in the COMET database.")
                
            # Link to COMET volcano page
            comet_url = get_comet_url_for_volcano(volcano_data['name'], location)
            if comet_url:
                st.markdown(f"[View in COMET Volcano Portal]({comet_url})")
        else:
            st.info(f"No matching volcano found in the COMET database for {volcano_data['name']}.")
            # Provide link to main COMET portal
            st.markdown(f"[Search COMET Volcano Portal]({COMET_BASE_URL})")
    except Exception as e:
        st.error(f"Error displaying COMET data: {str(e)}")