import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

from utils.volcano_types import Volcano, VolcanoDict
from utils.insar_data import get_insar_url_for_volcano
from data.volcano_data import VOLCANO_DATA

def get_known_volcano_data() -> pd.DataFrame:
    """
    Get volcano data from our known dataset
    
    Returns:
        pd.DataFrame: DataFrame containing volcano information
    """
    # Add InSAR URLs to data
    volcano_list = []
    for volcano in VOLCANO_DATA:
        # Create a copy to avoid modifying the original data
        volcano_copy = volcano.copy()
        
        # Add InSAR URL if available
        insar_url = get_insar_url_for_volcano(volcano_copy['name'])
        if insar_url:
            volcano_copy['insar_url'] = insar_url
            
        volcano_list.append(volcano_copy)
    
    # Convert to DataFrame
    df = pd.DataFrame(volcano_list)
    return df


def get_volcano_data() -> pd.DataFrame:
    """
    Fetch volcano data from the source
    Returns a pandas DataFrame with volcano information
    
    Note: We're using a data source that's stored locally since the API has changed.
    In a production environment, you would update to use the correct API endpoint.
    """
    # Get base volcano data
    volcano_df = get_known_volcano_data()
    
    # Add monitoring indicators
    # For a real implementation, you would check the actual availability of the data
    # For this demo, we're adding indicators for some well-known volcanoes
    well_monitored_volcanoes = [
        "Mauna Loa", "Kilauea", "Mount St. Helens", "Etna", "Vesuvius", 
        "Krakatau", "Merapi", "Fuji", "Pinatubo", "Cotopaxi",
        # Iceland volcanoes
        "Reykjanes", "Fagradalsfjall", "Krafla", "Askja", "Hekla", 
        "Eyjafjallajökull", "Katla", "Grimsvötn", "Bardarbunga"
    ]
    
    # Add monitoring indicators columns
    volcano_df['has_insar'] = volcano_df['name'].apply(lambda x: x in well_monitored_volcanoes)
    volcano_df['has_so2'] = volcano_df['name'].apply(lambda x: x in well_monitored_volcanoes)
    volcano_df['has_lava'] = volcano_df['name'].apply(lambda x: x in well_monitored_volcanoes)
    volcano_df['wovodat_id'] = volcano_df['name'].apply(lambda x: x if x in well_monitored_volcanoes else None)
    
    return volcano_df

def get_volcano_details(volcano_id: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific volcano, enhanced with monitoring data
    
    Args:
        volcano_id (str): The ID of the volcano to fetch details for
        
    Returns:
        Dict[str, Any]: Detailed information about the volcano
    """
    from utils.wovodat_utils import get_wovodat_volcano_data, get_volcano_monitoring_status
    
    # Search in our local data first
    for volcano in VOLCANO_DATA:
        if volcano['id'] == volcano_id:
            # Add InSAR URL if available
            details = volcano.copy()
            insar_url = get_insar_url_for_volcano(details['name'])
            if insar_url:
                details['insar_url'] = insar_url
                
            # Add monitoring flags
            # For a real implementation, you would check the actual availability of the data
            # For this demo, we're adding indicators for some well-known volcanoes
            well_monitored_volcanoes = [
                "Mauna Loa", "Kilauea", "Mount St. Helens", "Etna", "Vesuvius", 
                "Krakatau", "Merapi", "Fuji", "Pinatubo", "Cotopaxi",
                # Iceland volcanoes
                "Reykjanes", "Fagradalsfjall", "Krafla", "Askja", "Hekla", 
                "Eyjafjallajökull", "Katla", "Grimsvötn", "Bardarbunga"
            ]
            
            details['has_insar'] = details['name'] in well_monitored_volcanoes
            details['has_so2'] = details['name'] in well_monitored_volcanoes
            details['has_lava'] = details['name'] in well_monitored_volcanoes
            
            # Try to get WOVOdat data if available
            try:
                wovodat_data = get_wovodat_volcano_data(details['name'])
                if wovodat_data:
                    details['wovodat_url'] = wovodat_data['wovodat_url']
                    
                    # Get monitoring status
                    monitoring_status = get_volcano_monitoring_status(details['name'])
                    details['monitoring_status'] = monitoring_status['description']
            except Exception as e:
                print(f"Could not fetch WOVOdat data: {str(e)}")
                
            return details
    
    # If not found in local data, return a minimal response
    return {
        'id': volcano_id,
        'name': 'Unknown',
        'description': 'Details not available',
        'activity': 'Unknown',
        'country': 'Unknown',
        'region': 'Unknown',
        'has_insar': False,
        'has_so2': False,
        'has_lava': False
    }

# This code was updated to use a reliable local data source
# instead of depending on the external API which was not available
    
    
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
