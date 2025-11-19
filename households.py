# households.py
"""
Household resolution for Willow Creek NPCs.

Rules:
- If an NPC has a manual override, use that.
- Else, use last name -> "<LastName> House" for known families.
- Else, return generic "Home".
"""

from typing import Dict, Optional

# 1) Automatic households by last name
AUTO_HOUSEHOLDS: Dict[str, str] = {
    "Sturm": "Sturm House",
    "Carter": "Carter House",
    "Blake": "Blake House",
    "Madison": "Madison House",
    "Lockheart": "Lockheart House",
    "Kallio": "Kallio House",
    "Seinfeld": "Seinfeld House",
    "Kunitz": "Kunitz House",
    "Ruiz": "Ruiz House",
    "Thompson": "Thompson House",
    # Add more last names here if you introduce new families
}

# 2) Manual overrides: single-name or special-case NPCs
MANUAL_OVERRIDES: Dict[str, str] = {
    # Player character
    "Malcolm Newt": "Malcolm's House",

    # Tessa & kids – explicit shared weekday house
    "Tessa": "Tessa's House",
    "Milo": "Tessa's House",
    "Ivy": "Tessa's House",

    # Nate lives in the next town, separate household
    "Nate": "Nate's House",
}


def _get_last_name(full_name: str) -> Optional[str]:
    """Return last token as last name, or None if there isn't one."""
    parts = full_name.strip().split()
    if len(parts) < 2:
        return None
    return parts[-1]


def get_household(full_name: str) -> str:
    """
    Resolve an NPC's canonical household location.
    Priority:
      1. Manual overrides
      2. Auto map by last name
      3. Fallback: generic "Home"
    """
    # 1) Manual overrides for one-off NPCs
    if full_name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[full_name]

    # 2) Last-name based household
    last = _get_last_name(full_name)
    if last and last in AUTO_HOUSEHOLDS:
        return AUTO_HOUSEHOLDS[last]

    # 3) Fallback generic
    return "Home"
