# Integration Instructions

## How to Integrate the New Game Systems with web_app.py

### Step 1: Add API Router to web_app.py

At the top of `web_app.py`, add:

```python
from api_endpoints import router as api_router
from game_manager import get_game_manager
```

After the existing app initialization (around line 19), add:

```python
# Include API router
app.include_router(api_router)

# Initialize game manager
game_manager = None
```

### Step 2: Initialize Game Manager on Simulation Init

In the `_init_sim_handler` function (around line 82), add:

```python
# After chat.initialize()
global game_manager
if game_manager is None:
    game_manager = get_game_manager(chat.sim)
    game_manager.initialize_character("Malcolm Newt", is_player=True)

    # Initialize all NPCs
    for npc in chat.sim.npcs:
        if npc.full_name != "Malcolm Newt":
            game_manager.initialize_character(npc.full_name)
```

### Step 3: Add UI Endpoint

Add this endpoint to `web_app.py`:

```python
@app.get("/ui", response_class=HTMLResponse)
async def serve_game_ui():
    """Serve the game systems UI"""
    ui_path = BASE_DIR / "ui_components.html"
    if not ui_path.exists():
        return HTMLResponse("<h1>UI not found</h1>", status_code=404)
    return ui_path.read_text(encoding="utf-8")
```

### Step 4: Update Simulation Tick

In the existing `/narrate` endpoint (around line 150), add:

```python
# After simulation tick
if game_manager and game_manager.sim:
    game_manager.simulate_day()
```

### Complete Modified web_app.py Example

```python
# At top of file
from api_endpoints import router as api_router
from game_manager import get_game_manager

# After app creation
app = FastAPI()
app.include_router(api_router)

# Global state
chat: Optional[NarrativeChat] = None
current_mode: str = ""
game_manager = None  # Add this

# New endpoint for UI
@app.get("/ui", response_class=HTMLResponse)
async def serve_game_ui():
    ui_path = BASE_DIR / "ui_components.html"
    if not ui_path.exists():
        return HTMLResponse("<h1>UI not found</h1>", status_code=404)
    return ui_path.read_text(encoding="utf-8")

# In _init_sim_handler
async def _init_sim_handler(mode: str):
    global chat, current_mode, ai_prompt_generator, game_manager

    # ... existing init code ...

    if mode != current_mode or chat is None:
        chat = NarrativeChat(mode=mode)
        chat.initialize()
        current_mode = mode

        # Initialize game manager HERE
        if game_manager is None:
            game_manager = get_game_manager(chat.sim)
            game_manager.initialize_character("Malcolm Newt", is_player=True)
            for npc in chat.sim.npcs:
                if npc.full_name != "Malcolm Newt":
                    game_manager.initialize_character(npc.full_name)

        # ... rest of init ...

# In /narrate endpoint
@app.post("/narrate")
async def narrate_action(request: Request):
    # ... existing narration code ...

    # Add after simulation tick
    if game_manager and game_manager.sim:
        game_manager.simulate_day()

    # ... return response ...
```

## Testing the Integration

### 1. Test Basic Imports

```bash
python3 -c "
from game_manager import get_game_manager
from api_endpoints import router
print('✓ All imports successful')
"
```

### 2. Test Game Manager Initialization

```bash
python3 -c "
from game_manager import get_game_manager
from simulation_v2 import WillowCreekSimulation

sim = WillowCreekSimulation()
game = get_game_manager(sim)
game.initialize_character('Malcolm Newt', is_player=True)

print('✓ Game manager initialized')
print(f'  Skills: {len(game.skills.character_skills)} characters')
print(f'  Inventory: Malcolm has ${game.inventory.get_inventory(\"Malcolm Newt\").money}')
"
```

### 3. Test API Endpoints

Start the server:
```bash
python web_app.py
```

Then test endpoints:
```bash
# Test portraits endpoint
curl http://localhost:8000/api/portraits

# Test statistics endpoint
curl http://localhost:8000/api/statistics

# Test town map endpoint
curl http://localhost:8000/api/town-map
```

### 4. Test UI

Open browser to:
- http://localhost:8000/ui

Should see:
- Portrait Gallery tab
- Town Map tab
- Statistics tab
- Relationships tab

## Troubleshooting

### "Module not found" errors

Make sure you're in the Willowcreek directory:
```bash
cd /path/to/Willowcreek
python web_app.py
```

### "game_manager is None" errors

Make sure to initialize after simulation:
```python
game_manager = get_game_manager(chat.sim)
```

### UI not showing data

1. Check console for JavaScript errors
2. Verify API endpoints return data:
   ```bash
   curl http://localhost:8000/api/statistics
   ```
3. Check that game_manager is initialized

### API returns empty arrays

The game manager needs NPCs initialized:
```python
for npc in chat.sim.npcs:
    game_manager.initialize_character(npc.full_name)
```

## Next Steps

After integration:

1. **Add game actions to narrative** - Detect player actions in user input and trigger appropriate game_manager methods

2. **Display memories in UI** - Show recent memories in the narrative panel

3. **Add NPC interaction buttons** - Click on NPC portraits to talk, flirt, give gifts

4. **Show skill XP in notifications** - Display "Charisma +5 XP!" messages

5. **Create event calendar** - Display upcoming social events

6. **Add inventory UI** - Allow players to use items from inventory

7. **Show active gossip** - Display town gossip in sidebar

## Full Example: Adding "Talk" Action

```python
# In /narrate endpoint, before calling chat.narrate()

user_input_lower = user_input.lower()

# Detect "talk to X" action
if "talk to" in user_input_lower or "speak with" in user_input_lower:
    # Extract NPC name (simple version)
    for npc in chat.sim.npcs:
        if npc.full_name.lower() in user_input_lower:
            xp_gained = game_manager.talk_to_npc("Malcolm Newt", npc.full_name)

            # Add notification to narration
            if xp_gained:
                narration += f"\n\n**[{', '.join(xp_gained)}]**"

            break
```

This gives players XP for talking to NPCs and shows level-up messages!
