#!/usr/bin/env python3
"""
Portrait Generation Script for Willow Creek NPCs

Supports multiple image generation APIs:
- OpenAI DALL-E 3
- Stability AI (Stable Diffusion)
- Replicate (various models)
- Local Stable Diffusion

Usage:
    python scripts/generate_portraits.py --api openai --category all
    python scripts/generate_portraits.py --api stability --category roster --characters "Sarah Madison,David Madison"
"""

import os
import json
import argparse
import time
import requests
from pathlib import Path
from typing import Optional, List, Dict
import base64


class PortraitGenerator:
    """Generate portraits using various AI APIs"""

    def __init__(self, api_type: str, api_key: Optional[str] = None):
        self.api_type = api_type.lower()
        self.api_key = api_key or os.getenv(f"{api_type.upper()}_API_KEY")
        self.output_dir = Path("portraits")
        self.output_dir.mkdir(exist_ok=True)

        # Load prompts
        with open("portrait_prompts.json", "r") as f:
            self.prompts = json.load(f)

    def generate_with_openai(self, prompt: str, character_name: str, category: str) -> bool:
        """Generate using OpenAI DALL-E 3"""
        if not self.api_key:
            print("❌ OPENAI_API_KEY not found. Set it via environment variable or config.")
            return False

        try:
            import openai
            openai.api_key = self.api_key

            print(f"🎨 Generating {character_name} with DALL-E 3...")

            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download and save
            image_data = requests.get(image_url).content
            output_path = self.output_dir / category / f"{character_name.replace(' ', '_')}.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"✅ Saved to {output_path}")
            return True

        except ImportError:
            print("❌ OpenAI library not installed. Run: pip install openai")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def generate_with_stability(self, prompt: str, character_name: str, category: str) -> bool:
        """Generate using Stability AI"""
        if not self.api_key:
            print("❌ STABILITY_API_KEY not found. Set it via environment variable or config.")
            return False

        try:
            print(f"🎨 Generating {character_name} with Stability AI...")

            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            body = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }

            response = requests.post(url, headers=headers, json=body)

            if response.status_code != 200:
                print(f"❌ Error: {response.text}")
                return False

            data = response.json()

            # Save image
            for i, image in enumerate(data["artifacts"]):
                output_path = self.output_dir / category / f"{character_name.replace(' ', '_')}.png"
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(image["base64"]))

                print(f"✅ Saved to {output_path}")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def generate_with_replicate(self, prompt: str, character_name: str, category: str) -> bool:
        """Generate using Replicate API"""
        if not self.api_key:
            print("❌ REPLICATE_API_KEY not found. Set it via environment variable or config.")
            return False

        try:
            import replicate

            print(f"🎨 Generating {character_name} with Replicate...")

            # Using SDXL model
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024,
                    "num_outputs": 1
                }
            )

            # Download image
            image_url = output[0]
            image_data = requests.get(image_url).content

            output_path = self.output_dir / category / f"{character_name.replace(' ', '_')}.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"✅ Saved to {output_path}")
            return True

        except ImportError:
            print("❌ Replicate library not installed. Run: pip install replicate")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def generate_with_local_sd(self, prompt: str, character_name: str, category: str) -> bool:
        """Generate using local Stable Diffusion (via automatic1111 API)"""
        try:
            print(f"🎨 Generating {character_name} with Local SD...")

            # Assumes automatic1111 webui running on default port
            url = "http://127.0.0.1:7860/sdapi/v1/txt2img"

            payload = {
                "prompt": prompt,
                "negative_prompt": "ugly, deformed, low quality, blurry, cartoon, anime",
                "steps": 30,
                "width": 1024,
                "height": 1024,
                "cfg_scale": 7,
                "sampler_name": "DPM++ 2M Karras",
            }

            response = requests.post(url, json=payload)

            if response.status_code != 200:
                print(f"❌ Error: {response.text}")
                print("❌ Make sure automatic1111 webui is running with --api flag")
                return False

            data = response.json()

            # Save image
            image_data = base64.b64decode(data["images"][0])
            output_path = self.output_dir / category / f"{character_name.replace(' ', '_')}.png"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"✅ Saved to {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def generate_portrait(self, character_name: str, prompt: str, category: str) -> bool:
        """Generate a single portrait using the configured API"""

        # Check if already exists
        output_path = self.output_dir / category / f"{character_name.replace(' ', '_')}.png"
        if output_path.exists():
            print(f"⏭️  Skipping {character_name} (already exists)")
            return True

        api_methods = {
            "openai": self.generate_with_openai,
            "stability": self.generate_with_stability,
            "replicate": self.generate_with_replicate,
            "local": self.generate_with_local_sd,
        }

        if self.api_type not in api_methods:
            print(f"❌ Unknown API type: {self.api_type}")
            print(f"   Available: {', '.join(api_methods.keys())}")
            return False

        return api_methods[self.api_type](prompt, character_name, category)

    def generate_batch(
        self,
        category: str = "all",
        characters: Optional[List[str]] = None,
        delay: float = 1.0
    ):
        """Generate multiple portraits"""

        categories_to_process = []
        if category == "all":
            categories_to_process = ["npc_generic", "npc_roster"]
        else:
            categories_to_process = [category]

        total = 0
        success = 0
        failed = 0

        for cat in categories_to_process:
            if cat not in self.prompts:
                print(f"⚠️  Category '{cat}' not found in prompts")
                continue

            # Create output directory
            (self.output_dir / cat).mkdir(parents=True, exist_ok=True)

            prompts_data = self.prompts[cat]

            # Filter by character names if specified
            if characters:
                prompts_data = {
                    name: prompt for name, prompt in prompts_data.items()
                    if name in characters
                }

            print(f"\n{'='*60}")
            print(f"📁 Processing {cat}: {len(prompts_data)} characters")
            print(f"{'='*60}\n")

            for char_name, prompt_text in prompts_data.items():
                total += 1

                if self.generate_portrait(char_name, prompt_text, cat):
                    success += 1
                else:
                    failed += 1

                # Rate limiting
                if delay > 0:
                    time.sleep(delay)

        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Generation Complete!")
        print(f"{'='*60}")
        print(f"✅ Successful: {success}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate NPC portraits for Willow Creek",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all portraits using OpenAI
  python scripts/generate_portraits.py --api openai --category all

  # Generate only roster characters using Stability AI
  python scripts/generate_portraits.py --api stability --category npc_roster

  # Generate specific characters
  python scripts/generate_portraits.py --api openai --characters "Sarah Madison,David Madison"

  # Use local Stable Diffusion
  python scripts/generate_portraits.py --api local --category all

Environment Variables:
  OPENAI_API_KEY      - For OpenAI DALL-E 3
  STABILITY_API_KEY   - For Stability AI
  REPLICATE_API_KEY   - For Replicate
        """
    )

    parser.add_argument(
        "--api",
        type=str,
        required=True,
        choices=["openai", "stability", "replicate", "local"],
        help="Which API to use for generation"
    )

    parser.add_argument(
        "--category",
        type=str,
        default="all",
        choices=["all", "npc_generic", "npc_roster"],
        help="Which category to generate (default: all)"
    )

    parser.add_argument(
        "--characters",
        type=str,
        help="Comma-separated list of specific character names to generate"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or set via environment variable)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )

    args = parser.parse_args()

    # Parse character list
    char_list = None
    if args.characters:
        char_list = [c.strip() for c in args.characters.split(",")]

    # Create generator
    generator = PortraitGenerator(args.api, args.api_key)

    # Generate
    generator.generate_batch(
        category=args.category,
        characters=char_list,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
