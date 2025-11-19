# systems/location_facilities.py
"""
Location Facilities System

Defines what facilities/sub-locations exist at each location and what needs
they can satisfy. This allows NPCs to handle needs contextually at their
current location instead of always going home.

Example:
  "Willow Creek High School" has:
    - cafeteria (can satisfy hunger)
    - restrooms (can satisfy bladder, hygiene)
    - classrooms (satisfy fun via learning, social via peer interaction)
"""

from typing import Dict, List, Set

# ---------------------------------------------------------
# FACILITY DEFINITIONS
# ---------------------------------------------------------

LOCATION_FACILITIES: Dict[str, Dict[str, List[str]]] = {
    # SCHOOLS
    "Willow Creek High School": {
        "cafeteria": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "classrooms": ["fun", "social"],
        "gym": ["fun", "energy"],  # PE class, exercise
    },

    "Willow Creek Pre-School": {
        "snack area": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "play area": ["fun", "social"],
    },

    # DAYCARE
    "Willow Creek Daycare Center": {
        "snack area": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "play area": ["fun", "social"],
    },

    # WORKPLACES - GENERAL
    "Main Street Diner": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "dining area": ["social"],
    },

    "Willow Creek Clinic": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "staff lounge": ["energy", "social"],
    },

    "Willow Creek Police Station": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "locker room": ["hygiene"],
    },

    "Willow Creek Grocery": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Willow Creek Mall - Food Court": {
        "food vendors": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "seating area": ["social"],
    },

    "Willow Creek Mall - Retail Wing": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    # WORKPLACES - SPECIALIZED
    "Willow Creek Naval Base": {
        "mess hall": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "barracks": ["energy"],
    },

    "Offshore Oil Rig": {
        "mess hall": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "bunk room": ["energy"],
    },

    "Engineering Firm": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Hanson Auto Shop": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "County Roads Depot": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Thompson Carpentry": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    # RELIGIOUS
    "Willow Creek Lutheran Church": {
        "fellowship hall": ["hunger", "social"],
        "restrooms": ["bladder", "hygiene"],
        "sanctuary": ["social"],
    },

    "Oak Street Church": {
        "fellowship hall": ["hunger", "social"],
        "restrooms": ["bladder", "hygiene"],
    },

    # HEALTHCARE
    "Magnolia Mental Health Center": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "therapy rooms": ["social"],
    },

    # SERVICES
    "Voss Massage Studio": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Maple Salon": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Sycamore Post Office": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
    },

    # RECREATION
    "Willow Creek Park": {
        "picnic area": ["hunger", "social"],
        "public restrooms": ["bladder"],
        "playground": ["fun", "social"],
    },

    "Willow Creek Bar & Grill": {
        "bar area": ["hunger", "social"],
        "restrooms": ["bladder", "hygiene"],
    },

    "Cedar Lanes Bowling Alley": {
        "snack bar": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "arcade": ["fun", "social"],
    },

    "Namaste Yoga Studio": {
        "break area": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "studio": ["energy", "social"],
    },

    # ARTS & CULTURE
    "Art Cooperative": {
        "break room": ["hunger"],
        "restrooms": ["bladder", "hygiene"],
        "studio": ["fun", "social"],
    },

    "Willow Creek Public Library": {
        "restrooms": ["bladder", "hygiene"],
        "reading area": ["fun", "social"],
    },
}


# ---------------------------------------------------------
# ACTIVITY DURATION & SATISFACTION
# ---------------------------------------------------------

ACTIVITY_CONFIG: Dict[str, Dict[str, float]] = {
    "eating": {
        "duration": 0.5,      # 30 minutes
        "satisfaction": 40.0,  # reduces hunger by 40 points
    },
    "bathroom": {
        "duration": 0.1,       # 6 minutes
        "satisfaction": 50.0,  # reduces bladder by 50 points
    },
    "shower": {
        "duration": 0.25,      # 15 minutes
        "satisfaction": 40.0,  # increases hygiene by 40 points
    },
    "sleeping": {
        "duration": 1.0,       # 1 hour (for short naps at work/school)
        "satisfaction": 30.0,  # increases energy by 30 points
    },
    "socializing": {
        "duration": 0.5,       # 30 minutes
        "satisfaction": 25.0,  # increases social by 25 points
    },
    "fun": {
        "duration": 0.5,       # 30 minutes
        "satisfaction": 25.0,  # increases fun by 25 points
    },
    "privacy": {
        "duration": 0.5,       # 30 minutes
        "satisfaction": 30.0,  # reduces horny by 30 points
    },
}


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_facilities_for_location(location: str) -> Dict[str, List[str]]:
    """
    Get all facilities available at a location.
    Returns dict of {sub_location: [needs_satisfied]}
    """
    return LOCATION_FACILITIES.get(location, {})


def can_satisfy_need_at_location(location: str, need: str) -> bool:
    """
    Check if a specific need can be satisfied at this location.
    """
    facilities = get_facilities_for_location(location)
    for sub_loc, needs in facilities.items():
        if need in needs:
            return True
    return False


def get_sub_location_for_need(location: str, need: str) -> str:
    """
    Get the appropriate sub-location for satisfying a specific need.
    Returns the first matching sub-location, or None if not found.
    """
    facilities = get_facilities_for_location(location)
    for sub_loc, needs in facilities.items():
        if need in needs:
            return sub_loc
    return None


def get_activity_duration(activity: str) -> float:
    """Get how long an activity takes in hours."""
    return ACTIVITY_CONFIG.get(activity, {}).get("duration", 0.5)


def get_activity_satisfaction(activity: str) -> float:
    """Get how much an activity satisfies a need."""
    return ACTIVITY_CONFIG.get(activity, {}).get("satisfaction", 20.0)


def get_all_locations_with_facilities() -> List[str]:
    """Get list of all locations that have facilities defined."""
    return list(LOCATION_FACILITIES.keys())
