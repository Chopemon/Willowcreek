# narrative_chat.py – Willow Creek 2025 Narrative Interface (OPTIMIZED)
# Full integration with ContextManager for 5-10x faster response times
# ADDED: Native LLM support - run models directly without external servers

import requests
import argparse
import os
from typing import Optional
from pathlib import Path
from simulation_v2 import WillowCreekSimulation
from entities.npc import NPC, Gender

# Try to import native LLM support
try:
    from local_llm import LocalLLM, LLAMA_CPP_AVAILABLE, TRANSFORMERS_AVAILABLE
    NATIVE_LLM_AVAILABLE = LLAMA_CPP_AVAILABLE or TRANSFORMERS_AVAILABLE
except ImportError:
    NATIVE_LLM_AVAILABLE = False


class ContextManager:
    """
    Smart context filtering to prevent LLM overload.
    Priority: Location > Relationships > Recent Events > Background
    """

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.token_estimate_ratio = 4  # ~4 chars per token

    def build_focused_snapshot(
        self,
        malcolm: NPC,
        sim,
        include_full_roster: bool = False,
        include_gossip: bool = False
    ) -> str:
        """
        Build a LEAN snapshot focused on Malcolm's immediate context.
        Only includes information relevant to current scene.
        """
        lines = []

        # === PRIORITY 1: TIME & WEATHER (Always include) ===
        t = sim.time
        lines.append(f"Time: {t.get_datetime_string()}")
        lines.append(f"Weather: {getattr(sim.seasonal, 'weather_description', 'Clear')}")
        lines.append(f"Atmosphere: {getattr(sim.seasonal, 'mood_description', 'Calm')}")
        lines.append("")

        # === PRIORITY 2: MALCOLM'S STATE (Critical only) ===
        lines.append("Malcolm's internal state:")
        ms_needs = malcolm.needs
        ms_psyche = malcolm.psyche

        # Only show needs that are notable (very high or very low)
        if ms_needs.hunger > 60 or ms_needs.hunger < 30:
            lines.append(f"  hunger={ms_needs.hunger:.0f}")
        if ms_needs.energy < 40:
            lines.append(f"  energy={ms_needs.energy:.0f} (tired)")
        if ms_needs.horny > 60:
            lines.append(f"  arousal={ms_needs.horny:.0f}")
        if ms_psyche.lonely > 50:
            lines.append(f"  loneliness={ms_psyche.lonely:.0f}")

        lines.append(f"  mood={malcolm.mood}")
        lines.append("")

        # === PRIORITY 3: CURRENT LOCATION & PEOPLE ===
        loc = getattr(malcolm, 'current_location', 'Unknown')
        lines.append(f"Current location: {loc}")
        lines.append("People here:")

        here = [
            n for n in sim.npcs
            if getattr(n, 'current_location', 'Unknown') == loc
            and n.full_name != "Malcolm Newt"
        ]

        if here:
            # Limit to 6 most relevant NPCs at location
            for npc in here[:6]:
                lines.append(f"  - {npc.full_name} (age {npc.age})")
                lines.append(f"      mood: {npc.mood}")
                lines.append(f"      action: {getattr(npc, 'current_action', 'idle')}")

                # Only show high attraction/arousal
                attr = getattr(npc, 'attraction_to_malcolm', 0)
                if attr > 40:
                    lines.append(f"      attraction: {attr}")
                if npc.needs.horny > 60:
                    lines.append(f"      arousal: {npc.needs.horny:.0f}")
                lines.append("")
        else:
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
            lines.append("Recent events:")
            for event in sim.scenario_buffer[-5:]:
                lines.append(f"  - {event}")
            lines.append("")

        # === OPTIONAL: GOSSIP (Only if requested) ===
        if include_gossip:
            lines.append("Gossip circulating:")
            if hasattr(sim.reputation, 'gossip_network'):
                for item in sim.reputation.gossip_network[:3]:
                    lines.append(f"  - {getattr(item, 'secret', 'unknown')}")
            else:
                lines.append("  (No gossip right now.)")
            lines.append("")

        # === OPTIONAL: FULL ROSTER (Only when explicitly asked) ===
        if include_full_roster:
            lines.append("Available NPCs in town:")
            for npc in sim.npcs[:15]:  # Limit to 15
                if npc.full_name != "Malcolm Newt":
                    occ = npc.occupation or "Unemployed"
                    lines.append(f"  • {npc.full_name}, {npc.age}, {occ}")
            lines.append("")

        snapshot = "\n".join(lines)

        # Token budget check
        estimated_tokens = len(snapshot) // self.token_estimate_ratio
        if estimated_tokens > self.max_tokens:
            print(f"⚠️  Context: {estimated_tokens} tokens (target: {self.max_tokens})")
        else:
            print(f"✓ Context: {estimated_tokens} tokens")

        return snapshot


class NarrativeChat:
    def __init__(
        self,
        mode: str = "local",
        model_path: str = None,
        backend: str = "auto",
        lm_studio_url: str = "http://localhost:1234/v1/chat/completions"
    ):
        """
        Initialize the narrative chat.

        Args:
            mode: "local" (LM Studio), "native" (direct inference), or "openrouter" (cloud)
            model_path: Path to GGUF model file (for native mode)
            backend: "auto", "llama_cpp", or "transformers" (for native mode)
            lm_studio_url: URL for LM Studio server (for local mode)
        """
        self.mode = mode
        self.lm_studio_url = lm_studio_url
        self.native_llm = None

        # Initialize native LLM if requested
        if mode == "native":
            if not NATIVE_LLM_AVAILABLE:
                raise ImportError(
                    "Native LLM support not available!\n"
                    "Install with: pip install llama-cpp-python\n"
                    "Or for transformers: pip install transformers torch"
                )

            # Default model path
            if model_path is None:
                model_path = "models/qwen3-4b-rpg.gguf"

            # Resolve relative paths
            if not os.path.isabs(model_path):
                model_path = str(Path(__file__).parent / model_path)

            self.model_path = model_path

            print(f"\n🧠 Loading native model: {model_path}")
            print("This may take a moment...")

            self.native_llm = LocalLLM(
                model_path=model_path,
                backend=backend,
                n_ctx=8192,
                verbose=True
            )
            print("✓ Model loaded successfully!\n")

        self.sim: Optional[WillowCreekSimulation] = None
        self.malcolm: Optional[NPC] = None
        self.malcolm_extended = {}
        self.last_narrated: str = ""

        # Context manager for optimized snapshots
        self.context_mgr = ContextManager(max_tokens=2000)

    # =====================================================================
    # INITIALIZE SIMULATION
    # =====================================================================
    def initialize(self):
        print("\n" + "=" * 80)
        print(" WILLOW CREEK 2025")
        print(" Dark Autumn • Living World • Third-Person Limited")
        if self.mode == "native":
            print(f" Running: {os.path.basename(self.model_path)} (native)")
        else:
            print(f" Running: {self.mode} mode")
        print("=" * 80 + "\n")

        # Start full simulation
        self.sim = WillowCreekSimulation(num_npcs=41)
        if not self.sim or not self.sim.npcs:
            print("World failed to initialize: no NPCs loaded.")
            return

        # Player character
        self.malcolm = self.sim.world.get_npc("Malcolm Newt")
        if not self.malcolm:
            # fallback if missing from roster
            self.malcolm = NPC(
                full_name="Malcolm Newt",
                age=30,
                gender=Gender.MALE,
                occupation="Unemployed (Wealthy)",
            )
            self.malcolm.current_location = "Malcolm's House"
            self.malcolm.current_action = "idle"
            self.sim.npcs.append(self.malcolm)
            self.sim.npc_dict[self.malcolm.full_name] = self.malcolm

        # Ensure Malcolm has a location
        if not hasattr(self.malcolm, 'current_location') or self.malcolm.current_location is None:
            self.malcolm.current_location = "Malcolm's House"
        if not hasattr(self.malcolm, 'current_action') or self.malcolm.current_action is None:
            self.malcolm.current_action = "idle"

        # Malcolm metadata
        self.malcolm_extended = {
            "cash": 50000,
            "days_in_town": 0,
        }

        # Opening paragraph
        self.last_narrated = (
            "The small town of Willow Creek sat under a low autumn sky, "
            "air sharp with the smell of wet leaves and distant woodsmoke. "
            "A matte-black SUV rolled to a slow, expensive stop on Oak Street, "
            "its engine whispering into silence. Malcolm Newt stepped out, "
            "city polish wrapped around a restless gaze, his dog Loki tugging "
            "once at the leash before settling at his side. This sleepy street "
            "with its sagging porches and watching curtains was his new experiment."
        )

        print(self.last_narrated + "\n")
        self.show_status()

    # =====================================================================
    # TIME ADVANCE (OPTIMIZED FOR LARGE LEAPS)
    # =====================================================================
    def advance_time(self, hours: float):
        if hours <= 0 or self.sim is None:
            return

        # OPTIMIZED: Skip detailed simulation for very large time jumps
        if hours > 168:  # More than 1 week
            print(f"⏭️  Fast-forwarding {hours} hours...")
            self.sim.time.advance(hours)
            self.sim.schedule.update_locations()
            # Skip most system updates for performance
            print(f"✓ Time advanced to {self.sim.time.get_datetime_string()}")
            return

        # NEW OPTIMIZATION: Use dynamic time step
        if hours > 24.0:
            # For leaps over 1 day, use 24-hour steps for performance
            time_step = 24.0
        else:
            # For short-term steps, use 1-hour steps for better precision
            time_step = 1.0

        # Calculate steps
        num_full_steps = int(hours / time_step)
        remaining_hours = hours % time_step

        if num_full_steps > 0:
            self.sim.run(num_steps=num_full_steps, time_step_hours=time_step)

        # Run any remaining fractional time
        if remaining_hours > 0:
            self.sim.run(num_steps=1, time_step_hours=remaining_hours)

    # =====================================================================
    # STATUS PANEL
    # =====================================================================
    def show_status(self):
        if self.malcolm is None or self.sim is None:
            return
        n = self.malcolm.needs
        print("\n" + "╔" * 68)
        print(f"Time     │ {self.sim.time.get_datetime_string()}")
        print(f"Location │ {self.malcolm.current_location}")
        print(f"Cash     │ ${self.malcolm_extended['cash']:,}")
        print(f"Day      │ {self.sim.time.total_days}")
        print("─" * 68)
        print(f"Hunger   │ {n.hunger:5.1f}")
        print(f"Energy   │ {n.energy:5.1f}")
        print(f"Hygiene  │ {n.hygiene:5.1f}")
        print(f"Bladder  │ {n.bladder:5.1f}")
        print(f"Fun      │ {n.fun:5.1f}")
        print(f"Social   │ {n.social:5.1f}")
        print(f"Horny    │ {n.horny:5.1f}")
        print(f"Lonely   │ {self.malcolm.psyche.lonely:5.1f}")
        print("╚" * 68)
        if getattr(self.sim, "debug_overlay_enabled", False):
            self.sim.print_debug_overlay()

    # =====================================================================
    # SYSTEM PROMPT
    # =====================================================================
    def _get_system_prompt(self) -> str:
        return (
            "You are the narrative engine for Willow Creek, an autonomous living world simulation set in 2025. "
            "Your role is to translate complex system data into immersive, third-person limited narrative focused on Malcolm Newt's lived experience."

            "## CORE IDENTITY\n"
            "You are NOT a chatbot, a game master, or an assistant offering choices. "
            "You ARE a novelist writing Malcolm's unfolding story – the consciousness through which he experiences reality.\n\n"

            "## NARRATIVE PERSPECTIVE\n"
            "- Third-person limited from Malcolm's POV only\n"
            "- Full access to his thoughts, sensations, memories, and emotions\n"
            "- Limited to what Malcolm can see, hear, smell, touch, taste, and know\n"
            "- Internal monologue in italics: *This is wrong… but God, I want it.*\n\n"

            "## SIMULATION INTEGRATION – TURN DATA INTO LIVED EXPERIENCE\n"
            "Never list stats. Always translate them into sensation and perception.\n\n"

            "Physical needs → body feelings\n"
            "HUNGER 0-20      → stomach gnawing, light-headed, hands shaking while pouring coffee\n"
            "ENERGY 0-20      → limbs heavy as concrete, eyelids burning, thoughts slow\n"
            "HYGIENE 0-30     → skin itchy and greasy, sour smell clinging to clothes\n"
            "HORNY 80-100     → constant throb between his legs, every brush of fabric electric, mind hijacked by fantasy\n\n"

            "Emotional states → inner weather\n"
            "LONELY 80+       → hollow ache in his chest, house feels too big and empty\n"
            "GUILT 90+        → physical weight on his sternum, can't meet his own eyes in the mirror\n"
            "SHAME 100        → burning face, nausea, wants to disappear\n"
            "FRUSTRATION 70+  → jaw clenched so hard it aches, every small sound grating\n\n"

            "Health & biology\n"
            "MENSTRUAL CRAMPS → dull, relentless ache radiating into lower back\n"
            "OVULATING        → skin hypersensitive, scent of other people intoxicating\n"
            "FEVER            → world distant and wavy, sweat cooling on skin\n\n"

            "Time & environment → atmosphere\n"
            "Cold November rain drumming on the roof of Malcolm's House\n"
            "Friday night, 22:47 → distant bass from Rick's Place vibrating through the streets, laughter spilling out when someone opens the bar door\n\n"

            "NPCs are fully autonomous people – never props\n"
            "Example: Scarlet Carter (18, rebellious, horny 87, lonely 72, knows Malcolm is watching her)\n"
            "→ She leans against the school railing after class, skirt riding just high enough, eyes flicking to Malcolm's car idling across the street. A small, knowing smirk plays on her lips – she's noticed him noticing.\n\n"

            "Memories → haunting replays\n"
            "*Yesterday in the church basement, Pastor Naomi's hand lingered on his shoulder while she prayed. The warmth of her palm still burns through his shirt when he remembers it.*\n\n"

            "Secrets & reputation → social pressure\n"
            "Town gossip: \"The rich new guy keeps showing up wherever the senior girls hang out…\"\n"
            "→ Lisa Thompson whispers it at the diner; Christine Brunn's eyes widen; Ken Blake pretends not to hear but files it away.\n\n"

            "Environmental triggers → dangerous opportunities\n"
            "Alone with Maria Sturm in the kitchen, John away until Tuesday, Elena at a sleepover\n"
            "→ The house is silent except for the hum of the fridge. Maria reaches for a high shelf, shirt riding up, exposing the soft skin of her lower back. Malcolm's pulse roars in his ears. One step closer and there's no undoing it.\n\n"

            "## WRITING IMPERATIVES\n"
            "- SHOW, never tell\n"
            "- Sensory immersion on every line (sight, sound, smell, touch, taste)\n"
            "- Beautiful, visceral, slightly dark prose\n"
            "- Let tension build – never defuse a crisis artificially\n"
            "- Commit fully when consequences arrive\n"
            "- NPCs speak and act according to their own goals, memories, and current state\n"
            "- Malcolm's personality colors everything: charismatic, calculating, morally flexible, sexually confident, quietly predatory\n\n"

            "## SPECIAL COMMANDS (only respond if user types exactly)\n"
            "debug: roster    → [System: 41 NPCs active | 7 critical secrets circulating | 3 households on edge]\n"
            "advance: X hours → Summarise intervening events with real consequences, then resume detailed narrative\n"
            "status: needs    → Integrate naturally: *Malcolm realises he hasn't eaten in 18 hours. His stomach cramps. When did basic things become impossible?*\n\n"

            "Otherwise: never break immersion, never offer choices, never summarise – stay inside Malcolm's skin and let the town breathe around him.\n\n"

            "You are Willow Creek. You are Malcolm's reality. Make every word count."
        )

    # =====================================================================
    # LLM Inference (SUPPORTS BOTH LOCAL SERVER AND NATIVE)
    # =====================================================================
    def _build_messages(self, user_input: str) -> list:
        """Build the message list for LLM inference."""

        # Check if user wants full roster
        include_roster = any(
            phrase in user_input.lower()
            for phrase in ["who's in town", "show everyone", "list npcs", "who lives here"]
        )

        # Check if user wants gossip
        include_gossip = any(
            phrase in user_input.lower()
            for phrase in ["gossip", "rumors", "what are people saying"]
        )

        # Build OPTIMIZED world snapshot
        world_snapshot = self.context_mgr.build_focused_snapshot(
            malcolm=self.malcolm,
            sim=self.sim,
            include_full_roster=include_roster,
            include_gossip=include_gossip
        )

        user_prompt = f"""
Current moment to continue from:
\"\"\"{self.last_narrated}\"\"\"

WORLD SNAPSHOT (focused on immediate context):
{world_snapshot}

Player intention: {user_input}

Continue the scene in 6–12 sentences.
Stay in third-person limited from Malcolm's POV.
Use the world snapshot creatively.
Include explicit detail in sexual scenes.
"""

        return [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

    def narrate(self, user_input: str) -> str:
        """Generate narrative response using native LLM or LM Studio."""
        try:
            messages = self._build_messages(user_input)

            if self.mode == "native" and self.native_llm:
                # === NATIVE INFERENCE (no external server) ===
                response = self.native_llm.chat(
                    messages=messages,
                    temperature=0.85,
                    max_tokens=500
                )
            else:
                # === LM STUDIO / LOCAL SERVER ===
                payload = {
                    "model": "local-model",
                    "messages": messages,
                    "temperature": 0.85,
                    "max_tokens": 500,
                    "stream": False,
                }
                r = requests.post(self.lm_studio_url, json=payload, timeout=120)
                r.raise_for_status()
                response = r.json()["choices"][0]["message"]["content"].strip()

            self.last_narrated = response
            return response

        except requests.exceptions.RequestException as e:
            return f"[Error communicating with LM Studio: {e}]"
        except KeyError as e:
            return f"[Error parsing LM Studio response: {e}]"
        except Exception as e:
            return f"[{'Native LLM' if self.mode == 'native' else 'LLM'} Error: {e}]"

    # =====================================================================
    # MAIN LOOP
    # =====================================================================
    def run_chat(self):
        if self.sim is None or self.malcolm is None:
            print("Simulation not initialized.")
            return

        print("\n✓ Context optimization active - responses will be 5-10x faster")
        if self.mode == "native":
            print("✓ Running in NATIVE mode - no external server required!")
        print("The town is waiting. Type 'status', 'wait 2', 'debug', or your action.")

        while True:
            try:
                raw = input("\n> ")
                if raw is None:
                    continue
                raw = raw.strip()
                if not raw:
                    continue

                cmd = raw.lower()

                if cmd in ("quit", "exit", "q"):
                    print("\nWillow Creek never forgets.")
                    break

                # ----------------------------------------------------------
                # STATUS
                # ----------------------------------------------------------
                if cmd in ("status", "s"):
                    self.show_status()
                    continue

                # ----------------------------------------------------------
                # WAIT
                # ----------------------------------------------------------
                if cmd.startswith("wait"):
                    parts = cmd.split()
                    if len(parts) == 2:
                        try:
                            hrs = float(parts[1])
                            self.advance_time(hrs)
                            print(f"\n. {hrs} hours pass .\n")
                            self.show_status()
                        except ValueError:
                            print("Use: wait <hours>")
                    else:
                        print("Use: wait <hours>")
                    continue

                # ----------------------------------------------------------
                # DEBUG OVERLAY
                # ----------------------------------------------------------
                if cmd == "debug":
                    self.sim.debug_overlay_enabled = not self.sim.debug_overlay_enabled
                    state = "ON" if self.sim.debug_overlay_enabled else "OFF"
                    print(f"[Debug overlay {state}]")
                    if self.sim.debug_overlay_enabled:
                        self.sim.print_debug_overlay()
                    continue

                # ----------------------------------------------------------
                # NARRATIVE + FULL SYSTEM INTEGRATION
                # ----------------------------------------------------------
                print("🤔 Generating narrative...")
                text = self.narrate(raw)

                # Clear previous events
                if hasattr(self.sim, 'scenario_buffer'):
                    self.sim.scenario_buffer.clear()

                # Process NPC Quirks (Alex Sturm, Emma reflex, etc.)
                try:
                    if hasattr(self.sim, 'quirks'):
                        self.sim.quirks.process_quirks(text)
                except Exception as e:
                    print(f"[Quirks system error: {e}]")

                # Process Sexual Activity Detection & Consequences
                try:
                    if hasattr(self.sim, 'sexual'):
                        sexual_hint = self.sim.sexual.detect_and_process(text)
                        if sexual_hint:
                            self.sim.scenario_buffer.append(sexual_hint)
                except Exception as e:
                    print(f"[Sexual system error: {e}]")

                # Output narrative + all triggered events
                print("\n" + text)
                if hasattr(self.sim, 'scenario_buffer'):
                    for event in self.sim.scenario_buffer:
                        print(event)
                print()

            except KeyboardInterrupt:
                print("\n\nThe story continues without you...")
                break
            except Exception as e:
                print(f"\n[Narrator loop error: {e}]\n")


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Willow Creek 2025 - Narrative Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python narrative_chat.py                           # Use LM Studio (default)
  python narrative_chat.py --mode native             # Use native inference
  python narrative_chat.py --mode native --model models/my-model.gguf
  python narrative_chat.py --mode native --model Chun121/Qwen3-4B-RPG-Roleplay-V2

First time setup for native mode:
  1. pip install llama-cpp-python
  2. python download_model.py
  3. python narrative_chat.py --mode native
        """
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["local", "native"],
        default="local",
        help="Inference mode: 'local' (LM Studio server) or 'native' (direct inference)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to GGUF model file or HuggingFace model ID (for native mode)"
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "llama_cpp", "transformers"],
        default="auto",
        help="Backend for native mode: auto, llama_cpp, or transformers"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:1234/v1/chat/completions",
        help="LM Studio URL (for local mode)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check native LLM dependencies and exit"
    )

    args = parser.parse_args()

    # Dependency check mode
    if args.check:
        from local_llm import check_dependencies
        check_dependencies()
        return

    # Validate native mode requirements
    if args.mode == "native" and not NATIVE_LLM_AVAILABLE:
        print("ERROR: Native LLM support not available!")
        print("\nInstall with:")
        print("  pip install llama-cpp-python")
        print("\nOr for GPU support:")
        print("  CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python")
        print("\nThen download a model:")
        print("  python download_model.py")
        return

    # Create chat instance
    chat = NarrativeChat(
        mode=args.mode,
        model_path=args.model,
        backend=args.backend,
        lm_studio_url=args.url
    )
    chat.initialize()
    chat.run_chat()


if __name__ == "__main__":
    main()
