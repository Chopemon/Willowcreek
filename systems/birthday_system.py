# systems/birthday_system.py
"""
Birthday & Aging System v1.0
- Assigns each NPC a stable birthday (day-of-year, 0–364)
- Increments age once per year on their birthday
- Optionally logs a memory if MemorySystem supports it
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC
    from systems.memory_system import MemorySystem


@dataclass
class BirthdayRecord:
    npc_name: str
    day_of_year: int           # 0–364
    last_celebrated_day: int = -9999  # world total_days when last processed


class BirthdaySystem:
    def __init__(self, time: "TimeSystem", memory_system: Optional["MemorySystem"] = None):
        self.time = time
        self.memory = memory_system
        self.birthdays: Dict[str, BirthdayRecord] = {}

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------
    def register_npcs(self, npcs: List["NPC"]):
        """Ensure every NPC has a stable birthday."""
        for npc in npcs:
            if npc.full_name in self.birthdays:
                continue

            rng = random.Random(npc.full_name)  # stable per name
            day_of_year = rng.randint(0, 364)

            self.birthdays[npc.full_name] = BirthdayRecord(
                npc_name=npc.full_name,
                day_of_year=day_of_year,
                last_celebrated_day=-9999,
            )

    def _current_day_of_year(self) -> int:
        return self.time.total_days % 365

    # ------------------------------------------------------------------
    # DAILY UPDATE
    # ------------------------------------------------------------------
    def update_for_day(self, npcs: List["NPC"]) -> List[str]:
        """Call once per in-game day when day changes."""
        if not npcs:
            return []

        today_index = self._current_day_of_year()
        today_world_day = self.time.total_days
        had_birthdays: List[str] = []

        self.register_npcs(npcs)

        for npc in npcs:
            rec = self.birthdays.get(npc.full_name)
            if not rec:
                continue

            if rec.day_of_year != today_index:
                continue
            if rec.last_celebrated_day == today_world_day:
                continue

            old_age = npc.age
            npc.age = old_age + 1
            rec.last_celebrated_day = today_world_day
            had_birthdays.append(npc.full_name)

            # Optional memory hook
            if self.memory is not None:
                try:
                    location = getattr(npc, "current_location", "Unknown")
                    add_mem = getattr(self.memory, "add_memory", None)
                    if callable(add_mem):
                        add_mem(
                            npc_name=npc.full_name,
                            content=f"Birthday in Willow Creek (turned {npc.age}).",
                            memory_type="life_event",
                            importance="significant",
                            current_day=today_world_day,
                            emotions_felt=["joy"],
                            people_involved=[],
                            location=location,
                        )
                except Exception as e:
                    print(f"[BirthdaySystem] Memory logging failed for {npc.full_name}: {e}")

        if had_birthdays:
            print(f"🎂 BIRTHDAYS TODAY: {', '.join(had_birthdays)}")

        return had_birthdays

    def get_upcoming_birthdays(self, within_days: int = 7) -> Dict[int, List[str]]:
        result: Dict[int, List[str]] = {}
        if not self.birthdays:
            return result

        current_day_index = self._current_day_of_year()
        for rec in self.birthdays.values():
            diff = (rec.day_of_year - current_day_index) % 365
            if 0 < diff <= within_days:
                result.setdefault(diff, []).append(rec.npc_name)
        return result

    def export_state(self) -> Dict:
        return {
            "birthdays": [
                {
                    "npc_name": rec.npc_name,
                    "day_of_year": rec.day_of_year,
                    "last_celebrated_day": rec.last_celebrated_day,
                }
                for rec in self.birthdays.values()
            ]
        }
