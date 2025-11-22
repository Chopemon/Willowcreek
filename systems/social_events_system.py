# systems/social_events_system.py
# Social events like parties, gatherings, festivals

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import time


class EventType(Enum):
    PARTY = "party"
    FESTIVAL = "festival"
    GATHERING = "gathering"
    DATE = "date"
    WEDDING = "wedding"
    BIRTHDAY = "birthday"


@dataclass
class SocialEvent:
    id: str
    name: str
    event_type: EventType
    location: str
    host: str
    day: int
    start_hour: int
    duration_hours: int
    attendees: List[str] = field(default_factory=list)
    invited: List[str] = field(default_factory=list)
    description: str = ""
    
    def is_active(self, current_day: int, current_hour: int) -> bool:
        if current_day != self.day:
            return False
        return self.start_hour <= current_hour < (self.start_hour + self.duration_hours)
    
    def is_invited(self, character_name: str) -> bool:
        return character_name in self.invited


class SocialEventsSystem:
    def __init__(self):
        self.events: List[SocialEvent] = []
        self.past_events: List[SocialEvent] = []
    
    def create_event(
        self,
        name: str,
        event_type: EventType,
        location: str,
        host: str,
        day: int,
        start_hour: int,
        duration_hours: int,
        invited: List[str] = None
    ) -> SocialEvent:
        event = SocialEvent(
            id=f"event_{len(self.events)}",
            name=name,
            event_type=event_type,
            location=location,
            host=host,
            day=day,
            start_hour=start_hour,
            duration_hours=duration_hours,
            invited=invited or []
        )
        self.events.append(event)
        return event
    
    def get_active_events(self, current_day: int, current_hour: int) -> List[SocialEvent]:
        return [e for e in self.events if e.is_active(current_day, current_hour)]
    
    def attend_event(self, event: SocialEvent, character_name: str):
        if character_name not in event.attendees:
            event.attendees.append(character_name)
    
    def get_upcoming_events(self, current_day: int, days_ahead: int = 7) -> List[SocialEvent]:
        return [e for e in self.events if current_day <= e.day <= current_day + days_ahead]
