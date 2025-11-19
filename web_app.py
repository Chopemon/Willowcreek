#############################################################
# web_app.py — FINAL FIXED VERSION (Event Reporting)
#############################################################
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional

# Custom Imports
from narrative_chat import NarrativeChat
from world_snapshot_builder import build_frontend_snapshot
from services.comfyui_client import ComfyUIClient
from services.scene_image_generator import SceneAnalyzer, ImagePromptGenerator
import os

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = ""

# Image Generation Services
COMFYUI_ENABLED = os.getenv("COMFYUI_ENABLED", "false").lower() == "true"
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
comfyui_client = ComfyUIClient(base_url=COMFYUI_URL) if COMFYUI_ENABLED else None
scene_analyzer = SceneAnalyzer()
prompt_generator = ImagePromptGenerator()

# Serve Static Files (CSS/JS)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Serve Generated Images
generated_images_dir = BASE_DIR / "static" / "generated_images"
generated_images_dir.mkdir(exist_ok=True)
app.mount("/generated_images", StaticFiles(directory=generated_images_dir), name="generated_images")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>ERROR: index.html not found</h1>", status_code=500)
    return index_path.read_text(encoding="utf-8")

# --- INIT SIMULATION ---
@app.get("/api/init", response_class=JSONResponse)
async def init_sim(request: Request):
    global chat, current_mode
    mode = request.query_params.get("mode", "openrouter")
    
    if mode != current_mode or chat is None:
        print(f"Initializing Simulation in {mode} mode...")
        try:
            chat = NarrativeChat(mode=mode)
            chat.initialize()
            current_mode = mode
            narration = f"**[System: Initialized {mode.upper()} Mode]**\n\n{chat.last_narrated}"
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    else:
        chat.initialize()
        narration = f"**[System: Reset {mode.upper()} Mode]**\n\n{chat.last_narrated}"
            
    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({"narration": narration, "snapshot": snapshot, "images": []})

# --- ACTION HANDLER ---
@app.post("/api/act", response_class=JSONResponse)
async def process_action(request: Request):
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started. Click 'Start'."}, status_code=400)
        
    data = await request.json()
    text = data.get("text", "").strip()
    
    reply = ""
    generated_images = []  # Initialize for all code paths

    if text.lower() == "debug":
        chat.sim.debug_enabled = not chat.sim.debug_enabled
        reply = f"[Debug: {chat.sim.debug_enabled}]"

    elif text.lower().startswith("wait"):
        try:
            hours = float(text.split()[1])
        except:
            hours = 1

        # Advance time. The tick will populate scenario_buffer with any time-based events.
        chat.advance_time(hours)
        reply = f". {hours} hours pass ."

        # --- Event Reporting for WAIT ---
        if hasattr(chat.sim, 'scenario_buffer'):
            for e in chat.sim.scenario_buffer:
                reply += f"\n\n[SYSTEM EVENT]: {e}"

        # Generate images for wait events too
        if COMFYUI_ENABLED and comfyui_client and hasattr(chat.sim, 'scenario_buffer'):
            for event_text in chat.sim.scenario_buffer:
                scene_context = scene_analyzer.analyze_scene(event_text, chat.sim, chat.malcolm)

                if scene_context and scene_context.priority >= 7:
                    print(f"[ImageGen] Generating image for wait event: {scene_context.activity}")
                    positive_prompt, negative_prompt = prompt_generator.generate_prompt(scene_context)

                    try:
                        image_url = await comfyui_client.generate_image(
                            prompt=positive_prompt,
                            negative_prompt=negative_prompt,
                            width=832,
                            height=1216,
                            steps=20,
                            cfg_scale=7.0
                        )

                        if image_url:
                            generated_images.append({
                                "url": image_url,
                                "caption": scene_context.activity,
                                "scene_type": scene_context.scene_type
                            })
                    except Exception as e:
                        print(f"[ImageGen] Error: {e}")

        # Clear after processing
        if hasattr(chat.sim, 'scenario_buffer'):
            chat.sim.scenario_buffer.clear()

    else:
        # 1. Clear buffer before starting (to prevent carrying over events from a previous WAIT)
        chat.sim.scenario_buffer.clear()
        
        # 2. Generate narrative
        reply = chat.narrate(text)
        
        # 3. Advance time (tick runs and generates internal events into scenario_buffer)
        chat.advance_time(5.0 / 60.0)

        # 4. Run text-based event detection (appends to buffer)
        # FIXED: Use both LLM output (reply) and User Input (text) for better detection
        detection_text = reply + " " + text
        
        try: chat.sim.quirks.process_quirks(detection_text)
        except Exception as e: print(f"Quirks detection failed: {e}")
        try:
            hint = chat.sim.sexual.detect_and_process(detection_text)
            if hint:
                chat.sim.scenario_buffer.append(hint)
        except Exception as e: print(f"Sexual detection failed: {e}")

        # 5. Report events
        if hasattr(chat.sim, 'scenario_buffer'):
            for e in chat.sim.scenario_buffer:
                reply += f"\n\n[SYSTEM EVENT]: {e}"

        # 6. GENERATE IMAGES for interesting scenes
        if COMFYUI_ENABLED and comfyui_client and hasattr(chat.sim, 'scenario_buffer'):
            for event_text in chat.sim.scenario_buffer:
                # Analyze if this event deserves an image
                scene_context = scene_analyzer.analyze_scene(event_text, chat.sim, chat.malcolm)

                if scene_context and scene_context.priority >= 7:  # High priority scenes only
                    print(f"[ImageGen] Generating image for: {scene_context.activity}")

                    # Generate image prompt
                    positive_prompt, negative_prompt = prompt_generator.generate_prompt(scene_context)

                    # Generate image via ComfyUI
                    try:
                        image_url = await comfyui_client.generate_image(
                            prompt=positive_prompt,
                            negative_prompt=negative_prompt,
                            width=832,
                            height=1216,
                            steps=20,
                            cfg_scale=7.0
                        )

                        if image_url:
                            generated_images.append({
                                "url": image_url,
                                "caption": scene_context.activity,
                                "scene_type": scene_context.scene_type
                            })
                            print(f"[ImageGen] ✓ Image generated: {image_url}")
                    except Exception as e:
                        print(f"[ImageGen] Error generating image: {e}")

        # Clear scenario buffer after processing
        if hasattr(chat.sim, 'scenario_buffer'):
            chat.sim.scenario_buffer.clear()

    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({
        "narration": reply,
        "snapshot": snapshot,
        "images": generated_images  # NEW: Include generated images
    })

if __name__ == "__main__":
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)