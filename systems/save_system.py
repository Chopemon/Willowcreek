# systems/save_system.py
# Save/load game state

import json
from typing import Dict, Optional, List
from datetime import datetime
import os


class SaveSystem:
    def __init__(self, save_directory: str = "./saves"):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)
    
    def save_game(self, slot_name: str, game_state: Dict) -> bool:
        try:
            save_path = os.path.join(self.save_directory, f"{slot_name}.json")
            
            game_state['save_metadata'] = {
                'slot_name': slot_name,
                'save_time': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(save_path, 'w') as f:
                json.dump(game_state, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, slot_name: str) -> Optional[Dict]:
        try:
            save_path = os.path.join(self.save_directory, f"{slot_name}.json")
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r') as f:
                game_state = json.load(f)
            
            return game_state
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saves(self) -> List[Dict]:
        saves = []
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                slot_name = filename[:-5]
                saves.append({'slot_name': slot_name})
        
        return saves
