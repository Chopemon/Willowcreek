# entities/npc.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


# ---------------------------------------------------------
# Gender enum
# ---------------------------------------------------------
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# ---------------------------------------------------------
# Needs + psyche stubs (your full systems exist elsewhere)
# ---------------------------------------------------------
@dataclass
class Needs:
    hunger: float = 80.0
    energy: float = 90.0
    hygiene: float = 85.0
    bladder: float = 20.0
    social: float = 60.0
    fun: float = 70.0
    horny: float = 30.0


@dataclass
class PsycheState:
    lonely: float = 20.0


# ---------------------------------------------------------
# Background data class
# ---------------------------------------------------------
@dataclass
class NPCBackground:
    currentConflict: str = ""
    vulnerability: str = ""


# ---------------------------------------------------------
# NPC class
# ---------------------------------------------------------
@dataclass
class NPC:
    full_name: str
    age: int
    gender: Gender = Gender.OTHER
    affiliation: str = ""          # original field
    occupation: Optional[str] = "" # FIXED, extracted properly
    appearance: str = ""
    coreTraits: List[str] = field(default_factory=list)
    libidoLevel: int = 0
    status: str = "active"
    relationship: int = 0

    memory_bank: Set[str] = field(default_factory=set)
    private_secrets: Set[str] = field(default_factory=set)  # renamed from privateHabits
    dislikes: List[str] = field(default_factory=list)

    relationships: Dict[str, Dict[str, str]] = field(default_factory=dict)
    background: NPCBackground = field(default_factory=NPCBackground)

    # Runtime state
    current_location: str = "Home"
    home_location: str = "Home"
    mood: str = "Neutral" # <-- NEW: Fixed AttributeError
    current_task: str = ""
    
    needs: Needs = field(default_factory=Needs)
    psyche: PsycheState = field(default_factory=PsycheState)

    def __post_init__(self):
        # Fix None fields
        if not self.affiliation:
            self.affiliation = ""
        if not self.occupation:
            self.occupation = ""


# ---------------------------------------------------------
# JOB KEYWORD MAP USED FOR EXTRACTION
# ---------------------------------------------------------
JOB_KEYWORDS = [
    "pastor", "minister", "teacher", "nurse", "doctor", "paramedic",
    "therapist", "massage", "officer", "police", "librarian", "barista",
    "chef", "cook", "waiter", "waitress", "server", "cashier", "retail",
    "clerk", "yoga", "instructor", "navy", "military", "mechanic",
    "carpenter", "janitor", "assistant", "security", "firefighter"
]


# ---------------------------------------------------------
# NPC CREATOR
# ---------------------------------------------------------
def create_npc_from_dict(data: dict) -> NPC:
    """
    FULLY FIXED loader.
    - Correctly extracts job from affiliation.
    - Does NOT truncate job titles incorrectly.
    - Does NOT treat family words as jobs.
    - Safely loads all fields.
    """

    name = data.get("name", "Unnamed NPC")
    age = data.get("age", 30)
    gender_str = str(data.get("gender", "other")).lower()

    gender = (
        Gender.MALE if gender_str == "male" else
        Gender.FEMALE if gender_str == "female" else
        Gender.OTHER
    )

    affiliation = data.get("affiliation", "") or ""

    # ------------ FIXED JOB EXTRACTION ------------
    raw_occ = data.get("occupation")
    occ = None

    if raw_occ:
        occ = raw_occ.strip().lower()
    else:
        text = affiliation.lower()

        # look for job keyword anywhere in the affiliation text
        for kw in JOB_KEYWORDS:
            if kw in text:
                occ = kw
                break

    # if no job found, leave occ = None → scheduler treats NPC as unemployed
    # and sends them to hangouts

    # ---------------------------------------------------------
    # CREATE NPC OBJECT
    # ---------------------------------------------------------
    npc = NPC(
        full_name=name,
        age=age,
        gender=gender,
        affiliation=affiliation,
        occupation=occ or "",
        appearance=data.get("appearance", ""),
        coreTraits=data.get("coreTraits", []),
        libidoLevel=data.get("libidoLevel", 0),
        status=data.get("status", "active"),
        relationship=data.get("relationship", 0),

        memory_bank=set(data.get("memory", [])),
        private_secrets=set(data.get("privateHabits", [])),  # FIXED naming
        dislikes=data.get("dislikes", []),

        relationships=data.get("relationships", {}),
        background=NPCBackground(
            currentConflict=str(data.get("background", {}).get("currentConflict", "") or ""),
            vulnerability=str(data.get("background", {}).get("vulnerability", "") or ""),
        ),
    )

    # Home location: derived from last name or explicitly set
    if "home_location" in data:
        npc.home_location = data["home_location"]
    else:
        # Special case: Malcolm Newt (protagonist) gets "Home"
        if name == "Malcolm Newt":
            npc.home_location = "Home"
        else:
            # Derive from last name (e.g., "Sarah Madison" -> "Madison House")
            parts = name.strip().split()
            if len(parts) >= 2:
                last_name = parts[-1]
                npc.home_location = f"{last_name} House"
            else:
                # Single name NPCs (like "Nate", "Tessa", "Hanna")
                npc.home_location = f"{name}'s House"

    return npc
