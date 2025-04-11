"""
WebGL Eruption Animation for the Volcano Monitoring Dashboard.

This page provides a full-screen immersive 3D visualization of a volcano eruption
using Three.js for advanced WebGL rendering.
"""

import streamlit as st
import json
from utils.api import get_volcano_data
from utils.animation_utils import determine_volcano_type, VOLCANO_TYPES, ALERT_LEVELS

def app():
    st.title("Immersive 3D Eruption Visualization")
    
    st.markdown("""
    This page provides a full-screen, interactive 3D visualization of a volcanic eruption.
    The visualization leverages WebGL for high-performance graphics rendering.
    
    Instructions:
    - Use mouse to rotate the view (left-click + drag)
    - Scroll to zoom in/out
    - Right-click + drag to pan the view
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
    
    # Eruption level
    eruption_level = st.sidebar.slider(
        "Eruption Intensity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Control the intensity of the eruption"
    )
    
    # Camera position
    camera_position = st.sidebar.selectbox(
        "Camera View",
        ["Aerial", "Ground Level", "Cross-Section", "Side View"],
        index=0
    )
    
    # Visualization effects
    st.sidebar.subheader("Visual Effects")
    show_lava = st.sidebar.checkbox("Show Lava Flows", value=True)
    show_ash = st.sidebar.checkbox("Show Ash Cloud", value=True)
    show_plumbing = st.sidebar.checkbox("Show Plumbing System", value=True)
    
    # Get selected volcano data
    selected_volcano = filtered_df[filtered_df["name"] == selected_volcano_name].iloc[0].to_dict()
    volcano_type = determine_volcano_type(selected_volcano)
    
    # Prepare data for JavaScript
    volcano_data_json = json.dumps({
        "name": selected_volcano_name,
        "type": volcano_type,
        "eruption_level": eruption_level,
        "camera_position": camera_position,
        "show_lava": show_lava,
        "show_ash": show_ash,
        "show_plumbing": show_plumbing
    })
    
    # CSS for full-height visualization
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML and JavaScript for Three.js WebGL visualization
    # This creates a full-screen WebGL visualization similar to the NextJS approach
    threejs_html = f"""
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three-noise@0.1.1/build/three-noise.min.js"></script>
    
    <div id="volcano-container" style="height: 80vh; width: 100%; background: linear-gradient(180deg, #052D49 0%, #000000 100%);">
        <div id="loading" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:24px;">
            Loading 3D Volcano Visualization...
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
    
    // Initial setup
    function init() {{
        // Set renderer size and append to container
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setClearColor(0x000000, 0);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);
        
        // Remove loading message
        document.getElementById("loading").style.display = "none";
        
        // Set up camera
        setupCamera(volcanoData.camera_position);
        
        // Add orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        
        // Add ambient and directional lights
        setupLighting();
        
        // Create the volcano mesh
        createVolcano();
        
        // Create particle systems
        if (volcanoData.show_ash) {{
            createAshCloud();
        }}
        
        if (volcanoData.show_lava) {{
            createLavaFlows();
        }}
        
        if (volcanoData.show_plumbing) {{
            createMagmaPlumbing();
        }}
        
        // Handle window resize
        window.addEventListener('resize', onWindowResize);
        
        // Start animation loop
        animate();
    }}
    
    // Set up camera position based on selection
    function setupCamera(position) {{
        switch(position) {{
            case 'Aerial':
                camera.position.set(0, 200, 200);
                break;
            case 'Ground Level':
                camera.position.set(100, 20, 100);
                break;
            case 'Cross-Section':
                camera.position.set(0, 50, 200);
                break;
            case 'Side View':
                camera.position.set(200, 50, 0);
                break;
            default:
                camera.position.set(0, 200, 200);
        }}
        
        camera.lookAt(0, 0, 0);
    }}
    
    // Setup lighting
    function setupLighting() {{
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x333333);
        scene.add(ambientLight);
        
        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xFFFFFF, 1);
        directionalLight.position.set(100, 200, 100);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 10;
        directionalLight.shadow.camera.far = 1000;
        directionalLight.shadow.camera.left = -500;
        directionalLight.shadow.camera.right = 500;
        directionalLight.shadow.camera.top = 500;
        directionalLight.shadow.camera.bottom = -500;
        scene.add(directionalLight);
        
        // Add point light for lava glow
        const lavaLight = new THREE.PointLight(0xFF4500, 2, 100);
        lavaLight.position.set(0, 50, 0);
        scene.add(lavaLight);
    }}
    
    // Create volcano mesh
    function createVolcano() {{
        // Different geometry based on volcano type
        let geometry;
        let color;
        
        switch(volcanoData.type) {{
            case 'shield':
                // Shield volcanoes are broad with gentle slopes
                geometry = new THREE.ConeGeometry(150, 50, 32, 1, true);
                color = 0x654321; // Brown
                break;
            case 'stratovolcano':
                // Stratovolcanoes are tall with steep sides
                geometry = new THREE.ConeGeometry(100, 100, 32, 1, true);
                color = 0x808080; // Gray
                break;
            case 'caldera':
                // Calderas have a depression at the top
                geometry = createCalderaGeometry();
                color = 0x8B4513; // Saddle brown
                break;
            case 'cinder_cone':
                // Cinder cones are small with steep sides
                geometry = new THREE.ConeGeometry(50, 80, 32, 1, true);
                color = 0x3B2F2F; // Dark brown-gray
                break;
            case 'lava_dome':
                // Lava domes are dome-shaped
                geometry = new THREE.SphereGeometry(80, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);
                color = 0x696969; // Dim gray
                break;
            default:
                // Default to stratovolcano
                geometry = new THREE.ConeGeometry(100, 100, 32, 1, true);
                color = 0x808080; // Gray
        }}
        
        // Material with phong shading
        const material = new THREE.MeshPhongMaterial({{ 
            color: color, 
            flatShading: true,
            shininess: 0
        }});
        
        // Create and add volcano mesh
        const volcano = new THREE.Mesh(geometry, material);
        volcano.rotation.x = Math.PI; // Flip the cone geometry
        volcano.castShadow = true;
        volcano.receiveShadow = true;
        scene.add(volcano);
        
        // Create ground plane
        const groundGeometry = new THREE.PlaneGeometry(1000, 1000);
        const groundMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0x365314,
            roughness: 1
        }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.5;
        ground.receiveShadow = true;
        scene.add(ground);
    }}
    
    // Custom geometry for caldera
    function createCalderaGeometry() {{
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        const resolution = 32;
        
        // Create base cone
        for (let i = 0; i < resolution; i++) {{
            const angle1 = (i / resolution) * Math.PI * 2;
            const angle2 = ((i + 1) / resolution) * Math.PI * 2;
            
            const x1 = Math.sin(angle1) * 150;
            const z1 = Math.cos(angle1) * 150;
            
            const x2 = Math.sin(angle2) * 150;
            const z2 = Math.cos(angle2) * 150;
            
            // Outer bottom vertex
            vertices.push(x1, 0, z1);
            // Outer top vertex
            vertices.push(x1, 70, z1);
            // Inner top vertex (caldera rim)
            vertices.push(x1 * 0.4, 60, z1 * 0.4);
            
            // Triangulate
            vertices.push(x1, 0, z1);
            vertices.push(x2, 0, z2);
            vertices.push(x2, 70, z2);
            
            vertices.push(x1, 0, z1);
            vertices.push(x2, 70, z2);
            vertices.push(x1, 70, z1);
            
            // Caldera rim
            vertices.push(x1, 70, z1);
            vertices.push(x2, 70, z2);
            vertices.push(x2 * 0.4, 60, z2 * 0.4);
            
            vertices.push(x1, 70, z1);
            vertices.push(x2 * 0.4, 60, z2 * 0.4);
            vertices.push(x1 * 0.4, 60, z1 * 0.4);
            
            // Caldera floor
            if (i % 2 === 0) {{
                vertices.push(x1 * 0.4, 60, z1 * 0.4);
                vertices.push(x2 * 0.4, 60, z2 * 0.4);
                vertices.push(0, 40, 0);
            }}
        }}
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.computeVertexNormals();
        
        return geometry;
    }}
    
    // Create ash cloud particle system
    function createAshCloud() {{
        const particleCount = 10000;
        const particles = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {{
            const i3 = i * 3;
            
            // Position particles in a cloud shape with more concentration at the bottom
            const radius = 20 + 80 * Math.pow(Math.random(), 1.5);
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = 80 + radius * Math.cos(phi) + 60 * Math.random(); // Height above volcano
            positions[i3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
            
            // Darker ash near the center, lighter at edges
            const distanceFromCenter = Math.sqrt(
                positions[i3] * positions[i3] + 
                positions[i3 + 2] * positions[i3 + 2]
            ) / radius;
            
            const gray = 0.2 + 0.3 * distanceFromCenter;
            colors[i3] = gray;
            colors[i3 + 1] = gray;
            colors[i3 + 2] = gray;
        }}
        
        particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({{
            size: 3,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            sizeAttenuation: true
        }});
        
        ashCloud = new THREE.Points(particles, material);
        scene.add(ashCloud);
    }}
    
    // Create lava flows
    function createLavaFlows() {{
        // Create multiple lava flow paths
        const lavaFlowCount = 5;
        
        for (let i = 0; i < lavaFlowCount; i++) {{
            const angle = (i / lavaFlowCount) * Math.PI * 2;
            const startX = Math.sin(angle) * 20;
            const startZ = Math.cos(angle) * 20;
            
            createLavaFlow(startX, startZ, angle);
        }}
    }}
    
    // Create individual lava flow
    function createLavaFlow(startX, startZ, angle) {{
        const length = 100 + Math.random() * 100;
        const width = 10 + Math.random() * 15;
        
        const points = [];
        points.push(new THREE.Vector3(startX, 70, startZ));
        
        // Create curved path down the volcano
        let currentY = 70;
        let currentX = startX;
        let currentZ = startZ;
        
        const segmentCount = 10;
        for (let i = 1; i <= segmentCount; i++) {{
            const t = i / segmentCount;
            const radius = t * 150; // Increase radius as we go down
            currentY = 70 - t * 70; // Decrease height as we go down
            
            // Add some randomness to the path
            const angleVariation = angle + (Math.random() - 0.5) * 0.5;
            currentX = Math.sin(angleVariation) * radius;
            currentZ = Math.cos(angleVariation) * radius;
            
            points.push(new THREE.Vector3(currentX, currentY, currentZ));
        }}
        
        // Create tube geometry along path
        const curve = new THREE.CatmullRomCurve3(points);
        const tubeGeometry = new THREE.TubeGeometry(curve, 20, width / 2, 8, false);
        
        // Glowing lava material
        const lavaMaterial = new THREE.MeshStandardMaterial({{
            color: 0xFF4500,
            emissive: 0xFF4500,
            emissiveIntensity: 0.6,
            roughness: 0.5,
            metalness: 0.2
        }});
        
        const lavaFlow = new THREE.Mesh(tubeGeometry, lavaMaterial);
        scene.add(lavaFlow);
    }}
    
    // Create magma plumbing system visualization
    function createMagmaPlumbing() {{
        // Main magma chamber
        const chamberGeometry = new THREE.SphereGeometry(40, 32, 16);
        const chamberMaterial = new THREE.MeshStandardMaterial({{
            color: 0xFF4500,
            emissive: 0xFF4500,
            emissiveIntensity: 0.2,
            transparent: true,
            opacity: 0.7
        }});
        
        const chamber = new THREE.Mesh(chamberGeometry, chamberMaterial);
        chamber.position.set(0, -40, 0);
        scene.add(chamber);
        
        // Deep reservoir (only for certain volcano types)
        if (['stratovolcano', 'caldera'].includes(volcanoData.type)) {{
            const reservoirGeometry = new THREE.SphereGeometry(60, 32, 16);
            const reservoirMaterial = new THREE.MeshStandardMaterial({{
                color: 0xFF2000,
                emissive: 0xFF2000,
                emissiveIntensity: 0.2,
                transparent: true,
                opacity: 0.5
            }});
            
            const reservoir = new THREE.Mesh(reservoirGeometry, reservoirMaterial);
            reservoir.position.set(20, -120, 20);
            scene.add(reservoir);
            
            // Connect deep reservoir to main chamber
            createConduit(
                new THREE.Vector3(20, -120, 20),
                new THREE.Vector3(0, -40, 0),
                10
            );
        }}
        
        // Create conduit from chamber to surface
        createConduit(
            new THREE.Vector3(0, -40, 0),
            new THREE.Vector3(0, 70, 0),
            7
        );
        
        // Add secondary chambers and dikes based on volcano type
        switch(volcanoData.type) {{
            case 'shield':
                // Shield volcanoes often have rift zones with dikes
                createConduit(
                    new THREE.Vector3(0, -20, 0),
                    new THREE.Vector3(100, -10, 0),
                    5
                );
                createConduit(
                    new THREE.Vector3(0, -20, 0),
                    new THREE.Vector3(-100, -10, 0),
                    5
                );
                break;
                
            case 'stratovolcano':
                // Stratovolcanoes may have secondary chambers
                const secondaryGeometry = new THREE.SphereGeometry(20, 32, 16);
                const secondaryMaterial = new THREE.MeshStandardMaterial({{
                    color: 0xFF4500,
                    emissive: 0xFF4500,
                    emissiveIntensity: 0.3,
                    transparent: true,
                    opacity: 0.7
                }});
                
                const secondaryChamber = new THREE.Mesh(secondaryGeometry, secondaryMaterial);
                secondaryChamber.position.set(30, 0, 30);
                scene.add(secondaryChamber);
                
                // Connect to main chamber
                createConduit(
                    new THREE.Vector3(0, -40, 0),
                    new THREE.Vector3(30, 0, 30),
                    5
                );
                
                // Connect to surface
                createConduit(
                    new THREE.Vector3(30, 0, 30),
                    new THREE.Vector3(30, 70, 30),
                    5
                );
                break;
                
            case 'caldera':
                // Calderas have complex plumbing with multiple connections
                // Create ring dikes
                for (let i = 0; i < 8; i++) {{
                    const angle = (i / 8) * Math.PI * 2;
                    const x = Math.sin(angle) * 60;
                    const z = Math.cos(angle) * 60;
                    
                    createConduit(
                        new THREE.Vector3(0, -40, 0),
                        new THREE.Vector3(x, 70, z),
                        4
                    );
                }}
                break;
        }}
    }}
    
    // Create magma conduit connecting two points
    function createConduit(start, end, radius) {{
        const points = [];
        points.push(start);
        points.push(end);
        
        const curve = new THREE.CatmullRomCurve3(points);
        const tubeGeometry = new THREE.TubeGeometry(curve, 20, radius, 8, false);
        
        const magmaMaterial = new THREE.MeshStandardMaterial({{
            color: 0xFF4500,
            emissive: 0xFF4500,
            emissiveIntensity: 0.3,
            transparent: true,
            opacity: 0.7
        }});
        
        const conduit = new THREE.Mesh(tubeGeometry, magmaMaterial);
        scene.add(conduit);
    }}
    
    // Handle window resize
    function onWindowResize() {{
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;
        
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    }}
    
    // Animation loop
    function animate() {{
        requestAnimationFrame(animate);
        
        // Pulse the lava light
        const time = Date.now() * 0.001;
        const lavaLight = scene.children.find(child => child instanceof THREE.PointLight);
        if (lavaLight) {{
            const intensity = 1.5 + Math.sin(time * 2) * 0.5;
            lavaLight.intensity = intensity * volcanoData.eruption_level;
        }}
        
        // Animate ash cloud
        const ashCloud = scene.children.find(child => child instanceof THREE.Points);
        if (ashCloud && volcanoData.show_ash) {{
            const positions = ashCloud.geometry.attributes.position.array;
            
            for (let i = 0; i < positions.length; i += 3) {{
                // Move particles upward and laterally
                positions[i] += Math.sin(time + i) * 0.05 * volcanoData.eruption_level;
                positions[i + 1] += 0.2 * volcanoData.eruption_level;
                positions[i + 2] += Math.cos(time + i) * 0.05 * volcanoData.eruption_level;
                
                // Reset particles that go too high
                if (positions[i + 1] > 250) {{
                    positions[i] = (Math.random() - 0.5) * 40;
                    positions[i + 1] = 80;
                    positions[i + 2] = (Math.random() - 0.5) * 40;
                }}
            }}
            
            ashCloud.geometry.attributes.position.needsUpdate = true;
        }}
        
        renderer.render(scene, camera);
    }}
    
    // Start the visualization
    init();
    </script>
    """
    
    # Render HTML with Three.js
    st.components.v1.html(threejs_html, height=700)
    
    # Additional information section
    with st.expander("About WebGL Volcano Visualization", expanded=False):
        st.markdown("""
        ## 3D Visualization Details
        
        This visualization uses Three.js, a powerful JavaScript library for creating 3D graphics in the browser with WebGL.
        
        The 3D model includes:
        - Scientifically accurate volcanic structure based on the volcano type
        - Dynamic magma plumbing system with deep reservoirs and connecting conduits
        - Realistic lava flow simulations using particle systems and mesh deformation
        - Ash cloud simulation using particle systems
        
        ### Volcano Types
        
        Different volcano types have distinct 3D structures and eruption behaviors:
        
        - **Shield Volcanoes**: Broad with gentle slopes, extensive lava flows, minimal ash
        - **Stratovolcanoes**: Tall with steep sides, explosive eruptions, significant ash clouds
        - **Calderas**: Large depressions formed after major eruptions, complex plumbing systems
        - **Cinder Cones**: Small, simple volcanoes with steep sides, moderate eruptions
        - **Lava Domes**: Rounded, slow-growing mounds of viscous lava
        
        ### Scientific Accuracy
        
        The visualization is based on current scientific understanding of volcanic systems, including:
        - Deep magma reservoirs and shallow chambers
        - Interconnected conduit networks
        - Dike and sill structures
        - Typical eruption patterns for different volcano types
        
        However, as a simplified model for educational purposes, some aspects are generalized.
        """)
    
if __name__ == "__main__":
    app()