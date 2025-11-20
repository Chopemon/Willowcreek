# services/scene_image_generator.py
"""
Intelligent Scene Image Generator for Willowcreek
Analyzes narrative events and generates appropriate image prompts for ComfyUI.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class SceneContext:
    """Context information for image generation"""
    scene_type: str  # "sexual", "quirk", "drama", "crime", "casual"
    priority: int  # 1-10, higher = more important to visualize
    characters: List[str]
    location: str
    time_of_day: str  # "morning", "afternoon", "evening", "night"
    weather: str
    mood: str  # "tense", "passionate", "playful", "dark", etc.
    explicit_level: int  # 0-10, how NSFW the scene is
    activity: str  # Brief description of what's happening
    raw_event: str  # Original event text


class SceneAnalyzer:
    """
    Analyzes simulation events to determine which deserve image generation
    and builds appropriate prompts.
    """

    def __init__(self):
        # Event patterns and their priorities
        self.patterns = {
            # Sexual activity (highest priority)
            r"\[SEXUAL:": {"type": "sexual", "priority": 10, "explicit": 8},
            r"\[SEXUAL ENCOUNTER:": {"type": "sexual", "priority": 10, "explicit": 8},

            # Character quirks (high visual impact)
            r"\[EMMA REFLEX:": {"type": "quirk", "priority": 9, "explicit": 7},
            r"\[ALEX STURM:.*Frustration": {"type": "quirk", "priority": 8, "explicit": 6},
            r"\[LIANNA:.*jealous": {"type": "quirk", "priority": 7, "explicit": 3},
            r"\[LISA FOX:.*dominant": {"type": "quirk", "priority": 7, "explicit": 5},

            # School drama
            r"hallway.*argument": {"type": "drama", "priority": 6, "explicit": 2},
            r"gossip.*spread": {"type": "drama", "priority": 5, "explicit": 1},

            # Crime
            r"\[CRIME:": {"type": "crime", "priority": 7, "explicit": 3},

            # General dramatic moments
            r"tension.*builds": {"type": "tension", "priority": 6, "explicit": 4},
            r"confrontation": {"type": "drama", "priority": 6, "explicit": 2},
        }

    def should_generate_image(self, event_text: str) -> bool:
        """
        Determine if an event is visually interesting enough for image generation.

        Args:
            event_text: The event description from scenario_buffer

        Returns:
            True if image should be generated
        """
        # Check against patterns
        for pattern, config in self.patterns.items():
            if re.search(pattern, event_text, re.IGNORECASE):
                return config["priority"] >= 6  # Threshold for image generation

        return False

    def analyze_scene(self, event_text: str, sim: Any, malcolm: Any) -> Optional[SceneContext]:
        """
        Analyze an event and extract scene context for image generation.

        Args:
            event_text: The event description
            sim: The simulation object
            malcolm: Malcolm NPC object

        Returns:
            SceneContext if scene should be visualized, None otherwise
        """
        if not self.should_generate_image(event_text):
            return None

        # Determine scene type and config
        scene_config = self._match_pattern(event_text)
        if not scene_config:
            return None

        # Extract characters mentioned
        characters = self._extract_characters(event_text, sim)

        # Build context
        context = SceneContext(
            scene_type=scene_config["type"],
            priority=scene_config["priority"],
            characters=characters,
            location=malcolm.current_location or "Unknown Location",
            time_of_day=self._get_time_of_day(sim.time.hour),
            weather=getattr(sim.world, "weather", "clear"),
            mood=self._extract_mood(event_text, scene_config["type"]),
            explicit_level=scene_config["explicit"],
            activity=self._extract_activity(event_text),
            raw_event=event_text
        )

        return context

    def _match_pattern(self, text: str) -> Optional[Dict]:
        """Find the first matching pattern and return its config"""
        for pattern, config in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return config
        return None

    def _extract_characters(self, text: str, sim: Any) -> List[str]:
        """Extract character names mentioned in the event"""
        characters = []

        # Always include Malcolm
        characters.append("Malcolm Newt")

        # Check for NPC names in text
        if hasattr(sim, 'npc_dict'):
            for npc_name in sim.npc_dict.keys():
                if npc_name in text:
                    characters.append(npc_name)

        return list(set(characters))  # Remove duplicates

    def _get_time_of_day(self, hour: int) -> str:
        """Convert hour to time of day description"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def _extract_mood(self, text: str, scene_type: str) -> str:
        """Determine the mood/atmosphere of the scene"""
        text_lower = text.lower()

        # Keyword-based mood detection
        if any(word in text_lower for word in ["passion", "desire", "lust", "aroused"]):
            return "passionate"
        elif any(word in text_lower for word in ["tense", "tension", "anxious", "nervous"]):
            return "tense"
        elif any(word in text_lower for word in ["playful", "teasing", "giggle"]):
            return "playful"
        elif any(word in text_lower for word in ["dark", "shadow", "forbidden", "secret"]):
            return "dark"
        elif any(word in text_lower for word in ["angry", "argument", "fight"]):
            return "confrontational"
        elif any(word in text_lower for word in ["gentle", "soft", "tender"]):
            return "intimate"

        # Default by scene type
        mood_defaults = {
            "sexual": "passionate",
            "quirk": "tense",
            "drama": "confrontational",
            "crime": "dark",
            "tension": "tense"
        }
        return mood_defaults.get(scene_type, "atmospheric")

    def _extract_activity(self, text: str) -> str:
        """Extract a brief description of what's happening"""
        # Remove system tags
        cleaned = re.sub(r'\[.*?\]', '', text).strip()

        # Take first sentence or up to 100 chars
        sentences = cleaned.split('.')
        if sentences:
            return sentences[0][:100].strip()

        return cleaned[:100].strip()


class ImagePromptGenerator:
    """
    Generates detailed image prompts for ComfyUI based on scene context.
    Optimized for creating cinematic, narrative-driven images.
    """

    def __init__(self):
        # Base quality tags for all images
        self.base_quality = "masterpiece, best quality, highly detailed, 4k, professional photograph"

        # Style presets for different scene types
        self.style_presets = {
            "sexual": "intimate photography, soft lighting, shallow depth of field, cinematic",
            "quirk": "dramatic moment, character focus, emotional expression, narrative storytelling",
            "drama": "tense atmosphere, dynamic composition, environmental storytelling",
            "crime": "dark atmosphere, film noir, high contrast, moody lighting",
            "tension": "psychological tension, subtle expressions, atmospheric"
        }

        # Negative prompt defaults
        self.base_negative = "low quality, blurry, distorted, ugly, deformed, cartoon, anime, bad anatomy"

    def generate_prompt(self, context: SceneContext) -> Tuple[str, str]:
        """
        Generate a detailed image prompt from scene context.

        Args:
            context: SceneContext with scene information

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        # Build character descriptions
        character_desc = self._build_character_description(context.characters)

        # Build setting description
        setting_desc = self._build_setting_description(
            context.location, context.time_of_day, context.weather
        )

        # Build action/pose description
        action_desc = self._build_action_description(context.activity, context.scene_type)

        # Get style preset
        style = self.style_presets.get(context.scene_type, "cinematic photography")

        # Mood/atmosphere
        mood_desc = self._build_mood_description(context.mood)

        # Compose positive prompt
        positive_parts = [
            self.base_quality,
            style,
            character_desc,
            action_desc,
            setting_desc,
            mood_desc
        ]

        positive_prompt = ", ".join(filter(None, positive_parts))

        # Build negative prompt
        negative_prompt = self._build_negative_prompt(context.explicit_level)

        # Log the generated prompts
        print(f"\n[ImageGen] === Generated Prompts ===")
        print(f"[ImageGen] Positive: {positive_prompt}")
        print(f"[ImageGen] Negative: {negative_prompt}")
        print(f"[ImageGen] ========================\n")

        return positive_prompt, negative_prompt

    def _build_character_description(self, characters: List[str]) -> str:
        """Build description of characters in the scene"""
        if not characters:
            return "person"

        # For now, use generic descriptions
        # TODO: Add character-specific appearance data
        if len(characters) == 1:
            return "1person, adult, realistic human"
        elif len(characters) == 2:
            return "2people, man and woman, realistic humans"
        else:
            return f"{len(characters)}people, group, realistic humans"

    def _build_setting_description(self, location: str, time: str, weather: str) -> str:
        """Build description of the setting"""
        parts = []

        # Location keywords
        if "school" in location.lower():
            parts.append("school setting, hallway or classroom")
        elif "home" in location.lower() or "bedroom" in location.lower():
            parts.append("bedroom interior, residential setting")
        elif "mall" in location.lower() or "shop" in location.lower():
            parts.append("shopping area, commercial interior")
        elif "park" in location.lower():
            parts.append("outdoor park, natural setting")
        else:
            parts.append("interior space")

        # Time of day
        time_lighting = {
            "morning": "soft morning light",
            "afternoon": "bright daylight",
            "evening": "golden hour, warm lighting",
            "night": "dim lighting, night atmosphere"
        }
        parts.append(time_lighting.get(time, "natural lighting"))

        return ", ".join(parts)

    def _build_action_description(self, activity: str, scene_type: str) -> str:
        """Build description of what's happening"""
        # Use the extracted activity
        if activity:
            # Sanitize and condense activity description
            sanitized = activity.replace('"', '').replace('[', '').replace(']', '')
            return sanitized[:80]  # Limit length

        # Fallback based on scene type
        defaults = {
            "sexual": "intimate moment, close proximity",
            "quirk": "character-specific moment, unique expression",
            "drama": "confrontation, intense interaction",
            "crime": "secretive action, furtive behavior",
            "tension": "tense moment, psychological intensity"
        }
        return defaults.get(scene_type, "narrative moment")

    def _build_mood_description(self, mood: str) -> str:
        """Build atmospheric/mood description"""
        mood_tags = {
            "passionate": "intense emotion, passionate atmosphere",
            "tense": "tension, anxious energy, dramatic lighting",
            "playful": "lighthearted, playful energy",
            "dark": "dark atmosphere, shadows, mysterious",
            "confrontational": "conflict, aggressive posturing",
            "intimate": "intimate, private moment, soft focus"
        }
        return mood_tags.get(mood, "atmospheric, emotional depth")

    def _build_negative_prompt(self, explicit_level: int) -> str:
        """Build negative prompt based on explicit level"""
        negative_parts = [self.base_negative]

        # Add more restrictions for highly explicit scenes
        if explicit_level >= 8:
            negative_parts.append("explicit nudity, pornographic, genitals")
        elif explicit_level >= 5:
            negative_parts.append("overly sexual, explicit content")

        # Always avoid these
        negative_parts.append("text, watermark, logo, multiple heads, bad hands")

        return ", ".join(negative_parts)
