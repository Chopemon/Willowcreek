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
            self._run_ai_director(user_input or "world shifts")
            self._update_memory(user_input or "continue", content, world_snapshot, memory_owner)
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

    def _build_focus_profile(self, npc: Optional[NPC]) -> str:
        if not npc:
            return "Focus unavailable; default to Malcolm as catalyst."

        background = getattr(npc, "background", None)
        conflict = getattr(background, "currentConflict", "") if background else ""
        vulnerability = getattr(background, "vulnerability", "") if background else ""
        traits = ", ".join(getattr(npc, "coreTraits", [])[:5]) or "unspecified"
        return (
            f"Name: {npc.full_name}\n"
            f"Age: {getattr(npc, 'age', 'unknown')}\n"
            f"Occupation: {getattr(npc, 'occupation', '') or 'unknown'}\n"
            f"Affiliation: {getattr(npc, 'affiliation', '') or 'unknown'}\n"
            f"Location: {getattr(npc, 'current_location', 'Unknown')}\n"
            f"Mood: {getattr(npc, 'mood', 'Neutral')}\n"
            f"Core traits: {traits}\n"
            f"Current conflict: {conflict or 'none known'}\n"
            f"Vulnerability: {vulnerability or 'none known'}"
        )

    def _score_npc_tension(self, npc: NPC) -> Tuple[float, str]:
        score = 0.0
        reasons: List[str] = []

        if self.sim and hasattr(self.sim, "reputation"):
            gossip_count = len(self.sim.reputation.get_gossip_about(npc.full_name))
            if gossip_count:
                score += gossip_count * 2.0
                reasons.append(f"{gossip_count} gossip thread(s)")

        background = getattr(npc, "background", None)
        conflict = getattr(background, "currentConflict", "") if background else ""
        if conflict:
            score += 2.0
            reasons.append("active personal conflict")

        mood = str(getattr(npc, "mood", "Neutral")).lower()
        if mood not in {"neutral", "calm", ""}:
            score += 1.5
            reasons.append(f"heightened mood ({mood})")

        malcolm_loc = getattr(self.malcolm, "current_location", None) if self.malcolm else None
        if malcolm_loc and getattr(npc, "current_location", None) == malcolm_loc:
            score += 2.0
            reasons.append("near Malcolm (catalyst proximity)")

        if any(npc.full_name in event for event in self.last_director_events):
            score += 2.5
            reasons.append("director flagged reaction")

        reason = ", ".join(reasons) if reasons else "ambient town rhythm"
        return score, reason

    def _select_focus_npc(self, user_input: str) -> Tuple[Optional[NPC], str]:
        if not self.sim or not self.sim.npcs:
            return self.malcolm, "fallback focus"

        scored: List[Tuple[float, NPC, str]] = []
        for npc in self.sim.npcs:
            score, reason = self._score_npc_tension(npc)
            scored.append((score, npc, reason))

        scored.sort(key=lambda item: item[0], reverse=True)
        candidate_score, candidate_npc, candidate_reason = scored[0]

        current_focus = self.sim.npc_dict.get(self.tv_focus_npc_name) if self.tv_focus_npc_name else None
        if current_focus:
            current_score, current_reason = self._score_npc_tension(current_focus)
            should_cut = (self.tv_beat % max(self.tv_cut_interval, 1) == 0) or (candidate_score >= current_score + 2.0)
            if not should_cut:
                return current_focus, f"stay on current arc: {current_reason}"

        self.tv_focus_npc_name = candidate_npc.full_name
        return candidate_npc, f"cut to tension: {candidate_reason}"

    def start_story(self, starter_text: str) -> None:
        """Set a custom story starter and reset short narrative history."""
        self.last_narrated = (starter_text or "").strip() or self.last_narrated
        self.narrative_history = []

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
