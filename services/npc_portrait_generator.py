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
        Build ComfyUI prompt for NPC portrait using natural language tags.

        Args:
            npc_name: Name of the NPC
            npc_data: NPC data with appearance information
            portrait_type: "headshot" or "full_body"

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        # Extract appearance data
        gender = npc_data.get('gender', 'person')
        age = npc_data.get('age', 25)
        traits = npc_data.get('traits', [])
        quirk = npc_data.get('quirk', '')
        appearance = npc_data.get('appearance', '')
        occupation = npc_data.get('occupation', '')

        # Convert Gender enum to string if needed
        if hasattr(gender, 'value'):
            gender = gender.value
        elif hasattr(gender, 'name'):
            gender = gender.name

        gender = str(gender).lower()

        # Build tag list
        tags = []

        # Core tags
        tags.append("photograph")
        tags.append("professional")
        tags.append("high resolution")
        tags.append("detailed")

        # Gender and age tags
        if gender == 'male':
            if age < 13:
                tags.extend(["boy", "child"])
            elif age < 18:
                tags.extend(["teenage boy", "teenager", "young"])
            elif age < 30:
                tags.extend(["man", "young adult"])
            elif age < 50:
                tags.extend(["man", "adult"])
            else:
                tags.extend(["man", "mature", "older"])
        elif gender == 'female':
            if age < 13:
                tags.extend(["girl", "child"])
            elif age < 18:
                tags.extend(["teenage girl", "teenager", "young"])
            elif age < 30:
                tags.extend(["woman", "young adult"])
            elif age < 50:
                tags.extend(["woman", "adult"])
            else:
                tags.extend(["woman", "mature", "older"])
        else:
            if age < 18:
                tags.extend(["young person", "teenager"])
            else:
                tags.extend(["person", "adult"])

        # Parse appearance for specific features
        if appearance:
            appearance_lower = appearance.lower()

            # Hair color
            hair_colors = ["blonde", "brown", "black", "red", "auburn", "gray", "grey", "white", "silver"]
            for color in hair_colors:
                if color in appearance_lower:
                    tags.append(f"{color} hair")
                    break

            # Hair style
            if "ponytail" in appearance_lower:
                tags.append("ponytail")
            elif "braided" in appearance_lower or "braid" in appearance_lower:
                tags.append("braided hair")
            elif "short hair" in appearance_lower:
                tags.append("short hair")
            elif "long hair" in appearance_lower:
                tags.append("long hair")
            elif "medium" in appearance_lower and "hair" in appearance_lower:
                tags.append("medium-length hair")

            # Eye color
            eye_colors = ["blue", "green", "brown", "hazel", "gray", "grey"]
            for color in eye_colors:
                if f"{color} eyes" in appearance_lower:
                    tags.append(f"{color} eyes")
                    break

            # Build/physique
            if "muscular" in appearance_lower or "athletic" in appearance_lower:
                tags.extend(["athletic", "fit physique", "toned"])
            elif "slim" in appearance_lower or "slender" in appearance_lower:
                tags.extend(["slender", "slim build"])
            elif "curvy" in appearance_lower:
                tags.extend(["curvy", "feminine physique"])

            # Skin tone
            if "pale" in appearance_lower or "fair" in appearance_lower:
                tags.append("light skin")
            elif "tan" in appearance_lower or "olive" in appearance_lower:
                tags.append("medium skin tone")
            elif "dark" in appearance_lower and "skin" in appearance_lower:
                tags.append("dark skin")

            # Features
            if "attractive" in appearance_lower or "beautiful" in appearance_lower or "handsome" in appearance_lower:
                tags.append("attractive")
            if "tattoo" in appearance_lower:
                tags.append("tattoos")
            if "piercing" in appearance_lower:
                tags.append("piercings")

        # Clothing style based on occupation, traits, and personality
        clothing_tags = []
        clothing_added = False

        # OCCUPATION-BASED CLOTHING (highest priority)
        if occupation:
            occ_lower = occupation.lower()

            # Medical professions
            if any(word in occ_lower for word in ['nurse', 'doctor', 'paramedic', 'medical']):
                if gender == 'female':
                    clothing_tags.extend(["nurse uniform", "medical scrubs", "white coat", "professional medical attire"])
                else:
                    clothing_tags.extend(["medical scrubs", "white coat", "professional medical attire"])
                clothing_added = True

            # Education
            elif any(word in occ_lower for word in ['teacher', 'professor', 'instructor', 'educator']):
                if gender == 'female':
                    clothing_tags.extend(["blouse", "cardigan", "professional skirt", "business casual", "glasses"])
                else:
                    clothing_tags.extend(["button-up shirt", "slacks", "tie", "business casual", "glasses"])
                clothing_added = True

            # Law enforcement / emergency
            elif any(word in occ_lower for word in ['officer', 'police', 'sheriff', 'deputy', 'firefighter']):
                clothing_tags.extend(["uniform", "badge", "professional", "authoritative"])
                clothing_added = True

            # Religious
            elif any(word in occ_lower for word in ['pastor', 'minister', 'priest', 'clergy']):
                if gender == 'female':
                    clothing_tags.extend(["modest dress", "professional attire", "conservative clothing"])
                else:
                    clothing_tags.extend(["clergy collar", "dress shirt", "black pants", "professional"])
                clothing_added = True

            # Mechanics / manual labor
            elif any(word in occ_lower for word in ['mechanic', 'technician', 'engineer', 'worker', 'construction']):
                if gender == 'female':
                    clothing_tags.extend(["work clothes", "denim", "coveralls", "practical clothing", "work boots"])
                else:
                    clothing_tags.extend(["work shirt", "denim", "coveralls", "practical clothing", "work boots"])
                clothing_added = True

            # Food service
            elif any(word in occ_lower for word in ['chef', 'cook', 'bartender', 'waitress', 'waiter', 'server']):
                if 'chef' in occ_lower or 'cook' in occ_lower:
                    clothing_tags.extend(["chef coat", "apron", "professional kitchen attire"])
                else:
                    clothing_tags.extend(["server uniform", "apron", "casual professional"])
                clothing_added = True

            # Retail / customer service
            elif any(word in occ_lower for word in ['cashier', 'sales', 'clerk', 'retail', 'receptionist']):
                if gender == 'female':
                    clothing_tags.extend(["polo shirt", "name tag", "casual professional", "khakis"])
                else:
                    clothing_tags.extend(["polo shirt", "name tag", "casual professional", "khakis"])
                clothing_added = True

            # Business / office
            elif any(word in occ_lower for word in ['manager', 'executive', 'accountant', 'administrator', 'secretary']):
                if gender == 'female':
                    clothing_tags.extend(["business suit", "blazer", "pencil skirt", "blouse", "professional attire", "heels"])
                else:
                    clothing_tags.extend(["business suit", "tie", "dress shirt", "slacks", "professional attire"])
                clothing_added = True

            # Creative professions
            elif any(word in occ_lower for word in ['artist', 'designer', 'photographer', 'writer']):
                clothing_tags.extend(["creative style", "casual artistic", "unique fashion", "bohemian"])
                clothing_added = True

            # Fitness / athletics
            elif any(word in occ_lower for word in ['trainer', 'coach', 'athlete', 'fitness', 'gym']):
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "yoga pants", "fitness clothing", "tight clothing"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top", "gym shorts", "fitness clothing"])
                clothing_added = True

            # Agriculture / outdoors
            elif any(word in occ_lower for word in ['farmer', 'rancher', 'gardener', 'landscaper']):
                clothing_tags.extend(["work clothes", "flannel", "jeans", "boots", "practical outdoor wear"])
                clothing_added = True

        # TRAIT-BASED MODIFICATIONS (secondary priority)
        if traits:
            traits_str = ' '.join(traits).lower()

            # Athletic/active traits
            if any(word in traits_str for word in ['athletic', 'active', 'energetic', 'fitness']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "yoga pants", "fitness clothing"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top", "gym shorts"])
                clothing_added = True

            # Professional/serious traits
            elif any(word in traits_str for word in ['professional', 'serious', 'organized', 'responsible']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["business casual", "blouse", "professional attire"])
                else:
                    clothing_tags.extend(["business casual", "button-up shirt", "slacks"])
                clothing_added = True

            # Creative/artistic traits
            elif any(word in traits_str for word in ['creative', 'artistic', 'expressive']) and not clothing_added:
                clothing_tags.extend(["creative style", "unique fashion", "artistic clothing", "colorful"])
                clothing_added = True

            # Shy/modest traits - adjust existing clothing
            if any(word in traits_str for word in ['shy', 'modest', 'reserved', 'conservative']):
                clothing_tags.extend(["modest", "conservative cut"])

            # Confident/bold traits - adjust existing clothing
            if any(word in traits_str for word in ['confident', 'bold', 'outgoing', 'flirty']):
                clothing_tags.extend(["fitted", "fashionable", "stylish"])

        # QUIRK-BASED ADDITIONS (tertiary priority)
        if quirk and not clothing_added:
            quirk_lower = quirk.lower()
            if "athletic" in quirk_lower or "fitness" in quirk_lower:
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "tight clothing"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top"])
                clothing_added = True
            elif "professional" in quirk_lower or "business" in quirk_lower:
                clothing_tags.extend(["business casual", "professional attire"])
                clothing_added = True

        # DEFAULT CLOTHING (if nothing matched)
        if not clothing_added:
            if age < 18:
                clothing_tags.extend(["casual wear", "t-shirt", "jeans"])
            elif age < 30:
                if gender == 'female':
                    clothing_tags.extend(["casual modern", "jeans", "top"])
                else:
                    clothing_tags.extend(["casual wear", "t-shirt", "jeans"])
            else:
                clothing_tags.extend(["casual clothing", "comfortable"])

        # Add all clothing tags
        tags.extend(clothing_tags)

        # Expression/mood based on quirk
        if quirk:
            quirk_lower = quirk.lower()
            if "flirt" in quirk_lower or "seductive" in quirk_lower:
                tags.extend(["confident", "smiling", "alluring gaze", "makeup", "lips"])
            elif "shy" in quirk_lower or "nervous" in quirk_lower:
                tags.extend(["gentle expression", "soft smile", "natural makeup"])
            elif "dominant" in quirk_lower or "assertive" in quirk_lower:
                tags.extend(["confident", "strong expression", "serious"])
            elif "playful" in quirk_lower or "mischievous" in quirk_lower:
                tags.extend(["smiling", "playful expression", "friendly"])
            else:
                tags.extend(["natural expression", "slight smile"])
        else:
            tags.extend(["natural expression", "slight smile"])

        # Portrait type specific tags
        if portrait_type == "full_body":
            tags.extend([
                "full body",
                "standing",
                "complete figure",
                "head to toe",
                "full outfit visible",
                "studio shot",
                "white background",
                "natural light",
                "indoors",
                "minimalistic background",
                "soft focus background",
                "sharp focus on subject",
                "well proportioned",
                "symmetrical",
                "fashion"
            ])
        else:  # headshot
            tags.extend([
                "close-up",
                "head and shoulders",
                "portrait",
                "face focus",
                "studio shot",
                "white background",
                "natural light",
                "soft lighting",
                "sharp focus on eyes",
                "symmetrical face",
                "beauty",
                "professional headshot"
            ])

        # Quality tags
        tags.extend([
            "photorealistic",
            "natural skin texture",
            "high quality",
            "masterpiece",
            "detailed face",
            "sharp details"
        ])

        # Build positive prompt from tags
        positive_prompt = ", ".join(tags)

        # Build negative prompt
        negative_tags = [
            "low quality",
            "blurry",
            "distorted",
            "ugly",
            "deformed",
            "disfigured",
            "cartoon",
            "anime",
            "3d render",
            "bad anatomy",
            "bad proportions",
            "multiple heads",
            "extra limbs",
            "bad hands",
            "bad feet",
            "missing fingers",
            "extra fingers",
            "fused fingers",
            "text",
            "watermark",
            "logo",
            "signature",
            "username",
            "artist name",
            "cropped",
            "out of frame",
            "worst quality",
            "jpeg artifacts",
            "duplicate",
            "mutation"
        ]

        # Type-specific negative tags
        if portrait_type == "full_body":
            negative_tags.extend([
                "headshot only",
                "close-up only",
                "cropped body",
                "sitting",
                "kneeling",
                "lying down"
            ])
        else:  # headshot
            negative_tags.extend([
                "full body",
                "cropped face",
                "sunglasses",
                "hat",
                "hood"
            ])

        negative_prompt = ", ".join(negative_tags)

        print(f"[PortraitGen] {portrait_type} prompt for {npc_name}:")
        print(f"[PortraitGen]   Positive: {positive_prompt[:150]}..." if len(positive_prompt) > 150 else f"[PortraitGen]   Positive: {positive_prompt}")
        print(f"[PortraitGen]   Negative: {negative_prompt[:150]}..." if len(negative_prompt) > 150 else f"[PortraitGen]   Negative: {negative_prompt}")

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
