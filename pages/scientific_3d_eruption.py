"""
Scientific 3D Eruption Animation for the Volcano Monitoring Dashboard.

This page provides a scientifically accurate, full eruption cycle visualization 
using Three.js/WebGL for advanced rendering while maintaining scientific 
accuracy across all eruption phases.
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
from utils.api import get_volcano_data
from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS
from utils.cinematic_animation import generate_cinematic_eruption

def app():
    st.title("Scientific 3D Eruption Cycle")
    
    st.markdown("""
    This page provides a scientifically accurate, interactive 3D visualization of
    the complete eruption cycle, from initial magma buildup through all eruption phases.
    
    The model follows the same physical processes and data used in our scientific simulations
    but rendered with advanced WebGL technology for immersive visualization.
    
    ### Eruption Phases Visualization:
    - **Magma Buildup**: Watch deep and shallow magma chambers fill over time
    - **Increased Seismicity**: Observe seismic activity as pressure increases
    - **Initial Eruption**: See the beginning stages of eruption as magma reaches the surface
    - **Main Eruption**: Witness the peak eruption with characteristic behavior for the selected volcano type
    - **Waning Activity**: Observe the gradual decline of eruptive activity
    """)
    
    # Load volcano data
    volcanoes_df = get_volcano_data()
    
    # Sidebar for volcano selection
    st.sidebar.title("Volcano Selection")
    
    # Region filter
    regions = ["All"] + sorted(volcanoes_df["region"].unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region:", regions)
    
    # Filter by region if not "All"
    if selected_region != "All":
        filtered_df = volcanoes_df[volcanoes_df["region"] == selected_region]
    else:
        filtered_df = volcanoes_df
    
    # Volcano name filter
    volcano_names = sorted(filtered_df["name"].unique().tolist())
    selected_volcano_name = st.sidebar.selectbox(
        "Select Volcano:", 
        volcano_names
    )
    
    # Animation controls
    st.sidebar.subheader("Animation Controls")
    
    # Animation speed
    animation_speed = st.sidebar.slider(
        "Animation Speed",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1,
        help="Control how fast the eruption animation plays"
    )
    
    # Quality settings
    quality = st.sidebar.select_slider(
        "Visualization Quality",
        options=["Low", "Medium", "High"],
        value="Medium",
        help="Higher quality shows more detail but may be slower on some devices"
    )
    
    # Camera position
    camera_position = st.sidebar.selectbox(
        "Camera View",
        ["Aerial", "Ground Level", "Cross-Section", "Side View"],
        index=0
    )
    
    # Visualization options
    st.sidebar.subheader("Visualization Options")
    show_metrics = st.sidebar.checkbox("Show Eruption Metrics", value=True)
    show_plumbing = st.sidebar.checkbox("Show Complete Plumbing System", value=True)
    show_labels = st.sidebar.checkbox("Show Feature Labels", value=True)
    
    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = determine_volcano_type(selected_volcano)
    
    # Calculate eruption parameters using the same cinematic animation model
    # This ensures we use the same scientifically accurate data and phase progression
    with st.spinner("Calculating eruption parameters..."):
        eruption_data = generate_cinematic_eruption(selected_volcano, frames=120)
        animation_data = eruption_data['animation_data']
        phases = list(dict.fromkeys(animation_data['phase']))
        
        # Extract key data points for WebGL visualization
        # We'll sample data points from each phase to match the scientific model
        phase_sample_points = {}
        for phase in phases:
            phase_indices = [i for i, p in enumerate(animation_data['phase']) if p == phase]
            if phase_indices:
                # Get mid-point for each phase
                mid_idx = phase_indices[len(phase_indices) // 2]
                phase_sample_points[phase] = {
                    'magma_level': animation_data['magma_level'][mid_idx],
                    'deformation': animation_data['deformation'][mid_idx],
                    'eruption_height': animation_data['eruption_height'][mid_idx],
                    'lava_flow': animation_data['lava_flow'][mid_idx],
                    'ash_density': animation_data['ash_density'][mid_idx]
                }
    
    # Create phase timeline using the scientific data
    st.subheader("Eruption Phase Timeline")
    cols = st.columns(len(phases))
    for i, phase in enumerate(phases):
        with cols[i]:
            # Get count of frames in this phase for width calculation
            frame_count = animation_data['phase'].count(phase)
            percentage = frame_count / len(animation_data['phase']) * 100
            
            # Color based on phase
            phase_colors = {
                'initial': "#3366CC",
                'buildup': "#FF9900",
                'initial_eruption': "#FF6600",
                'main_eruption': "#CC0000",
                'waning': "#9966CC"
            }
            color = phase_colors.get(phase, "#AAAAAA")
            
            # Display formatted phase name and percentage
            formatted_phase = " ".join(word.capitalize() for word in phase.split('_'))
            st.markdown(
                f"<div style='background-color:{color}; padding:10px; border-radius:5px; "
                f"color:white; text-align:center; height:60px;'>"
                f"<b>{formatted_phase}</b><br>{percentage:.1f}%</div>",
                unsafe_allow_html=True
            )
    
    # Prepare data for JavaScript
    volcano_params = {
        'name': selected_volcano_name,
        'type': volcano_type,
        'animation_speed': animation_speed,
        'quality': quality,
        'camera_position': camera_position,
        'show_metrics': show_metrics,
        'show_plumbing': show_plumbing,
        'show_labels': show_labels,
        'eruption_data': {
            'phases': phases,
            'phase_samples': phase_sample_points,
            # Key volcano metrics based on type
            'metrics': VOLCANO_TYPES[volcano_type]
        }
    }
    
    # Add volcano type specific data
    if volcano_type == 'shield':
        # Shield volcanoes have lower viscosity, extensive lava flows
        volcano_params['lava_viscosity'] = 0.2  # Low viscosity (0-1 scale)
        volcano_params['ash_production'] = 0.3  # Lower ash production
        volcano_params['lava_temperature'] = 1200  # Higher temperature (°C)
    elif volcano_type == 'stratovolcano':
        # Stratovolcanoes have higher viscosity, more explosive
        volcano_params['lava_viscosity'] = 0.8  # High viscosity
        volcano_params['ash_production'] = 0.9  # High ash production
        volcano_params['lava_temperature'] = 950  # Lower temperature
    elif volcano_type == 'caldera':
        # Calderas have extremely large magma chambers and explosive potential
        volcano_params['lava_viscosity'] = 0.7
        volcano_params['ash_production'] = 1.0  # Highest ash production
        volcano_params['lava_temperature'] = 900
    elif volcano_type == 'cinder_cone':
        # Cinder cones are smaller with moderate explosivity
        volcano_params['lava_viscosity'] = 0.6
        volcano_params['ash_production'] = 0.7
        volcano_params['lava_temperature'] = 1000
    elif volcano_type == 'lava_dome':
        # Lava domes have extremely high viscosity
        volcano_params['lava_viscosity'] = 1.0  # Highest viscosity
        volcano_params['ash_production'] = 0.4
        volcano_params['lava_temperature'] = 800  # Lowest temperature
    else:
        # Default values
        volcano_params['lava_viscosity'] = 0.5
        volcano_params['ash_production'] = 0.5
        volcano_params['lava_temperature'] = 1000
    
    # Convert data to JSON for JavaScript
    volcano_data_json = json.dumps(volcano_params)
    
    # CSS for full-height visualization
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Controls for the 3D eruption phases
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        buildup_btn = st.button("Magma Buildup", key="buildup", use_container_width=True)
    with col2:
        seismicity_btn = st.button("Seismic Activity", key="seismic", use_container_width=True)
    with col3:
        initial_btn = st.button("Initial Eruption", key="initial", use_container_width=True)
    with col4:
        main_btn = st.button("Main Eruption", key="main", use_container_width=True)
    with col5:
        waning_btn = st.button("Waning Activity", key="waning", use_container_width=True)
    
    # Create hidden input to track selected phase for JavaScript
    if buildup_btn:
        selected_phase = "buildup"
    elif seismicity_btn:
        selected_phase = "initial"
    elif initial_btn:
        selected_phase = "initial_eruption"
    elif main_btn:
        selected_phase = "main_eruption"
    elif waning_btn:
        selected_phase = "waning"
    else:
        selected_phase = "buildup"  # Default to start
    
    # Pass selected phase to JavaScript
    st.markdown(f"""
    <input type="hidden" id="selected_phase" value="{selected_phase}">
    """, unsafe_allow_html=True)
    
    # HTML and JavaScript for the scientific WebGL visualization
    threejs_html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
    
    <div id="volcano-container" style="height: 70vh; width: 100%; background: linear-gradient(180deg, #052D49 0%, #000000 100%); position: relative;">
        <div id="loading" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:24px;">
            Loading Scientific Volcano Model...
        </div>
        
        <!-- Metrics panel -->
        <div id="metrics-panel" style="position: absolute; top: 20px; right: 20px; background: rgba(0,0,0,0.7); color: white; padding: 15px; border-radius: 5px; font-family: sans-serif; display: none;">
            <h3 style="margin-top: 0; color: #FF9900;">Eruption Metrics</h3>
            <div id="phase-name" style="font-weight: bold; margin-bottom: 10px;"></div>
            <table style="width: 100%;">
                <tr>
                    <td>Magma Level:</td>
                    <td id="magma-level">0%</td>
                </tr>
                <tr>
                    <td>Deformation:</td>
                    <td id="deformation">0 cm</td>
                </tr>
                <tr>
                    <td>Eruption Column:</td>
                    <td id="eruption-height">0 km</td>
                </tr>
                <tr>
                    <td>Lava Flow Rate:</td>
                    <td id="lava-flow">0 m³/s</td>
                </tr>
                <tr>
                    <td>Ash Density:</td>
                    <td id="ash-density">0 g/m³</td>
                </tr>
                <tr>
                    <td>Temperature:</td>
                    <td id="temperature">- °C</td>
                </tr>
            </table>
        </div>
        
        <!-- Phase indicator -->
        <div id="phase-indicator" style="position: absolute; bottom: 20px; left: 20px; right: 20px; height: 30px; background: rgba(0,0,0,0.5); border-radius: 15px; overflow: hidden;">
            <div id="phase-progress" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FF9900, #CC0000); transition: width 0.5s ease-in-out;"></div>
            <div id="phase-label" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: bold;"></div>
        </div>
    </div>
    
    <script>
    // Volcano data from Python
    const volcanoData = {volcano_data_json};
    
    // Set up the scene, camera, and renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    const container = document.getElementById("volcano-container");
    const clock = new THREE.Clock();
    
    // Global objects to track
    let volcano, magmaChamber, deepReservoir, mainConduit, secondaryChambers = [];
    let lavaFlows = [], ashCloud, eruption_column;
    let currentPhase = document.getElementById("selected_phase").value || "buildup";
    let phaseProgress = 0;
    
    // Optimize for performance based on quality setting
    const quality = volcanoData.quality || 'Medium';
    const particleCount = {{'Low': 2000, 'Medium': 5000, 'High': 10000}}[quality];
    const segmentCount = {{'Low': 16, 'Medium': 24, 'High': 32}}[quality];
    const geometryDetail = {{'Low': 8, 'Medium': 16, 'High': 32}}[quality];
    
    // Initial setup
    function init() {{
        // Set renderer size and append to container
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setClearColor(0x000000, 0);
        renderer.shadowMap.enabled = quality !== 'Low';  // Disable shadows on low quality
        if (renderer.shadowMap.enabled) {{
            renderer.shadowMap.type = THREE.PCFShadowMap; // Simpler shadow type for performance
        }}
        container.appendChild(renderer.domElement);
        
        // Remove loading message
        document.getElementById("loading").style.display = "none";
        
        // Show metrics panel if enabled
        if (volcanoData.show_metrics) {{
            document.getElementById("metrics-panel").style.display = "block";
        }}
        
        // Set up camera
        setupCamera(volcanoData.camera_position);
        
        // Add orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 1.5; // Limit to not go below ground
        
        // Add ambient and directional lights
        setupLighting();
        
        // Create the terrain
        createTerrain();
        
        // Create volcano with scientifically accurate morphology
        createVolcano();
        
        // Create scientifically accurate plumbing system
        if (volcanoData.show_plumbing) {{
            createMagmaPlumbingSystem();
        }}
        
        // Create dynamic elements
        createDynamicElements();
        
        // Set initial phase
        updatePhase(currentPhase);
        
        // Handle window resize
        window.addEventListener('resize', onWindowResize);
        
        // Start animation loop
        animate();
    }}
    
    // Set up camera position based on selection
    function setupCamera(position) {{
        switch(position) {{
            case 'Aerial':
                camera.position.set(0, 150, 200);
                break;
            case 'Ground Level':
                camera.position.set(100, 20, 100);
                break;
            case 'Cross-Section':
                camera.position.set(-50, 50, 200);
                break;
            case 'Side View':
                camera.position.set(200, 50, 0);
                break;
            default:
                camera.position.set(0, 150, 200);
        }}
        
        camera.lookAt(0, 0, 0);
    }}
    
    // Setup lighting
    function setupLighting() {{
        // Ambient light for general illumination
        const ambientLight = new THREE.AmbientLight(0x333333);
        scene.add(ambientLight);
        
        // Main sunlight - simpler shadow setup for performance
        const sunlight = new THREE.DirectionalLight(0xFFFFFF, 1);
        sunlight.position.set(100, 200, 100);
        
        if (renderer.shadowMap.enabled) {{
            sunlight.castShadow = true;
            // Reduced shadow quality for better performance
            sunlight.shadow.mapSize.width = quality === 'High' ? 2048 : 1024;
            sunlight.shadow.mapSize.height = quality === 'High' ? 2048 : 1024;
            sunlight.shadow.camera.near = 10;
            sunlight.shadow.camera.far = 1000;
            sunlight.shadow.camera.left = -500;
            sunlight.shadow.camera.right = 500;
            sunlight.shadow.camera.top = 500;
            sunlight.shadow.camera.bottom = -500;
        }}
        scene.add(sunlight);
        
        // Add magma glow light - will be visible during eruption
        const magmaLight = new THREE.PointLight(0xFF4500, 0, 150);
        magmaLight.position.set(0, 50, 0);
        scene.add(magmaLight);
    }}
    
    // Create terrain - simplified for performance
    function createTerrain() {{
        // Create large ground plane - lower resolution for performance
        const groundSize = 1000;
        const groundDetail = quality === 'Low' ? 32 : (quality === 'Medium' ? 48 : 64);
        
        const groundGeometry = new THREE.PlaneGeometry(groundSize, groundSize, groundDetail, groundDetail);
        
        // Add some natural terrain variation
        const vertices = groundGeometry.attributes.position.array;
        for (let i = 0; i < vertices.length; i += 3) {{
            // Skip center area where volcano will be
            const x = vertices[i];
            const z = vertices[i+2];
            const distanceFromCenter = Math.sqrt(x*x + z*z);
            
            if (distanceFromCenter > 50) {{
                // Add terrain variation based on distance
                vertices[i+1] = (Math.sin(x/30) + Math.cos(z/30)) * 2 * (distanceFromCenter / groundSize * 10);
            }}
        }}
        
        // Ground material varies by volcano environment
        let groundColor;
        switch(volcanoData.type) {{
            case 'shield':
                // Hawaii-like terrain
                groundColor = 0x365314; // Dark green
                break;
            case 'stratovolcano':
                // Snowy or rocky terrain
                groundColor = 0x8A9A5B; // Moss green
                break;
            case 'caldera':
                // Desert/arid environment
                groundColor = 0xA98958; // Tan/sandy
                break;
            default:
                groundColor = 0x556B2F; // Olive
        }}
        
        // Simpler material for better performance
        const groundMaterial = new THREE.MeshStandardMaterial({{ 
            color: groundColor,
            roughness: 1,
            metalness: 0.1,
            flatShading: quality !== 'Low'  // Disable flat shading on low quality
        }});
        
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.5;
        if (renderer.shadowMap.enabled) {{
            ground.receiveShadow = true;
        }}
        scene.add(ground);
    }}
    
    // Create volcano with scientifically accurate morphology
    function createVolcano() {{
        // Different geometry based on volcano type
        let geometry;
        let color;
        
        // Set shape parameters based on scientific models
        switch(volcanoData.type) {{
            case 'shield':
                // Shield volcanoes are broad with gentle slopes
                geometry = createShieldVolcanoGeometry();
                color = 0x654321; // Brown
                break;
            case 'stratovolcano':
                // Stratovolcanoes are tall with steep sides
                geometry = createStratovolcanoGeometry();
                color = 0x808080; // Gray
                break;
            case 'caldera':
                // Calderas have a depression at the top
                geometry = createCalderaGeometry();
                color = 0x8B4513; // Saddle brown
                break;
            case 'cinder_cone':
                // Cinder cones are small with steep sides
                geometry = createCinderConeGeometry();
                color = 0x3B2F2F; // Dark brown-gray
                break;
            case 'lava_dome':
                // Lava domes are dome-shaped
                geometry = createLavaDomeGeometry();
                color = 0x696969; // Dim gray
                break;
            default:
                // Default to stratovolcano
                geometry = createStratovolcanoGeometry();
                color = 0x808080; // Gray
        }}
        
        // Material with roughness for natural look - simplified for performance
        const material = new THREE.MeshStandardMaterial({{ 
            color: color, 
            flatShading: quality !== 'Low',
            roughness: 0.9,
            metalness: 0.1
        }});
        
        // Create and add volcano mesh
        volcano = new THREE.Mesh(geometry, material);
        if (renderer.shadowMap.enabled) {{
            volcano.castShadow = true;
            volcano.receiveShadow = true;
        }}
        scene.add(volcano);
        
        // Add labels if enabled and not in low quality mode
        if (volcanoData.show_labels && quality !== 'Low') {{
            addVolcanoLabels();
        }}
    }}
    
    // Simplified geometries for better loading performance
    // Custom shield volcano geometry (broad, gentle slopes)
    function createShieldVolcanoGeometry() {{
        const radius = 150;
        const height = 50;
        // Adjust detail based on quality setting
        const radialSegments = segmentCount;
        const heightSegments = geometryDetail / 2;
        
        // Create base cone with gentle slope
        const geometry = new THREE.ConeGeometry(radius, height, radialSegments, heightSegments, true);
        geometry.rotateX(Math.PI); // Flip to have base at y=0
        
        // For medium/high quality, add a crater
        if (quality !== 'Low') {{
            // Create a simplified crater by directly manipulating vertices
            const positions = geometry.attributes.position.array;
            const centerIndex = positions.length - 3; // Top center vertex
            
            // Create a depression at the top
            positions[centerIndex + 1] -= 5; // Lower the center point
            
            // Lower vertices near the top to create crater shape
            for (let i = 0; i < positions.length; i += 3) {{
                const y = positions[i + 1];
                // If near the top
                if (y < -height + 10) {{
                    // Calculate distance from center in xz plane
                    const x = positions[i];
                    const z = positions[i + 2];
                    const distFromCenter = Math.sqrt(x*x + z*z);
                    
                    // If close to center but not at center
                    if (distFromCenter < 20 && distFromCenter > 0.1) {{
                        // Create crater shape
                        positions[i + 1] -= 5 * (1 - distFromCenter/20);
                    }}
                }}
            }}
            
            // Update geometry
            geometry.attributes.position.needsUpdate = true;
            geometry.computeVertexNormals();
        }}
        
        // For high quality, add natural variation
        if (quality === 'High') {{
            addNaturalVariation(geometry, 0.05);
        }}
        
        return geometry;
    }}
    
    // Create simple stratovolcano geometry
    function createStratovolcanoGeometry() {{
        const radius = 100;
        const height = 100;
        // Adjust detail based on quality setting
        const radialSegments = segmentCount;
        const heightSegments = geometryDetail / 2;
        
        // Create base cone
        const geometry = new THREE.ConeGeometry(radius, height, radialSegments, heightSegments, true);
        geometry.rotateX(Math.PI); // Flip to have base at y=0
        
        // For medium/high quality, add a crater
        if (quality !== 'Low') {{
            // Manipulate vertices to create crater
            const positions = geometry.attributes.position.array;
            
            // Create a depression at the top
            for (let i = 0; i < positions.length; i += 3) {{
                const y = positions[i + 1];
                
                // If near the top
                if (y < -height + 20) {{
                    // Calculate distance from center in xz plane
                    const x = positions[i];
                    const z = positions[i + 2];
                    const distFromCenter = Math.sqrt(x*x + z*z);
                    
                    // If close to center but not at center
                    if (distFromCenter < 25 && distFromCenter > 0.1) {{
                        // Create crater shape
                        positions[i + 1] -= 15 * (1 - distFromCenter/25);
                    }}
                }}
            }}
            
            // Update geometry
            geometry.attributes.position.needsUpdate = true;
            geometry.computeVertexNormals();
        }}
        
        // For high quality, add natural variation
        if (quality === 'High') {{
            addNaturalVariation(geometry, 0.1);
        }}
        
        return geometry;
    }}
    
    // Simplified caldera geometry for better performance
    function createCalderaGeometry() {{
        // Base shape - reduced complexity for performance
        const outerRadius = 150;
        const innerRadius = 60;
        const height = 70;
        const floorHeight = 40;
        
        // Simplified approach: two cylinders and a cone
        const outerShape = new THREE.CylinderGeometry(
            outerRadius, outerRadius, 1, segmentCount, 1, true
        );
        
        // Create cone for sides
        const sideShape = new THREE.CylinderGeometry(
            innerRadius, outerRadius, height, segmentCount, 1, true
        );
        sideShape.translate(0, -height/2, 0);
        
        // Create inner cylinder for caldera floor
        const floorShape = new THREE.CylinderGeometry(
            0, innerRadius, height - floorHeight, segmentCount, 1, true
        );
        floorShape.translate(0, -height + (height - floorHeight)/2, 0);
        
        // Merge geometries
        const mergedGeometry = new THREE.BufferGeometry();
        
        // Function to merge buffer geometries
        function mergeBufferGeometries(geometries) {{
            // Count total vertices and faces
            let vertexCount = 0;
            for (const geo of geometries) {{
                vertexCount += geo.attributes.position.count;
            }}
            
            // Create merged arrays
            const positions = new Float32Array(vertexCount * 3);
            const normals = new Float32Array(vertexCount * 3);
            
            // Copy data
            let offset = 0;
            for (const geo of geometries) {{
                const posArr = geo.attributes.position.array;
                const normArr = geo.attributes.normal.array;
                
                positions.set(posArr, offset * 3);
                normals.set(normArr, offset * 3);
                
                offset += geo.attributes.position.count;
            }}
            
            // Create merged geometry
            const merged = new THREE.BufferGeometry();
            merged.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            merged.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
            
            return merged;
        }}
        
        // Merge the parts
        const geometry = mergeBufferGeometries([outerShape, sideShape, floorShape]);
        
        // For high quality, add some variation
        if (quality === 'High') {{
            addNaturalVariation(geometry, 0.1);
        }}
        
        return geometry;
    }}
    
    // Create simplified cinder cone geometry
    function createCinderConeGeometry() {{
        const radius = 50;
        const height = 80;
        // Adjust detail based on quality setting
        const radialSegments = segmentCount;
        const heightSegments = geometryDetail / 2;
        
        // Create base cone with steep slope
        const geometry = new THREE.ConeGeometry(radius, height, radialSegments, heightSegments, true);
        geometry.rotateX(Math.PI); // Flip to have base at y=0
        
        // For medium/high quality, add a crater
        if (quality !== 'Low') {{
            // Create a simplified crater by modifying vertices
            const positions = geometry.attributes.position.array;
            
            // Create a depression at the top
            for (let i = 0; i < positions.length; i += 3) {{
                const y = positions[i + 1];
                
                // If near the top
                if (y < -height + 15) {{
                    // Calculate distance from center in xz plane
                    const x = positions[i];
                    const z = positions[i + 2];
                    const distFromCenter = Math.sqrt(x*x + z*z);
                    
                    // If close to center but not at center
                    if (distFromCenter < 20 && distFromCenter > 0.1) {{
                        // Create crater shape
                        positions[i + 1] -= 10 * (1 - distFromCenter/20);
                    }}
                }}
            }}
            
            // Update geometry
            geometry.attributes.position.needsUpdate = true;
            geometry.computeVertexNormals();
        }}
        
        // For high quality, add pronounced natural variation
        if (quality === 'High') {{
            addNaturalVariation(geometry, 0.15);
        }}
        
        return geometry;
    }}
    
    // Create simplified lava dome geometry
    function createLavaDomeGeometry() {{
        // Create dome shape
        const radius = 80;
        // Adjust detail based on quality setting
        const widthSegments = segmentCount;
        const heightSegments = geometryDetail / 2;
        
        // Use half sphere for dome
        const geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments, 0, Math.PI * 2, 0, Math.PI / 2);
        
        // For high quality, add blocky, cracked surface
        if (quality === 'High') {{
            addNaturalVariation(geometry, 0.2);
        }}
        
        return geometry;
    }}
    
    // Add natural terrain variation to geometry - simplified for performance
    function addNaturalVariation(geometry, intensity) {{
        const positions = geometry.attributes.position.array;
        
        // Reduce iterations for better performance
        const skipFactor = quality === 'Low' ? 6 : (quality === 'Medium' ? 3 : 1);
        
        for (let i = 0; i < positions.length; i += 3 * skipFactor) {{
            const x = positions[i];
            const y = positions[i+1];
            const z = positions[i+2];
            
            // Skip points at y=0 (base of volcano)
            if (Math.abs(y) < 0.1) continue;
            
            // Add deterministic variation based on position
            const noise1 = Math.sin(x/10) * Math.cos(z/10) * intensity;
            const noise2 = Math.cos(x/15) * Math.sin(z/15) * intensity;
            
            positions[i] += noise1 * 10;
            positions[i+1] += noise2 * 10;
            positions[i+2] += noise1 * 10;
        }}
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
    }}
    
    // Add labels to volcano features - simplified to text overlay for better performance
    function addVolcanoLabels() {{
        // In a real implementation, this would use CSS2DRenderer
        // For this simplified version, we'll just add text overlay
        
        // Create HTML overlay for labels
        const labelContainer = document.createElement('div');
        labelContainer.style.position = 'absolute';
        labelContainer.style.top = '0';
        labelContainer.style.left = '0';
        labelContainer.style.width = '100%';
        labelContainer.style.height = '100%';
        labelContainer.style.pointerEvents = 'none';
        container.appendChild(labelContainer);
        
        // Add some basic labels
        const labels = [
            {{ text: 'Summit Crater', x: 50, y: 30 }},
            {{ text: 'Magma Chamber', x: 50, y: 70 }},
            {{ text: volcanoData.type === 'shield' ? 'Rift Zone' : 
                   volcanoData.type === 'caldera' ? 'Caldera Floor' : 
                   'Main Conduit', x: 70, y: 50 }}
        ];
        
        // Create label elements
        labels.forEach(label => {{
            const div = document.createElement('div');
            div.className = 'volcano-label';
            div.textContent = label.text;
            div.style.position = 'absolute';
            div.style.left = label.x + '%';
            div.style.top = label.y + '%';
            div.style.color = 'white';
            div.style.padding = '2px 6px';
            div.style.background = 'rgba(0,0,0,0.6)';
            div.style.borderRadius = '3px';
            div.style.fontSize = '12px';
            div.style.transform = 'translate(-50%, -50%)';
            
            labelContainer.appendChild(div);
        }});
    }}
    
    // Get appropriate summit height based on volcano type
    function getSummitHeight() {{
        switch(volcanoData.type) {{
            case 'shield': return 50;
            case 'stratovolcano': return 100;
            case 'caldera': return 70;
            case 'cinder_cone': return 80;
            case 'lava_dome': return 80;
            default: return 60;
        }}
    }}
    
    // Create simplified magma plumbing system
    function createMagmaPlumbingSystem() {{
        // Create main magma chamber
        const chamberDetail = quality === 'Low' ? 16 : (quality === 'Medium' ? 24 : 32);
        const chamberGeometry = new THREE.SphereGeometry(40, chamberDetail, chamberDetail/2);
        const chamberMaterial = new THREE.MeshStandardMaterial({{
            color: 0xFF4500,
            emissive: 0xFF4500,
            emissiveIntensity: 0.2,
            transparent: true,
            opacity: 0.7
        }});
        
        magmaChamber = new THREE.Mesh(chamberGeometry, chamberMaterial);
        magmaChamber.position.set(0, -40, 0);
        scene.add(magmaChamber);
        
        // Create simplified conduits based on volcano type
        switch(volcanoData.type) {{
            case 'shield':
                // Shield volcanoes have a connected deep reservoir and rift zones
                createDeepReservoir(-20, -120, -20, 60);
                
                // Only create main conduit for low quality
                if (quality !== 'Low') {{
                    // Create rift zones (radiating lateral dikes)
                    createConduit(
                        new THREE.Vector3(0, -20, 0),
                        new THREE.Vector3(80, 5, 0),
                        7
                    );
                }}
                
                // Main conduit to surface
                mainConduit = createConduit(
                    new THREE.Vector3(0, -40, 0),
                    new THREE.Vector3(0, 50, 0),
                    8
                );
                break;
                
            case 'stratovolcano':
                // Stratovolcanoes have complex plumbing with multiple chambers
                createDeepReservoir(20, -120, 20, 60);
                
                // In medium/high quality, add secondary chamber
                if (quality !== 'Low') {{
                    // Create secondary chamber
                    const secondaryGeometry = new THREE.SphereGeometry(20, chamberDetail, chamberDetail/2);
                    const secondaryChamber = new THREE.Mesh(secondaryGeometry, chamberMaterial);
                    secondaryChamber.position.set(30, 0, 30);
                    scene.add(secondaryChamber);
                    secondaryChambers.push(secondaryChamber);
                    
                    // Connect chambers
                    createConduit(
                        new THREE.Vector3(0, -40, 0),
                        new THREE.Vector3(30, 0, 30),
                        6
                    );
                }}
                
                // Connect to deep reservoir in medium/high quality
                if (quality !== 'Low') {{
                    createConduit(
                        new THREE.Vector3(20, -120, 20),
                        new THREE.Vector3(0, -40, 0),
                        10
                    );
                }}
                
                // Main conduit to surface
                mainConduit = createConduit(
                    new THREE.Vector3(0, -40, 0),
                    new THREE.Vector3(0, 100, 0),
                    8
                );
                break;
                
            case 'caldera':
                // Calderas have large main chamber and complex conduit system
                createDeepReservoir(0, -150, 0, 100);
                
                // Connect to deep reservoir
                if (quality !== 'Low') {{
                    createConduit(
                        new THREE.Vector3(0, -150, 0),
                        new THREE.Vector3(0, -40, 0),
                        12
                    );
                    
                    // Create ring dikes in medium/high quality
                    const ringCount = quality === 'Medium' ? 4 : 8;
                    for (let i = 0; i < ringCount; i++) {{
                        const angle = (i / ringCount) * Math.PI * 2;
                        const x = Math.sin(angle) * 60;
                        const z = Math.cos(angle) * 60;
                        
                        if (i === 0) {{
                            mainConduit = createConduit(
                                new THREE.Vector3(0, -40, 0),
                                new THREE.Vector3(x, 70, z),
                                8
                            );
                        }} else {{
                            createConduit(
                                new THREE.Vector3(0, -40, 0),
                                new THREE.Vector3(x, 70, z),
                                5
                            );
                        }}
                    }}
                }} else {{
                    // Just one main conduit in low quality
                    mainConduit = createConduit(
                        new THREE.Vector3(0, -40, 0),
                        new THREE.Vector3(0, 70, 0),
                        8
                    );
                }}
                break;
                
            case 'cinder_cone':
                // Cinder cones have simple, direct conduit systems
                mainConduit = createConduit(
                    new THREE.Vector3(0, -40, 0),
                    new THREE.Vector3(0, 80, 0),
                    7
                );
                break;
                
            case 'lava_dome':
                // Lava domes have thick conduit
                createDeepReservoir(0, -120, 0, 50);
                
                // Connect to deep reservoir in medium/high quality
                if (quality !== 'Low') {{
                    createConduit(
                        new THREE.Vector3(0, -120, 0),
                        new THREE.Vector3(0, -40, 0),
                        10
                    );
                }}
                
                // Thick main conduit for viscous lava
                mainConduit = createConduit(
                    new THREE.Vector3(0, -40, 0),
                    new THREE.Vector3(0, 80, 0),
                    12
                );
                break;
        }}
    }}
    
    // Create a deep magma reservoir
    function createDeepReservoir(x, y, z, radius) {{
        const chamberDetail = quality === 'Low' ? 16 : (quality === 'Medium' ? 24 : 32);
        const reservoirGeometry = new THREE.SphereGeometry(radius, chamberDetail, chamberDetail/2);
        const reservoirMaterial = new THREE.MeshStandardMaterial({{
            color: 0xFF2000,
            emissive: 0xFF2000,
            emissiveIntensity: 0.2,
            transparent: true,
            opacity: 0.5
        }});
        
        deepReservoir = new THREE.Mesh(reservoirGeometry, reservoirMaterial);
        deepReservoir.position.set(x, y, z);
        scene.add(deepReservoir);
        
        return deepReservoir;
    }}
    
    // Create magma conduit connecting two points - simplified for performance
    function createConduit(start, end, radius) {{
        // Use cylinder for low quality, curved tube for medium/high
        let conduit;
        
        if (quality === 'Low') {{
            // For low quality, use a simple cylinder
            const direction = new THREE.Vector3().subVectors(end, start);
            const height = direction.length();
            const midpoint = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
            
            const geometry = new THREE.CylinderGeometry(radius, radius, height, 12, 1);
            
            // Orient to point from start to end
            const axis = new THREE.Vector3(0, 1, 0);
            const normalizedDirection = direction.clone().normalize();
            const quaternion = new THREE.Quaternion().setFromUnitVectors(axis, normalizedDirection);
            geometry.applyQuaternion(quaternion);
            
            // Move to correct position
            geometry.translate(midpoint.x, midpoint.y, midpoint.z);
            
            const magmaMaterial = new THREE.MeshStandardMaterial({{
                color: 0xFF4500,
                emissive: 0xFF4500,
                emissiveIntensity: 0.3,
                transparent: true,
                opacity: 0.7
            }});
            
            conduit = new THREE.Mesh(geometry, magmaMaterial);
        }} else {{
            // For medium/high quality, use a curved tube
            const points = [];
            points.push(start);
            
            // Add slight bend for more natural look
            const midPoint = new THREE.Vector3(
                (start.x + end.x) / 2 + (Math.random() - 0.5) * 10,
                (start.y + end.y) / 2,
                (start.z + end.z) / 2 + (Math.random() - 0.5) * 10
            );
            points.push(midPoint);
            points.push(end);
            
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeDetail = quality === 'Medium' ? 12 : 20;
            const tubeGeometry = new THREE.TubeGeometry(curve, tubeDetail, radius, 8, false);
            
            const magmaMaterial = new THREE.MeshStandardMaterial({{
                color: 0xFF4500,
                emissive: 0xFF4500,
                emissiveIntensity: 0.3,
                transparent: true,
                opacity: 0.7
            }});
            
            conduit = new THREE.Mesh(tubeGeometry, magmaMaterial);
        }}
        
        scene.add(conduit);
        return conduit;
    }}
    
    // Create dynamic eruption elements - simplified for performance
    function createDynamicElements() {{
        // Create lava flows - initially hidden
        createLavaFlows();
        
        // Create ash cloud - initially hidden
        createAshCloud();
        
        // Create eruption column - initially hidden
        createEruptionColumn();
    }}
    
    // Create simplified lava flows based on volcano type
    function createLavaFlows() {{
        // Create different numbers/types of lava flows based on volcano type
        let flowCount, flowLength, flowWidth;
        
        // Reduce complexity for performance
        switch(volcanoData.type) {{
            case 'shield':
                flowCount = quality === 'Low' ? 2 : (quality === 'Medium' ? 4 : 6);
                flowLength = 200;
                flowWidth = 15;
                break;
            case 'stratovolcano':
                flowCount = quality === 'Low' ? 2 : (quality === 'Medium' ? 3 : 4);
                flowLength = 120;
                flowWidth = 10;
                break;
            case 'caldera':
                flowCount = quality === 'Low' ? 1 : (quality === 'Medium' ? 2 : 3);
                flowLength = 80;
                flowWidth = 12;
                break;
            case 'cinder_cone':
                flowCount = quality === 'Low' ? 1 : 2;
                flowLength = 100;
                flowWidth = 8;
                break;
            case 'lava_dome':
                flowCount = 1;
                flowLength = 50;
                flowWidth = 20;
                break;
            default:
                flowCount = quality === 'Low' ? 1 : (quality === 'Medium' ? 2 : 3);
                flowLength = 100;
                flowWidth = 10;
        }}
        
        // Create multiple lava flow paths
        for (let i = 0; i < flowCount; i++) {{
            const angle = (i / flowCount) * Math.PI * 2;
            const startX = Math.sin(angle) * 20;
            const startZ = Math.cos(angle) * 20;
            
            const flow = createLavaFlow(startX, startZ, angle, flowLength, flowWidth);
            lavaFlows.push(flow);
        }}
    }}
    
    // Create simplified individual lava flow
    function createLavaFlow(startX, startZ, angle, length, width) {{
        // Use simplified approach for low quality
        let lavaFlow;
        const summitHeight = getSummitHeight();
        
        if (quality === 'Low') {{
            // For low quality, use simple cone shape
            const flowGeometry = new THREE.ConeGeometry(width, length, 8, 1, true);
            flowGeometry.rotateX(-Math.PI/2); // Lay it down
            flowGeometry.translate(0, 0, length/2); // Center at origin
            
            // Rotate to face correct direction
            flowGeometry.rotateY(angle);
            
            // Position at summit
            flowGeometry.translate(startX, summitHeight, startZ);
            
            // Lava material with glow based on temperature
            const lavaColor = getColorForTemperature(volcanoData.lava_temperature);
            const lavaMaterial = new THREE.MeshStandardMaterial({{
                color: lavaColor,
                emissive: lavaColor,
                emissiveIntensity: 0.6,
                roughness: 0.7,
                metalness: 0.3
            }});
            
            lavaFlow = new THREE.Mesh(flowGeometry, lavaMaterial);
        }} else {{
            // For medium/high quality, use curved path
            const points = [];
            points.push(new THREE.Vector3(startX, summitHeight, startZ));
            
            // Create curved path down the volcano
            let currentY = summitHeight;
            let currentX = startX;
            let currentZ = startZ;
            
            // Reduce segments for better performance
            const segmentCount = quality === 'Medium' ? 6 : 10;
            for (let i = 1; i <= segmentCount; i++) {{
                const t = i / segmentCount;
                const radius = t * length; // Increase radius as we go down
                
                // Decrease height logarithmically for realistic flow
                currentY = summitHeight * Math.pow(0.95, i*2);
                
                // Add some randomness to the path with more pronounced meandering
                // for lower viscosity lava (shield volcanoes)
                const angleVariation = angle + 
                    (Math.random() - 0.5) * (1 - volcanoData.lava_viscosity);
                currentX = Math.sin(angleVariation) * radius;
                currentZ = Math.cos(angleVariation) * radius;
                
                points.push(new THREE.Vector3(currentX, currentY, currentZ));
            }}
            
            // Create tube geometry along path
            const curve = new THREE.CatmullRomCurve3(points);
            const tubeDetail = quality === 'Medium' ? 12 : 20;
            const tubeGeometry = new THREE.TubeGeometry(curve, tubeDetail, width / 2, 8, false);
            
            // Lava material with glow based on temperature
            const lavaColor = getColorForTemperature(volcanoData.lava_temperature);
            const lavaMaterial = new THREE.MeshStandardMaterial({{
                color: lavaColor,
                emissive: lavaColor,
                emissiveIntensity: 0.6,
                roughness: 0.7,
                metalness: 0.3
            }});
            
            lavaFlow = new THREE.Mesh(tubeGeometry, lavaMaterial);
        }}
        
        lavaFlow.visible = false; // Hidden initially
        scene.add(lavaFlow);
        
        return lavaFlow;
    }}
    
    // Get color based on temperature
    function getColorForTemperature(temp) {{
        // Convert temperature to RGB color
        // Higher temps are brighter orange/yellow
        if (temp >= 1200) {{
            return 0xFFAA00; // Very hot (bright yellow-orange)
        }} else if (temp >= 1000) {{
            return 0xFF8800; // Hot (orange)
        }} else if (temp >= 800) {{
            return 0xFF4400; // Moderate (red-orange)
        }} else {{
            return 0xDD2200; // Cooler (dark red)
        }}
    }}
    
    // Create ash cloud particle system - simplified for performance
    function createAshCloud() {{
        const geometry = new THREE.BufferGeometry();
        const particles = particleCount; // Reduced for performance
        const positions = new Float32Array(particles * 3);
        const colors = new Float32Array(particles * 3);
        
        // Create initial positions - not visible yet
        for (let i = 0; i < positions.length; i += 3) {{
            positions[i] = 0;
            positions[i+1] = 0;
            positions[i+2] = 0;
            
            colors[i] = 0.3;
            colors[i+1] = 0.3;
            colors[i+2] = 0.3;
        }}
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        // Reduced point size for performance
        const material = new THREE.PointsMaterial({{
            size: quality === 'Low' ? 2 : 3,
            vertexColors: true,
            transparent: true,
            opacity: 0,
            sizeAttenuation: true
        }});
        
        ashCloud = new THREE.Points(geometry, material);
        scene.add(ashCloud);
    }}
    
    // Create simplified eruption column
    function createEruptionColumn() {{
        // Create column parameters based on volcano type
        let height = 0;
        let radius = 0;
        
        switch(volcanoData.type) {{
            case 'shield':
                height = 80;  // Lower column
                radius = 20;
                break;
            case 'stratovolcano':
                height = 200; // Tall column
                radius = 30;
                break;
            case 'caldera':
                height = 250; // Very tall column
                radius = 40;
                break;
            case 'cinder_cone':
                height = 120; // Moderate column
                radius = 15;
                break;
            case 'lava_dome':
                height = 50;  // Minimal column
                radius = 25;
                break;
        }}
        
        // Create eruption column geometry - simplified for performance
        let geometry;
        if (quality === 'Low') {{
            // For low quality, use a simple cone
            geometry = new THREE.ConeGeometry(radius, height, 8, 1);
        }} else {{
            geometry = createEruptionColumnGeometry(height, radius);
        }}
        
        const material = new THREE.MeshStandardMaterial({{
            color: 0x666666,
            transparent: true,
            opacity: 0,
            roughness: 1
        }});
        
        eruption_column = new THREE.Mesh(geometry, material);
        eruption_column.position.y = getSummitHeight();
        scene.add(eruption_column);
    }}
    
    // Create eruption column geometry - medium/high quality only
    function createEruptionColumnGeometry(height, radius) {{
        const points = [];
        // Reduce segments for better performance
        const segments = quality === 'Medium' ? 6 : 10;
        
        // Create profile curve for lathe geometry
        for (let i = 0; i <= segments; i++) {{
            const t = i / segments;
            
            // Umbrella-like shape for eruption column
            let r;
            if (t < 0.2) {{
                // Base of column is narrower
                r = radius * t * 5;
            }} else {{
                // Upper part expands outward
                r = radius * (1 + t);
            }}
            
            points.push(new THREE.Vector2(r, t * height));
        }}
        
        // Reduce radial segments for better performance
        const radialSegments = quality === 'Medium' ? 12 : 20;
        const geometry = new THREE.LatheGeometry(points, radialSegments);
        return geometry;
    }}
    
    // Update phase based on current selection
    function updatePhase(phase) {{
        currentPhase = phase;
        phaseProgress = 0;
        
        // Update phase indicator
        document.getElementById("phase-label").innerText = currentPhase.replace('_', ' ').toUpperCase();
        
        // Reset phase progress bar
        document.getElementById("phase-progress").style.width = "0%";
        
        // Update metrics display
        updateMetricsPanel(phase, 0);
        
        // Get eruption data for this phase
        const phaseData = volcanoData.eruption_data.phase_samples[phase];
        
        // Update visual elements to match phase
        updateVisualElements(phase, phaseData);
    }}
    
    // Update metrics panel with current phase data
    function updateMetricsPanel(phase, progress) {{
        if (!volcanoData.show_metrics) return;
        
        // Get all metrics panels
        const magmaLevel = document.getElementById("magma-level");
        const deformation = document.getElementById("deformation");
        const eruptionHeight = document.getElementById("eruption-height");
        const lavaFlow = document.getElementById("lava-flow");
        const ashDensity = document.getElementById("ash-density");
        const temperature = document.getElementById("temperature");
        
        // Calculate current data values
        const phaseData = volcanoData.eruption_data.phase_samples[phase];
        if (!phaseData) return;
        
        // Format values for display
        magmaLevel.innerText = Math.round(phaseData.magma_level * 100) + "%";
        deformation.innerText = (phaseData.deformation * 100).toFixed(1) + " cm";
        eruptionHeight.innerText = (phaseData.eruption_height / 10).toFixed(1) + " km";
        lavaFlow.innerText = Math.round(phaseData.lava_flow * 100) + " m³/s";
        ashDensity.innerText = Math.round(phaseData.ash_density * 1000) + " g/m³";
        temperature.innerText = volcanoData.lava_temperature + " °C";
        
        // Update phase name
        document.getElementById("phase-name").innerText = 
            phase.replace('_', ' ').toUpperCase() + " PHASE - " + 
            Math.round(progress * 100) + "% complete";
    }}
    
    // Update visual elements based on phase - simplified for performance
    function updateVisualElements(phase, phaseData) {{
        // Get current magma light
        const magmaLight = scene.children.find(child => 
            child instanceof THREE.PointLight && child.color.r > 0.5 && child.color.g < 0.5);
        
        if (!phaseData) return;
        
        // Update magma chamber properties
        if (magmaChamber) {{
            // Scale magma chamber slightly based on phase to show pressure
            const scale = 1 + phaseData.magma_level * 0.2;
            magmaChamber.scale.set(scale, scale, scale);
            
            // Adjust glow intensity
            magmaChamber.material.emissiveIntensity = 0.2 + phaseData.magma_level * 0.3;
        }}
        
        // Update deep reservoir properties (when present)
        if (deepReservoir) {{
            deepReservoir.material.emissiveIntensity = 0.1 + phaseData.magma_level * 0.2;
        }}
        
        // Update main conduit to show magma rising
        if (mainConduit) {{
            // Adjust opacity to show magma flow
            if (phase === 'buildup') {{
                // Gradually fill conduit during buildup
                mainConduit.material.opacity = 0.3 + phaseData.magma_level * 0.5;
            }} else {{
                // Full conduit during eruption
                mainConduit.material.opacity = 0.9;
            }}
        }}
        
        // Update secondary chambers when present
        secondaryChambers.forEach(chamber => {{
            chamber.material.emissiveIntensity = 0.2 + phaseData.magma_level * 0.3;
        }});
        
        // Update lava flows
        lavaFlows.forEach((flow, index) => {{
            // Only show lava flows during eruption phases
            flow.visible = ['initial_eruption', 'main_eruption'].includes(phase);
            
            if (flow.visible) {{
                // Scale flow based on lava_flow value, with some variation
                const flowScale = phaseData.lava_flow * (0.7 + Math.random() * 0.6);
                flow.scale.set(flowScale, flowScale, flowScale);
                
                // Adjust opacity
                flow.material.opacity = Math.min(0.3 + phaseData.lava_flow * 0.7, 1.0);
            }}
        }});
        
        // Update ash cloud 
        if (ashCloud) {{
            const material = ashCloud.material;
            
            // Only show ash during eruption phases
            material.opacity = ['initial_eruption', 'main_eruption', 'waning'].includes(phase) ? 
                phaseData.ash_density * 0.6 : 0;
                
            if (material.opacity > 0) {{
                // For Low/Medium quality, no need to update all particles every frame
                if (quality !== 'Low') {{
                    setupAshCloudParticles(phaseData.ash_density, phaseData.eruption_height);
                }}
            }}
        }}
        
        // Update eruption column
        if (eruption_column) {{
            // Only show eruption column during eruption phases
            eruption_column.material.opacity = ['initial_eruption', 'main_eruption'].includes(phase) ? 
                Math.min(phaseData.eruption_height * 0.5, 0.9) : 0;
                
            if (eruption_column.material.opacity > 0) {{
                // Scale column based on eruption_height
                const heightScale = 0.5 + phaseData.eruption_height * 0.5;
                eruption_column.scale.set(1, heightScale, 1);
            }}
        }}
        
        // Update magma light intensity
        if (magmaLight) {{
            // Light intensity varies by phase
            if (['initial_eruption', 'main_eruption'].includes(phase)) {{
                magmaLight.intensity = 1 + phaseData.magma_level * 1.5;
            }} else {{
                magmaLight.intensity = phaseData.magma_level * 0.5;
            }}
        }}
    }}
    
    // Setup ash cloud particles - simplified for medium/high quality only
    function setupAshCloudParticles(density, height) {{
        if (!ashCloud) return;
        
        const positions = ashCloud.geometry.attributes.position.array;
        const colors = ashCloud.geometry.attributes.color.array;
        
        const summitHeight = getSummitHeight();
        const eruptionHeight = height * 200; // Convert to scene units
        const ashRadius = 50 + density * 150; // Cloud radius grows with density
        
        // Limit updates for performance
        const updateFactor = quality === 'Medium' ? 3 : 1; // Update every 3rd particle for medium quality
        
        for (let i = 0; i < positions.length; i += 3 * updateFactor) {{
            // Create cloud shape that expands with height
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            
            // Vertical distribution - more particles higher up for larger eruptions
            const heightFactor = Math.pow(Math.random(), 0.5); // Bias toward top of cloud
            const particleHeight = summitHeight + heightFactor * eruptionHeight;
            
            // Horizontal distribution - umbrella shape that widens with height
            const distFromCenter = (particleHeight - summitHeight) / eruptionHeight;
            const radius = ashRadius * distFromCenter;
            
            positions[i] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i+1] = particleHeight;
            positions[i+2] = radius * Math.sin(phi) * Math.sin(theta);
            
            // Color gradient - darker at base, lighter at top
            const gray = 0.2 + 0.3 * distFromCenter;
            colors[i] = gray;
            colors[i+1] = gray;
            colors[i+2] = gray;
        }}
        
        ashCloud.geometry.attributes.position.needsUpdate = true;
        ashCloud.geometry.attributes.color.needsUpdate = true;
    }}
    
    // Handle window resize
    function onWindowResize() {{
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;
        
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    }}
    
    // Animation loop - optimized for performance
    function animate() {{
        requestAnimationFrame(animate);
        
        const delta = clock.getDelta();
        const elapsed = clock.getElapsedTime();
        
        // Advance phase progress
        phaseProgress += delta * volcanoData.animation_speed * 0.2;
        if (phaseProgress > 1) phaseProgress = 1;
        
        // Update progress bar
        document.getElementById("phase-progress").style.width = (phaseProgress * 100) + "%";
        
        // Update metrics only every few frames for better performance
        if (Math.floor(elapsed * 10) % 3 === 0) {{
            updateMetricsPanel(currentPhase, phaseProgress);
        }}
        
        // Animate ash cloud when visible - simplified for performance
        if (ashCloud && ashCloud.material.opacity > 0) {{
            // Only animate in medium/high quality
            if (quality !== 'Low') {{
                const positions = ashCloud.geometry.attributes.position.array;
                
                // Reduce number of updates for better performance
                const updateFactor = quality === 'Medium' ? 6 : 3;
                
                for (let i = 0; i < positions.length; i += 3 * updateFactor) {{
                    // Simple vertical movement
                    positions[i+1] += 0.2 * volcanoData.animation_speed;
                    
                    // Reset particles that drift too far
                    if (positions[i+1] > getSummitHeight() + 300) {{
                        positions[i+1] = getSummitHeight() + 20;
                    }}
                }}
                
                ashCloud.geometry.attributes.position.needsUpdate = true;
            }}
        }}
        
        // Animate lava flows - reduced for performance
        if (quality !== 'Low' && Math.floor(elapsed * 2) % 2 === 0) {{
            lavaFlows.forEach(flow => {{
                if (flow.visible) {{
                    // Pulse lava glow
                    flow.material.emissiveIntensity = 0.5 + Math.sin(elapsed * 3) * 0.2;
                }}
            }});
        }}
        
        // Animate magma light
        const magmaLight = scene.children.find(child => 
            child instanceof THREE.PointLight && child.color.r > 0.5 && child.color.g < 0.5);
        if (magmaLight && magmaLight.intensity > 0) {{
            magmaLight.intensity *= 0.9 + Math.sin(elapsed * 3) * 0.1;
        }}
        
        renderer.render(scene, camera);
    }}
    
    // Simplified CSG implementation for geometric operations
    class CSG {{
        static fromMesh(mesh) {{
            return new CSG(mesh);
        }}
        
        constructor(mesh) {{
            this.mesh = mesh.clone();
        }}
        
        subtract(otherCSG) {{
            // Simplified for this example
            return this;
        }}
        
        static toMesh(csg, matrix) {{
            return csg.mesh;
        }}
    }}
    
    // Start the visualization once DOM is ready
    init();
    
    // Listen for phase button clicks from Streamlit
    const buttons = document.querySelectorAll(".stButton button");
    buttons.forEach(button => {{
        button.addEventListener("click", event => {{
            // Update is handled through the hidden input
        }});
    }});
    
    // Check for phase changes - reduced frequency for performance
    setInterval(() => {{
        const newPhase = document.getElementById("selected_phase").value;
        if (newPhase && newPhase !== currentPhase) {{
            updatePhase(newPhase);
        }}
    }}, 1000); // Check less frequently
    </script>
    """
    
    # Display the script for the 3D visualization
    st.components.v1.html(threejs_html, height=900)
    
    # Scientific explanation section
    with st.expander("Scientific Background", expanded=False):
        st.markdown(f"""
        ## Scientific Information: {volcano_type.replace('_', ' ').title()} Volcanoes
        
        {VOLCANO_TYPES[volcano_type]['description']}
        
        ### Eruption Sequence
        
        The 3D model shows the scientifically accurate progression of a volcanic eruption:
        
        1. **Magma Buildup Phase**: Magma accumulates in the chamber, causing ground deformation as pressure increases.
        
        2. **Seismic Activity Phase**: Increased pressure leads to rock fracturing, creating earthquake swarms.
        
        3. **Initial Eruption Phase**: Magma reaches the surface, often beginning with steam emissions and small explosions.
        
        4. **Main Eruption Phase**: Peak activity with characteristics specific to this volcano type:
           - {'Low viscosity lava flows, minimal explosivity' if volcano_type == 'shield' else ''}
           - {'Explosive eruptions with ash columns and pyroclastic flows' if volcano_type == 'stratovolcano' else ''}
           - {'Massive eruption potential with caldera collapse' if volcano_type == 'caldera' else ''}
           - {'Strombolian explosions and cinder/ash ejection' if volcano_type == 'cinder_cone' else ''}
           - {'Slow extrusion of extremely viscous lava forming a dome' if volcano_type == 'lava_dome' else ''}
        
        5. **Waning Phase**: Declining activity as magma supply diminishes.
        
        ### Magma Plumbing System
        
        The visualization shows the complex internal structure of the volcano:
        
        - **Deep Magma Reservoir**: Located in the lower crust (10-30 km depth)
        - **Shallow Magma Chamber**: Located 2-5 km beneath the volcano
        - **Conduit System**: Pathways connecting chambers to the surface
        - **Dikes and Sills**: Lateral intrusions of magma
        
        ### Technical Details
        
        This model incorporates scientific data on:
        
        - Magma viscosity: {volcano_params.get('lava_viscosity', 0.5)*100:.0f}% (scale where 100% = highest viscosity)
        - Typical eruption temperature: {volcano_params.get('lava_temperature', 1000)}°C
        - Ash production potential: {volcano_params.get('ash_production', 0.5)*100:.0f}% (relative scale)
        
        ### References
        
        1. Global Volcanism Program, Smithsonian Institution
        2. USGS Volcano Hazards Program
        3. Sigmundsson, F. (2016). New insights into magma plumbing along rift systems
        4. Cashman, K. V., & Sparks, R. S. J. (2013). How volcanoes work
        """)
    
if __name__ == "__main__":
    app()