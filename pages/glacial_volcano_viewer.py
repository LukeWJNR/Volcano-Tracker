"""
Glacial Volcano Viewer page for the Volcano Monitoring Dashboard.

This page embeds a React-based visualization of glaciated volcanoes and their risk factors.
It provides a responsive grid of volcano risk cards with detailed information about each volcano.
"""

import streamlit as st

def app():
    st.title("Glacial Volcanoes Viewer")
    
    st.markdown("""
    ## Climate Change & Volcanic Activity
    
    This page presents detailed information about glaciated volcanoes around the world that may be affected by climate change.
    The melting of glaciers that cover these volcanoes can lead to:
    
    - Reduced confining pressure on magma chambers
    - Increased chances of explosive eruptions
    - Higher risk of lahars (volcanic mudflows)
    - Changes in hydrothermal systems
    
    The interactive cards below show risk assessments for each volcano, including:
    
    - Alert level and eruption type
    - Deformation rate measurements (mm/year)
    - SO₂ emission levels where available
    - Links to InSAR imagery for further analysis
    """)
    
    # Embed our React-based visualization using an iframe
    st.markdown("""
    <div style="margin-top: 20px;">
        <h3>Glaciated Volcano Risk Cards</h3>
        <iframe 
            src="http://localhost:3000/embed" 
            height="800" 
            style="width:100%;border:none;overflow:auto;">
        </iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Note:** The React application must be running on port 3000 for the embedded cards to display.
    Start the application by running `npm run dev` in the glacial-volcano-viewer directory.
    In a production environment, use the deployed URL of the React app instead of localhost.
    """)
    
    st.markdown("""
    ## Sources & Methodology
    
    Data for this visualization is sourced from:
    
    - Global Volcanism Program (GVP) database
    - InSAR satellite monitoring networks
    - Published research on climate-volcano interactions
    - Volcanic observatories worldwide
    
    Risk assessments are based on:
    
    - Historical eruption patterns
    - Current monitoring data
    - Glacier coverage and recent changes
    - Proximity to population centers
    """)
    
if __name__ == "__main__":
    app()