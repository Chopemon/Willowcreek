# systems/reputation_system.py
"""
Reputation & Gossip Network System v1.1
Purpose: Track social standing and information spread through the community.
Now neighbor-aware: neighbors gossip more and faster when sim.neighbor_map is available.
"""

from typing import Dict, List, Optional, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import random

if TYPE_CHECKING:
    from entities.npc import NPC
    from core.time_system import TimeSystem
    from core.simulation_v2 import WillowCreekSimulation


class SocialStatus(str, Enum):
    OUTCAST = "outcast"
    DISLIKED = "disliked"
    NORMAL = "normal"
    LIKED = "liked"
    POPULAR = "popular"
    RESPECTED = "respected"


@dataclass
class Reputation:
    """Individual NPC reputation data"""
    npc_name: str
    town_reputation: float = 50.0  # 0-100 scale
    known_secrets: List[str] = field(default_factory=list)
    gossip_about: List[str] = field(default_factory=list)
    social_status: SocialStatus = SocialStatus.NORMAL

    def update_status(self):
        """Update social status based on reputation score"""
        if self.town_reputation >= 85:
            self.social_status = SocialStatus.RESPECTED
        elif self.town_reputation >= 70:
            self.social_status = SocialStatus.POPULAR
        elif self.town_reputation >= 50:
            self.social_status = SocialStatus.LIKED
        elif self.town_reputation >= 30:
            self.social_status = SocialStatus.NORMAL
        elif self.town_reputation >= 15:
            self.social_status = SocialStatus.DISLIKED
        else:
            self.social_status = SocialStatus.OUTCAST

    def modify_reputation(self, amount: float):
        """Modify reputation with bounds checking"""
        self.town_reputation = max(0, min(100, self.town_reputation + amount))
        self.update_status()


@dataclass
class Gossip:
    """A piece of gossip spreading through the network"""
    about: str  # Person or people involved
    secret: str  # The actual gossip
    known_by: Set[str] = field(default_factory=set)  # NPCs who know
    spread_day: int = 0
    severity: int = 5  # 1-10, how damaging/juicy
    verified: bool = False  # Is it actually true?
    spread_rate: float = 0.3  # Base chance to spread per interaction
    decay_rate: float = 0.05  # How fast people forget

    def spread_to(self, npc_name: str, multiplier: float = 1.0) -> bool:
        """Attempt to spread gossip to an NPC with optional multiplier."""
        if npc_name in self.known_by:
            return False

        chance = min(1.0, self.spread_rate * multiplier)
        if random.random() < chance:
            self.known_by.add(npc_name)
            return True
        return False

    def decay(self):
        """Gossip fades over time"""
        if random.random() < self.decay_rate:
            if self.known_by:
                # Pop an arbitrary knower
                self.known_by.pop()


class ReputationSystem:
    """
    Manages reputation and gossip network.
    Tracks social standing and information spread.
    Now takes optional sim reference to use neighbor_map if available.
    """

    def __init__(self, sim: Optional["WillowCreekSimulation"] = None):
        self.sim = sim
        self.reputations: Dict[str, Reputation] = {}
        self.gossip_network: List[Gossip] = []
        self.life_events: List[Dict] = []
        self.initialized = False

    def attach_sim(self, sim: "WillowCreekSimulation"):
        """Optional helper if you want to attach sim after construction."""
        self.sim = sim

    def init_reputation(self, npc_name: str) -> Reputation:
        """Initialize reputation for an NPC"""
        if npc_name not in self.reputations:
            self.reputations[npc_name] = Reputation(npc_name=npc_name)
        return self.reputations[npc_name]

    def get_reputation(self, npc_name: str) -> Optional[Reputation]:
        """Get an NPC's reputation"""
        return self.reputations.get(npc_name)

    def modify_reputation(self, npc_name: str, amount: float, reason: str = ""):
        """Modify an NPC's reputation"""
        rep = self.init_reputation(npc_name)
        old_rep = rep.town_reputation
        rep.modify_reputation(amount)

        if reason:
            print(f"  {npc_name}'s reputation: {old_rep:.1f} -> {rep.town_reputation:.1f} ({reason})")

    def create_gossip(
        self,
        about: str,
        secret: str,
        initial_knowers: List[str],
        severity: int,
        spread_day: int,
        verified: bool = False
    ) -> Gossip:
        """Create and add gossip to the network"""
        gossip = Gossip(
            about=about,
            secret=secret,
            known_by=set(initial_knowers),
            spread_day=spread_day,
            severity=severity,
            verified=verified,
            spread_rate=min(0.5, 0.1 + (severity / 20))  # Higher severity spreads faster
        )

        self.gossip_network.append(gossip)
        print(f"📢 NEW GOSSIP: {secret} (known by {len(initial_knowers)} people)")

        # Damage reputation if severe and verified
        if severity >= 7 and verified:
            primary_target = about.split(" and ")[0]
            self.modify_reputation(primary_target, -severity * 3, "scandal")

        return gossip

    # ------------------------------------------------------------------
    # ORIGINAL RANDOM SPREAD (kept for compatibility, not neighbor-aware)
    # ------------------------------------------------------------------
    def spread_gossip_randomly(self, npc_list: List[str], spread_count: int = 3):
        """Randomly spread existing gossip to NPCs (legacy, not neighbor-aware)."""
        for gossip in self.gossip_network:
            if len(gossip.known_by) >= len(npc_list) * 0.7:
                continue

            candidates = [npc for npc in npc_list if npc not in gossip.known_by]
            if not candidates:
                continue

            targets = random.sample(candidates, min(spread_count, len(candidates)))
            for target in targets:
                if gossip.spread_to(target):
                    print(f"  💬 {target} heard: {gossip.secret}")

    # ------------------------------------------------------------------
    # NEW NEIGHBOR-AWARE SPREAD ENTRYPOINT (use this from simulation_v2)
    # ------------------------------------------------------------------
    def _spread_between(self, speaker: "NPC", listener: "NPC"):
        """
        Spread gossip from speaker to listener.
        Neighbors and shared location enhance spread chance.
        """
        # Which gossip does speaker know?
        known_gossip = [g for g in self.gossip_network if speaker.full_name in g.known_by]
        if not known_gossip:
            return

        # Pick one gossip randomly
        gossip = random.choice(known_gossip)

        # Base multiplier = 1.0
        multiplier = 1.0

        # Neighbors gossip more if neighbor_map is available
        neighbors = []
        if self.sim and hasattr(self.sim, "neighbor_map"):
            neighbors = self.sim.neighbor_map.get(speaker.full_name, [])
            if listener.full_name in neighbors:
                multiplier *= 1.6

        # Shared exact location
        if speaker.current_location and speaker.current_location == listener.current_location:
            multiplier *= 1.3

        if gossip.spread_to(listener.full_name, multiplier=multiplier):
            print(f"  💬 {listener.full_name} heard: {gossip.secret}")

    def spread_gossip(self, npcs: List["NPC"]):
        """
        New neighbor-aware gossip spread.
        Call this from simulation_v2.run(self.npcs).
        """
        if not npcs or not self.gossip_network:
            return

        # A few random interactions per tick
        interactions = max(1, len(npcs) // 2)
        for _ in range(interactions):
            speaker, listener = random.sample(npcs, 2)
            self._spread_between(speaker, listener)

        # Let gossip decay slowly
        self.decay_gossip()

    # ------------------------------------------------------------------
    # Rest of your original logic
    # ------------------------------------------------------------------
    def process_hookup_gossip(
        self,
        npc1: str,
        npc2: str,
        hookup_type: str,
        victim: Optional[str],
        current_day: int
    ):
        """Process gossip from hookups/affairs"""
        if random.random() < 0.30:
            if hookup_type == "betrayal_hookup" and victim:
                secret = f"{npc1} cheated on {victim} with {npc2}"
                severity = 8
            else:
                secret = f"{npc1} hooked up with {npc2}"
                severity = 4

            self.create_gossip(
                about=f"{npc1} and {npc2}",
                secret=secret,
                initial_knowers=[],  # Will be populated by spread
                severity=severity,
                spread_day=current_day,
                verified=True
            )

            if hookup_type == "betrayal_hookup":
                self.modify_reputation(npc1, -20, "cheating scandal")

    def process_affair_gossip(
        self,
        cheater: str,
        partner: str,
        victim: str,
        current_day: int
    ) -> bool:
        """Process gossip from ongoing affairs (5% chance per check)"""
        if random.random() < 0.05:
            secret = f"{cheater} is having an affair with {partner} (cheating on {victim})"

            self.create_gossip(
                about=f"{cheater} and {partner}",
                secret=secret,
                initial_knowers=[],
                severity=10,
                spread_day=current_day,
                verified=True
            )

            self.modify_reputation(cheater, -30, "affair exposed")
            return True

        return False

    def trigger_random_life_event(self, npc_list: List['NPC'], current_day: int) -> Optional[Dict]:
        """5% chance to trigger random life event for an NPC"""
        if random.random() > 0.05 or not npc_list:
            return None

        npc = random.choice(npc_list)

        events = [
            ("job_loss", -5, "lost their job"),
            ("job_promotion", 10, "got promoted"),
            ("minor_accident", -3, "had a minor accident"),
            ("inheritance", 8, "received an inheritance"),
            ("health_scare", 0, "had a health scare"),
            ("car_breakdown", -2, "car broke down"),
            ("family_visit", 0, "has family visiting"),
            ("lottery_win", 15, "won the lottery"),
            ("pet_death", -5, "pet passed away"),
            ("home_repair", -3, "major home repair needed")
        ]

        event_type, rep_change, description = random.choice(events)

        event = {
            'npc': npc.full_name,
            'event': event_type,
            'day': current_day,
            'description': f"{npc.full_name} {description}",
            'consequences': []
        }

        self.life_events.append(event)

        if rep_change != 0:
            self.modify_reputation(npc.full_name, rep_change, description)

        print(f"🎲 RANDOM EVENT: {event['description']}")

        return event

    def decay_gossip(self):
        """Gossip fades over time"""
        for gossip in self.gossip_network[:]:
            gossip.decay()
            if len(gossip.known_by) == 0:
                self.gossip_network.remove(gossip)

    def get_npc_gossip(self, npc_name: str) -> List[Gossip]:
        """Get all gossip known by a specific NPC"""
        return [g for g in self.gossip_network if npc_name in g.known_by]

    def get_gossip_about(self, npc_name: str) -> List[Gossip]:
        """Get all gossip about a specific NPC"""
        return [g for g in self.gossip_network if npc_name in g.about]

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        avg_rep = (
            sum(r.town_reputation for r in self.reputations.values()) / len(self.reputations)
            if self.reputations else 50.0
        )

        return {
            'total_npcs_tracked': len(self.reputations),
            'average_reputation': avg_rep,
            'active_gossip': len(self.gossip_network),
            'total_life_events': len(self.life_events),
            'status_distribution': {
                status.value: sum(1 for r in self.reputations.values() if r.social_status == status)
                for status in SocialStatus
            }
        }

    def export(self) -> Dict:
        """Export reputation data"""
        return {
            'reputations': {
                name: {
                    'town_reputation': rep.town_reputation,
                    'known_secrets': rep.known_secrets,
                    'gossip_about': rep.gossip_about,
                    'social_status': rep.social_status.value
                }
                for name, rep in self.reputations.items()
            },
            'gossip_network': [
                {
                    'about': g.about,
                    'secret': g.secret,
                    'known_by': list(g.known_by),
                    'spread_day': g.spread_day,
                    'severity': g.severity
                }
                for g in self.gossip_network
            ],
            'life_events': self.life_events
        }
