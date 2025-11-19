# systems/relationships.py
"""Relationship Management System"""
from typing import Dict, List, TYPE_CHECKING
import networkx as nx

if TYPE_CHECKING:
    from entities.npc import NPC

class RelationshipManager:
    """Manages NPC-to-NPC relationships"""
    
    def __init__(self, npcs: List['NPC']):
        self.relationships: Dict[str, dict] = {}
        self.graph = nx.Graph()
        self.npcs = npcs
        self._initialize_relationships()

    def _initialize_relationships(self):
        """Initializes the relationship graph with all known NPCs."""
        for npc in self.npcs:
            self.graph.add_node(npc.full_name)
        
        print(f"Relationship Manager initialized with {len(self.npcs)} NPCs.")

    def create_relationship(self, npc1: str, npc2: str, rel_type: str = "stranger", 
                          level: float = 0, attraction: float = 0):
        key = self._make_key(npc1, npc2)
        self.relationships[key] = {
            'npc1': npc1, 'npc2': npc2, 'type': rel_type,
            'level': level, 'attraction': attraction, 'history': []
        }
        self.graph.add_edge(npc1, npc2, weight=level)
    
    def _make_key(self, npc1: str, npc2: str) -> str:
        names = sorted([npc1, npc2])
        return f"{names[0]} <-> {names[1]}"
    
    def export(self) -> dict:
        return self.relationships
    
    def process_interactions(self, time_delta: float):
        """Placeholder for processing relationship changes based on time or actions."""
        pass
    
    def update_all_relationships(self, npcs: List['NPC'], time_delta: float):
        """
        Update all relationships based on current states and proximity.
        Called every simulation step to keep relationships dynamic.
        """
        # Natural relationship decay over time if not maintained
        for key, rel in list(self.relationships.items()):
            # Relationships naturally decay slowly if not maintained
            if rel['level'] > 0:
                rel['level'] = max(0, rel['level'] - 0.01 * time_delta)
            
            # Attraction can shift based on needs
            npc1_obj = next((n for n in npcs if n.full_name == rel['npc1']), None)
            npc2_obj = next((n for n in npcs if n.full_name == rel['npc2']), None)
            
            if npc1_obj and npc2_obj:
                # If both are horny and lonely, attraction increases
                if npc1_obj.needs.horny > 70 and npc1_obj.psyche.lonely > 70:
                    rel['attraction'] = min(100, rel['attraction'] + 0.1)
                if npc2_obj.needs.horny > 70 and npc2_obj.psyche.lonely > 70:
                    rel['attraction'] = min(100, rel['attraction'] + 0.1)
                
                # Update graph weight
                if self.graph.has_edge(rel['npc1'], rel['npc2']):
                    self.graph[rel['npc1']][rel['npc2']]['weight'] = rel['level']
    
    def get_relationship(self, npc1: str, npc2: str):
        """Get relationship between two NPCs"""
        key = self._make_key(npc1, npc2)
        if key in self.relationships:
            rel = self.relationships[key]
            # Return a simple object-like structure
            class RelData:
                def __init__(self, data):
                    self.relationship_type = type('obj', (object,), {'value': data.get('type', 'stranger')})()
                    self.attraction_level = data.get('attraction', 0)
                    self.trust = data.get('level', 0) * 10  # Scale to 0-100
                    self.comfort = data.get('level', 0) * 10
            return RelData(rel)
        return None 
    
    def get_average_relationship_level(self) -> float:
        if not self.relationships:
            return 0.0
        return sum(r['level'] for r in self.relationships.values()) / len(self.relationships)
    
    def get_most_connected_npc(self) -> str:
        if not self.graph.nodes:
            return "N/A (No NPCs)"
        degree_centrality = nx.degree_centrality(self.graph)
        return max(degree_centrality, key=degree_centrality.get) if degree_centrality else "N/A"