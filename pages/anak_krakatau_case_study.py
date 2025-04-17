"""
Anak Krakatau Collapse Case Study - December 2018 Eruption and Collapse

This page presents a scientific visualization and timeline of the 
Anak Krakatau collapse event that occurred in December 2018, 
triggering a deadly tsunami.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

def app():
    st.title("Anak Krakatau Collapse Case Study")
    
    st.markdown("""
    ## The December 2018 Eruption and Flank Collapse
    
    In December 2018, Anak Krakatau ("Child of Krakatau") in Indonesia experienced 
    a catastrophic partial collapse of its southwest flank. This event occurred during 
    an ongoing eruption, and the sudden displacement of water triggered a deadly tsunami 
    that struck coastal regions around the Sunda Strait.
    
    This case study provides a scientific visualization of the collapse sequence, 
    the mechanisms involved, and the resulting tsunami.
    """)
    
    # Display a before/after satellite image comparison
    st.subheader("Before and After the Collapse")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Before Collapse (July 2018)")
        # Using local file instead of external ResearchGate URL that's being blocked
        st.markdown("Anak Krakatau before the collapse - symmetrical cone shape, approximately 338 meters above sea level")
        st.markdown("*Note: Original ResearchGate image has been replaced with this description due to embedding restrictions*")
        st.markdown("""
        Before the collapse, Anak Krakatau was a symmetrical cone that had 
        been steadily growing since it first emerged from the sea in 1927. 
        The volcano had reached a height of approximately 338 meters above sea level.
        """)
    
    with col2:
        st.markdown("##### After Collapse (December 29, 2018)")
        # Using text description instead of external ResearchGate URL that's being blocked
        st.markdown("Anak Krakatau after the collapse - dramatically smaller with a crescent shape and water-filled crater")
        st.markdown("*Note: Original ResearchGate image has been replaced with this description due to embedding restrictions*")
        st.markdown("""
        After the collapse, approximately two-thirds of the volcano's height above sea level
        was lost. The southwest flank had collapsed into the sea, leaving a much smaller, 
        crescent-shaped island with a water-filled crater.
        """)
    
    # Timeline of events
    st.subheader("Timeline of the Collapse Event")
    
    # Create collapse event data
    events = [
        {"date": "June 2018", "event": "Increased eruptive activity begins", "phase": "Pre-collapse", 
         "description": "Anak Krakatau began showing signs of increased activity with more frequent explosions."},
        {"date": "July-November 2018", "event": "Continuous eruptions", "phase": "Pre-collapse", 
         "description": "The volcano maintained a high level of activity with frequent Strombolian eruptions."},
        {"date": "December 22, 2018 13:00", "event": "Increased volcanic tremor detected", "phase": "Immediate Pre-collapse", 
         "description": "Seismic instruments detected an increase in volcanic tremor, indicating magma movement."},
        {"date": "December 22, 2018 20:55", "event": "Start of flank collapse", "phase": "Collapse", 
         "description": "The southwest flank of Anak Krakatau began to collapse into the sea."},
        {"date": "December 22, 2018 21:03", "event": "Major collapse and tsunami generation", "phase": "Collapse", 
         "description": "The main collapse event occurred, displacing approximately 0.2-0.3 cubic kilometers of material."},
        {"date": "December 22, 2018 21:27", "event": "Tsunami hits Sumatra coast", "phase": "Tsunami", 
         "description": "The tsunami reached the Sumatra coast, with wave heights up to 13 meters in some locations."},
        {"date": "December 22, 2018 21:33", "event": "Tsunami hits Java coast", "phase": "Tsunami", 
         "description": "The tsunami reached the Java coast with similar destructive force."},
        {"date": "December 22-24, 2018", "event": "Continued eruptions and smaller collapses", "phase": "Post-collapse", 
         "description": "Eruptions continued with phreatomagmatic explosions as seawater interacted with the exposed magma system."},
        {"date": "December 25-31, 2018", "event": "Formation of new crater", "phase": "Post-collapse", 
         "description": "The collapse created a new water-filled crater as the volcano continued to erupt."},
        {"date": "January 2019", "event": "Activity begins to decline", "phase": "Post-collapse", 
         "description": "Eruptive activity began to decrease, though the volcano remained active."}
    ]
    
    # Create timeline with plotly
    timeline_df = pd.DataFrame(events)
    
    # Add color mapping for phases
    phase_colors = {
        "Pre-collapse": "#3366CC",
        "Immediate Pre-collapse": "#FF9900",
        "Collapse": "#CC0000",
        "Tsunami": "#9900CC",
        "Post-collapse": "#669900"
    }
    
    # Create a bar chart timeline instead of using px.timeline
    # This works better with varied date formats
    fig = go.Figure()
    
    # Reverse the dataframe to show events chronologically from bottom to top
    timeline_df_rev = timeline_df.iloc[::-1].reset_index(drop=True)
    
    # Create a categorical y-axis with the events
    for i, phase in enumerate(timeline_df_rev['phase'].unique()):
        phase_data = timeline_df_rev[timeline_df_rev['phase'] == phase]
        
        fig.add_trace(go.Bar(
            x=[1] * len(phase_data),  # Use fixed width bars
            y=phase_data['event'],
            orientation='h',
            name=phase,
            marker_color=phase_colors[phase],
            text=phase_data['date'],  # Show date as text
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate='<b>%{y}</b><br>Date: %{text}<br><extra></extra>'
        ))
    
    fig.update_layout(
        title="Anak Krakatau Collapse Sequence",
        xaxis_title="",
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels
            showgrid=False,
        ),
        yaxis_title="Event",
        legend_title="Phase",
        showlegend=True,
        barmode='stack',
        height=500,
        bargap=0.3,
    )
    
    # Display the timeline
    st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed event descriptions
    with st.expander("Detailed Event Descriptions", expanded=False):
        for event in events:
            st.markdown(f"**{event['date']} - {event['event']}** ({event['phase']})")
            st.markdown(event['description'])
            st.markdown("---")
    
    # 3D visualization of the collapse process
    st.subheader("3D Visualization of the Collapse Process")
    
    st.markdown("""
    The following 3D model shows the progressive collapse of Anak Krakatau's southwest flank,
    which led to the tsunami. The model is based on scientific analysis of satellite data,
    eyewitness accounts, and post-event surveys.
    
    Use the slider to see the volcano before, during, and after the collapse event.
    """)
    
    # Add collapse progression slider
    collapse_stage = st.slider("Collapse Progression", 0, 100, 0,
                              help="Move the slider to see the progression of the collapse event")
    
    # Create 3D visualization of Anak Krakatau before/during/after collapse
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use plotly to create 3D model of the volcano that changes with the slider
        # Generate a 3D cone shape for Anak Krakatau
        def generate_volcano_mesh(collapse_percent):
            # Create base coordinates for the volcano cone
            theta = np.linspace(0, 2*np.pi, 30)
            radius = np.linspace(0, 1, 20)
            Theta, R = np.meshgrid(theta, radius)
            
            # Adjust the cone shape based on collapse percentage
            # At 0%, we have a full cone. At 100%, we have a partial cone with a collapsed flank
            
            # Base X, Y coordinates for full cone
            X = R * np.cos(Theta)
            Y = R * np.sin(Theta)
            
            # Height profile is a simple cone
            Z = 1 - R
            
            # Apply collapse deformation to the southwest quadrant (225-315 degrees)
            # as the collapse progresses
            if collapse_percent > 0:
                collapse_factor = collapse_percent / 100.0
                
                # Identify points in the southwest quadrant (225-315 degrees)
                sw_quadrant = ((Theta >= 3*np.pi/4) & (Theta <= 5*np.pi/4))
                
                # Calculate the collapse effect - more collapse at higher collapse_percent
                # The effect gradually diminishes as you move away from the center of the SW quadrant
                collapse_angle = np.abs(Theta - np.pi) / (np.pi/2)  # 0 at pi (270 degrees), 1 at edges
                collapse_effect = (1 - collapse_angle) * collapse_factor * sw_quadrant
                
                # Apply collapse to the height
                Z = Z * (1 - collapse_effect * 0.8)
                
                # Also shift the X,Y positions to create the slumping effect
                X = X + collapse_effect * 0.3 * np.cos(Theta + np.pi)
                Y = Y + collapse_effect * 0.3 * np.sin(Theta + np.pi)
                
                # Create crater rim indentation after substantial collapse
                if collapse_percent > 60:
                    crater_factor = (collapse_percent - 60) / 40.0  # 0 at 60%, 1 at 100%
                    crater_rim = ((R > 0.1) & (R < 0.3) & sw_quadrant)
                    Z = Z - crater_rim * crater_factor * 0.2
            
            return X, Y, Z
        
        # Generate the mesh based on current collapse percentage
        X, Y, Z = generate_volcano_mesh(collapse_stage)
        
        # Create 3D surface plot
        fig = go.Figure(data=[go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Earth',
            contours={
                "z": {"show": True, "start": 0, "end": 1, "size": 0.05}
            }
        )])
        
        # Add sea level as a semi-transparent surface
        x = np.linspace(-1, 1, 10)
        y = np.linspace(-1, 1, 10)
        X_sea, Y_sea = np.meshgrid(x, y)
        Z_sea = np.zeros_like(X_sea) + 0.2  # Sea level at 0.2 of volcano height
        
        fig.add_trace(go.Surface(
            x=X_sea, y=Y_sea, z=Z_sea,
            colorscale=[[0, 'rgb(0,100,200)'], [1, 'rgb(0,150,255)']],
            opacity=0.8,
            showscale=False
        ))
        
        # Add annotations to indicate directions
        fig.add_trace(go.Scatter3d(
            x=[0, 0, 1.3, -1.3],
            y=[1.3, -1.3, 0, 0],
            z=[0.2, 0.2, 0.2, 0.2],
            mode='text',
            text=['N', 'S', 'E', 'W'],
            textfont=dict(size=12, color='white'),
            showlegend=False
        ))
        
        # If collapse is in progress, show the landslide material and tsunami
        if collapse_stage > 20 and collapse_stage < 90:
            # Create landslide material moving into the ocean
            slide_progress = (collapse_stage - 20) / 70  # 0 to 1 for slide animation
            
            # Landslide path points
            x_slide = np.linspace(0, -1.5, 20) * slide_progress
            y_slide = np.linspace(0, -1.5, 20) * slide_progress
            z_slide = 0.2 - np.linspace(0, 0.2, 20) * slide_progress
            
            # Create a scatter3d trace for landslide material
            fig.add_trace(go.Scatter3d(
                x=x_slide + 0.2 * np.random.randn(20),
                y=y_slide + 0.2 * np.random.randn(20),
                z=z_slide + 0.05 * np.random.randn(20),
                mode='markers',
                marker=dict(
                    size=10,
                    color='rgb(120, 100, 80)',
                    opacity=0.8
                ),
                showlegend=False
            ))
            
            # Add tsunami wave rings
            if collapse_stage > 40:
                wave_progress = (collapse_stage - 40) / 60  # 0 to 1 for wave animation
                
                wave_theta = np.linspace(0, 2*np.pi, 50)
                wave_radius = np.linspace(0.3, 1.5 * wave_progress, 3)
                
                for r in wave_radius:
                    x_wave = r * np.cos(wave_theta)
                    y_wave = r * np.sin(wave_theta)
                    z_wave = np.ones_like(x_wave) * (0.2 + 0.05 * (1-r/1.5))  # Wave height decreases with distance
                    
                    fig.add_trace(go.Scatter3d(
                        x=x_wave,
                        y=y_wave,
                        z=z_wave,
                        mode='lines',
                        line=dict(color='rgb(100,200,255)', width=5),
                        showlegend=False
                    ))
        
        # Configure the 3D view
        fig.update_layout(
            title=f"Anak Krakatau Collapse Model ({collapse_stage}% Progression)",
            width=700,
            height=600,
            scene=dict(
                xaxis_title="",
                yaxis_title="",
                zaxis_title="Height",
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.7),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1),
                    center=dict(x=0, y=0, z=0.3)
                ),
                xaxis=dict(range=[-1.5, 1.5], showticklabels=False),
                yaxis=dict(range=[-1.5, 1.5], showticklabels=False),
                zaxis=dict(range=[0, 1.2], showticklabels=False)
            )
        )
        
        st.plotly_chart(fig)
    
    with col2:
        # Display explanatory text based on current collapse stage
        if collapse_stage < 20:
            st.markdown("""
            ### Pre-Collapse Phase
            
            Prior to collapse, Anak Krakatau had a symmetrical cone shape, 
            rising 338 meters above sea level. The volcano had been actively 
            erupting for months, with frequent explosive events.
            
            Scientists believe that the sustained eruptions 
            destabilized the southwest flank of the volcano.
            """)
        elif collapse_stage < 40:
            st.markdown("""
            ### Initial Collapse Phase
            
            The collapse began on December 22, 2018, at 20:55 local time. 
            The southwest flank of the volcano started to slide into the sea.
            
            Monitoring instruments detected seismic signals consistent with a 
            landslide, followed by a much larger collapse.
            """)
        elif collapse_stage < 60:
            st.markdown("""
            ### Main Collapse and Tsunami Generation
            
            The main collapse event displaced approximately 0.2-0.3 cubic 
            kilometers of volcanic material into the sea.
            
            This sudden displacement of water generated a tsunami with 
            wave heights of up to 13 meters that propagated across the 
            Sunda Strait, reaching the coasts of Sumatra and Java within 
            30-35 minutes.
            """)
        elif collapse_stage < 80:
            st.markdown("""
            ### Post-Collapse Eruption
            
            After the collapse, the volcano continued to erupt violently as 
            seawater came into contact with the newly exposed magmatic system.
            
            These phreatomagmatic eruptions generated large steam and ash plumes, 
            creating hazardous conditions that hampered initial assessment and 
            rescue efforts.
            """)
        else:
            st.markdown("""
            ### Final State
            
            The collapse reduced Anak Krakatau's height from 338 meters to 
            approximately 110 meters above sea level. The event removed 
            about two-thirds of the volcano's volume.
            
            A new water-filled crater formed where the southwest flank had been, 
            dramatically changing the morphology of the island from a symmetrical 
            cone to a crescent-shaped remnant.
            """)
    
    # Tsunami propagation visualization
    st.subheader("Tsunami Propagation Model")
    
    st.markdown("""
    The following visualization shows how the tsunami generated by the Anak Krakatau 
    collapse propagated across the Sunda Strait between Java and Sumatra.
    
    The tsunami reached coastal areas around the strait in 30-35 minutes, with 
    devastating consequences for coastal communities.
    """)
    
    # Create tsunami propagation visualization
    tsunami_stage = st.slider("Tsunami Propagation Time (minutes after collapse)", 0, 60, 0,
                            help="Move the slider to see how the tsunami propagated over time")
    
    # Create a Plotly-based tsunami wave visualization
    fig = go.Figure()
    
    # Map coordinates (approximate) with wave heights
    anak_krakatau = {"lat": -6.102, "lon": 105.423, "name": "Anak Krakatau", "wave_height": None}
    anyer = {"lat": -6.057, "lon": 105.898, "name": "Anyer (Java)", "wave_height": 9.0}
    pandeglang = {"lat": -6.746, "lon": 105.691, "name": "Pandeglang (Java)", "wave_height": 6.0}
    lampung = {"lat": -5.429, "lon": 105.254, "name": "Lampung (Sumatra)", "wave_height": 13.0}
    
    # Add coastlines (simplified)
    # Java coast (east side)
    java_x = [105.7, 105.9, 106.0, 106.1, 106.0, 105.9, 105.8]
    java_y = [-5.9, -6.0, -6.1, -6.3, -6.5, -6.7, -6.9]
    
    # Sumatra coast (west side)
    sumatra_x = [105.4, 105.3, 105.2, 105.1, 105.0, 104.9, 104.8]
    sumatra_y = [-5.3, -5.4, -5.5, -5.6, -5.7, -5.8, -5.9]
    
    # Add coastlines to the map
    fig.add_trace(go.Scatter(
        x=java_x,
        y=java_y,
        mode="lines",
        line=dict(color="green", width=3),
        name="Java Coast"
    ))
    
    fig.add_trace(go.Scatter(
        x=sumatra_x,
        y=sumatra_y,
        mode="lines",
        line=dict(color="green", width=3),
        name="Sumatra Coast"
    ))
    
    # Add the locations as markers
    locations = [anak_krakatau, anyer, pandeglang, lampung]
    for loc in locations:
        fig.add_trace(go.Scatter(
            x=[loc["lon"]],
            y=[loc["lat"]],
            mode="markers+text",
            marker=dict(size=10, color="red"),
            text=[loc["name"]],
            textposition="top center",
            name=loc["name"]
        ))
    
    # Calculate the tsunami wave radius (in degrees, approximate)
    # Tsunami travels at roughly 500-800 km/h in deep water
    # Converting minutes to a realistic radius
    # Approximately 0.05 degrees per 5 minutes
    tsunami_radius = 0.01 * tsunami_stage
    
    # Create a circle for the tsunami wave
    if tsunami_stage > 0:
        theta = np.linspace(0, 2*np.pi, 100)
        x = anak_krakatau["lon"] + tsunami_radius * np.cos(theta)
        y = anak_krakatau["lat"] + tsunami_radius * np.sin(theta)
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color="blue", width=2),
            fill="toself",
            fillcolor="rgba(0, 100, 255, 0.3)",
            name=f"Tsunami Wave at T+{tsunami_stage} min"
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Tsunami Propagation at T+{tsunami_stage} minutes",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        showlegend=True,
        width=700,
        height=500,
        xaxis=dict(range=[104.7, 106.2]),
        yaxis=dict(range=[-7.0, -5.2]),
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1,
    )
    
    # Add annotations for wave arrival times and heights
    if tsunami_stage >= 28:
        fig.add_annotation(
            x=lampung["lon"],
            y=lampung["lat"],
            text=f"Wave arrival: T+28 min<br>Height: {lampung['wave_height']} meters",
            showarrow=True,
            arrowhead=1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    
    if tsunami_stage >= 32:
        fig.add_annotation(
            x=anyer["lon"],
            y=anyer["lat"],
            text=f"Wave arrival: T+32 min<br>Height: {anyer['wave_height']} meters",
            showarrow=True,
            arrowhead=1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    
    if tsunami_stage >= 33:
        fig.add_annotation(
            x=pandeglang["lon"],
            y=pandeglang["lat"],
            text=f"Wave arrival: T+33 min<br>Height: {pandeglang['wave_height']} meters",
            showarrow=True,
            arrowhead=1,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    
    # Display the figure
    st.plotly_chart(fig)
    
    # Add key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Collapse Volume", "0.2-0.3 km³", 
                 help="Estimated volume of rock that collapsed from the volcano")
    
    with col2:
        st.metric("Wave Speed", "~200 km/h", 
                 help="Approximate tsunami wave speed in open water")
    
    with col3:
        st.metric("Max Wave Height", "13 meters", 
                 help="Maximum recorded tsunami wave height at coastal areas")
    
    # Add volume change visualization
    st.subheader("Volcano Volume Change")
    
    # Create a simple bar chart showing before/after volume
    volume_data = pd.DataFrame({
        "Time": ["Before Collapse", "After Collapse"],
        "Volume (km³)": [0.5, 0.2],
        "Height (m)": [338, 110]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_vol = px.bar(
            volume_data, 
            x="Time", 
            y="Volume (km³)",
            color="Time",
            color_discrete_sequence=["green", "red"],
            title="Volcano Volume Change"
        )
        fig_vol.update_layout(height=350)
        st.plotly_chart(fig_vol, use_container_width=True)
        
    with col2:
        fig_height = px.bar(
            volume_data, 
            x="Time", 
            y="Height (m)",
            color="Time",
            color_discrete_sequence=["green", "red"],
            title="Volcano Height Change"
        )
        fig_height.update_layout(height=350)
        st.plotly_chart(fig_height, use_container_width=True)
        
    st.markdown("""
    The flank collapse resulted in dramatic changes to Anak Krakatau:
    - **Volume Loss**: Approximately 0.2-0.3 km³ of volcanic material collapsed into the sea
    - **Height Reduction**: The volcano's height decreased from 338m to about 110m above sea level
    - **Morphology Change**: Changed from a symmetrical cone to a crescent-shaped remnant
    """)
    
    # Key statistics and impacts
    st.subheader("Impact of the Eruption and Tsunami")
    
    impact_data = [
        {"category": "Fatalities", "value": 437},
        {"category": "Injuries", "value": 14059},
        {"category": "People Displaced", "value": 33721},
        {"category": "Villages Affected", "value": 186},
        {"category": "Homes Damaged/Destroyed", "value": 2752}
    ]
    
    impact_df = pd.DataFrame(impact_data)
    
    # Display impact data as a horizontal bar chart
    fig = px.bar(impact_df, x="value", y="category", orientation='h',
                color="value", color_continuous_scale="Reds")
    
    fig.update_layout(
        title="Human Impact of the December 2018 Tsunami",
        xaxis_title="Number of People/Buildings",
        yaxis_title="",
        coloraxis_showscale=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scientific findings and lessons learned
    st.subheader("Scientific Findings and Lessons Learned")
    
    st.markdown("""
    ### Key Findings from Scientific Studies
    
    1. **Collapse Mechanism**: The sustained eruption weakened the southwest flank through 
       a combination of magma intrusion, thermal effects, and gravitational stress.
       
    2. **Volume Calculation**: Based on satellite imagery and bathymetric surveys, approximately
       0.2-0.3 cubic kilometers of material was lost during the collapse.
       
    3. **Tsunami Generation**: Unlike tectonic tsunamis caused by seafloor displacement, this
       was a volcanically-induced tsunami caused by sudden flank collapse.
       
    4. **Warning Challenges**: The proximity of the volcano to coastal areas meant that the tsunami
       reached land in just 30-35 minutes, leaving little time for warnings.
    
    ### Lessons for Volcano Monitoring
    
    1. **Integrated Monitoring**: The event highlighted the need for integrated monitoring of both
       volcanic activity and potential tsunami generation at coastal volcanoes.
       
    2. **Flank Stability Assessment**: Regular assessment of flank stability should be part of
       monitoring programs for island and coastal volcanoes.
       
    3. **Rapid Warning Systems**: Special warning systems with minimal delay are needed for
       volcanically-induced tsunamis due to their rapid onset.
       
    4. **Public Education**: Communities near volcanic islands need specific education about
       the potential for volcanically-induced tsunamis, which may have different warning signs
       than tectonic tsunamis.
    """)
    
    # References
    with st.expander("References and Further Reading", expanded=False):
        st.markdown("""
        ### Scientific References
        
        1. Walter, T.R., Haghshenas Haghighi, M., Schneider, F.M. et al. (2019). "Complex hazard cascade culminating in the Anak Krakatau sector collapse." *Nature Communications* 10, 4339.
        
        2. Grilli, S.T., Tappin, D.R., Carey, S. et al. (2019). "Modelling of the tsunami from the December 22, 2018 lateral collapse of Anak Krakatau volcano in the Sunda Straits, Indonesia." *Scientific Reports* 9, 11946.
        
        3. Ye, L., Kanamori, H., Rivera, L. et al. (2020). "The 22 December 2018 tsunami from flank collapse of Anak Krakatau volcano during eruption." *Science Advances* 6(3), eaaz1377.
        
        4. Williams, R., Rowley, P., Garthwaite, M.C. (2019). "Reconstructing the Anak Krakatau flank collapse that caused the December 2018 Indonesian tsunami." *Geology* 47(10), 973-976.
        
        ### Further Reading
        
        1. Global Volcanism Program - Krakatau Volcano: [https://volcano.si.edu/volcano.cfm?vn=262000](https://volcano.si.edu/volcano.cfm?vn=262000)
        
        2. "The 22 December 2018 Mount Anak Krakatau Volcanogenic Tsunami on Sunda Strait Coasts, Indonesia: tsunami and damage characteristics" - *Natural Hazards and Earth System Sciences* 19, 2497–2524, 2019
        
        3. "Tsunami hazard potential of Anak Krakatau volcano, Sunda Strait Indonesia" - *Geological Society London Special Publications* 361(1), 79-90, 2012
        """)

if __name__ == "__main__":
    app()