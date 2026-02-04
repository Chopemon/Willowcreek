from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


BASE_DIR = Path("data") / "npcs"


def _npc_dir(name: str) -> Path:
    return BASE_DIR / name


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_identity(name: str) -> dict:
    return _load_json(_npc_dir(name) / "identity.json")


def load_state(name: str) -> dict:
    return _load_json(_npc_dir(name) / "state.json")


def load_relationships(name: str) -> dict:
    return _load_json(_npc_dir(name) / "relationships.json")


def append_memory(name: str, ts: str, memory_type: str, salience: int, text: str) -> None:
    npc_dir = _npc_dir(name)
    npc_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": ts,
        "type": memory_type,
        "salience": salience,
        "text": text,
    }
    path = npc_dir / "memory.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_memories(path: Path) -> Iterable[dict]:
    if not path.exists():
        return []
    memories: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                memories.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return memories


def retrieve_relevant_memories(name: str, query: str, k: int) -> list[dict]:
    path = _npc_dir(name) / "memory.jsonl"
    memories = list(_read_memories(path))
    if not memories:
        return []

    normalized_query = query.strip().lower()
    if normalized_query:
        tokens = {token for token in normalized_query.replace(",", " ").split() if token}
        if tokens:
            filtered = [
                memory
                for memory in memories
                if any(token in str(memory.get("text", "")).lower() for token in tokens)
            ]
            if filtered:
                return filtered[-k:]

    return memories[-k:]
