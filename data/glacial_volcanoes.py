"""
Data file containing known glaciated volcanoes or volcanoes affected by glacial melting.
This data is used in the Climate & Volcanoes page to show the connection between 
glacial retreat and volcanic activity.
"""

# Volcanoes affected by glacial melting
GLACIAL_VOLCANOES = [
    {
        "name": "Grímsvötn",
        "country": "Iceland",
        "lat": 64.41,
        "lng": -17.32,
        "elevation": 1725,
        "notes": "Beneath Vatnajökull glacier, erupted multiple times since 1996.",
        "risk_level": "High"
    },
    {
        "name": "Katla",
        "country": "Iceland",
        "lat": 63.63,
        "lng": -19.05,
        "elevation": 1512,
        "notes": "Subglacial volcano, known for explosive eruptions under Mýrdalsjökull.",
        "risk_level": "High"
    },
    {
        "name": "Eyjafjallajökull",
        "country": "Iceland",
        "lat": 63.63,
        "lng": -19.62,
        "elevation": 1651,
        "notes": "Famous for 2010 eruption that disrupted air travel across Europe.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Spurr",
        "country": "Alaska, USA",
        "lat": 61.3,
        "lng": -152.25,
        "elevation": 3374,
        "notes": "Glacier-covered stratovolcano, last erupted 1992.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Erebus",
        "country": "Antarctica",
        "lat": -77.53,
        "lng": 167.16,
        "elevation": 3794,
        "notes": "World's southernmost active volcano, partly glaciated.",
        "risk_level": "Low"
    },
    {
        "name": "Sollipulli",
        "country": "Chile",
        "lat": -38.97,
        "lng": -71.52,
        "elevation": 2282,
        "notes": "Ice-filled caldera showing signs of deglaciation and increased thermal activity.",
        "risk_level": "Medium"
    },
    {
        "name": "Mount Rainier",
        "country": "Washington, USA",
        "lat": 46.85,
        "lng": -121.76,
        "elevation": 4392,
        "notes": "Heavily glaciated stratovolcano near Seattle, considered very high risk.",
        "risk_level": "High"
    },
    {
        "name": "Mount Shasta",
        "country": "California, USA",
        "lat": 41.41,
        "lng": -122.19,
        "elevation": 4322,
        "notes": "Significant glacier loss in recent decades, potentially affecting stability.",
        "risk_level": "Medium"
    },
    {
        "name": "Nevado del Ruiz",
        "country": "Colombia",
        "lat": 4.89,
        "lng": -75.32,
        "elevation": 5321,
        "notes": "Glacier melting contributed to deadly lahars in 1985 disaster.",
        "risk_level": "High"
    },
    {
        "name": "Mount Baker",
        "country": "Washington, USA",
        "lat": 48.78,
        "lng": -121.81,
        "elevation": 3286,
        "notes": "Glaciers retreating rapidly, increased fumarole activity noted since 1975.",
        "risk_level": "Medium"
    }
]

def get_glacial_volcanoes():
    """Return the list of glacial volcanoes."""
    return GLACIAL_VOLCANOES