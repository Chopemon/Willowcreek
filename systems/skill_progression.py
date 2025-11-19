# systems/skill_progression.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from entities.npc import NPC


@dataclass
class SkillState:
    level: int = 0
    xp: float = 0.0


class SkillProgressionSystem:
    """
    Tracks NPC skills. External code calls `register_action` with skill tags.
    """

    def __init__(self):
        # npc_name -> skill_name -> SkillState
        self.skills: Dict[str, Dict[str, SkillState]] = {}

    def _get_skill_state(self, npc_name: str, skill: str) -> SkillState:
        npc_skills = self.skills.setdefault(npc_name, {})
        if skill not in npc_skills:
            npc_skills[skill] = SkillState()
        return npc_skills[skill]

    def register_action(self, npc: NPC, skill: str, base_xp: float = 1.0):
        st = self._get_skill_state(npc.full_name, skill)
        st.xp += base_xp
        # Simple leveling curve: 10 * (level + 1)
        needed = 10 * (st.level + 1)
        while st.xp >= needed:
            st.xp -= needed
            st.level += 1
            needed = 10 * (st.level + 1)

    def get_skill_level(self, npc: NPC, skill: str) -> int:
        return self.skills.get(npc.full_name, {}).get(skill, SkillState()).level

    def get_skill_summary(self, npc: NPC) -> Dict[str, int]:
        return {k: v.level for k, v in self.skills.get(npc.full_name, {}).items()}
