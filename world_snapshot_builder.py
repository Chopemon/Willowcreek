# world_snapshot_builder.py - Comprehensive World State for AI Narrator
# DEFENSIVE VERSION - checks all attributes before use
# FIXED: Bridge functions moved to global scope, indentation corrected.
# MODIFIED: Removed the call to _build_nearby_npcs() in build_complete_snapshot.

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import datetime

if TYPE_CHECKING:
    from simulation_v2 import WillowCreekSimulation
    from entities.npc import NPC


class WorldSnapshotBuilder:
    """
    Builds complete omniscient world snapshots for the AI narrator.
    Defensive version that handles missing attributes gracefully.
    """
    
    def __init__(self, sim: 'WillowCreekSimulation'):
        self.sim = sim
    
    def build_complete_snapshot(self, malcolm: 'NPC') -> str:
        """
        Generate full world state including ALL systems.
        This is what the AI narrator sees.
        """
        sections = []
        
        try:
            sections.append(self._build_time_and_environment())
        except Exception as e:
            sections.append(f"## TIME & ENVIRONMENT\n[Error: {e}]")
        
        try:
            sections.append(self._build_malcolm_state(malcolm))
        except Exception as e:
            sections.append(f"## MALCOLM STATE\n[Error: {e}]")
        
        # --- NEARBY NPCS REMOVED DUE TO INACCURATE LOCATION DATA ---
        # try:
        #     sections.append(self._build_nearby_npcs(malcolm))
        # except Exception as e:
        #     sections.append(f"## NEARBY NPCs\n[Error: {e}]")
        
        try:
            sections.append(self._build_all_npc_states())
        except Exception as e:
            sections.append(f"## ALL NPCs\n[Error: {e}]")
        
        try:
            sections.append(self._build_relationships())
        except Exception as e:
            sections.append(f"## RELATIONSHIPS\n[Error: {e}]")
        
        try:
            sections.append(self._build_goals())
        except Exception as e:
            sections.append(f"## GOALS\n[Error: {e}]")
        
        try:
            sections.append(self._build_biology_health())
        except Exception as e:
            sections.append(f"## BIOLOGY\n[Error: {e}]")
        
        return "\n\n".join(sections)
    
    def _build_time_and_environment(self) -> str:
        """Current time, weather, season"""
        time_str = self.sim.time.get_datetime_string()
        day_of_week = self.sim.time.current_time.strftime("%A")
        season = getattr(self.sim.time, 'season', 'autumn').title()
        weather = getattr(self.sim.world, 'weather', 'Clear')
        temp = getattr(self.sim.world, 'temperature', 55)
        
        return f"""## TIME & ENVIRONMENT
{time_str} ({day_of_week})
Season: {season} | Weather: {weather} | Temperature: {temp}°F
Day #{self.sim.time.total_days} of simulation"""
    
    def _build_malcolm_state(self, malcolm: 'NPC') -> str:
        """Malcolm's complete physical and psychological state"""
        n = malcolm.needs
        p = malcolm.psyche
        
        # Mood handling
        mood_display = "unknown"
        try:
            if hasattr(malcolm, 'mood'):
                if isinstance(malcolm.mood, str):
                    mood_display = malcolm.mood
                elif hasattr(malcolm.mood, 'value'):
                    mood_display = malcolm.mood.value
                elif hasattr(malcolm.mood, 'current_mood'):
                    if hasattr(malcolm.mood.current_mood, 'value'):
                        mood_display = malcolm.mood.current_mood.value
                    else:
                        mood_display = str(malcolm.mood.current_mood)
        except:
            pass
        
        # Biological state
        bio_state = ""
        try:
            if hasattr(self.sim, 'female_biology') and hasattr(self.sim.female_biology, 'cycles'):
                if malcolm.full_name in self.sim.female_biology.cycles:
                    fb = self.sim.female_biology.cycles[malcolm.full_name]
                    bio_state = f"\nCycle: Day {fb.day_in_cycle}/28 | Phase: {fb.phase}"
                    if fb.phase == "ovulation":
                        bio_state += " (OVULATING)"
                    elif fb.phase == "menstruation":
                        bio_state += " (MENSTRUATING)"
        except:
            pass
        
        return f"""## MALCOLM NEWT - COMPLETE STATE
Location: {getattr(malcolm, 'current_location', 'Unknown')}
Age: {malcolm.age} | Occupation: {getattr(malcolm, 'occupation', 'Unknown')}

PHYSICAL NEEDS:
- Hunger: {n.hunger:.1f}/100 {"[STARVING]" if n.hunger < 20 else ""}
- Energy: {n.energy:.1f}/100 {"[EXHAUSTED]" if n.energy < 20 else ""}
- Hygiene: {n.hygiene:.1f}/100 {"[FILTHY]" if n.hygiene < 30 else ""}
- Bladder: {n.bladder:.1f}/100 {"[DESPERATE]" if n.bladder < 20 else ""}
- Horny: {n.horny:.1f}/100 {"[SEXUALLY DESPERATE]" if n.horny > 85 else ""}

PSYCHOLOGICAL STATE:
- Lonely: {p.lonely:.1f}/100 {"[CRUSHING LONELINESS]" if p.lonely > 80 else ""}
- Mood: {mood_display.upper()}{bio_state}"""
    
    def _build_nearby_npcs(self, malcolm: 'NPC') -> str:
        """NPCs in Malcolm's current location"""
        nearby = [
            npc for npc in self.sim.npcs
            if getattr(npc, 'current_location', 'Void') == getattr(malcolm, 'current_location', 'Void')
            and npc.full_name != malcolm.full_name
        ]
        
        if not nearby:
            return f"## NEARBY NPCs\nNone - Malcolm is alone at {getattr(malcolm, 'current_location', 'Unknown')}"
        
        lines = [f"## NEARBY NPCs ({len(nearby)} present at {getattr(malcolm, 'current_location', 'Unknown')})"]
        
        for npc in nearby[:10]:
            # Mood handling
            mood_display = "unknown"
            try:
                if isinstance(npc.mood, str):
                    mood_display = npc.mood
                elif hasattr(npc.mood, 'value'):
                    mood_display = npc.mood.value
            except:
                pass
            
            # States
            states = []
            if npc.needs.horny > 85:
                states.append("HORNY")
            if npc.psyche.lonely > 80:
                states.append("LONELY")
            
            # Ovulation check
            try:
                if hasattr(self.sim, 'female_biology') and hasattr(self.sim.female_biology, 'cycles'):
                    if npc.full_name in self.sim.female_biology.cycles:
                        fb = self.sim.female_biology.cycles[npc.full_name]
                        if fb.phase == "ovulation":
                            states.append("OVULATING")
            except:
                pass
            
            state_str = f" [{' | '.join(states)}]" if states else ""
            
            lines.append(
                f"  • {npc.full_name} ({npc.age}, {getattr(npc, 'occupation', 'Unknown')})\n"
                f"    Horny: {npc.needs.horny:.0f} | Lonely: {npc.psyche.lonely:.0f} | Mood: {mood_display}{state_str}"
            )
        
        return "\n".join(lines)
    
    def _build_all_npc_states(self) -> str:
        """Critical states for ALL NPCs"""
        lines = [f"## ALL TOWN RESIDENTS ({len(self.sim.npcs)} total)"]
        
        # Group by location
        loc_map = {}
        for npc in self.sim.npcs:
            loc = getattr(npc, 'current_location', 'Unknown')
            loc_map.setdefault(loc, []).append(npc)
        
        for location, npcs in sorted(loc_map.items()):
            lines.append(f"\n### {location} ({len(npcs)} present)")
            for npc in npcs[:15]:
                flags = []
                if npc.needs.horny > 85:
                    flags.append("HORNY")
                if npc.psyche.lonely > 80:
                    flags.append("LONELY")
                if npc.needs.energy < 20:
                    flags.append("EXHAUSTED")
                
                flag_str = f" [{', '.join(flags)}]" if flags else ""
                
                # Mood
                mood_display = "?"
                try:
                    if isinstance(npc.mood, str):
                        mood_display = npc.mood
                    elif hasattr(npc.mood, 'value'):
                        mood_display = npc.mood.value
                except:
                    pass
                
                lines.append(
                    f"  • {npc.full_name} ({npc.age}): H:{npc.needs.horny:.0f} L:{npc.psyche.lonely:.0f} {mood_display}{flag_str}"
                )
        
        return "\n".join(lines)
    
    def _build_relationships(self) -> str:
        """Relationship information"""
        lines = ["## RELATIONSHIPS"]
        
        # Check if relationships system exists
        if not hasattr(self.sim, 'relationships'):
            lines.append("\n[Relationship system not available]")
            return "\n".join(lines)
        
        # Count relationships
        try:
            rel_count = len(getattr(self.sim.relationships, 'relationships', {}))
            lines.append(f"\n### Total Relationships: {rel_count}")
        except:
            lines.append("\n### Relationships: Unknown")
        
        return "\n".join(lines)
    
    def _build_goals(self) -> str:
        """Goals and motivations"""
        lines = ["## GOALS & MOTIVATIONS"]
        
        if not hasattr(self.sim, 'goals'):
            lines.append("\n[Goals system not available]")
            return "\n".join(lines)
        
        # Try to get Malcolm's goals
        try:
            if hasattr(self.sim.goals, 'get_active_goals') and hasattr(self.sim, 'malcolm'):
                malcolm_goals = self.sim.goals.get_active_goals(self.sim.malcolm.full_name)
                if malcolm_goals:
                    lines.append("\n### Malcolm's Goals:")
                    for goal in malcolm_goals[:5]:
                        lines.append(f"  • {goal.description}")
        except Exception as e:
            lines.append(f"\n[Could not load goals: {e}]")
        
        return "\n".join(lines)
    
    def _build_biology_health(self) -> str:
        """Biology and health states"""
        lines = ["## BIOLOGY & HEALTH"]
        
        # Menstrual cycles
        try:
            if hasattr(self.sim, 'female_biology') and hasattr(self.sim.female_biology, 'cycles'):
                ovulating = []
                menstruating = []
                
                for npc in self.sim.npcs:
                    if npc.full_name in self.sim.female_biology.cycles:
                        fb = self.sim.female_biology.cycles[npc.full_name]
                        if fb.phase == "ovulation":
                            ovulating.append(npc.full_name)
                        elif fb.phase == "menstruation":
                            menstruating.append(npc.full_name)
                
                if ovulating:
                    lines.append(f"\n### Ovulating: {', '.join(ovulating[:10])}")
                if menstruating:
                    lines.append(f"### Menstruating: {', '.join(menstruating[:10])}")
        except Exception as e:
            lines.append(f"\n[Biology data error: {e}]")
        
        # Pregnancies
        try:
            if hasattr(self.sim, 'pregnancy') and hasattr(self.sim.pregnancy, 'states'):
                pregnant = []
                for npc in self.sim.npcs:
                    if npc.full_name in self.sim.pregnancy.states:
                        pd = self.sim.pregnancy.states[npc.full_name]
                        if pd.is_pregnant:
                            weeks = pd.pregnancy_day // 7
                            pregnant.append(f"{npc.full_name} ({weeks}w)")
                
                if pregnant:
                    lines.append(f"\n### Pregnant: {', '.join(pregnant)}")
        except Exception as e:
            lines.append(f"\n[Pregnancy data error: {e}]")
        
        return "\n".join(lines)


# ============================================================================
# GLOBAL BRIDGE FUNCTIONS (REQUIRED FOR WEB APP & NARRATIVE CHAT)
# ============================================================================

def create_narrative_context(sim: 'WillowCreekSimulation', malcolm: 'NPC') -> str:
    """
    Bridge function used by narrative_chat.py to get the full prompt.
    """
    builder = WorldSnapshotBuilder(sim)
    return builder.build_complete_snapshot(malcolm)

def build_frontend_snapshot(sim: 'WillowCreekSimulation', malcolm: 'NPC') -> Dict[str, Any]:
    """
    Bridge function used by web_app.py to populate the UI.
    Returns structured data for the enhanced dashboard.
    """
    # Get the full text snapshot for backward compatibility
    full_text = create_narrative_context(sim, malcolm)

    # Extract Malcolm's section for the side panel
    malcolm_stats = "Check main output for details."

    # Search for Malcolm's section header
    lower_text = full_text.lower()
    start_markers = ["## malcolm", "### malcolm", "malcolm's status", "malcolm state"]

    start_idx = -1
    for marker in start_markers:
        idx = lower_text.find(marker)
        if idx != -1:
            start_idx = idx
            break

    if start_idx != -1:
        # We found the start of Malcolm's section
        rest_of_text = full_text[start_idx:]

        # Find the NEXT section (denoted by ##) to know where to stop
        # Skip the first couple of chars so we don't find the header we just found
        next_section_idx = rest_of_text.find("##", 5)

        if next_section_idx != -1:
            malcolm_stats = rest_of_text[:next_section_idx].strip()
        else:
            malcolm_stats = rest_of_text.strip()

    # Build structured data for enhanced dashboard
    needs_data = {
        "hunger": getattr(malcolm.needs, 'hunger', 50),
        "energy": getattr(malcolm.needs, 'energy', 80),
        "hygiene": getattr(malcolm.needs, 'hygiene', 60),
        "bladder": getattr(malcolm.needs, 'bladder', 60),
        "fun": getattr(malcolm.needs, 'fun', 50),
        "social": getattr(malcolm.needs, 'social', 50),
        "horny": getattr(malcolm.needs, 'horny', 30)
    }

    psychological_data = {
        "lonely": getattr(malcolm.psyche, 'lonely', 20),
        "mood": getattr(malcolm, 'mood', 'Neutral'),
        "stress": 0  # Add if you have stress tracking
    }

    # Time and location data
    time_str = f"{sim.time.hour:02d}:{sim.time.minute:02d}"
    date_str = sim.time.get_datetime_string().split()[0:3]  # Get "Monday, September 01"
    date_str = " ".join(date_str)

    return {
        "full_context": full_text,
        "malcolm_stats": malcolm_stats,
        # Structured data for enhanced dashboard
        "needs": needs_data,
        "psychological": psychological_data,
        "location": getattr(malcolm, 'current_location', 'Unknown'),
        "time": time_str,
        "date": date_str,
        "age": getattr(malcolm, 'age', 30),
        "occupation": getattr(malcolm, 'occupation', '')
    }