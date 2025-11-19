# systems/growth_development_system.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from core.time_system import TimeSystem
from entities.npc import NPC


@dataclass
class DevelopmentState:
    npc_name: str
    stage: str = "adult"  # child, preteen, teen, young_adult, adult, elder
    last_checked_age: int = 0


class GrowthDevelopmentSystem:
    """
    Tracks life-stage transitions and provides a clean 'stage' for each NPC.
    """

    def __init__(self, time: TimeSystem):
        self.time = time
        self.states: Dict[str, DevelopmentState] = {}

    def ensure_npc(self, npc: NPC):
        if npc.full_name not in self.states:
            self.states[npc.full_name] = DevelopmentState(
                npc_name=npc.full_name,
                stage=self._stage_for_age(npc.age),
                last_checked_age=npc.age,
            )

    def _stage_for_age(self, age: int) -> str:
        if age < 12:
            return "child"
        if age < 15:
            return "preteen"
        if age < 19:
            return "teen"
        if age < 30:
            return "young_adult"
        if age < 60:
            return "adult"
        return "elder"

    def get_stage(self, npc: NPC) -> str:
        self.ensure_npc(npc)
        return self.states[npc.full_name].stage

    def update_for_year(self, npcs):
        """
        Call this roughly when age increments, or once per in-world year.
        """
        for npc in npcs:
            self.ensure_npc(npc)
            st = self.states[npc.full_name]
            new_stage = self._stage_for_age(npc.age)
            if new_stage != st.stage:
                st.stage = new_stage
                st.last_checked_age = npc.age
                # You can hook into this to adjust traits, goals, etc.
