# systems/health_disease_system.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from core.time_system import TimeSystem
from entities.npc import NPC
import random


@dataclass
class Disease:
    name: str
    duration_days: int
    contagion_chance: float  # per contact
    severity: float          # how much it drains energy per day
    days_sick: int = 0


class HealthDiseaseSystem:
    """
    Simple health & disease simulation.
    - Some NPCs get sick randomly
    - Disease spreads to others in same location
    - Affects needs (energy, fun, social)
    """

    def __init__(self, time: TimeSystem):
        self.time = time
        self.active: Dict[str, List[Disease]] = {}
        self.catalog = {
            "common_cold": Disease("Common Cold", duration_days=7, contagion_chance=0.10, severity=5.0),
            "flu": Disease("Flu", duration_days=10, contagion_chance=0.20, severity=10.0),
        }

    def get_diseases(self, npc: NPC) -> List[Disease]:
        return self.active.get(npc.full_name, [])

    def infect(self, npc: NPC, disease_key: str):
        if disease_key not in self.catalog:
            return
        current = self.active.setdefault(npc.full_name, [])
        # Avoid duplicating same disease
        if any(d.name == self.catalog[disease_key].name for d in current):
            return
        # Create a copy
        base = self.catalog[disease_key]
        current.append(Disease(base.name, base.duration_days, base.contagion_chance, base.severity))

    def update_for_day(self, npcs: List[NPC], location_map: Dict[str, List[NPC]]):
        # Random primary infections
        for npc in npcs:
            if random.random() < 0.001:  # 0.1% daily baseline
                self.infect(npc, "common_cold")

        # Spread in shared locations
        for loc, occupants in location_map.items():
            sick = [n for n in occupants if self.get_diseases(n)]
            healthy = [n for n in occupants if not self.get_diseases(n)]
            if not sick or not healthy:
                continue
            for s in sick:
                for h in healthy:
                    for d in self.get_diseases(s):
                        if random.random() < d.contagion_chance:
                            self.infect(h, "common_cold")

        # Progress and recovery
        for npc in npcs:
            lst = self.active.get(npc.full_name, [])
            if not lst:
                continue
            still = []
            for d in lst:
                d.days_sick += 1
                # Apply effects
                if hasattr(npc, "needs"):
                    npc.needs.energy = max(0.0, npc.needs.energy - d.severity)
                    npc.needs.fun = max(0.0, npc.needs.fun - d.severity * 0.3)
                    npc.needs.social = max(0.0, npc.needs.social - d.severity * 0.2)
                if d.days_sick < d.duration_days:
                    still.append(d)
            if still:
                self.active[npc.full_name] = still
            else:
                self.active.pop(npc.full_name, None)
