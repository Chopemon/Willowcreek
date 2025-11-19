# systems/micro_interactions_system.py
"""
MicroInteractionsSystem v1.1 - CONTEXTUALLY AWARE
- Tiny moment-to-moment social nudges between NPCs
- Interaction type is now biased by the existing relationship score.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from core.time_system import TimeSystem
    from entities.npc import NPC
    from systems.emotional_contagion import EmotionalContagionSystem
    from systems.relationships import RelationshipManager


@dataclass
class MicroInteraction:
    kind: str
    a: str
    b: str
    location: str


class MicroInteractionsSystem:
    def __init__(
        self,
        time: "TimeSystem",
        emotional: "EmotionalContagionSystem",
        relationships: "RelationshipManager",
    ):
        self.time = time
        self.emotional = emotional
        self.relationships = relationships
        self.recent: List[MicroInteraction] = []

    def _log(self, kind: str, a: "NPC", b: "NPC", loc: str):
        mi = MicroInteraction(kind=kind, a=a.full_name, b=b.full_name, location=loc)
        self.recent.append(mi)
        if len(self.recent) > 100:
            self.recent.pop(0)

    # -------------------------------------------------------------
    # NEW: CONTEXTUAL BIAS HELPER
    # -------------------------------------------------------------
    def _get_interaction_threshold(self, a: "NPC", b: "NPC") -> float:
        """
        Calculates a probability threshold (0.0 to 1.0) for a positive interaction.
        Uses the existing relationship score to bias the chance.
        """
        # Ensure RelationshipManager has the expected method
        if not hasattr(self.relationships, 'get_score'):
            return 0.5 # Default to 50/50 if relationship data is inaccessible

        # Assuming get_score returns a value on a scale, e.g., 0 to 100
        score = self.relationships.get_score(a.full_name, b.full_name)
        
        # Normalize the 0-100 score to a 0.0-1.0 probability threshold:
        # Score 0 -> Threshold ~0.2 (20% chance of positive/warm)
        # Score 50 -> Threshold 0.5 (50% chance)
        # Score 100 -> Threshold ~0.8 (80% chance)
        
        # Simple linear mapping with a slightly flattened curve for less extremism:
        # The range is 0.2 to 0.8
        min_p = 0.2
        max_p = 0.8
        
        normalized_score = max(0, min(100, score)) / 100.0
        
        return min_p + (normalized_score * (max_p - min_p))
        
    # -------------------------------------------------------------
    # UPDATED: update_step now uses the contextual threshold
    # -------------------------------------------------------------
    def update_step(self, npcs: List["NPC"], location_map: Dict[str, List["NPC"]]):
        for loc, occupants in location_map.items():
            if len(occupants) < 2:
                continue
            if random.random() > 0.05:  # 5% chance per location per step
                continue

            a, b = random.sample(occupants, k=2)
            
            # Get the probability threshold for a positive interaction (warm_glance)
            threshold = self._get_interaction_threshold(a, b)
            
            roll = random.random()

            try:
                # If the roll is BELOW the threshold, it is a positive (warm) interaction
                if roll < threshold:
                    kind = "warm_glance"
                    self._log(kind, a, b, loc)
                    self.emotional.seed_emotion(a, "warmth", intensity=0.15)
                    self.emotional.seed_emotion(b, "warmth", intensity=0.10)
                    # optional relationship nudge
                    if hasattr(self.relationships, "adjust_relationship"):
                        self.relationships.adjust_relationship(a.full_name, b.full_name, delta=1)
                else:
                    # If the roll is ABOVE the threshold, it is a negative (awkward) interaction
                    kind = "awkward_moment"
                    self._log(kind, a, b, loc)
                    self.emotional.seed_emotion(a, "embarrassment", intensity=0.15)
                    self.emotional.seed_emotion(b, "embarrassment", intensity=0.15)
                    # optional relationship nudge (use -1 for negative interactions)
                    if hasattr(self.relationships, "adjust_relationship"):
                         self.relationships.adjust_relationship(a.full_name, b.full_name, delta=-1) 

            except Exception as e:
                # print(f"[MicroInteractions] error: {e}") # Keep commented out unless debugging
                pass