# systems/milestone_tracker.py
"""
Milestone & Event Tracker System

Tracks and records major life events and milestones:
- Birthdays and aging
- Relationship milestones (friendships, romances, breakups)
- Major life changes (job changes, moves, etc.)
- Achievements and memorable moments
- Conflicts and resolutions
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from entities.npc import NPC


class MilestoneType(Enum):
    """Categories of milestones"""
    BIRTHDAY = "birthday"
    RELATIONSHIP_FORMED = "relationship_formed"
    RELATIONSHIP_BROKEN = "relationship_broken"
    ROMANCE_STARTED = "romance_started"
    ROMANCE_ENDED = "romance_ended"
    MARRIAGE = "marriage"
    PREGNANCY = "pregnancy"
    BIRTH = "birth"
    DEATH = "death"
    JOB_CHANGE = "job_change"
    MOVE = "move"
    ACHIEVEMENT = "achievement"
    CONFLICT = "conflict"
    RESOLUTION = "resolution"
    SCANDAL = "scandal"
    SECRET_REVEALED = "secret_revealed"
    HEALTH_EVENT = "health_event"
    CRIME = "crime"
    EDUCATION = "education"
    OTHER = "other"


class MilestoneImportance(Enum):
    """How significant the milestone is"""
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    LIFE_CHANGING = 4


@dataclass
class Milestone:
    """A single milestone event"""
    milestone_type: MilestoneType
    importance: MilestoneImportance
    day: int
    simulation_time: str
    primary_npc: str
    secondary_npcs: List[str] = field(default_factory=list)
    description: str = ""
    location: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    emotional_impact: str = ""  # positive, negative, mixed, neutral

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.milestone_type.value,
            'importance': self.importance.value,
            'day': self.day,
            'time': self.simulation_time,
            'primary_npc': self.primary_npc,
            'secondary_npcs': self.secondary_npcs,
            'description': self.description,
            'location': self.location,
            'details': self.details,
            'tags': self.tags,
            'emotional_impact': self.emotional_impact
        }


class MilestoneTracker:
    """
    Tracks and manages all milestone events in the simulation.

    Features:
    - Automatic tracking of major events
    - Manual milestone recording
    - Timeline generation
    - NPC-specific history
    - Achievement tracking
    """

    def __init__(self, sim):
        self.sim = sim
        self.milestones: List[Milestone] = []
        self.npc_milestones: Dict[str, List[Milestone]] = {}

        # Tracking state for detecting changes
        self._previous_ages: Dict[str, int] = {}
        self._previous_relationships: Dict[str, Dict[str, float]] = {}
        self._previous_locations: Dict[str, str] = {}

    # ========================================================================
    # AUTOMATIC MILESTONE DETECTION
    # ========================================================================

    def update(self, npcs: List[NPC]):
        """
        Check for milestones that happened this update.
        Call this every simulation step or day.
        """
        self._detect_birthdays(npcs)
        self._detect_relationship_changes(npcs)
        self._detect_location_changes(npcs)

    def _detect_birthdays(self, npcs: List[NPC]):
        """Detect when NPCs have birthdays"""
        for npc in npcs:
            prev_age = self._previous_ages.get(npc.full_name, npc.age)

            if npc.age > prev_age:
                self.record_milestone(
                    milestone_type=MilestoneType.BIRTHDAY,
                    importance=self._get_birthday_importance(npc.age),
                    primary_npc=npc.full_name,
                    description=f"{npc.full_name} turned {npc.age} years old",
                    location=npc.current_location,
                    details={'new_age': npc.age, 'previous_age': prev_age},
                    emotional_impact="positive"
                )

            self._previous_ages[npc.full_name] = npc.age

    def _get_birthday_importance(self, age: int) -> MilestoneImportance:
        """Determine importance based on age milestones"""
        milestone_ages = [13, 16, 18, 21, 30, 40, 50, 60, 70, 80, 90, 100]
        if age in milestone_ages:
            return MilestoneImportance.MAJOR
        elif age % 10 == 0:
            return MilestoneImportance.MODERATE
        return MilestoneImportance.MINOR

    def _detect_relationship_changes(self, npcs: List[NPC]):
        """Detect significant relationship changes"""
        for npc in npcs:
            prev_rels = self._previous_relationships.get(npc.full_name, {})

            for rel_name, rel_data in npc.relationships.items():
                current_affinity = rel_data.get('affinity', 0)
                prev_affinity = prev_rels.get(rel_name, 0)

                # New strong friendship formed
                if prev_affinity < 70 and current_affinity >= 70:
                    self.record_milestone(
                        milestone_type=MilestoneType.RELATIONSHIP_FORMED,
                        importance=MilestoneImportance.MODERATE,
                        primary_npc=npc.full_name,
                        secondary_npcs=[rel_name],
                        description=f"{npc.full_name} and {rel_name} became close friends",
                        location=npc.current_location,
                        details={'affinity': current_affinity},
                        emotional_impact="positive"
                    )

                # Relationship turned romantic
                if prev_affinity < 80 and current_affinity >= 80:
                    self.record_milestone(
                        milestone_type=MilestoneType.ROMANCE_STARTED,
                        importance=MilestoneImportance.MAJOR,
                        primary_npc=npc.full_name,
                        secondary_npcs=[rel_name],
                        description=f"{npc.full_name} and {rel_name} started a romance",
                        location=npc.current_location,
                        details={'affinity': current_affinity},
                        emotional_impact="positive",
                        tags=['romance', 'love']
                    )

                # Relationship broken
                if prev_affinity >= 50 and current_affinity < 20:
                    self.record_milestone(
                        milestone_type=MilestoneType.RELATIONSHIP_BROKEN,
                        importance=MilestoneImportance.MODERATE,
                        primary_npc=npc.full_name,
                        secondary_npcs=[rel_name],
                        description=f"{npc.full_name} and {rel_name} had a falling out",
                        location=npc.current_location,
                        details={'affinity': current_affinity, 'previous': prev_affinity},
                        emotional_impact="negative",
                        tags=['conflict', 'breakup']
                    )

            # Update previous state
            self._previous_relationships[npc.full_name] = {
                name: data.get('affinity', 0)
                for name, data in npc.relationships.items()
            }

    def _detect_location_changes(self, npcs: List[NPC]):
        """Detect when NPCs move to new locations"""
        for npc in npcs:
            prev_loc = self._previous_locations.get(npc.full_name, npc.current_location)

            # Check if home location changed (moving houses)
            if hasattr(npc, 'home_location') and prev_loc != npc.home_location:
                if prev_loc and prev_loc != npc.home_location:
                    self.record_milestone(
                        milestone_type=MilestoneType.MOVE,
                        importance=MilestoneImportance.MAJOR,
                        primary_npc=npc.full_name,
                        description=f"{npc.full_name} moved from {prev_loc} to {npc.home_location}",
                        location=npc.home_location,
                        details={'from': prev_loc, 'to': npc.home_location},
                        emotional_impact="mixed"
                    )

            self._previous_locations[npc.full_name] = npc.current_location

    # ========================================================================
    # MANUAL MILESTONE RECORDING
    # ========================================================================

    def record_milestone(
        self,
        milestone_type: MilestoneType,
        importance: MilestoneImportance,
        primary_npc: str,
        description: str = "",
        secondary_npcs: Optional[List[str]] = None,
        location: str = "",
        details: Optional[Dict[str, Any]] = None,
        emotional_impact: str = "neutral",
        tags: Optional[List[str]] = None
    ) -> Milestone:
        """Manually record a milestone event"""

        milestone = Milestone(
            milestone_type=milestone_type,
            importance=importance,
            day=self.sim.time.total_days,
            simulation_time=self.sim.time.get_datetime_string(),
            primary_npc=primary_npc,
            secondary_npcs=secondary_npcs or [],
            description=description,
            location=location,
            details=details or {},
            tags=tags or [],
            emotional_impact=emotional_impact
        )

        self.milestones.append(milestone)

        # Add to NPC-specific history
        if primary_npc not in self.npc_milestones:
            self.npc_milestones[primary_npc] = []
        self.npc_milestones[primary_npc].append(milestone)

        # Also add to secondary NPCs' histories
        for npc_name in milestone.secondary_npcs:
            if npc_name not in self.npc_milestones:
                self.npc_milestones[npc_name] = []
            self.npc_milestones[npc_name].append(milestone)

        # Log important milestones
        if importance.value >= MilestoneImportance.MAJOR.value:
            print(f"🎯 MILESTONE: {description}")

        return milestone

    # ========================================================================
    # QUERYING MILESTONES
    # ========================================================================

    def get_npc_history(self, npc_name: str, limit: int = 10) -> List[Milestone]:
        """Get milestone history for a specific NPC"""
        milestones = self.npc_milestones.get(npc_name, [])
        return sorted(milestones, key=lambda m: m.day, reverse=True)[:limit]

    def get_recent_milestones(self, days: int = 7, limit: int = 20) -> List[Milestone]:
        """Get recent milestones from the last N days"""
        cutoff_day = self.sim.time.total_days - days
        recent = [m for m in self.milestones if m.day >= cutoff_day]
        return sorted(recent, key=lambda m: m.day, reverse=True)[:limit]

    def get_milestones_by_type(
        self,
        milestone_type: MilestoneType,
        limit: int = 20
    ) -> List[Milestone]:
        """Get milestones of a specific type"""
        filtered = [m for m in self.milestones if m.milestone_type == milestone_type]
        return sorted(filtered, key=lambda m: m.day, reverse=True)[:limit]

    def get_major_milestones(self, limit: int = 50) -> List[Milestone]:
        """Get only major/life-changing milestones"""
        major = [
            m for m in self.milestones
            if m.importance.value >= MilestoneImportance.MAJOR.value
        ]
        return sorted(major, key=lambda m: m.day, reverse=True)[:limit]

    # ========================================================================
    # TIMELINE & STATISTICS
    # ========================================================================

    def generate_timeline(self, npc_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate a chronological timeline of events"""
        if npc_name:
            events = self.npc_milestones.get(npc_name, [])
        else:
            events = self.milestones

        timeline = []
        for milestone in sorted(events, key=lambda m: m.day):
            timeline.append({
                'day': milestone.day,
                'date': milestone.simulation_time,
                'type': milestone.milestone_type.value,
                'description': milestone.description,
                'importance': milestone.importance.value,
                'npcs': [milestone.primary_npc] + milestone.secondary_npcs
            })

        return timeline

    def get_statistics(self) -> Dict[str, Any]:
        """Get milestone statistics"""
        type_counts = {}
        importance_counts = {}

        for milestone in self.milestones:
            # Count by type
            type_name = milestone.milestone_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

            # Count by importance
            imp_name = milestone.importance.name
            importance_counts[imp_name] = importance_counts.get(imp_name, 0) + 1

        return {
            'total_milestones': len(self.milestones),
            'by_type': type_counts,
            'by_importance': importance_counts,
            'npcs_with_milestones': len(self.npc_milestones),
            'recent_7_days': len(self.get_recent_milestones(days=7))
        }

    # ========================================================================
    # EXPORT & IMPORT
    # ========================================================================

    def export_milestones(self, filename: str = "milestones.json"):
        """Export all milestones to JSON"""
        import json

        data = {
            'total_milestones': len(self.milestones),
            'simulation_day': self.sim.time.total_days,
            'milestones': [m.to_dict() for m in self.milestones]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(self.milestones)} milestones to {filename}")

    def print_recent_milestones(self, days: int = 7):
        """Print recent milestones to console"""
        recent = self.get_recent_milestones(days=days)

        if not recent:
            print(f"\nNo milestones in the last {days} days.")
            return

        print(f"\n{'=' * 70}")
        print(f" RECENT MILESTONES (Last {days} days)")
        print(f"{'=' * 70}\n")

        for milestone in recent:
            icon = self._get_milestone_icon(milestone.milestone_type)
            print(f"{icon} Day {milestone.day} - {milestone.description}")
            if milestone.location:
                print(f"   Location: {milestone.location}")
            if milestone.secondary_npcs:
                print(f"   Involved: {', '.join(milestone.secondary_npcs)}")
            print()

    def _get_milestone_icon(self, milestone_type: MilestoneType) -> str:
        """Get emoji icon for milestone type"""
        icons = {
            MilestoneType.BIRTHDAY: "🎂",
            MilestoneType.RELATIONSHIP_FORMED: "🤝",
            MilestoneType.ROMANCE_STARTED: "💕",
            MilestoneType.ROMANCE_ENDED: "💔",
            MilestoneType.MARRIAGE: "💒",
            MilestoneType.PREGNANCY: "🤰",
            MilestoneType.BIRTH: "👶",
            MilestoneType.DEATH: "⚰️",
            MilestoneType.CONFLICT: "⚔️",
            MilestoneType.ACHIEVEMENT: "🏆",
            MilestoneType.SCANDAL: "📰",
            MilestoneType.SECRET_REVEALED: "🔓",
            MilestoneType.MOVE: "🏠",
            MilestoneType.CRIME: "🚔",
        }
        return icons.get(milestone_type, "📌")
