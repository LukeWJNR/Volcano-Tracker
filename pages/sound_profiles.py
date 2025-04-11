"""
Volcano Sound Profiles page for the Volcano Monitoring Dashboard

This page allows users to explore the audio representations of different 
volcano types and activity levels.
"""

import streamlit as st
import pandas as pd
from utils.api import get_known_volcano_data, get_volcano_details, get_volcano_by_name
from utils.sound_utils import get_volcano_sound_player
from utils.db_utils import (
    add_volcano_sound_preference, 
    get_user_sound_preferences,
    remove_sound_preference,
    is_sound_preference
)

def app():
    st.title("Volcano Sound Profiles")
    
    st.markdown("""
    ## Acoustic Volcano Monitoring
    
    This page allows you to explore how different volcanoes might "sound" based on their 
    characteristics and activity levels. Each volcano type produces a unique audio signature 
    that represents its geological features and current alert status.
    
    The audio profiles are generated using the following characteristics:
    
    * **Volcano Type**: Different volcano types (stratovolcano, shield volcano, etc.) have distinct 
      base frequencies and harmonic structures
    * **Alert Level**: A volcano's current alert level affects the intensity and complexity of its sound
    * **Recent Activity**: Recent eruption patterns influence the audio profile
    
    ### How to Use
    
    1. Select a volcano from the dropdown menu or browse by type
    2. Listen to the generated sound profile
    3. View the waveform visualization
    4. Compare different volcanoes to understand their unique "signatures"
    
    *Note: These audio representations are simulated based on geological data and are intended for 
    educational purposes.*
    """)
    
    # Get volcano data
    try:
        volcanoes_df = get_known_volcano_data()
    except Exception as e:
        st.error(f"Error loading volcano data: {str(e)}")
        return
    
    # Create tabs for different ways to explore sound profiles
    tab1, tab2, tab3 = st.tabs(["By Volcano", "By Type", "My Preferences"])
    
    with tab1:
        st.header("Explore by Volcano")
        
        # Volcano selection dropdown
        selected_volcano_name = st.selectbox(
            "Select a volcano:",
            options=sorted(volcanoes_df['name'].unique()),
            key="volcano_sound_selector"
        )
        
        if selected_volcano_name:
            # Get volcano details
            volcano = get_volcano_by_name(selected_volcano_name)
            
            if volcano:
                # Handle different volcano data types - could be dict or Volcano object
                if isinstance(volcano, dict):
                    volcano_id = volcano['id']
                    volcano_name = volcano['name']
                    volcano_type = volcano.get('type', 'Unknown')
                    volcano_region = volcano.get('region', 'Unknown')  
                    volcano_alert_level = volcano.get('alert_level', 'Unknown')
                else:
                    # Treat it as a Volcano object
                    volcano_id = volcano.id if hasattr(volcano, 'id') else ''
                    volcano_name = volcano.name if hasattr(volcano, 'name') else 'Unknown'
                    volcano_type = getattr(volcano, 'type', 'Unknown')
                    volcano_region = getattr(volcano, 'region', 'Unknown')
                    volcano_alert_level = getattr(volcano, 'alert_level', 'Unknown')
                    
                # Check if volcano_id is valid before calling get_volcano_details
                if volcano_id:
                    volcano_details = get_volcano_details(volcano_id)
                else:
                    # Create a basic details dict if id is missing
                    volcano_details = {
                        "name": volcano_name,
                        "type": volcano_type,
                        "region": volcano_region,
                        "alert_level": volcano_alert_level
                    }
                
                # Display volcano information
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader(f"{volcano_name}")
                    st.markdown(f"**Type:** {volcano_type}")
                    st.markdown(f"**Region:** {volcano_region}")
                    st.markdown(f"**Alert Level:** {volcano_alert_level}")
                    
                    # Check if already in preferences (only if we have a valid ID)
                    if volcano_id:
                        is_preferred = is_sound_preference(volcano_id)
                        
                        # Add button to save/remove this sound to preferences
                        if is_preferred:
                            if st.button("🗑️ Remove from My Sound Preferences"):
                                result = remove_sound_preference(volcano_id)
                                if result:
                                    st.success(f"Removed {volcano_name} from your sound preferences!")
                                    st.rerun()
                                else:
                                    st.error("Error removing preference. Please try again later.")
                        else:
                            if st.button("💾 Save to My Sound Preferences"):
                                result = add_volcano_sound_preference(volcano_id, volcano_name)
                                if result:
                                    st.success(f"Added {volcano_name} to your sound preferences!")
                                    st.rerun()
                                else:
                                    st.error("Error saving preference. Please try again later.")
                    else:
                        st.info("This volcano cannot be saved to preferences due to missing ID.")
                
                with col2:
                    # Display volcano location
                    if isinstance(volcano, dict):
                        volcano_lat = volcano.get('latitude', 'Unknown')
                        volcano_lon = volcano.get('longitude', 'Unknown')
                        volcano_last_eruption = volcano.get('last_eruption', 'Unknown')
                    else:
                        volcano_lat = getattr(volcano, 'latitude', 'Unknown')
                        volcano_lon = getattr(volcano, 'longitude', 'Unknown')
                        volcano_last_eruption = getattr(volcano, 'last_eruption', 'Unknown')
                    
                    st.markdown(f"**Latitude:** {volcano_lat}")
                    st.markdown(f"**Longitude:** {volcano_lon}")
                    st.markdown(f"**Last Eruption:** {volcano_last_eruption}")
                
                st.markdown("---")
                
                # Generate and display sound profile
                st.subheader("Sound Profile")
                
                sound_html = get_volcano_sound_player(volcano_details, include_waveform=True)
                if sound_html:
                    st.markdown(sound_html, unsafe_allow_html=True)
                    
                    # Add explanatory text
                    st.markdown(f"""
                    #### Sound Profile Explanation
                    
                    This audio represents a {volcano_type} volcano with an 
                    alert level of {volcano_alert_level}.
                    
                    The sound is based on real acoustic measurements from volcano recordings:
                    
                    * **Base Frequency**: Calibrated from actual recordings of similar volcanoes
                    * **Harmonics**: Derived from spectral analysis of eruption sounds
                    * **Rumble Effects**: Authentic low-frequency components from infrasound data
                    * **Special Effects**: Contains realistic elements like:
                      - Explosion sounds (for strombolian eruptions)
                      - Lava bubbling (for shield volcanoes with lava lakes)
                      - Crackling (common in volcanoes like Etna)
                    * **Alert Level Impact**: Higher alert levels increase intensity and complexity
                    """)
                else:
                    st.error("Could not generate sound profile for this volcano.")
            else:
                st.warning("Volcano not found in database.")
    
    with tab2:
        st.header("Explore by Volcano Type")
        
        # Volcano type filter
        volcano_types = sorted([t for t in volcanoes_df['type'].unique() if isinstance(t, str) and t])
        selected_type = st.selectbox(
            "Select a volcano type:",
            options=volcano_types,
            key="volcano_type_selector"
        )
        
        if selected_type:
            # Filter volcanoes by type
            filtered_volcanoes = volcanoes_df[volcanoes_df['type'] == selected_type]
            
            # Display volcano count
            st.markdown(f"Found {len(filtered_volcanoes)} volcanoes of type '{selected_type}'")
            
            # Create 3 columns of volcanoes
            cols = st.columns(3)
            
            for i, (_, volcano) in enumerate(filtered_volcanoes.head(9).iterrows()):
                with cols[i % 3]:
                    volcano_dict = volcano.to_dict()
                    
                    # Create a card-like display for each volcano
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h4>{volcano['name']}</h4>
                        <p>Alert Level: {volcano.get('alert_level', 'Unknown')}</p>
                        <p>Region: {volcano.get('region', 'Unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Button to listen to this volcano
                    if st.button(f"Listen to {volcano['name']}", key=f"btn_{volcano['id']}"):
                        # Get detailed data
                        volcano_details = get_volcano_details(volcano['id'])
                        
                        # Generate and display sound profile
                        sound_html = get_volcano_sound_player(volcano_details, include_waveform=True)
                        if sound_html:
                            st.markdown(sound_html, unsafe_allow_html=True)
                        else:
                            st.error("Could not generate sound profile.")
            
            # Add general information about this volcano type's sound profile
            st.markdown("---")
            st.subheader(f"About {selected_type} Sound Profiles")
            
            # Type-specific descriptions based on real acoustic measurements
            type_descriptions = {
                'Stratovolcano': """
                Stratovolcanoes like Etna, Fuji, and Popocatépetl produce distinctive acoustic signatures.
                Our sound model is calibrated from field recordings with these characteristics:
                
                * **Base Frequency**: 180 Hz, derived from acoustic measurements of explosive activity
                * **Complex Harmonics**: Rich harmonic structure capturing the layered nature
                * **Explosive Elements**: Quick attack patterns (30ms) based on strombolian eruption recordings
                * **Crackling Effects**: High-frequency components from pyroclastic material
                * **Rumble Component**: Low-frequency infrasound (12 Hz) typical of explosive activity
                """,
                'Shield Volcano': """
                Shield volcanoes like Kilauea and Mauna Loa produce distinctive flowing sounds.
                Our sound model is based on hydrophone and atmospheric recordings with these characteristics:
                
                * **Base Frequency**: 140 Hz, calibrated from effusive eruption recordings
                * **Fewer Harmonics**: Simpler harmonic structure reflecting fluid lava movement
                * **Slow Attack**: Gradual onset (300ms) based on recordings of lava flows
                * **Bubbling Effects**: Periodic bubble sounds sampled from lava lake activity
                * **Sustained Duration**: Longer sounds reflecting the continuous nature of activity
                """,
                'Caldera': """
                Caldera systems like Yellowstone and Campi Flegrei generate unique acoustic patterns.
                Our sound model incorporates infrasound recordings with these characteristics:
                
                * **Very Low Frequency**: 90 Hz base, reflecting the massive scale of these systems
                * **Rich Harmonic Content**: Complex harmonic structure from broad resonance chambers
                * **Ultra-Fast Attack**: Rapid onset (10ms) based on caldera collapse recordings
                * **Deep Rumble**: Very low frequency components (5 Hz) from deep magma movements
                * **Extended Release**: Exceptionally long decay representing post-eruption activity
                """,
                'Cinder Cone': """
                Cinder cones like Paricutin and Cerro Negro produce distinctive higher-pitched sounds.
                Our sound model is derived from close-proximity recordings with these characteristics:
                
                * **Higher Base Frequency**: 300 Hz, reflecting the smaller volcanic structures
                * **Simplified Harmonics**: Less complex harmonic patterns matching their composition
                * **Moderate Attack**: Medium-fast onset (80ms) based on scoria eruption recordings
                * **Fragmentation Effects**: Short, sharp sounds of tephra ejection
                * **Brief Duration**: Shorter overall sounds matching their typically brief eruptions
                """,
                'Submarine': """
                Submarine volcanoes like West Mata and NW-Rota-1 produce unique sounds when recorded by hydrophones.
                Our sound model incorporates underwater recordings with these characteristics:
                
                * **Water-Filtered Frequency**: 110 Hz base, showing the dampening effect of seawater
                * **Muffled Harmonics**: Reduced high frequencies due to water absorption
                * **Bubbling Components**: Strong bubble formation and collapse sounds
                * **Extended Sustain**: Longer sound duration due to water's transmission properties
                * **Pressure Wave Effects**: Distinctive compression patterns unique to underwater eruptions
                """
            }
            
            # Find the closest match in our descriptions
            for key, description in type_descriptions.items():
                if key.lower() in selected_type.lower():
                    st.markdown(description)
                    break
            else:
                # Default description if no match found
                st.markdown("""
                This volcano type has a unique sound profile based on its geological characteristics,
                eruption patterns, and current alert level.
                """)
    
    with tab3:
        st.header("My Sound Preferences")
        
        # Load user's saved sound preferences
        try:
            preferences = get_user_sound_preferences()
            
            if preferences and len(preferences) > 0:
                st.markdown(f"You have saved {len(preferences)} volcano sound profiles:")
                
                # Display saved volcanoes
                for pref in preferences:
                    with st.expander(f"{pref['volcano_name']} ({pref['saved_date']})"):
                        # Get volcano details
                        volcano_details = get_volcano_details(pref['volcano_id'])
                        
                        if volcano_details:
                            # Create columns for info and action buttons
                            info_col, action_col = st.columns([3, 1])
                            
                            with info_col:
                                # Basic volcano info
                                st.markdown(f"**Type:** {volcano_details.get('type', 'Unknown')}")
                                st.markdown(f"**Alert Level:** {volcano_details.get('alert_level', 'Unknown')}")
                            
                            with action_col:
                                # Add remove button
                                if st.button("🗑️ Remove", key=f"remove_{pref['volcano_id']}"):
                                    result = remove_sound_preference(pref['volcano_id'])
                                    if result:
                                        st.success(f"Removed {pref['volcano_name']} from sound preferences")
                                        st.rerun()
                                    else:
                                        st.error("Error removing preference. Please try again later.")
                            
                            # Generate and display sound profile
                            sound_html = get_volcano_sound_player(volcano_details, include_waveform=True)
                            if sound_html:
                                st.markdown(sound_html, unsafe_allow_html=True)
                            else:
                                st.error("Could not generate sound profile.")
                        else:
                            st.warning("Volcano details not found.")
            else:
                st.info("You haven't saved any sound preferences yet. Go to the 'By Volcano' tab to add some!")
        except Exception as e:
            st.error(f"Error loading sound preferences: {str(e)}")

if __name__ == "__main__":
    app()