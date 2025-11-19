# systems/dialogue.py
import random
from entities.npc import NPC

# Dark, intimate, small-town dialogue lines
DIALOGUE_TEMPLATES = {
    "greeting": [
        "{npc} meets Malcolm's eyes and smiles slowly, like she's been waiting for this moment.",
        "{npc} leans in just a little too close, her voice low: \"You don't belong here... but I'm glad you came.\"",
        "{npc} bites her lip, glancing away before looking back. \"People talk about you, you know.\"",
        "{npc} brushes her hair behind her ear, voice soft: \"I've seen you watching.\"",
    ],
    "flirt": [
        "{npc} lets her hand rest on Malcolm's arm longer than necessary. \"Careful... some things in this town bite back.\"",
        "{npc} laughs, low and warm. \"You're trouble. The kind I might not mind.\"",
        "{npc} tilts her head, eyes dark. \"My husband’s out of town… just so you know.\"",
        "{npc} whispers, barely audible over the music: \"Meet me out back in ten minutes.\"",
    ],
    "nervous": [
        "{npc} fidgets with her wedding ring, unable to meet his gaze for long.",
        "{npc} glances toward the door every few seconds, voice trembling slightly.",
        "{npc} laughs too quickly. \"We shouldn’t be talking like this… should we?\"",
    ],
    "bold": [
        "{npc} steps closer, voice husky: \"Tell me what you want, Malcolm. No games.\"",
        "{npc} traces a finger down his chest. \"I don’t care who sees.\"",
        "{npc} leans in until her lips nearly brush his ear: \"Take me somewhere dark.\"",
    ],
    "refusal": [
        "{npc} pulls back suddenly, eyes wide. \"I… I can’t. Not here.\"",
        "{npc} shakes her head, stepping away. \"This was a mistake.\"",
    ],
    "secret": [
        "{npc} lowers her voice: \"There’s a back room at Harmony Studio… if you’re interested.\"",
        "{npc} smirks. \"Pastor Naomi isn’t as pure as she pretends. Just ask her daughter.\"",
        "{npc} whispers: \"Rick keeps cameras behind the bar. Everything gets recorded.\"",
    ]
}

def generate_dialogue(npc: NPC, malcolm: NPC, context: str = "normal") -> str:
    """Generate one line of dialogue from NPC to Malcolm"""
    if npc.age < 18:
        return f"{npc.full_name} avoids eye contact and hurries away."

    mood = "flirt"
    if npc.psyche.stress > 70:
        mood = random.choice(["nervous", "refusal"])
    elif npc.needs.horny > 70 or npc.psyche.lonely > 60:
        mood = random.choice(["bold", "flirt", "secret"])
    elif random.random() < 0.3:
        mood = random.choice(["greeting", "secret"])

    template = random.choice(DIALOGUE_TEMPLATES.get(mood, DIALOGUE_TEMPLATES["greeting"]))
    return template.format(npc=npc.full_name.split()[0])