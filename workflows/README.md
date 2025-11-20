# ComfyUI Workflow Integration

## How to Use Custom Workflows

The Willow Creek game can automatically generate images using your custom ComfyUI workflows!

### Quick Start

1. **Export your workflow from ComfyUI:**
   - Open ComfyUI in your browser (http://127.0.0.1:8188)
   - Load your desired workflow
   - Click "Save (API Format)" button
   - Save the JSON file as `sdxl_upscale.json` in this directory

2. **Required Node IDs:**
   Your workflow must have these nodes for automatic prompt injection:
   - **Node 1**: CLIPTextEncode for positive prompt (will be auto-filled)
   - **Node 2**: CLIPTextEncode for negative prompt (will be auto-filled)
   - **Node 30**: Seed generator (will be auto-filled)
   - **Node 7 or 57**: SaveImage node (for output)

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
