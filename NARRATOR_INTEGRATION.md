# How to Give the AI Narrator Access to All Game Systems

## The Problem

Currently, the narrator only sees basic world state:
- Time, weather
- Malcolm's needs (hunger, energy, horny)
- NPC states (horny, lonely, energy)
- Basic biology (pregnancy, ovulation)

**The narrator does NOT see:**
- Skills and XP
- Reputation and gossip
- Memories
- Deep relationships (friendship/romance scores)
- Inventory
- Social events
- NPC autonomous interactions

## The Solution

Use `enhanced_snapshot_builder.py` which adds all game systems to the narrator's context.

---

## Integration: Option 1 (Simple - Automatic)

### Step 1: Modify `narrative_chat.py`

Change line 9 from:
```python
from world_snapshot_builder import create_narrative_context
```

To:
```python
from enhanced_snapshot_builder import create_narrative_context
```

**That's it!** The enhanced version is backward compatible.

### What the narrator now sees:

```
## TIME & ENVIRONMENT
Monday, September 01, 2025, 08:30 AM (Monday)
Season: Autumn | Weather: Clear | Temperature: 55°F
Day #1 of simulation

## MALCOLM NEWT - COMPLETE STATE
Location: Malcolm's House
Age: 30 | Occupation: Unknown

PHYSICAL NEEDS:
- Hunger: 50.0/100
- Energy: 80.0/100
- Hygiene: 60.0/100
- Bladder: 60.0/100
- Horny: 30.0/100

PSYCHOLOGICAL STATE:
- Lonely: 20.0/100
- Mood: NEUTRAL

## MALCOLM'S SKILLS                    <-- NEW!
  Charisma: Lvl 3/10
  Seduction: Lvl 2/10
  Athletic: Lvl 1/10

## MALCOLM'S INVENTORY                 <-- NEW!
Money: $750
Items: Flowers x2, Book x1

## MALCOLM'S REPUTATION                <-- NEW!
Town Opinion: Positive (25/100)
Known For: Charming, Friendly

## NOTABLE RESIDENTS (8 shown, 41 total)

### Coffee Shop
  • Sarah Johnson (28): H:75 L:35 E:65 | F:45 R:30 [horny,attracted]  <-- NEW! Shows relationship!
  • John Smith (32): H:40 L:80 E:50 | F:15 R:5 [LONELY]

### Park
  • Emma Davis (25): H:85 L:25 E:70 | F:60 R:15 [HORNY,friend]  <-- NEW! Friend status!
  • Mike Williams (29): H:30 L:90 E:40 | F:80 R:5 [LONELY,best friend]  <-- Best friend!

## RECENT MEMORIES                     <-- NEW!
  • Gave flowers to Sarah at Coffee Shop
  • Had deep conversation with Emma at Park
  • Flirted with Sarah (successful!)

## EVENTS HAPPENING NOW                <-- NEW!
  • Town Festival at Town Square (hosted by Mayor)
    Malcolm is invited! 15 people attending

Upcoming:
  • Sarah's Birthday Party - Day 5 at 18:00

## TOWN GOSSIP                         <-- NEW!
  • Malcolm and Sarah were seen holding hands! (spread to 8 people)
  • Someone saw Malcolm buying flowers (spread to 3 people)

## NPC ACTIVITY TODAY                  <-- NEW!
  • Sarah Johnson flirted with John Smith
  • Emma Davis had a conflict with Mike Williams

## BIOLOGY & HEALTH
Pregnant: None
Menstruating: Emily Brown (if horny>70 or lonely>70)
```

---

## Integration: Option 2 (Manual - More Control)

If you want to customize what the narrator sees, manually edit `narrative_chat.py`:

```python
# At top of file
from game_manager import get_game_manager
from enhanced_snapshot_builder import create_enhanced_narrative_context

# In narrate() method (around line 87-89)
def narrate(self, user_input: str) -> str:
    # Get game manager
    game = get_game_manager(self.sim)

    # Get enhanced world snapshot
    world_snapshot = create_enhanced_narrative_context(self.sim, self.malcolm)

    # ... rest of narrate method ...
```

---

## What Each New Section Does

### 1. **MALCOLM'S SKILLS**
Tells narrator Malcolm's abilities
- **Use Case**: Narrator can mention "Your practiced charm..." if Charisma is high
- **Use Case**: Narrator can describe physical feats based on Athletic level

### 2. **MALCOLM'S INVENTORY**
Tells narrator what Malcolm has
- **Use Case**: "You reach into your pocket and pull out the flowers you bought..."
- **Use Case**: If low on money, narrator can reflect Malcolm's financial state

### 3. **MALCOLM'S REPUTATION**
Tells narrator how town perceives Malcolm
- **Use Case**: NPCs react differently if Malcolm is "Creepy" vs "Charming"
- **Use Case**: "People whisper as you walk by..." if reputation is bad

### 4. **Enhanced NPC States** (F:45 R:30)
Shows friendship and romance scores
- **F:45** = Friendship 45/100 (friend level)
- **R:30** = Romance 30/100 (romantic interest forming)
- **Use Case**: Narrator knows Sarah is attracted, can describe her body language differently
- **Use Case**: If showing "best friend", narrator can write warmer dialogue

### 5. **RECENT MEMORIES**
Gives narrator context of what just happened
- **Use Case**: Narrator can reference previous interactions naturally
- **Use Case**: "As you approach Sarah, you remember the flowers you gave her yesterday..."

### 6. **EVENTS HAPPENING NOW**
Tells narrator about active social events
- **Use Case**: "The festival is in full swing, music drifting from the town square..."
- **Use Case**: Can naturally suggest Malcolm attend if invited

### 7. **TOWN GOSSIP**
Shows rumors circulating
- **Use Case**: NPCs might mention gossip in conversation
- **Use Case**: "You overhear whispers about you and Sarah..."
- **Use Case**: Creates emergent drama and reactions

### 8. **NPC ACTIVITY TODAY**
Shows what NPCs did autonomously
- **Use Case**: "You notice Sarah seems flustered - you saw her talking with John earlier..."
- **Use Case**: Creates jealousy scenarios naturally
- **Use Case**: World feels alive with NPCs having their own lives

---

## Benefits for Narrative Quality

### Before (Standard Snapshot):
```
User: "I talk to Sarah"
Narrator: "Sarah greets you warmly. She seems friendly."
```
*Generic, doesn't reflect history or relationship*

### After (Enhanced Snapshot):
```
User: "I talk to Sarah"
Narrator sees:
  - F:45 R:30 [attracted]
  - Memory: "Gave flowers to Sarah yesterday"
  - Gossip: "Malcolm and Sarah were seen holding hands"

Narrator: "Sarah's eyes light up when she sees you, a faint blush
coloring her cheeks. She touches the flowers you gave her yesterday,
still sitting on her desk. 'I've been hoping you'd come by,' she says
softly, glancing around to see if anyone's watching - the whole town
seems to know about you two now."
```
*Rich, contextual, reflects game state!*

---

## Token Optimization

The enhanced snapshot is **token-optimized**:

- ✅ Only shows top 3 skills (not all 8)
- ✅ Only shows important inventory items (gifts, key items)
- ✅ Only shows reputation if notable (not neutral)
- ✅ Only shows NPCs with high stats OR significant relationship with Malcolm
- ✅ Only shows last 3 memories (not all)
- ✅ Only shows active events + 2 upcoming (not all)
- ✅ Only shows top 3 juiciest gossip
- ✅ Only shows interesting NPC interactions (flirts/conflicts, not regular talks)

**Result**: Adds ~300-500 tokens for MUCH richer context

**Previous optimization** already reduced snapshot by 42-49%, so there's room for this!

---

## Automatic Updates

The narrator automatically sees updates as they happen:

```python
# Player talks to Sarah
game.talk_to_npc("Malcolm Newt", "Sarah Johnson")

# Next narration, narrator sees:
# - F:47 (was 45, +2 from talking)
# - Memory: "Had conversation with Sarah Johnson"
# - Statistics updated

# Player gives flowers
game.give_gift("Malcolm Newt", "Sarah Johnson", "flowers")

# Next narration, narrator sees:
# - F:55 (was 47, +8 from gift)
# - R:35 (was 30, +5 from gift)
# - Memory: "Gave Bouquet of Flowers to Sarah Johnson"
# - Inventory: Flowers x1 (was x2)
# - Reputation: Known For: Generous, Charming

# NPCs interact autonomously
game.simulate_day()

# Next narration, narrator sees:
# - NPC ACTIVITY: "Sarah Johnson flirted with John Smith"
# - Sarah's F with John increased
# - Potential jealousy if Malcolm is dating Sarah
```

---

## Testing

### Test the enhanced snapshot:

```python
from enhanced_snapshot_builder import create_enhanced_narrative_context
from simulation_v2 import WillowCreekSimulation
from game_manager import get_game_manager

# Initialize
sim = WillowCreekSimulation()
malcolm = sim.npc_dict["Malcolm Newt"]
game = get_game_manager(sim)
game.initialize_character("Malcolm Newt", is_player=True)

# Do some actions
game.talk_to_npc("Malcolm Newt", "Sarah Johnson")
game.give_gift("Malcolm Newt", "Sarah Johnson", "flowers")
game.flirt_with_npc("Malcolm Newt", "Sarah Johnson")

# Generate snapshot
snapshot = create_enhanced_narrative_context(sim, malcolm)
print(snapshot)
```

You should see all the new sections!

---

## Customization

Want to add/remove sections? Edit `enhanced_snapshot_builder.py`:

```python
# To add a new section:
def _build_my_custom_section() -> str:
    """My custom data for narrator"""
    return "## MY CUSTOM SECTION\nCustom data here"

# In create_enhanced_narrative_context():
sections.append(_build_my_custom_section())

# To remove a section, just comment it out:
# sections.append(_build_recent_gossip())  # Disabled
```

---

## Fallback Safety

The enhanced snapshot has fallback safety:

```python
try:
    sections.append(_build_malcolm_skills())
except:
    pass  # Silently skip if error
```

If any new system isn't initialized, that section is just skipped. The narrator still gets all the standard data.

---

## Summary

**Before**: Narrator only knew basic needs and NPC states
**After**: Narrator knows skills, reputation, relationships, memories, events, gossip, and NPC activities

**Integration**: Change one import in `narrative_chat.py`
**Token Cost**: +300-500 tokens (~15-20% increase)
**Benefit**: Massively richer, context-aware narratives

**The narrator now has FULL AWARENESS of all game systems!** 🎯
