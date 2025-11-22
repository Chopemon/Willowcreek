# systems/reputation_system.py
# Reputation and gossip system

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random


class ReputationTrait(Enum):
    """Reputation traits (what people think of you)"""
    CHARMING = "charming"
    TRUSTWORTHY = "trustworthy"
    MYSTERIOUS = "mysterious"
    FRIENDLY = "friendly"
    FLIRTATIOUS = "flirtatious"
    PLAYER = "player"          # Dates many people
    GENEROUS = "generous"
    SELFISH = "selfish"
    RESPECTFUL = "respectful"
    CREEPY = "creepy"
    RELIABLE = "reliable"
    GOSSIP = "gossip"          # Spreads rumors
    DRAMA_MAGNET = "drama_magnet"


class GossipType(Enum):
    """Types of gossip"""
    RELATIONSHIP = "relationship"    # "Did you hear X is dating Y?"
    BREAKUP = "breakup"              # "X and Y broke up!"
    CHEATING = "cheating"            # "X was seen with Y!"
    PREGNANCY = "pregnancy"          # "I heard X is pregnant!"
    SCANDAL = "scandal"              # General scandal
    COMPLIMENT = "compliment"        # Positive gossip
    INSULT = "insult"                # Negative gossip
    OBSERVATION = "observation"      # "X was at the bar last night"


@dataclass
class Gossip:
    """A piece of gossip"""
    gossip_type: GossipType
    subject: str                     # Who it's about
    content: str                     # The gossip text
    source: str                      # Who started it
    spread_count: int = 0            # How many people know
    day_created: int = 0
    juiciness: int = 5               # 1-10, affects spread rate
    
    def spreads_to(self) -> bool:
        """Random chance gossip spreads further (based on juiciness)"""
        return random.randint(1, 10) <= self.juiciness


@dataclass
class Reputation:
    """A character's reputation"""
    character_name: str
    
    # Overall reputation score (-100 to +100)
    overall_score: float = 0.0
    
    # Trait scores (0-100, how strongly they have this trait)
    traits: Dict[ReputationTrait, float] = field(default_factory=dict)
    
    # Group-specific reputations
    group_scores: Dict[str, float] = field(default_factory=dict)
    
    # Notable events people know about
    known_facts: List[str] = field(default_factory=list)
    
    def add_trait(self, trait: ReputationTrait, amount: float):
        """Add to a reputation trait"""
        current = self.traits.get(trait, 0.0)
        self.traits[trait] = min(100, max(0, current + amount))
    
    def get_primary_traits(self, count: int = 3) -> List[ReputationTrait]:
        """Get top N reputation traits"""
        sorted_traits = sorted(
            self.traits.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [trait for trait, score in sorted_traits[:count] if score > 20]
    
    def get_reputation_summary(self) -> str:
        """Get readable reputation description"""
        if self.overall_score > 60:
            base = "highly respected"
        elif self.overall_score > 30:
            base = "well-liked"
        elif self.overall_score > -30:
            base = "neutral reputation"
        elif self.overall_score > -60:
            base = "somewhat disliked"
        else:
            base = "poor reputation"
        
        primary_traits = self.get_primary_traits(3)
        if primary_traits:
            trait_str = ", ".join([t.value for t in primary_traits])
            return f"{base} ({trait_str})"
        return base


class ReputationSystem:
    """Manages reputation and gossip"""
    
    def __init__(self):
        self.reputations: Dict[str, Reputation] = {}
        self.active_gossip: List[Gossip] = []
        self.gossip_network: Dict[str, List[Gossip]] = {}  # Who knows what gossip
    
    def get_reputation(self, character_name: str) -> Reputation:
        """Get or create character's reputation"""
        if character_name not in self.reputations:
            self.reputations[character_name] = Reputation(character_name=character_name)
        return self.reputations[character_name]
    
    def modify_reputation(self, character_name: str, amount: float, reason: str = ""):
        """Modify overall reputation"""
        rep = self.get_reputation(character_name)
        rep.overall_score = max(-100, min(100, rep.overall_score + amount))
        
        if reason:
            rep.known_facts.append(reason)
    
    def add_reputation_trait(self, character_name: str, trait: ReputationTrait, amount: float):
        """Add to a specific reputation trait"""
        rep = self.get_reputation(character_name)
        rep.add_trait(trait, amount)
    
    def create_gossip(
        self,
        gossip_type: GossipType,
        subject: str,
        content: str,
        source: str,
        juiciness: int,
        current_day: int
    ) -> Gossip:
        """Create new gossip"""
        gossip = Gossip(
            gossip_type=gossip_type,
            subject=subject,
            content=content,
            source=source,
            juiciness=juiciness,
            day_created=current_day
        )
        
        self.active_gossip.append(gossip)
        
        # Source knows the gossip
        if source not in self.gossip_network:
            self.gossip_network[source] = []
        self.gossip_network[source].append(gossip)
        
        return gossip
    
    def spread_gossip(self, gossip: Gossip, to_character: str):
        """Spread gossip to a character"""
        if to_character not in self.gossip_network:
            self.gossip_network[to_character] = []
        
        # Don't add duplicate
        if gossip not in self.gossip_network[to_character]:
            self.gossip_network[to_character].append(gossip)
            gossip.spread_count += 1
    
    def simulate_gossip_spread(self, all_npcs: List, current_day: int):
        """Simulate gossip spreading through the town"""
        for gossip in self.active_gossip:
            # Old gossip fades
            age = current_day - gossip.day_created
            if age > 7:  # Gossip older than a week fades
                continue
            
            # Each person who knows the gossip might spread it
            knowers = [npc for npc, gossips in self.gossip_network.items() if gossip in gossips]
            
            for knower in knowers:
                if gossip.spreads_to():
                    # Spread to random person
                    target = random.choice(all_npcs)
                    if target.full_name != knower:
                        self.spread_gossip(gossip, target.full_name)
    
    def get_gossip_about(self, subject: str) -> List[Gossip]:
        """Get all gossip about a character"""
        return [g for g in self.active_gossip if g.subject == subject]
    
    def character_knows_gossip(self, character_name: str, gossip: Gossip) -> bool:
        """Check if character knows specific gossip"""
        return character_name in self.gossip_network and gossip in self.gossip_network[character_name]
    
    def get_character_gossip(self, character_name: str, limit: int = 10) -> List[Gossip]:
        """Get gossip a character knows"""
        if character_name not in self.gossip_network:
            return []
        return self.gossip_network[character_name][-limit:]
    
    def handle_action_reputation(self, character_name: str, action: str, witness: Optional[str] = None):
        """Update reputation based on action"""
        rep = self.get_reputation(character_name)
        
        if action == "help_someone":
            self.modify_reputation(character_name, 5, f"{character_name} helped someone")
            self.add_reputation_trait(character_name, ReputationTrait.GENEROUS, 10)
            self.add_reputation_trait(character_name, ReputationTrait.FRIENDLY, 5)
        
        elif action == "flirt":
            self.add_reputation_trait(character_name, ReputationTrait.FLIRTATIOUS, 5)
            self.add_reputation_trait(character_name, ReputationTrait.CHARMING, 3)
        
        elif action == "caught_cheating":
            self.modify_reputation(character_name, -20, f"{character_name} was caught cheating")
            self.add_reputation_trait(character_name, ReputationTrait.PLAYER, 30)
            self.add_reputation_trait(character_name, ReputationTrait.TRUSTWORTHY, -40)
        
        elif action == "gift_giving":
            self.add_reputation_trait(character_name, ReputationTrait.GENEROUS, 8)
            self.add_reputation_trait(character_name, ReputationTrait.CHARMING, 5)
        
        elif action == "gossip":
            self.add_reputation_trait(character_name, ReputationTrait.GOSSIP, 10)
        
        elif action == "respectful":
            self.add_reputation_trait(character_name, ReputationTrait.RESPECTFUL, 8)
            self.modify_reputation(character_name, 3)
        
        elif action == "creepy":
            self.add_reputation_trait(character_name, ReputationTrait.CREEPY, 15)
            self.modify_reputation(character_name, -10)
    
    def get_summary(self, character_name: str) -> str:
        """Get reputation summary"""
        rep = self.get_reputation(character_name)
        
        lines = [
            f"\n{character_name}'s Reputation:",
            f"Overall: {rep.overall_score:.0f}/100 ({rep.get_reputation_summary()})",
            "\nKnown For:"
        ]
        
        for trait in rep.get_primary_traits(5):
            score = rep.traits[trait]
            lines.append(f"  {trait.value.title()}: {score:.0f}/100")
        
        gossip_about = self.get_gossip_about(character_name)
        if gossip_about:
            lines.append(f"\nGossip circulating: {len(gossip_about)} rumors")
        
        return "\n".join(lines)
