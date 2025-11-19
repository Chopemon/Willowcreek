# systems/emotional_contagion.py
"""
Emotional Contagion System v1.1
Purpose: Emotions spread between NPCs creating group dynamics.
Now neighbor-aware when a simulation with neighbor_map is attached.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import random

if TYPE_CHECKING:
    from entities.npc import NPC
    from core.time_system import TimeSystem
    from core.simulation_v2 import WillowCreekSimulation


class EmotionType(str, Enum):
    TENSION = "tension"
    FEAR = "fear"
    SHAME = "shame"
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    ANXIETY = "anxiety"
    LOVE = "love"
    DESIRE = "desire"
    GUILT = "guilt"


@dataclass
class ActiveEmotion:
    """An active emotional state in the simulation"""
    emotion: EmotionType
    source: str  # What caused it
    epicenter: str  # Where it's strongest (location/person)
    affected_people: List[str] = field(default_factory=list)
    intensity: int = 5  # 1-10
    spreading: bool = True
    symptoms: List[str] = field(default_factory=list)
    duration_days: Optional[int] = None
    chronic: bool = False
    escalating: bool = False
    damaging: bool = False

    def spread_to(self, npc_name: str, reduction: float = 0.7):
        """Spread emotion to another NPC with reduced intensity"""
        if npc_name not in self.affected_people:
            self.affected_people.append(npc_name)
            return int(self.intensity * reduction)
        return 0


@dataclass
class HouseholdMood:
    """Emotional climate of a household"""
    location: str
    primary_mood: str
    intensity: int  # 1-10
    sources: List[str] = field(default_factory=list)
    atmosphere: str = ""
    symptoms: List[str] = field(default_factory=list)
    chronic: bool = False

    def update_intensity(self, change: int):
        """Modify intensity with bounds"""
        self.intensity = max(1, min(10, self.intensity + change))


@dataclass
class GroupState:
    """Emotional state of a group/location"""
    group_name: str
    dominant_mood: str
    undercurrent: Optional[str] = None
    sub_groups: Dict[str, str] = field(default_factory=dict)
    intensity: int = 5


class EmotionalContagionSystem:
    """
    Manages emotional spread and group dynamics.
    Now supports neighbor-aware proximity spreading if a simulation is attached.
    """

    def __init__(self, sim: Optional["WillowCreekSimulation"] = None):
        self.sim = sim
        self.active_emotions: List[ActiveEmotion] = []
        self.household_moods: Dict[str, HouseholdMood] = {}
        self.group_states: Dict[str, GroupState] = {}
        self.initialized = False

    def attach_sim(self, sim: "WillowCreekSimulation"):
        self.sim = sim

    def initialize_emotional_landscape(self):
        """Set up initial emotional states"""
        if self.initialized:
            return

        # Sturm House - Extreme tension from Alex-Maria-John dynamic
        self.household_moods["Sturm House"] = HouseholdMood(
            location="Sturm House",
            primary_mood="Extreme tension",
            intensity=8,
            sources=["Alex-Maria forbidden attraction", "John's jealousy", "Elena's confusion"],
            atmosphere="Awkward silences, unspoken conflict",
            symptoms=[
                "Awkward silences at dinner",
                "Elena feels unsafe but doesn't know why",
                "Maria confused by tension",
                "John's anger building"
            ],
            chronic=True
        )

        self.active_emotions.append(ActiveEmotion(
            emotion=EmotionType.TENSION,
            source="Alex-Maria-John dynamic",
            epicenter="Sturm House",
            affected_people=["Alex Sturm", "Maria Sturm", "John Sturm", "Elena Sturm"],
            intensity=8,
            symptoms=[
                "Awkward silences at dinner",
                "Elena feels unsafe but doesn't know why",
                "Maria confused by tension",
                "John's anger building"
            ],
            chronic=True,
            escalating=True
        ))

        # Carter House - Fear from domestic violence
        self.household_moods["Carter House"] = HouseholdMood(
            location="Carter House",
            primary_mood="Fear",
            intensity=10,
            sources=["Tony's violence", "Unpredictable outbursts", "Economic control"],
            atmosphere="Walking on eggshells, hypervigilance",
            symptoms=[
                "Hypervigilance",
                "Walking on eggshells",
                "Lianna mimics mother's fawning",
                "Both startle at loud noises"
            ],
            chronic=True
        )

        self.active_emotions.append(ActiveEmotion(
            emotion=EmotionType.FEAR,
            source="Tony's violence",
            epicenter="Carter House",
            affected_people=["Scarlet Carter", "Lianna Carter"],
            intensity=10,
            symptoms=[
                "Hypervigilance",
                "Walking on eggshells",
                "Lianna mimics mother's fawning",
                "Both startle at loud noises"
            ],
            chronic=True,
            damaging=True
        ))

        # Blake House - Disconnection and unmet needs
        self.household_moods["Blake House"] = HouseholdMood(
            location="Blake House",
            primary_mood="Disconnected",
            intensity=6,
            sources=["Nina's affair interest", "Ken's suspicion", "Sexual frustration"],
            atmosphere="Polite strangers living together",
            symptoms=[
                "Forced politeness",
                "Emotional distance growing",
                "Kids sense parents' unhappiness"
            ]
        )

        self.active_emotions.append(ActiveEmotion(
            emotion=EmotionType.DESIRE,
            source="Nina's unmet sexual needs",
            epicenter="Blake House",
            affected_people=["Nina Blake"],
            intensity=7,
            spreading=False  # Contained within Nina
        ))

        # Madison House - Stable love (rare in this town)
        self.household_moods["Madison House"] = HouseholdMood(
            location="Madison House",
            primary_mood="Stable/Loving",
            intensity=8,
            sources=["David's devotion", "Sarah's contentment"],
            atmosphere="Warm, safe",
            symptoms=["Eve has secure childhood", "Genuine affection displayed"]
        )

        # Group states
        self.group_states["High School"] = GroupState(
            group_name="High School",
            dominant_mood="Teenage angst + excitement",
            sub_groups={
                "Popular kids": "Confident, dramatic",
                "Alex's isolation": "Withdrawn from peers",
                "Lianna's group": "Supportive friends noticing changes"
            },
            intensity=7
        )

        self.group_states["Church Community"] = GroupState(
            group_name="Church Community",
            dominant_mood="Judgmental piety",
            undercurrent="Everyone hiding sins",
            intensity=6
        )

        self.group_states["The Tipsy Stag"] = GroupState(
            group_name="The Tipsy Stag",
            dominant_mood="Escapism",
            undercurrent="Drowning problems",
            sub_groups={
                "Tony": "Violent drunk",
                "Ken": "Suspicious, drinking more"
            },
            intensity=6
        )

        self.initialized = True
        print("✓ Emotional contagion system initialized")
        print(f"  • {len(self.active_emotions)} active emotional states")
        print(f"  • {len(self.household_moods)} household moods tracked")

    def add_emotion(self, emotion: ActiveEmotion):
        """Add a new emotional state to the system"""
        self.active_emotions.append(emotion)
        print(f"💭 NEW EMOTION: {emotion.emotion.value} at {emotion.epicenter} (intensity {emotion.intensity})")

    # ------------------------------------------------------------------
    # NEIGHBOR-AWARE PROXIMITY SPREAD
    # ------------------------------------------------------------------
    def spread_emotion_by_proximity(
        self,
        source_npc: str,
        target_npcs: List[str],
        location: str
    ):
        """
        Spread emotions based on who's in the same location.
        Neighboring households get slightly stronger spread (less reduction).
        """
        neighbor_set = set()
        if self.sim and hasattr(self.sim, "neighbor_map"):
            neighbor_set = set(self.sim.neighbor_map.get(source_npc, []))

        for emotion in self.active_emotions:
            if not emotion.spreading:
                continue
            if source_npc not in emotion.affected_people:
                continue

            for target in target_npcs:
                if target == source_npc:
                    continue

                reduction = 0.7
                if target in neighbor_set:
                    reduction = 0.5  # neighbors carry the mood more strongly

                emotion.spread_to(target, reduction)

    def spread_emotions(self, npcs: List["NPC"], loc_map: Optional[Dict[str, List["NPC"]]] = None):
        """
        New entrypoint: spread emotions each tick across all NPCs.
        Uses location AND neighborhood (if sim.neighbor_map exists).
        OPTIMIZED: Accepts pre-built location map to avoid redundant grouping.
        """
        if not npcs:
            return

        self.initialize_emotional_landscape()

        # OPTIMIZATION: Use cached location map if provided, otherwise build it
        if loc_map is None:
            by_location: Dict[str, List["NPC"]] = {}
            for npc in npcs:
                loc = npc.current_location or "Nowhere"
                by_location.setdefault(loc, []).append(npc)
        else:
            by_location = loc_map

        # Within each location, spread emotions between NPCs present
        for loc, group in by_location.items():
            if len(group) < 2:
                continue

            names = [n.full_name for n in group]
            for source in names:
                targets = [n for n in names if n != source]
                if targets:
                    self.spread_emotion_by_proximity(source, targets, loc)

    # ------------------------------------------------------------------
    # REST OF ORIGINAL API
    # ------------------------------------------------------------------
    def check_household_contagion(self, household: str) -> List[str]:
        """Get effects of household emotional climate"""
        if household not in self.household_moods:
            return []

        mood = self.household_moods[household]
        effects = []

        if mood.intensity >= 7:
            effects.append(f"{household} emotional climate: {mood.primary_mood} (intensity {mood.intensity}/10)")

            if mood.chronic:
                effects.append(f"Long-term psychological impact on residents")

        return effects

    def detect_emotional_clashes(
        self,
        npc1: str,
        npc2: str,
        location: str
    ) -> Optional[str]:
        """Detect when NPCs with contrasting emotions meet"""
        npc1_emotions = [e for e in self.active_emotions if npc1 in e.affected_people]
        npc2_emotions = [e for e in self.active_emotions if npc2 in e.affected_people]

        if not npc1_emotions or not npc2_emotions:
            return None

        contrasts = {
            EmotionType.JOY: EmotionType.SADNESS,
            EmotionType.LOVE: EmotionType.ANGER,
            EmotionType.FEAR: EmotionType.JOY
        }

        for e1 in npc1_emotions:
            for e2 in npc2_emotions:
                if contrasts.get(e1.emotion) == e2.emotion or contrasts.get(e2.emotion) == e1.emotion:
                    return f"{npc1}'s {e1.emotion.value} clashes with {npc2}'s {e2.emotion.value} at {location}"

        return None

    def get_dominant_emotion_at(self, location: str) -> Optional[str]:
        """Get the dominant emotion at a location"""
        if location in self.household_moods:
            return self.household_moods[location].primary_mood

        if location in self.group_states:
            return self.group_states[location].dominant_mood

        location_emotions = [e for e in self.active_emotions if e.epicenter == location]
        if location_emotions:
            strongest = max(location_emotions, key=lambda x: x.intensity)
            return strongest.emotion.value

        return None

    def decay_emotions(self, days_passed: int = 1):
        """Non-chronic emotions decay over time"""
        for emotion in self.active_emotions[:]:
            if not emotion.chronic:
                emotion.intensity -= days_passed
                if emotion.intensity <= 0:
                    self.active_emotions.remove(emotion)

    def escalate_emotion(self, location: str, emotion_type: EmotionType, amount: int):
        """Intensify an existing emotion"""
        for emotion in self.active_emotions:
            if emotion.epicenter == location and emotion.emotion == emotion_type:
                emotion.intensity = min(10, emotion.intensity + amount)
                emotion.escalating = True
                print(f"⬆️ ESCALATION: {emotion_type.value} at {location} now at {emotion.intensity}/10")
                return

    def get_npc_emotional_state(self, npc_name: str) -> List[str]:
        """Get all emotions affecting an NPC"""
        emotions = []
        for emotion in self.active_emotions:
            if npc_name in emotion.affected_people:
                emotions.append(f"{emotion.emotion.value} (intensity {emotion.intensity})")
        return emotions

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        emotion_counts = {}
        for emotion in self.active_emotions:
            emotion_counts[emotion.emotion.value] = emotion_counts.get(emotion.emotion.value, 0) + 1

        return {
            'active_emotions': len(self.active_emotions),
            'households_tracked': len(self.household_moods),
            'group_states': len(self.group_states),
            'emotion_distribution': emotion_counts,
            'chronic_emotions': sum(1 for e in self.active_emotions if e.chronic),
            'escalating_emotions': sum(1 for e in self.active_emotions if e.escalating)
        }

    def export(self) -> Dict:
        """Export emotional data"""
        return {
            'active_emotions': [
                {
                    'emotion': e.emotion.value,
                    'source': e.source,
                    'epicenter': e.epicenter,
                    'affected_people': e.affected_people,
                    'intensity': e.intensity,
                    'chronic': e.chronic,
                    'escalating': e.escalating
                }
                for e in self.active_emotions
            ],
            'household_moods': {
                name: {
                    'primary_mood': mood.primary_mood,
                    'intensity': mood.intensity,
                    'sources': mood.sources,
                    'atmosphere': mood.atmosphere
                }
                for name, mood in self.household_moods.items()
            },
            'group_states': {
                name: {
                    'dominant_mood': state.dominant_mood,
                    'intensity': state.intensity
                }
                for name, state in self.group_states.items()
            }
        }
