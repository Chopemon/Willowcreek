# systems/story_arc_system.py
# Procedural story arc generator.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import random


@dataclass
class StoryArc:
    title: str
    participants: List[str]
    stage: str = "setup"
    days_active: int = 0
    beats: List[str] = field(default_factory=list)

    def advance(self) -> None:
        self.days_active += 1
        if self.stage == "setup" and self.days_active >= 3:
            self.stage = "rising"
        elif self.stage == "rising" and self.days_active >= 7:
            self.stage = "climax"
        elif self.stage == "climax" and self.days_active >= 10:
            self.stage = "resolution"


class StoryArcSystem:
    """
    Generates long-term arcs and updates them over time.
    """

    def __init__(self):
        self.arcs: Dict[str, StoryArc] = {}

    def create_arc(self, title: str, participants: List[str]) -> StoryArc:
        arc = StoryArc(title=title, participants=participants)
        self.arcs[title] = arc
        return arc

    def seed_daily_arc(self, npc_names: List[str]) -> None:
        if not npc_names or len(self.arcs) >= 5:
            return
        p1 = random.choice(npc_names)
        p2 = random.choice([n for n in npc_names if n != p1])
        title = f"{p1} & {p2}: {random.choice(['rivalry', 'romance', 'mystery'])}"
        if title not in self.arcs:
            arc = self.create_arc(title, [p1, p2])
            arc.beats.append("A new tension emerges.")

    def update_for_day(self) -> None:
        for arc in list(self.arcs.values()):
            arc.advance()
            if arc.stage == "resolution" and arc.days_active >= 12:
                arc.beats.append("Arc resolved.")
