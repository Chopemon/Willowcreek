# systems/knowledge_graph.py
# Knowledge graph for tracking who knows what.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class KnowledgeFact:
    subject: str
    content: str
    is_true: bool
    source: str


class KnowledgeGraph:
    """
    Tracks knowledge facts per character.
    """

    def __init__(self):
        self.knowledge: Dict[str, List[KnowledgeFact]] = {}

    def add_fact(self, knower: str, fact: KnowledgeFact) -> None:
        self.knowledge.setdefault(knower, []).append(fact)

    def get_facts(self, knower: str) -> List[KnowledgeFact]:
        return list(self.knowledge.get(knower, []))

    def knows_fact(self, knower: str, content: str) -> bool:
        return any(f.content == content for f in self.knowledge.get(knower, []))
