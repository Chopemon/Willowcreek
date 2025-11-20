# ComfyUI Workflow Integration

## How to Use Custom Workflows

The Willow Creek game can automatically generate images using your custom ComfyUI workflows!

### Quick Start

1. **Export your workflow from ComfyUI:**
   - Open ComfyUI in your browser (http://127.0.0.1:8188)
   - Load your desired workflow
   - Click "Save (API Format)" button
   - Save the JSON file as `sdxl_upscale.json` in this directory

2. **Configure Node IDs (IMPORTANT!):**

   Edit `config.json` to match your workflow's node IDs:

   ```json
   {
     "node_mapping": {
       "positive_prompt": "1",
       "negative_prompt": "2",
       "seed": "30",
       "samplers": ["50", "61", "3"]
     }
   }
   ```

   **How to find your node IDs:**
   - Open your workflow JSON file
   - Search for `"class_type": "CLIPTextEncode"` - note the node numbers
   - The first one is usually positive prompt, second is negative
   - Search for seed-related nodes (KSampler, SeedGenerator)
   - Update `config.json` with your node numbers

   **Example:** If your workflow has:
   - Node 5: Positive prompt → `"positive_prompt": "5"`
   - Node 6: Negative prompt → `"negative_prompt": "6"`
   - Node 15: Seed → `"seed": "15"`
   - Nodes 20, 25: Samplers → `"samplers": ["20", "25"]`

3. **Restart the game** and enable ComfyUI:
   ```bash
   export COMFYUI_ENABLED=true
   export COMFYUI_URL=http://127.0.0.1:8188
   python web_app.py
   ```

### Supported Workflows

The system is designed for SDXL workflows with:
- Text-to-image generation
- Optional upscaling
- Optional detail enhancement
- Portrait dimensions (832x1216) recommended

### How It Works

When an important scene occurs in the game:
1. The scene is analyzed for visual priority
2. A detailed prompt is generated
3. The prompt is injected into Node 1 (positive) and Node 2 (negative)
4. A random seed is injected into Node 30 and sampler nodes
5. The workflow is sent to ComfyUI for generation
6. The resulting image appears in the web interface

### Troubleshooting

**"Workflow not found" message?**
- Make sure `sdxl_upscale.json` exists in this directory
- Check that the JSON file is valid (exported from ComfyUI in API format)

**Images not generating?**
- Verify ComfyUI is running (http://127.0.0.1:8188)
- Check that your workflow uses the standard node IDs (1, 2, 30)
- Look at server console for detailed error messages

**Wrong model loading?**
- Export your workflow with the correct checkpoint already selected
- The system preserves all model/settings from your saved workflow
