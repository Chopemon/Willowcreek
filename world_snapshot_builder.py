# world_snapshot_builder.py - Comprehensive World State for AI Narrator
# DEFENSIVE VERSION - checks all attributes before use
# FIXED: Bridge functions moved to global scope, indentation corrected.
# MODIFIED: Removed the call to _build_nearby_npcs() in build_complete_snapshot.
# OPTIMIZED: Added smart caching for world snapshots and NPC states

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import datetime
from utils.cache_manager import world_snapshot_cache, npc_state_cache

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

        OPTIMIZED: Caches result for 60 seconds based on simulation time.
        """
        # Create cache key based on simulation time (changes every game hour/day)
        cache_key = f"snapshot_{self.sim.time.total_days}_{self.sim.time.hour}"

        # Check cache first
        cached = world_snapshot_cache.get(cache_key)
        if cached is not None:
            return cached

        sections = []

        try:
            sections.append(self._build_time_and_environment())
        except Exception as e:
            sections.append(f"## TIME & ENVIRONMENT\n[Error: {e}]")

        try:
            sections.append(self._build_malcolm_state(malcolm))
        except Exception as e:
            sections.append(f"## MALCOLM STATE\n[Error: {e}]")

        # Include recent events from scenario_buffer for the AI narrator
        try:
            sections.append(self._build_recent_events())
        except Exception as e:
            sections.append(f"## RECENT EVENTS\n[Error: {e}]")

        # --- NEARBY NPCS REMOVED DUE TO INACCURATE LOCATION DATA ---
        # try:
        #     sections.append(self._build_nearby_npcs(malcolm))
        # except Exception as e:
        #     sections.append(f"## NEARBY NPCs\n[Error: {e}]")

        try:
            sections.append(self._build_all_npc_states())
        except Exception as e:
            sections.append(f"## ALL NPCs\n[Error: {e}]")

        # OPTIMIZED: Only include non-empty sections
        try:
            rel_section = self._build_relationships()
            if rel_section:
                sections.append(rel_section)
        except Exception as e:
            sections.append(f"## RELATIONSHIPS\n[Error: {e}]")

        try:
            goals_section = self._build_goals()
            if goals_section:
                sections.append(goals_section)
        except Exception as e:
            sections.append(f"## GOALS\n[Error: {e}]")

        try:
            bio_section = self._build_biology_health()
            if bio_section:
                sections.append(bio_section)
        except Exception as e:
            sections.append(f"## BIOLOGY\n[Error: {e}]")

        result = "\n\n".join(sections)

        # Cache the result
        world_snapshot_cache.set(result, cache_key)

        return result
    
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

    def _build_recent_events(self) -> str:
        """Recent dramatic events that the AI narrator should incorporate"""
        if not hasattr(self.sim, 'scenario_buffer') or not self.sim.scenario_buffer:
            return ""  # No events to report

        lines = ["## RECENT EVENTS"]
        lines.append("**IMPORTANT: The following events just occurred and MUST be woven into the narrative:**\n")

        for event in self.sim.scenario_buffer:
            lines.append(f"  • {event}")

        return "\n".join(lines)

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
        """
        OPTIMIZED: Context-aware NPC filtering to reduce token usage.
        Only includes NPCs that are narratively relevant.
        """
        # Filter to only include narratively relevant NPCs
        relevant_npcs = []

        for npc in self.sim.npcs:
            # Skip Malcolm himself
            if npc.full_name == "Malcolm Newt":
                continue

            # Include if: High horny (>70), High lonely (>70), Low energy (<30)
            # OR recently interacted (would need interaction tracking)
            is_relevant = (
                npc.needs.horny > 70 or
                npc.psyche.lonely > 70 or
                npc.needs.energy < 30
            )

            if is_relevant:
                relevant_npcs.append(npc)

        # If too few relevant NPCs, include a few random ones for context
        if len(relevant_npcs) < 5:
            for npc in self.sim.npcs:
                if npc not in relevant_npcs and npc.full_name != "Malcolm Newt":
                    relevant_npcs.append(npc)
                    if len(relevant_npcs) >= 8:
                        break

        # Limit to max 15 NPCs to save tokens
        relevant_npcs = relevant_npcs[:15]

        if not relevant_npcs:
            return "## NOTABLE RESIDENTS\n[No NPCs currently in notable states]"

        lines = [f"## NOTABLE RESIDENTS ({len(relevant_npcs)} shown, {len(self.sim.npcs)} total)"]

        # Group by location for context
        loc_map = {}
        for npc in relevant_npcs:
            loc = getattr(npc, 'current_location', 'Unknown')
            loc_map.setdefault(loc, []).append(npc)

        for location, npcs in sorted(loc_map.items()):
            lines.append(f"\n### {location}")
            for npc in npcs:
                # Use abbreviated format to save tokens
                flags = []
                if npc.needs.horny > 85:
                    flags.append("HORNY")
                elif npc.needs.horny > 70:
                    flags.append("horny")

                if npc.psyche.lonely > 80:
                    flags.append("LONELY")
                elif npc.psyche.lonely > 70:
                    flags.append("lonely")

                if npc.needs.energy < 20:
                    flags.append("EXHAUSTED")

                # Check for ovulation (important for narrative)
                try:
                    if hasattr(self.sim, 'female_biology') and hasattr(self.sim.female_biology, 'cycles'):
                        if npc.full_name in self.sim.female_biology.cycles:
                            fb = self.sim.female_biology.cycles[npc.full_name]
                            if fb.phase == "ovulation":
                                flags.append("OVULATING")
                except:
                    pass

                flag_str = f" [{','.join(flags)}]" if flags else ""

                # Abbreviated format: Name (age): H:## L:## E:## [FLAGS]
                lines.append(
                    f"  • {npc.full_name} ({npc.age}): "
                    f"H:{npc.needs.horny:.0f} L:{npc.psyche.lonely:.0f} E:{npc.needs.energy:.0f}"
                    f"{flag_str}"
                )

        return "\n".join(lines)
    
    def _build_relationships(self) -> str:
        """
        OPTIMIZED: Relationship information (compact).
        Only shows count to save tokens.
        """
        # Check if relationships system exists
        if not hasattr(self.sim, 'relationships'):
            return ""  # Skip section if not available

        # Count relationships
        try:
            rel_count = len(getattr(self.sim.relationships, 'relationships', {}))
            if rel_count > 0:
                return f"## RELATIONSHIPS\nTotal active relationships: {rel_count}"
            else:
                return ""  # Skip if no relationships
        except:
            return ""  # Skip on error
    
    def _build_goals(self) -> str:
        """
        OPTIMIZED: Goals and motivations (compact).
        Only shows active goals if they exist.
        """
        if not hasattr(self.sim, 'goals'):
            return ""  # Skip if no goals system

        # Try to get Malcolm's goals
        try:
            if hasattr(self.sim.goals, 'get_active_goals') and hasattr(self.sim, 'malcolm'):
                malcolm_goals = self.sim.goals.get_active_goals(self.sim.malcolm.full_name)
                if malcolm_goals:
                    lines = ["## MALCOLM'S GOALS"]
                    for goal in malcolm_goals[:3]:  # Limit to 3 most important goals
                        lines.append(f"  • {goal.description}")
                    return "\n".join(lines)
        except:
            pass

        return ""  # Skip section if no goals or error
    
    def _build_biology_health(self) -> str:
        """
        OPTIMIZED: Biology and health states.
        Only shows if there are actual notable states to report.
        """
        lines = []
        has_content = False

        # Pregnancies (always important)
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
                    if not has_content:
                        lines.append("## BIOLOGY & HEALTH")
                        has_content = True
                    lines.append(f"Pregnant: {', '.join(pregnant)}")
        except:
            pass

        # Menstruating (only if critical/notable)
        try:
            if hasattr(self.sim, 'female_biology') and hasattr(self.sim.female_biology, 'cycles'):
                menstruating = []

                # Only list menstruating NPCs if they're in notable states (high horny/lonely)
                for npc in self.sim.npcs:
                    if npc.full_name in self.sim.female_biology.cycles:
                        fb = self.sim.female_biology.cycles[npc.full_name]
                        if fb.phase == "menstruation":
                            # Only include if in extreme state
                            if npc.needs.horny > 70 or npc.psyche.lonely > 70:
                                menstruating.append(npc.full_name)

                if menstruating:
                    if not has_content:
                        lines.append("## BIOLOGY & HEALTH")
                        has_content = True
                    lines.append(f"Menstruating: {', '.join(menstruating[:5])}")
        except:
            pass

        # If no content, skip entire section
        if not has_content:
            return ""

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
    # Handle None cases
    if not sim or not malcolm:
        return {
            "text": "## WORLD STATE\nSimulation initializing...",
            "malcolm_state": "Initializing...",
            "needs": {},
            "psychological": {},
            "world_time": "Day 0, 00:00"
        }

    # Get the full text snapshot using enhanced version
    from enhanced_snapshot_builder import create_narrative_context as enhanced_context
    full_text = enhanced_context(sim, malcolm)

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