# NPC Portrait Batch Generator

This script pre-generates portraits for all NPCs in `npc_data/npc_roster.json` **and** `npc_data/npc_generic.json` (generic NPCs).

## Prerequisites

1. **ComfyUI must be running** at `http://127.0.0.1:8188`
2. Make sure you have the correct checkpoint model loaded (cyberrealisticXL)

## Usage

```bash
# From the Willowcreek directory

# Generate headshots (1024x1024, head & shoulders, default)
python3 scripts/generate_all_portraits.py

# Generate cowboy shots (896x1152, waist up)
python3 scripts/generate_all_portraits.py --type cowboy_shot

# Generate full body portraits (832x1216, head to toe)
python3 scripts/generate_all_portraits.py --type full_body

# Or explicitly specify headshots
python3 scripts/generate_all_portraits.py --type headshot
```

## Portrait Types

### Headshot (default)
- **Dimensions:** 1024x1024 pixels (square)
- **Composition:** Head and shoulders portrait
- **Focus:** Face details, eyes, expression
- **Best for:** Character avatars, profile pictures, UI displays

### Cowboy Shot
- **Dimensions:** 896x1152 pixels (portrait orientation)
- **Composition:** Waist up, medium shot showing upper body
- **Focus:** Face, upper outfit, torso
- **Best for:** Character dialogue portraits, showing outfit + face, social media style

### Full Body
- **Dimensions:** 832x1216 pixels (portrait orientation)
- **Composition:** Standing pose, full body from head to feet
- **Focus:** Complete outfit, body language, full appearance
- **Best for:** Character reference sheets, detailed character views

## What It Does

1. Reads all NPCs from `npc_data/npc_roster.json`
2. For each NPC:
   - Checks if portrait already exists (skips if cached)
   - Generates a portrait using their appearance data (1024x1024 for headshot, 832x1216 for full body)
   - Saves image to `static/generated_images/`
   - Updates cache in `static/npc_portraits/portrait_cache.json`
3. Shows progress and summary

## After Generation

Once complete, the simulation will automatically use these portraits when NPCs appear in narratives. No additional configuration needed!

## Caching

- Headshots and full body portraits are cached separately
- You can have both types for the same NPC
- Cache keys format: `{npc_name}_headshot` or `{npc_name}_full_body`
- Each NPC can have multiple portrait types without conflict

## Regenerating Portraits

If you want to regenerate a specific portrait type:
1. Delete the entry from `static/npc_portraits/portrait_cache.json`
   - Example: Remove `"Sarah Madison_full_body"` entry
2. Run the script again with the same `--type`

Or to regenerate ALL headshots:
```bash
# Manual: Edit portrait_cache.json and remove all *_headshot entries
python3 scripts/generate_all_portraits.py --type headshot
```

Or to regenerate ALL full body portraits:
```bash
# Manual: Edit portrait_cache.json and remove all *_full_body entries
python3 scripts/generate_all_portraits.py --type full_body
```

## Timing

- Each portrait takes ~10-30 seconds to generate (depends on ComfyUI speed)
- For 20 NPCs, expect ~10-15 minutes total
- Script shows progress and can be interrupted with Ctrl+C
