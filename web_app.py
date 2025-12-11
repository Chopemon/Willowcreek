#############################################################
# web_app.py — FINAL FIXED VERSION (Event Reporting)
# UPDATED: Native LLM support added
#############################################################
import uvicorn
import argparse
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional

# Custom Imports
from narrative_chat import NarrativeChat
from world_snapshot_builder import build_frontend_snapshot

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = ""
native_model_path: Optional[str] = None  # Set via command line 

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

def main():
    global native_model_path

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
    args = parser.parse_args()

    # Set global model path for native mode
    if args.model:
        native_model_path = args.model
        if not Path(native_model_path).is_absolute():
            native_model_path = str(BASE_DIR / native_model_path)
        print(f"Native LLM mode enabled with model: {native_model_path}")

    print(f"Starting server at http://127.0.0.1:{args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()