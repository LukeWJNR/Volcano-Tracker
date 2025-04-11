"""
Web scraping utilities for gathering volcanic monitoring data from various sources
"""

import requests
import json
import pandas as pd
from datetime import datetime
import trafilatura
from typing import Dict, List, Optional, Any, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_website_text_content(url: str) -> str:
    """
    Extract the main text content of a website.
    
    Args:
        url (str): URL to scrape
        
    Returns:
        str: Extracted text content
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text if text else "No content extracted"
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return f"Error: {str(e)}"

def get_so2_data() -> pd.DataFrame:
    """
    Fetch the latest SO2 data from NASA FIRMS (Fire Information for Resource Management System).
    
    Returns:
        pd.DataFrame: DataFrame containing SO2 emission data
    """
    try:
        # NASA FIRMS SO2 data API
        url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/8a74b08c88ddbb5c4a27a1a2d25d4ae0/VIIRS_SNPP_NRT/world/1"
        response = requests.get(url)
        
        if response.status_code == 200:
            # Save the CSV data to a temporary file
            with open('temp_so2_data.csv', 'w') as f:
                f.write(response.text)
            
            # Load the CSV data into a DataFrame
            so2_df = pd.read_csv('temp_so2_data.csv')
            
            # Filter for volcanic sources (this is a simplification)
            # In reality, we'd need more sophisticated filtering to separate volcanic SO2 from other sources
            volcanic_so2 = so2_df[so2_df['confidence'] > 80]  # High confidence detections
            
            return volcanic_so2
        else:
            logger.warning(f"Failed to fetch SO2 data: {response.status_code}")
            return pd.DataFrame()  # Return empty DataFrame on failure
    except Exception as e:
        logger.error(f"Error fetching SO2 data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_volcanic_ash_data() -> pd.DataFrame:
    """
    Fetch the latest volcanic ash advisory data from VAAC (Volcanic Ash Advisory Centers).
    
    Returns:
        pd.DataFrame: DataFrame containing volcanic ash advisory data
    """
    try:
        # Fetch data from Washington VAAC (example)
        url = "https://www.ssd.noaa.gov/VAAC/vaac-list.json"
        response = requests.get(url)
        
        if response.status_code == 200:
            vaac_data = response.json()
            
            # Convert to DataFrame
            ash_data = []
            for advisory in vaac_data:
                ash_data.append({
                    'volcano_name': advisory.get('volcano', 'Unknown'),
                    'latitude': advisory.get('lat'),
                    'longitude': advisory.get('lon'),
                    'advisory_time': advisory.get('advisoryTime'),
                    'ash_height_ft': advisory.get('ashHeight'),
                    'ash_direction': advisory.get('ashDirection'),
                    'source': advisory.get('source', 'VAAC')
                })
            
            ash_df = pd.DataFrame(ash_data)
            return ash_df
        else:
            logger.warning(f"Failed to fetch volcanic ash data: {response.status_code}")
            return pd.DataFrame()  # Return empty DataFrame on failure
    except Exception as e:
        logger.error(f"Error fetching volcanic ash data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_radon_data() -> pd.DataFrame:
    """
    Fetch radon gas measurement data from monitoring stations near volcanic areas.
    Note: This is a placeholder - real implementation would connect to authorized radon monitoring APIs.
    
    Returns:
        pd.DataFrame: DataFrame containing radon measurement data
    """
    try:
        # For a real implementation, we would fetch from an actual radon monitoring network API
        # For example: EPA RadNet or similar national monitoring networks
        
        # Since there isn't a single public API for global radon data specifically for volcanoes,
        # we would need proper authorization to access such specialized monitoring data
        
        logger.info("To implement radon data monitoring, we need access to appropriate monitoring APIs")
        
        # Return a placeholder empty DataFrame for now
        return pd.DataFrame(columns=[
            'station_id', 'volcano_name', 'latitude', 'longitude', 
            'radon_level_bq_m3', 'measurement_time', 'source'
        ])
    except Exception as e:
        logger.error(f"Error fetching radon data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_wms_capabilities(wms_url: str) -> Dict:
    """
    Get the capabilities of a WMS (Web Map Service) to discover available layers.
    
    Args:
        wms_url (str): Base URL of the WMS service
        
    Returns:
        Dict: Dictionary containing WMS capabilities information
    """
    try:
        # Add GetCapabilities request to the URL
        capabilities_url = f"{wms_url}?service=WMS&request=GetCapabilities"
        response = requests.get(capabilities_url)
        
        if response.status_code == 200:
            # Parse the XML response
            # For production use, we would use a proper XML parser like ElementTree
            return {"status": "success", "content": response.text}
        else:
            logger.warning(f"Failed to fetch WMS capabilities: {response.status_code}")
            return {"status": "error", "message": f"HTTP error {response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching WMS capabilities: {str(e)}")
        return {"status": "error", "message": str(e)}