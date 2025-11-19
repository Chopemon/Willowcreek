# systems/needs.py
"""
Needs System — cleaned and unified.
Returns semantic targets ("Home", "Kitchen", "Public") rather than physical locations.
AutonomousSystem handles mapping using households.get_household().
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class NPCNeeds:
    hunger: float = 50
    energy: float = 80
    hygiene: float = 60
    bladder: float = 60
    fun: float = 50
    social: float = 50
    horny: float = 30

    def dominant(self) -> str:
        vals = {
            "hunger": self.hunger,
            "energy": self.energy,
            "hygiene": self.hygiene,
            "bladder": self.bladder,
            "fun": self.fun,
            "social": self.social,
            "horny": self.horny,
        }
        return max(vals, key=vals.get)


class NeedsSystem:
    def __init__(self):
        self.rates = {
            "hunger": 1.0,
            "energy": 0.8,
            "hygiene": 0.4,
            "bladder": 0.5,
            "fun": 0.6,
            "social": 0.4,
            "horny": 0.7,
        }

    def process_needs(self, npcs, hours: float):
        for npc in npcs:
            n = npc.needs

            n.hunger += self.rates["hunger"] * hours * 8
            n.energy -= self.rates["energy"] * hours * 5
            n.hygiene -= self.rates["hygiene"] * hours * 4
            n.bladder += self.rates["bladder"] * hours * 6
            n.fun -= self.rates["fun"] * hours * 2
            n.social -= self.rates["social"] * hours * 2
            n.horny += self.rates["horny"] * hours * 3

            # Clamp
            for attr in vars(n):
                val = getattr(n, attr)
                setattr(n, attr, max(0, min(100, val)))

    def suggest_action(self, npc):
        """
        Returns a dict with:
        - action: "eat", "sleep", "bathroom", "shower", "fun", "social", or "free_time"
        - location: SEMANTIC target: "Kitchen", "Bedroom", "Bathroom", "Public", etc.

        NOTE: These thresholds determine CRITICAL needs that override scheduled activities
        (school, work, etc.). Thresholds are set high to prevent NPCs from abandoning
        their schedules unless they're in genuine distress.

        Actual location is resolved in AutonomousSystem.
        """
        n = npc.needs

        # CRITICAL EMERGENCIES ONLY - these override school/work
        # Bladder emergency
        if n.bladder > 90:
            return {"action": "bathroom", "location": "Bathroom"}

        # Extreme exhaustion - about to pass out
        if n.energy < 15:
            return {"action": "sleep", "location": "Bedroom"}

        # Severe hygiene problem
        if n.hygiene < 10:
            return {"action": "shower", "location": "Bathroom"}

        # Starvation level hunger
        if n.hunger > 90:
            return {"action": "eat", "location": "Kitchen"}

        # Severe social isolation
        if n.social < 15:
            return {"action": "socialize", "location": "Public"}

        # Extreme boredom/depression
        if n.fun < 15:
            return {"action": "fun", "location": "Public"}

        # Horny is handled by Emotional/Autonomous private logic
        if n.horny > 90:
            return {"action": "privacy", "location": "Bedroom"}

        # No critical needs - follow schedule
        return {"action": "free_time", "location": None}
