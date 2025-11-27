# Portrait Generation Guide

This guide will help you auto-generate portraits for all NPCs in Willow Creek using AI image generation.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Options](#api-options)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Option 1: OpenAI DALL-E 3 (Recommended)

**Pros:** Highest quality, best prompt adherence, easiest to use
**Cons:** Costs ~$0.04 per image ($2-3 for all characters)

```bash
# 1. Install OpenAI library
pip install openai

# 2. Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# 3. Generate all portraits
python scripts/generate_portraits.py --api openai --category all
```

### Option 2: Local Stable Diffusion (Free!)

**Pros:** Completely free, unlimited generations
**Cons:** Requires setup, needs good GPU

```bash
# 1. Install and run automatic1111 webui with API enabled
# See: https://github.com/AUTOMATIC1111/stable-diffusion-webui

# 2. Generate portraits
python scripts/generate_portraits.py --api local --category all
```

## 🎨 API Options

### 1. OpenAI DALL-E 3 ⭐ Recommended

**Best for:** Highest quality, production use

- **Quality:** ⭐⭐⭐⭐⭐
- **Speed:** Fast (10-20 seconds per image)
- **Cost:** ~$0.04 per image
- **Setup:** Very easy

```bash
# Get API key: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."
python scripts/generate_portraits.py --api openai --category all
```

### 2. Stability AI (Stable Diffusion XL)

**Best for:** Good balance of quality and cost

- **Quality:** ⭐⭐⭐⭐
- **Speed:** Fast (5-10 seconds per image)
- **Cost:** ~$0.01 per image
- **Setup:** Easy

```bash
# Get API key: https://platform.stability.ai/
export STABILITY_API_KEY="sk-..."
python scripts/generate_portraits.py --api stability --category all
```

### 3. Replicate

**Best for:** Trying different models

- **Quality:** ⭐⭐⭐⭐
- **Speed:** Medium (15-30 seconds per image)
- **Cost:** ~$0.005-0.02 per image
- **Setup:** Easy

```bash
# Get API key: https://replicate.com/account
pip install replicate
export REPLICATE_API_KEY="r8_..."
python scripts/generate_portraits.py --api replicate --category all
```

### 4. Local Stable Diffusion (Free) 🆓

**Best for:** Unlimited free generations, custom models

- **Quality:** ⭐⭐⭐⭐ (depends on model)
- **Speed:** Varies (GPU dependent)
- **Cost:** FREE
- **Setup:** More complex

```bash
# 1. Install automatic1111 webui
# https://github.com/AUTOMATIC1111/stable-diffusion-webui

# 2. Run with API enabled
./webui.sh --api

# 3. Generate
python scripts/generate_portraits.py --api local --category all
```

## 📦 Installation

### 1. Basic Setup

```bash
# Already done if you've been using Willow Creek
cd Willowcreek
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 2. Install API Libraries (as needed)

```bash
# For OpenAI
pip install openai

# For Replicate
pip install replicate

# For Stability AI (uses requests, already installed)
# No additional installation needed

# For Local SD (uses requests, already installed)
# Just need to run automatic1111 webui
```

### 3. Set API Keys

#### Option A: Environment Variables (Recommended)

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
export STABILITY_API_KEY="sk-your-key-here"
export REPLICATE_API_KEY="r8_your-key-here"

# Windows
set OPENAI_API_KEY=sk-your-key-here
set STABILITY_API_KEY=sk-your-key-here
set REPLICATE_API_KEY=r8_your-key-here
```

#### Option B: .env File

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your favorite editor
```

#### Option C: Command Line

```bash
python scripts/generate_portraits.py --api openai --api-key "sk-your-key-here" --category all
```

## 💡 Usage Examples

### Generate Everything

```bash
# All characters, both categories
python scripts/generate_portraits.py --api openai --category all
```

### Generate Specific Category

```bash
# Only NPC roster (main characters)
python scripts/generate_portraits.py --api openai --category npc_roster

# Only generic NPCs
python scripts/generate_portraits.py --api openai --category npc_generic
```

### Generate Specific Characters

```bash
# Just a few characters
python scripts/generate_portraits.py \
  --api openai \
  --characters "Sarah Madison,David Madison,Eve Madison"
```

### Adjust Rate Limiting

```bash
# Add 2 second delay between requests (for API rate limits)
python scripts/generate_portraits.py \
  --api openai \
  --category all \
  --delay 2.0
```

### Resume After Interruption

The script automatically skips existing images, so you can safely re-run:

```bash
# If interrupted, just run again - it will skip completed ones
python scripts/generate_portraits.py --api openai --category all
```

## 📁 Output Structure

Generated portraits are saved to:

```
portraits/
├── npc_generic/
│   ├── Marjorie_Hales.png
│   ├── Earl_Peterson.png
│   ├── Aaliyah_Flores.png
│   └── ...
└── npc_roster/
    ├── Sarah_Madison.png
    ├── David_Madison.png
    ├── Eve_Madison.png
    └── ...
```

## 🔧 Troubleshooting

### "API key not found"

```bash
# Make sure you've set the environment variable
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY% # Windows

# Or pass it directly
python scripts/generate_portraits.py --api openai --api-key "sk-..." --category all
```

### "ModuleNotFoundError: No module named 'openai'"

```bash
# Install the required library
pip install openai
```

### "Connection refused" (Local SD)

```bash
# Make sure automatic1111 is running with API enabled
./webui.sh --api

# Check it's running at http://127.0.0.1:7860
```

### "Rate limit exceeded"

```bash
# Add delay between requests
python scripts/generate_portraits.py --api openai --delay 2.0 --category all

# Or generate in smaller batches
python scripts/generate_portraits.py --api openai --category npc_roster
# Wait a bit...
python scripts/generate_portraits.py --api openai --category npc_generic
```

### Images look wrong/low quality

**For DALL-E 3:**
- DALL-E 3 is already at max quality
- The prompts are very detailed and should produce good results

**For Stability AI:**
- Try increasing steps in the script (edit `generate_portraits.py`, change `steps: 30` to `steps: 50`)

**For Local SD:**
- Make sure you're using a good checkpoint model (like Realistic Vision or Deliberate)
- Increase steps (change `steps: 30` to `steps: 50-80`)
- Try different samplers (DPM++ 2M Karras, Euler a, etc.)

## 💰 Cost Estimation

### All Characters (54 total: 25 generic + 29 roster)

| API | Cost per Image | Total Cost |
|-----|---------------|------------|
| OpenAI DALL-E 3 | $0.040 | ~$2.16 |
| Stability AI | $0.010 | ~$0.54 |
| Replicate | $0.005-0.02 | ~$0.27-1.08 |
| Local SD | FREE | $0.00 |

### Recommended Approach

**For Production/Final Version:**
- Use OpenAI DALL-E 3 (~$2-3 total)
- Highest quality and best prompt adherence

**For Development/Testing:**
- Use Local SD (free)
- Unlimited iterations to get prompts right

**For Budget:**
- Use Stability AI (~$0.50 total)
- Good quality at lower cost

## 🎯 Advanced Tips

### Using Different Models Locally

Edit `generate_portraits.py` and modify the `generate_with_local_sd` function to use different parameters:

```python
payload = {
    "prompt": prompt,
    "negative_prompt": "ugly, deformed, low quality, blurry, cartoon, anime",
    "steps": 50,  # Increase for better quality
    "width": 1024,
    "height": 1024,
    "cfg_scale": 7,
    "sampler_name": "Euler a",  # Try different samplers
    "seed": -1,  # Set specific seed for reproducibility
}
```

### Batch Processing with Error Handling

```bash
# Generate roster first (main characters)
python scripts/generate_portraits.py --api openai --category npc_roster

# Review the results, then generate generic
python scripts/generate_portraits.py --api openai --category npc_generic
```

### Custom Prompts

Edit `portrait_prompts.json` to customize any character's prompt, then re-run generation for just that character:

```bash
# Delete the old image
rm portraits/npc_roster/Sarah_Madison.png

# Regenerate just that one
python scripts/generate_portraits.py --api openai --characters "Sarah Madison"
```

## 📚 Additional Resources

- [OpenAI DALL-E 3 Docs](https://platform.openai.com/docs/guides/images)
- [Stability AI API Docs](https://platform.stability.ai/docs/getting-started)
- [Replicate Docs](https://replicate.com/docs)
- [Automatic1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

## 🤝 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure your API keys are valid
3. Verify you have the required libraries installed
4. Check the console output for specific error messages

---

**Happy portrait generating!** 🎨✨
