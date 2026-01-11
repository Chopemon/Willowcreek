from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional
from uuid import uuid4


@dataclass
class MemoryRecord:
    id: str
    npc_id: str
    timestamp: str
    content: str
    kind: str
    emotional_tone: str
    importance: float
    tags: List[str] = field(default_factory=list)
    source: str = ""

    @staticmethod
    def create(
        npc_id: str,
        content: str,
        kind: str = "observation",
        emotional_tone: str = "neutral",
        importance: float = 0.3,
        tags: Optional[Iterable[str]] = None,
        source: str = "simulation",
    ) -> "MemoryRecord":
        return MemoryRecord(
            id=str(uuid4()),
            npc_id=npc_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            content=content,
            kind=kind,
            emotional_tone=emotional_tone,
            importance=float(importance),
            tags=list(tags or []),
            source=source,
        )


class MemoryStore:
    def __init__(self, root: str | Path = "memory") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, npc_id: str) -> Path:
        return self.root / f"{npc_id}.jsonl"

    def add(self, record: MemoryRecord) -> None:
        path = self._path_for(record.npc_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def list(self, npc_id: str) -> List[MemoryRecord]:
        path = self._path_for(npc_id)
        if not path.exists():
            return []
        records: List[MemoryRecord] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                records.append(MemoryRecord(**payload))
        return records

    def search(self, npc_id: str, query: str) -> List[MemoryRecord]:
        results = []
        query_lower = query.lower()
        for record in self.list(npc_id):
            if query_lower in record.content.lower():
                results.append(record)
        return results
