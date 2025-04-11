"""
User notes page for the Volcano Monitoring Dashboard
"""
import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# Add the root directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_utils import get_all_user_notes

# Set page config
st.set_page_config(
    page_title="Your Volcano Notes",
    page_icon="📝",
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
st.title("📝 Your Volcano Notes")
st.markdown("""
This page displays all the notes you've saved about various volcanoes.
Use this to keep track of your observations and research findings.
""")

# Get all user notes
try:
    notes = get_all_user_notes()
    
    if not notes or len(notes) == 0:
        st.info("You haven't added any notes yet. Go to the main page, select a volcano, and add some notes!")
    else:
        # Create a DataFrame for better display
        notes_df = pd.DataFrame([
            {
                "Volcano": note['volcano_name'],
                "Note": note['note_text'],
                "Date Added": note['created_at'],
                "Last Updated": note['updated_at'],
                "ID": note['volcano_id']
            } for note in notes
        ])
        
        # Add a button to return to main page for each volcano
        def handle_view_volcano(volcano_id, volcano_name):
            st.session_state.view_volcano_id = volcano_id
            st.session_state.view_volcano_name = volcano_name
            # This redirects to the main page with the selected volcano
            # The main page will need to handle this session state variable
            
        # Display each note in an expander
        for i, note in notes_df.iterrows():
            with st.expander(f"{note['Volcano']} - Updated: {note['Last Updated'].strftime('%Y-%m-%d')}"):
                st.markdown(f"**Note:**")
                st.markdown(note['Note'])
                st.markdown("---")
                st.markdown(f"*Created on {note['Date Added'].strftime('%Y-%m-%d %H:%M')}*")
                
                # Add a link to the main page
                st.markdown(f"[View this volcano on the main page](/)")
                
        # Option to download notes as CSV
        if st.button("Download All Notes as CSV"):
            csv = notes_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"volcano_notes_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
except Exception as e:
    st.error(f"Error loading notes: {str(e)}")

# Link back to main page
st.markdown("---")
st.markdown("[← Back to Main Dashboard](/)") 