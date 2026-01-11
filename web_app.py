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
from services.scene_image_generator import SceneAnalyzer, ImagePromptGenerator, AIPromptGenerator
from services.npc_portrait_generator import NPCPortraitGenerator
from api_endpoints import router as api_router
from game_manager import get_game_manager
import os

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# Include API router for game systems
app.include_router(api_router)

# Global State
chat: Optional[NarrativeChat] = None
current_mode: str = ""
game_manager_instance = None

# Image Generation Services
COMFYUI_ENABLED = os.getenv("COMFYUI_ENABLED", "false").lower() == "true"
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")
AI_PROMPTS_ENABLED = os.getenv("AI_PROMPTS_ENABLED", "true").lower() == "true"  # AI-based prompt generation
PORTRAITS_ENABLED = os.getenv("PORTRAITS_ENABLED", "true").lower() == "true"  # NPC portrait generation

comfyui_client = ComfyUIClient(base_url=COMFYUI_URL) if COMFYUI_ENABLED else None
scene_analyzer = SceneAnalyzer()

# Initialize both prompt generators (will use one based on config)
template_prompt_generator = ImagePromptGenerator()
ai_prompt_generator = None  # Will be initialized based on LLM mode

# Initialize portrait generator
portrait_generator = NPCPortraitGenerator(comfyui_client) if (COMFYUI_ENABLED and PORTRAITS_ENABLED) else None

print(f"[ImageGen] AI-based prompt generation: {'ENABLED' if AI_PROMPTS_ENABLED else 'DISABLED'}")
print(f"[PortraitGen] NPC portraits: {'ENABLED' if PORTRAITS_ENABLED and COMFYUI_ENABLED else 'DISABLED'}")

# Serve Static Files (CSS/JS)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Serve Generated Images
generated_images_dir = BASE_DIR / "static" / "generated_images"
generated_images_dir.mkdir(exist_ok=True)
app.mount("/generated_images", StaticFiles(directory=generated_images_dir), name="generated_images")

# Serve NPC Portraits
npc_portraits_dir = BASE_DIR / "static" / "npc_portraits"
npc_portraits_dir.mkdir(exist_ok=True)
app.mount("/npc_portraits", StaticFiles(directory=npc_portraits_dir), name="npc_portraits")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    # Serve enhanced dashboard
    index_path = BASE_DIR / "index_enhanced.html"
    if not index_path.exists():
        return HTMLResponse("<h1>ERROR: index_enhanced.html not found</h1>", status_code=500)
    return index_path.read_text(encoding="utf-8")

@app.get("/ui", response_class=HTMLResponse)
async def serve_game_systems_ui():
    """Serve the game systems UI (portraits, map, stats, relationships)"""
    ui_path = BASE_DIR / "ui_components.html"
    if not ui_path.exists():
        return HTMLResponse("<h1>ERROR: ui_components.html not found</h1>", status_code=404)
    return ui_path.read_text(encoding="utf-8")

# --- INIT SIMULATION (supports both GET and POST) ---
async def _init_sim_handler(mode: str):
    """Shared handler for init simulation"""
    global chat, current_mode, ai_prompt_generator, game_manager_instance

    print(f"\n[WebApp] ===== INIT REQUEST =====")
    print(f"[WebApp] Requested mode: {mode}")
    print(f"[WebApp] Current mode: {current_mode}")
    print(f"[WebApp] ==========================\n")

    try:
        if mode != current_mode or chat is None:
            print(f"Initializing Simulation in {mode} mode...")
            chat = NarrativeChat(mode=mode)
            chat.initialize()
            current_mode = mode

            # Initialize AI prompt generator with matching mode
            if AI_PROMPTS_ENABLED:
                ai_prompt_generator = AIPromptGenerator(mode=mode)
                print(f"[ImageGen] Initialized AI prompt generator in {mode} mode")

            narration = f"**[System: Initialized {mode.upper()} Mode]**\n\n{getattr(chat, 'last_narrated', 'Starting simulation...')}"
        else:
            chat.initialize()
            narration = f"**[System: Reset {mode.upper()} Mode]**\n\n{getattr(chat, 'last_narrated', 'Resetting simulation...')}"

        # Initialize game manager with all 17 systems
        if chat and chat.sim and game_manager_instance is None:
            game_manager_instance = get_game_manager(chat.sim)
            game_manager_instance.initialize_character("Malcolm Newt", is_player=True)
            print(f"[WebApp] Game manager initialized with {len(chat.sim.npcs)} NPCs")

        snapshot = build_frontend_snapshot(chat.sim if chat else None, chat.malcolm if chat else None)
        return JSONResponse({"narration": narration, "snapshot": snapshot, "images": [], "portraits": []})
    except Exception as e:
        import traceback
        print(f"[WebApp] ERROR during initialization:")
        print(traceback.format_exc())
        return JSONResponse({"error": f"Initialization failed: {str(e)}"}, status_code=500)

def generate_image_prompts(scene_context, narrative_text: Optional[str] = None):
    """
    Generate image prompts using either AI or template-based method.

    Args:
        scene_context: SceneContext object
        narrative_text: Optional narrative text for AI-based generation

    Returns:
        Tuple of (positive_prompt, negative_prompt)
    """
    if AI_PROMPTS_ENABLED and ai_prompt_generator and narrative_text:
        # Use AI to generate prompts from narrative
        return ai_prompt_generator.generate_prompt_from_narrative(narrative_text, scene_context)
    else:
        # Use template-based generation
        return template_prompt_generator.generate_prompt(scene_context)


async def generate_npc_portraits(narrative_text: str):
    """
    Detect NPCs in narrative and generate portraits for them.
    Generates both headshot (close-up) and full_body portraits.

    Args:
        narrative_text: The narrative text to analyze

    Returns:
        List of portrait dictionaries with {name, headshot_url, full_body_url}
    """
    if not portrait_generator or not chat:
        return []

    # Detect which NPCs are mentioned
    mentioned_npcs = portrait_generator.detect_npcs_in_text(narrative_text, chat.sim.npc_dict)

    if not mentioned_npcs:
        return []

    print(f"[PortraitGen] Detected NPCs in narrative: {', '.join(mentioned_npcs)}")

    portraits = []
    for npc_name in mentioned_npcs:
        # Get NPC data - check both main NPC dict and generic NPCs
        npc = chat.sim.npc_dict.get(npc_name)
        if not npc:
            print(f"[PortraitGen] NPC {npc_name} not found in roster, skipping")
            continue

        # Prepare NPC data for generation
        # Check both occupation and affiliation fields
        occupation = ''
        if hasattr(npc, 'occupation') and npc.occupation:
            occupation = npc.occupation
        elif hasattr(npc, 'affiliation') and npc.affiliation:
            occupation = npc.affiliation

        npc_data = {
            'gender': npc.gender if hasattr(npc, 'gender') else 'person',
            'age': npc.age if hasattr(npc, 'age') else 25,
            'traits': npc.coreTraits if hasattr(npc, 'coreTraits') else [],
            'quirk': npc.quirk if hasattr(npc, 'quirk') else '',
            'appearance': npc.appearance if hasattr(npc, 'appearance') else '',
            'occupation': occupation
        }

        # Generate or get BOTH portrait types
        headshot_url = portrait_generator.get_portrait_url(npc_name, "headshot")
        full_body_url = portrait_generator.get_portrait_url(npc_name, "full_body")

        # Generate headshot if missing
        if not headshot_url:
            print(f"[PortraitGen] Generating headshot for {npc_name}")
            headshot_url = await portrait_generator.generate_portrait(npc_name, npc_data, "headshot")

        # Generate full body if missing
        if not full_body_url:
            print(f"[PortraitGen] Generating full_body for {npc_name}")
            full_body_url = await portrait_generator.generate_portrait(npc_name, npc_data, "full_body")

        if headshot_url or full_body_url:
            portraits.append({
                "name": npc_name,
                "headshot": headshot_url,
                "full_body": full_body_url
            })

    return portraits


@app.get("/api/init", response_class=JSONResponse)
async def init_sim_get(request: Request):
    mode = request.query_params.get("mode", "openrouter")
    return await _init_sim_handler(mode)

@app.post("/api/init", response_class=JSONResponse)
async def init_sim_post(request: Request):
    try:
        data = await request.json()
        mode = data.get("mode", "openrouter")
    except:
        mode = request.query_params.get("mode", "openrouter")
    return await _init_sim_handler(mode)

# --- ACTION HANDLER ---
@app.post("/api/act", response_class=JSONResponse)
async def process_action(request: Request):
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started. Click 'Start'."}, status_code=400)

    data = await request.json()
    # Support both 'text' (old) and 'action' (new enhanced dashboard)
    text = data.get("action") or data.get("text", "")
    text = text.strip()
    
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
                    # Wait events don't have narrative, use template-based prompts
                    positive_prompt, negative_prompt = generate_image_prompts(scene_context)

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

        # 1.5. DETECT LOCATION CHANGES from user action (pre-narrative)
        text_lower = text.lower()
        location_keywords = {
            'diner': 'Diner',
            'coffee shop': 'Coffee Shop',
            'cafe': 'Coffee Shop',
            'park': 'Park',
            'bar': 'Bar',
            'pub': 'Bar',
            'gym': 'Gym',
            'library': 'Library',
            'town square': 'Town Square',
            'square': 'Town Square',
            'general store': 'General Store',
            'store': 'General Store',
            'shop': 'General Store',
            'high school': 'Willow Creek High School',
            'school': 'Willow Creek High School',
            'home': 'Home',
            'house': 'Home',
            'apartment': 'Home',
            'my place': 'Home'
        }

        # Check if user is going somewhere (expanded detection)
        movement_phrases = ['go to', 'head to', 'walk to', 'drive to', 'at the',
                           'enter', 'arrive at', 'visit', 'stop by', 'i walk']
        if any(phrase in text_lower for phrase in movement_phrases):
            for keyword, location in location_keywords.items():
                if keyword in text_lower:
                    chat.malcolm.current_location = location
                    print(f"[Location] Malcolm moved to: {location}")
                    break

        # 2. Generate narrative
        reply = chat.narrate(text)

        # 2.5 DETECT LOCATION from AI response (post-narrative)
        reply_lower = reply.lower()
        for keyword, location in location_keywords.items():
            # Look for contextual clues in the narrative
            if any(phrase in reply_lower for phrase in [
                f'walked into the {keyword}',
                f'entered the {keyword}',
                f'inside the {keyword}',
                f'at the {keyword}',
                f'in the {keyword}',
                f"the {keyword}'s",
                f'{keyword} door',
                f'{keyword} window'
            ]):
                if chat.malcolm.current_location != location:
                    chat.malcolm.current_location = location
                    print(f"[Location] Detected from narrative: Malcolm is at {location}")
                break
        
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

        # 5. Events are now in scenario_buffer and will be passed to narrator via world snapshot
        # If there are events, generate a follow-up narrative incorporating them
        if hasattr(chat.sim, 'scenario_buffer') and chat.sim.scenario_buffer:
            # Generate additional narrative to incorporate the events
            follow_up_prompt = "Continue the scene, incorporating the recent dramatic events."
            follow_up_narrative = chat.narrate(follow_up_prompt)
            reply += "\n\n" + follow_up_narrative

        # 6. GENERATE IMAGES for interesting scenes
        if COMFYUI_ENABLED and comfyui_client and hasattr(chat.sim, 'scenario_buffer'):
            for event_text in chat.sim.scenario_buffer:
                # Analyze if this event deserves an image
                scene_context = scene_analyzer.analyze_scene(event_text, chat.sim, chat.malcolm)

                if scene_context and scene_context.priority >= 7:  # High priority scenes only
                    print(f"[ImageGen] Generating image for: {scene_context.activity}")

                    # Generate image prompt (with AI using narrative text if enabled)
                    positive_prompt, negative_prompt = generate_image_prompts(scene_context, narrative_text=reply)

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

    # Generate NPC portraits for mentioned characters
    npc_portraits = await generate_npc_portraits(reply) if portrait_generator else []

    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({
        "narration": reply,
        "snapshot": snapshot,
        "images": generated_images,  # Scene images
        "portraits": npc_portraits  # NPC portraits
    })

# --- WAIT ENDPOINT ---
@app.post("/api/wait", response_class=JSONResponse)
async def wait_time(request: Request):
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started. Click 'Start'."}, status_code=400)

    data = await request.json()
    hours = data.get("hours", 1)

    generated_images = []

    # Advance time
    chat.advance_time(hours)
    reply = f". {hours} hours pass ."

    # If events occurred during wait, generate narrative for them
    if hasattr(chat.sim, 'scenario_buffer') and chat.sim.scenario_buffer:
        # Generate narrative incorporating the events
        event_prompt = f"Narrate what happened during the {hours} hour wait, incorporating the recent events."
        event_narrative = chat.narrate(event_prompt)
        reply += "\n\n" + event_narrative

    # Generate images for wait events
    if COMFYUI_ENABLED and comfyui_client and hasattr(chat.sim, 'scenario_buffer'):
        for event_text in chat.sim.scenario_buffer:
            scene_context = scene_analyzer.analyze_scene(event_text, chat.sim, chat.malcolm)

            if scene_context and scene_context.priority >= 7:
                print(f"[ImageGen] Generating image for wait event: {scene_context.activity}")
                # Wait events don't have narrative, use template-based prompts
                positive_prompt, negative_prompt = generate_image_prompts(scene_context)

                try:
                    image_url = await comfyui_client.generate_image(
                        prompt=positive_prompt,
                        negative_prompt=negative_prompt,
                        width=832, height=1216, steps=20, cfg_scale=7.0
                    )

                    if image_url:
                        generated_images.append({
                            "url": image_url,
                            "caption": scene_context.activity,
                            "scene_type": scene_context.scene_type
                        })
                except Exception as e:
                    print(f"[ImageGen] Error: {e}")

    # Clear buffer
    if hasattr(chat.sim, 'scenario_buffer'):
        chat.sim.scenario_buffer.clear()

    snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
    return JSONResponse({
        "narration": reply,
        "snapshot": snapshot,
        "images": generated_images
    })

# --- MANUAL IMAGE GENERATION ENDPOINT ---
@app.post("/api/generate-image", response_class=JSONResponse)
async def generate_image_manual():
    """Manually trigger image generation for the current scene"""
    global chat
    if chat is None or chat.sim is None or chat.malcolm is None:
        return JSONResponse({"error": "Sim not started. Click 'Start'."}, status_code=400)

    if not COMFYUI_ENABLED or not comfyui_client:
        return JSONResponse({
            "success": False,
            "error": "ComfyUI is not enabled. Set COMFYUI_ENABLED=true environment variable."
        })

    generated_images = []

    try:
        # Get current scene context
        snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)
        current_context = f"Malcolm is at {snapshot.get('location', 'Unknown')} at {snapshot.get('time', 'unknown time')}. "

        # Use the last narrative if available, or build a basic scene description
        if hasattr(chat, 'last_narrative') and chat.last_narrative:
            scene_text = chat.last_narrative
        else:
            scene_text = current_context + f"Malcolm ({chat.malcolm.age} years old) is here."

        # Analyze the scene
        scene_context = scene_analyzer.analyze_scene(scene_text, chat.sim, chat.malcolm)

        if not scene_context:
            # Force a basic scene if analyzer returns None
            from services.scene_image_generator import SceneContext
            scene_context = SceneContext(
                scene_type="general",
                priority=5,
                characters=[chat.malcolm.full_name],
                location=snapshot.get('location', 'Unknown'),
                time_of_day=chat.sim.time.time_of_day if hasattr(chat.sim, 'time') else "day",
                weather=chat.sim.time.season if hasattr(chat.sim.time, 'season') else "clear",
                mood="neutral",
                explicit_level=0,
                activity="current scene",
                raw_event=scene_text
            )

        print(f"[ImageGen] Manual generation: {scene_context.activity} at {scene_context.location}")

        # Generate prompts (could use last narrative, but safer to use templates for manual generation)
        positive_prompt, negative_prompt = generate_image_prompts(scene_context, narrative_text=chat.last_narrated if chat else None)

        # Generate image
        image_url = await comfyui_client.generate_image(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            width=832, height=1216, steps=20, cfg_scale=7.0
        )

        if image_url:
            generated_images.append({
                "url": image_url,
                "caption": scene_context.activity,
                "scene_type": scene_context.scene_type
            })
            print(f"[ImageGen] Successfully generated image: {image_url}")
            return JSONResponse({
                "success": True,
                "images": generated_images
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "Image generation returned no URL"
            })

    except Exception as e:
        print(f"[ImageGen] Manual generation error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

# --- SNAPSHOT ENDPOINT ---
@app.get("/api/snapshot", response_class=JSONResponse)
async def get_snapshot():
    global chat
    if chat is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    # build_frontend_snapshot handles None gracefully, but check anyway
    snapshot = build_frontend_snapshot(chat.sim if chat else None, chat.malcolm if chat else None)
    return JSONResponse(snapshot)

# --- LOCATIONS ENDPOINT ---
@app.get("/api/locations", response_class=JSONResponse)
async def get_locations():
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    # Build location map
    locations = {}
    for npc in chat.sim.npcs:
        loc = getattr(npc, "current_location", "Unknown")
        if loc not in locations:
            locations[loc] = []
        locations[loc].append(npc.full_name)

    malcolm_location = getattr(chat.malcolm, "current_location", "Unknown")

    return JSONResponse({
        "locations": locations,
        "malcolm_location": malcolm_location
    })

# --- NPCS ENDPOINT ---
@app.get("/api/npcs", response_class=JSONResponse)
async def get_npcs():
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    npcs_data = []
    for npc in chat.sim.npcs:
        npcs_data.append({
            "name": npc.full_name,
            "age": getattr(npc, "age", None),
            "occupation": getattr(npc, "occupation", "Unknown"),
            "location": getattr(npc, "current_location", "Unknown")
        })

    return JSONResponse({"npcs": npcs_data})

# --- TIMELINE ENDPOINT ---
@app.get("/api/timeline", response_class=JSONResponse)
async def get_timeline():
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    # Check if timeline exists
    events = []
    if hasattr(chat.sim, 'event_log'):
        events = chat.sim.event_log

    return JSONResponse({"events": events})

# --- ANALYSIS ENDPOINT ---
@app.get("/api/analysis", response_class=JSONResponse)
async def get_analysis():
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    # Calculate relationship metrics
    relationships = chat.sim.relationships.get_all_relationships()
    total_relationships = len(relationships)

    avg_affinity = 0
    if relationships:
        affinities = [rel.get('affinity', 0) for rel in relationships]
        avg_affinity = sum(affinities) / len(affinities)

    # Time elapsed
    time_elapsed = f"{chat.sim.current_hour:02d}:{chat.sim.current_minute:02d}"

    # Activity tracking (simplified)
    total_actions = 0
    top_activity = "N/A"

    return JSONResponse({
        "total_relationships": total_relationships,
        "avg_affinity": avg_affinity,
        "total_actions": total_actions,
        "top_activity": top_activity,
        "time_elapsed": time_elapsed,
        "total_npcs": len(chat.sim.npcs)
    })

# --- SAVE CHECKPOINT ---
@app.post("/api/save", response_class=JSONResponse)
async def save_checkpoint():
    global chat
    if chat is None or chat.sim is None:
        return JSONResponse({"error": "Sim not started"}, status_code=400)

    try:
        import pickle
        checkpoint_path = BASE_DIR / "checkpoint.pkl"

        with open(checkpoint_path, 'wb') as f:
            pickle.dump({
                "sim": chat.sim,
                "malcolm": chat.malcolm,
                "mode": current_mode
            }, f)

        print(f"[Save] Checkpoint saved to {checkpoint_path}")
        return JSONResponse({"success": True, "message": "Checkpoint saved successfully"})

    except Exception as e:
        print(f"[Save] Error: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# --- LOAD CHECKPOINT ---
@app.post("/api/load", response_class=JSONResponse)
async def load_checkpoint():
    global chat, current_mode

    try:
        import pickle
        checkpoint_path = BASE_DIR / "checkpoint.pkl"

        if not checkpoint_path.exists():
            return JSONResponse({"success": False, "error": "No checkpoint found"}, status_code=404)

        with open(checkpoint_path, 'rb') as f:
            data = pickle.load(f)

        # Restore state
        if chat is None:
            chat = NarrativeChat(mode=data["mode"])

        chat.sim = data["sim"]
        chat.malcolm = data["malcolm"]
        current_mode = data["mode"]

        snapshot = build_frontend_snapshot(chat.sim, chat.malcolm)

        print(f"[Load] Checkpoint loaded from {checkpoint_path}")
        return JSONResponse({
            "success": True,
            "message": "Checkpoint loaded successfully",
            "snapshot": snapshot
        })

    except Exception as e:
        print(f"[Load] Error: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# --- RESET SIMULATION ---
@app.post("/api/reset", response_class=JSONResponse)
async def reset_simulation():
    global chat, current_mode

    chat = None
    current_mode = ""

    return JSONResponse({"success": True, "message": "Simulation reset"})

if __name__ == "__main__":
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
