# systems/family_tree_system.py
# Family trees and inheritance.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FamilyNode:
    name: str
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    spouse: Optional[str] = None


class FamilyTreeSystem:
    """
    Maintains parent/child relationships and handles inheritance.
    """

    def __init__(self):
        self.nodes: Dict[str, FamilyNode] = {}

    def ensure_member(self, name: str) -> FamilyNode:
        if name not in self.nodes:
            self.nodes[name] = FamilyNode(name=name)
        return self.nodes[name]

    def add_parent_child(self, parent: str, child: str) -> None:
        parent_node = self.ensure_member(parent)
        child_node = self.ensure_member(child)
        if child not in parent_node.children:
            parent_node.children.append(child)
        if parent not in child_node.parents:
            child_node.parents.append(parent)

    def set_spouse(self, person_a: str, person_b: str) -> None:
        self.ensure_member(person_a).spouse = person_b
        self.ensure_member(person_b).spouse = person_a

    def get_ancestors(self, name: str, depth: int = 3) -> List[str]:
        ancestors = []
        frontier = [name]
        for _ in range(depth):
            next_frontier = []
            for person in frontier:
                node = self.nodes.get(person)
                if node:
                    ancestors.extend(node.parents)
                    next_frontier.extend(node.parents)
            frontier = next_frontier
        return ancestors

    def distribute_inheritance(self, deceased: str, estate_value: int) -> Dict[str, int]:
        node = self.nodes.get(deceased)
        if not node:
            return {}
        heirs = node.children or ([node.spouse] if node.spouse else [])
        heirs = [h for h in heirs if h]
        if not heirs:
            return {}
        share = estate_value // len(heirs)
        return {heir: share for heir in heirs}
