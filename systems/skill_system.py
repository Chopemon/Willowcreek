# systems/skill_system.py
# Skill and progression system for Malcolm and NPCs

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class SkillType(Enum):
    """Different skill types in the game"""
    CHARISMA = "charisma"          # Conversation, persuasion, charm
    ATHLETIC = "athletic"          # Physical activities, fitness
    INTELLIGENCE = "intelligence"  # Knowledge, problem-solving
    CREATIVITY = "creativity"      # Arts, music, writing
    COOKING = "cooking"            # Food preparation
    MECHANICAL = "mechanical"      # Repairs, building
    SEDUCTION = "seduction"        # Romantic/sexual appeal
    EMPATHY = "empathy"           # Understanding emotions


@dataclass
class Skill:
    """Individual skill with level and experience"""
    skill_type: SkillType
    level: int = 1
    experience: float = 0.0

    @property
    def next_level_xp(self) -> float:
        """XP needed for next level (exponential scaling)"""
        return 100 * (1.5 ** (self.level - 1))

    @property
    def progress_to_next(self) -> float:
        """Progress to next level as percentage (0-100)"""
        return (self.experience / self.next_level_xp) * 100

    def add_experience(self, amount: float) -> List[str]:
        """
        Add experience and handle level ups.
        Returns list of messages about level ups.
        """
        self.experience += amount
        messages = []

        # Handle multiple level ups
        while self.experience >= self.next_level_xp and self.level < 10:
            self.experience -= self.next_level_xp
            self.level += 1
            messages.append(f"{self.skill_type.value.title()} increased to level {self.level}!")

        # Cap at level 10
        if self.level >= 10:
            self.experience = 0

        return messages

    def get_modifier(self) -> float:
        """
        Get skill modifier for checks (1.0 - 2.0).
        Level 1 = 1.0x, Level 10 = 2.0x
        """
        return 1.0 + (self.level - 1) * 0.111  # Scales from 1.0 to ~2.0


class SkillSystem:
    """Manages skills for all characters"""

    def __init__(self):
        self.character_skills: Dict[str, Dict[SkillType, Skill]] = {}

    def initialize_character(self, character_name: str, starting_skills: Optional[Dict[SkillType, int]] = None):
        """
        Initialize a character's skills.
        starting_skills: dict of SkillType -> starting level
        """
        if character_name in self.character_skills:
            return  # Already initialized

        self.character_skills[character_name] = {}

        # Initialize all skills at level 1
        for skill_type in SkillType:
            starting_level = 1
            if starting_skills and skill_type in starting_skills:
                starting_level = starting_skills[skill_type]

            self.character_skills[character_name][skill_type] = Skill(
                skill_type=skill_type,
                level=starting_level
            )

    def get_skill(self, character_name: str, skill_type: SkillType) -> Optional[Skill]:
        """Get a character's skill"""
        if character_name not in self.character_skills:
            return None
        return self.character_skills[character_name].get(skill_type)

    def get_skill_level(self, character_name: str, skill_type: SkillType) -> int:
        """Get skill level (returns 0 if not initialized)"""
        skill = self.get_skill(character_name, skill_type)
        return skill.level if skill else 0

    def add_experience(self, character_name: str, skill_type: SkillType, amount: float) -> List[str]:
        """Add experience to a skill. Returns level-up messages."""
        if character_name not in self.character_skills:
            self.initialize_character(character_name)

        skill = self.character_skills[character_name][skill_type]
        return skill.add_experience(amount)

    def perform_skill_check(self, character_name: str, skill_type: SkillType, difficulty: float = 50.0) -> tuple[bool, float]:
        """
        Perform a skill check.

        Args:
            character_name: Character performing check
            skill_type: Which skill to use
            difficulty: Base difficulty (0-100, default 50)

        Returns:
            (success: bool, roll: float)
        """
        import random

        skill = self.get_skill(character_name, skill_type)
        modifier = skill.get_modifier() if skill else 1.0

        # Roll 1-100, multiply by skill modifier
        roll = random.uniform(1, 100) * modifier

        success = roll >= difficulty
        return success, roll

    def get_character_summary(self, character_name: str) -> str:
        """Get a summary of character's skills"""
        if character_name not in self.character_skills:
            return f"{character_name}: No skills initialized"

        skills = self.character_skills[character_name]
        lines = [f"\n{character_name}'s Skills:"]

        for skill_type in SkillType:
            skill = skills[skill_type]
            lines.append(
                f"  {skill_type.value.title()}: Lvl {skill.level} "
                f"({skill.progress_to_next:.0f}% to next)"
            )

        return "\n".join(lines)

    def get_top_skills(self, character_name: str, count: int = 3) -> List[tuple[SkillType, int]]:
        """Get character's top N skills by level"""
        if character_name not in self.character_skills:
            return []

        skills = self.character_skills[character_name]
        sorted_skills = sorted(
            [(st, skill.level) for st, skill in skills.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_skills[:count]


# Activity XP rewards
XP_REWARDS = {
    "conversation": {SkillType.CHARISMA: 5, SkillType.EMPATHY: 3},
    "persuade": {SkillType.CHARISMA: 10},
    "flirt": {SkillType.SEDUCTION: 8, SkillType.CHARISMA: 3},
    "workout": {SkillType.ATHLETIC: 15},
    "read": {SkillType.INTELLIGENCE: 10},
    "cook": {SkillType.COOKING: 12},
    "repair": {SkillType.MECHANICAL: 10},
    "create_art": {SkillType.CREATIVITY: 12},
    "intimate": {SkillType.SEDUCTION: 15, SkillType.EMPATHY: 5},
}
