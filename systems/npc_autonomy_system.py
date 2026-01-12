# systems/npc_autonomy_system.py
# NPC-to-NPC interactions and autonomous behavior

from typing import Dict, List, Optional
import random

from systems.memory_system import MemoryImportance, MemoryType

class NPCAutonomy:
    def __init__(self):
        self.npc_relationships: Dict[tuple, float] = {}
        self.npc_interactions_today: List[tuple] = []
    
    def simulate_npc_interactions(
        self,
        npcs: List,
        relationship_manager,
        current_day: int,
        current_hour: int,
        memory_system=None,
        economy_system=None,
        llm_client=None,
    ):
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
                        self._npc_interact(
                            npc_a,
                            npc_b,
                            relationship_manager,
                            current_day,
                            current_hour,
                            memory_system=memory_system,
                            economy_system=economy_system,
                            llm_client=llm_client,
                        )
    
    def _npc_interact(
        self,
        npc_a,
        npc_b,
        relationship_manager,
        current_day: int,
        current_hour: int,
        memory_system=None,
        economy_system=None,
        llm_client=None,
    ):
        """Two NPCs interact"""
        interaction_type = self._choose_interaction_type(
            npc_a,
            npc_b,
            relationship_manager,
            current_day,
            current_hour,
            memory_system=memory_system,
            economy_system=economy_system,
            llm_client=llm_client,
        )
        if interaction_type == "ignore":
            return
        
        relationship_manager.record_interaction(npc_a.full_name, npc_b.full_name, interaction_type)
        self.npc_interactions_today.append((npc_a.full_name, npc_b.full_name, interaction_type))

        if memory_system:
            description = f"{npc_a.full_name} and {npc_b.full_name} {interaction_type}ed."
            memory_system.add_memory(
                npc_a.full_name,
                memory_type=MemoryType.CONVERSATION,
                description=description,
                sim_day=current_day,
                sim_hour=current_hour,
                importance=MemoryImportance.MINOR,
                participants=[npc_b.full_name],
                emotional_tone=self._tone_for_interaction(interaction_type),
                tags=["autonomy", interaction_type],
            )
            memory_system.add_memory(
                npc_b.full_name,
                memory_type=MemoryType.CONVERSATION,
                description=description,
                sim_day=current_day,
                sim_hour=current_hour,
                importance=MemoryImportance.MINOR,
                participants=[npc_a.full_name],
                emotional_tone=self._tone_for_interaction(interaction_type),
                tags=["autonomy", interaction_type],
            )

    def _choose_interaction_type(
        self,
        npc_a,
        npc_b,
        relationship_manager,
        current_day: int,
        current_hour: int,
        memory_system=None,
        economy_system=None,
        llm_client=None,
    ) -> str:
        if not llm_client:
            return random.choice(["talk", "flirt", "conflict"])

        relationship = relationship_manager.get_relationship(npc_a.full_name, npc_b.full_name)
        memory_context = ""
        if memory_system:
            memory_context = memory_system.build_memory_context(
                npc_a.full_name,
                current_sim_day=current_day,
                limit=3,
            )

        job_context = ""
        if economy_system:
            job = economy_system.get_job(npc_a.full_name)
            if job:
                job_context = f"Job: {job.title} at {job.employer} (Level {job.level})."

        prompt = (
            "Decide the NPC's immediate interaction with another NPC. "
            "Respond with exactly one word from: talk, flirt, conflict, ignore.\n"
            f"NPC A: {npc_a.full_name}\n"
            f"NPC B: {npc_b.full_name}\n"
            f"Relationship: friendship {relationship.friendship_points:.0f}, "
            f"romance {relationship.romantic_points:.0f}, status {relationship.status.name}\n"
            f"Day {current_day}, Hour {current_hour}\n"
            f"{job_context}\n"
            f"{memory_context}\n"
            "Choice:"
        )

        response = llm_client.generate(prompt, max_new_tokens=10, temperature=0.4).text.strip().lower()
        for token in response.replace(",", " ").split():
            if token in {"talk", "flirt", "conflict", "ignore"}:
                return token
        return random.choice(["talk", "flirt", "conflict"])

    @staticmethod
    def _tone_for_interaction(interaction_type: str) -> str:
        if interaction_type == "flirt":
            return "warm"
        if interaction_type == "conflict":
            return "tense"
        return "neutral"
