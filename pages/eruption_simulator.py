"""
Volcano Eruption Risk Simulator page for the Volcano Monitoring Dashboard.

This page provides an interactive simulation of volcanic eruption risk and progression,
allowing users to visualize potential eruption scenarios for various volcano types.
The simulation includes gas emission patterns and radioactive disequilibria in volcanic plumes,
based on scientific models of degassing processes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.api import get_volcano_data
from utils.risk_assessment import generate_risk_levels
from utils.analytics import inject_ga_tracking, track_event
from utils.gas_monitoring import (
    simulate_gas_emissions, 
    plot_gas_emissions, 
    calculate_gas_ratios, 
    plot_gas_ratios,
    simulate_radioactive_disequilibria
)

def app():
    # Inject Google Analytics tracking
    inject_ga_tracking()
    
    st.title("Volcano Eruption Risk Simulator")
    
    # Track page view
    track_event('page_view', 'eruption_simulator')
    
    st.markdown("""
    This interactive tool simulates potential volcanic eruption scenarios based on 
    historical data and current volcano characteristics. Watch how a volcanic crisis 
    might unfold and how monitoring parameters change over time.
    
    **Disclaimer:** This simulation is for educational purposes and uses simplified models. 
    Real volcanic eruptions are complex phenomena with many variables that cannot be 
    precisely predicted.
    """)
    
    # Load volcano data
    volcano_data = get_volcano_data()
    # Add risk assessment data
    volcano_data = generate_risk_levels(volcano_data)
    
    # Select volcano
    st.subheader("Select a Volcano to Simulate")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        region_filter = st.selectbox(
            "Filter by Region", 
            options=["All"] + sorted(volcano_data["region"].dropna().unique().tolist()),
            index=0
        )
    
    filtered_df = volcano_data if region_filter == "All" else volcano_data[volcano_data["region"] == region_filter]
    
    with col2:
        # Check if we have a pre-selected volcano from the risk map
        if 'simulator_volcano' in st.session_state:
            default_volcano = st.session_state['simulator_volcano']
            # Remove it from session state to avoid persistence after page reload
            volcano_name = st.session_state.pop('simulator_volcano')
            
            # Find the index of the selected volcano
            try:
                default_index = sorted(filtered_df["name"].tolist()).index(volcano_name)
            except ValueError:
                # If volcano not found in filtered region, switch to All regions
                region_filter = "All"
                filtered_df = volcano_data
                try:
                    default_index = sorted(filtered_df["name"].tolist()).index(volcano_name)
                except ValueError:
                    default_index = 0
        else:
            default_index = 0
        
        selected_volcano_name = st.selectbox(
            "Select Volcano",
            options=sorted(filtered_df["name"].tolist()),
            index=default_index
        )
    
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0]
    
    # Display basic volcano information
    st.subheader(f"Volcano Information: {selected_volcano['name']}")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"**Type:** {selected_volcano['type']}")
        st.markdown(f"**Country:** {selected_volcano['country']}")
    with col2:
        st.markdown(f"**Elevation:** {selected_volcano['elevation']} m")
        st.markdown(f"**Risk Level:** {selected_volcano.get('risk_level', 'Unknown')}")
    with col3:
        st.markdown(f"**Last Eruption:** {selected_volcano.get('last_eruption', 'Unknown')}")
        st.markdown(f"**VEI Range:** {selected_volcano.get('vei_range', '1-3')}")
    
    # Simulation parameters
    st.subheader("Simulation Parameters")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Check if we have a pre-set probability from the risk map
        if 'simulator_probability' in st.session_state:
            default_probability = st.session_state.pop('simulator_probability')
        else:
            default_probability = int(float(selected_volcano.get('risk_factor', 0.3)) * 100)
            
        eruption_probability = st.slider(
            "Eruption Probability (%)", 
            min_value=0, 
            max_value=100, 
            value=default_probability,
            help="Likelihood of an eruption occurring during the simulation period"
        )
        
        simulation_days = st.slider(
            "Simulation Period (Days)", 
            min_value=1, 
            max_value=30, 
            value=14,
            help="Number of days to simulate"
        )
    
    with col2:
        max_vei = st.slider(
            "Maximum Volcanic Explosivity Index (VEI)", 
            min_value=1, 
            max_value=7, 
            value=min(5, int(selected_volcano.get('vei_range', '3').split('-')[-1])),
            help="Maximum potential eruption intensity (1=small, 7=super-colossal)"
        )
        
        scenario = st.selectbox(
            "Eruption Scenario",
            options=["Gradual Buildup", "Sudden Explosion", "Multiple Events", "False Alarm"],
            index=0,
            help="Type of eruption scenario to simulate"
        )
    
    # Navigation links
    nav_col1, nav_col2 = st.columns([1, 1])
    with nav_col1:
        st.markdown("[← Return to Risk Map](risk_map)", unsafe_allow_html=False)
    
    # Run simulation button
    if st.button("Run Simulation", type="primary"):
        # Track simulation run event
        track_event('simulation_run', 'eruption_simulator', 
                    f"volcano:{selected_volcano_name}", 
                    eruption_probability)
                    
        with st.spinner("Running eruption simulation..."):
            # Run the simulation
            simulation_results = run_eruption_simulation(
                selected_volcano,
                eruption_probability,
                simulation_days,
                max_vei,
                scenario
            )
            
            # Display the animated simulation
            display_simulation_results(simulation_results, scenario)
            
            # Display simulation summary
            st.subheader("Simulation Summary")
            
            # Check if eruption occurred
            if simulation_results["eruption_occurred"]:
                eruption_day = next((i for i, v in enumerate(simulation_results["vei"]) if v > 0), None)
                st.warning(f"⚠️ Simulated eruption occurred on Day {eruption_day + 1} with VEI {max(simulation_results['vei'])}")
                
                # Impact assessment
                impact = assess_eruption_impact(simulation_results, selected_volcano)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("Potential Impacts")
                    for category, details in impact["categories"].items():
                        st.markdown(f"**{category}:** {details}")
                
                with col2:
                    st.subheader("Recommended Actions")
                    for action in impact["recommendations"]:
                        st.markdown(f"- {action}")
            else:
                st.success("✅ No significant eruption occurred during the simulation period")
                st.markdown("""
                Even without an eruption, continuous monitoring is essential as 
                volcanic systems can change rapidly. Regular data collection and 
                analysis help scientists track changes in volcanic behavior.
                """)

def run_eruption_simulation(volcano, eruption_probability, simulation_days, max_vei, scenario):
    """
    Run the eruption simulation based on input parameters
    
    Args:
        volcano (pd.Series): Selected volcano data
        eruption_probability (int): Probability of eruption (0-100)
        simulation_days (int): Number of days to simulate
        max_vei (int): Maximum VEI to simulate
        scenario (str): Eruption scenario type
        
    Returns:
        dict: Simulation results
    """
    # Initialize result arrays
    timestamps = [datetime.now() + timedelta(days=i) for i in range(simulation_days)]
    seismic_activity = np.zeros(simulation_days)
    gas_emissions = np.zeros(simulation_days)
    ground_deformation = np.zeros(simulation_days)
    vei = np.zeros(simulation_days)
    alert_levels = ["Normal"] * simulation_days
    
    # Extract volcano-specific characteristics
    volcano_type = volcano['type'].lower() if 'type' in volcano else 'stratovolcano'
    volcano_country = volcano['country'] if 'country' in volcano else ''
    volcano_name = volcano['name'] if 'name' in volcano else 'Unknown Volcano'
    
    # Set modifiers based on volcano type
    seismic_modifier = 1.0
    gas_modifier = 1.0
    deformation_modifier = 1.0
    vei_modifier = 1.0
    
    # Apply volcano type modifiers
    if 'shield' in volcano_type:
        # Shield volcanoes like many Hawaiian volcanoes - more fluid lava, less explosive
        seismic_modifier = 0.8
        gas_modifier = 1.2
        deformation_modifier = 1.3
        vei_modifier = 0.7
    elif 'caldera' in volcano_type:
        # Calderas can have significant explosions
        seismic_modifier = 1.2
        gas_modifier = 1.3
        deformation_modifier = 0.9
        vei_modifier = 1.4
    elif 'stratovolcano' in volcano_type:
        # Stratovolcanoes tend to be more explosive
        seismic_modifier = 1.1
        gas_modifier = 1.0
        deformation_modifier = 1.0
        vei_modifier = 1.2
    elif 'subglacial' in volcano_type or 'jökull' in volcano_name.lower():
        # Subglacial volcanoes (common in Iceland)
        seismic_modifier = 1.1
        gas_modifier = 0.8  # Gas partially trapped by ice
        deformation_modifier = 1.2
        vei_modifier = 1.1  # Can be explosive due to ice-magma interaction
    
    # Apply country-specific adjustments
    if 'iceland' in volcano_country.lower():
        # Icelandic volcanoes often have extensive fissure systems
        if 'fissure' in volcano_type.lower() or 'system' in volcano_type.lower() or 'reykjanes' in volcano_name.lower():
            # Increased seismic swarms and ground deformation
            seismic_modifier *= 1.2
            deformation_modifier *= 1.3
            
        # Special case for famous Icelandic volcanoes
        if any(name in volcano_name.lower() for name in ['katla', 'hekla', 'eyjafjallajökull', 'eyjafjallajokull', 'grimsvötn', 'grimsvotn', 'bardarbunga']):
            # These have had notable eruptions
            eruption_probability = max(eruption_probability, eruption_probability * 1.2)
            vei_modifier *= 1.2
    
    # Determine if eruption occurs based on probability
    eruption_occurs = np.random.random() < (eruption_probability / 100)
    
    # Set eruption day if eruption occurs
    if eruption_occurs:
        if scenario == "Sudden Explosion":
            # Some volcanoes like Hekla are known for sudden eruptions
            if 'hekla' in volcano_name.lower():
                eruption_day = np.random.randint(1, int(simulation_days * 0.4))  # Hekla erupts with less warning
            else:
                eruption_day = np.random.randint(1, int(simulation_days * 0.7))
        elif scenario == "Multiple Events":
            if 'iceland' in volcano_country.lower() and ('fissure' in volcano_type.lower() or 'system' in volcano_type.lower()):
                # Icelandic fissure eruptions often have multiple events closer together
                eruption_day = np.random.randint(1, int(simulation_days * 0.3))
            else:
                eruption_day = np.random.randint(1, int(simulation_days * 0.4))
            second_eruption_day = np.random.randint(eruption_day + 2, simulation_days - 1)
        else:  # Gradual Buildup or False Alarm
            eruption_day = np.random.randint(int(simulation_days * 0.6), simulation_days - 1)
    else:
        eruption_day = simulation_days + 1  # No eruption
    
    # Generate data based on scenario
    if scenario == "Gradual Buildup" and eruption_occurs:
        # Steadily increasing activity leading to eruption
        for i in range(simulation_days):
            if i < eruption_day:
                progress = i / eruption_day
                seismic_activity[i] = 0.2 + (2.8 * progress) + (np.random.random() * 0.5)
                gas_emissions[i] = 0.3 + (2.7 * progress**2) + (np.random.random() * 0.4)
                ground_deformation[i] = 0.1 + (1.9 * progress**1.5) + (np.random.random() * 0.3)
                
                # Set alert levels based on activity
                if progress < 0.3:
                    alert_levels[i] = "Normal"
                elif progress < 0.6:
                    alert_levels[i] = "Advisory"
                elif progress < 0.8:
                    alert_levels[i] = "Watch"
                else:
                    alert_levels[i] = "Warning"
            else:
                # Eruption and aftermath
                days_after = i - eruption_day
                eruption_intensity = max_vei - (days_after * 0.5 if days_after > 0 else 0)
                vei[i] = max(0, eruption_intensity)
                
                seismic_activity[i] = 4.0 - (days_after * 0.3 if days_after > 0 else 0) + (np.random.random() * 0.7)
                gas_emissions[i] = 5.0 - (days_after * 0.2 if days_after > 0 else 0) + (np.random.random() * 0.8)
                ground_deformation[i] = 3.0 - (days_after * 0.1 if days_after > 0 else 0) + (np.random.random() * 0.5)
                
                alert_levels[i] = "Warning"
    
    elif scenario == "Sudden Explosion" and eruption_occurs:
        # Low activity with sudden explosion
        for i in range(simulation_days):
            if i < eruption_day - 1:
                seismic_activity[i] = 0.5 + (np.random.random() * 0.5)
                gas_emissions[i] = 0.6 + (np.random.random() * 0.4)
                ground_deformation[i] = 0.3 + (np.random.random() * 0.3)
                alert_levels[i] = "Normal"
            elif i == eruption_day - 1:
                # Day before eruption - sudden increase
                seismic_activity[i] = 2.5 + (np.random.random() * 0.5)
                gas_emissions[i] = 2.0 + (np.random.random() * 0.4)
                ground_deformation[i] = 1.5 + (np.random.random() * 0.3)
                alert_levels[i] = "Watch"
            else:
                # Eruption and aftermath
                days_after = i - eruption_day
                eruption_intensity = max_vei - (days_after * 0.7 if days_after > 0 else 0)
                vei[i] = max(0, eruption_intensity)
                
                seismic_activity[i] = 4.5 - (days_after * 0.4 if days_after > 0 else 0) + (np.random.random() * 0.7)
                gas_emissions[i] = 5.0 - (days_after * 0.5 if days_after > 0 else 0) + (np.random.random() * 0.8)
                ground_deformation[i] = 3.5 - (days_after * 0.3 if days_after > 0 else 0) + (np.random.random() * 0.5)
                
                alert_levels[i] = "Warning"
    
    elif scenario == "Multiple Events" and eruption_occurs:
        # Multiple eruption events
        for i in range(simulation_days):
            if i < eruption_day:
                # Build up to first eruption
                progress = i / eruption_day
                seismic_activity[i] = 0.3 + (2.2 * progress) + (np.random.random() * 0.5)
                gas_emissions[i] = 0.4 + (2.1 * progress**2) + (np.random.random() * 0.4)
                ground_deformation[i] = 0.2 + (1.3 * progress**1.5) + (np.random.random() * 0.3)
                
                # Set alert levels
                if progress < 0.4:
                    alert_levels[i] = "Normal"
                elif progress < 0.7:
                    alert_levels[i] = "Advisory"
                else:
                    alert_levels[i] = "Watch"
            
            elif i == eruption_day:
                # First eruption
                vei[i] = max_vei * 0.7
                seismic_activity[i] = 4.0 + (np.random.random() * 0.7)
                gas_emissions[i] = 4.5 + (np.random.random() * 0.8)
                ground_deformation[i] = 3.0 + (np.random.random() * 0.5)
                alert_levels[i] = "Warning"
            
            elif i < second_eruption_day:
                # Period between eruptions
                days_after_first = i - eruption_day
                days_before_second = second_eruption_day - i
                
                # Activity decreases after first eruption but starts to build again
                seismic_activity[i] = 2.0 + (1.5 * (1 - days_before_second/days_after_first)) + (np.random.random() * 0.6)
                gas_emissions[i] = 2.5 + (1.2 * (1 - days_before_second/days_after_first)) + (np.random.random() * 0.5)
                ground_deformation[i] = 1.8 + (0.8 * (1 - days_before_second/days_after_first)) + (np.random.random() * 0.4)
                
                alert_levels[i] = "Watch"
            
            elif i == second_eruption_day:
                # Second eruption (typically stronger)
                vei[i] = max_vei
                seismic_activity[i] = 4.5 + (np.random.random() * 0.7)
                gas_emissions[i] = 5.0 + (np.random.random() * 0.8)
                ground_deformation[i] = 3.5 + (np.random.random() * 0.5)
                alert_levels[i] = "Warning"
            
            else:
                # Aftermath of second eruption
                days_after = i - second_eruption_day
                eruption_intensity = max_vei - (days_after * 0.6 if days_after > 0 else 0)
                vei[i] = max(0, eruption_intensity)
                
                seismic_activity[i] = 4.0 - (days_after * 0.3 if days_after > 0 else 0) + (np.random.random() * 0.7)
                gas_emissions[i] = 4.5 - (days_after * 0.25 if days_after > 0 else 0) + (np.random.random() * 0.8)
                ground_deformation[i] = 3.0 - (days_after * 0.2 if days_after > 0 else 0) + (np.random.random() * 0.5)
                
                alert_levels[i] = "Warning"
    
    else:  # False Alarm or no eruption
        # Fluctuating activity but no eruption
        for i in range(simulation_days):
            # Generate some random peaks in activity that don't lead to eruption
            day_factor = i / simulation_days
            random_peak = np.sin(i * 0.8) * 1.2 + np.sin(i * 0.3) * 0.8
            
            seismic_activity[i] = 0.5 + random_peak * 0.8 + (np.random.random() * 0.4)
            gas_emissions[i] = 0.6 + random_peak * 0.7 + (np.random.random() * 0.3)
            ground_deformation[i] = 0.3 + random_peak * 0.5 + (np.random.random() * 0.2)
            
            # Determine alert level based on activity
            activity_level = (seismic_activity[i] + gas_emissions[i] + ground_deformation[i]) / 3
            
            if activity_level < 1.0:
                alert_levels[i] = "Normal"
            elif activity_level < 1.8:
                alert_levels[i] = "Advisory"
            elif activity_level < 2.5:
                alert_levels[i] = "Watch"
            else:
                alert_levels[i] = "Warning"
    
    # Normalize values to 0-5 scale for visualization
    seismic_activity = np.clip(seismic_activity, 0, 5)
    gas_emissions = np.clip(gas_emissions, 0, 5)
    ground_deformation = np.clip(ground_deformation, 0, 5)
    
    # Return simulation results
    return {
        "timestamps": timestamps,
        "seismic_activity": seismic_activity,
        "gas_emissions": gas_emissions,
        "ground_deformation": ground_deformation,
        "vei": vei,
        "alert_levels": alert_levels,
        "eruption_occurred": eruption_occurs,
        "volcano_type": volcano_type,
        "volcano_name": volcano_name,
        "volcano_country": volcano_country
    }

def display_simulation_results(results, scenario):
    """
    Display the simulation results as animated charts
    
    Args:
        results (dict): Simulation results
        scenario (str): Eruption scenario type
    """
    st.subheader("Eruption Simulation Results")
    
    # Create tabs for different visualizations
    monitoring_tab, alert_tab, gas_emissions_tab, gas_ratios_tab, isotopes_tab = st.tabs([
        "Monitoring Parameters", 
        "Alert Levels", 
        "Gas Emissions",
        "Gas Ratios",
        "Radioactive Isotopes"
    ])
    
    # Convert timestamps to strings for plotting
    dates = [ts.strftime("%Y-%m-%d") for ts in results["timestamps"]]
    days = [f"Day {i+1}" for i in range(len(dates))]
    
    # Find eruption days
    eruption_days = [i for i, v in enumerate(results["vei"]) if v > 0] if "vei" in results else []
    
    # Tab 1: Monitoring Parameters
    with monitoring_tab:
        # Create the figure for monitoring parameters
        fig = go.Figure()
        
        # Add traces for each monitoring parameter
        fig.add_trace(go.Scatter(
            x=days, 
            y=results["seismic_activity"],
            mode='lines+markers',
            name='Seismic Activity',
            line=dict(color='red', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=days, 
            y=results["gas_emissions"],
            mode='lines+markers',
            name='Gas Emissions',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=days, 
            y=results["ground_deformation"],
            mode='lines+markers',
            name='Ground Deformation',
            line=dict(color='green', width=2)
        ))
        
        # Add VEI bars if there was an eruption
        if max(results["vei"]) > 0:
            fig.add_trace(go.Bar(
                x=days,
                y=results["vei"],
                name='Eruption VEI',
                marker_color='rgba(128, 0, 128, 0.7)'  # Purple with transparency
            ))
        
        # Update layout
        fig.update_layout(
            title='Volcanic Monitoring Parameters Over Time',
            xaxis_title='Simulation Timeline',
            yaxis_title='Intensity (0-5 scale)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Display the figure with animation
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Alert Levels
    with alert_tab:
        # Display alert level changes
        alert_colors = {
            "Normal": "#00cc00",  # Green
            "Advisory": "#ffcc00",  # Yellow
            "Watch": "#ff9900",  # Orange
            "Warning": "#ff0000"   # Red
        }
        
        # Create figure for alert levels
        fig2 = go.Figure()
        
        # Convert alert levels to numeric for visualization
        alert_numeric = {
            "Normal": 1,
            "Advisory": 2,
            "Watch": 3,
            "Warning": 4
        }
        
        alert_values = [alert_numeric[level] for level in results["alert_levels"]]
        
        # Add alert level trace
        fig2.add_trace(go.Scatter(
            x=days,
            y=alert_values,
            mode='lines+markers',
            line=dict(color='black', width=2),
            marker=dict(
                size=10,
                color=[alert_colors[level] for level in results["alert_levels"]],
                line=dict(width=2, color='black')
            ),
            name='Alert Level'
        ))
        
        # Add colored horizontal regions for each alert level
        fig2.add_shape(
            type="rect",
            x0=0, x1=len(days)-1,
            y0=0.5, y1=1.5,
            fillcolor=alert_colors["Normal"],
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        
        fig2.add_shape(
            type="rect",
            x0=0, x1=len(days)-1,
            y0=1.5, y1=2.5,
            fillcolor=alert_colors["Advisory"],
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        
        fig2.add_shape(
            type="rect",
            x0=0, x1=len(days)-1,
            y0=2.5, y1=3.5,
            fillcolor=alert_colors["Watch"],
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        
        fig2.add_shape(
            type="rect",
            x0=0, x1=len(days)-1,
            y0=3.5, y1=4.5,
            fillcolor=alert_colors["Warning"],
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        
        # Add text annotations for alert levels
        fig2.add_annotation(
            x=len(days)-1, y=1,
            text="Normal",
            showarrow=False,
            xanchor="right",
            font=dict(color="black", size=10)
        )
        
        fig2.add_annotation(
            x=len(days)-1, y=2,
            text="Advisory",
            showarrow=False,
            xanchor="right",
            font=dict(color="black", size=10)
        )
        
        fig2.add_annotation(
            x=len(days)-1, y=3,
            text="Watch",
            showarrow=False,
            xanchor="right",
            font=dict(color="black", size=10)
        )
        
        fig2.add_annotation(
            x=len(days)-1, y=4,
            text="Warning",
            showarrow=False,
            xanchor="right",
            font=dict(color="black", size=10)
        )
        
        # Update layout
        fig2.update_layout(
            title='Volcanic Alert Level Changes',
            xaxis_title='Simulation Timeline',
            yaxis_title='Alert Level',
            showlegend=False,
            yaxis=dict(
                tickvals=[1, 2, 3, 4],
                ticktext=["Normal", "Advisory", "Watch", "Warning"],
                range=[0.5, 4.5]
            )
        )
        
        # Display the figure
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tab 3: Gas Emissions
    with gas_emissions_tab:
        st.markdown("""
        ### Volcanic Gas Emissions
        
        Gas emissions are one of the most important indicators of volcanic activity. Changes in gas output 
        and composition often precede eruptions and can provide crucial insights into magma movement.
        """)
        
        # Get volcano type from the simulation results or use default
        volcano_type = results.get("volcano_type", "stratovolcano")
        
        # Simulate detailed gas emission data based on the scenario and volcano type
        gas_data = simulate_gas_emissions(
            simulation_days=len(days),
            eruption_probability=100 if results["eruption_occurred"] else 0,
            eruption_days=eruption_days,
            scenario=scenario,
            volcano_type=volcano_type
        )
        
        # Create and display the gas emissions chart
        gas_fig = plot_gas_emissions(gas_data, eruption_days)
        st.plotly_chart(gas_fig, use_container_width=True)
        
        # Display supplementary information about gas emissions
        st.markdown("""
        **Key Gas Species Monitored at Volcanoes:**
        
        - **SO₂ (Sulfur Dioxide)**: Major volcanic gas, correlates strongly with eruption potential
        - **CO₂ (Carbon Dioxide)**: Deep magmatic gas, often increases before eruptions
        - **H₂S (Hydrogen Sulfide)**: Present in many volcanic systems, especially hydrothermal
        - **HCl (Hydrogen Chloride)**: Increases during shallow magma intrusion phases
        - **HF (Hydrogen Fluoride)**: Highly toxic gas released during eruptions
        - **Radon**: Radioactive gas that can indicate new pathways opening in the volcanic edifice
        """)
    
    # Tab 4: Gas Ratios
    with gas_ratios_tab:
        st.markdown("""
        ### Volcanic Gas Ratios
        
        The ratios between different gas species provide crucial information about magma depth, 
        composition, and movement. Changing ratios often provide early warning of impending eruptions.
        """)
        
        # Calculate gas ratios from the simulated data
        gas_ratios = calculate_gas_ratios(gas_data)
        
        # Create and display the gas ratios chart
        ratios_fig = plot_gas_ratios(gas_data, gas_ratios, eruption_days)
        st.plotly_chart(ratios_fig, use_container_width=True)
        
        # Display key interpretations of gas ratios
        st.markdown("""
        **Interpretation of Gas Ratios:**
        
        - **CO₂/SO₂ Ratio**: 
            - Rising ratio may indicate deep magma intrusion
            - Ratio typically increases days to weeks before eruptions
        
        - **SO₂/H₂S Ratio**: 
            - Higher values indicate oxidized, shallow magma
            - Sharp increases often precede explosive activity
        
        - **HCl/SO₂ Ratio**: 
            - Increases when magma is shallow and degassing efficiently
            - Used to track shallow magma movement
        
        - **HF/HCl Ratio**: 
            - Relatively constant for a given magma type
            - Changes may indicate new magma composition
        """)
    
    # Tab 5: Radioactive Isotopes
    with isotopes_tab:
        st.markdown("""
        ### Radioactive Isotopes in Volcanic Gases
        
        Radioactive disequilibria in volcanic gases can provide insights into magma dynamics and degassing processes.
        Short-lived isotopes like ²¹⁰Pb, ²¹⁰Bi, and ²¹⁰Po (from the ²³⁸U decay chain) behave differently during 
        degassing due to their different volatilities.
        """)
        
        # Simulate parameters for radioactive equilibria
        col1, col2 = st.columns(2)
        
        with col1:
            # Estimate magma residence time based on scenario and eruption
            if scenario == "Gradual Buildup":
                default_residence = 150
            elif scenario == "Sudden Explosion":
                default_residence = 30
            elif scenario == "Multiple Events":
                default_residence = 100
            else:
                default_residence = 60
                
            magma_residence_time = st.slider(
                "Magma Residence Time (days)",
                min_value=0,
                max_value=365,
                value=default_residence,
                help="Time magma spends in the degassing reservoir"
            )
        
        with col2:
            # Estimate gas transfer time based on scenario
            if scenario == "Sudden Explosion":
                default_transfer = 0.2
            else:
                default_transfer = 1.0
                
            gas_transfer_time = st.slider(
                "Gas Transfer Time (days)",
                min_value=0.1,
                max_value=10.0,
                value=default_transfer,
                step=0.1,
                help="Time for gas to transfer from magma to the surface"
            )
        
        # Define volatility factors for radioactive isotopes
        volatility = {
            'Rn-222': 0.95,  # Radon is highly volatile
            'Pb-210': 0.05,  # Lead is less volatile
            'Bi-210': 0.3,   # Bismuth moderate volatility
            'Po-210': 0.8    # Polonium is highly volatile
        }
        
        # Calculate radioactive disequilibria
        activity_ratios = simulate_radioactive_disequilibria(
            magma_residence_time=magma_residence_time,
            gas_transfer_time=gas_transfer_time,
            volatility_factors=volatility
        )
        
        # Display the calculated ratios
        st.subheader("Calculated Activity Ratios")
        
        # Create a bar chart for the activity ratios
        ratio_names = []
        ratio_values = []
        
        for name, value in activity_ratios.items():
            if 'corrected' not in name:  # Skip corrected values for simplicity
                ratio_names.append(name)
                ratio_values.append(value)
        
        isotope_fig = go.Figure(data=[
            go.Bar(
                x=ratio_names,
                y=ratio_values,
                marker_color=['purple', 'blue', 'green'],
                text=[f"{v:.2f}" for v in ratio_values],
                textposition='auto'
            )
        ])
        
        isotope_fig.update_layout(
            title='Predicted Radioactive Disequilibria in Volcanic Gases',
            xaxis_title='Isotope Ratio',
            yaxis_title='Activity Ratio',
            yaxis=dict(type='log', range=[np.log10(0.1), np.log10(100)])
        )
        
        st.plotly_chart(isotope_fig, use_container_width=True)
        
        # Display interpretation
        st.markdown("""
        **Interpretation:**
        
        - **Po-210/Pb-210 Ratio >1**: Indicates preferential degassing of more volatile Po
        - **High Ratios**: Longer magma residence time in the degassing reservoir
        - **Low Transfer Time**: Higher ratios due to less decay during transit
        
        *Based on scientific studies from Mt. Etna, these ratios can vary significantly 
        during different volcanic states, from quiescence to eruption.*
        """)
        
        # Reference to scientific paper
        st.markdown("""
        ---
        **Reference**: Terray, L., et al. (2018). A New Degassing Model to Infer Magma Dynamics from
        Radioactive Disequilibria in Volcanic Plumes. *Geosciences*, 8(1), 27.
        """, unsafe_allow_html=True)
    
    # Display an animated eruption visualization if eruption occurred
    if results["eruption_occurred"] and max(results["vei"]) > 0:
        st.subheader("Eruption Visualization")
        
        # Find the eruption day(s)
        eruption_days = [i for i, v in enumerate(results["vei"]) if v > 0]
        
        if eruption_days:
            # Create an animated visualization of the eruption
            # For this example, we'll use a simple animation that shows the eruption column height
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                first_eruption_day = eruption_days[0]
                max_vei_value = max(results["vei"])
                max_vei_day = results["vei"].argmax()
                
                st.info(f"First eruption detected on Day {first_eruption_day + 1}")
                st.info(f"Maximum VEI of {max_vei_value:.1f} reached on Day {max_vei_day + 1}")
                
                if scenario == "Multiple Events" and len(eruption_days) > 1:
                    st.info(f"Multiple eruption events detected: Days {', '.join([str(day + 1) for day in eruption_days])}")
            
            with col2:
                # Display visual representation of maximum VEI
                st.metric("Maximum VEI", f"{max_vei_value:.1f}")
                st.progress(max_vei_value / 7)  # Scale to VEI range (0-7)
                
                # Map VEI to eruption column height (km)
                vei_to_height = {
                    1: "0.1-1 km",
                    2: "1-5 km",
                    3: "3-15 km",
                    4: "10-25 km",
                    5: "20-35 km",
                    6: ">30 km",
                    7: ">40 km"
                }
                
                vei_int = int(max_vei_value)
                if vei_int < 1:
                    vei_int = 1
                if vei_int > 7:
                    vei_int = 7
                    
                st.markdown(f"**Estimated Eruption Column Height:** {vei_to_height[vei_int]}")

def assess_eruption_impact(results, volcano):
    """
    Assess the potential impact of the simulated eruption
    
    Args:
        results (dict): Simulation results
        volcano (pd.Series): Selected volcano data
        
    Returns:
        dict: Impact assessment and recommendations
    """
    max_vei = max(results["vei"])
    
    # Initialize impact categories
    impact = {
        "categories": {
            "Ashfall": "",
            "Pyroclastic Flows": "",
            "Lahars/Mudflows": "",
            "Air Travel": "",
            "Local Communities": ""
        },
        "recommendations": []
    }
    
    # Assess impacts based on VEI
    if max_vei < 2:
        impact["categories"]["Ashfall"] = "Minor, localized within a few km of the vent"
        impact["categories"]["Pyroclastic Flows"] = "Unlikely or very limited"
        impact["categories"]["Lahars/Mudflows"] = "Possible in immediate vicinity if water sources present"
        impact["categories"]["Air Travel"] = "Minimal disruption, localized flight path adjustments"
        impact["categories"]["Local Communities"] = "Limited evacuation may be needed within 5 km"
        
        impact["recommendations"] = [
            "Monitor the situation closely",
            "Prepare for possible escalation",
            "Issue advisories for communities within 5-10 km",
            "Restrict access to the immediate vicinity of the volcano",
            "Inform local airlines about potential ash hazards"
        ]
        
    elif max_vei < 4:
        impact["categories"]["Ashfall"] = "Moderate, potentially affecting areas up to 50 km downwind"
        impact["categories"]["Pyroclastic Flows"] = "Possible within 5-15 km of the vent"
        impact["categories"]["Lahars/Mudflows"] = "Likely in drainages, could extend 10-30 km"
        impact["categories"]["Air Travel"] = "Regional disruption, flight cancellations likely"
        impact["categories"]["Local Communities"] = "Evacuation recommended within 10-20 km"
        
        impact["recommendations"] = [
            "Evacuate high-risk areas within 10-20 km",
            "Issue air travel warnings for a 100 km radius",
            "Prepare emergency shelters for evacuees",
            "Mobilize emergency response teams",
            "Implement respiratory protection measures for affected communities",
            "Monitor river systems for lahar hazards"
        ]
        
    else:  # VEI 4+
        impact["categories"]["Ashfall"] = "Heavy, potentially affecting areas >100 km downwind"
        impact["categories"]["Pyroclastic Flows"] = "Highly likely within 20-30+ km of the vent"
        impact["categories"]["Lahars/Mudflows"] = "Major lahars likely, could extend 50+ km"
        impact["categories"]["Air Travel"] = "Major international disruption, possible continental scale"
        impact["categories"]["Local Communities"] = "Full evacuation needed within 30+ km"
        
        impact["recommendations"] = [
            "Immediate evacuation of all areas within 30+ km",
            "Close all airports within 300+ km",
            "Activate national/international disaster response",
            "Prepare for long-term displacement of populations",
            "Coordinate with neighboring countries/regions on ash management",
            "Implement public health measures for respiratory protection",
            "Establish monitoring for potential secondary hazards",
            "Prepare for agricultural and livestock impacts"
        ]
    
    # Additional considerations based on volcano characteristics
    if "island" in volcano.get("type", "").lower() or volcano.get("country", "").lower() in ["indonesia", "philippines", "japan"]:
        impact["categories"]["Tsunami Risk"] = "Possible if eruption is explosive and near coastline"
        impact["recommendations"].append("Monitor coastal areas for potential tsunami generation")
    
    if volcano.get("elevation", 0) > 3000:
        impact["categories"]["Ice/Snow Interaction"] = "Possible melting of ice/snow causing additional lahars"
        impact["recommendations"].append("Monitor glaciers and snow packs for rapid melting")
    
    return impact

# Run the app when this script is run directly
if __name__ == "__main__":
    app()