# systems/dialogue_system.py
# Interactive dialogue system with conversation trees

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DialogueCondition(Enum):
    MIN_FRIENDSHIP = "min_friendship"
    MIN_ROMANCE = "min_romance"
    MIN_SKILL = "min_skill"
    HAS_ITEM = "has_item"
    RELATIONSHIP_STATUS = "relationship_status"


@dataclass
class DialogueChoice:
    id: str
    text: str
    response: str
    effects: Dict[str, float] = field(default_factory=dict)
    conditions: Dict[DialogueCondition, any] = field(default_factory=dict)
    skill_check: Optional[tuple] = None
    leads_to: Optional[str] = None
    ends_conversation: bool = False


@dataclass
class DialogueNode:
    id: str
    npc_line: str
    choices: List[DialogueChoice] = field(default_factory=list)
    conditions: Dict[DialogueCondition, any] = field(default_factory=dict)
    one_time: bool = False


class DialogueTree:
    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.nodes: Dict[str, DialogueNode] = {}
        self.start_node_id: str = "greeting"
        self.used_one_time_nodes: set = set()
    
    def add_node(self, node: DialogueNode):
        self.nodes[node.id] = node
    
    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        return self.nodes.get(node_id)


class DialogueSystem:
    def __init__(self):
        self.dialogue_trees: Dict[str, DialogueTree] = {}
    
    def create_dialogue_tree(self, npc_name: str) -> DialogueTree:
        tree = DialogueTree(npc_name)
        self.dialogue_trees[npc_name] = tree
        return tree
    
    def get_dialogue_tree(self, npc_name: str) -> Optional[DialogueTree]:
        return self.dialogue_trees.get(npc_name)


# Quick dialogue responses
QUICK_DIALOGUES = {
    "greeting": {
        "stranger": ["Hello there.", "Hi."],
        "friend": ["Hey! How's it going?", "Good to see you!"],
    },
    "farewell": {
        "stranger": ["Goodbye.", "See you."],
        "friend": ["See you soon!", "Catch you later!"],
    }
}
