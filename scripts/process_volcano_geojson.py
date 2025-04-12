#!/usr/bin/env python3
"""
Script to process the GVP volcano list GeoJSON file and extract glacial volcanoes.
This will enhance our existing glacial_volcanoes.py data with more complete information.
"""

import json
import os
import sys
from typing import Dict, List, Any

# Known glaciated volcanoes by name - we'll match these against the GeoJSON data
# These are volcanoes known to be affected by glacial melting or have glaciers on them
KNOWN_GLACIATED_VOLCANOES = [
    "Grímsvötn", "Katla", "Eyjafjallajökull", "Mount Spurr", "Mount Erebus", 
    "Sollipulli", "Mount Rainier", "Mount Shasta", "Nevado del Ruiz", "Mount Baker",
    "Vatnajökull", "Mount Redoubt", "Cotopaxi", "Tungurahua", "Villarrica",
    "Ruapehu", "Popocatépetl", "Mount St. Helens", "Mount Hood", "Öræfajökull"
]

# Additional potential glacial volcanoes based on location (Iceland, Alaska, Andes, etc.)
POTENTIAL_GLACIAL_REGIONS = [
    "Iceland", "Antarctica", "Alaska", "Washington", "Oregon", "Andes"
]

def process_geojson_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Process the GeoJSON file to extract glaciated volcanoes
    
    Args:
        filepath: Path to the GeoJSON file
        
    Returns:
        List of dictionaries containing glacial volcano data
    """
    print(f"Processing GeoJSON file: {filepath}")
    
    # Check if file exists
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist")
        return []
    
    # Read the GeoJSON file
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not parse {filepath} as JSON")
        return []
    
    # Extract features
    features = data.get('features', [])
    print(f"Found {len(features)} volcano features in the GeoJSON")
    
    # Extract glaciated volcanoes
    glacial_volcanoes = []
    
    for feature in features:
        properties = feature.get('properties', {})
        volcano_name = properties.get('Volcano_Name', '')
        country = properties.get('Country', '')
        subregion = properties.get('Subregion', '')
        elevation = properties.get('Elevation__m_', 0)
        lat = properties.get('Latitude', 0)
        lng = properties.get('Longitude', 0)
        
        # Check if this is a known glaciated volcano
        is_glaciated = False
        risk_level = "Medium"
        notes = ""
        
        # Check by name
        for name in KNOWN_GLACIATED_VOLCANOES:
            if name.lower() in volcano_name.lower():
                is_glaciated = True
                risk_level = "High"
                notes = "Known to be affected by glacial melting"
                break
        
        # If not already identified, check by region
        if not is_glaciated:
            for region in POTENTIAL_GLACIAL_REGIONS:
                if region.lower() in country.lower() or region.lower() in subregion.lower():
                    # For volcanoes in potentially glaciated regions, require high elevation
                    if elevation > 2000:  # Typically glaciers form at high elevations
                        is_glaciated = True
                        risk_level = "Medium"
                        notes = f"High-elevation volcano in {region}, likely affected by glacial dynamics"
                        break
        
        # Skip non-glaciated volcanoes
        if not is_glaciated:
            continue
        
        # Add to our list
        glacial_volcanoes.append({
            "name": volcano_name,
            "country": country,
            "lat": lat,
            "lng": lng,
            "elevation": elevation,
            "risk_level": risk_level,
            "notes": notes
        })
    
    print(f"Identified {len(glacial_volcanoes)} glaciated volcanoes")
    return glacial_volcanoes

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python process_volcano_geojson.py <geojson_file>")
        sys.exit(1)
    
    # Get the filepath
    filepath = sys.argv[1]
    
    # Process the file
    glacial_volcanoes = process_geojson_file(filepath)
    
    # Print the results as Python code
    print("\n# Python code for glacial_volcanoes.py:")
    print("GLACIAL_VOLCANOES = [")
    for volcano in glacial_volcanoes:
        print(f"    {{")
        print(f"        \"name\": \"{volcano['name']}\",")
        print(f"        \"country\": \"{volcano['country']}\",")
        print(f"        \"lat\": {volcano['lat']},")
        print(f"        \"lng\": {volcano['lng']},")
        print(f"        \"elevation\": {volcano['elevation']},")
        print(f"        \"risk_level\": \"{volcano['risk_level']}\",")
        print(f"        \"notes\": \"{volcano['notes']}\"")
        print(f"    }},")
    print("]")

if __name__ == "__main__":
    main()