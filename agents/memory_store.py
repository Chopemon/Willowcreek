from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REQUIRED_IDENTITY_KEYS = {
    "id",
    "name",
    "age",
    "affiliation",
    "appearance",
}
REQUIRED_STATE_KEYS = {
    "location",
    "mood",
    "current_task",
}

DEFAULT_IDENTITY = {
    "coreTraits": [],
    "status": "active",
    "background": {
        "currentConflict": "",
        "vulnerability": "",
    },
}
DEFAULT_STATE = {
    "needs": {},
}
DEFAULT_RELATIONSHIPS: Dict[str, Any] = {}
DEFAULT_MEMORY: List[Dict[str, Any]] = []


def _require_keys(data: Dict[str, Any], required: set[str], label: str) -> None:
    missing = required.difference(data)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"{label} missing required keys: {missing_list}")


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            entries.append(json.loads(stripped))
    return entries


def load_npc_store(npc_dir: str | Path) -> Dict[str, Any]:
    npc_path = Path(npc_dir)
    identity = _load_json(npc_path / "identity.json")
    state = _load_json(npc_path / "state.json")
    relationships_path = npc_path / "relationships.json"
    memory_path = npc_path / "memory.jsonl"

    _require_keys(identity, REQUIRED_IDENTITY_KEYS, "identity.json")
    _require_keys(state, REQUIRED_STATE_KEYS, "state.json")

    identity_with_defaults = {**DEFAULT_IDENTITY, **identity}
    state_with_defaults = {**DEFAULT_STATE, **state}

    if relationships_path.exists():
        relationships = _load_json(relationships_path)
    else:
        relationships = DEFAULT_RELATIONSHIPS

    memory = _load_jsonl(memory_path) if memory_path.exists() else DEFAULT_MEMORY

    if not isinstance(relationships, dict):
        raise ValueError("relationships.json must contain an object")

    return {
        "identity": identity_with_defaults,
        "state": state_with_defaults,
        "relationships": relationships,
        "memory": memory,
    }
