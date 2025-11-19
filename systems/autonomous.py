# systems/autonomous.py
from typing import TYPE_CHECKING
import random

from households import get_household

if TYPE_CHECKING:
    from core.simulation_v2 import WillowCreekSimulation
    from entities.npc import NPC


MILO_IVY_NAMES = {"Milo", "Ivy"}


def is_with_nate(time) -> bool:
    """
    Weekend custody window:
      - Friday (4) from 18:00 onwards
      - All Saturday (5)
      - Sunday (6) until 18:00
    Assumes day_of_week: Monday=0 ... Sunday=6
    """
    day = time.day_of_week
    hour = time.hour

    # Friday evening
    if day == 4 and hour >= 18:
        return True
    # Saturday all day
    if day == 5:
        return True
    # Sunday until 18:00
    if day == 6 and hour < 18:
        return True

    return False


class AutonomousSystem:
    def __init__(self, sim: "WillowCreekSimulation"):
        self.sim = sim

    def process_all(self, hours: float):
        for npc in self.sim.npcs:
            # Malcolm is player-driven; don't auto-move him
            if npc.full_name == "Malcolm Newt":
                continue

            # 1. Critical needs override everything
            action = self.sim.needs.suggest_action(npc)
            if action["action"] != "free_time":
                npc.current_location = self._resolve_location(action["location"], npc)
                continue

            # 2. Goals
            goal = self.sim.goals.get_highest_priority_goal(npc.full_name)
            if goal and random.random() < 0.8:
                npc.current_location = self._goal_to_location(goal, npc)
                continue

            # 3. Default schedule
            # NOTE: ScheduleSystem already handles default scheduling comprehensively,
            # so we don't need to override it here. Only critical needs and goals
            # should override the schedule system's placement.
            # self._default_schedule(npc)

    def _resolve_location(self, suggested: str, npc: "NPC") -> str:
        """
        Map high-level need locations to concrete world locations.
        Home-like needs route to the NPC's own household,
        EXCEPT Milo/Ivy, who stay wherever they currently are
        (Tessa's House on weekdays or Nate's House on weekends).
        """
        home_like = {"Kitchen", "Bedroom", "Bathroom", "Living Room", "Home"}

        if suggested in home_like:
            # Milo & Ivy: use current home (Tessa or Nate) without teleporting
            if npc.full_name in MILO_IVY_NAMES:
                return npc.current_location or get_household(npc.full_name)
            # Everyone else: go to their canonical household
            return get_household(npc.full_name)

        if suggested == "Public":
            # canonical name from locations.py
            return "The Main Street Diner"

        # Fallback: stay where they are, or go home if unknown
        return npc.current_location or get_household(npc.full_name)

    def _goal_to_location(self, goal, npc: "NPC") -> str:
        """
        Turn a goal description into a concrete location using canonical names.
        """
        g = goal.goal.lower()
        t = self.sim.time

        # School / study related
        if any(x in g for x in ["grade", "homework", "study", "school", "exam"]):
            if t.is_school_hours:
                return "Willow Creek High School"
            return get_household(npc.full_name)

        # Socializing
        if "social" in g or "friend" in g or "party" in g:
            # After school/work: park, otherwise diner as default hub
            if t.hour >= 15 and t.time_of_day in ("afternoon", "evening"):
                return "Willow Creek Park"
            return "The Main Street Diner"

        # Private / secretive / relief – keep it to their own house
        if any(x in g for x in ["relief", "secret", "privacy", "alone"]):
            return get_household(npc.full_name)

        # No clear mapping → stay where they are
        return npc.current_location

    def _default_schedule(self, npc: "NPC"):
        """
        Basic day schedule when needs/goals don't dictate anything special.
        Uses TimeSystem helpers + household mapping.
        Also handles Milo & Ivy's weekend custody with Nate.
        Now includes occasional evening neighbor visits.
        """
        t = self.sim.time
        home_loc = get_household(npc.full_name)

        # === Special case: Milo & Ivy weekend custody ===
        if npc.full_name in MILO_IVY_NAMES:
            if is_with_nate(t):
                npc.current_location = "Nate's House"
            else:
                npc.current_location = "Tessa's House"
            return

        # === Students ===
        if 5 <= npc.age <= 18:
            if t.is_school_hours:
                npc.current_location = "Willow Creek High School"
            else:
                # Free time: park in afternoons/evenings, otherwise home
                if t.time_of_day in ("afternoon", "evening") and not t.is_weekend:
                    npc.current_location = "Willow Creek Park"
                else:
                    npc.current_location = home_loc
            return

        # === Adults ===
        occ = (npc.occupation or "")

        if t.is_business_hours:
            # Teachers work at the school
            if "Teacher" in occ:
                npc.current_location = "Willow Creek High School"
            # Pastor works at church
            elif "Pastor" in occ:
                npc.current_location = "Oak Street Church"
            # Therapists / masseuse / artists often work from home or studio
            elif any(x in occ for x in ["Artist", "Masseuse", "Therapist"]):
                npc.current_location = home_loc
            else:
                # Generic working adult: diner as default 'work/social hub'
                npc.current_location = "The Main Street Diner"
        else:
            # Off work ⇒ go home / household
            npc.current_location = home_loc

        # === Evening neighbor visits (adults only) ===
        neighbor_map = getattr(self.sim, "neighbor_map", None)
        if (
            neighbor_map
            and t.time_of_day == "evening"
            and not t.is_business_hours
            and npc.age >= 18
            and random.random() < 0.15
        ):
            hood_neighbors = neighbor_map.get(npc.full_name, [])
            if hood_neighbors:
                chosen = random.choice(hood_neighbors)
                target_home = get_household(chosen)
                npc.current_location = target_home
