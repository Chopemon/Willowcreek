# check_files.py - Verify all required files are present
import os
import sys

print("=" * 70)
print("WILLOW CREEK FILE CHECKER")
print("=" * 70)
print(f"\nChecking directory: {os.getcwd()}\n")

required_files = [
    # Core files
    ("narrative_chat.py", "Main interface"),
    ("simulation_v2.py", "Main simulation engine"),
    ("npc.py", "NPC definitions"),
    ("time_system.py", "Time tracking"),
    ("world_state.py", "World state"),
    ("world_snapshot_builder.py", "AI narrator data"),
    
    # System files
    ("needs.py", "Needs system"),
    ("relationships.py", "Relationships"),
    ("autonomous.py", "Autonomous behavior"),
    ("goals_system.py", "Goals"),
    ("reputation_system.py", "Reputation"),
    ("environmental_triggers.py", "Environment"),
    ("emotional_contagion.py", "Emotions"),
    ("memory_system.py", "Memory"),
    ("seasonal_dynamics.py", "Seasons"),
    ("schedule_system.py", "Schedules"),
    
    # Biology systems
    ("female_biology_system.py", "Female biology"),
    ("pregnancy_system.py", "Pregnancy"),
    ("health_disease_system.py", "Health"),
    ("growth_development_system.py", "Growth"),
    
    # Drama systems
    ("skill_progression.py", "Skills"),
    ("consequence_cascades.py", "Consequences"),
    ("dynamic_triggers.py", "Dynamic triggers"),
    ("birthday_system.py", "Birthdays"),
    ("event_system.py", "Events"),
    ("school_drama_system.py", "School drama"),
    ("addiction_system.py", "Addictions"),
    ("crime_system.py", "Crime"),
    ("micro_interactions_system.py", "Micro interactions"),
    
    # Special systems
    ("npc_quirks_system.py", "NPC quirks"),
    ("sexual_activity_system.py", "Sexual activity"),
    ("debug_overlay.py", "Debug"),
]

required_folders = [
    ("npc_data", "NPC data folder"),
]

required_data_files = [
    ("npc_data/npc_roster.json", "Main NPC roster"),
    ("npc_data/npc_generic.json", "Generic NPCs"),
    ("npc_data/Malcolm_Newt.json", "Malcolm data"),
]

missing = []
found = []

print("CHECKING PYTHON FILES:")
print("-" * 70)
for filename, description in required_files:
    if os.path.exists(filename):
        print(f"  ✓ {filename:<35} ({description})")
        found.append(filename)
    else:
        print(f"  ✗ {filename:<35} MISSING!")
        missing.append(filename)

print("\nCHECKING FOLDERS:")
print("-" * 70)
for folder, description in required_folders:
    if os.path.isdir(folder):
        print(f"  ✓ {folder:<35} ({description})")
        found.append(folder)
    else:
        print(f"  ✗ {folder:<35} MISSING!")
        missing.append(folder)

print("\nCHECKING DATA FILES:")
print("-" * 70)
for filepath, description in required_data_files:
    if os.path.exists(filepath):
        print(f"  ✓ {filepath:<35} ({description})")
        found.append(filepath)
    else:
        print(f"  ✗ {filepath:<35} MISSING!")
        missing.append(filepath)

print("\n" + "=" * 70)
print(f"SUMMARY: {len(found)} found, {len(missing)} missing")
print("=" * 70)

if missing:
    print("\n⚠️  MISSING FILES:")
    for item in missing:
        print(f"    - {item}")
    print("\nYou need to copy all files from /mnt/project/ to your local directory.")
    print("Make sure all .py files and the npc_data folder are present!")
    sys.exit(1)
else:
    print("\n✓ All required files found!")
    print("You can now run: python narrative_chat.py")
    sys.exit(0)
