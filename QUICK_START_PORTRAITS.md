# 🎨 Quick Start: Generate All Portraits

The fastest way to generate portraits for all 54 NPCs.

## ⚡ 60 Second Setup

### Option 1: OpenAI DALL-E 3 (Best Quality)

```bash
# 1. Install
pip install openai

# 2. Set API key (get from https://platform.openai.com/api-keys)
export OPENAI_API_KEY="sk-..."

# 3. Generate
python scripts/generate_portraits.py --api openai --category all

# Done! Check portraits/ folder
```

**Cost: ~$2-3 for all 54 characters**

---

### Option 2: Free (Local Stable Diffusion)

```bash
# 1. Install automatic1111 webui
# See: https://github.com/AUTOMATIC1111/stable-diffusion-webui

# 2. Run with API
./webui.sh --api  # or webui-user.bat on Windows

# 3. Generate
python scripts/generate_portraits.py --api local --category all

# Done! Check portraits/ folder
```

**Cost: FREE (requires GPU)**

---

## 📊 What Gets Generated

```
portraits/
├── npc_generic/      (25 characters)
│   ├── Marjorie_Hales.png
│   ├── Earl_Peterson.png
│   └── ...
└── npc_roster/       (29 characters)
    ├── Sarah_Madison.png
    ├── David_Madison.png
    └── ...
```

## 🧪 Test First (Optional)

Before generating all portraits, test with one:

```bash
python scripts/test_portrait_gen.py --api openai
```

This generates just Sarah Madison to verify your setup works.

## 🔍 More Options

For detailed documentation, see [PORTRAIT_GENERATION.md](PORTRAIT_GENERATION.md)

- Different APIs (Stability AI, Replicate)
- Generate specific characters only
- Customize prompts
- Troubleshooting
- Cost breakdowns

## ❓ Quick FAQ

**Q: Which API should I use?**
- **Best quality:** OpenAI DALL-E 3 (~$2-3)
- **Best value:** Stability AI (~$0.50)
- **Free:** Local Stable Diffusion (requires setup)

**Q: How long does it take?**
- OpenAI: ~15 minutes for all 54 characters
- Stability: ~10 minutes
- Local SD: Varies (depends on GPU)

**Q: Can I regenerate specific characters?**
Yes! Just delete the image and run with `--characters "Name"`:
```bash
rm portraits/npc_roster/Sarah_Madison.png
python scripts/generate_portraits.py --api openai --characters "Sarah Madison"
```

**Q: What if I get interrupted?**
No problem! Just re-run the same command. It automatically skips existing images.

---

**That's it! Start generating:** 🚀

```bash
python scripts/generate_portraits.py --api openai --category all
```
