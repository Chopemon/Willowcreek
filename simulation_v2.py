# simulation_v2.py - Willow Creek 2025 Simulation Core (FULLY INTEGRATED + QUIRKS + SEXUAL)

from typing import List, Dict, Optional
from datetime import datetime
import json
import os

from core.time_system import TimeSystem
from core.world_state import WorldState
from entities.npc import NPC, Gender  # Added Gender import

# Core systems
from systems.needs import NeedsSystem
from systems.relationships import RelationshipManager
from systems.autonomous import AutonomousSystem
from systems.goals_system import GoalsSystem
from systems.reputation_system import ReputationSystem
from systems.environmental_triggers import EnvironmentalSystem
from systems.emotional_contagion import EmotionalContagionSystem
from systems.seasonal_dynamics import SeasonalDynamicsSystem
from systems.memory_system import MemorySystem
from systems.schedule_system import ScheduleSystem

# Life systems
from systems.female_biology_system import FemaleBiologySystem
from systems.pregnancy_system import PregnancySystem
from systems.health_disease_system import HealthDiseaseSystem
from systems.growth_development_system import GrowthDevelopmentSystem
from systems.skill_progression import SkillProgressionSystem
from systems.consequence_cascades import ConsequenceCascadesSystem
from systems.dynamic_triggers import DynamicTriggerSystem

# Drama stack
from systems.birthday_system import BirthdaySystem
from systems.event_system import EventSystem
from systems.school_drama_system import SchoolDramaSystem
from systems.addiction_system import AddictionSystem
from systems.crime_system import CrimeSystem
from systems.micro_interactions_system import MicroInteractionsSystem

# NEW: QUIRKS + SEXUAL ACTIVITY SYSTEMS
from systems.npc_quirks_system import NPCQuirksSystem
from systems.sexual_activity_system import SexualActivitySystem
from systems.debug_overlay import DebugOverlay

# COMPREHENSIVE WORLD SNAPSHOT FOR AI NARRATOR
from world_snapshot_builder import WorldSnapshotBuilder


class WillowCreekSimulation:
    def __init__(self, num_npcs: int = 41, start_date: Optional[datetime] = None):
        print("=== WILLOW CREEK 2025 - FULLY AUTONOMOUS WORLD ===\n")

        # Core
        self.time = TimeSystem(start_date or datetime(2025, 9, 1, 8, 0))
        self.world = WorldState()
        self.current_step = 0
        self.npcs: List[NPC] = []
        self.npc_dict: Dict[str, NPC] = {}
        self.debug_overlay_enabled: bool = False
        self.scenario_buffer: List[str] = []  # For quirks & sexual events
        self.debug_enabled = True
        self.debug = DebugOverlay(self)

        # Load NPC roster
        base_dir = os.path.dirname(os.path.abspath(__file__))
        npc_folder = os.path.join(base_dir, "npc_data")
        print(f"Loading NPC roster from folder: {npc_folder}")

        success = self.world.load_npc_roster(npc_folder)
        if not success:
            print("[WorldState] Failed to load NPC roster.")
            return

        self.npcs = list(self.world.npc_roster.values())
        self.npc_dict = self.world.npc_roster
        print(f"Loaded {len(self.npcs)} NPCs\n")

        # Initialize all systems
        self.relationships = RelationshipManager(self.npcs)
        self.needs = NeedsSystem()
        self.autonomous = AutonomousSystem(self)
        self.goals = GoalsSystem()
        self.reputation = ReputationSystem(self)
        self.environmental = EnvironmentalSystem()
        self.emotional = EmotionalContagionSystem(self)
        self.seasonal = SeasonalDynamicsSystem()
        self.memory = MemorySystem()
        self.schedule = ScheduleSystem(self)

        # Life systems
        self.female_biology = FemaleBiologySystem(self.time)
        self.pregnancy = PregnancySystem(self.time, self.female_biology)
        self.health = HealthDiseaseSystem(self.time)
        self.development = GrowthDevelopmentSystem(self.time)
        self.skills = SkillProgressionSystem()
        self.consequences = ConsequenceCascadesSystem(self.reputation, self.emotional, self.memory)
        self.dynamic_triggers = DynamicTriggerSystem(self.time)

        # Drama stack
        self.birthdays = BirthdaySystem(self.time, self.memory)
        self.events = EventSystem(self.time, self.consequences)
        self.school_drama = SchoolDramaSystem(
            self.time, self.reputation, self.emotional, self.memory, self.consequences
        )
        self.addiction = AddictionSystem(self.time)
        self.crime = CrimeSystem(self.time, self.reputation, self.consequences)
        self.micro = MicroInteractionsSystem(self.time, self.emotional, self.relationships)

        # NEW SYSTEMS
        self.quirks = NPCQuirksSystem(self)
        self.sexual = SexualActivitySystem(self)

        # WORLD SNAPSHOT BUILDER - Comprehensive state for AI narrator
        self.snapshot_builder = WorldSnapshotBuilder(self)

        print("All systems initialized.\n")

        # Initialize NPC metadata
        for npc in self.npcs:
            self.goals.initialize_npc_goals(npc, self.time.total_days)
            self.memory.initialize_npc_memory(npc.full_name)
            self.reputation.init_reputation(npc.full_name)
            self.female_biology.ensure_npc(npc)
            self.pregnancy.ensure_npc(npc)
            self.development.ensure_npc(npc)

        self.birthdays.register_npcs(self.npcs)
        self.schedule.update_locations()

        # Find or create Malcolm
        self.malcolm = self.npc_dict.get("Malcolm Newt")
        if not self.malcolm:
            # Fallback for Malcolm if not found in roster
            self.malcolm = NPC(full_name="Malcolm Newt", age=30, gender=Gender.MALE)
            self.npcs.append(self.malcolm)
            self.npc_dict["Malcolm Newt"] = self.malcolm

        print(f"Start time: {self.time.get_datetime_string()}\n")

    # =====================================================================
    # SINGLE-STEP TICK
    # =====================================================================
    def tick(self, time_step_hours: float = 1.0):
        """
        Single-step simulation tick (same logic as one iteration of run()).
        This is what the web UI / NarrativeChat should call.
        """
        self.current_step += 1
        prev_day = self.time.total_days

        # Advance time
        self.time.advance(time_step_hours)

        # Update schedules and locations
        self.schedule.update_locations()

        # Core simulation systems
        self.needs.process_needs(self.npcs, time_step_hours)
        self.seasonal.update(self.time)
        self.environmental.check_triggers(self.npcs, self.time)
        self.autonomous.process_all(time_step_hours)

        # Build location map AFTER autonomous system runs (fixes location display bug)
        loc_map = self._build_location_map()
        self.emotional.spread_emotions(self.npcs)
        self.memory.consolidate_memories(self.time.total_days)
        self.goals.update_all(self.time.total_days)
        self.reputation.spread_gossip(self.npcs)

        # Drama/Interaction stacks
        self.micro.update_step(self.npcs, loc_map)
        self.school_drama.update_step(self.npcs, loc_map)
        self.events.update_step(self.npcs, loc_map)
        self.crime.update_step(self.npcs, loc_map)
        self.addiction.update_step(self.npcs)
        self.dynamic_triggers.update(self.npcs)

        # Day-change updates
        if self.time.total_days != prev_day:
            prev_day = self.time.total_days
            self.female_biology.update_for_day(self.npcs)
            self.pregnancy.update_for_day(self.npcs)
            self.health.update_for_day(self.npcs, loc_map)
            self.development.update_for_year(self.npcs)
            self.birthdays.update_for_day(self.npcs)
            self.addiction.update_for_day(self.npcs)
            self.crime.update_for_day(self.npcs)
            self.events.update_for_day(self.npcs, loc_map)

        # Autonomous sexual & quirk behavior
        self.sexual.try_autonomous_behavior()

    # =====================================================================
    # CLASS METHODS (OUTSIDE OF __INIT__)
    # =====================================================================

    def build_world_snapshot(self, malcolm):
        """
        Full omniscient world-state snapshot.
        Delegates to the comprehensive WorldSnapshotBuilder for complete system integration.
        """
        return self.snapshot_builder.build_complete_snapshot(malcolm)

    def get_attraction(self, npc):
        return getattr(npc, "attraction_to_malcolm", 0)

    def _build_location_map(self) -> Dict[str, List[NPC]]:
        """
        Build a mapping from location name -> list of NPC objects
        based on their current_location field.
        """
        loc_groups: Dict[str, List[NPC]] = {}

        for npc in self.npcs:
            loc = getattr(npc, "current_location", None)
            if not loc:
                loc = "Unknown"

            loc_groups.setdefault(loc, []).append(npc)

        return loc_groups

    def run(self, num_steps: int = 24, time_step_hours: float = 1.0):
        """
        Batch runner used for offline sims / debugging.
        Web UI will usually call tick() instead.
        """
        prev_day = self.time.total_days

        for _ in range(num_steps):
            self.current_step += 1
            self.time.advance(time_step_hours)

            self.schedule.update_locations()

            self.needs.process_needs(self.npcs, time_step_hours)
            self.seasonal.update(self.time)
            self.environmental.check_triggers(self.npcs, self.time)
            self.autonomous.process_all(time_step_hours)

            # Build location map AFTER autonomous system runs (fixes location display bug)
            loc_map = self._build_location_map()
            self.emotional.spread_emotions(self.npcs)
            self.memory.consolidate_memories(self.time.total_days)
            self.goals.update_all(self.time.total_days)
            self.reputation.spread_gossip(self.npcs)

            self.micro.update_step(self.npcs, loc_map)
            self.school_drama.update_step(self.npcs, loc_map)
            self.events.update_step(self.npcs, loc_map)
            self.crime.update_step(self.npcs, loc_map)
            self.addiction.update_step(self.npcs)
            self.dynamic_triggers.update(self.npcs)

            if self.time.total_days != prev_day:
                prev_day = self.time.total_days
                self.female_biology.update_for_day(self.npcs)
                self.pregnancy.update_for_day(self.npcs)
                self.health.update_for_day(self.npcs, loc_map)
                self.development.update_for_year(self.npcs)
                self.birthdays.update_for_day(self.npcs)
                self.addiction.update_for_day(self.npcs)
                self.crime.update_for_day(self.npcs)
                self.events.update_for_day(self.npcs, loc_map)

            # Autonomous sexual & quirk behavior
            self.sexual.try_autonomous_behavior()

    def get_statistics(self):
        if self.npcs:
            horny = sum(n.needs.horny for n in self.npcs) / len(self.npcs)
            lonely = sum(n.psyche.lonely for n in self.npcs) / len(self.npcs)
            secrets = sum(len(getattr(n, "private_secrets", [])) for n in self.npcs)
        else:
            horny = lonely = 0.0
            secrets = 0

        return {
            "Day": self.time.total_days,
            "Time": self.time.get_datetime_string(),
            "NPCs": len(self.npcs),
            "Avg Horny": f"{horny:.1f}",
            "Avg Lonely": f"{lonely:.1f}",
            "Secrets": secrets,
            "Gossip": len(self.reputation.gossip_network),
            "Active Emotions": len(self.emotional.active_emotions),
            "Weather": getattr(self.world, "weather", None) or "Clear",
            "Season": getattr(self.time, "season", "autumn").title(),
        }

    def export_to_janitor_ai(self, filename="willow_creek_full.js"):
        data = {
            "town": "Willow Creek",
            "time": self.time.get_datetime_string(),
            "npc_count": len(self.npcs),
            "npcs": [
                {
                    "name": n.full_name,
                    "age": n.age,
                    "location": getattr(n, "current_location", "Unknown"),
                    "horny": round(n.needs.horny, 1),
                    "lonely": round(n.psyche.lonely, 1),
                }
                for n in self.npcs
            ],
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"File created: {filename}")

    def print_debug_overlay(self):
        """
        Debug overlay that **always** reflects the latest schedule state.
        """

        

        # Build fresh map from current_location
        loc_groups = self._build_location_map()

        print("────────────────────────────────────────────────────────────────────────────────")
        print(f"DEBUG OVERLAY — {self.time.get_datetime_string()}")
        print("────────────────────────────────────────────────────────────────────────────────")
        print()

        # ------------------------------------------------------------------
        # NPC LOCATIONS
        # ------------------------------------------------------------------
        print("NPC LOCATIONS:")
        for loc, npc_list in sorted(loc_groups.items(), key=lambda kv: kv[0]):
            names = ", ".join(sorted(n.full_name for n in npc_list))
            print(f"  • {loc}: {names}")
        print()

        # ------------------------------------------------------------------
        # GOSSIP + EMOTIONS
        # ------------------------------------------------------------------
        gossip_network = getattr(self.reputation, "gossip_network", [])
        gossip_count = len(gossip_network) if gossip_network is not None else 0
        print(f"GOSSIP NETWORK: {gossip_count} active items")

        active_emotions = getattr(self.emotional, "active_emotions", [])
        emotion_count = len(active_emotions) if active_emotions is not None else 0
        print(f"ACTIVE EMOTIONS: {emotion_count} active entries")
        print()

        # ------------------------------------------------------------------
        # SICKNESS + PREGNANCY
        # ------------------------------------------------------------------
        sick_names: List[str] = []
        sick_state = getattr(self.health, "sick_npcs", None)
        if isinstance(sick_state, dict):
            for name, is_sick in sick_state.items():
                if is_sick:
                    sick_names.append(name)
        elif isinstance(sick_state, list):
            sick_names.extend(sick_state)

        print(f"SICK NPCs: {len(sick_names)}")
        if sick_names:
            print("  • " + ", ".join(sorted(sick_names)))

        active_pregnancies = getattr(self.pregnancy, "active_pregnancies", [])
        preg_count = len(active_pregnancies) if active_pregnancies is not None else 0
        print(f"ACTIVE PREGNANCIES: {preg_count}")
        print()

        # ------------------------------------------------------------------
        # CRIME / ADDICTION / SCHOOL DRAMA
        # ------------------------------------------------------------------
        recent_crimes = getattr(self.crime, "recent_crimes", [])
        crime_count = len(recent_crimes) if recent_crimes is not None else 0

        addiction_states = getattr(self.addiction, "states", {})
        add_count = len(addiction_states) if addiction_states is not None else 0

        recent_drama = getattr(self.school_drama, "recent_events", [])
        drama_count = len(recent_drama) if recent_drama is not None else 0

        print(f"CRIME EVENTS (recent): {crime_count}")
        print(f"ADDICTION CASES:       {add_count}")
        print(f"SCHOOL DRAMA EVENTS:   {drama_count}")
        print()

        # ------------------------------------------------------------------
        # GLOBAL NEEDS SUMMARY
        # ------------------------------------------------------------------
        if self.npcs:
            avg_hunger = sum(n.needs.hunger for n in self.npcs) / len(self.npcs)
            avg_horny = sum(n.needs.horny for n in self.npcs) / len(self.npcs)
            avg_lonely = sum(n.psyche.lonely for n in self.npcs) / len(self.npcs)
        else:
            avg_hunger = avg_horny = avg_lonely = 0.0

        print("GLOBAL NEEDS SUMMARY:")
        print(f"  • Avg Hunger: {avg_hunger:.1f}")
        print(f"  • Avg Horny:  {avg_horny:.1f}")
        print(f"  • Avg Lonely: {avg_lonely:.1f}")
        print()
        print("────────────────────────────────────────────────────────────────────────────────")
