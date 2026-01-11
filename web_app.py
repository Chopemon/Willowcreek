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
from narrative_chat import NarrativeChat, CONFIG
from world_snapshot_builder import build_frontend_snapshot

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = ""
current_model: str = ""

# Serve Static Files (CSS/JS)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>ERROR: index.html not found</h1>", status_code=500)
    return index_path.read_text(encoding="utf-8")

def list_local_models() -> list[str]:
    models_dir = BASE_DIR / "models"
    if not models_dir.exists():
        return []
    models: list[str] = []
    for item in sorted(models_dir.iterdir(), key=lambda path: path.name.lower()):
        if item.name.startswith("."):
            continue
        if item.is_dir() or item.is_file():
            models.append(item.name)
    return models

@app.get("/api/models", response_class=JSONResponse)
async def list_models(request: Request):
    mode = request.query_params.get("mode", "local")
    if mode != "local":
        return JSONResponse({"models": [], "default_model": CONFIG.get(mode, {}).get("model_name", "")})
    return JSONResponse({
        "models": list_local_models(),
        "default_model": CONFIG["local"]["model_name"]
    })

# --- INIT SIMULATION ---
@app.get("/api/init", response_class=JSONResponse)
async def init_sim(request: Request):
    global chat, current_mode, current_model
    mode = request.query_params.get("mode", "openrouter")
    model = request.query_params.get("model", "").strip()
    
    if mode != current_mode or chat is None or (model and model != current_model):
        mode_label = f"{mode}"
        if model:
            mode_label += f" ({model})"
        print(f"Initializing Simulation in {mode_label} mode...")
        try:
            chat = NarrativeChat(mode=mode, model_name=model or None)
            chat.initialize()
            current_mode = mode
            current_model = chat.model_name
            narration = f"**[System: Initialized {mode.upper()} Mode ({chat.model_name})]**\n\n{chat.last_narrated}"
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
    else:
        chat.initialize()
        narration = f"**[System: Reset {mode.upper()} Mode ({chat.model_name})]**\n\n{chat.last_narrated}"
            
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

if __name__ == "__main__":
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
