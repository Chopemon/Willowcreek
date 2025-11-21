#!/usr/bin/env python3
"""
Batch Portrait Generator for Willow Creek NPCs
Generates portraits for all NPCs in npc_roster.json and caches them.
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.comfyui_client import ComfyUIClient
from services.npc_portrait_generator import NPCPortraitGenerator


async def generate_all_portraits(portrait_type: str = "headshot"):
    """Generate portraits for all NPCs in npc_roster.json"""

    # Setup
    base_dir = Path(__file__).parent.parent
    roster_file = base_dir / "npc_data" / "npc_roster.json"

    print("=" * 60)
    print("Willow Creek NPC Portrait Batch Generator")
    print(f"Portrait Type: {portrait_type.upper()}")
    print("=" * 60)

    # Check if ComfyUI is available
    comfyui_url = "http://127.0.0.1:8188"
    print(f"\n[Setup] Checking ComfyUI at {comfyui_url}...")

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{comfyui_url}/system_stats") as resp:
                if resp.status != 200:
                    print(f"[Error] ComfyUI not responding properly")
                    return
        print("[Setup] ✓ ComfyUI is running")
    except Exception as e:
        print(f"[Error] Cannot connect to ComfyUI: {e}")
        print(f"[Error] Please start ComfyUI first!")
        return

    # Initialize clients
    print("[Setup] Initializing ComfyUI client...")
    comfyui_client = ComfyUIClient(base_url=comfyui_url)

    print("[Setup] Initializing portrait generator...")
    portrait_gen = NPCPortraitGenerator(comfyui_client=comfyui_client)

    # Load NPC roster
    print(f"\n[Loading] Reading NPC roster from {roster_file}...")
    if not roster_file.exists():
        print(f"[Error] NPC roster not found at {roster_file}")
        return

    with open(roster_file, 'r', encoding='utf-8') as f:
        npc_roster = json.load(f)

    print(f"[Loading] ✓ Found {len(npc_roster)} NPCs in roster")

    # Generate portraits
    print("\n" + "=" * 60)
    print("Starting Portrait Generation")
    print("=" * 60 + "\n")

    successful = 0
    skipped = 0
    failed = 0

    for idx, npc in enumerate(npc_roster, 1):
        npc_name = npc.get('name', 'Unknown')

        print(f"\n[{idx}/{len(npc_roster)}] Processing: {npc_name}")
        print("-" * 40)

        # Check if already cached
        if portrait_gen.has_portrait(npc_name, portrait_type):
            existing_url = portrait_gen.get_portrait_url(npc_name, portrait_type)
            print(f"  ℹ Already cached ({portrait_type}): {existing_url}")
            skipped += 1
            continue

        # Prepare NPC data
        npc_data = {
            'gender': npc.get('gender', 'person'),
            'age': npc.get('age', 25),
            'traits': npc.get('coreTraits', []),
            'quirk': npc.get('quirk', ''),
            'appearance': npc.get('appearance', '')
        }

        print(f"  Age: {npc_data['age']}")
        print(f"  Gender: {npc_data['gender']}")
        print(f"  Appearance: {npc_data['appearance'][:80]}...")

        # Generate portrait
        try:
            portrait_url = await portrait_gen.generate_portrait(npc_name, npc_data, portrait_type)

            if portrait_url:
                print(f"  ✓ SUCCESS: {portrait_url}")
                successful += 1
            else:
                print(f"  ✗ FAILED: Generation returned None")
                failed += 1

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

        # Small delay between generations to avoid overwhelming ComfyUI
        await asyncio.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"\n✓ Successful: {successful}")
    print(f"ℹ Skipped (already cached): {skipped}")
    print(f"✗ Failed: {failed}")
    print(f"\nTotal NPCs: {len(npc_roster)}")

    print(f"\nPortraits saved to: {base_dir / 'static' / 'generated_images'}/")
    print(f"Cache file: {base_dir / 'static' / 'npc_portraits' / 'portrait_cache.json'}")
    print("\nThe simulation will now automatically use these portraits!")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate portraits for all NPCs in npc_roster.json")
    parser.add_argument(
        "--type",
        choices=["headshot", "full_body"],
        default="headshot",
        help="Type of portrait to generate: 'headshot' (768x768, circular) or 'full_body' (512x896, standing)"
    )
    args = parser.parse_args()

    print("\nStarting batch portrait generation...")
    print("This may take a while depending on the number of NPCs.\n")

    try:
        asyncio.run(generate_all_portraits(portrait_type=args.type))
    except KeyboardInterrupt:
        print("\n\n[Interrupted] Portrait generation cancelled by user.")
    except Exception as e:
        print(f"\n\n[Error] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
