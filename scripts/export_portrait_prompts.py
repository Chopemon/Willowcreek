#!/usr/bin/env python3
"""
Export all NPC portrait prompts to a text file.
This generates prompts for both headshot and full_body portraits without actually generating images.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.npc_portrait_generator import NPCPortraitGenerator


def export_all_prompts(output_file: str = "portrait_prompts.txt"):
    """Export portrait prompts for all NPCs to a text file"""

    base_dir = Path(__file__).parent.parent
    roster_file = base_dir / "npc_data" / "npc_roster.json"
    generic_file = base_dir / "npc_data" / "npc_generic.json"
    output_path = base_dir / output_file

    print("=" * 60)
    print("NPC Portrait Prompt Exporter")
    print("=" * 60)

    # Initialize portrait generator (without ComfyUI client)
    print("\n[Setup] Initializing portrait prompt generator...")
    portrait_gen = NPCPortraitGenerator(comfyui_client=None)

    # Load NPC roster
    print(f"[Loading] Reading NPC roster from {roster_file}...")
    if not roster_file.exists():
        print(f"[Error] NPC roster not found at {roster_file}")
        return

    with open(roster_file, 'r', encoding='utf-8') as f:
        npc_roster = json.load(f)

    print(f"[Loading] ✓ Found {len(npc_roster)} main NPCs")

    # Load generic NPCs
    generic_roster = []
    if generic_file.exists():
        print(f"[Loading] Reading generic NPCs from {generic_file}...")
        with open(generic_file, 'r', encoding='utf-8') as f:
            generic_roster = json.load(f)
        print(f"[Loading] ✓ Found {len(generic_roster)} generic NPCs")
        npc_roster.extend(generic_roster)
    else:
        print(f"[Loading] ℹ No generic NPCs file found (optional)")

    print(f"[Loading] ✓ Total NPCs to process: {len(npc_roster)}")

    # Generate prompts and write to file
    print(f"\n[Export] Writing prompts to {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("WILLOW CREEK NPC PORTRAIT PROMPTS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total NPCs: {len(npc_roster)}\n")
        f.write(f"Generated prompts for both HEADSHOT and FULL_BODY portraits\n\n")

        for idx, npc in enumerate(npc_roster, 1):
            npc_name = npc.get('name', 'Unknown')

            # Prepare NPC data
            # Check both 'occupation' and 'affiliation' fields for job info
            occupation = npc.get('occupation', '') or npc.get('affiliation', '')

            npc_data = {
                'gender': npc.get('gender', 'person'),
                'age': npc.get('age', 25),
                'traits': npc.get('coreTraits', []),
                'quirk': npc.get('quirk', ''),
                'appearance': npc.get('appearance', ''),
                'occupation': occupation
            }

            # Write NPC header
            f.write("=" * 80 + "\n")
            f.write(f"[{idx}/{len(npc_roster)}] {npc_name}\n")
            f.write("=" * 80 + "\n\n")

            # Basic info
            f.write(f"Age: {npc_data['age']}\n")
            f.write(f"Gender: {npc_data['gender']}\n")
            f.write(f"Occupation: {npc_data['occupation']}\n")
            f.write(f"Traits: {', '.join(npc_data['traits'])}\n")
            f.write(f"Quirk: {npc_data['quirk']}\n")
            f.write(f"Appearance: {npc_data['appearance'][:100]}...\n\n")

            # Generate HEADSHOT prompt
            f.write("-" * 80 + "\n")
            f.write("HEADSHOT PORTRAIT (1024x1024)\n")
            f.write("-" * 80 + "\n\n")

            try:
                positive_prompt, negative_prompt = portrait_gen._build_portrait_prompt(
                    npc_name, npc_data, portrait_type="headshot"
                )

                f.write("POSITIVE PROMPT:\n")
                f.write(positive_prompt + "\n\n")

                f.write("NEGATIVE PROMPT:\n")
                f.write(negative_prompt + "\n\n")
            except Exception as e:
                f.write(f"ERROR: {e}\n\n")

            # Generate FULL_BODY prompt
            f.write("-" * 80 + "\n")
            f.write("FULL BODY PORTRAIT (832x1216)\n")
            f.write("-" * 80 + "\n\n")

            try:
                positive_prompt, negative_prompt = portrait_gen._build_portrait_prompt(
                    npc_name, npc_data, portrait_type="full_body"
                )

                f.write("POSITIVE PROMPT:\n")
                f.write(positive_prompt + "\n\n")

                f.write("NEGATIVE PROMPT:\n")
                f.write(negative_prompt + "\n\n")
            except Exception as e:
                f.write(f"ERROR: {e}\n\n")

            f.write("\n\n")

            # Print progress
            print(f"  [{idx}/{len(npc_roster)}] Exported: {npc_name}")

    print(f"\n[Success] ✓ Exported {len(npc_roster)} NPC prompts to {output_path}")
    print(f"\nFile size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export all NPC portrait prompts to a text file")
    parser.add_argument(
        "--output",
        default="portrait_prompts.txt",
        help="Output filename (default: portrait_prompts.txt)"
    )

    args = parser.parse_args()

    try:
        export_all_prompts(output_file=args.output)
    except KeyboardInterrupt:
        print("\n\n[Interrupted] Export cancelled by user.")
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback
        traceback.print_exc()
