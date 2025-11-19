# systems/seasonal_dynamics.py
"""
Seasonal & Cyclical Dynamics System v1.0
Purpose: World feels alive with recurring patterns and seasonal changes
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from core.time_system import TimeSystem


class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class SeasonalEffect:
    """Effects of a season on the world"""
    season: Season
    mood: str
    events: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    dangers: List[str] = field(default_factory=list)
    npc_effects: Dict[str, str] = field(default_factory=dict)


@dataclass
class WeeklyPattern:
    """Effects of day of the week"""
    day: DayOfWeek
    mood: str
    teen_behavior: Optional[str] = None
    adult_behavior: Optional[str] = None
    special_events: List[str] = field(default_factory=list)


@dataclass
class CyclicalEvent:
    """Recurring events (full moon, payday, etc.)"""
    name: str
    frequency_days: int
    last_occurrence: int
    effects: List[str] = field(default_factory=list)
    
    def is_due(self, current_day: int) -> bool:
        """Check if event should occur"""
        return (current_day - self.last_occurrence) >= self.frequency_days
    
    def trigger(self, current_day: int):
        """Mark event as occurred"""
        self.last_occurrence = current_day


class SeasonalDynamicsSystem:
    """
    Manages seasonal effects and cyclical patterns
    Creates temporal context that affects NPC behavior
    """
    
    def __init__(self):
        self.seasonal_effects: Dict[Season, SeasonalEffect] = {}
        self.weekly_patterns: Dict[DayOfWeek, WeeklyPattern] = {}
        self.cyclical_events: List[CyclicalEvent] = []
        self.active_effects: List[str] = []
        self.initialized = False
        
    def initialize_patterns(self):
        """Set up all seasonal and cyclical patterns"""
        if self.initialized:
            return
        
        # Define seasonal effects
        self.seasonal_effects = {
            Season.AUTUMN: SeasonalEffect(
                season=Season.AUTUMN,
                mood="Back-to-routine stress, melancholy",
                events=[
                    "School year started",
                    "Football season",
                    "Homecoming dance (teens excited)",
                    "Halloween approaching"
                ],
                opportunities=[
                    "School dance = asking crushes",
                    "Halloween party = drinking opportunity",
                    "Cooler weather = more indoor time = more family tension"
                ],
                npc_effects={
                    "Teens": "School stress, social pressure, excitement",
                    "Adults": "Routine settling in, seasonal depression starting",
                    "Scarlet": "Holidays approaching = more family time with Tony = more danger"
                }
            ),
            
            Season.WINTER: SeasonalEffect(
                season=Season.WINTER,
                mood="Isolation, seasonal depression, family pressure",
                events=[
                    "Holidays approaching",
                    "Christmas stress",
                    "New Year's resolutions"
                ],
                opportunities=[
                    "Holiday parties = drinking",
                    "Family gatherings = forced proximity",
                    "Cold = trapped inside more"
                ],
                dangers=[
                    "Domestic violence increases during holidays",
                    "Depression worsens",
                    "Alcohol consumption up"
                ]
            ),
            
            Season.SPRING: SeasonalEffect(
                season=Season.SPRING,
                mood="Hope, renewal, awakening",
                events=[
                    "Prom approaching",
                    "Graduation season",
                    "Spring break"
                ],
                opportunities=[
                    "Warm weather = more outdoor encounters",
                    "Spring break = unsupervised teens",
                    "End of school year = transitions"
                ]
            ),
            
            Season.SUMMER: SeasonalEffect(
                season=Season.SUMMER,
                mood="Freedom, heat, restlessness",
                events=[
                    "School's out",
                    "Vacation season",
                    "4th of July"
                ],
                opportunities=[
                    "Unsupervised teens all day",
                    "Night swimming = romantic opportunities",
                    "Heat = shorter tempers, less clothing"
                ]
            )
        }
        
        # Define weekly patterns
        self.weekly_patterns = {
            DayOfWeek.MONDAY: WeeklyPattern(
                day=DayOfWeek.MONDAY,
                mood="Back to grind",
                teen_behavior="School stress renewed",
                adult_behavior="Work week begins"
            ),
            
            DayOfWeek.TUESDAY: WeeklyPattern(
                day=DayOfWeek.TUESDAY,
                mood="Midweek grind",
                special_events=["Routine, predictable, boring"]
            ),
            
            DayOfWeek.WEDNESDAY: WeeklyPattern(
                day=DayOfWeek.WEDNESDAY,
                mood="Hump day",
                special_events=["Nina's yoga classes busiest", "Alex's workout day"]
            ),
            
            DayOfWeek.THURSDAY: WeeklyPattern(
                day=DayOfWeek.THURSDAY,
                mood="Almost weekend",
                special_events=["Anticipation building"]
            ),
            
            DayOfWeek.FRIDAY: WeeklyPattern(
                day=DayOfWeek.FRIDAY,
                mood="RELIEF + EXCITEMENT",
                teen_behavior="Party planning begins",
                adult_behavior="Drinking increases 40%",
                special_events=[
                    "Underage drinking attempts",
                    "Nina at bar without Ken",
                    "Affairs more likely"
                ]
            ),
            
            DayOfWeek.SATURDAY: WeeklyPattern(
                day=DayOfWeek.SATURDAY,
                mood="Freedom",
                teen_behavior="Unsupervised",
                adult_behavior="Catch up on life",
                special_events=[
                    "Tony drunk by afternoon = Scarlet in danger"
                ]
            ),
            
            DayOfWeek.SUNDAY: WeeklyPattern(
                day=DayOfWeek.SUNDAY,
                mood="Rest + Obligation",
                special_events=[
                    "Church: Social pressure, judgment",
                    "Family dinners: Forced proximity",
                    "Sturm family dinner: Alex/Maria/John tension peaks",
                    "Tony hungover: unpredictable",
                    "Evening: Dread of Monday"
                ]
            )
        }
        
        # Initialize cyclical events
        self.cyclical_events = [
            CyclicalEvent(
                name="Full Moon",
                frequency_days=28,
                last_occurrence=0,
                effects=[
                    "Sleep disruption",
                    "Moods intensified",
                    "Supernatural beliefs activated"
                ]
            ),
            CyclicalEvent(
                name="Payday (1st)",
                frequency_days=30,  # Approximation
                last_occurrence=1,
                effects=[
                    "Financial stress relief",
                    "Spending increases",
                    "Scarlet saves portion for escape",
                    "Tony drinks more with money"
                ]
            ),
            CyclicalEvent(
                name="Payday (15th)",
                frequency_days=30,
                last_occurrence=15,
                effects=[
                    "Financial stress relief",
                    "Spending increases"
                ]
            )
        ]
        
        self.initialized = True
        print("✓ Seasonal dynamics system initialized")
    
    def update(self, time_system: 'TimeSystem') -> List[str]:
        """Update and return active temporal effects"""
        if not self.initialized:
            self.initialize_patterns()
        
        self.active_effects = []
        current_day = time_system.total_days
        
        # Get current season
        season = Season(time_system.season.lower())
        if season in self.seasonal_effects:
            effect = self.seasonal_effects[season]
            self.active_effects.append(f"SEASON ({season.value}): {effect.mood}")
            
            # Special seasonal events
            if season == Season.AUTUMN and 30 <= current_day <= 100:
                self.active_effects.append("Homecoming dance approaching - teen excitement and drama high")
        
        # Get day of week effects
        day_name = time_system.day_name.lower()
        try:
            day = DayOfWeek(day_name)
            if day in self.weekly_patterns:
                pattern = self.weekly_patterns[day]
                
                if day == DayOfWeek.FRIDAY:
                    self.active_effects.append("FRIDAY: Party anticipation, drinking up 40%, affairs more likely")
                
                elif day == DayOfWeek.SATURDAY:
                    self.active_effects.append("SATURDAY: Tony drunk by afternoon - Scarlet in danger")
                
                elif day == DayOfWeek.SUNDAY:
                    self.active_effects.append("SUNDAY: Church obligations, family dinners, forced proximity creates tension")
        except ValueError:
            pass  # Day name not in enum
        
        # Check cyclical events
        for event in self.cyclical_events:
            if event.is_due(current_day):
                event.trigger(current_day)
                self.active_effects.append(f"{event.name}: {'; '.join(event.effects)}")
        
        # Full moon check
        if current_day % 28 == 0:
            self.active_effects.append("Full moon tonight - sleep disrupted, emotions heightened")
        
        # Payday check (1st and 15th of month)
        day_of_month = time_system.current_time.day
        if day_of_month in [1, 15]:
            self.active_effects.append("Payday - financial stress temporarily relieved, spending up")
        
        return self.active_effects
    
    def get_seasonal_modifier(self, season: Season, behavior_type: str) -> float:
        """Get a modifier for behavior based on season"""
        modifiers = {
            Season.WINTER: {
                'depression': 1.3,
                'alcohol_use': 1.2,
                'domestic_violence': 1.4,
                'social_activity': 0.7
            },
            Season.SUMMER: {
                'teen_freedom': 1.5,
                'romantic_encounters': 1.3,
                'outdoor_activity': 1.4,
                'sexual_activity': 1.2
            },
            Season.AUTUMN: {
                'school_stress': 1.4,
                'routine_establishment': 1.2,
                'social_pressure': 1.3
            },
            Season.SPRING: {
                'hope': 1.3,
                'new_relationships': 1.2,
                'transitions': 1.4
            }
        }
        
        return modifiers.get(season, {}).get(behavior_type, 1.0)
    
    def get_day_modifier(self, day: DayOfWeek, behavior_type: str) -> float:
        """Get a modifier for behavior based on day of week"""
        modifiers = {
            DayOfWeek.FRIDAY: {
                'partying': 1.5,
                'drinking': 1.4,
                'hookups': 1.3,
                'affairs': 1.2
            },
            DayOfWeek.SATURDAY: {
                'domestic_violence': 1.6,  # Tony drunk
                'unsupervised_teens': 1.5,
                'family_time': 0.8
            },
            DayOfWeek.SUNDAY: {
                'family_tension': 1.4,
                'forced_proximity': 1.5,
                'social_judgment': 1.3
            }
        }
        
        return modifiers.get(day, {}).get(behavior_type, 1.0)
    
    def is_high_risk_time(self, time_system: 'TimeSystem') -> bool:
        """Check if current time has elevated risk factors"""
        day_name = time_system.day_name.lower()
        
        # Saturday evening = Tony drunk and violent
        if day_name == 'saturday' and time_system.hour >= 14:
            return True
        
        # Sunday family dinners = forced proximity
        if day_name == 'sunday' and 17 <= time_system.hour <= 20:
            return True
        
        # Winter holidays = elevated domestic violence
        season = Season(time_system.season.lower())
        if season == Season.WINTER:
            return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        return {
            'seasonal_effects_defined': len(self.seasonal_effects),
            'weekly_patterns_defined': len(self.weekly_patterns),
            'cyclical_events_tracked': len(self.cyclical_events),
            'active_effects_current': len(self.active_effects)
        }
    
    def export(self) -> Dict:
        """Export seasonal data"""
        return {
            'cyclical_events': [
                {
                    'name': e.name,
                    'frequency_days': e.frequency_days,
                    'last_occurrence': e.last_occurrence,
                    'effects': e.effects
                }
                for e in self.cyclical_events
            ],
            'active_effects': self.active_effects
        }