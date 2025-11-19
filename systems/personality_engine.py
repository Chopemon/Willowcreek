# systems/personality_engine.py
"""
Personality-Driven Decision Making Engine

Enhances NPC autonomy with personality-based behavior:
- Trait-based decision modifiers
- Emotional state influences
- Consistency in character actions
- Dynamic reactions based on personality
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import random


class PersonalityTrait(Enum):
    """Core personality traits"""
    OUTGOING = "outgoing"
    SHY = "shy"
    AMBITIOUS = "ambitious"
    LAZY = "lazy"
    KIND = "kind"
    MEAN = "mean"
    BRAVE = "brave"
    FEARFUL = "fearful"
    IMPULSIVE = "impulsive"
    CAUTIOUS = "cautious"
    ROMANTIC = "romantic"
    PRACTICAL = "practical"
    CREATIVE = "creative"
    LOGICAL = "logical"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"


class PersonalityEngine:
    """
    Enhances NPC decision-making with personality-driven behavior.

    Features:
    - Personality trait extraction from NPC data
    - Decision weighting based on personality
    - Mood-influenced choices
    - Consistent character behavior
    """

    def __init__(self):
        # Map common trait keywords to PersonalityTraits
        self.trait_keywords = {
            'outgoing': PersonalityTrait.OUTGOING,
            'extroverted': PersonalityTrait.OUTGOING,
            'social': PersonalityTrait.OUTGOING,
            'shy': PersonalityTrait.SHY,
            'introverted': PersonalityTrait.SHY,
            'reserved': PersonalityTrait.SHY,
            'ambitious': PersonalityTrait.AMBITIOUS,
            'driven': PersonalityTrait.AMBITIOUS,
            'lazy': PersonalityTrait.LAZY,
            'laid-back': PersonalityTrait.LAZY,
            'kind': PersonalityTrait.KIND,
            'caring': PersonalityTrait.KIND,
            'compassionate': PersonalityTrait.KIND,
            'mean': PersonalityTrait.MEAN,
            'cruel': PersonalityTrait.MEAN,
            'brave': PersonalityTrait.BRAVE,
            'courageous': PersonalityTrait.BRAVE,
            'fearful': PersonalityTrait.FEARFUL,
            'anxious': PersonalityTrait.FEARFUL,
            'impulsive': PersonalityTrait.IMPULSIVE,
            'spontaneous': PersonalityTrait.IMPULSIVE,
            'cautious': PersonalityTrait.CAUTIOUS,
            'careful': PersonalityTrait.CAUTIOUS,
            'romantic': PersonalityTrait.ROMANTIC,
            'practical': PersonalityTrait.PRACTICAL,
            'realistic': PersonalityTrait.PRACTICAL,
            'creative': PersonalityTrait.CREATIVE,
            'artistic': PersonalityTrait.CREATIVE,
            'logical': PersonalityTrait.LOGICAL,
            'rational': PersonalityTrait.LOGICAL,
            'optimistic': PersonalityTrait.OPTIMISTIC,
            'cheerful': PersonalityTrait.OPTIMISTIC,
            'pessimistic': PersonalityTrait.PESSIMISTIC,
            'cynical': PersonalityTrait.PESSIMISTIC,
        }

    # ========================================================================
    # PERSONALITY EXTRACTION
    # ========================================================================

    def extract_traits(self, npc) -> List[PersonalityTrait]:
        """Extract personality traits from NPC data"""
        traits = []

        # Check coreTraits field
        if hasattr(npc, 'coreTraits') and npc.coreTraits:
            for trait_str in npc.coreTraits:
                trait_lower = trait_str.lower()
                for keyword, trait in self.trait_keywords.items():
                    if keyword in trait_lower and trait not in traits:
                        traits.append(trait)

        # If no traits found, assign some defaults based on age
        if not traits:
            if npc.age < 18:
                traits.append(PersonalityTrait.IMPULSIVE)
            elif npc.age < 30:
                traits.append(PersonalityTrait.AMBITIOUS)
            else:
                traits.append(PersonalityTrait.CAUTIOUS)

        return traits

    # ========================================================================
    # DECISION MAKING
    # ========================================================================

    def make_decision(
        self,
        npc,
        options: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Choose from multiple options based on personality.

        Args:
            npc: The NPC making the decision
            options: List of dicts with 'action', 'location', 'weight' keys
            context: Additional context (mood, needs, etc.)

        Returns:
            The chosen option
        """
        if not options:
            return {'action': 'idle', 'location': npc.current_location}

        traits = self.extract_traits(npc)
        context = context or {}

        # Modify weights based on personality
        weighted_options = []
        for option in options:
            base_weight = option.get('weight', 1.0)
            modified_weight = self._apply_personality_modifiers(
                base_weight, option, traits, npc, context
            )
            weighted_options.append({
                **option,
                'final_weight': max(0.01, modified_weight)  # Ensure positive
            })

        # Choose based on weighted random selection
        total_weight = sum(opt['final_weight'] for opt in weighted_options)
        rand_val = random.uniform(0, total_weight)

        cumulative = 0
        for option in weighted_options:
            cumulative += option['final_weight']
            if rand_val <= cumulative:
                return option

        return weighted_options[0]  # Fallback

    def _apply_personality_modifiers(
        self,
        base_weight: float,
        option: Dict[str, Any],
        traits: List[PersonalityTrait],
        npc,
        context: Dict[str, Any]
    ) -> float:
        """Apply personality-based modifiers to decision weight"""
        weight = base_weight
        action = option.get('action', '').lower()
        option_type = option.get('type', '').lower()

        # OUTGOING vs SHY
        if PersonalityTrait.OUTGOING in traits:
            if 'social' in action or option_type == 'social':
                weight *= 1.5
        elif PersonalityTrait.SHY in traits:
            if 'social' in action or option_type == 'social':
                weight *= 0.5
            if 'home' in action or 'bedroom' in option.get('location', '').lower():
                weight *= 1.3

        # AMBITIOUS vs LAZY
        if PersonalityTrait.AMBITIOUS in traits:
            if any(word in action for word in ['work', 'study', 'practice', 'improve']):
                weight *= 1.4
        elif PersonalityTrait.LAZY in traits:
            if any(word in action for word in ['work', 'study', 'exercise']):
                weight *= 0.6
            if any(word in action for word in ['relax', 'rest', 'sleep']):
                weight *= 1.4

        # IMPULSIVE vs CAUTIOUS
        if PersonalityTrait.IMPULSIVE in traits:
            if option_type == 'risky' or 'adventure' in action:
                weight *= 1.5
        elif PersonalityTrait.CAUTIOUS in traits:
            if option_type == 'risky':
                weight *= 0.4
            if option_type == 'safe':
                weight *= 1.3

        # ROMANTIC
        if PersonalityTrait.ROMANTIC in traits:
            if 'romance' in action or 'date' in action:
                weight *= 1.6

        # CREATIVE vs LOGICAL
        if PersonalityTrait.CREATIVE in traits:
            if any(word in action for word in ['create', 'art', 'music', 'write']):
                weight *= 1.4
        elif PersonalityTrait.LOGICAL in traits:
            if any(word in action for word in ['analyze', 'solve', 'plan']):
                weight *= 1.4

        # KIND vs MEAN
        if PersonalityTrait.KIND in traits:
            if 'help' in action or option_type == 'altruistic':
                weight *= 1.5
        elif PersonalityTrait.MEAN in traits:
            if 'help' in action:
                weight *= 0.5
            if 'competitive' in option_type or 'conflict' in action:
                weight *= 1.3

        # OPTIMISTIC vs PESSIMISTIC (affects risk tolerance)
        if PersonalityTrait.OPTIMISTIC in traits:
            if option_type == 'risky':
                weight *= 1.2
        elif PersonalityTrait.PESSIMISTIC in traits:
            if option_type == 'safe':
                weight *= 1.2

        # Mood modifiers
        mood = getattr(npc, 'mood', 'Neutral').lower()
        if mood in ['happy', 'excited', 'joyful']:
            if option_type == 'social':
                weight *= 1.2
        elif mood in ['sad', 'depressed', 'lonely']:
            if 'home' in action or option_type == 'solitary':
                weight *= 1.3

        # Needs-based urgency
        if context.get('urgent_need'):
            # If this action addresses urgent need, boost it
            if option.get('addresses_need') == context.get('urgent_need'):
                weight *= 2.0

        return weight

    # ========================================================================
    # GOAL PRIORITIZATION
    # ========================================================================

    def prioritize_goals(
        self,
        npc,
        goals: List[Any]
    ) -> List[Any]:
        """
        Reorder goals based on personality.

        Args:
            npc: The NPC
            goals: List of Goal objects

        Returns:
            Reordered list of goals
        """
        traits = self.extract_traits(npc)

        # Calculate priority scores
        scored_goals = []
        for goal in goals:
            score = goal.urgency  # Base score

            # Personality modifiers
            goal_cat = goal.category.lower()

            if PersonalityTrait.AMBITIOUS in traits:
                if goal_cat in ['career', 'skill', 'achievement']:
                    score += 0.2
            elif PersonalityTrait.LAZY in traits:
                if goal_cat in ['career', 'skill']:
                    score -= 0.2

            if PersonalityTrait.OUTGOING in traits:
                if goal_cat == 'social':
                    score += 0.15
            elif PersonalityTrait.SHY in traits:
                if goal_cat == 'social':
                    score -= 0.15

            if PersonalityTrait.ROMANTIC in traits:
                if goal_cat == 'romance':
                    score += 0.25

            if PersonalityTrait.KIND in traits:
                if goal_cat == 'help_others':
                    score += 0.2

            scored_goals.append((score, goal))

        # Sort by score (descending)
        scored_goals.sort(key=lambda x: x[0], reverse=True)

        return [goal for score, goal in scored_goals]

    # ========================================================================
    # REACTION GENERATION
    # ========================================================================

    def generate_reaction(
        self,
        npc,
        event_type: str,
        event_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate personality-appropriate reaction to event.

        Args:
            npc: The NPC
            event_type: Type of event ('good_news', 'bad_news', 'surprise', etc.)
            event_context: Additional context

        Returns:
            Reaction mood/emotion string
        """
        traits = self.extract_traits(npc)
        event_context = event_context or {}

        # Base reactions
        reactions = {
            'good_news': 'happy',
            'bad_news': 'sad',
            'surprise': 'surprised',
            'conflict': 'angry',
            'achievement': 'proud',
            'romance': 'excited',
            'loss': 'grief'
        }

        base_reaction = reactions.get(event_type, 'neutral')

        # Personality modifications
        if event_type == 'good_news':
            if PersonalityTrait.OPTIMISTIC in traits:
                return 'elated'
            elif PersonalityTrait.PESSIMISTIC in traits:
                return 'cautiously_happy'

        elif event_type == 'bad_news':
            if PersonalityTrait.OPTIMISTIC in traits:
                return 'disappointed_but_hopeful'
            elif PersonalityTrait.PESSIMISTIC in traits:
                return 'devastated'
            elif PersonalityTrait.BRAVE in traits:
                return 'determined'
            elif PersonalityTrait.FEARFUL in traits:
                return 'anxious'

        elif event_type == 'conflict':
            if PersonalityTrait.BRAVE in traits:
                return 'confrontational'
            elif PersonalityTrait.FEARFUL in traits:
                return 'scared'
            elif PersonalityTrait.MEAN in traits:
                return 'aggressive'
            elif PersonalityTrait.KIND in traits:
                return 'conciliatory'

        elif event_type == 'social_invitation':
            if PersonalityTrait.OUTGOING in traits:
                return 'excited'
            elif PersonalityTrait.SHY in traits:
                return 'nervous'

        return base_reaction

    # ========================================================================
    # BEHAVIOR CONSISTENCY
    # ========================================================================

    def is_action_consistent(
        self,
        npc,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, float]:
        """
        Check if an action is consistent with NPC's personality.

        Returns:
            (is_consistent, consistency_score)
            consistency_score: 0.0 (very inconsistent) to 1.0 (very consistent)
        """
        traits = self.extract_traits(npc)
        context = context or {}
        score = 0.5  # Neutral starting point

        action_lower = action.lower()

        # Check for major inconsistencies
        if PersonalityTrait.SHY in traits and 'public_speech' in action_lower:
            score = 0.2
        elif PersonalityTrait.OUTGOING in traits and 'avoid_people' in action_lower:
            score = 0.3
        elif PersonalityTrait.KIND in traits and 'betray' in action_lower:
            score = 0.1
        elif PersonalityTrait.BRAVE in traits and 'flee_from_confrontation' in action_lower:
            score = 0.2
        elif PersonalityTrait.LAZY in traits and 'extra_work' in action_lower:
            score = 0.3
        elif PersonalityTrait.AMBITIOUS in traits and 'quit_job' in action_lower:
            score = 0.2
        else:
            score = 0.7  # Most actions are reasonably consistent

        # Strong personality matches boost score
        if PersonalityTrait.ROMANTIC in traits and 'romance' in action_lower:
            score = 0.9
        elif PersonalityTrait.CREATIVE in traits and 'create' in action_lower:
            score = 0.9

        is_consistent = score >= 0.5
        return is_consistent, score

    # ========================================================================
    # PERSONALITY SUMMARY
    # ========================================================================

    def get_personality_summary(self, npc) -> Dict[str, Any]:
        """Get a summary of NPC's personality profile"""
        traits = self.extract_traits(npc)

        return {
            'name': npc.full_name,
            'traits': [t.value for t in traits],
            'behavioral_tendencies': self._get_behavioral_tendencies(traits),
            'decision_modifiers': self._get_decision_modifiers(traits)
        }

    def _get_behavioral_tendencies(self, traits: List[PersonalityTrait]) -> List[str]:
        """Get list of behavioral tendencies from traits"""
        tendencies = []

        if PersonalityTrait.OUTGOING in traits:
            tendencies.append("Seeks social interaction")
        if PersonalityTrait.SHY in traits:
            tendencies.append("Prefers solitude")
        if PersonalityTrait.AMBITIOUS in traits:
            tendencies.append("Driven to succeed")
        if PersonalityTrait.LAZY in traits:
            tendencies.append("Avoids hard work")
        if PersonalityTrait.KIND in traits:
            tendencies.append("Helps others")
        if PersonalityTrait.MEAN in traits:
            tendencies.append("Causes conflict")
        if PersonalityTrait.ROMANTIC in traits:
            tendencies.append("Values romance")
        if PersonalityTrait.IMPULSIVE in traits:
            tendencies.append("Acts without planning")
        if PersonalityTrait.CAUTIOUS in traits:
            tendencies.append("Thinks before acting")

        return tendencies

    def _get_decision_modifiers(self, traits: List[PersonalityTrait]) -> Dict[str, str]:
        """Get description of how traits modify decisions"""
        modifiers = {}

        if PersonalityTrait.OUTGOING in traits:
            modifiers['social_actions'] = "+50% weight"
        if PersonalityTrait.SHY in traits:
            modifiers['social_actions'] = "-50% weight"
        if PersonalityTrait.AMBITIOUS in traits:
            modifiers['work_study'] = "+40% weight"
        if PersonalityTrait.LAZY in traits:
            modifiers['work_study'] = "-40% weight"
        if PersonalityTrait.IMPULSIVE in traits:
            modifiers['risky_actions'] = "+50% weight"
        if PersonalityTrait.CAUTIOUS in traits:
            modifiers['risky_actions'] = "-60% weight"

        return modifiers
