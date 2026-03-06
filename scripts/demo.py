#!/usr/bin/env python3
"""Willow Creek simulation demo compatible with the current engine.

This script is environment-friendly and can run short smoke tests or longer sims.
"""

import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation_v2 import WillowCreekSimulation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Willow Creek simulation demo")
    parser.add_argument("--days", type=int, default=2, help="In-game days to simulate (default: 2)")
    parser.add_argument("--step-hours", type=float, default=1.0, help="Hours per simulation step")
    parser.add_argument(
        "--update-hours",
        type=int,
        default=6,
        help="How often to print progress updates (in in-game hours)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="willow_creek_demo_output.json",
        help="Path for JanitorAI export",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("=" * 70)
    print(" WILLOW CREEK 2025 - SIMULATION DEMO")
    print("   Autonomous NPCs • Relationships • Secrets • Drama")
    print("=" * 70)

    sim = WillowCreekSimulation()

    total_steps = max(1, int((args.days * 24) / args.step_hours))
    steps_per_update = max(1, int(args.update_hours / args.step_hours))

    print(
        f"Launching simulation: {args.days} day(s), "
        f"{total_steps:,} steps, {args.step_hours}h/step, updates every {args.update_hours}h"
    )

    start_time = time.time()
    current_step = 0

    hints = [
        "Morning routines", "School run", "Secret affair", "Pastor Naomi counsels",
        "Someone got caught", "Nina posting", "Michael spying", "Rose being tsundere",
        "Mindy tripped", "Maria flashed", "Yoga class spicy", "Late-night texting",
    ]

    while current_step < total_steps:
        chunk = min(steps_per_update, total_steps - current_step)
        sim.run(num_steps=chunk, time_step_hours=args.step_hours)
        current_step += chunk

        elapsed = max(0.001, time.time() - start_time)
        speed = current_step / elapsed
        progress = current_step / total_steps

        print(
            f"\rDay {sim.time.total_days:3d} | {sim.time.get_datetime_string()} | "
            f"{sim.time.season} • {(sim.world.weather or 'Clear').ljust(12)} | "
            f"{random.choice(hints).ljust(28)} | "
            f"{progress:.1%} ({current_step:,}/{total_steps:,}) | ~{speed:.0f} steps/sec",
            end="",
            flush=True,
        )

    print("\n\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)

    stats = sim.get_statistics()
    print("\nFinal State:")
    print(f"   Date    : {stats['Time']}")
    print(f"   Day     : {stats['Day']}")
    print(f"   NPCs    : {stats['NPCs']}")
    print(f"   Gossip  : {stats['Gossip']}")
    print(f"   Weather : {stats['Weather']}")

    print(f"\nExporting world state -> {args.output}")
    sim.export_to_janitor_ai(args.output)
    print("Done.")


if __name__ == "__main__":
    main()
