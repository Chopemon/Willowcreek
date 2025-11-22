# Willow Creek - Game Systems Guide

**Complete documentation for all 17 game systems**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Mechanics](#core-mechanics)
3. [Relationship Systems](#relationship-systems)
4. [Social Systems](#social-systems)
5. [World Systems](#world-systems)
6. [Meta Systems](#meta-systems)
7. [Integration Guide](#integration-guide)
8. [UI Components](#ui-components)
9. [API Reference](#api-reference)

---

## Getting Started

### Quick Setup

```python
from game_manager import get_game_manager

# Initialize the game manager (connects all 17 systems)
game = get_game_manager(simulation)

# Initialize the player
game.initialize_character("Malcolm Newt", is_player=True)

# Initialize NPCs
for npc in simulation.npcs:
    game.initialize_character(npc.full_name)
```

### Running the Web UI

```bash
# Start the server with new UI components
python web_app.py
```

Then open your browser to:
- Main game: `http://localhost:8000`
- Systems UI: `http://localhost:8000/ui`

---

## Core Mechanics

### 1. Skill System (`systems/skill_system.py`)

**8 Skills Available:**
- **Charisma** - Conversation, persuasion, charm
- **Athletic** - Physical activities, fitness
- **Intelligence** - Knowledge, problem-solving
- **Creativity** - Arts, music, writing
- **Cooking** - Food preparation
- **Mechanical** - Repairs, building
- **Seduction** - Romantic/sexual appeal
- **Empathy** - Understanding emotions

**Usage:**

```python
from systems.skill_system import SkillType

# Add experience
messages = game.skills.add_experience("Malcolm Newt", SkillType.CHARISMA, 10)
# Returns: ["Charisma increased to level 2!"] if leveled up

# Get skill level
level = game.skills.get_skill_level("Malcolm Newt", SkillType.SEDUCTION)

# Perform skill check
success, roll = game.skills.perform_skill_check(
    "Malcolm Newt",
    SkillType.CHARISMA,
    difficulty=50
)
# Returns: (True, 75.3) if successful

# Get skill summary
summary = game.skills.get_character_summary("Malcolm Newt")
```

**XP Rewards by Activity:**
```python
{
    "conversation": {Charisma: 5, Empathy: 3},
    "flirt": {Seduction: 8, Charisma: 3},
    "workout": {Athletic: 15},
    "read": {Intelligence: 10},
    "cook": {Cooking: 12},
    "intimate": {Seduction: 15, Empathy: 5}
}
```

---

### 2. Inventory System (`systems/inventory_system.py`)

**Item Categories:**
- Gifts (flowers, chocolate, books, wine)
- Consumables (coffee, energy drinks, food)
- Clothing (casual, formal, athletic wear)
- Tools
- Key Items

**Usage:**

```python
# Get inventory
inventory = game.inventory.get_inventory("Malcolm Newt")

# Add money
inventory.add_money(100)

# Buy/add item
inventory.add_item("flowers", 2)  # Add 2 flowers

# Use consumable
success, message, effects = game.inventory.use_item(
    "Malcolm Newt",
    "coffee",
    npc=malcolm
)
# Effects: {"energy": 15, "mood": 5}

# Give gift
success, msg = game.give_gift("Malcolm Newt", "Jane Doe", "flowers")

# Check inventory
print(f"Money: ${inventory.money}")
print(f"Items: {inventory.items}")
print(f"Slots: {inventory.used_slots}/{inventory.max_slots}")
```

**Pre-defined Items:**

| Item | Category | Price | Effect |
|------|----------|-------|--------|
| Flowers | Gift | $25 | Relationship +10 |
| Chocolate | Gift | $20 | Relationship +8 |
| Book | Gift | $15 | Relationship +7 |
| Wine | Gift | $30 | Relationship +12 |
| Coffee | Consumable | $5 | Energy +15, Mood +5 |
| Energy Drink | Consumable | $8 | Energy +30 |
| Sandwich | Consumable | $10 | Hunger +30, Energy +5 |
| Pizza | Consumable | $15 | Hunger +50, Mood +10 |

---

### 3. Memory System (`systems/memory_system.py`)

**Memory Types:**
- First Meeting, Conversation, Gift Given/Received
- First Kiss, Intimate Moment, Date
- Conflict, Breakup, Caught Cheating
- Pregnancy Discovered, Birth
- Achievement, Special Event

**Importance Levels:**
- Trivial (1), Minor (2), Moderate (3), Significant (4), Major (5), Life-Changing (10)

**Usage:**

```python
from systems.memory_system import MemoryType, MemoryImportance

# Add memory
game.memory.add_memory(
    character_name="Malcolm Newt",
    memory_type=MemoryType.FIRST_KISS,
    description="First kiss with Sarah at the park",
    sim_day=game.sim.time.total_days,
    sim_hour=game.sim.time.hour,
    importance=MemoryImportance.SIGNIFICANT,
    participants=["Sarah Johnson"],
    location="Willow Creek Park"
)

# Get recent memories
memories = game.memory.get_recent_memories("Malcolm Newt", count=10)

# Get memories with specific person
shared = game.memory.get_memories_with("Malcolm Newt", "Sarah Johnson", limit=20)

# Get relationship timeline
timeline = game.memory.get_relationship_timeline("Malcolm Newt", "Sarah Johnson")

# Track "first time" events
is_first = game.memory.track_first("malcolm_first_date")  # Returns True first time
```

---

## Relationship Systems

### 4. Relationship System (`systems/relationship_system.py`)

**Relationship Statuses (0-8):**
1. Stranger
2. Acquaintance
3. Friend
4. Close Friend
5. Best Friend
6. Romantic Interest
7. Dating
8. Committed
9. Married

**Relationship Metrics:**
- Friendship Points (0-100)
- Romantic Points (0-100)
- Trust (0-100)
- Respect (0-100)
- Chemistry (0-100, calculated)
- Jealousy Level (0-100)

**Attraction Levels:**
- None, Slight, Moderate, Strong, Intense

**Usage:**

```python
# Get relationship
rel = game.relationships.get_relationship("Malcolm Newt", "Sarah Johnson")

# Add friendship
game.relationships.add_friendship("Malcolm Newt", "Sarah Johnson", 10)

# Add romance
game.relationships.add_romance("Malcolm Newt", "Sarah Johnson", 15)

# Start dating (requires romance 40+, friendship 30+)
success = game.relationships.start_dating("Malcolm Newt", "Sarah Johnson")

# Commit relationship (requires dating status, romance 70+, friendship 60+)
success = game.relationships.commit_relationship("Malcolm Newt", "Sarah Johnson")

# Record interaction
game.relationships.record_interaction("Malcolm Newt", "Sarah Johnson", "talk")
# Types: talk, deep_talk, flirt, date, kiss, gift, conflict

# Get summary
summary = game.relationships.get_summary("Malcolm Newt", "Sarah Johnson")
print(summary)
```

**Relationship Decay:**
- Relationships naturally decay over time if not maintained
- Decay rate: 0.5 friendship points per day
- Use `record_interaction()` to reset decay timer

---

### 5. Reputation System (`systems/reputation_system.py`)

**Reputation Traits:**
- Charming, Trustworthy, Mysterious, Friendly
- Flirtatious, Player (dates many people)
- Generous, Selfish
- Respectful, Creepy
- Reliable, Gossip, Drama Magnet

**Gossip Types:**
- Relationship, Breakup, Cheating
- Pregnancy, Scandal
- Compliment, Insult, Observation

**Usage:**

```python
from systems.reputation_system import ReputationTrait, GossipType

# Get reputation
rep = game.reputation.get_reputation("Malcolm Newt")
print(f"Overall: {rep.overall_score}/100")
print(f"Traits: {rep.get_primary_traits(3)}")

# Modify reputation
game.reputation.modify_reputation("Malcolm Newt", 10, reason="Helped someone")

# Add reputation trait
game.reputation.add_reputation_trait("Malcolm Newt", ReputationTrait.CHARMING, 15)

# Create gossip
gossip = game.reputation.create_gossip(
    gossip_type=GossipType.RELATIONSHIP,
    subject="Malcolm Newt",
    content="Malcolm and Sarah were seen holding hands!",
    source="Town Gossip",
    juiciness=7,
    current_day=game.sim.time.total_days
)

# Spread gossip
game.reputation.spread_gossip(gossip, to_character="Jane Doe")

# Handle actions that affect reputation
game.reputation.handle_action_reputation("Malcolm Newt", "help_someone")
# Actions: help_someone, flirt, caught_cheating, gift_giving, gossip, respectful, creepy
```

---

### 6. Intimate Relationship System (`systems/intimate_system.py`)

**Intimacy Levels:**
1. None
2. Kissed
3. Intimate
4. Regular Partner
5. Committed Intimate

**Usage:**

```python
# Record first kiss
game.intimate.record_first_kiss("Malcolm Newt", "Sarah Johnson", current_day)

# Record intimate encounter
game.intimate.record_intimate_encounter("Malcolm Newt", "Sarah Johnson", current_day)

# Get intimate relationship
intimate_rel = game.intimate.get_intimate_relationship("Malcolm Newt", "Sarah Johnson")
print(f"Level: {intimate_rel.intimacy_level.name}")
print(f"Times: {intimate_rel.times_intimate}")
print(f"Satisfaction: {intimate_rel.satisfaction}/100")
```

---

## Social Systems

### 7. Dialogue System (`systems/dialogue_system.py`)

**Dialogue Conditions:**
- Minimum friendship/romance required
- Skill level required
- Has specific item
- Relationship status
- Time of day, Location
- First time only

**Usage:**

```python
from systems.dialogue_system import DialogueNode, DialogueChoice

# Create dialogue tree
tree = game.dialogue.create_dialogue_tree("Sarah Johnson")

# Add greeting node
greeting = DialogueNode(
    id="greeting",
    npc_line="Hi! How are you?",
    choices=[
        DialogueChoice(
            id="flirt",
            text="You look beautiful today.",
            response="Oh! Thank you, that's sweet!",
            effects={"friendship": 3, "romance": 5},
            skill_check=(SkillType.CHARISMA, 30)
        ),
        DialogueChoice(
            id="friendly",
            text="I'm good! How about you?",
            response="I'm doing great, thanks for asking!",
            effects={"friendship": 5}
        )
    ]
)
tree.add_node(greeting)

# Start conversation
context = {
    "friendship": 50,
    "romance": 20,
    "skills": {SkillType.CHARISMA: 5}
}
node = game.dialogue.start_conversation("Sarah Johnson", context)

# Get available choices
choices = game.dialogue.get_available_choices(tree, node, context)

# Select choice
next_node = game.dialogue.select_choice(tree, choices[0])

# Apply effects
game.dialogue.apply_choice_effects(
    choices[0],
    game.relationships,
    "Malcolm Newt",
    "Sarah Johnson"
)
```

**Quick Dialogue Responses:**
```python
from systems.dialogue_system import QUICK_DIALOGUES

# Get appropriate greeting based on relationship level
greetings = QUICK_DIALOGUES["greeting"]["friend"]  # ["Hey! How's it going?", ...]
```

---

### 8. Social Events System (`systems/social_events_system.py`)

**Event Types:**
- Party, Festival, Gathering
- Date, Wedding, Birthday

**Usage:**

```python
from systems.social_events_system import EventType

# Create event
event = game.social_events.create_event(
    name="Sarah's Birthday Party",
    event_type=EventType.BIRTHDAY,
    location="Sarah's House",
    host="Sarah Johnson",
    day=15,
    start_hour=18,
    duration_hours=4,
    invited=["Malcolm Newt", "Jane Doe", "John Smith"]
)

# Check if event is active
if event.is_active(current_day=15, current_hour=19):
    print("Party is happening!")

# Attend event
game.social_events.attend_event(event, "Malcolm Newt")

# Get upcoming events
upcoming = game.social_events.get_upcoming_events(current_day=10, days_ahead=7)
```

---

### 9. Family System (`systems/family_system.py`)

**Family Relations:**
- Parent, Child, Sibling, Spouse
- Grandparent, Grandchild
- Aunt/Uncle, Niece/Nephew, Cousin

**Usage:**

```python
from systems.family_system import FamilyRelation

# Add family relationship
game.family.add_family_relation("John Smith", "Sarah Smith", FamilyRelation.SIBLING)

# Check if related
if game.family.are_related("John Smith", "Sarah Smith"):
    print("They're family!")

# Get family members
siblings = game.family.get_family_members("John Smith", FamilyRelation.SIBLING)

# Create household
household = game.family.create_household("123 Oak Street", owner="Malcolm Newt")

# Move in together
game.family.move_in("Sarah Johnson", household.id)

# Get household members
housemates = game.family.get_household_members("Malcolm Newt")
```

---

### 10. NPC Autonomy System (`systems/npc_autonomy_system.py`)

NPCs interact with each other independently!

**Usage:**

```python
# Simulate NPC interactions (call daily)
game.npc_autonomy.simulate_npc_interactions(
    game.sim.npcs,
    game.relationships,
    current_day=game.sim.time.total_days,
    current_hour=game.sim.time.hour
)

# Get today's interactions
interactions = game.npc_autonomy.get_todays_interactions()
# Returns: ["Sarah Johnson and John Smith talk", "Jane Doe and Mike Williams flirt", ...]
```

**How it works:**
- Groups NPCs by location
- 20% chance of interaction between NPCs at same location
- Interaction types: talk, flirt, conflict
- Automatically updates relationship between NPCs

---

## World Systems

### 11. Dynamic Events System (`systems/dynamic_events_system.py`)

**Event Categories:**
- Encounter, Opportunity, Crisis, Discovery, Social

**Usage:**

```python
# Check for random event
context = {
    "location": "Park",
    "hour": 14
}
event = game.dynamic_events.check_for_event(context)

if event:
    print(event.description)
    # Display choices to player
    for choice_text, outcome in event.choices:
        print(f"- {choice_text}")
```

**Pre-defined Events:**
- **Lost Wallet** - Find wallet, return it or keep money
- **Friendly Dog** - Pet a friendly dog at park
- **Coffee Shop Encounter** - Bump into someone, spill coffee

**Adding Custom Events:**
```python
from systems.dynamic_events_system import DynamicEvent, EventCategory

custom_event = DynamicEvent(
    id="meet_stranger",
    name="Mysterious Stranger",
    description="A stranger approaches you...",
    category=EventCategory.ENCOUNTER,
    probability=0.05,
    conditions={"location": "Bar", "time_range": (20, 24)},
    choices=[
        ("Talk to them", {"friendship": +10, "reputation": +5}),
        ("Ignore them", {})
    ]
)
game.dynamic_events.event_pool.append(custom_event)
```

---

### 12. Location System (`systems/location_system.py`)

**Locations:**
- Park (walk, jog, picnic, read)
- Coffee Shop (drink coffee, read, socialize, work)
- Bar (drink, eat, socialize, play pool)
- Gym (workout, yoga, swim)

**Usage:**

```python
# Get location
location = game.locations.get_location("Coffee Shop")

# Check if open
if location.is_open(current_hour=14):
    print("Coffee shop is open!")

# Move character
success = game.locations.move_character(
    "Malcolm Newt",
    from_location="Home",
    to_location="Coffee Shop",
    hour=14
)

# Get occupants
people_here = game.locations.get_occupants("Coffee Shop")
```

---

### 13. Economy System (`systems/economy_system.py`)

**Job Types:**
- Retail, Office, Medical, Education, Service, Creative

**Usage:**

```python
from systems.economy_system import Job, JobType

# Get available jobs
jobs = game.economy.available_jobs

# Hire character
barista_job = jobs[0]  # Barista job
game.economy.hire("Malcolm Newt", barista_job)

# Get character's job
job = game.economy.get_job("Malcolm Newt")
print(f"Job: {job.title}")
print(f"Pay: ${job.hourly_pay}/hour")
print(f"Weekly Income: ${job.weekly_income}")

# Money operations
money = game.economy.get_money("Malcolm Newt")
game.economy.add_money("Malcolm Newt", 100)
success = game.economy.spend_money("Malcolm Newt", 50)

# Pay weekly wages (call every 7 days)
game.economy.pay_weekly_wages()
```

---

## Meta Systems

### 14. Statistics System (`systems/statistics_system.py`)

**Tracked Stats:**
- NPCs met, Conversations, Friends, Romances, Dates
- Money earned/spent, Gifts given/received
- Locations visited, Events attended, Skills leveled
- Days played

**Usage:**

```python
# Get stats
stats = game.statistics.get_stats("Malcolm Newt")

# Record events
game.statistics.record_npc_met("Malcolm Newt")
game.statistics.record_conversation("Malcolm Newt")
game.statistics.record_date("Malcolm Newt")
game.statistics.record_location_visit("Malcolm Newt", "Park")

# Get summary
summary = stats.get_summary()
print(summary)
```

---

### 15. Save System (`systems/save_system.py`)

**Usage:**

```python
# Save game
success = game.save_game("my_save_slot")

# Load game
game_state = game.load_game("my_save_slot")

# List all saves
saves = game.save_system.list_saves()
for save in saves:
    print(f"{save['slot_name']} - Day {save['day']} - {save['save_time']}")

# Delete save
game.save_system.delete_save("my_save_slot")
```

---

### 16. Consequences System (`systems/consequences_system.py`)

Automatic consequences for player actions!

**Consequence Types:**
- Jealousy Drama (dating multiple people)
- Caught Cheating
- Pregnancy Outcomes
- Reputation Changes

**Usage:**

```python
# Simulate consequences (call daily)
game.consequences.check_for_consequences(
    game.relationships,
    game.reputation,
    game.sim.pregnancy,
    current_day=game.sim.time.total_days
)

# Trigger caught cheating
game.consequences.trigger_caught_cheating(
    cheater="Malcolm Newt",
    partner="Sarah Johnson",
    caught_with="Jane Doe",
    current_day=15,
    relationship_manager=game.relationships,
    reputation_system=game.reputation
)
# Effects: Romance -50, Trust -80, Reputation damage

# Get active consequences
consequences = game.consequences.get_active_consequences()
```

---

## Integration Guide

### Quick Integration with Existing Simulation

```python
# In your main simulation file
from game_manager import get_game_manager

class WillowCreekSimulation:
    def __init__(self):
        # ... existing init ...

        # Add game manager
        self.game = get_game_manager(self)

        # Initialize characters
        self.game.initialize_character("Malcolm Newt", is_player=True)
        for npc in self.npcs:
            self.game.initialize_character(npc.full_name)

    def tick(self, hours):
        # ... existing tick ...

        # Simulate game systems
        self.game.simulate_day()
```

### Adding to Narrative Generation

```python
# In narrative_chat.py or equivalent

def process_player_action(user_input: str):
    # Detect action type
    if "talk to" in user_input.lower():
        npc_name = extract_npc_name(user_input)
        xp_gained = game.talk_to_npc("Malcolm Newt", npc_name)

    elif "flirt" in user_input.lower():
        npc_name = extract_npc_name(user_input)
        success, msg = game.flirt_with_npc("Malcolm Newt", npc_name)

    elif "give" in user_input.lower():
        npc_name, item = extract_gift_info(user_input)
        success, msg = game.give_gift("Malcolm Newt", npc_name, item)
```

---

## UI Components

### Accessing the New UI

```bash
# The UI components are available at:
http://localhost:8000/ui
```

**4 Tabs Available:**

1. **Portrait Gallery** - View all NPC portraits with relationship status
2. **Town Map** - Interactive map showing NPC locations
3. **Statistics** - Player stats, skills, money, memories
4. **Relationships** - All active relationships with details

### API Endpoints

See `api_endpoints.py` for all available endpoints:

```
GET  /api/portraits          - Get all NPC portraits
GET  /api/town-map           - Get town map data
GET  /api/statistics         - Get player statistics
GET  /api/relationships      - Get all relationships
GET  /api/npc/{name}         - Get NPC details
GET  /api/inventory          - Get player inventory
GET  /api/skills             - Get player skills
GET  /api/events/upcoming    - Get upcoming events
GET  /api/gossip             - Get recent gossip

POST /api/action/talk/{npc}  - Talk to NPC
POST /api/action/flirt/{npc} - Flirt with NPC
POST /api/action/give-gift/{npc}/{item} - Give gift
```

---

## Example Gameplay Flow

```python
from game_manager import get_game_manager
from systems.skill_system import SkillType

# Initialize
game = get_game_manager(simulation)
game.initialize_character("Malcolm Newt", is_player=True)

# Day 1: Meet Sarah
game.talk_to_npc("Malcolm Newt", "Sarah Johnson")
# Gains: Charisma +5 XP, Empathy +3 XP, Friendship +2

# Day 2: Buy flowers and give gift
inventory = game.inventory.get_inventory("Malcolm Newt")
inventory.add_item("flowers", 1)
game.give_gift("Malcolm Newt", "Sarah Johnson", "flowers")
# Gains: Friendship +10, Reputation trait "Generous" +8

# Day 3: Flirt
success, msg = game.flirt_with_npc("Malcolm Newt", "Sarah Johnson")
if success:
    # Gains: Seduction +8 XP, Romance +5, Reputation "Flirtatious" +5
    pass

# Day 5: Ask on date
if game.relationships.get_relationship("Malcolm Newt", "Sarah Johnson").romantic_points >= 30:
    game.go_on_date("Malcolm Newt", "Sarah Johnson", "Coffee Shop")
    # Gains: Friendship +5, Romance +10, Memory created

# Day 10: Start dating
game.relationships.start_dating("Malcolm Newt", "Sarah Johnson")
# Status changed to "Dating"

# Day 30: NPC autonomy kicks in
# Sarah and John might interact independently
# Gossip spreads about Malcolm and Sarah dating
# Jealousy mechanics activate if Malcolm dates others

# Save progress
game.save_game("my_playthrough")
```

---

## Best Practices

1. **Call `simulate_day()` regularly** - Enables NPC autonomy, gossip spread, consequences
2. **Track memories for important events** - Enriches narrative
3. **Use skill checks for actions** - Makes gameplay more dynamic
4. **Check consequences** - Dating multiple people triggers drama
5. **Monitor reputation** - Actions have town-wide effects
6. **Give gifts strategically** - Different NPCs prefer different items
7. **Visit different locations** - Unlock activities and random events
8. **Save frequently** - Multiple save slots available

---

## Troubleshooting

**"No memories showing"**
- Make sure to add memories when events occur
- Call `game.memory.add_memory()` for important actions

**"Skills not leveling up"**
- Check XP requirements: `skill.next_level_xp`
- Activities grant different XP amounts

**"NPCs not interacting"**
- Call `game.simulate_day()` regularly
- NPCs must be at same location (20% interaction chance)

**"Reputation not changing"**
- Use `game.reputation.handle_action_reputation()` for actions
- Some actions have delayed reputation effects

---

## Credits

All 17 systems designed and implemented for the Willow Creek simulation game.

For questions or issues, consult the source code in `/systems/` directory.

**Happy gaming! 🎮**
