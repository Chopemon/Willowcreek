# narrative_chat.py
# FIXED: Restored original atmospheric opening, system prompt, and prompt structure.

import requests
import os
from typing import Optional, List, Dict, Tuple
from pathlib import Path
from simulation_v2 import WillowCreekSimulation
from entities.npc import NPC
from enhanced_snapshot_builder import create_narrative_context
from llm_client import LocalLLMClient
from systems.ai_orchestrator import (
    AIDirector,
    BrainRouter,
    CentralWorldEngine,
    CharacterState,
    PerceptionSystem,
    VectorMemoryStore,
    WorldEvent,
)

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
    },
    "lmstudio": {
        "api_url": os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1/chat/completions"),
        "model_name": os.getenv("LMSTUDIO_MODEL_NAME", "local-model"),
        "memory_model_name": os.getenv("LMSTUDIO_MEMORY_MODEL_NAME", "local-model"),
        "key_env": None,
        "context_size": 2048
    }
}

NARRATIVE_MAX_TOKENS = 2048
MEMORY_MAX_TOKENS = 2048
DIRECTOR_MAX_REQUESTS_PER_TICK = 2

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
        self.context_size = CONFIG[mode].get("context_size")
        self.ai_director_enabled = os.getenv("ENABLE_AI_DIRECTOR", "1") != "0"
        self.director_max_requests_per_tick = _resolve_max_tokens(
            "DIRECTOR_MAX_REQUESTS_PER_TICK",
            DIRECTOR_MAX_REQUESTS_PER_TICK,
        )
        self.world_engine: Optional[CentralWorldEngine] = None
        self.perception_system: Optional[PerceptionSystem] = None
        self.vector_memory: Optional[VectorMemoryStore] = None
        self.brain_router: Optional[BrainRouter] = None
        self.ai_director: Optional[AIDirector] = None
        self.last_director_events: List[str] = []

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
        self.tv_mode_enabled = os.getenv("ENABLE_TV_MODE", "1") != "0"
        self.tv_cut_interval = _resolve_max_tokens("TV_CUT_INTERVAL", 3)
        self.tv_scene_hours = _resolve_max_tokens("TV_SCENE_HOURS", 1)
        self.tv_beat = 0
        self.tv_focus_npc_name: Optional[str] = None

    def initialize(self):
        self.sim = WillowCreekSimulation()
        
        # Robustly find Malcolm
        self.malcolm = self.sim.npc_dict.get("Malcolm Newt")
        if not self.malcolm and self.sim.npcs:
            self.malcolm = self.sim.npcs[0]

        # TV-mode cold open: visual, concise, and action-forward.
        self.last_narrated = (
            "Morning rain still clung to the sidewalks of Willow Creek when a matte-black Rivian R1S rolled silently onto Oak Street. "
            "The neighborhood carried the smell of wet leaves, woodsmoke, and routines no one had interrupted yet.\n"
            "Malcolm Newt stepped out like he already belonged there—open jacket, steady hands, unreadable eyes. "
            "Loki, his Doberman, dropped from the passenger side, and Malcolm clipped on the leash without looking away from the houses around him.\n"
            "Across the street, a woman on a porch was trying to push a teenage boy out the door while he kept scribbling in a notebook, refusing to move. "
            "Halfway down the block, another woman paced beside a sedan with a phone pressed to her ear, twisting her hair tighter every few seconds.\n"
            "\"Time to map the territory, boy,\" Malcolm said softly.\n"
            "His attention settled on the woman by the sedan. Public distress usually meant private fracture. "
            "He reached back into the Rivian, took a bouquet from the front seat, and started across the street with Loki at his side."
        )

        # Initialize history with the static system prompt
        # Note: We don't put `last_narrated` in history yet; it gets fed via the user prompt structure below.
        self.narrative_history = []

        if self.ai_director_enabled:
            self._initialize_ai_director()

    def narrate(self, user_input: str) -> str:
        if self.tv_mode_enabled:
            return self._narrate_tv_mode(user_input)

        # Legacy Malcolm-anchored flow
        return self._narrate_single_focus(user_input)

    def _narrate_single_focus(self, user_input: str) -> str:
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
        if self.last_director_events:
            events_block = "\n".join(f"- {item}" for item in self.last_director_events)
            world_snapshot = f"{world_snapshot}\n\n## NPC EVENT-DRIVEN REACTIONS\n{events_block}"

        system_prompt = (
            "You are the narrative voice of Willow Creek, autumn 2025. "
            "Write in third-person limited, anchored to Malcolm Newt's perspective."
        )
        user_prompt = f"""
        Current scene:
        \"\"\"{self.last_narrated}\"\"\"

        WORLD STATE:
        {world_snapshot}

        Player action: {user_input}
        """
        return self._generate_scene(system_prompt, user_prompt, user_input, world_snapshot, "Malcolm Newt")

    def _narrate_tv_mode(self, user_input: str) -> str:
        if self.sim and self.tv_scene_hours > 0:
            self.sim.tick(float(self.tv_scene_hours))
            self._sync_world_engine_state()

        self.tv_beat += 1
        focus_npc, tension_reason = self._select_focus_npc(user_input)
        focus_name = focus_npc.full_name if focus_npc else "Malcolm Newt"

        world_snapshot = create_narrative_context(self.sim, self.malcolm)
        if self.sim and self.sim.memory and self.memory_enabled:
            query = f"{user_input}\n{self.last_narrated}\n{focus_name}"
            retrieved = self.sim.memory.build_retrieved_memory_context(
                focus_name,
                query,
                current_sim_day=self.sim.time.total_days,
            )
            if retrieved:
                world_snapshot = f"{world_snapshot}\n\n{retrieved}"

        if self.last_director_events:
            events_block = "\n".join(f"- {item}" for item in self.last_director_events)
            world_snapshot = f"{world_snapshot}\n\n## DIRECTOR FEED\n{events_block}"

        focus_profile = self._build_focus_profile(focus_npc)
        system_prompt = (
            "You are the showrunner-narrator for an ensemble TV drama set in Willow Creek. "
            "Malcolm Newt is the catalyst and central thread, but each scene can focus on different residents.\n"
            "Write in third-person limited from the CURRENT CAMERA FOCUS character only.\n"
            "Preserve character truth using their profile, conflict, vulnerabilities, and social context.\n"
            "Scene cuts should feel like prestige TV: motivated by gossip, relationship tension, and emerging conflict.\n"
            "Use 6-10 sentences with meaningful dialogue and subtext."
        )

        user_prompt = f"""
        EPISODE BEAT: {self.tv_beat}
        CAMERA FOCUS: {focus_name}
        CUT MOTIVATION: {tension_reason}

        FOCUS CHARACTER PROFILE:
        {focus_profile}

        PREVIOUS SCENE:
        \"\"\"{self.last_narrated}\"\"\"

        WORLD STATE:
        {world_snapshot}

        STORY THREAD:
        Malcolm is the new stranger in town. Gossip about him is spreading through Willow Creek.

        DIRECTION:
        {user_input or 'Continue the episode naturally with a meaningful scene cut if needed.'}
        """

        return self._generate_scene(system_prompt, user_prompt, user_input, world_snapshot, focus_name)

    def _select_focus_npc(self, user_input: str) -> Tuple[Optional[NPC], str]:
        if not self.sim or not self.sim.npcs:
            self.tv_focus_npc_name = "Malcolm Newt"
            return self.malcolm, "Holding on Malcolm while the ensemble initializes."

        normalized_input = (user_input or "").strip().lower()
        candidates: List[NPC] = [npc for npc in self.sim.npcs if npc.full_name != "Malcolm Newt"]
        if not candidates:
            self.tv_focus_npc_name = "Malcolm Newt"
            return self.malcolm, "No alternate cast available yet."

        # 1) Player-directed override: if user names an NPC, focus them immediately.
        for npc in candidates:
            if npc.full_name.lower() in normalized_input:
                self.tv_focus_npc_name = npc.full_name
                return npc, f"Player directed camera toward {npc.full_name}."

        candidate_names = {npc.full_name for npc in candidates}

        # 2) Keep the current POV between cuts for scene continuity.
        if self.tv_focus_npc_name in candidate_names and self.tv_cut_interval > 1:
            if self.tv_beat % self.tv_cut_interval != 0:
                held = next((npc for npc in candidates if npc.full_name == self.tv_focus_npc_name), None)
                if held:
                    return held, f"Hold on {held.full_name} to complete the current scene beat."

        # 3) Automatic cut: score cast tension and rotate deterministically across top contenders.
        scored: List[Tuple[int, str, NPC]] = []
        for npc in candidates:
            score = self._score_npc_tension(npc)
            scored.append((score, npc.full_name, npc))

        scored.sort(key=lambda item: (-item[0], item[1]))
        top_pool = [item[2] for item in scored[: max(1, min(4, len(scored)))]]
        chosen = top_pool[(self.tv_beat // max(self.tv_cut_interval, 1)) % len(top_pool)]
        self.tv_focus_npc_name = chosen.full_name
        return chosen, f"Automatic ensemble cut to {chosen.full_name} based on active conflict and vulnerability signals."

    @staticmethod
    def _score_npc_tension(npc: NPC) -> int:
        score = 1

        conflict = (getattr(getattr(npc, "background", None), "currentConflict", "") or "").strip()
        vulnerability = (getattr(getattr(npc, "background", None), "vulnerability", "") or "").strip()
        mood = (getattr(npc, "mood", "") or "").strip().lower()

        if conflict:
            score += 4
        if vulnerability:
            score += 3
        if mood and mood not in {"neutral", "fine", "okay"}:
            score += 2

        needs = getattr(npc, "needs", None)
        if needs:
            pressure_channels = [
                getattr(needs, "social", 100),
                getattr(needs, "energy", 100),
                getattr(needs, "fun", 100),
                100 - getattr(needs, "bladder", 0),
            ]
            if any(value < 40 for value in pressure_channels):
                score += 1

        return score

    def _build_focus_profile(self, focus_npc: Optional[NPC]) -> str:
        if not focus_npc:
            return "Malcolm Newt remains the implied focus while ensemble context loads."

        conflict = (focus_npc.background.currentConflict or "none surfaced") if focus_npc.background else "none surfaced"
        vulnerability = (focus_npc.background.vulnerability or "not publicly visible") if focus_npc.background else "not publicly visible"
        traits = ", ".join(focus_npc.coreTraits[:4]) if focus_npc.coreTraits else "No clear trait tags"
        location = getattr(focus_npc, "current_location", "Unknown") or "Unknown"
        occupation = focus_npc.occupation or focus_npc.affiliation or "unlisted"

        return (
            f"Name: {focus_npc.full_name}\n"
            f"Age: {focus_npc.age} | Occupation/Affiliation: {occupation}\n"
            f"Current location: {location} | Mood: {focus_npc.mood}\n"
            f"Core traits: {traits}\n"
            f"Current conflict: {conflict}\n"
            f"Vulnerability: {vulnerability}"
        )

    def _generate_scene(
        self,
        system_prompt: str,
        user_prompt: str,
        user_input: str,
        world_snapshot: str,
        memory_owner: str,
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.narrative_history[-4:])
        messages.append({"role": "user", "content": user_prompt})

        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key != "NOT_REQUIRED":
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.85,
            "max_tokens": NARRATIVE_MAX_TOKENS,
        }
        if self.context_size:
            payload["max_context_tokens"] = self.context_size

        try:
            if self.local_client:
                prompt = self._build_prompt(messages)
                response = self.local_client.generate(
                    prompt,
                    max_new_tokens=payload["max_tokens"],
                    temperature=payload["temperature"],
                )
                content = response.text
            else:
                res = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                if res.status_code != 200:
                    return f"[API Error: {res.text}]"
                content = res.json()["choices"][0]["message"]["content"]

            self.narrative_history.append({"role": "user", "content": user_input or "continue"})
            self.narrative_history.append({"role": "assistant", "content": content})
            self.last_narrated = content
            self._run_ai_director(user_input)
            self._update_memory(user_input, content, world_snapshot)
            return content
        except Exception as e:
            return f"[Connection Error: {e}]"

    def advance_time(self, hours):
        if self.sim:
            self.sim.tick(hours)
            self._sync_world_engine_state()

    def _update_memory(self, user_input: str, response: str, world_snapshot: str, memory_owner: str = "Malcolm Newt") -> None:
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
                memory_owner,
                memory_type,
                description,
                current_day,
                current_hour,
                importance,
                participants=participants,
                location=location,
            )

    def _initialize_ai_director(self) -> None:
        if not self.sim:
            return

        self.world_engine = CentralWorldEngine(
            hour=self.sim.time.hour,
            weather=getattr(self.sim.world, "weather", "Clear"),
        )
        self.world_engine.day = self.sim.time.total_days

        for npc in self.sim.npcs:
            location = getattr(npc, "current_location", "Unknown") or "Unknown"
            self.world_engine.upsert_character(
                CharacterState(
                    name=npc.full_name,
                    location=location,
                    state="idle",
                    persona=f"You are {npc.full_name}, a resident of Willow Creek.",
                    routine_state="background",
                )
            )

        self.perception_system = PerceptionSystem(self.world_engine)
        self.vector_memory = VectorMemoryStore()
        self.brain_router = BrainRouter(self._director_model_call)
        self.ai_director = AIDirector(
            self.world_engine,
            self.perception_system,
            self.vector_memory,
            self.brain_router,
        )

    def _sync_world_engine_state(self) -> None:
        if not self.sim or not self.world_engine:
            return

        self.world_engine.day = self.sim.time.total_days
        self.world_engine.hour = self.sim.time.hour
        self.world_engine.set_weather(getattr(self.sim.world, "weather", "Clear"))

        for npc in self.sim.npcs:
            location = getattr(npc, "current_location", "Unknown") or "Unknown"
            if npc.full_name in self.world_engine.characters:
                self.world_engine.move_character(npc.full_name, location)
            else:
                self.world_engine.upsert_character(
                    CharacterState(
                        name=npc.full_name,
                        location=location,
                        state="idle",
                        persona=f"You are {npc.full_name}, a resident of Willow Creek.",
                        routine_state="background",
                    )
                )

    def _run_ai_director(self, user_input: str) -> None:
        self.last_director_events = []
        if not self.ai_director_enabled or not self.ai_director or not self.world_engine:
            return

        self._sync_world_engine_state()
        event_location = getattr(self.malcolm, "current_location", "Unknown") if self.malcolm else "Unknown"
        event = WorldEvent(
            event_type="player_action",
            location=event_location or "Unknown",
            description=user_input,
            participants=["Malcolm Newt"],
            priority=2,
        )

        self.ai_director.enqueue_event(event)
        self.ai_director.run_background_routines()
        decisions = self.ai_director.process_queue(
            max_requests_per_tick=self.director_max_requests_per_tick,
        )

        if not decisions:
            return

        for npc_name, decision in decisions:
            action = decision.get("action", "wait")
            target = decision.get("target")
            dialogue = decision.get("dialogue", "")
            summary = f"{npc_name}: {action}"
            if target:
                summary += f" -> {target}"
            if dialogue:
                summary += f" | says: {dialogue}"
            self.last_director_events.append(summary)
            if self.vector_memory:
                self.vector_memory.add_memory(
                    npc_name,
                    f"Responded to player event with action '{action}' and dialogue '{dialogue}'",
                    tags=["player_action", "director_decision"],
                    weight=1.2,
                )

    def _director_model_call(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Return strict JSON only with keys: dialogue, action, target, reasoning. "
                    "No markdown, no prose outside JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_key != "NOT_REQUIRED":
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 300,
        }
        if self.context_size:
            payload["max_context_tokens"] = self.context_size

        if self.local_client:
            local_prompt = self._build_prompt(messages)
            result = self.local_client.generate(
                local_prompt,
                max_new_tokens=payload["max_tokens"],
                temperature=payload["temperature"],
            )
            return result.text

        res = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
        if res.status_code != 200:
            return "{\"dialogue\":\"...\",\"action\":\"wait\",\"target\":null,\"reasoning\":\"director_api_error\"}"
        return res.json()["choices"][0]["message"]["content"]
