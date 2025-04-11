import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

from utils.volcano_types import Volcano, VolcanoDict
from utils.insar_data import get_insar_url_for_volcano

# USGS Volcano API endpoints
# USGS_VOLCANO_API_URL = "https://volcano.si.edu/api/v1/volcanoes"  # Original URL (not working)
USGS_VOLCANO_API_URL = "https://www.usgs.gov/programs/VHP/volcano-data" 
USGS_VOLCANO_DETAILS_URL = "https://www.usgs.gov/programs/VHP/volcano/{volcano_id}"

def get_volcano_data() -> pd.DataFrame:
    """
    Fetch volcano data from the source
    Returns a pandas DataFrame with volcano information
    
    Note: We're using a data source that's stored locally since the API has changed.
    In a production environment, you would update to use the correct API endpoint.
    """
    try:
        # Try to fetch from API first
        response = requests.get(USGS_VOLCANO_API_URL, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                # Process API data as before
                # (this part would be updated if the API is working)
            except Exception:
                # If JSON parsing fails, fall back to local data
                return get_known_volcano_data()
        else:
            # If API call failed, use known volcano data
            return get_known_volcano_data()
            
    except requests.exceptions.RequestException:
        # Use the known volcano data
        return get_known_volcano_data()

def get_volcano_details(volcano_id: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific volcano
    
    Args:
        volcano_id (str): The ID of the volcano to fetch details for
        
    Returns:
        Dict[str, Any]: Detailed information about the volcano
    """
    try:
        url = USGS_VOLCANO_DETAILS_URL.format(volcano_id=volcano_id)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant details
        details = {
            'id': volcano_id,
            'description': data.get('description', ''),
            'activity': data.get('activity', ''),
            'monitoring': data.get('monitoring', ''),
            'hazard_info': data.get('hazard_info', ''),
            # Look for additional fields that match our type definition
            'name': data.get('name', ''),
            'country': data.get('country', ''),
            'region': data.get('region', ''),
        }
        
        # Try to get volcano name to check for InSAR data
        volcano_name = data.get('name', '')
        if volcano_name:
            insar_url = get_insar_url_for_volcano(volcano_name)
            if insar_url:
                details['insar_url'] = insar_url
        
        return details
    
    except requests.exceptions.RequestException as e:
        # Since we need to handle this gracefully on the frontend,
        # we'll raise a more informative exception
        raise Exception(f"Failed to fetch volcano details: {str(e)}")

# Function to handle the case when the USGS API is not working as expected
def get_fallback_volcano_data() -> pd.DataFrame:
    """
    Fallback function to provide a minimal dataset when the API is unavailable
    This is only used in case of complete API failure
    """
    # In a real application, this could fetch data from a backup source or cache
    return pd.DataFrame(columns=[
        'id', 'name', 'country', 'region', 'latitude', 'longitude',
        'elevation', 'type', 'last_eruption', 'alert_level', 'insar_url'
    ])
    
    
def get_volcano_by_name(name: str) -> Optional[Volcano]:
    """
    Get a volcano object by name from the current dataset
    
    Args:
        name (str): The name of the volcano to find
        
    Returns:
        Optional[Volcano]: Volcano object if found, None otherwise
    """
    try:
        df = get_volcano_data()
        filtered = df[df['name'] == name]
        
        if not filtered.empty:
            # Convert the first match to a dictionary and then to a Volcano object
            volcano_dict = filtered.iloc[0].to_dict()
            return Volcano.from_dict(volcano_dict)
            
    except Exception as e:
        print(f"Error finding volcano by name: {str(e)}")
        
    return None
