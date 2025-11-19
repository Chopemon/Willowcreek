# systems/npc_quirks_system.py
# NPC QUIRKS & SPECIAL BEHAVIORS v2.0 — FULL PYTHON PORT

from __future__ import annotations
from typing import Dict, Any, List
import random


class NPCQuirksSystem:
    def __init__(self, simulation):
        self.sim = simulation
        self.npcs = {npc.full_name: npc for npc in simulation.npcs}
        self.time = simulation.time
        
        # FIXED: 100% safe access
        self.malcolm = getattr(simulation, "malcolm", None) or simulation.npc_dict.get("Malcolm Newt")
        
        self.schedule = simulation.schedule
        self.reputation = simulation.reputation
        self.message_count = 0
        self.recent_triggers: List[str] = [] # Internal buffer for snapshot

    def get_recent_triggers(self) -> List[str]:
        """
        Returns the list of quirks triggered during the last step for the LLM snapshot.
        Clears the list after reading to ensure only current triggers are shown next time.
        """
        triggers = list(self.recent_triggers)
        self.recent_triggers.clear() # Clear the list after reading for the current snapshot
        return triggers


    def process_quirks(self, last_message: str):
        self.message_count += 1
        text = last_message.lower()
        current_day = self.time.total_days
        hour = self.time.hour

        # =======================================================================
        # QUIRK LOGIC START (FULL REINTEGRATION)
        # =======================================================================

        # --- Alex Sturm (Frustration/Release Quirk) ---
        alex = self.npcs.get("Alex Sturm")
        if alex and self.message_count % 20 == 0:
            # Initialize attributes if they don't exist
            if not hasattr(alex, "frustrationLevel"):
                alex.frustrationLevel = 3.0
            if not hasattr(alex, "daysSinceRelease"):
                alex.daysSinceRelease = 0
            if not hasattr(alex, "lastRelease"):
                alex.lastRelease = current_day
            if not hasattr(alex, "currentMood"):
                alex.currentMood = "conflicted"

            alex.daysSinceRelease = current_day - alex.lastRelease
            
            # Check if John is away
            john_loc = getattr(self.schedule, "current_locations", {}).get("John Sturm", "")
            john_away = "home" not in john_loc.lower() if john_loc else True

            # Frustration increases when alone
            if john_away and random.random() < 0.4:
                alex.frustrationLevel = min(10.0, alex.frustrationLevel + 1)
                alex.currentMood = "tense"
                self._add_scenario(f"[ALEX STURM: Frustration increased. John away. Frustration: {alex.frustrationLevel:.1f}]")

            # Frustration increases with time
            if alex.daysSinceRelease > 3 and random.random() < 0.3:
                alex.frustrationLevel = min(10.0, alex.frustrationLevel + 0.5)
                self._add_scenario(f"[ALEX STURM: Frustration simmering. Days since release: {alex.daysSinceRelease}]")

            # Release trigger (garage workout)
            if alex.frustrationLevel > 5 and random.random() < 0.3:
                alex.frustrationLevel = max(0.0, alex.frustrationLevel - 2)
                alex.lastRelease = current_day
                alex.daysSinceRelease = 0
                alex.currentMood = "relieved but guilty"
                self._add_scenario(f"[ALEX STURM: Intense garage workout. Tension released. Frustration: {alex.frustrationLevel:.1f}]")
                # print(f"Alex workout release - frustration: {alex.frustrationLevel:.1f}")

            # Critical frustration display
            if alex.frustrationLevel >= 7 and random.random() < 0.2:
                self._add_scenario(f"[ALEX STURM: Body rigid, avoids eye contact. Frustration critical ({alex.frustrationLevel:.1f}/10, {alex.daysSinceRelease} days)]")

            # Maria/Sturm keyword tension
            if ("maria" in text or "sturm" in text) and john_away:
                alex.frustrationLevel = min(10.0, alex.frustrationLevel + 0.5)
                self._add_scenario("[ALEX: Alone with Maria — guilt and desire collide]")

        # --- Emma (Reflex Quirk) ---
        if "emma" in text:
            triggers = ["banana", "curved fruit", "yellow peel"]
            if any(t in text for t in triggers):
                self._add_scenario(
                    "[EMMA REFLEX: Body arches involuntarily. Thighs clench. Muffled moan escapes. "
                    "Face burns crimson with shame. She has an intense orgasm.]"
                )

        # --- Nora (Anxiety/TikTok Quirk) ---
        nora = self.npcs.get("Nora Holbrook")
        if nora and self.message_count % 20 == 0 and random.random() < 0.2:
            self._add_scenario(
                "[NORA: Scrolls TikTok. Clutches blanket when anxious. "
                "Fascinated by gender differences. Asks wide-eyed questions]"
            )
            if hour > 20:
                self._add_scenario("[NORA: Late hour — clings to family]")
        
        # --- Lianna (Jealousy/Obsession Quirk) ---
        lianna = self.npcs.get("Lianna West")
        if lianna and "chloe" in text.lower() and random.random() < 0.5:
            self._add_scenario("[LIANNA: Her eyes flash cold as she observes Chloe. The possessive edge in her voice is subtle but sharp.]")

        # --- Lisa (Dominance/Flirt Quirk) ---
        lisa = self.npcs.get("Lisa Fox")
        if lisa and self.message_count % 15 == 0 and random.random() < 0.3:
            self._add_scenario("[LISA: Crosses her legs slowly, maintaining unbroken eye contact, a silent challenge in her grin.]")

        # --- Michael (Recklessness Quirk) ---
        michael = self.npcs.get("Michael Chen")
        if michael and michael.current_location == "The Hideout" and random.random() < 0.3:
            self._add_scenario("[MICHAEL: Pulls out his phone and covertly records a risky stunt, looking for a new viral moment.]")

        # --- Eva (Escapism Quirk) ---
        eva = self.npcs.get("Eva Sterling")
        if eva and eva.current_location == "Willow Creek Library" and random.random() < 0.4:
            self._add_scenario("[EVA: Her expression is distant, lost in the pages of a fantasy novel, avoiding reality.]")
        
        # --- Nina (Insecurity Quirk) ---
        nina = self.npcs.get("Nina Sharpe")
        if nina and random.random() < 0.2 and ("compliment" in text or "beautiful" in text):
            self._add_scenario("[NINA: Flinches slightly at the compliment, immediately looking down and smoothing her clothes, unable to accept genuine praise.]")

        # --- Agnes (Judgment Quirk) ---
        agnes = self.npcs.get("Agnes Plum")
        if agnes and random.random() < 0.1:
            self._add_scenario("[AGNES: Her gaze sweeps over the room, settling briefly on someone with an air of subtle disapproval. The silent judgment is palpable.]")

        # --- Scarlet (Vulnerability Quirk) ---
        scarlet = self.npcs.get("Scarlet Reyes")
        if scarlet and scarlet.needs.social < 30:
             self._add_scenario("[SCARLET: Tugs nervously at her sleeve, the bravado slipping to reveal a brief flash of genuine loneliness and need for comfort.]")

        # --- Lily (Loyalty Quirk) ---
        lily = self.npcs.get("Lily Vance")
        if lily and ("family" in text or "vance" in text) and random.random() < 0.3:
            self._add_scenario("[LILY: Her posture straightens, eyes narrowed with fierce, protective loyalty. She will defend her family name to the end.]")

        # --- Isabella (Aesthetic Quirk) ---
        isabella = self.npcs.get("Isabella Chen")
        if isabella and random.random() < 0.2:
            self._add_scenario("[ISABELLA: Pauses a conversation to adjust a scarf or jacket, prioritizing her meticulous, trendy aesthetic above all else.]")

        # --- Damien (Need for Validation Quirk) ---
        damien = self.npcs.get("Damien Cole")
        if damien and random.random() < 0.2 and "ignored" in text:
            self._add_scenario("[DAMIEN: Speaks louder than necessary, throwing out a cynical, witty remark just to force a reaction from those ignoring him.]")

        # --- Christine (Over-Caring Quirk) ---
        christine = self.npcs.get("Christine Wells")
        if christine and christine.needs.social < 50:
            self._add_scenario("[CHRISTINE: Offers unsolicited advice and a warm drink to a random NPC, seeking connection by attempting to fix a non-existent problem.]")
        
        # --- Penny (Control Quirk) ---
        penny = self.npcs.get("Penny Rose")
        if penny and random.random() < 0.15:
            self._add_scenario("[PENNY: Quickly steps in to organize a pile of misplaced items or reroute a conversation, revealing her strong need for control.]")

        # --- Mindy (Self-Sabotage Quirk) ---
        mindy = self.npcs.get("Mindy Clark")
        if mindy and random.random() < 0.1:
            self._add_scenario("[MINDY: Just as a positive opportunity arises, she makes an oddly deflating or self-deprecating comment, actively pushing success away.]")

        # --- Rose (Secretiveness Quirk) ---
        rose = self.npcs.get("Rose Sterling")
        if rose and random.random() < 0.2:
            self._add_scenario("[ROSE: Her hand hovers near her mouth as she speaks, a flicker of panic suggesting she almost revealed a secret she shouldn't have.]")

        # --- Luke (Provocation Quirk) ---
        luke = self.npcs.get("Luke Vance")
        if luke and random.random() < 0.15 and "calm" in text:
            self._add_scenario("[LUKE: Eyes darting around, he leans into a heated discussion, clearly enjoying the tension and chaos he is helping to create.]")

        # --- Tim (Social Incompetence Quirk) ---
        tim = self.npcs.get("Tim Wells")
        if tim and random.random() < 0.2:
            self._add_scenario("[TIM: Recites a complex technical fact about a mundane subject, completely misreading the social cue to change the topic.]")

        # --- Tony (Sarcasm Quirk) ---
        tony = self.npcs.get("Tony Rose")
        if tony and random.random() < 0.1:
            self._add_scenario("[TONY: A slow, knowing smirk spreads across his face, followed by a remark dripping with heavy, unmistakable sarcasm.]")

        # =======================================================================
        # QUIRK LOGIC END
        # =======================================================================

    def _add_scenario(self, text: str):
        if hasattr(self.sim, "scenario_buffer"):
            self.sim.scenario_buffer.append(text)
            self.recent_triggers.append(text)
        else:
            print(text)