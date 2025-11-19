# core/checkpoint_manager.py
"""
Checkpoint Manager for Willow Creek Simulation
Provides save/load functionality with versioning and metadata
"""

import json
import pickle
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import gzip


@dataclass
class CheckpointMetadata:
    """Metadata for a simulation checkpoint"""
    checkpoint_name: str
    created_at: str
    simulation_time: str
    total_days: int
    num_npcs: int
    version: str = "1.0"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CheckpointManager:
    """
    Manages simulation checkpoints with save/load functionality.

    Features:
    - Save/load complete simulation state
    - Automatic versioning
    - Compressed storage
    - Metadata tracking
    - Quick save/load slots
    """

    def __init__(self, checkpoints_dir: str = "checkpoints"):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(exist_ok=True)
        self.metadata_file = self.checkpoints_dir / "checkpoints_index.json"
        self._load_index()

    def _load_index(self):
        """Load the checkpoints index"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save_index(self):
        """Save the checkpoints index"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def save_checkpoint(self, sim, name: Optional[str] = None, description: str = "") -> str:
        """
        Save a complete simulation checkpoint.

        Args:
            sim: WillowCreekSimulation instance
            name: Optional checkpoint name (auto-generated if not provided)
            description: Optional description

        Returns:
            Path to saved checkpoint
        """
        # Generate checkpoint name if not provided
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"checkpoint_{timestamp}"

        # Create metadata
        metadata = CheckpointMetadata(
            checkpoint_name=name,
            created_at=datetime.now().isoformat(),
            simulation_time=sim.time.get_datetime_string(),
            total_days=sim.time.total_days,
            num_npcs=len(sim.npcs),
            description=description
        )

        # Prepare checkpoint data
        checkpoint_data = {
            'metadata': metadata.to_dict(),
            'time_system': self._serialize_time_system(sim.time),
            'world_state': self._serialize_world_state(sim.world),
            'npcs': self._serialize_npcs(sim.npcs),
            'systems': self._serialize_systems(sim),
            'current_step': sim.current_step
        }

        # Save checkpoint (compressed)
        checkpoint_path = self.checkpoints_dir / f"{name}.ckpt"
        with gzip.open(checkpoint_path, 'wb') as f:
            pickle.dump(checkpoint_data, f)

        # Update index
        self.index[name] = metadata.to_dict()
        self._save_index()

        file_size = checkpoint_path.stat().st_size / 1024  # KB
        print(f"✓ Checkpoint saved: {name}")
        print(f"  Location: {checkpoint_path}")
        print(f"  Size: {file_size:.1f} KB")
        print(f"  NPCs: {metadata.num_npcs}")
        print(f"  Sim Time: {metadata.simulation_time}")

        return str(checkpoint_path)

    def load_checkpoint(self, name: str, sim):
        """
        Load a checkpoint into an existing simulation.

        Args:
            name: Checkpoint name (without .ckpt extension)
            sim: WillowCreekSimulation instance to load into
        """
        checkpoint_path = self.checkpoints_dir / f"{name}.ckpt"

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {name}")

        print(f"Loading checkpoint: {name}...")

        # Load checkpoint data
        with gzip.open(checkpoint_path, 'rb') as f:
            checkpoint_data = pickle.load(f)

        # Restore simulation state
        self._restore_time_system(sim.time, checkpoint_data['time_system'])
        self._restore_world_state(sim.world, checkpoint_data['world_state'])
        self._restore_npcs(sim, checkpoint_data['npcs'])
        self._restore_systems(sim, checkpoint_data['systems'])
        sim.current_step = checkpoint_data['current_step']

        metadata = checkpoint_data['metadata']
        print(f"✓ Checkpoint loaded: {name}")
        print(f"  Sim Time: {metadata['simulation_time']}")
        print(f"  Total Days: {metadata['total_days']}")
        print(f"  NPCs: {metadata['num_npcs']}")

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints"""
        return sorted(
            self.index.values(),
            key=lambda x: x['created_at'],
            reverse=True
        )

    def delete_checkpoint(self, name: str):
        """Delete a checkpoint"""
        checkpoint_path = self.checkpoints_dir / f"{name}.ckpt"

        if checkpoint_path.exists():
            checkpoint_path.unlink()

        if name in self.index:
            del self.index[name]
            self._save_index()
            print(f"✓ Checkpoint deleted: {name}")

    def quick_save(self, sim, slot: int = 1) -> str:
        """Quick save to a numbered slot (1-10)"""
        if not 1 <= slot <= 10:
            raise ValueError("Quick save slot must be between 1 and 10")

        name = f"quicksave_{slot}"
        return self.save_checkpoint(sim, name, f"Quick save slot {slot}")

    def quick_load(self, sim, slot: int = 1):
        """Quick load from a numbered slot (1-10)"""
        if not 1 <= slot <= 10:
            raise ValueError("Quick load slot must be between 1 and 10")

        name = f"quicksave_{slot}"
        self.load_checkpoint(name, sim)

    # ========================================================================
    # SERIALIZATION HELPERS
    # ========================================================================

    def _serialize_time_system(self, time_system) -> Dict[str, Any]:
        """Serialize TimeSystem state"""
        return {
            'current_time': time_system.current_time.isoformat(),
            'total_days': time_system.total_days
        }

    def _restore_time_system(self, time_system, data: Dict[str, Any]):
        """Restore TimeSystem state"""
        time_system.current_time = datetime.fromisoformat(data['current_time'])
        time_system.total_days = data['total_days']
        time_system._update_internal_state()

    def _serialize_world_state(self, world_state) -> Dict[str, Any]:
        """Serialize WorldState"""
        return {
            'weather': world_state.weather
        }

    def _restore_world_state(self, world_state, data: Dict[str, Any]):
        """Restore WorldState"""
        world_state.weather = data['weather']

    def _serialize_npcs(self, npcs: List) -> List[Dict[str, Any]]:
        """Serialize all NPCs"""
        serialized = []
        for npc in npcs:
            npc_data = {
                'full_name': npc.full_name,
                'age': npc.age,
                'gender': npc.gender.value,
                'affiliation': npc.affiliation,
                'occupation': npc.occupation,
                'appearance': npc.appearance,
                'coreTraits': npc.coreTraits,
                'libidoLevel': npc.libidoLevel,
                'status': npc.status,
                'relationship': npc.relationship,
                'memory_bank': list(npc.memory_bank),
                'private_secrets': list(npc.private_secrets),
                'dislikes': npc.dislikes,
                'relationships': npc.relationships,
                'background': {
                    'currentConflict': npc.background.currentConflict,
                    'vulnerability': npc.background.vulnerability
                },
                'current_location': npc.current_location,
                'home_location': npc.home_location,
                'mood': npc.mood,
                'needs': {
                    'hunger': npc.needs.hunger,
                    'energy': npc.needs.energy,
                    'hygiene': npc.needs.hygiene,
                    'bladder': npc.needs.bladder,
                    'social': npc.needs.social,
                    'fun': npc.needs.fun,
                    'horny': npc.needs.horny
                },
                'psyche': {
                    'lonely': npc.psyche.lonely
                }
            }
            serialized.append(npc_data)
        return serialized

    def _restore_npcs(self, sim, npcs_data: List[Dict[str, Any]]):
        """Restore NPCs state"""
        from entities.npc import Gender, Needs, PsycheState, NPCBackground

        # Update existing NPCs
        for npc_data in npcs_data:
            npc_name = npc_data['full_name']
            if npc_name in sim.npc_dict:
                npc = sim.npc_dict[npc_name]

                # Restore basic fields
                npc.age = npc_data['age']
                npc.status = npc_data['status']
                npc.relationship = npc_data['relationship']
                npc.current_location = npc_data['current_location']
                npc.home_location = npc_data['home_location']
                npc.mood = npc_data['mood']
                npc.memory_bank = set(npc_data['memory_bank'])
                npc.private_secrets = set(npc_data['private_secrets'])

                # Restore needs
                needs_data = npc_data['needs']
                npc.needs.hunger = needs_data['hunger']
                npc.needs.energy = needs_data['energy']
                npc.needs.hygiene = needs_data['hygiene']
                npc.needs.bladder = needs_data['bladder']
                npc.needs.social = needs_data['social']
                npc.needs.fun = needs_data['fun']
                npc.needs.horny = needs_data['horny']

                # Restore psyche
                npc.psyche.lonely = npc_data['psyche']['lonely']

    def _serialize_systems(self, sim) -> Dict[str, Any]:
        """Serialize system states (minimal - most regenerate from NPC data)"""
        return {
            'scenario_buffer': sim.scenario_buffer,
            'debug_enabled': sim.debug_enabled
        }

    def _restore_systems(self, sim, systems_data: Dict[str, Any]):
        """Restore system states"""
        sim.scenario_buffer = systems_data.get('scenario_buffer', [])
        sim.debug_enabled = systems_data.get('debug_enabled', True)

        # Refresh relationships from current NPC state (if available)
        if hasattr(sim, 'relationships') and sim.relationships is not None:
            sim.relationships = type(sim.relationships)(sim.npcs)

        # Update schedules based on restored time (if available)
        if hasattr(sim, 'schedule') and sim.schedule is not None:
            sim.schedule.update_locations()


def add_checkpoint_methods_to_simulation():
    """
    Monkey-patch checkpoint methods into WillowCreekSimulation.
    Call this at module load time or in __init__.
    """
    from simulation_v2 import WillowCreekSimulation

    def save_checkpoint(self, name: Optional[str] = None, description: str = ""):
        """Save simulation checkpoint"""
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = CheckpointManager()
        return self._checkpoint_manager.save_checkpoint(self, name, description)

    def load_checkpoint(self, name: str):
        """Load simulation checkpoint"""
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = CheckpointManager()
        self._checkpoint_manager.load_checkpoint(name, self)

    def list_checkpoints(self):
        """List all checkpoints"""
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = CheckpointManager()
        return self._checkpoint_manager.list_checkpoints()

    def quick_save(self, slot: int = 1):
        """Quick save to slot"""
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = CheckpointManager()
        return self._checkpoint_manager.quick_save(self, slot)

    def quick_load(self, slot: int = 1):
        """Quick load from slot"""
        if not hasattr(self, '_checkpoint_manager'):
            self._checkpoint_manager = CheckpointManager()
        self._checkpoint_manager.quick_load(self, slot)

    # Add methods to class
    WillowCreekSimulation.save_checkpoint = save_checkpoint
    WillowCreekSimulation.load_checkpoint = load_checkpoint
    WillowCreekSimulation.list_checkpoints = list_checkpoints
    WillowCreekSimulation.quick_save = quick_save
    WillowCreekSimulation.quick_load = quick_load
