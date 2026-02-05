# systems/db_save_system.py
# Database-backed save/load (SQLite).

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List


@dataclass
class DBSaveMetadata:
    slot_name: str
    branch: str
    save_time: str


class DatabaseSaveSystem:
    def __init__(self, db_path: str = "./saves/world_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS saves (
                    slot_name TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    save_time TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (slot_name, branch)
                )
                """
            )

    def save_game(self, slot_name: str, branch: str, game_state: Dict) -> bool:
        payload = json.dumps(game_state, default=str)
        save_time = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO saves (slot_name, branch, save_time, payload)
                VALUES (?, ?, ?, ?)
                """,
                (slot_name, branch, save_time, payload),
            )
        return True

    def load_game(self, slot_name: str, branch: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM saves WHERE slot_name = ? AND branch = ?",
                (slot_name, branch),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def list_saves(self) -> List[DBSaveMetadata]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT slot_name, branch, save_time FROM saves").fetchall()
        return [DBSaveMetadata(slot_name=row[0], branch=row[1], save_time=row[2]) for row in rows]
