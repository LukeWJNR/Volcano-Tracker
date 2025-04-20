"""
Crustal Load Simulator for the Volcano Monitoring Dashboard.

This page provides interactive simulations of how changes in surface loads
affect crustal deformation, stress, and volcanic systems. Based on the CrusDe
framework, it enables users to model effects of various loading scenarios:

1. Glacial unloading - simulating volcanic responses to ice mass loss
2. Sea level changes - modeling the impact of rising oceans on coastal volcanoes
3. Lava flow loading - studying how new deposition affects local strain fields
4. Seasonal water loading - understanding cyclical stresses in volcanic regions

These simulations help understand climate-volcano connections by quantifying
how surface load changes can influence magma chamber pressure, edifice stability,
and ultimately eruption likelihood.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import folium
import plotly.graph_objects as go
import plotly.express as px
from streamlit_folium import st_folium

from utils.api import get_known_volcano_data
from utils.crusde_utils import (
    create_xml_experiment,
    simulate_crustal_response,
    plot_displacement_map,
    create_time_slider_map,
    create_plotly_time_series,
    plot_cross_section,
    plot_3d_surface,
    calculate_volcanic_risk_impact
)

def app():
    st.title("🏔️ Crustal Load Simulator")
    
    st.markdown("""
    This simulation tool models how surface load changes influence crustal deformation
    and volcanic systems. Based on the CrusDe framework, it helps understand climate-volcano
    connections by quantifying effects of processes like glacial melting, sea level rise,
    and lava flows on volcanic stability and eruption potential.
    
    Select a simulation type and customize parameters to explore different scenarios.
    """)
    
    # Add session state for simulation results
    if 'crusde_simulation_results' not in st.session_state:
        st.session_state['crusde_simulation_results'] = None
    
    if 'selected_volcano' not in st.session_state:
        st.session_state['selected_volcano'] = None
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "🧊 Simulation Setup", 
        "📊 Results Analysis",
        "🌋 Volcanic Impact Assessment"
    ])
    
    with tab1:
        st.header("Simulation Configuration")
        
        # Select simulation type
        simulation_type = st.selectbox(
            "Select Load Change Scenario",
            [
                "Glacial Unloading", 
                "Sea Level Rise", 
                "Lava Flow Loading",
                "Reservoir/Lake Level Change"
            ],
            index=0
        )
        
        # Load volcanic regions and volcanoes
        volcanoes_df = get_known_volcano_data()
        
        # Define sample regions
        regions = {
            "Iceland": {"lat": 64.9, "lon": -19.0},
            "Hawaii": {"lat": 19.4, "lon": -155.3},
            "Alaska": {"lat": 61.4, "lon": -152.0},
            "Andes": {"lat": -23.5, "lon": -67.8},
            "Cascades": {"lat": 46.2, "lon": -121.5},
            "Indonesia": {"lat": -7.5, "lon": 110.0},
            "Japan": {"lat": 35.6, "lon": 138.2},
            "Kamchatka": {"lat": 56.0, "lon": 160.0},
            "Mediterranean": {"lat": 37.7, "lon": 14.9}
        }
        
        # Select region and load center
        col1, col2 = st.columns(2)
        
        with col1:
            selected_region = st.selectbox(
                "Select Region",
                list(regions.keys()),
                index=0
            )
            
            # Show volcanoes in the selected region
            center_lat = regions[selected_region]["lat"]
            center_lon = regions[selected_region]["lon"]
            
            # Find volcanoes within ~300km of center
            region_volcanoes = volcanoes_df[
                (np.abs(volcanoes_df['latitude'] - center_lat) < 3) & 
                (np.abs(volcanoes_df['longitude'] - center_lon) < 3)
            ]
            
            # Get volcano names list
            volcano_options = ["Custom Location"] + region_volcanoes['name'].tolist()
            
            selected_volcano = st.selectbox(
                "Volcano/Location",
                volcano_options,
                index=0
            )
            
            # Store selected volcano in session state
            if selected_volcano != "Custom Location":
                volcano_data = region_volcanoes[region_volcanoes['name'] == selected_volcano].iloc[0]
                st.session_state['selected_volcano'] = {
                    "name": selected_volcano,
                    "latitude": volcano_data['latitude'],
                    "longitude": volcano_data['longitude'],
                    "type": volcano_data.get('type', "Unknown"),
                    "country": volcano_data.get('country', "Unknown")
                }
            else:
                st.session_state['selected_volcano'] = None
        
        with col2:
            # Custom location input if needed
            if selected_volcano == "Custom Location":
                center_lat = st.number_input("Center Latitude", value=center_lat, format="%.4f")
                center_lon = st.number_input("Center Longitude", value=center_lon, format="%.4f")
            else:
                # Use volcano coordinates
                center_lat = region_volcanoes[region_volcanoes['name'] == selected_volcano]['latitude'].iloc[0]
                center_lon = region_volcanoes[region_volcanoes['name'] == selected_volcano]['longitude'].iloc[0]
                
                st.write(f"Coordinates: {center_lat:.4f}, {center_lon:.4f}")
                
                # Show volcano info
                volcano_type = region_volcanoes[region_volcanoes['name'] == selected_volcano]['type'].iloc[0]
                volcano_country = region_volcanoes[region_volcanoes['name'] == selected_volcano]['country'].iloc[0]
                
                st.write(f"Type: {volcano_type}")
                st.write(f"Country: {volcano_country}")
        
        # Create a small map to show location
        location_map = folium.Map(location=[center_lat, center_lon], zoom_start=8)
        folium.Marker(
            location=[center_lat, center_lon],
            popup=selected_volcano if selected_volcano != "Custom Location" else "Custom Location",
            icon=folium.Icon(color="red", icon="fire", prefix="fa")
        ).add_to(location_map)
        
        # Show map
        st.write("Simulation Location:")
        st_folium(location_map, width=400, height=300)
        
        # Simulation parameters based on type
        st.subheader("Load Parameters")
        
        col1, col2 = st.columns(2)
        
        if simulation_type == "Glacial Unloading":
            with col1:
                glacier_radius = st.slider("Glacier Radius (km)", 1, 50, 10)
                ice_thickness = st.slider("Initial Ice Thickness (m)", 50, 1000, 500)
                melt_duration = st.slider("Melting Period (years)", 10, 200, 100)
            
            with col2:
                remaining_ice = st.slider("Remaining Ice (%)", 0, 90, 10)
                elastic_thickness = st.slider("Elastic Thickness (km)", 10, 100, 30)
                time_steps = st.slider("Time Steps", 5, 50, 20)
                
            load_params = {
                "radius_km": glacier_radius,
                "initial_height_m": ice_thickness,
                "density_kg_m3": 900,  # Ice density
                "final_fraction": remaining_ice / 100.0
            }
            
            # Map settings
            region_width = max(glacier_radius * 10, 50)  # km
            region_height = max(glacier_radius * 10, 50)  # km
            resolution = max(0.5, glacier_radius / 10)  # km
            
        elif simulation_type == "Sea Level Rise":
            with col1:
                coastline_width = st.slider("Coastline Width (km)", 10, 200, 50)
                sea_level_rise = st.slider("Sea Level Rise (m)", 0.1, 10.0, 1.0)
                rise_duration = st.slider("Rise Period (years)", 10, 200, 80)
            
            with col2:
                elastic_thickness = st.slider("Elastic Thickness (km)", 10, 100, 30)
                water_depth = st.slider("Average Water Depth (m)", 10, 5000, 100)
                time_steps = st.slider("Time Steps", 5, 50, 20)
                
            load_params = {
                "coastline_width_km": coastline_width,
                "initial_height_m": 0,
                "final_height_m": sea_level_rise,
                "water_depth_m": water_depth,
                "density_kg_m3": 1025  # Seawater density
            }
            
            # Map settings
            region_width = max(coastline_width * 4, 100)  # km
            region_height = max(coastline_width * 4, 100)  # km
            resolution = max(1.0, coastline_width / 20)  # km
            
        elif simulation_type == "Lava Flow Loading":
            with col1:
                flow_radius = st.slider("Lava Flow Radius (km)", 0.5, 20.0, 5.0)
                flow_thickness = st.slider("Lava Flow Thickness (m)", 1, 200, 50)
                flow_duration = st.slider("Eruption Duration (days)", 1, 100, 30)
            
            with col2:
                lava_density = st.slider("Lava Density (kg/m³)", 2000, 3000, 2700)
                elastic_thickness = st.slider("Elastic Thickness (km)", 10, 100, 30)
                time_steps = st.slider("Time Steps", 5, 50, 20)
                
            load_params = {
                "radius_km": flow_radius,
                "height_m": flow_thickness,
                "density_kg_m3": lava_density,
                "eruption_time_years": flow_duration / 365.0  # Convert days to years
            }
            
            # Map settings
            region_width = max(flow_radius * 10, 30)  # km
            region_height = max(flow_radius * 10, 30)  # km
            resolution = max(0.2, flow_radius / 10)  # km
            
        elif simulation_type == "Reservoir/Lake Level Change":
            with col1:
                reservoir_radius = st.slider("Reservoir Radius (km)", 1, 50, 10)
                level_change = st.slider("Water Level Change (m)", -50, 50, 20)
                change_duration = st.slider("Change Period (months)", 1, 60, 12)
            
            with col2:
                cycle_type = st.selectbox(
                    "Cycle Type",
                    ["One-time change", "Annual cycle", "Seasonal cycle"],
                    index=0
                )
                elastic_thickness = st.slider("Elastic Thickness (km)", 10, 100, 30)
                time_steps = st.slider("Time Steps", 5, 50, 20)
                
            load_params = {
                "radius_km": reservoir_radius,
                "height_m": abs(level_change),
                "density_kg_m3": 1000,  # Water density
                "is_removal": level_change < 0
            }
            
            # Map settings
            region_width = max(reservoir_radius * 10, 40)  # km
            region_height = max(reservoir_radius * 10, 40)  # km
            resolution = max(0.5, reservoir_radius / 10)  # km
        
        # Select the earth model
        st.subheader("Earth Model Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            earth_model = st.selectbox(
                "Crustal Response Model",
                ["Elastic Halfspace", "Thick Plate", "Relaxed State", "Exponential Decay"],
                index=0
            )
            
            # Map earth model to CrusDe model
            model_map = {
                "Elastic Halfspace": "elastic",
                "Thick Plate": "thick_plate",
                "Relaxed State": "relaxed",
                "Exponential Decay": "exponential_decay"
            }
            
            earth_model_code = model_map[earth_model]
        
        with col2:
            # If exponential decay is selected, add decay time parameter
            if earth_model == "Exponential Decay":
                decay_time = st.slider("Decay Time (years)", 1, 50, 10)
                load_params["decay_time_years"] = decay_time
            
            # Duration based on simulation type
            if simulation_type == "Glacial Unloading":
                duration_years = melt_duration
            elif simulation_type == "Sea Level Rise":
                duration_years = rise_duration
            elif simulation_type == "Lava Flow Loading":
                duration_years = max(1, flow_duration / 365.0 * 5)  # 5x eruption duration
            else:  # Reservoir
                duration_years = max(1, change_duration / 12.0 * 5)  # 5x change duration
            
            # Allow user to adjust duration
            duration_years = st.slider(
                "Simulation Duration (years)", 
                min_value=max(1, int(duration_years / 2)),
                max_value=int(duration_years * 2),
                value=int(duration_years)
            )
        
        # Run simulation button
        if st.button("Run Simulation"):
            with st.spinner("Running crustal deformation simulation..."):
                try:
                    # Create experiment name
                    experiment_name = f"{simulation_type.replace(' ', '_')}_{selected_region}"
                    
                    # Create simulation parameters dictionary directly (skip the XML generation)
                    simulation_params = {
                        "name": experiment_name,
                        "load_type": simulation_type.lower().replace(" ", "_").replace("/", "_"),
                        "load_params": load_params,
                        "earth_model": earth_model_code,
                        "time_steps": time_steps,
                        "duration_years": duration_years,
                        "lat_center": center_lat,
                        "lon_center": center_lon,
                        "region_width_km": region_width,
                        "region_height_km": region_height,
                        "resolution_km": resolution
                    }
                    
                    # Run simulation directly
                    results = simulate_crustal_response(simulation_params)
                    
                    # Store results in session state
                    st.session_state['crusde_simulation_results'] = results
                    
                    st.success(f"Simulation completed: {experiment_name}")
                    st.write("Navigate to the Results Analysis tab to view detailed outputs.")
                except Exception as e:
                    st.error(f"Error running simulation: {str(e)}")
                    st.info("Note: This is a scientific simulation of crustal deformation patterns based on elastic theory and simplification of the CrusDe framework. The full CrusDe implementation requires system dependencies not available in this environment.")
                    st.info("Please try adjusting the parameters or selecting a different simulation type.")
    
    with tab2:
        st.header("Simulation Results Analysis")
        
        # Check if we have simulation results
        if st.session_state['crusde_simulation_results'] is None:
            st.info("Run a simulation in the Setup tab to see results here.")
        else:
            results = st.session_state['crusde_simulation_results']
            
            # Display simulation parameters
            st.subheader(f"Simulation: {results['name']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"Duration: {results['parameters']['duration_years']} years")
                st.write(f"Region Width: {results['parameters']['width_km']} km")
                
            with col2:
                st.write(f"Time Steps: {results['parameters']['timesteps']}")
                st.write(f"Region Height: {results['parameters']['height_km']} km")
                
            with col3:
                st.write(f"Resolution: {results['parameters']['resolution_km']} km")
                st.write(f"Center: {results['parameters']['center_lat']:.4f}, {results['parameters']['center_lon']:.4f}")
            
            # Create visualization controls
            st.subheader("Visualization Controls")
            
            col1, col2 = st.columns(2)
            
            with col1:
                visualization_type = st.selectbox(
                    "Visualization Type",
                    ["Static Map", "Time Animation", "Time Series", "Cross-Section", "3D Surface"],
                    index=0
                )
                
                plot_type = st.selectbox(
                    "Data to Display",
                    ["Vertical Displacement", "Horizontal Displacement", "Strain Magnitude"],
                    index=0
                )
                
                # Convert selection to code value
                plot_type_code = plot_type.lower().replace(" ", "_")
            
            with col2:
                # Time control for static visualizations
                if visualization_type in ["Static Map", "Cross-Section", "3D Surface"]:
                    time_index = st.slider(
                        "Time Step", 
                        0, 
                        results['parameters']['timesteps'] - 1, 
                        results['parameters']['timesteps'] - 1
                    )
                    
                    time_years = results['times'][time_index]
                    st.write(f"Time: {time_years:.2f} years")
                
                # Additional controls based on visualization type
                if visualization_type == "Cross-Section":
                    start_lat = st.number_input(
                        "Start Latitude",
                        value=float(results['parameters']['center_lat'] - results['parameters']['height_km'] / 222)
                    )
                    
                    start_lon = st.number_input(
                        "Start Longitude",
                        value=float(results['parameters']['center_lon'] - results['parameters']['width_km'] / 222)
                    )
                    
                    end_lat = st.number_input(
                        "End Latitude",
                        value=float(results['parameters']['center_lat'] + results['parameters']['height_km'] / 222)
                    )
                    
                    end_lon = st.number_input(
                        "End Longitude",
                        value=float(results['parameters']['center_lon'] + results['parameters']['width_km'] / 222)
                    )
                
                elif visualization_type == "Time Series":
                    point_lat = st.number_input(
                        "Point Latitude",
                        value=float(results['parameters']['center_lat'])
                    )
                    
                    point_lon = st.number_input(
                        "Point Longitude",
                        value=float(results['parameters']['center_lon'])
                    )
                
                elif visualization_type == "3D Surface":
                    exaggeration = st.slider(
                        "Vertical Exaggeration", 
                        100, 
                        10000, 
                        1000
                    )
            
            # Create visualization based on selection
            st.subheader("Visualization")
            
            if visualization_type == "Static Map":
                map_obj = plot_displacement_map(
                    results, 
                    time_index=time_index,
                    plot_type=plot_type_code
                )
                
                st_folium(map_obj, width=800, height=600)
                
            elif visualization_type == "Time Animation":
                map_obj = create_time_slider_map(
                    results,
                    plot_type=plot_type_code
                )
                
                st_folium(map_obj, width=800, height=600)
                
                st.info("Use the time slider at the bottom of the map to animate through time steps.")
                
            elif visualization_type == "Time Series":
                fig = create_plotly_time_series(
                    results,
                    lat=point_lat,
                    lon=point_lon,
                    plot_type=plot_type_code
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif visualization_type == "Cross-Section":
                fig = plot_cross_section(
                    results,
                    start_lat=start_lat,
                    start_lon=start_lon,
                    end_lat=end_lat,
                    end_lon=end_lon,
                    time_index=time_index,
                    plot_type=plot_type_code
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif visualization_type == "3D Surface":
                fig = plot_3d_surface(
                    results,
                    time_index=time_index,
                    plot_type=plot_type_code,
                    exaggeration=exaggeration
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("Drag to rotate the 3D view. Scroll to zoom.")
            
            # Analysis and insights section
            st.subheader("Analysis Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Maximum displacement
                if plot_type == "Vertical Displacement":
                    max_disp = np.max(np.abs(results["vertical_displacement"][time_index]))
                    max_up = np.max(results["vertical_displacement"][time_index])
                    max_down = np.min(results["vertical_displacement"][time_index])
                    
                    st.metric("Maximum Vertical Displacement", f"{max_disp:.4f} m")
                    st.metric("Maximum Uplift", f"{max_up:.4f} m")
                    st.metric("Maximum Subsidence", f"{max_down:.4f} m")
                    
                elif plot_type == "Horizontal Displacement":
                    he = results["horizontal_displacement_e"][time_index]
                    hn = results["horizontal_displacement_n"][time_index]
                    h_disp = np.sqrt(he**2 + hn**2)
                    max_h_disp = np.max(h_disp)
                    
                    st.metric("Maximum Horizontal Displacement", f"{max_h_disp:.4f} m")
                    
                elif plot_type == "Strain Magnitude":
                    exx = results["strain_xx"][time_index]
                    eyy = results["strain_yy"][time_index]
                    exy = results["strain_xy"][time_index]
                    strain = np.sqrt(0.5 * (exx**2 + eyy**2 + 2 * exy**2)) * 1e6  # Convert to microstrain
                    max_strain = np.max(strain)
                    
                    st.metric("Maximum Strain", f"{max_strain:.2f} μstrain")
            
            with col2:
                # Affected area metrics
                if plot_type == "Vertical Displacement":
                    # Calculate areas with significant displacement
                    significant_threshold = 0.01  # 1 cm
                    area_affected = np.sum(np.abs(results["vertical_displacement"][time_index]) > significant_threshold)
                    total_area = results["vertical_displacement"][time_index].size
                    
                    percent_affected = (area_affected / total_area) * 100
                    
                    st.metric("Area with >1cm Displacement", f"{percent_affected:.1f}%")
                    
                    # Calculate volume change
                    cell_area_km2 = results['parameters']['resolution_km'] ** 2
                    volume_change = np.sum(results["vertical_displacement"][time_index]) * cell_area_km2 * 1e6  # in m³
                    
                    st.metric("Net Volume Change", f"{volume_change:.2e} m³")
                
                elif plot_type == "Horizontal Displacement":
                    # Calculate areas with significant displacement
                    he = results["horizontal_displacement_e"][time_index]
                    hn = results["horizontal_displacement_n"][time_index]
                    h_disp = np.sqrt(he**2 + hn**2)
                    
                    significant_threshold = 0.01  # 1 cm
                    area_affected = np.sum(h_disp > significant_threshold)
                    total_area = h_disp.size
                    
                    percent_affected = (area_affected / total_area) * 100
                    
                    st.metric("Area with >1cm Displacement", f"{percent_affected:.1f}%")
                
                elif plot_type == "Strain Magnitude":
                    # Calculate areas with significant strain
                    exx = results["strain_xx"][time_index]
                    eyy = results["strain_yy"][time_index]
                    exy = results["strain_xy"][time_index]
                    strain = np.sqrt(0.5 * (exx**2 + eyy**2 + 2 * exy**2)) * 1e6  # Convert to microstrain
                    
                    significant_threshold = 1.0  # 1 microstrain
                    area_affected = np.sum(strain > significant_threshold)
                    total_area = strain.size
                    
                    percent_affected = (area_affected / total_area) * 100
                    
                    st.metric("Area with >1μ Strain", f"{percent_affected:.1f}%")
            
            # Time evolution analysis
            st.subheader("Time Evolution Analysis")
            
            if plot_type == "Vertical Displacement":
                # Extract center point time series
                center_lat_idx = np.argmin(np.abs(results["lats"] - results['parameters']['center_lat']))
                center_lon_idx = np.argmin(np.abs(results["lons"] - results['parameters']['center_lon']))
                
                center_timeseries = results["vertical_displacement"][:, center_lat_idx, center_lon_idx]
                
                # Create time series plot
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=results["times"],
                    y=center_timeseries,
                    mode='lines+markers',
                    name='Center Displacement',
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Vertical Displacement Over Time (Center Point)",
                    xaxis_title="Time (years)",
                    yaxis_title="Displacement (m)",
                    template="plotly_white",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif plot_type == "Horizontal Displacement":
                # Extract center point time series
                center_lat_idx = np.argmin(np.abs(results["lats"] - results['parameters']['center_lat']))
                center_lon_idx = np.argmin(np.abs(results["lons"] - results['parameters']['center_lon']))
                
                center_he_timeseries = results["horizontal_displacement_e"][:, center_lat_idx, center_lon_idx]
                center_hn_timeseries = results["horizontal_displacement_n"][:, center_lat_idx, center_lon_idx]
                center_h_magnitude = np.sqrt(center_he_timeseries**2 + center_hn_timeseries**2)
                
                # Create time series plot
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=results["times"],
                    y=center_h_magnitude,
                    mode='lines+markers',
                    name='Center Horizontal Displacement',
                    line=dict(width=3, color='green'),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Horizontal Displacement Over Time (Center Point)",
                    xaxis_title="Time (years)",
                    yaxis_title="Displacement (m)",
                    template="plotly_white",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == "Strain Magnitude":
                # Extract center point time series
                center_lat_idx = np.argmin(np.abs(results["lats"] - results['parameters']['center_lat']))
                center_lon_idx = np.argmin(np.abs(results["lons"] - results['parameters']['center_lon']))
                
                exx_timeseries = results["strain_xx"][:, center_lat_idx, center_lon_idx]
                eyy_timeseries = results["strain_yy"][:, center_lat_idx, center_lon_idx]
                exy_timeseries = results["strain_xy"][:, center_lat_idx, center_lon_idx]
                
                center_strain_magnitude = np.sqrt(0.5 * (exx_timeseries**2 + eyy_timeseries**2 + 2 * exy_timeseries**2)) * 1e6
                
                # Create time series plot
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=results["times"],
                    y=center_strain_magnitude,
                    mode='lines+markers',
                    name='Center Strain Magnitude',
                    line=dict(width=3, color='purple'),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Strain Magnitude Over Time (Center Point)",
                    xaxis_title="Time (years)",
                    yaxis_title="Strain (μstrain)",
                    template="plotly_white",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Volcanic Impact Assessment")
        
        # Check if we have simulation results and selected volcano
        if st.session_state['crusde_simulation_results'] is None:
            st.info("Run a simulation in the Setup tab to see volcanic impact assessment.")
        else:
            results = st.session_state['crusde_simulation_results']
            
            # Volcanic assessment controls
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state['selected_volcano'] is not None:
                    # Use selected volcano
                    volcano_name = st.session_state['selected_volcano']["name"]
                    volcano_lat = st.session_state['selected_volcano']["latitude"]
                    volcano_lon = st.session_state['selected_volcano']["longitude"]
                    
                    st.write(f"Selected Volcano: {volcano_name}")
                    st.write(f"Coordinates: {volcano_lat:.4f}, {volcano_lon:.4f}")
                else:
                    # Use custom location from simulation
                    volcano_lat = results['parameters']['center_lat']
                    volcano_lon = results['parameters']['center_lon']
                    
                    st.write("Using simulation center point for assessment")
                    st.write(f"Coordinates: {volcano_lat:.4f}, {volcano_lon:.4f}")
                
                # Time control
                time_index = st.slider(
                    "Assessment Time", 
                    0, 
                    results['parameters']['timesteps'] - 1, 
                    results['parameters']['timesteps'] - 1,
                    key="assessment_time_index"
                )
                
                time_years = results['times'][time_index]
                st.write(f"Time: {time_years:.2f} years")
            
            with col2:
                # Run impact assessment
                if st.button("Calculate Volcanic Impact"):
                    with st.spinner("Analyzing volcanic impact..."):
                        impact = calculate_volcanic_risk_impact(
                            results,
                            volcano_lat=volcano_lat,
                            volcano_lon=volcano_lon,
                            time_index=time_index
                        )
                        
                        # Store in session state
                        st.session_state['volcanic_impact'] = impact
                        
                        st.success("Impact assessment completed.")
            
            # Display impact assessment if available
            if 'volcanic_impact' in st.session_state:
                impact = st.session_state['volcanic_impact']
                
                st.subheader("Deformation at Volcano Location")
                
                # Create metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Vertical Displacement",
                        f"{impact['vertical_displacement']:.3f} m",
                        delta=f"{impact['vertical_displacement']:.3f}",
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Horizontal Displacement",
                        f"{impact['horizontal_displacement']:.3f} m",
                        delta=f"{impact['horizontal_displacement']:.3f}",
                        delta_color="normal"
                    )
                
                with col3:
                    st.metric(
                        "Strain Magnitude",
                        f"{impact['strain_magnitude']:.2f} μstrain",
                        delta=f"{impact['strain_magnitude']:.2f}",
                        delta_color="normal"
                    )
                
                st.subheader("Volcanic Risk Assessment")
                
                # Create metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Magma Pressure Change",
                        f"{impact['pressure_change']:.1f}",
                        delta=f"{impact['pressure_change']:.1f}",
                        delta_color="normal"
                    )
                
                with col2:
                    st.metric(
                        "Edifice Stability Impact",
                        f"{impact['stability_impact']:.1f}",
                        delta=f"{impact['stability_impact']:.1f}",
                        delta_color="normal"
                    )
                
                with col3:
                    st.metric(
                        "Magma Pathway Dilation",
                        f"{impact['pathway_dilation']:.1f}",
                        delta=f"{impact['pathway_dilation']:.1f}",
                        delta_color="normal"
                    )
                
                # Overall risk assessment
                st.subheader("Overall Volcanic Risk Impact")
                
                # Select color based on risk level
                risk_color = {
                    "Low": "green",
                    "Medium": "orange",
                    "High": "red"
                }[impact['risk_level']]
                
                # Create risk gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = impact['risk_index'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Index", 'font': {'size': 24}},
                    delta = {'reference': 5, 'increasing': {'color': "red"}},
                    gauge = {
                        'axis': {'range': [0, 15], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': risk_color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 5], 'color': 'lightgreen'},
                            {'range': [5, 10], 'color': 'lightorange'},
                            {'range': [10, 15], 'color': 'lightcoral'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': impact['risk_index']
                        }
                    }
                ))
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Risk interpretation
                st.markdown(f"""
                ### Risk Interpretation: {impact['risk_level']} Risk Level
                
                The simulation indicates that the **{simulation_type.lower()}** scenario would have a 
                **{impact['risk_level'].lower()} impact** on volcanic risk at this location.
                
                **Key findings:**
                
                1. **Magma Chamber Pressure**: {'Increased' if impact['pressure_change'] > 0 else 'Decreased'} pressure in the magma storage system, which could 
                   {'enhance' if impact['pressure_change'] > 0 else 'reduce'} the likelihood of magma mobilization.
                   
                2. **Edifice Stability**: The crustal strain indicates {'potential weakening' if impact['stability_impact'] > 5 else 'minimal impact'} of the volcano's 
                   structural integrity, {'potentially' if impact['stability_impact'] > 5 else 'unlikely to be'} affecting slope stability.
                   
                3. **Magma Pathways**: {'Enhanced' if impact['pathway_dilation'] > 5 else 'Minimal changes to'} dilation of potential magma pathways, which could 
                   {'facilitate' if impact['pathway_dilation'] > 5 else 'have little effect on'} magma ascent to the surface.
                
                Overall, this {simulation_type.lower()} scenario {'may significantly alter' if impact['risk_level'] == 'High' else 'could moderately affect' if impact['risk_level'] == 'Medium' else 'is likely to have minimal impact on'} 
                the volcanic system's behavior at this location. {'Further monitoring is strongly recommended.' if impact['risk_level'] == 'High' else 'Regular monitoring would be prudent.' if impact['risk_level'] == 'Medium' else 'Standard monitoring protocols should be sufficient.'}
                """)
                
                # Scientific context
                st.subheader("Scientific Context")
                
                if simulation_type == "Glacial Unloading":
                    st.markdown("""
                    **Glacial Unloading and Volcanism**
                    
                    Glacial retreat can trigger increased volcanic activity through several mechanisms:
                    
                    1. **Isostatic Rebound**: As ice melts, the reduced load on the Earth's crust causes uplift,
                    which can decompress the magma chamber and trigger melting or allow existing magma to rise.
                    
                    2. **Stress Field Changes**: The changing stresses in the crust can open new fractures or widen
                    existing ones, creating pathways for magma to reach the surface.
                    
                    3. **Pressure Gradient Changes**: Alterations in the subsurface pressure gradients can affect
                    the stability of volatile-rich magmas, potentially triggering eruptions.
                    
                    Historical examples include increased eruption frequency in Iceland following the end of the
                    last ice age, and current observations of increased activity in areas experiencing rapid
                    glacial retreat like Alaska and the Andes.
                    """)
                
                elif simulation_type == "Sea Level Rise":
                    st.markdown("""
                    **Sea Level Rise and Coastal Volcanoes**
                    
                    Rising sea levels can influence coastal and island volcanoes through several mechanisms:
                    
                    1. **Hydrostatic Loading**: Increased water height adds pressure on the seafloor,
                    potentially affecting submarine magma systems and flank stability.
                    
                    2. **Groundwater Table Changes**: Rising sea levels can elevate coastal water tables,
                    potentially increasing phreatic (steam-driven) explosion risks.
                    
                    3. **Flank Stability**: Water saturation and wave erosion can destabilize volcanic flanks,
                    potentially leading to sector collapses and tsunamis.
                    
                    Examples include concerns about the stability of island volcanoes such as Anak Krakatau,
                    Kilauea, and Stromboli, where sea level changes could contribute to major flank collapses.
                    """)
                
                elif simulation_type == "Lava Flow Loading":
                    st.markdown("""
                    **Lava Loading Effects**
                    
                    The addition of new lava flows can affect volcanic systems through:
                    
                    1. **Structural Loading**: New lava adds weight to volcanic edifices, potentially
                    compressing underlying magma chambers or destabilizing flanks.
                    
                    2. **Thermal Effects**: Hot lava can alter the thermal regime of the volcano,
                    affecting crystallization processes and volatile behavior in magma chambers.
                    
                    3. **Pathway Sealing/Opening**: New flows can either seal existing gas escape pathways,
                    leading to pressure buildup, or create new weak zones for future eruptions.
                    
                    Notable examples include the ongoing activity at Kilauea, where repeated lava flows
                    have influenced subsequent eruption patterns, and Etna, where flank loading has been
                    linked to changes in eruption style and location.
                    """)
                
                elif simulation_type == "Reservoir/Lake Level Change":
                    st.markdown("""
                    **Reservoir-Induced Seismicity and Volcanism**
                    
                    Changes in large water bodies near volcanoes can influence activity through:
                    
                    1. **Stress Changes**: Rapid filling or draining of reservoirs alters the local stress field,
                    potentially triggering seismic activity and influencing volcanic systems.
                    
                    2. **Pore Pressure Effects**: Water level changes affect groundwater systems, changing
                    pore pressure in volcanic edifices and potentially destabilizing them.
                    
                    3. **Seasonal Effects**: In natural systems, seasonal lake level or snowpack changes can
                    produce cyclical patterns in volcanic activity.
                    
                    Examples include observations of correlation between reservoir level changes and seismic activity
                    near volcanoes in regions like the Philippines (Taal), and potential seasonal patterns at
                    volcanoes like Popocatépetl in Mexico.
                    """)

if __name__ == "__main__":
    app()