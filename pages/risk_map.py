"""
Risk assessment heat map page for the Volcano Monitoring Dashboard
"""
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from utils.api import get_volcano_data
from utils.map_utils import create_risk_heatmap
from utils.risk_assessment import generate_risk_levels
from utils.db_utils import save_risk_assessment, get_highest_risk_volcanoes
from utils.insar_data import generate_smithsonian_wms_url

# Set page config
st.set_page_config(
    page_title="Volcanic Risk Heat Map",
    page_icon="🌋",
    layout="wide"
)

# Add custom styling
st.markdown("""
<style>
    /* Page styling for compact display */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
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
    
    /* Make map responsive */
    iframe {
        width: 100%;
        min-height: 500px;
    }
    
    /* Risk level colors */
    .low-risk { color: blue; }
    .moderate-risk { color: green; }
    .high-risk { color: orange; }
    .very-high-risk { color: red; }
</style>
""", unsafe_allow_html=True)

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

# Main title
st.title("🔥 Volcanic Risk Heat Map")

# Introduction 
st.markdown("""
This map displays a predictive volcanic risk assessment based on multiple factors:

1. **Alert levels** - Current volcanic alert status from monitoring agencies
2. **Eruption history** - How recently the volcano has erupted
3. **Volcano type** - Certain types (stratovolcanoes, calderas) present higher risks
4. **Monitoring coverage** - Volcanoes with less monitoring have higher uncertainty
5. **Regional activity** - Areas with recent elevated activity

The heat map intensity (blue to red) indicates the calculated risk level. 
Red/orange markers indicate volcanoes with high or very high risk assessments.
""")

# Display a loading message
with st.spinner("Generating volcanic risk assessment..."):
    # Load volcano data
    try:
        volcano_df = get_volcano_data()
        
        # Create the heat map
        heatmap, risk_df = create_risk_heatmap(volcano_df)
        
        # Display the map
        st.subheader("Volcanic Risk Heat Map")
        
        # Option to include Smithsonian WMS layer
        show_smithsonian = st.checkbox("Show Smithsonian Holocene Eruptions WMS Layer", value=False)
        
        if show_smithsonian:
            # Generate a global view of the Smithsonian WMS with better rendering
            smithsonian_global_url = "https://geoserver-apia.sprep.org/geoserver/global/wms?service=WMS&version=1.1.0&request=GetMap&layers=global%3AGlobal_2013_HoloceneEruptions_SmithsonianVOTW&bbox=-180.0%2C-90.0%2C180.0%2C90.0&width=1500&height=650&srs=EPSG%3A4326&format=application/openlayers"
            
            # Display an explanation
            st.info("This WMS layer displays the Smithsonian Global Volcanism Program's Holocene Eruptions dataset. The layer shows volcanoes with documented eruptions during the Holocene epoch (approximately the last 11,700 years).")
            
            # Show tabs for different regions to enable better viewing
            tab_global, tab_america, tab_asia_pacific, tab_europe_africa = st.tabs(["Global View", "Americas", "Asia-Pacific", "Europe & Africa"])
            
            with tab_global:
                # Global view
                st.markdown(f"[Open Global View in New Tab]({smithsonian_global_url})")
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:5px; border-radius:5px; margin-bottom:10px;">
                    <iframe src="{smithsonian_global_url}" width="100%" height="400" frameborder="0"></iframe>
                </div>
                """, unsafe_allow_html=True)
                
            with tab_america:
                # Americas view
                americas_url = "https://geoserver-apia.sprep.org/geoserver/global/wms?service=WMS&version=1.1.0&request=GetMap&layers=global%3AGlobal_2013_HoloceneEruptions_SmithsonianVOTW&bbox=-170.0%2C-60.0%2C-30.0%2C80.0&width=1000&height=800&srs=EPSG%3A4326&format=application/openlayers"
                st.markdown(f"[Open Americas View in New Tab]({americas_url})")
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:5px; border-radius:5px; margin-bottom:10px;">
                    <iframe src="{americas_url}" width="100%" height="400" frameborder="0"></iframe>
                </div>
                """, unsafe_allow_html=True)
                
            with tab_asia_pacific:
                # Asia-Pacific view
                asia_pacific_url = "https://geoserver-apia.sprep.org/geoserver/global/wms?service=WMS&version=1.1.0&request=GetMap&layers=global%3AGlobal_2013_HoloceneEruptions_SmithsonianVOTW&bbox=70.0%2C-60.0%2C-150.0%2C70.0&width=1000&height=800&srs=EPSG%3A4326&format=application/openlayers"
                st.markdown(f"[Open Asia-Pacific View in New Tab]({asia_pacific_url})")
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:5px; border-radius:5px; margin-bottom:10px;">
                    <iframe src="{asia_pacific_url}" width="100%" height="400" frameborder="0"></iframe>
                </div>
                """, unsafe_allow_html=True)
                
            with tab_europe_africa:
                # Europe-Africa view
                europe_africa_url = "https://geoserver-apia.sprep.org/geoserver/global/wms?service=WMS&version=1.1.0&request=GetMap&layers=global%3AGlobal_2013_HoloceneEruptions_SmithsonianVOTW&bbox=-30.0%2C-40.0%2C60.0%2C70.0&width=1000&height=800&srs=EPSG%3A4326&format=application/openlayers"
                st.markdown(f"[Open Europe & Africa View in New Tab]({europe_africa_url})")
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:5px; border-radius:5px; margin-bottom:10px;">
                    <iframe src="{europe_africa_url}" width="100%" height="400" frameborder="0"></iframe>
                </div>
                """, unsafe_allow_html=True)
            
        # Show the risk heatmap
        st_folium(heatmap, width=800, height=500)
        
        # Create risk statistics
        risk_counts = risk_df['risk_level'].value_counts().sort_index()
        risk_percentages = 100 * risk_counts / len(risk_df)
        
        # Create visualization of risk levels
        st.subheader("Risk Level Assessment")
        cols = st.columns(4)
        
        risk_levels = ['Low', 'Moderate', 'High', 'Very High']
        colors = ['blue', 'green', 'orange', 'red']
        
        for i, (level, color) in enumerate(zip(risk_levels, colors)):
            if level in risk_counts:
                count = risk_counts[level]
                percentage = risk_percentages[level]
                
                with cols[i]:
                    st.markdown(f"""
                    <div style="border-radius:5px; border:1px solid {color}; padding:10px; text-align:center;">
                        <h3 style="color:{color};">{level} Risk</h3>
                        <p style="font-size:2rem; margin:0; color:{color}; font-weight:bold;">{count}</p>
                        <p>volcanoes</p>
                        <p>{percentage:.1f}% of total</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Display the highest risk volcanoes
        st.subheader("Highest Risk Volcanoes")
        
        # Save risk assessment data to database
        with st.spinner("Saving risk assessments to database..."):
            # Process top high-risk volcanoes 
            for _, volcano in risk_df[risk_df['risk_factor'] >= 0.5].iterrows():
                # Get individual scores for detailed breakdown
                eruption_score = None
                type_score = None
                monitoring_score = None
                regional_score = None
                
                try:
                    # Save to database
                    save_risk_assessment(
                        volcano_data=volcano.to_dict(),
                        risk_factor=volcano['risk_factor'],
                        risk_level=volcano['risk_level'],
                        eruption_score=eruption_score,
                        type_score=type_score,
                        monitoring_score=monitoring_score,
                        regional_score=regional_score
                    )
                except Exception as e:
                    st.warning(f"Could not save risk assessment for {volcano['name']}: {str(e)}")
        
        # Get top 10 highest risk volcanoes
        top_risk = risk_df.sort_values('risk_factor', ascending=False).head(10)
        
        # Create a dataframe for display
        display_df = top_risk[['name', 'country', 'risk_level', 'risk_factor', 'alert_level', 'last_eruption']].copy()
        display_df.columns = ['Volcano', 'Country', 'Risk Level', 'Risk Factor', 'Alert Level', 'Last Eruption']
        
        # Apply styling to the Risk Level column
        def color_risk_level(val):
            if val == 'Very High':
                return 'color: red; font-weight: bold'
            elif val == 'High':
                return 'color: orange; font-weight: bold'
            elif val == 'Moderate':
                return 'color: green'
            else:
                return 'color: blue'
        
        # Display the styled table
        st.dataframe(
            display_df.style.applymap(color_risk_level, subset=['Risk Level']),
            use_container_width=True
        )
        
        # Risk assessment methodology
        with st.expander("Risk Assessment Methodology", expanded=False):
            st.markdown("""
            ### Risk Assessment Methodology
            
            The volcanic risk assessment model calculates a risk factor (0-1 scale) based on multiple weighted factors:
            
            #### Factors and Weights
            
            | Factor | Weight | Description |
            | ------ | ------ | ----------- |
            | Alert Level | 35% | Current official alert status from monitoring agencies |
            | Eruption History | 25% | How recently the volcano has erupted |
            | Volcano Type | 15% | Different volcano types have different eruption potentials |
            | Monitoring Coverage | 15% | Less monitored volcanoes have greater uncertainty |
            | Regional Activity | 10% | Some regions currently show heightened activity |
            
            #### Risk Categories
            
            - **Very High Risk (0.75-1.0)**: Volcanoes with current warnings, recent eruptions, and/or in highly active regions
            - **High Risk (0.5-0.75)**: Volcanoes showing significant activity or with recent historical eruptions
            - **Moderate Risk (0.25-0.5)**: Volcanoes with moderate activity levels or historical eruptions
            - **Low Risk (0-0.25)**: Dormant volcanoes or those with long periods since last activity
            
            > **Note**: This risk assessment is a simplified model for demonstration purposes and should not be used for official hazard planning. Always refer to official volcanic hazard warnings from geological surveys and monitoring agencies.
            """)
        
    except Exception as e:
        st.error(f"Error creating risk heat map: {str(e)}")
        
# Link back to main page
st.markdown("---")
st.markdown("[← Back to Main Dashboard](/)")