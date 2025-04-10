import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import time

from utils.api import get_volcano_data, get_volcano_details
from utils.map_utils import create_volcano_map, create_popup_html

# Set page config
st.set_page_config(
    page_title="Volcano Monitoring Dashboard",
    page_icon="🌋",
    layout="wide",
)

# App title and description
st.title("🌋 Volcano Monitoring Dashboard")
st.markdown("""
This dashboard displays real-time data about active volcanoes around the world, 
sourced from the USGS Volcano Hazards Program. You can explore the map, filter volcanoes, 
and access InSAR satellite imagery data for research and monitoring purposes.
""")

# Initialize session state for storing selected volcano
if 'selected_volcano' not in st.session_state:
    st.session_state.selected_volcano = None

if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Sidebar with filters
st.sidebar.title("Filters")

# Load volcano data
with st.spinner("Loading volcano data..."):
    try:
        volcanos_df = get_volcano_data()
        if st.session_state.last_update is None:
            st.session_state.last_update = datetime.now()
    except Exception as e:
        st.error(f"Error loading volcano data: {str(e)}")
        st.stop()

# Extract unique regions for filter
regions = sorted(volcanos_df['region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

# Name filter
volcano_name_filter = st.sidebar.text_input("Filter by Volcano Name")

# Apply filters
filtered_df = volcanos_df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['region'] == selected_region]

if volcano_name_filter:
    filtered_df = filtered_df[filtered_df['name'].str.contains(volcano_name_filter, case=False)]

# Display last update time
if st.session_state.last_update:
    st.sidebar.markdown(f"**Last updated:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Refresh button
if st.sidebar.button("Refresh Data"):
    with st.spinner("Refreshing volcano data..."):
        try:
            volcanos_df = get_volcano_data()
            st.session_state.last_update = datetime.now()
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error refreshing data: {str(e)}")

# Information about data source
st.sidebar.markdown("---")
st.sidebar.markdown("""
### Data Sources
- Volcano data: [USGS Volcano Hazards Program](https://www.usgs.gov/programs/VHP)
- InSAR data: Links to appropriate satellite imagery providers
""")

# Create two columns for the layout
col1, col2 = st.columns([7, 3])

with col1:
    # Create and display the map
    st.subheader("Active Volcano Map")
    
    # Display a message about the number of volcanos shown
    st.markdown(f"Showing {len(filtered_df)} volcanos")
    
    # Create the map
    m = create_volcano_map(filtered_df)
    
    # Display the map
    folium_static(m, width=800, height=500)

with col2:
    st.subheader("Volcano Information")
    
    if st.session_state.selected_volcano:
        volcano = st.session_state.selected_volcano
        
        st.markdown(f"### {volcano['name']}")
        st.markdown(f"**Region:** {volcano['region']}")
        st.markdown(f"**Country:** {volcano['country']}")
        
        # Alert level with color coding
        alert_level = volcano.get('alert_level', 'Unknown')
        alert_color = {
            'Normal': 'green',
            'Advisory': 'yellow',
            'Watch': 'orange',
            'Warning': 'red',
            'Unknown': 'gray'
        }.get(alert_level, 'gray')
        
        st.markdown(f"**Alert Level:** <span style='color:{alert_color};font-weight:bold;'>{alert_level}</span>", unsafe_allow_html=True)
        
        st.markdown(f"**Elevation:** {volcano['elevation']} meters")
        st.markdown(f"**Type:** {volcano['type']}")
        
        # Last eruption info
        if 'last_eruption' in volcano and volcano['last_eruption']:
            st.markdown(f"**Last Known Eruption:** {volcano['last_eruption']}")
        else:
            st.markdown("**Last Known Eruption:** Unknown")
        
        # Fetch and display additional details
        try:
            volcano_details = get_volcano_details(volcano['id'])
            
            if volcano_details:
                st.markdown("### Additional Information")
                
                if 'description' in volcano_details and volcano_details['description']:
                    st.markdown(f"**Description:** {volcano_details['description']}")
                
                if 'activity' in volcano_details and volcano_details['activity']:
                    st.markdown(f"**Recent Activity:** {volcano_details['activity']}")
        except Exception as e:
            st.warning(f"Could not load additional details: {str(e)}")
        
        # InSAR Data links
        st.markdown("### InSAR Satellite Data")
        
        # Sentinel Hub link
        sentinel_hub_url = f"https://www.sentinel-hub.com/explore/sentinelplayground/?zoom=12&lat={volcano['latitude']}&lng={volcano['longitude']}&preset=1_NATURAL_COLOR&layers=B01,B02,B03&maxcc=20&gain=1.0&gamma=1.0&time=2021-06-01%7C2021-12-01&atmFilter=&showDates=false"
        st.markdown(f"[View on Sentinel Hub]({sentinel_hub_url})")
        
        # ESA Copernicus link
        copernicus_url = f"https://scihub.copernicus.eu/dhus/#/home?latitude={volcano['latitude']}&longitude={volcano['longitude']}&zoom=12"
        st.markdown(f"[Search ESA Copernicus Data]({copernicus_url})")
        
        # USGS link
        usgs_url = f"https://www.usgs.gov/volcanoes/volcanoes-around-the-world/{volcano['name'].lower().replace(' ', '-')}"
        st.markdown(f"[USGS Volcano Information]({usgs_url})")
    else:
        st.info("Select a volcano on the map to view details")

# Function to handle volcano selection from the map
def handle_volcano_selection():
    # This function works with streamlit_folium's callbacks
    # That's handled in the map_utils.py file
    pass

# Create a placeholder for map click events
volcano_selector = st.empty()

# Manual volcano selection (as an alternative to map clicks)
st.markdown("### Can't use the map? Select a volcano from the list:")
selected_volcano_name = st.selectbox(
    "Choose a volcano",
    options=filtered_df['name'].tolist(),
    index=None,
    key="volcano_selector"
)

if selected_volcano_name:
    selected_volcano_data = filtered_df[filtered_df['name'] == selected_volcano_name].iloc[0].to_dict()
    st.session_state.selected_volcano = selected_volcano_data
    st.rerun()
