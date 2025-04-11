"""
Data file containing known volcano information.
This serves as a fallback when the external API is unavailable.
The data is sourced from reputable sources and formatted to match our application needs.
"""

# List of known volcanoes with their details
VOLCANO_DATA = [
    {
        "id": "mauna_loa",
        "name": "Mauna Loa",
        "country": "United States",
        "region": "Hawaii",
        "latitude": 19.4756,
        "longitude": -155.6054,
        "elevation": 4169,
        "type": "Shield volcano",
        "last_eruption": "2022",
        "alert_level": "Normal",
        "description": "Mauna Loa is the largest active volcano on Earth and one of five volcanoes that form the Island of Hawaii. Mauna Loa has erupted 33 times since its first well-documented historical eruption in 1843.",
        "activity": "Most recent eruption began on November 27, 2022, and ended on December 10, 2022."
    },
    {
        "id": "kilauea",
        "name": "Kilauea",
        "country": "United States",
        "region": "Hawaii",
        "latitude": 19.4069,
        "longitude": -155.2834,
        "elevation": 1222,
        "type": "Shield volcano",
        "last_eruption": "Active",
        "alert_level": "Watch",
        "description": "Kilauea is the youngest and most active volcano on the island of Hawaii. It is a shield volcano, which means it is a gently sloping mountain produced from a large number of generally very fluid lava flows.",
        "activity": "Ongoing eruptions and lava lake activity in the summit crater."
    },
    {
        "id": "mount_st_helens",
        "name": "Mount St. Helens",
        "country": "United States",
        "region": "Washington",
        "latitude": 46.1914,
        "longitude": -122.1956,
        "elevation": 2549,
        "type": "Stratovolcano",
        "last_eruption": "2008",
        "alert_level": "Normal",
        "description": "Mount St. Helens is an active stratovolcano located in Washington State, in the Pacific Northwest region of the United States. It is famous for its catastrophic eruption on May 18, 1980.",
        "activity": "Periodic dome-building eruptions, most recently from 2004 to 2008."
    },
    {
        "id": "etna",
        "name": "Etna",
        "country": "Italy",
        "region": "Sicily",
        "latitude": 37.7510,
        "longitude": 14.9934,
        "elevation": 3329,
        "type": "Stratovolcano",
        "last_eruption": "Active",
        "alert_level": "Advisory",
        "description": "Mount Etna is an active stratovolcano on the east coast of Sicily, Italy. It is the highest active volcano in Europe outside the Caucasus and the highest peak in Italy south of the Alps.",
        "activity": "Frequent eruptions and explosive events, with ongoing activity."
    },
    {
        "id": "mount_fuji",
        "name": "Mount Fuji",
        "country": "Japan",
        "region": "Honshu",
        "latitude": 35.3606,
        "longitude": 138.7274,
        "elevation": 3776,
        "type": "Stratovolcano",
        "last_eruption": "1707-1708",
        "alert_level": "Normal",
        "description": "Mount Fuji is the highest mountain in Japan, standing at 3,776 meters. It is an active stratovolcano that last erupted in 1707–1708. Mount Fuji is one of Japan's 'Three Holy Mountains'.",
        "activity": "No recent activity, but considered active and potentially hazardous."
    },
    {
        "id": "mount_vesuvius",
        "name": "Mount Vesuvius",
        "country": "Italy",
        "region": "Naples",
        "latitude": 40.8216,
        "longitude": 14.4283,
        "elevation": 1281,
        "type": "Stratovolcano",
        "last_eruption": "1944",
        "alert_level": "Normal",
        "description": "Mount Vesuvius is a somma-stratovolcano located on the Gulf of Naples, about 9 km east of Naples. It is known for its eruption in 79 CE that led to the burying and destruction of the Roman cities of Pompeii and Herculaneum.",
        "activity": "No current activity, but closely monitored due to population density in the area."
    },
    {
        "id": "mount_erebus",
        "name": "Mount Erebus",
        "country": "Antarctica",
        "region": "Ross Island",
        "latitude": -77.5321,
        "longitude": 167.1665,
        "elevation": 3794,
        "type": "Stratovolcano",
        "last_eruption": "Active",
        "alert_level": "Normal",
        "description": "Mount Erebus is the second-highest volcano in Antarctica and the southernmost active volcano on Earth. It is the 6th-highest ultra mountain on an island.",
        "activity": "Persistent lava lake activity and minor explosive eruptions."
    },
    {
        "id": "yellowstone_caldera",
        "name": "Yellowstone Caldera",
        "country": "United States",
        "region": "Wyoming",
        "latitude": 44.4280,
        "longitude": -110.5885,
        "elevation": 2805,
        "type": "Caldera",
        "last_eruption": "70,000 years ago",
        "alert_level": "Normal",
        "description": "The Yellowstone Caldera is a volcanic caldera and supervolcano in Yellowstone National Park in the Western United States. The caldera is located in the northwest corner of Wyoming.",
        "activity": "Hydrothermal features, continuous ground deformation, and seismic activity."
    },
    {
        "id": "krakatoa",
        "name": "Krakatoa",
        "country": "Indonesia",
        "region": "Sunda Strait",
        "latitude": -6.1018,
        "longitude": 105.4233,
        "elevation": 813,
        "type": "Caldera",
        "last_eruption": "2020",
        "alert_level": "Watch",
        "description": "Krakatoa is a caldera in the Sunda Strait between the islands of Java and Sumatra. It is famous for its catastrophic eruption in 1883, which was one of the deadliest and most destructive volcanic events in recorded history.",
        "activity": "Continuing dome growth and explosive activity."
    },
    {
        "id": "popocatepetl",
        "name": "Popocatépetl",
        "country": "Mexico",
        "region": "Central Mexico",
        "latitude": 19.0223,
        "longitude": -98.6275,
        "elevation": 5426,
        "type": "Stratovolcano",
        "last_eruption": "Active",
        "alert_level": "Yellow Phase 2",
        "description": "Popocatépetl is an active stratovolcano located in the states of Puebla, Mexico, and Morelos, in Central Mexico. It is the second-highest peak in Mexico after Citlaltépetl.",
        "activity": "Frequent ash emissions and occasional explosive events."
    }
]