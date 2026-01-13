# game_manager.py
# Unified game manager that integrates all 17 systems

from typing import Optional, Dict, List
from systems.skill_system import SkillSystem, SkillType, XP_REWARDS
from systems.inventory_system import InventorySystem
from systems.memory_system import MemorySystem, MemoryType, MemoryImportance
from systems.relationship_system import RelationshipManager
from systems.reputation_system import ReputationSystem, ReputationTrait, GossipType
from systems.dialogue_system import DialogueSystem
from systems.social_events_system import SocialEventsSystem, EventType
from systems.family_system import FamilySystem, FamilyRelation
from systems.dynamic_events_system import DynamicEventsSystem
from systems.economy_system import EconomySystem
from systems.location_system import LocationSystem
from systems.npc_autonomy_system import NPCAutonomy
from systems.statistics_system import StatisticsSystem
from systems.save_system import SaveSystem
from systems.intimate_system import IntimateSystem
from systems.consequences_system import ConsequencesSystem


class GameManager:
    """
    Unified game manager that coordinates all game systems.
    This is the main integration point for the Willow Creek simulation.
    """

    def __init__(self, simulation=None, llm_client=None):
        self.sim = simulation
        self.llm_client = llm_client

        # Initialize all systems
        self.skills = SkillSystem()
        self.inventory = InventorySystem()
        self.memory = MemorySystem()
        self.relationships = RelationshipManager()
        self.reputation = ReputationSystem()
        self.dialogue = DialogueSystem()
        self.social_events = SocialEventsSystem()
        self.family = FamilySystem()
        self.dynamic_events = DynamicEventsSystem()
        self.economy = EconomySystem()
        self.locations = LocationSystem()
        self.npc_autonomy = NPCAutonomy()
        self.statistics = StatisticsSystem()
        self.save_system = SaveSystem()
        self.intimate = IntimateSystem()
        self.consequences = ConsequencesSystem()

        print("[GameManager] All 17 systems initialized successfully!")

    def initialize_character(self, character_name: str, is_player: bool = False):
        """Initialize all system data for a character"""
        # Skills
        self.skills.initialize_character(character_name)

        # Inventory
        inventory = self.inventory.get_inventory(character_name)
        if is_player:
            # Give player some starting items
            inventory.add_item("coffee", 3)
            inventory.add_item("flowers", 1)
            inventory.money = 1000  # Start with more money

        # Statistics
        if is_player:
            self.statistics.get_stats(character_name)

        # Reputation
        self.reputation.get_reputation(character_name)

        print(f"[GameManager] Initialized character: {character_name}")

    # ========================================================================
    # INTERACTION METHODS
    # ========================================================================

    def talk_to_npc(self, player_name: str, npc_name: str):
        """Player talks to an NPC"""
        # Record interaction
        self.relationships.record_interaction(player_name, npc_name, "talk")

        # Add XP
        xp_gained = self.skills.add_experience(player_name, SkillType.CHARISMA, 5)
        self.skills.add_experience(player_name, SkillType.EMPATHY, 3)

        # Add memory
        if self.sim:
            self.memory.add_memory(
                player_name,
                MemoryType.CONVERSATION,
                f"Had a conversation with {npc_name}",
                self.sim.time.total_days,
                self.sim.time.hour,
                MemoryImportance.MINOR,
                participants=[npc_name],
                emotional_tone="friendly",
                tags=["conversation"],
            )

        # Update statistics
        self.statistics.record_conversation(player_name)

        # Check for first meeting
        rel = self.relationships.get_relationship(player_name, npc_name)
        if rel.times_talked == 1:
            self.statistics.record_npc_met(player_name)

        return xp_gained

    def flirt_with_npc(self, player_name: str, npc_name: str) -> tuple[bool, str]:
        """Player flirts with NPC"""
        # Skill check
        success, roll = self.skills.perform_skill_check(player_name, SkillType.SEDUCTION, difficulty=40)

        if success:
            # Successful flirt
            self.relationships.record_interaction(player_name, npc_name, "flirt")
            self.skills.add_experience(player_name, SkillType.SEDUCTION, 8)
            self.skills.add_experience(player_name, SkillType.CHARISMA, 3)
            self.reputation.handle_action_reputation(player_name, "flirt")

            return True, f"Your flirt was successful! (Roll: {roll:.0f})"
        else:
            # Failed flirt - awkward
            self.reputation.add_reputation_trait(player_name, ReputationTrait.CREEPY, 5)
            return False, f"That was awkward... (Roll: {roll:.0f})"

    def give_gift(self, giver: str, receiver: str, item_id: str) -> tuple[bool, str]:
        """Give a gift to an NPC"""
        success, msg = self.inventory.give_item(giver, receiver, item_id, 1)

        if success:
            # Record gift
            self.relationships.record_interaction(giver, receiver, "gift")

            # Add memory
            item = self.inventory.get_item(item_id)
            if self.sim and item:
                self.memory.add_memory(
                    giver,
                    MemoryType.GIFT_GIVEN,
                    f"Gave {item.name} to {receiver}",
                    self.sim.time.total_days,
                    self.sim.time.hour,
                    MemoryImportance.MODERATE,
                    participants=[receiver],
                    emotional_tone="warm",
                    tags=["gift"],
                )

                self.memory.add_memory(
                    receiver,
                    MemoryType.GIFT_RECEIVED,
                    f"Received {item.name} from {giver}",
                    self.sim.time.total_days,
                    self.sim.time.hour,
                    MemoryImportance.MODERATE,
                    participants=[giver],
                    emotional_tone="grateful",
                    tags=["gift"],
                )

            # Reputation boost
            self.reputation.handle_action_reputation(giver, "gift_giving")

            # Statistics
            stats = self.statistics.get_stats(giver)
            stats.gifts_given += 1

            receiver_stats = self.statistics.get_stats(receiver)
            receiver_stats.gifts_received += 1

        return success, msg

    def go_on_date(self, person_a: str, person_b: str, location: str) -> str:
        """Two people go on a date"""
        # Record date
        self.relationships.record_interaction(person_a, person_b, "date")

        # Add XP
        self.skills.add_experience(person_a, SkillType.CHARISMA, 10)
        self.skills.add_experience(person_a, SkillType.SEDUCTION, 5)

        # Add memories
        if self.sim:
            for person in [person_a, person_b]:
                other = person_b if person == person_a else person_a
                self.memory.add_memory(
                    person,
                    MemoryType.DATE,
                    f"Went on a date with {other} at {location}",
                    self.sim.time.total_days,
                    self.sim.time.hour,
                    MemoryImportance.SIGNIFICANT,
                    participants=[other],
                    location=location,
                    emotional_tone="romantic",
                    tags=["date"],
                )

        # Statistics
        self.statistics.record_date(person_a)

        return f"{person_a} and {person_b} had a wonderful date at {location}!"

    def perform_activity(self, character_name: str, activity: str, location: str = ""):
        """Character performs an activity and gains appropriate XP"""
        if activity in XP_REWARDS:
            messages = []
            for skill_type, xp in XP_REWARDS[activity].items():
                level_ups = self.skills.add_experience(character_name, skill_type, xp)
                messages.extend(level_ups)

                # Track skill leveling
                if level_ups:
                    stats = self.statistics.get_stats(character_name)
                    stats.skills_leveled += len(level_ups)

            # Record location visit
            if location:
                self.statistics.record_location_visit(character_name, location)

            return messages
        return []

    # ========================================================================
    # DAILY SIMULATION
    # ========================================================================

    def simulate_day(self):
        """Run daily simulation for all systems"""
        if not self.sim:
            return

        current_day = self.sim.time.total_days
        current_hour = self.sim.time.hour

        # NPC autonomy - NPCs interact with each other
        self.npc_autonomy.simulate_npc_interactions(
            self.sim.npcs,
            self.relationships,
            current_day,
            current_hour,
            memory_system=self.memory,
            economy_system=self.economy,
            llm_client=self.llm_client,
        )

        # Decay memories for all characters
        self.memory.decay_memories(current_day)

        # Gossip spreads
        self.reputation.simulate_gossip_spread(self.sim.npcs, current_day)

        # Check for consequences
        self.consequences.check_for_consequences(
            self.relationships,
            self.reputation,
            getattr(self.sim, 'pregnancy', None),
            current_day
        )

        # Weekly wage payment (every 7 days)
        if current_day % 7 == 0:
            self.economy.pay_weekly_wages()
            for character_name in list(self.economy.character_jobs.keys()):
                self.economy.evaluate_promotions(character_name)

    # ========================================================================
    # SAVE/LOAD
    # ========================================================================

    def save_game(self, slot_name: str) -> bool:
        """Save entire game state"""
        game_state = {
            'current_day': self.sim.time.total_days if self.sim else 0,
            'current_hour': self.sim.time.hour if self.sim else 0,
            # Add minimal state - full state requires serialization work
            'player_inventory': {
                'items': self.inventory.get_inventory("Malcolm Newt").items,
                'money': self.inventory.get_inventory("Malcolm Newt").money
            },
            'player_skills': {
                skill_type.value: skill.level
                for skill_type, skill in self.skills.character_skills.get("Malcolm Newt", {}).items()
            }
        }

        return self.save_system.save_game(slot_name, game_state)

    def load_game(self, slot_name: str) -> Optional[Dict]:
        """Load game state"""
        return self.save_system.load_game(slot_name)

    # ========================================================================
    # UI DATA METHODS
    # ========================================================================

    def get_player_dashboard(self, player_name: str = "Malcolm Newt") -> Dict:
        """Get all data for player dashboard UI"""
        inventory = self.inventory.get_inventory(player_name)
        stats = self.statistics.get_stats(player_name)
        reputation = self.reputation.get_reputation(player_name)

        # Get top skills
        top_skills = self.skills.get_top_skills(player_name, 5)

        # Get recent memories (use get_memories with limit parameter)
        recent_memories = self.memory.get_memories(player_name, limit=10)

        # Get active relationships
        active_relationships = []
        for (person_a, person_b), rel in self.relationships.relationships.items():
            if player_name in (person_a, person_b):
                other = person_b if person_a == player_name else person_a
                active_relationships.append({
                    'name': other,
                    'status': rel.status.name,
                    'friendship': rel.friendship_points,
                    'romance': rel.romantic_points
                })

        return {
            'money': inventory.money,
            'inventory_items': len(inventory.items),
            'reputation_score': reputation.overall_score,
            'top_skills': [(st.value, level) for st, level in top_skills],
            'npcs_met': stats.npcs_met,
            'conversations': stats.conversations_had,
            'dates': stats.dates_been_on,
            'friends': stats.friends_made,
            'recent_memories': [m.get_summary() for m in recent_memories],
            'relationships': active_relationships[:10]
        }

    def get_npc_info(self, npc_name: str, player_name: str = "Malcolm Newt") -> Dict:
        """Get detailed NPC information for UI"""
        rel = self.relationships.get_relationship(player_name, npc_name)
        rep = self.reputation.get_reputation(npc_name)
        memories = self.memory.get_memories(player_name, participant=npc_name, limit=5)

        return {
            'name': npc_name,
            'relationship_status': rel.status.name,
            'friendship': rel.friendship_points,
            'romance': rel.romantic_points,
            'trust': rel.trust,
            'attraction': rel.attraction.name,
            'times_talked': rel.times_talked,
            'times_dated': rel.times_dated,
            'reputation': rep.overall_score,
            'reputation_traits': [t.value for t in rep.get_primary_traits(3)],
            'shared_memories': [m.get_summary() for m in memories]
        }


# Global game manager instance
game_manager: Optional[GameManager] = None


def get_game_manager(simulation=None) -> GameManager:
    """Get or create the global game manager"""
    global game_manager
    if game_manager is None:
        game_manager = GameManager(simulation)
    return game_manager
