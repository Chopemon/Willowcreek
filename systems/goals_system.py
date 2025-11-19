# systems/goals_system.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


# ============================================================
# DATA CLASS FOR NPC GOALS
# ============================================================
@dataclass
class Goal:
    """
    Unified advanced goal model for Willow Creek 2025.
    """
    description: str
    category: str
    urgency: float
    started_day: int

    # --- ADVANCED PROPERTIES ---
    private: bool = False                   # secret goals (only internal)
    shame_level: float = 0.0                # 0–1 (affects gossip/emotion)
    progress: float = 0.0                   # completion % for long-term goals
    difficulty: float = 0.5                 # how hard the goal is
    emotional_cost: float = 0.0             # negative emotional effect if failing
    reward_value: float = 0.0               # positive emotional effect when succeeding
    fear_avoidance: float = 0.0             # how much fear blocks the goal
    obstacles: List[str] = field(default_factory=list)
    completed: bool = False
    abandoned: bool = False
    notes: List[str] = field(default_factory=list)

    # For daily updates
    last_update_day: int = -1

    def adjust_urgency(self, delta: float):
        self.urgency = max(0.0, min(1.0, self.urgency + delta))

    def advance_progress(self, effort: float):
        """
        NPC progress toward completing long-term goals.
        """
        gain = (effort * (1.0 - self.difficulty)) - self.fear_avoidance
        gain = max(gain, -0.1)  # can't regress too hard

        self.progress = max(0.0, min(1.0, self.progress + gain))

        if self.progress >= 1.0:
            self.completed = True

    def fail_daily(self):
        """
        Daily emotional penalty for not addressing goals.
        """
        penalty = self.emotional_cost * 0.25
        self.shame_level = min(1.0, self.shame_level + penalty)


# ============================================================
# MAIN SYSTEM: GOALSYSTEM V3
# ============================================================
class GoalsSystem:
    """
    Hybrid of:
    - Old deep psychological goal engine
    - New needs-reactive, simulation-compatible goal engine

    Simulation expects:
      ✔ initialize_npc_goals(npc, current_day)
      ✔ update_all(current_day)
    """

    def __init__(self):
        self.goals: Dict[str, List[Goal]] = {}

    # ---------------------------------------------------------
    # INITIAL GOAL SEEDING
    # ---------------------------------------------------------
    def initialize_npc_goals(self, npc, current_day: int):
        """
        Called once at the start of simulation.
        Creates 1–3 foundational long-term goals for each NPC.
        """

        name = npc.full_name
        if name in self.goals:
            return

        occupation = getattr(npc, "occupation", "").lower()
        age = npc.age

        base_goals: List[Goal] = []

        # ---------------- TEENS ----------------
        if age <= 18:
            base_goals.append(Goal(
                description="Survive school and avoid humiliation.",
                category="social",
                urgency=0.6,
                started_day=current_day,
                shame_level=0.3,
                emotional_cost=0.2,
                fear_avoidance=0.1,
                difficulty=0.4,
            ))

            base_goals.append(Goal(
                description="Figure out identity and friendships.",
                category="identity",
                urgency=0.5,
                started_day=current_day,
                private=True,
                shame_level=0.2,
                difficulty=0.5,
                reward_value=0.3,
            ))

        # ---------------- YOUNG ADULT ----------------
        elif 19 <= age <= 30:
            base_goals.append(Goal(
                description="Find direction and meaning in life.",
                category="identity",
                urgency=0.5,
                started_day=current_day,
                difficulty=0.6,
                emotional_cost=0.25,
            ))

        # ---------------- ADULTS / PARENTS ----------------
        else:
            base_goals.append(Goal(
                description="Maintain stability in family relationships.",
                category="family",
                urgency=0.6,
                started_day=current_day,
                difficulty=0.5,
                emotional_cost=0.2,
                reward_value=0.4,
            ))

        # ---------------- OCCUPATIONAL GOALS ----------------
        if "teacher" in occupation:
            base_goals.append(Goal(
                description="Keep students safe and avoid scandals.",
                category="work",
                urgency=0.7,
                started_day=current_day,
                difficulty=0.4,
                shame_level=0.2,
                fear_avoidance=0.15,
            ))

        if "pastor" in occupation:
            base_goals.append(Goal(
                description="Maintain congregation trust.",
                category="faith",
                urgency=0.75,
                started_day=current_day,
                difficulty=0.5,
                reward_value=0.3,
            ))

        if "police" in occupation or "officer" in occupation:
            base_goals.append(Goal(
                description="Keep the town safe and watch for danger signs.",
                category="order",
                urgency=0.65,
                started_day=current_day,
                difficulty=0.4,
            ))

        # fallback
        if not base_goals:
            base_goals.append(Goal(
                description="Get through daily life without crisis.",
                category="generic",
                urgency=0.4,
                started_day=current_day,
            ))

        self.goals[name] = base_goals

    # ---------------------------------------------------------
    # UPDATE ALL NPC GOALS (SIM-REQUIRED)
    # ---------------------------------------------------------
    def update_all(self, current_day: int):
        for npc_name in list(self.goals.keys()):
            self.update_npc_goals(npc_name, current_day)

    # ---------------------------------------------------------
    # NPC DAILY GOAL UPDATE (MERGED ADVANCED LOGIC)
    # ---------------------------------------------------------
    def update_npc_goals(self, npc_name: str, current_day: int, npc_obj=None):
        g_list = self.goals.get(npc_name, [])
        if not g_list:
            return

        # DAILY DECAY & FAILURE PENALTY
        for g in g_list:
            if g.completed or g.abandoned:
                continue

            # slight urgency decay
            g.adjust_urgency(-0.02)

            # failure shame buildup
            g.fail_daily()

        # NEED-BASED REACTIVE GOALS (NEW SYSTEM)
        if npc_obj is not None:
            self._react_to_needs(npc_name, npc_obj, current_day)

        # LONG-TERM PROGRESS (OLD SYSTEM)
        if npc_obj is not None:
            self._apply_progress(npc_name, npc_obj, current_day)

        # Remove old abandoned goals
        filtered = []
        for g in g_list:
            age = current_day - g.started_day
            if (age > 120 and g.urgency < 0.2) or g.abandoned:
                continue
            filtered.append(g)

        self.goals[npc_name] = filtered

    # -------------------------------------------------------------------
    # INTERNAL: NEED-DRIVEN GOAL CREATION + URGENCY BOOST
    # -------------------------------------------------------------------
    def _react_to_needs(self, npc_name, npc, current_day):
        nd = npc.needs
        psyche = npc.psyche

        # Hunger
        if nd.hunger > 70:
            self._boost_or_add(
                npc_name,
                "survival",
                "Find food soon.",
                0.6,
                current_day,
                private=False,
            )

        # Loneliness
        if psyche.lonely > 60:
            self._boost_or_add(
                npc_name,
                "connection",
                "Seek emotional connection with someone.",
                0.7,
                current_day,
                private=True
            )

        # Horny / intimacy
        if nd.horny > 70:
            self._boost_or_add(
                npc_name,
                "intimacy",
                "Find intimacy or relief.",
                0.65,
                current_day,
                private=True,
            )

    # -------------------------------------------------------------------
    # INTERNAL: BOOST EXISTING OR CREATE NEW GOAL
    # -------------------------------------------------------------------
    def _boost_or_add(self, npc_name, category, description, urgency, current_day, private):
        lst = self.goals.get(npc_name, [])
        for g in lst:
            if g.category == category and not g.completed:
                g.adjust_urgency(0.12)
                g.notes.append(f"Urgency boosted on day {current_day}.")
                return

        lst.append(Goal(
            description=description,
            category=category,
            urgency=urgency,
            private=private,
            started_day=current_day,
            shame_level=0.1 if private else 0.0,
            difficulty=0.4,
        ))
        self.goals[npc_name] = lst

    # -------------------------------------------------------------------
    # INTERNAL: PROGRESSION / ADVANCEMENT
    # -------------------------------------------------------------------
    def _apply_progress(self, npc_name, npc, current_day):
        for g in self.goals.get(npc_name, []):
            if g.completed:
                continue

            # Effort from NPC depends on needs + psyche
            effort = 0.08

            # Low energy reduces ability to pursue goals
            if npc.energy < 40:
                effort *= 0.5

            # High shame/fear reduces progress
            effort -= g.shame_level * 0.03
            effort -= g.fear_avoidance * 0.04

            g.advance_progress(effort)

    # -------------------------------------------------------------------
    # PUBLIC ACCESS
    # -------------------------------------------------------------------
    def get_active_goals(self, npc_name) -> List[Goal]:
        lst = self.goals.get(npc_name, [])
        return sorted(
            [g for g in lst if not g.completed and not g.abandoned],
            key=lambda x: x.urgency,
            reverse=True,
        )

    def debug_summary(self, npc_name: str):
        """Used in overlay."""
        active = self.get_active_goals(npc_name)
        return [
            {
                "goal": g.description,
                "category": g.category,
                "urgency": round(g.urgency, 2),
                "progress": round(g.progress, 2),
                "shame": round(g.shame_level, 2),
                "private": g.private,
            }
            for g in active
        ]
