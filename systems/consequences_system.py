# systems/consequences_system.py
# Consequences of actions (pregnancy outcomes, drama, etc.)

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ConsequenceType(Enum):
    PREGNANCY_OUTCOME = "pregnancy_outcome"
    JEALOUSY_DRAMA = "jealousy_drama"
    CAUGHT_CHEATING = "caught_cheating"
    REPUTATION_CHANGE = "reputation_change"


@dataclass
class Consequence:
    consequence_type: ConsequenceType
    description: str
    affected_characters: List[str]
    severity: int
    day_triggered: int
    resolved: bool = False


class ConsequencesSystem:
    def __init__(self):
        self.active_consequences: List[Consequence] = []
    
    def trigger_caught_cheating(
        self,
        cheater: str,
        partner: str,
        caught_with: str,
        current_day: int,
        relationship_manager,
        reputation_system
    ):
        consequence = Consequence(
            consequence_type=ConsequenceType.CAUGHT_CHEATING,
            description=f"{partner} caught {cheater} with {caught_with}!",
            affected_characters=[cheater, partner, caught_with],
            severity=10,
            day_triggered=current_day
        )
        self.active_consequences.append(consequence)
        
        # Apply effects
        rel = relationship_manager.get_relationship(cheater, partner)
        rel.romantic_points = max(0, rel.romantic_points - 50)
        rel.trust = max(0, rel.trust - 80)
        
        reputation_system.handle_action_reputation(cheater, "caught_cheating", witness=partner)
