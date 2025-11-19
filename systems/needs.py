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
        Actual location is resolved in AutonomousSystem.
        """
        n = npc.needs

        # Immediate criticals
        if n.bladder > 85:
            return {"action": "bathroom", "location": "Bathroom"}

        if n.hygiene < 20:
            return {"action": "shower", "location": "Bathroom"}

        if n.energy < 25:
            return {"action": "sleep", "location": "Bedroom"}

        if n.hunger > 75:
            return {"action": "eat", "location": "Kitchen"}

        # Secondary needs
        if n.social < 30:
            return {"action": "socialize", "location": "Public"}

        if n.fun < 30:
            return {"action": "fun", "location": "Public"}

        # Horny is handled by Emotional/Autonomous private logic
        if n.horny > 85:
            return {"action": "privacy", "location": "Bedroom"}

        return {"action": "free_time", "location": None}
