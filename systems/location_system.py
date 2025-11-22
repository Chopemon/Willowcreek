# systems/location_system.py
# Enhanced location system with activities

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class LocationType(Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    PARK = "park"
    ENTERTAINMENT = "entertainment"
    PUBLIC = "public"


@dataclass
class Location:
    name: str
    location_type: LocationType
    description: str
    capacity: int = 50
    activities: List[str] = field(default_factory=list)
    open_hours: tuple = (0, 24)  # (open_hour, close_hour)
    current_occupants: Set[str] = field(default_factory=set)
    
    def is_open(self, hour: int) -> bool:
        return self.open_hours[0] <= hour < self.open_hours[1]
    
    def can_enter(self, hour: int) -> bool:
        return self.is_open(hour) and len(self.current_occupants) < self.capacity
    
    def add_occupant(self, character_name: str):
        self.current_occupants.add(character_name)
    
    def remove_occupant(self, character_name: str):
        self.current_occupants.discard(character_name)


class LocationSystem:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self._initialize_locations()
    
    def _initialize_locations(self):
        self.locations = {
            "Park": Location(
                name="Willow Creek Park",
                location_type=LocationType.PARK,
                description="A peaceful park with walking trails",
                activities=["walk", "jog", "picnic", "read"],
                open_hours=(6, 22)
            ),
            "Coffee Shop": Location(
                name="Willow Creek Cafe",
                location_type=LocationType.COMMERCIAL,
                description="Cozy coffee shop with free wifi",
                activities=["drink_coffee", "read", "socialize", "work"],
                open_hours=(6, 20)
            ),
            "Bar": Location(
                name="The Rusty Nail",
                location_type=LocationType.ENTERTAINMENT,
                description="Local bar and grill",
                activities=["drink", "eat", "socialize", "play_pool"],
                open_hours=(16, 2)
            ),
            "Gym": Location(
                name="Willow Creek Fitness",
                location_type=LocationType.COMMERCIAL,
                description="Modern gym with equipment",
                activities=["workout", "yoga", "swim"],
                open_hours=(5, 23)
            ),
        }
    
    def get_location(self, name: str) -> Optional[Location]:
        return self.locations.get(name)
    
    def get_occupants(self, location_name: str) -> Set[str]:
        location = self.get_location(location_name)
        return location.current_occupants if location else set()
    
    def move_character(self, character_name: str, from_location: str, to_location: str, hour: int) -> bool:
        to_loc = self.get_location(to_location)
        
        if not to_loc or not to_loc.can_enter(hour):
            return False
        
        # Remove from old location
        if from_location:
            from_loc = self.get_location(from_location)
            if from_loc:
                from_loc.remove_occupant(character_name)
        
        # Add to new location
        to_loc.add_occupant(character_name)
        return True
