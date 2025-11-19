# Willow Creek - Enhanced Features Part 2

This document describes the advanced features added to your Willow Creek simulation.

---

## 🆕 Feature 3: Analysis Tools & Visualization

Comprehensive analysis and metrics system for deep insights into your simulation.

### Features

- **Relationship Network Analysis**: Detailed metrics on social connections
- **Behavior Pattern Tracking**: Monitor NPC routines and states
- **Time-Series Data**: Track trends over time
- **Social Cluster Detection**: Identify friend groups automatically
- **Critical State Monitoring**: Find NPCs needing attention
- **Comprehensive Reporting**: Export full analysis to JSON

### Usage

#### In Python Code

```python
from simulation_v2 import WillowCreekSimulation

sim = WillowCreekSimulation(num_npcs=0)
sim.run(num_steps=100, time_step_hours=1.0)

# Get comprehensive analysis
sim.analyzer.print_summary()

# Analyze relationships
rel_analysis = sim.analyzer.analyze_relationships()
print(f"Network Density: {rel_analysis['network_density']}")
print(f"Most Connected NPC: {rel_analysis['most_connected']}")
print(f"Strongest Bonds: {rel_analysis['strongest_bonds'][:5]}")

# Analyze behavior patterns
behavior = sim.analyzer.analyze_behavior_patterns()
print(f"Location Distribution: {behavior['location_distribution']}")
print(f"Needs Summary: {behavior['needs_summary']}")

# Find social clusters
clusters = sim.analyzer.find_social_clusters()
print(f"Social Groups: {clusters}")

# Get NPCs in critical state
critical = behavior['npcs_in_critical_state']
for npc_info in critical:
    print(f"{npc_info['name']}: {npc_info['issues']}")

# Generate and export full report
report = sim.analyzer.generate_comprehensive_report()
sim.analyzer.export_report("my_analysis.json")

# Get visualization data for graphs
graph_data = sim.analyzer.get_relationship_graph_data(min_affinity=20)
# graph_data has 'nodes' and 'edges' for visualization libraries
```

#### Analysis Metrics Provided

**Relationship Metrics:**
- Total relationships count
- Average affinity level
- Network density (interconnectedness)
- Most/least connected NPCs
- Strongest bonds identification
- Relationship type distribution (best friends, friends, acquaintances, enemies)

**Behavior Metrics:**
- Location distribution (where NPCs are)
- Mood distribution
- Needs analysis (averages, mins, maxes, critical counts)
- NPCs in critical states (starving, exhausted, lonely, etc.)

**Event Metrics:**
- Event counts by type
- Total events tracked
- Recent events by category
- Upcoming milestones

**Social Structure:**
- Social cluster detection
- Friend group identification
- Community analysis

### Output Format

```python
{
    'time': {
        'current_time': 'Monday, September 01, 2025 08:00 AM',
        'total_days': 1,
        'season': 'autumn',
        'weather': 'Clear'
    },
    'relationships': {
        'total_relationships': 150,
        'avg_affinity': 45.2,
        'network_density': 0.342,
        'most_connected': 'Sarah Madison',
        'strongest_bonds': [...]
    },
    'behaviors': {
        'location_distribution': {...},
        'mood_distribution': {...},
        'needs_summary': {...},
        'npcs_in_critical_state': [...]
    },
    'events': {...},
    'social_clusters': [...]
}
```

---

## 🆕 Feature 5: Milestone & Event Tracking

Advanced event tracking system that records major life events and milestones.

### Features

- **Automatic Detection**: Birthdays, relationship changes, location moves
- **Manual Recording**: Add custom milestones anytime
- **Event Categories**: 15+ types including birthdays, romances, achievements, conflicts
- **Importance Levels**: Minor, Moderate, Major, Life-changing
- **Timeline Generation**: Chronological event history
- **NPC-Specific History**: Personal timeline for each NPC
- **Export Capabilities**: Save milestones to JSON

### Milestone Types

```
BIRTHDAY, RELATIONSHIP_FORMED, RELATIONSHIP_BROKEN,
ROMANCE_STARTED, ROMANCE_ENDED, MARRIAGE, PREGNANCY,
BIRTH, DEATH, JOB_CHANGE, MOVE, ACHIEVEMENT, CONFLICT,
RESOLUTION, SCANDAL, SECRET_REVEALED, HEALTH_EVENT,
CRIME, EDUCATION, OTHER
```

### Usage

#### Automatic Tracking

The system automatically detects and records:

- **Birthdays**: When NPCs age up
- **Relationship Milestones**:
  - Affinity increases to 70+ (close friends formed)
  - Affinity increases to 80+ (romance started)
  - Affinity drops below 20 from 50+ (relationship broken)
- **Location Changes**: When NPCs move houses

```python
from simulation_v2 import WillowCreekSimulation

sim = WillowCreekSimulation(num_npcs=0)

# Milestones are tracked automatically as you run
sim.run(num_steps=100, time_step_hours=1.0)

# View recent milestones
sim.milestones.print_recent_milestones(days=7)

# Get statistics
stats = sim.milestones.get_statistics()
print(f"Total Milestones: {stats['total_milestones']}")
print(f"By Type: {stats['by_type']}")
```

#### Manual Recording

```python
from systems.milestone_tracker import MilestoneType, MilestoneImportance

# Record custom milestone
sim.milestones.record_milestone(
    milestone_type=MilestoneType.ACHIEVEMENT,
    importance=MilestoneImportance.MAJOR,
    primary_npc="Sarah Madison",
    secondary_npcs=["David Madison", "Eve Madison"],
    description="Sarah won the art competition!",
    location="Art Cooperative",
    details={'prize': '1st place', 'category': 'painting'},
    emotional_impact="positive",
    tags=['art', 'achievement', 'public']
)

# Record scandal
sim.milestones.record_milestone(
    milestone_type=MilestoneType.SCANDAL,
    importance=MilestoneImportance.MAJOR,
    primary_npc="Nina Blake",
    description="Nina's affair was discovered",
    emotional_impact="negative",
    tags=['scandal', 'secret', 'drama']
)
```

#### Querying Milestones

```python
# Get NPC's personal history
history = sim.milestones.get_npc_history("Sarah Madison", limit=10)
for milestone in history:
    print(f"Day {milestone.day}: {milestone.description}")

# Get recent milestones
recent = sim.milestones.get_recent_milestones(days=7, limit=20)

# Get by type
birthdays = sim.milestones.get_milestones_by_type(
    MilestoneType.BIRTHDAY,
    limit=20
)

# Get only major events
major_events = sim.milestones.get_major_milestones(limit=50)

# Generate timeline
timeline = sim.milestones.generate_timeline()  # All events
npc_timeline = sim.milestones.generate_timeline(npc_name="Sarah Madison")
```

#### Export & Statistics

```python
# Export all milestones
sim.milestones.export_milestones("milestones.json")

# Get statistics
stats = sim.milestones.get_statistics()
# {
#     'total_milestones': 1547,
#     'by_type': {'birthday': 42, 'relationship_formed': 234, ...},
#     'by_importance': {'MINOR': 890, 'MODERATE': 450, ...},
#     'npcs_with_milestones': 68,
#     'recent_7_days': 45
# }
```

### Milestone Data Structure

```python
{
    'type': 'romance_started',
    'importance': 3,  # MAJOR
    'day': 5,
    'time': 'Monday, September 05, 2025 02:30 PM',
    'primary_npc': 'Sarah Madison',
    'secondary_npcs': ['David Madison'],
    'description': 'Sarah Madison and David Madison started a romance',
    'location': 'Downtown Café',
    'details': {'affinity': 82},
    'tags': ['romance', 'love'],
    'emotional_impact': 'positive'
}
```

---

## 🆕 Feature 6: Personality-Driven AI

Enhanced autonomous behavior with personality-based decision making.

### Features

- **Trait Extraction**: Automatically extracts personality from NPC data
- **Decision Modifiers**: Personality affects all choices
- **Mood Integration**: Emotional states influence behavior
- **Goal Prioritization**: Reorder goals based on personality
- **Reaction Generation**: Personality-appropriate responses
- **Consistency Checking**: Validate actions match character

### Personality Traits

```
OUTGOING / SHY
AMBITIOUS / LAZY
KIND / MEAN
BRAVE / FEARFUL
IMPULSIVE / CAUTIOUS
ROMANTIC / PRACTICAL
CREATIVE / LOGICAL
OPTIMISTIC / PESSIMISTIC
```

### Usage

#### Personality Extraction

```python
from simulation_v2 import WillowCreekSimulation

sim = WillowCreekSimulation(num_npcs=0)

# Get personality profile
npc = sim.npcs[0]
profile = sim.personality.get_personality_summary(npc)

print(f"Name: {profile['name']}")
print(f"Traits: {profile['traits']}")
print(f"Tendencies: {profile['behavioral_tendencies']}")
print(f"Modifiers: {profile['decision_modifiers']}")

# Example output:
# Name: Sarah Madison
# Traits: ['creative', 'outgoing', 'kind']
# Tendencies: ['Seeks social interaction', 'Values romance', 'Helps others']
# Modifiers: {'social_actions': '+50% weight', 'work_study': '+40% weight'}
```

#### Decision Making

```python
# Present options to personality engine
options = [
    {
        'action': 'attend_party',
        'location': 'Community Center',
        'weight': 1.0,
        'type': 'social'
    },
    {
        'action': 'study_alone',
        'location': 'Library',
        'weight': 1.0,
        'type': 'solitary'
    },
    {
        'action': 'help_friend',
        'location': 'Friend House',
        'weight': 1.0,
        'type': 'altruistic'
    }
]

# Let personality decide
decision = sim.personality.make_decision(
    npc,
    options,
    context={'mood': npc.mood, 'urgent_need': 'social'}
)

print(f"Decision: {decision['action']} at {decision['location']}")
print(f"Final weight: {decision['final_weight']}")

# Outgoing NPCs will boost 'attend_party'
# Shy NPCs will boost 'study_alone'
# Kind NPCs will boost 'help_friend'
```

#### Personality Modifiers

Different traits modify decision weights:

- **OUTGOING**: Social actions +50%, Home actions -50%
- **SHY**: Social actions -50%, Home actions +30%
- **AMBITIOUS**: Work/study +40%
- **LAZY**: Work/study -40%, Rest +40%
- **IMPULSIVE**: Risky actions +50%
- **CAUTIOUS**: Risky actions -60%, Safe actions +30%
- **ROMANTIC**: Romance actions +60%
- **KIND**: Help actions +50%
- **MEAN**: Help actions -50%, Conflict +30%

#### Goal Prioritization

```python
# Get NPC's goals
from systems.goals_system import Goal

goals = [
    Goal(description="Make friends", category="social", urgency=0.5, started_day=1),
    Goal(description="Get promotion", category="career", urgency=0.7, started_day=1),
    Goal(description="Find romance", category="romance", urgency=0.6, started_day=1),
]

# Reorder based on personality
prioritized = sim.personality.prioritize_goals(npc, goals)

# OUTGOING npc will prioritize social goals higher
# AMBITIOUS npc will prioritize career goals higher
# ROMANTIC npc will prioritize romance goals higher
```

#### Reaction Generation

```python
# Generate personality-appropriate reaction
reaction = sim.personality.generate_reaction(
    npc,
    event_type='good_news',
    event_context={'importance': 'major'}
)

# OPTIMISTIC: 'elated'
# PESSIMISTIC: 'cautiously_happy'
# BRAVE: 'determined'

# Conflict reaction
reaction = sim.personality.generate_reaction(npc, 'conflict')
# BRAVE: 'confrontational'
# FEARFUL: 'scared'
# MEAN: 'aggressive'
# KIND: 'conciliatory'
```

#### Consistency Checking

```python
# Check if action fits personality
is_consistent, score = sim.personality.is_action_consistent(
    npc,
    action='public_speech'
)

# SHY npc: (False, 0.2)
# OUTGOING npc: (True, 0.9)

print(f"Consistent: {is_consistent}, Score: {score:.2f}")
```

### Integration with Autonomous System

The personality engine can be integrated with the autonomous system for smarter NPCs:

```python
# In autonomous behavior:
traits = sim.personality.extract_traits(npc)

if PersonalityTrait.OUTGOING in traits:
    # Boost chance of going to social locations
    pass
elif PersonalityTrait.SHY in traits:
    # Boost chance of staying home
    pass
```

---

## 🔧 Complete Integration Example

```python
from simulation_v2 import WillowCreekSimulation
from systems.milestone_tracker import MilestoneType, MilestoneImportance

# Create simulation with all enhanced features
sim = WillowCreekSimulation(num_npcs=0)

# Run for a week
print("Running 7-day simulation...")
for day in range(1, 8):
    sim.run(num_steps=24, time_step_hours=1.0)

    # Daily analysis
    print(f"\n--- Day {day} ---")

    # Check milestones
    recent = sim.milestones.get_recent_milestones(days=1, limit=5)
    if recent:
        print(f"Milestones today: {len(recent)}")
        for m in recent[:3]:
            print(f"  • {m.description}")

    # Check critical NPCs
    behavior = sim.analyzer.analyze_behavior_patterns()
    critical = behavior['npcs_in_critical_state']
    if critical:
        print(f"NPCs needing attention: {len(critical)}")

# Final comprehensive analysis
print("\n" + "=" * 70)
print("FINAL ANALYSIS")
print("=" * 70)

# Relationship analysis
rel = sim.analyzer.analyze_relationships()
print(f"\nRelationships: {rel['total_relationships']} total")
print(f"Network Density: {rel['network_density']}")
print(f"Most Connected: {rel['most_connected']}")

# Milestone summary
stats = sim.milestones.get_statistics()
print(f"\nMilestones: {stats['total_milestones']} total")
print(f"Types: {list(stats['by_type'].keys())}")

# Export everything
print("\nExporting data...")
sim.analyzer.export_report("week_analysis.json")
sim.milestones.export_milestones("week_milestones.json")
sim.save_checkpoint("week_1", "After first week")

print("\n✓ Complete!")
```

---

## 📊 New API Endpoints (Web Dashboard)

The web dashboard has been extended with new endpoints:

```
GET  /api/milestones/recent?days=7  - Get recent milestones
GET  /api/milestones/npc/<name>     - Get NPC's history
GET  /api/analysis/summary          - Get analysis summary
GET  /api/analysis/clusters         - Get social clusters
GET  /api/personality/<name>        - Get NPC personality profile
```

---

## 🎯 Use Cases

### 1. Story Generation

```python
# Get dramatic events for story
major_events = sim.milestones.get_major_milestones(limit=20)
for event in major_events:
    if event.milestone_type in [MilestoneType.SCANDAL, MilestoneType.ROMANCE_STARTED]:
        print(f"Story Beat: {event.description}")
```

### 2. Character Development Tracking

```python
# Track a character's journey
npc_name = "Sarah Madison"
history = sim.milestones.get_npc_history(npc_name, limit=100)

print(f"\n{npc_name}'s Journey:")
for milestone in history:
    print(f"Day {milestone.day}: {milestone.description}")
```

### 3. Social Network Analysis

```python
# Analyze town's social structure
clusters = sim.analyzer.find_social_clusters()
print(f"Found {len(clusters)} friend groups")

for i, cluster in enumerate(clusters, 1):
    print(f"\nGroup {i}: {', '.join(cluster)}")
```

### 4. Behavior Prediction

```python
# Predict NPC behavior based on personality
npc = sim.npc_dict["Nina Blake"]
profile = sim.personality.get_personality_summary(npc)

print(f"{npc.full_name} is likely to:")
for tendency in profile['behavioral_tendencies']:
    print(f"  - {tendency}")
```

---

## 🐛 Troubleshooting

### High Milestone Count

If you're getting too many milestones:
- Adjust detection thresholds in `milestone_tracker.py`
- Filter by importance level when querying
- Focus on major milestones only

### Performance with Large Populations

For 100+ NPCs:
- Use `analyzer.get_relationship_graph_data(min_affinity=40)` to reduce edges
- Limit analysis to specific NPCs
- Run analysis less frequently

### Personality Not Affecting Behavior

Ensure the autonomous system is using personality checks:
```python
# Check if personality is integrated
traits = sim.personality.extract_traits(npc)
print(f"Traits detected: {traits}")
```

---

## 📝 Future Enhancements

Potential improvements:

- [ ] Machine learning for behavior prediction
- [ ] Automated story arc detection
- [ ] Personality evolution over time
- [ ] Advanced social network metrics (centrality, betweenness)
- [ ] Milestone triggers (events cause other events)
- [ ] Character arc completion tracking
- [ ] Emotional trajectory analysis
- [ ] Predictive analytics for relationships

---

## 📚 API Reference

### SimulationAnalyzer

```python
analyzer = SimulationAnalyzer(sim)

# Main methods
analyzer.analyze_relationships() -> Dict
analyzer.analyze_behavior_patterns() -> Dict
analyzer.analyze_events() -> Dict
analyzer.find_social_clusters() -> List[List[str]]
analyzer.generate_comprehensive_report() -> Dict
analyzer.export_report(filename) -> str
analyzer.print_summary() -> None
analyzer.get_relationship_graph_data(min_affinity) -> Dict
```

### MilestoneTracker

```python
tracker = MilestoneTracker(sim)

# Recording
tracker.record_milestone(type, importance, npc, ...) -> Milestone
tracker.update(npcs) -> None  # Auto-detect

# Querying
tracker.get_npc_history(name, limit) -> List[Milestone]
tracker.get_recent_milestones(days, limit) -> List[Milestone]
tracker.get_milestones_by_type(type, limit) -> List[Milestone]
tracker.get_major_milestones(limit) -> List[Milestone]

# Utility
tracker.generate_timeline(npc_name?) -> List[Dict]
tracker.get_statistics() -> Dict
tracker.export_milestones(filename) -> None
tracker.print_recent_milestones(days) -> None
```

### PersonalityEngine

```python
engine = PersonalityEngine()

# Extraction
engine.extract_traits(npc) -> List[PersonalityTrait]

# Decision Making
engine.make_decision(npc, options, context?) -> Dict
engine.prioritize_goals(npc, goals) -> List[Goal]

# Reactions
engine.generate_reaction(npc, event_type, context?) -> str
engine.is_action_consistent(npc, action, context?) -> Tuple[bool, float]

# Utility
engine.get_personality_summary(npc) -> Dict
```

---

**Enjoy your enhanced simulation with deep analytics and personality-driven AI! 🚀**
