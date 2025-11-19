# CLAUDE.md - AI Assistant Guide for Willow Creek 2025

> **Last Updated:** November 19, 2025
> **Version:** 2.0 - Python Simulation Engine
> **Purpose:** Comprehensive guide for AI assistants working with the Willow Creek codebase

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture](#architecture)
4. [Code Conventions](#code-conventions)
5. [Key Systems](#key-systems)
6. [Development Workflow](#development-workflow)
7. [Data Structures](#data-structures)
8. [Important Files](#important-files)
9. [Best Practices for AI Assistants](#best-practices-for-ai-assistants)
10. [Common Tasks](#common-tasks)

---

## Project Overview

**Willow Creek 2025** is an advanced autonomous world simulation engine built in Python. It simulates a living, breathing town with autonomous NPCs (non-player characters) who have:

- **Complex needs** (hunger, energy, hygiene, social, fun, horny)
- **Dynamic relationships** (family, friends, romance, enemies)
- **Realistic biology** (menstrual cycles, pregnancy, aging, health)
- **Autonomous behaviors** (schedules, goals, quirks, addictions)
- **Social systems** (reputation, memory, emotional contagion)
- **Life events** (birthdays, school drama, crimes, micro-interactions)

### Key Features

- **10x Performance Improvement** over JavaScript version (~250ms vs ~2500ms for 40 NPCs, 1000 steps)
- **Type-Safe NPCs** using Python dataclasses with validation
- **Vectorized Operations** with NumPy for efficient batch processing
- **Network Analysis** using NetworkX for relationship graphs and community detection
- **Easy Export** to JanitorAI format for integration with AI roleplay systems
- **Comprehensive Systems** - 29 specialized systems managing all aspects of simulation

### Primary Use Cases

1. **Simulation Development** - Build and test autonomous NPC behaviors
2. **Data Analysis** - Analyze relationship networks, social dynamics, life patterns
3. **AI Integration** - Export world state for use in LLM-based narratives (JanitorAI)
4. **Research** - Study emergent behaviors in agent-based simulations

---

## Tech Stack

### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.8+ | Core language |
| **NumPy** | ≥1.24.0 | Vectorized numerical operations |
| **Pandas** | ≥2.0.0 | Data analysis and export |
| **Pydantic** | ≥2.0.0 | Data validation and settings |
| **NetworkX** | ≥3.1 | Graph/network analysis for relationships |
| **Mesa** | ≥2.1.0 | Agent-based modeling framework |
| **Matplotlib** | ≥3.7.0 | Data visualization |
| **Seaborn** | ≥0.12.0 | Statistical visualizations |
| **Plotly** | ≥5.14.0 | Interactive visualizations |

### Development Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Testing framework |
| **pytest-cov** | Code coverage |
| **black** | Code formatting |
| **pylint** | Linting |
| **mypy** | Static type checking |

### Optional Dependencies

- **TextBlob** - Natural language processing for dialogue
- **python-louvain** - Community detection in relationship networks
- **tqdm** - Progress bars for long simulations

---

## Architecture

### Directory Structure

```
Willowcreek/
├── core/                       # Core simulation engine
│   ├── __init__.py
│   ├── time_system.py         # Time management (hours, days, seasons)
│   └── world_state.py         # World state and NPC roster loading
│
├── entities/                   # Entity definitions
│   ├── __init__.py
│   └── npc.py                 # NPC dataclass, Needs, PsycheState
│
├── systems/                    # All simulation systems (29 total)
│   ├── __init__.py
│   ├── needs.py               # Hunger, energy, hygiene, etc.
│   ├── relationships.py       # NPC-to-NPC relationships
│   ├── autonomous.py          # Autonomous decision-making
│   ├── goals_system.py        # Goal tracking and achievement
│   ├── reputation_system.py   # Social reputation tracking
│   ├── memory_system.py       # Event memory and recall
│   ├── schedule_system.py     # Daily schedules and routines
│   ├── emotional_contagion.py # Emotion spreading between NPCs
│   ├── environmental_triggers.py # Environment-based events
│   ├── seasonal_dynamics.py   # Seasonal effects on behavior
│   ├── female_biology_system.py # Menstrual cycle simulation
│   ├── pregnancy_system.py    # Pregnancy and childbirth
│   ├── health_disease_system.py # Health and disease
│   ├── growth_development_system.py # Aging and development
│   ├── skill_progression.py   # Skill learning and improvement
│   ├── consequence_cascades.py # Event consequences
│   ├── dynamic_triggers.py    # Dynamic event triggering
│   ├── birthday_system.py     # Birthday events
│   ├── event_system.py        # General event management
│   ├── school_drama_system.py # School-specific events
│   ├── addiction_system.py    # Addiction mechanics
│   ├── crime_system.py        # Crime and consequences
│   ├── custody_events.py      # Child custody events
│   ├── micro_interactions_system.py # Small social interactions
│   ├── npc_quirks_system.py   # NPC quirks and unique behaviors
│   ├── sexual_activity_system.py # Sexual activity tracking
│   ├── dialogue.py            # Dialogue generation
│   └── debug_overlay.py       # Debug information display
│
├── exporters/                  # Export utilities
│   ├── __init__.py
│   └── janitor_ai.py          # Export to JanitorAI format
│
├── scripts/                    # Utility scripts
│   ├── demo.py                # 500-day simulation demo
│   ├── view_npcs.py           # View NPC roster
│   ├── import_npcs.py         # Import NPCs from JSON
│   └── convert.py             # Data conversion utilities
│
├── npc_data/                   # NPC data files
│   ├── npc_roster.json        # Main NPC roster
│   └── npc_generic.json       # Generic background NPCs
│
├── npc/                        # Individual NPC files (JSON)
├── triggers/                   # Event trigger definitions
├── static/                     # Static assets (web app)
├── venv/                       # Python virtual environment
│
├── simulation_v2.py            # Main simulation class (INTEGRATED)
├── world_snapshot_builder.py  # World snapshot for AI narrators
├── web_app.py                  # Flask web interface (optional)
├── locations.py                # Location definitions
├── neighborhoods.py            # Neighborhood definitions
├── households.py               # Household management
├── narrative_chat.py           # AI narrative chat interface
├── requirements.txt            # Python dependencies
└── README.md                   # User-facing documentation
```

### Core Components

#### 1. **Time System** (`core/time_system.py`)
- Manages simulation time (hours, days, weeks, months, years)
- Tracks seasons (Spring, Summer, Fall, Winter)
- Provides date/time formatting utilities
- Handles time progression during simulation

#### 2. **World State** (`core/world_state.py`)
- Loads NPC roster from JSON files
- Manages global world state (weather, etc.)
- Provides NPC lookup by name
- Handles duplicate NPC resolution

#### 3. **NPC Entity** (`entities/npc.py`)
- **Dataclass-based** NPC definition
- Properties: name, age, gender, occupation, traits, appearance
- Runtime state: location, mood, needs, psyche
- Relationships: dict of NPC-to-NPC connections
- Memory: set of remembered events and secrets

#### 4. **Simulation Engine** (`simulation_v2.py`)
- **Main orchestrator** for all systems
- Initializes all 29 subsystems
- Runs simulation step-by-step
- Exports statistics and world state
- Handles JanitorAI export

---

## Code Conventions

### 1. **Type Hints Everywhere**

Always use type hints for function parameters and return values:

```python
def create_relationship(self, npc1: str, npc2: str, rel_type: str = "stranger",
                       level: float = 0, attraction: float = 0) -> None:
    pass
```

### 2. **Dataclasses for Data Structures**

Use `@dataclass` for all data structures with `field()` for complex defaults:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Set

@dataclass
class NPC:
    full_name: str
    age: int
    gender: Gender = Gender.OTHER
    memory_bank: Set[str] = field(default_factory=set)
    relationships: Dict[str, Dict[str, str]] = field(default_factory=dict)
```

### 3. **Enums for Categorical Data**

Use `Enum` for categorical values:

```python
from enum import Enum

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
```

### 4. **Naming Conventions**

| Type | Convention | Example |
|------|------------|---------|
| **Classes** | PascalCase | `RelationshipManager`, `NeedsSystem` |
| **Functions** | snake_case | `update_all_relationships()` |
| **Variables** | snake_case | `npc_roster`, `time_delta` |
| **Constants** | UPPER_SNAKE_CASE | `JOB_KEYWORDS`, `MAX_NEEDS` |
| **Private** | Leading underscore | `_initialize_relationships()` |

### 5. **Docstrings**

Use triple-quoted docstrings for modules, classes, and complex functions:

```python
def update_all_relationships(self, npcs: List['NPC'], time_delta: float):
    """
    Update all relationships based on current states and proximity.
    Called every simulation step to keep relationships dynamic.
    """
    pass
```

### 6. **Type Checking with TYPE_CHECKING**

Avoid circular imports using `TYPE_CHECKING`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.npc import NPC

class RelationshipManager:
    def __init__(self, npcs: List['NPC']):
        pass
```

### 7. **Error Handling**

Use explicit error handling with informative messages:

```python
try:
    # Load data
    data = self._load_json_list(path)
except Exception as e:
    print(f"[WorldState] ERROR loading roster: {e}")
    return False
```

### 8. **File Encoding**

Always specify UTF-8 encoding for file operations:

```python
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
```

---

## Key Systems

The simulation is powered by **29 specialized systems**. Each system is responsible for a specific aspect of the simulation.

### Core Systems

| System | File | Purpose |
|--------|------|---------|
| **NeedsSystem** | `systems/needs.py` | Manages hunger, energy, hygiene, bladder, social, fun, horny |
| **RelationshipManager** | `systems/relationships.py` | NPC-to-NPC relationships, attraction, trust, social networks |
| **AutonomousSystem** | `systems/autonomous.py` | Autonomous decision-making and behaviors |
| **GoalsSystem** | `systems/goals_system.py` | Goal tracking and achievement |
| **ReputationSystem** | `systems/reputation_system.py` | Social reputation and standing |
| **MemorySystem** | `systems/memory_system.py` | Event memory and recall |
| **ScheduleSystem** | `systems/schedule_system.py` | Daily schedules and routines |

### Environmental & Social Systems

| System | File | Purpose |
|--------|------|---------|
| **EmotionalContagion** | `systems/emotional_contagion.py` | Emotions spreading between NPCs |
| **EnvironmentalTriggers** | `systems/environmental_triggers.py` | Environment-based events |
| **SeasonalDynamics** | `systems/seasonal_dynamics.py` | Seasonal effects on behavior |

### Life Systems

| System | File | Purpose |
|--------|------|---------|
| **FemaleBiologySystem** | `systems/female_biology_system.py` | Menstrual cycle simulation |
| **PregnancySystem** | `systems/pregnancy_system.py` | Pregnancy and childbirth |
| **HealthDiseaseSystem** | `systems/health_disease_system.py` | Health, disease, and injuries |
| **GrowthDevelopment** | `systems/growth_development_system.py` | Aging and development milestones |
| **SkillProgression** | `systems/skill_progression.py` | Skill learning and improvement |

### Event & Drama Systems

| System | File | Purpose |
|--------|------|---------|
| **ConsequenceCascades** | `systems/consequence_cascades.py` | Event consequences and ripple effects |
| **DynamicTriggers** | `systems/dynamic_triggers.py` | Dynamic event triggering based on conditions |
| **BirthdaySystem** | `systems/birthday_system.py` | Birthday events and celebrations |
| **EventSystem** | `systems/event_system.py` | General event management |
| **SchoolDramaSystem** | `systems/school_drama_system.py` | School-specific events and drama |
| **AddictionSystem** | `systems/addiction_system.py` | Addiction mechanics and recovery |
| **CrimeSystem** | `systems/crime_system.py` | Crime, detection, and consequences |
| **CustodyEvents** | `systems/custody_events.py` | Child custody events |
| **MicroInteractions** | `systems/micro_interactions_system.py` | Small social interactions |

### Character Systems

| System | File | Purpose |
|--------|------|---------|
| **NPCQuirksSystem** | `systems/npc_quirks_system.py` | Unique NPC behaviors and quirks |
| **SexualActivitySystem** | `systems/sexual_activity_system.py` | Sexual activity tracking |
| **Dialogue** | `systems/dialogue.py` | Dialogue generation |

### Debug & Utility

| System | File | Purpose |
|--------|------|---------|
| **DebugOverlay** | `systems/debug_overlay.py` | Debug information display |

---

## Development Workflow

### 1. **Setting Up the Environment**

```bash
# Navigate to project directory
cd /home/user/Willowcreek

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Running the Simulation**

```bash
# Run the 500-day demo
python scripts/demo.py

# View NPC roster
python scripts/view_npcs.py
```

### 3. **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### 4. **Code Quality Checks**

```bash
# Format code
black .

# Lint code
pylint entities/ core/ systems/

# Type checking
mypy entities/ core/ systems/
```

### 5. **Common Development Tasks**

#### Adding a New System

1. Create file in `systems/` directory: `systems/my_new_system.py`
2. Define system class with required methods
3. Import in `simulation_v2.py`
4. Initialize in `WillowCreekSimulation.__init__()`
5. Call system methods in simulation step loop

Example:

```python
# systems/my_new_system.py
class MyNewSystem:
    def __init__(self):
        print("MyNewSystem initialized")

    def update(self, npcs, time_delta):
        """Called each simulation step"""
        pass
```

```python
# simulation_v2.py
from systems.my_new_system import MyNewSystem

class WillowCreekSimulation:
    def __init__(self, num_npcs: int = 41):
        # ... other systems ...
        self.my_system = MyNewSystem()
```

#### Adding a New NPC

1. Edit `npc_data/npc_roster.json`
2. Add new NPC object with required fields
3. Reload simulation

Required fields:
```json
{
  "full_name": "Jane Doe",
  "age": 30,
  "gender": "female",
  "occupation": "Teacher",
  "appearance": "Athletic build, brown hair",
  "coreTraits": ["Friendly", "Intelligent", "Organized"],
  "relationships": {}
}
```

#### Modifying NPC Properties

NPCs are loaded from JSON and converted to dataclass instances. To modify:

1. **At runtime**: Access via `sim.npc_dict["NPC Name"]` and modify properties
2. **Persistent changes**: Edit JSON files in `npc_data/`

---

## Data Structures

### NPC Structure

```python
@dataclass
class NPC:
    # Core identity
    full_name: str                           # "Maria Sturm"
    age: int                                 # 35
    gender: Gender                           # Gender.FEMALE
    occupation: Optional[str]                # "Housewife"
    appearance: str                          # "Attractive, blonde hair..."

    # Personality & traits
    coreTraits: List[str]                    # ["Submissive", "Caring"]
    libidoLevel: int                         # 0-100

    # Social
    affiliation: str                         # "Smith Family"
    relationships: Dict[str, Dict[str, str]] # NPC relationships

    # State
    status: str                              # "active" | "inactive"
    relationship: int                        # Relationship level (0-100)
    current_location: str                    # "Home" | "Work" | etc.
    home_location: str                       # "123 Main St"
    mood: str                                # "Happy" | "Sad" | etc.

    # Internal state
    needs: Needs                             # Hunger, energy, etc.
    psyche: PsycheState                      # Emotional state

    # Memory & secrets
    memory_bank: Set[str]                    # Set of remembered events
    private_secrets: Set[str]                # Private habits/secrets
    dislikes: List[str]                      # List of dislikes

    # Background
    background: NPCBackground                # Conflict, vulnerability
```

### Needs Structure

```python
@dataclass
class Needs:
    hunger: float = 80.0      # 0-100, higher = more satisfied
    energy: float = 90.0      # 0-100, higher = more energetic
    hygiene: float = 85.0     # 0-100, higher = cleaner
    bladder: float = 20.0     # 0-100, higher = more urgent
    social: float = 60.0      # 0-100, higher = more satisfied
    fun: float = 70.0         # 0-100, higher = more entertained
    horny: float = 30.0       # 0-100, higher = more aroused
```

### Relationship Structure

```python
{
    "npc1": "Alice",
    "npc2": "Bob",
    "type": "friend",           # friend, family, romantic, enemy, stranger
    "level": 75.0,              # 0-100, relationship strength
    "attraction": 30.0,         # 0-100, romantic/sexual attraction
    "history": []               # List of interaction events
}
```

### Time System

```python
class TimeSystem:
    hour: int              # 0-23
    day: int               # 1-30
    month: int             # 1-12
    year: int              # 2025+
    total_days: int        # Days since start
    season: str            # "Spring" | "Summer" | "Fall" | "Winter"
```

---

## Important Files

### Core Files You'll Modify Often

| File | Purpose | When to Edit |
|------|---------|--------------|
| `npc_data/npc_roster.json` | Main NPC roster | Adding/editing NPCs |
| `simulation_v2.py` | Main simulation engine | Adding new systems, changing simulation flow |
| `entities/npc.py` | NPC definition | Adding NPC properties |
| `systems/*.py` | Individual systems | Modifying system behavior |
| `requirements.txt` | Python dependencies | Adding new libraries |

### Configuration Files

| File | Purpose |
|------|---------|
| `.gitattributes` | Git line ending configuration |
| `requirements.txt` | Python package dependencies |

### Data Files

| File/Dir | Purpose |
|----------|---------|
| `npc_data/npc_roster.json` | Main NPC roster (hand-crafted characters) |
| `npc_data/npc_generic.json` | Generic background NPCs (optional) |
| `npc/*.json` | Individual NPC files (alternative storage) |
| `willow_creek_demo.json` | Demo simulation export |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/demo.py` | Run 500-day simulation demo |
| `scripts/view_npcs.py` | View NPC roster details |
| `scripts/import_npcs.py` | Import NPCs from various sources |
| `scripts/convert.py` | Data conversion utilities |

### Utility Files

| File | Purpose |
|------|---------|
| `world_snapshot_builder.py` | Build world snapshots for AI narrators |
| `world_snapshot_builder_fixed.py` | Fixed version of snapshot builder |
| `web_app.py` | Flask web interface (optional) |
| `narrative_chat.py` | AI narrative chat interface |
| `check_files.py` | File integrity checking |

---

## Best Practices for AI Assistants

### 1. **Always Read Before Editing**

Before modifying any file, always read it first to understand its current state.

```python
# DO THIS
Read file → Understand structure → Make targeted edits

# NOT THIS
Assume structure → Make edits → Hope it works
```

### 2. **Preserve Existing Patterns**

When adding new code, match existing patterns:

- If the codebase uses dataclasses, continue using dataclasses
- If type hints are everywhere, add type hints to new code
- Match existing naming conventions and code style

### 3. **Use Appropriate Tools**

| Task | Tool |
|------|------|
| **Search for files** | Use `Glob` tool |
| **Search code** | Use `Grep` tool |
| **Read files** | Use `Read` tool |
| **Edit files** | Use `Edit` tool (not `Write` for existing files) |
| **Run commands** | Use `Bash` tool |
| **Multi-step tasks** | Use `TodoWrite` to track progress |

### 4. **Understand System Dependencies**

Systems often depend on each other. Before modifying a system, check:

1. **What systems does it import?** (Check imports at top of file)
2. **What systems import it?** (Search for imports: `grep -r "from systems.X import"`)
3. **How is it initialized in `simulation_v2.py`?**

### 5. **Test After Changes**

After making changes:

1. **Run the demo**: `python scripts/demo.py` (if simulation-related)
2. **Check for errors**: Look for Python tracebacks
3. **Verify output**: Ensure expected behavior

### 6. **Handle JSON Carefully**

When editing JSON files:

- **Always validate JSON syntax** (use `json.load()` to verify)
- **Preserve existing structure** (field names, data types)
- **Use UTF-8 encoding** for special characters
- **Pretty-print with indentation** for readability

### 7. **Document Complex Changes**

For non-trivial changes:

- Add docstrings to new functions/classes
- Add inline comments for complex logic
- Update CLAUDE.md if architecture changes

### 8. **Git Workflow**

When making commits:

1. **Make atomic commits** (one logical change per commit)
2. **Write clear commit messages** (what & why, not how)
3. **Test before committing** (run demo, check for errors)

Example commit messages:
```
✅ Add new emotion system for NPC mood tracking
✅ Fix relationship decay calculation in RelationshipManager
✅ Update NPC roster with 5 new characters
❌ Fixed stuff
❌ Changes
❌ Update
```

### 9. **Performance Considerations**

- **Use NumPy for batch operations** on multiple NPCs
- **Avoid nested loops** over NPC lists (use vectorization)
- **Cache expensive computations** (relationship graphs, etc.)
- **Profile before optimizing** (use `time.time()` or `cProfile`)

### 10. **Working with Types**

- **Always use type hints** for function signatures
- **Use `Optional[T]`** for values that can be None
- **Use `List[T]`, `Dict[K, V]`** for generic collections
- **Import from `typing`**: `from typing import List, Dict, Optional`

---

## Common Tasks

### Task 1: Add a New NPC Trait

**File:** `entities/npc.py`

```python
@dataclass
class NPC:
    # ... existing fields ...
    new_trait: str = ""  # Add new trait with default value
```

Then update `npc_data/npc_roster.json` to include the new trait for NPCs.

### Task 2: Add a New Need

**File:** `entities/npc.py`

```python
@dataclass
class Needs:
    # ... existing needs ...
    creativity: float = 50.0  # New need
```

**File:** `systems/needs.py`

Update `NeedsSystem` to handle the new need's decay/increase logic.

### Task 3: Create a Custom Event

**File:** `systems/event_system.py` or create new file `systems/my_event.py`

```python
class MyEventSystem:
    def __init__(self):
        self.events = []

    def trigger_event(self, npc, event_type):
        """Trigger a custom event for an NPC"""
        event = {
            'npc': npc.full_name,
            'type': event_type,
            'timestamp': datetime.now()
        }
        self.events.append(event)
        npc.memory_bank.add(f"Experienced {event_type}")
```

### Task 4: Export Data to JSON

**Use Case:** Export simulation state for analysis

```python
import json

# Get all NPCs as dicts
npc_data = [vars(npc) for npc in sim.npcs]

# Export to JSON
with open('npc_export.json', 'w', encoding='utf-8') as f:
    json.dump(npc_data, f, indent=2, default=str)
```

### Task 5: Analyze Relationship Network

**Use Case:** Find most connected NPCs, detect communities

```python
# Most connected NPC
most_social = sim.relationships.get_most_connected_npc()

# Average relationship level
avg_level = sim.relationships.get_average_relationship_level()

# Community detection (requires python-louvain)
import community as community_louvain

communities = community_louvain.best_partition(sim.relationships.graph)
```

### Task 6: Filter NPCs by Criteria

**Use Case:** Find all NPCs with specific traits

```python
# Find all teachers
teachers = [npc for npc in sim.npcs if npc.occupation == "Teacher"]

# Find all NPCs with high libido
high_libido = [npc for npc in sim.npcs if npc.libidoLevel > 70]

# Find all NPCs in a relationship
in_relationships = [npc for npc in sim.npcs if npc.relationships]
```

### Task 7: Modify Simulation Speed

**File:** `scripts/demo.py` or custom script

```python
# Fast simulation (1000 steps = ~42 days)
sim.run(num_steps=1000, steps_per_day=24, time_step_hours=1.0)

# Slow simulation with shorter time steps (smoother updates)
sim.run(num_steps=1000, steps_per_day=24, time_step_hours=0.5)
```

### Task 8: Debug Specific System

**Use Debug Overlay:**

```python
# Enable debug overlay
sim.debug_overlay_enabled = True

# Run simulation
sim.run(num_steps=100, steps_per_day=24)

# Check debug output
sim.debug.print_current_state()
```

### Task 9: Export to JanitorAI

**File:** `exporters/janitor_ai.py`

```python
# After running simulation
from exporters.janitor_ai import export_to_janitor_ai

export_to_janitor_ai(sim, output_file='willow_creek_state.js')
```

The exported `.js` file can be loaded in JanitorAI lorebook for use with AI roleplay.

### Task 10: Create Custom Visualization

**Use Case:** Visualize relationship network

```python
import matplotlib.pyplot as plt
import networkx as nx

# Get relationship graph
G = sim.relationships.graph

# Draw network
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue',
        node_size=500, font_size=8, font_weight='bold')

# Save to file
plt.savefig('relationship_network.png', dpi=300, bbox_inches='tight')
plt.close()
```

---

## Additional Resources

### Understanding the Simulation Flow

```
1. Initialize simulation (load NPCs, create systems)
   ↓
2. Run simulation loop:
   For each time step:
     a. Update time system (advance hour)
     b. Update needs system (decay needs)
     c. Update relationships (dynamic changes)
     d. Update autonomous behaviors (NPCs make decisions)
     e. Update all other systems (events, health, etc.)
     f. Record statistics
   ↓
3. Export results (statistics, world state, JanitorAI format)
```

### Key Design Principles

1. **Modularity** - Each system is independent and focused on one aspect
2. **Type Safety** - Use type hints and dataclasses for data validation
3. **Performance** - Use NumPy for vectorized operations where possible
4. **Extensibility** - Easy to add new systems without modifying core
5. **Data-Driven** - NPCs and world state loaded from JSON files
6. **Export-Friendly** - Easy to export data for analysis and AI integration

### Common Pitfalls to Avoid

1. **Don't modify NPC data structures while iterating** - Make a copy first
2. **Don't assume NPCs exist** - Always check `if npc in sim.npc_dict`
3. **Don't ignore time_delta** - Use it for time-dependent calculations
4. **Don't forget UTF-8 encoding** - Especially for NPC names with special characters
5. **Don't use `Write` on existing files** - Use `Edit` instead to preserve content

### Debugging Tips

1. **Print statements are your friend** - Add `print()` for debugging
2. **Check the demo output** - Run `scripts/demo.py` to see if it works
3. **Use the debug overlay** - Set `sim.debug_overlay_enabled = True`
4. **Check JSON validity** - Use `python -m json.tool file.json` to validate
5. **Check imports** - `ImportError` usually means missing dependency or typo

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **2.0** | Nov 19, 2025 | Complete rewrite for Python simulation engine |
| **1.0** | (Previous) | JavaScript version (deprecated) |

---

## Contact & Support

This is an open-source project. For issues or contributions:

1. **Check the README.md** for user-facing documentation
2. **Review this CLAUDE.md** for development guidelines
3. **Explore the codebase** - code is well-documented
4. **Run the demo** - `python scripts/demo.py` to see it in action

---

**End of CLAUDE.md**
