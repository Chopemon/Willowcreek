# systems/npc_autonomy_system.py
# NPC-to-NPC interactions and autonomous behavior

from typing import Dict, List, Optional
import random


class NPCAutonomy:
    def __init__(self):
        self.npc_relationships: Dict[tuple, float] = {}
        self.npc_interactions_today: List[tuple] = []
    
    def simulate_npc_interactions(self, npcs: List, relationship_manager, current_day: int, current_hour: int):
        """Simulate NPCs interacting with each other"""
        self.npc_interactions_today = []
        
        # Group NPCs by location
        location_groups = {}
        for npc in npcs:
            loc = getattr(npc, 'current_location', 'Unknown')
            if loc not in location_groups:
                location_groups[loc] = []
            location_groups[loc].append(npc)
        
        # NPCs at same location might interact
        for location, npc_group in location_groups.items():
            if len(npc_group) < 2:
                continue
            
            # Random pairwise interactions
            for i, npc_a in enumerate(npc_group):
                for npc_b in npc_group[i+1:]:
                    # 20% chance of interaction
                    if random.random() < 0.2:
                        self._npc_interact(npc_a, npc_b, relationship_manager)
    
    def _npc_interact(self, npc_a, npc_b, relationship_manager):
        """Two NPCs interact"""
        interaction_type = random.choice(["talk", "flirt", "conflict"])
        
        relationship_manager.record_interaction(npc_a.full_name, npc_b.full_name, interaction_type)
        self.npc_interactions_today.append((npc_a.full_name, npc_b.full_name, interaction_type))
