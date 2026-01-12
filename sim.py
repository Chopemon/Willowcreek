from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from llm_client import LocalLLMClient
from memory_store import MemoryRecord, MemoryStore


@dataclass
class NPCProfile:
    npc_id: str
    identity: Dict
    state: Dict
    relationships: Dict


class NPCActor:
    def __init__(self, profile: NPCProfile, memory_store: MemoryStore) -> None:
        self.profile = profile
        self.memory_store = memory_store

    def act(self, llm_client: LocalLLMClient | None = None) -> str:
        name = self.profile.identity["name"]
        location = self.profile.state["current_location"]
        core_traits = ", ".join(self.profile.identity["coreTraits"])
        memory_seed = self.profile.state.get("memory_bank", [])
        memory_hint = memory_seed[0] if memory_seed else "Reflects on the day"
        recent_memories = self.memory_store.list(self.profile.npc_id)[-3:]
        memory_lines = [record.content for record in recent_memories]
        relationships = self.profile.relationships.get("relationships", {})
        relationship_summary = ", ".join(
            f"{other_npc}: {data.get('relationship', 'unknown')}"
            for other_npc, data in list(relationships.items())[:3]
        )

        prompt = (
            f"NPC: {name}\n"
            f"Location: {location}\n"
            f"Core traits: {core_traits}\n"
            f"Relationships: {relationship_summary or 'none'}\n"
            f"Memory seed: {memory_hint}\n"
            f"Recent memories: {', '.join(memory_lines) or 'none'}\n"
            "Describe a short, present-tense action the NPC takes next."
        )

        if llm_client:
            response = llm_client.generate(prompt)
            action_text = response.text.strip()
        else:
            action_text = f"{name} pauses at {location}, thinking about {memory_hint.lower()}."

        record = MemoryRecord.create(
            npc_id=self.profile.npc_id,
            content=action_text,
            kind="reflection",
            emotional_tone="thoughtful",
            importance=0.4,
            tags=["tick", "autonomy"],
            source="sim.py",
        )
        self.memory_store.add(record)
        return action_text


def load_npc_profile(npc_folder: Path) -> NPCProfile:
    identity = json.loads((npc_folder / "identity.json").read_text(encoding="utf-8"))
    state = json.loads((npc_folder / "state.json").read_text(encoding="utf-8"))
    relationships = json.loads(
        (npc_folder / "relationships.json").read_text(encoding="utf-8")
    )
    npc_id = identity["npc_id"]
    return NPCProfile(
        npc_id=npc_id,
        identity=identity,
        state=state,
        relationships=relationships,
    )


def load_profiles(npc_root: Path) -> List[NPCProfile]:
    profiles: List[NPCProfile] = []
    for folder in sorted(npc_root.iterdir()):
        if not folder.is_dir():
            continue
        if not (folder / "identity.json").exists():
            continue
        profiles.append(load_npc_profile(folder))
    return profiles


def run_simulation(npc_root: Path, ticks: int, use_llm: bool) -> None:
    memory_store = MemoryStore()
    llm_client = LocalLLMClient() if use_llm else None
    profiles = load_profiles(npc_root)

    for tick in range(1, ticks + 1):
        print(f"\n--- Tick {tick} ---")
        for profile in profiles:
            actor = NPCActor(profile, memory_store)
            action = actor.act(llm_client=llm_client)
            print(action)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple NPC tick loop.")
    parser.add_argument("--npc-root", default="npc", type=Path)
    parser.add_argument("--ticks", default=1, type=int)
    parser.add_argument("--use-llm", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_simulation(args.npc_root, args.ticks, args.use_llm)
