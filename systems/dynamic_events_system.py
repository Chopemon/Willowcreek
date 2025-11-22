# systems/dynamic_events_system.py
# Random dynamic events that can occur

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import random


class EventCategory(Enum):
    ENCOUNTER = "encounter"
    OPPORTUNITY = "opportunity"
    CRISIS = "crisis"
    DISCOVERY = "discovery"
    SOCIAL = "social"


@dataclass
class DynamicEvent:
    id: str
    name: str
    description: str
    category: EventCategory
    probability: float  # 0.0 to 1.0
    conditions: Dict = None
    effects: Dict = None
    choices: List[tuple] = None  # (choice_text, outcome)
    
    def can_trigger(self, context: Dict) -> bool:
        if self.conditions is None:
            return True
        
        for condition, value in self.conditions.items():
            if condition == "location" and context.get("location") != value:
                return False
            elif condition == "time_range":
                hour = context.get("hour", 12)
                if not (value[0] <= hour <= value[1]):
                    return False
        
        return True


class DynamicEventsSystem:
    def __init__(self):
        self.event_pool: List[DynamicEvent] = []
        self.triggered_events: List[str] = []
        self._initialize_events()
    
    def _initialize_events(self):
        self.event_pool = [
            DynamicEvent(
                id="lost_wallet",
                name="Lost Wallet",
                description="You find a wallet on the ground. It has an ID inside.",
                category=EventCategory.OPPORTUNITY,
                probability=0.05,
                choices=[
                    ("Return it to the owner", {"reputation": +15, "karma": +10}),
                    ("Keep the money", {"money": +50, "reputation": -10})
                ]
            ),
            DynamicEvent(
                id="friendly_dog",
                name="Friendly Dog",
                description="A friendly dog approaches you, wagging its tail.",
                category=EventCategory.ENCOUNTER,
                probability=0.1,
                conditions={"location": "Park"},
                choices=[
                    ("Pet the dog", {"mood": +5}),
                    ("Ignore it", {})
                ]
            ),
            DynamicEvent(
                id="coffee_shop_encounter",
                name="Coffee Shop Encounter",
                description="You bump into someone at the coffee shop and spill their coffee!",
                category=EventCategory.SOCIAL,
                probability=0.08,
                conditions={"location": "Coffee Shop"},
                choices=[
                    ("Apologize and buy them a new coffee", {"reputation": +5, "money": -5}),
                    ("Apologize quickly and leave", {"reputation": -3})
                ]
            )
        ]
    
    def check_for_event(self, context: Dict) -> Optional[DynamicEvent]:
        available_events = [e for e in self.event_pool if e.can_trigger(context)]
        
        for event in available_events:
            if random.random() < event.probability:
                self.triggered_events.append(event.id)
                return event
        
        return None
