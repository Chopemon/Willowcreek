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

    def has_portrait(self, npc_name: str) -> bool:
        """Check if NPC already has a portrait."""
        return npc_name in self.portrait_cache

    def get_portrait_url(self, npc_name: str) -> Optional[str]:
        """Get portrait URL for an NPC if it exists."""
        return self.portrait_cache.get(npc_name)

    async def generate_portrait(self, npc_name: str, npc_data: Dict) -> Optional[str]:
        """
        Generate a portrait for an NPC.

        Args:
            npc_name: Name of the NPC
            npc_data: NPC data dictionary with appearance info

        Returns:
            URL to the generated portrait image, or None if generation failed
        """
        if not self.comfyui_client:
            print(f"[PortraitGen] ComfyUI client not available")
            return None

        # Check cache first
        if self.has_portrait(npc_name):
            print(f"[PortraitGen] Using cached portrait for {npc_name}")
            return self.get_portrait_url(npc_name)

        print(f"[PortraitGen] Generating new portrait for {npc_name}")

        # Build portrait prompt from NPC data
        positive_prompt, negative_prompt = self._build_portrait_prompt(npc_name, npc_data)

        try:
            # Generate portrait image (square format for portraits)
            image_url = await self.comfyui_client.generate_image(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=768,
                height=768,
                steps=25,  # More steps for better quality portraits
                cfg_scale=7.5
            )

            if image_url:
                # Update cache
                self.portrait_cache[npc_name] = image_url
                self._save_cache()
                print(f"[PortraitGen] ✓ Portrait generated for {npc_name}: {image_url}")
                return image_url
            else:
                print(f"[PortraitGen] Failed to generate portrait for {npc_name}")
                return None

        except Exception as e:
            print(f"[PortraitGen] Error generating portrait for {npc_name}: {e}")
            return None

    def _build_portrait_prompt(self, npc_name: str, npc_data: Dict) -> Tuple[str, str]:
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

        # Determine age description
        if age < 18:
            age_desc = "teenage"
        elif age < 30:
            age_desc = "young adult"
        elif age < 50:
            age_desc = "adult"
        else:
            age_desc = "mature adult"

        # Build character description
        gender_desc = "man" if gender.lower() == 'male' else "woman" if gender.lower() == 'female' else "person"

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
            f"{age_desc} {gender_desc}",
            "head and shoulders portrait",
            mood,
            "soft studio lighting, neutral background",
            "photorealistic, natural skin texture",
            "sharp focus on eyes",
            "cinematic lighting, professional photography"
        ]

        positive_prompt = ", ".join(positive_parts)

        # Build negative prompt
        negative_prompt = (
            "low quality, blurry, distorted, ugly, deformed, cartoon, anime, bad anatomy, "
            "multiple heads, bad hands, text, watermark, logo, full body, cropped face, "
            "sunglasses, extreme close-up, wide angle, fish eye"
        )

        print(f"[PortraitGen] Prompt for {npc_name}:")
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
