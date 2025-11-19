#!/usr/bin/env python3
"""
Test script for new enhanced features:
- Analysis tools
- Milestone tracking
- Personality-driven behavior
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from simulation_v2 import WillowCreekSimulation


def test_analyzer():
    """Test the simulation analyzer"""
    print("\n" + "=" * 70)
    print(" TESTING SIMULATION ANALYZER")
    print("=" * 70)

    sim = WillowCreekSimulation(num_npcs=0)

    # Run simulation for a bit
    print("\nRunning simulation for 24 hours...")
    sim.run(num_steps=24, time_step_hours=1.0)

    # Test analysis features
    print("\n--- COMPREHENSIVE SUMMARY ---")
    sim.analyzer.print_summary()

    print("\n--- RELATIONSHIP ANALYSIS ---")
    rel_analysis = sim.analyzer.analyze_relationships()
    print(f"Network Density: {rel_analysis['network_density']}")
    print(f"Total Relationships: {rel_analysis['total_relationships']}")
    print(f"Most Connected: {rel_analysis['most_connected']}")

    print("\n--- BEHAVIOR PATTERNS ---")
    behavior = sim.analyzer.analyze_behavior_patterns()
    print(f"Top 3 Locations: {list(behavior['location_distribution'].items())[:3]}")

    if behavior['npcs_in_critical_state']:
        print(f"\n⚠️  NPCs in Critical State:")
        for npc in behavior['npcs_in_critical_state'][:3]:
            print(f"   - {npc['name']}: {', '.join(npc['issues'])}")

    print("\n--- SOCIAL CLUSTERS ---")
    clusters = sim.analyzer.find_social_clusters()
    print(f"Found {len(clusters)} social clusters")
    for i, cluster in enumerate(clusters[:3], 1):
        print(f"   Cluster {i}: {', '.join(cluster)}")

    # Export report
    print("\n--- EXPORTING REPORT ---")
    sim.analyzer.export_report("test_analysis_report.json")

    print("\n✓ Analyzer test complete!")


def test_milestones():
    """Test the milestone tracking system"""
    print("\n" + "=" * 70)
    print(" TESTING MILESTONE TRACKER")
    print("=" * 70)

    sim = WillowCreekSimulation(num_npcs=0)

    print("\nRunning simulation for 48 hours...")
    sim.run(num_steps=48, time_step_hours=1.0)

    # Check milestones
    stats = sim.milestones.get_statistics()
    print(f"\nMilestone Statistics:")
    print(f"   Total Milestones: {stats['total_milestones']}")
    print(f"   By Type: {stats['by_type']}")
    print(f"   By Importance: {stats['by_importance']}")

    # Show recent milestones
    print("\n--- RECENT MILESTONES ---")
    sim.milestones.print_recent_milestones(days=7)

    # Manual milestone recording
    from systems.milestone_tracker import MilestoneType, MilestoneImportance

    if sim.npcs:
        npc = sim.npcs[0]
        print(f"\nManually recording test milestone for {npc.full_name}...")

        sim.milestones.record_milestone(
            milestone_type=MilestoneType.ACHIEVEMENT,
            importance=MilestoneImportance.MAJOR,
            primary_npc=npc.full_name,
            description=f"{npc.full_name} completed a major achievement!",
            location=npc.current_location,
            emotional_impact="positive",
            tags=['test', 'achievement']
        )

    # Get NPC history
    if sim.npcs:
        npc_name = sim.npcs[0].full_name
        history = sim.milestones.get_npc_history(npc_name, limit=5)
        print(f"\n--- HISTORY FOR {npc_name} ---")
        for milestone in history:
            print(f"   Day {milestone.day}: {milestone.description}")

    # Export milestones
    print("\n--- EXPORTING MILESTONES ---")
    sim.milestones.export_milestones("test_milestones.json")

    print("\n✓ Milestone tracker test complete!")


def test_personality():
    """Test the personality engine"""
    print("\n" + "=" * 70)
    print(" TESTING PERSONALITY ENGINE")
    print("=" * 70)

    sim = WillowCreekSimulation(num_npcs=0)

    if not sim.npcs:
        print("\n⚠️  No NPCs loaded, skipping personality test")
        return

    # Test personality extraction
    print("\n--- PERSONALITY PROFILES ---")
    for npc in sim.npcs[:5]:
        profile = sim.personality.get_personality_summary(npc)
        print(f"\n{profile['name']}:")
        print(f"   Traits: {', '.join(profile['traits'])}")
        print(f"   Tendencies: {', '.join(profile['behavioral_tendencies'][:3])}")

    # Test decision making
    print("\n--- DECISION MAKING TEST ---")
    test_npc = sim.npcs[0]
    print(f"\nTesting with {test_npc.full_name}...")

    options = [
        {'action': 'socialize', 'location': 'Park', 'weight': 1.0, 'type': 'social'},
        {'action': 'work', 'location': 'Office', 'weight': 1.0, 'type': 'career'},
        {'action': 'relax', 'location': 'Home', 'weight': 1.0, 'type': 'rest'},
        {'action': 'adventure', 'location': 'Unknown', 'weight': 1.0, 'type': 'risky'},
    ]

    decision = sim.personality.make_decision(test_npc, options)
    print(f"   Decision: {decision['action']} at {decision['location']}")
    print(f"   Final weight: {decision.get('final_weight', 'N/A')}")

    # Test reaction generation
    print("\n--- REACTION GENERATION ---")
    reaction = sim.personality.generate_reaction(test_npc, 'good_news')
    print(f"   Good News Reaction: {reaction}")

    reaction = sim.personality.generate_reaction(test_npc, 'conflict')
    print(f"   Conflict Reaction: {reaction}")

    # Test consistency checking
    print("\n--- BEHAVIOR CONSISTENCY ---")
    actions = ['socialize_at_party', 'avoid_all_people', 'help_stranger', 'work_overtime']

    for action in actions:
        is_consistent, score = sim.personality.is_action_consistent(test_npc, action)
        status = "✓" if is_consistent else "✗"
        print(f"   {status} {action}: {score:.2f}")

    print("\n✓ Personality engine test complete!")


def test_integrated():
    """Test all systems working together"""
    print("\n" + "=" * 70)
    print(" TESTING INTEGRATED SYSTEMS")
    print("=" * 70)

    sim = WillowCreekSimulation(num_npcs=0)

    print("\nRunning 7-day simulation with all enhanced features...")

    for day in range(1, 8):
        sim.run(num_steps=24, time_step_hours=1.0)

        if day % 2 == 0:
            print(f"\n--- Day {day} Update ---")
            recent_milestones = sim.milestones.get_recent_milestones(days=2, limit=3)
            if recent_milestones:
                print(f"Recent Milestones ({len(recent_milestones)}):")
                for m in recent_milestones[:3]:
                    print(f"   • {m.description}")

    print("\n--- FINAL COMPREHENSIVE ANALYSIS ---")
    report = sim.analyzer.generate_comprehensive_report()

    print(f"\nTime: Day {report['time']['total_days']}, {report['time']['current_time']}")
    print(f"Relationships: {report['relationships']['total_relationships']} total")
    print(f"Network Density: {report['relationships']['network_density']}")
    print(f"Events: {report['events']['total_events']} total")
    print(f"Milestones: Tracked across {report['time']['total_days']} days")

    print("\n✓ Integrated test complete!")


def main():
    """Run all tests"""
    print("=" * 70)
    print(" WILLOW CREEK ENHANCED FEATURES TEST SUITE")
    print("=" * 70)

    try:
        test_analyzer()
        test_milestones()
        test_personality()
        test_integrated()

        print("\n" + "=" * 70)
        print(" ✅ ALL TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
