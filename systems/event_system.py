# systems/event_system.py
"""
EventSystem v1.0
- Handles ambient town events and bigger beats
- Can call ConsequenceCascadesSystem for ripples
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC
    from systems.consequence_cascades import ConsequenceCascadesSystem


@dataclass
class WorldEvent:
    kind: str
    location: str
    actors: List[str]
    payload: Dict[str, Any]


class EventSystem:
    def __init__(self, time: "TimeSystem", consequences: "ConsequenceCascadesSystem"):
        self.time = time
        self.consequences = consequences
        self.recent_events: List[WorldEvent] = []

    def _record(self, kind: str, location: str, actors: List["NPC"], payload: Dict[str, Any] | None = None):
        payload = payload or {}
        ev = WorldEvent(
            kind=kind,
            location=location,
            actors=[a.full_name for a in actors],
            payload=payload,
        )
        self.recent_events.append(ev)
        if len(self.recent_events) > 50:
            self.recent_events.pop(0)

        try:
            self.consequences.record_event(kind, actors, location, payload)
        except Exception as e:
            print(f"[EventSystem] Consequence cascade failed for {kind}: {e}")

    # ------------------------------------------------------------------
    # STEP-LEVEL UPDATE (hourly-ish)
    # ------------------------------------------------------------------
    def update_step(self, npcs: List["NPC"], location_map: Dict[str, List["NPC"]]):
        hour = self.time.hour

        # Example: evening crowd event
        if 18 <= hour < 21 and random.random() < 0.02:
            loc = random.choice([
                "Main Street Diner",
                "Downtown Café",
                "Willow Creek Mall - Food Court",
                "Cedar Lanes Bowling Alley",
            ])
            actors = location_map.get(loc, [])
            if len(actors) >= 2:
                picked = random.sample(actors, k=min(3, len(actors)))
                self._record("evening_crowd_scene", loc, picked, {"note": "busy evening atmosphere"})

    # ------------------------------------------------------------------
    # DAILY UPDATE
    # ------------------------------------------------------------------
    def update_for_day(self, npcs: List["NPC"], location_map: Dict[str, List["NPC"]]):
        # Once-per-day global events
        if random.random() < 0.05:
            # community-style event
            loc = random.choice(["Community Center", "Lutheran Church", "Willow Creek Park"])
            actors = location_map.get(loc, [])
            if len(actors) >= 3:
                picked = random.sample(actors, k=min(6, len(actors)))
            else:
                picked = actors
            self._record("community_event", loc, picked, {"note": "small town gathering"})
