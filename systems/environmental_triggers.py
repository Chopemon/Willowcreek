# systems/environmental_triggers.py
"""
Environmental Triggers System v1.0
Purpose: Locations create opportunities and risks based on who's present
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import random

if TYPE_CHECKING:
    from entities.npc import NPC
    from core.time_system import TimeSystem


class TriggerOutcome(str, Enum):
    SEXUAL_TENSION_EXTREME = "sexual_tension_extreme"
    TENSION_TRIANGULATED = "tension_triangulated"
    INTIMATE_MOMENT = "intimate_moment"
    FORBIDDEN_ENCOUNTER = "forbidden_encounter"
    PROFESSIONAL_FLIRTATION = "professional_flirtation"
    DOMESTIC_VIOLENCE = "domestic_violence"
    SOCIAL_PRESSURE = "social_pressure"
    EMOTIONAL_BREAKTHROUGH = "emotional_breakthrough"


@dataclass
class LocationTrigger:
    """Defines a trigger that can occur at a location"""
    name: str
    chance: float  # 0.0 to 1.0
    outcome: TriggerOutcome
    risk_description: str
    consequences: List[str] = field(default_factory=list)
    time_restrictions: Optional[List[str]] = None  # ["morning", "night", etc.]
    required_npcs: List[str] = field(default_factory=list)
    excluded_npcs: List[str] = field(default_factory=list)
    min_npcs: int = 1
    max_npcs: int = 99

    def check_conditions(
        self,
        present_npcs: List[str],
        time_of_day: str,
    ) -> bool:
        """Check if trigger conditions are met"""
        # Check time restrictions
        if self.time_restrictions and time_of_day not in self.time_restrictions:
            return False

        # Check NPC count
        if not (self.min_npcs <= len(present_npcs) <= self.max_npcs):
            return False

        # Check required NPCs are present
        if self.required_npcs:
            if not all(npc in present_npcs for npc in self.required_npcs):
                return False

        # Check excluded NPCs are not present
        if self.excluded_npcs:
            if any(npc in present_npcs for npc in self.excluded_npcs):
                return False

        return True

    def attempt_trigger(self) -> bool:
        """Roll for trigger activation"""
        return random.random() < self.chance


@dataclass
class TriggeredEvent:
    """Record of a trigger that activated"""
    location: str
    trigger_name: str
    outcome: TriggerOutcome
    involved_npcs: List[str]
    day: int
    time_of_day: str
    consequences: List[str]


class EnvironmentalSystem:
    """
    Manages location-based triggers and environmental interactions
    Creates dynamic situations based on who is where and when
    """

    def __init__(self):
        self.location_triggers: Dict[str, List[LocationTrigger]] = {}
        self.active_events: List[TriggeredEvent] = []
        self.event_history: List[TriggeredEvent] = []
        self.initialized = False

    def initialize_locations(self):
        """Set up all location triggers"""
        if self.initialized:
            return

        # Sturm House - Sexual tension and family drama
        self.location_triggers["Sturm House"] = [
            LocationTrigger(
                name="alone_with_Maria",
                chance=0.80,
                outcome=TriggerOutcome.SEXUAL_TENSION_EXTREME,
                risk_description="Alex may act on impulse",
                consequences=["frustration +3", "arousal +5", "risk of incident"],
                required_npcs=["Alex Sturm", "Maria Sturm"],
                max_npcs=2,
            ),
            LocationTrigger(
                name="John_home_watching",
                chance=0.60,
                outcome=TriggerOutcome.TENSION_TRIANGULATED,
                risk_description="John notices Alex watching Maria",
                consequences=["suspicion +2", "jealousy triggered"],
                required_npcs=["John Sturm", "Alex Sturm", "Maria Sturm"],
            ),
            LocationTrigger(
                name="early_morning_kitchen",
                chance=0.50,
                outcome=TriggerOutcome.FORBIDDEN_ENCOUNTER,
                risk_description="Maria in nightgown, Alex alone",
                consequences=["extreme tension", "Alex retreats to garage"],
                time_restrictions=["morning"],
                required_npcs=["Alex Sturm", "Maria Sturm"],
                max_npcs=2,
            ),
            LocationTrigger(
                name="family_dinner_tension",
                chance=0.70,
                outcome=TriggerOutcome.TENSION_TRIANGULATED,
                risk_description="Forced proximity creates awkwardness",
                consequences=["Elena senses something wrong", "Maria confused"],
                time_restrictions=["evening"],
                min_npcs=3,
            ),
        ]

        # Blake House - Marital tension and affairs
        self.location_triggers["Blake House"] = [
            LocationTrigger(
                name="Nina_alone_frustrated",
                chance=0.40,
                outcome=TriggerOutcome.SEXUAL_TENSION_EXTREME,
                risk_description="Nina's desires intensify when alone",
                consequences=["arousal +4", "affair temptation +3"],
                required_npcs=["Nina Blake"],
                max_npcs=1,
                time_restrictions=["evening", "night"],
            ),
            LocationTrigger(
                name="Ken_ignoring_Nina",
                chance=0.50,
                outcome=TriggerOutcome.SOCIAL_PRESSURE,
                risk_description="Ken distracted, Nina feels unseen",
                consequences=["resentment +3", "distance grows"],
                required_npcs=["Ken Blake", "Nina Blake"],
                min_npcs=2,
            ),
            LocationTrigger(
                name="Nina_texts_other_man",
                chance=0.35,
                outcome=TriggerOutcome.FORBIDDEN_ENCOUNTER,
                risk_description="Nina emotionally invests elsewhere",
                consequences=["affair path opens", "guilt +2"],
                required_npcs=["Nina Blake"],
            ),
        ]

        # Madison House - Creative pressure and emotional climate
        self.location_triggers["Madison House"] = [
            LocationTrigger(
                name="late_night_work",
                chance=0.50,
                outcome=TriggerOutcome.EMOTIONAL_BREAKTHROUGH,
                risk_description="Artistic focus alters mood of house",
                consequences=["creative flow", "emotional exhaustion"],
                required_npcs=["Sarah Madison"],
                time_restrictions=["night"],
            )
        ]

        # Carter House - Domestic violence danger
        self.location_triggers["Carter House"] = [
            LocationTrigger(
                name="violence_escalation",
                chance=0.50,
                outcome=TriggerOutcome.DOMESTIC_VIOLENCE,
                risk_description="Tony's violence toward Scarlet",
                consequences=["trauma", "fear +5", "escape planning intensifies"],
                time_restrictions=["evening", "night"],
            ),
            LocationTrigger(
                name="Lianna_witnessing",
                chance=0.30,
                outcome=TriggerOutcome.DOMESTIC_VIOLENCE,
                risk_description="Lianna sees abuse",
                consequences=["childhood trauma", "normalization of violence"],
                required_npcs=["Lianna Carter", "Tony Carter", "Scarlet Carter"],
            ),
        ]

        # School - Teen drama (canonical name)
        self.location_triggers["Willow Creek High School"] = [
            LocationTrigger(
                name="hallway_encounter",
                chance=0.40,
                outcome=TriggerOutcome.SOCIAL_PRESSURE,
                risk_description="Public social dynamics",
                consequences=["reputation shift", "gossip spreads"],
                time_restrictions=["morning", "afternoon"],
                min_npcs=3,
            ),
            LocationTrigger(
                name="locker_room_privacy",
                chance=0.25,
                outcome=TriggerOutcome.INTIMATE_MOMENT,
                risk_description="Private conversations in vulnerable setting",
                consequences=["bonds form", "secrets shared"],
                min_npcs=2,
                max_npcs=3,
            ),
        ]

        # Willow Creek Park - Romantic opportunities
        self.location_triggers["Willow Creek Park"] = [
            LocationTrigger(
                name="secluded_path",
                chance=0.60,
                outcome=TriggerOutcome.INTIMATE_MOMENT,
                risk_description="Privacy enables romantic encounters",
                consequences=["relationship deepens", "attraction +2"],
                min_npcs=2,
                max_npcs=2,
                time_restrictions=["afternoon", "evening"],
            ),
            LocationTrigger(
                name="public_display",
                chance=0.30,
                outcome=TriggerOutcome.SOCIAL_PRESSURE,
                risk_description="Public encounter creates witnesses",
                consequences=["gossip starts", "reputation affected"],
                min_npcs=3,
            ),
        ]

        # Namaste Yoga - Professional boundaries
        self.location_triggers["Namaste Yoga"] = [
            LocationTrigger(
                name="Nina_teaching_attracted_client",
                chance=0.30,
                outcome=TriggerOutcome.PROFESSIONAL_FLIRTATION,
                risk_description="Nina's sexuality expressed through teaching",
                consequences=["boundary crossing risk", "attraction +2"],
                required_npcs=["Nina Blake"],
                min_npcs=2,
            )
        ]

        # Rick's Place (bar from locations.py) - Alcohol and lowered inhibitions
        self.location_triggers["Rick's Place"] = [
            LocationTrigger(
                name="drunk_encounter",
                chance=0.50,
                outcome=TriggerOutcome.INTIMATE_MOMENT,
                risk_description="Alcohol lowers inhibitions",
                consequences=["hookup risk", "regret potential"],
                time_restrictions=["evening", "night"],
                min_npcs=2,
            ),
            LocationTrigger(
                name="Tony_drinking",
                chance=0.70,
                outcome=TriggerOutcome.DOMESTIC_VIOLENCE,
                risk_description="Tony gets drunk, goes home violent",
                consequences=["Scarlet in danger", "violence likely"],
                required_npcs=["Tony Carter"],
                time_restrictions=["evening", "night"],
            ),
        ]

        self.initialized = True
        print("✓ Environmental trigger system initialized")

    # === RUNTIME API ===

    def check_location_triggers(
        self,
        location: str,
        present_npcs: List[str],
        time_of_day: str,
        current_day: int,
    ) -> List[TriggeredEvent]:
        """Check and activate triggers for a location"""
        if not self.initialized:
            self.initialize_locations()

        if location not in self.location_triggers:
            return []

        triggered_events = []

        for trigger in self.location_triggers[location]:
            # Check if conditions are met
            if not trigger.check_conditions(present_npcs, time_of_day):
                continue

            # Attempt to trigger
            if trigger.attempt_trigger():
                event = TriggeredEvent(
                    location=location,
                    trigger_name=trigger.name,
                    outcome=trigger.outcome,
                    involved_npcs=present_npcs.copy(),
                    day=current_day,
                    time_of_day=time_of_day,
                    consequences=trigger.consequences.copy(),
                )

                triggered_events.append(event)
                self.active_events.append(event)
                self.event_history.append(event)

                print(f"⚡ TRIGGER ACTIVATED: {location} - {trigger.name}")
                print(f"   Outcome: {trigger.outcome.value}")
                print(f"   Involved: {', '.join(present_npcs)}")

        return triggered_events

    def get_location_risk_level(self, location: str, present_npcs: List[str], time_of_day: str) -> int:
        """Calculate risk level (0-10) for current situation"""
        if location not in self.location_triggers:
            return 0

        risk = 0
        for trigger in self.location_triggers[location]:
            if trigger.check_conditions(present_npcs, time_of_day):
                # Higher chance = higher risk
                risk += int(trigger.chance * 10)

                # Domestic violence = maximum risk
                if trigger.outcome == TriggerOutcome.DOMESTIC_VIOLENCE:
                    risk += 10

        return min(10, risk)

    def clear_old_events(self, days_to_keep: int = 7):
        """Clear old events from active list"""
        if not self.active_events:
            return

        current_day = max(e.day for e in self.active_events)
        self.active_events = [
            e for e in self.active_events if current_day - e.day <= days_to_keep
        ]

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        outcome_counts: Dict[str, int] = {}
        for event in self.event_history:
            outcome_counts[event.outcome.value] = outcome_counts.get(event.outcome.value, 0) + 1

        return {
            "total_events": len(self.event_history),
            "active_events": len(self.active_events),
            "by_outcome": outcome_counts,
        }

    def check_triggers(self, npcs: List["NPC"], time: "TimeSystem"):
        """
        High-level helper used by the simulation:
        groups NPCs by location and runs checks.
        """
        if not self.initialized:
            self.initialize_locations()

        # Group NPCs by location
        by_location: Dict[str, List[str]] = {}
        for npc in npcs:
            by_location.setdefault(npc.current_location, []).append(npc.full_name)

        for location, present in by_location.items():
            self.check_location_triggers(
                location=location,
                present_npcs=present,
                time_of_day=time.time_of_day,
                current_day=time.total_days,
            )
