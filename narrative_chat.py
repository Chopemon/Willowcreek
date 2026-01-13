# narrative_chat.py
# FIXED: Restored original atmospheric opening, system prompt, and prompt structure.

import requests
import os
from typing import Optional, List, Dict
from pathlib import Path
from simulation_v2 import WillowCreekSimulation
from entities.npc import NPC
from enhanced_snapshot_builder import create_narrative_context
from llm_client import LocalLLMClient

def _resolve_max_tokens(env_name: str, default: int) -> int:
    value = os.getenv(env_name)
    if not value:
        return default
    try:
        return max(int(value), 1)
    except ValueError:
        return default


CONFIG = {
    "openrouter": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model_name": "tngtech/deepseek-r1t2-chimera:free",
        "memory_model_name": "openai/gpt-4o-mini",
        "key_env": "OPENROUTER_API_KEY"
    },
    "local": {
        "api_url": "http://localhost:1234/v1/chat/completions",
        "model_name": "local-model",
        "memory_model_name": "local-model",
        "key_env": None,
        "context_size": 2048
    }
}

NARRATIVE_MAX_TOKENS = 2048
MEMORY_MAX_TOKENS = 2048

class NarrativeChat:
    def __init__(
        self,
        mode: str = "openrouter",
        model_name: Optional[str] = None,
        memory_model_name: Optional[str] = None,
        api_url: Optional[str] = None,
    ):
        if mode not in CONFIG: raise ValueError(f"Invalid mode: {mode}")

        self.mode = mode
        self.api_url = api_url or (None if mode == "local" else CONFIG[mode]["api_url"])
        self.model_name = model_name or CONFIG[mode]["model_name"]
        self.memory_model_name = memory_model_name or self.model_name or CONFIG[mode]["memory_model_name"]
        self.local_client: Optional[LocalLLMClient] = None
        self.local_memory_client: Optional[LocalLLMClient] = None

        # Debug logging for mode initialization
        print(f"\n[NarrativeChat] ===== INITIALIZING =====")
        print(f"[NarrativeChat] Mode: {mode}")
        print(f"[NarrativeChat] API URL: {self.api_url or 'local-client'}")
        print(f"[NarrativeChat] Model: {self.model_name}")
        print(f"[NarrativeChat] Memory Model: {self.memory_model_name}")

        if mode == "local":
            self.api_key = "NOT_REQUIRED"
            resolved_model = self._resolve_local_model(self.model_name)
            resolved_memory_model = self._resolve_local_model(self.memory_model_name)
            self.local_client = LocalLLMClient(model_name=resolved_model)
            if self.memory_model_name == self.model_name:
                self.local_memory_client = self.local_client
            else:
                self.local_memory_client = LocalLLMClient(model_name=resolved_memory_model)
            print(f"[NarrativeChat] API Key: Not required for local mode")
        elif CONFIG[mode]["key_env"]:
            self.api_key = os.getenv(CONFIG[mode]["key_env"])
            if not self.api_key:
                print(f"WARNING: {CONFIG[mode]['key_env']} not set.")
            else:
                print(f"[NarrativeChat] API Key: {'*' * 10} (found)")
        else:
            self.api_key = "NOT_REQUIRED"
            print(f"[NarrativeChat] API Key: Not required for local mode")

        print(f"[NarrativeChat] ========================\n")

        self.sim: Optional[WillowCreekSimulation] = None
        self.malcolm: Optional[NPC] = None
        self.narrative_history: List[Dict] = [] 
        self.last_narrated: str = ""
        self.memory_enabled = True

    def initialize(self):
        self.sim = WillowCreekSimulation()
        
        # Robustly find Malcolm
        self.malcolm = self.sim.npc_dict.get("Malcolm Newt")
        if not self.malcolm and self.sim.npcs:
            self.malcolm = self.sim.npcs[0]

        # --- RESTORED ORIGINAL STARTING MESSAGE ---
        self.last_narrated = (
            "The small town of Willow Creek, on this Monday morning at 8:30 AM, carried the heavy scent of recent rain and distant woodsmoke. "
            "It was the smell of quiet stagnation.\n"
            "A sleek, matte-black Rivian R1S—silent as a predator—glided to a stop outside Malcolm’s new house on Oak Street. "
            "The electric silence of the truck was quickly absorbed by the low ambient hum of the neighborhood.\n"
            "Malcolm Newt stepped out, his expensive, unzipped jacket offering a casual contrast to his sharp, unblinking gaze. "
            "Loki, his Doberman, moved with coiled efficiency from the passenger side, his collar jangling once before Malcolm snapped the leash on.\n"
            "\"Time to map the territory, boy,\" Malcolm murmured, taking in the scene. He thought of his new possession—the house—as a strategic insertion point into this closed system. He intended to master it.\n"
            "He observed his immediate neighbors with the detached interest of a scientist studying a petri dish:\n"
            "On a nearby porch, a woman in her early thirties was attempting to usher a teenage boy toward the street. Her agitation was palpable—a tightly pinched mouth, arms gesturing sharply. "
            "The boy, however, resisted, hunched over a small notebook, scribbling furiously as if battling a deadline for his life. He looked up, his movements stiff and defensive, his eyes meeting Malcolm’s across the distance. "
            "The boy's gaze was unsettlingly analytical, holding none of the usual teenage boredom. Malcolm registered a spark of suspicion—an observer who was also being observed. Interesting. The pressure point is the son.\n"
            "Further down the street, a different kind of tension was unfolding. A woman with unruly chestnut hair, clearly past forty, was pacing beside her parked sedan. "
            "She was twisting a section of her hair repeatedly—a tell for acute anxiety—while holding a phone to her ear. Her voice was too low to discern, but her body language spoke of distress and vulnerability, a private storm being aired on a public street. "
            "Malcolm cataloged the hurried gestures and the restless energy. Unresolved conflict, easily exploitable.\n"
            "Loki gave a soft, expectant whuff, tugging the leash gently toward the newly mown lawn. The crisp air, the contained dramas, the predictable routines—all waiting to be disrupted. "
            "Malcolm smiled faintly, adjusting the collar of his jacket."
        )

        # Initialize history with the static system prompt
        # Note: We don't put `last_narrated` in history yet; it gets fed via the user prompt structure below.
        self.narrative_history = []

    def narrate(self, user_input: str) -> str:
        # 1. Get World Snapshot
        world_snapshot = create_narrative_context(self.sim, self.malcolm)
        if self.sim and self.sim.memory and self.memory_enabled:
            query = f"{user_input}\n{self.last_narrated}"
            retrieved = self.sim.memory.build_retrieved_memory_context(
                "Malcolm Newt",
                query,
                current_sim_day=self.sim.time.total_days,
            )
            if retrieved:
                world_snapshot = f"{world_snapshot}\n\n{retrieved}"

        # --- DIALOGUE-FOCUSED SYSTEM PROMPT ---
        system_prompt = (
            "You are the narrative voice of Willow Creek, autumn 2025: a small American town heavy with secrets and unspoken desires. "
            "Write in third-person limited, anchored to Malcolm Newt's perspective. "
            "\n\n"
            "DIALOGUE REQUIREMENTS:\n"
            "- Include substantial character dialogue in every response (60-70% dialogue, 30-40% description)\n"
            "- Characters speak naturally with distinct voices, regional quirks, and subtext\n"
            "- Malcolm speaks his thoughts aloud - show his words in quotes\n"
            "- Use dialogue to reveal character, advance plot, and create tension\n"
            "- Balance conversation with brief sensory details (scents, textures, sounds)\n"
            "\n"
            "STYLE:\n"
            "- Literary noir atmosphere: tense, observant, laden with meaning\n"
            "- Show subtext through what's said vs. what's meant\n"
            "- Use body language and micro-reactions between dialogue lines\n"
            "- The air feels damp with woodsmoke; every word carries weight\n"
            "\n"
            "RULES:\n"
            "- Use provided world snapshot as absolute truth\n"
            "- Continue the scene in 6-10 sentences with multiple lines of dialogue\n"
            "- Never summarize, never offer choices, never break immersion\n"
            "- The town is watching. Something is always about to happen."
        )

        # --- RESTORED ORIGINAL USER PROMPT STRUCTURE ---
        user_prompt = f"""
        Current scene:
        \"\"\"{self.last_narrated}\"\"\"

        WORLD STATE:
        {world_snapshot}

        Player action: {user_input}

        Continue the narrative with substantial dialogue. Include Malcolm's spoken words and NPC responses.
        """

        # Build Messages for API
        # OPTIMIZED: Reduced from 6 to 4 turns to save tokens (250-500 tokens per call)
        messages = [{"role": "system", "content": system_prompt}]

        # Add simple history (exclude system/rich prompts to save tokens, just raw conversation)
        # We take the last 4 interactions (2 user + 2 assistant) from history to maintain continuity
        messages.extend(self.narrative_history[-4:]) 
        
        # Append the current detailed prompt
        messages.append({"role": "user", "content": user_prompt})

        # Prepare Payload
        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key != "NOT_REQUIRED":
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.85, # Slightly higher for creative writing
            "max_tokens": NARRATIVE_MAX_TOKENS
        }
        if self.context_size:
            payload["max_context_tokens"] = self.context_size

        try:
            if self.local_client:
                print(f"[NarrativeChat] Using local model: {self.model_name}")
                prompt = self._build_prompt(messages)
                response = self.local_client.generate(
                    prompt,
                    max_new_tokens=payload["max_tokens"],
                    temperature=payload["temperature"],
                )
                content = response.text
            else:
                print(f"[NarrativeChat] Making API call to: {self.api_url}")
                print(f"[NarrativeChat] Using model: {self.model_name}")
                print(f"[NarrativeChat] Temperature: {payload['temperature']}, Max tokens: {payload['max_tokens']}")

                res = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

                print(f"[NarrativeChat] Response status: {res.status_code}")

                if res.status_code != 200:
                    print(f"[NarrativeChat] API Error: {res.text}")
                    return f"[API Error: {res.text}]"

                content = res.json()["choices"][0]["message"]["content"]
                print(f"[NarrativeChat] Response received, length: {len(content)} characters")

            # Update History
            # We store the simplified version in history to avoid exploding context size with repetitive World States
            self.narrative_history.append({"role": "user", "content": user_input})
            self.narrative_history.append({"role": "assistant", "content": content})

            self.last_narrated = content
            self._update_memory(user_input, content, world_snapshot)
            return content
        except Exception as e:
            return f"[Connection Error: {e}]"

    def advance_time(self, hours):
        if self.sim:
            self.sim.tick(hours)

    def _update_memory(self, user_input: str, response: str, world_snapshot: str) -> None:
        if not self.sim or not self.sim.memory or not self.memory_enabled:
            return

        prompt = (
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

        user_payload = (
            f"World snapshot:\n{world_snapshot}\n\n"
            f"Player action: {user_input}\n\n"
            f"Narrative response:\n{response}\n"
        )

        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key != "NOT_REQUIRED":
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.memory_model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_payload},
            ],
            "temperature": 0.2,
            "max_tokens": MEMORY_MAX_TOKENS,
        }
        if self.context_size:
            payload["max_context_tokens"] = self.context_size

        try:
            if self.local_memory_client:
                prompt_text = self._build_prompt(payload["messages"])
                response = self.local_memory_client.generate(
                    prompt_text,
                    max_new_tokens=payload["max_tokens"],
                    temperature=payload["temperature"],
                )
                content = response.text
            else:
                res = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                if res.status_code != 200:
                    print(f"[NarrativeChat] Memory model error: {res.text}")
                    return
                content = res.json()["choices"][0]["message"]["content"]

            memories = self._parse_memory_json(content)
            if not memories:
                return
            self._store_memories(memories)
        except Exception as exc:
            print(f"[NarrativeChat] Memory update failed: {exc}")

    @staticmethod
    def _build_prompt(messages: List[Dict]) -> str:
        lines = []
        for message in messages:
            role = message.get("role", "user").upper()
            content = message.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    @staticmethod
    def _resolve_local_model(model_name: str) -> str:
        if not model_name:
            return model_name
        candidate = Path(model_name)
        if candidate.exists():
            return str(candidate.resolve())
        has_separator = "/" in model_name or "\\" in model_name
        if has_separator:
            return model_name
        models_root = Path(os.getenv("LOCAL_MODELS_DIR", "models"))
        resolved = models_root / model_name
        if resolved.exists():
            return str(resolved.resolve())
        return model_name

    def _parse_memory_json(self, content: str) -> List[Dict]:
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

    def _store_memories(self, memories: List[Dict]) -> None:
        from systems.memory_system import MemoryType, MemoryImportance

        current_day = self.sim.time.total_days
        current_hour = self.sim.time.hour

        for entry in memories:
            description = str(entry.get("description", "")).strip()
            if not description:
                continue

            memory_type_value = str(entry.get("memory_type", "special_event")).lower()
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
