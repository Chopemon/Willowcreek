#!/usr/bin/env python3
"""
Simple test for checkpoint manager without full simulation
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.checkpoint_manager import CheckpointManager

def main():
    print("=" * 70)
    print(" CHECKPOINT MANAGER TEST (Standalone)")
    print("=" * 70)
    print()

    # Create checkpoint manager
    cm = CheckpointManager(checkpoints_dir="test_checkpoints")
    print("✓ Checkpoint manager created")
    print(f"  Checkpoints directory: test_checkpoints/")
    print()

    # Test listing empty checkpoints
    checkpoints = cm.list_checkpoints()
    print(f"Current checkpoints: {len(checkpoints)}")
    print()

    # Create a simple mock simulation object
    class MockSimulation:
        def __init__(self):
            from core.time_system import TimeSystem
            from core.world_state import WorldState

            self.time = TimeSystem(datetime(2025, 9, 1, 8, 0))
            self.world = WorldState()
            self.npcs = []
            self.npc_dict = {}
            self.current_step = 0
            self.scenario_buffer = []
            self.debug_enabled = True

    print("Creating mock simulation...")
    sim = MockSimulation()
    print(f"  Simulation time: {sim.time.get_datetime_string()}")
    print()

    # Test save
    print("Testing checkpoint save...")
    try:
        checkpoint_path = cm.save_checkpoint(
            sim,
            name="test_ckpt_1",
            description="Test checkpoint"
        )
        print("✓ Save successful!")
        print()
    except Exception as e:
        print(f"✗ Save failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Modify simulation
    print("Advancing simulation...")
    sim.time.advance(24)
    sim.current_step = 24
    print(f"  New time: {sim.time.get_datetime_string()}")
    print(f"  Current step: {sim.current_step}")
    print()

    # Test load
    print("Testing checkpoint load...")
    try:
        cm.load_checkpoint("test_ckpt_1", sim)
        print("✓ Load successful!")
        print(f"  Restored time: {sim.time.get_datetime_string()}")
        print(f"  Restored step: {sim.current_step}")
        print()
    except Exception as e:
        print(f"✗ Load failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # List checkpoints
    print("Listing checkpoints...")
    checkpoints = cm.list_checkpoints()
    print(f"  Total checkpoints: {len(checkpoints)}")
    for ckpt in checkpoints:
        print(f"    - {ckpt['checkpoint_name']}")
        print(f"      Time: {ckpt['simulation_time']}")
    print()

    print("=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)

    # Cleanup
    import shutil
    shutil.rmtree("test_checkpoints", ignore_errors=True)
    print("\n✓ Test directory cleaned up")

if __name__ == "__main__":
    main()
