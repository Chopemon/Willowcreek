# systems/dynamic_triggers.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List
from core.time_system import TimeSystem
from entities.npc import NPC


@dataclass
class DynamicTrigger:
    name: str
    chance: float
    condition: Callable[[TimeSystem, List[NPC]], bool]
    action: Callable[[TimeSystem, List[NPC]], None]


class DynamicTriggerSystem:
    """
    Simple dynamic triggers framework.
    You register triggers with a condition + action.
    Each update, conditions are checked and actions may fire.
    """

    def __init__(self, time: TimeSystem):
        self.time = time
        self.triggers: List[DynamicTrigger] = []

    def add_trigger(self, trig: DynamicTrigger):
        self.triggers.append(trig)

    def update(self, npcs: List[NPC]):
        import random
        for trig in self.triggers:
            if not trig.condition(self.time, npcs):
                continue
            if random.random() < trig.chance:
                trig.action(self.time, npcs)
