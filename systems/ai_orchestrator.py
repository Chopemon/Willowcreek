"""AI orchestration stack for event-driven character cognition.

This module provides a practical reference implementation for the architecture
needed to scale many NPCs with occasional LLM calls:

1. Central world engine state (time, weather, locations, state machine)
2. Perception summaries scoped to each character
3. Long-term memory retrieval for relevant context injection
4. Brain routing with a constrained JSON action contract
5. AI director queue that only wakes characters on important events
"""

from __future__ import annotations

import json
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Tuple


@dataclass
class WorldObject:
    object_id: str
    name: str
    location: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterState:
    name: str
    location: str
    state: str = "idle"
    persona: str = ""
    routine_state: str = "background"


@dataclass
class WorldEvent:
    event_type: str
    location: str
    description: str
    participants: List[str] = field(default_factory=list)
    priority: int = 1


class CentralWorldEngine:
    """Ground-truth world model with basic time/physics/state tracking."""

    def __init__(self, hour: int = 8, weather: str = "Clear") -> None:
        self.day = 1
        self.hour = hour
        self.weather = weather
        self.characters: Dict[str, CharacterState] = {}
        self.objects: Dict[str, WorldObject] = {}

    def advance_time(self, hours: int = 1) -> None:
        total = self.hour + max(hours, 0)
        self.day += total // 24
        self.hour = total % 24

    def set_weather(self, weather: str) -> None:
        self.weather = weather

    def upsert_character(self, character: CharacterState) -> None:
        self.characters[character.name] = character

    def set_character_state(self, name: str, state: str, routine_state: str = "background") -> None:
        if name not in self.characters:
            return
        self.characters[name].state = state
        self.characters[name].routine_state = routine_state

    def move_character(self, name: str, location: str) -> None:
        if name not in self.characters:
            return
        self.characters[name].location = location

    def upsert_object(self, world_object: WorldObject) -> None:
        self.objects[world_object.object_id] = world_object


class PerceptionSystem:
    """Produces localized sensory text so agents never see omniscient state."""

    def __init__(self, world: CentralWorldEngine):
        self.world = world

    def summarize_for(self, character_name: str, nearby_events: Iterable[WorldEvent]) -> str:
        character = self.world.characters.get(character_name)
        if not character:
            return "You are nowhere."

        co_located = [
            other.name
            for other in self.world.characters.values()
            if other.location == character.location and other.name != character.name
        ]
        visible_objects = [obj.name for obj in self.world.objects.values() if obj.location == character.location]
        visible_events = [e.description for e in nearby_events if e.location == character.location]

        lines = [
            f"You are in {character.location}.",
            f"It is day {self.world.day}, {self.world.hour:02d}:00. Weather: {self.world.weather}.",
            f"Nearby characters: {', '.join(co_located) if co_located else 'none'}.",
            f"Visible objects: {', '.join(visible_objects) if visible_objects else 'none'}.",
        ]
        if visible_events:
            lines.append(f"Recent events: {' | '.join(visible_events)}.")
        return " ".join(lines)


@dataclass
class MemoryRecord:
    text: str
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0


class VectorMemoryStore:
    """Simple embedding-free memory retrieval using token similarity.

    It mimics vector retrieval behavior with cosine-like scoring over token
    frequency vectors, keeping dependencies minimal.
    """

    def __init__(self) -> None:
        self._memories: Dict[str, List[MemoryRecord]] = defaultdict(list)

    def add_memory(self, character_name: str, text: str, tags: Optional[List[str]] = None, weight: float = 1.0) -> None:
        self._memories[character_name].append(MemoryRecord(text=text, tags=tags or [], weight=weight))

    def query(self, character_name: str, query_text: str, top_k: int = 3) -> List[MemoryRecord]:
        memories = self._memories.get(character_name, [])
        if not memories:
            return []

        query_vector = self._vectorize(query_text)
        scored: List[Tuple[float, MemoryRecord]] = []
        for memory in memories:
            candidate_vector = self._vectorize(f"{memory.text} {' '.join(memory.tags)}")
            similarity = self._cosine(query_vector, candidate_vector) * memory.weight
            if similarity > 0:
                scored.append((similarity, memory))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[:top_k]]

    @staticmethod
    def _vectorize(text: str) -> Dict[str, float]:
        vector: Dict[str, float] = defaultdict(float)
        for token in text.lower().replace("\n", " ").split(" "):
            token = "".join(ch for ch in token if ch.isalnum() or ch == "_")
            if token:
                vector[token] += 1.0
        return dict(vector)

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(a.get(token, 0.0) * b.get(token, 0.0) for token in a)
        mag_a = math.sqrt(sum(value * value for value in a.values()))
        mag_b = math.sqrt(sum(value * value for value in b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


class BrainRouter:
    """Builds constrained prompts and validates JSON action output."""

    ACTION_SCHEMA = {
        "dialogue": "string",
        "action": "string",
        "target": "string|null",
        "reasoning": "string",
    }

    def __init__(self, model_call: Callable[[str], str]) -> None:
        self.model_call = model_call

    def think(self, character: CharacterState, perception: str, memories: List[MemoryRecord]) -> Dict[str, Any]:
        memory_block = "\n".join(f"- {m.text}" for m in memories) or "- none"
        prompt = (
            f"Persona: {character.persona or character.name}.\n"
            "You must return only JSON with keys: dialogue, action, target, reasoning.\n"
            f"Current state: {character.state}.\n"
            f"Perception: {perception}\n"
            f"Relevant memories:\n{memory_block}\n"
            "Respond with compact JSON only."
        )

        raw = self.model_call(prompt)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "dialogue": "...",
                "action": "wait",
                "target": None,
                "reasoning": "Fallback due to invalid model output.",
            }

        validated = {
            "dialogue": str(payload.get("dialogue", "...")),
            "action": str(payload.get("action", "wait")),
            "target": payload.get("target"),
            "reasoning": str(payload.get("reasoning", "")),
        }
        return validated


class AIDirector:
    """Event-driven orchestrator that queues and staggers LLM calls."""

    def __init__(
        self,
        world: CentralWorldEngine,
        perception_system: PerceptionSystem,
        memory_store: VectorMemoryStore,
        brain_router: BrainRouter,
    ) -> None:
        self.world = world
        self.perception_system = perception_system
        self.memory_store = memory_store
        self.brain_router = brain_router
        self.event_queue: Deque[Tuple[str, WorldEvent]] = deque()

    def enqueue_event(self, event: WorldEvent) -> None:
        for character in self.world.characters.values():
            if character.location == event.location:
                self.event_queue.append((character.name, event))

    def run_background_routines(self) -> None:
        for character in self.world.characters.values():
            if character.routine_state == "background":
                # Cheap deterministic behavior without an LLM call
                if character.state == "working":
                    character.state = "working"
                elif character.state == "sleeping":
                    character.state = "sleeping"

    def process_queue(self, max_requests_per_tick: int = 5) -> List[Tuple[str, Dict[str, Any]]]:
        results: List[Tuple[str, Dict[str, Any]]] = []
        processed = 0
        while self.event_queue and processed < max_requests_per_tick:
            character_name, event = self.event_queue.popleft()
            character = self.world.characters.get(character_name)
            if not character:
                continue

            perception = self.perception_system.summarize_for(character_name, [event])
            memories = self.memory_store.query(character_name, f"{event.description} {event.event_type}")
            decision = self.brain_router.think(character, perception, memories)
            results.append((character_name, decision))
            processed += 1
        return results
