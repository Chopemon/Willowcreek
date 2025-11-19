# systems/female_biology_system.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from core.time_system import TimeSystem
from entities.npc import NPC, Gender


@dataclass
class CycleState:
    npc_name: str
    cycle_length: int = 28         # days
    day_in_cycle: int = 0          # 0..cycle_length-1
    last_updated_day: int = 0
    phase: str = "follicular"      # follicular, ovulation, luteal, menstruation

    def update_phase(self):
        # Simple approximate phase mapping
        d = self.day_in_cycle
        if d < 4:
            self.phase = "menstruation"
        elif d < 13:
            self.phase = "follicular"
        elif d < 16:
            self.phase = "ovulation"
        else:
            self.phase = "luteal"


class FemaleBiologySystem:
    """
    Tracks menstrual cycles for female NPCs.
    Provides:
      - per-NPC CycleState
      - ovulation window
      - simple mood hooks (optionally used by other systems)
    """

    def __init__(self, time: TimeSystem):
        self.time = time
        self.cycles: Dict[str, CycleState] = {}

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def ensure_npc(self, npc: NPC):
        if npc.gender != Gender.FEMALE:
            return
        if npc.full_name not in self.cycles:
            # Randomize offset so everyone isn't in sync
            offset = (hash(npc.full_name) % 28)
            self.cycles[npc.full_name] = CycleState(
                npc_name=npc.full_name,
                cycle_length=28,
                day_in_cycle=offset,
                last_updated_day=self.time.total_days,
            )
            self.cycles[npc.full_name].update_phase()

    def get_cycle(self, npc: NPC) -> Optional[CycleState]:
        return self.cycles.get(npc.full_name)

    def is_fertile_window(self, npc: NPC) -> bool:
        """
        Returns True if NPC is in (rough) fertile window.
        Other systems (pregnancy) can use this.
        """
        cs = self.get_cycle(npc)
        if not cs:
            return False
        # Rough 6-day fertility window around ovulation
        return cs.phase in ("ovulation", "late_follicular", "early_luteal") or (
            10 <= cs.day_in_cycle <= 16
        )

    # ------------------------------------------------------------------
    # UPDATE LOOP
    # ------------------------------------------------------------------
    def update_for_day(self, npcs):
        """
        Call this once per in-game day.
        """
        current_day = self.time.total_days
        for npc in npcs:
            if npc.gender != Gender.FEMALE:
                continue

            self.ensure_npc(npc)
            cs = self.cycles[npc.full_name]

            if cs.last_updated_day < current_day:
                # Advance one or more days
                delta = current_day - cs.last_updated_day
                cs.day_in_cycle = (cs.day_in_cycle + delta) % cs.cycle_length
                cs.last_updated_day = current_day
                cs.update_phase()

                # Optional hooks: slight mood tweaks
                # You can tune these as you like.
                if hasattr(npc, "psyche"):
                    if cs.phase == "menstruation":
                        npc.psyche.lonely = min(100.0, npc.psyche.lonely + 5.0)
                    elif cs.phase == "ovulation":
                        npc.needs.social = min(100.0, npc.needs.social + 3.0)
