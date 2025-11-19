# core/world_state.py

import json
import os
from entities.npc import create_npc_from_dict


class WorldState:
    def __init__(self):
        self.weather = "Clear"
        # key: full_name → NPC instance
        self.npc_roster = {}

    def _load_json_list(self, path: str):
        """Helper: load a JSON file that should contain a list of NPC dicts."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Expected a list in {path}, got {type(data)}")
        return data

    def load_npc_roster(self, folder_path: str) -> bool:
        """
        Load NPCs from:
          - npc_roster.json  (your main hand-written cast)
          - npc_generic.json (optional, background townies)

        Both files live in the same folder, e.g. npc_data/.
        """
        try:
            main_path = os.path.join(folder_path, "npc_roster.json")
            generic_path = os.path.join(folder_path, "npc_generic.json")

            if not os.path.isfile(main_path):
                print(f"[WorldState] ERROR: npc_roster.json not found at {main_path}")
                return False

            all_entries = []

            # Main cast
            print(f"[WorldState] Loading core roster: {main_path}")
            core_list = self._load_json_list(main_path)
            all_entries.extend(core_list)
            print(f"[WorldState] Core NPCs found: {len(core_list)}")

            # Optional generic townies
            if os.path.isfile(generic_path):
                print(f"[WorldState] Loading generic NPCs: {generic_path}")
                generic_list = self._load_json_list(generic_path)
                all_entries.extend(generic_list)
                print(f"[WorldState] Generic NPCs found: {len(generic_list)}")
            else:
                print(f"[WorldState] No npc_generic.json found at {generic_path} (this is fine).")

            # Build NPC objects, avoid duplicates by full_name
            added = 0
            for npc_entry in all_entries:
                npc = create_npc_from_dict(npc_entry)
                if npc.full_name in self.npc_roster:
                    # Last-in wins; if you prefer first-in-wins, skip instead
                    # print(f"[WorldState] Duplicate NPC name '{npc.full_name}', overwriting previous.")
                    pass
                else:
                    added += 1
                self.npc_roster[npc.full_name] = npc

            print(f"[WorldState] Loaded {len(self.npc_roster)} unique NPCs "
                  f"(from {len(all_entries)} entries, {added} new).")
            return True

        except Exception as e:
            print(f"[WorldState] ERROR loading roster: {e}")
            return False

    def get_npc(self, name: str):
        return self.npc_roster.get(name)
