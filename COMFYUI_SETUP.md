# ComfyUI Image Generation Setup

This document explains how to enable automatic image generation for dramatic scenes in Willowcreek.

## Overview

When enabled, the system automatically:
1. **Detects** interesting narrative moments (sexual encounters, character quirks, school drama, etc.)
2. **Generates** detailed image prompts from the scene context
3. **Creates** images via ComfyUI API
4. **Displays** generated images in the web interface

## Requirements

### 1. Install ComfyUI

Download and install ComfyUI:
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 2. Download a Model

You need at least one Stable Diffusion model. Recommended:

**SDXL (High Quality):**
- Download: [sd_xl_base_1.0.safetensors](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
- Place in: `ComfyUI/models/checkpoints/`

**OR Realistic Model (Better for character scenes):**
- [Realistic Vision v5.1](https://civitai.com/models/4201/realistic-vision-v51)
- [DreamShaper XL](https://civitai.com/models/112902/dreamshaper-xl)

### 3. Start ComfyUI Server

```bash
cd ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

ComfyUI will be available at: `http://127.0.0.1:8188`

## Enable in Willowcreek

### Method 1: Environment Variables (Recommended)

Create a `.env` file in the Willowcreek directory:

```env
# Enable ComfyUI integration
COMFYUI_ENABLED=true

# ComfyUI server URL (default: http://127.0.0.1:8188)
COMFYUI_URL=http://127.0.0.1:8188

# OpenRouter API key (for narrative generation)
OPENROUTER_API_KEY=your_key_here
```

Then load environment variables before starting:

```bash
export $(cat .env | xargs)
python web_app.py
```

### Method 2: Direct Export

```bash
export COMFYUI_ENABLED=true
export COMFYUI_URL=http://127.0.0.1:8188
python web_app.py
```

## How It Works

### Automatic Scene Detection

The system analyzes events from the simulation and generates images for:

**Priority 10 - Sexual Encounters:**
- Detected when: `[SEXUAL:` tag appears in events
- Example: Intimate moments, passionate scenes

**Priority 9 - Emma's Reflex (Character Quirk):**
- Detected when: `[EMMA REFLEX:` tag appears
- Example: Involuntary physical reactions

**Priority 8 - Alex Sturm Frustration:**
- Detected when: `[ALEX STURM:` with "Frustration" mentioned
- Example: Tension buildup when husband is away

**Priority 7+ - Other Dramatic Moments:**
- School confrontations
- Crimes
- Intense emotional moments

### Image Generation Flow

```
Narrative Event → Scene Analyzer → Priority Check (≥7)
                      ↓
              Image Prompt Generator
                      ↓
        Positive Prompt + Negative Prompt
                      ↓
              ComfyUI API Call
                      ↓
         Image Saved + URL Returned
                      ↓
          Displayed in Web Interface
```

### Example Prompts

**Sexual Scene:**
```
Positive: masterpiece, best quality, highly detailed, 4k, professional
photograph, intimate photography, soft lighting, shallow depth of field,
cinematic, 2people, man and woman, realistic humans, intimate moment,
close proximity, bedroom interior, residential setting, dim lighting,
night atmosphere, intense emotion, passionate atmosphere

Negative: low quality, blurry, distorted, ugly, deformed, cartoon,
anime, bad anatomy, explicit nudity, pornographic, genitals, text,
watermark, logo, multiple heads, bad hands
```

**Character Quirk (Emma):**
```
Positive: masterpiece, best quality, highly detailed, 4k, professional
photograph, dramatic moment, character focus, emotional expression,
narrative storytelling, 1person, adult, realistic human, body arches
involuntarily, school setting, hallway or classroom, bright daylight,
tense, anxious energy, dramatic lighting

Negative: low quality, blurry, distorted, ugly, deformed, cartoon,
anime, bad anatomy, overly sexual, explicit content, text, watermark
```

## Custom Workflows

### Using Your Own ComfyUI Workflow

Edit `services/comfyui_client.py` and modify the `_build_default_workflow()` method:

```python
def _build_default_workflow(self, prompt, negative_prompt, ...):
    # Load your custom workflow JSON
    with open('my_workflow.json') as f:
        workflow = json.load(f)

    # Update prompt nodes
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt

    return workflow
```

### Adjusting Model

In `comfyui_client.py`, change the checkpoint:

```python
"4": {
    "inputs": {
        "ckpt_name": "dreamshaper_xl.safetensors"  # Your model name
    },
    "class_type": "CheckpointLoaderSimple"
}
```

## Customization

### Scene Priority Threshold

In `web_app.py`, adjust which scenes get images:

```python
if scene_context and scene_context.priority >= 7:  # Change this number
    # Generate image
```

Lower = more images, Higher = only most dramatic scenes

### Image Settings

In `web_app.py`, adjust generation parameters:

```python
image_url = await comfyui_client.generate_image(
    prompt=positive_prompt,
    negative_prompt=negative_prompt,
    width=832,        # Change image size
    height=1216,      # Portrait orientation
    steps=20,         # More steps = better quality (slower)
    cfg_scale=7.0     # Prompt adherence (higher = stricter)
)
```

### Adding New Scene Types

Edit `services/scene_image_generator.py`:

```python
self.patterns = {
    # Add your pattern
    r"\[MY_EVENT:": {"type": "custom", "priority": 8, "explicit": 5},
    # ... existing patterns
}
```

## Troubleshooting

### No Images Appearing

1. **Check ComfyUI is running:**
   ```bash
   curl http://127.0.0.1:8188/system_stats
   ```

2. **Check environment variable:**
   ```python
   python -c "import os; print(os.getenv('COMFYUI_ENABLED'))"
   ```

3. **Check server logs** for `[ImageGen]` messages

### Image Generation Slow

- Reduce `steps` (try 15-18)
- Use smaller resolution (e.g., 768x1024)
- Use faster model (SD1.5 instead of SDXL)
- Enable GPU acceleration in ComfyUI

### Poor Image Quality

- Increase `steps` (try 25-30)
- Adjust `cfg_scale` (try 6.0-9.0)
- Use better checkpoint model
- Improve prompts in `scene_image_generator.py`

### Images Don't Match Scene

**Improve character descriptions:**

Edit `services/scene_image_generator.py`:

```python
def _build_character_description(self, characters):
    # Add character-specific appearance data
    char_data = {
        "Emma Pearson": "young woman, blonde hair, innocent look",
        "Malcolm Newt": "man, 30s, casual clothing",
        # ... add more
    }

    descriptions = [char_data.get(c, "person") for c in characters]
    return ", ".join(descriptions)
```

## Performance

**Generation Time:**
- SDXL: ~10-30 seconds per image (GPU)
- SD1.5: ~5-15 seconds per image (GPU)
- CPU only: 2-10 minutes (not recommended)

**Storage:**
- Each image: ~500KB - 2MB
- Daily simulation: ~10-50 images
- Weekly: ~350 images (~700MB)

Images are stored in: `static/generated_images/`

## Advanced: LoRA & Embeddings

To use character-specific LoRAs or textual inversions, add nodes to the workflow:

```python
"10": {
    "inputs": {
        "lora_name": "emma_character_v2.safetensors",
        "strength_model": 0.8,
        "strength_clip": 0.8,
        "model": ["4", 0]
    },
    "class_type": "LoraLoader"
}
```

Place LoRA files in: `ComfyUI/models/loras/`

## Safety & Content Filtering

The system includes automatic filtering:

- **Explicit Level 8+:** Adds `explicit nudity, pornographic, genitals` to negative prompt
- **Explicit Level 5-7:** Adds `overly sexual, explicit content` to negative prompt

Adjust in `services/scene_image_generator.py`:

```python
def _build_negative_prompt(self, explicit_level: int) -> str:
    # Customize content filtering here
    pass
```

## Disable Image Generation

Set environment variable:

```bash
export COMFYUI_ENABLED=false
python web_app.py
```

Or remove from `.env` file.

---

## Support

For issues:
1. Check ComfyUI logs: `ComfyUI/comfyui.log`
2. Check Willowcreek console for `[ImageGen]` and `[ComfyUI]` messages
3. Verify model files are in correct directory
4. Test ComfyUI independently before integrating
