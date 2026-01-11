# narrative_chat.py – Willow Creek 2025 Narrative Interface
# FIXED VERSION with robust error handling
import requests
from typing import Optional
from simulation_v2 import WillowCreekSimulation
from entities.npc import NPC, Gender


class NarrativeChat:
    def __init__(
        self,
        lm_studio_url: str = "http://localhost:1234/v1/chat/completions",
        memory_model_name: str = "local-model",
    ):
        self.lm_studio_url = lm_studio_url
        self.memory_model_name = memory_model_name
        self.sim: Optional[WillowCreekSimulation] = None
        self.malcolm: Optional[NPC] = None
        self.malcolm_extended = {}
        self.last_narrated: str = ""
        self.memory_enabled = True

    def initialize(self):
        print("\n" + "=" * 80)
        print(" WILLOW CREEK 2025")
        print(" Dark Autumn • Living World • Third-Person Limited")
        print("=" * 80 + "\n")

        # Start full simulation
        self.sim = WillowCreekSimulation(num_npcs=41)
        if not self.sim or not self.sim.npcs:
            print("World failed to initialize: no NPCs loaded.")
            return

        # Player character
        self.malcolm = self.sim.world.get_npc("Malcolm Newt")
        if not self.malcolm:
            self.malcolm = NPC(
                full_name="Malcolm Newt",
                age=30,
                gender=Gender.MALE,
                occupation="Unemployed (Wealthy)",
            )
            self.sim.npcs.append(self.malcolm)
            self.sim.npc_dict[self.malcolm.full_name] = self.malcolm

        self.malcolm_extended = {
            "cash": 50000,
            "days_in_town": 0,
        }

        self.last_narrated = (
            "The small town of Willow Creek, on this Monday morning at 8:00 AM, "
            "carried the heavy scent of recent rain and distant woodsmoke. It was the smell of quiet stagnation.\n"
            "A sleek, matte-black Rivian R1S—silent as a predator—glided to a stop outside Malcolm’s new house on Oak Street. "
            "The electric silence of the truck was quickly absorbed by the low ambient hum of the neighborhood.\n"
            "Malcolm Newt stepped out, his expensive, unzipped jacket offering a casual contrast to his sharp, unblinking gaze. "
            "Loki, his Doberman, moved with coiled efficiency from the passenger side, his collar jangling once before Malcolm snapped the leash on.\n"
            "\"Time to map the territory, boy,\" Malcolm murmured, taking in the scene. He thought of his new possession—the house—as a strategic insertion point into this closed system. He intended to master it.\n"
            "He observed his immediate neighbors with the detached interest of a scientist studying a petri dish:\n"
            "On a nearby porch, a woman in her early thirties was attempting to usher a teenage boy toward the street. "
            "Her agitation was palpable—a tightly pinched mouth, arms gesturing sharply. The boy, however, resisted, "
            "hunched over a small notebook, scribbling furiously as if battling a deadline for his life. He looked up, his "
            "movements stiff and defensive, his eyes meeting Malcolm’s across the distance. The boy's gaze was unsettlingly "
            "analytical, holding none of the usual teenage boredom. Malcolm registered a spark of suspicion—an observer who was also being observed. "
            "Interesting. The pressure point is the son.\n"
            "Further down the street, a different kind of tension was unfolding. A woman with unruly chestnut hair, clearly past forty, "
            "was pacing beside her parked sedan. She was twisting a section of her hair repeatedly—a tell for acute anxiety—while holding a phone to her ear. "
            "Her voice was too low to discern, but her body language spoke of distress and vulnerability, a private storm being aired on a public street. "
            "Malcolm cataloged the hurried gestures and the restless energy. Unresolved conflict, easily exploitable.\n"
            "Loki gave a soft, expectant whuff, tugging the leash gently toward the newly mown lawn. The crisp air, the contained dramas, "
            "the predictable routines—all waiting to be disrupted. Malcolm smiled faintly, adjusting the collar of his jacket."
        )

        print(self.last_narrated + "\n")
        self.show_status()

    def advance_time(self, hours: float):
        if hours <= 0 or self.sim is None:
            return

        if hours > 24.0:
            time_step = 24.0
        else:
            time_step = 1.0
        
        num_full_steps = int(hours / time_step)
        remaining_hours = hours % time_step

        if num_full_steps > 0:
            self.sim.run(num_steps=num_full_steps, time_step_hours=time_step)
        
        if remaining_hours > 0:
            self.sim.run(num_steps=1, time_step_hours=remaining_hours)

    def show_status(self):
        if self.malcolm is None or self.sim is None:
            return
        n = self.malcolm.needs
        print("\n" + "═" * 68)
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
        print("═" * 68)

    def _build_lm_payload(self, user_input: str):
        nearby = [
            npc.full_name
            for npc in self.sim.npcs
            if npc.current_location == self.malcolm.current_location
            and npc.full_name != "Malcolm Newt"
        ][:6]
        
        # Build world snapshot
        world_snapshot = self.sim.build_world_snapshot(self.malcolm)

        system_prompt = (
    "You are the living, breathing narrative voice of Willow Creek, autumn 2025: a small American town heavy with secrets, "
    "unspoken desires, and the low hum of hidden lives. Write exclusively in third-person limited, anchored to Malcolm Newt’s senses "
    "and perceptions. Let the air feel damp with woodsmoke and wet leaves, let every glance and half-heard conversation carry weight. "
    "Use the provided world snapshot and recent events as absolute truth. Continue the scene in 4–8 vivid, flowing sentences. "
    "Never summarize, never offer choices, never speak as Malcolm, never break immersion. "
    "The town is watching. The porch lights flicker. Something is always about to happen."
)

        user_prompt = f"""
        Current scene:
        \"\"\"{self.last_narrated}\"\"\"

        WORLD STATE:
        {world_snapshot}

        Player action: {user_input}

        Continue the narrative in 4-8 sentences, third-person limited from Malcolm's POV.
        """

        return {
            "model": "local-model",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.85,
            "max_tokens": 500,
            "stream": False,
        }

    def _build_memory_payload(self, user_input: str, response: str, world_snapshot: str):
        system_prompt = (
            "You extract durable narrative memories from the latest scene.\n"
            "Return ONLY JSON (no markdown). Use this schema:\n"
            "[\n"
            "  {\n"
            "    \"description\": \"short memory description\",\n"
            "    \"memory_type\": \"conversation|conflict|gift_given|gift_received|special_event|first_meeting|achievement|embarrassment|betrayal\",\n"
            "    \"importance\": \"trivial|minor|moderate|significant|major|life_changing\",\n"
            "    \"participants\": [\"Name A\", \"Name B\"],\n"
            "    \"location\": \"Location if known\"\n"
            "  }\n"
            "]\n"
            "Rules: 0-3 memories, only include durable events that should persist.\n"
        )

        user_prompt = (
            f"World snapshot:\n{world_snapshot}\n\n"
            f"Player action: {user_input}\n\n"
            f"Narrative response:\n{response}\n"
        )

        return {
            "model": self.memory_model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 300,
            "stream": False,
        }

    def narrate(self, user_input: str) -> str:
        payload = self._build_lm_payload(user_input)
        
        try:
            r = requests.post(self.lm_studio_url, json=payload, timeout=120)
            r.raise_for_status()
            
            # Try to parse JSON response
            try:
                json_response = r.json()
            except ValueError as e:
                print(f"\n[ERROR] LM Studio returned invalid JSON.")
                print(f"Response status: {r.status_code}")
                print(f"Response text (first 500 chars): {r.text[:500]}")
                print(f"\nTroubleshooting:")
                print(f"  1. Is LM Studio running at {self.lm_studio_url}?")
                print(f"  2. Do you have a model loaded?")
                print(f"  3. Is the local server started in LM Studio?\n")
                return "[Narrator Error: LM Studio response invalid]"
            
            # Extract content
            if "choices" in json_response and len(json_response["choices"]) > 0:
                response = json_response["choices"][0]["message"]["content"].strip()
                self.last_narrated = response
                world_snapshot = self.sim.build_world_snapshot(self.malcolm)
                self._update_memory(user_input, response, world_snapshot)
                return response
            else:
                print(f"\n[ERROR] Unexpected response format from LM Studio:")
                print(f"{json_response}\n")
                return "[Narrator Error: Unexpected response format]"
                
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Cannot connect to LM Studio at {self.lm_studio_url}")
            print("\nTroubleshooting:")
            print("  1. Is LM Studio running?")
            print("  2. Is the local server started? (Click 'Start Server' in LM Studio)")
            print("  3. Is the URL correct? (Default: http://localhost:1234)")
            print("  4. Do you have a model loaded in LM Studio?\n")
            return "[Narrator Error: Cannot connect to LM Studio - see console]"
            
        except requests.exceptions.Timeout:
            print(f"\n[ERROR] LM Studio request timed out after 120 seconds.")
            print("The model might be too slow or stuck.\n")
            return "[Narrator Error: Request timed out]"
            
        except Exception as e:
            print(f"\n[ERROR] Unexpected error calling LM Studio: {e}\n")
            import traceback
            traceback.print_exc()
            return f"[Narrator Error: {e}]"

    def _update_memory(self, user_input: str, response: str, world_snapshot: str) -> None:
        if not self.sim or not self.sim.memory or not self.memory_enabled:
            return

        payload = self._build_memory_payload(user_input, response, world_snapshot)

        try:
            r = requests.post(self.lm_studio_url, json=payload, timeout=60)
            r.raise_for_status()
            json_response = r.json()
        except Exception as exc:
            print(f"\n[ERROR] Memory model call failed: {exc}")
            return

        if "choices" not in json_response or not json_response["choices"]:
            return

        content = json_response["choices"][0]["message"]["content"].strip()
        memories = self._parse_memory_json(content)
        if not memories:
            return
        self._store_memories(memories)

    def _parse_memory_json(self, content: str):
        import json

        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1 and end > start:
            content = content[start : end + 1]

        try:
            data = json.loads(content)
        except Exception:
            return []

        if not isinstance(data, list):
            return []

        return [item for item in data if isinstance(item, dict)]

    def _store_memories(self, memories):
        from systems.memory_system import MemoryType, MemoryImportance

        current_day = self.sim.time.total_days
        current_hour = self.sim.time.hour

        memory_type_map = {
            "conversation": MemoryType.CONVERSATION,
            "conflict": MemoryType.CONFLICT,
            "gift_given": MemoryType.GIFT_GIVEN,
            "gift_received": MemoryType.GIFT_RECEIVED,
            "special_event": MemoryType.SPECIAL_EVENT,
            "first_meeting": MemoryType.FIRST_MEETING,
            "achievement": MemoryType.ACHIEVEMENT,
            "embarrassment": MemoryType.EMBARRASSMENT,
            "betrayal": MemoryType.BETRAYAL,
        }

        for entry in memories:
            description = str(entry.get("description", "")).strip()
            if not description:
                continue

            memory_type_value = str(entry.get("memory_type", "special_event")).lower()
            memory_type = memory_type_map.get(memory_type_value, MemoryType.SPECIAL_EVENT)

            importance_value = str(entry.get("importance", "minor")).upper()
            importance = MemoryImportance.MINOR
            if hasattr(MemoryImportance, importance_value):
                importance = MemoryImportance[importance_value]

            participants = entry.get("participants") or []
            if not isinstance(participants, list):
                participants = []

            location = str(entry.get("location", "")).strip()

            self.sim.memory.add_memory(
                "Malcolm Newt",
                memory_type,
                description,
                current_day,
                current_hour,
                importance,
                participants=participants,
                location=location,
            )

    def run_chat(self):
        if self.sim is None or self.malcolm is None:
            print("Simulation not initialized.")
            return

        print("\n" + "="*68)
        print("COMMANDS:")
        print("  status / s     - Show Malcolm's status")
        print("  wait <hours>   - Advance time")
        print("  quit / q       - Exit")
        print("  [anything else] - Narrative action")
        print("="*68 + "\n")

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

                if cmd in ("status", "s"):
                    self.show_status()
                    continue
                    
                # FIX: Moved Debug Check Here
                if cmd == "debug":
                    self.sim.debug_enabled = not self.sim.debug_enabled
                    state = "ON" if self.sim.debug_enabled else "OFF"
                    print(f"[Debug overlay {state}]")
                    if self.sim.debug_enabled:
                        print(self.sim.debug.render())
                    continue    

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
                    
                  

                # Narrative
                text = self.narrate(raw)
                
                # Process systems
                self.sim.scenario_buffer.clear()
                
                try:
                    self.sim.quirks.process_quirks(text)
                except:
                    pass
                
                try:
                    sexual_hint = self.sim.sexual.detect_and_process(text)
                    if sexual_hint:
                        self.sim.scenario_buffer.append(sexual_hint)
                except:
                    pass

                # Output
                print("\n" + text)
                for event in self.sim.scenario_buffer:
                    print(event)
                print()

            except KeyboardInterrupt:
                print("\n\nThe story continues without you...")
                break
            except Exception as e:
                print(f"\n[Narrator loop error: {e}]")
                import traceback
                traceback.print_exc()
                
                  


def main():
    chat = NarrativeChat()
    chat.initialize()
    chat.run_chat()
    
    


if __name__ == "__main__":
    main()
