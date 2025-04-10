import requests
import pandas as pd
from datetime import datetime

# USGS Volcano API endpoints
USGS_VOLCANO_API_URL = "https://volcano.si.edu/api/v1/volcanoes"
USGS_VOLCANO_DETAILS_URL = "https://volcano.si.edu/api/v1/volcano/{volcano_id}"

def get_volcano_data():
    """
    Fetch volcano data from the USGS API
    Returns a pandas DataFrame with volcano information
    """
    try:
        response = requests.get(USGS_VOLCANO_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform data into a pandas DataFrame
        volcano_list = []
        
        for volcano in data:
            # Extract relevant information
            volcano_info = {
                'id': volcano.get('id', ''),
                'name': volcano.get('name', 'Unknown'),
                'country': volcano.get('country', 'Unknown'),
                'region': volcano.get('region', 'Unknown'),
                'latitude': volcano.get('latitude', 0),
                'longitude': volcano.get('longitude', 0),
                'elevation': volcano.get('elevation', 0),
                'type': volcano.get('type', 'Unknown'),
                'last_eruption': volcano.get('last_eruption', ''),
                'alert_level': volcano.get('alert_level', 'Unknown'),
            }
            
            volcano_list.append(volcano_info)
        
        # Create DataFrame
        df = pd.DataFrame(volcano_list)
        
        # If the API doesn't provide alert levels, use this mock data for demonstration
        # In a real application, we would use actual alert data from a proper source
        if 'alert_level' not in df.columns or df['alert_level'].isna().all():
            # Sample alert levels - in real application this would come from the API
            df['alert_level'] = 'Unknown'
        
        return df
    
    except requests.exceptions.RequestException as e:
        # Since we need to handle this gracefully on the frontend,
        # we'll raise a more informative exception
        raise Exception(f"Failed to fetch volcano data: {str(e)}")

def get_volcano_details(volcano_id):
    """
    Fetch detailed information about a specific volcano
    
    Args:
        volcano_id (str): The ID of the volcano to fetch details for
        
    Returns:
        dict: Detailed information about the volcano
    """
    try:
        url = USGS_VOLCANO_DETAILS_URL.format(volcano_id=volcano_id)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant details
        details = {
            'description': data.get('description', ''),
            'activity': data.get('activity', ''),
            'monitoring': data.get('monitoring', ''),
            'hazard_info': data.get('hazard_info', '')
        }
        
        return details
    
    except requests.exceptions.RequestException as e:
        # Since we need to handle this gracefully on the frontend,
        # we'll raise a more informative exception
        raise Exception(f"Failed to fetch volcano details: {str(e)}")

# Function to handle the case when the USGS API is not working as expected
def get_fallback_volcano_data():
    """
    Fallback function to provide a minimal dataset when the API is unavailable
    This is only used in case of complete API failure
    """
    # In a real application, this could fetch data from a backup source or cache
    # For now, we'll return an empty DataFrame with the expected structure
    return pd.DataFrame(columns=[
        'id', 'name', 'country', 'region', 'latitude', 'longitude',
        'elevation', 'type', 'last_eruption', 'alert_level'
    ])
