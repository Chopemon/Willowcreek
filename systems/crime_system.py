# systems/crime_system.py
"""
CrimeSystem v1.0
- Models petty crime & town incidents
- Hooks into ReputationSystem and ConsequenceCascadesSystem
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC
    from systems.reputation_system import ReputationSystem
    from systems.consequence_cascades import ConsequenceCascadesSystem


@dataclass
class CrimeEvent:
    kind: str
    actor: str
    location: str
    payload: Dict[str, Any]


class CrimeSystem:
    def __init__(
        self,
        time: "TimeSystem",
        reputation: "ReputationSystem",
        consequences: "ConsequenceCascadesSystem",
    ):
        self.time = time
        self.reputation = reputation
        self.consequences = consequences
        self.recent_crimes: List[CrimeEvent] = []

    def _record(self, kind: str, actor: "NPC", location: str, payload: Dict[str, Any] | None = None):
        payload = payload or {}
        ce = CrimeEvent(kind=kind, actor=actor.full_name, location=location, payload=payload)
        self.recent_crimes.append(ce)
        if len(self.recent_crimes) > 50:
            self.recent_crimes.pop(0)

        try:
            self.consequences.record_event(kind, [actor], location, payload)
        except Exception as e:
            print(f"[CrimeSystem] Consequence cascade failed: {e}")

    def _is_high_risk_location(self, loc: str) -> bool:
        loc = loc.lower()
        return any(k in loc for k in ["mall", "park", "alley", "downtown", "bowling"])

    def update_step(self, npcs: List["NPC"], location_map: Dict[str, List["NPC"]]):
        hour = self.time.hour
        night = hour >= 21 or hour < 5

        for loc, occupants in location_map.items():
            if not occupants:
                continue

            # Very small base chance per location
            base = 0.001
            if self._is_high_risk_location(loc):
                base *= 4
            if night:
                base *= 3

            if random.random() >= base:
                continue

            actor = random.choice(occupants)
            # Petty theft / vandalism flavour
            kind = random.choice(["petty_theft", "vandalism", "shoplifting"])
            self._record(kind, actor, loc, {"time": hour})

            # Small reputation penalty
            try:
                self.reputation.adjust_reputation(actor.full_name, delta=-3)
            except Exception:
                pass

    def update_for_day(self, npcs: List["NPC"]):
        # Could add daily investigations / follow-up here later
        pass
