# systems/statistics_system.py
# Track and display player statistics

from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Statistics:
    character_name: str
    
    # Social stats
    npcs_met: int = 0
    conversations_had: int = 0
    friends_made: int = 0
    romances_started: int = 0
    dates_been_on: int = 0
    relationships_total: int = 0
    
    # Intimate stats
    first_kisses: int = 0
    intimate_encounters: int = 0
    
    # Economic stats
    money_earned: int = 0
    money_spent: int = 0
    gifts_given: int = 0
    gifts_received: int = 0
    
    # Activities
    locations_visited: set = field(default_factory=set)
    events_attended: int = 0
    skills_leveled: int = 0
    
    # Time
    days_played: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    
    def get_summary(self) -> str:
        lines = [
            f"\nStatistics for {self.character_name}:",
            f"Days Played: {self.days_played}",
            "",
            "Social:",
            f"  People Met: {self.npcs_met}",
            f"  Conversations: {self.conversations_had}",
            f"  Friends: {self.friends_made}",
            f"  Romances: {self.romances_started}",
            f"  Dates: {self.dates_been_on}",
            "",
            "Economic:",
            f"  Money Earned: ${self.money_earned}",
            f"  Money Spent: ${self.money_spent}",
            f"  Net Worth: ${self.money_earned - self.money_spent}",
            f"  Gifts Given: {self.gifts_given}",
            "",
            "Activities:",
            f"  Locations Visited: {len(self.locations_visited)}",
            f"  Events Attended: {self.events_attended}",
            f"  Skills Leveled: {self.skills_leveled}",
        ]
        return "\n".join(lines)


class StatisticsSystem:
    def __init__(self):
        self.stats: Dict[str, Statistics] = {}
    
    def get_stats(self, character_name: str) -> Statistics:
        if character_name not in self.stats:
            self.stats[character_name] = Statistics(character_name=character_name)
        return self.stats[character_name]
    
    def record_npc_met(self, character_name: str):
        self.get_stats(character_name).npcs_met += 1
    
    def record_conversation(self, character_name: str):
        self.get_stats(character_name).conversations_had += 1
    
    def record_date(self, character_name: str):
        self.get_stats(character_name).dates_been_on += 1
    
    def record_location_visit(self, character_name: str, location: str):
        self.get_stats(character_name).locations_visited.add(location)
    
    def record_money_transaction(self, character_name: str, amount: int, is_income: bool):
        stats = self.get_stats(character_name)
        if is_income:
            stats.money_earned += amount
        else:
            stats.money_spent += abs(amount)
