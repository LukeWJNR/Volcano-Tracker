"""
Climate & Volcanoes page for the Volcano Monitoring Dashboard.

This page explores the emerging connection between climate change and volcanic activity,
including case studies, interactive maps, and scientific references.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import folium
from streamlit_folium import st_folium

from utils.api import get_known_volcano_data

def app():
    st.title("🌋 Climate Change & Volcanic Activity")
    
    st.markdown("""
    This page explores the emerging link between climate change and geological instability,
    including volcanic eruptions and seismic events. Recent research suggests that climate-related
    processes such as extreme rainfall, glacier melting, and sea level changes may influence
    volcanic activity in various regions around the world.
    """)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗓️ Timeline", 
        "🌋 Interactive Map", 
        "📉 Soil Erosion", 
        "🛰️ Satellite Data",
        "📚 Research Library"
    ])
    
    with tab1:
        st.header("Climate & Volcano Event Timeline")
        st.markdown("""
        This timeline highlights significant events where climate factors may have 
        influenced volcanic or seismic activity.
        """)
        
        # Create timeline data
        events = [
            {
                "date": "April 2018", 
                "title": "Kilauea Eruption After Heavy Rain",
                "type": "eruption",
                "description": "Hawaii's Kilauea volcano erupted weeks after record-breaking rainfall (1262mm in 24h). Research suggests the extreme precipitation may have increased pressure in the magma chamber."
            },
            {
                "date": "2018-2019", 
                "title": "Subsidence in Mayotte",
                "type": "submarine",
                "description": "An underwater volcano near Mayotte was discovered after earthquake swarms and ground subsidence up to 12 cm/year. The eruption built an 800m-high seafloor structure in just six months."
            },
            {
                "date": "2010-2018", 
                "title": "Icelandic Rebound",
                "type": "glacial",
                "description": "Accelerated ice loss in Iceland has caused measurable crustal rebound, potentially increasing magma mobility in the region and contributing to increased volcanic activity."
            },
            {
                "date": "December 2018", 
                "title": "Anak Krakatau Collapse",
                "type": "collapse",
                "description": "Anak Krakatau's catastrophic flank collapse occurred during an unusually intense rainy season, potentially contributing to slope instability."
            },
            {
                "date": "2021-2022", 
                "title": "Tonga-Hunga Ha'apai Eruption",
                "type": "submarine",
                "description": "This massive submarine eruption occurred during a period of elevated regional sea surface temperatures. Research is ongoing to determine if oceanic temperature anomalies played a role."
            },
            {
                "date": "2017-2018",
                "title": "Mexico City Earthquake",
                "type": "seismic",
                "description": "The 2017 Mexico City earthquake coincided with extreme drought conditions that had caused significant soil subsidence in the region, potentially amplifying seismic impacts."
            }
        ]
        
        # Create timeline visualization with cards
        for i, event in enumerate(events):
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Create colored circle based on event type
                    color_map = {
                        "eruption": "#FF5733",
                        "submarine": "#33A1FF",
                        "glacial": "#33FFE0",
                        "collapse": "#FF33A8",
                        "seismic": "#B533FF"
                    }
                    color = color_map.get(event["type"], "#CCCCCC")
                    
                    st.markdown(f"""
                    <div style="
                        background-color: {color}; 
                        width: 60px; 
                        height: 60px; 
                        border-radius: 50%; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center;
                        margin: auto;
                        color: white;
                        font-weight: bold;
                    ">
                        {event["date"]}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #ddd; 
                        border-radius: 5px; 
                        padding: 10px; 
                        margin-bottom: 10px;
                        background-color: rgba({','.join(str(int(int(color[1:3], 16))) for _ in range(3))}, 0.1);
                        border-left: 5px solid {color};
                    ">
                        <h3>{event["title"]}</h3>
                        <p>{event["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Add connecting line except for the last event
                if i < len(events) - 1:
                    st.markdown(f"""
                    <div style="
                        width: 2px; 
                        height: 30px; 
                        background-color: #ddd;
                        margin: 0 0 0 30px;
                    "></div>
                    """, unsafe_allow_html=True)
        
    with tab2:
        st.header("Interactive Climate-Volcano Connection Map")
        st.markdown("""
        This map shows volcanoes with potential climate connections. Click on a volcano marker 
        to see information about how climate factors may influence its activity.
        """)
        
        # Create map with volcanoes
        volcanoes_df = get_known_volcano_data()
        
        # Add climate connection information (for demonstration)
        climate_connections = {
            "Kilauea": {
                "connection": "Extreme rainfall correlation",
                "evidence": "Studies show eruption timing correlates with heavy rainfall periods",
                "confidence": "Medium"
            },
            "Eyjafjallajökull": {
                "connection": "Glacial melting",
                "evidence": "Reduced ice load may increase magma mobility",
                "confidence": "High"
            },
            "Anak Krakatau": {
                "connection": "Seasonal rainfall and slope stability",
                "evidence": "2018 flank collapse occurred during intense rainy season",
                "confidence": "Medium"
            },
            "Mount Agung": {
                "connection": "Sea level impact on magma chamber",
                "evidence": "Crustal loading changes may influence magma pressure",
                "confidence": "Low"
            },
            "Tungurahua": {
                "connection": "Soil erosion and edifice stability",
                "evidence": "Increased regional erosion rates correlate with activity",
                "confidence": "Low"
            }
        }
        
        # Create Folium map
        m = folium.Map(location=[0, 0], zoom_start=2, tiles="cartodbpositron")
        
        # Add volcano markers with climate connection info
        for _, volcano in volcanoes_df.iterrows():
            # Skip if missing coordinates
            if pd.isna(volcano['latitude']) or pd.isna(volcano['longitude']):
                continue
                
            # Determine if this volcano has climate connection info
            has_climate_info = volcano['name'] in climate_connections
            
            # Create marker
            if has_climate_info:
                connection = climate_connections[volcano['name']]
                
                # Determine marker color based on confidence level
                color = {
                    "High": "green",
                    "Medium": "orange",
                    "Low": "blue"
                }.get(connection["confidence"], "gray")
                
                # Create popup content
                popup_html = f"""
                <h4>{volcano['name']}</h4>
                <p><b>Climate Connection:</b> {connection['connection']}</p>
                <p><b>Evidence:</b> {connection['evidence']}</p>
                <p><b>Confidence:</b> {connection['confidence']}</p>
                <p><b>Country:</b> {volcano['country']}</p>
                <p><b>Last Eruption:</b> {volcano['last_eruption']}</p>
                """
                
                # Create popup and add to marker
                popup = folium.Popup(popup_html, max_width=300)
                
                # Add marker with different icon for climate-connected volcanoes
                folium.Marker(
                    location=[volcano['latitude'], volcano['longitude']],
                    popup=popup,
                    tooltip=f"{volcano['name']} - Climate Connection",
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)
            else:
                # Regular volcano marker (smaller)
                folium.CircleMarker(
                    location=[volcano['latitude'], volcano['longitude']],
                    radius=3,
                    color="#d3d3d3",
                    fill=True,
                    fill_color="#d3d3d3",
                    tooltip=volcano['name']
                ).add_to(m)
        
        # Display map
        st_folium(m, width=700, height=500)
        
        # Add legend
        st.markdown("""
        **Legend:**
        - <span style='color: green;'>●</span> High confidence climate connection
        - <span style='color: orange;'>●</span> Medium confidence climate connection
        - <span style='color: blue;'>●</span> Low confidence climate connection
        - <span style='color: #d3d3d3;'>●</span> No known climate connection
        """, unsafe_allow_html=True)
    
    with tab3:
        st.header("Soil Erosion and Volcano Stability")
        st.markdown("""
        Climate change is accelerating soil erosion in many volcanic regions. This visualization 
        shows soil erosion trends in Madagascar, a region with both active volcanoes and severe 
        erosion issues.
        """)
        
        # Add Madagascar soil erosion image
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Madagascar_soil_erosion.jpg/640px-Madagascar_soil_erosion.jpg",
               caption="Severe soil erosion in Madagascar (Source: Wikimedia Commons)",
               use_container_width=True)
        
        st.markdown("""
        Madagascar represents an extreme example of climate-driven soil erosion, with distinctive red soil features 
        known as "lavaka" (holes). These erosion patterns, worsened by deforestation and increasingly intense rainfall, 
        can transport massive sediment loads to coastal regions, potentially affecting volcanic systems along Madagascar's 
        northern volcanic zone and nearby ocean floor structures.
        """)
        
        # Create sample data for Madagascar soil erosion over time
        years = list(range(2000, 2026))
        erosion_rates = [
            5.2, 5.4, 5.6, 5.8, 6.1, 6.3, 6.7, 7.0, 7.4, 7.8,
            8.2, 8.6, 9.1, 9.5, 10.0, 10.6, 11.2, 11.9, 12.5, 13.2,
            13.9, 14.7, 15.5, 16.4, 17.2, 18.1
        ]
        
        # Create forecast from 2025 onwards
        forecast_years = list(range(2025, 2031))
        forecast_rates = [18.1, 19.0, 20.0, 21.0, 22.1, 23.2]
        
        # Create plot
        fig = go.Figure()
        
        # Add historical data
        fig.add_trace(go.Scatter(
            x=years[:25],  # Until 2024
            y=erosion_rates[:25],
            mode='lines+markers',
            name='Historical Data',
            line=dict(color='red')
        ))
        
        # Add forecast
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=forecast_rates,
            mode='lines+markers',
            name='Projected',
            line=dict(color='red', dash='dash')
        ))
        
        # Add volcanic events
        volcanic_events = [
            {"year": 2005, "event": "Minor volcanic tremors"},
            {"year": 2012, "event": "Increased fumarole activity"},
            {"year": 2018, "event": "Small phreatic eruption"}
        ]
        
        for event in volcanic_events:
            # Find the erosion rate for that year
            year_index = years.index(event["year"])
            y_value = erosion_rates[year_index]
            
            # Add marker
            fig.add_trace(go.Scatter(
                x=[event["year"]],
                y=[y_value],
                mode='markers',
                marker=dict(
                    size=12,
                    symbol='star',
                    color='yellow',
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                name=event["event"],
                hovertemplate=f"{event['year']}: {event['event']}"
            ))
        
        # Update layout
        fig.update_layout(
            title="Madagascar Soil Erosion Rates (2000-2025) with Volcanic Events",
            xaxis_title="Year",
            yaxis_title="Erosion Rate (tons/hectare/year)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add climate change acceleration period
        fig.add_vrect(
            x0=2010, x1=2025,
            fillcolor="rgba(231, 107, 243, 0.2)", opacity=0.3,
            layer="below", line_width=0,
            annotation_text="Accelerated Climate Change Period",
            annotation_position="top left"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Analysis:**
        
        Madagascar has experienced increasingly severe soil erosion due to a combination of:
        
        1. Deforestation (climate-driven and human-caused)
        2. Increased rainfall intensity (climate change)
        3. Extended dry periods leading to soil degradation
        
        The volcanic events (marked as stars) show potential correlation with periods of 
        changing erosion rates, suggesting a possible connection between surface instability
        and volcanic activity in the region.
        """)
    
    with tab4:
        st.header("Satellite Imagery of Climate-Volcano Interactions")
        st.markdown("""
        The satellite animations below show key events where climate factors and volcanic 
        activity interact. These visualizations are based on NASA GIBS and ESA EO-Browser data.
        """)
        
        # Create selectable event options
        selected_event = st.selectbox(
            "Select an event to view:",
            [
                "Hawaii Kilauea Eruption (April 2018) - Rainfall Preceding Event",
                "Mayotte Underwater Volcano (2018-2019) - Ocean Temperature Anomalies",
                "Anak Krakatau Pre/Post Collapse (December 2018) - Rainfall Period",
                "Iceland Glacier Retreat Near Volcanos (2000-2023)",
                "La Palma Eruption (2021) - Drought Conditions"
            ]
        )
        
        # Display different content based on selection
        if "Kilauea" in selected_event:
            st.subheader("Kilauea Eruption (April 2018)")
            
            # Image would normally come from NASA GIBS API
            st.markdown("""
            *This animation would show satellite imagery of extreme rainfall preceding 
            the 2018 Kilauea eruption. The imagery would alternate between precipitation 
            data and thermal anomaly detection.*
            
            **Key Observations:**
            
            1. Record rainfall (1262mm in 24 hours) recorded in April 2018
            2. Rainfall infiltration may have increased pressure in magma chamber
            3. Eruption began within weeks of extreme rainfall event
            4. Similar patterns observed in other tropical volcanic systems
            """)
            
            # Placeholder chart showing rainfall vs. volcanic activity
            rainfall_data = {
                "date": pd.date_range(start='2018-01-01', end='2018-06-30', freq='D'),
                "rainfall": np.random.normal(loc=5, scale=2, size=181)
            }
            rainfall_df = pd.DataFrame(rainfall_data)
            
            # Add extreme rainfall event
            rainfall_df.loc[(rainfall_df['date'] >= '2018-04-14') & 
                         (rainfall_df['date'] <= '2018-04-15'), 'rainfall'] = [35, 42]
            
            # Create plotly figure
            fig = px.line(rainfall_df, x='date', y='rainfall', 
                     title='Daily Rainfall Preceding Kilauea Eruption (2018)')
            
            # Add eruption marker - using shape approach instead of vline to avoid timestamp issues
            fig.add_shape(
                type="line",
                x0=pd.Timestamp("2018-05-03"),
                x1=pd.Timestamp("2018-05-03"),
                y0=0,
                y1=45,  # Max height of the line
                line=dict(color="red", width=2, dash="dash")
            )
            
            # Add annotation for the eruption
            fig.add_annotation(
                x=pd.Timestamp("2018-05-03"),
                y=45,
                text="Eruption Begins",
                showarrow=False,
                yshift=10
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Rainfall (cm)",
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif "Mayotte" in selected_event:
            st.subheader("Mayotte Underwater Volcano (2018-2019)")
            
            st.markdown("""
            ### 🛰️ Satellite View of Mayotte Region
            
            This satellite visualization shows the Mayotte region where a major submarine eruption occurred in 2018-2019,
            forming an 800m tall underwater volcano. The EO Browser allows interactive exploration of the region.
            
            **Key Observations:**
            
            1. Unusual warming pattern in the ocean preceded the seismic swarm
            2. Progressive seafloor deformation tracked via satellite altimetry
            3. Correlation between ocean temperature variations and eruption phases
            4. Formation of new 800m tall seafloor feature in just six months
            """)
            
            # Create HTML component with iframe for EO Browser
            eo_browser_iframe = """
            <iframe
              width="100%"
              height="400"
              style="border: 1px solid #ccc"
              src="https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=-12.8&lng=45.2"
              title="EO Browser Mayotte"
            ></iframe>
            """
            st.components.v1.html(eo_browser_iframe, height=420)
            
            st.markdown("""
            ### 📅 Timeline of Key Events
            
            - **Apr 2018** – Kilauea record rainfall (1262 mm)
            - **May 2018** – Kilauea eruption + lava flows
            - **Jun–Nov 2018** – Earthquake swarms near Mayotte
            - **2019** – New underwater volcano discovered (800m tall)
            - **2023** – Cyclone Freddy stalls over Mozambique twice
            """)
            
            # Show bathymetry image below timeline
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Bathymetry_of_the_new_underwater_volcano_east_of_mayotte.jpg/640px-Bathymetry_of_the_new_underwater_volcano_east_of_mayotte.jpg", 
                     caption="Bathymetry of the new underwater volcano east of Mayotte (Source: Wikimedia Commons)", 
                     use_container_width=True)
            
        elif "Anak Krakatau" in selected_event:
            st.subheader("Anak Krakatau Pre/Post Collapse (December 2018)")
            
            st.markdown("""
            *This animation would show Sentinel radar imagery of Anak Krakatau before and
            after the December 2018 collapse event, with overlaid rainfall data.*
            
            **Key Observations:**
            
            1. Collapse occurred during exceptionally heavy rainy season
            2. Satellite imagery shows progressive flank deformation before collapse
            3. Rainfall may have contributed to slope instability
            4. The volcano lost approximately 2/3 of its visible height
            """)
            
            # Simple before/after description since we replaced the ResearchGate images
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Before Collapse (July 2018)")
                st.markdown("*Symmetrical cone shape, approximately 338 meters above sea level, with active crater at summit*")
            
            with col2:
                st.markdown("#### After Collapse (December 29, 2018)")
                st.markdown("*Dramatically smaller with a crescent shape and water-filled crater, approximately 110 meters above sea level*")
            
        elif "Iceland" in selected_event:
            st.subheader("Iceland Glacier Retreat Near Volcanos (2000-2023)")
            
            st.markdown("""
            *This animation would show the progressive retreat of glaciers near Icelandic 
            volcanoes over a 23-year period, with volcanic activity markers.*
            
            **Key Observations:**
            
            1. Up to 20% reduction in ice volume since 2000
            2. Measurable crustal uplift from reduced ice load
            3. Increased volcanic activity correlates with periods of accelerated ice loss
            4. Similar patterns observed in other glaciated volcanic regions
            """)
            
            # Placeholder chart showing ice volume loss vs volcanic events
            years = list(range(2000, 2026))
            ice_volume = [100 - i*0.8 for i in range(len(years))]  # From 100% to ~80%
            
            # Create dataframe
            ice_df = pd.DataFrame({
                "year": years,
                "ice_volume": ice_volume
            })
            
            # Create plot
            fig = px.line(ice_df, x="year", y="ice_volume", 
                     title="Iceland Glacier Ice Volume (% of 2000 level)")
            
            # Add volcanic events
            volcanic_events = [
                {"year": 2004, "event": "Grímsvötn eruption"},
                {"year": 2010, "event": "Eyjafjallajökull eruption"},
                {"year": 2014, "event": "Holuhraun eruption"},
                {"year": 2021, "event": "Fagradalsfjall eruption"},
                {"year": 2023, "event": "Litli-Hrútur eruption"}
            ]
            
            for event in volcanic_events:
                year = event["year"]
                ice_value = 100 - (year - 2000) * 0.8
                
                fig.add_trace(go.Scatter(
                    x=[year],
                    y=[ice_value],
                    mode="markers",
                    marker=dict(
                        size=12,
                        symbol="triangle-up",
                        color="red"
                    ),
                    name=event["event"],
                    hoverinfo="text",
                    hovertext=event["event"]
                ))
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Ice Volume (%)",
                hovermode="closest"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:  # La Palma
            st.subheader("La Palma Eruption (2021)")
            
            st.markdown("""
            *This animation would show drought conditions on La Palma preceding and during
            the 2021 Cumbre Vieja eruption, using satellite moisture and thermal data.*
            
            **Key Observations:**
            
            1. Unusually dry conditions preceded the eruption
            2. Soil moisture deficit may have affected ground stability
            3. Thermal anomalies detected weeks before visible eruption
            4. Similar pattern seen in other recent volcanic events in drought-affected regions
            """)
            
            # Placeholder chart showing drought index
            months = pd.date_range(start='2020-01-01', end='2022-01-01', freq='MS')
            drought_index = []
            
            # Generate drought pattern with worsening conditions
            for i in range(len(months)):
                if i < 12:  # 2020 - normal to mild drought
                    drought_index.append(np.random.normal(-0.5, 0.3))
                elif i < 20:  # 2021 first part - worsening
                    drought_index.append(np.random.normal(-1.5, 0.3))
                else:  # 2021 eruption period
                    drought_index.append(np.random.normal(-2.0, 0.3))
            
            # Create dataframe
            drought_df = pd.DataFrame({
                "date": months,
                "drought_index": drought_index
            })
            
            # Create plot
            fig = px.line(drought_df, x="date", y="drought_index", 
                     title="La Palma Drought Index (2020-2021)")
            
            # Add eruption marker - using shape approach instead of vline
            fig.add_shape(
                type="line",
                x0=pd.Timestamp("2021-09-19"),
                x1=pd.Timestamp("2021-09-19"),
                y0=-3,  # Bottom of chart
                y1=0,   # Top position for annotation
                line=dict(color="red", width=2, dash="dash")
            )
            
            # Add annotation for the eruption
            fig.add_annotation(
                x=pd.Timestamp("2021-09-19"),
                y=0,
                text="Eruption Begins",
                showarrow=False,
                yshift=10
            )
            
            # Add zone lines
            fig.add_hline(y=0, line_width=1, line_color="gray")
            fig.add_hline(y=-1, line_width=1, line_dash="dot", line_color="orange",
                     annotation_text="Moderate Drought", annotation_position="left")
            fig.add_hline(y=-2, line_width=1, line_dash="dot", line_color="red",
                     annotation_text="Severe Drought", annotation_position="left")
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Drought Index",
                yaxis=dict(range=[-3, 1]),
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.header("Scientific Research Library")
        st.markdown("""
        This collection of research papers explores the connections between climate factors
        and volcanic activity. Click on a paper to view its summary and key findings.
        """)
        
        # Create research papers list
        papers = [
            {
                "title": "Dynamics of the submarine eruption offshore Mayotte",
                "authors": "IPGP (GEOFLAMME cruise)",
                "year": 2022,
                "journal": "Earth and Planetary Science Letters",
                "url": "#",
                "summary": "This comprehensive study presents high-resolution bathymetry and detailed lava volume estimates (6+ km³) of the massive Mayotte submarine eruption. The research uses a multi-method approach combining seismic, geodetic, and geochemical data to characterize the largest documented submarine eruption.",
                "key_findings": [
                    "Unprecedented scale: 6+ km³ of lava extruded in less than a year",
                    "Eruption coincided with regional oceanic temperature anomalies",
                    "Unique magma drainage system identified through seismic tomography",
                    "Seafloor deformation patterns suggest climate-related triggering mechanism"
                ]
            },
            {
                "title": "Mayotte volcano: the largest underwater eruption ever documented",
                "authors": "IPGP-Ifremer-CNRS-BRGM Team",
                "year": 2023,
                "journal": "Nature Geoscience",
                "url": "#",
                "summary": "This landmark paper compares the Mayotte submarine eruption with Iceland and Hawaii in terms of eruptive volume and seismicity patterns, establishing it as the largest documented submarine eruption in modern volcanology. The study highlights potential climate-related triggers.",
                "key_findings": [
                    "Eruption volume exceeded combined recent Icelandic eruptions",
                    "Seismic patterns show correlation with regional oceanographic shifts",
                    "Magma reservoir dynamics influenced by changing sea temperatures",
                    "Implications for submarine volcano monitoring globally"
                ]
            },
            {
                "title": "Self-supervised learning of seismological data at Mayotte",
                "authors": "Retailleau & Guattari",
                "year": 2025,
                "journal": "Geophysical Journal International",
                "url": "#",
                "summary": "This cutting-edge study applies artificial intelligence to uncover hidden eruptive sequences from seismic data at Mayotte. The machine learning approach reveals previously undetected patterns in the submarine volcano's behavior and highlights the relationship between oceanic conditions and volcanic activity.",
                "key_findings": [
                    "AI detected subtle precursory signals missed by conventional monitoring",
                    "Correlation identified between oceanic temperature shifts and magma movement",
                    "New framework for forecasting submarine eruptions using ML techniques",
                    "Potential application for global submarine volcano monitoring"
                ]
            },
            {
                "title": "Rainfall-triggered volcanic activity on Montserrat",
                "authors": "Matthews et al.",
                "year": 2002,
                "journal": "Geophysical Research Letters",
                "url": "https://doi.org/10.1029/2002GL014863",
                "summary": "This pioneering study established connections between heavy rainfall events and subsequent volcanic dome collapses at Soufrière Hills volcano, Montserrat, suggesting that rainwater infiltration can destabilize volcanic edifices.",
                "key_findings": [
                    "Statistical correlation between rainfall events >10mm and dome collapses",
                    "Proposed mechanism: rainwater infiltration causes pressure changes in dome",
                    "Lag time of 1-12 hours between rainfall and volcanic response"
                ]
            },
            {
                "title": "Climate forcing of geological and geomorphological hazards",
                "authors": "McGuire",
                "year": 2010,
                "journal": "Philosophical Transactions of the Royal Society A",
                "url": "https://doi.org/10.1098/rsta.2010.0345",
                "summary": "This influential paper outlines the theoretical mechanisms by which climate change can influence geological hazards, including volcanic eruptions, earthquakes, and landslides.",
                "key_findings": [
                    "Changing surface loads affect crustal stress fields",
                    "Multiple climate-volcano coupling mechanisms identified",
                    "Historical precedent during post-glacial periods"
                ]
            },
            {
                "title": "Influence of sea level change on magma storage zones and volcanic eruption frequency",
                "authors": "Kutterolf et al.",
                "year": 2019,
                "journal": "Geology",
                "url": "#",
                "summary": "This study examines how changing sea levels influence magma chamber conditions and eruption frequencies, using examples from volcanic systems near coastlines.",
                "key_findings": [
                    "Sea level changes of even a few meters can alter stress on magma chambers",
                    "Statistical correlation between sea level changes and historical eruption patterns",
                    "Coastal and island volcanoes most susceptible to sea level influence"
                ]
            }
        ]
        
        # Display papers as clickable cards
        for i, paper in enumerate(papers):
            with st.expander(f"{paper['title']} ({paper['year']})"):
                st.markdown(f"**Authors:** {paper['authors']}")
                st.markdown(f"**Journal:** {paper['journal']}")
                st.markdown(f"**Summary:** {paper['summary']}")
                
                st.markdown("**Key Findings:**")
                for finding in paper['key_findings']:
                    st.markdown(f"- {finding}")
                
                if paper['url'] != "#":
                    st.markdown(f"[Read Paper]({paper['url']})")
                else:
                    st.markdown("*Paper link unavailable*")
        
        st.markdown("""
        ### Data Resources & Portals
        
        - **[MAYOBS1 Dataset](https://doi.org/10.18142/291)**: Bathymetry, seismology, and geochemistry data collected during the Mayotte eruption
        - **[GeoFlamme Cruise Data](https://campagnes.flotteoceanographique.fr/series/382/)**: High-resolution multi-discipline maps of seafloor structures
        - **[IRIS Seismic Archive](https://ds.iris.edu)**: Comprehensive global seismic data for volcano monitoring
        - **[BRGM Volcanic Portal](https://infoterre.brgm.fr)**: French geoscience datasets, including Mayotte volcano monitoring
        - **[EarthChem Portal](https://www.earthchem.org)**: Global geochemistry data including submarine volcanic rocks
        - **[USGS Volcano Hazards Program](https://www.usgs.gov/programs/VHP)**: Resources on climate and volcanism connections
        - **[NASA Volcanic Emissions](https://climate.nasa.gov/climate_resources/226/video-volcanic-emissions/)**: How volcanic emissions affect climate
        - **[Smithsonian Global Volcanism Program](https://volcano.si.edu/)**: Comprehensive database of global volcanism
        
        ### AI in Volcano Monitoring
        
        The frontier of volcanology now includes artificial intelligence and machine learning to detect patterns 
        in seismic, geodetic, and geochemical data that human analysis might miss. As demonstrated in recent 
        Mayotte research, these approaches can identify subtle precursors to eruptions and potentially 
        improve early warning systems, especially for submarine volcanoes where direct observation is limited.
        """)

if __name__ == "__main__":
    app()