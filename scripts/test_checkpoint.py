#!/usr/bin/env python3
"""
Test script for checkpoint save/load functionality
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation_v2 import WillowCreekSimulation


def main():
    print("=" * 70)
    print(" CHECKPOINT SYSTEM TEST")
    print("=" * 70)
    print()

    # Create simulation
    print("Creating simulation...")
    sim = WillowCreekSimulation(num_npcs=0)
    print(f"Initial state: {sim.time.get_datetime_string()}")
    print(f"NPCs: {len(sim.npcs)}")
    print()

    # Run for a bit
    print("Running simulation for 24 hours...")
    sim.run(num_steps=24, time_step_hours=1.0)
    print(f"After run: {sim.time.get_datetime_string()}")
    print(f"Current step: {sim.current_step}")
    print()

    # Save checkpoint
    print("Saving checkpoint...")
    checkpoint_path = sim.save_checkpoint(
        name="test_checkpoint",
        description="Test checkpoint after 24 hours"
    )
    print()

    # Continue simulation
    print("Continuing simulation for another 24 hours...")
    sim.run(num_steps=24, time_step_hours=1.0)
    print(f"After more run: {sim.time.get_datetime_string()}")
    print(f"Current step: {sim.current_step}")
    print()

    # Load checkpoint
    print("Loading checkpoint...")
    sim.load_checkpoint("test_checkpoint")
    print(f"After load: {sim.time.get_datetime_string()}")
    print(f"Current step: {sim.current_step}")
    print()

    # Test quick save/load
    print("Testing quick save...")
    sim.run(num_steps=12, time_step_hours=1.0)
    print(f"Before quick save: {sim.time.get_datetime_string()}")
    sim.quick_save(slot=1)
    print()

    print("Running more...")
    sim.run(num_steps=12, time_step_hours=1.0)
    print(f"After more run: {sim.time.get_datetime_string()}")
    print()

    print("Quick loading...")
    sim.quick_load(slot=1)
    print(f"After quick load: {sim.time.get_datetime_string()}")
    print()

    # List checkpoints
    print("Available checkpoints:")
    checkpoints = sim.list_checkpoints()
    for i, ckpt in enumerate(checkpoints, 1):
        print(f"  {i}. {ckpt['checkpoint_name']}")
        print(f"     Time: {ckpt['simulation_time']}")
        print(f"     Created: {ckpt['created_at'][:19]}")
        print(f"     NPCs: {ckpt['num_npcs']}")
        if ckpt['description']:
            print(f"     Description: {ckpt['description']}")
        print()

    print("=" * 70)
    print("✓ Checkpoint system test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
