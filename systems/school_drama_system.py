# systems/school_drama_system.py
"""
SchoolDramaSystem v1.0
- Runs at Willow Creek High School during school hours
- Creates drama: arguments, gossip, kind acts, crush moments
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC
    from systems.reputation_system import ReputationSystem
    from systems.emotional_contagion import EmotionalContagionSystem
    from systems.memory_system import MemorySystem
    from systems.consequence_cascades import ConsequenceCascadesSystem


@dataclass
class DramaEvent:
    kind: str
    actors: List[str]
    location: str


class SchoolDramaSystem:
    def __init__(
        self,
        time: "TimeSystem",
        reputation: "ReputationSystem",
        emotional: "EmotionalContagionSystem",
        memory: "MemorySystem",
        consequences: "ConsequenceCascadesSystem",
    ):
        self.time = time
        self.reputation = reputation
        self.emotional = emotional
        self.memory = memory
        self.consequences = consequences
        self.recent_events: List[DramaEvent] = []

    def _log(self, kind: str, actors: List["NPC"], location: str):
        ev = DramaEvent(kind=kind, actors=[a.full_name for a in actors], location=location)
        self.recent_events.append(ev)
        if len(self.recent_events) > 50:
            self.recent_events.pop(0)

    def _teen_group(self, npcs: List["NPC"]) -> List["NPC"]:
        return [n for n in npcs if 13 <= n.age <= 19]

    def update_step(self, npcs: List["NPC"], location_map: Dict[str, List["NPC"]]):
        # only during school days/hours
        if self.time.is_weekend:
            return
        if not (8 <= self.time.hour < 15):
            return

        school_npcs = location_map.get("Willow Creek High School", [])
        teens = self._teen_group(school_npcs)
        if len(teens) < 2:
            return

        # small chance each step
        roll = random.random()
        if roll < 0.03:
            # hallway argument
            a, b = random.sample(teens, k=2)
            self._log("hallway_argument", [a, b], "Willow Creek High School")
            try:
                # slight rep penalty for both
                self.reputation.adjust_reputation(a.full_name, delta=-1)
                self.reputation.adjust_reputation(b.full_name, delta=-1)
            except Exception:
                pass
            try:
                self.emotional.seed_emotion(a, "anger", intensity=0.3)
                self.emotional.seed_emotion(b, "anger", intensity=0.3)
            except Exception:
                pass
            try:
                self.consequences.record_event(
                    "public_argument", [a, b], "Willow Creek High School", {"scope": "teen_drama"}
                )
            except Exception:
                pass

        elif roll < 0.06:
            # kind act (help with books, notes, etc.)
            a, b = random.sample(teens, k=2)
            self._log("kind_act", [a, b], "Willow Creek High School")
            try:
                self.emotional.seed_emotion(a, "warmth", intensity=0.3)
                self.emotional.seed_emotion(b, "warmth", intensity=0.3)
            except Exception:
                pass
            try:
                self.reputation.adjust_reputation(a.full_name, delta=1)
                self.reputation.adjust_reputation(b.full_name, delta=1)
            except Exception:
                pass
            try:
                self.consequences.record_event(
                    "kind_public_act", [a, b], "Willow Creek High School", {"scope": "teen_drama"}
                )
            except Exception:
                pass

        elif roll < 0.09:
            # gossip spread
            spreaders = random.sample(teens, k=min(3, len(teens)))
            self._log("gossip", spreaders, "Willow Creek High School")
            try:
                for s in spreaders:
                    self.emotional.seed_emotion(s, "excitement", intensity=0.2)
            except Exception:
                pass
            # let reputation_system handle actual gossip network if it has support
            try:
                if hasattr(self.reputation, "inject_school_gossip"):
                    names = [s.full_name for s in spreaders]
                    self.reputation.inject_school_gossip(names, location="Willow Creek High School")
            except Exception as e:
                print(f"[SchoolDrama] gossip injection failed: {e}")
