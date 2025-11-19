#!/usr/bin/env python3
"""
Willow Creek 2025 - 500-Day Demo
Works with your current simulation.py (no progress_callback needed)
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.simulation import WillowCreekSimulation


def main():
    print("=" * 70)
    print(" WILLOW CREEK 2025 - 500 DAY SIMULATION")
    print("   Autonomous NPCs • Relationships • Secrets • Drama")
    print("=" * 70)
    print()

    sim = WillowCreekSimulation(num_npcs=0)  # Use only your custom roster

    total_steps = 500 * 24
    steps_per_update = 6

    print(f"Launching 500-day simulation ({total_steps:,} hourly steps)")
    print("Live progress (updates every 6 in-game hours):\n")

    start_time = time.time()

    # This is the correct way with your current code:
    sim.run(
        num_steps=total_steps,
        steps_per_day=24,
        time_step_hours=1.0
    )

    # Manual progress display (we poll the time system ourselves)
    current_step = 0
    while current_step < total_steps:
        # Advance in chunks of 6 steps for smooth display
        chunk = min(steps_per_update, total_steps - current_step)
        sim.run(num_steps=chunk, steps_per_day=24, time_step_hours=1.0)
        current_step += chunk

        day = sim.time.total_days
        date_str = sim.time.get_date_string()
        time_str = sim.time.get_time_string()
        season = sim.time.season
        weather = sim.world.weather or "Clear"

        hints = [
            "Morning routines", "School run", "Secret affair", "Pastor Naomi counsels",
            "Someone got caught", "Nina posting", "Michael spying", "Rose being tsundere",
            "Mindy tripped", "Maria flashed", "Yoga class spicy", "Late-night texting"
        ]

        elapsed = time.time() - start_time
        speed = current_step / elapsed if elapsed > 0 else 0
        progress = current_step / total_steps

        print(f"\rDay {day:3d} | {date_str} | {time_str} | {season} • {weather.ljust(12)} | "
              f"{random.choice(hints).ljust(28)} | {progress:.1%} ({current_step:,}/{total_steps:,}) | ~{speed:.0f} steps/sec",
              end="", flush=True)

    print("\n\n" + "=" * 70)
    print("500 DAYS COMPLETED!")
    print("=" * 70)

    stats = sim.get_statistics()
    print(f"\nFinal State:")
    print(f"   Date           : {sim.time.get_datetime_string()}")
    print(f"   Total Days     : {sim.time.total_days}")
    print(f"   NPCs           : {stats['num_npcs']}")
    print(f"   Relationships  : {stats['num_relationships']}")
    print(f"   Avg Affinity   : {stats['avg_relationship_level']:.2f}")
    print(f"   Most Connected : {sim.relationships.get_most_connected_npc()}")

    output_file = "willow_creek_500_days.js"
    print(f"\nExporting world state → {output_file}")
    sim.export_to_janitor_ai(output_file)

    print(f"\nDone! Your town has lived 500 days of pure drama.")
    print(f"   → Load '{output_file}' into JanitorAI/SillyTavern")
    print("=" * 70)


if __name__ == "__main__":
    main()