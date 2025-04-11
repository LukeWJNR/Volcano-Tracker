"""
Favorites page for the Volcano Monitoring Dashboard
"""
import os
import sys
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_favorite_volcanoes, remove_favorite_volcano
from utils.map_utils import create_volcano_map, create_popup_html
from utils.api import get_volcano_details

# Set page config
st.set_page_config(
    page_title="Your Favorite Volcanoes",
    page_icon="❤️",
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

# Page header
st.title("❤️ Your Favorite Volcanoes")
st.markdown("""
This page displays all the volcanoes you've saved as favorites.
You can view them on a map or in a table format.
""")

# Get all favorite volcanoes
try:
    favorites = get_favorite_volcanoes()
    
    if not favorites or len(favorites) == 0:
        st.info("You haven't added any favorites yet. Go to the main page, select a volcano, and add it to your favorites!")
    else:
        # Create a DataFrame for display
        favorites_df = pd.DataFrame(favorites)
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Map View", "Table View"])
        
        with tab1:
            st.subheader("Map of Your Favorite Volcanoes")
            
            # Create the map
            m = folium.Map(location=[0, 0], zoom_start=2)
            
            # Add markers for each favorite
            for fav in favorites:
                folium.Marker(
                    location=[fav['latitude'], fav['longitude']],
                    popup=create_popup_html({
                        'name': fav['name'],
                        'region': fav.get('region', 'Unknown'),
                        'country': fav.get('country', 'Unknown'),
                        'id': fav['id']
                    }),
                    tooltip=fav['name'],
                    icon=folium.Icon(color='red', icon='heart', prefix='fa')
                ).add_to(m)
            
            # Add custom styling for the map to make it auto-scale
            st.markdown("""
            <style>
                /* Make the map container responsive */
                iframe {
                    width: 100%;
                    min-height: 450px;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Display the map to fill container
            folium_static(m)
        
        with tab2:
            st.subheader("Table of Your Favorite Volcanoes")
            
            # Display as a table
            display_df = favorites_df[['name', 'region', 'country', 'latitude', 'longitude']]
            display_df.columns = ['Name', 'Region', 'Country', 'Latitude', 'Longitude']
            st.dataframe(display_df, height=400)
            
            # Select a volcano to view details or remove
            selected_volcano = st.selectbox(
                "Select a volcano to view details or remove from favorites",
                options=favorites_df['name'].tolist(),
                index=None
            )
            
            if selected_volcano:
                selected_data = favorites_df[favorites_df['name'] == selected_volcano].iloc[0]
                
                st.markdown(f"### {selected_data['name']}")
                st.markdown(f"**Region:** {selected_data.get('region', 'Unknown')}")
                st.markdown(f"**Country:** {selected_data.get('country', 'Unknown')}")
                
                # Add button to remove from favorites
                if st.button(f"❌ Remove {selected_data['name']} from Favorites"):
                    try:
                        remove_favorite_volcano(selected_data['volcano_id'])
                        st.success(f"Removed {selected_data['name']} from favorites")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing from favorites: {str(e)}")
                
                # Link to view on main page
                st.markdown(f"[View this volcano on the main page](/)")
except Exception as e:
    st.error(f"Error loading favorites: {str(e)}")

# Link back to main page
st.markdown("---")
st.markdown("[← Back to Main Dashboard](/)")