# services/npc_portrait_generator.py
"""
NPC Portrait Generator for Willowcreek
Generates and caches character portrait images using ComfyUI.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Tuple
import asyncio


class NPCPortraitGenerator:
    """
    Manages NPC portrait generation and caching.
    Creates consistent portrait images for NPCs in the game.
    """

    def __init__(self, comfyui_client=None):
        """
        Initialize portrait generator.

        Args:
            comfyui_client: ComfyUIClient instance for image generation
        """
        self.comfyui_client = comfyui_client
        self.base_dir = Path(__file__).parent.parent
        self.portraits_dir = self.base_dir / "static" / "npc_portraits"
        self.portraits_dir.mkdir(exist_ok=True)

        # Cache file to track generated portraits
        self.cache_file = self.portraits_dir / "portrait_cache.json"
        self.portrait_cache = self._load_cache()

        print(f"[PortraitGen] Initialized. Cache contains {len(self.portrait_cache)} portraits")

    def _load_cache(self) -> Dict[str, str]:
        """Load portrait cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[PortraitGen] Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """Save portrait cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.portrait_cache, f, indent=2)
        except Exception as e:
            print(f"[PortraitGen] Error saving cache: {e}")

    def has_portrait(self, npc_name: str, portrait_type: str = "headshot") -> bool:
        """Check if NPC already has a portrait of specified type."""
        cache_key = f"{npc_name}_{portrait_type}"
        return cache_key in self.portrait_cache

    def get_portrait_url(self, npc_name: str, portrait_type: str = "headshot") -> Optional[str]:
        """Get portrait URL for an NPC if it exists."""
        cache_key = f"{npc_name}_{portrait_type}"
        return self.portrait_cache.get(cache_key)

    async def generate_portrait(self, npc_name: str, npc_data: Dict, portrait_type: str = "headshot") -> Optional[str]:
        """
        Generate a portrait for an NPC.

        Args:
            npc_name: Name of the NPC
            npc_data: NPC data dictionary with appearance info
            portrait_type: Type of portrait - "headshot" (768x768) or "full_body" (512x896)

        Returns:
            URL to the generated portrait image, or None if generation failed
        """
        if not self.comfyui_client:
            print(f"[PortraitGen] ComfyUI client not available")
            return None

        # Check cache first
        if self.has_portrait(npc_name, portrait_type):
            print(f"[PortraitGen] Using cached {portrait_type} portrait for {npc_name}")
            return self.get_portrait_url(npc_name, portrait_type)

        print(f"[PortraitGen] Generating new {portrait_type} portrait for {npc_name}")

        # Build portrait prompt from NPC data
        positive_prompt, negative_prompt = self._build_portrait_prompt(npc_name, npc_data, portrait_type)

        # Set dimensions based on portrait type
        if portrait_type == "full_body":
            width, height = 832, 1216  # Taller aspect ratio for full body
        else:  # headshot
            width, height = 1024, 1024  # Square for circular headshot

        try:
            # Create filename: NPC_Name_headshot or NPC_Name_full_body
            safe_name = npc_name.replace(" ", "_").replace("'", "")
            custom_filename = f"{safe_name}_{portrait_type}"

            # Generate portrait image
            image_url = await self.comfyui_client.generate_image(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=25,  # More steps for better quality portraits
                cfg_scale=7.5,
                custom_filename=custom_filename
            )

            if image_url:
                # Update cache with type-specific key
                cache_key = f"{npc_name}_{portrait_type}"
                self.portrait_cache[cache_key] = image_url
                self._save_cache()
                print(f"[PortraitGen] ✓ {portrait_type} portrait generated for {npc_name}: {image_url}")
                return image_url
            else:
                print(f"[PortraitGen] Failed to generate {portrait_type} portrait for {npc_name}")
                return None

        except Exception as e:
            print(f"[PortraitGen] Error generating {portrait_type} portrait for {npc_name}: {e}")
            return None

    def _build_portrait_prompt(self, npc_name: str, npc_data: Dict, portrait_type: str = "headshot") -> Tuple[str, str]:
        """
        Build ComfyUI prompt for NPC portrait.

        Args:
            npc_name: Name of the NPC
            npc_data: NPC data with appearance information

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        # Extract appearance data
        gender = npc_data.get('gender', 'person')
        age = npc_data.get('age', 25)
        traits = npc_data.get('traits', [])
        quirk = npc_data.get('quirk', '')
        appearance = npc_data.get('appearance', '')

        # Convert Gender enum to string if needed
        if hasattr(gender, 'value'):
            gender = gender.value
        elif hasattr(gender, 'name'):
            gender = gender.name

        gender = str(gender).lower()

        # Build character description with explicit age and gender
        # Determine gender-specific terms
        if gender == 'male':
            if age < 13:
                gender_term = "boy"
            elif age < 18:
                gender_term = "teenage boy"
            else:
                gender_term = "man"
        elif gender == 'female':
            if age < 13:
                gender_term = "girl"
            elif age < 18:
                gender_term = "teenage girl"
            else:
                gender_term = "woman"
        else:
            # Fallback for non-binary or unknown gender - default to adult terms
            if age < 18:
                gender_term = "young person"
            else:
                gender_term = "person"

        # Build age descriptor with actual age
        if age < 18:
            age_desc = f"{age} year old {gender_term}"
        elif age < 30:
            age_desc = f"{age} year old young {gender_term}"
        elif age < 50:
            age_desc = f"{age} year old {gender_term}"
        else:
            age_desc = f"{age} year old mature {gender_term}"

        # Use full appearance description directly
        appearance_features = appearance if appearance else ""

        # Extract personality hints for visual style
        mood = "neutral, calm expression"
        if quirk:
            quirk_lower = quirk.lower()
            if "flirt" in quirk_lower or "seductive" in quirk_lower:
                mood = "confident, alluring gaze"
            elif "dominant" in quirk_lower or "assertive" in quirk_lower:
                mood = "strong, determined expression"
            elif "shy" in quirk_lower or "nervous" in quirk_lower:
                mood = "gentle, soft expression"
            elif "playful" in quirk_lower or "mischievous" in quirk_lower:
                mood = "playful, slight smile"

        # Build positive prompt
        positive_parts = [
            "masterpiece, best quality, highly detailed, 4k",
            "professional portrait photograph",
            age_desc,
        ]

        # Add appearance features if available
        if appearance_features:
            positive_parts.append(appearance_features)

        # Adjust composition based on portrait type
        if portrait_type == "full_body":
            positive_parts.extend([
                "full body portrait, standing pose",
                mood,
                "showing complete outfit and clothing details",
                "full body visible from head to feet",
                "soft studio lighting, neutral background",
                "photorealistic, natural skin texture",
                "professional photography, well proportioned",
                "cinematic lighting"
            ])

            # Negative prompt for full body (no "full body" in exclusions)
            negative_prompt = (
                "low quality, blurry, distorted, ugly, deformed, cartoon, anime, bad anatomy, "
                "multiple heads, bad hands, bad feet, text, watermark, logo, cropped, "
                "close-up only, headshot, extreme close-up, wide angle, fish eye, sitting, kneeling"
            )
        else:  # headshot
            positive_parts.extend([
                "head and shoulders portrait",
                mood,
                "soft studio lighting, neutral background",
                "photorealistic, natural skin texture",
                "sharp focus on eyes",
                "cinematic lighting, professional photography"
            ])

            # Negative prompt for headshot
            negative_prompt = (
                "low quality, blurry, distorted, ugly, deformed, cartoon, anime, bad anatomy, "
                "multiple heads, bad hands, text, watermark, logo, full body, cropped face, "
                "sunglasses, extreme close-up, wide angle, fish eye"
            )

        positive_prompt = ", ".join(positive_parts)

        print(f"[PortraitGen] {portrait_type} prompt for {npc_name}:")
        print(f"[PortraitGen]   Positive: {positive_prompt}")
        print(f"[PortraitGen]   Negative: {negative_prompt}")

        return positive_prompt, negative_prompt

    def detect_npcs_in_text(self, text: str, npc_dict: Dict) -> list:
        """
        Detect which NPCs are mentioned in the narrative text.

        Args:
            text: Narrative text to search
            npc_dict: Dictionary of NPC names to NPC objects

        Returns:
            List of NPC names mentioned in the text
        """
        mentioned_npcs = []

        for npc_name in npc_dict.keys():
            # Check full name
            if npc_name in text:
                mentioned_npcs.append(npc_name)
                continue

            # Check first name only
            first_name = npc_name.split()[0]
            if first_name in text and first_name not in mentioned_npcs:
                mentioned_npcs.append(npc_name)

        return mentioned_npcs

    def _extract_visual_features(self, appearance: str) -> str:
        """
        Extract visual features from appearance description for image prompts.

        Args:
            appearance: Text description of character appearance

        Returns:
            Comma-separated string of visual features suitable for image generation
        """
        if not appearance:
            return ""

        appearance_lower = appearance.lower()
        features = []

        # Extract hair features
        hair_keywords = ['blonde', 'black hair', 'brown hair', 'red hair', 'dark hair',
                        'curly', 'straight', 'long hair', 'short hair', 'ponytail',
                        'pigtails', 'braid', 'messy hair', 'beard', 'buzzcut']
        for keyword in hair_keywords:
            if keyword in appearance_lower:
                features.append(keyword)

        # Extract eye features
        eye_keywords = ['blue eyes', 'green eyes', 'brown eyes', 'hazel eyes',
                       'tired eyes', 'sharp eyes', 'kind eyes', 'intense eyes',
                       'rugged eyes', 'gentle eyes', 'expressive eyes']
        for keyword in eye_keywords:
            if keyword in appearance_lower:
                features.append(keyword)

        # Extract body features
        body_keywords = ['athletic build', 'muscular', 'tall', 'petite', 'slim',
                        'lean', 'strong arms', 'strong hands', 'broad-shouldered']
        for keyword in body_keywords:
            if keyword in appearance_lower:
                features.append(keyword)

        # Extract facial features
        face_keywords = ['glasses', 'freckles', 'charming smile', 'warm smile',
                        'stern expression', 'tired face', 'kind smile', 'rugged']
        for keyword in face_keywords:
            if keyword in appearance_lower:
                features.append(keyword)

        # Extract style/clothing hints (useful for portrait framing)
        style_keywords = ['professional attire', 'casual', 'neat', 'flannel',
                         'tattoos', 'tattooed']
        for keyword in style_keywords:
            if keyword in appearance_lower:
                features.append(keyword)

        return ", ".join(features) if features else ""
