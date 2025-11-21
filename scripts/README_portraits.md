# NPC Portrait Batch Generator

This script pre-generates portraits for all NPCs in `npc_data/npc_roster.json`.

## Prerequisites

1. **ComfyUI must be running** at `http://127.0.0.1:8188`
2. Make sure you have the correct checkpoint model loaded (cyberrealisticXL)

## Usage

```bash
# From the Willowcreek directory
python3 scripts/generate_all_portraits.py
```

## What It Does

1. Reads all NPCs from `npc_data/npc_roster.json`
2. For each NPC:
   - Checks if portrait already exists (skips if cached)
   - Generates a 768x768 portrait using their appearance data
   - Saves image to `static/generated_images/`
   - Updates cache in `static/npc_portraits/portrait_cache.json`
3. Shows progress and summary

## After Generation

Once complete, the simulation will automatically use these portraits when NPCs appear in narratives. No additional configuration needed!

## Regenerating Portraits

If you want to regenerate a portrait:
1. Delete the entry from `static/npc_portraits/portrait_cache.json`
2. Run the script again

Or to regenerate ALL portraits:
```bash
rm static/npc_portraits/portrait_cache.json
python3 scripts/generate_all_portraits.py
```

## Timing

- Each portrait takes ~10-30 seconds to generate (depends on ComfyUI speed)
- For 20 NPCs, expect ~10-15 minutes total
- Script shows progress and can be interrupted with Ctrl+C
