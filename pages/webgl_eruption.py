"""
WebGL Eruption Animation for the Volcano Monitoring Dashboard.

This page provides a message that this visualization has been replaced by the Scientific 3D eruption page.
"""

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx, RerunData, RerunException

def app():
    st.title("Page Moved")
    
    st.warning("This page has been discontinued in favor of our improved Scientific 3D Eruption visualization.")
    
    st.markdown("""
    ### Please use the Scientific 3D Eruption page
    
    We have consolidated our 3D visualizations into a single, more scientifically accurate model.
    
    Please use the Scientific 3D Eruption page for a more comprehensive visualization experience.
    """)
    
    if st.button("Go to Scientific 3D Eruption"):
        # Get current page info
        ctx = get_script_run_ctx()
        if ctx is None:
            st.error("Could not navigate to the Scientific 3D Eruption page. Please use the sidebar navigation.")
            return
            
        # Generate new route for scientific_3d_eruption page
        new_page_name = "pages/scientific_3d_eruption.py"
        
        # Raise rerun exception to switch pages
        raise RerunException(
            RerunData(
                page_script_hash=ctx.page_script_hash,
                page_name=new_page_name,
            )
        )

if __name__ == "__main__":
    app()