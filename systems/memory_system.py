# systems/memory_system.py
# Memory system for tracking important events and interactions

from typing import Dict, List, Optional
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
    real_timestamp: datetime = field(default_factory=datetime.now)

    def get_age_days(self, current_sim_day: int) -> int:
        """How many sim days ago this memory was created"""
        return current_sim_day - self.sim_day

    def get_summary(self) -> str:
        """Get a readable summary of the memory"""
        participants_str = ", ".join(self.participants) if self.participants else "someone"
        return f"Day {self.sim_day}, {self.sim_hour:02d}:00 - {self.description} (with {participants_str})"


class MemorySystem:
    """Manages memories for all characters"""

    def __init__(self):
        self.character_memories: Dict[str, List[Memory]] = {}
        self.firsts_tracker: Dict[str, bool] = {}

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
        metadata: Dict = None
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
            metadata=metadata or {}
        )

        self.character_memories[character_name].append(memory)
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
