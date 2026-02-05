# systems/timeline_system.py
# Branching timelines manager.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime


@dataclass
class TimelineBranch:
    name: str
    parent: Optional[str]
    created_at: str


class TimelineSystem:
    def __init__(self):
        self.branches: Dict[str, TimelineBranch] = {
            "main": TimelineBranch(name="main", parent=None, created_at=datetime.utcnow().isoformat())
        }

    def create_branch(self, name: str, parent: str = "main") -> TimelineBranch:
        branch = TimelineBranch(name=name, parent=parent, created_at=datetime.utcnow().isoformat())
        self.branches[name] = branch
        return branch

    def list_branches(self) -> Dict[str, TimelineBranch]:
        return dict(self.branches)
