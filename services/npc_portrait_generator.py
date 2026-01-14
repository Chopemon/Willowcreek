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
import requests


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

        self.prompt_llm_enabled = os.getenv("PORTRAIT_PROMPT_LLM_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
        self.prompt_model_name = os.getenv(
            "PORTRAIT_PROMPT_MODEL",
            "llama3.3-8b-instruct-thinking-heretic-uncensored-claude-4.5-opus-high-reasoning-i1",
        )
        self.prompt_api_url = os.getenv(
            "LM_STUDIO_API_URL",
            os.getenv("LOCAL_API_URL", "http://localhost:1234/v1/chat/completions"),
        )
        self.prompt_timeout_seconds = self._resolve_prompt_timeout()

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

    @staticmethod
    def _resolve_prompt_timeout() -> int:
        raw_value = os.getenv("PORTRAIT_PROMPT_TIMEOUT_SECONDS", "120")
        try:
            return max(int(raw_value), 1)
        except ValueError:
            return 120

    def has_portrait(self, npc_name: str, portrait_type: str = "headshot") -> bool:
        """Check if NPC already has a portrait of specified type."""
        cache_key = f"{npc_name}_{portrait_type}"
        return cache_key in self.portrait_cache

    def get_portrait_url(self, npc_name: str, portrait_type: str = "headshot") -> Optional[str]:
        """Get portrait URL for an NPC if it exists."""
        cache_key = f"{npc_name}_{portrait_type}"
        return self.portrait_cache.get(cache_key)

    def _infer_gender_from_name(self, npc_name: str) -> str:
        """
        Infer gender from NPC name using common name patterns.
        Returns 'male' or 'female', defaults to 'female' if uncertain.
        """
        # Common female first names
        female_names = [
            'sarah', 'scarlet', 'tessa', 'agnes', 'anna', 'caty', 'isabella', 'eve', 'emma',
            'elena', 'hanna', 'christine', 'eva', 'lianna', 'lily', 'lisa', 'ivy', 'maria',
            'rose', 'angela', 'zoey', 'marta', 'rebecca', 'rachel', 'samantha', 'jessica',
            'jennifer', 'linda', 'barbara', 'susan', 'nancy', 'karen', 'betty', 'helen',
            'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle', 'laura', 'melissa',
            'kimberly', 'elizabeth', 'amy', 'stephanie', 'nicole', 'heather', 'ashley',
            'marjorie', 'aaliyah', 'chloe', 'rita', 'gladys', 'yelena', 'mina', 'clara',
            'nina', 'patricia', 'dorothy', 'deborah', 'virginia', 'catherine', 'joyce',
            'diane', 'alice', 'julie', 'frances', 'gloria', 'ann', 'jane', 'marie'
        ]

        # Common male first names
        male_names = [
            'steve', 'tim', 'tom', 'alex', 'daniel', 'damien', 'kenny', 'david', 'ken',
            'john', 'james', 'nate', 'luke', 'lucas', 'hiro', 'michael', 'robert', 'william',
            'richard', 'joseph', 'thomas', 'charles', 'christopher', 'matthew', 'anthony',
            'mark', 'donald', 'steven', 'paul', 'andrew', 'joshua', 'kenneth', 'kevin',
            'brian', 'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan',
            'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin',
            'earl', 'hassan', 'derek', 'omar', 'caleb', 'toby', 'ralph', 'logan', 'tyler',
            'eddie', 'marshall', 'grant', 'marcus', 'vincent', 'raymond', 'peter', 'harold',
            'douglas', 'henry', 'carl', 'arthur', 'gerald', 'roger', 'keith', 'jeremy',
            'lawrence', 'sean', 'christian', 'austin', 'benjamin', 'samuel', 'frank', 'scott'
        ]

        # Extract first name (before space)
        first_name = npc_name.split()[0].lower()

        # Check against known names
        if first_name in female_names:
            return 'female'
        elif first_name in male_names:
            return 'male'

        # Check name endings (common patterns)
        if first_name.endswith(('a', 'ie', 'y', 'lyn', 'lynn', 'elle', 'ette', 'ine', 'een')):
            return 'female'

        # Default to female if uncertain (safer for most cases)
        return 'female'

    async def generate_portrait_prompts(
        self,
        npc_name: str,
        npc_data: Dict,
        portrait_type: str = "headshot",
    ) -> Tuple[str, str]:
        if not self.prompt_llm_enabled:
            return self._build_portrait_prompt(npc_name, npc_data, portrait_type)

        prompt_from_llm = self._generate_portrait_prompt_with_llm(npc_name, npc_data, portrait_type)
        if prompt_from_llm:
            return prompt_from_llm

        return self._build_portrait_prompt(npc_name, npc_data, portrait_type)

    async def generate_portrait(
        self,
        npc_name: str,
        npc_data: Dict,
        portrait_type: str = "headshot",
        prompts: Optional[Tuple[str, str]] = None,
    ) -> Optional[str]:
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

        # Check cache first (skip when explicit prompts are provided)
        if prompts is None and self.has_portrait(npc_name, portrait_type):
            print(f"[PortraitGen] Using cached {portrait_type} portrait for {npc_name}")
            return self.get_portrait_url(npc_name, portrait_type)

        print(f"[PortraitGen] Generating new {portrait_type} portrait for {npc_name}")

        # Build portrait prompt from NPC data
        if prompts is None:
            positive_prompt, negative_prompt = await self.generate_portrait_prompts(npc_name, npc_data, portrait_type)
        else:
            positive_prompt, negative_prompt = prompts
            print(f"[PortraitGen] Using provided prompts for {npc_name} ({portrait_type})")

        # Set dimensions based on portrait type
        if portrait_type == "full_body":
            width, height = 832, 1216  # Taller aspect ratio for full body
        elif portrait_type == "cowboy_shot":
            width, height = 896, 1152  # Medium ratio for waist-up
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

    def _generate_portrait_prompt_with_llm(
        self,
        npc_name: str,
        npc_data: Dict,
        portrait_type: str,
    ) -> Optional[Tuple[str, str]]:
        system_prompt = (
            "You are an expert prompt engineer for photorealistic character portraits in ComfyUI/Stable Diffusion. "
            "Use the provided profile to craft a concise, vivid prompt. "
            "The positive prompt must start with a phrase like \"portrait of <Name>, a woman/man...\". "
            "Include the NPC name for consistency. Avoid unsafe or explicit content."
        )

        gender = npc_data.get("gender", "person")
        if hasattr(gender, "value"):
            gender = gender.value
        elif hasattr(gender, "name"):
            gender = gender.name

        user_prompt = (
            "Create a portrait prompt using this NPC profile:\n"
            f"Name: {npc_name}\n"
            f"Gender: {gender}\n"
            f"Age: {npc_data.get('age', 25)}\n"
            f"Appearance: {npc_data.get('appearance', '')}\n"
            f"Occupation: {npc_data.get('occupation', '')}\n"
            f"Traits: {', '.join(npc_data.get('traits', []))}\n"
            f"Quirk: {npc_data.get('quirk', '')}\n"
            f"Portrait type: {portrait_type}\n\n"
            "Output format:\n"
            "POSITIVE: ...\n"
            "NEGATIVE: ..."
        )

        payload = {
            "model": self.prompt_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.6,
            "max_tokens": 512,
        }

        try:
            print(f"[PortraitGen] Generating prompt via LLM for {npc_name} ({portrait_type})")
            response = requests.post(
                self.prompt_api_url,
                json=payload,
                timeout=self.prompt_timeout_seconds,
            )
            if response.status_code != 200:
                print(f"[PortraitGen] Prompt LLM error: {response.status_code} - {response.text}")
                return None

            content = response.json()["choices"][0]["message"]["content"]
            parsed = self._parse_prompt_response(content)
            if parsed:
                return parsed

            print("[PortraitGen] Prompt LLM response could not be parsed, falling back.")
            return None
        except Exception as exc:
            print(f"[PortraitGen] Prompt LLM request failed: {exc}")
            return None

    def _parse_prompt_response(self, content: str) -> Optional[Tuple[str, str]]:
        positive_prompt = None
        negative_prompt = None

        for line in content.splitlines():
            if line.strip().lower().startswith("positive:"):
                positive_prompt = line.split(":", 1)[1].strip()
            elif line.strip().lower().startswith("negative:"):
                negative_prompt = line.split(":", 1)[1].strip()

        if positive_prompt and negative_prompt:
            return positive_prompt, negative_prompt

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

        # Infer gender from name if missing or ambiguous
        if gender not in ['male', 'female']:
            gender = self._infer_gender_from_name(npc_name)
            print(f"[PortraitGen] Inferred gender '{gender}' from name '{npc_name}'")

        # Build tag list
        tags = []
        tags.append(f"portrait of {npc_name}")

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

        # Include raw appearance description for direct prompting
        if appearance:
            tags.append(appearance)

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

            # Build/physique - DETAILED body features extraction
            if "muscular" in appearance_lower or "athletic" in appearance_lower:
                tags.extend(["athletic", "fit physique", "toned"])
            elif "slim" in appearance_lower or "slender" in appearance_lower:
                tags.extend(["slender", "slim build"])
            elif "curvy" in appearance_lower:
                tags.extend(["curvy", "feminine physique"])

            # Specific body features for female characters
            if gender == 'female':
                # Breast size - extract from appearance
                if any(word in appearance_lower for word in ['large breasts', 'd-cup', 'dd-cup', 'e-cup', 'big breasts', 'huge breasts']):
                    tags.extend(["large breasts", "busty", "cleavage"])
                elif any(word in appearance_lower for word in ['medium breasts', 'c-cup', 'b-cup', 'average breasts']):
                    tags.append("medium breasts")
                elif any(word in appearance_lower for word in ['small breasts', 'a-cup', 'petite breasts']):
                    tags.append("small breasts")

                # Posterior/hips
                if any(word in appearance_lower for word in ['round posterior', 'large posterior', 'big butt', 'round butt', 'thicc', 'wide hips']):
                    tags.extend(["round posterior", "wide hips", "curvy hips"])

                # Overall figure descriptors
                if "hourglass" in appearance_lower:
                    tags.extend(["hourglass figure", "feminine curves"])
                if "voluptuous" in appearance_lower:
                    tags.extend(["voluptuous", "curvaceous"])
                if "petite" in appearance_lower:
                    tags.extend(["petite", "small frame"])
                if any(word in appearance_lower for word in ['alluring', 'sexy figure', 'attractive figure']):
                    tags.extend(["attractive figure", "appealing physique"])

            # Male body features
            if gender == 'male':
                if any(word in appearance_lower for word in ['broad shoulders', 'wide shoulders']):
                    tags.append("broad shoulders")
                if "muscular" in appearance_lower:
                    tags.extend(["muscular build", "defined muscles"])
                if any(word in appearance_lower for word in ['lean', 'athletic build']):
                    tags.extend(["lean build", "athletic physique"])

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

            # Fitness / athletics / yoga (CHECK FIRST before education catches "instructor")
            if any(word in occ_lower for word in ['yoga', 'trainer', 'coach', 'athlete', 'fitness', 'gym']):
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "yoga pants", "fitness clothing", "tight clothing"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top", "gym shorts", "fitness clothing"])
                clothing_added = True

            # Medical professions
            elif any(word in occ_lower for word in ['nurse', 'doctor', 'paramedic', 'medical']):
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

            # Agriculture / outdoors
            elif any(word in occ_lower for word in ['farmer', 'rancher', 'gardener', 'landscaper']):
                clothing_tags.extend(["work clothes", "flannel", "jeans", "boots", "practical outdoor wear"])
                clothing_added = True

        # TRAIT-BASED MODIFICATIONS (secondary priority) - Much more detailed for personality variance
        if traits:
            traits_str = ' '.join(traits).lower()

            # Athletic/sports enthusiast
            if any(word in traits_str for word in ['athletic', 'active', 'energetic', 'fitness', 'sporty']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "yoga pants", "fitness clothing", "sneakers"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top", "basketball shorts", "sweatpants", "sneakers"])
                clothing_added = True

            # Rebellious/punk/edgy
            elif any(word in traits_str for word in ['rebellious', 'defiant', 'edgy', 'punk', 'alternative']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["ripped jeans", "band t-shirt", "leather jacket", "combat boots", "dark clothing", "grunge style"])
                else:
                    clothing_tags.extend(["ripped jeans", "band t-shirt", "leather jacket", "combat boots", "dark clothing", "punk style"])
                clothing_added = True

            # Nerdy/intellectual/gamer
            elif any(word in traits_str for word in ['nerdy', 'intellectual', 'studious', 'bookish', 'geeky', 'gamer']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["graphic t-shirt", "hoodie", "jeans", "glasses", "sneakers", "casual nerdy"])
                else:
                    clothing_tags.extend(["graphic t-shirt", "cargo shorts", "hoodie", "glasses", "sneakers", "gamer style"])
                clothing_added = True

            # Popular/preppy/fashionable
            elif any(word in traits_str for word in ['popular', 'preppy', 'fashionable', 'trendy', 'stylish']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["trendy outfit", "designer jeans", "crop top", "fashionable", "jewelry", "makeup", "stylish"])
                else:
                    clothing_tags.extend(["polo shirt", "khakis", "boat shoes", "preppy style", "clean cut", "neat"])
                clothing_added = True

            # Shy/introverted/quiet
            elif any(word in traits_str for word in ['shy', 'introverted', 'quiet', 'timid', 'reserved']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["oversized sweater", "modest jeans", "comfortable clothing", "muted colors", "simple style"])
                else:
                    clothing_tags.extend(["hoodie", "jeans", "plain t-shirt", "muted colors", "comfortable", "unassuming"])
                clothing_added = True

            # Outgoing/party/social
            elif any(word in traits_str for word in ['outgoing', 'social', 'party', 'extroverted', 'friendly']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["bright colors", "fun outfit", "trendy", "eye-catching", "social butterfly style"])
                else:
                    clothing_tags.extend(["casual shirt", "jeans", "friendly style", "approachable", "colorful"])
                clothing_added = True

            # Creative/artistic/bohemian
            elif any(word in traits_str for word in ['creative', 'artistic', 'expressive', 'bohemian', 'unique']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["bohemian dress", "artistic style", "unique fashion", "layered clothing", "creative accessories"])
                else:
                    clothing_tags.extend(["vintage shirt", "artistic style", "unique fashion", "creative look", "unconventional"])
                clothing_added = True

            # Confident/bold/dominant
            elif any(word in traits_str for word in ['confident', 'bold', 'dominant', 'assertive', 'strong']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["fitted outfit", "bold colors", "confident style", "statement piece", "powerful look"])
                else:
                    clothing_tags.extend(["fitted shirt", "confidence", "bold style", "strong presence", "masculine"])
                clothing_added = True

            # Flirty/seductive/romantic
            elif any(word in traits_str for word in ['flirty', 'seductive', 'romantic', 'charming']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["low-cut top", "tight jeans", "feminine style", "alluring", "fashionable", "makeup"])
                else:
                    clothing_tags.extend(["fitted shirt", "stylish", "attractive", "well-groomed", "charming look"])
                clothing_added = True

            # Serious/professional/responsible
            elif any(word in traits_str for word in ['serious', 'professional', 'organized', 'responsible', 'mature']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["business casual", "blouse", "neat style", "professional look", "organized"])
                else:
                    clothing_tags.extend(["button-up shirt", "neat", "professional casual", "responsible look", "mature"])
                clothing_added = True

            # Lazy/casual/relaxed
            elif any(word in traits_str for word in ['lazy', 'relaxed', 'casual', 'laid-back', 'easygoing']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["sweatpants", "oversized t-shirt", "comfortable", "casual lazy style", "relaxed fit"])
                else:
                    clothing_tags.extend(["sweatpants", "hoodie", "comfortable", "lazy style", "relaxed", "casual wear"])
                clothing_added = True

            # Adventurous/outdoorsy
            elif any(word in traits_str for word in ['adventurous', 'outdoorsy', 'nature', 'explorer']) and not clothing_added:
                clothing_tags.extend(["outdoor clothing", "hiking boots", "practical wear", "cargo pants", "adventure style"])
                clothing_added = True

            # Religious/devout/conservative
            elif any(word in traits_str for word in ['religious', 'devout', 'faithful', 'pious']) and not clothing_added:
                if gender == 'female':
                    clothing_tags.extend(["modest dress", "conservative clothing", "long skirt", "covered", "traditional"])
                else:
                    clothing_tags.extend(["modest clothing", "conservative", "neat", "traditional style", "respectful"])
                clothing_added = True

            # ADDITIONAL TRAIT MODIFIERS (can combine with above)
            # These add to existing clothing rather than replacing

            # Modest/conservative traits - adjust existing clothing
            if any(word in traits_str for word in ['modest', 'conservative']) and clothing_added:
                clothing_tags.extend(["modest", "conservative cut", "appropriate"])

            # Confident/bold traits - adjust existing clothing
            if any(word in traits_str for word in ['confident', 'bold', 'daring']) and clothing_added:
                clothing_tags.extend(["fitted", "fashionable", "eye-catching"])

            # Messy/sloppy traits
            if any(word in traits_str for word in ['messy', 'sloppy', 'disheveled', 'unkempt']):
                clothing_tags.extend(["wrinkled", "disheveled", "casual messy"])

            # Clean/neat traits
            if any(word in traits_str for word in ['neat', 'clean', 'tidy', 'organized']):
                clothing_tags.extend(["neat", "well-maintained", "clean appearance"])

            # Wealthy/rich traits
            if any(word in traits_str for word in ['wealthy', 'rich', 'privileged', 'elite']):
                clothing_tags.extend(["expensive", "designer", "high-end fashion", "luxury"])

            # Poor/struggling traits
            if any(word in traits_str for word in ['poor', 'struggling', 'worn']):
                clothing_tags.extend(["worn clothing", "old clothes", "simple", "budget"])

            # Muscular/strong physique
            if any(word in traits_str for word in ['muscular', 'strong', 'buff', 'built']):
                if gender == 'male':
                    clothing_tags.extend(["fitted to show physique", "muscular build visible"])

            # Sexy/attractive emphasis
            if any(word in traits_str for word in ['sexy', 'attractive', 'beautiful', 'gorgeous', 'hot']):
                if gender == 'female':
                    clothing_tags.extend(["attractive", "flattering fit", "shows figure"])
                else:
                    clothing_tags.extend(["attractive", "well-fitted", "handsome"])

        # QUIRK-BASED ADDITIONS (tertiary priority) - Enhanced for more personality
        if quirk and not clothing_added:
            quirk_lower = quirk.lower()

            # Athletic/fitness quirks
            if any(word in quirk_lower for word in ['athletic', 'fitness', 'workout', 'gym', 'sports']):
                if gender == 'female':
                    clothing_tags.extend(["sports bra", "athletic wear", "tight clothing", "fitness style"])
                else:
                    clothing_tags.extend(["athletic wear", "tank top", "gym clothing", "sporty"])
                clothing_added = True

            # Flirty/seductive quirks
            elif any(word in quirk_lower for word in ['flirt', 'seduc', 'tease', 'provocative']):
                if gender == 'female':
                    clothing_tags.extend(["low-cut", "tight", "revealing", "alluring outfit", "sexy style"])
                else:
                    clothing_tags.extend(["fitted shirt", "unbuttoned", "attractive", "charming style"])
                clothing_added = True

            # Professional/business quirks
            elif any(word in quirk_lower for word in ['professional', 'business', 'formal', 'corporate']):
                if gender == 'female':
                    clothing_tags.extend(["business suit", "blazer", "professional attire", "formal"])
                else:
                    clothing_tags.extend(["business suit", "tie", "professional attire", "formal"])
                clothing_added = True

            # Bookish/nerdy quirks
            elif any(word in quirk_lower for word in ['book', 'nerd', 'geek', 'intellectual', 'smart']):
                clothing_tags.extend(["glasses", "cardigan", "casual intellectual", "bookish style"])
                clothing_added = True

            # Party/social quirks
            elif any(word in quirk_lower for word in ['party', 'social', 'outgoing', 'life of the party']):
                if gender == 'female':
                    clothing_tags.extend(["party outfit", "trendy", "eye-catching", "fun style", "vibrant"])
                else:
                    clothing_tags.extend(["stylish", "trendy", "social", "party casual"])
                clothing_added = True

            # Artistic/creative quirks
            elif any(word in quirk_lower for word in ['artist', 'creative', 'artsy', 'bohemian']):
                clothing_tags.extend(["artistic style", "bohemian", "creative outfit", "unique fashion", "expressive"])
                clothing_added = True

            # Rebellious/bad boy-girl quirks
            elif any(word in quirk_lower for word in ['rebel', 'bad boy', 'bad girl', 'troublemaker', 'delinquent']):
                if gender == 'female':
                    clothing_tags.extend(["leather jacket", "ripped jeans", "edgy", "rebellious style", "dark clothing"])
                else:
                    clothing_tags.extend(["leather jacket", "ripped jeans", "edgy", "bad boy style", "rebellious"])
                clothing_added = True

            # Shy/quiet quirks
            elif any(word in quirk_lower for word in ['shy', 'quiet', 'timid', 'withdrawn']):
                if gender == 'female':
                    clothing_tags.extend(["oversized sweater", "modest", "comfortable", "shy style", "muted colors"])
                else:
                    clothing_tags.extend(["hoodie", "plain", "unassuming", "quiet style", "simple"])
                clothing_added = True

            # Outdoorsy/nature quirks
            elif any(word in quirk_lower for word in ['outdoor', 'nature', 'hiker', 'camper']):
                clothing_tags.extend(["outdoor clothing", "hiking gear", "practical", "nature style", "rugged"])
                clothing_added = True

            # Goth/dark quirks
            elif any(word in quirk_lower for word in ['goth', 'dark', 'emo', 'gothic']):
                clothing_tags.extend(["all black", "dark clothing", "goth style", "black outfit", "alternative fashion"])
                clothing_added = True

        # DEFAULT CLOTHING (if nothing matched) - Add variety based on age and gender
        if not clothing_added:
            # Use hash of NPC name for consistent but varied style selection
            name_hash = sum(ord(c) for c in npc_name) % 8

            if age < 13:
                # Children
                if gender == 'female':
                    styles = [
                        ["dress", "colorful", "playful"],
                        ["t-shirt", "shorts", "casual"],
                        ["overalls", "cheerful", "kid style"],
                        ["hoodie", "jeans", "comfortable"]
                    ]
                    clothing_tags.extend(styles[name_hash % 4])
                else:
                    styles = [
                        ["t-shirt", "shorts", "casual kid"],
                        ["graphic tee", "jeans", "playful"],
                        ["hoodie", "sweatpants", "comfortable"],
                        ["button-up shirt", "neat kid style"]
                    ]
                    clothing_tags.extend(styles[name_hash % 4])

            elif age < 18:
                # Teens - Maximum variety
                if gender == 'female':
                    styles = [
                        ["graphic t-shirt", "ripped jeans", "sneakers", "casual teen"],
                        ["crop top", "high-waisted jeans", "trendy", "fashionable teen"],
                        ["hoodie", "leggings", "comfortable", "relaxed teen style"],
                        ["band t-shirt", "skinny jeans", "converse", "alternative teen"],
                        ["oversized sweater", "jeans", "cozy", "soft teen style"],
                        ["flannel shirt", "denim", "casual", "tomboy style"],
                        ["tank top", "shorts", "athletic", "sporty casual"],
                        ["blouse", "skirt", "neat", "preppy teen"]
                    ]
                    clothing_tags.extend(styles[name_hash])
                else:
                    styles = [
                        ["graphic t-shirt", "jeans", "sneakers", "casual teen"],
                        ["hoodie", "sweatpants", "comfortable", "relaxed teen"],
                        ["band t-shirt", "ripped jeans", "alternative", "edgy teen"],
                        ["polo shirt", "chinos", "preppy", "clean-cut teen"],
                        ["flannel shirt", "jeans", "casual", "laid-back teen"],
                        ["basketball jersey", "shorts", "sporty", "athletic teen"],
                        ["button-up shirt", "jeans", "neat", "mature teen"],
                        ["skateboard shirt", "cargo shorts", "skater style", "urban teen"]
                    ]
                    clothing_tags.extend(styles[name_hash])

            elif age < 30:
                # Young adults
                if gender == 'female':
                    styles = [
                        ["casual modern", "jeans", "trendy top", "young adult style"],
                        ["dress", "fashionable", "young professional"],
                        ["blouse", "slacks", "business casual", "working woman"],
                        ["t-shirt", "jeans", "casual comfortable"],
                        ["sweater", "leggings", "cozy modern"],
                        ["tank top", "shorts", "casual summer"]
                    ]
                    clothing_tags.extend(styles[name_hash % 6])
                else:
                    styles = [
                        ["casual shirt", "jeans", "modern style"],
                        ["button-up", "slacks", "young professional"],
                        ["t-shirt", "jeans", "relaxed casual"],
                        ["polo shirt", "chinos", "smart casual"],
                        ["hoodie", "jeans", "comfortable modern"],
                        ["henley", "jeans", "casual masculine"]
                    ]
                    clothing_tags.extend(styles[name_hash % 6])

            elif age < 50:
                # Middle-aged adults
                if gender == 'female':
                    styles = [
                        ["blouse", "slacks", "professional adult"],
                        ["casual dress", "comfortable mature"],
                        ["cardigan", "jeans", "practical adult"],
                        ["business casual", "neat mature style"]
                    ]
                    clothing_tags.extend(styles[name_hash % 4])
                else:
                    styles = [
                        ["button-up shirt", "slacks", "mature professional"],
                        ["polo shirt", "khakis", "casual adult"],
                        ["collared shirt", "jeans", "practical mature"],
                        ["sweater", "slacks", "comfortable adult"]
                    ]
                    clothing_tags.extend(styles[name_hash % 4])

            else:
                # Older adults
                if gender == 'female':
                    clothing_tags.extend(["modest dress", "comfortable", "mature style", "practical"])
                else:
                    clothing_tags.extend(["button-up shirt", "slacks", "comfortable", "mature gentleman"])

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
        elif portrait_type == "cowboy_shot":
            tags.extend([
                "cowboy shot",
                "waist up",
                "upper body",
                "from waist",
                "torso visible",
                "medium shot",
                "upper outfit visible",
                "standing",
                "studio shot",
                "white background",
                "natural light",
                "indoors",
                "minimalistic background",
                "sharp focus",
                "well proportioned",
                "fashion",
                "character focus"
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
        elif portrait_type == "cowboy_shot":
            negative_tags.extend([
                "full body",
                "legs visible",
                "feet visible",
                "headshot only",
                "close-up only",
                "cropped at chest",
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
