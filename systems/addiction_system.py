# systems/addiction_system.py
"""
AddictionSystem v1.0
- Tracks per-NPC addiction states
- Handles cravings, withdrawal, and subtle need impacts
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC


@dataclass
class AddictionState:
    substance: str
    severity: float        # 0–1
    days_since_use: int = 0
    craving: float = 0.0   # 0–100


class AddictionSystem:
    def __init__(self, time: "TimeSystem"):
        self.time = time
        self.states: Dict[str, AddictionState] = {}

    def get_state(self, npc: "NPC") -> AddictionState | None:
        return self.states.get(npc.full_name)

    def add_addiction(self, npc: "NPC", substance: str, severity: float = 0.5):
        self.states[npc.full_name] = AddictionState(
            substance=substance,
            severity=max(0.0, min(1.0, severity)),
            days_since_use=0,
            craving=20.0 * severity,
        )

    def record_use(self, npc: "NPC"):
        st = self.states.get(npc.full_name)
        if not st:
            return
        st.days_since_use = 0
        st.craving = max(5.0, st.craving * 0.5)

    # ------------------------------------------------------------------
    # STEP-LEVEL
    # ------------------------------------------------------------------
    def update_step(self, npcs):
        # Step-level we keep it light
        for npc in npcs:
            st = self.states.get(npc.full_name)
            if not st:
                continue

            # Small random mood impact from cravings
            if st.craving > 50.0 and hasattr(npc, "needs"):
                npc.needs.fun = max(0.0, npc.needs.fun - 0.3 * st.severity)
                npc.needs.energy = max(0.0, npc.needs.energy - 0.2 * st.severity)

    # ------------------------------------------------------------------
    # DAILY
    # ------------------------------------------------------------------
    def update_for_day(self, npcs):
        for npc in npcs:
            st = self.states.get(npc.full_name)
            if not st:
                continue
            st.days_since_use += 1
            # Craving rises with time since use & severity
            st.craving = min(100.0, st.craving + 2.0 + 3.0 * st.severity)

            # If craving very high, more serious impacts
            if hasattr(npc, "needs"):
                if st.craving > 70.0:
                    npc.needs.energy = max(0.0, npc.needs.energy - 3.0 * st.severity)
                    npc.needs.fun = max(0.0, npc.needs.fun - 2.0 * st.severity)
                    npc.needs.social = max(0.0, npc.needs.social - 1.0 * st.severity)
