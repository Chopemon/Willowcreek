from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from entities.npc import NPC


@dataclass
class Perception:
    time: datetime
    location: str
    nearby_people: List[str]
    notable_events: List[str]
    player_message: Optional[str]


@dataclass
class Decision:
    location: Optional[str] = None
    task: Optional[str] = None
    mood: Optional[str] = None


@dataclass
class CallBudget:
    max_calls: int
    remaining: int

    def consume(self, count: int = 1) -> bool:
        if self.remaining < count:
            return False
        self.remaining -= count
        return True


class NPCAgent:
    def __init__(self, npc: NPC):
        self.npc = npc

    def tick(self, perception: Perception, budget: CallBudget) -> Decision:
        decision = Decision()

        if perception.nearby_people:
            names = ", ".join(perception.nearby_people[:2])
            decision.task = f"Socializing with {names}"
        else:
            decision.task = "Keeping to their routine"

        if perception.player_message and self.npc.full_name.lower() in perception.player_message.lower():
            decision.mood = "Alert"

        if perception.location == "Unknown" and getattr(self.npc, "home_location", None):
            decision.location = self.npc.home_location

        return decision
