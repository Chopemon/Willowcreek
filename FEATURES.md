# Willow Creek - New Features Guide

This document describes the newly added features to your Willow Creek simulation.

## 🆕 Feature 1: Save/Load System (Checkpoint Manager)

A complete checkpoint system that allows you to save and restore simulation states at any point.

### Features

- **Compressed Storage**: Checkpoints are saved with gzip compression for efficiency
- **Metadata Tracking**: Each checkpoint includes simulation time, NPC count, and descriptions
- **Quick Save/Load**: 10 quick-save slots for rapid saving/loading
- **Version Control**: Automatic versioning for future compatibility

### Usage

#### In Python Code

```python
from simulation_v2 import WillowCreekSimulation

# Create simulation
sim = WillowCreekSimulation(num_npcs=0)

# Run for a while
sim.run(num_steps=100, time_step_hours=1.0)

# Save checkpoint with custom name
sim.save_checkpoint(
    name="my_checkpoint",
    description="After 100 steps"
)

# Quick save to slot 1
sim.quick_save(slot=1)

# Continue simulation
sim.run(num_steps=100, time_step_hours=1.0)

# Load previous checkpoint
sim.load_checkpoint("my_checkpoint")

# Or quick load
sim.quick_load(slot=1)

# List all checkpoints
checkpoints = sim.list_checkpoints()
for ckpt in checkpoints:
    print(f"{ckpt['checkpoint_name']}: {ckpt['simulation_time']}")
```

#### Via Web Dashboard

1. Start the enhanced web dashboard (see below)
2. Navigate to the "💾 Saves" tab
3. Enter a checkpoint name and optional description
4. Click "Save" to create a checkpoint
5. Click "Load" on any checkpoint to restore that state

### Storage Location

Checkpoints are stored in the `checkpoints/` directory:
- `checkpoints/checkpoint_name.ckpt` - Compressed checkpoint data
- `checkpoints/checkpoints_index.json` - Metadata index

### What Gets Saved

- Simulation time and day count
- All NPC states (needs, relationships, locations, etc.)
- World state (weather, etc.)
- Current simulation step
- System buffers and flags

---

## 🎨 Feature 2: Enhanced Web Dashboard

A completely redesigned web interface with real-time monitoring and visualization.

### Features

#### Real-Time Statistics
- Live updates every 5 seconds
- Visual stat cards for key metrics
- Animated bar chart showing needs levels
- Tracks: Day, Time, NPCs, Horny, Lonely, Secrets, Weather, Season

#### NPC Location Tracking
- See where all NPCs are in real-time
- Grouped by location with NPC moods
- Auto-refreshes when you interact

#### Relationship Network Graph
- Visual network of NPC relationships
- Interactive graph visualization
- Shows relationship strength through line thickness
- Displays affinity levels on hover

#### Save/Load Integration
- Full checkpoint management from the web UI
- Create, load, and view checkpoints
- Browse checkpoint history with timestamps

### How to Use

#### Starting the Enhanced Dashboard

1. **Option A: Replace the default dashboard**
   ```bash
   # Backup original
   mv index.html index_old.html
   mv static/script.js static/script_old.js
   mv static/styles.css static/styles_old.css

   # Use enhanced version
   mv index_enhanced.html index.html
   ```

2. **Option B: Access directly** (recommended for testing)
   - The enhanced dashboard is available at: `/index_enhanced.html`
   - Just navigate to: `http://127.0.0.1:8000/index_enhanced.html`

3. **Start the server**
   ```bash
   python web_app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:8000
   ```
   or
   ```
   http://127.0.0.1:8000/index_enhanced.html
   ```

#### Using the Dashboard

1. **Select Mode**: Choose between Local LLM or OpenRouter
2. **Start Simulation**: Click "Start Simulation" to initialize
3. **Interact**: Type actions in the chat interface
4. **Monitor**: Switch between tabs to view different data:
   - 📊 **Stats**: Real-time statistics and charts
   - 📍 **Locations**: Where NPCs are located
   - 🔗 **Network**: Relationship graph visualization
   - 💾 **Saves**: Checkpoint management

#### Keyboard Shortcuts

- `Enter`: Send action
- Type `wait 1` to advance time 1 hour
- Type `debug` to toggle debug mode

### New API Endpoints

The enhanced dashboard adds these API endpoints:

```
GET  /api/stats              - Get real-time statistics
GET  /api/locations          - Get NPC locations
GET  /api/relationships      - Get relationship graph data
GET  /api/checkpoint/list    - List all checkpoints
POST /api/checkpoint/save    - Save a checkpoint
POST /api/checkpoint/load    - Load a checkpoint
```

---

## 📊 Technical Details

### Checkpoint File Format

Checkpoints use Python's `pickle` with gzip compression:

```python
{
    'metadata': {
        'checkpoint_name': str,
        'created_at': str (ISO format),
        'simulation_time': str,
        'total_days': int,
        'num_npcs': int,
        'version': str,
        'description': str
    },
    'time_system': {...},
    'world_state': {...},
    'npcs': [...],
    'systems': {...},
    'current_step': int
}
```

### Dashboard Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js for bar charts
- **Network Graph**: Vis.js Network for relationship visualization
- **Backend**: FastAPI with async endpoints
- **Communication**: RESTful JSON API

---

## 🚀 Quick Start Examples

### Example 1: Long Simulation with Checkpoints

```python
from simulation_v2 import WillowCreekSimulation

sim = WillowCreekSimulation(num_npcs=0)

# Save at the start
sim.quick_save(slot=1)

# Run for 100 days
for day in range(1, 101):
    sim.run(num_steps=24, time_step_hours=1.0)

    # Save every 10 days
    if day % 10 == 0:
        sim.save_checkpoint(
            name=f"day_{day}",
            description=f"Checkpoint at day {day}"
        )
        print(f"Saved checkpoint: day_{day}")

# List all checkpoints
print("\nAll checkpoints:")
for ckpt in sim.list_checkpoints():
    print(f"  - {ckpt['checkpoint_name']} ({ckpt['total_days']} days)")
```

### Example 2: Interactive Dashboard Session

1. Start the web server
2. Open http://127.0.0.1:8000/index_enhanced.html
3. Click "Start Simulation"
4. Type: `wait 24` to advance one day
5. Switch to "📊 Stats" tab to see live metrics
6. Switch to "🔗 Network" tab to see relationship graph
7. Switch to "💾 Saves" tab
8. Save a checkpoint named "first_day"
9. Continue interacting
10. Load "first_day" to return to that state

---

## 🐛 Troubleshooting

### Checkpoint Issues

**Problem**: "Checkpoint not found"
- Check that the checkpoint name matches exactly (case-sensitive)
- Verify `checkpoints/` directory exists

**Problem**: "Failed to load checkpoint"
- The checkpoint may be from an incompatible version
- Try creating a new checkpoint instead

### Dashboard Issues

**Problem**: Dashboard not loading
- Ensure the server is running: `python web_app.py`
- Check the console for errors
- Try a different browser

**Problem**: Stats not updating
- The simulation must be started first
- Check browser console for JavaScript errors
- Refresh the page

**Problem**: Network graph not showing
- Ensure NPCs have relationships defined
- Only relationships with affinity > 20 are shown
- Limited to first 20 NPCs for performance

### Dependencies

If you encounter import errors, install dependencies:

```bash
pip install numpy pandas networkx matplotlib seaborn plotly fastapi uvicorn pydantic
```

---

## 📝 Future Enhancements

Potential improvements for the future:

- [ ] Export checkpoints to cloud storage
- [ ] Checkpoint comparison tool
- [ ] Auto-save every N steps
- [ ] Checkpoint branching (save game trees)
- [ ] More detailed relationship graph filters
- [ ] Time-series charts for needs over time
- [ ] Event timeline visualization
- [ ] NPC detail popup on graph click

---

## 🤝 Contributing

Want to extend these features? Here are some ideas:

1. **Add more visualization types** (Edit `index_enhanced.html`, `script_enhanced.js`)
2. **Enhance checkpoint metadata** (Edit `core/checkpoint_manager.py`)
3. **Add new API endpoints** (Edit `web_app.py`)
4. **Create checkpoint export formats** (JSON, CSV, etc.)

---

## 📄 License

These features are part of your Willow Creek project. Use them however you like!

---

**Enjoy your enhanced simulation! 🎉**
