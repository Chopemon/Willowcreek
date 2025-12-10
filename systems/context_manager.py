# systems/context_manager.py
# Smart context filtering to prevent LLM overload
# Priority: Location > Relationships > Recent Events > Background

from typing import List, Dict, Optional
from entities.npc import NPC


class ContextManager:
    """
    Smart context filtering to prevent LLM overload.
    Priority: Location > Relationships > Recent Events > Background
    """

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.token_estimate_ratio = 4  # chars per token estimate

    def build_focused_snapshot(
        self,
        malcolm: NPC,
        sim,
        include_full_roster: bool = False,
        include_gossip: bool = False
    ) -> str:
        """
        Build a LEAN snapshot focused on Malcolm's immediate context.
        Only includes information relevant to the current scene.

        Args:
            malcolm: The player character NPC
            sim: The simulation instance
            include_full_roster: Include full NPC list (expensive)
            include_gossip: Include current gossip (moderate)

        Returns:
            Formatted string snapshot for LLM context
        """
        lines = []
        budget = self.max_tokens * self.token_estimate_ratio

        # === PRIORITY 1: IMMEDIATE CONTEXT (Always include) ===
        t = sim.time
        lines.append(f"Time: {t.get_datetime_string()}")
        lines.append(f"Location: {malcolm.current_location}")
        lines.append(f"Weather: {getattr(sim.seasonal, 'weather_description', 'Clear')}")
        lines.append(f"Atmosphere: {getattr(sim.seasonal, 'mood_description', 'Calm')}")
        lines.append("")

        # === PRIORITY 2: MALCOLM'S STATE (Critical only) ===
        lines.append("Malcolm's State:")
        ms_needs = malcolm.needs
        ms_psyche = malcolm.psyche

        # Only show needs that are notable (very high or very low)
        if ms_needs.hunger > 60 or ms_needs.hunger < 30:
            lines.append(f"  Hunger: {ms_needs.hunger:.0f}")
        if ms_needs.energy < 40:
            lines.append(f"  Energy: {ms_needs.energy:.0f} (tired)")
        if ms_needs.horny > 60:
            lines.append(f"  Arousal: {ms_needs.horny:.0f}")
        if ms_psyche.lonely > 50:
            lines.append(f"  Loneliness: {ms_psyche.lonely:.0f}")

        lines.append(f"  Mood: {malcolm.mood}")
        lines.append("")

        # === PRIORITY 3: PEOPLE AT LOCATION ===
        loc = getattr(malcolm, 'current_location', 'Unknown')
        here = [
            n for n in sim.npcs
            if getattr(n, 'current_location', 'Unknown') == loc
            and n.full_name != "Malcolm Newt"
        ]

        if here:
            lines.append(f"Present at {loc}:")
            for npc in here[:6]:  # Limit to 6 NPCs
                lines.append(f"  • {npc.full_name} ({npc.age})")
                lines.append(f"    Mood: {npc.mood}")
                lines.append(f"    Action: {getattr(npc, 'current_action', 'idle')}")

                # Only include attraction if significant
                attr = getattr(npc, 'attraction_to_malcolm', 0)
                if attr > 30:
                    lines.append(f"    Attraction: {attr}")
                if npc.needs.horny > 60:
                    lines.append(f"    Arousal: {npc.needs.horny:.0f}")
            lines.append("")
        else:
            lines.append(f"Present at {loc}:")
            lines.append("  (Nobody else here.)")
            lines.append("")

        # === PRIORITY 4: NEARBY ACTIVITY (Compressed) ===
        lines.append("Nearby activity:")
        nearby = []
        for npc in sim.npcs:
            npc_loc = getattr(npc, 'current_location', 'Unknown')
            if npc_loc != loc:
                action = getattr(npc, 'current_action', 'none')
                if action in ("arguing", "shouting", "fighting", "flirting", "crying"):
                    nearby.append(f"{npc.full_name} is {action} at {npc_loc}")

        if nearby:
            for entry in nearby[:3]:  # Limit to 3
                lines.append(f"  - {entry}")
        else:
            lines.append("  (Quiet nearby)")
        lines.append("")

        # === PRIORITY 5: RECENT EVENTS (Last 5 only) ===
        if hasattr(sim, 'scenario_buffer') and sim.scenario_buffer:
            lines.append("Recent Events:")
            for event in sim.scenario_buffer[-5:]:
                lines.append(f"  - {event}")
            lines.append("")

        # === OPTIONAL: GOSSIP (Only if requested) ===
        if include_gossip:
            lines.append("Gossip circulating:")
            if hasattr(sim, 'reputation') and hasattr(sim.reputation, 'gossip_network'):
                for item in sim.reputation.gossip_network[:3]:
                    lines.append(f"  - {getattr(item, 'secret', 'unknown')}")
            else:
                lines.append("  (No gossip right now.)")
            lines.append("")

        # === OPTIONAL: Full roster (only if explicitly requested) ===
        if include_full_roster:
            lines.append("Available NPCs:")
            for npc in sim.npcs[:20]:  # Limit to 20
                if npc.full_name != "Malcolm Newt":
                    occ = npc.occupation or "Unemployed"
                    lines.append(f"  • {npc.full_name}, {npc.age}, {occ}")
            lines.append("")

        # === TOWN POPULATION COUNT ===
        nearby_count = sum(
            1 for n in sim.npcs
            if getattr(n, 'current_location', 'Unknown') != loc
        )
        lines.append(f"Town Population: {nearby_count} NPCs elsewhere")

        snapshot = "\n".join(lines)

        # Token budget check
        estimated_tokens = len(snapshot) // self.token_estimate_ratio
        if estimated_tokens > self.max_tokens:
            print(f"⚠️  Context still large ({estimated_tokens} tokens), consider further trimming")
        else:
            print(f"✓ Context: {estimated_tokens} tokens")

        return snapshot

    def get_npc_summary(self, npc: NPC, detailed: bool = False) -> str:
        """
        Get a summary of an NPC for context.

        Args:
            npc: The NPC to summarize
            detailed: Include full details or just basics

        Returns:
            Formatted NPC summary string
        """
        if detailed:
            lines = [
                f"{npc.full_name} ({npc.age}, {npc.gender.value})",
                f"  Occupation: {npc.occupation or 'Unemployed'}",
                f"  Location: {getattr(npc, 'current_location', 'Unknown')}",
                f"  Mood: {npc.mood}",
                f"  Action: {getattr(npc, 'current_action', 'idle')}",
            ]

            # Add notable stats
            if npc.needs.horny > 60:
                lines.append(f"  Arousal: {npc.needs.horny:.0f}")
            if npc.needs.energy < 30:
                lines.append(f"  Energy: {npc.needs.energy:.0f} (exhausted)")
            if hasattr(npc, 'attraction_to_malcolm') and npc.attraction_to_malcolm > 30:
                lines.append(f"  Attraction to Malcolm: {npc.attraction_to_malcolm}")

            return "\n".join(lines)
        else:
            return f"{npc.full_name} ({npc.age}) - {npc.mood}"

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a piece of text."""
        return len(text) // self.token_estimate_ratio
