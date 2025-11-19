#!/usr/bin/env python3
"""
View imported NPC data - Quick summary and analysis
"""

import json
from pathlib import Path
from collections import Counter

def analyze_npcs():
    """Analyze imported NPCs"""
    
    json_file = Path("imported_npcs.json")
    
    if not json_file.exists():
        print("❌ No imported_npcs.json found")
        print("   Run: python import_npcs_v2.py first")
        return
    
    # Load NPCs
    with open(json_file, 'r', encoding='utf-8') as f:
        npcs = json.load(f)
    
    print("=" * 70)
    print(f"WILLOW CREEK - NPC DATA ANALYSIS")
    print("=" * 70)
    print(f"\n✓ Loaded {len(npcs)} NPCs from imported_npcs.json\n")
    
    # Basic stats
    print("📊 DEMOGRAPHICS:")
    print(f"   Total NPCs: {len(npcs)}")
    
    # Gender distribution
    genders = Counter(npc['gender'] for npc in npcs)
    print(f"   Male: {genders.get('male', 0)}")
    print(f"   Female: {genders.get('female', 0)}")
    
    # Age statistics
    ages = [npc['age'] for npc in npcs]
    print(f"\n📈 AGE STATISTICS:")
    print(f"   Youngest: {min(ages)}")
    print(f"   Oldest: {max(ages)}")
    print(f"   Average: {sum(ages) / len(ages):.1f}")
    
    # Age groups
    children = sum(1 for age in ages if age < 13)
    teens = sum(1 for age in ages if 13 <= age < 18)
    adults = sum(1 for age in ages if 18 <= age < 65)
    seniors = sum(1 for age in ages if age >= 65)
    
    print(f"\n👥 AGE GROUPS:")
    print(f"   Children (0-12): {children}")
    print(f"   Teens (13-17): {teens}")
    print(f"   Adults (18-64): {adults}")
    print(f"   Seniors (65+): {seniors}")
    
    # Occupations
    occupations = Counter(npc['occupation'] for npc in npcs)
    print(f"\n💼 OCCUPATIONS:")
    for occ, count in occupations.most_common(10):
        print(f"   {occ}: {count}")
    
    # Addresses
    addresses = Counter(npc['home_address'] for npc in npcs)
    print(f"\n🏠 HOUSING:")
    print(f"   Unique addresses: {len(addresses)}")
    print(f"\n   Families (multiple NPCs at same address):")
    for addr, count in addresses.most_common():
        if count > 1:
            residents = [npc['full_name'] for npc in npcs if npc['home_address'] == addr]
            print(f"   {addr}: {count} residents")
            for resident in residents:
                print(f"      - {resident}")
    
    # Personality analysis
    print(f"\n🧠 PERSONALITY AVERAGES:")
    avg_openness = sum(npc['personality']['openness'] for npc in npcs) / len(npcs)
    avg_conscientiousness = sum(npc['personality']['conscientiousness'] for npc in npcs) / len(npcs)
    avg_extroversion = sum(npc['personality']['extroversion'] for npc in npcs) / len(npcs)
    avg_agreeableness = sum(npc['personality']['agreeableness'] for npc in npcs) / len(npcs)
    avg_neuroticism = sum(npc['personality']['neuroticism'] for npc in npcs) / len(npcs)
    
    print(f"   Openness: {avg_openness:.2f}/10")
    print(f"   Conscientiousness: {avg_conscientiousness:.2f}/10")
    print(f"   Extroversion: {avg_extroversion:.2f}/10")
    print(f"   Agreeableness: {avg_agreeableness:.2f}/10")
    print(f"   Neuroticism: {avg_neuroticism:.2f}/10")
    
    # List all NPCs
    print(f"\n📋 ALL NPCS:")
    print(f"{'Name':<25} {'Age':>4} {'Gender':<8} {'Occupation':<20}")
    print("-" * 70)
    for npc in sorted(npcs, key=lambda x: x['full_name']):
        print(f"{npc['full_name']:<25} {npc['age']:>4} {npc['gender']:<8} {npc['occupation']:<20}")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run: python demo.py")
    print("  2. Simulation will use these NPCs")
    print("  3. Export to JanitorAI format")

if __name__ == "__main__":
    analyze_npcs()
