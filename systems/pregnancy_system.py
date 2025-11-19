# systems/pregnancy_system.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from core.time_system import TimeSystem
from entities.npc import NPC, Gender
from systems.female_biology_system import FemaleBiologySystem


@dataclass
class PregnancyState:
    npc_name: str
    is_pregnant: bool = False
    days_pregnant: int = 0
    trimester: int = 0
    father_name: Optional[str] = None
    known_to_npc: bool = False
    due_day: Optional[int] = None


class PregnancySystem:
    """
    Handles conception probability and pregnancy progression.

    This system assumes EXTERNAL code calls `register_unprotected_intimacy`
    when appropriate. It does NOT parse chat text or explicit content.
    """

    def __init__(self, time: TimeSystem, female_biology: FemaleBiologySystem):
        self.time = time
        self.female_biology = female_biology
        self.states: Dict[str, PregnancyState] = {}

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def ensure_npc(self, npc: NPC):
        if npc.gender != Gender.FEMALE:
            return
        if npc.full_name not in self.states:
            self.states[npc.full_name] = PregnancyState(npc_name=npc.full_name)

    def get_state(self, npc: NPC) -> Optional[PregnancyState]:
        return self.states.get(npc.full_name)

    def register_unprotected_intimacy(self, npc: NPC, partner_name: str):
        """
        Call this externally when the story/simulation indicates
        a possible conception event (non-explicit).
        """
        if npc.gender != Gender.FEMALE:
            return

        self.ensure_npc(npc)
        ps = self.states[npc.full_name]
        if ps.is_pregnant:
            return  # already pregnant

        cs = self.female_biology.get_cycle(npc)
        if not cs:
            return

        # Simple fertility model: higher chance in fertile window
        if 10 <= cs.day_in_cycle <= 16:
            base_chance = 0.25
        elif 7 <= cs.day_in_cycle <= 19:
            base_chance = 0.10
        else:
            base_chance = 0.01

        import random
        if random.random() < base_chance:
            ps.is_pregnant = True
            ps.days_pregnant = 0
            ps.trimester = 1
            ps.father_name = partner_name
            ps.due_day = self.time.total_days + 280  # ~40 weeks
            ps.known_to_npc = False  # can be set true later by events

    # ------------------------------------------------------------------
    # UPDATE LOOP
    # ------------------------------------------------------------------
    def update_for_day(self, npcs):
        current_day = self.time.total_days
        for npc in npcs:
            if npc.gender != Gender.FEMALE:
                continue

            self.ensure_npc(npc)
            ps = self.states[npc.full_name]

            if not ps.is_pregnant:
                continue

            ps.days_pregnant += 1

            # Trimester shifts (roughly)
            if ps.days_pregnant < 13 * 7:
                ps.trimester = 1
            elif ps.days_pregnant < 26 * 7:
                ps.trimester = 2
            else:
                ps.trimester = 3

            # Simple physical/needs impact
            if hasattr(npc, "needs"):
                if ps.trimester == 1:
                    npc.needs.energy = max(0.0, npc.needs.energy - 2.0)
                elif ps.trimester == 2:
                    npc.needs.energy = max(0.0, npc.needs.energy - 1.0)
                elif ps.trimester == 3:
                    npc.needs.energy = max(0.0, npc.needs.energy - 3.0)
                    npc.needs.bladder = min(100.0, npc.needs.bladder + 3.0)

            # Birth event
            if ps.due_day is not None and current_day >= ps.due_day:
                # For now, simply mark pregnancy ended.
                ps.is_pregnant = False
                ps.days_pregnant = 0
                ps.trimester = 0
                ps.due_day = None
                # You can hook in here to spawn a baby NPC or mark family changes.
