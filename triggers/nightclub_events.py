# triggers/nightclub_events.py
import random
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.simulation_v2 import WillowCreekSimulation
    from entities.npc import NPC

NIGHTCLUB_EVENTS = [
    # Flirting & seduction (non-graphic)
    "{npc1} leans close to {npc2} on the dance floor, their voices lost under the bass as they talk far too close to be innocent.",
    "{npc1} buys {npc2} a drink at the bar; their hands brush and neither of them moves away right away.",
    "{npc2} ends up dancing closer to {npc1} than they meant to when the DJ drops a slower track, drawing a few looks from the crowd.",
    "Club owner Valentina Rossi watches {npc1} and {npc2} from the VIP booth, quietly filing their body language away as information.",

    # Tension & drama
    "{npc1} watches {npc2} laugh with someone else at the bar, swirling their drink a little too tightly.",
    "A wedding ring disappears into a pocket before {npc2} heads back onto the floor with {npc1}.",
    "Two friends exchange a look that says they will absolutely talk about {npc1} and {npc2} tomorrow.",

    # Inhibitions dropping
    "{npc2} finishes another drink and pulls {npc1} toward the edge of the dance floor, insisting they need 'somewhere quieter to talk'.",
    "A phone camera flashes briefly as someone records the crowd; {npc1} and {npc2} are right in the center of the shot.",
    "A small circle forms near the DJ booth as a group of regulars start a loose, messy dance line; {npc1} drags {npc2} into it, laughing.",

    # Reputation & consequences
    "Later, half the bar notices {npc1} and {npc2} slip out together, and the glances that follow them out say more than words.",
    "By closing time, a few people at the bar are already trading theories about {npc1} and {npc2}'s 'chemistry' tonight.",
    "Valentina makes a quiet note on the tab and on the behavior: some nights at The Circuit are worth remembering."
]


def trigger_nightclub_event(sim: "WillowCreekSimulation") -> Optional[str]:
    """
    Trigger a random nightclub event at The Circuit.
    Only fires on Friday/Saturday nights, with enough adult NPCs present.
    """
    # Friday (4) or Saturday (5)
    if sim.time.day_of_week not in (4, 5):
        return None

    # Time window: 21:00–03:00
    hour = sim.time.hour
    if not (21 <= hour or hour < 3):
        return None

    # Who is actually inside The Circuit right now?
    present = [
        npc
        for npc in sim.npcs
        if npc.current_location == "The Circuit" and npc.age >= 21
    ]

    if len(present) < 3:
        return None

    event_template = random.choice(NIGHTCLUB_EVENTS)
    npc1 = random.choice(present)
    # ensure npc2 is a different person
    npc2 = random.choice([n for n in present if n != npc1])

    return event_template.format(
        npc1=npc1.full_name.split()[-1],
        npc2=npc2.full_name.split()[-1],
    )
