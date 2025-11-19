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

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = "" 

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

# --- NEW ENDPOINTS FOR ENHANCED DASHBOARD ---

@app.get("/api/stats", response_class=JSONResponse)
async def get_stats():
    """Get real-time simulation statistics"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    stats = chat.sim.get_statistics()
    return JSONResponse(stats)

@app.get("/api/relationships", response_class=JSONResponse)
async def get_relationships():
    """Get relationship graph data"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    # Build relationship graph data
    nodes = []
    edges = []

    for npc in chat.sim.npcs[:20]:  # Limit to first 20 for performance
        nodes.append({
            "id": npc.full_name,
            "label": npc.full_name,
            "age": npc.age,
            "location": npc.current_location
        })

    # Get relationship edges
    for npc in chat.sim.npcs[:20]:
        for rel_name, rel_data in npc.relationships.items():
            if rel_name in [n.full_name for n in chat.sim.npcs[:20]]:
                affinity = rel_data.get('affinity', 0)
                if affinity > 20:  # Only show significant relationships
                    edges.append({
                        "from": npc.full_name,
                        "to": rel_name,
                        "value": affinity,
                        "title": f"Affinity: {affinity}"
                    })

    return JSONResponse({"nodes": nodes, "edges": edges})

@app.post("/api/checkpoint/save", response_class=JSONResponse)
async def save_checkpoint(request: Request):
    """Save simulation checkpoint"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    data = await request.json()
    name = data.get("name")
    description = data.get("description", "")

    try:
        path = chat.sim.save_checkpoint(name, description)
        return JSONResponse({"success": True, "path": path})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/checkpoint/load", response_class=JSONResponse)
async def load_checkpoint(request: Request):
    """Load simulation checkpoint"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    data = await request.json()
    name = data.get("name")

    try:
        chat.sim.load_checkpoint(name)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/checkpoint/list", response_class=JSONResponse)
async def list_checkpoints():
    """List all checkpoints"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    checkpoints = chat.sim.list_checkpoints()
    return JSONResponse({"checkpoints": checkpoints})

@app.get("/api/locations", response_class=JSONResponse)
async def get_locations():
    """Get NPCs grouped by location"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    loc_map = chat.sim._build_location_map()
    locations = {}
    for loc, npcs in loc_map.items():
        locations[loc] = [{"name": npc.full_name, "mood": npc.mood} for npc in npcs]

    return JSONResponse({"locations": locations})

# --- NEW ENDPOINTS FOR FEATURES 3, 5, 6 ---

@app.get("/api/analysis/summary", response_class=JSONResponse)
async def get_analysis_summary():
    """Get comprehensive analysis summary"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        # Get relationship analysis
        rel_analysis = chat.sim.analyzer.analyze_relationships()

        # Get behavior patterns
        behavior = chat.sim.analyzer.analyze_behavior_patterns()

        # Get social clusters
        clusters = chat.sim.analyzer.find_social_clusters()

        return JSONResponse({
            "relationships": rel_analysis,
            "behaviors": behavior,
            "social_clusters": clusters[:5]  # Top 5 clusters
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/analysis/full", response_class=JSONResponse)
async def get_full_analysis():
    """Get full comprehensive report"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        report = chat.sim.analyzer.generate_comprehensive_report()
        return JSONResponse(report)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/milestones/recent", response_class=JSONResponse)
async def get_recent_milestones():
    """Get recent milestones"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    days = 7  # Last 7 days by default
    try:
        milestones = chat.sim.milestones.get_recent_milestones(days=days, limit=50)

        # Convert to JSON-serializable format
        milestone_list = []
        for m in milestones:
            milestone_list.append({
                'type': m.milestone_type.value,
                'importance': m.importance.value,
                'day': m.day,
                'time': m.simulation_time,
                'primary_npc': m.primary_npc,
                'secondary_npcs': m.secondary_npcs,
                'description': m.description,
                'location': m.location,
                'emotional_impact': m.emotional_impact,
                'tags': m.tags
            })

        return JSONResponse({"milestones": milestone_list})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/milestones/stats", response_class=JSONResponse)
async def get_milestone_stats():
    """Get milestone statistics"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        stats = chat.sim.milestones.get_statistics()
        return JSONResponse(stats)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/milestones/npc/{npc_name}", response_class=JSONResponse)
async def get_npc_milestones(npc_name: str):
    """Get milestones for specific NPC"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        history = chat.sim.milestones.get_npc_history(npc_name, limit=20)

        milestone_list = []
        for m in history:
            milestone_list.append({
                'type': m.milestone_type.value,
                'importance': m.importance.value,
                'day': m.day,
                'time': m.simulation_time,
                'description': m.description,
                'location': m.location,
                'emotional_impact': m.emotional_impact
            })

        return JSONResponse({"npc": npc_name, "milestones": milestone_list})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/milestones/timeline", response_class=JSONResponse)
async def get_timeline():
    """Get full timeline of events"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        timeline = chat.sim.milestones.generate_timeline()
        # Limit to recent events for performance
        return JSONResponse({"timeline": timeline[-100:]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/personality/all", response_class=JSONResponse)
async def get_all_personalities():
    """Get personality profiles for all NPCs"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        profiles = []
        for npc in chat.sim.npcs[:20]:  # Limit to first 20 for performance
            profile = chat.sim.personality.get_personality_summary(npc)
            profiles.append(profile)

        return JSONResponse({"personalities": profiles})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/personality/{npc_name}", response_class=JSONResponse)
async def get_npc_personality(npc_name: str):
    """Get personality profile for specific NPC"""
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        npc = chat.sim.npc_dict.get(npc_name)
        if not npc:
            return JSONResponse({"error": f"NPC '{npc_name}' not found"}, status_code=404)

        profile = chat.sim.personality.get_personality_summary(npc)
        return JSONResponse(profile)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)