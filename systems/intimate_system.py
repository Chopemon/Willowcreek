# systems/intimate_system.py
# Intimate relationship depth mechanics

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class IntimacyLevel(Enum):
    NONE = 0
    KISSED = 1
    INTIMATE = 2
    REGULAR_PARTNER = 3
    COMMITTED_INTIMATE = 4


@dataclass
class IntimateRelationship:
    person_a: str
    person_b: str
    intimacy_level: IntimacyLevel = IntimacyLevel.NONE
    times_intimate: int = 0
    satisfaction: float = 50.0  # 0-100
    last_intimate_day: int = -1
    preferences_compatibility: float = 50.0  # 0-100
    
    def record_intimate_encounter(self, day: int, satisfaction_change: float = 0):
        self.times_intimate += 1
        self.last_intimate_day = day
        self.satisfaction = max(0, min(100, self.satisfaction + satisfaction_change))
        
        if self.intimacy_level == IntimacyLevel.NONE:
            self.intimacy_level = IntimacyLevel.INTIMATE
        elif self.times_intimate >= 5 and self.intimacy_level == IntimacyLevel.INTIMATE:
            self.intimacy_level = IntimacyLevel.REGULAR_PARTNER


class IntimateSystem:
    def __init__(self):
        self.intimate_relationships: Dict[tuple, IntimateRelationship] = {}
    
    def _get_key(self, person_a: str, person_b: str) -> tuple:
        return tuple(sorted([person_a, person_b]))
    
    def get_intimate_relationship(self, person_a: str, person_b: str) -> Optional[IntimateRelationship]:
        key = self._get_key(person_a, person_b)
        if key not in self.intimate_relationships:
            self.intimate_relationships[key] = IntimateRelationship(person_a=key[0], person_b=key[1])
        return self.intimate_relationships[key]
    
    def record_first_kiss(self, person_a: str, person_b: str, day: int):
        rel = self.get_intimate_relationship(person_a, person_b)
        if rel.intimacy_level == IntimacyLevel.NONE:
            rel.intimacy_level = IntimacyLevel.KISSED
    
    def record_intimate_encounter(self, person_a: str, person_b: str, day: int):
        rel = self.get_intimate_relationship(person_a, person_b)
        rel.record_intimate_encounter(day)
    
    def get_intimacy_summary(self, person_a: str, person_b: str) -> str:
        rel = self.get_intimate_relationship(person_a, person_b)
        return f"{person_a} & {person_b}: {rel.intimacy_level.name}, {rel.times_intimate} times, Satisfaction: {rel.satisfaction:.0f}/100"
