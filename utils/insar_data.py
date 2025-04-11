"""
Utilities for handling InSAR satellite data links
"""
import json
import os
import requests
from typing import Dict, List, Optional, Any


def fetch_insar_links() -> List[Dict[str, Any]]:
    """
    Fetch InSAR links from GitHub repository or use cached data
    
    Returns:
        List[Dict[str, Any]]: List of InSAR links with volcano names and URLs
    """
    # First, try to load from GitHub
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/openvolcano/data/main/insar_links.json",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Could not fetch InSAR links from GitHub: {e}")
    
    # If GitHub fails, use local fallback data
    return [
        {
            "name": "Mauna Loa",
            "insarUrl": "https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=19.5&lng=-155.6"
        },
        {
            "name": "Etna",
            "insarUrl": "https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=37.7&lng=15.0"
        },
        {
            "name": "Mount Erebus",
            "insarUrl": "https://apps.sentinel-hub.com/eo-browser/?zoom=6&lat=-77.5&lng=167.2"
        },
        {
            "name": "Mount St. Helens",
            "insarUrl": "https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/applications/land-monitoring/geological-hazards"
        },
        {
            "name": "Kilauea",
            "insarUrl": "https://volcano.si.edu/volcano.cfm?vn=332010"
        }
    ]


def get_insar_url_for_volcano(volcano_name: str) -> Optional[str]:
    """
    Get the InSAR URL for a specific volcano by name
    
    Args:
        volcano_name (str): Name of the volcano
        
    Returns:
        Optional[str]: URL to InSAR data if available, None otherwise
    """
    insar_links = fetch_insar_links()
    
    # Find a match by name
    match = next((link for link in insar_links if link["name"] == volcano_name), None)
    
    if match and "insarUrl" in match:
        return match["insarUrl"]
    
    return None


def generate_sentinel_hub_url(latitude: float, longitude: float) -> str:
    """
    Generate a URL to Sentinel Hub for the given coordinates
    
    Args:
        latitude (float): Latitude of the volcano
        longitude (float): Longitude of the volcano
        
    Returns:
        str: URL to Sentinel Hub
    """
    return (
        f"https://www.sentinel-hub.com/explore/sentinelplayground/"
        f"?zoom=12&lat={latitude}&lng={longitude}"
        f"&preset=1_NATURAL_COLOR&layers=B01,B02,B03"
        f"&maxcc=20&gain=1.0&gamma=1.0&time=2021-06-01%7C2021-12-01"
        f"&atmFilter=&showDates=false"
    )


def generate_copernicus_url(latitude: float, longitude: float) -> str:
    """
    Generate a URL to ESA Copernicus for the given coordinates
    
    Args:
        latitude (float): Latitude of the volcano
        longitude (float): Longitude of the volcano
        
    Returns:
        str: URL to ESA Copernicus
    """
    return (
        f"https://scihub.copernicus.eu/dhus/#/home"
        f"?latitude={latitude}&longitude={longitude}&zoom=12"
    )