# enhanced_snapshot_builder.py
# Enhanced world snapshot that includes all 17 game systems

from typing import TYPE_CHECKING
from game_manager import get_game_manager

if TYPE_CHECKING:
    from simulation_v2 import WillowCreekSimulation
    from entities.npc import NPC


def create_enhanced_narrative_context(sim: 'WillowCreekSimulation', malcolm: 'NPC') -> str:
    """
    Enhanced world snapshot that includes all game systems.
    This is what the AI narrator sees - optimized for tokens but comprehensive.
    """

    # Get the standard snapshot first
    from world_snapshot_builder import WorldSnapshotBuilder
    builder = WorldSnapshotBuilder(sim)

    sections = []

    # 1. Standard sections (time, Malcolm state, NPCs, etc.)
    try:
        sections.append(builder._build_time_and_environment())
    except:
        pass

    try:
        sections.append(builder._build_malcolm_state(malcolm))
    except:
        pass

    try:
        sections.append(builder._build_recent_events())
    except:
        pass

    # 2. NEW: Malcolm's Skills (top 3 only to save tokens)
    try:
        sections.append(_build_malcolm_skills())
    except:
        pass

    # 3. NEW: Malcolm's Inventory (important items only)
    try:
        sections.append(_build_malcolm_inventory())
    except:
        pass

    # 4. NEW: Malcolm's Reputation
    try:
        sections.append(_build_malcolm_reputation())
    except:
        pass

    # 5. Enhanced NPC states (includes relationship details)
    try:
        sections.append(_build_enhanced_npc_states(malcolm))
    except:
        sections.append(builder._build_all_npc_states())

    # 6. NEW: Recent Memories (last 3 to provide context)
    try:
        sections.append(_build_recent_memories())
    except:
        pass

    # 7. NEW: Active Social Events
    try:
        sections.append(_build_active_events(sim))
    except:
        pass

    # 8. NEW: Recent Gossip (juicy rumors!)
    try:
        sections.append(_build_recent_gossip())
    except:
        pass

    # 9. NEW: Recent NPC Interactions (what NPCs did today)
    try:
        sections.append(_build_npc_autonomy_updates())
    except:
        pass

    # 10. Standard biology section
    try:
        bio_section = builder._build_biology_health()
        if bio_section:
            sections.append(bio_section)
    except:
        pass

    return "\n\n".join(sections)


def _build_malcolm_skills() -> str:
    """Malcolm's top skills (compressed format)"""
    try:
        game = get_game_manager()
        if not game or not game.sim or "Malcolm Newt" not in game.skills.character_skills:
            return ""
    except:
        return ""

    top_skills = game.skills.get_top_skills("Malcolm Newt", count=3)
    if not top_skills:
        return ""

    lines = ["## MALCOLM'S SKILLS"]
    for skill_type, level in top_skills:
        skill_name = skill_type.value.title()
        lines.append(f"  {skill_name}: Lvl {level}/10")

    return "\n".join(lines)


def _build_malcolm_inventory() -> str:
    """Malcolm's inventory (important items only)"""
    try:
        game = get_game_manager()
        if not game or not game.sim:
            return ""
    except:
        return ""

    inventory = game.inventory.get_inventory("Malcolm Newt")

    # Only show if Malcolm has interesting items or low money
    important_items = []
    for item_id, quantity in inventory.items.items():
        item = game.inventory.get_item(item_id)
        if item and item.category.value in ["gift", "key_item"]:
            important_items.append(f"{item.name} x{quantity}")

    if not important_items and inventory.money > 500:
        return ""  # Skip if nothing interesting

    lines = ["## MALCOLM'S INVENTORY"]
    lines.append(f"Money: ${inventory.money}")
    if important_items:
        lines.append(f"Items: {', '.join(important_items)}")

    return "\n".join(lines)


def _build_malcolm_reputation() -> str:
    """Malcolm's reputation in town"""
    try:
        game = get_game_manager()
        if not game or not game.sim:
            return ""
    except:
        return ""

    rep = game.reputation.get_reputation("Malcolm Newt")

    # Only include if reputation is notable (not neutral)
    if abs(rep.overall_score) < 10 and not rep.get_primary_traits(1):
        return ""

    lines = ["## MALCOLM'S REPUTATION"]

    if rep.overall_score > 20:
        lines.append(f"Town Opinion: Positive ({rep.overall_score:.0f}/100)")
    elif rep.overall_score < -20:
        lines.append(f"Town Opinion: Negative ({rep.overall_score:.0f}/100)")

    traits = rep.get_primary_traits(3)
    if traits:
        trait_names = [t.value.title() for t in traits]
        lines.append(f"Known For: {', '.join(trait_names)}")

    return "\n".join(lines) if len(lines) > 1 else ""


def _build_enhanced_npc_states(malcolm: 'NPC') -> str:
    """Enhanced NPC states with relationship details"""
    try:
        game = get_game_manager()
        if not game or not hasattr(game, 'sim') or not game.sim:
            # Fallback to standard
            from world_snapshot_builder import WorldSnapshotBuilder
            builder = WorldSnapshotBuilder(None)
            return builder._build_all_npc_states() if game else "## NOTABLE RESIDENTS\n[No data]"
    except:
        # Fallback to standard
        from world_snapshot_builder import WorldSnapshotBuilder
        builder = WorldSnapshotBuilder(game.sim if game else None)
        return builder._build_all_npc_states() if game else "## NOTABLE RESIDENTS\n[No data]"

    # Get notable NPCs (same filter as token optimization)
    relevant_npcs = []
    for npc in game.sim.npcs:
        if npc.full_name == "Malcolm Newt":
            continue

        # Get relationship data
        rel = game.relationships.get_relationship("Malcolm Newt", npc.full_name)

        # Include if: high stats, or significant relationship with Malcolm
        is_relevant = (
            npc.needs.horny > 70 or
            npc.psyche.lonely > 70 or
            npc.needs.energy < 30 or
            rel.friendship_points > 40 or  # NEW: Include friends
            rel.romantic_points > 30 or     # NEW: Include romantic interests
            rel.times_talked > 5            # NEW: Include frequent contacts
        )

        if is_relevant:
            relevant_npcs.append((npc, rel))

    # If too few, add a few randoms
    if len(relevant_npcs) < 5:
        for npc in game.sim.npcs:
            if npc.full_name != "Malcolm Newt":
                rel = game.relationships.get_relationship("Malcolm Newt", npc.full_name)
                if (npc, rel) not in relevant_npcs:
                    relevant_npcs.append((npc, rel))
                    if len(relevant_npcs) >= 8:
                        break

    # Limit to 12 for tokens
    relevant_npcs = relevant_npcs[:12]

    if not relevant_npcs:
        return "## NOTABLE RESIDENTS\n[No one currently notable]"

    lines = [f"## NOTABLE RESIDENTS ({len(relevant_npcs)} shown, {len(game.sim.npcs)} total)"]

    # Group by location
    loc_map = {}
    for npc, rel in relevant_npcs:
        loc = getattr(npc, 'current_location', 'Unknown')
        loc_map.setdefault(loc, []).append((npc, rel))

    for location, npc_rel_pairs in sorted(loc_map.items()):
        lines.append(f"\n### {location}")
        for npc, rel in npc_rel_pairs:
            # Build status flags
            flags = []

            # Physical/psychological states
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

            # NEW: Relationship status with Malcolm
            if rel.status.value >= 7:  # Dating or higher
                flags.append(f"DATING MALCOLM")
            elif rel.status.value >= 5:  # Romantic interest
                flags.append("attracted")
            elif rel.friendship_points >= 80:
                flags.append("best friend")
            elif rel.friendship_points >= 60:
                flags.append("close friend")
            elif rel.friendship_points >= 40:
                flags.append("friend")

            # Ovulation
            try:
                if hasattr(game.sim, 'female_biology') and hasattr(game.sim.female_biology, 'cycles'):
                    if npc.full_name in game.sim.female_biology.cycles:
                        fb = game.sim.female_biology.cycles[npc.full_name]
                        if fb.phase == "ovulation":
                            flags.append("OVULATING")
            except:
                pass

            flag_str = f" [{','.join(flags)}]" if flags else ""

            # Compact format with relationship data
            lines.append(
                f"  • {npc.full_name} ({npc.age}): "
                f"H:{npc.needs.horny:.0f} L:{npc.psyche.lonely:.0f} E:{npc.needs.energy:.0f} | "
                f"F:{rel.friendship_points:.0f} R:{rel.romantic_points:.0f}"
                f"{flag_str}"
            )

    return "\n".join(lines)


def _build_recent_memories() -> str:
    """Malcolm's recent memories (last 3 for context)"""
    try:
        game = get_game_manager()
        if not game or not game.sim:
            return ""
    except:
        return ""

    memories = game.memory.get_memories("Malcolm Newt", limit=3)
    if not memories:
        return ""

    lines = ["## RECENT MEMORIES"]
    for memory in memories:
        # Simple format: what happened
        lines.append(f"  • {memory.description}")

    return "\n".join(lines)


def _build_active_events(sim) -> str:
    """Active social events happening now"""
    try:
        game = get_game_manager()
        if not game or not game.sim or not sim:
            return ""
    except:
        return ""

    current_day = sim.time.total_days
    current_hour = sim.time.hour

    active_events = game.social_events.get_active_events(current_day, current_hour)
    upcoming_events = game.social_events.get_upcoming_events(current_day, days_ahead=1)

    if not active_events and not upcoming_events:
        return ""

    lines = []

    if active_events:
        lines.append("## EVENTS HAPPENING NOW")
        for event in active_events:
            lines.append(f"  • {event.name} at {event.location} (hosted by {event.host})")
            if event.is_invited("Malcolm Newt"):
                lines.append(f"    Malcolm is invited! {len(event.attendees)} people attending")

    if upcoming_events and len(upcoming_events) > 0:
        if not lines:
            lines.append("## UPCOMING EVENTS")
        else:
            lines.append("\nUpcoming:")
        for event in upcoming_events[:2]:  # Max 2 to save tokens
            lines.append(f"  • {event.name} - Day {event.day} at {event.start_hour}:00")

    return "\n".join(lines) if lines else ""


def _build_recent_gossip() -> str:
    """Recent town gossip (last 3 juicy rumors)"""
    try:
        game = get_game_manager()
        if not game or not game.sim:
            return ""
    except:
        return ""

    # Get recent gossip sorted by juiciness
    gossip_list = game.reputation.active_gossip[-10:]  # Last 10
    gossip_list = sorted(gossip_list, key=lambda g: g.juiciness, reverse=True)

    if not gossip_list:
        return ""

    lines = ["## TOWN GOSSIP"]
    for gossip in gossip_list[:3]:  # Top 3 juiciest
        lines.append(f"  • {gossip.content} (spread to {gossip.spread_count} people)")

    return "\n".join(lines)


def _build_npc_autonomy_updates() -> str:
    """What NPCs did today (autonomous interactions)"""
    try:
        game = get_game_manager()
        if not game or not game.sim:
            return ""
    except:
        return ""

    interactions = game.npc_autonomy.npc_interactions_today
    if not interactions or len(interactions) == 0:
        return ""

    # Only show interesting interactions
    interesting = [
        (a, b, itype) for a, b, itype in interactions
        if itype in ["flirt", "conflict"]  # Only show flirts and conflicts, not regular talks
    ]

    if not interesting:
        return ""

    lines = ["## NPC ACTIVITY TODAY"]
    for person_a, person_b, interaction_type in interesting[:3]:  # Max 3
        if interaction_type == "flirt":
            lines.append(f"  • {person_a} flirted with {person_b}")
        elif interaction_type == "conflict":
            lines.append(f"  • {person_a} had a conflict with {person_b}")

    return "\n".join(lines)


# Backward compatibility - can be used as drop-in replacement
def create_narrative_context(sim: 'WillowCreekSimulation', malcolm: 'NPC') -> str:
    """
    Backward compatible wrapper.
    Returns enhanced context if game manager is available, otherwise standard.
    """
    try:
        return create_enhanced_narrative_context(sim, malcolm)
    except:
        # Fallback to standard
        from world_snapshot_builder import WorldSnapshotBuilder
        builder = WorldSnapshotBuilder(sim)
        return builder.build_complete_snapshot(malcolm)
