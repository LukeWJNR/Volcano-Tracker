import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime
import time
import os

from utils.api import get_volcano_data, get_volcano_details
from utils.map_utils import create_volcano_map, create_popup_html
from utils.web_scraper import get_volcano_additional_info
from utils.insar_data import get_insar_url_for_volcano, generate_sentinel_hub_url, generate_copernicus_url
from utils.wovodat_utils import (
    get_wovodat_volcano_data,
    get_so2_data,
    get_lava_injection_data,
    get_wovodat_insar_url,
    get_volcano_monitoring_status
)
from utils.db_utils import (
    add_favorite_volcano, 
    remove_favorite_volcano, 
    get_favorite_volcanoes, 
    is_favorite_volcano,
    add_search_history,
    get_search_history,
    add_user_note,
    get_user_note,
    get_all_user_notes,
    # New database functions
    get_volcano_characteristics,
    save_volcano_characteristics,
    get_volcano_eruption_history,
    add_eruption_event,
    get_volcano_satellite_images,
    add_satellite_image,
    get_volcano_risk_assessment
)

# Set page config
st.set_page_config(
    page_title="Volcano Monitoring Dashboard",
    page_icon="🌋",
    layout="wide",
    menu_items={
        'Get Help': 'https://github.com/openvolcano/data',
        'About': 'Volcano Monitoring Dashboard providing real-time information about active volcanoes worldwide with InSAR satellite imagery links.'
    }
)

# Custom CSS for iframe embedding
st.markdown("""
<style>
    /* Make the app more compact for iframe embedding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Adjust header sizes for compact display */
    h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
    
    /* Make sidebar narrower to maximize map space */
    [data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 250px !important;
    }
    
    /* Responsive adjustments for iframe */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem !important;
        }
        
        [data-testid="stSidebar"] {
            min-width: 200px !important;
            max-width: 200px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🌋 Volcano Monitoring Dashboard")
st.markdown("""
This dashboard displays real-time data about active volcanoes around the world, 
sourced from the USGS Volcano Hazards Program. You can explore the map, filter volcanoes, 
and access InSAR satellite imagery data for research and monitoring purposes.
""")

# Add navigation links
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("app.py", label="🏠 Main Dashboard", icon="🌋")
with col2:
    st.page_link("pages/favorites.py", label="❤️ Your Favorites", icon="❤️")
with col3:
    st.page_link("pages/notes.py", label="📝 Your Notes", icon="📝")
with col4:
    st.page_link("pages/risk_map.py", label="🔥 Risk Heat Map", icon="🔥")

st.markdown("---")

# Initialize session state for storing selected volcano
if 'selected_volcano' not in st.session_state:
    st.session_state.selected_volcano = None

if 'last_update' not in st.session_state:
    st.session_state.last_update = None
    
# Initialize other session state variables
if 'user_note' not in st.session_state:
    st.session_state.user_note = ""
    
if 'favorites' not in st.session_state:
    # Load favorites from database
    try:
        st.session_state.favorites = get_favorite_volcanoes()
    except Exception as e:
        st.session_state.favorites = []
        st.warning(f"Could not load favorites: {str(e)}")

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

# Track search filters
if 'last_region' not in st.session_state:
    st.session_state.last_region = "All"
    
if 'last_name_filter' not in st.session_state:
    st.session_state.last_name_filter = ""

# Apply filters
filtered_df = volcanos_df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['region'] == selected_region]
    
    # Track region change for search history
    if selected_region != st.session_state.last_region:
        try:
            add_search_history(selected_region, "region")
            st.session_state.last_region = selected_region
        except Exception as e:
            st.sidebar.warning(f"Could not save search history: {str(e)}")

if volcano_name_filter:
    filtered_df = filtered_df[filtered_df['name'].str.contains(volcano_name_filter, case=False)]
    
    # Track name filter change for search history
    if volcano_name_filter != st.session_state.last_name_filter:
        try:
            add_search_history(volcano_name_filter, "name")
            st.session_state.last_name_filter = volcano_name_filter
        except Exception as e:
            st.sidebar.warning(f"Could not save search history: {str(e)}")

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

# Favorite Volcanoes section in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Your Favorite Volcanoes")

# Display favorites
if st.session_state.favorites and len(st.session_state.favorites) > 0:
    for fav in st.session_state.favorites:
        if st.sidebar.button(f"🌋 {fav['name']}", key=f"fav_{fav['id']}"):
            # Find the volcano in the dataframe and set as selected
            selected_row = filtered_df[filtered_df['name'] == fav['name']]
            if not selected_row.empty:
                st.session_state.selected_volcano = selected_row.iloc[0].to_dict()
                st.rerun()
else:
    st.sidebar.info("You haven't added any favorites yet. Click on a volcano and use the 'Add to Favorites' button to save it here.")

# Search History section
if 'show_history' not in st.session_state:
    st.session_state.show_history = False

# Toggle for search history
st.sidebar.markdown("---")
show_history = st.sidebar.checkbox("Show Search History", value=st.session_state.show_history)
if show_history != st.session_state.show_history:
    st.session_state.show_history = show_history
    st.rerun()

if st.session_state.show_history:
    st.sidebar.subheader("Recent Searches")
    
    try:
        history = get_search_history(limit=5)
        if history and len(history) > 0:
            for item in history:
                st.sidebar.markdown(
                    f"**{item['search_term']}** ({item['search_type']}) - {item['created_at']}"
                )
        else:
            st.sidebar.info("No search history yet")
    except Exception as e:
        st.sidebar.warning(f"Could not load search history: {str(e)}")

# Information about data source
st.sidebar.markdown("---")
st.sidebar.markdown("""
### Data Sources
- Volcano data: [USGS Volcano Hazards Program](https://www.usgs.gov/programs/VHP)
- InSAR data: Links to appropriate satellite imagery providers
- Additional information: [Climate Links - Volcanoes](https://climatelinks.weebly.com/volcanoes.html)
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
    
    # Add custom styling and meta tags for proper iframe embedding
    st.markdown("""
    <head>
        <!-- Make sure content can be embedded in iframes -->
        <meta http-equiv="X-Frame-Options" content="ALLOWALL">
        <meta http-equiv="Access-Control-Allow-Origin" content="*">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <style>
        /* Make the map container responsive */
        iframe {
            width: 100%;
            min-height: 450px;
        }
        
        /* Additional iframe embedding optimization */
        body {
            overflow: auto;
        }
        
        /* Make sure the content fits within iframe bounds */
        .block-container {
            max-width: 100% !important;
            padding-left: 5px !important;
            padding-right: 5px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the map with full container width
    folium_static(m)

with col2:
    st.subheader("Volcano Information")
    
    if st.session_state.selected_volcano:
        volcano = st.session_state.selected_volcano
        
        # Favorite button
        is_favorite = is_favorite_volcano(volcano['id'])
        col_info, col_fav = st.columns([3, 1])
        
        with col_info:
            st.markdown(f"### {volcano['name']}")
        
        with col_fav:
            if is_favorite:
                if st.button("❤️ Remove from Favorites"):
                    try:
                        remove_favorite_volcano(volcano['id'])
                        st.success(f"Removed {volcano['name']} from favorites")
                        # Reload favorites
                        st.session_state.favorites = get_favorite_volcanoes()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing from favorites: {str(e)}")
            else:
                if st.button("🤍 Add to Favorites"):
                    try:
                        add_favorite_volcano(volcano)
                        st.success(f"Added {volcano['name']} to favorites")
                        # Reload favorites
                        st.session_state.favorites = get_favorite_volcanoes()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding to favorites: {str(e)}")
        
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
        
        # User Notes section
        st.markdown("### Your Notes")
        
        # Get existing note if any
        existing_note = get_user_note(volcano['id'])
        note_text = existing_note['note_text'] if existing_note else ""
        
        # Note input
        user_note = st.text_area(
            "Add your notes about this volcano:",
            value=note_text,
            height=100,
            key=f"note_{volcano['id']}"
        )
        
        # Save note button
        if st.button("Save Note"):
            if user_note:
                try:
                    add_user_note(volcano['id'], volcano['name'], user_note)
                    st.success("Note saved successfully!")
                except Exception as e:
                    st.error(f"Error saving note: {str(e)}")
            else:
                st.warning("Note is empty. Please add some text to save.")
        
        # InSAR Data links
        st.markdown("### InSAR Satellite Data")
        
        # Get specific InSAR URL for this volcano if available
        insar_url = get_insar_url_for_volcano(volcano['name'])
        if insar_url:
            st.markdown(f"[View InSAR Data for {volcano['name']}]({insar_url})")
            st.markdown("---")
        
        # Generate Sentinel Hub URL
        sentinel_hub_url = generate_sentinel_hub_url(volcano['latitude'], volcano['longitude'])
        st.markdown(f"[View on Sentinel Hub]({sentinel_hub_url})")
        
        # Generate ESA Copernicus URL
        copernicus_url = generate_copernicus_url(volcano['latitude'], volcano['longitude'])
        st.markdown(f"[Search ESA Copernicus Data]({copernicus_url})")
        
        # USGS link
        usgs_url = f"https://www.usgs.gov/volcanoes/volcanoes-around-the-world/{volcano['name'].lower().replace(' ', '-')}"
        st.markdown(f"[USGS Volcano Information]({usgs_url})")
        
        # ASF SARVIEWS link (if coordinates are available)
        if 'latitude' in volcano and 'longitude' in volcano:
            sarviews_url = f"https://sarviews-hazards.alaska.edu/#{volcano['latitude']},{volcano['longitude']},6"
            st.markdown(f"[ASF SARVIEWS (SAR Data)]({sarviews_url})")
        
        # WOVOdat Monitoring Data
        st.markdown("### WOVOdat Monitoring Data")
        with st.expander("View Monitoring Data from WOVOdat", expanded=False):
            with st.spinner("Loading WOVOdat data..."):
                try:
                    # Get WOVOdat volcano data
                    wovodat_data = get_wovodat_volcano_data(volcano['name'])
                    
                    if wovodat_data:
                        # Check if it's an Icelandic volcano or standard WOVOdat
                        if wovodat_data.get('is_iceland', False):
                            # Display Iceland-specific information
                            st.markdown("### Icelandic Volcano Monitoring")
                            st.markdown(f"[Icelandic Met Office Volcanic Monitoring]({wovodat_data['wovodat_url']})")
                            
                            if 'volcano_discovery_url' in wovodat_data:
                                st.markdown(f"[VolcanoDiscovery - Reykjanes]({wovodat_data['volcano_discovery_url']})")
                            
                            if 'icelandic_met_url' in wovodat_data:
                                st.markdown(f"[Latest Magma Movement - IMO]({wovodat_data['icelandic_met_url']})")
                                
                            if 'special_note' in wovodat_data:
                                st.info(wovodat_data['special_note'])
                        else:
                            # Standard WOVOdat link
                            st.markdown(f"[View on WOVOdat]({wovodat_data['wovodat_url']})")
                        
                        # Get monitoring status
                        monitoring_status = get_volcano_monitoring_status(volcano['name'])
                        
                        # Display monitoring status
                        st.markdown("#### Monitoring Status")
                        st.markdown(monitoring_status['description'])
                        
                        # Show source if available
                        if 'source' in monitoring_status:
                            st.caption(f"Source: {monitoring_status['source']}")
                        
                        # Create tabs for different types of monitoring data
                        if wovodat_data.get('is_iceland', False):
                            # Iceland-specific tabs
                            iceland_tab1, iceland_tab2, iceland_tab3, iceland_tab4 = st.tabs([
                                "Ground Deformation", "Gas Emissions", 
                                "Magma Movement", "Live Monitoring"
                            ])
                            
                            with iceland_tab1:
                                # InSAR/GPS data from Icelandic Met Office
                                insar_url = get_wovodat_insar_url(volcano['name'])
                                if insar_url:
                                    st.markdown(f"[View Ground Deformation Data]({insar_url})")
                                    st.markdown("The Icelandic Meteorological Office uses GPS and InSAR data to monitor ground deformation at Icelandic volcanoes. This helps detect magma movement and potential eruption precursors.")
                                    st.markdown("![InSAR Example](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/Mauna%20Loa%20interferogram.jpg)")
                                    st.caption("Example of InSAR interferogram showing ground deformation")
                                
                            with iceland_tab2:
                                # SO2 data from Icelandic Met Office
                                so2_data = get_so2_data(volcano['name'])
                                if so2_data:
                                    st.markdown(f"[View Gas Emission Data]({so2_data['url']})")
                                    st.markdown(so2_data['description'])
                                    if 'notes' in so2_data:
                                        st.markdown(so2_data['notes'])
                            
                            with iceland_tab3:
                                # Magma movement data
                                lava_data = get_lava_injection_data(volcano['name'])
                                if lava_data:
                                    st.markdown(f"[View Magma Movement/Eruption Data]({lava_data['url']})")
                                    st.markdown(lava_data['description'])
                                    
                                    # Special notes for Reykjanes
                                    if volcano['name'] == "Reykjanes" and 'notes' in lava_data:
                                        st.info(lava_data['notes'])
                                    
                                    if 'volcano_discovery_url' in lava_data:
                                        st.markdown(f"[VolcanoDiscovery - Additional Data]({lava_data['volcano_discovery_url']})")
                            
                            with iceland_tab4:
                                # Live monitoring from Icelandic Met Office
                                st.markdown("### Live Monitoring Data")
                                st.markdown("[Live Earthquake Data from Icelandic Met Office](https://en.vedur.is/earthquakes-and-volcanism/earthquakes)")
                                st.markdown("[Live Webcams of Volcanic Areas](https://www.ruv.is/frett/2023/03/30/live-feed-from-the-eruption)")
                                
                                # Embed an iframe with the IMO earthquake map
                                st.markdown("""
                                <iframe src="https://en.vedur.is/earthquakes-and-volcanism/earthquakes/reykjanespeninsula" 
                                width="100%" height="600" frameborder="0"></iframe>
                                """, unsafe_allow_html=True)
                        else:
                            # Standard WOVOdat tabs
                            wovodat_tab1, wovodat_tab2, wovodat_tab3 = st.tabs(["InSAR Data", "SO2 Emissions", "Lava Injection"])
                            
                            with wovodat_tab1:
                                # InSAR data from WOVOdat
                                insar_wovodat_url = get_wovodat_insar_url(volcano['name'])
                                if insar_wovodat_url:
                                    st.markdown(f"[View InSAR Data on WOVOdat]({insar_wovodat_url})")
                                    st.markdown("InSAR (Interferometric Synthetic Aperture Radar) data shows ground deformation, which can indicate magma movement beneath the volcano.")
                                    st.markdown("![InSAR Example](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/Mauna%20Loa%20interferogram.jpg)")
                                    st.caption("Example of InSAR interferogram showing ground deformation")
                                else:
                                    st.info("No InSAR data available for this volcano in WOVOdat.")
                            
                            with wovodat_tab2:
                                # SO2 data
                                so2_data = get_so2_data(volcano['name'])
                                if so2_data:
                                    st.markdown(f"[View SO2 Emission Data on WOVOdat]({so2_data['url']})")
                                    st.markdown(so2_data['description'])
                                    st.markdown("SO2 (sulfur dioxide) is a significant gas released during volcanic eruptions. Monitoring SO2 levels helps track volcanic activity and potential environmental impacts.")
                                else:
                                    st.info("No SO2 emission data available for this volcano in WOVOdat.")
                            
                            with wovodat_tab3:
                                # Lava injection data
                                lava_data = get_lava_injection_data(volcano['name'])
                                if lava_data:
                                    st.markdown(f"[View Eruption/Lava Data on WOVOdat]({lava_data['url']})")
                                    st.markdown(lava_data['description'])
                                    st.markdown("Lava injection and eruption data provides information about the volume, composition, and behavior of magma during volcanic activity.")
                                else:
                                    st.info("No lava injection/eruption data available for this volcano in WOVOdat.")
                    else:
                        st.info("This volcano does not have monitoring data in WOVOdat.")
                        st.markdown("[Visit WOVOdat](https://wovodat.org/gvmid/index.php?type=world) to explore other monitored volcanoes.")
                except Exception as e:
                    st.warning(f"Could not load WOVOdat data: {str(e)}")
        
        # Climate Links Information
        st.markdown("### Climate Links Information")
        with st.expander("View Educational Information", expanded=False):
            with st.spinner("Loading educational information..."):
                try:
                    climate_link_info = get_volcano_additional_info("https://climatelinks.weebly.com/volcanoes.html")
                    if climate_link_info and climate_link_info['content']:
                        # Display a subset of the content (first 500 characters) to keep it manageable
                        content = climate_link_info['content']
                        preview = content[:500] + "..." if len(content) > 500 else content
                        st.markdown(preview)
                        st.markdown(f"[Read more on Climate Links]({climate_link_info['source_url']})")
                    else:
                        st.info("No additional educational information available.")
                except Exception as e:
                    st.warning(f"Could not load educational information: {str(e)}")
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
