# systems/aging_system.py
# Aging and death mechanics.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import random

from entities.npc import NPC


@dataclass
class AgingState:
    npc_name: str
    last_age_update_day: int = 0
    deceased: bool = False


class AgingSystem:
    """
    Advances age annually and applies mortality checks.
    """

    def __init__(self):
        self.states: Dict[str, AgingState] = {}

    def ensure_npc(self, npc: NPC) -> AgingState:
        if npc.full_name not in self.states:
            self.states[npc.full_name] = AgingState(npc_name=npc.full_name)
        return self.states[npc.full_name]

    def update_for_day(self, npcs: List[NPC], current_day: int) -> List[str]:
        events: List[str] = []
        for npc in npcs:
            state = self.ensure_npc(npc)
            if state.deceased:
                continue

            if current_day - state.last_age_update_day >= 365:
                npc.age += 1
                state.last_age_update_day = current_day

            if self._mortality_check(npc.age):
                npc.status = "deceased"
                state.deceased = True
                events.append(f"{npc.full_name} passed away at age {npc.age}.")
        return events

    def _mortality_check(self, age: int) -> bool:
        if age < 60:
            return False
        chance = min(0.15, (age - 55) / 200.0)
        return random.random() < chance
