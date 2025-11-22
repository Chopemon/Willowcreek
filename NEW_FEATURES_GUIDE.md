# New Features Guide - Willow Creek Game Systems

## 🎮 How to Access the New Features

All 17 new game systems are now integrated and ready to use!

### Main Game Interface
**URL**: `http://127.0.0.1:8000/`
- The standard narrative interface
- All new game systems are active in the background
- Enhanced AI narrator sees all game data (skills, inventory, reputation, memories, etc.)

### Game Systems UI Dashboard
**URL**: `http://127.0.0.1:8000/ui`

This is a **brand new interface** with 4 tabs:

#### 📸 **Tab 1: Portrait Gallery**
- See all NPC portraits in a grid layout
- View relationship bars (Friendship & Romance)
- See relationship status with each NPC
- Click to see details (age, occupation, times talked)
- **Endpoint**: `/api/portraits`

#### 🗺️ **Tab 2: Town Map**
- Interactive town map showing all locations
- See which NPCs are at each location in real-time
- Visual markers for places with NPCs
- Hover to see occupants
- **Endpoint**: `/api/town-map`

#### 📊 **Tab 3: Statistics Dashboard**
- **Economy**: Money, inventory items
- **Skills**: Your top 8 skills with XP and levels
- **Memories**: Total memory count
- **Social**: Total relationships, active gossip
- **Achievements**: Track your progression
- **Endpoint**: `/api/statistics`

#### 💕 **Tab 4: Relationships**
- Detailed view of all active relationships
- Shows friendship level, romance level, trust, respect
- Attraction and chemistry scores
- Relationship status (Stranger → Acquaintance → Friend → Dating → etc.)
- **Endpoint**: `/api/relationships`

---

## 🎯 The 17 New Game Systems

All these systems are **automatically active** in your simulation:

### Social Systems
1. **Skill System** (8 skills: Charisma, Athletic, Intelligence, Creativity, Cooking, Mechanical, Seduction, Empathy)
2. **Inventory System** (Items, gifts, consumables, money)
3. **Memory System** (Tracks events, interactions, importance levels)
4. **Relationship System** (9 statuses from Stranger to Married)
5. **Reputation System** (Town-wide reputation, 13 traits, gossip spreading)
6. **Dialogue System** (Mood-aware, context-sensitive responses)

### World Systems
7. **Social Events System** (Parties, gatherings, town events)
8. **Family System** (Household relationships)
9. **Dynamic Events System** (Random encounters)
10. **Economy System** (Business ownership, income)
11. **Location System** (Enhanced locations, activities)
12. **NPC Autonomy** (NPCs interact independently!)

### Meta Systems
13. **Statistics System** (Comprehensive tracking)
14. **Save System** (Multiple save slots)
15. **Intimate Relationship System** (Adult content tracking)
16. **Consequences System** (Jealousy, cheating, automatic reactions)

### Integration
17. **Game Manager** (Unified control for all 16 systems)

---

## 🚀 Quick Start

1. **Start the server**:
   ```bash
   python web_app.py
   ```

2. **Open the main game**:
   - Go to `http://127.0.0.1:8000/`
   - Click "Start" to initialize
   - Play as normal

3. **Open the systems dashboard** (in a new tab):
   - Go to `http://127.0.0.1:8000/ui`
   - Browse the 4 tabs
   - All data updates in real-time!

---

## 📡 Available API Endpoints

### Game Systems
- `GET /api/portraits` - All NPCs with portraits and relationships
- `GET /api/town-map` - Town map with NPC locations
- `GET /api/statistics` - Player statistics (skills, money, memories)
- `GET /api/relationships` - All active relationships
- `GET /api/locations` - Location data with occupants
- `GET /api/npcs` - All NPCs with basic info
- `GET /api/timeline` - Event log
- `GET /api/analysis` - Relationship analytics

### Game Actions (via Game Manager)
- `POST /api/action/talk/{npc}` - Talk to an NPC
- `POST /api/action/flirt/{npc}` - Flirt with an NPC
- `POST /api/action/give-gift/{npc}/{item}` - Give a gift
- `POST /api/action/learn-skill/{skill}` - Practice a skill
- `POST /api/action/buy-item/{item}` - Buy an item

---

## 🎨 What the AI Narrator Now Sees

The enhanced narrator has full awareness of:
- Your top 3 skills (with levels)
- Your important inventory items
- Your town reputation
- Notable NPCs with relationship scores (e.g., "Emma (F:45 R:30)")
- Your last 3 memories
- Active events happening today
- Top 3 most juicy gossip
- NPC autonomous interactions (who flirted with whom!)

This makes the AI's responses **much more contextual and aware** of the game state!

---

## 📖 Full Documentation

- **GAME_SYSTEMS_README.md** - Complete guide to all 17 systems (1200+ lines)
- **INTEGRATION_INSTRUCTIONS.md** - Technical integration details
- **NARRATOR_INTEGRATION.md** - How narrator awareness works

---

## 🐛 Troubleshooting

**Issue**: UI shows "Sim not started"
- **Fix**: Go to main interface first (`http://127.0.0.1:8000/`), click "Start", then refresh the `/ui` page

**Issue**: Portraits not loading
- **Fix**: Portraits are generated on-demand. Talk to NPCs in the game to trigger portrait generation.

**Issue**: Empty statistics
- **Fix**: Play the game for a few in-game hours to accumulate data

---

## 🎉 Enjoy!

You now have a fully-featured life simulation with:
- ✅ 70 NPCs with autonomous behavior
- ✅ Skills, inventory, and money
- ✅ Deep relationship system
- ✅ Town-wide reputation and gossip
- ✅ Memories and statistics tracking
- ✅ Interactive map and portraits
- ✅ AI narrator with full game awareness

Have fun in Willow Creek! 🌳
