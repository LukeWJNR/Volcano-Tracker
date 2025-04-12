"""
Data file containing known glaciated volcanoes or volcanoes affected by glacial melting,
plus special cases of climate-related volcanic activity such as the Mayotte submarine volcano.

This data is used in the Climate & Volcanoes page to show the connection between 
glacial retreat, climate change, and volcanic activity.

Data sourced from Global Volcanism Program (GVP) and enhanced with climate impact analysis.
"""

# Volcanoes affected by glacial melting, derived from GVP data
GLACIAL_VOLCANOES = [
    # High-risk, well-documented glaciated volcanoes
    {
        "name": "Grímsvötn",
        "country": "Iceland",
        "lat": 64.41,
        "lng": -17.32,
        "elevation": 1725,
        "notes": "Beneath Vatnajökull glacier, erupted multiple times since 1996. Frequent subglacial eruptions.",
        "risk_level": "High"
    },
    {
        "name": "Katla",
        "country": "Iceland",
        "lat": 63.63,
        "lng": -19.05,
        "elevation": 1512,
        "notes": "Subglacial volcano, known for explosive eruptions under Mýrdalsjökull. Overdue for eruption.",
        "risk_level": "High"
    },
    {
        "name": "Eyjafjallajökull",
        "country": "Iceland",
        "lat": 63.63,
        "lng": -19.62,
        "elevation": 1651,
        "notes": "Famous for 2010 eruption that disrupted air travel across Europe. Closely linked to Katla activity.",
        "risk_level": "High"
    },
    {
        "name": "Mount Rainier",
        "country": "United States",
        "lat": 46.85,
        "lng": -121.76,
        "elevation": 4392,
        "notes": "Heavily glaciated stratovolcano near Seattle. Risk of lahars from glacier melt threatens populated areas.",
        "risk_level": "High"
    },
    {
        "name": "Nevado del Ruiz",
        "country": "Colombia",
        "lat": 4.89,
        "lng": -75.32,
        "elevation": 5321,
        "notes": "Glacier melting contributed to deadly lahars in 1985 disaster that killed over 23,000 people.",
        "risk_level": "High"
    },
    {
        "name": "Ruapehu",
        "country": "New Zealand",
        "lat": -39.28,
        "lng": 175.57,
        "elevation": 2797,
        "notes": "Active summit crater lake and glaciers. Frequent eruptions and lahars from melting ice.",
        "risk_level": "High"
    },
    {
        "name": "Öræfajökull",
        "country": "Iceland",
        "lat": 64.0,
        "lng": -16.65,
        "elevation": 2110,
        "notes": "Iceland's highest peak with an ice-filled caldera. Rapid glacier retreat observed since 1990s.",
        "risk_level": "High"
    },
    
    # Medium-risk glaciated volcanoes
    {
        "name": "Mount Spurr",
        "country": "United States",
        "lat": 61.3,
        "lng": -152.25,
        "elevation": 3374,
        "notes": "Glacier-covered stratovolcano in Alaska, last erupted 1992. Shows signs of increasing geothermal activity.",
        "risk_level": "Medium"
    },
    {
        "name": "Sollipulli",
        "country": "Chile",
        "lat": -38.97,
        "lng": -71.52,
        "elevation": 2282,
        "notes": "Ice-filled caldera showing signs of deglaciation and increased thermal activity in recent decades.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Shasta",
        "country": "United States",
        "lat": 41.41,
        "lng": -122.19,
        "elevation": 4322,
        "notes": "Significant glacier loss in recent decades, potentially affecting stability of volcanic edifice.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Baker",
        "country": "United States",
        "lat": 48.78,
        "lng": -121.81,
        "elevation": 3286,
        "notes": "Glaciers retreating rapidly, increased fumarole activity noted since 1975.",
        "risk_level": "Medium"
    },
    {
        "name": "Cotopaxi",
        "country": "Ecuador",
        "lat": -0.677,
        "lng": -78.436,
        "elevation": 5911,
        "notes": "One of the world's highest active volcanoes with extensive glacier cover. Recent eruptions accelerating ice loss.",
        "risk_level": "Medium"
    },
    {
        "name": "Villarrica",
        "country": "Chile",
        "lat": -39.42,
        "lng": -71.93,
        "elevation": 2847,
        "notes": "Very active volcano with glacier cap. Frequent eruptions cause rapid ice melt and lahar risk.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Redoubt",
        "country": "United States",
        "lat": 60.485,
        "lng": -152.742,
        "elevation": 3108,
        "notes": "Glacier-covered Alaska volcano. 2009 eruption caused significant melting and mudflows.",
        "risk_level": "Medium"
    },
    {
        "name": "Veniaminof",
        "country": "United States",
        "lat": 56.17,
        "lng": -159.38,
        "elevation": 2507,
        "notes": "Large Alaskan volcano with ice-filled caldera. Recent eruptions have melted significant portions of ice cap.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Hood",
        "country": "United States",
        "lat": 45.374,
        "lng": -121.695,
        "elevation": 3426,
        "notes": "Oregon's highest peak with 12 named glaciers. All glaciers in retreat, exposing unstable volcanic material.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount St. Helens",
        "country": "United States",
        "lat": 46.2,
        "lng": -122.18,
        "elevation": 2549,
        "notes": "Lost most glaciers in 1980 eruption. New glacier forming in crater, but ongoing volcanic activity threatens stability.",
        "risk_level": "Medium"
    },
    {
        "name": "Popocatépetl",
        "country": "Mexico",
        "lat": 19.023,
        "lng": -98.622,
        "elevation": 5426,
        "notes": "Small glaciers on summit, dramatically retreating due to climate change and frequent eruptions.",
        "risk_level": "Medium"
    },
    
    # Low-risk or research-focused glaciated volcanoes
    {
        "name": "Mount Erebus",
        "country": "Antarctica",
        "lat": -77.53,
        "lng": 167.16,
        "elevation": 3794,
        "notes": "World's southernmost active volcano with permanent glacial cover. Important for climate-volcano research.",
        "risk_level": "Low"
    },
    {
        "name": "Deception Island",
        "country": "Antarctica",
        "lat": -62.97,
        "lng": -60.65,
        "elevation": 576,
        "notes": "Antarctic horseshoe-shaped island with glaciers. Recent volcanic unrest being monitored by researchers.",
        "risk_level": "Low"
    },
    {
        "name": "Mount Melbourne",
        "country": "Antarctica",
        "lat": -74.35,
        "lng": 164.7,
        "elevation": 2732,
        "notes": "Active Antarctic volcano entirely covered by ice. Provides valuable data on subglacial volcanic processes.",
        "risk_level": "Low"
    },
    
    # Special cases: Climate-related volcanism not directly involving glaciers
    {
        "name": "Mayotte Submarine Volcano",
        "country": "France (Mayotte)",
        "lat": -12.84,
        "lng": 45.42,
        "elevation": -3000,
        "notes": "Discovered in 2018-2019 after seismic swarm. Research suggests link between submarine volcanism and climate-related oceanic changes. Largest underwater eruption ever documented.",
        "risk_level": "Medium"
    }
]

def get_glacial_volcanoes():
    """Return the list of glacial volcanoes."""
    return GLACIAL_VOLCANOES