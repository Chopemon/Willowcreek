# analysis/simulation_analyzer.py
"""
Comprehensive Analysis Tools for Willow Creek Simulation

Provides visualization, metrics, and insights about:
- Relationship networks
- NPC behavior patterns
- Time-series data
- Social dynamics
- Event patterns
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import json


class SimulationAnalyzer:
    """Main analyzer for simulation metrics and patterns"""

    def __init__(self, sim):
        self.sim = sim

    # ========================================================================
    # RELATIONSHIP ANALYSIS
    # ========================================================================

    def analyze_relationships(self) -> Dict[str, Any]:
        """Comprehensive relationship network analysis"""

        total_relationships = 0
        affinity_levels = []
        relationship_types = Counter()

        # Network metrics
        connections_per_npc = defaultdict(int)
        strongest_bonds = []

        for npc in self.sim.npcs:
            for rel_name, rel_data in npc.relationships.items():
                total_relationships += 1

                affinity = rel_data.get('affinity', 0)
                affinity_levels.append(affinity)

                # Count connection
                connections_per_npc[npc.full_name] += 1

                # Track strong relationships
                if affinity > 70:
                    strongest_bonds.append({
                        'from': npc.full_name,
                        'to': rel_name,
                        'affinity': affinity
                    })

                # Categorize relationship type
                if affinity > 80:
                    relationship_types['best_friends'] += 1
                elif affinity > 60:
                    relationship_types['friends'] += 1
                elif affinity > 40:
                    relationship_types['acquaintances'] += 1
                elif affinity < 20:
                    relationship_types['enemies'] += 1

        # Find most/least connected NPCs
        most_connected = max(connections_per_npc.items(), key=lambda x: x[1]) if connections_per_npc else ("None", 0)
        least_connected = min(connections_per_npc.items(), key=lambda x: x[1]) if connections_per_npc else ("None", 0)

        # Calculate statistics
        avg_affinity = sum(affinity_levels) / len(affinity_levels) if affinity_levels else 0

        return {
            'total_relationships': total_relationships,
            'avg_affinity': round(avg_affinity, 2),
            'relationship_types': dict(relationship_types),
            'most_connected': most_connected[0],
            'most_connections_count': most_connected[1],
            'least_connected': least_connected[0],
            'least_connections_count': least_connected[1],
            'strongest_bonds': sorted(strongest_bonds, key=lambda x: x['affinity'], reverse=True)[:10],
            'network_density': self._calculate_network_density()
        }

    def _calculate_network_density(self) -> float:
        """Calculate how interconnected the social network is"""
        n = len(self.sim.npcs)
        if n <= 1:
            return 0.0

        max_possible = n * (n - 1)  # directed graph
        actual = sum(len(npc.relationships) for npc in self.sim.npcs)

        return round(actual / max_possible, 3) if max_possible > 0 else 0.0

    def find_social_clusters(self) -> List[List[str]]:
        """Identify groups of NPCs who interact frequently"""
        # Simple clustering based on relationship strength
        clusters = []
        processed = set()

        for npc in self.sim.npcs:
            if npc.full_name in processed:
                continue

            cluster = [npc.full_name]
            processed.add(npc.full_name)

            # Find their close friends
            for rel_name, rel_data in npc.relationships.items():
                if rel_data.get('affinity', 0) > 70 and rel_name not in processed:
                    cluster.append(rel_name)
                    processed.add(rel_name)

            if len(cluster) > 1:
                clusters.append(cluster)

        return sorted(clusters, key=len, reverse=True)

    # ========================================================================
    # BEHAVIOR PATTERN ANALYSIS
    # ========================================================================

    def analyze_behavior_patterns(self) -> Dict[str, Any]:
        """Analyze NPC behavior patterns and routines"""

        location_distribution = Counter()
        mood_distribution = Counter()
        needs_analysis = {
            'hunger': [],
            'energy': [],
            'hygiene': [],
            'social': [],
            'fun': [],
            'horny': [],
            'lonely': []
        }

        for npc in self.sim.npcs:
            # Location patterns
            location_distribution[npc.current_location] += 1

            # Mood distribution
            mood_distribution[npc.mood] += 1

            # Needs analysis
            needs_analysis['hunger'].append(npc.needs.hunger)
            needs_analysis['energy'].append(npc.needs.energy)
            needs_analysis['hygiene'].append(npc.needs.hygiene)
            needs_analysis['social'].append(npc.needs.social)
            needs_analysis['fun'].append(npc.needs.fun)
            needs_analysis['horny'].append(npc.needs.horny)
            needs_analysis['lonely'].append(npc.psyche.lonely)

        # Calculate averages and identify extremes
        needs_summary = {}
        for need, values in needs_analysis.items():
            if values:
                needs_summary[need] = {
                    'avg': round(sum(values) / len(values), 1),
                    'min': round(min(values), 1),
                    'max': round(max(values), 1),
                    'critical_count': sum(1 for v in values if v < 20 or v > 90)
                }

        return {
            'location_distribution': dict(location_distribution.most_common()),
            'mood_distribution': dict(mood_distribution),
            'needs_summary': needs_summary,
            'npcs_in_critical_state': self._find_critical_npcs()
        }

    def _find_critical_npcs(self) -> List[Dict[str, Any]]:
        """Find NPCs with critical needs or extreme states"""
        critical = []

        for npc in self.sim.npcs:
            issues = []

            if npc.needs.hunger < 20:
                issues.append('starving')
            if npc.needs.energy < 20:
                issues.append('exhausted')
            if npc.needs.hygiene < 20:
                issues.append('dirty')
            if npc.psyche.lonely > 80:
                issues.append('very_lonely')
            if npc.needs.horny > 90:
                issues.append('extremely_horny')

            if issues:
                critical.append({
                    'name': npc.full_name,
                    'issues': issues,
                    'location': npc.current_location
                })

        return critical

    # ========================================================================
    # TIME-SERIES ANALYSIS
    # ========================================================================

    def get_time_summary(self) -> Dict[str, Any]:
        """Get current time context and statistics"""
        return {
            'current_time': self.sim.time.get_datetime_string(),
            'total_days': self.sim.time.total_days,
            'current_step': self.sim.current_step,
            'day_of_week': self.sim.time.weekday_name,
            'time_of_day': self.sim.time.time_of_day,
            'season': self.sim.time.season,
            'is_weekend': self.sim.time.is_weekend,
            'weather': self.sim.world.weather
        }

    # ========================================================================
    # EVENT ANALYSIS
    # ========================================================================

    def analyze_events(self) -> Dict[str, Any]:
        """Analyze event patterns and history"""

        event_counts = Counter()
        recent_events_by_type = defaultdict(list)

        # Analyze recent events from event system
        if hasattr(self.sim, 'events') and hasattr(self.sim.events, 'recent_events'):
            for event in self.sim.events.recent_events:
                event_counts[event.kind] += 1
                recent_events_by_type[event.kind].append({
                    'location': event.location,
                    'actors': event.actors
                })

        # Get milestone events
        milestones = []

        # Check birthday system
        if hasattr(self.sim, 'birthdays'):
            upcoming = self.sim.birthdays.get_upcoming_birthdays(within_days=7)
            for days_away, names in upcoming.items():
                milestones.append({
                    'type': 'birthday',
                    'in_days': days_away,
                    'npcs': names
                })

        return {
            'event_counts': dict(event_counts),
            'total_events': sum(event_counts.values()),
            'recent_events_by_type': dict(recent_events_by_type),
            'upcoming_milestones': milestones
        }

    # ========================================================================
    # COMPREHENSIVE REPORT
    # ========================================================================

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a complete analysis report"""
        return {
            'time': self.get_time_summary(),
            'relationships': self.analyze_relationships(),
            'behaviors': self.analyze_behavior_patterns(),
            'events': self.analyze_events(),
            'social_clusters': self.find_social_clusters(),
            'statistics': self.sim.get_statistics()
        }

    def export_report(self, filename: str = "simulation_report.json"):
        """Export comprehensive report to JSON file"""
        report = self.generate_comprehensive_report()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✓ Report exported to: {filename}")
        return filename

    # ========================================================================
    # VISUALIZATION DATA
    # ========================================================================

    def get_relationship_graph_data(self, min_affinity: int = 20) -> Dict[str, List]:
        """Get data formatted for network visualization libraries"""
        nodes = []
        edges = []

        # Create nodes
        for npc in self.sim.npcs:
            nodes.append({
                'id': npc.full_name,
                'label': npc.full_name,
                'age': npc.age,
                'occupation': npc.occupation,
                'location': npc.current_location,
                'group': self._get_npc_group(npc)
            })

        # Create edges
        added_edges = set()
        for npc in self.sim.npcs:
            for rel_name, rel_data in npc.relationships.items():
                affinity = rel_data.get('affinity', 0)

                if affinity >= min_affinity:
                    # Avoid duplicate edges
                    edge_key = tuple(sorted([npc.full_name, rel_name]))
                    if edge_key not in added_edges:
                        edges.append({
                            'from': npc.full_name,
                            'to': rel_name,
                            'value': affinity,
                            'title': f"Affinity: {affinity}",
                            'color': self._get_edge_color(affinity)
                        })
                        added_edges.add(edge_key)

        return {'nodes': nodes, 'edges': edges}

    def _get_npc_group(self, npc) -> int:
        """Categorize NPC for graph visualization"""
        if npc.age < 18:
            return 1  # Teens
        elif npc.age < 30:
            return 2  # Young adults
        elif npc.age < 50:
            return 3  # Adults
        else:
            return 4  # Seniors

    def _get_edge_color(self, affinity: float) -> str:
        """Get edge color based on affinity level"""
        if affinity > 80:
            return '#00ff00'  # Green - best friends
        elif affinity > 60:
            return '#90ee90'  # Light green - friends
        elif affinity > 40:
            return '#ffff00'  # Yellow - neutral
        else:
            return '#ff0000'  # Red - enemies

    # ========================================================================
    # TREND ANALYSIS
    # ========================================================================

    def get_needs_trends(self) -> Dict[str, List[float]]:
        """Get current needs distribution for trending"""
        trends = {
            'hunger': [],
            'energy': [],
            'social': [],
            'horny': [],
            'lonely': []
        }

        for npc in self.sim.npcs:
            trends['hunger'].append(npc.needs.hunger)
            trends['energy'].append(npc.needs.energy)
            trends['social'].append(npc.needs.social)
            trends['horny'].append(npc.needs.horny)
            trends['lonely'].append(npc.psyche.lonely)

        return trends

    def print_summary(self):
        """Print a formatted summary to console"""
        print("\n" + "=" * 70)
        print(" SIMULATION ANALYSIS SUMMARY")
        print("=" * 70)

        time_info = self.get_time_summary()
        print(f"\n📅 TIME: {time_info['current_time']}")
        print(f"   Day {time_info['total_days']} | {time_info['season'].title()} | {time_info['weather']}")

        rel_info = self.analyze_relationships()
        print(f"\n🔗 RELATIONSHIPS:")
        print(f"   Total: {rel_info['total_relationships']}")
        print(f"   Avg Affinity: {rel_info['avg_affinity']}")
        print(f"   Most Connected: {rel_info['most_connected']} ({rel_info['most_connections_count']} connections)")
        print(f"   Network Density: {rel_info['network_density']}")

        behavior_info = self.analyze_behavior_patterns()
        print(f"\n👥 BEHAVIOR PATTERNS:")
        print(f"   Top Locations: {list(behavior_info['location_distribution'].items())[:3]}")
        if behavior_info['npcs_in_critical_state']:
            print(f"   ⚠️  Critical NPCs: {len(behavior_info['npcs_in_critical_state'])}")

        event_info = self.analyze_events()
        print(f"\n📰 EVENTS:")
        print(f"   Total Events: {event_info['total_events']}")
        if event_info['upcoming_milestones']:
            print(f"   Upcoming Milestones: {len(event_info['upcoming_milestones'])}")

        clusters = self.find_social_clusters()
        if clusters:
            print(f"\n👨‍👩‍👧‍👦 SOCIAL CLUSTERS:")
            for i, cluster in enumerate(clusters[:3], 1):
                print(f"   {i}. {', '.join(cluster[:5])}{'...' if len(cluster) > 5 else ''}")

        print("\n" + "=" * 70)
