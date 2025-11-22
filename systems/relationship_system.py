# systems/relationship_system.py
# Deep relationship mechanics with friendship/romance levels, attraction, compatibility

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random


class RelationshipStatus(Enum):
    """Relationship status levels"""
    STRANGER = 0
    ACQUAINTANCE = 1
    FRIEND = 2
    CLOSE_FRIEND = 3
    BEST_FRIEND = 4
    ROMANTIC_INTEREST = 5
    DATING = 6
    COMMITTED = 7
    MARRIED = 8


class AttractionLevel(Enum):
    """Physical/romantic attraction levels"""
    NONE = 0
    SLIGHT = 1
    MODERATE = 2
    STRONG = 3
    INTENSE = 4


@dataclass
class Relationship:
    """Relationship between two people"""
    person_a: str
    person_b: str
    
    # Friendship metrics
    friendship_points: float = 0.0  # 0-100
    trust: float = 50.0              # 0-100
    respect: float = 50.0            # 0-100
    
    # Romance metrics  
    romantic_points: float = 0.0     # 0-100
    attraction: AttractionLevel = AttractionLevel.NONE
    chemistry: float = 0.0           # 0-100, calculated from compatibility
    
    # Status
    status: RelationshipStatus = RelationshipStatus.STRANGER
    
    # Tracking
    times_talked: int = 0
    times_dated: int = 0
    gifts_exchanged: int = 0
    conflicts: int = 0
    days_since_last_interaction: int = 0
    
    # Special states
    is_intimate: bool = False
    first_kiss_day: int = -1
    first_intimate_day: int = -1
    
    # Jealousy/drama
    jealousy_level: float = 0.0      # 0-100
    
    def get_friendship_level(self) -> str:
        """Get friendship level name"""
        if self.friendship_points >= 80:
            return "Best Friends"
        elif self.friendship_points >= 60:
            return "Close Friends"
        elif self.friendship_points >= 40:
            return "Friends"
        elif self.friendship_points >= 20:
            return "Acquaintances"
        else:
            return "Strangers"
    
    def get_romance_level(self) -> str:
        """Get romance level name"""
        if self.status in [RelationshipStatus.MARRIED, RelationshipStatus.COMMITTED]:
            return self.status.name.title()
        elif self.status == RelationshipStatus.DATING:
            return "Dating"
        elif self.status == RelationshipStatus.ROMANTIC_INTEREST:
            return "Romantic Interest"
        elif self.romantic_points >= 60:
            return "Strong Attraction"
        elif self.romantic_points >= 30:
            return "Mild Attraction"
        else:
            return "No Romance"
    
    def decay_over_time(self, days: int):
        """Relationships decay if not maintained"""
        decay_rate = 0.5 * days  # 0.5 points per day
        self.friendship_points = max(0, self.friendship_points - decay_rate)
        self.romantic_points = max(0, self.romantic_points - decay_rate * 0.7)
        self.days_since_last_interaction += days


class RelationshipManager:
    """Manages all relationships in the game"""
    
    def __init__(self):
        # Store as (person_a, person_b) tuple key
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        
    def _get_key(self, person_a: str, person_b: str) -> Tuple[str, str]:
        """Get consistent key for relationship (alphabetical order)"""
        return tuple(sorted([person_a, person_b]))
    
    def get_relationship(self, person_a: str, person_b: str) -> Relationship:
        """Get or create relationship"""
        key = self._get_key(person_a, person_b)
        if key not in self.relationships:
            self.relationships[key] = Relationship(person_a=key[0], person_b=key[1])
        return self.relationships[key]
    
    def add_friendship(self, person_a: str, person_b: str, amount: float):
        """Add friendship points"""
        rel = self.get_relationship(person_a, person_b)
        rel.friendship_points = min(100, rel.friendship_points + amount)
        rel.days_since_last_interaction = 0
        
        # Auto-upgrade status
        if rel.friendship_points >= 80 and rel.status.value < RelationshipStatus.BEST_FRIEND.value:
            rel.status = RelationshipStatus.BEST_FRIEND
        elif rel.friendship_points >= 60 and rel.status.value < RelationshipStatus.CLOSE_FRIEND.value:
            rel.status = RelationshipStatus.CLOSE_FRIEND
        elif rel.friendship_points >= 40 and rel.status.value < RelationshipStatus.FRIEND.value:
            rel.status = RelationshipStatus.FRIEND
        elif rel.friendship_points >= 20 and rel.status == RelationshipStatus.STRANGER:
            rel.status = RelationshipStatus.ACQUAINTANCE
    
    def add_romance(self, person_a: str, person_b: str, amount: float):
        """Add romantic points"""
        rel = self.get_relationship(person_a, person_b)
        rel.romantic_points = min(100, rel.romantic_points + amount)
        rel.days_since_last_interaction = 0
        
        # Auto-upgrade to romantic interest
        if rel.romantic_points >= 30 and rel.status.value < RelationshipStatus.ROMANTIC_INTEREST.value:
            rel.status = RelationshipStatus.ROMANTIC_INTEREST
    
    def start_dating(self, person_a: str, person_b: str) -> bool:
        """Start dating relationship. Returns success."""
        rel = self.get_relationship(person_a, person_b)
        
        # Need minimum romance and friendship
        if rel.romantic_points < 40 or rel.friendship_points < 30:
            return False
        
        rel.status = RelationshipStatus.DATING
        return True
    
    def commit_relationship(self, person_a: str, person_b: str) -> bool:
        """Commit to exclusive relationship"""
        rel = self.get_relationship(person_a, person_b)
        
        if rel.status != RelationshipStatus.DATING:
            return False
        
        if rel.romantic_points < 70 or rel.friendship_points < 60:
            return False
        
        rel.status = RelationshipStatus.COMMITTED
        return True
    
    def calculate_compatibility(self, npc1, npc2) -> float:
        """
        Calculate compatibility between two NPCs based on traits.
        Returns 0-100 score.
        """
        score = 50.0  # Base compatibility
        
        # Age difference (prefer similar ages)
        age_diff = abs(npc1.age - npc2.age)
        if age_diff <= 3:
            score += 15
        elif age_diff <= 7:
            score += 5
        elif age_diff > 15:
            score -= 10
        
        # Random personality compatibility (would need trait system)
        score += random.uniform(-20, 20)
        
        return max(0, min(100, score))
    
    def calculate_attraction(self, from_npc, to_npc) -> AttractionLevel:
        """
        Calculate physical attraction level.
        This is one-directional (A attracted to B != B attracted to A)
        """
        # Base on age appropriateness, random chance, etc.
        age_appropriate = abs(from_npc.age - to_npc.age) <= 15
        
        if not age_appropriate:
            return AttractionLevel.NONE
        
        # Random attraction roll (would be based on appearance traits in full implementation)
        roll = random.randint(0, 100)
        
        if roll >= 90:
            return AttractionLevel.INTENSE
        elif roll >= 70:
            return AttractionLevel.STRONG
        elif roll >= 40:
            return AttractionLevel.MODERATE
        elif roll >= 20:
            return AttractionLevel.SLIGHT
        else:
            return AttractionLevel.NONE
    
    def record_interaction(self, person_a: str, person_b: str, interaction_type: str):
        """Record an interaction between two people"""
        rel = self.get_relationship(person_a, person_b)
        rel.days_since_last_interaction = 0
        
        if interaction_type == "talk":
            rel.times_talked += 1
            self.add_friendship(person_a, person_b, 2)
        elif interaction_type == "deep_talk":
            rel.times_talked += 1
            self.add_friendship(person_a, person_b, 5)
            rel.trust += 3
        elif interaction_type == "flirt":
            self.add_romance(person_a, person_b, 5)
        elif interaction_type == "date":
            rel.times_dated += 1
            self.add_romance(person_a, person_b, 10)
            self.add_friendship(person_a, person_b, 5)
        elif interaction_type == "kiss":
            self.add_romance(person_a, person_b, 15)
        elif interaction_type == "gift":
            rel.gifts_exchanged += 1
            self.add_friendship(person_a, person_b, 8)
            self.add_romance(person_a, person_b, 5)
        elif interaction_type == "conflict":
            rel.conflicts += 1
            rel.friendship_points = max(0, rel.friendship_points - 15)
            rel.trust = max(0, rel.trust - 20)
    
    def get_summary(self, person_a: str, person_b: str) -> str:
        """Get readable relationship summary"""
        rel = self.get_relationship(person_a, person_b)
        
        lines = [
            f"\nRelationship: {person_a} & {person_b}",
            f"Status: {rel.status.name.replace('_', ' ').title()}",
            f"Friendship: {rel.friendship_points:.0f}/100 ({rel.get_friendship_level()})",
            f"Romance: {rel.romantic_points:.0f}/100 ({rel.get_romance_level()})",
            f"Trust: {rel.trust:.0f}/100",
            f"Attraction: {rel.attraction.name}",
            f"Chemistry: {rel.chemistry:.0f}/100",
            f"\nInteractions:",
            f"  Talked: {rel.times_talked} times",
            f"  Dated: {rel.times_dated} times",
            f"  Gifts: {rel.gifts_exchanged}",
            f"  Conflicts: {rel.conflicts}",
            f"  Last interaction: {rel.days_since_last_interaction} days ago"
        ]
        
        return "\n".join(lines)
