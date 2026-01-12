# systems/memory_system.py
# Memory system for tracking important events and interactions

import json
import os
from typing import Dict, List, Optional, Iterable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    """Types of memories"""
    FIRST_MEETING = "first_meeting"
    CONVERSATION = "conversation"
    GIFT_GIVEN = "gift_given"
    GIFT_RECEIVED = "gift_received"
    FIRST_KISS = "first_kiss"
    INTIMATE_MOMENT = "intimate_moment"
    CONFLICT = "conflict"
    DATE = "date"
    BREAKUP = "breakup"
    PREGNANCY_DISCOVERED = "pregnancy_discovered"
    BIRTH = "birth"
    ACHIEVEMENT = "achievement"
    EMBARRASSMENT = "embarrassment"
    BETRAYAL = "betrayal"
    CAUGHT_CHEATING = "caught_cheating"
    SPECIAL_EVENT = "special_event"


class MemoryImportance(Enum):
    """How important/memorable an event is"""
    TRIVIAL = 1
    MINOR = 2
    MODERATE = 3
    SIGNIFICANT = 4
    MAJOR = 5
    LIFE_CHANGING = 10


@dataclass
class Memory:
    """A single memory"""
    memory_type: MemoryType
    description: str
    sim_day: int
    sim_hour: int
    importance: MemoryImportance
    participants: List[str] = field(default_factory=list)
    location: str = ""
    metadata: Dict = field(default_factory=dict)
    emotional_tone: str = "neutral"
    tags: List[str] = field(default_factory=list)
    strength: float = 1.0
    last_accessed_day: Optional[int] = None
    last_decay_day: Optional[int] = None
    real_timestamp: datetime = field(default_factory=datetime.now)

    def get_age_days(self, current_sim_day: int) -> int:
        """How many sim days ago this memory was created"""
        return current_sim_day - self.sim_day

    def get_summary(self) -> str:
        """Get a readable summary of the memory"""
        participants_str = ", ".join(self.participants) if self.participants else "someone"
        return f"Day {self.sim_day}, {self.sim_hour:02d}:00 - {self.description} (with {participants_str})"

    def recall(self, current_sim_day: int, boost: float = 0.05) -> None:
        """Mark this memory as recalled to strengthen it slightly."""
        self.last_accessed_day = current_sim_day
        self.strength = min(2.0, self.strength + boost)

    def get_weight(self, current_sim_day: int) -> float:
        """Compute salience weight for recall."""
        age_days = max(0, current_sim_day - self.sim_day)
        recency_bonus = max(0.0, 10.0 - age_days)
        intensity = max(0.1, self.strength)
        return (self.importance.value * 2.0 + recency_bonus) * intensity


class MemorySystem:
    """Manages memories for all characters"""

    def __init__(self, memory_path: Optional[str] = None, auto_save: bool = True):
        self.character_memories: Dict[str, List[Memory]] = {}
        self.firsts_tracker: Dict[str, bool] = {}
        self.memory_path = memory_path
        self.auto_save = auto_save

        if self.memory_path:
            self.load_from_file(self.memory_path)

    def add_memory(
        self,
        character_name: str,
        memory_type: MemoryType,
        description: str,
        sim_day: int,
        sim_hour: int,
        importance: MemoryImportance,
        participants: List[str] = None,
        location: str = "",
        metadata: Dict = None,
        emotional_tone: str = "neutral",
        tags: Optional[Iterable[str]] = None,
        strength: float = 1.0
    ) -> Memory:
        """Add a memory to a character"""
        if character_name not in self.character_memories:
            self.character_memories[character_name] = []

        memory = Memory(
            memory_type=memory_type,
            description=description,
            sim_day=sim_day,
            sim_hour=sim_hour,
            importance=importance,
            participants=participants or [],
            location=location,
            metadata=metadata or {},
            emotional_tone=emotional_tone,
            tags=list(tags or []),
            strength=strength,
            last_decay_day=sim_day
        )

        self.character_memories[character_name].append(memory)

        if self.auto_save and self.memory_path:
            self.save_to_file(self.memory_path)

        return memory

    def get_memories(
        self,
        character_name: str,
        memory_type: Optional[MemoryType] = None,
        min_importance: Optional[MemoryImportance] = None,
        participant: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Memory]:
        """Get character's memories with optional filters"""
        if character_name not in self.character_memories:
            return []

        memories = self.character_memories[character_name]

        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        if min_importance:
            memories = [m for m in memories if m.importance.value >= min_importance.value]

        if participant:
            memories = [m for m in memories if participant in m.participants]

        memories = sorted(memories, key=lambda m: (m.sim_day, m.sim_hour), reverse=True)

        if limit:
            memories = memories[:limit]

        return memories

    def get_recent_memories(self, character_name: str, count: int = 10) -> List[Memory]:
        """Get most recent memories for a character."""
        return self.get_memories(character_name, limit=count)

    def get_salient_memories(
        self,
        character_name: str,
        current_sim_day: int,
        limit: int = 5,
        min_importance: Optional[MemoryImportance] = None,
        participant: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> List[Memory]:
        """Get top memories weighted by importance and recency."""
        memories = self.get_memories(
            character_name,
            min_importance=min_importance,
            participant=participant,
        )

        if tags:
            tag_set = set(tags)
            memories = [m for m in memories if tag_set.intersection(m.tags)]

        weighted = sorted(memories, key=lambda m: m.get_weight(current_sim_day), reverse=True)
        return weighted[:limit]

    def build_memory_context(
        self,
        character_name: str,
        current_sim_day: int,
        limit: int = 5,
        min_importance: MemoryImportance = MemoryImportance.MINOR,
    ) -> str:
        """Build a compact memory summary for prompts."""
        memories = self.get_salient_memories(
            character_name,
            current_sim_day=current_sim_day,
            limit=limit,
            min_importance=min_importance,
        )
        if not memories:
            return ""

        lines = [f"{character_name}'s recent memories:"]
        for memory in memories:
            memory.recall(current_sim_day)
            tone = f" ({memory.emotional_tone})" if memory.emotional_tone else ""
            lines.append(f"- {memory.get_summary()}{tone}")
        return "\n".join(lines)

    def decay_memories(
        self,
        current_sim_day: int,
        daily_decay: float = 0.03,
        min_strength: float = 0.2,
    ) -> None:
        """Decay memory strength over time."""
        for memories in self.character_memories.values():
            for memory in memories:
                last_decay = memory.last_decay_day or memory.sim_day
                elapsed = max(0, current_sim_day - last_decay)
                if elapsed <= 0:
                    continue
                memory.strength = max(min_strength, memory.strength - daily_decay * elapsed)
                memory.last_decay_day = current_sim_day

    def reinforce_memory(
        self,
        character_name: str,
        description_contains: str,
        current_sim_day: int,
        boost: float = 0.1,
    ) -> int:
        """Reinforce memories matching text; returns count reinforced."""
        if character_name not in self.character_memories:
            return 0
        count = 0
        needle = description_contains.lower()
        for memory in self.character_memories[character_name]:
            if needle in memory.description.lower():
                memory.recall(current_sim_day, boost=boost)
                count += 1
        return count

    def get_relationship_timeline(self, character_name: str, other_character: str) -> str:
        """Get timeline of relationship with another character"""
        memories = self.get_memories(character_name, participant=other_character, limit=50)

        if not memories:
            return f"{character_name} has no memories with {other_character}."

        memories = list(reversed(memories))
        lines = [f"\n{character_name}'s History with {other_character}:"]
        for memory in memories:
            lines.append(f"  Day {memory.sim_day}: {memory.description}")

        return "\n".join(lines)

    def save_to_file(self, memory_path: str) -> None:
        try:
            directory = os.path.dirname(memory_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            data = {
                "character_memories": {
                    name: [self._memory_to_dict(memory) for memory in memories]
                    for name, memories in self.character_memories.items()
                },
                "firsts_tracker": self.firsts_tracker,
            }

            with open(memory_path, "w", encoding="utf-8") as file_handle:
                json.dump(data, file_handle, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[MemorySystem] Failed to save memories to {memory_path}: {exc}")

    def load_from_file(self, memory_path: str) -> None:
        if not os.path.exists(memory_path):
            return

        try:
            with open(memory_path, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except Exception as exc:
            print(f"[MemorySystem] Failed to load memories from {memory_path}: {exc}")
            return

        character_memories = data.get("character_memories", {})
        loaded_memories: Dict[str, List[Memory]] = {}
        for name, memories in character_memories.items():
            loaded_memories[name] = [self._memory_from_dict(entry) for entry in memories]

        self.character_memories = loaded_memories
        self.firsts_tracker = data.get("firsts_tracker", {})

    def _memory_to_dict(self, memory: Memory) -> Dict:
        return {
            "memory_type": memory.memory_type.value,
            "description": memory.description,
            "sim_day": memory.sim_day,
            "sim_hour": memory.sim_hour,
            "importance": memory.importance.name,
            "participants": memory.participants,
            "location": memory.location,
            "metadata": memory.metadata,
            "emotional_tone": memory.emotional_tone,
            "tags": memory.tags,
            "strength": memory.strength,
            "last_accessed_day": memory.last_accessed_day,
            "last_decay_day": memory.last_decay_day,
            "real_timestamp": memory.real_timestamp.isoformat(),
        }

    def _memory_from_dict(self, data: Dict) -> Memory:
        memory_type_value = data.get("memory_type", MemoryType.SPECIAL_EVENT.value)
        try:
            memory_type = MemoryType(memory_type_value)
        except ValueError:
            memory_type = MemoryType.SPECIAL_EVENT

        importance_value = data.get("importance", MemoryImportance.MINOR.name)
        try:
            importance = MemoryImportance[importance_value]
        except KeyError:
            importance = MemoryImportance.MINOR

        real_timestamp = data.get("real_timestamp")
        parsed_timestamp = datetime.now()
        if real_timestamp:
            try:
                parsed_timestamp = datetime.fromisoformat(real_timestamp)
            except ValueError:
                parsed_timestamp = datetime.now()

        return Memory(
            memory_type=memory_type,
            description=data.get("description", ""),
            sim_day=data.get("sim_day", 0),
            sim_hour=data.get("sim_hour", 0),
            importance=importance,
            participants=data.get("participants", []),
            location=data.get("location", ""),
            metadata=data.get("metadata", {}),
            emotional_tone=data.get("emotional_tone", "neutral"),
            tags=data.get("tags", []),
            strength=float(data.get("strength", 1.0)),
            last_accessed_day=data.get("last_accessed_day"),
            last_decay_day=data.get("last_decay_day"),
            real_timestamp=parsed_timestamp,
        )
