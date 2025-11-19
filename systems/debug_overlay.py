class DebugOverlay:
    def __init__(self, sim):
        self.sim = sim

    def render(self):
        sim = self.sim
        out = []

        out.append("════════════════════════════════════════════════════════")
        out.append(f"DEBUG OVERLAY — {sim.time.get_datetime_string()}")
        out.append("════════════════════════════════════════════════════════")
        out.append("")

        # LOCATION REMOVED — AI ONLY KNOWS THIS, NOT PLAYER
        # (Simulation still internally tracks current_location)

        # GOSSIP
        out.append(f"GOSSIP ITEMS: {len(sim.reputation.gossip_network)}")
        out.append("")

        # EMOTIONS
        out.append(f"ACTIVE EMOTIONS: {len(sim.emotional.active_emotions)}")
        out.append("")

        # HEALTH
        sick = getattr(sim.health, "sick_npcs", {})
        out.append(f"SICK NPCs: {len(sick)}")

        preg = getattr(sim.pregnancy, "active_pregnancies", [])
        out.append(f"PREGNANCIES: {len(preg)}")
        out.append("")

        # CRIME
        crimes = getattr(sim.crime, "recent_crimes", [])
        out.append(f"RECENT CRIME EVENTS: {len(crimes)}")

        # ADDICTION
        addiction = getattr(sim.addiction, "states", {})
        out.append(f"ADDICTION CASES: {len(addiction)}")

        # SCHOOL DRAMA
        drama = getattr(sim.school_drama, "recent_events", [])
        out.append(f"SCHOOL DRAMA EVENTS: {len(drama)}")
        out.append("")

        # GLOBAL NEEDS
        if sim.npcs:
            avg_hunger = sum(n.needs.hunger for n in sim.npcs) / len(sim.npcs)
            avg_horny = sum(n.needs.horny for n in sim.npcs) / len(sim.npcs)
            avg_lonely = sum(n.psyche.lonely for n in sim.npcs) / len(sim.npcs)
        else:
            avg_hunger = avg_horny = avg_lonely = 0.0

        out.append("GLOBAL NEEDS SUMMARY:")
        out.append(f"  • Hunger: {avg_hunger:.1f}")
        out.append(f"  • Horny:  {avg_horny:.1f}")
        out.append(f"  • Lonely: {avg_lonely:.1f}")
        out.append("")
        out.append("════════════════════════════════════════════════════════")

        return "\n".join(out)
