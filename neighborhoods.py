# neighborhoods.py
from typing import Dict, Optional

"""
Neighborhood + address registry for Willow Creek.

We map:
    Neighborhood name → { Household name → full street address }

Other systems only need get_neighborhood(household), but we also expose
get_address_for_household() so NPC.home_address or UI can show real addresses.
"""

NEIGHBORHOODS: Dict[str, Dict[str, str]] = {
    # Malcolm + Sturm + Tessa live on the same street
    "Oak Street": {
        "Malcolm's House": "Oak Street 1",
        "Sturm House": "Oak Street 3",
        "Tessa's House": "Oak Street 5",
    },

    # Carter / Thompson / Lockheart cluster
    "Willow Lane": {
        "Carter House": "Willow Lane 2",
        "Thompson House": "Willow Lane 4",
        "Lockheart House": "Willow Lane 6",
    },

    # Riverside family homes
    "Riverside Loop": {
        "Blake House": "Riverside Loop 10",
        "Kallio House": "Riverside Loop 12",
    },

    # Paired houses further out
    "Sycamore Lane": {
        "Seinfeld House": "Sycamore Lane 8",
        "Kunitz House": "Sycamore Lane 10",
    },

    # New neighborhood you added for Isabella & Lucas
    "Cedar View": {
        "Ruiz House": "Cedar View 1",
    },

    # Nate lives outside the town proper
    "Out-of-Town": {
        "Nate's House": "County Road 5 (Out of Town)",
    },
}


def get_neighborhood(household: Optional[str]) -> str:
    """
    Return the neighborhood name for a given household, or "None" if unknown.

    Used by:
      - simulation_v2._build_neighbor_map()
      - debug overlay / status panel
    """
    if not household:
        return "None"

    for hood, houses in NEIGHBORHOODS.items():
        # houses is a dict: {household_name: address}
        if household in houses:
            return hood

    return "None"


def get_address_for_household(household: Optional[str]) -> Optional[str]:
    """
    Return the full street address (e.g. 'Oak Street 3') for a household,
    or None if we don't have it registered.
    """
    if not household:
        return None

    for hood, houses in NEIGHBORHOODS.items():
        addr = houses.get(household)
        if addr:
            return addr

    return None
