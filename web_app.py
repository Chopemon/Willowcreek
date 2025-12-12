#############################################################
# web_app.py — FINAL FIXED VERSION (Event Reporting)
# UPDATED: Native LLM support added
# UPDATED: ComfyUI image generation support
#############################################################
import uvicorn
import argparse
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional

# Custom Imports
from narrative_chat import NarrativeChat
from world_snapshot_builder import build_frontend_snapshot
from services.comfyui_client import get_comfyui_client, ComfyUIClient

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = ""
native_model_path: Optional[str] = None  # Set via command line
comfyui_address: str = "127.0.0.1:8188"  # Default ComfyUI address

# Serve Static Files (CSS/JS)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>ERROR: index.html not found</h1>", status_code=500)
    return index_path.read_text(encoding="utf-8")

# --- INIT SIMULATION ---
@app.get("/api/init", response_class=JSONResponse)
async def init_sim(request: Request):
    global chat, current_mode, native_model_path
    mode = request.query_params.get("mode", "native" if native_model_path else "local")

    if mode != current_mode or chat is None:
        print(f"Initializing Simulation in {mode} mode...")
        try:
            if mode == "native":
                chat = NarrativeChat(mode="native", model_path=native_model_path)
            else:
                chat = NarrativeChat(mode=mode)
            chat.initialize()
            current_mode = mode
            narration = f"**[System: Initialized {mode.upper()} Mode]**\n\n{chat.last_narrated}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": str(e)}, status_code=500)
    else:
        chat.initialize()
        narration = f"**[System: Reset {mode.upper()} Mode]**\n\n{chat.last_narrated}"

    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({"narration": narration, "snapshot": snapshot})

# --- ACTION HANDLER ---
@app.post("/api/act", response_class=JSONResponse)
async def process_action(request: Request):
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started. Click 'Start'."}, status_code=400)
        
    data = await request.json()
    text = data.get("text", "").strip()
    
    reply = ""
    
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
        
        # --- FIXED: Event Reporting for WAIT ---
        if hasattr(chat.sim, 'scenario_buffer'):
            for e in chat.sim.scenario_buffer:
                reply += f"\n\n[SYSTEM EVENT]: {e}"
            chat.sim.scenario_buffer.clear() # Clear after reporting

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
            chat.sim.scenario_buffer.clear() # Clear after reporting

    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({"narration": reply, "snapshot": snapshot})


# --- COMFYUI IMAGE GENERATION ---
@app.get("/api/comfyui/status", response_class=JSONResponse)
async def comfyui_status():
    """Check if ComfyUI server is available."""
    client = get_comfyui_client(comfyui_address)
    available = client.is_server_available()
    return JSONResponse({
        "available": available,
        "address": comfyui_address,
        "current_workflow": client.current_workflow_name or None
    })


@app.get("/api/comfyui/workflows", response_class=JSONResponse)
async def list_workflows():
    """List available workflow files."""
    client = get_comfyui_client(comfyui_address)
    workflows = client.get_available_workflows()
    return JSONResponse({
        "workflows": workflows,
        "current": client.current_workflow_name or None
    })


@app.post("/api/comfyui/load", response_class=JSONResponse)
async def load_workflow(request: Request):
    """Load a workflow by name."""
    data = await request.json()
    workflow_name = data.get("workflow", "")

    if not workflow_name:
        return JSONResponse({"error": "No workflow specified"}, status_code=400)

    client = get_comfyui_client(comfyui_address)
    success = client.load_workflow(workflow_name)

    if success:
        return JSONResponse({
            "success": True,
            "workflow": workflow_name
        })
    else:
        return JSONResponse({
            "error": f"Failed to load workflow: {workflow_name}"
        }, status_code=400)


@app.post("/api/comfyui/upload", response_class=JSONResponse)
async def upload_workflow(request: Request):
    """Upload a new workflow JSON."""
    data = await request.json()
    name = data.get("name", "").strip()
    workflow_json = data.get("workflow")

    if not name or not workflow_json:
        return JSONResponse({"error": "Name and workflow required"}, status_code=400)

    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_").strip()
    if not safe_name:
        return JSONResponse({"error": "Invalid workflow name"}, status_code=400)

    workflows_dir = BASE_DIR / "workflows"
    workflows_dir.mkdir(exist_ok=True)

    workflow_path = workflows_dir / f"{safe_name}.json"

    try:
        import json
        with open(workflow_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_json, f, indent=2)

        return JSONResponse({
            "success": True,
            "name": safe_name,
            "path": str(workflow_path)
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/comfyui/generate", response_class=JSONResponse)
async def generate_image(request: Request):
    """Generate an image using ComfyUI."""
    data = await request.json()
    prompt = data.get("prompt", "")
    negative_prompt = data.get("negative_prompt", "")
    seed = data.get("seed", -1)
    workflow = data.get("workflow")  # Optional: switch workflow

    if not prompt:
        return JSONResponse({"error": "No prompt provided"}, status_code=400)

    client = get_comfyui_client(comfyui_address)

    # Check server
    if not client.is_server_available():
        return JSONResponse({
            "error": f"ComfyUI server not available at {comfyui_address}"
        }, status_code=503)

    # Load workflow if specified
    if workflow:
        if not client.load_workflow(workflow):
            return JSONResponse({
                "error": f"Failed to load workflow: {workflow}"
            }, status_code=400)

    # Check if we have a workflow
    if not client.current_workflow:
        workflows = client.get_available_workflows()
        if workflows:
            client.load_workflow(workflows[0])
        else:
            return JSONResponse({
                "error": "No workflow loaded. Upload a workflow first."
            }, status_code=400)

    # Generate
    try:
        image_bytes = client.generate_and_wait(prompt, negative_prompt, seed)

        if image_bytes:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return JSONResponse({
                "success": True,
                "image": image_base64,
                "workflow": client.current_workflow_name
            })
        else:
            return JSONResponse({
                "error": "Image generation failed"
            }, status_code=500)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/comfyui/portrait", response_class=JSONResponse)
async def generate_portrait(request: Request):
    """Generate a character portrait."""
    data = await request.json()
    character_name = data.get("name", "")
    description = data.get("description", "")
    scene = data.get("scene", "")
    seed = data.get("seed", -1)

    if not character_name:
        return JSONResponse({"error": "No character name"}, status_code=400)

    client = get_comfyui_client(comfyui_address)

    if not client.is_server_available():
        return JSONResponse({
            "error": f"ComfyUI server not available"
        }, status_code=503)

    if not client.current_workflow:
        workflows = client.get_available_workflows()
        if workflows:
            client.load_workflow(workflows[0])
        else:
            return JSONResponse({
                "error": "No workflow loaded"
            }, status_code=400)

    try:
        image_bytes = client.generate_portrait(character_name, description, scene, seed)

        if image_bytes:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            return JSONResponse({
                "success": True,
                "image": image_base64,
                "character": character_name
            })
        else:
            return JSONResponse({
                "error": "Portrait generation failed"
            }, status_code=500)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def main():
    global native_model_path, comfyui_address

    parser = argparse.ArgumentParser(description="Willow Creek Web UI")
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        help="Path to GGUF model file for native mode (e.g., models/unsloth.Q8_0.gguf)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--comfyui", "-c",
        type=str,
        default="127.0.0.1:8188",
        help="ComfyUI server address (default: 127.0.0.1:8188)"
    )
    args = parser.parse_args()

    # Set global model path for native mode
    if args.model:
        native_model_path = args.model
        if not Path(native_model_path).is_absolute():
            native_model_path = str(BASE_DIR / native_model_path)
        print(f"Native LLM mode enabled with model: {native_model_path}")

    # Set ComfyUI address
    comfyui_address = args.comfyui
    print(f"ComfyUI server: {comfyui_address}")

    print(f"Starting server at http://127.0.0.1:{args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()