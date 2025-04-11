"""
Volcano News and External Resources page for the Volcano Monitoring Dashboard.

This page integrates external volcano monitoring and news resources into our dashboard.
"""

import streamlit as st

# Set page config
st.set_page_config(
    page_title="Volcano News & Resources",
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
</style>
""", unsafe_allow_html=True)

# Add navigation links
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("app.py", label="🏠 Main Dashboard", icon="🌋")
with col2:
    st.page_link("pages/sar_animations.py", label="📡 SAR Animations", icon="📡")
with col3:
    st.page_link("pages/risk_map.py", label="🔥 Risk Heat Map", icon="🔥")
with col4:
    st.page_link("pages/favorites.py", label="❤️ Your Favorites", icon="❤️")
with col5:
    st.page_link("pages/notes.py", label="📝 Your Notes", icon="📝")

st.markdown("---")

# Main title
st.title("🗞️ Volcano News & External Resources")

st.markdown("""
This page integrates external volcano monitoring resources and news feeds to provide comprehensive 
real-time information about volcanic activity worldwide.
""")

# Volcano Discovery Widget section
st.header("Volcano Discovery Live Map")

st.markdown("""
This live map from Volcano Discovery shows current volcanic activity around the world.
Click 'enlarge' in the top-right corner to view the map in full-screen mode.
""")

# Render the Volcano Discovery widget
volcano_discovery_widget_html = """
<!-- begin VolcanoWidget -->
<div id="VW_bigMap" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:999999;">
<div id="VW_backDiv" style="background:#000;filter:alpha(opacity=80);opacity:.8;height:100%;width:100%;position:absolute;top:0px;left:0px;z-index:-1;" onclick="switchFrame('VW_smallMap','VW_bigMap','enlarge','small map','100%','500px',0,-180);return false;"></div></div>
<div id="VW_smallMap" style="clear:left"><div id="VW_mCont" style="width:100%;height:500px;position:relative;margin:0;background:#fff;"><a name="VW_mCont"></a><div style="position:absolute;top:8px;right:28px;height:15px;text-align:right;vertical-align:middle;font:12px Verdana,sans-serif;font-weight:bold">[<a href="#" style="color:#bb202a" onclick="switchFrame('VW_smallMap','VW_bigMap','enlarge','small map','100%','500px',0,-180);return false;"><span id="VW_mSwitch">enlarge</span></a>]</div><iframe id="VW_iframe" width="100%" height="100%" scrolling="no" frameborder="0" marginwidth="0" marginheight="0" src="https://earthquakes.volcanodiscovery.com"></iframe></div></div>
<script type="text/javascript">function switchFrame(a,b,c,d,e,f,g,h){var i=document.getElementById("VW_mCont");var j=document.getElementById("VW_mSwitch").firstChild;if(j.nodeValue==c){j.nodeValue=d}else{j.nodeValue=c}var k=i.parentNode.getAttribute("id");if(k==a){var l=b}else{var l=a}var m=i.parentNode;var n=document.getElementById(l);n.appendChild(i);m.style.display="none";n.style.display="";if(l==a){i.style.width=e;i.style.height=f;i.style.margin=0;i.style.top=""}else{i.style.width="80%";i.style.height="80%";i.style.margin="auto";i.style.top="20px"}window.location.hash="VW_mCont"}</script>
<!-- end VolcanoWidget / http://www.volcano-news.com/active-volcanoes-map/get-widget.html -->
"""

st.markdown(volcano_discovery_widget_html, unsafe_allow_html=True)

st.markdown("""
*Source: [Volcano Discovery](https://www.volcanodiscovery.com)*
""")

# Add a section for other volcano monitoring resources
st.header("Additional Volcano Monitoring Resources")

# Create tabbed interface for different resources
tab1, tab2, tab3 = st.tabs(["USGS Volcano Updates", "Smithsonian Global Volcanism Program", "Icelandic Met Office"])

with tab1:
    st.subheader("USGS Volcano Hazards Program")
    st.markdown("""
    The USGS Volcano Hazards Program monitors and studies active and potentially active volcanoes, assesses their hazards, 
    and issues warnings of potential eruptions.
    """)
    
    # Display USGS embedded content
    st.markdown("""
    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:20px;">
        <iframe src="https://volcanoes.usgs.gov/vhp/updates.html" width="100%" height="600px" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("[Visit USGS Volcano Hazards Program](https://volcanoes.usgs.gov/index.html)")

with tab2:
    st.subheader("Smithsonian Global Volcanism Program")
    st.markdown("""
    The Smithsonian Global Volcanism Program documents, analyzes, and disseminates information about global volcanic activity.
    """)
    
    # Display Smithsonian embedded content
    st.markdown("""
    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:20px;">
        <iframe src="https://volcano.si.edu/gvp_currenteruptions.cfm" width="100%" height="600px" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("[Visit Smithsonian Global Volcanism Program](https://volcano.si.edu/)")

with tab3:
    st.subheader("Icelandic Meteorological Office - Volcano Monitoring")
    st.markdown("""
    The Icelandic Meteorological Office monitors volcanic activity in Iceland, one of the most volcanically active 
    regions in the world.
    """)
    
    # Display Icelandic Met Office embedded content
    st.markdown("""
    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin-bottom:20px;">
        <iframe src="https://en.vedur.is/earthquakes-and-volcanism/volcanic-eruptions/" width="100%" height="600px" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("[Visit Icelandic Meteorological Office](https://en.vedur.is/earthquakes-and-volcanism/volcanic-eruptions/)")

# Latest News Feed
st.header("Latest Volcano News")

# Create two columns for different news sources
col1, col2 = st.columns(2)

with col1:
    st.subheader("Volcano Discovery News")
    st.markdown("""
    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; height:400px; overflow-y:scroll;">
        <iframe src="https://www.volcanodiscovery.com/volcano-news.html" width="100%" height="1200px" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("USGS Volcano News")
    st.markdown("""
    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; height:400px; overflow-y:scroll;">
        <iframe src="https://www.usgs.gov/news/news-releases?field_topics_tid=78&field_state_territory_tid=All" width="100%" height="1200px" frameborder="0"></iframe>
    </div>
    """, unsafe_allow_html=True)

# Add a note about data sources
st.markdown("---")
st.markdown("""
**Note**: All information on this page is sourced from official volcano monitoring agencies and reputable scientific sources.
The external content is provided through iframes and may have varying update frequencies.
""")

# Link back to main page
st.markdown("[← Back to Main Dashboard](/)")

if __name__ == "__main__":
    pass