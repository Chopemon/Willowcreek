# systems/job_market_system.py
# Unemployment and job hunting behavior.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from systems.economy_system import EconomySystem, Job


@dataclass
class EmploymentStatus:
    npc_name: str
    unemployed_days: int = 0
    seeking_job: bool = True
    last_application_day: int = -1


class JobMarketSystem:
    """
    Tracks unemployment cycles and job hunting attempts.
    """

    def __init__(self, economy: EconomySystem):
        self.economy = economy
        self.statuses: Dict[str, EmploymentStatus] = {}

    def ensure_npc(self, npc_name: str) -> EmploymentStatus:
        if npc_name not in self.statuses:
            self.statuses[npc_name] = EmploymentStatus(npc_name=npc_name)
        return self.statuses[npc_name]

    def mark_unemployed(self, npc_name: str) -> None:
        status = self.ensure_npc(npc_name)
        status.seeking_job = True
        status.unemployed_days = 0

    def update_for_day(self, npc_names: List[str], current_day: int, skill_levels: Optional[Dict[str, Dict[str, int]]] = None) -> None:
        for name in npc_names:
            status = self.ensure_npc(name)
            if self.economy.get_job(name):
                status.unemployed_days = 0
                status.seeking_job = False
                continue

            status.unemployed_days += 1
            status.seeking_job = True

            if status.last_application_day == current_day:
                continue

            if status.unemployed_days >= 3:
                job = self._pick_job_for(name)
                if job:
                    levels = (skill_levels or {}).get(name, {})
                    if self.economy.apply_for_job(name, job, skill_levels=levels):
                        status.seeking_job = False
                        status.unemployed_days = 0
                status.last_application_day = current_day

    def _pick_job_for(self, npc_name: str) -> Optional[Job]:
        if not self.economy.available_jobs:
            return None
        return self.economy.available_jobs[hash(npc_name) % len(self.economy.available_jobs)]
