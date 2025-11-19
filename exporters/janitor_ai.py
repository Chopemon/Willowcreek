"""
JanitorAI Exporter - Convert Python simulation state to JavaScript
"""

from typing import TYPE_CHECKING
from pathlib import Path
import json

if TYPE_CHECKING:
    from core.simulation import WillowCreekSimulation


def export_to_js(simulation: 'WillowCreekSimulation', output_file: str):
    """
    Export simulation state to JavaScript for JanitorAI
    
    Args:
        simulation: WillowCreekSimulation instance
        output_file: Output JavaScript file path
    """
    print(f"\n=== EXPORTING TO JANITOR AI FORMAT ===")
    print(f"Output file: {output_file}\n")
    
    # Convert NPCs to JS format
    npcs_js = [npc.to_js_format() for npc in simulation.npcs]
    
    # Convert relationships to JS format
    relationships_js = simulation.relationships.to_js_format()
    
    # Time state
    time_js = {
        'totalDays': simulation.time.total_days,
        'currentDay': simulation.time.day_name,
        'dayOfWeek': simulation.time.day_of_week + 1,  # JS uses 1-7
        'date': simulation.time.get_date_string(),
        'month': simulation.time.current_time.month,
        'dayOfMonth': simulation.time.current_time.day,
        'year': simulation.time.current_time.year,
        'hour': simulation.time.hour,
        'minute': simulation.time.minute,
        'season': simulation.time.season,
        'timeString': simulation.time.get_time_string()
    }
    
    # Generate JavaScript code
    js_code = f"""// =================================================================
// WILLOW CREEK 2025 - AUTO-GENERATED FROM PYTHON SIMULATION
// =================================================================
// Generated: {simulation.time.current_time.isoformat()}
// Simulation Day: {simulation.time.total_days}
// NPCs: {len(npcs_js)}
// Relationships: {len(relationships_js)}
// =================================================================

console.log("=== [PYTHON-EXPORT] Loading simulation state ===");

const shared = context.character.shared_context;

// =================================================================
// NPCS
// =================================================================

shared.npcs = {json.dumps(npcs_js, indent=2)};

console.log("✓ Loaded " + shared.npcs.length + " NPCs");

// =================================================================
// RELATIONSHIPS
// =================================================================

shared.npcRelationships = {json.dumps(relationships_js, indent=2)};

console.log("✓ Loaded " + Object.keys(shared.npcRelationships).length + " relationships");

// =================================================================
// TIME SYSTEM
// =================================================================

shared.time = {json.dumps(time_js, indent=2)};

console.log("✓ Time: " + shared.time.currentDay + " - " + shared.time.timeString);
console.log("✓ Season: " + shared.time.season);

// =================================================================
// STATISTICS
// =================================================================

shared.simulationStats = {json.dumps(simulation.statistics, indent=2)};

console.log("=== [PYTHON-EXPORT] Load complete ===");
console.log("Total simulation days: " + shared.time.totalDays);
"""
    
    # Write to file with UTF-8 encoding (fixes Windows Unicode issues)
    Path(output_file).write_text(js_code, encoding='utf-8')
    
    print(f"✓ Exported {len(npcs_js)} NPCs")
    print(f"✓ Exported {len(relationships_js)} relationships")
    print(f"✓ Current day: {simulation.time.total_days}")
    print(f"✓ JavaScript file created: {output_file}")
    print(f"\n=== EXPORT COMPLETE ===\n")


def create_janitor_ai_script(
    npcs: list,
    relationships: dict,
    time_state: dict,
    output_file: str
):
    """
    Create standalone JanitorAI script from components
    
    Args:
        npcs: List of NPC dictionaries
        relationships: Relationship dictionary
        time_state: Time state dictionary
        output_file: Output file path
    """
    js_code = f"""// Willow Creek 2025 - JanitorAI Import
const shared = context.character.shared_context;

shared.npcs = {json.dumps(npcs, indent=2)};
shared.npcRelationships = {json.dumps(relationships, indent=2)};
shared.time = {json.dumps(time_state, indent=2)};

console.log("✓ Loaded simulation state");
"""
    
    Path(output_file).write_text(js_code)


if __name__ == "__main__":
    # Demo
    from core.simulation import WillowCreekSimulation
    
    sim = WillowCreekSimulation(num_npcs=5)
    sim.run(num_steps=10)
    export_to_js(sim, "test_export.js")
