# systems/consequence_cascades.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
from entities.npc import NPC
from systems.reputation_system import ReputationSystem
from systems.emotional_contagion import EmotionalContagionSystem
from systems.memory_system import MemorySystem


@dataclass
class EventRecord:
    kind: str
    actors: List[str]
    location: str
    payload: Dict[str, Any]


class ConsequenceCascadesSystem:
    """
    Receives high-level events and applies cascading consequences:
      - reputation changes
      - memories
      - emotional contagion seeds
    """

    def __init__(
        self,
        reputation: ReputationSystem,
        emotions: EmotionalContagionSystem,
        memory: MemorySystem,
    ):
        self.reputation = reputation
        self.emotions = emotions
        self.memory = memory
        self.event_log: List[EventRecord] = []

    def record_event(self, kind: str, actors: List[NPC], location: str, payload: Dict[str, Any] | None = None):
        payload = payload or {}
        rec = EventRecord(
            kind=kind,
            actors=[a.full_name for a in actors],
            location=location,
            payload=payload,
        )
        self.event_log.append(rec)

        # Simple examples of cascading logic
        if kind == "public_argument":
            for a in actors:
                self.memory.add_memory(a, f"Had an argument at {location}")
                self.emotions.seed_emotion(a, "anger", intensity=0.4)
            # Reputation drop for aggressor, if any
            aggressor = payload.get("aggressor")
            if isinstance(aggressor, NPC):
                self.reputation.adjust_reputation(aggressor.full_name, delta=-5)

        elif kind == "kind_public_act":
            for a in actors:
                self.memory.add_memory(a, f"Helped someone at {location}")
                self.emotions.seed_emotion(a, "warmth", intensity=0.3)
                self.reputation.adjust_reputation(a.full_name, delta=3)

        # You can extend this with many event types.
