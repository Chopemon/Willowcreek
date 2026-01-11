from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from agents import memory_store


@dataclass(slots=True)
class Perception:
    observations: list[str] = field(default_factory=list)
    timestamp: str | None = None


@dataclass(slots=True)
class Decision:
    action: str
    rationale: str | None = None


class NPCAgent:
    def __init__(self, name: str) -> None:
        self.name = name
        self.identity = memory_store.load_identity(name)
        self.state = memory_store.load_state(name)
        self.relationships = memory_store.load_relationships(name)

    def perceive(self, observations: Iterable[str], timestamp: str | None = None) -> Perception:
        return Perception(observations=list(observations), timestamp=timestamp)

    def decide(self, perception: Perception) -> Decision:
        if perception.observations:
            return Decision(action="observe", rationale="Tracking recent observations.")
        return Decision(action="idle", rationale="No new observations.")

    def remember(self, ts: str, memory_type: str, salience: int, text: str) -> None:
        memory_store.append_memory(self.name, ts, memory_type, salience, text)

    def retrieve_memories(self, query: str, k: int = 5) -> list[dict]:
        return memory_store.retrieve_relevant_memories(self.name, query, k)
