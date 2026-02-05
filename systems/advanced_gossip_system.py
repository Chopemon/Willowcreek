# systems/advanced_gossip_system.py
# True/false rumors and knowledge graph integration.

from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random

from systems.knowledge_graph import KnowledgeGraph, KnowledgeFact


@dataclass
class Rumor:
    subject: str
    content: str
    source: str
    is_true: bool
    juiciness: int = 5
    spread_count: int = 0
    day_created: int = 0

    def spreads_to(self) -> bool:
        return random.randint(1, 10) <= self.juiciness


class AdvancedGossipSystem:
    """
    Tracks rumors with truth values and a knowledge graph.
    """

    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.active_rumors: List[Rumor] = []

    def create_rumor(self, subject: str, content: str, source: str, is_true: bool, current_day: int, juiciness: int = 5) -> Rumor:
        rumor = Rumor(
            subject=subject,
            content=content,
            source=source,
            is_true=is_true,
            juiciness=juiciness,
            day_created=current_day,
        )
        self.active_rumors.append(rumor)
        self.knowledge_graph.add_fact(source, KnowledgeFact(subject=subject, content=content, is_true=is_true, source=source))
        return rumor

    def spread_rumor(self, rumor: Rumor, to_character: str) -> None:
        if self.knowledge_graph.knows_fact(to_character, rumor.content):
            return
        self.knowledge_graph.add_fact(
            to_character,
            KnowledgeFact(subject=rumor.subject, content=rumor.content, is_true=rumor.is_true, source=rumor.source),
        )
        rumor.spread_count += 1

    def simulate_spread(self, npc_names: List[str], current_day: int) -> None:
        for rumor in list(self.active_rumors):
            if current_day - rumor.day_created > 14:
                continue
            knowers = [name for name in npc_names if self.knowledge_graph.knows_fact(name, rumor.content)]
            for knower in knowers:
                if rumor.spreads_to() and npc_names:
                    target = random.choice(npc_names)
                    if target != knower:
                        self.spread_rumor(rumor, target)
