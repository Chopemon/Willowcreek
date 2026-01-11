# narrative_chat.py
# FIXED: Restored original atmospheric opening, system prompt, and prompt structure.

import requests
import os
from typing import Optional, List, Dict
from simulation_v2 import WillowCreekSimulation
from entities.npc import NPC
from world_snapshot_builder import create_narrative_context

CONFIG = {
    "openrouter": {
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model_name": "tngtech/deepseek-r1t2-chimera:free",
        "key_env": "OPENROUTER_API_KEY"
    },
    "local": {
        "api_url": "http://localhost:1234/v1/chat/completions",
        "model_name": "local-model",
        "key_env": None
    }
}

class NarrativeChat:
    def __init__(self, mode: str = "openrouter", model_name: Optional[str] = None):
        if mode not in CONFIG: raise ValueError(f"Invalid mode: {mode}")
        
        self.mode = mode
        if mode == "local":
            self.api_url = os.getenv("LOCAL_LLM_URL", CONFIG[mode]["api_url"])
        else:
            self.api_url = CONFIG[mode]["api_url"]
        self.model_name = model_name or CONFIG[mode]["model_name"]
        
        if CONFIG[mode]["key_env"]:
            self.api_key = os.getenv(CONFIG[mode]["key_env"])
            if not self.api_key: 
                print(f"WARNING: {CONFIG[mode]['key_env']} not set.")
        else:
            self.api_key = "NOT_REQUIRED"

        self.sim: Optional[WillowCreekSimulation] = None
        self.malcolm: Optional[NPC] = None
        self.narrative_history: List[Dict] = [] 
        self.last_narrated: str = ""

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
        
        # --- RESTORED ORIGINAL SYSTEM PROMPT ---
        system_prompt = (
            "You are the living, breathing narrative voice of Willow Creek, autumn 2025: a small American town heavy with secrets, "
            "unspoken desires, and the low hum of hidden lives. Write exclusively in third-person limited, anchored to Malcolm Newt’s senses "
            "and perceptions. Let the air feel damp with woodsmoke and wet leaves, let every glance and half-heard conversation carry weight. "
            "Use the provided world snapshot and recent events as absolute truth. Continue the scene in 4–8 vivid, flowing sentences. "
            "Never summarize, never offer choices, never speak as Malcolm, never break immersion. "
            "The town is watching. The porch lights flicker. Something is always about to happen."
        )

        # --- RESTORED ORIGINAL USER PROMPT STRUCTURE ---
        user_prompt = f"""
        Current scene:
        \"\"\"{self.last_narrated}\"\"\"

        WORLD STATE:
        {world_snapshot}

        Player action: {user_input}

        Continue the narrative in 4-8 sentences, third-person limited from Malcolm's POV.
        """

        # Build Messages for API
        # We include the system prompt, relevant history (last 6 turns to keep context window managed), and the new rich user prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add simple history (exclude system/rich prompts to save tokens, just raw conversation)
        # We take the last few interactions from history to maintain continuity logic
        messages.extend(self.narrative_history[-6:]) 
        
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
            "max_tokens": 800
        }

        try:
            res = requests.post(self.api_url, headers=headers, json=payload)
            if res.status_code != 200: return f"[API Error: {res.text}]"
            
            content = res.json()["choices"][0]["message"]["content"]
            
            # Update History
            # We store the simplified version in history to avoid exploding context size with repetitive World States
            self.narrative_history.append({"role": "user", "content": user_input})
            self.narrative_history.append({"role": "assistant", "content": content})
            
            self.last_narrated = content 
            return content
        except Exception as e:
            return f"[Connection Error: {e}]"

    def advance_time(self, hours):
        if self.sim:
            self.sim.tick(hours)
